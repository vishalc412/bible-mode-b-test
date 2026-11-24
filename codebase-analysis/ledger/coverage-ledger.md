# Coverage ledger

Depth: deep. Snapshot: 24 files, 2026-11-24. Inventory: `ledger/inventory.json` of 2026-11-24.

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

The whole-analysis gate is being rerun after revision. The current source inventory includes 24 files and 14 source files; exact symbol, branch, call-graph and citation coverage is recorded below after the gate completes. `.github/bible/bible_queue.py` is 1,310 lines (`.github/bible/bible_queue.py:1-1310`). The separate catalog endpoint cards cover both manually matched GET paths; the static route counter detects none (`ledger/coverage-report.md`).

<!-- cites .github/bible/bible_queue.py@161344dc7ddde551f4020972e6d61c782a86d480 -->
