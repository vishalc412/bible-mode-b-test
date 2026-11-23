"""Checks every planned certificate and trust store; writes certs.json.

usage: cert_check.py --repo <repo> --plan <certs-to-check.yaml> --out <certs.json>
                     [--min-renew-before-days N] [--max-server-lifetime-days N] [--max-client-lifetime-days N]

The plan's renew_before_days and max_lifetime_days may be stricter than the
limits given on the command line (check.sh gives the policy's), never looser,
and renew_before_days is never below 0.

The plan (paths relative to the repository root):

    environment: local                 # local | test | staging | production
    renew_before_days: 21
    max_lifetime_days: 90
    local_fingerprints: tls-migration/local/ca-fingerprints.txt   # optional
    certificates:
      - path: tls-migration/local/certs/inventory-server.crt
        role: server                   # server | client
        issuer_ca: tls-migration/local/certs/server-ca.crt
        names: [localhost, inventory, 127.0.0.1]     # server: every name consumers use
      - path: tls-migration/local/certs/orders.crt
        role: client
        issuer_ca: tls-migration/local/certs/inventory-consumers-ca.crt
        consumer_id: orders
    trust_stores:
      - path: tls-migration/local/certs/inventory-consumers-ca.crt
        used_by: inventory, for client certificates
        expect_only: [local-dev-inventory-consumers-ca]
        previous_ca: tls-migration/local/certs/inventory-consumers-ca.previous.crt   # optional, during a rotation

expect_only lists one name per certificate in the file: during a CA rotation
the trust file holds the new CA and the previous one, so the name is listed twice.

Names are not identity: anyone can make a CA with the planned name. So every
certificate in a trust store must also be, by SHA-256 fingerprint, a CA that
really issued (signature checked) a planned certificate, or one of its CAs in
the same issuer file, or a declared previous CA: a file named in the store's
previous_ca, or the rotation files certgen-test-ca.sh writes beside the store
(<name>.previous.crt, <name>.current.crt). A store that is the issuer_ca of a
planned certificate must hold the CA that issued it. A store whose CAs issue
nothing in this plan (a consumer-only run's copy of the producer's server CA,
a kit's ca-bundle.pem) must hold exactly one CA, besides declared previous ones.

Throwaway CAs stay in their environment: a "local-dev-" CA fails anywhere but
local, and a "test-" CA (or one marked "tls-migration test only") fails
anywhere but test. A leaf that would outlive the CA that signed it fails too.

Every check is pass or fail; a file that cannot be read is a fail, never a
skip. Exit status 0 when nothing failed, 1 otherwise, 2 for a bad plan.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tlslib  # noqa: E402

LOCAL_PREFIX = "local-dev-"
TEST_PREFIX = "test-"
TEST_MARK = "tls-migration test only"


def plan_path_problems(repo: Path, plan: dict[str, Any]) -> list[str]:
    """Every path in the plan that leads out of the repository (D3)."""
    named = [("local_fingerprints", plan.get("local_fingerprints"))]
    for section in ("certificates", "trust_stores"):
        for index, entry in enumerate(plan.get(section) or []):
            if not isinstance(entry, dict):
                continue
            for key in ("path", "issuer_ca", "previous_ca"):
                value = entry.get(key)
                named += [(f"{section}[{index}].{key}", item) for item in (value if isinstance(value, list) else [value])]
    problems = []
    for key, value in named:
        if value in (None, ""):
            continue
        try:
            tlslib.repo_path(repo, value)
        except ValueError as problem:
            problems.append(f"{key}: {problem}")
    return problems


def _result(ok: bool, detail: str) -> dict[str, str]:
    return {"result": "pass" if ok else "fail", "detail": detail}


def load_local_fingerprints(repo: Path, plan: dict[str, Any]) -> set[str]:
    listed = plan.get("local_fingerprints")
    if not listed:
        return set()
    path = repo / listed
    if not path.is_file():
        return set()
    return {line.split()[0].lower() for line in tlslib.read_regular(path).splitlines() if line.strip()}


def is_local_dev(info: dict[str, Any], fingerprints: set[str]) -> bool:
    names = [info.get("subject_cn") or "", info.get("issuer_cn") or ""]
    return any(name.startswith(LOCAL_PREFIX) for name in names) or info.get("fingerprint_sha256") in fingerprints


def is_test_ca(info: dict[str, Any]) -> bool:
    """True for a certificate that is, or was signed by, a certgen-test-ca.sh test CA."""
    names = [info.get("subject_cn") or "", info.get("issuer_cn") or ""]
    marked = TEST_MARK in (info.get("subject") or "") or TEST_MARK in (info.get("issuer") or "")
    return marked or any(name.startswith(TEST_PREFIX) and name.endswith(("-ca", "-untrusted-client")) for name in names)


def check_certificate(repo: Path, entry: dict[str, Any], plan: dict[str, Any], fingerprints: set[str]) -> dict[str, Any]:
    path = repo / str(entry.get("path", ""))
    role = entry.get("role")
    report: dict[str, Any] = {"path": entry.get("path"), "role": role, "checks": {}}
    checks = report["checks"]
    if role not in ("server", "client"):
        checks["role"] = _result(False, f"role must be server or client, got {role!r}")
        return report
    try:
        info = tlslib.cert_info(path)
    except (OSError, ValueError) as problem:
        checks["readable"] = _result(False, str(problem))
        return report
    report["subject_cn"] = info["subject_cn"]
    report["issuer_cn"] = info["issuer_cn"]
    report["not_after"] = info["not_after"]
    report["fingerprint_sha256"] = info["fingerprint_sha256"]
    checks["readable"] = _result(True, "certificate parsed; no key in the file")

    wanted_usage = ["serverAuth"] if role == "server" else ["clientAuth"]
    checks["usage"] = _result(
        info["extended_key_usage"] == wanted_usage,
        f"extended key usage {info['extended_key_usage'] or 'absent'}; expected exactly {wanted_usage}",
    )
    checks["not_ca"] = _result(not info["is_ca"], "CA:FALSE" if not info["is_ca"] else "certificate is a CA")

    if role == "server":
        names = [str(n) for n in entry.get("names") or []]
        missing = [n for n in names if not tlslib.name_covered(n, info["san"])]
        if not names:
            checks["names"] = _result(False, "the plan lists no names for this server; every consumer address must be listed")
        else:
            checks["names"] = _result(not missing, "all names covered" if not missing else f"not covered: {missing}")
    else:
        consumer = str(entry.get("consumer_id") or "")
        checks["names"] = _result(
            bool(consumer) and info["subject_cn"] == consumer,
            f"CN={info['subject_cn']}; expected CN={consumer or '(no consumer_id in plan)'}",
        )

    issuer = entry.get("issuer_ca")
    if not issuer:
        checks["chain"] = _result(False, "the plan names no issuer_ca")
    else:
        purpose = "sslserver" if role == "server" else "sslclient"
        try:
            ok, message = tlslib.verify_chain(path, repo / str(issuer), purpose)
        except (OSError, ValueError) as problem:
            ok, message = False, str(problem)
        checks["chain"] = _result(ok, f"verified against {issuer} only, purpose {purpose}: {message}")
        try:
            ca_ends = [tlslib.cert_info_from_pem(pem)["not_after"] for pem in tlslib.split_bundle(repo / str(issuer))]
        except (OSError, ValueError):
            ca_ends = []
        if ca_ends:
            within = info["not_after"] <= max(ca_ends)
            checks["within_issuer"] = _result(
                within, "ends before its CA does" if within else f"ends {info['not_after']}, after its CA ({max(ca_ends)})")

    limits = plan.get("_limits") or {}
    # The plan may be stricter than the limits it is given, never looser; a negative
    # renewal margin would accept a certificate that has already expired.
    renew_before = max(int(plan.get("renew_before_days", 21)), 0, int(limits.get("min_renew_before_days") or 0))
    left = tlslib.days_left(info)
    not_yet = tlslib.days_left({"not_after": info["not_before"]}) > 0
    checks["validity"] = _result(
        left > renew_before and not not_yet,
        f"{left:.1f} days left (must be more than {renew_before})" + ("; not valid yet" if not_yet else ""),
    )
    max_life = int(plan.get("max_lifetime_days", 90))
    ceiling = limits.get(f"max_{role}_lifetime_days")
    if ceiling:
        max_life = min(max_life, int(ceiling))
    life = tlslib.lifetime_days(info)
    checks["lifetime"] = _result(life <= max_life + 1, f"lifetime {life:.0f} days (limit {max_life})")
    checks["key"] = _result(tlslib.key_allowed(info["key_type"]), f"key {info['key_type']}")

    environment = plan.get("_effective_environment", plan.get("environment"))
    if environment != "local":
        local = is_local_dev(info, fingerprints)
        checks["no_local_dev"] = _result(not local, "chains to a local-dev CA" if local else "no local-dev CA")
    if environment != "test":
        test = is_test_ca(info)
        checks["no_test_ca"] = _result(
            not test, f"issued by a test CA, which is only for the test environment (this is {environment})" if test else "no test CA")
    return report


def _verifies(leaf: str, untrusted: list[str], ca: str, purpose: str | None) -> bool:
    """True when the leaf's signature chains to this one CA certificate (taken as
    the trust anchor, so an intermediate counts), and to nothing else."""
    with tempfile.TemporaryDirectory() as scratch:
        anchor = Path(scratch) / "ca.pem"
        anchor.write_text(ca + "\n", encoding="utf-8")
        # Who signed it is the question, not whether it is still valid: dates are E5's.
        cmd = ["openssl", "verify", "-no-CApath", "-no-CAstore", "-partial_chain", "-no_check_time", "-CAfile", str(anchor)]
        if untrusted:
            helpers = Path(scratch) / "untrusted.pem"
            helpers.write_text("\n".join(untrusted) + "\n", encoding="utf-8")
            cmd += ["-untrusted", str(helpers)]
        if purpose:
            cmd += ["-purpose", purpose]
        code, out, _ = tlslib.run(cmd, stdin=leaf)
    return code == 0 and "OK" in out


def issuing_cas(repo: Path, plan: dict[str, Any]) -> dict[str, Any]:
    """The CAs that really issue the planned certificates, by fingerprint: for
    each certificate, the CA in its issuer_ca file its signature chains to, and
    the CAs in that file that in turn issued that one. {"server": [...],
    "client": [...], "by_issuer_file": {path: [...]}}."""
    found: dict[str, set[str]] = {"server": set(), "client": set()}
    by_file: dict[str, set[str]] = {}
    for entry in plan.get("certificates") or []:
        if not isinstance(entry, dict) or entry.get("role") not in found or not entry.get("issuer_ca"):
            continue
        try:
            leaf = tlslib.split_bundle(repo / str(entry.get("path", "")))
            cas = [(pem, tlslib.cert_info_from_pem(pem)) for pem in tlslib.split_bundle(repo / str(entry["issuer_ca"]))]
        except (OSError, ValueError):
            continue
        if not leaf:
            continue
        issued = [(pem, info) for pem, info in cas if _verifies(leaf[0], leaf[1:], pem, None)]
        chain = list(issued)
        while True:          # the CAs above the issuing one, in the same file
            more = [(pem, info) for pem, info in cas if (pem, info) not in chain
                    and any(_verifies(child, [], pem, None) for child, _ in chain)]
            if not more:
                break
            chain += more
        prints = {info["fingerprint_sha256"] for _, info in chain}
        found[entry["role"]] |= prints
        by_file.setdefault(str(entry["issuer_ca"]), set()).update(prints)
    return {"server": sorted(found["server"]), "client": sorted(found["client"]),
            "by_issuer_file": {k: sorted(v) for k, v in by_file.items()}}


def _previous_cas(repo: Path, entry: dict[str, Any]) -> tuple[set[str], list[str]]:
    """Fingerprints of the CAs a trust store may hold besides the planned ones
    during a rotation: the store's previous_ca files and the rotation files
    beside it. (fingerprints, the files they came from)."""
    path = repo / str(entry.get("path", ""))
    stem = path.name[:-len(path.suffix)] if path.suffix else path.name
    files = [repo / str(f) for f in (entry.get("previous_ca") if isinstance(entry.get("previous_ca"), list)
                                     else [entry["previous_ca"]] if entry.get("previous_ca") else [])]
    files += [path.parent / f"{stem}.previous{path.suffix}", path.parent / f"{stem}.current{path.suffix}"]
    prints: set[str] = set()
    used = []
    for candidate in files:
        if candidate.resolve() == path.resolve() or not candidate.is_file():
            continue
        try:
            prints |= {tlslib.cert_info_from_pem(pem)["fingerprint_sha256"] for pem in tlslib.split_bundle(candidate)}
            used.append(tlslib.shown_path(candidate, repo))
        except (OSError, ValueError):
            continue
    return prints, used


def check_trust_store(repo: Path, entry: dict[str, Any], plan: dict[str, Any], fingerprints: set[str],
                      issuing: dict[str, Any] | None = None) -> dict[str, Any]:
    path = repo / str(entry.get("path", ""))
    report: dict[str, Any] = {"path": entry.get("path"), "used_by": entry.get("used_by"), "checks": {}}
    expected = sorted(str(name) for name in entry.get("expect_only") or [])
    try:
        pems = tlslib.split_bundle(path)
        infos = [tlslib.cert_info_from_pem(pem) for pem in pems]
    except (OSError, ValueError) as problem:
        report["checks"]["readable"] = _result(False, str(problem))
        return report
    found = sorted(info["subject_cn"] or info["subject"] for info in infos)
    report["contains"] = found
    report["fingerprints"] = sorted(info["fingerprint_sha256"] for info in infos)
    if not expected:
        report["checks"]["scope"] = _result(False, "the plan gives no expect_only list for this trust store")
    else:
        report["checks"]["scope"] = _result(
            found == expected,
            "holds exactly the planned CA(s)" if found == expected else f"holds {found}; planned only {expected}",
        )
    report["checks"]["all_ca"] = _result(
        bool(infos) and all(info["is_ca"] for info in infos),
        "every entry is a CA certificate" if infos else "empty trust store",
    )
    if issuing is not None:
        report["checks"]["planned_ca"] = _planned_ca_check(repo, entry, infos, issuing, report)
    if plan.get("_effective_environment", plan.get("environment")) != "local":
        local = any(is_local_dev(info, fingerprints) for info in infos)
        report["checks"]["no_local_dev"] = _result(not local, "holds a local-dev CA" if local else "no local-dev CA")
    environment = plan.get("_effective_environment", plan.get("environment"))
    if environment != "test":
        test = any(is_test_ca(info) for info in infos)
        report["checks"]["no_test_ca"] = _result(
            not test, f"holds a test CA, which is only for the test environment (this is {environment})" if test else "no test CA")
    return report


def _planned_ca_check(repo: Path, entry: dict[str, Any], infos: list[dict[str, Any]], issuing: dict[str, Any],
                      report: dict[str, Any]) -> dict[str, str]:
    """Every certificate in the store is a planned CA, by fingerprint, not by name."""
    planned = set(issuing.get("server") or []) | set(issuing.get("client") or [])
    previous, previous_files = _previous_cas(repo, entry)
    report["previous_fingerprints"] = sorted(previous)
    report["previous_files"] = previous_files
    held = [(info["fingerprint_sha256"], info.get("subject_cn") or info.get("subject")) for info in infos]
    as_issuer = issuing.get("by_issuer_file", {}).get(str(entry.get("path")))
    if as_issuer is not None and not set(as_issuer) & {fp for fp, _ in held}:
        return _result(False, "this file is the issuer_ca of planned certificates, but holds none of the CAs that issued them")
    if any(fp in planned for fp, _ in held) or as_issuer is not None:
        strangers = [f"{name} (SHA-256 {fp[:16]}…)" for fp, name in held if fp not in planned and fp not in previous]
        if strangers:
            return _result(False, f"holds {strangers}: not the CA that issued a planned certificate and not a declared previous CA "
                           "(a name proves nothing; the fingerprint is compared)")
        return _result(True, "every CA is, by fingerprint, one that issued a planned certificate"
                       + (f" or a declared previous CA ({', '.join(previous_files)})" if previous_files else ""))
    others = [(fp, name) for fp, name in held if fp not in previous]
    if len(others) != 1:
        return _result(False, f"none of its CAs issues a certificate in this plan, so it may hold exactly one (the other side's CA, "
                       f"as a kit delivers it), besides a declared previous CA; it holds {len(others)}")
    return _result(True, f"one CA outside this plan's certificates ({others[0][1]}, SHA-256 {others[0][0][:16]}…): the other side's")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--min-renew-before-days", type=int, help="a floor for renew_before_days the plan cannot lower "
                        "(check.sh passes the policy's)")
    parser.add_argument("--max-server-lifetime-days", type=int, help="a ceiling for a server certificate's lifetime the plan cannot raise")
    parser.add_argument("--max-client-lifetime-days", type=int, help="a ceiling for a client certificate's lifetime the plan cannot raise")
    parser.add_argument("--environment", help="the run's environment from the manifest; the local-dev checks follow it, "
                        "not the plan's own environment line")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    try:
        plan = tlslib.load_yaml(repo / args.plan if not Path(args.plan).is_absolute() else args.plan) or {}
    except (OSError, ValueError) as problem:
        print(f"cannot read the plan: {problem}", file=sys.stderr)
        return 2
    if plan.get("environment") not in ("local", "test", "staging", "production"):
        print("the plan must name environment: local, test, staging or production", file=sys.stderr)
        return 2
    outside = plan_path_problems(repo, plan)
    if outside:
        print("the plan names paths outside the repository (a plan may only name files inside it; nothing was read): "
              + "; ".join(outside[:5]), file=sys.stderr)
        return 2
    plan["_effective_environment"] = args.environment or plan.get("environment")
    plan["_limits"] = {"min_renew_before_days": args.min_renew_before_days, "max_server_lifetime_days": args.max_server_lifetime_days,
                       "max_client_lifetime_days": args.max_client_lifetime_days}
    fingerprints = load_local_fingerprints(repo, plan)
    certificates = [check_certificate(repo, e, plan, fingerprints) for e in plan.get("certificates") or []]
    issuing = issuing_cas(repo, plan)
    stores = [check_trust_store(repo, e, plan, fingerprints, issuing) for e in plan.get("trust_stores") or []]

    def fails(items: list[dict[str, Any]], names: tuple[str, ...] | None = None) -> int:
        return sum(
            1 for item in items for name, check in item["checks"].items()
            if check["result"] == "fail" and (names is None or name in names)
        )

    result = {
        "tool": "cert_check.py",
        "generated_at": tlslib.iso(tlslib.now_utc()),
        "environment": plan["_effective_environment"],
        "plan_environment": plan.get("environment"),
        "limits": {"renew_before_days": max(int(plan.get("renew_before_days", 21)), 0, args.min_renew_before_days or 0),
                   "plan_renew_before_days": plan.get("renew_before_days"), "plan_max_lifetime_days": plan.get("max_lifetime_days"),
                   **{k: v for k, v in plan["_limits"].items() if v is not None}},
        "plan": tlslib.shown_path(repo / args.plan if not Path(args.plan).is_absolute() else args.plan, repo),
        "certificates": certificates,
        "trust_stores": stores,
        "certificate_count": len(certificates),
        "trust_store_count": len(stores),
        "failures": fails(certificates) + fails(stores),
        "trust_scope_violations": fails(stores, ("scope", "all_ca", "planned_ca")),
        "issuing_cas": {"server": issuing["server"], "client": issuing["client"]},
        "local_dev_violations": fails(certificates, ("no_local_dev",)) + fails(stores, ("no_local_dev",)),
        "test_ca_violations": fails(certificates, ("no_test_ca",)) + fails(stores, ("no_test_ca",)),
    }
    if args.environment and args.environment != plan.get("environment"):
        result["failures"] += 1
        result["note"] = f"the plan says environment {plan.get('environment')}, the run is {args.environment}"
    if not certificates:
        result["failures"] += 1
        result["note"] = "the plan lists no certificates"
    tlslib.write_json(args.out, result, repo)
    for item in certificates + stores:
        bad = [f"{n}: {c['detail']}" for n, c in item["checks"].items() if c["result"] == "fail"]
        print(f"{'FAIL' if bad else 'ok  '} {item['path']}" + ("".join(f"\n       {b}" for b in bad)))
    print(f"failures: {result['failures']}  trust scope violations: {result['trust_scope_violations']}")
    return 0 if result["failures"] == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except tlslib.UnsafeWrite as refused:   # a link or a path out of the repository (D2): nothing written
        print(f"refused: {refused}", file=sys.stderr)
        sys.exit(2)
