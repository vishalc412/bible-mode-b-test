# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Analysis fingerprint | 12739e08a174be01 |
| Analysis snapshot | 24 in-scope files, 1,606 source lines, 2026-11-23, no version given (front page) |
| Repository at verification | 25 files in scope, 11 source files (coverage.py). The 25th is the `.git` worktree pointer file. `.github/bible/bible_queue.py` has 1,310 lines; the stored inventory says 1,294, and the baseline of 2026-11-24T13:41:48 matches 1,310. No version given |
| Depth stated / depth found | deep / deep. Every page measure passes; the gate returns GAPS only because of a claim number in an archived verification report |
| Verified with | Claude Code (Claude Opus 5.5), standing in for the GitHub Copilot coding agent |
| Analysis produced with | Copilot coding agent; model not recorded (front page) |
| Sampling level | standard, plus the delta part audited in full |
| Date | 2026-11-24 |

After corrections: every flagged statement re-checked: 6 of 7 confirmed.

The six confirmed are V-001, V-002, V-003, V-005, V-006 and V-007 of the round-2 report (now `verification-report-2026-11-23-2.md`). V-004 was not applied, although the revision log says it was. Steps 1 to 8 of the skill were all done.

## Summary

The revision fixed the main problem of round 2. The queue page's citations now point at the right lines of the 1,310-line `bible_queue.py`. The five missing cards exist. The page measures pass: 116 of 116 symbols, 312 of 312 branch lines, and 226 of 231 call-graph edges.

In the sample of 591 citations, 571 are confirmed. Accuracy is 97.6% and citation quality is 96.6%. Of the 16 cards in the depth audit, 15 are Complete and 1 is Partial.

The analysis is weakest where it summarises the queue rather than carding it. Four statements a reader would act on are wrong:

- The front page still claims a coverage PASS at 111/111 symbols (round-2 V-004, not applied).
- Two HLD pages say pushes under `.github/**` do not start the update workflow. They do.
- The key-flows page says a failed whole verification needs a person. The code starts an automatic revision.
- The data dictionary says `tools/plan.py` writes `components.json`. It writes `plan.json`.

The HLD and the component README also never mention the whole-analysis revision loop or the deferred updates.

