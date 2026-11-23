"""Live probes against a producer; writes probes.json.

usage:
  probe_tls.py --repo <repo> --plan <probe-plan.yaml> --out <probes.json> [--manifest tls-migration/tls-services.yaml]
  probe_tls.py --baseline --url <http url> [--url ...] --out <behaviour-before.json>
  probe_tls.py --repo <repo> --server-only <host:port> [--ca <ca file>] [--manifest ...]

--server-only: an HTTPS endpoint that asks for no client certificate (a third
party with a public CA). One request with certificate and host name checking
on, no client certificate, TLS 1.2 or later; the same host rule as every probe.
Writes tls-migration/evidence/server-only/<host>_<port>.json: target, protocol,
cipher, the certificate's subject, issuer and end date, the verify result, the
total and handshake time in ms, and when. Exit 0 pass, 1 fail or not run, 2 refused.

Timing: every request (the baseline, P1 and the other HTTP probes) records
total_ms and, over TLS, handshake_ms. It is a record for the report and never
decides a probe.

The plan (paths relative to the repository root, inside it; the keys may be
under the exported TLS_PRIVATE_DIR, written $TLS_PRIVATE_DIR/...):

    environment: local
    stage: 6                          # producer stage reached, 2 to 6
    target:
      host: localhost
      https_port: 8443
      http_port: 8080                 # the legacy plain port; omit if there never was one
      path: /stock/SKU-1
      expected_status: 200
      server_ca: tls-migration/local/certs/server-ca.crt
      expected_issuer: local-dev-server-ca
      expected_names: [localhost]
    health:                           # optional; the platform's probe path
      url: http://localhost:8081/actuator/health
      attempts: 3
    allowed_client:
      cert: tls-migration/local/certs/inventory-orders.crt
      key: $TLS_PRIVATE_DIR/local/inventory/orders/client.key   # passed to curl by path, never opened
    probe_certs: $TLS_PRIVATE_DIR/probe-local/inventory          # from make-probe-certs.sh
    baseline: tls-migration/evidence/behaviour-before.json
    baseline_ignore: [receivedOver]   # fields expected to change (e.g. a scheme echo)

Every probe sends a real request and is judged on the response or the alert,
never on "CONNECTED": under TLS 1.3 a server that rejects a client
certificate finishes the handshake and refuses on the first read.
A refusal only counts when P1 proved the service is up; otherwise the refusal
probes are "not run". A probe the local openssl cannot even attempt (it has
no TLS 1.1 or no weak ciphers to offer) is "not run", never "pass".
A refusal is the handshake failing or the connection being reset after the
certificate was offered (curl exit 35, 55, 56) or a 4xx refusal status. A curl
exit that means a problem on this side (58/59: the probe certificate or key
could not be loaded; 6, 7, 28: name, connection, timeout; 60, 77: the server
certificate or CA file) is "not run", and "accepted" is said only with a real
HTTP status. A probe certificate is sent only when its .crt and .key exist,
belong together and are valid now (P3, P4, and P1 when it uses
tls-probe-allowed); otherwise that probe is "not run". probes.json records
each probe certificate's SHA-256 fingerprint and end date (probe_certificates).

probes.json records bound_inputs: the SHA-256 of the producer config, the
allowlist, both plans and every planned certificate, read from the manifest.
check.sh refuses recorded probes when any of those files changed since.
At stage 6 P7 always runs: against target.http_port, or the producer's
legacy port from the manifest or config (8080 when neither says), and against
every other port the discovery step recorded for an in-scope host
(evidence/inventory.json): plain HTTP must be closed on all of them.

P1 records the SHA-256 of the client certificate it used; check.sh requires
it to expect and get a 2xx, to be compared with a baseline covering its path,
and to use a planned client certificate or tls-probe-allowed. health.url must
be an http:// or https:// URL (check.sh --live also holds its host to
in_scope_hosts).

Where a probe may connect (the same rule as check.sh --live, on every path):
this machine in a local run, or a host in the manifest's in_scope_hosts; never a
link-local or cloud metadata address, never a host the manifest does not list.
A plan that names another host is refused before anything is sent. Only http
and https are spoken, no redirect is followed, and only P1's answer is kept
(it is the one compared with the baseline), with secret values masked.

Every request carries X-TLS-Migration-Probe with a tag that is new on each run
(the probe id and a random part, 8 characters). The tags are appended to
probe-tags.log beside probes.json; readiness leaves out only recorded tags.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tlslib  # noqa: E402

# curl exit codes that mean the server refused us: the handshake failed (35),
# or the connection was reset or alerted on the first read or write after the
# client certificate was offered (56, 55; TLS 1.3 refuses only then).
CURL_TLS_REFUSALS = {35, 55, 56}
# curl exit codes that mean the request never reached a decision of the server:
# a problem on this machine or on the way. A refusal probe that ends this way is
# "not run", never "pass" (a missing probe key is not a server refusing it).
CURL_LOCAL_FAILURES = {
    6: "could not resolve the host name",
    7: "nothing listening on the port",
    28: "timed out",
    58: "curl could not load the client certificate or key on this machine (missing, unreadable or not matching)",
    59: "curl could not use the cipher list on this machine",
    60: "the server's certificate did not verify against target.server_ca",
    77: "curl could not read the CA file target.server_ca",
    80: "the TLS connection could not be shut down cleanly",
    90: "pinned public key did not match",
    91: "certificate status check failed",
    92: "HTTP/2 stream error",
}
REFUSAL_STATUSES = {"400", "401", "403", "495", "496"}
NOT_LISTENING = {7}
PROBE_HEADER = "X-TLS-Migration-Probe"


# ---------------------------------------------------------------- judging
# The same functions judge a live run and re-judge a recorded one in check.sh,
# so a hand-edited "result" field cannot survive the gate.

def judge(expected: str, observed: dict[str, Any], context: dict[str, Any] | None = None) -> tuple[str, str]:
    context = context or {}
    kind = observed.get("kind")
    if expected.startswith("status:"):
        if observed.get("precondition_failed"):
            return "not run", observed["precondition_failed"]
        want = expected.split(":", 1)[1]
        status = str(observed.get("http_status", ""))
        if observed.get("curl_exit") in NOT_LISTENING:
            return "fail", "nothing listening on the port"
        if status != want:
            return "fail", f"HTTP {status or 'none'} (curl exit {observed.get('curl_exit')}); expected {want}"
        if "body_matches_baseline" in observed and observed["body_matches_baseline"] is False:
            return "fail", "response differs from the baseline: " + str(observed.get("body_difference", ""))
        return "pass", f"HTTP {status}"
    if expected == "refused":
        if observed.get("precondition_failed"):
            return "not run", observed["precondition_failed"]
        exit_code = observed.get("curl_exit")
        status = str(observed.get("http_status", "") or "")
        if exit_code in NOT_LISTENING:
            return "not run", "nothing listening; a refusal cannot be told from an outage"
        if exit_code in CURL_LOCAL_FAILURES:
            return "not run", (f"curl exit {exit_code}: {CURL_LOCAL_FAILURES[exit_code]}; the request did not reach "
                               "the server's decision, so no refusal is proven")
        if exit_code in CURL_TLS_REFUSALS:
            return "pass", f"refused by TLS (curl exit {exit_code})"
        if status in REFUSAL_STATUSES:
            return "pass", f"refused with HTTP {status}"
        if re.fullmatch(r"[1-5]\d\d", status):
            return "fail", f"accepted: HTTP {status} (curl exit {exit_code})"
        # No HTTP answer and no known refusal: neither accepted nor refused.
        return "not run", f"no HTTP status and curl exit {exit_code}: neither a refusal nor an answer was seen"
    if expected == "protocol-refused":
        if observed.get("precondition_failed"):
            return "not run", observed["precondition_failed"]
        if observed.get("client_cannot_offer"):
            return "not run", "the local openssl cannot offer this; not tested"
        if observed.get("negotiated"):
            return "fail", f"server accepted {observed.get('protocol')} {observed.get('cipher')}"
        if observed.get("connect_failed"):
            return "not run", "could not connect at all"
        if not observed.get("refusal_seen"):
            return "not run", "no alert or refusal was seen, so a refusal is not proven"
        return "pass", "server refused the handshake"
    if expected == "closed":
        # Every port plain HTTP was ever served on must refuse the connection.
        ports = dict(observed.get("ports") or {})
        first = {"curl_exit": observed.get("curl_exit"), "http_status": observed.get("http_status")}
        still_open = {port: seen for port, seen in ports.items() if seen.get("curl_exit") not in NOT_LISTENING}
        if first["curl_exit"] not in NOT_LISTENING:        # the request itself, whatever the per-port record says
            still_open.setdefault("", first)
        if not still_open:
            return "pass", "plain HTTP port closed" + (f" (ports tried: {', '.join(sorted(ports))})" if ports else "")
        port, seen = sorted(still_open.items())[0]
        return "fail", (f"plain HTTP still answers{' on port ' + port if port else ''}: "
                        f"HTTP {seen.get('http_status')} (curl exit {seen.get('curl_exit')})")
    if expected == "answers":
        status = str(observed.get("http_status", ""))
        return ("pass", f"plain HTTP answers ({status}) as planned before stage 6") if status.startswith(("2", "3", "4")) and status != "000" \
            else ("fail", f"plain HTTP should still answer before stage 6; got {status or 'nothing'}")
    if expected == "chain-ok":
        if observed.get("connect_failed"):
            return "fail", observed.get("detail", "could not read the presented chain")
        problems = []
        if observed.get("verify_code") != "0":
            problems.append(f"verify return code {observed.get('verify_code')}")
        # The plan's expected issuer, else the one recorded with the probe. With neither,
        # the issuer is not compared: verify_code 0 already says the chain ends at the plan's CA.
        expected_issuer = context.get("expected_issuer") or observed.get("expected_issuer")
        if expected_issuer and observed.get("issuer_cn") != expected_issuer:
            problems.append(f"issuer {observed.get('issuer_cn')} is not {expected_issuer}")
        if observed.get("protocol") not in ("TLSv1.2", "TLSv1.3"):
            problems.append(f"protocol {observed.get('protocol')}")
        if observed.get("missing_names"):
            problems.append(f"names not covered: {observed['missing_names']}")
        if observed.get("days_left") is not None and observed["days_left"] <= observed.get("renew_before_days", 21):
            problems.append(f"only {observed['days_left']:.0f} days left")
        return ("fail", "; ".join(problems)) if problems else ("pass", f"{observed.get('protocol')}, issuer {observed.get('issuer_cn')}")
    if expected == "healthy":
        statuses = observed.get("statuses") or []
        if not statuses:
            return "fail", "no health probe was made"
        bad = [s for s in statuses if not str(s).startswith("2")]
        return ("fail", f"health statuses {statuses}") if bad else ("pass", f"{len(statuses)} health probes answered {statuses[0]}")
    if expected == "not-applicable":
        return "not applicable", observed.get("detail", "")
    if kind == "unknown":
        return "not run", observed.get("detail", "")
    return "fail", f"unknown expectation {expected!r}"


def expected_cases(stage: int, has_http_port: bool, has_health: bool) -> dict[str, str]:
    """The probes a run at this stage must contain, with what each must show."""
    cases = {
        "P1": "status",
        "P2": "refused" if stage >= 5 else "status",
        "P3": "refused",
        "P4": "status:403" if stage >= 4 else "not-applicable",
        "P5": "protocol-refused",
        "P6": "protocol-refused",
        "P9": "chain-ok",
    }
    if has_http_port:
        cases["P7"] = "closed" if stage >= 6 else "answers"
    if has_health:
        cases["P10"] = "healthy"
    return cases


# ---------------------------------------------------------------- binding

def bound_inputs(repo: Path, manifest: dict[str, Any]) -> dict[str, str]:
    """SHA-256 of every file a probe result depends on, by repository path: every
    Spring config source of the producer's module (not only the listed files),
    every deployment file that sets one of its stage keys, the producer module's
    code (src/main) and build files, and those of the modules it depends on, the
    allowlist, both plans and every planned certificate."""
    producer = manifest.get("producer") if isinstance(manifest.get("producer"), dict) else {}
    names: list[str] = []
    for key in ("config_files",):
        value = producer.get(key)
        names += [str(v) for v in (value if isinstance(value, list) else [value] if value else [])]
    try:
        import check_gate  # noqa: PLC0415 - the gate owns the discovery; imported late, it imports this module

        names += [name for name in check_gate.config_source_names(repo, manifest) if name not in names]
        # The producer's code and build files too: a probe describes the build it ran
        # against, so a change to the connector's code after probing means probing again.
        names += [name for name in check_gate.producer_code_names(repo, manifest) if name not in names]
    except Exception as problem:  # noqa: BLE001 - an unreadable source must not hide the others
        names.append(f"(config discovery failed: {type(problem).__name__})")
    for value in (producer.get("allowlist"), manifest.get("probe_plan"), manifest.get("cert_plan")):
        if value:
            names.append(str(value))
    cert_plan = manifest.get("cert_plan")
    try:
        plan_file = _path(repo, cert_plan) if cert_plan else None
    except ValueError:
        plan_file = None
    if plan_file is not None and plan_file.is_file():
        try:
            plan = tlslib.load_yaml(plan_file) or {}
        except ValueError:
            plan = {}
        for item in (plan.get("certificates") or []) + (plan.get("trust_stores") or []):
            if isinstance(item, dict) and item.get("path"):
                names.append(str(item["path"]))
    bound = {}
    for name in dict.fromkeys(names):
        try:
            path = _path(repo, name)
        except ValueError:
            bound[name] = "outside the repository: not read"
            continue
        bound[name] = tlslib.sha256_file(path) if path.is_file() else "missing"
    return bound


# ---------------------------------------------------------------- probing

def _path(repo: Path, value: Any, private: bool = False) -> Path:
    """A path the plan or manifest names: inside the repository only, or under the
    exported TLS_PRIVATE_DIR for the keys (private=True). Raises ValueError."""
    return tlslib.repo_path(repo, value, private)


# Never a probe target, whatever a file says: link-local addresses and the cloud
# metadata services, by address and by name.
_METADATA_NAMES = {"metadata", "metadata.google.internal", "metadata.goog", "instance-data",
                   "instance-data.ec2.internal", "metadata.azure.com", "metadata.tencentyun.com"}
_HOST_SYNTAX = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?")


def _address(host: str):
    import ipaddress  # noqa: PLC0415

    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


def is_loopback(host: Any) -> bool:
    """True for a name or address of this machine: a loopback address (127.0.0.0/8, ::1),
    the unspecified address (0.0.0.0, ::), or exactly the names localhost and
    host.docker.internal (brackets, case and a trailing dot ignored). A DNS name that
    only looks local (127.example.com, x.localhost) is not this machine: it can resolve
    anywhere, so it needs the user's yes like any other host."""
    text = str(host).lower().strip().strip("[]").rstrip(".")
    if text in ("localhost", "host.docker.internal"):
        return True
    address = _address(text)
    return address is not None and (address.is_loopback or address.is_unspecified)


