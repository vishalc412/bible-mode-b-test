```text
NEXT PACKET 2 of 13 (11 done, 84%; 0 in this chat, budget 6)
Component: bible-mode-b
Read:      .github/bible/bible_queue.py lines 307-662 (of 867), in full
Write:     codebase-analysis/lld/bible-mode-b/README.md (extend)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (8):
  - card `Queue.held` (method, lines 431-450) - branch lines to cite: 435, 439, 440, 448; calls: `labels_of`, `any`, `ATTEMPT.sub`, `self.gh.set_body`, `re.search`, `self.gh.assign`, `self.gh.comment`, `self.gh.close`, `assignment`, `l.startswith`, `issue.get`, `self.model_for`, `get`, `base.group`; stamp `<!-- code: 469f7ed189c0 -->`: the code changed since the card was written: rewrite it and replace its stamp
  - card `Queue.model_for` (method, lines 452-454) - branch lines to cite: 454; calls: `labels_of`, `self.settings.get`; stamp `<!-- code: 17f084589886 -->`: branch lines not in its Branches and errors table: 454
  - card `Queue.fail_or_retry` (method, lines 464-483) - branch lines to cite: 467, 470, 478, 482; calls: `int`, `ATTEMPT.search`, `issue.get`, `self.gh.comment`, `self.gh.close_pr`, `self.gh.label`, `self.gh.unassign`, `self.gh.close`, `ATTEMPT.sub`, `re.search`, `self.gh.create_issue`, `sorted`, `assignment`, `self.model_for`, `base.group`, `labels_of`, `l.startswith`; stamp `<!-- code: c86515a02433 -->`: branch lines not in its Branches and errors table: 467, 470, 478, 482
  - card `Queue.reconcile` (method, lines 486-496) - branch lines to cite: 488, 490, 495; calls: `self.gh.default_branch`, `self.gh.issues`, `settings_of`, `self.log`, `self.run`, `type`; stamp `<!-- code: 405a62c3c051 -->`: branch lines not in its Branches and errors table: 488, 490, 495
  - card `Queue.run` (method, lines 498-534) - branch lines to cite: 503, 507, 509, 512, 514, 518, 521, 525, 526, 530, 532; calls: `settings.get`, `json_file`, `catalog.get`, `self.plan_phase`, `isinstance`, `c.get`, `().strip`, `n.strip`, `asked.split`, `self.render`, `join`, `self.run_issues`, `gh.close`, `self.component`, `endswith`, `startswith`, `type`, `str`, `as_int`, `self.start_chunk` and 3 more (ledger/symbol-checklist.md); stamp `<!-- code: 3557926dc2ac -->`: branch lines not in its Branches and errors table: 507, 525, 526, 530, 532
  - card `Queue.plan_phase` (method, lines 536-558) - branch lines to cite: 539, 541, 549, 552, 555, 557; calls: `self.run_issues`, `issue_text`, `gh.create_issue`, `self.render`, `assignment`, `settings.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`; stamp `<!-- code: f5b3e835d2d7 -->`: branch lines not in its Branches and errors table: 539, 541, 549, 552, 555, 557
  - card `Queue.start_chunk` (method, lines 560-572) - branch lines to cite: 564, 566, 571; calls: `gh.branch_sha`, `gh.create_branch`, `gh.reset_branch`, `self.run_issues`, `comp_label`, `issue_text`, `gh.create_issue`, `assignment`, `self.settings.get`; stamp `<!-- code: 7f612dd5f454 -->`: branch lines not in its Branches and errors table: 564, 566, 571
  - card `Queue.component` (method, lines 574-661) - branch lines to cite: 577, 579, 581, 583, 587, 590, 592, 598, 602, 604, 610, 611, 619, 620, 639, 648; calls: `gh.branch_prs`, `pr.get`, `get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `status_of`, `status.get`, `self.check`, `len`, `self.start_chunk`, `self.estimate.get`, `gh.close`, `labels_of`, `max`, `h.get`, `i.get`, `report_facts`, `gh.file` and 6 more (ledger/symbol-checklist.md); stamp `<!-- code: fc69fea4bbee -->`: the code changed since the card was written: rewrite it and replace its stamp

When every item is written, tick the packet in progress.md, write one line to the user, and run next.py again.
Keep going: run next.py after every packet until it prints NEW CHAT or DONE. Do not end your turn in between.
Command: python3 -I .github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep

Note: --new-session ran before the last chat reached NEW CHAT or DONE, so its count carries over (2 other jobs so far). In the same chat this keeps the loop bounded; in a new chat after a failure it only means NEW CHAT comes sooner. A person can delete ledger/session.json for a full budget.
```
