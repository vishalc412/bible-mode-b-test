#!/usr/bin/env bash
# Checks that this consumer can call the producer over mutual TLS, and writes
# verify-result.json for the producer team. Needs bash, curl and OpenSSL 3 or 4
# (not LibreSSL, the openssl macOS ships).
#
# usage: ./verify.sh --expect-fingerprint <sha256> [--kit-fingerprint <sha256>] [--cert <file>] [--key <file>] [--out <file>]
#        ./verify.sh --expect-fingerprint <sha256> [--kit-fingerprint <sha256>] --p12 <bundle.p12> --p12-password-file <file> [--out <file>]
#
#   --kit-fingerprint     the kit fingerprint (the SHA-256 of SHA256SUMS) the
#                         producer team sent you apart from the kit. Before
#                         any key or certificate is read, SHA256SUMS must have
#                         that SHA-256 and every file it lists must match it;
#                         otherwise nothing is done.
#   --expect-fingerprint  the SHA-256 of ca-bundle.pem that the producer team
#                         sent you separately from this kit (ticket, chat or
#                         phone). The script refuses to run unless the file
#                         holds exactly one certificate and matches it: one
#                         extra certificate is enough to be refused. (That one
#                         certificate's own SHA-256 fingerprint is accepted too.)
#                         The one exception is a server CA rotation overlap
#                         (a kit built with --previous-server-ca): exactly two
#                         CA certificates with the same name, the new one
#                         first, and only the SHA-256 of the whole file.
#   --cert                your signed certificate; default client.crt in this
#                         folder, else <producer>-<consumer>.crt in this folder
#   --key                 your key; default the one make-csr.sh made:
#                         $TLS_PRIVATE_DIR/[<env>/]<producer>/<consumer>/client.key
#                         (TLS_PRIVATE_DIR defaults to ~/.tls-migration/private)
#   --p12, --p12-password-file
#                         route B: the PKCS12 bundle and the file holding its
#                         password. The password is read from the file by
#                         openssl and never appears on a command line.
#   Paths you give are relative to where you run the script from.
#
# The request carries the header X-TLS-Migration-Probe with a fresh random
# 8-character tag ([A-Za-z0-9]), also written to verify-result.json as
# probe_tag, so the producer can tell this check from your service's real
# calls. It proves you CAN connect; a tagged call never counts as your service
# having moved.
#
# It also runs the handshake again with openssl, expecting a name the server
# certificate does not carry (P8): that must fail with a host name mismatch,
# and only that failure counts. The result is openssl_wrong_name_refused (also
# written as wrong_name_refused, the name check.sh reads). It shows the
# endpoint and CA behave correctly for a client that checks names; it does
# not test your own service's client, which must keep host name checking on
# and have a test that shows it (consumer.md, step 8).
#
# Before anything is sent, your certificate is checked: its CN must be the
# consumer= of endpoint.txt, it must chain to consumer-ca.crt for client use,
# it must not have expired, and the key must belong to it. If any of these
# fails, nothing is sent, verify-result.json says which, and the exit status
# is not 0.
#
# verify-result.json holds no key material: endpoint, fingerprints, your
# certificate's name, fingerprint and expiry, TLS version, cipher, HTTP status.
set -euo pipefail
caller_dir="$(pwd)"
cd "$(dirname "${BASH_SOURCE[0]}")"
die() { echo "error: $*" >&2; exit 1; }
usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "${BASH_SOURCE[0]}" >&2; exit "${1:-2}"; }
# A path the caller gave is relative to where they ran the script, not to the kit.
from_caller() { case "$1" in /*) echo "$1" ;; *) echo "$caller_dir/$1" ;; esac; }

expected="" cert="" key="" out="verify-result.json" p12="" p12_password="" kit_fingerprint=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --expect-fingerprint) expected="$(echo "${2:-}" | tr -d ': ' | tr 'A-F' 'a-f')"; shift 2 || usage ;;
    --kit-fingerprint) kit_fingerprint="${2:-}"; shift 2 || usage ;;
    --cert) cert="$(from_caller "${2:-}")"; shift 2 || usage ;;
    --key) key="$(from_caller "${2:-}")"; shift 2 || usage ;;
    --out) out="$(from_caller "${2:-}")"; shift 2 || usage ;;
    --p12) p12="$(from_caller "${2:-}")"; shift 2 || usage ;;
    --p12-password-file) p12_password="$(from_caller "${2:-}")"; shift 2 || usage ;;
    --help|-h) usage 0 ;;
    *) usage ;;
  esac
done
[[ -n "$expected" ]] || die "--expect-fingerprint is required: ask the producer team for it over a channel other than this kit"

command -v curl >/dev/null || die "curl is needed and was not found. Ask the person at this machine to install it; an assistant never installs software or changes the machine. Nothing was checked."
command -v openssl >/dev/null || die "OpenSSL 3 or later is needed and was not found. Ask the person at this machine to install it and put it first on PATH; an assistant never installs software or changes the machine. Nothing was checked."
banner="$(openssl version 2>/dev/null || true)"
version="$(echo "$banner" | awk '{print $2}')"
if [[ "$banner" != OpenSSL\ * ]] || ! [[ "${version%%.*}" =~ ^[0-9]+$ && "${version%%.*}" -ge 3 ]]; then
  die "OpenSSL 3 or later is needed; found '$banner' (the openssl macOS ships is LibreSSL). Ask the person at this machine to install OpenSSL 3 and put it first on PATH; an assistant never installs software or changes the machine. Nothing was checked."
fi

# The kit, checked against the fingerprint sent apart from it, before any key is read (D7).
sha256_of() { openssl dgst -sha256 "$1" | awk '{print $NF}'; }
if [[ -n "$kit_fingerprint" ]]; then
  wanted="$(printf '%s' "$kit_fingerprint" | tr -d ': ' | tr 'A-F' 'a-f')"
  [[ "$wanted" =~ ^[0-9a-f]{64}$ ]] || die "--kit-fingerprint must be a SHA-256: 64 hexadecimal characters"
  [[ -f SHA256SUMS && ! -L SHA256SUMS ]] || die "this kit has no SHA256SUMS, so it cannot be checked; do not use it, call the producer team. Nothing was done."
  [[ "$(sha256_of SHA256SUMS)" == "$wanted" ]] || die "the kit fingerprint does not match: SHA256SUMS is not the one the producer team sent. Do not use this kit; call the producer team. Nothing was done."
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ ^([0-9a-f]{64})\ \ (.+)$ ]] || die "SHA256SUMS holds a line that is not '<sha256>  <file>'; do not use this kit. Nothing was done."
    name="${BASH_REMATCH[2]}"
    case "/$name/" in */../*|//*) die "SHA256SUMS names $name, outside the kit; do not use this kit. Nothing was done." ;; esac
    [[ -f "$name" && ! -L "$name" ]] || die "$name, listed in SHA256SUMS, is missing from the kit; do not use it. Nothing was done."
    [[ "$(sha256_of "$name")" == "${BASH_REMATCH[1]}" ]] || die "$name does not match SHA256SUMS: the kit was changed. Do not use it; call the producer team. Nothing was done."
  done < SHA256SUMS
  echo "kit checked: SHA256SUMS matches the fingerprint and every file it lists matches" >&2
fi

# A value from endpoint.txt, without the carriage return a Windows editor adds.
field() { sed -n "s/^$1=//p" endpoint.txt | tr -d '\r' | head -1; }
url="$(field url)"
consumer="$(field consumer)"
producer="$(field producer)"
environment="$(field environment)"
[[ -n "$url" && -n "$consumer" && -n "$producer" ]] || die "endpoint.txt has no url=, consumer= or producer= line"

# The trust check, before anything is sent anywhere.
[[ -f ca-bundle.pem ]] || die "ca-bundle.pem is missing from this kit"
ca_count="$(grep -c -- '-----BEGIN CERTIFICATE-----' ca-bundle.pem || true)"
bundle_sha256="$(openssl dgst -sha256 ca-bundle.pem | awk '{print $NF}')"
actual="$(openssl x509 -in ca-bundle.pem -noout -fingerprint -sha256 | cut -d= -f2 | tr -d : | tr 'A-F' 'a-f')"
# Anything outside the certificate blocks (another block type, stray text) is not a plain CA file.
outside="$(awk '/-----BEGIN CERTIFICATE-----/ { inside = 1; next } /-----END CERTIFICATE-----/ { inside = 0; next } !inside && NF { print }' ca-bundle.pem | wc -l | tr -d ' ')"
scratch=""
cleanup() { [[ -n "$scratch" ]] && rm -rf "$scratch"; return 0; }
trap cleanup EXIT
# Every signal ends the script through its EXIT trap, a closed terminal (HUP)
# too: the unpacked bundle key in the scratch folder never stays behind.
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
scratch="$(umask 077; mktemp -d)"
body="$scratch/body"
ca_overlap=false previous_ca=""
# The one two-certificate form: a server CA rotation overlap. Both are CAs with
# the same name (the new one, then the one it replaced), nothing else is in the
# file, and the value given is the SHA-256 of the whole file.
if [[ "$ca_count" -eq 2 && "$outside" -eq 0 && "$expected" == "$bundle_sha256" ]]; then
  awk -v dir="$scratch" '/-----BEGIN CERTIFICATE-----/ { n++ } n { print > (dir "/ca-" n ".pem") }' ca-bundle.pem
  subject_of() { openssl x509 -in "$1" -noout -subject -nameopt RFC2253 2>/dev/null; }
  is_ca() { openssl x509 -in "$1" -noout -ext basicConstraints 2>/dev/null | grep -q 'CA:TRUE'; }
  previous_ca="$(openssl x509 -in "$scratch/ca-2.pem" -noout -fingerprint -sha256 2>/dev/null | cut -d= -f2 | tr -d : | tr 'A-F' 'a-f')"
  if [[ -n "$(subject_of "$scratch/ca-1.pem")" && "$(subject_of "$scratch/ca-1.pem")" == "$(subject_of "$scratch/ca-2.pem")" ]] \
      && is_ca "$scratch/ca-1.pem" && is_ca "$scratch/ca-2.pem" && [[ -n "$previous_ca" && "$previous_ca" != "$actual" ]]; then
    ca_overlap=true
  fi
fi
if [[ "$ca_overlap" != true ]]; then
  [[ "$ca_count" -eq 1 && "$outside" -eq 0 ]] || die "ca-bundle.pem holds $ca_count certificates (and $outside other line(s)); a kit holds exactly one CA certificate and nothing else (during a server CA rotation: the new and the previous CA of the same name, checked against the SHA-256 of the whole file). Do not use this kit; call the producer team."
  previous_ca=""
fi
# (During an overlap only the whole-file SHA-256 got this far: it is what made ca_overlap true.)
if [[ "$expected" == "$bundle_sha256" || "$expected" == "$actual" ]]; then
  :
else
  die "ca-bundle.pem does not match the fingerprint you were given (file sha256 $bundle_sha256, $ca_count certificate(s)); do not use this kit, call the producer team"
fi

route="A"
if [[ -n "$p12" ]]; then
  route="B"
  [[ -f "$p12" ]] || die "no bundle at $p12"
  [[ -n "$p12_password" && -f "$p12_password" ]] || die "--p12 needs --p12-password-file <the file holding the bundle's password>"
  # The bundle is unpacked into a private scratch folder that is removed when
  # the script ends. The password goes from its file to openssl; it is never an argument.
  ( umask 077
    openssl pkcs12 -in "$p12" -passin "file:$p12_password" -nokeys -clcerts -out "$scratch/client.crt" 2>/dev/null \
      && openssl pkcs12 -in "$p12" -passin "file:$p12_password" -nocerts -noenc -out "$scratch/client.key" 2>/dev/null
  ) || die "could not open $p12 with the password in $p12_password"
  cert="$scratch/client.crt"
  key="$scratch/client.key"
else
  if [[ -z "$cert" ]]; then
    cert="client.crt"
    [[ -f "$cert" || ! -f "$producer-$consumer.crt" ]] || cert="$producer-$consumer.crt"
  fi
  [[ -n "$key" ]] || key="${TLS_PRIVATE_DIR:-$HOME/.tls-migration/private}/${environment:+$environment/}$producer/$consumer/client.key"
  [[ -f "$cert" ]] || die "no certificate at $cert. Save the certificate the producer team sent back as client.crt in this folder (send them your .csr first if you have not), or name it with --cert. Route B: use --p12."
  [[ -f "$key" ]] || die "no key at $key; run ./make-csr.sh first, or name your key with --key"
fi

# Your certificate, before anything is sent: the right name, from this
# producer's consumer CA, for client use, in date, and with its own key.
pub_hash() { [[ -n "$1" ]] && printf '%s\n' "$1" | openssl dgst -sha256 | awk '{print $NF}'; return 0; }
client_cn="$(openssl x509 -in "$cert" -noout -subject -nameopt RFC2253 2>/dev/null | sed -E 's/.*CN=([^,]+).*/\1/')"
cn_ok=false chain_ok=false in_date=false key_ok=false
[[ -n "$client_cn" && "$client_cn" == "$consumer" ]] && cn_ok=true
if [[ -f consumer-ca.crt ]] && openssl verify -no-CApath -no-CAstore -CAfile consumer-ca.crt -purpose sslclient "$cert" >/dev/null 2>&1; then
  chain_ok=true
fi
openssl x509 -in "$cert" -noout -checkend 0 >/dev/null 2>&1 && in_date=true
cert_pub="$(pub_hash "$(openssl x509 -in "$cert" -noout -pubkey 2>/dev/null || true)")"
key_pub="$(pub_hash "$(openssl pkey -in "$key" -pubout -passin pass: 2>/dev/null || true)")"
[[ -n "$cert_pub" && "$cert_pub" == "$key_pub" ]] && key_ok=true
client_checks_ok=false
problems=()
[[ "$cn_ok" == true ]] || problems+=("its CN is '${client_cn:-none}', not this kit's consumer '$consumer'")
[[ "$chain_ok" == true ]] || problems+=("it does not chain to consumer-ca.crt for client use (another producer's or a self-made certificate?)")
[[ "$in_date" == true ]] || problems+=("it has expired")
[[ "$key_ok" == true ]] || problems+=("the key $key does not belong to it")
[[ ${#problems[@]} -eq 0 ]] && client_checks_ok=true

# Host and port, with a bracketed IPv6 literal handled.
hostport="$(echo "$url" | sed -E 's#^https://([^/?]+).*#\1#')"
case "$hostport" in
  \[*\]:*) host="${hostport%%]*}"; host="${host#[}"; port="${hostport##*]:}" ;;
  \[*\]) host="${hostport#[}"; host="${host%]}"; port=443 ;;
  *:*) host="${hostport%:*}"; port="${hostport##*:}" ;;
  *) host="$hostport"; port=443 ;;
