#!/usr/bin/env bash
# Makes the client certificates the probes need.
#
# usage:
#   make-probe-certs.sh --env local|test --producer <p> [--allowlist <allowed-consumers.yaml>]
#   make-probe-certs.sh --request-only --env staging|production --producer <p> --out <requests-dir> [--force]
#
#   probe-unlisted   CN=tls-probe-unlisted, from the producer's consumer CA. It
#                    is never in allowed-consumers.yaml: must get 403 (P4)
#   probe-untrusted  CN=tls-probe-untrusted, from a CA nothing trusts: must be
#                    refused at the handshake (P3)
#   probe-allowed    CN=tls-probe-allowed, from the producer's consumer CA: the
#                    probe identity for P1 where the producer run holds no
#                    consumer's key (every environment but local). Made only
#                    when allowed-consumers.yaml lists the id tls-probe-allowed.
#
# local and test: the script signs all three with the throwaway CAs.
# staging and production (--request-only): only a person at a terminal, who
# types the environment's name when asked (input that is not a terminal is
# refused; an assistant writes the command into tls-migration/requests/ for the
# target's owners instead). The keys are made here, at the probe
# location; <out>/probe-unlisted.csr and <out>/probe-allowed.csr go to the real
# consumer issuer (the signed files come back as probe-unlisted.crt and
# probe-allowed.crt in the probe folder); probe-untrusted is signed on the spot
# by a throwaway CA whose key is discarded, since nothing may trust it anyway.
# A second --request-only is refused once a signed probe-unlisted.crt or
# probe-allowed.crt is in the probe folder, and while their keys exist (their
# requests are still out): new keys would orphan the signed certificates or
# the requests on their way. --force makes new keys and requests anyway (the
# signed certificates are removed, since they no longer match).
# Probe certificates live 7 days: re-run this script before each probe run
# that is more than a week after the last one.
#
# Everything lives in $TLS_PRIVATE_DIR/probe-<env>/<producer>/ (the probe plan's
# probe_certs), is used only by probe-tls.sh, and is never mounted by a workload.
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

usage() { print_usage "${BASH_SOURCE[0]}"; exit 2; }
env_name="" producer="" allowlist="" request_only=0 out_dir="" force=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) env_name="${2:-}"; shift 2 || usage ;;
    --producer) producer="${2:-}"; shift 2 || usage ;;
    --allowlist) allowlist="${2:-}"; shift 2 || usage ;;
    --request-only) request_only=1; shift ;;
    --out) out_dir="${2:-}"; shift 2 || usage ;;
    --force) force=1; shift ;;
    *) usage ;;
  esac
done
[[ -n "$env_name" && -n "$producer" ]] || usage
[[ "$producer" =~ $ID_RE ]] || die "producer name must be lowercase letters, digits and hyphens"
check_env_name "$env_name"
require_openssl3

# A person types the environment's name before a staging or production key is made (D8).
[[ "$request_only" -eq 1 ]] && confirm_environment "$env_name" "the probe keys and requests for $producer"
probe_dir="$(probe_dir_for "$env_name" "$producer")"
ensure_private_dir "$probe_dir"
work="$(mktemp -d)"
# A run stopped half-way (Ctrl-C, a kill, a closed terminal) leaves no
# half-written key behind: every signal ends the script through this trap.
trap 'rm -rf "$work"; rm -f "$probe_dir"/probe-*.key.new' EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
# Key identifiers are written explicitly: OpenSSL 4 no longer adds them by default, and a client
# that holds two CAs of the same name (a rotation) picks the issuer by them.
printf 'basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=clientAuth\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n' > "$work/ext"

