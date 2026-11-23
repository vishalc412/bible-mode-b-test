```text
NEXT PACKET 3 of 3 (2 done, 66%; 2 in this chat, budget 6)
Component: catalog
Read:      components/catalog/test_catalog.py lines 1-12 (of 12), in full
Write:     codebase-analysis/lld/catalog/test_catalog.md (create; right under its title: Source file: `components/catalog/test_catalog.py`)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (3):
  - no page declares this file
  - test `CatalogTest` (lines 6-8): name it in the page's tests table with what it checks
  - test `CatalogTest.test_price_of_known_sku` (lines 7-8): name it in the page's tests table with what it checks

When every item is written, write one line to the user, and run next.py again.
Write only under lld/catalog/, lld/api/catalog/ and ledger/components/catalog/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component catalog
```
