#!/usr/bin/env bash
# Makes a producer's server certificate.
#
# usage:
#   make-server-cert.sh --env local|test --service <name> --names <list> --out <public-dir> [--days N]
#                       [--renew-before N | --policy <file>] [--after-overlap] [--force]
#   make-server-cert.sh --request-only --env staging|production --service <name> --names <list> --out <public-dir> [--reuse-key]
#
#   --names   every name a consumer uses to reach the service, comma separated,
#             e.g. "inventory,inventory.shop.svc.cluster.local,localhost,127.0.0.1".
#             IP addresses become IP entries; everything else DNS entries. No
#             ports. A wildcard is allowed only as the whole first label over
#             at least two more (*.shop.internal).
#   --days    leaf lifetime; default 30 in local, 90 in test; never past the
#             CA's own end date
#   --renew-before N
#             a certificate with N days or fewer left is re-issued; default the
#             renew_before_days of --policy <file> (the policy file, or a
#             certs-to-check.yaml plan), else 21: the value cert-check.sh fails
#             a certificate at. Keep it equal to the plan's renew_before_days.
#   --after-overlap
#             after a server CA rotation, the leaf the previous CA signed is kept
#             (consumers that trust only the old CA keep working) until every
#             consumer trusts both CAs; then run with --after-overlap to
#             re-issue it under the new CA. --force re-issues in any case.
#             When that leaf can no longer be kept (--renew-before days or
#             fewer left, its key gone, or new names), the run stops with exit
#             1 and changes nothing: it never cuts consumers off by itself.
#   --request-only
#             staging/production: asks the person at the terminal to type the
#             environment's name first and stops on anything else, or when its
#             input is not a terminal (an assistant never runs this for staging
#             or production: it writes the command into
#             tls-migration/requests/<name>.md for the target's owners). Then
#             writes a NEW key and a certificate request
#             with the right names and usage, for the company CA, Vault or
#             cert-manager to sign. Nothing is signed here. Run it where the
#             key will live (the target host or the deployment pipeline), not
#             on a workstation; where cert-manager or Vault can make the key
#             in place, use that instead. --reuse-key keeps the key of an
#             earlier request for this environment (a request that is still
#             waiting for its certificate).
#
# Output: <out>/<service>-server.crt (leaf, then the server CA), or
# <out>/<service>-server.csr. The common name is the first name of at most
# 64 characters (the limit of a CN), else the service name; every name is in
# the subjectAltName. The key: $TLS_PRIVATE_DIR/<env>/<service>/server.key;
# every environment has its own, none is ever reused for another.
# Reuses a certificate only when it has the same names, more than
# --renew-before days left, was signed by this environment's current CA (or by
# the previous one during a rotation overlap, see --after-overlap) and matches
# the key; else it is re-issued. The new key and certificate replace the old pair together, and
# only once signing has worked. Two runs for the same service at once: the
# second is refused (a lock in the key folder), never mixed with the first.
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

usage() { print_usage "${BASH_SOURCE[0]}"; exit 2; }

env_name="" service="" names="" out_dir="" days="" force=0 request_only=0 reuse_key=0
renew_before="" policy="" after_overlap=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) env_name="${2:-}"; shift 2 || usage ;;
    --service) service="${2:-}"; shift 2 || usage ;;
    --names) names="${2:-}"; shift 2 || usage ;;
    --out) out_dir="${2:-}"; shift 2 || usage ;;
    --days) days="${2:-}"; shift 2 || usage ;;
    --force) force=1; shift ;;
    --request-only) request_only=1; shift ;;
    --reuse-key) reuse_key=1; shift ;;
    --renew-before) renew_before="${2:-}"; shift 2 || usage ;;
    --policy) policy="${2:-}"; shift 2 || usage ;;
    --after-overlap) after_overlap=1; shift ;;
    *) usage ;;
  esac
done
[[ -n "$service" && -n "$names" && -n "$out_dir" ]] || usage
[[ -n "$env_name" ]] || die "--env is required (local, test, staging or production): every environment has its own key"
check_env_name "$env_name"
[[ "$service" =~ $ID_RE ]] || die "service name must be lowercase letters, digits and hyphens"
require_openssl3

# Every name is checked before anything is created. Prints the subjectAltName
# value, then the common name (the first name).
checked="$(py - "$names" "$service" <<'PY'
import ipaddress
import re
import sys

LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
san, first = [], None
for raw in sys.argv[1].split(","):
    name = "".join(raw.split())
    if not name:
        continue
    try:
        entry = "IP:" + str(ipaddress.ip_address(name))
    except ValueError:
        host = name.lower()
        labels = host.split(".")
        if ":" in host or "/" in host:
            sys.exit(f"'{name}' is not a host name or an IP address (give the name only: no port, no scheme, no brackets)")
        if all(label.isdigit() for label in labels):
            sys.exit(f"'{name}' looks like an incomplete IP address")
        if labels[0] == "*":
            if len(labels) < 3:
                sys.exit(f"'{name}': a wildcard needs at least two labels after it (*.shop.internal)")
            labels = labels[1:]
        if len(host) > 253 or not all(LABEL.match(label) for label in labels):
            sys.exit(f"'{name}' is not a valid host name (letters, digits and hyphens per label; a wildcard only as the whole first label)")
        entry = "DNS:" + host
    if entry not in san:
        san.append(entry)
    first = first or entry.split(":", 1)[1]