def host_problem(host: Any, manifest: dict[str, Any] | None, environment: Any) -> str | None:
    """Why no probe may connect to `host`, or None (D6). Allowed: this machine in a
    local run, or one of in_scope_hosts. Never a link-local or cloud metadata
    address. Pure: reads nothing, connects to nothing."""
    text = str(host or "").strip().lower().rstrip(".")
    bare = text[1:-1] if text.startswith("[") and text.endswith("]") else text
    address = _address(bare)
    if address is None and not _HOST_SYNTAX.fullmatch(bare):
        return f"'{str(host)[:60]}' is not a host name or an address"
    if address is not None:
        mapped = getattr(address, "ipv4_mapped", None)
        if address.is_link_local or (mapped is not None and mapped.is_link_local) \
                or str(address) in ("100.100.100.200", "fd00:ec2::254", "192.0.0.192"):
            return f"{bare} is a link-local or cloud metadata address; never probed"
    if bare in _METADATA_NAMES:
        return f"{bare} is a cloud metadata name; never probed"
    if is_loopback(bare):
        return None if environment == "local" else f"{bare} is this machine; outside a local run a probe goes to the producer"
    if manifest:
        import check_gate  # noqa: PLC0415 - the gate owns the scope rule; imported late, it imports this module

        if check_gate.Scope(manifest).covers(bare):
            return None
    return f"{bare} is not one of the manifest's in_scope_hosts" + (" (or this machine, in a local run)" if environment == "local" else "")


