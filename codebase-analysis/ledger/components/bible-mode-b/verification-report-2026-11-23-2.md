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

The component's two pages (`lld/bible-mode-b/README.md`, `lld/bible-mode-b/bible_queue.md`) are complete and almost always accurate. The coverage gate passes on every measure. Of 195 sampled citation rows, 193 were confirmed, 1 was wrong (a function count) and 1 was overstated (the error handling of one method). All 8 cards I audited in full were `Complete`. Nothing in the pages was a secret, and the component calls no other catalog component.

The weak spot is the generated part of the module page, which the gate cannot see:

- 26 of the 27 `GitHub.*` cards say `Called by: No call site is in this source range`. `Queue` and `main` call them through `self.gh.<method>` and `gh.<method>`. A reader asking what depends on `GitHub.tarball`, `GitHub.merge` or `GitHub.create_issue` would be told "nothing" (V-003).
- The call graph has five edges the code does not contain, among them `check -->|"run"| run`: `Queue.check` calls `subprocess.run`, not `Queue.run` (V-004).

The verdict is `PASS AFTER CORRECTIONS`, not `PASS`: there are two `major` corrections, and a `Wrong` statement stands behind diagram elements (the verdict table forbids that for `PASS`). Coverage, accuracy (99.0%) and depth (100% of 8 cards) are above the thresholds, and every problem has a specific correction. A sample was checked, not every row. The diagrams were read, not rendered. I saw the summary of an earlier round's report (`verification-report-2026-11-23.md`) before judging; every finding below was re-derived from the code, not copied from it. The author's model is not stated, so a person or another model should re-check the two `major` corrections and a few confirmed statements.

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
| Citations in the analysis / checked | 648 / 195 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 193 / 0 / 1 / 1 / 0 |
| Omissions (significant) / Inconsistent | 0 (4 minor) / 3 (2 major or covered by a major row, see V-003 to V-005) |
| Accuracy / citation quality | 99.0% (194 / 195) / 99.0% (193 / 195)* |
| Cards audited: Complete / Partial / Shallow / Wrong | 8 / 0 / 0 / 0 |
| Depth / depth, usable | 100% / 100% |

\* Accuracy = (Confirmed + Citation off) / checked = 193 / 195 = 99.0%; the Overstated row counts against both figures. Citation quality = Confirmed / checked = 193 / 195 = 99.0%.

## How the sample was selected

Component scope: the gate was run as `coverage.py --depth deep --component bible-mode-b --report ledger/components/bible-mode-b/verification-coverage.md`; it wrote the component's `citations.tsv` (648 rows). Standard level:

