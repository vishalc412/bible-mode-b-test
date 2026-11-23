---
id: lld/orders/test_catalog_client
kind: module
component: orders
source: components/orders/test_catalog_client.py
summary: Exercises the catalog HTTP client against a local catalog server
uses: [symbol:CatalogClientTest, component:catalog]
---
# test_catalog_client

Source file: `components/orders/test_catalog_client.py`

| | |
| --- | --- |
| Component | `orders` (its design page is `README.md` in this folder) |
| Lines | 66 |
| Role | Runs integration-style checks of the orders catalog client against a locally started catalog service. |
| Imports that matter | `components.catalog.service`, `components.orders.catalog_client`, `threading`, `unittest`, `urllib` (`components/orders/test_catalog_client.py:1-8`) |
| Module-level state | None declared (`components/orders/test_catalog_client.py:1-66`). |

## Summary

`CatalogClientTest` starts a catalog service on loopback and an ephemeral port, directs `CATALOG_URL` to it for the class's tests, then shuts down the server and restores the previous environment setting (`components/orders/test_catalog_client.py:12-28`). Its test methods check price retrieval, line totals, input validation, unknown and unusual SKUs, query handling, and percent-encoded SKU decoding (`components/orders/test_catalog_client.py:37-62`).

## Tests

| Test or support function | Lines | What it checks or does |
| --- | --- | --- |
| `CatalogClientTest` | 12-62 | Groups fixture setup, a GET helper, and seven test methods against the local catalog service (`components/orders/test_catalog_client.py:12-62`). |
| `CatalogClientTest.setUpClass` | 13-19 | Starts `service.make_server("127.0.0.1", 0)` in a daemon thread; stores the allocated base URL and current `CATALOG_URL`, then sets the environment variable to the local server URL (`components/orders/test_catalog_client.py:13-19`). |
| `CatalogClientTest.tearDownClass` | 21-28 | Shuts down and closes the server, then removes `CATALOG_URL` if it was initially unset or restores its saved value (`components/orders/test_catalog_client.py:21-28`). |
| `CatalogClientTest.get` | 30-35 | Requests a path from the local server with a five-second timeout; returns status and parsed JSON, including for `HTTPError` responses (`components/orders/test_catalog_client.py:30-35`). |
| `CatalogClientTest.test_remote_price` | 37-38 | Checks that the client returns `24.0` for `SKU-1` (`components/orders/test_catalog_client.py:37-38`). |
| `CatalogClientTest.test_remote_line_total` | 40-41 | Checks that the client returns `12.0` for two `SKU-3` items (`components/orders/test_catalog_client.py:40-41`). |
| `CatalogClientTest.test_quantity_must_be_positive` | 43-45 | Checks that a zero quantity raises `ValueError` (`components/orders/test_catalog_client.py:43-45`). |
| `CatalogClientTest.test_unknown_sku` | 47-49 | Checks that requesting `SKU-9` raises `urllib.error.HTTPError` (`components/orders/test_catalog_client.py:47-49`). |
| `CatalogClientTest.test_odd_skus_are_quoted_not_misrouted` | 51-54 | Checks that SKU strings containing `#`, `?`, a space, a non-ASCII character, or `/../health` raise `HTTPError` rather than resolving as a different successful request (`components/orders/test_catalog_client.py:51-54`). |
| `CatalogClientTest.test_query_string_ignored_by_server` | 56-58 | Checks that a query on `/health` leaves the response at 200 with `{"status": "ok"}`, and that the `SKU-1` price request with a query returns a price of `24.0` (`components/orders/test_catalog_client.py:56-58`). |
| `CatalogClientTest.test_percent_encoded_sku_decoded` | 60-62 | Checks that `/price/SKU%2D1` returns status 200 and a decoded SKU of `SKU-1` (`components/orders/test_catalog_client.py:60-62`). |

## Module-level code

When run as a script, the module invokes `unittest.main()` (`components/orders/test_catalog_client.py:65-66`).