def curl(url: str, ca: Path | None, cert: Path | None = None, key: Path | None = None,
         probe_id: str | None = None) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(delete=False) as body_file:
        body_path = body_file.name
    # -q first: no ~/.curlrc. http and https only, and no redirect is followed:
    # a probe goes where the plan's checked host is, nowhere else (D6).
    cmd = ["curl", "-q", "-sS", "--max-time", "10", "--proto", "=http,https", "--proto-redir", "=http,https",
           "--max-redirs", "0", "-o", body_path, "-w", CURL_WRITE_OUT]
    if probe_id:
        # Tags the request so readiness does not count the probe as a consumer call.
        cmd += ["-H", f"{PROBE_HEADER}: {probe_id}"]
    if ca:
        cmd += ["--cacert", str(ca)]
    if cert:
        cmd += ["--cert", str(cert)]
    if key:
        cmd += ["--key", str(key)]
    cmd.append(url)
    code, out, err = tlslib.run(cmd, timeout=20)
    body = Path(body_path).read_text(errors="replace")[:2000]
    os.unlink(body_path)
    status, timing = _write_out(out)
    return {"kind": "http", "url": tlslib.mask_secrets(url), "curl_exit": code, "http_status": status,
            "stderr": tlslib.mask_secrets(err.strip()[:300]), "body": body, **timing}


# What curl prints after each request: the status, then the times (seconds) from
# the start to the end, to the TCP connection and to the end of the TLS handshake.
CURL_WRITE_OUT = "%{http_code} %{time_total} %{time_connect} %{time_appconnect}"


def _write_out(out: str) -> tuple[str, dict[str, Any]]:
    """(HTTP status, timing) from CURL_WRITE_OUT: total_ms for the whole request and,
    over TLS, handshake_ms (the TLS handshake alone, after the TCP connection).
    Timing is a record for the report; it never decides a probe."""
    fields = (out or "").split()
    status = fields[0][-3:] if fields else ""
    timing: dict[str, Any] = {}
    try:
        total, connect, handshake_end = (float(value) for value in fields[1:4])
    except ValueError:
        return status, timing
    if total > 0:
        timing["total_ms"] = round(total * 1000, 1)
    if handshake_end > 0 and handshake_end >= connect:
        timing["handshake_ms"] = round((handshake_end - connect) * 1000, 1)
    return status, timing


