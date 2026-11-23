---
id: lld/orders/test_orders
kind: module
component: orders
source: components/orders/test_orders.py
summary: Checks the local order line-total helper
uses: [symbol:OrdersTest]
---
# test_orders

Source file: `components/orders/test_orders.py`

| | |
| --- | --- |
| Component | `orders` (its design page is `README.md` in this folder) |
| Lines | 12 |
| Role | Contains a unit test for `orders.line_total`. |
| Imports that matter | `unittest`, `components.orders.orders` (`components/orders/test_orders.py:1-3`) |
| Module-level state | None declared (`components/orders/test_orders.py:1-12`). |

## Summary

The `OrdersTest` test case checks the line total for two units of `SKU-3` (`components/orders/test_orders.py:6-8`).

## Tests

| Test or support function | Lines | What it checks or does |
| --- | --- | --- |
| `OrdersTest` | 6-8 | Defines the order helper's unit test (`components/orders/test_orders.py:6-8`). |
| `OrdersTest.test_line_total` | 7-8 | Asserts that `orders.line_total("SKU-3", 2)` equals `12.0` (`components/orders/test_orders.py:7-8`). |

## Module-level code

When run as a script, the module invokes `unittest.main()` (`components/orders/test_orders.py:11-12`).