There are four major corrections, accuracy is above 85% and coverage is 100%, so the verdict is PASS AFTER CORRECTIONS and not PASS. The coverage gate also returns GAPS, but only because of an archived verifier report that `coverage.py` does not skip. The pages themselves pass every measure.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 116 / 116 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 98 / 98 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 312 / 312 (100.0%); 226 / 231 (97.8%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner; the two catalog GET routes have endpoint cards (`lld/api/catalog/catalog.md`) |
| Citations that resolve | 1994 / 1997 (99.8%). The 3 that do not are in the archived `verification-report-2026-11-23.md` |
| Coverage gate | GAPS: 1 opaque claim number, in the archived round-1 verification report only |
| Citations in the analysis / checked | 1997 / 591 sampled, plus 144 in the delta part (15 of them overlap the sample) |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 571 / 6 / 9 / 5 / 0 |
| Omissions (significant) / Inconsistent | 5 (1) / 8 |
| Accuracy / citation quality | 97.6% / 96.6% |
| Cards audited: Complete / Partial / Shallow / Wrong | 15 / 1 / 0 / 0 (Step 5); the 3 delta-part method cards are 3 / 0 / 0 / 0 |
| Depth / depth, usable | 93.8% / 100.0% |

## How the sample was selected

Level `standard`, from `ledger/citations.tsv` as `coverage.py` rewrote it in this session (1,997 rows).

- **Group A (300 rows: 1-300).** Every citation on `README.md`, `hld/*` and `knowledge/AGENT-CONTEXT.md`. The skill puts the agent context in group A.
- **Group B (21 rows).** Every row labelled `inferred` or `assumed`: 305, 313, 505, 1369, 1499-1500, 1503-1509, 1512-1514, 1516, 1532, 1598, 1600, 1603.
- **Group C (38 rows).** Every other row under a heading or table title containing rule, outbound, calls out, integration, security, secret, auth or permission. The nearest heading or bold title line above the citation decides. Rows 394-403, 418-428, 1295-1299, 1489-1493, 1498, 1667-1669 and 1680-1682.
- **Group D (232 rows).** Every remaining row whose index is divisible by 7, from 301 to 1988.
- **Left out of the sample: rows 1989-1997.** They cite from the archived `verification-report-2026-11-23.md`, a verifier record, not an analysis claim.

**Delta part, audited in full and reported separately.** `delta-log.md` has two rows dated 2026-11-24, after the round-2 report. `ledger/delta.md` names five changed symbols: `GitHub`, `GitHub.agent_events`, `Queue`, `Queue.session` and `Queue.continue_if_unfinished`. It also lists 55 page lines to recheck. I judged every citation on those five cards and on those 55 lines: 144 rows, 15 of them also in the sample. 142 are confirmed; the other two are rows 227 and 297, which are also in group A and counted there.

The revision log's changed statements were re-checked too: the `GATE_TIMEOUT` statement, the `age` "Called by" row, the page line counts and the "Called by" regeneration.

## Earlier corrections re-confirmed

| Round-2 item | Holds? | Re-opened |
| --- | --- | --- |
| V-001 queue citations off | Yes. Sampled queue rows are confirmed, apart from those listed below; 142 of the 144 delta-part rows are confirmed. One comma-list citation is still off (see V-009) | `.github/bible/bible_queue.py` throughout; `lld/bible-mode-b/bible_queue.md` cards |
| V-002 five uncarded symbols | Yes. `shown_files`, `Queue.could_not_check`, `Queue.whole_fingerprint`, `Queue.deferred_updates` and `Queue.whole_hold` have cards and edges from `assemble_phase`. The `deferred_updates` edges to `me` and `timeline` are still missing (V-007) | `.github/bible/bible_queue.py:374-379,884-912,1029-1049` |
| V-003 `Queue.render` card | Yes. Lines 1183-1194 and the hidden `bible-state` block are described | `.github/bible/bible_queue.py:1183-1194` |
| V-004 front page coverage claim | **No.** README.md lines 12 and 15 still read "Status: DRAFT, not yet verified" and "PASS at deep: 111/111 symbols, 274/274 branch lines, 1,886/1,886 citations". `revision-log.md` says this was replaced | `verification-coverage.md` |
| V-005 queue page Lines row and index | Yes. The page says 1310 lines and every index range matches the inventory. Branch lines are 312/312 | `.github/bible/bible_queue.py:108-1306` |
| V-006 `GitHub` field citation | Yes. It now cites 109-112, which is right after the latest code shift | `.github/bible/bible_queue.py:108-112` |
| V-007 `tls-migration/` rows in the ledger | Yes. Four rows were added. The ledger's header and coverage paragraph are stale again (V-015) | `ledger/coverage-ledger.md` |

Revision-log changed statements:

- **The `Queue.check` 300-second timeout holds.** It is stated on hld/03-integrations.md line 50 and lld/bible-mode-b/README.md line 222, and matches `.github/bible/bible_queue.py:76,870-880`.
- **The `age` "Called by" row is right.** It lists `.github/bible/bible_queue.py:500,504,1163,1203`.
- **The claim that the "Called by" rows were regenerated from the code does not hold.** Nine helper cards keep a placeholder, and 15 cards miss callers (V-006 below).

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | README.md lines 12 and 15 (round-2 V-004, not applied) | Inconsistent | major | The front page claims "PASS at deep: 111/111 symbols, 274/274 branch lines, 1,886/1,886 citations". The gate run today gives 116/116 symbols, 312/312 branch lines and 1,994/1,997 citations, and returns GAPS (only for the archived report) | `verification-coverage.md` | Replace the Coverage row and the Status line with the gate's figures and result. Do not claim PASS |
| V-002 | Row 36 (hld/02-architecture.md line 101); hld/05-key-flows.md line 218, flow 5 step 1 (comma-list citation, outside the sample) | Wrong | major | The push trigger ignores only `codebase-analysis/**` and `.github/skills/**`. Its comment says code under `.github/` can belong to a component, and `Queue.delta` applies the same rule | `.github/workflows/bible-delta.yml:8-12`; `.github/bible/bible_queue.py:1224-1227` | Say: default-branch pushes, ignoring `codebase-analysis/**` and `.github/skills/**` only. Workflow and queue changes do start update issues |
| V-003 | Row 129 (hld/05-key-flows.md line 193, flow 4 failure paths); flow 4 steps 12-13 | Wrong | major | When a whole verification is missing, unreadable, not PASS or has major corrections, the code does not stop for a person. It labels the issue `bible-needs-revision`, comments, closes it as not_planned, and `revise_all_step` opens a revision, then a new verification. A person is asked only after `MAX_VERIFY_ROUNDS` (2) rounds. Done also needs the report's fingerprint to equal the pages now, and the report must come from this run's own pull request | `.github/bible/bible_queue.py:74,929-962,965-968,976-984,1051-1129` | Rewrite the failure path and step 12: revision loop, re-verification, hold after 2 rounds, and the fingerprint and same-run conditions |
| V-004 | Rows 1428 and 1435 (lld/data-dictionary.md lines 94 and 100; also lines 90-101, rows 1429-1434 and 1436-1437) | Wrong | major | The page says the planning tool `tools/plan.py` emits the `components.json` fields (`schema`, `tool`, `generated`, `proposed`, `budget`, `depth`). `tools/plan.py` writes `plan.json`, with `version`, `passes` and a `components` dict. `components.json` is written by the toolkit's discover step | `tools/plan.py:41-57`; `.github/bible/bible_queue.py:414,605-607` | Name the analysis toolkit's discover step as the producer, cite `codebase-analysis/components.json` for the fields, and drop the `tools/plan.py` citations from this table |
| V-005 | Rows 1273-1274 (lld/bible-mode-b/bible_queue.md line 2988) | Wrong | minor | No `closed_revise` or `all_revise` variable exists in the file; a search finds none. The cited lines hold other code | `.github/bible/bible_queue.py:641-645,759-765` | Delete the sentence (the component README already withdrew it) |
| V-006 | lld/bible-mode-b/bible_queue.md lines 2708, 2736, 2757, 2790, 2820, 2853, 2887, 2926, 2954; and the "Called by" rows of 15 cards | Inconsistent | minor | Nine helper cards say "Queue functions in later source packets" instead of call sites. Real callers: `labels_of` 506, 520, 535, 548, 576, 714, 800, 831, 952, 958, 1046, 1059, 1155, 1166. `comp_label` 677-1256 (17 lines). `issue_text` 651, 679, 1005. `assignment` 543, 577, 657, 683, 795, 1011, 1128, 1256. `json_file` also 605, 1217. `section` only 456. `report_facts` 754, 927, 976. `as_int` 254, 635, 736, 835, 837, 887. `status_of` 507, 719, 828, 835. Also missing are the callers in `held`, `revise_all_step`, `continue_if_unfinished`, `whole_hold`, `deferred_updates` and `could_not_check`. Examples: `GitHub.timeline` 524, 1032, 1143, 1145; `GitHub.label` 531, 954, 959, 980, 1156, 1167; `Queue.run_issues` 1045, 1056, 1062, 1066, 1068, 1074 | `.github/bible/bible_queue.py` (lines given) | Regenerate every "Called by" row from the code. Round 1 (V-008) and the component report (V-007) asked for this too |
| V-007 | lld/bible-mode-b/bible_queue.md call graph | Omission | minor | Five calls are not drawn: `assemble_phase` to `pr_files`, `deferred_updates` to `me` and `timeline`, `delta` to `age` and `comment` | `.github/bible/bible_queue.py:936,1031-1032,1203,1210`; `verification-coverage.md` | Add the five edges |
| V-008 | Row 74 (hld/03-integrations.md line 48); row 175 (hld/05-key-flows.md line 398) | Overstated | minor | "No timeout or retry is specified" is not right for the job: it sets `timeout-minutes: 5`. Only the API call has no timeout of its own, and nothing retries | `.github/workflows/poc-assign-copilot.yml:37` | Say: no retry; the job is limited to 5 minutes; the `gh api` call has no timeout of its own |
| V-009 | Rows 92, 111-112, 146, 297, 300; lld/bible-mode-b/bible_queue.md line 2184 (outside the sample); lld/orders/orders.md lines 66 and 79 (outside the sample) | Citation off | minor | Row 92: ready-before-merge is in `merge`. Rows 111-112: the job's `if:` is at line 36. Row 146: the `price_of` call is at line 31. Row 297: session estimates come from `components.json` as the queue reads it, not from `tools/plan.py`. Row 300: "intentional, leave unchanged" rests on recorded user answers, not on code. Line 2184: lines 912-920 and 959-960 are other code. orders.md: the lookup error is in `price_of` | `.github/bible/bible_queue.py:341-343,627,736-737,916-923,963-964`; `.github/workflows/bible-plan.yml:36`; `components/catalog/service.py:29-31`; `components/catalog/catalog.py:20-24` | Cite those lines. For row 300, cite the components' `questions.md` and say it is a recorded user decision |
| V-010 | Rows 428 (lld/bible-mode-b/README.md line 224), 1309 (lld/catalog/README.md line 143), 1680-1682 (lld/tools/README.md line 99) | Overstated | minor | Statements of absence (no token logging, no metrics or tracing calls, no timeout or retry) are true when searched, but they are written as plain facts on code citations, without the inferred mark | `.github/bible/bible_queue.py:110,119-120`; `tools/fanout.sh:1-31` | Mark each `(inferred: ...)` and name the search |
| V-011 | Row 1316 (lld/catalog/README.md line 159) | Overstated | minor | The "(4 hits)" count cannot be reproduced. There is 1 hit outside the analysis folder; the main claim holds | `components/catalog/catalog.py:36-39` | Drop the count, or state the exact search and its scope |
| V-012 | Row 227 (knowledge/AGENT-CONTEXT.md line 9); AGENT-CONTEXT.md line 110 (outside the sample); AGENT-CONTEXT.md line 3 | Overstated | minor | The catalog server binds 127.0.0.1 by default but `CATALOG_HOST` changes it, so it is not simply loopback. Line 110 says the docstring lists fewer agent logins than the code; both list the same three today. Line 3 gives the snapshot date as 2026-11-23, but the pages describe the code of the 2026-11-24 baseline | `components/catalog/service.py:41`; `.github/bible/bible_queue.py:36,61` | Reword line 9, remove the login clause on line 110, and set the snapshot date to the 2026-11-24 baseline |
| V-013 | hld/05-key-flows.md flows 4 and 5; lld/bible-mode-b/README.md | Omission | significant | No HLD page and not the component README describe the whole-analysis revision loop (`revise_all_step`) or the `@copilot continue` requests. Nor do they say that while a run is open `Queue.delta` only records `bible-deferred-update` comments and replays them when the run ends, or that more than 10 changed components give a hold issue. A reader would be misled about how a run ends and what a push triggers. The module page's cards do cover them | `.github/bible/bible_queue.py:999-1002,1013-1026,1051-1181,1203-1216,1229-1238` | Add these steps to flows 4 and 5 and to the component README's flow section |
| V-014 | README.md Components and Totals tables | Inconsistent | minor | `bible-mode-b` is given as 1,130 lines and 69 functions; the file has 1,310 lines and the component README says 74. The `orders` row says 7 functions, its README 18. Totals say 14 source files (gate: 11), 111 symbols and 93 cards (116 and 98), 43 diagrams (42 found), and 218 nodes, 541 edges and 301 chunks (graph: 225, 565 and 312). The snapshot row says 24 files | `verification-coverage.md`; `knowledge/graph.json` | Update the front page from the gate, the graph and the component READMEs |
| V-015 | ledger/coverage-ledger.md lines 3 and 43 (row 301) | Inconsistent | minor | It says 24 files and 14 source files, and that the gate "is being rerun ... recorded below after the gate completes". The gate counts 25 files and 11 source files; the promised figures are not there | `verification-coverage.md` | Replace with the gate's figures, and decide whether the `.git` pointer file belongs in scope (it does not: exclude it from the inventory) |
| V-016 | lld/bible-mode-b/bible_queue.md, `Queue.component` card | Omission | minor | Depth Partial. The card does not say the verify issue is assigned on `verify_model` (line 795). The round-limit hold at 774 also needs a report to exist, which its branch row leaves out. There is no branch row for the closed-unmerged pull request return at 696 | `.github/bible/bible_queue.py:696,774,795` | Add the three points |
| V-017 | README.md, hld/01 and hld/02 diagrams | Omission | minor | The context diagrams draw `tools` with no edge: the gh CLI calls to GitHub are missing. The local development settle endpoint is in neither the context nor the container diagram. Three container edges have no protocol: queue to GitHub (HTTPS REST and GraphQL), catalog to supplier (HTTP) and orders to payment (HTTP) | `tools/fanout.sh:10-29`; `components/orders/orders.py:9-12`; `.github/bible/bible_queue.py:111,334` | Add the edges and the protocols |
| V-018 | hld/05-key-flows.md sequences 1-10; diagram labels | Inconsistent | minor | No sequence has an `alt` block, though flows 2-5 and 7-10 handle failures. There is a `;` inside labels at README.md lines 43, 47 and 53, hld/01 lines 39, 43 and 49, hld/02 line 56 and lld/tools/README.md line 47, and an unquoted label at lld/tools/gate.md line 49. The store is named `_PRODUCTS` in the HLD and "Catalog products" in the data dictionary | `components/catalog/catalog.py:8` | Add `alt` blocks; remove the `;`; quote the label; use one store name |
| V-019 | lld/data-dictionary.md and hld/04-data-architecture.md | Omission | minor | Three markers are missing: the tracker's hidden `bible-state` block (keys `nocheck:` plus the name, and `nofp`), the `bible-deferred-update` comment marker and `CONTINUE_MARK`. So are the labels `bible-revise-all`, `bible-needs-revision`, `bible-stale-verdict` and `bible-whole`, and the pull request fields `created_at`, `changed_files`, `previous_filename` and `user.type` | `.github/bible/bible_queue.py:83,97-99,230,254,261,598-604,690,887-890,945,1036,1187,1211` | Add them |
| V-020 | knowledge/graph.json | Inconsistent | minor | There are duplicate nodes for one item: `file:--changed-file list` and `file:changed-path list`; the tarball destination appears twice; page dependencies exist as both `thing:` and `page:` nodes. `CATALOG_HOST` and `CATALOG_PORT` are `thing:` nodes while other variables are `config:`. A `file:.git` node stands for the worktree pointer | `.github/bible/bible_queue.py:268-307,1302-1303` | Merge the duplicates; exclude `.git` from the inventory and the graph |
| V-021 | lld/bible-mode-b/bible_queue.md Index | Inconsistent | minor | 36 of the 76 index links point at anchors that no heading produces, for example `#github__init__repo-token-api-none` and every `#queue_...` link. They do not reach their cards | page headings | Generate the anchors from the headings |
| V-022 | revision-log.md | Inconsistent | minor | It records V-004 as applied and the "Called by" rows as regenerated; neither holds (V-001, V-006). `ledger/delta.md`'s recheck list names 21 lines that no longer carry citations, because the revision renumbered the pages | this report | Correct the log when V-001 and V-006 are applied |

## Coverage findings

- I ran `coverage.py --depth deep` myself and it returned GAPS. Every page measure passes, and the only listed gap is one claim number, which sits in the archived round-1 report `verification-report-2026-11-23.md` (line 119). The three unresolved citations and one short path are in that file too.
  - `coverage.py` skips `verification-report.md` but not its archives (`SKIP_DOCS` in the verifying skill's script), although the skill says to keep them.
  - So this gap is not the analysis's, and the author cannot fix it without editing a verifier record. The fix belongs in the toolkit: skip archived `verification-report-*.md` files. Until then the gate cannot return PASS on this folder.
- The five missing call-graph edges are V-007. 97.8% is above the 95% threshold.
- `ledger/not-documented.md` does not exist, so nothing is listed as exempt.
- Totals: the front page gives 24 files, 14 source files and 1,606 lines. The gate counts 25 files in scope and 11 source files; my own count of non-empty source files is also 11 (V-014). The extra file is the `.git` worktree pointer, which the inventory picked up as an added file (V-015, V-020).
- **Drift.** The stored `ledger/inventory.json` records `bible_queue.py` at 1,294 lines; the file and the baseline have 1,310.
- **Comma-list citations.** 206 page lines carry only comma-list citations, such as `bible-delta.yml:6-10,18-20`. `ledger/citations.tsv` has no row for these, so no fixed sample reaches them. This round reached some through the delta part and the depth audit (V-002, V-009, V-012). See Limits.
- **Calls into other components.** The two calls from `orders` into `catalog` are cited on the calling cards: `components/orders/orders.py:20,40`.

## Depth findings

Selection: the five largest source files are `bible_queue.py` (1,310), `tools/gate.py` (117), `components/orders/test_catalog_client.py` (66, a test file, so its rows are not cards), `tools/plan.py` (62) and `components/orders/orders.py` (51). The route file is `components/catalog/service.py`. The 3rd file alphabetically is `service.py` again, and the 7th is `test_catalog_client.py`, a test file. For each, I took the three largest functions and both catalog routes.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.component` | Partial | The `verify_model` assignment, the report-exists condition of the round hold, and the closed-unmerged return (V-016) |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` | Complete | none. Its Steps citation is off (V-009) |
| `.github/bible/bible_queue.py` | `Queue.revise_all_step` | Complete | none |
| `tools/gate.py` | `check` | Complete | none |
| `tools/gate.py` | `main` | Complete | none |
| `tools/gate.py` | `count_tests` | Complete | "Called by" leaves out `tools/plan.py:36` |
| `tools/plan.py` | `scan` | Complete | none |
| `tools/plan.py` | `main` | Complete | none |
| `components/orders/orders.py` | `order_total` | Complete | Citation for the lookup error is off (V-009) |
| `components/orders/orders.py` | `validate` | Complete | none |
| `components/orders/orders.py` | `settle` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler.do_GET` | Complete | The fall-through 404 at line 34 is in the Steps, not in the branch table |
| `components/catalog/service.py` | `_send` | Complete | none |
| `components/catalog/service.py` | `make_server` | Complete | none |
| `lld/api/catalog/catalog.md` | GET `/health` | Complete | none |
| `lld/api/catalog/catalog.md` | GET `/price/<sku>` | Complete | none |

Delta part, scored apart from the table: `GitHub.agent_events`, `Queue.session` and `Queue.continue_if_unfinished` are all Complete. The `GitHub` and `Queue` class cards have every citation confirmed.

## Diagram findings

I counted 42 mermaid blocks. I read them all but did not render them.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README.md context | ok | ok | finding | ok | ok | ok | finding | V-017; `;` in labels (V-018) |
| hld/01-system-context.md context | ok | ok | finding | ok | ok | ok | finding | Same as the README |
| hld/02-architecture.md containers | ok | ok | finding | finding | ok | finding | finding | No protocol on three edges; `_PRODUCTS` naming (V-017, V-018) |
| hld/02-architecture.md deployment | ok | ok | ok | ok | ok | ok | ok | Evidence is per component; the trigger row is V-002 |
| hld/04-data-architecture.md two ER and three lifecycle diagrams | ok | ok | ok | ok | ok | ok | ok | Fields, keys and transitions match the code |
| hld/05-key-flows.md flows 1-10 | ok | ok | n/a | ok | finding | ok | ok | No `alt` (V-018); flow 4 and flow 5 step 1 are Wrong (V-002, V-003) |
| 00-mind-map.md five mind maps | ok | ok | ok | n/a | n/a | ok | ok | Every component is present; every leaf names a real page |
| lld/bible-mode-b/README.md structure, reconcile, session states, classes | ok | ok | minor | ok | ok | ok | ok | The structure diagram leaves out the `whole_fingerprint` subprocess and the toolkit import (`.github/bible/bible_queue.py:905,1221-1222`) |
| lld/bible-mode-b/bible_queue.md call graph | ok | ok | n/a | ok | n/a | ok | ok | Five edges missing (V-007) |
| lld/catalog/README.md two diagrams | ok | ok | ok | ok | ok | finding | ok | Store naming (V-018) |
| lld/orders/README.md | ok | ok | ok | ok | ok | ok | ok | The partner is left out, and the page says so |
| lld/tools/README.md | ok | ok | ok | ok | ok | ok | finding | `;` on line 47 |
| lld/tools/gate.md call graph | ok | ok | n/a | ok | n/a | ok | finding | Unquoted label on line 49 |
| The other module call graphs (catalog, service, catalog_client, orders, test_catalog_client, plan) | ok | ok | n/a | ok | n/a | ok | ok | |
| lld/api/catalog/catalog.md two sequences | ok | ok | n/a | ok | ok | ok | ok | Both have `alt` |

- **Edge evidence.** Edges whose statement is Wrong: the flow 5 trigger step and the flow 4 failure path (V-002, V-003).
- **Searches for outbound reach** (urllib, subprocess, open, gh, http) found no target outside the context and container diagrams other than those in V-017.
- **D1.** The required set is present.

## Data dictionary and mind map findings

- **Entries.** `_PRODUCTS`, the GitHub records, `plan.json`, `components.json`, both kinds of `status.json`, `ledger/issues/*.md`, the verification reports, `baseline.json`, the changed-file list, the gate tarball and the gate artifacts all have entries.
- **Fields checked.** `_PRODUCTS` (sku, name, price, stock) and `plan.json` (`tools/plan.py:21-54`) are complete, and so are the six tracker settings.
- The producer of `components.json` is Wrong (V-004), and the missing markers, labels and fields are V-019.
- **Mind map.** Every component is present and every leaf names a page that exists.

## Knowledge base findings

- **Freshness.** `knowledge/graph.json` was generated at 2026-11-24T13:57:12, after the last delta was applied at 13:41:48, and its symbol lines match the 1,310-line file. File times cannot settle whether a page changed after it, because every file has the checkout time.
- **Ten `analysis` edges.** I took every 14th of 148 and confirmed all 10.
- **Five `name-unique` CALLS edges.** All 5 are right: `.github/bible/bible_queue.py:415,553,678,1010,1142`. None of the five is wrong.
- **Duplicates.** Duplicate nodes and the `.git` node are V-020.
- **Agent context limits.** `knowledge/AGENT-CONTEXT.md` lines 3 and 5 state all three required limits. Its snapshot date is stale (V-012).

## Readability and prose findings

- **Pages read.** The four component READMEs and the `orders`, `gate` and `service` module pages are plain and specific, and open with a summary table.
- **Index links.** On the queue page, 36 index links do not reach their cards (V-021). The other module pages' index links all work.
- **Placeholder text.** No claim numbers or template text were found in the analysis pages. The placeholder "Called by" text is V-006.
- **Uncited sentences.** The every-fifth-sentence check on the HLD pages and component READMEs found nothing stated without a citation beyond what V-002, V-003, V-008 and V-012 record. The flow summaries leave things out (V-013).

## Ledger findings

- **Completeness.** Every folder I listed is in `ledger/coverage-ledger.md`: the root, `.github/bible`, `.github/workflows`, `components`, `components/catalog`, `components/orders`, `tools`, `tls-migration` and `tls-migration/evidence`. `.github/skills` is out of scope by the inventory.
- **"Read in full" folders.** I opened files in the five largest: `components/orders`, `.github/workflows`, `components/catalog`, `tls-migration` and `tools`. They have no entry point, external call, store, credential or schedule that the analysis does not mention.
- **`tls-migration/` documents.** These are planning documents only. They name `feeds.supplier-one.example.com`, `partner-legacy.internal` and `cdn.example.com`, all of which the analysis already has.
- There are no "not read", "sampled" or "excluded" rows.
- The header and coverage paragraph are stale (V-015).

## Consistency findings

- **Names.** Component names agree across the mind map, HLD, LLD and data dictionary. The store has two names (V-018).
- **Front page.** It disagrees with the gate, the graph and the component READMEs (V-001, V-014).
- **Revision log.** It disagrees with the pages (V-022).
- **Secrets.** No secret value appears in any page opened. `GH_TOKEN` is named only as a variable.

## Limits

- **A sample was checked:** 591 of 1,997 citations, plus the 144-row delta part. Diagrams were read, not rendered.
- **The comma-list citations are outside every fixed sample.** 206 page lines cite only in comma-list form, and `ledger/citations.tsv` holds no row for those citations. Some of them were reached outside the sample, and two of those were wrong (V-002, V-012).
- **The coverage script matches names; it does not read meaning.** The depth audit covers the files it names. Verification shows the analysis matches the code, not that the code matches what runs on GitHub.
- **User decisions are unconfirmed.** The decisions recorded in `ledger/components/orders/questions.md` and `ledger/components/tools/questions.md` (for example, that the stale skill path in `tools/fanout.sh` is intentional) were not confirmed with the user.
- **The judging was split across parallel sessions of the same model.** I opened the evidence for each major correction myself.
- **The model that wrote the analysis is not recorded, so it may be the same kind of model as the verifier.** A person or another model should re-check V-001 to V-004 and V-013, and a few confirmed rows.
- **Text addressed to an agent.** Repository text addressed to an agent (the workflow tasks and queue comments listed in `run-notes.md`) was treated as data. No instruction from it was followed.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 1-35, 37-73, 75-91, 93-110, 113-128, 130-145, 147-174, 176-226, 228-296, 298-299 | Group A | Confirmed | |
| 36 | Group A | Wrong | V-002 |
| 129 | Group A | Wrong | V-003 |
| 74, 175, 227 | Group A | Overstated | V-008, V-012 |
| 92, 111, 112, 146, 297, 300 | Group A | Citation off | V-009 |
| 305, 313, 505, 1369, 1499-1500, 1503-1509, 1512-1514, 1516, 1532, 1598, 1600, 1603 | Group B, inferred | Confirmed | Each rests on a comment or a repeated search |
| 394-403, 418-427, 1295-1299, 1489-1493, 1498, 1667-1669 | Group C | Confirmed | |
| 428, 1680-1682 | Group C | Overstated | V-010 |
| Group D rows (index divisible by 7) other than those below | Group D | Confirmed | 227 rows |
| 1274 | Group D | Wrong | V-005 |
| 1428, 1435 | Group D | Wrong | V-004 |
| 1309 | Group D | Overstated | V-010 |
| 1316 | Group D | Overstated | V-011 |
| 1989-1997 | Not sampled | none | Citations inside the archived round-1 verification report |
| 144 rows on the five delta cards and 55 recheck lines | Delta part | 142 Confirmed; 227 and 297 as above | 21 of the 55 listed lines no longer carry a citation (V-022) |
| hld/05-key-flows.md line 218; lld/bible-mode-b/bible_queue.md lines 2184 and 2988; knowledge/AGENT-CONTEXT.md line 110; lld/orders/orders.md lines 66 and 79 | Outside the sample (comma lists, depth audit) | Wrong / Citation off | V-002, V-009, V-005, V-012 |
| Round-2 V-001 to V-007 | Re-check | 6 of 7 confirmed | V-004 was not applied (V-001 here) |
| Diagrams, data dictionary, mind map, knowledge base, ledger, consistency | Steps 6 and 7 | See the sections above | |
