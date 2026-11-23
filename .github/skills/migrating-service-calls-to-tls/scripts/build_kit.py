"""Builds a consumer kit for one consumer of a producer.

usage: build_kit.py --producer <p> --consumer <id> --endpoint <https url> --names <a,b,...>
                    --server-ca <server-ca.crt> --consumer-ca <producer-consumers-ca.crt> --out <kits folder>
                    [--env local|test|staging|production] [--client-cert <certificate>] [--bundle <p12>]
                    [--cutover <date>] [--contact <text>] [--lifetime-days N]
                    [--previous-server-ca <server-ca.previous.crt>]

Writes <out>/kit-<producer>-for-<consumer>/ with README.md, endpoint.txt,
ca-bundle.pem (the server CA: what the consumer trusts), consumer-ca.crt (the
CA that signs the consumer's certificate, public, so the consumer can check
its own chain), make-csr.sh with _key_folder.sh (the key folder checks it
sources), make-csr.ps1, verify.sh, snippets/, SHA256SUMS (the SHA-256 of every
other kit file but KIT-MANIFEST.json, in the form `shasum -a 256 -c` reads) and
KIT-MANIFEST.json (SHA-256 of every file, and the kit fingerprint).

Prints the SHA-256 of ca-bundle.pem and the kit fingerprint (the SHA-256 of
SHA256SUMS). Both must reach the consumer over a different channel from the
kit: the kit's README has the consumer check the fingerprint and every file
before any script in the kit runs. verify.sh runs only when ca-bundle.pem holds
exactly one certificate and nothing else, and the value it is given equals
the SHA-256 of the whole file or that certificate's own SHA-256 fingerprint
(during a rotation overlap: the two CAs below, and the whole-file SHA-256 only).

--server-ca must hold exactly one CA certificate: a kit trusts one CA, and
check.sh (E9) fails a kit that holds more. During a server CA rotation the
trust file certgen-test-ca.sh writes holds two; build the kit from
<out>/server-ca.current.crt (the new CA alone) and add
--previous-server-ca <out>/server-ca.previous.crt: the kit's ca-bundle.pem then
holds exactly those two (new first), both CAs with the same name, so the
consumer trusts the leaf the old CA signed and the one the new CA will sign.
verify.sh accepts a two-certificate ca-bundle.pem only in that form, and only
given the SHA-256 of the whole file. See certificates.md, "CA rotation".

--server-ca must be a CA that may sign server certificates: one restricted
to client authentication (a consumer CA, the negative-test CA) is refused. A
throwaway CA (local-dev-* or test-*, made by certgen-test-ca.sh) is refused
for any --env but its own, for --server-ca and --consumer-ca alike.

--lifetime-days is what the kit's README tells the consumer; default 30 in
local and for a route B bundle (which never lives longer), 90 elsewhere.

--endpoint is copied into shell and code snippets, so it is checked: https,
a host name or address, an optional port, a plain path and query, nothing else.

--env keeps the consumer's key for this environment apart from its keys for
others (the key path becomes <env>/<producer>/<consumer>).

--bundle is route B (a ready-made PKCS12): only where the policy allows it.
It must be a PKCS12 file (anything else is refused before the kit is
written). The bundle holds a key, so it is never copied into the kit: the manifest
records its SHA-256, route "B" and key_travelled true, and a person delivers
the bundle and its password over two other channels. The README then carries
the route B steps.
"""
from __future__ import annotations

import argparse
import ipaddress
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_rules  # noqa: E402
import tlslib  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "kit-template"
ID_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
REQUIRED = ["README.md", "endpoint.txt", "ca-bundle.pem", "consumer-ca.crt", "make-csr.sh", "_key_folder.sh", "make-csr.ps1", "verify.sh",
            "snippets/spring.yml", "snippets/node.js", "snippets/python.py", "snippets/go.go",
            "snippets/dotnet.cs", "snippets/curl.sh", "SHA256SUMS"]
