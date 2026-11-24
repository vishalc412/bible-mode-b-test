---
id: reference/risks-and-surprises
kind: reference
source: [components/catalog/catalog.py, components/catalog/service.py, components/orders/orders.py, components/orders/catalog_client.py, .github/bible/bible_queue.py, .github/workflows/bible-queue.yml, tools/fanout.sh, codebase-analysis/components.json, codebase-analysis/ledger/inventory.json]
summary: Records operational, security, data, and analysis-maintenance concerns with their evidence pages
depends_on: [page:hld/01-system-context.md, page:hld/02-architecture.md, page:hld/03-integrations.md, page:hld/04-data-architecture.md, page:hld/06-cross-cutting.md]
---
# Risks and surprises

| # | What | Why it matters | Evidence | Page |
| --- | --- | --- | --- | --- |
| 1 | Settlement traffic uses plain HTTP to the hard-coded partner endpoint; the adjacent source comment says TLS is “coming soon” but gives no date (inferred: the comment at `components/orders/orders.py:7-9`). | Settlement data travels without TLS (assumed: HTTP carries no transport encryption), and the migration timing is unknown. | `components/orders/orders.py:7-9`, `components/orders/orders.py:45-50` | [`Integrations`](../hld/03-integrations.md) |
| 2 | The catalog API has no handler authentication and binds to loopback by default but can be configured to bind elsewhere. | A non-loopback deployment can expose unauthenticated price and health routes; `make_server` configures no TLS (`components/catalog/service.py:40-43`). | `components/catalog/service.py:15-34`, `components/catalog/service.py:40-49` | [`Cross-cutting`](../hld/06-cross-cutting.md) |
| 3 | The supplier feed URL is a hard-coded `https://` source constant, fetched with a certificate-verifying context, and a redirect to `http://` is refused; the HTTPS migration records say the live supplier endpoint was never contacted, so its certificate is not proven (inferred: per `https-migration/https-migration-summary.md:29`). | Changing the supplier endpoint requires a source change, and the verified-HTTPS behaviour is shown by a mocked unit test only (`components/catalog/test_catalog.py:14-30`). | `components/catalog/catalog.py:8`, `components/catalog/catalog.py:18-24`, `components/catalog/catalog.py:48-55` | [`Integrations`](../hld/03-integrations.md) |
| 4 | Product data is a process-local dictionary; feed updates change only known SKUs and directly convert indexed fields. | Data disappears when the process exits, unknown products are ignored, and malformed entries can fail during update (assumed: Python behaviour of process memory, key lookup, `float` and `int`). | `components/catalog/catalog.py:11-15`, `components/catalog/catalog.py:58-63` | [`Data architecture`](../hld/04-data-architecture.md) |
| 5 | The supplier fetch docstring claims a nightly cron run, but no scheduler or source caller is present (inferred: a search for `fetch_supplier_feed` finds 2 hits, its definition and one test call at `components/catalog/test_catalog.py:19`, and a search for `cron` and `schedul` finds 3 hits, the docstring and the queue's own schedule at `.github/workflows/bible-queue.yml:8-9`). | Do not assume prices or stock refresh automatically. | `components/catalog/catalog.py:48-55`; search disposition in `progress.md` (Sweep, Scheduled/background work) | [`Integrations`](../hld/03-integrations.md) |
| 6 | The remote catalog client is an intended separate-service path, but its only in-repository callers are tests (inferred: its docstring, `components/orders/catalog_client.py:1-4`, names the separate-service use, and a search of the repository finds `catalog_client` used only in `components/orders/test_catalog_client.py`, 6 hits); current order helpers import the catalog directly. | Do not treat the HTTP path as the current deployed request flow. | `components/orders/orders.py:5`, `components/orders/orders.py:19-20`, `components/orders/orders.py:35-42`; `components/orders/catalog_client.py:1-4`, `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-62` | [`Architecture`](../hld/02-architecture.md) |
| 7 | `tools/fanout.sh` points generated issue recipients at a nonexistent `component-analysis` skill (inferred: a listing of `.github/skills/` shows 7 folders, none named `component-analysis`). | Fanout-created instructions refer to stale tooling; the answered decision is to document, not change, this path. | `tools/fanout.sh:13-15` | [`Tools component`](../lld/tools/README.md) |
| 8 | The `Queue.session` docstring omits the returned `start-error` state. | Readers relying on the docstring may misunderstand session classification. | `.github/bible/bible_queue.py:578`, `.github/bible/bible_queue.py:581-582` | [`Queue module`](../lld/bible-mode-b/bible_queue.md) |
| 9 | The queue checks PRs using toolkit scripts from the default-branch checkout and reads the component branch tarball as input data. | The gate's trusted implementation comes from the default branch, not from the agent's PR. | `.github/workflows/bible-queue.yml:26-30`; `.github/bible/bible_queue.py:976-995` | [`Queue component`](../lld/bible-mode-b/README.md) |
| 10 | GitHub calls have request timeouts but no retry inside a request (inferred: a search of `components`, `tools` and `.github/workflows` for `retry`, `retries`, `backoff` and `tenacity` finds 0 hits, and the 17 hits in `.github/bible/bible_queue.py` are comments, messages and the session retry `fail_or_retry`, none around a request); `GitHub.call` makes one request and raises on failure; a component whose call raises is tried again at the next scheduled queue run; the queue's one retry applies to a failed agent session (a start Copilot refuses is held at once). | Transient API failures can stop the current queue operation rather than being retried automatically. | `.github/bible/bible_queue.py:117`, `.github/bible/bible_queue.py:128-140`, `.github/bible/bible_queue.py:298`, `.github/bible/bible_queue.py:642-661`, `.github/bible/bible_queue.py:741-744` | [`Cross-cutting`](../hld/06-cross-cutting.md) |
| 11 | Gate pass 3 checks test-count growth and runs unittest discovery; several order functions are not covered by the current tests (inferred: a search of the three test files for `order_total`, `validate` and `settle` finds 0 hits). | Passing existing tests does not establish behavior for totals, validation, or settlement. | `tools/gate.py:63-78`; `components/orders/test_orders.py:6-8`; `components/orders/test_catalog_client.py:37-62` | [`Cross-cutting`](../hld/06-cross-cutting.md) |
| 12 | The current queue module spans 1,434 lines, so old component-size estimates should not be assumed current. | Component-size metadata and the queue's session estimate may need refreshing after source changes. | `.github/bible/bible_queue.py:1-1434`; `.github/bible/bible_queue.py:738`, `.github/bible/bible_queue.py:847-848` | [`Coverage ledger`](../ledger/coverage-ledger.md) |
| 13 | The catalog implements two GET path matches in an imperative handler. | Do not interpret a static route scan as evidence that the catalog has no HTTP endpoints; both routes have endpoint cards. | `components/catalog/service.py:24-34` | [`Integrations`](../hld/03-integrations.md) |
| 14 | The docstring of `report_facts` lists five returned values while the function returns six, and the component pull request text says `verified (PASS, ...)` also when the accepted verdict was `PASS AFTER CORRECTIONS`. | A reader of the docstring misses the sixth value, which `accepted` reads; the pull request text can understate that corrections were applied. | `.github/bible/bible_queue.py:479-480`, `.github/bible/bible_queue.py:506-507`, `.github/bible/bible_queue.py:532`, `.github/bible/bible_queue.py:867-870` | [`Queue component`](../lld/bible-mode-b/README.md) |

<!-- cites .github/bible/bible_queue.py@a625b4c3353b1744b965b8bbee13e6b3ed5f72a6 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites components/catalog/catalog.py@75bb1dc767dc16cad9a5ed5555a7293bc004275b -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/catalog/test_catalog.py@29eeea56df47ceb3c96481a327851eee696ec67d -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites https-migration/https-migration-summary.md@8af6a247647debc371a600624b95b7c94326da9c -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->
