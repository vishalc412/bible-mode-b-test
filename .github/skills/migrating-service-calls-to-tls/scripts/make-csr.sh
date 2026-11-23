#!/usr/bin/env bash
# Makes a consumer's private key and certificate request. Stand-alone: it is
# also copied into every consumer kit, so it needs only bash and OpenSSL 3 or 4.
#
# usage: make-csr.sh [--consumer <id>] [--producer <name>] [--env <env>] [--out <dir>]
#                    [--renew [--force] | --activate --cert <new certificate> [--cert-out <file>] | --replace]
#                    [--kit-fingerprint <sha256>]
#
#   --consumer  your consumer id, as the producer team gave it to you
#   --producer  the producer this key is for: one key per producer, never shared
#   --env       local, test, staging or production; keeps each environment's key apart
#               In a kit all three come from endpoint.txt: run ./make-csr.sh with no arguments.
#   --out       where to write <producer>-<consumer>.csr; default: the current folder
#   --renew     renewal: a new key in client.key.next and a request from it; the
#               key in use stays in place, so your service keeps working. Refused
#               while an earlier renewal is waiting for its certificate (--force
#               starts again and makes the earlier request useless).
#   --activate --cert <file>
#               once the new certificate has arrived (save it as client.crt.next,
#               never over client.crt, which is still in use): checks that it
#               belongs to client.key.next, then swaps key and certificate
#               together. The old pair is kept as client.key.previous and
#               <certificate>.previous. --cert-out is the certificate file your
#               service reads; default client.crt in the kit folder (or beside
#               the key outside a kit). --cert may not be that same file.
#               Then restart the service, or update its secret from the new pair.
#   --replace   a new client.key straight away (a lost key). The certificate in
#               use stops matching: ask for a new one with the request written.
#   --kit-fingerprint <sha256>
#               in a kit: the kit fingerprint the producer team sent you apart
#               from the kit (the SHA-256 of SHA256SUMS). Before any key is
#               touched, SHA256SUMS must have that SHA-256 and every file it
#               lists must match it; otherwise nothing is done.
#
# For staging and production a key is made only by a person at a terminal: the
# script asks for the environment's name to be typed and stops on anything
# else, or when its input is not a terminal. An assistant never runs it for
# those environments; it writes the command for the owners of the target.
#
# The key goes to <root>/[<env>/]<producer>/<consumer>/client.key, mode 0600,
# and never anywhere else. <root> is $TLS_PRIVATE_DIR, default
# ~/.tls-migration/private. Run this where the key will live: on the machine or
# in the pipeline that loads the service's secret store. Send only the .csr
# to the producer team. The key never leaves this machine.
set -euo pipefail
umask 077

die() { echo "error: $*" >&2; exit 1; }
usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "${BASH_SOURCE[0]}" >&2; exit "${1:-2}"; }
ID_RE='^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
consumer="" producer="" env_name="" out_dir="." mode="first" force=0 new_cert="" cert_out="" in_kit=0 kit_fingerprint=""
# A value from endpoint.txt, without the carriage return a Windows editor adds.
kit_field() { sed -n "s/^$1=//p" "$here/endpoint.txt" | tr -d '\r' | head -1; }
if [[ -f "$here/endpoint.txt" ]]; then
  in_kit=1
  consumer="$(kit_field consumer)"
  producer="$(kit_field producer)"
  env_name="$(kit_field environment)"
fi
while [[ $# -gt 0 ]]; do
  case "$1" in
    --consumer) consumer="${2:-}"; shift 2 || usage ;;
    --producer) producer="${2:-}"; shift 2 || usage ;;
    --env) env_name="${2:-}"; shift 2 || usage ;;
    --out) out_dir="${2:-}"; shift 2 || usage ;;
    --renew) mode="renew"; shift ;;
    --activate) mode="activate"; shift ;;
    --replace) mode="replace"; shift ;;
    --force) force=1; shift ;;
    --cert) new_cert="${2:-}"; shift 2 || usage ;;
    --cert-out) cert_out="${2:-}"; shift 2 || usage ;;
    --kit-fingerprint) kit_fingerprint="${2:-}"; shift 2 || usage ;;
    --help|-h) usage 0 ;;
    *) usage ;;
  esac
