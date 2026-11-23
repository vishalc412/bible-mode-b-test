# Progress

Repository: `/home/runner/work/bible-mode-b-test/bible-mode-b-test`
Depth: deep
Started: 2026-11-23
Version: not provided

## Pass 1 — Inventory

- Inventory snapshot: 20 in-scope files, 14 source files, 1,320 source lines, 108 classes and functions, 0 routes.
- The generated file list and symbol checklist are in `ledger/inventory.json` and `ledger/symbol-checklist.md`.
- The coverage ledger is `ledger/coverage-ledger.md`; all 20 files are not yet read.
- Excluded: `.git`, `codebase-analysis`, and the repository's `.github/skills/*` toolkits, as listed in the inventory checklist.

## Work plan

| Pass | Work | Status |
| --- | --- | --- |
| 1 | Inventory and coverage ledger | done |
| 2 | Components and packet plan; run discovery | done |
| 3–11 | Component pages and whole-system analysis | not started; outside this task |

## Components

| Component | Folders and files | Language | Starts by | Entry points | Packets |
| --- | --- | --- | --- | --- | ---: |
| `catalog` | `components/catalog/` | Python 3; standard-library HTTP server (`components/catalog/service.py:7-12`) | `python3 -m components.catalog.service` (`components/catalog/service.py:40-48`) | `CatalogHandler.do_GET`, `make_server` (`components/catalog/service.py:24-43`) | 3 |
| `orders` | `components/orders/` | Python 3; standard library (`components/orders/orders.py:1-5`) | Imported and called by Python code (`components/orders/test_orders.py:1-8`) | `line_total`, `order_total`, `validate`, `settle` (`components/orders/orders.py:19-51`) | 4 |
| `bible-mode-b` | `.github/bible/`, `.github/workflows/` | Python 3 and GitHub Actions YAML (`.github/bible/bible_queue.py:1-10`) | Manual dispatch, 15-minute schedule, and default-branch push workflows (`.github/workflows/bible-plan.yml:7-8`, `.github/workflows/bible-queue.yml:7-10`, `.github/workflows/bible-delta.yml:6-10,16-18`, `.github/workflows/poc-assign-copilot.yml:11-13`) | `bible_queue.py start`, `reconcile`, `delta` (`.github/bible/bible_queue.py:1-10,797-844`) | 4 |
| `tools` | `tools/` | Python 3 and Bash (`tools/plan.py:8-15`, `tools/fanout.sh:1-6`) | CLI and shell invocation (`tools/plan.py:41-61`, `tools/gate.py:81-116`, `tools/fanout.sh:1-6`) | `plan.py`, `gate.py`, `fanout.sh` (`tools/plan.py:41-61`, `tools/gate.py:81-116`, `tools/fanout.sh:1-6`) | 3 |

Discovery succeeded and wrote `components.json`, `components.md`, and issue texts under `ledger/issues/`. No component was started. Next: have the user choose component names or all before starting component analysis.
