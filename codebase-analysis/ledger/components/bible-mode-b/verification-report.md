# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Scope | component bible-mode-b |
| Analysis fingerprint | dee0a05d04621400 |
| Analysis snapshot | component row in `components.md`: 1 source file, 844 lines (2026-11-23); no version given |
| Repository at verification | 1 source file (`.github/bible/bible_queue.py`), 848 lines, plus 4 workflow files in `.github/workflows/`; coverage drift: `bible_queue.py` 844 -> 848 lines against the stored inventory (2026-11-23). The pages already cite the 848-line file (README Size row) |
| Depth stated / depth found | deep / deep (front matter, full cards with cited branch lines, call graph) |
| Verified with | GitHub Copilot coding agent (model not stated) |
| Analysis produced with | not stated |
| Sampling level | standard |
| Date | 2026-11-23 |

## Summary

The component's two pages (`lld/bible-mode-b/README.md`, `lld/bible-mode-b/bible_queue.md`) are complete by the gate's measures and mostly accurate. I re-ran the coverage gate: it passes on every measure (650 of 650 citations resolve; 66 of 66 cards; 161 of 161 branch lines; 163 of 163 call edges).

Unlike the earlier rounds (fingerprint `e5dc7e620c582f3a`), these pages have been changed: the fingerprint differs, the source is 848 lines, and a few earlier corrections are fixed. I judged the pages as they are now, from the code, and read the earlier reports only afterwards.

I opened all 195 selected citation rows and compared each with the cited lines (the first three lines of each range were shown; ranges that carry a claim on later lines were opened in full). Result: 176 confirmed, 15 citation off, 1 overstated, 3 wrong. Accuracy is 97.9%, citation quality 90.3%.

Where it is weak:

- **`Queue.component` card is wrong in one place.** The card (steps 2 and 3, the pseudo-code, the branch row at line 583 and the `result.endswith` call) says that when the open session's `follow` result does not end in `merged`, the method returns it, and otherwise carries on. The code returns the `follow` result unconditionally (`.github/bible/bible_queue.py:585`); there is no `endswith` test. This is the largest card in the file and describes a different control flow (V-001).
- **25 `GitHub.*` cards say "No call site is in this source range"** although `Queue` and `main` call them as `self.gh.<name>(...)` or `gh.<name>(...)` (for example `tarball` at `.github/bible/bible_queue.py:706`, `merge` at `:693`, `create_issue` at `:834`). Only `GitHub.prs` is truly uncalled (V-002).
- **The call graph has five edges the code does not contain** (V-003).
- **The Surprises section (README lines 191 and 197) says `Queue.component` builds `closed_revise` but does not use it.** There is no `closed_revise` in the source; the earlier code was rewritten (V-004).

The verdict is `PASS AFTER CORRECTIONS`, not `PASS`: three `major` corrections stand, one audited card is `Wrong`, and a `Wrong` statement stands behind a diagram element (V-003). Coverage is 100%; accuracy 97.9% is above both bars; depth is 80% (4 of 5 audited cards), exactly the usable floor, so the depth figure is weak evidence from a five-card audit. Each problem has a specific correction. The author's model is not stated, so a person or another model should re-check the three `major` corrections.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 1 / 1 (100.0%) |
| Symbols accounted for | 68 / 68 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 66 / 66 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 161 / 161, 163 / 163, 2 / 2 (all 100.0%) |
| Routes with an endpoint card | 0 / 0 (100.0%) |
| Citations that resolve | 650 / 650 (100.0%) |
| Coverage gate | PASS |
| Citations in the analysis / selected / checked | 650 / 195 / 195 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 176 / 15 / 1 / 3 / 0 |
| Omissions (significant) / Inconsistent | 0 (4 minor) / 3 (V-002 major, V-004 minor, V-010 minor) |
| Accuracy / citation quality | 97.9% (191 / 195) / 90.3% (176 / 195) |
| Cards audited: Complete / Partial / Shallow / Wrong | 4 / 0 / 0 / 1 |
| Depth / depth, usable | 80% / 80% |