def _without_body(observed: dict[str, Any]) -> dict[str, Any]:
    """A probe's record without the answer it got: only P1's answer is kept (D6)."""
    observed.pop("body", None)
    return observed


def name_check_flags(host: str) -> list[str]:
    """The openssl flag that checks the server certificate against the host: an
    address is matched to the certificate's IP names (-verify_ip), a host name to
    its DNS names (-verify_hostname would never match an address)."""
    return ["-verify_ip", host] if _address(host) is not None else ["-verify_hostname", host]


def s_client_command(host: str, port: int, extra: list[str], ca: Path | None = None) -> list[str]:
    # Server name indication carries host names only, never an address (RFC 6066).
    sni = [] if _address(host) is not None else ["-servername", host]
    cmd = ["openssl", "s_client", "-connect", f"[{host}]:{port}" if ":" in host else f"{host}:{port}"] + sni + extra
    if ca:
        cmd += ["-CAfile", str(ca), "-no-CApath", "-no-CAstore"]
    return cmd


def s_client(host: str, port: int, extra: list[str], ca: Path | None = None) -> tuple[int, str]:
    cmd = s_client_command(host, port, extra, ca)
    code, out, err = tlslib.run(cmd, stdin="", timeout=20)
    return code, out + "\n" + err


def protocol_probe(host: str, port: int, flags: list[str]) -> dict[str, Any]:
    _, text = s_client(host, port, flags)
    lowered = text.lower()
    observed: dict[str, Any] = {"kind": "tls", "flags": flags, "excerpt": _excerpt(text)}
    if "no protocols available" in lowered or "no ciphers available" in lowered or "no cipher match" in lowered:
        observed["client_cannot_offer"] = True
        return observed
    if "connection refused" in lowered or "connect:errno" in lowered:
        observed["connect_failed"] = True
        return observed
    cipher = re.search(r"Cipher is (\S+)", text)
    protocol = re.search(r"Protocol\s*:\s*(\S+)", text) or re.search(r"New, (TLSv[\d.]+)", text)
    negotiated = bool(cipher and cipher.group(1) not in ("(NONE)", "0000"))
    refusal = re.search(r"alert (protocol version|handshake failure|insufficient security|illegal parameter)"
                        r"|wrong version number|unsupported protocol|no shared cipher|sslv3 alert", lowered)
    observed.update({
        "refusal_seen": bool(refusal) and not negotiated,
        "negotiated": negotiated,
        "protocol": protocol.group(1) if protocol else None,
        "cipher": cipher.group(1) if cipher else None,
    })
    return observed


def _cipher(text: str) -> str | None:
    """The cipher suite openssl s_client says was agreed, or None."""
    match = re.search(r"(?m)^\s*Cipher\s*:\s*(\S+)", text) or re.search(r"Cipher is (\S+)", text)
    value = match.group(1) if match else None
    return None if value in (None, "(NONE)", "0000") else value


def _excerpt(text: str) -> str:
    keep = [line for line in text.splitlines()
            if re.search(r"alert|error|Protocol|Cipher is|Verify return|New,|no protocols|no cipher", line, re.I)]
    return "\n".join(keep)[:600]


def chain_probe(host: str, port: int, ca: Path, plan_target: dict[str, Any], renew_before: int) -> dict[str, Any]:
    code, text = s_client(host, port, ["-showcerts", "-verify_return_error"], ca)
    observed: dict[str, Any] = {"kind": "chain", "expected_issuer": plan_target.get("expected_issuer"),
                                "renew_before_days": renew_before}
    pems = tlslib.PEM_CERT.findall(text)
    if not pems:
        observed.update({"connect_failed": True, "detail": _excerpt(text) or "no certificate presented"})
        return observed
    info = tlslib.cert_info_from_pem(pems[0])
    verify = re.search(r"Verify return code:\s*(\d+)", text)
    protocol = re.search(r"Protocol\s*:\s*(\S+)", text) or re.search(r"New, (TLSv[\d.]+)", text)
    cipher = _cipher(text)
    names = [str(n) for n in plan_target.get("expected_names") or [host]]
    observed.update({
        "verify_code": verify.group(1) if verify else None,
        "issuer_cn": info["issuer_cn"],
        "subject_cn": info["subject_cn"],
        "protocol": protocol.group(1) if protocol else None,
        "cipher": cipher,
        "san": info["san"],
        "missing_names": [n for n in names if not tlslib.name_covered(n, info["san"])],
        "not_after": info["not_after"],
        "days_left": round(tlslib.days_left(info), 1),
        "fingerprint_sha256": info["fingerprint_sha256"],
    })
    return observed


def probe_identity(cert: Path, key: Path) -> tuple[dict[str, Any], str | None]:
    """What a probe certificate is (SHA-256 fingerprint, validity), and why it
    cannot be sent (None when it can): both files must exist, the certificate
    must be valid now, and the key must belong to it. A probe curl could not
    even load proves nothing about the server."""
    facts: dict[str, Any] = {"file": str(cert), "sha256": None, "not_before": None, "not_after": None}
    redo = "re-run make-probe-certs.sh"
    if not cert.is_file():
        return facts, f"no {cert.name} in {cert.parent}; run make-probe-certs.sh"
    if not key.is_file():
        return facts, f"{key.name} is missing beside {cert.name}, so curl could not offer the certificate; {redo}"
    try:
        info = tlslib.cert_info(cert)
    except (OSError, ValueError) as problem:
        return facts, f"{cert.name} cannot be read ({problem}); {redo}"
    facts.update(sha256=info["fingerprint_sha256"], not_before=info["not_before"], not_after=info["not_after"])
    moment = tlslib.now_utc()
    if tlslib._parse_iso(info["not_before"]) > moment:
        return facts, f"{cert.name} is not valid yet (from {info['not_before']}); {redo}"
    if tlslib.days_left(info, moment) <= 0:
        return facts, f"{cert.name} expired on {info['not_after']}: a refusal of it would prove nothing; {redo}"
    if not tlslib.key_matches_cert(key, cert):
        return facts, f"{key.name} does not belong to {cert.name} (or cannot be read); {redo}"
    return facts, None


