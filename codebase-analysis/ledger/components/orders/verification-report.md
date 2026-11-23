# Verification report

| | |
| --- | --- |
| Verdict | PASS |
| Scope | component orders |
| Analysis fingerprint | 2328b6c86811f8a8 (`status.py --fingerprint --component orders`, run after judging) |
| Analysis snapshot | 4 source files, 158 lines (`components.md` row for `orders`), generated 2026-11-23 |
| Repository at verification | 4 source files (plus empty `__init__.py`), 158 lines; no drift |
| Depth stated / depth found | deep / deep |
| Verified with | GitHub Copilot coding agent (model not stated) |
| Analysis produced with | not stated |
| Sampling level | standard |
| Date | 2026-11-23 |

## Summary

The orders pages (README and four module pages) are complete, deep and accurate. The coverage gate passes at 100% on every measure. Of 69 sampled citation rows, 68 were `Confirmed` and 1 was `Citation off`; accuracy is 100%. All four audited cards are `Complete`. Outside the sample I found five `minor` problems (two catalog citations a few lines off, one test range off by one, one "Called by" list that misses a test, one README wording point) and no `major` one. No secret value and no significant omission. The weakest area is the diagrams: the partner settlement call is drawn nowhere in the component, and the catalog-client edge has no protocol or port. The pages repeat the Q1 deployment explanation in four places; the repetition is consistent.

The answer to Q1 in `questions.md` (both catalog paths intentional; HTTP path called only by tests; plain HTTP to `CATALOG_URL`) is a user decision. The code agrees with it (`components/orders/orders.py:5,19-20,35-41`; `components/orders/catalog_client.py:11,14-23`; a search of `*.py` finds `remote_price` and `remote_line_total` called only from `components/orders/test_catalog_client.py`). I did not confirm it with the user, so it is unconfirmed here.

The same model family may have written and verified this analysis (authoring model not stated); a person or another model should re-check the sampled statements if that matters.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 4 / 4 (100%) |
| Symbols accounted for | 20 / 20 (100%) |
| Functions with a full card (pseudo-code, branches cited) | 7 / 7 (100%) |
| Branch lines cited / call-graph edges drawn / front matter | 8 / 8; 6 / 6; 5 / 5 |
| Routes with an endpoint card | 0 / 0 (orders declares no routes) |
| Citations that resolve | 161 / 161 (100%) |
| Coverage gate | PASS (own run, `verification-coverage.md`) |
| Citations in the analysis / checked | 161 / 69 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 68 / 1 / 0 / 0 / 0 |
| Omissions (significant) / Inconsistent | 0 / 1 (plus 2 minor omissions and 2 minor citation-off findings outside the sample) |
| Accuracy / citation quality | 100% (69/69) / 98.6% (68/69) |
| Cards audited: Complete / Partial / Shallow / Wrong | 4 / 0 / 0 / 0 |
| Depth / depth, usable | 100% / 100% |

## How the sample was selected

Standard level, component scope, from `ledger/components/orders/citations.tsv` (161 rows, produced by my own run of `coverage.py --component orders`).

- Group A (README.md of the component): rows 1-50, all.
- Group B (label `inferred`/`assumed`, outside README): rows 65, 131, 133, 136, all.
- Group C (headings naming rule, outbound, integration, security, secret, auth, permission, outside README): none; the only such headings are in the README, already in group A.
- Group D (all other rows, index divisible by 7): 56, 63, 70, 77, 84, 91, 98, 105, 112, 119, 126, 140, 147, 154, 161.
- Group E (calls into another component): `orders.py:20` `line_total` -> `catalog.price_of`, and `orders.py:40` `validate` -> `catalog.in_stock`. Both opened with the called functions at `components/catalog/catalog.py:20-24` and `27-29`. The cards say what each call does with its result: the price is multiplied by `qty` and a `KeyError` propagates; a false result becomes the "not enough stock" error, and an unknown SKU counts as false. `Confirmed`.

Total 69 rows. Rows with several citations on one line were counted as rows.

Depth audit (component has fewer than seven files, so the largest card of every non-test file, plus two more from `orders.py`): `order_total` (largest in `orders.py`), `remote_price` (largest in `catalog_client.py`), `validate`, `settle`.

## Earlier corrections re-confirmed

