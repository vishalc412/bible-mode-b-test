---
id: lld/catalog/test_catalog
kind: module
component: catalog
source: components/catalog/test_catalog.py
summary: Checks the known SKU-1 price, that the supplier feed is fetched over verified HTTPS, and that a redirect to HTTP is refused
reads: []
writes: []
calls: []
uses: [symbol:price_of, symbol:fetch_supplier_feed, symbol:NoHTTPRedirectHandler]
config: []
exposes: []
---

# test_catalog

Source file: `components/catalog/test_catalog.py`

| | |
| --- | --- |
| Component | `catalog` (its design page is `README.md` in this folder) |
| Lines | 48 |
| Role | Contains three `unittest` checks: a known product price, the verified-HTTPS supplier fetch, and the refusal of a redirect to `http://`. |
| Imports that matter | `ssl`, `unittest`, `unittest.mock.patch`, `urllib.error.HTTPError`, `urllib.request.HTTPSHandler` and `Request`, and the sibling `catalog` module (`components/catalog/test_catalog.py:1-7`). |
| Module-level state | No runtime state is assigned; the test class and direct-execution guard are defined (`components/catalog/test_catalog.py:10-48`). |

## Summary

The test class inherits from `unittest.TestCase` and has three tests. Two of them cover the HTTPS migration of the supplier feed; neither contacts the network, because the first replaces `build_opener` with a mock and the second calls the redirect handler directly (`components/catalog/test_catalog.py:10-44`). Running this file directly invokes `unittest.main()` (`components/catalog/test_catalog.py:47-48`).

## Index

| Symbol | Kind | Lines | Description |
| --- | --- | --- | --- |
| `CatalogTest` | test class | 10-44 | Holds the three catalog tests (`components/catalog/test_catalog.py:10-44`). |
| `CatalogTest.test_price_of_known_sku` | test method | 11-12 | Checks the price for `SKU-1` (`components/catalog/test_catalog.py:11-12`). |
| `CatalogTest.test_supplier_feed_uses_verified_https` | test method | 14-30 | Checks the opener, the SSL context and the URL used by `fetch_supplier_feed` (`components/catalog/test_catalog.py:14-30`). |
| `CatalogTest.test_supplier_feed_rejects_redirect_to_http` | test method | 32-44 | Checks that `NoHTTPRedirectHandler.redirect_request` raises `HTTPError` for an `http://` target (`components/catalog/test_catalog.py:32-44`). |

## Tests

| Test | What it checks | Evidence |
| --- | --- | --- |
| `CatalogTest` | Groups the catalog tests under `unittest.TestCase` | `components/catalog/test_catalog.py:10` |
| `CatalogTest.test_price_of_known_sku` | Asserts that `catalog.price_of("SKU-1")` equals `24.0` | `components/catalog/test_catalog.py:11-12` |
| `CatalogTest.test_supplier_feed_uses_verified_https` | Patches `urllib.request.build_opener` in the catalog module and makes the mocked response body `{"products": []}`; asserts that `fetch_supplier_feed()` returns `{"products": []}`, that `build_opener` was called once with a `NoHTTPRedirectHandler` and an `HTTPSHandler`, that the handler's context has `check_hostname` true and `verify_mode` `ssl.CERT_REQUIRED`, and that `open` was called once with `https://feeds.supplier-one.example.com/v2/products.json` and `timeout=10` | `components/catalog/test_catalog.py:14-30` |
| `CatalogTest.test_supplier_feed_rejects_redirect_to_http` | Builds a `NoHTTPRedirectHandler` and a request for the HTTPS feed URL; asserts that `redirect_request` called with status `302`, reason `Found`, empty headers and an `http://` target raises `HTTPError` | `components/catalog/test_catalog.py:32-44` |

## Module-level code

When run as the main module, the `__main__` guard calls `unittest.main()` (`components/catalog/test_catalog.py:47-48`).

## Surprises

The second test reads the private attribute `_context` of the `HTTPSHandler` instance (`components/catalog/test_catalog.py:25`), which ties the test to a CPython implementation detail (assumed: `urllib.request.HTTPSHandler` keeps its context in `_context`). The file has no tests for unknown SKUs, stock, image URLs, `apply_feed`, or the HTTP server's behaviour (inferred: the whole file, `components/catalog/test_catalog.py:1-48`, holds three test methods, and they call only `price_of`, `fetch_supplier_feed` and `NoHTTPRedirectHandler`). The tests do not show that the live supplier endpoint presents a valid certificate (inferred: per `https-migration/https-migration-summary.md:29`).

<!-- cites components/catalog/test_catalog.py@29eeea56df47ceb3c96481a327851eee696ec67d -->

<!-- cites https-migration/https-migration-summary.md@8af6a247647debc371a600624b95b7c94326da9c -->