def compare_to_baseline(body: str, baseline: dict[str, Any] | None, path: str, ignore: list[str]) -> dict[str, Any]:
    if not baseline or path not in baseline:
        return {}
    expected = baseline[path].get("body")
    try:
        actual = json.loads(body)
    except ValueError:
        return {"body_matches_baseline": body.strip() == str(expected).strip(), "body_difference": "not JSON"}
    if isinstance(expected, dict) and isinstance(actual, dict):
        diffs = [k for k in set(expected) | set(actual) if k not in ignore and expected.get(k) != actual.get(k)]
        return {"body_matches_baseline": not diffs, "body_difference": diffs}
    return {"body_matches_baseline": expected == actual, "body_difference": "values differ" if expected != actual else ""}


def _port(value: Any, what: str) -> int:
    try:
        port = int(str(value))
    except ValueError:
        raise ValueError(f"{what} must be a port number") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"{what} must be a port number")
    return port


def target_problems(plan: dict[str, Any], manifest: dict[str, Any] | None) -> list[str]:
    """Every host the plan would connect to, held to host_problem, before anything is sent."""
    from urllib.parse import urlsplit  # noqa: PLC0415

    environment = (manifest or {}).get("environment") if manifest else plan.get("environment")
    target = plan.get("target") or {}
    problems = []
    wrong = host_problem(target.get("host"), manifest, environment)
    if wrong:
        problems.append(f"target.host: {wrong}")
    health = plan.get("health")
    if isinstance(health, dict) and health.get("url"):
        try:
            health_host = urlsplit(str(health["url"])).hostname or ""
        except ValueError:
            health_host = ""
        wrong = host_problem(health_host, manifest, environment)
        if wrong:
            problems.append(f"health.url: {wrong}")
    return problems


