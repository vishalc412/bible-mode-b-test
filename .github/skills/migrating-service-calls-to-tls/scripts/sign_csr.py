"""Signs a consumer's certificate request with a producer's consumer CA.

usage: sign_csr.py --env local|test --producer <p> --csr <file> --allowlist <allowed-consumers.yaml>
                   --out <dir> [--days N] [--name <file name>]

The request is untrusted input. It is refused when:
  - its self-signature does not verify;
  - it asks for CA:TRUE, for extra names, or for any usage besides client authentication;
  - it does not carry exactly one CN, or the CN is not a consumer id in the allowlist;
  - its key is not EC P-256/P-384 or RSA 2048+;
  - its subject carries anything besides the CN;
  - the allowlist is another producer's (its "producer:" line must equal --producer);
  - the CN starts with tls-probe-: the probe identities (tls-probe-allowed,
    tls-probe-unlisted, tls-probe-untrusted) are issued by make-probe-certs.sh
    only, even when one is on the allowlist.
Whatever extensions the request asks for are dropped. The script sets the
subject (CN=<id>), CA:FALSE, digitalSignature, clientAuth only, a URI name
spiffe://<trust-domain>/consumer/<id>, and the lifetime.

The lifetime (default 30 days in local, 90 in test) never runs past the CA's
own end date.

The consumer CA key is handed to openssl by path; this script never opens it.
Writes <out>/<producer>-<id>.crt (or <out>/<name> with --name) and prints its
metadata. The file appears only when signing worked. Give each consumer its
own --out folder (e.g. tls-migration/signed/<consumer>): a fixed --name in a
shared folder overwrites the previous consumer's certificate.
For a consumer's first certificate the name in its kit is client.crt; for a
renewal it is client.crt.next, never client.crt, which the service is still
using until make-csr.sh --activate swaps the new pair in.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tlslib  # noqa: E402

ID_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
TRUST_DOMAIN = re.compile(r"[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*")


PROBE_PREFIX = "tls-probe-"


def allowed_ids(allowlist_path: str, producer: str) -> tuple[set[str], str]:
    data = tlslib.load_yaml(allowlist_path) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"refused: {allowlist_path} is not an allowlist")
    listed_for = str(data.get("producer") or "")
    if listed_for != producer:
        raise SystemExit(
            f"refused: {allowlist_path} is the allowlist of producer '{listed_for or '(none named)'}', not of '{producer}'. "
            "Sign with the producer's own allowlist (its first line is 'producer: <name>')."
        )
    consumers = data.get("consumers") or []
    ids = set()
    for entry in consumers:
        if isinstance(entry, dict) and entry.get("id"):
            ids.add(str(entry["id"]))
    trust_domain = str(data.get("trust_domain") or "tls-migration.invalid")
    # Written into the certificate's extension file: anything but a host name
    # could smuggle extra names (",DNS:...") into the certificate.
    if not TRUST_DOMAIN.fullmatch(trust_domain):
        raise SystemExit(f"refused: trust_domain {trust_domain!r} in {allowlist_path} is not a plain host name")
    return ids, trust_domain


def inspect_request(csr_path: str) -> dict:
    code, text, err = tlslib.run(
        ["openssl", "req", "-in", csr_path, "-noout", "-text", "-verify", "-nameopt", "RFC2253"]
    )
    verified = "verify OK" in (text + err) or "self-signature ok" in (text + err)
    if code != 0 or not verified:
        raise SystemExit(f"refused: the request's self-signature does not verify ({err.strip()})")
    subject_match = re.search(r"^\s*Subject:\s*(.*)$", text, re.M)
    subject = subject_match.group(1).strip() if subject_match else ""
    parts = [p.strip() for p in re.split(r"(?<!\\),", subject) if p.strip()]
    if len(parts) != 1 or not parts[0].upper().startswith("CN="):
        raise SystemExit(f"refused: the subject must be exactly CN=<consumer id>; got '{subject}'")
    if "id-ecPublicKey" in text:
        curve = re.search(r"NIST CURVE:\s*(\S+)|ASN1 OID:\s*(\S+)", text)
        name = (curve.group(1) or curve.group(2)) if curve else "unknown"
        key_type = "EC " + {"prime256v1": "P-256", "secp384r1": "P-384"}.get(name, name)
    elif "rsaEncryption" in text:
        bits = re.search(r"Public-Key:\s*\((\d+) bit\b", text)
        key_type = f"RSA {bits.group(1) if bits else '?'}"
    else:
        key_type = "unknown"
    requested = re.findall(r"^\s*(X509v3 [^:]+):", text, re.M)
    # A request that asks to be a CA, to carry extra names or to serve TLS is
    # not a mistake to quietly correct: it is refused, so a person looks at it.
    if re.search(r"CA:TRUE", text):
        raise SystemExit("refused: the request asks for CA:TRUE")
    if "X509v3 Subject Alternative Name" in text:
        raise SystemExit("refused: the request asks for extra names (subjectAltName); the script sets the only name")
    eku = re.search(r"X509v3 Extended Key Usage:(?: critical)?\s*\n\s*(.+?)\n", text)
    if eku and eku.group(1).strip() != "TLS Web Client Authentication":
        raise SystemExit(f"refused: the request asks for usage '{eku.group(1).strip()}'; only client authentication is issued")
    return {"cn": parts[0][3:], "key_type": key_type, "requested_extensions": requested}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env", required=True, choices=["local", "test", "staging", "production"])
    parser.add_argument("--producer", required=True)
    parser.add_argument("--csr", required=True)
    parser.add_argument("--allowlist", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--days", type=int)
    parser.add_argument("--name", help="file name to write in --out; default <producer>-<consumer>.crt")
    args = parser.parse_args()

    if args.env not in ("local", "test"):
        raise SystemExit(
            f"refused: {args.env} requests are signed by the company CA, Vault or cert-manager, "
            "never on this machine. Attach the request to the signing ticket instead."
        )
    if not ID_PATTERN.match(args.producer):
        raise SystemExit("refused: producer name must be lowercase letters, digits and hyphens")
    # 0 or a negative number is refused, never read as "the default".
    days = args.days if args.days is not None else (30 if args.env == "local" else 90)
    if not 1 <= days <= 90:
        raise SystemExit("refused: --days must be 1 to 90")

    if args.name and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", args.name):
        raise SystemExit("refused: --name must be a plain file name")
    ids, trust_domain = allowed_ids(args.allowlist, args.producer)
    request = inspect_request(args.csr)
    consumer = request["cn"]
    if not ID_PATTERN.match(consumer):
        raise SystemExit(f"refused: '{consumer}' is not a valid consumer id")
    # A probe identity signed here could pass for the probe (or, for
    # tls-probe-allowed, be handed to a workload): only make-probe-certs.sh
    # issues them, into the probe folder.
    if consumer.startswith(PROBE_PREFIX):
        raise SystemExit(f"refused: {consumer} is a probe identity; only make-probe-certs.sh issues tls-probe-* certificates")
    if consumer not in ids:
        raise SystemExit(
            f"refused: '{consumer}' is not in {args.allowlist}. Add the consumer there first "
            "(with its owner, contact and cadence), then sign."
        )
    if not tlslib.key_allowed(request["key_type"]):
        raise SystemExit(f"refused: key type {request['key_type']} is not allowed (EC P-256 or RSA 2048+)")
    if request["requested_extensions"]:
        print(
            "note: the request asked for " + ", ".join(sorted(set(request["requested_extensions"])))
            + "; dropped. The script sets the extensions.",
            file=sys.stderr,
        )

    if not os.environ.get("TLS_PRIVATE_DIR"):
        raise SystemExit("refused: set TLS_PRIVATE_DIR to this project's key folder (the one certgen-test-ca.sh used)")
    private_dir = Path(os.environ["TLS_PRIVATE_DIR"])
    ca_key = private_dir / f"ca-{args.env}" / f"{args.producer}-consumers-ca.key"
    ca_crt = private_dir / f"ca-{args.env}" / f"{args.producer}-consumers-ca.crt"
    if not ca_key.exists() or not ca_crt.exists():
        raise SystemExit(f"refused: no {args.env} consumer CA for {args.producer}; run certgen-test-ca.sh --env {args.env} first")
    # A leaf never outlives its CA.
    ca_left = tlslib.leaf_days_within(tlslib.cert_info(ca_crt))
    if ca_left < 1:
        raise SystemExit(f"refused: the {args.env} consumer CA for {args.producer} has expired or ends within a day; run certgen-test-ca.sh first")
    if days > ca_left:
        print(f"note: lifetime cut from {days} to {ca_left} days: the CA ends then", file=sys.stderr)
        days = ca_left

    out_dir = Path(args.out)
    certificate = out_dir / (args.name or f"{args.producer}-{consumer}.crt")
    pending = certificate.with_name(certificate.name + ".new")
    try:
        # Never written through a symbolic link, never out of the repository (D2).
        for target in (certificate, pending):
            tlslib.check_write_target(target)
    except tlslib.UnsafeWrite as problem:
        raise SystemExit(f"refused: {problem}") from problem
    if not out_dir.exists():
        # A certificate is public: a new --out folder is readable by others (0755),
        # whatever the caller's umask; an existing one keeps its mode.
        previous_umask = os.umask(0o022)
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        finally:
            os.umask(previous_umask)
    for target in (certificate, pending):
        tlslib.check_write_target(target)
    if os.path.lexists(pending):
        pending.unlink()
    with tempfile.NamedTemporaryFile("w", suffix=".ext", delete=False) as ext:
        ext.write(
            "basicConstraints=critical,CA:FALSE\n"
            "keyUsage=critical,digitalSignature\n"
            "extendedKeyUsage=clientAuth\n"
            f"subjectAltName=URI:spiffe://{trust_domain}/consumer/{consumer}\n"
            # Explicit: OpenSSL 4 no longer adds key identifiers by default.
            "subjectKeyIdentifier=hash\n"
            "authorityKeyIdentifier=keyid,issuer\n"
        )
        ext_path = ext.name
    try:
        # x509 -req never copies request extensions unless told to; -subj replaces the subject.
        code, _, err = tlslib.run([
            "openssl", "x509", "-req", "-in", args.csr, "-CA", str(ca_crt), "-CAkey", str(ca_key),
            "-CAcreateserial", "-subj", f"/CN={consumer}", "-days", str(days), "-sha256",
            "-extfile", ext_path, "-out", str(pending),
        ])
    finally:
        os.unlink(ext_path)
    if code != 0:
        pending.unlink(missing_ok=True)
        raise SystemExit(f"signing failed: {err.strip()}")
    os.chmod(pending, 0o644)
    info = tlslib.cert_info(pending)
    if info["is_ca"] or info["extended_key_usage"] != ["clientAuth"]:
        pending.unlink()
        raise SystemExit("internal check failed: the signed certificate is not a client-only leaf; removed")
    os.replace(pending, certificate)
    print(
        f"signed: {certificate} subject=CN={consumer} issuer={info['issuer_cn']} "
        f"usage=clientAuth expires={info['not_after']} sha256={info['fingerprint_sha256']}"
    )
    print(f"send back: {certificate.name} to {consumer}. A first certificate is saved as client.crt in the kit folder. "
          "A renewal is saved as client.crt.next (never over client.crt, which is still in use), then "
          "./make-csr.sh --activate --cert client.crt.next swaps key and certificate together. "
          "(The kit already holds the server CA as ca-bundle.pem.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