esac
case "$host" in *:*) connect="[$host]:$port" ;; *) connect="$host:$port" ;; esac
# Server name indication is for host names only, never an address literal.
sni=()
if [[ "$host" != *:* && "$host" =~ [a-zA-Z] ]]; then sni=(-servername "$host"); fi

# A fresh tag on every run: a fixed value would let anyone's calls pass as this check.
probe_tag="$(openssl rand -hex 4)"
[[ "$probe_tag" =~ ^[A-Za-z0-9]{8}$ ]] || die "could not make a probe tag"
status="" curl_exit=null handshake="" wrong_name="" connection_attempted=false
if [[ "$client_checks_ok" == true ]]; then
  connection_attempted=true
  set +e
  # During an overlap the two CAs share a name. A server certificate without an
  # authority key identifier (OpenSSL 4 no longer adds one by default) leaves
  # some TLS libraries (curl on macOS, for one) trying only the first CA of that
  # name. curl is then given the one of the two kit CAs that openssl verifies
  # the server with; nothing outside the kit is ever trusted.
  curl_ca="ca-bundle.pem"
  if [[ "$ca_overlap" == true ]]; then
    for candidate in "$scratch/ca-1.pem" "$scratch/ca-2.pem"; do
      if openssl s_client -connect "$connect" ${sni[@]+"${sni[@]}"} -CAfile "$candidate" -no-CApath -no-CAstore \
          -cert "$cert" -key "$key" -verify_return_error </dev/null >/dev/null 2>&1; then
        curl_ca="$candidate"
        break
      fi
    done
  fi
  # -q: no ~/.curlrc. https only, and no redirect is followed.
  status="$(curl -q -sS --max-time 15 --proto =https --max-redirs 0 --cacert "$curl_ca" --cert "$cert" --key "$key" -H "X-TLS-Migration-Probe: $probe_tag" \
    -o "$body" -w '%{http_code}' "$url" 2>/dev/null)"
  curl_exit=$?
  handshake="$(openssl s_client -connect "$connect" ${sni[@]+"${sni[@]}"} -CAfile ca-bundle.pem -no-CApath -no-CAstore \
    -cert "$cert" -key "$key" -verify_return_error </dev/null 2>&1)"
  # P8: the same handshake, expecting a name the server certificate does not carry.
  wrong_name="$(openssl s_client -connect "$connect" ${sni[@]+"${sni[@]}"} -CAfile ca-bundle.pem -no-CApath -no-CAstore \
    -cert "$cert" -key "$key" -verify_hostname "wrong-name.tls-migration.invalid" -verify_return_error </dev/null 2>&1)"
  set -e
