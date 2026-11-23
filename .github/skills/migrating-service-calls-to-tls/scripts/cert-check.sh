#!/usr/bin/env bash
# Checks every planned certificate and trust store and writes certs.json.
#
# usage: cert-check.sh --repo <repo> --plan <certs-to-check.yaml> --out <certs.json> [--environment <the run's environment>]
#
# Checks: usage matches the role, CA:FALSE, names cover every consumer
# address, chain to the planned CA only, days left, lifetime, key type,
# a leaf ends before its CA, trust stores hold only the planned CA (by name and
# by SHA-256: the CA that really issued a planned certificate, or a declared
# previous CA during a rotation), no local-dev
# CA outside local, and no test CA outside test.
# Reads public certificates only. See cert_check.py for the plan format.
set -euo pipefail
command -v python3 >/dev/null || { echo "error: python3 (3.9 or later) is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 1; }
exec python3 -I -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/cert_check.py" "$@"
