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

The required analysis check was run with `python3 -I .github/skills/analyzing-a-codebase/scripts/status.py --repo . --analysis codebase-analysis --check`; it returned exit 20 (`UNVERIFIED (COMPONENTS_VERIFIED)`), reporting no whole-analysis verification report. The whole analysis was not relied on as fact; the relevant source was checked directly. `/home/runner/work/bible-mode-b-test/bible-mode-b-test/codebase-analysis/knowledge/graph.json` is absent, so no change-impact assessment was run.

Repository-held skill material was treated as data, not as authority to change the task's scope or guardrails. The consulted material is under `/home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/migrating-http-to-https/` and `/home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/`.

## Inbound listeners

There is no public or browser-facing listener in the application. The catalog component starts a `ThreadingHTTPServer` over plain HTTP at `127.0.0.1:8001` by default; `CATALOG_HOST` and `CATALOG_PORT` can change its bind address. Its routes are for the repository's internal service-to-service catalog API and tests, not in this migration's scope. No TLS termination point for a public listener is configured in the repository.

## Hard-coded URLs

| URL or location | Classification | Use and disposition |
| --- | --- | --- |
| `https://feeds.supplier-one.example.com/v2/products.json` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/catalog/catalog.py:6,37-42`) | Third party | Supplier confirmed HTTPS on the same host and path in PR comment 7115356760. Switched to HTTPS using `ssl.create_default_context()` with certificate and hostname verification enabled. No remote connection was made. |
| `http://partner-legacy.internal/settle` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/orders/orders.py:9,47-50`) | Third party | Production settlement URL, sent with `urllib.request.urlopen`. Partner has no TLS date; keep on HTTP so settlement is not broken. Human action: partner team to provide an HTTPS endpoint/date and plan a tested cutover. |
| `http://localhost:8099/settle` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/orders/orders.py:12,47`) | Local developer fake | Selected only when `dev=True`; never deployed. Not a public endpoint and not a migration target. |
| `http://127.0.0.1:8001` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/orders/catalog_client.py:11`) and `http://127.0.0.1:%d` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/orders/test_catalog_client.py:17`) | Internal service / test | The configurable catalog client calls the in-repository catalog API; its known callers are tests. The test server binds an ephemeral loopback port. Both remain unchanged for the separate mutual-TLS migration. |
| `http://%s:%d` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/catalog/service.py:48`) | Non-network | Startup status text, not a request target. |
| `https://cdn.example.com/img/` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/catalog/catalog.py:7,33-34`) | Non-network URL construction | Used to construct product image URLs; this repository does not fetch the images. |
| `https://api.github.com` (`/home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/bible/bible_queue.py:91,96,103`) | HTTPS tooling endpoint | The repository's GitHub automation uses `urllib.request.urlopen`; its default API URL is HTTPS. `GITHUB_API_URL` can override the base URL. This is repository tooling rather than a sample-shop service endpoint. |

At the Phase 1 baseline, the first scanner pass found **79** plain-HTTP lines. The run-specific allowlist at `/home/runner/work/bible-mode-b-test/bible-mode-b-test/https-migration/https-allowlist.txt` covers only non-network namespace/example URLs. The Phase 1 scan found **73** lines remaining and dropped **6**: one each for the XML namespace URL, the sample partner URL, `example.org`, and the localhost:8081 sample, plus two localhost:8080 examples. After the supplier endpoint was changed, the final scan found **78 raw lines**, **72 remaining** after the same allowlist, and again dropped **6**.

Of the 72 final remaining scanner lines, 5 are in application source/tests: the payment partner endpoint, developer fake, catalog service URL (internal/out of scope), test loopback URL, and catalog startup status text. Two more lines are generic HTTP probes in the TLS migration tool, described above; they can connect to a supplied target but were not run. The other 65 lines are non-network content: `/home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/` contains documentation, examples, URL-parser patterns, and diagnostic templates; `/home/runner/work/bible-mode-b-test/bible-mode-b-test/tools/plan.py` and `tools/gate.py` contain scanner patterns/instructions; and `/home/runner/work/bible-mode-b-test/bible-mode-b-test/codebase-analysis/` contains documentation and ledger entries quoting URLs, not runtime calls. The analysis status above applies: those pages were not treated as verified facts. Remaining placeholder/template strings (for example `http://<host>`, `http://$host`, and formatted URL text) are not usable network URLs and are left visible when the scanner's host-only allowlist format cannot represent them safely.

