#!/usr/bin/env bash
# One command for a producer and its consumers on a developer laptop.
#
# usage:
#   local-tls-up.sh --repo <repo> --producer <p> --allowlist <allowed-consumers.yaml> --names <list>
#                   [--after-overlap] [--force]
#   local-tls-up.sh --clean --repo <repo>
#
#   --names  every name the consumers use locally, e.g.
#            "localhost,127.0.0.1,::1,inventory,host.docker.internal"
#   --after-overlap
#            after a server CA rotation: re-issue the server certificate under
#            the new CA (make-server-cert.sh --after-overlap). Only once every
#            consumer trusts both CAs; until then the old leaf is kept.
#   --force  use the exported TLS_PRIVATE_DIR even though it is not this
#            repository's key folder (see "One key folder per repository")
#
# Creates (or reuses while valid) the local-dev CAs, the producer's server
# certificate, a key and signed client certificate for every consumer in the
# allowlist, and the refusal-probe certificates. Writes:
#   <repo>/tls-migration/local/certs/       public certificates only:
#       server-ca.crt, <producer>-consumers-ca.crt, <producer>-server.crt,
#       <producer>-<consumer>.crt
#   <repo>/tls-migration/local/ca-fingerprints.txt
#   <repo>/tls-migration/local/certs-to-check.yaml   the plan cert-check.sh reads;
#       run it for a second producer and that producer's entries are added
#   <repo>/tls-migration/local/private-dir.txt       the key folder (a path, no secret)
#   <repo>/tls-migration/local/key-folder-id.txt     which key folder is this
#       repository's (a random id, also kept in $TLS_PRIVATE_DIR/local/)
# Keys stay in $TLS_PRIVATE_DIR, outside the repository:
#   $TLS_PRIVATE_DIR/local/<producer>/server.key
#   $TLS_PRIVATE_DIR/local/<producer>/<consumer>/client.key
#   $TLS_PRIVATE_DIR/probe-local/<producer>/
# When TLS_PRIVATE_DIR is unset, the folder in private-dir.txt is used only when
# this toolkit made it for this repository: under ~/.tls-migration/private/,
# no symbolic link on the way, and holding the toolkit's mark naming this
# repository (local/repository.txt), or being this repository's default
# folder. A repository file never decides where keys go: any other recorded
# folder is ignored, with a note, and the default is used:
# ~/.tls-migration/private/<repo name>-<8 hex of its path>. Later commands need
# the same folder:  export TLS_PRIVATE_DIR="$(cat tls-migration/local/private-dir.txt)"
#
# One key folder per repository: a TLS_PRIVATE_DIR still exported from another
# repository would reuse that repository's CAs and replace its consumers' keys.
# So the run stops, unless --force, when the exported folder holds another
# repository's key folder id, holds local keys of unknown origin, or is not
# the folder recorded for this repository while that one still holds its keys.
#
# Adds tls-migration/local/ to the repository's .gitignore if it is missing.
# Nothing is written through a symbolic link: a file or folder under
# tls-migration/local/ (or .gitignore) that is a link stops the run.
# Safe to run again: anything the current CA did not sign, or that no longer
# matches its key, is re-issued. --clean removes every local key and
# certificate this command made, from the folder recorded in private-dir.txt
# only, and only when that folder is verified as above or equals the exported
# TLS_PRIVATE_DIR (otherwise nothing is removed); it never follows a symbolic
# link. The fingerprint list stays, so a leaked local CA is still recognised later.
# Never installs a CA in the system, a browser or the JVM.

# Before _common.sh, which refuses an unset TLS_PRIVATE_DIR: one folder per repository.
lt_repo="" lt_clean=0 lt_force=0 lt_recorded="" lt_recorded_raw="" lt_exported="${TLS_PRIVATE_DIR:-}"
lt_args=("$@")
for ((i = 0; i < ${#lt_args[@]}; i++)); do
  case "${lt_args[i]}" in
    --repo) lt_repo="${lt_args[i + 1]:-}" ;;
    --clean) lt_clean=1 ;;
    --force) lt_force=1 ;;
  esac
