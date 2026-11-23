```text
NEXT PACKET 1 of 3 (0 done, 0%; 0 in this chat, budget 6)
Component: catalog
Read:      components/catalog/service.py lines 1-49 (of 49), in full
Write:     codebase-analysis/lld/catalog/service.md (create; right under its title: Source file: `components/catalog/service.py`)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (6):
  - no page declares this file
  - card `CatalogHandler` (class, lines 15-37) - branch lines to cite: none; calls: none; stamp `<!-- code: f7c8d0d6009d -->`: not named on the page
  - card `CatalogHandler._send` (method, lines 16-22) - branch lines to cite: none; calls: `().encode`, `json.dumps`, `self.send_response`, `self.send_header`, `str`, `len`, `self.end_headers`, `self.wfile.write`; stamp `<!-- code: e4ce28347ba9 -->`: not named on the page
  - card `CatalogHandler.do_GET` (method, lines 24-34) - branch lines to cite: 26, 28, 32; calls: `urllib.parse.urlsplit`, `self._send`, `path.startswith`, `urllib.parse.unquote`, `len`, `catalog.price_of`; stamp `<!-- code: 36b27ea8c095 -->`: not named on the page
  - card `CatalogHandler.log_message` (method, lines 36-37) - branch lines to cite: none; calls: none; stamp `<!-- code: 98f39d7eebc6 -->`: not named on the page
  - card `make_server` (function, lines 40-43) - branch lines to cite: 42; calls: `os.environ.get`, `int`, `ThreadingHTTPServer`; stamp `<!-- code: a060da66ba9d -->`: not named on the page

When every item is written, write one line to the user, and run next.py again.
Write only under lld/catalog/, lld/api/catalog/ and ledger/components/catalog/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component catalog
```
