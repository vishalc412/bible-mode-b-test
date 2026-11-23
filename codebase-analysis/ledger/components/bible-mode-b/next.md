```text
NEXT PACKET 2 of 4 (1 done, 25%; 1 in this chat, budget 6)
Component: bible-mode-b
Read:      .github/bible/bible_queue.py lines 307-395 (of 844), in full
Write:     codebase-analysis/lld/bible-mode-b/bible_queue.md (extend)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (12):
  - card `now` (function, lines 307-309) - branch lines to cite: 309; calls: `os.environ.get`, `datetime.datetime.fromisoformat`, `datetime.datetime.now`, `stamp.replace`; stamp `<!-- code: 9fb56903ebfa -->`: not named on the page
  - card `age` (function, lines 312-313) - branch lines to cite: none; calls: `total_seconds`, `now`, `datetime.datetime.fromisoformat`, `stamp.replace`; stamp `<!-- code: f2f8bb65e56f -->`: not named on the page
  - card `settings_of` (function, lines 316-321) - branch lines to cite: 319, 320; calls: `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group`; stamp `<!-- code: a2abeca733b5 -->`: not named on the page
  - card `labels_of` (function, lines 324-325) - branch lines to cite: 325; calls: `isinstance`, `item.get`; stamp `<!-- code: 7a809f2b23af -->`: not named on the page
  - card `comp_label` (function, lines 328-329) - branch lines to cite: none; calls: none; stamp `<!-- code: 5ead08c5004d -->`: not named on the page
  - card `issue_text` (function, lines 332-338) - branch lines to cite: 336; calls: `gh.file`, `text.splitlines`, `startswith`, `strip`, `().strip`, `join`, `len`, `text.strip`; stamp `<!-- code: 0533b3261be5 -->`: not named on the page
  - card `assignment` (function, lines 341-345) - branch lines to cite: 343; calls: none; stamp `<!-- code: da5ca422ae7f -->`: not named on the page
  - card `json_file` (function, lines 348-353) - branch lines to cite: 351, 352; calls: `gh.file`, `json.loads`; stamp `<!-- code: 37acfbecddfa -->`: not named on the page
  - card `section` (function, lines 356-362) - branch lines to cite: 358, 362; calls: `re.search`, `re.escape`, `match.end`, `nxt.start`; stamp `<!-- code: 55167fd6e3c2 -->`: not named on the page
  - card `report_facts` (function, lines 365-378) - branch lines to cite: 368, 373, 378; calls: `re.sub`, `re.findall`, `len`, `sum`, `().splitlines`, `().startswith`, `re.search`, `section`, `line.lstrip`, `upper`, `printed.group`; stamp `<!-- code: a367c151c5b0 -->`: not named on the page
  - card `as_int` (function, lines 381-385) - branch lines to cite: 384; calls: `int`; stamp `<!-- code: 8081107d37e4 -->`: not named on the page
  - card `status_of` (function, lines 388-391) - branch lines to cite: 391; calls: `json_file`, `isinstance`; stamp `<!-- code: ad9adb38e0f7 -->`: not named on the page

When every item is written, write one line to the user, and run next.py again.
Write only under lld/bible-mode-b/, lld/api/bible-mode-b/ and ledger/components/bible-mode-b/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component bible-mode-b
```
