#!/usr/bin/env bash
# The deterministic gate for a TLS migration. Writes
# tls-migration/evidence/check-result.json and prints one line per check.
#
# usage: check.sh --repo <repo> [--manifest tls-migration/tls-services.yaml] [--out <file>]
#                 [--live [--live-target <host:port>]] [--policy <tls-policy.yaml>]
#
#   --live-target <host:port>
#             with --live: where the operator confirms the probes may connect.
#             Required outside local; it must equal the target the probe plan (or,
#             for a consumer, the kit's endpoint) names, else nothing is sent.
#             Give it once per endpoint when the run probes more than one.
#   --policy  the operator's policy file (or the environment variable TLS_POLICY).
#             Outside local it must be a file outside --repo: a policy inside the
#             repository under review is refused (exit 3).
#             Needed outside local: there the manifest's own "policy:" line is not
#             used, and without an operator policy readiness (E8) is "not run".
#             E5 takes the certificate renewal margin and lifetimes from it too
#             (the toolkit's defaults, 21 and 90 days, without one).
#
# Checks E0-E15: manifest, tests, plain http:// left, known ways of switching
# certificate checking off (pattern matching, not proof), keys in the
# repository, certificates re-checked from the files, probe results re-derived
# from what was observed, trust-store scope, readiness rebuilt from the log,
# kits, local-dev leaks, the report against the evidence, producer config
# against its stage, exceptions, cutover finished, and every file read (what
# was not scanned is listed in the result).
#
# Result: pass | pass with exceptions | not proven | fail.
# Exit: 0 pass (with or without exceptions), 1 fail, 2 not proven, 3 bad input.
# A check that could not run is "not run" and makes the result "not proven".
# The result file (the default one, or the --out file) says "fail" from the
# moment the gate starts until it ends; an --out that is a folder is bad input.
set -euo pipefail
command -v python3 >/dev/null || { echo "error: python3 (3.9 or later) is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 3; }
command -v openssl >/dev/null || { echo "error: OpenSSL 3 or later is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine." >&2; exit 3; }
exec python3 -I -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check_gate.py" "$@"
