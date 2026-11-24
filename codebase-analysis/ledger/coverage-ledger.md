# Coverage ledger

Depth: deep. Snapshot: 24 files in scope, 2026-11-24 (the `.git` worktree pointer file is not part of the repository's content and is not in the inventory). Inventory: `ledger/inventory.json` of 2026-11-24.

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
| `tls-migration/01-inventory.md` | read in full | `hld/02-architecture.md` |
| `tls-migration/02-certificate-plan.md` | read in full | `hld/02-architecture.md` |
| `tls-migration/tls-services.yaml` | read in full | `hld/02-architecture.md` |
| `tls-migration/evidence/inventory.json` | read in full | `hld/02-architecture.md` |

## Totals

| Status | Folders | Files |
| --- | ---: | ---: |
| not read | 0 | 0 |
| sampled | 0 | 0 |
| read in full | 8 | 24 |
| excluded | 0 | 0 |

## Coverage from coverage.py

The whole-analysis gate (`coverage.py --depth deep`, run on 24 Nov 2026 after this revision) counts 24 files in scope and 11 source files with a page: the inventory lists 14 source-language files, and the 3 empty `__init__.py` files hold no code. The figures are in `ledger/coverage-report.md`: result `PASS` at deep with 116/116 symbols, 98/98 functions with a full card, 320/320 branch lines, 232/232 call-graph edges, 2,213/2,213 citations, 17/17 front-matter pages, 2/2 calls into other components. `.github/bible/bible_queue.py` is 1,336 lines (`.github/bible/bible_queue.py:1-1336`). The separate catalog endpoint cards cover both manually matched GET paths; the static route counter detects none. The `.git` worktree pointer file that an earlier inventory listed as a 25th file is not part of the repository's content and is not in this inventory.

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->
