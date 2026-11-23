# Sourced by the certificate scripts. Not run on its own.
#
# Every script that makes a key sources this file first, so the same rules
# apply everywhere:
#   - umask 077: keys and their folders are readable by the owner only;
#   - keys live under TLS_PRIVATE_DIR, outside any source repository;
#   - only certificates, requests and metadata are ever printed.
#
# Layout under TLS_PRIVATE_DIR (one folder per project, <env> is local, test,
# staging or production; nothing is shared between environments):
#   ca-<env>/                                  the CAs (local and test only)
#   <env>/<service>/server.key                 a producer's server key
#   <env>/<producer>/<consumer>/client.key     a consumer's key for that producer
#   probe-<env>/<producer>/                    the probe certificates
#   bundles-<env>/                             route B work files
set -euo pipefail
umask 077
# A signal ends the script through its EXIT trap, so no half-written .new file
# is left behind (bash runs no EXIT trap when a signal kills it outright).
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# The helpers import one another; no bytecode is written into the skill folder.
export PYTHONDONTWRITEBYTECODE=1
# Every Python start is isolated (D1): -I keeps the current folder (the
# repository under review), PYTHONPATH and the user's site folder off sys.path,
# so a json.py or sitecustomize.py in the repository never runs; -B writes no
# bytecode (-I ignores PYTHONDONTWRITEBYTECODE). A script imports its siblings
# from its own folder itself.
py() { python3 -I -B "$@"; }

die() { echo "error: $*" >&2; exit 1; }
note() { echo "$*" >&2; }
# Prints a script's header comment (everything after the first line, up to the first code line).
print_usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$1" >&2; }

# --help must work before anything is set up.
help_requested=0
for _arg in "$@"; do
  [[ "$_arg" == "--help" || "$_arg" == "-h" ]] && help_requested=1
done
unset _arg

# No shared default: two projects with a consumer called "orders" must never
# share a key. local-tls-up.sh picks a per-repository folder when unset.
if [[ "$help_requested" -eq 0 && -z "${TLS_PRIVATE_DIR:-}" ]]; then
  die "set TLS_PRIVATE_DIR to this project's key folder, outside any repository (for example ~/.tls-migration/private/<project>). After local-tls-up.sh, the folder it chose is in tls-migration/local/private-dir.txt"
fi

ID_RE='^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'

# The CAs of one environment never mix with another's: local-dev and test
# CAs live in separate folders, so a test run can never reuse a local-dev key.
ca_dir_for() { echo "$TLS_PRIVATE_DIR/ca-$1"; }
server_key_dir() { echo "$TLS_PRIVATE_DIR/$1/$2"; }            # <env> <service>
client_key_dir() { echo "$TLS_PRIVATE_DIR/$1/$2/$3"; }         # <env> <producer> <consumer>
# One folder per producer: probe-unlisted is signed by that producer's consumer CA,
# so two producers sharing a folder would re-sign each other's refusal probe.
probe_dir_for() { echo "$TLS_PRIVATE_DIR/probe-$1${2:+/$2}"; }
bundles_dir_for() { echo "$TLS_PRIVATE_DIR/bundles-$1"; }

# "openssl 3" means OpenSSL 3. macOS ships LibreSSL 3.x under the same command
# name; it lacks options these scripts need and writes keys other tools refuse.
require_openssl3() {
  command -v openssl >/dev/null || die "OpenSSL 3 or later is needed and was not found. Ask the person at this machine to install it and put it first on PATH; an assistant never installs software or changes the machine."
  local banner version
  banner="$(openssl version 2>/dev/null || true)"
  version="$(echo "$banner" | awk '{print $2}')"
  if [[ "$banner" != OpenSSL\ * ]] || ! [[ "${version%%.*}" =~ ^[0-9]+$ && "${version%%.*}" -ge 3 ]]; then
    die "OpenSSL 3 or later is needed; found '$banner' (the openssl macOS ships is LibreSSL). Ask the person at this machine to install OpenSSL 3 and put it first on PATH; an assistant never installs software or changes the machine."
  fi
  command -v python3 >/dev/null || die "python3 (3.9 or later) is needed for the certificate checks and was not found. Ask the person at this machine to install it; an assistant never installs software."
}

# The key folder checks (KEY_FOLDER_HINT, refuse_inside_repo, refuse_foreign_dir,
# refuse_unsafe_parent, ensure_private_dir) live in _key_folder.sh: make-csr.sh
# uses the same copy, in the toolkit and in every consumer kit.
source "$scripts_dir/_key_folder.sh"