done
[[ -n "$consumer" ]] || die "--consumer <id> is required (in a kit it comes from endpoint.txt)"
[[ -n "$producer" ]] || die "--producer <name> is required: every producer gets its own key (in a kit it comes from endpoint.txt)"
[[ "$consumer" =~ $ID_RE ]] || die "consumer id must be lowercase letters, digits and hyphens"
[[ "$producer" =~ $ID_RE ]] || die "producer name must be lowercase letters, digits and hyphens"
case "$env_name" in ""|local|test|staging|production) ;; *) die "unknown environment '$env_name' (local, test, staging or production)" ;; esac

# "openssl 3" means OpenSSL 3. macOS ships LibreSSL 3.x under the same name: it
# writes keys other tools refuse and lacks options the kit needs.
command -v openssl >/dev/null || die "OpenSSL 3 or later is needed and was not found. Ask the person at this machine to install it and put it first on PATH; an assistant never installs software or changes the machine."
banner="$(openssl version 2>/dev/null || true)"
version="$(echo "$banner" | awk '{print $2}')"
if [[ "$banner" != OpenSSL\ * ]] || ! [[ "${version%%.*}" =~ ^[0-9]+$ && "${version%%.*}" -ge 3 ]]; then
  die "OpenSSL 3 or later is needed; found '$banner' (the openssl macOS ships is LibreSSL). Ask the person at this machine to install OpenSSL 3 and put it first on PATH; an assistant never installs software or changes the machine."
fi

