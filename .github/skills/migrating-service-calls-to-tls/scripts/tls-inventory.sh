#!/usr/bin/env bash
# First-pass inventory for a TLS migration. Read-only.
#
# usage: tls-inventory.sh --repo <repo> [--out <inventory.json>]
#
# Lists plain http:// URLs by host, code that switches certificate checking
# off, private keys in the repository (location only), text addressed to an
# AI assistant, and local-dev CA references outside local-only files.
set -euo pipefail
command -v python3 >/dev/null || { echo "error: python3 (3.9 or later) is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 1; }
exec python3 -I -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/tls_inventory.py" "$@"