if not san:
    sys.exit("no names given")
# A common name holds at most 64 characters: the first name that fits, else the service name.
common = next((entry.split(":", 1)[1] for entry in san if len(entry.split(":", 1)[1]) <= 64), sys.argv[2])
print(",".join(san))
print(common)
PY
)" || die "--names: see the message above"
san="$(echo "$checked" | sed -n 1p)"
common_name="$(echo "$checked" | sed -n 2p)"

# A person types the environment's name before a staging or production key is made (D8).
[[ "$request_only" -eq 1 ]] && confirm_environment "$env_name" "a server key and certificate request for $service"
key_dir="$(server_key_dir "$env_name" "$service")"
ensure_private_dir "$key_dir"
make_public_dir "$out_dir"
key="$key_dir/server.key"
for file in "$out_dir/$service-server.csr" "$out_dir/$service-server.crt" "$out_dir/$service-server.crt.new"; do
  [[ -L "$file" ]] && die "refused to write $file: it is a symbolic link; nothing was changed"
done
# One run at a time per key: a second run would share server.key.new and could
# leave a key that does not match the certificate. mkdir is atomic everywhere.
lock="$key_dir/.make-server-cert.lock"
mkdir "$lock" 2>/dev/null || die "another make-server-cert.sh is running for $service in $env_name ($lock exists); nothing was changed. Wait for it to finish (if none is running, a run was killed: remove the folder $lock)."
work="$(mktemp -d)"
trap 'rm -rf "$work"; rm -f "$key.new"; rmdir "$lock" 2>/dev/null || true' EXIT
# Key identifiers are written explicitly: OpenSSL 4 no longer adds them by default, and during a
# server CA rotation a client holding both CAs (same name) finds this leaf's issuer by them.
printf 'basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=serverAuth\nsubjectAltName=%s\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n' "$san" > "$work/ext"

if [[ "$request_only" -eq 1 ]]; then
  signing_key="$key"
  if [[ "$reuse_key" -eq 1 && -f "$key" ]]; then
    note "re-using the key of the earlier $env_name request (--reuse-key)"
  else
    [[ "$reuse_key" -eq 1 ]] && note "no earlier $env_name key for $service; making one"
    new_ec_key "$key.new"
    signing_key="$key.new"
  fi
  # The request is written from the new key first; the key in place changes only once that worked.
  run_or_die "could not write the certificate request; the key in place was left as it was" \
    openssl req -new -key "$signing_key" -subj "/CN=$common_name" -addext "subjectAltName=$san" \
      -addext "extendedKeyUsage=serverAuth" -addext "keyUsage=critical,digitalSignature" \
      -out "$work/request.csr"
  if [[ "$signing_key" == "$key.new" ]]; then
    if [[ -f "$key" ]]; then
      mv -f "$key" "$key.previous"
      note "a new key was made; the earlier one is kept as server.key.previous in case its certificate is still on its way (--reuse-key keeps one key)"
    fi
    mv -f "$key.new" "$key"
  fi
  mv -f "$work/request.csr" "$out_dir/$service-server.csr"
  chmod 644 "$out_dir/$service-server.csr"
  note "request written: $out_dir/$service-server.csr (send it to the issuer named in the policy file)"
  note "key: $key. It must already be where the $env_name service will read it: run this on the target or in the deployment pipeline, not on a workstation."
  openssl req -in "$out_dir/$service-server.csr" -noout -subject -nameopt RFC2253
  exit 0
fi

check_env_signs_locally "$env_name"
[[ -n "$days" ]] || { [[ "$env_name" == local ]] && days=30 || days=90; }
# Base 10 only: bash would read 08 as a bad octal number.
[[ "$days" =~ ^[1-9][0-9]*$ && "$days" -le 90 ]] || die "--days must be 1 to 90"

# The reuse threshold is the one the certificate check applies: a certificate
# reused here must not be failed by cert-check.sh the next minute.
if [[ -z "$renew_before" && -n "$policy" ]]; then
  [[ -f "$policy" ]] || die "no policy or plan file at $policy"
  renew_before="$(py - "$scripts_dir" "$policy" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import tlslib
data = tlslib.load_yaml(sys.argv[2]) or {}
value = data.get("renew_before_days")
if value is None and isinstance(data.get("certificates"), dict):
    value = data["certificates"].get("renew_before_days")
print("" if value is None else value)
PY
)" || die "cannot read renew_before_days from $policy"
  [[ -n "$renew_before" ]] || note "$policy sets no renew_before_days; using 21"
fi
renew_before="${renew_before:-21}"
[[ "$renew_before" =~ ^(0|[1-9][0-9]?)$ && "$renew_before" -le 89 ]] || die "--renew-before must be 0 to 89 days"
[[ "$days" -gt "$renew_before" ]] || note "--days $days is not more than --renew-before $renew_before: every run will re-issue the certificate"

