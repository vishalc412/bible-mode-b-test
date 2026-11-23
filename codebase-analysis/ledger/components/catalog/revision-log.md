Status: CORRECTED AFTER VERIFICATION (report of 2026-11-23; corrections applied, not re-verified)

# Revision log

Applied from: `verification-report.md` of 2026-11-23, verdict PASS AFTER CORRECTIONS.

| Item | Location | What was done | Code re-opened | Agrees with the report? |
| --- | --- | --- | --- | --- |
| V-001 | `lld/catalog/README.md` | Added the orders HTTP client and test-only call path to the structure diagram and interface text; removed the claim that no HTTP caller is identified. | `components/orders/catalog_client.py:1-4,11,16,19-23,26-29`; `components/orders/test_catalog_client.py:37-58` | Yes |
| V-002 | `lld/catalog/catalog.md` | Removed the HTTP handler from `get_product`'s callers; retained its calls through `price_of` and `in_stock`. | `components/catalog/service.py:31`; `components/catalog/catalog.py:21,28` | Yes |
| V-003 | `lld/catalog/catalog.md` | Added `orders.line_total` to `price_of` callers and `orders.validate` to `in_stock` callers. | `components/orders/orders.py:19-20,35-42` | Yes |
| V-004 | `lld/catalog/README.md`, `lld/api/catalog.md` | Documented that the routes have no authentication/authorization checks and are served without TLS; added the HTTP transport risk for whole-system assembly. | `components/catalog/service.py:24-34,40-43`; `components/orders/catalog_client.py:1-4,11,19-23` | Yes |
| V-005 | `lld/catalog/test_catalog.md` | Corrected the Tests table rows to have three cells, matching the header. | `components/catalog/test_catalog.py:6-8` | Yes |
| V-006 | `lld/api/catalog/catalog.md`; `lld/catalog/README.md` | Added endpoint cards for both GET routes, including request/response details, auth status, data touched, and sequence diagrams; linked the cards from the public interface. | `components/catalog/service.py:24-34,40-43`; `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-62` | Yes |
| V-007 | `lld/catalog/service.md` | Added the `CatalogHandler.do_GET` to `catalog.price_of` call-graph edge. | `components/catalog/service.py:31` | Yes |
| V-008 | Whole-system `components.json` and `components.md` | Not applied: these are outside the catalog component's permitted write folders; the HTTP edge is recorded in the catalog README for assembly. | `components/orders/catalog_client.py:19-23` | Yes; deferred to whole-system assembly |
| N-01 | Whole-system data dictionary | Not applied: the note about the product `name` field is for the data dictionary, which is outside this component revision's permitted folders. | `components/catalog/catalog.py:8-12` | Yes; deferred to whole-system assembly |

## Statements added
- The orders HTTP client uses plain HTTP for `GET /price/<sku>` and is exercised by the orders tests.
- Catalog GET routes do not check authentication or authorization and the server is not configured for TLS.
- Endpoint cards describe both catalog GET routes and their handled response paths.

## Statements corrected
- `get_product`, `price_of`, and `in_stock` caller lists now match the inspected call sites.
- The structure diagram no longer implies there is no in-repository HTTP client.

## Statements withdrawn
- The caveat that HTTP clients not identified in the repository are omitted.
- The claim that no caller of the catalog HTTP routes is identified.

## Questions closed or narrowed
None.

## Items not applied, with the reason
- V-008 and N-01 are deferred to whole-system assembly because their target files are outside the catalog component's allowed folders.