# SHA256SUMS lists every kit file but itself and KIT-MANIFEST.json (which records
# the SHA-256 of SHA256SUMS, so it cannot be listed in it), in the format
# `shasum -a 256 -c SHA256SUMS` reads. Its own SHA-256 is the kit fingerprint.
SUMS = "SHA256SUMS"
NOT_SUMMED = {SUMS, "KIT-MANIFEST.json"}


def sums_text(kit: Path) -> str:
    """The SHA256SUMS of a kit folder: '<sha256>  <relative name>' per file, sorted."""
    names = sorted(p.relative_to(kit).as_posix() for p in kit.rglob("*") if p.is_file() and not p.is_symlink())
    return "".join(f"{tlslib.sha256_file(kit / name)}  {name}\n" for name in names if name not in NOT_SUMMED)


def kit_fingerprint(kit: Path) -> str:
    """The kit fingerprint: the SHA-256 of its SHA256SUMS file."""
    return tlslib.sha256_file(kit / SUMS)
BLOCK = re.compile(r"\{\{#([A-Z_]+)\}\}\n?(.*?)\{\{/\1\}\}\n?", re.S)


def fill(text: str, values: dict[str, str], flags: dict[str, bool]) -> str:
    """Keeps {{#NAME}}...{{/NAME}} blocks whose flag is set, then fills {{NAME}} values."""
    text = BLOCK.sub(lambda m: m.group(2) if flags.get(m.group(1)) else "", text)
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def is_host(name: str, wildcard: bool = False) -> bool:
    try:
        ipaddress.ip_address(name)
        return True
    except ValueError:
        pass
    labels = name.lower().split(".")
    if wildcard and labels[0] == "*" and len(labels) >= 3:
        labels = labels[1:]
    return len(name) <= 253 and all(LABEL.match(label) for label in labels)


def checked_endpoint(endpoint: str) -> str:
    """Returns scheme://host[:port]; exits when the URL holds anything a snippet could trip over."""
    problem = None
    # urlsplit silently drops tabs and line breaks; the raw text is what lands in the snippets.
    if not endpoint.isascii() or re.search(r"[\x00-\x20\x7f]", endpoint):
        raise SystemExit("the endpoint is refused: it holds a space, a control character or a non-ASCII character. "
                         "It is copied into shell and code snippets, so it must be plain.")
    try:
        parts = urlsplit(endpoint)
        port = parts.port
    except ValueError as error:
        raise SystemExit(f"the endpoint is not a usable URL: {error}") from error
    host = parts.hostname or ""
    if parts.scheme != "https":
        problem = "it must be an https:// URL"
    elif parts.username is not None or parts.password is not None or "@" in parts.netloc:
        problem = "it must not carry a user name or password"
    elif not host or not is_host(host):
        problem = f"'{host}' is not a host name or an IP address"
    elif port is not None and not 1 <= port <= 65535:
        problem = "the port is out of range"
    elif parts.fragment:
        problem = "it must not carry a #fragment"
    elif not re.fullmatch(r"[A-Za-z0-9._~/%:@+,=&-]*", parts.path) or not re.fullmatch(r"[A-Za-z0-9._~/%:@+,=&?-]*", parts.query):
        problem = "the path and query may hold only letters, digits and . _ ~ / % : @ + , = & - (percent-encode anything else)"
    elif not re.fullmatch(r"[A-Za-z0-9.\-:\[\]]+", parts.netloc):
        problem = "the host part holds characters that are not allowed"
    if problem:
        raise SystemExit(f"the endpoint is refused: {problem}. It is copied into shell and code snippets, so it must be plain.")
    return f"https://{parts.netloc}"


# certgen-test-ca.sh names its CAs with these prefixes, one per environment.
THROWAWAY_PREFIXES = {"local-dev-": "local", "test-": "test"}
PKCS12_DATA_OID = bytes.fromhex("06092a864886f70d010701")   # 1.2.840.113549.1.7.1, the PFX's authSafe


def throwaway_env(common_name: str) -> str | None:
    return next((env for prefix, env in THROWAWAY_PREFIXES.items() if common_name.startswith(prefix)), None)