if [[ "$request_only" -eq 1 ]]; then
  [[ -n "$out_dir" ]] || die "--request-only needs --out <folder for the two requests>"
  for name in probe-unlisted probe-allowed; do
    if [[ -f "$probe_dir/$name.crt" && "$force" -eq 0 ]]; then
      die "$probe_dir/$name.crt is already signed: new keys now would make it useless, so nothing was changed. If the requests really must be made again (a lost or leaked probe key), run with --force and send the new requests."
    fi
  done
  for name in probe-unlisted probe-allowed; do
    if [[ -f "$probe_dir/$name.key" && "$force" -eq 0 ]]; then
      die "$probe_dir/$name.key exists: its request is probably still with the issuer, and a new key now would make the certificate that comes back useless, so nothing was changed. Put the signed certificate in $probe_dir as $name.crt when it arrives; if the request was lost, run with --force and send the new requests."
    fi
  done
  make_public_dir "$out_dir"
  for name in probe-unlisted probe-allowed; do
    [[ -L "$out_dir/$name.csr" ]] && die "refused to write $out_dir/$name.csr: it is a symbolic link; nothing was changed"
  done
  for name in probe-unlisted probe-allowed; do
    new_ec_key "$probe_dir/$name.key.new"
    run_or_die "could not write the request for $name" \
      openssl req -new -key "$probe_dir/$name.key.new" -subj "/CN=tls-$name" -out "$out_dir/$name.csr"
    mv -f "$probe_dir/$name.key.new" "$probe_dir/$name.key"
    chmod 644 "$out_dir/$name.csr"
    rm -f "$probe_dir/$name.crt"
  done
  # The untrusted pair: its CA exists only for this command.
  new_ec_key "$work/ca.key"
  run_or_die "could not make the throwaway CA" \
    openssl req -new -x509 -key "$work/ca.key" -subj "/CN=$env_name-negative-test-untrusted-client/OU=tls-migration probe only" \
      -days 8 -addext "basicConstraints=critical,CA:TRUE,pathlen:0" -addext "keyUsage=critical,keyCertSign" \
      -addext "subjectKeyIdentifier=hash" -addext "authorityKeyIdentifier=keyid:always" -out "$work/ca.crt"
  new_ec_key "$probe_dir/probe-untrusted.key.new"
  run_or_die "could not write the request for probe-untrusted" \
    openssl req -new -key "$probe_dir/probe-untrusted.key.new" -subj "/CN=tls-probe-untrusted" -out "$work/untrusted.csr"
  run_or_die "could not sign probe-untrusted" \
    openssl x509 -req -in "$work/untrusted.csr" -CA "$work/ca.crt" -CAkey "$work/ca.key" -CAcreateserial -days 7 -sha256 \
      -extfile "$work/ext" -out "$work/probe-untrusted.crt"
  mv -f "$probe_dir/probe-untrusted.key.new" "$probe_dir/probe-untrusted.key"
  mv -f "$work/probe-untrusted.crt" "$probe_dir/probe-untrusted.crt"
  chmod 644 "$probe_dir/probe-untrusted.crt"
  echo "requests: $out_dir/probe-unlisted.csr, $out_dir/probe-allowed.csr"
  echo "send both to the issuer of this producer's consumer certificates. tls-probe-allowed must be in allowed-consumers.yaml; tls-probe-unlisted must never be."
  echo "put the signed certificates in $probe_dir as probe-unlisted.crt and probe-allowed.crt"
  exit 0
fi

check_env_signs_locally "$env_name"

# issue <name> <cn> <ca stem>
issue() {
  local name="$1" cn="$2" stem="$3"
  local ca_key ca_crt
  ca_key="$(ca_dir_for "$env_name")/$stem.key" ca_crt="$(ca_dir_for "$env_name")/$stem.crt"
  [[ -f "$ca_key" && -f "$ca_crt" ]] || die "no CA $stem; run certgen-test-ca.sh --env $env_name first"
  new_ec_key "$probe_dir/$name.key.new"
  run_or_die "could not write the request for $name" \
    openssl req -new -key "$probe_dir/$name.key.new" -subj "/CN=$cn" -out "$work/$name.csr" || { rm -f "$probe_dir/$name.key.new"; exit 1; }
  run_or_die "could not sign $name" \
    openssl x509 -req -in "$work/$name.csr" -CA "$ca_crt" -CAkey "$ca_key" -CAcreateserial -days 7 -sha256 \
      -extfile "$work/ext" -out "$work/$name.crt" || { rm -f "$probe_dir/$name.key.new"; exit 1; }
  mv -f "$probe_dir/$name.key.new" "$probe_dir/$name.key"
  mv -f "$work/$name.crt" "$probe_dir/$name.crt"
  chmod 644 "$probe_dir/$name.crt"
  print_cert_metadata "$probe_dir/$name.crt"
}

issue probe-unlisted tls-probe-unlisted "$producer-consumers-ca"
issue probe-untrusted tls-probe-untrusted negative-ca
made="$probe_dir/probe-unlisted.crt, $probe_dir/probe-untrusted.crt"
if [[ -n "$allowlist" ]]; then
  [[ -f "$allowlist" ]] || die "no allowlist at $allowlist"
  if grep -Eq '^[[:space:]]*-?[[:space:]]*id:[[:space:]]*"?tls-probe-allowed"?[[:space:]]*(#.*)?$' "$allowlist"; then
    issue probe-allowed tls-probe-allowed "$producer-consumers-ca"
    made="$made, $probe_dir/probe-allowed.crt"
  else
    rm -f "$probe_dir/probe-allowed.crt" "$probe_dir/probe-allowed.key"
    [[ "$env_name" == local ]] || note "no probe-allowed certificate: $allowlist does not list the id tls-probe-allowed (needed for P1 outside local)"
  fi
fi
echo "probe certificates: $made"
