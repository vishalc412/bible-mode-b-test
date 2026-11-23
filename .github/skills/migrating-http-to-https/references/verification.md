# Verification

All must pass. Record the output of each in the summary. A check that connects to a host other than this machine waits for the user's yes on the exact host and port list. Where no endpoint is deployed yet, mark the live checks "not run" and list them as human actions; do not report them as passed.

| Check | Command or method | Pass when |
| --- | --- | --- |
| Tests | The repository's build and test command, shown to the user first | All pass; every changed assertion is listed |
| Redirect | `curl -sI http://<host><path>` for a page, a URL with a query string, a static file and each API endpoint | Every one returns `308` (`301` only where the termination point is outside this repository and cannot be changed) with an `https://` Location that keeps the path and query |
| Form POST | POST a form with a made-up field value to `http://<host>/` | Redirected, and the value does not appear in the Location |
| Serves TLS | `curl -sI https://<host><path>` for the same paths | Every one answers; the home page returns `200`; valid certificate chain |
| Scheme header | From a host other than the proxy, send `X-Forwarded-Proto: https` straight to the application | The application does not treat the request as HTTPS |
| No redirect loop | `curl -sIL https://<host>/` through the proxy | Ends in `200`; no repeated redirects |
| Old protocols off | `openssl s_client -connect <host>:443 -tls1_1 -cipher 'DEFAULT@SECLEVEL=0'` | The server answers with "alert protocol version". A closed port or a reset is not a refusal. If the client prints "no protocols available" it could not offer that version: report "not tested", not "pass". |
| Configuration alone (run in Phase 1) | Switch HTTPS on in the product's settings only, before any other change, in a test environment | Site still usable. If it loops or breaks, the fix belongs in the plan. |
| HSTS | Response headers on HTTPS, for the same paths | `Strict-Transport-Security` present on every response, static files included; absent on plain HTTP |
| Cookies | `Set-Cookie` headers across login, logout and preference pages; cookie writes in page scripts | Every cookie has `Secure`, `HttpOnly` and `SameSite` of `Lax` or `Strict`; script-written cookies set `secure` |
| Outbound verification | Search for disabled verification ([perl-tls.md](perl-tls.md)) | None found |
| No leftovers | `scripts/find-http-urls.sh <repo> https-migration/https-allowlist.txt` | `Plain-http lines remaining: 0`, or every remaining line is accounted for by category in the summary |

No response, an error page or a missing measurement is a failure to evaluate.
