#!/usr/bin/env bash
# Live probes P1-P10 against a producer; writes probes.json.
#
# usage:
#   probe-tls.sh --repo <repo> --plan <probe-plan.yaml> --out <probes.json>
#   probe-tls.sh --baseline --url <http url> [--url ...] --out <behaviour-before.json>
#   probe-tls.sh --repo <repo> --server-only <host:port> [--ca <ca file>]
#             an HTTPS endpoint that asks for no client certificate; writes
#             tls-migration/evidence/server-only/<host>_<port>.json
#
# Run it from the probe location the policy names. See probe_tls.py for the
# plan format and how each probe is judged.
set -euo pipefail
command -v python3 >/dev/null || { echo "error: python3 (3.9 or later) is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 1; }
command -v curl >/dev/null || { echo "error: curl is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 1; }
exec python3 -I -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/probe_tls.py" "$@"