def is_pkcs12(path: str) -> bool:
    """A DER PFX: SEQUENCE { INTEGER 3, ContentInfo of type data, ... }. Read only, never decrypted."""
    try:
        data = Path(path).read_bytes()
    except OSError:
        return False
    if len(data) < 16 or data[0] != 0x30:
        return False
    length_byte = data[1]
    offset = 2 + (length_byte & 0x7F if length_byte & 0x80 else 0)
    return data[offset:offset + 3] == b"\x02\x01\x03" and PKCS12_DATA_OID in data[offset + 3:offset + 40]


def one_line(value: str, label: str) -> str:
    if re.search(r"[\x00-\x1f\x7f]", value):
        raise SystemExit(f"{label} must be one line of plain text")
    return value.replace("|", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--producer", required=True)
    parser.add_argument("--consumer", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--names", required=True)
    parser.add_argument("--server-ca", required=True)
    parser.add_argument("--consumer-ca", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--env", choices=["local", "test", "staging", "production"])
    parser.add_argument("--client-cert")
    parser.add_argument("--bundle")
    parser.add_argument("--cutover", default="not set yet")
    parser.add_argument("--contact", default="the producer team")
    parser.add_argument("--lifetime-days", help="default 30 in local and for a --bundle, 90 elsewhere")
    parser.add_argument("--previous-server-ca", help="during a server CA rotation: server-ca.previous.crt, trusted beside the new CA")
    args = parser.parse_args()

    for value, label in ((args.producer, "producer"), (args.consumer, "consumer")):
        if not ID_PATTERN.match(value):
            raise SystemExit(f"{label} must be lowercase letters, digits and hyphens")
    base = checked_endpoint(args.endpoint)
    names = [n.strip() for n in args.names.split(",") if n.strip()]
    bad_names = [n for n in names if not is_host(n, wildcard=True)]
    if not names or bad_names:
        raise SystemExit(f"--names must be host names or IP addresses, comma separated; refused: {bad_names or 'none given'}")
    if args.lifetime_days is None:
        args.lifetime_days = "30" if args.bundle or args.env == "local" else "90"
    if not re.fullmatch(r"\d{1,4}", str(args.lifetime_days)):
        raise SystemExit("--lifetime-days must be a number")
    if args.bundle and int(args.lifetime_days) > 30:
        raise SystemExit("--lifetime-days: a route B bundle lives 30 days at most (its key has travelled)")
    if args.bundle and not is_pkcs12(args.bundle):
        raise SystemExit(f"--bundle {args.bundle} is not a PKCS12 file (.p12); route B delivers the bundle "
                         "issue-client-bundle.sh or the real issuer made, nothing else")

    try:
        ca_pems = tlslib.split_bundle(args.server_ca)
        ca_infos = [tlslib.cert_info_from_pem(p) for p in ca_pems]
        consumer_ca_pems = tlslib.split_bundle(args.consumer_ca)
        consumer_ca_infos = [tlslib.cert_info_from_pem(p) for p in consumer_ca_pems]
        previous_pems = tlslib.split_bundle(args.previous_server_ca) if args.previous_server_ca else []
        previous_infos = [tlslib.cert_info_from_pem(p) for p in previous_pems]
    except (OSError, ValueError) as problem:
        raise SystemExit(f"cannot read a CA file: {problem}") from problem
    if not ca_infos or not all(info["is_ca"] for info in ca_infos):
        raise SystemExit("--server-ca must hold a CA certificate, and nothing else")
    if len(ca_infos) != 1:
        raise SystemExit(f"--server-ca holds {len(ca_infos)} certificates; a kit trusts exactly one CA. "
                         "(During a server CA rotation, use server-ca.current.crt, the new CA alone: "
                         "see certificates.md, \"CA rotation\".)")
    # During an overlap the trust file may hold the previous consumer CA too; the first is the current one.
    if not consumer_ca_infos or not all(info["is_ca"] for info in consumer_ca_infos) or len(consumer_ca_infos) > 2 \
            or len({info["subject"] for info in consumer_ca_infos}) != 1:
        raise SystemExit("--consumer-ca must hold the producer's consumer CA (one certificate; two with the same name during a rotation)")
    if args.previous_server_ca:
        # The rotation overlap, and nothing else: the previous server CA, alone, with
        # the same name as the new one, a CA, still valid, and not the new one again.
        if len(previous_infos) != 1 or not previous_infos[0]["is_ca"]:
            raise SystemExit("--previous-server-ca must hold exactly one CA certificate (server-ca.previous.crt)")
        previous = previous_infos[0]
        if previous["subject"] != ca_infos[0]["subject"] or previous["fingerprint_sha256"] == ca_infos[0]["fingerprint_sha256"]:
            raise SystemExit("--previous-server-ca must be the CA the new --server-ca replaced: the same name, another "
                             "certificate (server-ca.previous.crt beside server-ca.current.crt)")
        if tlslib.days_left(previous) <= 0:
            raise SystemExit("--previous-server-ca has expired: the overlap is over; build the kit from --server-ca alone")
        ca_pems = ca_pems + previous_pems
    server_ca_usage = ca_infos[0]["extended_key_usage"]
    if server_ca_usage and "serverAuth" not in server_ca_usage:
        raise SystemExit(f"--server-ca {ca_infos[0]['subject_cn']} is limited to {', '.join(server_ca_usage)}: it cannot sign "
                         "server certificates. Is it a consumer CA or the negative-test CA? Use the producer's server CA.")
    for label, infos in (("--server-ca", ca_infos), ("--previous-server-ca", previous_infos), ("--consumer-ca", consumer_ca_infos)):
        for info in infos:
            own_env = throwaway_env(info["subject_cn"])
            if own_env and args.env and args.env != own_env:
                raise SystemExit(f"{label} {info['subject_cn']} is a throwaway {own_env} CA; a {args.env} kit never trusts it")
            if own_env and not args.env:
                print(f"note: {label} {info['subject_cn']} is a throwaway {own_env} CA; pass --env {own_env}", file=sys.stderr)

    kit = Path(args.out) / f"kit-{args.producer}-for-{args.consumer}"
    try:
        # Nothing is written through a symbolic link or out of the repository (D2).
        tlslib.check_write_target(kit / "KIT-MANIFEST.json")
        if kit.is_symlink():
            raise tlslib.UnsafeWrite(f"refused to write {kit}: it is a symbolic link")
        if kit.exists():
            shutil.rmtree(kit)
        tlslib.safe_mkdir(kit / "snippets")
    except OSError as problem:
        raise SystemExit(f"cannot write the kit: {problem}") from problem

    def put(name: str, text: str, mode: int = 0o644) -> None:
        tlslib.write_text(kit / name, text, mode=mode)

    key_subpath = "/".join(part for part in (args.env, args.producer, args.consumer) if part)
    values = {
        "PRODUCER": args.producer, "CONSUMER": args.consumer, "ENDPOINT": args.endpoint,
        "ENDPOINT_BASE": base, "NAMES": ", ".join(f"`{n}`" for n in names),
        "CUTOVER": one_line(args.cutover, "--cutover"), "CONTACT": one_line(args.contact, "--contact"),
        "LIFETIME": str(args.lifetime_days), "KEY_SUBPATH": key_subpath,
        "ENVIRONMENT": args.env or "not stated",
    }
    flags = {"ROUTE_A": not args.bundle, "ROUTE_B": bool(args.bundle)}
    for source in TEMPLATE.rglob("*"):
        if source.is_dir() or source.name == ".DS_Store" or source.name.endswith(".Tests.ps1"):
            continue   # the toolkit's own Pester test of make-csr.ps1 is not part of a kit
        put(source.relative_to(TEMPLATE).as_posix(), fill(source.read_text(), values, flags),
            0o755 if source.suffix == ".sh" else 0o644)
    put("make-csr.sh", (HERE / "make-csr.sh").read_text(), 0o755)
    put("_key_folder.sh", (HERE / "_key_folder.sh").read_text(), 0o644)
    put("ca-bundle.pem", "\n".join(ca_pems) + "\n")
    put("consumer-ca.crt", "\n".join(consumer_ca_pems) + "\n")
    put("endpoint.txt",
        f"url={args.endpoint}\nconsumer={args.consumer}\nproducer={args.producer}\nnames={','.join(names)}\n"
        + (f"environment={args.env}\n" if args.env else ""))
    route = "A"
    if args.client_cert:
        try:
            info = tlslib.cert_info(args.client_cert)
        except (OSError, ValueError) as problem:
            shutil.rmtree(kit)
            raise SystemExit(f"--client-cert cannot be used: {problem}") from problem
        if info["subject_cn"] != args.consumer or info["extended_key_usage"] != ["clientAuth"]:
            shutil.rmtree(kit)
            raise SystemExit("--client-cert is not a client certificate for this consumer")
        put("client.crt", "\n".join(tlslib.split_bundle(args.client_cert)) + "\n")
    bundle_sha256 = None
    if args.bundle:
        route = "B"
        bundle_sha256 = tlslib.sha256_file(args.bundle)

    put(SUMS, sums_text(kit))
    fingerprint = kit_fingerprint(kit)
    files = sorted(p.relative_to(kit).as_posix() for p in kit.rglob("*") if p.is_file())
    keys = scan_rules.find_private_keys(kit)
    ca_fingerprint = ca_infos[0]["fingerprint_sha256"]
    ca_bundle_sha256 = tlslib.sha256_file(kit / "ca-bundle.pem")
    manifest = {
        "tool": "build_kit.py",
        "generated_at": tlslib.iso(tlslib.now_utc()),
        "producer": args.producer,
        "consumer": args.consumer,
        "environment": args.env,
        "endpoint": args.endpoint,
        "route": route,
        "key_travelled": route == "B",
        "bundle_sha256": bundle_sha256,
        "ca_bundle_sha256": ca_bundle_sha256,
        "ca_certificates": len(ca_pems),
        "ca_fingerprint_sha256": ca_fingerprint,
        # A server CA rotation overlap: ca-bundle.pem holds the new CA, then the previous one.
        "ca_overlap": bool(previous_infos),
        "previous_ca_fingerprint_sha256": previous_infos[0]["fingerprint_sha256"] if previous_infos else None,
        "required_files": REQUIRED,
        # The SHA-256 of SHA256SUMS: sent to the consumer over another channel, checked before any script runs.
        "kit_fingerprint_sha256": fingerprint,
        "files": {name: tlslib.sha256_file(kit / name) for name in files},
        "private_key_files": [k["file"] for k in keys],
    }
    if keys:
        shutil.rmtree(kit)
        raise SystemExit(f"refused: the kit would hold key material: {[k['file'] for k in keys]}")
    tlslib.write_json(kit / "KIT-MANIFEST.json", manifest)
    print(f"kit: {tlslib.shown_path(kit, tlslib.find_repo_root(kit / 'KIT-MANIFEST.json'))}")
    print(f"route: {route}{' (key travelled: flag it in the report)' if route == 'B' else ''}")
    print(f"SHA-256 of ca-bundle.pem to send SEPARATELY (chat, phone or ticket): {ca_bundle_sha256}")
    if previous_infos:
        print(f"  (it covers the whole file: the new server CA {ca_fingerprint} and the previous one "
              f"{previous_infos[0]['fingerprint_sha256']}; during the overlap verify.sh accepts only this whole-file SHA-256)")
    else:
        print(f"  (it covers the whole file, {len(ca_pems)} certificate(s); the CA certificate's own fingerprint is {ca_fingerprint})")
    print(f"kit fingerprint (SHA-256 of {SUMS}) to send SEPARATELY too: {fingerprint}")
    print(f"  (the consumer checks it before running any script in the kit: shasum -a 256 {SUMS}, then "
          f"shasum -a 256 -c {SUMS}; or ./verify.sh and ./make-csr.sh --kit-fingerprint {fingerprint})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
