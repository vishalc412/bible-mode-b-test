# Changelog of the analysis

Newest first. One entry per update: the commits brought in, the code each changed, and what the update did to the pages. Written by `tracking-codebase-changes`; commit subjects are quoted from the repository as written.

## 2026-11-23 23:23 · copilot/bible-mode-b-update-analysis · `?` → `c2c01b1757`

2 commits, 24 files changed in the analysed code; functions: 0 changed, 105 added, 0 removed (commits made after the analysis was recorded, by date).

| Commit | Date | Subject | Code changed |
| --- | --- | --- | --- |
| `c2c01b1757` | 2026-11-23 | Initial plan | outside the analysed files |
| `033eb420d4` | 2026-11-23 | Merge PR #82: whole verification, PASS AFTER CORRECTIONS (reviewer agent approved) | `.github/bible/bible_queue.py` (added): `GitHub.__init__`, `GitHub.request`, `GitHub.call`, `GitHub.paged`, `GitHub.issues`, `GitHub.ensure_label` ... added<br>`.github/workflows/bible-delta.yml` (added)<br>`.github/workflows/bible-plan.yml` (added)<br>`.github/workflows/bible-queue.yml` (added)<br>`.github/workflows/poc-assign-copilot.yml` (added)<br>`.gitignore` (added)<br>`README.md` (added)<br>`components/__init__.py` (added)<br>`components/catalog/__init__.py` (added)<br>`components/catalog/catalog.py` (added): `get_product`, `price_of`, `in_stock`, `image_url`, `fetch_supplier_feed`, `apply_feed` added<br>`components/catalog/service.py` (added): `CatalogHandler._send`, `CatalogHandler.do_GET`, `CatalogHandler.log_message`, `make_server` added<br>`components/catalog/test_catalog.py` (added): `CatalogTest.test_price_of_known_sku` added<br>`components/orders/__init__.py` (added)<br>`components/orders/catalog_client.py` (added): `catalog_url`, `remote_price`, `remote_line_total` added<br>`components/orders/orders.py` (added): `line_total`, `order_total`, `validate`, `settle` added<br>`components/orders/test_catalog_client.py` (added): `CatalogClientTest.setUpClass`, `CatalogClientTest.tearDownClass`, `CatalogClientTest.get`, `CatalogClientTest.test_remote_price`, `CatalogClientTest.test_remote_line_total`, `CatalogClientTest.test_quantity_must_be_positive` ... added<br>`components/orders/test_orders.py` (added): `OrdersTest.test_line_total` added<br>`tls-migration/01-inventory.md` (added)<br>`tls-migration/02-certificate-plan.md` (added)<br>`tls-migration/evidence/inventory.json` (added)<br>`tls-migration/tls-services.yaml` (added)<br>`tools/fanout.sh` (added)<br>`tools/gate.py` (added): `fail`, `read`, `count_tests`, `check`, `main` added<br>`tools/plan.py` (added): `scan`, `main` added |

Analysis: 293 citations moved to new lines, 268 marked for a recheck, 0 renamed paths; 17 cards or endpoints to write or rewrite, 0 removals. Details in `ledger/delta.md`.
