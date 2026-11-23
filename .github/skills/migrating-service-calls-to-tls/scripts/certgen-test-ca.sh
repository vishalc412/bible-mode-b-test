#!/usr/bin/env bash
# Creates the throwaway certificate authorities for a local or test run.
#
# usage:
#   certgen-test-ca.sh --env local|test --producer <name> --out <public-dir>
#   certgen-test-ca.sh --clean --env <env> [--out <public-dir>]
#
# Creates, for one producer:
#   <prefix>server-ca                         signs server certificates
#   <prefix><producer>-consumers-ca           signs this producer's client certificates only
#   <prefix>negative-test-untrusted-client    for refusal probes; nothing may trust it
# where <prefix> is "local-dev-" in local and "test-" in test.
#
# Keys go to $TLS_PRIVATE_DIR/ca-<env>, mode 0600, outside any repository;
# local and test CAs never share a folder. The trust files go to --out:
#   <out>/server-ca.crt, <out>/<producer>-consumers-ca.crt
# In local, every CA fingerprint is appended to <out>/../ca-fingerprints.txt
# so a staging or production check can recognise it anywhere.
#
# Lifetime: 90 days in local, 180 in test. Safe to run again: a CA with more
# than 45 days left in local, 60 in test, and the expected name is reused.
# Below that it is rotated, early enough that the leaf the old CA signed can
# still be kept for a real overlap (more than make-server-cert.sh's
# --renew-before, 21 days by default, 7 in local-tls-up.sh): a new CA is made,
# the old certificate is kept as <name>.previous.crt until it expires, and the
# trust file in --out holds both (new first), so certificates issued by the
# old CA keep working during the overlap; <name>.current.crt and
# <name>.previous.crt hold each alone. The old CA key is removed.
# After a rotation, what to re-issue depends on the CA:
#   consumer CA  deploy the two-CA <producer>-consumers-ca.crt to the producer
#                first; then sign-csr.sh signs renewals with the new CA, at
#                each consumer's own pace, before the old CA expires.
#   server CA    do NOT re-issue the server certificate yet. Rebuild each kit
#                from server-ca.current.crt with --previous-server-ca
#                server-ca.previous.crt (the kit then trusts both); only
#                after EVERY consumer trusts both CAs run make-server-cert.sh
#                --after-overlap. Until then make-server-cert.sh (and
#                local-tls-up.sh) keep the leaf the previous CA signed, and
#                refuse to run when it can no longer be kept. See
#                certificates.md, "CA rotation".
#
# --clean --env <env> removes every CA, server key, client key, probe
# certificate and route B bundle this toolkit made for that environment under
# TLS_PRIVATE_DIR (including keys kept as .previous, .next or a .new left by
# an interrupted run). It never follows a symbolic link: when TLS_PRIVATE_DIR
# or one of its environment folders is a link, nothing is removed. A route B
# bundle written outside TLS_PRIVATE_DIR (bundles-<env>/made.txt) is listed,
# never removed: delete it by hand. And in
# --out only the CA files this script writes there: server-ca.crt and
# <producer>-consumers-ca.crt, with their .previous.crt and .current.crt forms,
# for the producers whose CAs it finds. It never touches another environment.
# It fails when it finds no key: that means TLS_PRIVATE_DIR is not the folder
# the keys were made in. Client keys made by make-csr.sh without --env belong
# to no environment, so no --clean removes them; they are listed.
# Never installs a CA in the system, a browser or the JVM trust store.
# Staging and production are refused: their CAs live in the company CA, Vault
# or cert-manager, never on a workstation.
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

usage() { print_usage "${BASH_SOURCE[0]}"; exit 2; }

env_name="" producer="" out_dir="" clean=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) env_name="${2:-}"; shift 2 || usage ;;
    --producer) producer="${2:-}"; shift 2 || usage ;;
    --out) out_dir="${2:-}"; shift 2 || usage ;;
    --clean) clean=1; shift ;;
    *) usage ;;
  esac
