---
id: lld/catalog/README
kind: component
component: catalog
source: [components/catalog/catalog.py, components/catalog/service.py, components/catalog/test_catalog.py]
summary: Provides product data and price and stock lookups to orders and over HTTP
reads: [store:_PRODUCTS, external:Supplier One]
writes: [store:_PRODUCTS]
calls: [external:Supplier One]
uses: [symbol:price_of, symbol:in_stock]
config: [config:CATALOG_HOST, config:CATALOG_PORT]
exposes: [route:GET /health, route:GET /price/{sku}]
---

# catalog

| | |
| --- | --- |
| Kind | service and Python library |
| Folders and files | `components/catalog/` |
| Technology | Python 3, standard-library `http.server`, `urllib.request`, `json`, and `unittest` (`components/catalog/service.py:7-12`, `components/catalog/catalog.py:2-3`, `components/catalog/test_catalog.py:1-3`) |
| Starts by | `python3 -m components.catalog.service` (per the module docstring, `components/catalog/service.py:1-5`); the main guard starts the server (`components/catalog/service.py:46-49`). |
| Size | 3 source files, 108 lines, 10 runtime functions, 2 GET path matches (`components/catalog/catalog.py:15-47`, `components/catalog/service.py:15-43`) |
| Depth | deep |

## Responsibility

The component stores three product records in the module-level `_PRODUCTS` dictionary and provides price and stock lookups (`components/catalog/catalog.py:8-12,15-29`). `orders` imports this module and calls `price_of` and `in_stock` directly (`components/orders/orders.py:5,19-20,35-42`). The HTTP server also offers GET handling for health and price paths, with `price_of` supplying the price response (`components/catalog/service.py:24-34`). Catalog code includes functions to fetch and apply supplier data, but no feed scheduling or orchestration is defined in this component (`components/catalog/catalog.py:36-47`).

## Structure

The modules and their direct data and call paths are shown below; the HTTP client is exercised by the orders tests.

```mermaid
flowchart TB
  orders["orders<br/>direct in-process caller"]
  ordershttp["orders.catalog_client<br/>remote price client"]
  ordershttptests["test_catalog_client.py<br/>exercises remote client"]
  subgraph catunit["catalog"]
    service["service.py<br/>HTTP GET handler"]
    catalogmod["catalog.py<br/>lookups and feed updates"]
    records[("_PRODUCTS<br/>in-memory product records")]
    testmod["test_catalog.py<br/>known-price test"]
  end
  supplier{{"Supplier One feed<br/>external"}}
  orders -->|"price_of and in_stock"| catalogmod
  ordershttptests -->|"calls remote_price and remote_line_total"| ordershttp
  ordershttp -->|"GET /price/{sku}<br/>HTTP, default :8001<br/>tests only in repository"| service
  service -->|"catalog.price_of"| catalogmod
  catalogmod -->|"reads and updates"| records
  testmod -->|"catalog.price_of"| catalogmod
  catalogmod -->|"urlopen, HTTP"| supplier
```

| Element | Evidence |
| --- | --- |
| `orders` -> `catalogmod` | `components/orders/orders.py:5,19-20,35-42` |
| `ordershttptests` -> `ordershttp` | `components/orders/test_catalog_client.py:37-54` |
| `ordershttp` -> `service` | `components/orders/catalog_client.py:1-4,11,16,19-23`; search `remote_price|remote_line_total` in `*.py`: 10 hits in 2 files, calls occur in `test_catalog_client.py` and the client's internal call at `components/orders/catalog_client.py:29` |
| `service` -> `catalogmod` | `components/catalog/service.py:12,24-34` |
| `catalogmod` -> `_PRODUCTS` | `components/catalog/catalog.py:8-12,15-17,42-47` |
| `testmod` -> `catalogmod` | `components/catalog/test_catalog.py:3,7-8` |
| `catalogmod` -> supplier feed | `components/catalog/catalog.py:5,36-39` |

## Modules