ca_key="$(ca_dir_for "$env_name")/server-ca.key"
ca_crt="$(ca_dir_for "$env_name")/server-ca.crt"
previous_ca="$(ca_dir_for "$env_name")/server-ca.previous.crt"
[[ -f "$ca_key" && -f "$ca_crt" ]] || die "no $env_name server CA; run certgen-test-ca.sh --env $env_name first"
crt="$out_dir/$service-server.crt"

# openssl prints ::1 as 0:0:0:0:0:0:0:1; both sides go through one normal form.
normal_names() { py -c 'import ipaddress,sys
out = []
for item in sys.stdin.read().replace(" ", "").replace("IPAddress:", "IP:").split(","):
    item = item.strip()
    if item.startswith("IP:"):
        item = "IP:" + str(ipaddress.ip_address(item[3:]))
    if item:
        out.append(item.lower() if item.startswith("DNS:") else item)
print(",".join(sorted(out)))'; }
names_unchanged() {
  local existing wanted
  existing="$(openssl x509 -in "$crt" -noout -ext subjectAltName 2>/dev/null | tail -n +2 | tr -d '\n' | normal_names || true)"
  wanted="$(echo "$san" | normal_names)"
  [[ "$existing" == "$wanted" ]]
}

# During a server CA rotation, consumers move to trusting both CAs at their own
# pace. A leaf from the new CA before they all have would cut them off, so the
# leaf the previous CA signed stays until --after-overlap (or --force).
if [[ "$force" -eq 0 && "$after_overlap" -eq 0 && -f "$crt" && -f "$previous_ca" ]] \
    && ! cert_verifies "$crt" "$ca_crt" && cert_verifies "$crt" "$previous_ca"; then
  if cert_still_valid "$crt" "$renew_before" && [[ -f "$key" ]] && key_matches_cert "$key" "$crt"; then
    names_unchanged || die "the names changed, but $crt was signed by the previous $env_name server CA and the rotation overlap is still on: a certificate from the new CA would be refused by every consumer that trusts only the old one. Once every consumer trusts both CAs, run again with --after-overlap (or --force to re-issue now regardless)."
    note "keeping $crt: it was signed by the previous $env_name server CA, and consumers may not trust the new one yet. Once every consumer trusts both CAs, run with --after-overlap to re-issue it under the new CA."
    print_cert_metadata "$crt"
    exit 0
  fi
  # The old leaf cannot be kept, and a leaf from the new CA would cut off every
  # consumer that trusts only the old one: stop, and say what to do.
  die "$crt was signed by the previous $env_name server CA and the rotation overlap is still on, but it can no longer be kept ($renew_before days or fewer left, or its key in $key_dir is gone or does not match). Nothing was changed. A certificate from the new CA now would be refused by every consumer that still trusts only the old CA. Rebuild each consumer's kit with --server-ca server-ca.current.crt --previous-server-ca server-ca.previous.crt and send it; once every consumer trusts both CAs (each has sent back a verify-result.json from the rebuilt kit with \"ca_overlap\": true and \"ok\": true; see certificates.md, \"CA rotation\"), run again with --after-overlap. --force re-issues now regardless."
fi

if [[ "$force" -eq 0 && -f "$key" ]] && cert_still_valid "$crt" "$renew_before"; then
  if ! names_unchanged; then
    note "re-issuing $crt: the names changed"
  elif ! cert_verifies "$crt" "$ca_crt"; then
    note "re-issuing $crt: it was not signed by the current $env_name server CA"
  elif ! key_matches_cert "$key" "$crt"; then
    note "re-issuing $crt: it does not match the key in $key_dir"
  else
    note "reusing $crt (same names, more than $renew_before days left, signed by the current CA, matches its key)"
    print_cert_metadata "$crt"
    exit 0
  fi
elif [[ "$force" -eq 0 && -f "$crt" ]]; then
  note "re-issuing $crt: $renew_before days or fewer left (or no key)"
fi

# A leaf never outlives its CA.
ca_left="$(cert_days_left "$ca_crt")"
[[ "$ca_left" -ge 1 ]] || die "the $env_name server CA has expired or ends within a day; run certgen-test-ca.sh --env $env_name first"
if [[ "$days" -gt "$ca_left" ]]; then
  note "lifetime cut from $days to $ca_left days: the CA ends then"
  days="$ca_left"
fi

# Build beside the pair in use; replace both together, and only on success.
new_ec_key "$key.new"
run_or_die "could not write the certificate request" \
  openssl req -new -key "$key.new" -subj "/CN=$common_name" -out "$work/csr"
run_or_die "the $env_name server CA could not sign the certificate; the key and certificate in use were left as they were" \
  openssl x509 -req -in "$work/csr" -CA "$ca_crt" -CAkey "$ca_key" -CAcreateserial \
    -subj "/CN=$common_name" -days "$days" -sha256 -extfile "$work/ext" -out "$work/leaf"
cat "$work/leaf" "$ca_crt" > "$crt.new"
chmod 644 "$crt.new"
mv -f "$key.new" "$key"
mv -f "$crt.new" "$crt"
print_cert_metadata "$crt"
