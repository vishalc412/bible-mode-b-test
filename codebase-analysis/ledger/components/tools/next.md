```text
NEXT PACKET 1 of 3 (0 done, 0%; 0 in this chat, budget 6)
Component: tools
Read:      tools/gate.py lines 1-117 (of 117), in full
Write:     codebase-analysis/lld/tools/gate.md (create; right under its title: Source file: `tools/gate.py`)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (6):
  - no page declares this file
  - card `fail` (function, lines 23-26) - branch lines to cite: 24, 26; calls: `print`; stamp `<!-- code: de986c493730 -->`: not named on the page
  - card `read` (function, lines 29-30) - branch lines to cite: 30; calls: `path.exists`, `path.read_text`; stamp `<!-- code: ed281972388d -->`: not named on the page
  - card `count_tests` (function, lines 33-39) - branch lines to cite: 35, 36, 37; calls: `ast.walk`, `ast.parse`, `read_text`, `isinstance`, `node.name.startswith`; stamp `<!-- code: 6d0b09eb9140 -->`: not named on the page
  - card `check` (function, lines 42-78) - branch lines to cite: 45, 47, 51, 53, 55, 57, 59, 61, 63, 64, 69, 71, 76; calls: `read`, `sorted`, `count_tests`, `subprocess.run`, `errors.append`, `any`, `risks.splitlines`, `().as_posix`, `glob`, `p.relative_to`; stamp `<!-- code: 705feaea6761 -->`: not named on the page
  - card `main` (function, lines 81-113) - branch lines to cite: 87, 91, 96, 97, 99, 102, 105, 107, 109, 111; calls: `argparse.ArgumentParser`, `ap.add_argument`, `ap.parse_args`, `json.loads`, `read_text`, `fail`, `read`, `status.get`, `isinstance`, `errors.append`, `check`, `print`; stamp `<!-- code: 4d59bf2d5380 -->`: not named on the page

When every item is written, write one line to the user, and run next.py again.
Write only under lld/tools/, lld/api/tools/ and ledger/components/tools/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component tools
```
