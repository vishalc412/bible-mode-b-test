# Coverage ledger

Depth: deep. Snapshot: 30 files in scope, 2026-11-24 (updated after the supplier-feed HTTPS change: six files under `https-migration/` were added) (the `.git` worktree pointer file is not part of the repository's content and is not in the inventory). Inventory: `ledger/inventory.json` of 2026-11-24.

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
| `https-migration/changed-files.txt` | read in full | `hld/02-architecture.md` |
| `https-migration/https-allowlist.txt` | read in full | `hld/02-architecture.md` |
| `https-migration/https-inventory.md` | read in full | `hld/02-architecture.md`, `lld/catalog/README.md` |
| `https-migration/https-migration-summary.md` | read in full | `hld/02-architecture.md`, `lld/catalog/catalog.md`, `lld/catalog/test_catalog.md`, `lld/catalog/README.md`, `reference/risks-and-surprises.md` |
| `https-migration/tests-before.txt` | read in full | `hld/02-architecture.md` |
| `https-migration/tests-after.txt` | read in full | `hld/02-architecture.md` |

## Totals

| Status | Folders | Files |
| --- | ---: | ---: |
| not read | 0 | 0 |
| sampled | 0 | 0 |
| read in full | 10 | 30 |
| excluded | 0 | 0 |

## Coverage from coverage.py

The whole-analysis gate (`coverage.py --depth deep`, run on 24 Nov 2026 after the update for the supplier-feed HTTPS change and the queue's re-check and replay changes) counts 30 files in scope and 11 source files with a page: the inventory lists 14 source-language files, and the 3 empty `__init__.py` files hold no code. The figures are in `ledger/coverage-report.md`. `.github/bible/bible_queue.py` is 1,434 lines (`.github/bible/bible_queue.py:1-1434`). The separate catalog endpoint cards cover both manually matched GET paths; the static route counter detects none. The `.git` worktree pointer file that an earlier inventory listed as a 25th file is not part of the repository's content and is not in this inventory.

<!-- cites .github/bible/bible_queue.py@a625b4c3353b1744b965b8bbee13e6b3ed5f72a6 -->
