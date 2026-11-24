---
id: lld/catalog/test_catalog
kind: module
component: catalog
source: components/catalog/test_catalog.py
summary: Checks that price lookup returns the known SKU-1 price
reads: []
writes: []
calls: []
uses: [symbol:price_of]
config: []
exposes: []
---

# test_catalog

Source file: `components/catalog/test_catalog.py`

| | |
| --- | --- |
| Component | `catalog` (its design page is `README.md` in this folder) |
| Lines | 12 |
| Role | Contains one `unittest` check for a known product price. |
| Imports that matter | `unittest` and the sibling `catalog` module (`components/catalog/test_catalog.py:1-3`). |
| Module-level state | No runtime state is assigned; the test class and direct-execution guard are defined (`components/catalog/test_catalog.py:6-12`). |

## Summary

The test class inherits from `unittest.TestCase` and has one test. Running this file directly invokes `unittest.main()` (`components/catalog/test_catalog.py:6-12`).

## Index

| Symbol | Kind | Lines | Description |
| --- | --- | --- | --- |
| `CatalogTest` | test class | 6-8 | Holds the catalog price test (`components/catalog/test_catalog.py:6-8`). |
| `CatalogTest.test_price_of_known_sku` | test method | 7-8 | Checks the price for `SKU-1` (`components/catalog/test_catalog.py:7-8`). |

## Tests

| Test | What it checks | Evidence |
| --- | --- | --- |
| `CatalogTest` | Groups the catalog test under `unittest.TestCase` | `components/catalog/test_catalog.py:6-8` |
| `CatalogTest.test_price_of_known_sku` | Asserts that `catalog.price_of("SKU-1")` equals `24.0` | `components/catalog/test_catalog.py:7-8` |

## Module-level code

When run as the main module, the `__main__` guard calls `unittest.main()` (`components/catalog/test_catalog.py:11-12`).

## Surprises

The file contains only a known-SKU price assertion; it has no tests here for unknown SKUs, stock, image URLs, feed parsing, or HTTP behavior (inferred: the whole file, `components/catalog/test_catalog.py:1-12`, holds one test method).

<!-- cites components/catalog/test_catalog.py@9be40d147e425d178067c8b34f19b28b9b374d1f -->
