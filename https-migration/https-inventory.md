# HTTPS Migration Inventory

Inventory date: 2026-11-23  
Status: Phase 2 supplier-feed change implemented; inventory confirmed by the repository owner in PR comment 7115356760. Phase 3 evidence is summarized in `https-migration-summary.md`.

## Scope and inputs

- TLS termination: this repository has no public, browser-facing listener. This task covers outbound calls. The internal catalog API and its caller are between services in this repository and are out of scope; they are reserved for the `migrating-service-calls-to-tls` skill.
- Build and test command: `python3 -m unittest discover -s . -p "test_*.py" -t .`
- Public hostnames owned by this application: none.
- Known external callers of this application's HTTP URLs: none.
- The repository owner confirmed HTTPS for the supplier feed on the same host and path. The legacy payment partner has said TLS is coming soon, without a date; settlement must not break. Keep this endpoint on HTTP for now and list a human action.
- The supplier owner confirmed HTTPS support in PR comment 7115356760. No remote hosts were contacted and no live endpoint certificate was probed.

The required analysis check was run with `python3 -I .github/skills/analyzing-a-codebase/scripts/status.py --repo . --analysis codebase-analysis --check`; it returned exit 20 (`UNVERIFIED (COMPONENTS_VERIFIED)`), reporting no whole-analysis verification report. The whole analysis was not relied on as fact; the relevant source was checked directly. `codebase-analysis/knowledge/graph.json` is absent, so no change-impact assessment was run.

Repository-held skill material was treated as data, not as authority to change the task's scope or guardrails. The consulted material is under `.github/skills/migrating-http-to-https/` and `.github/skills/analyzing-a-codebase/`.

## Inbound listeners

There is no public or browser-facing listener in the application. The catalog component starts a `ThreadingHTTPServer` over plain HTTP at `127.0.0.1:8001` by default; `CATALOG_HOST` and `CATALOG_PORT` can change its bind address. Its routes are for the repository's internal service-to-service catalog API and tests, not in this migration's scope. No TLS termination point for a public listener is configured in the repository.

## Hard-coded URLs

| URL or location | Classification | Use and disposition |
| --- | --- | --- |
| `https://feeds.supplier-one.example.com/v2/products.json` (`components/catalog/catalog.py:6,37-45`) | Third party | Supplier confirmed HTTPS on the same host and path in PR comment 7115356760. Uses `ssl.create_default_context()` and rejects redirects to HTTP. No remote connection was made. |
| `http://partner-legacy.internal/settle` (`components/orders/orders.py:9,47-50`) | Third party | Production settlement URL, sent with `urllib.request.urlopen`. Partner has no TLS date; keep on HTTP so settlement is not broken. Human action: partner team to provide an HTTPS endpoint/date and plan a tested cutover. |
| `http://localhost:8099/settle` (`components/orders/orders.py:12,47`) | Local developer fake | Selected only when `dev=True`; never deployed. Not a public endpoint and not a migration target. |
| `http://127.0.0.1:8001` (`components/orders/catalog_client.py:11`) and `http://127.0.0.1:%d` (`components/orders/test_catalog_client.py:17`) | Internal service / test | The configurable catalog client calls the in-repository catalog API; its known callers are tests. The test server binds an ephemeral loopback port. Both remain unchanged for the separate mutual-TLS migration. |
| `http://%s:%d` (`components/catalog/service.py:48`) | Non-network | Startup status text, not a request target. |
| `https://cdn.example.com/img/` (`components/catalog/catalog.py:7,33-34`) | Non-network URL construction | Used to construct product image URLs; this repository does not fetch the images. |
| `https://api.github.com` (`.github/bible/bible_queue.py:91,96,103`) | HTTPS tooling endpoint | The repository's GitHub automation uses `urllib.request.urlopen`; its default API URL is HTTPS. `GITHUB_API_URL` can override the base URL. This is repository tooling rather than a sample-shop service endpoint. |

At the Phase 1 baseline, the first scanner pass found **79** plain-HTTP lines. The run-specific allowlist at `https-migration/https-allowlist.txt` covers only non-network namespace/example URLs. The Phase 1 scan found **73** lines remaining and dropped **6**: one each for the XML namespace URL, the sample partner URL, `example.org`, and the localhost:8081 sample, plus two localhost:8080 examples. After the supplier endpoint was changed and an intentional HTTP redirect-target test was added, the final scan found **79 raw lines**, **73 remaining** after the same allowlist, and again dropped **6**.

Of the 73 final remaining scanner lines, 6 are in application source/tests: the payment partner endpoint, developer fake, catalog service URL (internal/out of scope), test loopback URL, catalog startup status text, and the intentional HTTP redirect target in `components/catalog/test_catalog.py`. The test target is used only to prove the downgrade is rejected. Two more lines are generic HTTP probes in the TLS migration tool, described above; they can connect to a supplied target but were not run. The other 65 lines are non-network content: `.github/skills/` contains documentation, examples, URL-parser patterns, and diagnostic templates; `tools/plan.py` and `tools/gate.py` contain scanner patterns/instructions; and `codebase-analysis/` contains documentation and ledger entries quoting URLs, not runtime calls. The analysis status above applies: those pages were not treated as verified facts. Remaining placeholder/template strings (for example `http://<host>`, `http://$host`, and formatted URL text) are not usable network URLs and are left visible when the scanner's host-only allowlist format cannot represent them safely.