This verification follows an earlier report, kept as `verification-report-2026-11-23.md`, whose verdict was `PASS` with minor corrections. The pages and their fingerprint (`2328b6c86811f8a8`) have not changed since, so those minor findings still stand and are repeated below (V-001 to V-005). This round did not re-check statements flagged earlier by anyone but me.

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/orders/README.md:16` (row for `catalog_client.py:6-9`) | Citation off | minor | `catalog_client.py` imports only `json`, `os`, `urllib.parse`, `urllib.request`; the catalog import is in `orders.py` | `components/orders/catalog_client.py:6-9`; `components/orders/orders.py:5` | Cite `orders.py:5` for "local catalog modules" and keep `catalog_client.py:6-9` for the standard library |
| V-002 | `lld/orders/orders.md:66,79,123` (citation `catalog.py:17-22`) | Citation off | minor | `price_of` is lines 20-24; the `KeyError` is raised at 22-23 | `components/catalog/catalog.py:20-24` | Cite `catalog.py:20-24` |
| V-003 | `lld/orders/orders.md:147,165` (citation `catalog.py:25-27`) | Citation off | minor | `in_stock` is lines 27-29; 25-26 are blank | `components/catalog/catalog.py:27-29` | Cite `catalog.py:27-29`, as `README.md:80` already does |
| V-004 | `lld/orders/catalog_client.md:113` | Citation off | minor | `test_quantity_must_be_positive` ends at line 45; line 46 is blank | `components/orders/test_catalog_client.py:43-45` | Cite `43-45` |
| V-005 | `lld/orders/catalog_client.md:80` (remote_price "Called by") | Omission | minor | `test_odd_skus_are_quoted_not_misrouted` also calls `remote_price` | `components/orders/test_catalog_client.py:51-54` | Add that test to "Called by" |

V-003 against V-002 and README is also the one `Inconsistent` finding: the same `in_stock` function is cited as 27-29 in the README and 25-27 in `orders.md`.

## Coverage findings

`coverage.py --component orders`, run by me at depth `deep`: result PASS. Source files with a page 4/4; symbols 20/20; full cards 7/7; routes 0/0; citations that resolve 161/161; branch lines 8/8; same-file calls drawn 6/6; front matter 5/5; calls into other components cited 2/2. Drift since stored inventory: none. No `ledger/not-documented.md` exists, which means no exclusions. Totals: `components.md` row says 4 files, 158 lines; my count is 51 + 29 + 12 + 66 = 158 lines over four files, plus two empty `__init__.py` files (0 lines, not source). README says "18 functions/methods": I count 4 + 3 + 1 + 10 = 18. They agree.

## Depth findings

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `components/orders/orders.py` | `order_total` | Complete | Every branch (`loyal`, `items >= BULK_THRESHOLD`), the non-stacking `max`, rounding and error propagation match lines 23-32 |
| `components/orders/orders.py` | `validate` | Complete | Loop, `if`/`elif`, both messages, unknown SKU treated as not in stock; matches lines 35-42 |
| `components/orders/orders.py` | `settle` | Complete | URL choice, JSON body, header, timeout, `== 200` result and uncaught exceptions; matches lines 45-51 |
| `components/orders/catalog_client.py` | `remote_price` | Complete | URL quoting, timeout, JSON parse, float conversion and absence of a handler (so the 404 `HTTPError` propagates) match lines 19-23 |

Route cards: none (the component has no routes; a search for route patterns in `components/orders/` finds none).

## Diagram findings

Read only; no renderer is installed, so D9 is a syntax read.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` Structure | ok | ok | minor: the partner settlement call is left out on purpose and stated in the text | minor: the `catalog_client` -> `service` edge says HTTP but not the default port 8001 | ok | ok | ok | Every edge has a row in the evidence table, judged `Confirmed` |
| `orders.md` Call graph | ok | ok | minor: `settle` -> partner URL is not drawn, yet it is the component's only outside call from this module | ok | ok | ok | ok | Edges `line_total`->`price_of`, `order_total`->`line_total`, `validate`->`in_stock` match lines 20, 25, 40 |
| `catalog_client.md` Call graph | ok | ok | ok | minor: `GET /price/{quoted SKU}` has no protocol | ok | ok | ok | Edges match lines 21-23 and 29 |
| `test_catalog_client.md` Call graph | ok | ok | ok | ok | ok | ok | ok | Edges match lines 14-19, 56-62 |