done

if [[ "$clean" -eq 1 ]]; then
  [[ -n "$env_name" ]] || die "--clean needs --env <local|test|staging|production>: it removes one environment's keys, never another's"
  check_env_name "$env_name"
  removed_keys=0
  remove() {
    [[ -f "$1" ]] || return 0
    case "$1" in *.key|*.key.*|*.p12) removed_keys=$((removed_keys + 1)) ;; esac
    rm -f -- "$1" && note "removed $1"
  }
  # A symbolic link is never followed (S-11): a link where a key folder should
  # be means the folder is not what this toolkit made; nothing is removed.
  [[ -L "$TLS_PRIVATE_DIR" ]] && die "TLS_PRIVATE_DIR ($TLS_PRIVATE_DIR) is a symbolic link; --clean never follows one. Nothing was removed."
  ca_dir="$(ca_dir_for "$env_name")"
  keys_dir="$TLS_PRIVATE_DIR/$env_name"
  probe_dir="$(probe_dir_for "$env_name")"
  bundles_dir="$(bundles_dir_for "$env_name")"
  for dir in "$ca_dir" "$keys_dir" "$probe_dir" "$bundles_dir"; do
    [[ -L "$dir" ]] && die "$dir is a symbolic link; --clean never follows one. Nothing was removed."
  done
  # The producers whose CAs are here: --out loses exactly their trust files, nothing else.
  producers=()
  for file in "$ca_dir"/*-consumers-ca.crt "$ca_dir"/*-consumers-ca.previous.crt; do
    [[ -f "$file" ]] || continue
    name="$(basename "$file")"; name="${name%.previous.crt}"; name="${name%.crt}"; name="${name%-consumers-ca}"
    [[ " ${producers[*]:-} " == *" $name "* ]] || producers+=("$name")
  done
  # Route B bundles: made.txt lists where they were written. Only a name inside
  # the key folder is removed; one anywhere else is listed for a person to delete.
  outside_bundles=""
  if [[ -f "$bundles_dir/made.txt" && ! -L "$bundles_dir/made.txt" ]]; then
    while IFS= read -r bundle; do
      [[ "$bundle" == *.p12 ]] || continue
      case "/$bundle/" in */../*) outside_bundles+="$bundle "; continue ;; esac
      if [[ "$bundle" == "$TLS_PRIVATE_DIR"/* ]]; then
        [[ -L "$bundle" ]] || remove "$bundle"
      else
        outside_bundles+="$bundle "
      fi
    done < "$bundles_dir/made.txt"
  fi
  # Only files this toolkit names are removed, then the folders left empty.
  # Every key it writes ends in .key, or in .key.<state> (.next, .previous,
  # .new): one pattern, so no kept or half-written key is missed.
  for dir in "$ca_dir" "$keys_dir" "$probe_dir" "$bundles_dir"; do
    [[ -d "$dir" ]] || continue
    while IFS= read -r file; do
      remove "$file"
    done < <(find "$dir" -type f \( -name '*.key' -o -name '*.key.*' -o -name '*.crt' -o -name '*.crt.*' -o -name '*.srl' \
               -o -name '*.p12' -o -name '*.p12.new' -o -name '*.password' -o -name '*.csr' -o -name 'made.txt' -o -name 'key-folder-id.txt' \
               -o -name 'repository.txt' \) 2>/dev/null)
    find "$dir" -depth -type d -empty -exec rmdir {} \; 2>/dev/null || true
  done
  # Nothing that looks like a key may survive a clean unnoticed.
  left="$(for dir in "$ca_dir" "$keys_dir" "$probe_dir" "$bundles_dir"; do
            [[ -d "$dir" ]] && find "$dir" -type f -name '*key*' 2>/dev/null; done; true)"
  [[ -z "$left" ]] || die "these files were left in place (not made by this toolkit, or could not be removed); look at them: $(echo "$left" | tr '\n' ' ')"
  if [[ -n "$out_dir" && -d "$out_dir" ]]; then
    for stem in server-ca ${producers[@]+"${producers[@]/%/-consumers-ca}"}; do
      for file in "$out_dir/$stem.crt" "$out_dir/$stem.previous.crt" "$out_dir/$stem.current.crt"; do
        [[ -f "$file" ]] && rm -f -- "$file" && note "removed $file"
      done
    done
  fi
  # make-csr.sh without --env puts a key at <producer>/<consumer>/client.key: in no environment.
  envless=""
  for file in "$TLS_PRIVATE_DIR"/*/*/client.key*; do
    [[ -f "$file" ]] || continue
    top="${file#"$TLS_PRIVATE_DIR"/}"; top="${top%%/*}"
    case "$top" in local|test|staging|production|ca-*|probe-*|bundles-*) continue ;; esac
    envless+="$file "
  done
  [[ -z "$envless" ]] || note "not removed: client keys made by make-csr.sh without --env belong to no environment, so no --clean removes them; look at them and delete them by hand if they are no longer used: $envless"
  [[ -z "$outside_bundles" ]] || note "not removed: route B bundles written outside the key folder (--clean deletes only inside it); delete them by hand if they are no longer used: $outside_bundles"
  [[ "$removed_keys" -gt 0 ]] || die "nothing to clean: no $env_name key under $TLS_PRIVATE_DIR. Is TLS_PRIVATE_DIR the folder the keys were made in? (after local-tls-up.sh it is in tls-migration/local/private-dir.txt; local-tls-up.sh --clean --repo <repo> finds it itself)"
  note "removed $removed_keys key file(s) of environment $env_name"
  exit 0