else
  for problem in "${problems[@]}"; do echo "error: your certificate $cert: $problem" >&2; done
  echo "error: nothing was sent; fix the certificate (save the one the producer team signed for you as client.crt) and run again" >&2
fi
tls_version="$(echo "$handshake" | sed -n 's/^ *Protocol *: *//p' | head -1)"
[[ -n "$tls_version" ]] || tls_version="$(echo "$handshake" | sed -nE 's/^New, (TLSv[0-9.]+).*/\1/p' | head -1)"
cipher="$(echo "$handshake" | sed -nE 's/.*Cipher is ([^ ]+).*/\1/p' | head -1)"
# Only a host name mismatch counts: any other failure (an untrusted CA, an
# expired certificate, no connection) says nothing about names.
if echo "$wrong_name" | grep -qi "hostname mismatch"; then
  wrong_name_refused=true
else
  wrong_name_refused=false
fi
client_sha256="$(openssl x509 -in "$cert" -noout -fingerprint -sha256 2>/dev/null | cut -d= -f2 | tr -d : | tr 'A-F' 'a-f')"
client_expires="$(openssl x509 -in "$cert" -noout -enddate 2>/dev/null | cut -d= -f2)"
ok=false
[[ "$client_checks_ok" == true && "$curl_exit" == 0 && "$status" =~ ^2 ]] && ok=true

