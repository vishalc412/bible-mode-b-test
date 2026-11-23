#!/usr/bin/env bash
# Route B (fallback): issues a ready-made PKCS12 bundle for a consumer that
# cannot run make-csr.sh. Local and test only, and only where the policy file
# sets consumer_fallback_bundle to allowed. The report must flag "key travelled".
#
# usage: issue-client-bundle.sh --env local|test --producer <p> --consumer <id> --allowlist <allowed-consumers.yaml> --out <dir> [--days N]
#
# Writes <out>/<producer>-<id>.p12 (AES-256; the consumer's key, its
# certificate and the consumer CA that signed it) and the password to
# $TLS_PRIVATE_DIR/bundles-<env>/<producer>-<id>.password, which a person
# sends over another channel. The password is never printed; do not open that
# file. The server CA is not in the bundle: the consumer trusts ca-bundle.pem
# from the kit.
# --out must be outside any repository: the bundle holds a key, so it never
# goes into a kit or a commit. build_kit.py records only its SHA-256. The
# bundle's path is recorded: certgen-test-ca.sh --clean --env <env> removes it
# when it lies inside TLS_PRIVATE_DIR, and lists it for a person otherwise.
# An --out folder that already exists is used as it is; a new one is created 0700.
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

usage() { print_usage "${BASH_SOURCE[0]}"; exit 2; }
env_name="" producer="" consumer="" allowlist="" out_dir="" days=30
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) env_name="${2:-}"; shift 2 || usage ;;
    --producer) producer="${2:-}"; shift 2 || usage ;;
    --consumer) consumer="${2:-}"; shift 2 || usage ;;
    --allowlist) allowlist="${2:-}"; shift 2 || usage ;;
    --out) out_dir="${2:-}"; shift 2 || usage ;;
    --days) days="${2:-}"; shift 2 || usage ;;
    *) usage ;;
  esac
done
[[ -n "$env_name" && -n "$producer" && -n "$consumer" && -n "$allowlist" && -n "$out_dir" ]] || usage
check_env_signs_locally "$env_name"
require_openssl3
[[ "$producer" =~ $ID_RE ]] || die "producer name must be lowercase letters, digits and hyphens"
[[ "$consumer" =~ $ID_RE ]] || die "consumer id must be lowercase letters, digits and hyphens"
[[ "$days" =~ ^[1-9][0-9]*$ && "$days" -le 30 ]] || die "a route B bundle lives at most 30 days"
[[ -f "$allowlist" ]] || die "no allowlist at $allowlist"

# Nothing is created for a consumer the producer has not listed.
py - "$scripts_dir" "$allowlist" "$producer" "$consumer" <<'PY' || exit 1
import sys
sys.path.insert(0, sys.argv[1])
import sign_csr
ids, _ = sign_csr.allowed_ids(sys.argv[2], sys.argv[3])
if sys.argv[4] not in ids:
    sys.exit(f"refused: '{sys.argv[4]}' is not in {sys.argv[2]}. Add the consumer there first, then issue the bundle.")
PY

ca_crt="$(ca_dir_for "$env_name")/$producer-consumers-ca.crt"
[[ -f "$ca_crt" ]] || die "no $env_name consumer CA for $producer; run certgen-test-ca.sh --env $env_name first"

work="$(bundles_dir_for "$env_name")"
ensure_private_dir "$work"
ensure_private_dir "$out_dir" "--out"
out_abs="$(cd "$out_dir" && pwd -P)"
name="$producer-$consumer"
key_dir="$work/keys/$producer/$consumer"
cleanup() {
  rm -f "$key_dir/client.key" "$key_dir/client.key.previous"
  rmdir "$key_dir" "$work/keys/$producer" "$work/keys" 2>/dev/null || true
}
trap cleanup EXIT

TLS_PRIVATE_DIR="$work/keys" "$scripts_dir/make-csr.sh" --consumer "$consumer" --producer "$producer" --out "$work" --replace >/dev/null
py "$scripts_dir/sign_csr.py" --env "$env_name" --producer "$producer" --csr "$work/$name.csr" \
  --allowlist "$allowlist" --out "$work" --days "$days" >/dev/null
password_file="$work/$name.password"
openssl rand -base64 18 | tr -d '\n' > "$password_file"
chmod 600 "$password_file"
run_or_die "could not write the bundle" \
  openssl pkcs12 -export -inkey "$key_dir/client.key" -in "$work/$name.crt" \
    -certfile "$ca_crt" -name "$consumer" \
    -keypbe AES-256-CBC -certpbe AES-256-CBC -macalg sha256 \
    -passout "file:$password_file" -out "$out_abs/$name.p12.new"
chmod 600 "$out_abs/$name.p12.new"
mv -f "$out_abs/$name.p12.new" "$out_abs/$name.p12"
grep -qxF "$out_abs/$name.p12" "$work/made.txt" 2>/dev/null || echo "$out_abs/$name.p12" >> "$work/made.txt"
echo "bundle: $out_abs/$name.p12 (route B; key travelled: record it in the report)"
echo "password: in $password_file. A person sends it over a different channel. Do not open it."