# Refuses a folder under a given repository even when that repository has no
# version-control folder (an export, or a copy made for the run).
refuse_under() {   # <folder> <repository>
  local dir="$1" rest="" repo
  # Resolved through the nearest folder that exists: nothing is created before the check.
  while [[ ! -d "$dir" ]]; do rest="/$(basename "$dir")$rest"; dir="$(dirname "$dir")"; done
  dir="$(cd "$dir" && pwd -P)$rest"
  repo="$(cd "$2" && pwd -P)"
  case "$dir/" in
    "$repo"/*) die "TLS_PRIVATE_DIR ($1) is inside the repository $repo; $KEY_FOLDER_HINT" ;;
  esac
}

# Refuses a file about to be written inside <repo> (D2) when the file, or any
# folder between the repository root and it, is a symbolic link, or when the
# folder it lands in resolves outside the repository. A file in a repository
# may never lead a write elsewhere (a shell start-up file, a key).
refuse_link_path() {   # <repository> <file>
  local root rest part current
  root="$(cd "$1" && pwd -P)"
  case "$2" in
    "$root"/*) rest="${2#"$root"/}" ;;
    *) die "refused to write $2: it is not inside the repository $root" ;;
  esac
  current="$root" rest="$rest/"
  while [[ -n "$rest" ]]; do
    part="${rest%%/*}" rest="${rest#*/}"
    [[ -n "$part" ]] || continue
    current="$current/$part"
    [[ -L "$current" ]] && die "refused to write $2: $current is a symbolic link (a file in the repository may not lead the toolkit elsewhere); nothing was written"
  done
  [[ -L "$2.tmp" ]] && die "refused to write $2: $2.tmp is a symbolic link; nothing was written"
  return 0
}

# A folder for public files (certificates, requests): readable by others, unlike
# the keys. Made 0755 when new; an existing folder keeps its mode.
make_public_dir() {   # <folder>
  [[ -d "$1" ]] || ( umask 022; mkdir -p "$1" )
}

check_env_signs_locally() {
  case "$1" in
    local|test) ;;
    staging|production) die "environment '$1' never signs on this machine; its certificates come from the company CA, Vault or cert-manager (certificate mode request-only, or platform-issues: a person or the pipeline applies what is written)" ;;
    *) die "unknown environment '$1' (local, test, staging or production)" ;;
  esac
}

check_env_name() {
  case "$1" in
    local|test|staging|production) ;;
    *) die "unknown environment '$1' (local, test, staging or production)" ;;
  esac
}

ca_prefix() {
  case "$1" in
    local) echo "local-dev-" ;;
    test) echo "test-" ;;
  esac
}

# Prints public metadata for a certificate: never key material.
print_cert_metadata() {
  py "$scripts_dir/cert_meta.py" "$@"
}

# The certificate's subject common name.
cert_cn() {
  openssl x509 -in "$1" -noout -subject -nameopt RFC2253 2>/dev/null | sed -E 's/^subject=//; s/(^|.*,)CN=([^,]+).*/\2/'
}

# True when a certificate exists and has more than $2 days left.
cert_still_valid() {
  [[ -f "$1" ]] || return 1
  openssl x509 -in "$1" -noout -checkend "$(( $2 * 86400 ))" >/dev/null 2>&1
}

# Whole days a leaf signed now may live and still end before <ca cert> does.
cert_days_left() {
  py - "$scripts_dir" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import tlslib
print(tlslib.leaf_days_within(tlslib.cert_info(sys.argv[2])))
PY
}

# True when the first certificate in <cert> chains to <ca> and nothing else.
cert_verifies() {   # <cert> <ca file>
  openssl verify -no-CApath -no-CAstore -CAfile "$2" "$1" >/dev/null 2>&1
}

# True when the key file and the certificate hold the same public key. Only the
# public half is derived and compared; nothing is printed.
key_matches_cert() {   # <key> <cert>
  local from_key from_cert
  from_key="$(openssl pkey -in "$1" -pubout 2>/dev/null | openssl dgst -sha256 | awk '{print $NF}')" || return 1
  from_cert="$(openssl x509 -in "$2" -noout -pubkey 2>/dev/null | openssl dgst -sha256 | awk '{print $NF}')" || return 1
  [[ -n "$from_key" && "$from_key" == "$from_cert" ]]
}

# Runs a command; its error output is shown only when it fails, and then in full.
run_or_die() {   # <what failed> <command...>
  local what="$1" log
  shift
  log="$(mktemp)"
  if ! "$@" 2>"$log" >/dev/null; then
    echo "error: $what:" >&2
    sed 's/^/  /' "$log" >&2
    rm -f "$log"
    return 1
  fi
  rm -f "$log"
}

new_ec_key() {
  # The key is written straight to its file; nothing is echoed. A named curve,
  # never explicit parameters: Java, Go and most TLS stacks refuse those.
  run_or_die "could not make a key at $1" \
    openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -pkeyopt ec_param_enc:named_curve -out "$1"
  chmod 600 "$1"
}