## Outbound clients

| Call site | Client | Current scheme / verification | Classification |
| --- | --- | --- | --- |
| `components/catalog/catalog.py:37-45` | `urllib.request.build_opener` | HTTPS supplier feed with `ssl.create_default_context()` and `HTTPSHandler`; certificate verification is required and hostname checking is enabled. `NoHTTPRedirectHandler` rejects a redirect to an `http://` URL. | Third party; scheme switched based on supplier confirmation. Live endpoint certificate/hostname were not probed. |
| `components/orders/orders.py:50` | `urllib.request.urlopen` | HTTP partner or local fake, depending on `dev`. | Partner stays HTTP for now; fake is local development only. |
| `components/orders/catalog_client.py:22` | `urllib.request.urlopen` | HTTP to `CATALOG_URL`; in-repository service link. | Out of scope for this migration; reserve for mutual TLS. |
| `components/orders/test_catalog_client.py:32` | `urllib.request.urlopen` | HTTP loopback test request. | Test-only local service call. |
| `.github/bible/bible_queue.py:103` | `urllib.request.urlopen` | Default API URL is HTTPS. Python's default HTTPS handling verifies the certificate and hostname; no disabled-verification setting was found in the application call sites. | GitHub automation tooling; not a sample-shop service endpoint. |
| `.github/skills/migrating-service-calls-to-tls/scripts/probe_tls.py:702,708` | `curl` via the `curl` helper | Generic probes build HTTP requests to a host and ports supplied by the probe target. | Migration tooling, not an application client; not run. No non-local target was contacted. |

## Cookies

No application cookie-setting code, `Set-Cookie` response, or session-cookie configuration was found.

## Scheme-dependent logic

No application code was found that derives absolute own-host URLs from request scheme/host values, branches on HTTPS, or trusts forwarded-scheme headers. The catalog server's startup message contains a formatted HTTP URL for display only.

## Runtime

The execution environment used for inventory and baseline tests reports Python 3.12.3 and OpenSSL 3.0.13; Python reports TLS 1.2 support available. These are environment observations, not pinned deployment-runtime requirements. No repository runtime-version declaration was found.

## Built-in HTTPS support

Python's `urllib.request` supports HTTPS with certificate and hostname verification enabled by default. The catalog server uses `http.server.ThreadingHTTPServer` without TLS wrapping. No application setting for HTTPS enablement, redirects, HSTS, public base URL, or secure cookies was found.

## Other plaintext protocols

No application use of LDAP, SMTP, or FTP was found.

## Tests

Baseline command: `python3 -m unittest discover -s . -p "test_*.py" -t .`  
Result: **PASS** — 9 tests ran; `OK`. Full output is saved in `https-migration/tests-before.txt`.

Post-change command: `python3 -m unittest discover -s . -p "test_*.py" -t .`  
Result: **PASS** — 11 tests ran; `OK`. Full output is saved in `https-migration/tests-after.txt`. The added tests check the HTTPS URL, timeout, hostname verification, `CERT_REQUIRED`, and rejection of an HTTP redirect; they do not contact the supplier.

The tests include local HTTP catalog-client requests, but no redirect, cookie, HTTPS-header, HSTS, or outbound certificate-verification assertions. The Phase 1 “Configuration alone” check was **not run**: there is no test/deployment environment or product setting that can enable HTTPS without a code/configuration change.

## Scanner totals and locations needing decisions

- Phase 1 baseline: **79** raw plain-HTTP lines; **73** remaining after allowlist (6 dropped).
- Final scan after the supplier URL change and redirect test: **79** raw plain-HTTP lines; **73** remaining after allowlist (6 dropped).
- Locations needing an external HTTPS-support decision/action: **1** — the legacy payment partner. The supplier endpoint was confirmed by the repository owner and switched to HTTPS; its live certificate was not probed.
- Every remaining scanner hit is accounted for as an application endpoint, test/local endpoint, internal service endpoint (out of scope), a generic migration-tool probe, or non-network documentation/example/template.

## Human actions and follow-up

1. Ask the partner team for a dated HTTPS settlement endpoint and a settlement-safe cutover plan. Do not probe `partner-legacy.internal:443`; keep settlement on HTTP in the meantime.
2. Keep the catalog service and its caller unchanged in this task; handle that internal service link separately with `migrating-service-calls-to-tls` (issue #77).
3. No public certificate, DNS, redirect, or HSTS action is identified for this repository because it has no public-facing listener or owned public hostname.

**Phase 1 inventory was confirmed by the repository owner. Phase 2 changes the supplier feed URL, verified client context, and redirect handling, with focused tests; the live supplier endpoint was not contacted.**