| Module page | Source file | Lines | Role | Main functions |
| --- | --- | ---: | --- | --- |
| [catalog](catalog.md) | `components/catalog/catalog.py` | 47 | Stores products and provides price, stock, image, and feed functions. | `get_product`, `price_of`, `in_stock`, `image_url`, `fetch_supplier_feed`, `apply_feed` (`components/catalog/catalog.py:15-47`) |
| [service](service.md) | `components/catalog/service.py` | 49 | Implements JSON GET responses and constructs the threaded server. | `CatalogHandler.do_GET`, `make_server` (`components/catalog/service.py:24-43`) |
| [test_catalog](test_catalog.md) | `components/catalog/test_catalog.py` | 12 | Checks a known-SKU price lookup. | `CatalogTest.test_price_of_known_sku` (`components/catalog/test_catalog.py:6-8`) |

## Main types

`CatalogHandler` is the component's request-handler class; it has no declared data attributes and defines the three methods shown. `make_server` passes it to `ThreadingHTTPServer` (`components/catalog/service.py:15-22,24-37,40-43`).

```mermaid
classDiagram
  class CatalogHandler {
    +_send(code, payload)
    +do_GET()
    +log_message(*args)
  }
  class ThreadingHTTPServer
  ThreadingHTTPServer --> CatalogHandler : uses handler
```

| Element | Evidence |
| --- | --- |
| `CatalogHandler` methods | `components/catalog/service.py:15-37` |
| `ThreadingHTTPServer` uses `CatalogHandler` | `components/catalog/service.py:10,40-43` |

## Public interface