done
# Is <folder>, read from the repository's private-dir.txt, a key folder this
# toolkit made for this repository (D4)? The exported TLS_PRIVATE_DIR, or a
# folder under ~/.tls-migration/private/ reached without a symbolic link that
# carries this repository's mark, or this repository's default folder.
lt_verified() {   # <folder>
  local folder="$1" base rest part current
  [[ -n "$folder" ]] || return 1
  [[ -n "$lt_exported" && "$folder" == "$lt_exported" ]] && return 0
  [[ "$folder" == /* ]] || return 1
  case "$folder/" in */../*|*/./*|*//*) return 1 ;; esac
  base="$HOME/.tls-migration/private"
  [[ "$folder" == "$base"/* && -d "$base" && ! -L "$base" && ! -L "$HOME/.tls-migration" ]] || return 1
  rest="${folder#"$base"/}/" current="$base"
  while [[ -n "$rest" ]]; do
    part="${rest%%/*}" rest="${rest#*/}"
    [[ -n "$part" ]] || continue
    current="$current/$part"
    [[ -L "$current" ]] && return 1
  done
  [[ -d "$folder" ]] || return 1
  [[ "$folder" == "$lt_default" ]] && return 0
  [[ ! -L "$folder/local" && ! -L "$folder/local/repository.txt" ]] || return 1
  [[ "$(head -1 "$folder/local/repository.txt" 2>/dev/null || true)" == "$repo_abs" ]]
}
if [[ -n "$lt_repo" && -d "$lt_repo" ]]; then
  repo_abs="$(cd "$lt_repo" && pwd -P)"
  lt_default="$HOME/.tls-migration/private/$(basename "$repo_abs")-$(printf %s "$repo_abs" | openssl dgst -sha256 | awk '{print substr($NF, 1, 8)}')"
  record_file="$repo_abs/tls-migration/local/private-dir.txt"
  if [[ -f "$record_file" && ! -L "$record_file" && -s "$record_file" ]]; then
    lt_recorded_raw="$(head -1 "$record_file")"
  fi
  if lt_verified "$lt_recorded_raw"; then
    lt_recorded="$lt_recorded_raw"
  elif [[ -n "$lt_recorded_raw" ]]; then
    echo "note: ignoring the key folder in tls-migration/local/private-dir.txt ($lt_recorded_raw): a file in the repository never decides where keys go. It is used only when it is the exported TLS_PRIVATE_DIR, or a folder this toolkit made for this repository under ~/.tls-migration/private/." >&2
  fi
  if [[ "$lt_clean" -eq 1 ]]; then
    # Only the folder this repository recorded, and only once verified: never whatever happens to be exported.
    if [[ -z "$lt_recorded_raw" ]]; then
      echo "error: nothing to clean: $repo_abs has no tls-migration/local/private-dir.txt, so no key folder is recorded for it. Nothing was removed (an exported TLS_PRIVATE_DIR is never cleaned on another repository's behalf)." >&2
      exit 1
    fi
    if [[ -z "$lt_recorded" ]]; then
      echo "error: the key folder recorded for this repository ($lt_recorded_raw) is not one this toolkit made for it (not under ~/.tls-migration/private/ with this repository's mark), so nothing was removed. If it really is this repository's key folder, export TLS_PRIVATE_DIR=$lt_recorded_raw and run --clean again." >&2
      exit 1
    fi
    if [[ -n "$lt_exported" && "$lt_exported" != "$lt_recorded" ]]; then
      echo "note: ignoring the exported TLS_PRIVATE_DIR ($lt_exported); --clean uses the folder recorded for this repository, $lt_recorded" >&2
    fi
    TLS_PRIVATE_DIR="$lt_recorded"
  elif [[ -z "$lt_exported" ]]; then
    TLS_PRIVATE_DIR="${lt_recorded:-$lt_default}"
  fi
  export TLS_PRIVATE_DIR
fi
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

usage() { print_usage "${BASH_SOURCE[0]}"; exit 2; }
repo="" producer="" allowlist="" names="" clean=0 overlap_flag=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) repo="${2:-}"; shift 2 || usage ;;
    --producer) producer="${2:-}"; shift 2 || usage ;;
    --allowlist) allowlist="${2:-}"; shift 2 || usage ;;
    --names) names="${2:-}"; shift 2 || usage ;;
    --clean) clean=1; shift ;;
    --force) shift ;;
    --after-overlap) overlap_flag=(--after-overlap); shift ;;
    *) usage ;;
  esac