def run_plan(repo: Path, plan: dict[str, Any], manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    """Runs the probes of a plan. Every host is checked first (target_problems):
    a plan that names a host the rule refuses raises ValueError, nothing sent."""
    target = plan.get("target") or {}
    problems = target_problems(plan, manifest)
    if problems:
        raise ValueError("no probe was sent: " + "; ".join(problems))
    host = str(target["host"]).strip().strip("[]")
    https_port = _port(target["https_port"], "target.https_port")
    path = str(target.get("path", "/"))
    if not re.fullmatch(r"/[^\s#]*", path):
        raise ValueError("target.path must start with / and hold no white space or #")
    stage = int(plan.get("stage", 2))
    if not 2 <= stage <= 6:
        raise ValueError("stage must be 2 to 6 (stage 1 changes no behaviour and has nothing to probe)")
    want_status = str(target.get("expected_status", 200))
    ca = _path(repo, target["server_ca"])
    allowed = plan.get("allowed_client") or {}
    client_cert = _path(repo, allowed["cert"], private=True) if allowed.get("cert") else None
    client_key = _path(repo, allowed["key"], private=True) if allowed.get("key") else None
    probe_dir = _path(repo, plan["probe_certs"], private=True) if plan.get("probe_certs") else None
    baseline = None
    if plan.get("baseline") and _path(repo, plan["baseline"]).is_file():
        baseline = json.loads(tlslib.read_regular(_path(repo, plan["baseline"])))
    health = plan.get("health")
    if health:
        # Only a web request is ever made for the health check; check.sh --live also holds its host to in_scope_hosts.
        if not isinstance(health, dict) or not re.match(r"(?i)^https?://[^\s@/]+(?:[/?#]\S*)?$", str(health.get("url") or "")):
            raise ValueError("health.url must be an http:// or https:// URL with a host and no user-info")
    ignore = [str(x) for x in plan.get("baseline_ignore") or []]
    url_host = f"[{host}]" if ":" in host else host
    url = f"https://{url_host}:{https_port}{path}"
    expectations = expected_cases(stage, bool(target.get("http_port")), bool(plan.get("health")))
    cases: list[dict[str, Any]] = []
    # A fresh tag per run, sent with every request and recorded: readiness leaves
    # out only tags it finds recorded, so nobody else's traffic can pass as a probe.
    nonce = secrets.token_hex(4)
    tags: list[str] = []

    def tag(case_id: str) -> str:
        value = (case_id + nonce)[:8]
        if value not in tags:
            tags.append(value)
        return value

    def add(case_id: str, name: str, expected: str, observed: dict[str, Any]) -> None:
        result, detail = judge(expected, observed, {"expected_issuer": target.get("expected_issuer")})
        cases.append({"id": case_id, "name": name, "expected": expected, "observed": observed,
                      "result": result, "detail": detail})

    # Every probe identity is checked before anything is sent (see probe_identity).
    identities: dict[str, dict[str, Any]] = {}
    identity_problems: dict[str, str | None] = {}
    for name in ("probe-untrusted", "probe-unlisted"):
        if probe_dir:
            identities[name], identity_problems[name] = probe_identity(probe_dir / f"{name}.crt", probe_dir / f"{name}.key")
    p1_problem = None
    if client_cert and client_key and client_cert.is_file():
        try:
            p1_is_probe = str(tlslib.cert_info(client_cert).get("subject_cn") or "").startswith("tls-probe-")
        except (OSError, ValueError):
            p1_is_probe = False
        if p1_is_probe:
            # tls-probe-allowed: a probe identity, checked like the others. A real
            # consumer's key is passed to curl by path and never opened.
            identities["probe-allowed"], p1_problem = probe_identity(client_cert, client_key)

    # P1: the allowed consumer, real request.
    if p1_problem:
        p1 = {"kind": "http", "curl_exit": None, "http_status": "", "precondition_failed": p1_problem}
    else:
        p1 = curl(url, ca, client_cert, client_key, tag("P1")) if client_cert and client_key else \
            {"kind": "http", "curl_exit": None, "http_status": "", "detail": "no allowed_client in the plan"}
    if client_cert:
        try:
            p1["client_cert_sha256"] = tlslib.cert_info(client_cert)["fingerprint_sha256"]   # which certificate P1 used
        except (OSError, ValueError):
            p1["client_cert_sha256"] = None
    p1.update(compare_to_baseline(p1.get("body", ""), baseline, path, ignore))
    add("P1", "allowed consumer, correct certificate, real request", f"status:{want_status}", p1)
    service_up = cases[-1]["result"] == "pass"
    gate = None if service_up else "P1 did not pass, so a refusal cannot be told from an outage"

    def refusal(observed: dict[str, Any]) -> dict[str, Any]:
        if gate:
            observed["precondition_failed"] = gate
        return observed

    # P2: no client certificate.
    p2 = _without_body(curl(url, ca, probe_id=tag("P2")))
    if expectations["P2"] == "refused":
        add("P2", "no client certificate", "refused", refusal(p2))
    else:
        add("P2", "no client certificate (allowed before stage 5)", f"status:{want_status}", p2)

    # P3: certificate from the untrusted negative-test CA.
    if not probe_dir:
        p3 = {"kind": "unknown", "precondition_failed": "no probe-untrusted certificate; run make-probe-certs.sh"}
    elif identity_problems.get("probe-untrusted"):
        p3 = {"kind": "unknown", "precondition_failed": identity_problems["probe-untrusted"]}
    else:
        p3 = _without_body(curl(url, ca, probe_dir / "probe-untrusted.crt", probe_dir / "probe-untrusted.key", tag("P3")))
    if probe_dir:
        p3.update(client_cert_sha256=identities["probe-untrusted"]["sha256"],
                  client_cert_not_after=identities["probe-untrusted"]["not_after"])
    add("P3", "certificate from an untrusted CA", "refused", refusal(p3))

    # P4: valid certificate, CN not on the allowlist.
    if expectations["P4"] == "not-applicable":
        add("P4", "valid certificate, CN not on the allowlist", "not-applicable",
            {"kind": "none", "detail": f"the allowlist is enforced from stage 4; this run is at stage {stage}"})
    elif probe_dir and not identity_problems.get("probe-unlisted"):
        p4 = _without_body(curl(url, ca, probe_dir / "probe-unlisted.crt", probe_dir / "probe-unlisted.key", tag("P4")))
        p4.update(client_cert_sha256=identities["probe-unlisted"]["sha256"],
                  client_cert_not_after=identities["probe-unlisted"]["not_after"])
        add("P4", "valid certificate, CN not on the allowlist", "status:403", p4)
    else:
        problem = identity_problems.get("probe-unlisted") or "no probe-unlisted certificate; run make-probe-certs.sh"
        add("P4", "valid certificate, CN not on the allowlist", "status:403",
            {"kind": "http", "curl_exit": None, "http_status": "", "detail": problem, "precondition_failed": problem})

    # P5, P6: old protocols and weak ciphers.
    p5 = protocol_probe(host, https_port, ["-tls1_1", "-cipher", "DEFAULT:@SECLEVEL=0"])
    p5_10 = protocol_probe(host, https_port, ["-tls1", "-cipher", "DEFAULT:@SECLEVEL=0"])
    if p5.get("negotiated") or p5_10.get("negotiated"):
        p5 = p5 if p5.get("negotiated") else p5_10
    elif p5.get("client_cannot_offer") and not p5_10.get("client_cannot_offer"):
        p5 = p5_10
    add("P5", "TLS 1.0 and 1.1 offered", "protocol-refused", refusal(p5))
    p6 = protocol_probe(host, https_port, ["-tls1_2", "-cipher", "NULL:eNULL:aNULL:EXPORT:RC4:DES:3DES:MD5:@SECLEVEL=0"])
    add("P6", "weak cipher suites offered", "protocol-refused", refusal(p6))

    # P7: the legacy plain HTTP port.
    # At stage 6 every port plain HTTP was ever served on is tried (target.http_ports:
    # the manifest's port and the ports the discovery step recorded).
    if target.get("http_port"):
        p7 = _without_body(curl(f"http://{url_host}:{_port(target['http_port'], 'target.http_port')}{path}", None,
                                probe_id=tag("P7")))
        if expectations["P7"] == "closed":
            ports = {str(int(target["http_port"])): {"curl_exit": p7["curl_exit"], "http_status": p7["http_status"]}}
            for extra in target.get("http_ports") or []:
                if str(int(extra)) not in ports:
                    seen = curl(f"http://{url_host}:{_port(extra, 'a legacy port')}{path}", None, probe_id=tag("P7"))
                    ports[str(int(extra))] = {"curl_exit": seen["curl_exit"], "http_status": seen["http_status"]}
            p7["ports"] = ports
        add("P7", "plain HTTP port", expectations["P7"], p7)

    # P9: what the server presents.
    add("P9", "presented chain, protocol and names", "chain-ok",
        chain_probe(host, https_port, ca, target, int(plan.get("renew_before_days", 21))))

    # P10: platform health probes, without a client certificate.
    if health:
        statuses = []
        for attempt in range(int(health.get("attempts", 3))):
            if attempt:
                time.sleep(float(health.get("interval_seconds", 2)))
            statuses.append(curl(str(health["url"]), ca if str(health["url"]).lower().startswith("https") else None,
                                     probe_id=tag("P10"))["http_status"])
        add("P10", "health probes without a client certificate", "healthy", {"kind": "health", "statuses": statuses})

    counts = {k: sum(1 for c in cases if c["result"] == k) for k in ("pass", "fail", "not run", "not applicable")}
    return {
        "tool": "probe_tls.py",
        "generated_at": tlslib.iso(tlslib.now_utc()),
        "environment": plan.get("environment"),
        "stage": stage,
        "target": {"host": host, "https_port": https_port, "http_port": target.get("http_port"), "path": path},
        "probe_tags": tags,
        # Which probe certificates were checked, by SHA-256 fingerprint and end date.
        "probe_certificates": {name: {"sha256": facts["sha256"], "not_after": facts["not_after"]}
                               for name, facts in identities.items()},
        "expected_case_ids": sorted(expectations),
        "cases": cases,
        "summary": counts,
        "failures": counts["fail"],
    }


# ---------------------------------------------------------------- server only (W1)
# An HTTPS endpoint that asks for no client certificate (a third party with a
# public CA, say): certificate and host name checked, TLS 1.2 or later, no
# client certificate. A consumer-side row with client_certificate: none.

SERVER_ONLY_FOLDER = "tls-migration/evidence/server-only"
_ENDPOINT = re.compile(r"\[([0-9A-Fa-f:.]+)\]:(\d{1,5})|([A-Za-z0-9.\-]+):(\d{1,5})")


def parse_endpoint(value: Any) -> tuple[str, int] | None:
    """host:port ([v6 address]:port) as (host, port), or None when it cannot be read."""
    match = _ENDPOINT.fullmatch(str(value or "").strip())
    if not match:
        return None
    host = (match.group(1) or match.group(3)).lower().rstrip(".")
    port = int(match.group(2) or match.group(4))
    return (host, port) if 1 <= port <= 65535 else None


def server_only_file(host: str, port: int) -> str:
    """Where probe-tls.sh --server-only writes its evidence, repository-relative."""
    return f"{SERVER_ONLY_FOLDER}/{re.sub(r'[^a-z0-9.-]', '-', host.lower())}_{int(port)}.json"


def server_only_probe(host: str, port: int, ca: Path | None = None, path: str = "/") -> dict[str, Any]:
    """One HTTPS request with certificate and host name checking on, no client
    certificate, TLS 1.2 or later (curl: the verdict and the timing), and what the
    server presented (openssl s_client: protocol, cipher, certificate). The
    caller has already held the host to host_problem."""
    url_host = f"[{host}]" if ":" in host else host
    cmd = ["curl", "-q", "-sS", "--max-time", "10", "--proto", "=https", "--proto-redir", "=https", "--max-redirs", "0",
           "--tlsv1.2", "-o", os.devnull, "-w", CURL_WRITE_OUT]
    if ca:
        cmd += ["--cacert", str(ca)]
    cmd.append(f"https://{url_host}:{int(port)}{path}")
    code, out, err = tlslib.run(cmd, timeout=20)
    status, timing = _write_out(out)
    observed: dict[str, Any] = {"kind": "server-only", "target": f"{url_host}:{int(port)}", "curl_exit": code,
                                "http_status": status, "stderr": tlslib.mask_secrets(err.strip()[:300]), **timing}
    extra = ["-showcerts", "-no_ssl3", "-no_tls1", "-no_tls1_1"] + name_check_flags(host)
    _, text = s_client(host, int(port), extra, ca)
    pems = tlslib.PEM_CERT.findall(text)
    protocol = re.search(r"Protocol\s*:\s*(\S+)", text) or re.search(r"New, (TLSv[\d.]+)", text)
    verify = re.search(r"Verify return code:\s*(\d+)", text)
    observed.update(protocol=protocol.group(1) if protocol else None, cipher=_cipher(text),
                    openssl_verify_code=verify.group(1) if verify else None)
    if pems:
        info = tlslib.cert_info_from_pem(pems[0])
        observed["certificate"] = {key: info.get(key) for key in ("subject", "issuer", "subject_cn", "issuer_cn",
                                                                  "not_after", "san", "fingerprint_sha256")}
    return observed


def judge_server_only(observed: dict[str, Any], host: str, moment: Any = None) -> tuple[str, str]:
    """pass, fail or not run for a server-only probe, from what was observed: the
    same function judges a live run and re-judges a recorded file in check.sh."""
    exit_code = observed.get("curl_exit")
    status = str(observed.get("http_status") or "")
    if exit_code in (6, 7, 28):
        return "not run", f"curl exit {exit_code}: {CURL_LOCAL_FAILURES[exit_code]}; nothing about TLS was shown"
    if exit_code != 0 or not re.fullmatch(r"[1-5]\d\d", status):
        reason = {35: "the TLS handshake failed (no TLS 1.2 or later, or the server wants a client certificate)",
                  51: "the certificate is not valid for the host name", 60: "the certificate did not verify",
                  56: "the connection was reset after the handshake (the server may want a client certificate)",
                  77: "the CA file could not be read"}.get(exit_code, "no verified HTTPS answer")
        return "fail", f"curl exit {exit_code}: {reason}"
    if observed.get("protocol") not in ("TLSv1.2", "TLSv1.3"):
        return "fail", f"protocol {observed.get('protocol')}: TLS 1.2 or later is required"
    cert = observed.get("certificate") if isinstance(observed.get("certificate"), dict) else None
    if not cert or not cert.get("not_after"):
        return "fail", "no certificate was recorded"
    try:
        left = tlslib.days_left(cert, moment)
    except (TypeError, ValueError):
        return "fail", "the certificate's end date cannot be read"
    if left <= 0:
        return "fail", f"the certificate expired on {cert['not_after']}"
    if not tlslib.name_covered(str(host), cert.get("san") or {}):
        return "fail", f"the certificate does not name {host}"
    return "pass", f"{observed.get('protocol')}, {observed.get('cipher')}, issuer {cert.get('issuer_cn')}, HTTP {status}"


def run_server_only(repo: Path, endpoint: str, manifest: dict[str, Any] | None, ca: Path | None = None) -> dict[str, Any]:
    """The evidence for one server-only endpoint. The host is held to the target rule
    (host_problem) first: a refused one raises ValueError and nothing is sent."""
    parsed = parse_endpoint(endpoint)
    if parsed is None:
        raise ValueError(f"--server-only {str(endpoint)[:60]!r} is not host:port")
    host, port = parsed
    environment = (manifest or {}).get("environment")
    wrong = host_problem(host, manifest, environment)
    if wrong:
        raise ValueError(f"no probe was sent: {wrong}")
    observed = server_only_probe(host, port, ca)
    result, detail = judge_server_only(observed, host)
    cert = observed.get("certificate") or {}
    return {
        "tool": "probe_tls.py --server-only",
        "generated_at": tlslib.iso(tlslib.now_utc()),
        "environment": environment,
        "target": f"{host}:{port}",
        "protocol": observed.get("protocol"),
        "cipher": observed.get("cipher"),
        "certificate": {key: cert.get(key) for key in ("subject", "issuer", "not_after")},
        "verify": {"ok": observed.get("curl_exit") == 0, "curl_exit": observed.get("curl_exit"),
                   "openssl_verify_code": observed.get("openssl_verify_code")},
        "total_ms": observed.get("total_ms"),
        "handshake_ms": observed.get("handshake_ms"),
        "ca": tlslib.shown_path(ca, repo) if ca else "the system trust store",
        "observed": observed,
        "result": result,
        "detail": detail,
    }


def record_tags(folder: Path, result: dict[str, Any], name: str = "probe-tags.log", repo: Path | None = None) -> None:
    """Appends this run's request tags to probe-tags.log in the evidence folder
    (or to another file: check.sh --live --tags-file). readiness.py leaves out
    log lines with a recorded tag and counts every other tagged line against
    the migration."""
    tags = result.get("probe_tags") or []
    if not tags:
        return
    try:
        target = tlslib.check_write_target(folder / name, repo)
        tlslib.safe_mkdir(folder, repo)
        if os.path.lexists(target) and not target.is_file():
            raise OSError(f"{target} is not a regular file")
        handle = os.open(target, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o644)
        with os.fdopen(handle, "a", encoding="utf-8") as stream:
            stream.write(f"{result.get('generated_at')} {' '.join(tags)}\n")
    except OSError as problem:
        print(f"note: could not record the probe tags ({problem}); readiness will count these probes as traffic", file=sys.stderr)


def record_baseline(urls: list[str], out: str) -> int:
    """The behaviour before the migration. The URLs come from the person running
    this (the command line), never from a repository file; http and https only."""
    result = {}
    for url in urls:
        if not re.match(r"(?i)^https?://[^\s@/]+(?:[/?#]\S*)?$", url):
            print(f"refused: {url[:80]} is not an http:// or https:// URL with a host and no user-info", file=sys.stderr)
            return 2
        observed = curl(url, None)
        try:
            body: Any = json.loads(observed["body"])
        except ValueError:
            body = observed["body"]
        path = "/" + url.split("://", 1)[1].split("/", 1)[1] if "/" in url.split("://", 1)[1] else "/"
        result[path] = {"url": url, "status": observed["http_status"], "body": body,
                        **{key: observed[key] for key in ("total_ms", "handshake_ms") if key in observed}}
        print(f"{tlslib.mask_secrets(url)}: HTTP {observed['http_status']}, {observed.get('total_ms')} ms")
    tlslib.write_json(out, result)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--plan")
    parser.add_argument("--manifest", default="tls-migration/tls-services.yaml")
    parser.add_argument("--out")
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--server-only", metavar="HOST:PORT",
                        help="an HTTPS endpoint that asks for no client certificate; writes " + SERVER_ONLY_FOLDER + "/<host>_<port>.json")
    parser.add_argument("--ca", help="with --server-only: the CA file to verify against (default: the system trust store)")
    args = parser.parse_args()
    if args.server_only:
        return main_server_only(args)
    if not args.out:
        parser.error("--out is required")
    if args.baseline:
        if not args.url:
            parser.error("--baseline needs at least one --url")
        return record_baseline(args.url, args.out)
    if not args.plan:
        parser.error("--plan is required")
    repo = Path(args.repo).resolve()
    # --plan, --manifest and --out come from the person running this: taken as given.
    plan_path = Path(args.plan) if Path(args.plan).is_absolute() else repo / args.plan
    try:
        plan = tlslib.load_yaml(plan_path) or {}
    except (OSError, ValueError) as problem:
        print(f"cannot read the probe plan: {problem}", file=sys.stderr)
        return 2
    if not isinstance(plan, dict):
        print("the probe plan is not a mapping", file=sys.stderr)
        return 2
    manifest_path = Path(args.manifest) if Path(args.manifest).is_absolute() else repo / args.manifest
    manifest = (tlslib.load_yaml(manifest_path) or {}) if manifest_path.is_file() else {}
    target = plan.get("target") or {}
    if int(plan.get("stage", 0)) >= 6:
        import check_gate  # noqa: PLC0415 - only to read the producer's legacy ports the way the gate does

        ports = check_gate.legacy_ports(repo, manifest) if manifest else ["8080"]
        if not target.get("http_port"):
            target = dict(target, http_port=int(ports[0]))
            print(f"note: stage 6 always probes plain HTTP (P7); using port {ports[0]}", file=sys.stderr)
        # Every port plain HTTP was served on: the manifest's and the ones discovery recorded.
        plan["target"] = dict(target, http_ports=sorted({int(p) for p in ports} | {int(target["http_port"])}))
    try:
        result = run_plan(repo, plan, manifest or None)
    except (KeyError, ValueError) as problem:
        print(f"bad probe plan: {problem}", file=sys.stderr)
        return 2
    result["plan"] = tlslib.shown_path(plan_path, repo)
    record_tags(Path(args.out).parent, result, repo=repo)
    if manifest:
        result["bound_inputs"] = bound_inputs(repo, manifest)
    else:
        print("note: no manifest found, so these probes are not bound to the config; check.sh will refuse them",
              file=sys.stderr)
    tlslib.write_json(args.out, result, repo)
    for case in result["cases"]:
        print(tlslib.mask_secrets(f"{case['id']:<4} {case['result']:<15} {case['name']}: {case['detail']}"))
    print(f"summary: {result['summary']}")
    return 0 if result["failures"] == 0 else 1


