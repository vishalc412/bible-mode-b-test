# Questions: orders

- [ ] Q1. Is `catalog_client.py` intended to be the production catalog access path when orders runs as a separate service, or is the direct import in `orders.py` intentional? The client module describes the HTTP path, but the main order module imports `components.catalog.catalog`, and the client functions have no production caller found in `components/**/*.py`.
