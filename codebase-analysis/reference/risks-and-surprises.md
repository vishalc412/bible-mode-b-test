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
| 1 | Settlement traffic uses plain HTTP to the hard-coded partner endpoint; the adjacent source comment says TLS is “coming soon” but gives no date. | Settlement data travels without TLS, and the migration timing is unknown. | `components/orders/orders.py:7-9`, `components/orders/orders.py:45-50` | [`Integrations`](../hld/03-integrations.md) |
| 2 | The catalog API has no handler authentication and binds to loopback by default but can be configured to bind elsewhere. | A non-loopback deployment can expose unauthenticated price and health routes; the repository does not show TLS. | `components/catalog/service.py:15-34`, `components/catalog/service.py:40-49` | [`Cross-cutting`](../hld/06-cross-cutting.md) |
| 3 | Supplier feed access uses plain HTTP, and the URL is a hard-coded source constant. | Feed contents are not protected in transit, and changing the supplier endpoint requires a source change. | `components/catalog/catalog.py:5`, `components/catalog/catalog.py:36-39` | [`Integrations`](../hld/03-integrations.md) |
| 4 | Product data is a process-local dictionary; feed updates change only known SKUs and directly convert indexed fields. | Data disappears when the process exits, unknown products are ignored, and malformed entries can fail during update. | `components/catalog/catalog.py:8-12`, `components/catalog/catalog.py:42-47` | [`Data architecture`](../hld/04-data-architecture.md) |
| 5 | The supplier fetch docstring claims a nightly cron run, but no scheduler or source caller is present. | Do not assume prices or stock refresh automatically. | `components/catalog/catalog.py:36-39`; search disposition in `progress.md` (Sweep, Scheduled/background work) | [`Integrations`](../hld/03-integrations.md) |
| 6 | The remote catalog client is an intended separate-service path, but its only in-repository callers are tests; current order helpers import the catalog directly. | Do not treat the HTTP path as the current deployed request flow. | `components/orders/orders.py:5`, `components/orders/orders.py:19-20`, `components/orders/orders.py:35-42`; `components/orders/catalog_client.py:1-4`, `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-62` | [`Architecture`](../hld/02-architecture.md) |
| 7 | `tools/fanout.sh` points generated issue recipients at a nonexistent `component-analysis` skill. | Fanout-created instructions refer to stale tooling; the answered decision is to document, not change, this path. | `tools/fanout.sh:13-15` | [`Tools component`](../lld/tools/README.md) |
| 8 | The `Queue.session` docstring omits the returned `start-error` state. | Readers relying on the docstring may misunderstand session classification. | `.github/bible/bible_queue.py:518`, `.github/bible/bible_queue.py:521-522` | [`Queue module`](../lld/bible-mode-b/bible_queue.md) |
| 9 | The queue checks PRs using toolkit scripts from the default-branch checkout and reads the component branch tarball as input data. | The gate's trusted implementation comes from the default branch, not from the agent's PR. | `.github/workflows/bible-queue.yml:26-30`; `.github/bible/bible_queue.py:886-905` | [`Queue component`](../lld/bible-mode-b/README.md) |
| 10 | GitHub calls have request timeouts but no general retry; the queue's one retry applies to a failed agent session (a start Copilot refuses is held at once). | Transient API failures can stop the current queue operation rather than being retried automatically. | `.github/bible/bible_queue.py:116`, `.github/bible/bible_queue.py:297`, `.github/bible/bible_queue.py:582-601` | [`Cross-cutting`](../hld/06-cross-cutting.md) |
| 11 | Gate pass 3 checks test-count growth and runs unittest discovery; several order functions are not covered by the current tests. | Passing existing tests does not establish behavior for totals, validation, or settlement. | `tools/gate.py:63-78`; `components/orders/test_orders.py:6-8`; `components/orders/test_catalog_client.py:37-62` | [`Cross-cutting`](../hld/06-cross-cutting.md) |
| 12 | The current queue module spans 1,336 lines, so old component-size estimates should not be assumed current. | Component-size metadata and the queue's session estimate may need refreshing after source changes. | `.github/bible/bible_queue.py:1-1336`; `.github/bible/bible_queue.py:650`, `.github/bible/bible_queue.py:759-760` | [`Coverage ledger`](../ledger/coverage-ledger.md) |
| 13 | The catalog implements two GET path matches in an imperative handler. | Do not interpret a static route scan as evidence that the catalog has no HTTP endpoints; both routes have endpoint cards. | `components/catalog/service.py:24-34` | [`Integrations`](../hld/03-integrations.md) |

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->
