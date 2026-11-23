# Catalog–orders TLS inventory

## Inputs and discovery

- Side: both. Environment: local, with no operator policy file.
- Producer: catalog, Python 3 standard-library `ThreadingHTTPServer`; consumer: orders, Python 3 standard-library `urllib.request`. Discovery ran with Python 3.12.3.
- Allowed consumer supplied: `orders`; owner: orders team; contact: repository owner; cadence: per order.
- Issuer: local development CAs, to be created by `local-tls-up.sh` on the developer machine, not in this run.
- Later build/test command: `python3 -m unittest discover -s . -p "test_*.py" -t .`. Live probes are to run on the developer machine at `127.0.0.1`; no live probes were run here.
- Analysis status check: exit 20, `UNVERIFIED (COMPONENTS_VERIFIED)`; no whole-analysis verification report. The knowledge graph `codebase-analysis/knowledge/graph.json` is absent. Analysis files are leads only; the findings below are confirmed against source.
- Machine-readable scanner output: `tls-migration/evidence/inventory.json`.

## Endpoints

| Endpoint | Role | Purpose | Criticality | Where set (file:line) | Runtime | Status | Impact | Priority | Decision | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `127.0.0.1:8001/price/<sku>` | we produce | Serve catalog prices | high | `components/catalog/service.py:24-33,40-43` | Python stdlib HTTP server; host and port overridden by `CATALOG_HOST`/`CATALOG_PORT` | to migrate | Separate-service orders cannot read prices if unavailable | 1 | migrate now | Server names and HTTPS port need confirmation; do not infer overrides from defaults. |
| `http://127.0.0.1:8001/price/<sku>` | we consume (internal) | Read prices and calculate remote line totals | high | `components/orders/catalog_client.py:11,14-23,26-29` | Python stdlib `urllib`; `CATALOG_URL` read per call | to migrate | Remote pricing/line totals fail for orders | 1 | migrate now | Default is HTTP; no explicit retry or HTTP fallback in this client. SKU is URL-quoted. |
| `127.0.0.1:8001/health` | we produce | Health response | medium | `components/catalog/service.py:24-27,40-43` | Same HTTP listener | to migrate | Existing health checks may fail during listener changes | 1 | migrate now | Health consumers and a separate local management port are not established by source; confirm before implementation. |
| `http://127.0.0.1:<ephemeral>/price/<sku>` and `/health` | we consume (internal) | Exercise catalog HTTP API in tests | low | `components/orders/test_catalog_client.py:13-19,30-62` | Local test server with dynamically allocated port | to migrate | HTTP integration tests must be adapted without losing their current assertions | 1 | migrate now | Test-only address, not another production consumer. |
| `http://feeds.supplier-one.example.com/v2/products.json` | third party | Fetch supplier product feed | high | `components/catalog/catalog.py:5,32-35` | Python stdlib `urllib` | not probed | Supplier feed fetch fails; product updates may be unavailable | — | out of scope | Separate HTTPS migration, issue #75; no external connection made. |
| `http://partner-legacy.internal/settle` | third party | Submit order settlement | high | `components/orders/orders.py:7-9,44-50` | Python stdlib `urllib` | not probed | Settlement requests fail | — | out of scope | Separate HTTPS migration, issue #75; no external connection made. |
| `http://localhost:8099/settle` | third party | Developer payment fake | low | `components/orders/orders.py:11-12,44-50` | Local fake selected by `dev=True` | not probed | Developer settlement flow fails if unavailable | — | out of scope | Payment integration, not the catalog listener. |
| `https://cdn.example.com/img/<sku>.jpg` | third party | Construct product image URL | low | `components/catalog/catalog.py:6,28-29` | URL returned to caller; no fetch in this function | not probed | Image consumers may be unable to load images | — | out of scope | Already HTTPS; no external connection made. |

`components/orders/orders.py:5,19-20,38-40` directly imports catalog for in-process pricing and stock validation; it does not use this network endpoint. The separate-service client is currently called by its own `remote_line_total` and by `components/orders/test_catalog_client.py:37-54`; no other repository callers were found.

The scanner's `http://%s:%d` at `components/catalog/service.py:48` is a formatted startup message, not a literal host. The analysis-document matches duplicate the addresses above and are not separate endpoints. `CATALOG_URL`, `CATALOG_HOST`, and `CATALOG_PORT` can be set at runtime; additional configured addresses cannot be inferred from this checkout.

## Separate findings and open items

- Scanner found no code that switches certificate checking off, no private-key or keystore files, and no `local-dev-` references outside local-only files.
- Scanner flagged AI-directed text at `.github/bible/bible_queue.py:284`; it was treated as data, not an instruction.
- Confirm actual local HTTPS listener port, names used by callers, health-check consumers and management port before implementing. The existing default is only `127.0.0.1:8001` for HTTP.
- The supplied cadence is per order; any readiness tooling requiring an enumerated observation cadence needs an explicit owner decision rather than silently changing that input.
- `unittest` does not itself produce the JUnit XML required by the later gate. No reporter was installed or approved here; tests and gate remain not run.