| Interface | Kind | Card or page | Evidence |
| --- | --- | --- | --- |
| `catalog.price_of(sku)` | function | [catalog module](catalog.md#price_ofsku) | `orders` calls it for each line total (`components/orders/orders.py:19-20`). |
| `catalog.in_stock(sku, qty)` | function | [catalog module](catalog.md#in_stocksku-qty1) | `orders.validate` calls it for positive-quantity lines (`components/orders/orders.py:35-42`). |
| `GET /health` | route | [endpoint card](../api/catalog/catalog.md#get-health) | The handler matches `/health` and returns status 200 (`components/catalog/service.py:26-27`). |
| `GET /price/<sku>` | route | [endpoint card](../api/catalog/catalog.md#get-pricesku) | The handler matches the `/price/` prefix, looks up the remaining decoded path, and responds (`components/catalog/service.py:28-34`). |
| `python3 -m components.catalog.service` | command | [service module](service.md#module-level-code) | The documented invocation and main guard (`components/catalog/service.py:1-5,46-49`). |

`orders.catalog_client.remote_price` constructs `GET /price/<sku>` using `CATALOG_URL` (default `http://127.0.0.1:8001`) and plain HTTP. A search for `remote_price|remote_line_total` in Python files found 10 hits in 2 files: the test call sites and `remote_line_total`'s internal call to `remote_price`; no other in-repository caller was found (`components/orders/catalog_client.py:1-4,11,16,19-23,26-29`; `components/orders/test_catalog_client.py:37-54`; search `remote_price|remote_line_total` in `*.py`).

The GET routes do not check authentication or authorization, and the server is created with `ThreadingHTTPServer` without TLS configuration (inferred: `CatalogHandler.do_GET` has no identity or permission checks and `make_server` constructs the server that the module identifies as HTTP; `components/catalog/service.py:24-34,40-43,48`).

## Business rules

| # | Rule, in plain words | Enforced in | Triggered by | Evidence |
| --- | --- | --- | --- | --- |
| C-01 | A missing SKU has no price and causes `price_of` to raise `KeyError` with the SKU in its message. | `price_of` | Price lookup | `components/catalog/catalog.py:20-24` |
| C-02 | Stock is sufficient only when a product exists and its stock is at least the requested quantity. | `in_stock` | Stock lookup | `components/catalog/catalog.py:27-29` |
| C-03 | Supplier-feed entries update only SKUs already present in `_PRODUCTS`; absent product lists produce no updates. | `apply_feed` | Feed application | `components/catalog/catalog.py:44-47` |
| C-04 | `GET /health` returns the health response with status 200. | `CatalogHandler.do_GET` | `/health` path | `components/catalog/service.py:24-27` |
| C-05 | An unrecognized catalog GET path returns status 404. | `CatalogHandler.do_GET` | Any unmatched path | `components/catalog/service.py:33-34` |

## Data

| Store or file | Reads | Writes | Data dictionary entry |
| --- | --- | --- | --- |
| `_PRODUCTS` (in-memory dictionary) | `get_product`, `price_of`, `in_stock`, and `apply_feed` read existing products (`components/catalog/catalog.py:8-12,15-29,44-45`). | `apply_feed` changes `price` and `stock` for matching products (`components/catalog/catalog.py:44-47`). | [Catalog module](catalog.md#module-level-code) |
| Supplier JSON response | `fetch_supplier_feed` reads and JSON-decodes the response body (`components/catalog/catalog.py:36-39`). | Not written by this component. | [Catalog module](catalog.md#fetch_supplier_feedtimeout10) |

## Outbound calls

| Target | Purpose | Protocol and scheme | Address from | Timeout, retry, fallback | Evidence |
| --- | --- | --- | --- | --- | --- |
| Supplier One feed (`feeds.supplier-one.example.com`) | Fetch product JSON | HTTP | Hard-coded `SUPPLIER_FEED_URL` | `timeout=10` by default; no retry or fallback in the function | `components/catalog/catalog.py:5,36-39` |

## Configuration read

| Key | Purpose | Default | Source | Evidence |
| --- | --- | --- | --- | --- |
| `CATALOG_HOST` | HTTP server bind host | `127.0.0.1` when the `host` argument is falsey | Environment, unless a truthy function argument is provided | `components/catalog/service.py:40-41` |
| `CATALOG_PORT` | HTTP server bind port | `8001` when `port` is `None` and the variable is unset | Environment, unless `port` is not `None` | `components/catalog/service.py:40,42` |

## Errors and resilience

`price_of` raises `KeyError` for a missing SKU; the `/price/` handler catches `KeyError` from its success response expression and returns 404 (`components/catalog/catalog.py:20-24`, `components/catalog/service.py:30-33`). The supplier fetch has a timeout argument but does not catch errors or retry (`components/catalog/catalog.py:36-39`). `apply_feed` directly indexes item fields and converts price and stock, so missing fields or invalid conversions can raise (`components/catalog/catalog.py:44-47`).

## Logging and monitoring

`CatalogHandler.log_message` discards the handler's log message by doing nothing (`components/catalog/service.py:36-37`). The three catalog source files define no metrics or tracing calls (inferred: a search of the three files for `metric`, `trace`, `opentelemetry`, `statsd` and `logging` found nothing; `components/catalog/catalog.py:1-47`, `components/catalog/service.py:1-49`, `components/catalog/test_catalog.py:1-12`).

## Tests

`CatalogTest.test_price_of_known_sku` asserts that `SKU-1` has price `24.0`; direct execution invokes `unittest.main()` (`components/catalog/test_catalog.py:6-12`). The test file contains no checks for missing SKUs, stock, images, feed processing, or HTTP behavior (`components/catalog/test_catalog.py:6-8`).

## Surprises

`orders` uses direct Python calls to `price_of` and `in_stock`; it also has an HTTP client for the price route, which is exercised by the orders tests (`components/orders/orders.py:5,19-20,35-42`; `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-54`). The supplier URL uses plain HTTP, and the fetch function's docstring says it runs nightly from cron, but a search for `fetch_supplier_feed` in the repository outside the analysis folder finds only its definition (`components/catalog/catalog.py:36-39`; search: `fetch_supplier_feed`, excluding `codebase-analysis/`). This component does not show the claimed schedule.

The component and class diagrams were checked by reading their syntax; no Mermaid renderer was available.

## For the whole-system pages

- **Risk:** The catalog GET routes have no authentication or authorization checks and use plain HTTP without TLS; the known orders HTTP client also uses plain HTTP (`components/catalog/service.py:24-34,40-43,48`; `components/orders/catalog_client.py:1-4,11,19-23`).
- **Risk:** Supplier-feed transport uses plain HTTP, and the URL is hard-coded (`components/catalog/catalog.py:5,36-39`).
- **Surprise:** The supplier-fetch docstring claims a nightly cron run, but no invocation is shown by a search for `fetch_supplier_feed` outside the analysis folder (its only hit is the definition at `components/catalog/catalog.py:36`) or by the function body (`components/catalog/catalog.py:36-39`).
- **Open questions:** No question requiring a person to answer was identified from the catalog component files.
- **Glossary:** `SKU` is the key used to identify each product in `_PRODUCTS` (`components/catalog/catalog.py:8-12`); the supplier feed's `products` collection contains the entries consumed by `apply_feed` (`components/catalog/catalog.py:42-47`).

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/catalog/test_catalog.py@9be40d147e425d178067c8b34f19b28b9b374d1f -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->