- Group A (the component's `README.md`): all 118 rows, indexes 1-118.
- Group B (`inferred` or `assumed` labels): row 128 (module page line 410). The `(inferred` sentences on the README are rows in group A.
- Group C (rule, outbound, security, auth sections): all rows fall on the README and are in group A; none were left in the module page.
- Group D (all other rows, in `bible_queue.md`): the 76 rows whose index is divisible by 7: 119, 126, 133, ... 644.
- Group E (calls from this component into another component): none (coverage report group E empty). The one cross-package call, `Queue.delta` importing the toolkit's `components` helpers, was opened anyway (`.github/bible/bible_queue.py:775-781`, `.github/skills/analyzing-a-codebase/scripts/components.py:151,232,236`): the card describes it correctly, including that `assign` returns a tuple whose first element is used.

Total 118 + 1 + 76 = 195 rows. Statements checked outside the sample are listed at the end.

## Earlier corrections re-confirmed

none (this report is not a re-check after a revision). A report from an earlier round was kept as `verification-report-2026-11-23.md`.

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/bible-mode-b/README.md:23` (Size), row 4 | Wrong | minor | The file has 66 `def` lines (functions and methods) and 2 classes: 68 symbols, which is the figure the gate and the module page use. The page says 67 functions/methods. | `.github/bible/bible_queue.py:88-844` (66 `def`, 2 `class`) | Write "66 functions/methods, 2 classes". |
| V-002 | `lld/bible-mode-b/README.md:151` (Outbound calls, GitHub API row), row 66 | Overstated | minor | "HTTP and URL/timeout/OS errors become `RuntimeError`" holds for `GitHub.call` and `GitHub.tarball`. `GitHub.ready` converts only `HTTPError`; a `URLError`, timeout or `OSError` from the GraphQL call propagates unchanged. | `.github/bible/bible_queue.py:287-291` | Add "except in `ready`, which wraps only HTTP errors". |
| V-003 | `lld/bible-mode-b/bible_queue.md` lines 419, 561, 616, 644, 677, 698, 727, 748, 769, 851, 885, 931, 960, 1023, 1056, 1077, 1120, 1143, 1164, 1185, 1206, 1227, 1248, 1303, 1332, 1353 (`Called by` rows of 26 `GitHub.*` cards) | Inconsistent | major | Each says "No call site is in this source range". All but `GitHub.prs` (line 800, correctly uncalled) have callers through `self.gh.` or `gh.`: `__init__` (`main`), `issues` (`Queue.run_issues`, `reconcile`, `delta`, `main`), `ensure_labels` (`main`), `create_issue` (`fail_or_retry`, `plan_phase`, `start_chunk`, `component`, `assemble_phase`, `main`), `default_branch`, `branch_sha`, `create_branch`, `reset_branch`, `file`, `linked_prs`, `branch_prs`, `is_agent_pr`, `start_error`, `pr_files`, `commit_time`, `tarball`, `label`, `unlabel`, `comment`, `close`, `set_body`, `unassign`, `assign`, `merge`, `close_pr`, `create_pr`. The cards carry no citation for the claim, and the gate does not check it. | `.github/bible/bible_queue.py:402,406,417,423,440,450,460,468,472,478,554-558,568,609,611,662,689-691,702,723,816,825` and others (all found by searching `gh\.<name>\(` and `self\.gh\.<name>\(`) | Fill each `Called by` row with its `Queue`/`main`/helper callers and lines; keep "No call site" only for `GitHub.prs`, and say it is unused. |
| V-004 | `lld/bible-mode-b/bible_queue.md:193,194,197,256,280` (call graph) | Wrong | major | Five edges are not in the code: `issuetext -->\|"file"\| call` and `jsonfile -->\|"file"\| call` (both call `GitHub.file`, which has its own edges at lines 342 and 344 in the same block); `runissues -->\|"issues"\| call` (calls `GitHub.issues`); `main -->\|"issues"\| paged` (calls `GitHub.issues`); `check -->\|"run"\| run` (`Queue.check` calls `subprocess.run`, not `Queue.run`). | `.github/bible/bible_queue.py:334,349,402,826,702-705` | Delete the five edges. For the first four the correct edge already exists; `check` needs none. |
| V-005 | `lld/bible-mode-b/bible_queue.md:908` (`GitHub.agent_events`), `:994` (`GitHub.assigned_at`), `:2043` (`Queue.render`), rows 245, 259, 546 | Omission | minor | Each `Called by` list is true but incomplete: `Queue.session` also calls `agent_events` (line 420) and `assigned_at` (line 418); `Queue.plan_phase` also calls `render` at line 548. Same cause as V-003. | `.github/bible/bible_queue.py:418,420,548` | Add the missing callers. |
| V-006 | `lld/bible-mode-b/README.md:20` (Folders and files) and `source:` front matter | Omission | minor | `.github/workflows/poc-assign-copilot.yml` (72 lines) lies in the component's declared path `.github/workflows/` and is neither listed nor declared out of scope. `progress.md:29` names it among the component's start points. It does not call `bible_queue.py`. | `.github/workflows/poc-assign-copilot.yml:8-13`; `codebase-analysis/progress.md:29` | Name it and say it is independent of the queue, or say why it is excluded. |
| V-007 | `lld/bible-mode-b/README.md:147-155` (Outbound calls) | Omission | minor | `Queue.check` also runs two external programs, `coverage.py` and `status.py` from `BIBLE_SKILLS`, with `subprocess.run` and the current interpreter. The page lists only the GitHub API and the in-process `components` import. The card for `Queue.check` does describe it. | `.github/bible/bible_queue.py:701-709` | Add a row "toolkit scripts, subprocess (`python -I`), path from `BIBLE_SKILLS`, no timeout". |
| V-008 | `lld/bible-mode-b/README.md:38-60` and the component's pages | Omission | minor | No sequence diagram for the `reconcile` flow (workflow, `Queue`, `GitHub`, GitHub API: four participants, with failure paths `fail_or_retry`/`hold_start_error`), and no lifecycle for the session states `waiting`, `running`, `finished`, `no-start`, `start-error` that `Queue.session` returns. The structure diagram omits the toolkit import used by `delta` and the subprocess calls. | `.github/bible/bible_queue.py:413-429,477-525,768-794` | Add one sequence diagram for `reconcile`, one state diagram for session states, and the two missing edges. |
| V-009 | `lld/bible-mode-b/bible_queue.md:106-400` (call graph) | Inconsistent | minor | The graph has no intro sentence and no evidence table: its 223 edges rest on the cards' `Calls` rows only. A reader cannot tell what an edge means or that name-only matching produced V-004. | module page lines 104-106 | Add a sentence on how the edges were derived and the limit of name matching. |
| V-010 | `lld/bible-mode-b/README.md:184-186` (Tests) | Inconsistent | minor | The paragraph states process ("checked through the `next.py` analysis workflow; no runtime tests were run for the documentation-only change"), which is not a fact about the component. The search result it states is right (no test file mentions `bible_queue`). | `grep` of `*test*` paths; none found | Keep only the search result. |
| V-011 | `lld/bible-mode-b/README.md` Surprises; `lld/bible-mode-b/bible_queue.md:410` area | Omission | minor | Not listed: the module docstring's `BIBLE_AGENT_LOGINS` default ("Copilot,copilot-swe-agent[bot]") differs from the code's three-entry default, and `GitHub.prs` is never called. | `.github/bible/bible_queue.py:36,60`; `.github/bible/bible_queue.py:172-174` | Add both to Surprises. |

## Coverage findings

`coverage.py` result `PASS` at depth `deep`, component scope (copy of its table):

| Measure | Done | Total | Share | Needed |
| --- | --- | --- | --- | --- |
| Source files with a page | 1 | 1 | 100.0% | 100% |
| Symbols accounted for | 68 | 68 | 100.0% | 100% |
| Functions with a full card | 66 | 66 | 100.0% | 100% |
| Routes with an endpoint card | 0 | 0 | 100.0% | 100% |
| Citations that resolve | 648 | 648 | 100.0% | 98% |
| Branch lines cited in their card | 160 | 160 | 100.0% | 95% |
| Same-file calls drawn in call graphs | 163 | 163 | 100.0% | 95% |
| LLD pages with knowledge-graph front matter | 2 | 2 | 100.0% | 100% |
| Calls into other components cited on the calling card | 0 | 0 | 100.0% | 100% |

- No gaps. Drift since the stored inventory: none.
- `ledger/not-documented.md` does not exist in the analysis folder, so no file is listed as skipped (component scope: none).
- Totals: `components.md` gives 1 file, 844 lines for the component; my count is one source file, 844 lines (`wc -l`). Symbols: I count 66 `def` and 2 `class` lines = 68, equal to the gate's total. The README's "67 functions/methods" disagrees (V-001).
- The gate counts that a call-graph edge exists for every same-file call (163 / 163); it does not check that every drawn edge is real. V-004 is that gap.

## Depth findings

Component scope with fewer than seven files: audit the largest card of each non-test file. The file has one; I audited eight cards, comparing every branch, field, call and error with the code.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.component` (565-643, largest) | Complete | The `needs a person: ... closed without merging` return at line 575-576 is in step 1 but not in the branch table. No effect on a reader's prediction. |
| `.github/bible/bible_queue.py` | `Queue.follow` (645-692) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` (713-753) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.run` (489-525) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.session` (413-429) | Complete | none |
| `.github/bible/bible_queue.py` | `GitHub.tarball` (234-259) | Complete | A malformed archive raises `tarfile.ReadError`, which is not caught (the card lists only the request errors); minor, left as a note. |
| `.github/bible/bible_queue.py` | `Queue.delta` (768-794) | Complete | none |
| `.github/bible/bible_queue.py` | `main` (797-840) | Complete | none |

Depth 8 / 8 = 100%; usable 100%. The `Called by` rows are not part of the card score; their errors are V-003 and V-005.

## Diagram findings

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README structure flowchart (`README.md:38-60`) | finding | ok | finding | ok | ok | ok | ok (read, not rendered) | Every edge has an evidence row and each citation shows the element. Missing: the toolkit import edge and the subprocess edge (V-008). No sequence or lifecycle diagram (V-008). |
| README class diagram (`README.md:80-110`) | ok | ok | ok | ok | ok | ok | ok (read, not rendered) | Fields and methods match the cited lines; `Queue --> GitHub` is supported by `Queue.run_issues` and others. |
| Module call graph (`bible_queue.md:106-400`) | ok | ok | ok | finding | finding | ok | ok (read, not rendered; one node id is `call`, which is not a reserved word in flowcharts) | 223 edges; five are false (V-004); edges have no evidence rows (V-009). |

I searched the repository for the ways the code reaches outside itself: `urllib.request` (the GitHub API, in the diagram), `subprocess` (V-007), `tempfile`/file writes (tarball tree, in the Data table), `open` (the `--changed-file` input, in the Data table). No database, queue, mail or spreadsheet.

## Data dictionary and mind map findings

none for this scope. The component owns no store: its data are GitHub issues, labels, branches and pull requests (README Data table, all rows confirmed) and a temporary tree. The data dictionary and the mind map do not exist yet and are left to the whole verification.

## Knowledge base findings

none for this scope; `knowledge/` is built when the whole analysis is assembled. Both component pages have the required front matter (gate: 2 / 2). The front matter of the README lists `calls: [external:GitHub API, symbol:components.rows_of, ...]`; I confirmed each against `.github/bible/bible_queue.py:775-781`.

## Readability and prose findings

- Read as a new engineer: the README opens with a table, then a plain responsibility paragraph, then the diagram; the order is sensible. The module page opens with a summary and an index whose every row links to its card; I found `GitHub.merge`, `Queue.follow` and `main` from the index without trouble.
- No claim numbers like `C-154`, no template text; one process sentence in Tests (V-010).
- Every fifth cited sentence or row on the README (rows at lines 22, 37, 62, 84, 119, 150, 176, 199, and so on) says no more than its citation, except V-001 and V-002.
- The README's "No other analysis component calls into this component" is marked `(inferred` and is right: my search of `*.py`, `*.yml`, `tools/` and the root `README.md` found six references to `bible_queue`/`.github/bible/`, in the source file and its three workflow adapters, as stated.

## Ledger findings

Component scope: `progress.md` and `ledger/coverage-ledger.md` belong to the planning step, so a stale row there is not this component's finding. `components.md` and `components.json` list the component with paths `.github/bible/` and `.github/workflows/`, which agrees with the pages except for V-006. `ledger/components/bible-mode-b/status.json` says `COMPONENT_DONE`, 4 of 4 packets, so the component was finished before this verification.

## Consistency findings

- Names agree between the front matter, the README and the module page (`GitHub`, `Queue`, `main`, `BIBLE_*`). Line ranges for `GitHub` (88-302) and `Queue` (396-794) agree with the code.
- The README's 67 functions disagrees with the 66 cards and the code (V-001).
- Option defaults in the README's Configuration table all match the code, including `--depth` default `deep` (`.github/bible/bible_queue.py:806`) and `GITHUB_API_URL` default (`:91`).
- No secret value appears in the component's pages. A search for common token prefixes and private-key headers found nothing.

## Limits

- A sample of 195 of 648 citation rows was checked (standard level), not all; the module page's rows outside the sample were not opened one by one.
- The coverage script matches names; it does not read meaning (V-003 and V-004 passed it). The depth audit covers eight cards of 66, not every card.
- Verification shows the pages match the code, not that the code matches what runs in production. No workflow was run.
- Diagrams were read, not rendered (no renderer installed).
- The call graph is built by name matching; edges between methods with the same name in the two classes (`issues`, `file`, `close`, `run`) are where it is wrong. Anyone using it as a lead should open the call line.
- The same model family may have written and verified this analysis (the author's model is not stated): a person or another model should re-check the two `major` corrections and a few confirmed statements.
- I saw the summary of an earlier round's report before judging; I re-derived every finding from the code.

## Everything checked

Every row of the sample that was not simply confirmed:

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 4 | group A | Wrong | V-001 |
| 66 | group A | Overstated | V-002 |
| 245 | group D | Confirmed | statement true; list incomplete (V-005) |
| 259 | group D | Confirmed | statement true; list incomplete (V-005) |
| 546 | group D | Confirmed | statement true; list incomplete (V-005) |

Confirmed rows, by range: 1-3, 5-65, 67-118 (group A); 119-644 divisible by 7 except 245, 259, 546 above (group D); 128 (group B, `(inferred` text: lines 88-92 show no annotations and no factory).

Statements checked outside the sample: the 27 `No call site` rows and the 223 call-graph edges (by searching the source and by an AST pass over the edges: V-003, V-004); the `Calls into other components` row for `Queue.delta`; the diagrams' edge labels; the cited workflow lines for `bible-plan.yml`, `bible-queue.yml`, `bible-delta.yml`; the 8 audited cards; the README's six-reference search; the toolkit signatures used by `Queue.delta`; no secret values in the pages.
