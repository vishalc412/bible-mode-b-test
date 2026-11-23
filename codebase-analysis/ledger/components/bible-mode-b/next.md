```text
NEXT PACKET 2 of 3 (1 done, 33%; 0 in this chat, budget 6)
Component: bible-mode-b
Read:      .github/bible/bible_queue.py lines 307-643 (of 848), in full
Write:     codebase-analysis/lld/bible-mode-b/README.md (extend)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (2):
  - card `Queue.run` (method, lines 489-525) - branch lines to cite: 494, 498, 500, 503, 505, 509, 512, 516, 517, 521, 523; calls: `settings.get`, `json_file`, `catalog.get`, `self.plan_phase`, `isinstance`, `c.get`, `().strip`, `n.strip`, `asked.split`, `self.render`, `join`, `self.run_issues`, `gh.close`, `self.component`, `endswith`, `startswith`, `type`, `str`, `as_int`, `self.start_chunk` and 3 more (ledger/symbol-checklist.md); stamp `<!-- code: 3557926dc2ac -->`: the code changed since the card was written: rewrite it and replace its stamp
  - card `Queue.component` (method, lines 565-642) - branch lines to cite: 568, 570, 572, 574, 578, 580, 586, 590, 592, 598, 599, 607, 608, 619, 628, 629; calls: `gh.branch_prs`, `pr.get`, `get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `status_of`, `status.get`, `self.check`, `len`, `self.start_chunk`, `self.estimate.get`, `gh.close`, `labels_of`, `max`, `h.get`, `i.get`, `report_facts`, `gh.file` and 4 more (ledger/symbol-checklist.md); stamp `<!-- code: 9d544dd09fb5 -->`: the code changed since the card was written: rewrite it and replace its stamp

When every item is written, write one line to the user, and run next.py again.
Write only under lld/bible-mode-b/, lld/api/bible-mode-b/ and ledger/components/bible-mode-b/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I .github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component bible-mode-b
```