## How the sample was selected

Gate run by me: `coverage.py --repo . --analysis codebase-analysis --depth deep --component bible-mode-b --report ledger/components/bible-mode-b/verification-coverage.md`; it rewrote the component's `citations.tsv` (650 rows). Standard level:

- Group A (`README.md`): all 118 rows, indexes 1-118.
- Group B (`inferred` or `assumed`, outside the README): row 128 (the only one).
- Group C (headings with rule, outbound, security, auth): all fall on the README, so already in group A.
- Group D (module page rows whose index is divisible by 7): 76 rows, 119, 126, ... 644.
- Group E (calls into another component): none; the component calls no other component.

Total 118 + 1 + 76 = 195 rows, all judged by me in this session.

## Earlier corrections re-confirmed

none (this is not a re-check after a revision: no `revision-log.md` exists for this component). For information, the earlier round's findings against the current pages: V-001 (67 vs 66 functions) still stands (here V-005); V-002 (`ready` wraps only HTTP errors) still stands (V-006); V-003 (27 "No call site" rows) still stands (V-002); V-004 (five false edges) still stands (V-003); V-006 to V-008 (workflow not named, toolkit subprocess calls, no sequence or lifecycle diagram) still stand (V-007, V-008, V-009). Fixed since: the `BIBLE_AGENT_LOGINS` default in the Configuration table, the `Queue.render` caller list (now includes `Queue.plan_phase`) and the file's line count (848, now stated).

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/bible-mode-b/bible_queue.md` card `Queue.component`: steps 2-3 (about line 1832), pseudo-code (`result = follow(issue)`, `if not merged: return result`), branch row `bible_queue.py:583`, `Calls` entry `result.endswith` | Wrong | major | `Queue.component` returns `self.follow(analysis, name, issue)` directly for the first open session issue; there is no test of the result and no fall-through. The comment at 582-584 gives the reason (a merge is the end of this run's work for the component; the next step is decided at the next check). | `.github/bible/bible_queue.py:577-585` | Step 2: "If an open chunk or verification issue exists: return a human-needed status if it is held, otherwise return the result of `follow`." Delete the branch row for 583, the `endswith` call and the pseudo-code `if not merged` line; fix the step-3 range to 586-591 and say the method continues only when no open session issue exists. |
| V-002 | `lld/bible-mode-b/bible_queue.md`, row `Called by` of 25 `GitHub.*` cards (lines 561, 616, 644, 677, 698, 727, 748, 769, 851, 885, 931, 960, 1023, 1056, 1077, 1120, 1143, 1164, 1185, 1206, 1227, 1248, 1303, 1332, 1353) | Inconsistent | major | Each says "No call site is in this source range", yet each is called from `Queue` or `main` through `self.gh.<name>` or `gh.<name>`. Callers: `issues` 402, 479, 786, 830; `ensure_labels` 829; `create_issue` 472, 536, 562, 620, 634, 752, 789, 834; `default_branch` 478, 774; `branch_sha` 554-555; `create_branch` 556; `reset_branch` 558; `file` 334, 349, 607, 690, 731, 776; `linked_prs` 406, 727; `branch_prs` 568; `is_agent_pr` 408, 728; `start_error` 417, 449; `pr_files` 661, 664, 683; `commit_time` 423; `tarball` 706; `label` 450, 462, 673-674; `unlabel` 694; `comment` 440, 452, 459, 464, 467, 755; `close` 468, 506, 601, 695, 735, 756; `set_body` 437, 767; `unassign` 451, 463; `assign` 439, 785; `merge` 693; `close_pr` 460; `create_pr` 609. `GitHub.__init__` (line 419) is constructed at 820. Only `GitHub.prs` has no caller. | `.github/bible/bible_queue.py:402,706,693,834,820`; `grep -n "\.prs("` finds nothing | Fill each row with the caller and line; keep "No call site" only for `GitHub.prs` and say it is unused. |
| V-003 | `lld/bible-mode-b/bible_queue.md:193, 194, 197, 256, 280` (call graph) | Wrong | major | Five edges are not in the code: `issuetext -->\|"file"\| call` and `jsonfile -->\|"file"\| call` (both call `gh.file`, which is `GitHub.file`, not `GitHub.call`), `runissues -->\|"issues"\| call` (calls `gh.issues`), `main -->\|"issues"\| paged` (calls `gh.issues`) and `check -->\|"run"\| run` (`Queue.check` calls `subprocess.run`, not `Queue.run`). Correct edges to `file` and `issues` already exist (lines 343, 345, 349, 376). | `.github/bible/bible_queue.py:334,349,402,708,711,826`; `:489` (`Queue.run`) | Delete the five edges. |
| V-004 | `lld/bible-mode-b/README.md:191, 197` (Surprises; whole-system risks), rows 105, 106 | Wrong | minor | There is no `closed_revise` in the source. The revision list is `all_revise` (614), and it is used at 617. | `.github/bible/bible_queue.py:604-608,613-618`; `grep -n closed_revise` finds nothing | Delete the `closed_revise` bullet in both places. |
| V-005 | `lld/bible-mode-b/README.md:23` (Size), row 4 | Wrong | minor | 66 `def` lines and 2 classes (68 symbols, as the gate counts). The page says 67 functions/methods. | `.github/bible/bible_queue.py:88-848` (grep: 66 `def`, 2 `class`) | Write "66 functions/methods, 2 classes". |
| V-006 | `lld/bible-mode-b/README.md:151` (Outbound calls, GitHub API), row 66 | Overstated | minor | "HTTP and URL/timeout/OS errors become `RuntimeError`" holds for `GitHub.call` and `tarball`; `GitHub.ready` converts only `HTTPError`. | `.github/bible/bible_queue.py:105-117`, `:283-291` | Add "except `ready`, which wraps only HTTP errors". |
| V-007 | `lld/bible-mode-b/README.md:147-155` (Outbound calls) | Omission | minor | `Queue.check` also runs `coverage.py` and `status.py` from `BIBLE_SKILLS` with `subprocess.run` and `python -I`, no timeout. The table lists only the GitHub API and the `components` import. | `.github/bible/bible_queue.py:706-711` | Add a row for the toolkit scripts (subprocess, path from `BIBLE_SKILLS`). |
| V-008 | `lld/bible-mode-b/README.md` (front matter `source:`, line 20) | Omission | minor | `.github/workflows/poc-assign-copilot.yml` lies in the component's declared path `.github/workflows/` and is named nowhere in the pages. It checks out and runs no repository code. | `.github/workflows/poc-assign-copilot.yml:1-8`; `components.md` row for `bible-mode-b` | Name it and say it is independent of the queue, or say why it is out of scope. |
| V-009 | `lld/bible-mode-b/README.md:38-60` | Omission | minor | No sequence diagram for the `reconcile` flow (workflow, `Queue`, `GitHub`, GitHub API, the failure path in `fail_or_retry`) and no lifecycle diagram for the session states `waiting`, `running`, `finished`, `no-start`, `start-error`; the structure diagram lacks the subprocess edge. | `.github/bible/bible_queue.py:413-429,477-525` | Add the two diagrams and the edge. |
| V-010 | `lld/bible-mode-b/bible_queue.md:2213` (`now`) and the `Called by` of `GitHub.agent_events` (row 245) and `GitHub.assigned_at` (row 259) | Omission | minor | `now` is also called by `Queue.render` (763) and the card says "Queue functions in later source packets"; `agent_events` and `assigned_at` are also called by `Queue.session` (420, 419). | `.github/bible/bible_queue.py:419,420,763` | Add the missing callers. |
| V-011 | Citations of the Configuration table, `lld/bible-mode-b/README.md:160-172`, rows 70, 71, 80, 82, 84, 86, 89, 90, 91, 92 | Citation off | minor | The CLI option rows cite lines four earlier than the code: `--components` is 805 (cited 801), `--model` 806 (cited 802), `--verify-model` 807 (cited 803), `--concurrency` 808 (cited 804), `--analysis` 809 (cited 805 and 810), `--depth` 810 (cited 806). `GITHUB_REPOSITORY` and `GH_TOKEN` are read at 817 (cited 813-815). The `--depth` use is at 708 (cited 703-705). | `.github/bible/bible_queue.py:805-810,817,708` | Move the citations to the lines shown. |
| V-012 | Other citations: row 62 (`README.md:145`, blank lines discarded: code at 840-841, not 836-838), row 50 (`README.md:135`, the PASS and fingerprint condition is at 608, outside 609-614), row 102 (`README.md:182`, 755-765 is the done comment and `render`, not logging), row 336 (`bible_queue.md:1403`, the `run_issues` call lines 608, 624, 625, 718, 720 are not calls; they are 613, 614, 722, 724), row 644 (`bible_queue.md:2540`, 307-391 holds only the module helpers, not the client, `Queue` or `main`) | Citation off | minor | True statements; the cited lines do not show them. | `.github/bible/bible_queue.py:608,613,614,722,724,840-841` | Re-point each citation as shown. |
| V-013 | `lld/bible-mode-b/README.md` Surprises | Omission | minor | Not listed: the module docstring says `BIBLE_AGENT_LOGINS` defaults to `Copilot,copilot-swe-agent[bot]` while the code adds `copilot-swe-agent`; `GitHub.prs` is never called. | `.github/bible/bible_queue.py:36` vs `:60`; `:172` | Add both to Surprises. |
| V-014 | `lld/bible-mode-b/bible_queue.md:104-110` (call graph) | Inconsistent | minor | No sentence on how edges were derived and no evidence table; the edges rest on name matching, the cause of V-003. | module page lines 104-110 | Add a sentence on derivation and its limit. |
| V-015 | `lld/bible-mode-b/README.md:184-186` (Tests) | Inconsistent | minor | The paragraph states process ("checked through the `next.py` analysis workflow; no runtime tests were run for the documentation-only change") instead of a fact about the component. | grep of test-named paths finds no `bible_queue` | Keep only the search result. |

## Coverage findings

`coverage.py` result `PASS` at depth `deep`, component scope (my run, same figures as `verification-coverage.md`): files 1/1, symbols 68/68, full cards 66/66, routes 0/0, citations resolve 650/650, branch lines 161/161, call edges 163/163, front matter 2/2, cross-component calls 0/0.

- No gaps. Drift: `bible_queue.py` is 848 lines, the stored inventory says 844. The pages cite the 848-line file; I found the line numbers shifted by four in the Configuration table and in a few caller lists (V-011, V-012), which is consistent with the pages being written against both versions.
- `ledger/not-documented.md` does not exist, so no file is listed as skipped.
- Totals: `components.md` says 1 file, 844 lines; `wc -l` gives 848 (drift only). Symbols 66 + 2 = 68, equal to the gate. The README says 67 functions (V-005).
- The gate checks that an edge exists for every call and that each card has cited branch lines; it does not check that every edge is real (V-003) or that a card matches the current control flow (V-001).

## Depth findings

The component has one non-test file; the audit takes its largest cards. Read against the code in this session: five.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.component` (565-642) | Wrong | Describes a `follow` result test (`endswith("merged")`) the code does not have; the method returns the `follow` result directly (585). The rest of the card (PR scan, gate, holds, verification, revision rounds) matches 566-642 (V-001) |
| `.github/bible/bible_queue.py` | `Queue.follow` (644-696) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.check` (698-715) | Complete | none |
| `.github/bible/bible_queue.py` | `GitHub.tarball` (234-259) | Complete | none in the steps and branches; the `Called by` row is wrong (V-002) |
| `.github/bible/bible_queue.py` | `main` (801-844) | Complete | none |

Depth 4 / 5 = 80%; usable 80%. The audit is smaller than the standard (the three largest functions of the five largest files), and a `Wrong` among the largest cards suggests other large cards written against the pre-edit source should be re-read: the card hashes in the pages did not catch the change.

## Diagram findings

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README structure flowchart (`README.md:38-60`) | finding | ok | finding | ok | ok | ok | ok (read, not rendered) | Missing subprocess edge; no sequence or lifecycle diagram (V-007, V-009) |
| README class diagram (`README.md:80-110`) | ok | ok | ok | ok | ok | ok | ok (read, not rendered) | Fields and methods match the cited lines |
| Module call graph (`bible_queue.md`, from line 106) | ok | ok | ok | finding | finding | ok | ok (read, not rendered) | Five false edges (V-003); no derivation sentence (V-014) |

Searched for ways the code reaches outside itself: `urllib.request` (GitHub API, drawn), `subprocess` (V-007), `tempfile` (gate tree, in the Data table). No database, queue, mail or spreadsheet.

## Data dictionary and mind map findings

none for this scope. The component owns no store; its data are GitHub issues, labels, branches and pull requests. The data dictionary and mind map are left to the whole verification.

## Knowledge base findings

none for this scope; `knowledge/` does not exist yet. Both pages have front matter (gate 2 / 2).

## Readability and prose findings

- The README opens with a summary table, a responsibility paragraph and a diagram, in a sensible order; the module page opens with an index that links to each card.
- No claim numbers, no template text; one process sentence (V-015).
- Cited sentences I opened say no more than their citation, except V-006 and V-004.

## Ledger findings

Component scope: `progress.md` and `ledger/coverage-ledger.md` belong to planning, so a stale row there is not this component's finding. `components.md` and `components.json` give paths `.github/bible/` and `.github/workflows/`; the pages agree except for V-008. `status.json` says `COMPONENT_DONE`, 3 of 3 packets.

## Consistency findings

- Names agree across front matter, README and module page. Option defaults in the Configuration table match the code (`BIBLE_AGENT_LOGINS` 60, `BIBLE_AGENT_APP` 64, `BIBLE_NOW` 307-309).
- README's 67 functions disagrees with 66 cards (V-005); the module page's own `Called by` rows disagree with the call graph's correct edges (V-002).
- No secret value appears in the pages (checked by location and kind: the only token mentions are the names `GH_TOKEN` and `BIBLE_ASSIGN_TOKEN`).

## Limits

- All 195 selected rows were judged, but for each I compared the claim with the first lines of the cited range plus the surrounding code where the claim sat further down; long ranges (for example `README.md` rows 52-57) were checked for the right function, not line by line.
- The coverage script matches names, not meaning (V-001 to V-003 passed it). The depth audit covers five cards of 66.
- Verification shows the pages match the code, not that the code matches what runs in production. Nothing was run except `coverage.py` and `status.py --fingerprint`.
- Diagrams were read, not rendered.
- The call graph is built by name matching; edges between same-named methods (`issues`, `file`, `close`, `run`) are where it is wrong. Open the call line before relying on an edge.
- The author's model is not stated; a person or another model should re-check the three `major` corrections and a few confirmed statements.
- Earlier reports for this component existed before I started (`verification-report-2026-11-23*.md`); I read them after forming my own judgments.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 4 | group A | Wrong | V-005 |
| 50, 62, 70, 71, 80, 82, 84, 86, 89, 90, 91, 92, 102, 336, 644 | groups A, D | Citation off | V-011, V-012 |
| 66 | group A | Overstated | V-006 |
| 105, 106 | group A | Wrong | V-004 |
| 245, 259 | group D | Confirmed | statements true; lists incomplete (V-010) |

Confirmed by me: every other row of the 195 (group A rows 1-3, 5-49, 51-61, 63-65, 67-69, 72-79, 81, 83, 85, 87, 88, 93-101, 103, 104, 107-118; group B row 128; the 76 group D rows except 336 and 644).

Outside the sample, by search and reading: the 25 `No call site` rows and the five false edges (V-002, V-003); the `Queue.component` card against 565-642 (V-001); `closed_revise` (V-004); the 66/2 symbol count; the `BIBLE_AGENT_LOGINS` default; the workflow list; the README's absence of `subprocess` and of a sequence diagram; the five audited cards.
