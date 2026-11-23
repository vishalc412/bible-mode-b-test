```text
NEXT PACKET 2 of 3 (1 done, 33%; 1 in this chat, budget 6)
Component: tools
Read:      tools/plan.py lines 1-62 (of 62), in full
Write:     codebase-analysis/lld/tools/plan.md (create; right under its title: Source file: `tools/plan.py`)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (3):
  - no page declares this file
  - card `scan` (function, lines 21-38) - branch lines to cite: 23, 24, 27, 29, 30, 31, 33, 34; calls: `sorted`, `component_dir.glob`, `().as_posix`, `append`, `path.read_text`, `path.name.startswith`, `ast.walk`, `enumerate`, `path.relative_to`, `ast.parse`, `isinstance`, `text.splitlines`, `HTTP.finditer`, `functions.append`, `http_sites.append`, `match.group`, `count_tests`; stamp `<!-- code: 86c2bf11760e -->`: not named on the page
  - card `main` (function, lines 41-58) - branch lines to cite: 43, 44; calls: `sorted`, `iterdir`, `d.is_dir`, `scan`, `d.name.startswith`, `out.parent.mkdir`, `out.write_text`, `json.dumps`, `print`, `out.relative_to`, `len`; stamp `<!-- code: fec6042cdffb -->`: not named on the page

When every item is written, write one line to the user, and run next.py again.
Write only under lld/tools/, lld/api/tools/ and ledger/components/tools/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component tools
```
