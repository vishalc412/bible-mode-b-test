# The inventory

`https-migration/https-inventory.md` has these sections:

- **Inbound:** listeners, ports, virtual hosts, health-check paths.
- **Hard-coded URLs:** every `http://` in code, templates, config, SQL seed data, email templates, WSDL and API specs, scripts and cron entries. Mark each as *own host*, *third party* or *non-network* (XML namespaces, DTDs and documentation are not network calls; leave them alone).
- **Outbound clients:** every HTTP client call site, with the library used and whether certificate verification is enabled.
- **Cookies:** every place a cookie is set, with its current flags.
- **Scheme-dependent logic:** code that builds absolute URLs or branches on the request scheme.
- **Runtime:** language version and TLS library version, and the highest TLS version they support.
- **Built-in support:** settings or code the application already has for HTTPS (redirect switches, secure-cookie flags, HSTS options, base-URL settings) and their current values. Legacy products often support HTTPS and ship with it off; the migration is then mostly configuration. Look for this first.
- **Other plaintext protocols:** LDAP, SMTP and FTP use. Report only; they are out of scope.
- **Tests:** whether any existing test checks redirects, cookies or headers. If none does, say so and recommend recording a behaviour baseline before code changes.

## Using the scanner

`scripts/find-http-urls.sh <repo>` lists every plain-http line; with the allowlist as a second argument (`https-migration/https-allowlist.txt`), it leaves out the lines the allowlist covers. The allowlist file must exist before you pass it. Expect noise: licence headers, XML namespaces, documentation and vendored libraries can be most of the raw hits. Use the "hosts by frequency" section to spot them, add each to the allowlist (one entry per line, starting with a host: `www.w3.org/2001/` or `http://www.w3.org/2001/`), and re-run.

The allowlist drops every output line that contains one of its entries. The script refuses an entry shorter than 8 characters or one that does not start with a host, and prints how many lines each entry dropped. Keep entries specific, and show the user each one you add.

## Third-party endpoints

For each third party, record whether it offers HTTPS. Checking that means a connection to the third party's host: show the user the host and port list and wait for a yes. One with no HTTPS equivalent stays on HTTP: record it in the summary under "Endpoints Remaining on HTTP" ([summary-format.md](summary-format.md)) and add, where the file format allows comments, the line:

`TODO: HTTPS not supported - requires infrastructure update`
