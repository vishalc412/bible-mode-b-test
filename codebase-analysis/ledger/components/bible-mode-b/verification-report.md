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

The component's two pages (`lld/bible-mode-b/README.md`, `lld/bible-mode-b/bible_queue.md`) are complete and nearly always accurate. The coverage gate, which I re-ran, passes on every measure (648 of 648 citations resolve; 66 of 66 cards; 160 of 160 branch lines; 163 of 163 call edges).

The standard-level sample is 195 citation rows. I opened and judged 28 of them myself in this session: 26 confirmed, 1 overstated, 1 wrong. The other rows were not re-opened here. An earlier verification round (`verification-report-2026-11-23-3.md`, the previous `verification-report.md`) judged other rows on the same pages (same fingerprint); I read it after judging, and its findings below are the ones I re-derived from the code.

The weak spot is the generated part of the module page, which the gate cannot see:

- 26 of the 27 `No call site is in this source range` rows are wrong. `Queue` and `main` call the `GitHub.*` methods through `self.gh.<name>` and `gh.<name>` (for example `GitHub.tarball` at `.github/bible/bible_queue.py:702`, `GitHub.merge` at `:689`, `GitHub.create_issue` at `:828`). A reader asking what depends on them is told "nothing" (V-003).
- The call graph has five edges the code does not contain, among them `check -->|"run"| run`: `Queue.check` calls `subprocess.run`, not `Queue.run` (V-004).

The verdict is `PASS AFTER CORRECTIONS`, not `PASS`: two `major` corrections stand, a `Wrong` statement (V-004) stands behind diagram elements, and accuracy on my sample (92.9%) is below the 95% `PASS` bar (above the 85% floor). Coverage is 100% and depth, usable, is 100%. Every problem has a specific correction. The author's model is not stated; a person or another model should re-check the two `major` corrections.

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
| Citations in the analysis / selected / judged by me | 648 / 195 / 28 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported (my 28) | 26 / 0 / 1 / 1 / 0 |
| Omissions (significant) / Inconsistent | 0 (5 minor) / 4 (V-003, V-004 major; V-009, V-010 minor) |
| Accuracy / citation quality | 92.9% (26 / 28) / 92.9% (26 / 28) |
| Cards audited: Complete / Partial / Shallow / Wrong | 5 / 0 / 0 / 0 |
| Depth / depth, usable | 100% / 100% |

The small sample includes the two known bad rows (4 and 66), so 92.9% is not a better estimate of the whole than the earlier round's 99.0% over all 195 rows.

## How the sample was selected

Gate run by me: `coverage.py --repo . --analysis codebase-analysis --depth deep --component bible-mode-b --report ledger/components/bible-mode-b/verification-coverage.md`; it wrote the component's `citations.tsv` (648 rows). Standard level:

- Group A (README.md): all 118 rows, indexes 1-118. Judged by me: 4, 6, 12, 18, 30, 42, 54, 60, 66, 78, 96, 102, 108, 114.
- Group B (`inferred`/`assumed`, outside the README): row 128. Judged by me.
- Group C (rule, outbound, security, auth headings): all fall on the README, so in group A.
- Group D (module page rows whose index is divisible by 7): 119, 126, ... 644. Judged by me: 119, 147, 203, 259, 301, 343, 420, 462, 511, 553, 595, 630, 644 (spread over the page).
- Group E (calls into another component): none.

## Earlier corrections re-confirmed