fi

[[ -n "$out_dir" && -n "$env_name" && -n "$producer" ]] || usage
[[ "$producer" =~ $ID_RE ]] || die "producer name must be lowercase letters, digits and hyphens"
check_env_signs_locally "$env_name"
require_openssl3

prefix="$(ca_prefix "$env_name")"
ca_dir="$(ca_dir_for "$env_name")"
ensure_private_dir "$ca_dir"
make_public_dir "$out_dir"
# A CA is rotated while it still has rotate_days left: more than the leaf's
# --renew-before (21 days by default) plus a real overlap, so the leaf the old
# CA signed can be kept until every consumer trusts the new one.
if [[ "$env_name" == local ]]; then ca_days=90 rotate_days=45; else ca_days=180 rotate_days=60; fi
# A run stopped half-way (Ctrl-C, a kill) leaves no half-written CA key behind.
made_new=()
trap 'rm -f ${made_new[@]+"${made_new[@]}"}' EXIT

# make_ca <file-stem> <common name> <extended key usage or ""> <keep the old one for an overlap: yes|no>
make_ca() {
  local stem="$1" cn="$2" eku="$3" overlap="$4"
  local key="$ca_dir/$stem.key" crt="$ca_dir/$stem.crt" previous="$ca_dir/$stem.previous.crt" ext
  if cert_still_valid "$crt" "$rotate_days" && [[ -f "$key" ]] && [[ "$(cert_cn "$crt")" == "$cn" ]] && key_matches_cert "$key" "$crt"; then
    note "reusing $cn (more than $rotate_days days left)"
  else
    if [[ -f "$crt" ]]; then
      if [[ "$overlap" == yes ]] && cert_still_valid "$crt" 0 && [[ "$(cert_cn "$crt")" == "$cn" ]]; then
        mv -f "$crt" "$previous"
        note "rotating $cn: the old CA certificate is kept as $(basename "$previous") until it expires; its key is removed"
      else
        note "replacing $crt: it is '$(cert_cn "$crt")' or no longer usable"
      fi
    fi
    made_new+=("$key.new" "$crt.new")
    new_ec_key "$key.new"
    ext="$(mktemp)"
    made_new+=("$ext")
    {
      printf '[req]\ndistinguished_name=dn\n[dn]\n[v3_ca]\n'
      echo "basicConstraints=critical,CA:TRUE,pathlen:0"
      echo "keyUsage=critical,keyCertSign,cRLSign"
      echo "subjectKeyIdentifier=hash"
      echo "authorityKeyIdentifier=keyid:always"   # explicit: OpenSSL 4 no longer adds it
      [[ -n "$eku" ]] && echo "extendedKeyUsage=$eku"
    } > "$ext"
    run_or_die "could not create the CA $cn" \
      openssl req -new -x509 -key "$key.new" -subj "/CN=$cn/OU=tls-migration $env_name only" \
        -days "$ca_days" -sha256 -extensions v3_ca -config "$ext" -out "$crt.new" || { rm -f "$ext" "$key.new" "$crt.new"; exit 1; }
    rm -f "$ext"
    mv -f "$key.new" "$key"
    mv -f "$crt.new" "$crt"
    chmod 644 "$crt"
    rm -f "$ca_dir/$stem.srl"
    note "created $cn"
  fi
  # The previous CA is trusted only while it is still valid.
  if [[ -f "$previous" ]] && ! cert_still_valid "$previous" 0; then
    rm -f "$previous"
    note "the previous $cn has expired; removed from the trust file"
  fi
}