D1: no sequence diagrams are required (no routes; no flow with three or more participants). No dashed edges, and the `inferred` statements are not drawn. A search of `components/orders/` for network, database, file, queue, mail and subprocess use (`urllib`, `socket`, `requests`, `sqlite`, `smtp`, `subprocess`, `open(`, `environ`) finds only the two `urllib` users and the one `os.environ.get("CATALOG_URL")`, all already documented. No missing outside system.

## Data dictionary and mind map findings

Not expected in component scope. Orders owns no store: the pages say so and cite the catalog's `_PRODUCTS` (`components/catalog/catalog.py:8-12`) correctly. Left to the whole verification.

## Knowledge base findings

Not expected in component scope. The five LLD pages carry front matter (`calls`, `reads`, `uses`) that matches the code: `external:partner-legacy.internal/settle` and `external:localhost:8099/settle` (`components/orders/orders.py:9,12`), `config:CATALOG_URL` (`components/orders/catalog_client.py:16`). Left to the whole verification.

## Readability and prose findings

Read as a new engineer: the README opens with a summary table, then responsibility, structure, modules, rules, outbound calls and surprises, in a sensible order; module pages open with a role table and summary and have an index with working anchors. Findings, all `minor`: the Q1 explanation appears four times (README Responsibility, Surprises, "For the whole-system pages", and `catalog_client.md` Surprises); consistent but repetitive. No claim numbers, no template text, no evidence lists standing in for explanation. Fifth-sentence check on the README (rows 5, 10, 15, 20, 25, 30, 35 and 40 of its citation-bearing lines): each statement says no more than its citation, apart from V-001.

## Ledger findings

Component scope: `progress.md` and `ledger/coverage-ledger.md` belong to the planning step and are not judged. The component folders match the discovery: `components/orders/` only (`components.json`). No "not read" or "excluded" rows apply.

## Consistency findings

Names (`orders`, `catalog`, `CATALOG_URL`, `partner-legacy.internal`) agree across the README, module pages and `components.md`. The only disagreement is V-003. `components.md` records orders -> catalog calls `in_stock, price_of`, which match the two group E calls. No secret value appears in the analysis (the search for password, secret, token and key finds only this report's own sentence about their absence and earlier report text). The plain-HTTP settlement URL (`components/orders/orders.py:9`) is documented as a risk in README Surprises, not a secret.

## Limits

- A sample was checked (standard level): 69 of 161 citation rows, and four depth cards, not every card.
- The coverage script matches names, not meaning.
- Verification shows the analysis matches the code, not that the code matches what runs in production.
- Diagrams were read, not rendered.
- The Q1 answer is a recorded user decision; I did not confirm it with the user.
- Whole-system pages, the data dictionary, the knowledge graph and the cross-component agreement with the HLD are not in this scope.
- The author's model is not stated; if the same model verified its own work, a person or another model should re-check V-001 to V-005 and a few confirmed statements.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 1-50 | Group A (README) | Confirmed, except the `catalog_client.py:6-9` row on README line 16 | Row for `README.md:16` `catalog_client.py:6-9` is `Citation off` (V-001) |
| 65, 131, 133, 136 | Group B (inferred) | Confirmed | Each absence checked by reading the function: no handler at `catalog_client.py:19-23` or `orders.py:45-51`; comments at `orders.py:7-12` say what the page says |
| 56, 63, 70, 77, 84, 91, 98, 105, 112, 119, 126, 140, 147, 154, 161 | Group D (index divisible by 7) | Confirmed | |
| `orders.py:20`, `orders.py:40` | Group E | Confirmed | See "How the sample was selected" |
| `orders.md:66,79,123,147,165`; `catalog_client.md:80,113` | Outside the sample | Citation off / Omission | V-002 to V-005 |
| `catalog_client.md:151`, `README.md:97,110` | Outside the sample | Confirmed | `catalog_client.py:3` docstring; `service.py:24-34,40-43` |
| Diagrams, search for outside calls, fingerprint, totals | Step 6 and 7 | See sections above | Fingerprint after judging: 2328b6c86811f8a8, same as the earlier report |