none (this is not a re-check after a revision; the fingerprint equals the earlier round's, so none of its corrections has been applied). I re-derived each correction below from the code.

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/bible-mode-b/README.md:23` (Size), row 4 | Wrong | minor | 66 `def` lines and 2 classes (68 symbols, as the gate counts). The page says 67 functions/methods. | `.github/bible/bible_queue.py:88-844` (grep: 66 `def`, 2 `class`) | Write "66 functions/methods, 2 classes". |
| V-002 | `lld/bible-mode-b/README.md:151` (Outbound calls, GitHub API), row 66 | Overstated | minor | "URL/timeout/OS errors become `RuntimeError`" holds for `GitHub.call`; `GitHub.ready` converts only `HTTPError`. | `.github/bible/bible_queue.py:105-117`, `:283-291` | Add "except in `ready`, which wraps only HTTP errors". |
| V-003 | `lld/bible-mode-b/bible_queue.md`, the `Called by` row of 26 `GitHub.*` cards (27 rows say "No call site is in this source range"; only `GitHub.prs` is uncalled) | Inconsistent | major | Callers exist through `self.gh.` and `gh.`: `tarball` (`Queue.check`, 702), `merge` (`Queue.follow`, 689), `create_issue` (e.g. 828), `file` (334, 349, 609, 686), `issues` (402). No citation backs the claim and the gate does not check it. | `.github/bible/bible_queue.py:334,349,402,689,702,828`; `grep -n "def prs\|\.prs("` finds only the definition (172) | Fill each row with its callers and lines; keep "No call site" only for `GitHub.prs` and say it is unused. |
| V-004 | `lld/bible-mode-b/bible_queue.md:193,194,197,256,280` (call graph) | Wrong | major | Five edges are not in the code: `issuetext -->\|"file"\| call` and `jsonfile -->\|"file"\| call` (both call `GitHub.file`, `gh.file` at 334 and 349), `runissues -->\|"issues"\| call` (calls `GitHub.issues`, 402), `main -->\|"issues"\| paged` (main calls `gh.issues`, 826) and `check -->\|"run"\| run` (`Queue.check` calls `subprocess.run`, 703, 707). | `.github/bible/bible_queue.py:334,349,402,703,707,826` | Delete the five edges; the correct edges exist for the first four, `check` needs none. |
| V-005 | `lld/bible-mode-b/bible_queue.md:908` (`GitHub.agent_events`), `:994` (`GitHub.assigned_at`, row 259), `:2043` (`Queue.render`) | Omission | minor | Each `Called by` list is true but incomplete: `Queue.session` also calls `assigned_at` (419) and `agent_events` (420); `Queue.plan_phase` also calls `render` (548). | `.github/bible/bible_queue.py:419,420,548` | Add the missing callers. |
| V-006 | `lld/bible-mode-b/README.md:20` and `source:` front matter | Omission | minor | `.github/workflows/poc-assign-copilot.yml` lies in the component's declared path `.github/workflows/`; neither page mentions it. It checks out and runs no repository code. | `.github/workflows/poc-assign-copilot.yml:1-8` | Name it and say it is independent of the queue, or say why it is out of scope. |
| V-007 | `lld/bible-mode-b/README.md:147-155` (Outbound calls) | Omission | minor | `Queue.check` also runs `coverage.py` and `status.py` from `BIBLE_SKILLS` with `subprocess.run` and `python -I`, no timeout. The table lists only the GitHub API and the `components` import. | `.github/bible/bible_queue.py:703-709` | Add a row for the toolkit scripts (subprocess, path from `BIBLE_SKILLS`). |
| V-008 | `lld/bible-mode-b/README.md:38-60` | Omission | minor | No sequence diagram for the `reconcile` flow (workflow, `Queue`, `GitHub`, GitHub API, `fail_or_retry` failure path) and no lifecycle diagram for session states `waiting`, `running`, `finished`, `no-start`, `start-error`; the structure diagram lacks the subprocess edge. | `.github/bible/bible_queue.py:413-429,477-525` | Add the two diagrams and the edge. |
| V-009 | `lld/bible-mode-b/bible_queue.md:104-110` (call graph) | Inconsistent | minor | No sentence on how edges were derived and no evidence table; edges rest on name matching, the cause of V-004. | module page lines 104-110 | Add a sentence on derivation and its limit. |
| V-010 | `lld/bible-mode-b/README.md:184-186` (Tests) | Inconsistent | minor | The paragraph states workflow process ("checked through the `next.py` analysis workflow; no runtime tests were run") rather than a fact about the component. | grep of `*test*` paths finds no mention of `bible_queue` | Keep only the search result. |
| V-011 | `lld/bible-mode-b/README.md` Surprises | Omission | minor | Not listed: the module docstring says `BIBLE_AGENT_LOGINS` defaults to `Copilot,copilot-swe-agent[bot]`, the code's default adds `copilot-swe-agent`; `GitHub.prs` is never called. | `.github/bible/bible_queue.py:36` vs `:60`; `:172` | Add both to Surprises. |

## Coverage findings

`coverage.py` result `PASS` at depth `deep`, component scope (my run, same figures as `verification-coverage.md`): files 1/1, symbols 68/68, full cards 66/66, routes 0/0, citations resolve 648/648, branch lines 160/160, call edges 163/163, front matter 2/2, cross-component calls 0/0.

- No gaps, no drift. `ledger/not-documented.md` does not exist, so no file is listed as skipped.
- Totals: `components.md` says 1 file, 844 lines; `wc -l` gives 844. Symbols 66 + 2 = 68, equal to the gate. The README's 67 disagrees (V-001).
- The gate checks that an edge exists for every call, not that every edge is real (V-004).

## Depth findings

The component has one non-test file, so I audited cards of the file. Cards read against the code in this session: five.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.check` (694-711) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.session` (413-429) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.follow` (645-692), branches at 659-692 | Complete | none |
| `.github/bible/bible_queue.py` | `GitHub.call` (105-117) | Complete | none |
| `.github/bible/bible_queue.py` | `main` (797-840) | Complete | none (validation, settings dict, tracker creation at 819-832 match) |

Depth 5 / 5 = 100%; usable 100%. The `Called by` rows are not part of the card score (V-003, V-005). The audit is smaller than the standard (the three largest functions of the five largest files; a one-file component), so the depth figure is weak evidence.

## Diagram findings

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README structure flowchart (`README.md:38-60`) | finding | ok | finding | ok | ok | ok | ok (read, not rendered) | Missing subprocess edge; no sequence or lifecycle diagram (V-007, V-008). |
| README class diagram (`README.md:80-110`) | ok | ok | ok | ok | ok | ok | ok (read, not rendered) | Fields and methods match the cited lines. |
| Module call graph (`bible_queue.md`, from line 106) | ok | ok | ok | finding | finding | ok | ok (read, not rendered) | Five false edges (V-004); no evidence rows (V-009). |

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

Component scope: `progress.md` and `ledger/coverage-ledger.md` belong to planning, so a stale row there is not this component's finding. `components.md` and `components.json` give paths `.github/bible/` and `.github/workflows/`; the pages agree except for V-006. `status.json` says `COMPONENT_DONE`, 4 of 4 packets.

## Consistency findings

- Names agree across front matter, README and module page. Option defaults in the Configuration table match the code (`BIBLE_AGENT_LOGINS` at line 60, `BIBLE_NOW` at 307-309).
- README's 67 functions disagrees with 66 cards (V-001).
- No secret value appears in the pages (checked by location and kind).

## Limits

- A sample was checked, not every row: of the 195 selected rows I judged 28 myself; the rest were not re-opened here.
- The coverage script matches names, not meaning (V-003 and V-004 passed it). The depth audit covers five cards of 66.
- Verification shows the pages match the code, not that the code matches what runs in production. Nothing was run.
- Diagrams were read, not rendered.
- The call graph is built by name matching; edges between same-named methods (`issues`, `file`, `close`, `run`) are where it is wrong. Open the call line before relying on an edge.
- The author's model is not stated; a person or another model should re-check the two `major` corrections and a few confirmed statements.
- An earlier report for this component existed before I started and I read it after forming my own judgments.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 4 | group A | Wrong | V-001 |
| 66 | group A | Overstated | V-002 |
| 259 | group D | Confirmed | statement true; list incomplete (V-005) |

Confirmed by me: group A rows 6, 12, 18, 30, 42, 54, 60, 78, 96, 102, 108, 114; group B row 128; group D rows 119, 147, 203, 301, 343, 420, 462, 511, 553, 595, 630, 644. Not re-opened: the other selected rows.

Outside the sample, by search: the 27 `No call site` rows and the five false edges (V-003, V-004); the `Queue.check` subprocess calls; the 66/2 symbol count; the `BIBLE_AGENT_LOGINS` default; the workflow list.