# trust_file <file-stem> <public name>: the current CA, then the previous one during an overlap.
trust_file() {
  local stem="$1" name="$2" file
  for file in "$out_dir/$name.crt" "$out_dir/$name.previous.crt" "$out_dir/$name.current.crt"; do
    [[ -L "$file" ]] && die "refused to write $file: it is a symbolic link; nothing was written"
  done
  if [[ -f "$ca_dir/$stem.previous.crt" ]]; then
    cat "$ca_dir/$stem.crt" "$ca_dir/$stem.previous.crt" > "$out_dir/$name.crt"
    cp "$ca_dir/$stem.previous.crt" "$out_dir/$name.previous.crt"
    cp "$ca_dir/$stem.crt" "$out_dir/$name.current.crt"
    chmod 644 "$out_dir/$name.previous.crt" "$out_dir/$name.current.crt"
    note "$out_dir/$name.crt holds two CAs (rotation overlap): list the name twice in the plan's expect_only; a kit is built from $name.current.crt"
  else
    cp "$ca_dir/$stem.crt" "$out_dir/$name.crt"
    rm -f "$out_dir/$name.previous.crt" "$out_dir/$name.current.crt"
  fi
  chmod 644 "$out_dir/$name.crt"
}

make_ca "server-ca" "${prefix}server-ca" "" yes
make_ca "$producer-consumers-ca" "${prefix}${producer}-consumers-ca" "clientAuth" yes
make_ca "negative-ca" "${prefix}negative-test-untrusted-client" "clientAuth" no

# Public parts only. The negative CA is not copied: nothing may trust it.
trust_file "server-ca" "server-ca"
trust_file "$producer-consumers-ca" "$producer-consumers-ca"

if [[ "$env_name" == "local" ]]; then
  fingerprints="$(cd "$out_dir/.." && pwd)/ca-fingerprints.txt"
  [[ -L "$fingerprints" ]] && die "refused to write $fingerprints: it is a symbolic link"
  touch "$fingerprints"
  for crt in "$ca_dir/server-ca.crt" "$ca_dir/$producer-consumers-ca.crt" "$ca_dir/negative-ca.crt"; do
    line="$(openssl x509 -in "$crt" -noout -fingerprint -sha256 | cut -d= -f2 | tr -d : | tr 'A-F' 'a-f') $(openssl x509 -in "$crt" -noout -subject -nameopt RFC2253 | sed 's/^subject=//')"
    grep -qxF "$line" "$fingerprints" || echo "$line" >> "$fingerprints"
  done
  chmod 644 "$fingerprints"
fi

print_cert_metadata "$out_dir/server-ca.crt" "$out_dir/$producer-consumers-ca.crt"
