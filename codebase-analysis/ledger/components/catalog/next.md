```text
NEXT PACKET 2 of 3 (1 done, 33%; 1 in this chat, budget 6)
Component: catalog
Read:      components/catalog/catalog.py lines 1-47 (of 47), in full
Write:     codebase-analysis/lld/catalog/catalog.md (create; right under its title: Source file: `components/catalog/catalog.py`)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (7):
  - no page declares this file
  - card `get_product` (function, lines 15-17) - branch lines to cite: none; calls: `_PRODUCTS.get`; stamp `<!-- code: 9e5f194ac459 -->`: not named on the page
  - card `price_of` (function, lines 20-24) - branch lines to cite: 22, 23; calls: `get_product`, `KeyError`; stamp `<!-- code: 9339c8a1a6d3 -->`: not named on the page
  - card `in_stock` (function, lines 27-29) - branch lines to cite: none; calls: `get_product`; stamp `<!-- code: 9dfed2fca633 -->`: not named on the page
  - card `image_url` (function, lines 32-33) - branch lines to cite: none; calls: `sku.lower`; stamp `<!-- code: ba322139b301 -->`: not named on the page
  - card `fetch_supplier_feed` (function, lines 36-39) - branch lines to cite: none; calls: `urllib.request.urlopen`, `json.loads`, `resp.read`; stamp `<!-- code: d1d97f4f1787 -->`: not named on the page
  - card `apply_feed` (function, lines 42-47) - branch lines to cite: 44, 45; calls: `feed.get`, `float`, `int`; stamp `<!-- code: 8a9129d98a7c -->`: not named on the page

When every item is written, write one line to the user, and run next.py again.
Write only under lld/catalog/, lld/api/catalog/ and ledger/components/catalog/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component catalog
```
