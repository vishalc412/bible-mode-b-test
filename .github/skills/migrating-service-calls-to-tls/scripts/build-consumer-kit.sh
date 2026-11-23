#!/usr/bin/env bash
# Builds a consumer kit: README, endpoint, the producer's server CA, the
# consumer CA, make-csr.sh, verify.sh, snippets for six runtimes, SHA256SUMS and a
# SHA-256 manifest.
#
# usage: build-consumer-kit.sh --producer <p> --consumer <id> --endpoint <https url> --names <a,b>
#                              --server-ca <server-ca.crt> --consumer-ca <producer-consumers-ca.crt>
#                              --out <tls-migration/kits> [--env <local|test|staging|production>]
#                              [--client-cert <certificate>] [--bundle <p12>]
#                              [--cutover <date>] [--contact <text>] [--lifetime-days N]
#                              [--previous-server-ca <server-ca.previous.crt>]
#
# --lifetime-days defaults to 30 in local and for a --bundle, 90 elsewhere.
# --previous-server-ca: during a server CA rotation, with --server-ca
# server-ca.current.crt, the kit trusts both (see certificates.md, "CA rotation").
# --server-ca must hold exactly one CA certificate, one that may sign server
# certificates; a throwaway CA is refused outside its own --env. Prints the SHA-256 of the kit's ca-bundle.pem
# and the kit fingerprint (the SHA-256 of the kit's SHA256SUMS); send both over a different channel from the
# kit. See build_kit.py for the rest.
set -euo pipefail
command -v python3 >/dev/null || { echo "error: python3 (3.9 or later) is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 1; }
exec python3 -I -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/build_kit.py" "$@"
