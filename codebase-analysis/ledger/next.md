```text
NEXT DELTA recheck codebase-analysis/verification-report-2026-11-23.md (4 citations waiting in 1 pages)

Each line below cites code that changed. Open the code, correct the citation and the sentence it supports, then delete the marker:
  - line 60: | V-001 | `lld/bible-mode-b/bible_queue.md` (591 citations), `lld/bible-mode-b/README.md` (110), `hld/05-key-flows.md` (28), `knowledge/AGENT-CONTEXT.md` (17), others (37) | Citation off | major | Of 
  - line 61: | V-002 | `lld/bible-mode-b/bible_queue.md:2228` card `settings_of` | Wrong | major | The function now rejects a missing or non-object marker, an unsafe `analysis` path, a `depth` outside `DEPTH_VALUE
  - line 62: | V-003 | `lld/bible-mode-b/bible_queue.md:2120` card `main` | Overstated | major | `main` now has `--analysis` and `--depth` options, and refuses settings that `settings_of` rejects; the card omits a
  - line 64: | V-005 | `lld/bible-mode-b/bible_queue.md` | Omission | major | `Queue.continue_if_unfinished` (a method that re-asks Copilot to continue and checks the timeline) and `GitHub.me` have no card or help

Then run next.py again.

Note: --new-session ran before the last chat reached NEW CHAT or DONE, so its count carries over (4 other jobs so far). In the same chat this keeps the loop bounded; in a new chat after a failure it only means NEW CHAT comes sooner. A person can delete ledger/session.json for a full budget.
```
