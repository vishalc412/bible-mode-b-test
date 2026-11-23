# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Scope | component bible-mode-b |
| Analysis fingerprint | e5dc7e620c582f3a |
| Analysis snapshot | component row in `components.md`: 1 source file, 844 lines (2026-11-23); no version given |
| Repository at verification | 1 source file (`.github/bible/bible_queue.py`), 844 lines, plus 4 workflow files in `.github/workflows/`; coverage drift: none (2026-11-23) |
| Depth stated / depth found | deep / deep (front matter, full cards with cited branch lines, call graph) |
| Verified with | GitHub Copilot coding agent (model not stated) |
| Analysis produced with | not stated |
| Sampling level | standard |
| Date | 2026-11-23 |

## Summary

The component's two pages (`lld/bible-mode-b/README.md`, `lld/bible-mode-b/bible_queue.md`) are complete and nearly always accurate. The coverage gate passes on every measure (648 of 648 citations resolve; 66 of 66 cards; 160 of 160 branch lines).

The standard-level sample is 195 citation rows. In this round I opened and judged 34 of them (all of group B, a spread of group A and of group D, and the rows behind each correction): 32 confirmed, 1 overstated, 1 wrong. The other 161 rows were not re-opened in this round; their results below come from the earlier rounds' reports (`verification-report-2026-11-23.md`, `verification-report-2026-11-23-2.md`) and are marked as carried, not judged by me. The pages are unchanged since those rounds (same fingerprint).

The weak spot is the generated part of the module page, which the gate cannot see:

- 26 of 27 `No call site is in this source range` rows are wrong. `Queue` and `main` call the `GitHub.*` methods through `self.gh.<name>` and `gh.<name>` (for example `GitHub.tarball` at `.github/bible/bible_queue.py:702`, `GitHub.merge` at `:689`, `GitHub.create_issue` at `:472,536,562,616,635,748,785,830`). A reader asking what depends on them is told "nothing" (V-003).
- The call graph has five edges the code does not contain, among them `check -->|"run"| run`: `Queue.check` calls `subprocess.run`, not `Queue.run` (V-004).

The verdict is `PASS AFTER CORRECTIONS`, not `PASS`: two `major` corrections stand, and a `Wrong` statement (V-004) stands behind diagram elements. Coverage is 100%, accuracy on my own sample is 94.1% (above the 85% floor, below the 95% `PASS` bar), and depth is 100%. Every problem has a specific correction. The author's model is not stated; a person or another model should re-check the two `major` corrections.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 1 / 1 (100.0%) |
| Symbols accounted for | 68 / 68 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 66 / 66 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 160 / 160, 163 / 163, 2 / 2 (all 100.0%) |
| Routes with an endpoint card | 0 / 0 (100.0%) |
| Citations that resolve | 648 / 648 (100.0%) |
| Coverage gate | PASS |
| Citations in the analysis / selected / judged by me | 648 / 195 / 34 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported (my 34) | 32 / 0 / 1 / 1 / 0 |
| Omissions (significant) / Inconsistent | 0 (5 minor) / 3 (V-003, V-004 major; V-009, V-010 minor, see Corrections) |
| Accuracy / citation quality | 94.1% (32 / 34) / 94.1% (32 / 34) |
| Cards audited: Complete / Partial / Shallow / Wrong | 8 / 0 / 0 / 0 |
| Depth / depth, usable | 100% / 100% |

Accuracy = (Confirmed + Citation off) / checked. The earlier rounds' sample of all 195 rows gave 193 confirmed (99.0%); the lower figure here is a small sample that includes both known bad rows (4 and 66), so it is not a better estimate of the whole.

## How the sample was selected

Gate run: `coverage.py --depth deep --component bible-mode-b --report ledger/components/bible-mode-b/verification-coverage.md`; it wrote the component's `citations.tsv` (648 rows). Standard level:

- Group A (README.md): all 118 rows, indexes 1-118. Judged by me: rows 4, 6, 18, 24, 30, 36, 42, 48, 54, 60, 66, 78, 84, 90, 96, 102, 108, 114.
- Group B (`inferred`/`assumed`): row 128. Judged by me.
- Group C (rule, outbound, security, auth headings): all fall on the README, so in group A.
- Group D (module page rows whose index is divisible by 7): 119, 126, ... 644 (76 rows). Judged by me: 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630 (those also divisible by 5), so the rows are spread evenly across the page.
- Group E (calls into another component): none.

## Earlier corrections re-confirmed

none (this is not a re-check after a revision). The pages carry the same fingerprint as the earlier rounds, so none of the earlier corrections has been applied; I re-derived each one below from the code.

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/bible-mode-b/README.md:23` (Size), row 4 | Wrong | minor | 66 `def` lines and 2 `class` lines (68 symbols, the figure the gate uses). The page says 67 functions/methods. | `.github/bible/bible_queue.py:88-844` (my count: `grep -c "def "` 66, `class` 2) | Write "66 functions/methods, 2 classes". |
| V-002 | `lld/bible-mode-b/README.md:151` (Outbound calls, GitHub API), row 66 | Overstated | minor | "URL/timeout/OS errors become `RuntimeError`" holds for `GitHub.call` and `GitHub.tarball`. `GitHub.ready` converts only `HTTPError`. | `.github/bible/bible_queue.py:283-291` | Add "except in `ready`, which wraps only HTTP errors". |
| V-003 | `lld/bible-mode-b/bible_queue.md`, the `Called by` row of 26 `GitHub.*` cards (27 rows say "No call site is in this source range"; only `GitHub.prs` is truly uncalled) | Inconsistent | major | Callers exist through `self.gh.` and `gh.`; examples I opened: `tarball` (`Queue.check`, line 702), `merge` (`Queue.follow`, 689), `create_issue` (472, 536, 562, 616, 635, 748, 785, 830), `issues` (402, 479, 782, 826), `assigned_at` (419), `agent_events` (420). No citation backs the claim and the gate does not check it. | `.github/bible/bible_queue.py:402,419,420,472,689,702,826` | Fill each row with its callers and lines; keep "No call site" only for `GitHub.prs` and say it is unused. |
| V-004 | `lld/bible-mode-b/bible_queue.md:193,194,197,256,280` (call graph) | Wrong | major | Five edges are not in the code: `issuetext -->\|"file"\| call`, `jsonfile -->\|"file"\| call` (both call `GitHub.file`, which has its own edges at 343 and 345), `runissues -->\|"issues"\| call` (calls `GitHub.issues`, edge at 376), `main -->\|"issues"\| paged` (main calls `gh.issues`, edge at 349) and `check -->\|"run"\| run` (`Queue.check` calls `subprocess.run`). | `.github/bible/bible_queue.py:334,349,402,702,826` | Delete the five edges; the correct edges already exist for the first four, `check` needs none. |
| V-005 | `lld/bible-mode-b/bible_queue.md:908` (`GitHub.agent_events`), `:994` (`GitHub.assigned_at`), `:2043` (`Queue.render`); rows 245 and 259, 546 | Omission | minor | Each `Called by` list is true but incomplete: `Queue.session` also calls `agent_events` (420) and `assigned_at` (419); `Queue.plan_phase` also calls `render` (548). | `.github/bible/bible_queue.py:419,420,548` | Add the missing callers. |
| V-006 | `lld/bible-mode-b/README.md:20` (Folders and files) and `source:` front matter | Omission | minor | `.github/workflows/poc-assign-copilot.yml` lies in the component's declared path `.github/workflows/`; neither page mentions it. It runs no repository code and does not call `bible_queue.py`. | `.github/workflows/poc-assign-copilot.yml:1-13`; grep of both pages finds no mention | Name it and say it is independent of the queue, or say why it is out of scope. |
| V-007 | `lld/bible-mode-b/README.md:147-155` (Outbound calls) | Omission | minor | `Queue.check` also runs `coverage.py` and `status.py` from `BIBLE_SKILLS` through `subprocess.run` with `python -I`, no timeout. The table lists only the GitHub API and the in-process `components` import. | `.github/bible/bible_queue.py:701-709` | Add a row for the toolkit scripts (subprocess, path from `BIBLE_SKILLS`). |
| V-008 | `lld/bible-mode-b/README.md:38-60` | Omission | minor | No sequence diagram for the `reconcile` flow (workflow, `Queue`, `GitHub`, GitHub API, with the `fail_or_retry` failure path), no lifecycle diagram for the session states `waiting`, `running`, `finished`, `no-start`, `start-error`; the structure diagram lacks the toolkit import and subprocess edges. | `.github/bible/bible_queue.py:413-429,477-525,775-781` | Add the two diagrams and the two edges. |
| V-009 | `lld/bible-mode-b/bible_queue.md:106-400` (call graph) | Inconsistent | minor | No intro sentence and no evidence table: the edges rest on the cards' `Calls` rows only, so a reader cannot tell the edges come from name matching (the cause of V-004). | module page lines 104-106 | Add a sentence on how edges were derived and the limit of name matching. |
| V-010 | `lld/bible-mode-b/README.md:184-186` (Tests) | Inconsistent | minor | The paragraph states process ("checked through the `next.py` analysis workflow...") rather than a fact about the component. The search result it states (no test file mentions `bible_queue`) is right. | grep of `*test*` paths | Keep only the search result. |
| V-011 | `lld/bible-mode-b/README.md` Surprises | Omission | minor | Not listed: the module docstring says `BIBLE_AGENT_LOGINS` defaults to "Copilot,copilot-swe-agent[bot]" while the code's default has a third entry `copilot-swe-agent`; `GitHub.prs` is never called. | `.github/bible/bible_queue.py:36,60`; `:172-174` | Add both to Surprises. |

## Coverage findings

`coverage.py` result `PASS` at depth `deep`, component scope:

| Measure | Done | Total | Share |
| --- | --- | --- | --- |
| Source files with a page | 1 | 1 | 100.0% |
| Symbols accounted for | 68 | 68 | 100.0% |
| Functions with a full card | 66 | 66 | 100.0% |
| Routes with an endpoint card | 0 | 0 | 100.0% |
| Citations that resolve | 648 | 648 | 100.0% |
| Branch lines cited in their card | 160 | 160 | 100.0% |
| Same-file calls drawn in call graphs | 163 | 163 | 100.0% |
| LLD pages with knowledge-graph front matter | 2 | 2 | 100.0% |
| Calls into other components cited on the calling card | 0 | 0 | 100.0% |

- No gaps, no drift. `ledger/not-documented.md` does not exist, so no file is listed as skipped.
- Totals: `components.md` says 1 file, 844 lines; `wc -l` gives 844. Symbols: 66 + 2 = 68, equal to the gate. The README's 67 disagrees (V-001).
- The gate checks that an edge exists for every call, not that every edge is real (V-004).

## Depth findings

The component has one non-test file; I audited the cards below against the code, as the earlier rounds did. In this round I re-opened the code for `Queue.check` (694-711), `GitHub.ready`, `GitHub.merge` area and `main`'s settings and issue creation (797-840); the other scores are carried from the earlier rounds (same pages, same code).

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.component` (565-643) | Complete (carried) | The `needs a person ... closed without merging` return (575-576) is in the steps, not in the branch table. |
| `.github/bible/bible_queue.py` | `Queue.follow` (645-692) | Complete (carried) | none |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` (713-753) | Complete (carried) | none |
| `.github/bible/bible_queue.py` | `Queue.run` (489-525) | Complete (carried) | none |
| `.github/bible/bible_queue.py` | `Queue.session` (413-429) | Complete (carried) | none |
| `.github/bible/bible_queue.py` | `GitHub.tarball` (234-259) | Complete (carried) | A malformed archive raises `tarfile.ReadError`, not caught and not listed; minor. |
| `.github/bible/bible_queue.py` | `Queue.delta` (768-794) | Complete (carried) | none |
| `.github/bible/bible_queue.py` | `main` (797-840) | Complete | none (re-checked: settings dict, tracker creation at 828-832) |

Depth 8 / 8 = 100%; usable 100%. The `Called by` rows are not part of the card score (V-003, V-005).

## Diagram findings

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README structure flowchart (`README.md:38-60`) | finding | ok | finding | ok | ok | ok | ok (read, not rendered) | Missing toolkit-import and subprocess edges; no sequence or lifecycle diagram (V-007, V-008). |
| README class diagram (`README.md:80-110`) | ok | ok | ok | ok | ok | ok | ok (read, not rendered) | Fields and methods match the cited lines (rows 24, 30, 36 confirmed). |
| Module call graph (`bible_queue.md:106-400`) | ok | ok | ok | finding | finding | ok | ok (read, not rendered) | Five false edges (V-004); no evidence rows (V-009). |

Searched for ways the code reaches outside itself: `urllib.request` (GitHub API, drawn), `subprocess` (V-007), `tempfile` (gate tree, in the Data table). No database, queue, mail or spreadsheet.

## Data dictionary and mind map findings

none for this scope. The component owns no store; its data are GitHub issues, labels, branches and pull requests. The data dictionary and mind map are left to the whole verification.

## Knowledge base findings

none for this scope; `knowledge/` does not exist yet. Both pages have front matter (gate 2 / 2).

## Readability and prose findings

- The README opens with a summary table, a responsibility paragraph and a diagram, in a sensible order; the module page opens with an index that links to each card.
- No claim numbers, no template text; one process sentence (V-010).
- Cited sentences I opened on the README say no more than their citation, except V-001 and V-002.

## Ledger findings

Component scope: `progress.md` and `ledger/coverage-ledger.md` belong to planning, so a stale row there is not this component's finding. `components.md` and `components.json` give paths `.github/bible/` and `.github/workflows/`; they agree with the pages except for V-006. `status.json` says `COMPONENT_DONE`, 4 of 4 packets.

## Consistency findings

- Names agree across front matter, README and module page. Option defaults in the Configuration table match the code (rows 84 and 90 confirmed).
- README's 67 functions disagrees with 66 cards (V-001).
- No secret value appears in the pages (checked by location and kind; none found).

## Limits

- A sample was checked, not every row: of the 195 selected rows I judged 34 myself in this round; the others are carried from earlier rounds on identical pages.
- The coverage script matches names, not meaning (V-003 and V-004 passed it). The depth audit covers eight cards of 66, and five of those scores are carried.
- Verification shows the pages match the code, not that the code matches what runs in production. Nothing was run.
- Diagrams were read, not rendered.
- The call graph is built by name matching; edges between same-named methods (`issues`, `file`, `close`, `run`) are where it is wrong. Open the call line before relying on an edge.
- The author's model is not stated; a person or another model should re-check the two `major` corrections and a few confirmed statements.
- Earlier reports for this component existed before I started; I re-derived the findings from the code but did read them.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 4 | group A | Wrong | V-001 |
| 66 | group A | Overstated | V-002 |
| 245 | group D | Confirmed | statement true; list incomplete (V-005) |

Confirmed by me: group A rows 6, 18, 24, 30, 36, 42, 48, 54, 60, 78, 84, 90, 96, 102, 108, 114; group B row 128 (no annotations or factory in lines 88-92); group D rows 140, 175, 210, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630. Carried, not re-opened: the remaining selected rows (A 1-118, D 119-644 divisible by 7), with rows 259 and 546 true but incomplete (V-005).

Outside the sample, by search: the 27 `No call site` rows and the five false edges (V-003, V-004); the `Queue.check` subprocess calls; the 66/2 symbol count; the AGENT_LOGINS default; the workflow list.