def main_server_only(args: argparse.Namespace) -> int:
    """probe_tls.py --server-only host:port: the evidence file E6 reads for a
    consumer-side row with client_certificate: none."""
    repo = Path(args.repo).resolve()
    manifest_path = Path(args.manifest) if Path(args.manifest).is_absolute() else repo / args.manifest
    manifest = (tlslib.load_yaml(manifest_path) or {}) if manifest_path.is_file() else {}
    if not manifest:
        print("refused: --server-only needs the manifest (its in_scope_hosts say where a probe may connect)", file=sys.stderr)
        return 2
    ca = Path(os.path.expanduser(args.ca)) if args.ca else None
    if ca is not None and not ca.is_absolute():
        ca = repo / ca
    try:
        result = run_server_only(repo, args.server_only, manifest, ca)
    except ValueError as problem:
        print(f"refused: {problem}", file=sys.stderr)
        return 2
    host, port = parse_endpoint(args.server_only) or ("", 0)
    out = repo / server_only_file(host, port)
    tlslib.write_json(out, result, repo)
    timing = ", ".join(f"{name} {result[key]} ms" for name, key in (("total", "total_ms"), ("handshake", "handshake_ms"))
                       if result.get(key) is not None) or "no timing: the connection did not complete"
    print(tlslib.mask_secrets(f"{result['target']}: {result['result']}: {result['detail']} ({timing})"))
    print(f"written: {tlslib.shown_path(out, repo)}")
    if ca is not None and manifest.get("environment") != "local":
        print(f"note: --ca was used for this probe only. Outside local, check.sh does not count this file and does not "
              f"use a CA from the repository: check.sh --live re-checks {host}:{port} against the system's trusted CAs",
              file=sys.stderr)
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except tlslib.UnsafeWrite as refused:   # a link or a path out of the repository (D2): nothing written
        print(f"refused: {refused}", file=sys.stderr)
        sys.exit(2)