# A JSON string value: every control character dropped, backslash and quote escaped.
json() { printf '%s' "$1" | LC_ALL=C tr -d '\000-\037\177' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }
[[ -L "$out" ]] && die "refused to write $out: it is a symbolic link"
cat > "$out" <<JSON
{
  "tool": "verify.sh",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "endpoint": "$(json "$url")",
  "consumer": "$(json "$consumer")",
  "producer": "$(json "$producer")",
  "route": "$route",
  "ca_fingerprint_sha256": "$actual",
  "ca_bundle_sha256": "$bundle_sha256",
  "ca_certificates": $ca_count,
  "ca_overlap": $ca_overlap,
  "previous_ca_fingerprint_sha256": "$previous_ca",
  "client_cn": "$(json "$client_cn")",
  "client_cert_sha256": "$client_sha256",
  "client_cn_matches_consumer": $cn_ok,
  "client_cert_chains_to_consumer_ca": $chain_ok,
  "client_cert_not_expired": $in_date,
  "client_key_matches_cert": $key_ok,
  "client_checks_ok": $client_checks_ok,
  "connection_attempted": $connection_attempted,
  "openssl_wrong_name_refused": $wrong_name_refused,
  "wrong_name_refused": $wrong_name_refused,
  "wrong_name_check": "openssl s_client on this machine, expecting wrong-name.tls-migration.invalid; passes on a host name mismatch only; not a test of the service's own client",
  "client_expires": "$(json "$client_expires")",
  "tls_version": "$(json "${tls_version:-unknown}")",
  "cipher": "$(json "${cipher:-unknown}")",
  "http_status": "$(json "${status:-000}")",
  "curl_exit": $curl_exit,
  "probe_header": "X-TLS-Migration-Probe",
  "probe_tag": "$probe_tag",
  "ok": $ok
}
JSON
echo "verify: ok=$ok status=${status:-000} tls=${tls_version:-unknown} cipher=${cipher:-unknown} openssl wrong name refused=$wrong_name_refused probe tag=$probe_tag -> $out"
[[ "$ok" == true && "$wrong_name_refused" == true ]]
