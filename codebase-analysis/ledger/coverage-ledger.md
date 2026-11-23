# Coverage ledger

Depth: deep. Snapshot: 20 files, 2026-11-23. Inventory: `ledger/inventory.json` of 2026-11-23.

| Path | Status | Pages |
| --- | --- | --- |
| `.gitignore` | read in full | `ledger/coverage-ledger.md` |
| `README.md` | read in full | `hld/01-system-context.md`, `README.md` |
| `.github/bible/bible_queue.py` | read in full | `lld/bible-mode-b/bible_queue.md`, `hld/01-system-context.md`–`hld/06-cross-cutting.md`, `lld/data-dictionary.md` |
| `.github/workflows/bible-delta.yml` | read in full | `lld/bible-mode-b/README.md`, `hld/02-architecture.md`, `hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `.github/workflows/bible-plan.yml` | read in full | `lld/bible-mode-b/README.md`, `hld/02-architecture.md`, `hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `.github/workflows/bible-queue.yml` | read in full | `lld/bible-mode-b/README.md`, `hld/02-architecture.md`, `hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `.github/workflows/poc-assign-copilot.yml` | read in full | `lld/bible-mode-b/README.md`, `hld/01-system-context.md`, `hld/02-architecture.md`, `hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `components/__init__.py` | read in full | `lld/catalog/README.md`, `lld/orders/README.md` |
| `components/catalog/__init__.py` | read in full | `lld/catalog/README.md` |
| `components/catalog/catalog.py` | read in full | `lld/catalog/catalog.md`, `hld/01-system-context.md`, `hld/03-integrations.md`, `hld/04-data-architecture.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md`, `lld/data-dictionary.md` |
| `components/catalog/service.py` | read in full | `lld/catalog/service.md`, `lld/api/catalog/catalog.md`, `hld/01-system-context.md`–`hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `components/catalog/test_catalog.py` | read in full | `lld/catalog/test_catalog.md`, `hld/06-cross-cutting.md` |
| `components/orders/__init__.py` | read in full | `lld/orders/README.md` |
| `components/orders/catalog_client.py` | read in full | `lld/orders/catalog_client.md`, `hld/01-system-context.md`–`hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `components/orders/orders.py` | read in full | `lld/orders/orders.md`, `hld/01-system-context.md`–`hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `components/orders/test_catalog_client.py` | read in full | `lld/orders/test_catalog_client.md`, `hld/01-system-context.md`, `hld/02-architecture.md`, `hld/03-integrations.md`, `hld/06-cross-cutting.md` |
| `components/orders/test_orders.py` | read in full | `lld/orders/test_orders.md`, `hld/06-cross-cutting.md` |
| `tools/fanout.sh` | read in full | `lld/tools/fanout.md`, `hld/02-architecture.md`, `hld/03-integrations.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `tools/gate.py` | read in full | `lld/tools/gate.md`, `hld/02-architecture.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md` |
| `tools/plan.py` | read in full | `lld/tools/plan.md`, `hld/02-architecture.md`, `hld/05-key-flows.md`, `hld/06-cross-cutting.md`, `lld/data-dictionary.md` |

## Totals

| Status | Folders | Files |
| --- | ---: | ---: |
| not read | 0 | 0 |
| sampled | 0 | 0 |
| read in full | 7 | 20 |
| excluded | 0 | 0 |

## Coverage from coverage.py

The whole-analysis gate passes at deep: all 11 of 11 source files with symbols have pages, all 111 symbols and 93 full function cards are accounted for, all 274 branch lines are cited, all 210 same-file call-graph edges are drawn, 17 of 17 LLD pages have front matter, and 1,886 of 1,886 citations resolve (100%). The changed queue source file is 1,130 lines long (`.github/bible/bible_queue.py:1-1130`). The separate catalog endpoint cards cover both manually matched GET paths; the static route counter detects none (`ledger/coverage-report.md`).

<!-- cites .github/bible/bible_queue.py@68e91ae09c53c283e7402334cfe2a715785b33ed -->
