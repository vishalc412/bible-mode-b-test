# Questions: orders

- [x] Q1. Is `catalog_client.py` intended to be the production catalog access path when orders runs as a separate service, or is the direct import in `orders.py` intentional? The client module describes the HTTP path, but the main order module imports `components.catalog.catalog`, and the client functions have no production caller found in `components/**/*.py`.
  Answer: Both paths are intentional. `orders.py` imports the catalog directly when orders and catalog run in one process (today's deployment). `catalog_client.py` is for orders running as its own service and reads prices from the catalog HTTP API (`components/catalog/service.py`). The HTTP path exists, its only callers are the tests, and it uses plain HTTP to `CATALOG_URL` (default `http://127.0.0.1:8001`).
