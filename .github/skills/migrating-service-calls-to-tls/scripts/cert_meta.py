"""Prints a one-line metadata summary for each certificate file given.

usage: cert_meta.py <cert.pem> [<cert.pem> ...]

Only public facts: subject, issuer, names, usage, expiry and SHA-256
fingerprint. Refuses a file that holds a private key.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tlslib  # noqa: E402


def main(paths: list[str]) -> int:
    status = 0
    for path in paths:
        try:
            info = tlslib.cert_info(path)
        except ValueError as problem:
            print(f"{path}: {problem}", file=sys.stderr)
            status = 1
            continue
        names = ",".join(info["san"]["dns"] + info["san"]["ip"] + info["san"]["uri"]) or "-"
        usage = ",".join(info["extended_key_usage"]) or ("CA" if info["is_ca"] else "-")
        print(
            f"{Path(path).name}: subject={info['subject_cn']} issuer={info['issuer_cn']} "
            f"names={names} usage={usage} key={info['key_type']} expires={info['not_after']} "
            f"sha256={info['fingerprint_sha256']}"
        )
    return status


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
