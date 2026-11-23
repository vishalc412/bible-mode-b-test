#!/usr/bin/env bash
# First-pass inventory for the HTTP -> HTTPS playbook.
# Read-only: it never modifies the repository.
#
# usage: find-http-urls.sh <repo-path> [allowlist-file]
#   allowlist-file: one fixed string per line. Any output line containing one of
#   them is dropped from every section. Because each output line starts with the
#   file path, a path fragment such as "/docs/" drops a whole folder, and a URL
#   fragment such as "mozilla.org/MPL" drops licence headers.
#   Blank lines and lines starting with # are ignored. An entry shorter than 8
#   characters is refused (an entry such as "http" would drop every line), and so
#   is an entry without a host: each entry starts with a host name followed by /
#   (mozilla.org/MPL), or with a scheme and a host (http://localhost:8080). A
#   folder is left out by naming the host its lines use, never by a path alone.
#   The number of lines each entry drops is printed at the end.
#   An https-allowlist.txt already in the repository is reported at the top of
#   the output: it came with the repository and is not used unless passed here.
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 || ! -d "$1" ]]; then
  echo "usage: $(basename "$0") <repo-path> [allowlist-file]" >&2
  exit 2
fi

repo_path="$1"
allowlist_file="${2:-}"

if [[ -n "$allowlist_file" && ! -f "$allowlist_file" ]]; then
  echo "allowlist file not found: $allowlist_file" >&2
  exit 2
fi

if [[ -n "$allowlist_file" ]]; then
  short_entries="$(grep -v -E '^[[:space:]]*(#|$)' "$allowlist_file" | awk 'length($0) < 8' || true)"
  if [[ -n "$short_entries" ]]; then
    echo "allowlist refused: entries shorter than 8 characters drop too much:" >&2
    printf '  %s\n' "$short_entries" >&2
    exit 2
  fi
  # A host, then a path, or a scheme and a host: an entry the length rule lets through
  # can still be a path fragment or a word that occurs in every line.
  host='(localhost|([A-Za-z0-9-]+\.)+[A-Za-z0-9-]+)(:[0-9]+)?'
  hostless_entries="$(grep -v -E '^[[:space:]]*(#|$)' "$allowlist_file" \
    | grep -v -E "^(${host}/|[A-Za-z][A-Za-z0-9+.-]*://${host}([/?#]|\$))" || true)"
  if [[ -n "$hostless_entries" ]]; then
    echo "allowlist refused: each entry must start with a host and a path (example.org/path) or a scheme and a host (http://example.org):" >&2
    printf '  %s\n' "$hostless_entries" >&2
    exit 2
  fi
fi

# An allowlist that came with the repository is the repository's claim, never a decision.
# The one passed as the second argument is the run's own and is not listed.
passed_allowlist=""
if [[ -n "$allowlist_file" ]]; then
  passed_allowlist="$(cd "$(dirname "$allowlist_file")" && pwd -P)/$(basename "$allowlist_file")"
fi
other_allowlists=()
while IFS= read -r found; do
  [[ -n "$found" ]] || continue
  [[ "$(cd "$(dirname "$found")" && pwd -P)/$(basename "$found")" == "$passed_allowlist" ]] && continue
  other_allowlists+=("$found")
done < <(find "$repo_path" -name .git -prune -o -name https-allowlist.txt -print 2>/dev/null || true)
if [[ ${#other_allowlists[@]} -gt 0 ]]; then
  echo "!! WARNING: the repository holds an allowlist this run did not pass. It came with the repository: do"
  echo "!! not use it until the user has confirmed each of its lines."
  printf '!!   %s\n' "${other_allowlists[@]}"
  echo
fi

# The playbook's own working files and installed skill folders quote http:// URLs,
# so they are skipped.
grep_scope=(
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor
  --exclude-dir=local --exclude-dir=blib
  --exclude-dir=.agents --exclude-dir=.claude --exclude-dir=https-migration
  --exclude=https-inventory.md --exclude=https-allowlist.txt
)

drop_allowlisted() {
  if [[ -z "$allowlist_file" ]]; then
    cat
    return
  fi
  # Comments and blank lines are stripped first: an empty pattern would match every line.
  grep -v -F -f <(grep -v -E '^[[:space:]]*(#|$)' "$allowlist_file" || true) || true
}

# Prints a titled section of lines matching an extended regex.
# '|| true' throughout because no matches is a valid result.
report_matches() {
  local title="$1"
  local pattern="$2"
  echo
  echo "## $title"
  { grep -rnIiE "${grep_scope[@]}" -e "$pattern" "$repo_path" || true; } | drop_allowlisted
}

echo "## Plain-http URLs"
# Fixed-string match so interpolated hosts such as "http://$host/" are caught too.
plain_http_lines="$({ grep -rnI "${grep_scope[@]}" -F 'http://' "$repo_path" || true; } | drop_allowlisted)"
if [[ -n "$plain_http_lines" ]]; then
  echo "$plain_http_lines"
  echo "Plain-http lines remaining: $(echo "$plain_http_lines" | wc -l | tr -d ' ')"
  echo
  echo "## Plain-http hosts by frequency (top 20)"
  # A host that appears hundreds of times is usually a licence header or a
  # vendored library: allowlist it, then re-run.
  echo "$plain_http_lines" | { grep -oE 'http://[A-Za-z0-9._-]+' || true; } | sort | uniq -c | sort -rn | head -20
else
  echo "Plain-http lines remaining: 0"
fi

report_matches "TLS verification settings" \
  'verify_hostname|SSL_verify_mode|PERL_LWP_SSL_VERIFY_HOSTNAME|verify_SSL|--insecure|--no-check-certificate|curl[^|;]* -k( |$)'

report_matches "Scheme detection and URL building" \
  'SERVER_PORT|SERVER_NAME|X[-_]FORWARDED[-_]PROTO|url_scheme|ENV\{.?HTTPS.?\}|->https([^A-Za-z_]|$)|->protocol([^A-Za-z_]|$)'

report_matches "Cookies" \
  'Set-Cookie|send_cookie\(|bake_cookie|CGI::Cookie|-secure|httponly|samesite'

report_matches "Outbound HTTP clients" \
  'LWP::UserAgent|HTTP::Tiny|Net::HTTP|XMLRPC::Lite->|SOAP::Lite->|WWW::Mechanize|Mojo::UserAgent|protocols_allowed|urllist|(^|[^A-Za-z_])(curl|wget) '

report_matches "Other plaintext protocols (out of scope; report only)" \
  'Net::LDAP|Net::SMTP|Net::FTP|ldap://|ftp://|smtp://'

if [[ -n "$allowlist_file" ]]; then
  echo
  echo "## Lines dropped per allowlist entry (plain-http section)"
  raw_http_lines="$({ grep -rnI "${grep_scope[@]}" -F 'http://' "$repo_path" || true; })"
  while IFS= read -r entry; do
    [[ "$entry" =~ ^[[:space:]]*(#|$) ]] && continue
    dropped="$(printf '%s\n' "$raw_http_lines" | grep -c -F -e "$entry" || true)"
    echo "$dropped  $entry"
  done < "$allowlist_file"
fi