# The kit, checked against the fingerprint sent apart from it, before any key is touched (D7).
sha256_of() { openssl dgst -sha256 "$1" | awk '{print $NF}'; }
if [[ -n "$kit_fingerprint" ]]; then
  [[ "$in_kit" -eq 1 ]] || die "--kit-fingerprint checks a consumer kit; this make-csr.sh is not in one (no endpoint.txt beside it)"
  wanted="$(printf '%s' "$kit_fingerprint" | tr -d ': ' | tr 'A-F' 'a-f')"
  [[ "$wanted" =~ ^[0-9a-f]{64}$ ]] || die "--kit-fingerprint must be a SHA-256: 64 hexadecimal characters"
  [[ -f "$here/SHA256SUMS" && ! -L "$here/SHA256SUMS" ]] || die "this kit has no SHA256SUMS, so it cannot be checked; do not use it, call the producer team. Nothing was done."
  [[ "$(sha256_of "$here/SHA256SUMS")" == "$wanted" ]] || die "the kit fingerprint does not match: SHA256SUMS is not the one the producer team sent. Do not use this kit; call the producer team. Nothing was done."
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ ^([0-9a-f]{64})\ \ (.+)$ ]] || die "SHA256SUMS holds a line that is not '<sha256>  <file>'; do not use this kit. Nothing was done."
    name="${BASH_REMATCH[2]}"
    case "/$name/" in */../*|//*) die "SHA256SUMS names $name, outside the kit; do not use this kit. Nothing was done." ;; esac
    [[ -f "$here/$name" && ! -L "$here/$name" ]] || die "$name, listed in SHA256SUMS, is missing from the kit; do not use it. Nothing was done."
    [[ "$(sha256_of "$here/$name")" == "${BASH_REMATCH[1]}" ]] || die "$name does not match SHA256SUMS: the kit was changed. Do not use it; call the producer team. Nothing was done."
  done < "$here/SHA256SUMS"
  echo "kit checked: SHA256SUMS matches the fingerprint and every file it lists matches" >&2
fi

# The key folder checks, the same copy the toolkit's other scripts use. Read
# only after the kit check above: in a kit it is one of the files checked.
[[ -f "$here/_key_folder.sh" ]] || die "_key_folder.sh is missing beside make-csr.sh; it belongs to the kit (or the toolkit's scripts folder). Nothing was made."
source "$here/_key_folder.sh"

# Nothing half-written is left behind, whatever stops the script (a signal, a
# closed terminal, an error): a key being written, a certificate being swapped
# in, or a renewal key whose request was never written.
pending_files=()
cleanup() {
  [[ ${#pending_files[@]} -gt 0 ]] && rm -f "${pending_files[@]}"
  return 0
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

private_root="${TLS_PRIVATE_DIR:-$HOME/.tls-migration/private}"
key_dir="$private_root/${env_name:+$env_name/}$producer/$consumer"
if [[ -z "$env_name" && "$in_kit" -eq 0 ]]; then
  echo "warning: no --env: this one key ($key_dir/client.key) would serve every environment, and no certgen-test-ca.sh --clean --env removes it. Pass --env local|test|staging|production to keep each environment's key apart." >&2
fi
# The same checks as every other key folder (_key_folder.sh): outside any
# repository, and every folder that exists on the way ours and writable by
# nobody else; a folder still to be made is checked through its nearest
# existing parent, before anything is created.
TLS_PRIVATE_DIR="$private_root"
# A person types the environment's name before a staging or production key is made (D8).
[[ "$mode" != activate ]] && confirm_environment "$env_name" "the client key and certificate request of $consumer for $producer"
ensure_private_dir "$key_dir"

key="$key_dir/client.key"
# The SHA-256 of a public key, or nothing when the file cannot be read (never the hash of empty input).
pub_hash() { [[ -n "$1" ]] && printf '%s\n' "$1" | openssl dgst -sha256 | awk '{print $NF}'; return 0; }
pub_of_key() { pub_hash "$(openssl pkey -in "$1" -pubout 2>/dev/null || true)"; }
pub_of_cert() { pub_hash "$(openssl x509 -in "$1" -noout -pubkey 2>/dev/null || true)"; }
new_key() {
  # A named curve, never explicit parameters: Java, Go and most TLS stacks refuse those.
  # Written beside its place and moved in once complete.
  pending_files+=("$1.new")
  rm -f "$1.new"
  openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -pkeyopt ec_param_enc:named_curve -out "$1.new" 2>/dev/null \
    || die "could not make a key at $1"
  chmod 600 "$1.new"
  mv -f "$1.new" "$1"
}

case "$mode" in
  activate)
    [[ -n "$new_cert" ]] || die "--activate needs --cert <the new certificate>: the key is swapped only together with the certificate that belongs to it"
    [[ -f "$new_cert" ]] || die "no certificate at $new_cert"
    [[ -f "$key.next" ]] || die "no renewal key at $key.next; run with --renew first"
    cert_pub="$(pub_of_cert "$new_cert")"
    [[ -n "$cert_pub" ]] || die "$new_cert is not a certificate openssl can read"
    next_pub="$(pub_of_key "$key.next")"
    [[ -n "$next_pub" ]] || die "the renewal key $key.next cannot be read; nothing was changed"
    if [[ "$cert_pub" != "$next_pub" ]]; then
      if [[ -f "$key" && "$cert_pub" == "$(pub_of_key "$key")" ]]; then
        die "$new_cert belongs to the key already in use, not to the renewal key; nothing was changed"
      fi
      die "$new_cert does not belong to the renewal key in $key.next (was --renew run again after the request was sent?); nothing was changed. Send the request from the last --renew, or run --renew --force and send that one."
    fi
    cert_cn="$(openssl x509 -in "$new_cert" -noout -subject -nameopt RFC2253 | sed -E 's/^subject=//; s/(^|.*,)CN=([^,]+).*/\2/')"
    [[ "$cert_cn" == "$consumer" ]] || die "$new_cert is for CN=$cert_cn, not for $consumer; nothing was changed"
    if [[ -z "$cert_out" ]]; then
      [[ "$in_kit" -eq 1 ]] && cert_out="$here/client.crt" || cert_out="$key_dir/client.crt"
    fi
    mkdir -p "$(dirname "$cert_out")"
    # The new certificate saved over the one in use: the old certificate is
    # already gone, so it cannot be kept, and the service now holds a
    # certificate that does not match its key. Refused, with the way out.
    if [[ -e "$cert_out" && "$new_cert" -ef "$cert_out" ]]; then
      die "$new_cert is the certificate file your service reads ($cert_out): the new certificate was saved over the one in use, so the old certificate is lost and cannot be kept as $(basename "$cert_out").previous. Nothing was changed. Move it aside and activate from there: mv $cert_out $cert_out.next && $(basename "${BASH_SOURCE[0]}") --activate --cert $cert_out.next. Next time save a renewal as client.crt.next."
    fi
    kept_cert=""
    pending_files+=("$cert_out.new")
    [[ -L "$cert_out" || -L "$cert_out.new" ]] && die "refused: $cert_out (or $cert_out.new) is a symbolic link; nothing was changed"
    ( umask 022; rm -f "$cert_out.new"; cp "$new_cert" "$cert_out.new" )
    if [[ -f "$cert_out" ]]; then
      if cmp -s "$cert_out" "$new_cert"; then
        note_cert="$cert_out already held the new certificate (a copy of $new_cert); the old certificate was not there to keep"
      else
        mv -f "$cert_out" "$cert_out.previous"
        kept_cert="$cert_out.previous"
      fi
    else
      note_cert="there was no certificate at $cert_out to keep"
    fi
    kept_key=""
    if [[ -f "$key" ]]; then mv -f "$key" "$key.previous"; kept_key="$key.previous"; fi
    mv -f "$key.next" "$key"
    mv -f "$cert_out.new" "$cert_out"
    echo "renewed: key $key and certificate $cert_out now belong together"
    # Says what was kept, and only that.
    if [[ -n "$kept_key" && -n "$kept_cert" ]]; then
      echo "the old pair is kept as $kept_key and $kept_cert; delete both once the new pair works"
    else
      [[ -n "$kept_key" ]] && echo "the old key is kept as $kept_key; delete it once the new pair works"
      [[ -n "$kept_cert" ]] && echo "the old certificate is kept as $kept_cert; delete it once the new pair works"
      [[ -n "${note_cert:-}" ]] && echo "$note_cert"
    fi
    echo "now restart the service, or update its secret from the new pair: a running client does not pick the new certificate up by itself"
    exit 0 ;;
  renew)
    if [[ -f "$key.next" && "$force" -eq 0 ]]; then
      die "a renewal is already waiting for its certificate ($key.next exists). Activate it with --activate --cert <file>, or start again with --renew --force (the request already sent becomes useless)."
    fi
    [[ -f "$key" ]] || die "no key in use at $key; run without --renew for a first request"
    # Until its request is written, the renewal key is half done: removed if the run stops.
    pending_files+=("$key.next")
    new_key "$key.next"
    signing_key="$key.next" ;;
  replace)
    if [[ -f "$key" ]]; then
      mv -f "$key" "$key.previous"
      echo "the key in use was replaced (kept as client.key.previous); the certificate in use no longer matches until the new one arrives" >&2
    fi
    new_key "$key"
    signing_key="$key" ;;
  first)
    if [[ -f "$key" ]]; then
      echo "a key already exists for $consumer at $producer; re-using it (--renew for a renewal, --replace for a new key now)" >&2
    else
      new_key "$key"
    fi
    signing_key="$key" ;;
esac

# The request is public: its folder is made readable by others when it is new.
[[ -d "$out_dir" ]] || ( umask 022; mkdir -p "$out_dir" )
csr="$out_dir/$producer-$consumer.csr"
[[ -L "$csr" ]] && die "refused to write $csr: it is a symbolic link"
# MSYS_NO_PATHCONV: Git Bash on Windows would turn /CN=... into a Windows path.
( umask 022; MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' openssl req -new -key "$signing_key" -subj "/CN=$consumer" -out "$csr" 2>/dev/null ) \
  || die "could not write the request $csr"
echo "request: $csr  (send this file to the $producer team)"
echo "subject: CN=$consumer"
echo "public key sha256: $(openssl req -in "$csr" -noout -pubkey | openssl pkey -pubin -outform DER 2>/dev/null | openssl dgst -sha256 | awk '{print $NF}')"
echo "key kept at: $signing_key  (never send it, never commit it)"
if [[ "$mode" == renew ]]; then
  # The request is written: the renewal key now waits for its certificate.
  pending_files=()
  echo "when the new certificate arrives, save it as client.crt.next (not over client.crt, which is in use), then: $(basename "${BASH_SOURCE[0]}") --activate --cert client.crt.next"
fi
exit 0
