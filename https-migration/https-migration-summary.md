# HTTPS Migration Summary Report: sample-shop, repository inventory, 2026-11-23

Overall result: not proven

The supplier feed URL now uses HTTPS and a default verifying SSL context. No remote endpoint was contacted, so there is no live certificate or hostname evidence. The internal catalog service/client were not changed and remain reserved for mutual TLS (issue #77).

## Successfully Migrated Endpoints

No endpoint is counted as successfully migrated: the verification criteria require live evidence for the endpoint, and no remote hosts were contacted.

## Endpoints Remaining on HTTP

| Endpoint URL | Reason | Priority | Action Required | Owner | Review date |
| --- | --- | --- | --- | --- | --- |
| `http://partner-legacy.internal/settle` | Partner has not confirmed HTTPS support; settlement must not break. | High | Obtain a dated HTTPS endpoint and agree a settlement-safe cutover. Keep HTTP until then. | Payment partner team and application owner | 2026-12-23 |

The localhost developer fake (`http://localhost:8099/settle`) remains HTTP because it is never deployed. The catalog API (`http://127.0.0.1:8001`) and its client remain unchanged because they are an internal service-to-service call out of scope for this migration.

## Endpoints with Warnings

| Endpoint URL | Warning | Recommended Action |
| --- | --- | --- |
| None observed | No external endpoint was contacted, so no certificate warnings were measured. | Verify the supplier endpoint certificate and hostname during an authorized deployment check. |

## Not proven

| Endpoint | Check | Reason not run | Who can run it |
| --- | --- | --- | --- |
| `https://feeds.supplier-one.example.com/v2/products.json` | Live supplier TLS and hostname/certificate validation | No remote hosts were contacted. The local test verifies the configured default SSL context but cannot establish the live endpoint's certificate or availability. | Application operator in an authorized deployment environment |
| Public application endpoints (none identified) | Redirect, form POST, serves TLS, scheme header, redirect loop, old protocols off, HSTS, and cookies | The repository has no public/browser-facing listener, public hostname, inbound routes, or cookie handling to exercise. | Not applicable unless deployment scope changes |
| Application configuration | Configuration alone | Not run in Phase 1: no test/deployment environment or product setting exists to enable HTTPS without a code/configuration change. | Application owner if such an environment becomes available |

## Verification

| Check | Result and recorded output |
| --- | --- |
| Tests | **PASS.** `python3 -m unittest discover -s . -p "test_*.py" -t .` — 11 tests ran; `OK`. Full output: `https-migration/tests-after.txt`. Added test assertions verify the supplier HTTPS URL, timeout, `context.check_hostname == True`, `context.verify_mode == ssl.CERT_REQUIRED`, and refusal of an HTTP redirect; no existing assertions were changed. |
| Redirect | **Not run.** No public application host or inbound route exists. |
| Form POST | **Not run.** No public application host or form endpoint exists. |
| Serves TLS | **Not run.** There is no public application listener; the external supplier was not contacted. |
| Scheme header | **Not run.** No public application listener or proxy is configured in this repository. |
| No redirect loop | **Not run.** No public TLS termination proxy exists in scope. |
| Old protocols off | **Not run.** No public TLS listener exists in scope. |
| Configuration alone | **Not run.** No HTTPS-only configuration switch or test deployment environment was available in Phase 1. |
| HSTS | **Not applicable.** The application has no inbound TLS termination point. |
| Cookies | **Not applicable.** No application cookies or sessions were found. |
| Outbound verification | **PASS (local configuration evidence only).** The focused tests confirmed the `ssl.create_default_context()` has hostname verification enabled, requires certificate verification, and the supplier fetch's redirect handler raises `HTTPError` on an HTTP redirect. Search for disabled verification settings in application/tooling source found no matches. Live supplier verification was not run. |
| No leftovers | **PASS with accounted findings.** `bash .github/skills/migrating-http-to-https/scripts/find-http-urls.sh . https-migration/https-allowlist.txt` reported `Plain-http lines remaining: 73`; 6 lines were dropped by the run-specific allowlist. Remaining hits are classified in `https-migration/https-inventory.md`: 6 application source/test lines (partner, local fake, internal catalog client/test, startup message, and the intentional HTTP target in the downgrade test), 2 generic migration-tool probe lines, and 65 documentation/example/template or scanner-pattern lines. |

## Rollback

The supplier change can be reverted by restoring the supplier URL to HTTP and removing the explicit SSL context, but doing so would reintroduce plaintext delivery and should require supplier/application-owner approval. There are no application redirect, HSTS, or public TLS-termination changes to roll back. The payment partner, local fake, and internal catalog service/client were not changed.

## Statistics

Counts are for the two in-scope external production outbound endpoints (supplier feed and payment partner); local developer fakes, internal service calls, and repository tooling are excluded.

- Total endpoints identified: 2
- Successfully migrated: 0 (0%)
- Remaining on HTTP: 1 (50%)
- Blocked by infrastructure / partner support: 1
- Not proven: 1 (50%)

## Human actions

1. Keep `http://partner-legacy.internal/settle` unchanged until the partner team confirms an HTTPS endpoint and the teams agree on a tested settlement-safe cutover; review by 2026-12-23.
2. During an authorized deployment verification, test the supplier HTTPS endpoint's certificate chain, hostname, and availability. No remote request was made for this inventory/change.
3. Keep the catalog API and client out of this migration; handle their mutual-TLS transition separately under issue #77.
4. No certificate, DNS, HTTP redirect, or HSTS action is identified for this repository because it has no public listener or owned public hostname.