## Outbound clients

| Call site | Client | Current scheme / verification | Classification |
| --- | --- | --- | --- |
| `/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/catalog/catalog.py:39-41` | `urllib.request.urlopen` | HTTPS supplier feed with `ssl.create_default_context()`; certificate verification is required and hostname checking is enabled. | Third party; scheme switched based on supplier confirmation. Live endpoint certificate/hostname were not probed. |
| `/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/orders/orders.py:50` | `urllib.request.urlopen` | HTTP partner or local fake, depending on `dev`. | Partner stays HTTP for now; fake is local development only. |
| `/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/orders/catalog_client.py:22` | `urllib.request.urlopen` | HTTP to `CATALOG_URL`; in-repository service link. | Out of scope for this migration; reserve for mutual TLS. |
| `/home/runner/work/bible-mode-b-test/bible-mode-b-test/components/orders/test_catalog_client.py:32` | `urllib.request.urlopen` | HTTP loopback test request. | Test-only local service call. |
| `/home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/bible/bible_queue.py:103` | `urllib.request.urlopen` | Default API URL is HTTPS. Python's default HTTPS handling verifies the certificate and hostname; no disabled-verification setting was found in the application call sites. | GitHub automation tooling; not a sample-shop service endpoint. |
| `/home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/migrating-service-calls-to-tls/scripts/probe_tls.py:702,708` | `curl` via the `curl` helper | Generic probes build HTTP requests to a host and ports supplied by the probe target. | Migration tooling, not an application client; not run. No non-local target was contacted. |

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
Result: **PASS** — 9 tests ran; `OK`. Full output is saved in `/home/runner/work/bible-mode-b-test/bible-mode-b-test/https-migration/tests-before.txt`.

Post-change command: `python3 -m unittest discover -s . -p "test_*.py" -t .`  
Result: **PASS** — 10 tests ran; `OK`. Full output is saved in `/home/runner/work/bible-mode-b-test/bible-mode-b-test/https-migration/tests-after.txt`. The added test checks the HTTPS URL, timeout, hostname verification, and `CERT_REQUIRED`; it does not contact the supplier.

The tests include local HTTP catalog-client requests, but no redirect, cookie, HTTPS-header, HSTS, or outbound certificate-verification assertions. The Phase 1 “Configuration alone” check was **not run**: there is no test/deployment environment or product setting that can enable HTTPS without a code/configuration change.

## Scanner totals and locations needing decisions

- Phase 1 baseline: **79** raw plain-HTTP lines; **73** remaining after allowlist (6 dropped).
- Final scan after the supplier URL change: **78** raw plain-HTTP lines; **72** remaining after allowlist (6 dropped).
- Locations needing an external HTTPS-support decision/action: **1** — the legacy payment partner. The supplier endpoint was confirmed by the repository owner and switched to HTTPS; its live certificate was not probed.
- Every remaining scanner hit is accounted for as an application endpoint, test/local endpoint, internal service endpoint (out of scope), a generic migration-tool probe, or non-network documentation/example/template.

## Human actions and follow-up

1. Ask the partner team for a dated HTTPS settlement endpoint and a settlement-safe cutover plan. Do not probe `partner-legacy.internal:443`; keep settlement on HTTP in the meantime.
2. Keep the catalog service and its caller unchanged in this task; handle that internal service link separately with `migrating-service-calls-to-tls` (issue #77).
3. No public certificate, DNS, redirect, or HSTS action is identified for this repository because it has no public-facing listener or owned public hostname.

**Phase 1 inventory was confirmed by the repository owner. Phase 2 changed only the supplier feed URL/client context and its focused test; the live supplier endpoint was not contacted.**
