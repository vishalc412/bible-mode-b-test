#!/usr/bin/env bash
# Builds consumer-readiness.md and readiness.json from the producer's access log.
#
# usage: readiness-from-logs.sh --log <file> --allowlist <allowed-consumers.yaml> --out <readiness.json>
#                               [--md <consumer-readiness.md>] [--min-observation-days N]
#                               [--signoff <cutover-signoff.yaml>] [--signoff-roles "<role>,..."]
#                               [--probe-tags <probe-tags.log>]
#
#   --probe-tags  the tags probe-tls.sh recorded for its own requests; default
#                 probe-tags.log in the --out folder (tls-migration/evidence/).
#                 Only lines with a recorded tag are left out.
#
# A consumer counts as ready only when seen on mutual TLS with its own
# certificate over its whole window, and the log covers that window. A line is
# read only when it is exactly the access record of references/producer.md
# (the marker starts the message, every field once, in order); other lines
# holding the marker are rejected and counted in rejected_lines.
set -euo pipefail
command -v python3 >/dev/null || { echo "error: python3 (3.9 or later) is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 1; }
exec python3 -I -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/readiness.py" "$@"