done
[[ -n "$repo" ]] || usage
[[ -d "$repo" ]] || die "no repository at $repo"
repo="$(cd "$repo" && pwd -P)"
local_dir="$repo/tls-migration/local"
certs="$local_dir/certs"
# Nothing under tls-migration/local/ may lead a write or a delete elsewhere (D2).
for path in "$repo/tls-migration" "$local_dir" "$certs" "$local_dir/requests" "$local_dir/plan.d"; do
  refuse_link_path "$repo" "$path"
done

id_file="$local_dir/key-folder-id.txt"
folder_id_file="$TLS_PRIVATE_DIR/local/key-folder-id.txt"
repo_id="$(head -1 "$id_file" 2>/dev/null || true)"
folder_id="$(head -1 "$folder_id_file" 2>/dev/null || true)"

if [[ "$clean" -eq 1 ]]; then
  if [[ -n "$folder_id" && "$folder_id" != "$repo_id" && "$lt_force" -eq 0 ]]; then
    die "the folder recorded for this repository ($TLS_PRIVATE_DIR) now holds another repository's keys (its key folder id differs); nothing was removed. --force cleans it anyway."
  fi
  note "key folder: $TLS_PRIVATE_DIR"
  [[ -L "$TLS_PRIVATE_DIR" ]] && die "the key folder $TLS_PRIVATE_DIR is a symbolic link; --clean never follows one. Nothing was removed."
  "$scripts_dir/certgen-test-ca.sh" --clean --env local --out "$certs"
  for file in "$certs"/*.crt "$local_dir"/requests/*.csr "$local_dir"/plan.d/*.part "$local_dir/certs-to-check.yaml" "$local_dir/private-dir.txt" "$id_file"; do
    [[ -f "$file" ]] && rm -f -- "$file" && note "removed $file"
  done
  rmdir "$certs" "$local_dir/requests" "$local_dir/plan.d" 2>/dev/null || true
  note "kept $local_dir/ca-fingerprints.txt: it lets a later check recognise these CAs if they leaked"
  exit 0
fi

[[ -n "$producer" && -n "$allowlist" && -n "$names" ]] || usage
[[ "$producer" =~ $ID_RE ]] || die "producer name must be lowercase letters, digits and hyphens"
[[ -f "$allowlist" ]] || die "no allowlist at $allowlist"
require_openssl3
# The key folder may not sit inside this repository, with or without version control.
refuse_under "$TLS_PRIVATE_DIR" "$repo"

# Is TLS_PRIVATE_DIR this repository's key folder? Decided by the id both keep,
# not by the path, so a repository moved or copied together with its keys
# still matches; another repository's folder never does.
if [[ "$lt_force" -eq 0 ]]; then
  if [[ -n "$folder_id" && "$folder_id" != "$repo_id" ]]; then
    die "TLS_PRIVATE_DIR ($TLS_PRIVATE_DIR) is the key folder of another repository (its id is not this repository's). Is it still exported from there? Using it would reuse that repository's CAs and replace its consumers' keys. Unset it (this repository then uses ${lt_recorded:-a folder of its own}), or pass --force to share it on purpose."
  fi
  # A folder made before key folder ids existed is accepted when it is the one this repository recorded.
  if [[ -z "$folder_id" && "$lt_recorded" != "$TLS_PRIVATE_DIR" && ( -d "$TLS_PRIVATE_DIR/ca-local" || -d "$TLS_PRIVATE_DIR/local" ) ]]; then
    die "TLS_PRIVATE_DIR ($TLS_PRIVATE_DIR) already holds local keys that no repository has claimed. If they are this repository's, pass --force; else unset TLS_PRIVATE_DIR or pick an empty folder."
  fi
  if [[ -z "$folder_id" && -n "$lt_recorded" && "$lt_recorded" != "$TLS_PRIVATE_DIR" && -n "$repo_id" \
        && "$(head -1 "$lt_recorded/local/key-folder-id.txt" 2>/dev/null || true)" == "$repo_id" ]]; then
    die "this repository's keys are in $lt_recorded (tls-migration/local/private-dir.txt), but TLS_PRIVATE_DIR is $TLS_PRIVATE_DIR. Unset TLS_PRIVATE_DIR or export the recorded folder; --force moves this repository to the new folder (new CAs and keys)."
  fi
fi
ensure_private_dir "$TLS_PRIVATE_DIR"
# With --force the repository adopts the folder's id, so later runs match it.
[[ -n "$folder_id" ]] && repo_id="$folder_id"
[[ -n "$repo_id" ]] || repo_id="$(openssl rand -hex 16)"

# Every file this run writes or changes in the repository, checked before the first write (D2).
for path in "$repo/.gitignore" "$local_dir/ca-fingerprints.txt" "$local_dir/certs-to-check.yaml" "$local_dir/private-dir.txt" \
            "$id_file" "$local_dir/plan.d/$producer.certs.part" "$local_dir/plan.d/$producer.stores.part"; do
  refuse_link_path "$repo" "$path"
done
for path in "$certs"/* "$local_dir"/requests/* "$local_dir"/plan.d/*; do
  [[ -L "$path" ]] && die "refused: $path is a symbolic link (a file in the repository may not lead the toolkit elsewhere); nothing was written"
done
# The parts of other producers are joined into the plan as they are, so each
# must be what this script writes: a regular file whose every line belongs to
# a list entry. Checked now, before any key is made.
for part in "$local_dir"/plan.d/*.part; do
  [[ -e "$part" || -L "$part" ]] || continue
  [[ -L "$part" || ! -f "$part" ]] && die "refused: $part is not a regular file; nothing was written"
  if grep -qvE '^    ?[a-z_]+: |^  - [a-z_]+: ' "$part"; then
    die "refused: $part holds a line local-tls-up.sh never writes; remove the file (it is re-made for its producer on its next run). Nothing was written."
  fi
done

# Public files: readable by a container user or a teammate, unlike the keys.
( umask 022; mkdir -p "$certs" "$local_dir/requests" "$local_dir/plan.d" )
chmod 755 "$local_dir" "$certs" "$local_dir/requests" "$local_dir/plan.d"

gitignore="$repo/.gitignore"
if ! grep -qxF "tls-migration/local/" "$gitignore" 2>/dev/null; then
  # A file without a final newline would glue the rule onto its last line.
  [[ -s "$gitignore" && -n "$(tail -c 1 "$gitignore")" ]] && echo >> "$gitignore"
  echo "tls-migration/local/" >> "$gitignore"
  note "added tls-migration/local/ to .gitignore"
fi

"$scripts_dir/certgen-test-ca.sh" --env local --producer "$producer" --out "$certs" >/dev/null
# --renew-before matches the plan's renew_before_days below.
"$scripts_dir/make-server-cert.sh" --env local --service "$producer" --names "$names" --out "$certs" --renew-before 7 ${overlap_flag[@]+"${overlap_flag[@]}"} >/dev/null

consumer_list="$(py - "$scripts_dir" "$allowlist" "$producer" <<'PY'
import re
import sys
sys.path.insert(0, sys.argv[1])
import tlslib
data = tlslib.load_yaml(sys.argv[2]) or {}
if str(data.get("producer") or "") != sys.argv[3]:
    sys.exit(f"{sys.argv[2]} is the allowlist of producer '{data.get('producer')}', not of '{sys.argv[3]}'")
ids = [str(c["id"]) for c in data.get("consumers") or [] if isinstance(c, dict) and c.get("id")]
bad = [i for i in ids if not re.fullmatch(r"[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?", i)]
if bad:
    sys.exit(f"consumer ids must be lowercase letters, digits and hyphens: {bad}")
print(" ".join(i for i in ids if not i.startswith("tls-probe-")))
PY
)" || die "the allowlist cannot be used (see above)"
[[ -n "$consumer_list" ]] || die "the allowlist names no consumers"
consumers=()
for consumer in $consumer_list; do consumers+=("$consumer"); done

consumer_ca="$(ca_dir_for local)/$producer-consumers-ca.crt"
for consumer in "${consumers[@]}"; do
  crt="$certs/$producer-$consumer.crt"
  key="$(client_key_dir local "$producer" "$consumer")/client.key"
  if cert_still_valid "$crt" 7 && [[ -f "$key" ]] && cert_verifies "$crt" "$consumer_ca" && key_matches_cert "$key" "$crt"; then
    note "reusing the certificate of $consumer"
    continue
  fi
  [[ -f "$crt" ]] && note "re-issuing the certificate of $consumer (expiring, not from the current CA, or not matching its key)"
  "$scripts_dir/make-csr.sh" --consumer "$consumer" --producer "$producer" --env local --out "$local_dir/requests" --replace >/dev/null 2>&1 \
    || die "could not make a key and request for $consumer"
  py "$scripts_dir/sign_csr.py" --env local --producer "$producer" --csr "$local_dir/requests/$producer-$consumer.csr" \
    --allowlist "$allowlist" --out "$certs" >/dev/null
  rm -f "$(dirname "$key")/client.key.previous"
done
"$scripts_dir/make-probe-certs.sh" --env local --producer "$producer" --allowlist "$allowlist" >/dev/null

# The plan cert-check.sh reads, one part per producer so a second producer adds
# to it. Paths are relative to the repository.
ca_names() {   # <trust file> <CA name>: the name once per certificate in the file
  local count out="" i
  count="$(grep -c 'BEGIN CERTIFICATE' "$1")"
  for ((i = 0; i < count; i++)); do out+="${out:+, }$2"; done
  echo "$out"
}
{
  echo "  - path: tls-migration/local/certs/$producer-server.crt"
  echo "    role: server"
  echo "    issuer_ca: tls-migration/local/certs/server-ca.crt"
  # Quoted: an IPv6 name such as ::1 is not valid as a bare YAML value.
  echo "    names: [$(echo "$names" | tr -d '[:space:]' | sed -e 's/^/"/' -e 's/$/"/' -e 's/,/", "/g')]"
  for consumer in "${consumers[@]}"; do
    echo "  - path: tls-migration/local/certs/$producer-$consumer.crt"
    echo "    role: client"
    echo "    issuer_ca: tls-migration/local/certs/$producer-consumers-ca.crt"
    echo "    consumer_id: $consumer"
  done
} > "$local_dir/plan.d/$producer.certs.part"
{
  echo "  - path: tls-migration/local/certs/$producer-consumers-ca.crt"
  echo "    used_by: $producer, to check client certificates"
  echo "    expect_only: [$(ca_names "$certs/$producer-consumers-ca.crt" "local-dev-$producer-consumers-ca")]"
} > "$local_dir/plan.d/$producer.stores.part"
plan="$local_dir/certs-to-check.yaml"
refuse_link_path "$repo" "$plan"
{
  echo "# Written by local-tls-up.sh. Checked by cert-check.sh and check.sh."
  echo "environment: local"
  echo "renew_before_days: 7"
  echo "max_lifetime_days: 30"
  echo "local_fingerprints: tls-migration/local/ca-fingerprints.txt"
  echo "certificates:"
  cat "$local_dir"/plan.d/*.certs.part
  echo "trust_stores:"
  cat "$local_dir"/plan.d/*.stores.part
  echo "  - path: tls-migration/local/certs/server-ca.crt"
  echo "    used_by: consumers, to check the server"
  echo "    expect_only: [$(ca_names "$certs/server-ca.crt" "local-dev-server-ca")]"
} > "$plan"
chmod 644 "$plan" "$local_dir"/plan.d/*.part

for path in "$plan" "$local_dir/private-dir.txt" "$id_file"; do refuse_link_path "$repo" "$path"; done
echo "$TLS_PRIVATE_DIR" > "$local_dir/private-dir.txt"
echo "$repo_id" > "$id_file"
chmod 644 "$local_dir/private-dir.txt" "$id_file"
( umask 077; echo "$repo_id" > "$folder_id_file" )
# The toolkit's mark: this key folder was made for this repository (D4).
( umask 077; echo "$repo" > "$TLS_PRIVATE_DIR/local/repository.txt" )

echo "local certificates for $producer and consumers: ${consumers[*]}"
shown=("$certs/server-ca.crt" "$certs/$producer-consumers-ca.crt" "$certs/$producer-server.crt")
for consumer in "${consumers[@]}"; do shown+=("$certs/$producer-$consumer.crt"); done
print_cert_metadata "${shown[@]}"
echo "keys: $TLS_PRIVATE_DIR (outside the repository; never open them)"
echo "for later commands: export TLS_PRIVATE_DIR=\"\$(cat tls-migration/local/private-dir.txt)\""
echo "plan for cert-check.sh: tls-migration/local/certs-to-check.yaml"
