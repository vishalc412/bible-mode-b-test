# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Analysis fingerprint | 24b18d98abe659bc |
| Analysis snapshot | 24 in-scope files, 1,812 source lines, code of 2026-11-24 (baseline 2026-11-24T14:34:00), no version given (front page) |
| Repository at verification | 24 files in scope, 11 source files (coverage.py); `.github/bible/bible_queue.py` has 1,336 lines; no drift from the stored inventory; no version given |
| Depth stated / depth found | deep / deep |
| Verified with | Claude Code (Claude Opus 5.5), standing in for the GitHub Copilot coding agent |
| Analysis produced with | Copilot coding agent (model not recorded) for planning, components, assembly and the first revisions; Claude Sonnet 5.5 for the revisions of 24 Nov 2026 afternoon (front page) |
| Sampling level | standard, plus the re-check part (every flagged and every changed statement) and the delta part audited in full |
| Date | 2026-11-24 |

After corrections: every flagged statement re-checked: 21 of 22 confirmed.

The 22 are V-001 to V-022 of the round-3 report (now `verification-report-2026-11-24.md`). V-014 (front-page totals) does not fully hold: two figures still disagree with the graph and the pages (V-015 here). Round 4. Steps 1 to 8 of the skill were all done.

## Summary

The revision applied the round-3 corrections well. The coverage gate now passes at deep with every measure at 100%: 116/116 symbols, 98/98 full cards, 320/320 branch lines, 232/232 call-graph edges and 2,970/2,970 citations. Every multi-range citation is now its own ledger row, so the fixed sample reaches them. The four round-3 majors (front page, push trigger, failure path of the whole verification, producer of `components.json`) are fixed. Every "Called by" row on the queue page matches the code, and every index link resolves.

Of the 1,114 sampled citations, 1,074 are confirmed. Accuracy is 97.9% and citation quality is 96.4%. The re-check part (318 split queue citations, 110 rows on changed cards and pages, 255 "Called by" citations checked mechanically) found 7 more minor errors outside the sample. Of the 16 cards in the depth audit, 13 are Complete and 3 are Partial, all three on the queue's whole-analysis logic.

Where the analysis is weakest is the text the revision added for the whole-analysis loop. Two statements a reader would act on are wrong:

- **Deferred updates are not always replayed.** Five places say the paths recorded on the tracker while a run is open are replayed when the run ends. The code replays them only when the run reaches its Done step. If a person closes the tracker, or the run never finishes, they are never replayed.
- **A stale PASS does not trigger a revision.** Two diagrams send a stale PASS ("a PASS about other pages") to a revision. The code labels it `bible-stale-verdict` and opens a new verification directly. The step tables next to both diagrams say this correctly.

The other findings are minor: 21 citations that point at neighbouring lines, overstated wording (mostly absence statements without the inferred mark), three Partial cards, two front-page counts off by one, a false docstring claim left in the risks page, and diagram details.

Why PASS AFTER CORRECTIONS and not PASS: the gate passes, accuracy is 97.9% and depth is 81.3% with no Shallow or Wrong card. But there are two major corrections, and one of them is a wrong diagram element.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 116 / 116 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 98 / 98 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 320 / 320 (100.0%); 232 / 232 (100.0%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner; the two catalog GET routes have endpoint cards (`lld/api/catalog/catalog.md`) |
| Citations that resolve | 2970 / 2970 (100.0%) |
| Coverage gate | PASS (depth deep); calls into other components 2 / 2 |
| Citations in the analysis / checked | 2970 / 1114 sampled; plus 428 re-check rows judged by hand and 255 "Called by" rows checked mechanically, outside the sample |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 1074 / 17 / 21 / 2 / 0 (sample only) |
| Omissions (significant) / Inconsistent | 6 (0) / 3 |
| Accuracy / citation quality | 97.9% (1091/1114) / 96.4% (1074/1114) |
| Cards audited: Complete / Partial / Shallow / Wrong | 13 / 3 / 0 / 0 (Step 5); the delta part's 6 cards are 3 / 3 / 0 / 0, reported apart |
| Depth / depth, usable | 81.3% / 100.0% |

## How the sample was selected

Level `standard`, from `ledger/citations.tsv` as `coverage.py` rewrote it in this session (2,970 rows). Unlike round 3, no rows were left out: the gate no longer reads the archived verifier reports.

- **Group A (707 rows: 1-707).** Every citation on `README.md`, `hld/*` and `knowledge/AGENT-CONTEXT.md`.
- **Group B (33 rows).** Every row labelled `inferred`: 712, 724, 878-880, 958, 1912-1914, 1935-1937, 2009, 2322, 2327, 2334-2340, 2343-2345, 2354, 2384, 2460, 2462, 2465, 2557-2559. No row is labelled `assumed`.
- **Group C (63 rows).** Every other row under a heading or bold title line containing rule, outbound, calls out, integration, security, secret, auth or permission. The nearest such line above the citation decides. Rows 831-852, 867-877, 1915-1919, 1925-1926, 2303-2309, 2318-2321, 2323-2326, 2328-2329, 2529-2531, 2542-2544. All of them fall under "Business rules" or "Outbound calls".
- **Group D (311 rows).** Every remaining row from 708 to 2970 whose index is divisible by 7.

**Re-check part, reported separately, not in the scores.** The skill asks a later round to re-check every statement the previous report flagged and every statement the revision changed. The rows were chosen by fixed rules:

- **R1 (318 rows).** Every row outside the sample that cites `.github/bible/bible_queue.py` and shares its page line with another citation of that file. This is the rule for the comma-list citations that N-06 re-mapped from the 1,310-line file and N-07 split. The split rows cannot be told apart from citations that were always separate, so the rule takes all of them.
- **R2 (255 rows).** Every "Called by" citation of the queue outside the sample. I checked all 74 "Called by" rows on `lld/bible-mode-b/bible_queue.md`, inside the sample or not, against an `ast` walk of the file.
- **R3 (110 rows).** Every other row outside the sample:
  - on the changed queue cards (`GitHub`, `GitHub.is_agent_pr`, `GitHub.pr_files`, `Queue`, `Queue.component`, `Queue.continue_if_unfinished`), the module text (page lines 1-111) and Surprises;
  - on `lld/bible-mode-b/README.md` lines 140-175 and 290-309;
  - on all of `lld/data-dictionary.md`;
  - on `lld/orders/orders.md` lines 66, 79 and 123.

**Delta part.** `delta-log.md` has one row newer than the round-3 report: 2026-11-24T14:34:00. It changed one file, `bible_queue.py`, and removed one, the `.git` pointer. Its changed functions are `GitHub.is_agent_pr`, `GitHub.pr_files` (with the new `COMPARE_MAX`) and `Queue.continue_if_unfinished`, plus the two class cards. These cards were audited in full (Depth findings, delta part). `ledger/delta.md` now reports nothing pending.

## Earlier corrections re-confirmed

| Round-3 item | Holds? | Re-opened |
| --- | --- | --- |
| V-001 front-page coverage claim | Yes. The Status line and Coverage row match the gate run today: PASS, 116/116, 98/98, 320/320, 232/232, 2,970/2,970, 17/17, 2/2 | `verification-coverage.md` |
| V-002 push trigger | Yes. `hld/02` line 107 and `hld/05` flow 5 step 1 say only `codebase-analysis/**` and `.github/skills/**` are ignored | `.github/workflows/bible-delta.yml:6-12,19` |
| V-003 failure path of the whole verification | Yes. The flow 4 failure paths and steps 12-14 describe the revision loop, the hold after `MAX_VERIFY_ROUNDS` and the fingerprint and same-run conditions. The rebuilt diagram has a new error (V-002 here) | `.github/bible/bible_queue.py:947-1050,1074-1152` |
| V-004 producer of `components.json` | Yes. The discover step is named, `tools/plan.py` is no longer cited, and every listed field exists in `components.json` | `codebase-analysis/components.json`; `.github/bible/bible_queue.py:628-633` |
| V-005 `closed_revise` sentence | Yes. A search of the pages finds neither name | search |
| V-006 "Called by" rows | Yes. All 74 rows match the call sites an `ast` walk finds (receivers `self`, `gh`, `self.gh`, `queue` and bare names) | `.github/bible/bible_queue.py` throughout |
| V-007 call-graph edges | Yes. The gate draws 232 of 232 | `verification-coverage.md` |
| V-008 POC timeout | Yes: no retry and the 5-minute job limit. The wording "the `gh api` call has no timeout of its own" goes past what the workflow shows (V-007 here) | `.github/workflows/poc-assign-copilot.yml:37,66-69` |
| V-009 citations | Yes. The rows on those statements are confirmed in groups A and R3 | as cited |
| V-010 absence statements | Yes. All three now carry `(inferred: ...)` with the search, and I repeated the searches | `lld/bible-mode-b/README.md:270`; `lld/catalog/README.md:143`; `lld/tools/README.md:99,114` |
| V-011 "4 hits" | Yes. The count is gone | search |
| V-012 `AGENT-CONTEXT.md` lines 3, 9, 110 | Yes. The date is 2026-11-24 (the time of the baseline is not given), line 9 names `CATALOG_HOST`, and the login clause is gone. The same false login claim is still in `reference/risks-and-surprises.md` risk 8 (V-003 here) | `components/catalog/service.py:40-43`; `.github/bible/bible_queue.py:36,61` |
| V-013 whole-analysis loop and deferred updates | Yes. Flows 4 and 5 and a new section of the component README describe them. Part of the new text overstates the replay (V-001 here) | `.github/bible/bible_queue.py:1036-1064,1222-1242` |
| V-014 front-page Components and Totals | **No, not fully.** Most figures now agree. Two do not: 323 chunks against 324 in `knowledge/graph.json` and `chunks.jsonl`, and 30 inferred statements against 31 `(inferred` marks in the pages (V-015 here) | `knowledge/graph.json` stats; page search |
| V-015 coverage-ledger header | Yes: 24 files in scope, 11 source files with a page, no promise left | `ledger/coverage-ledger.md:3,43` |
| V-016 `Queue.component` card | Yes. The `verify_model` assignment, the report-exists condition and the closed-unmerged return are all on the card. It is still Partial for other reasons (V-012 here) | `.github/bible/bible_queue.py:719,797,818` |
| V-017 diagram edges | Yes. The context and container diagrams have the `tools` to GitHub `gh` edge and the local settle fake; the three container edges carry protocols | `tools/fanout.sh:10-29`; `components/orders/orders.py:9-12` |
| V-018 `alt` blocks, `;`, quoting, store name | Yes. Flows 2-10 have `alt` blocks, no mermaid label holds `;` or `#`, the `gate.md` label is quoted, and the store is `_PRODUCTS` everywhere | a scan of all 44 blocks |
| V-019 markers, labels, PR fields | Yes. All appear in `lld/data-dictionary.md` | `.github/bible/bible_queue.py:83,97-99,230,254,261` |
| V-020 graph duplicates | Yes. There is no `thing:` or `file:.git` node, and no duplicate store or outside-system node | `knowledge/graph.json` |
| V-021 index anchors | Yes. All 104 in-page anchor links in the analysis resolve to a heading | page headings |
| V-022 revision log | Yes. The earlier wrong rows are annotated. The log has new small errors of its own (V-016 here) | `revision-log.md` |

The revision's own items N-01 to N-07 were re-checked as well:

- **N-03 and N-04 hold.** The `do_GET` fall-through 404 has a branch row, and the "Called by" row of `count_tests` names `tools/plan.py:36`.
- **N-05 holds.** The structure diagram has the toolkit helpers and the `whole_fingerprint` subprocess.
- **N-06 and N-07 hold for the mapping.** Of the 318 R1 rows, 314 are confirmed. None of the other four is a range mapped to a neighbouring function.
- **The delta part:** three of its six cards are Complete and three are Partial, all minor.

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | Row 406 (hld/05-key-flows.md:259, flow 5 step 5). The same claim is at hld/05:225 (flow 4 step 15), hld/04:158, lld/bible-mode-b/README.md:172 and :174, R-12 (README.md:249, row 848) and lld/data-dictionary.md:139 | Overstated | major | Deferred paths are read only by `deferred_updates`. Its only callers are in `assemble_phase`, on the way to Done. `reconcile` visits only open trackers. So paths recorded on a tracker that a person closes, or on a run that never reaches Done, are never replayed and never get update issues | `.github/bible/bible_queue.py:604-611,1036-1050,1052-1064` | Say: "replayed only when the run ends through its Done step; if the tracker is closed by a person, or the run never finishes, the recorded paths get no update issues and must be updated by hand". Use it in all six places |
| V-002 | hld/05-key-flows.md flow 4 sequence diagram, the `else corrections asked, or a PASS about other pages` branch; lld/bible-mode-b/README.md whole-analysis flowchart, edge `verdict -> revise` "corrections asked, or a PASS about other pages" | Inconsistent | major | A clean PASS that is stale, or not by this run, is labelled `bible-stale-verdict` and verified again with no revision. `revise_all_step` returns `None` when there is no correction verdict, or when a stale verdict is newer than it, and the loop opens a new verify-all. Step 14 of the flow 4 table and the README's "Stale or foreign PASS" row say so correctly; both diagrams contradict them | `.github/bible/bible_queue.py:975-980,1089-1094,1132-1135` | Split the branch. "Corrections asked" goes to a revise-all issue. "PASS about other pages or not by this run" goes to label `bible-stale-verdict` and create the next verify-all. Do the same in both diagrams |
| V-003 | Rows 2933-2935 (reference/risks-and-surprises.md:19, risk 8) | Wrong | minor | The module docstring lists the same three agent logins as line 61. The missing `start-error` is in the `Queue.session` docstring, not the module docstring. N-02 removed this claim from the component README but not from here | `.github/bible/bible_queue.py:36,61,518` | Reword to "`Queue.session`'s docstring omits the returned `start-error` state" and drop the login clause |
| V-004 | Row 594 (knowledge/AGENT-CONTEXT.md:37) | Wrong | minor | There is no module `components.orders.catalog`. `orders.py` imports `components.catalog.catalog` | `components/orders/orders.py:5` | Say "via `components.catalog.catalog`, imported directly by `orders.py`" |
| V-005 | Row 2252 (lld/data-dictionary.md:188, `UNREADABLE`) | Wrong | minor | A missing or empty report returns `None`, not `UNREADABLE`. `UNREADABLE` means the report does not have exactly one readable Verdict row. The difference matters for a component: `None` never counts toward the round hold | `.github/bible/bible_queue.py:470-478,797` | Say "the report does not have exactly one Verdict row with one recognised verdict (a missing report gives `None`)" |
| V-006 | Citation off on HLD pages, the front page and the agent context: rows 12 and 24 (README.md:23, :61), 99 (hld/02:74), 250 (hld/04:46), 293, 294 and 297 (hld/04:157-159), 303 (hld/04:162), 445 (hld/05:379), 501 (hld/06:53), 564 and 642 (AGENT-CONTEXT.md:9, :88) | Citation off | minor | Each statement is true, but its cited lines show something else. Row 12 cites `settings_of`; 24 and 564 cite `run`; 99 cites the `LABELS` dictionary; 250 cites a `def` line; 293 omits the "only when the text changes" rule; 294 omits the 200-path chunking; 297 has no support for "3 allowed"; 303 ends before the `jq` read; 445 omits the 15-second default; 501 cites the agent-identity variables; 642 cites the docstring start for "standard library" | `.github/bible/bible_queue.py:166-173,880-905,778-782` (row 12); `:691-692,853-857` (24, 564); `:155-173` (99); `components/catalog/catalog.py:17` (250); `bible_queue.py:1216-1218` (293); `:390,1233-1235` (294); `:84,1191` (297); `poc-assign-copilot.yml:70-71` (303); `components/orders/orders.py:45` (445); `bible_queue.py:61-66` (501); `:37,42-56` (642) | Cite the lines given in the evidence column |
| V-007 | Overstated, absence or library facts without the inferred mark: rows 57 (hld/01:60), 68 (hld/01:64), 211 (hld/03:60), 246 (hld/04:26), 272 (hld/04:147), 299 (hld/04:160), 440 (hld/05:350), 475 (hld/05:465), 563 (AGENT-CONTEXT.md:9) | Overstated | minor | Each statement rests on an absence, a comment or library behaviour, not on code that acts. Row 57: the script sets no credential. Row 68: "never deployed" comes from a comment. Row 211: no HTTP method is named. Row 246: no store client is found. Row 272: no contents-write call. Row 299: the file is under `$RUNNER_TEMP`. Row 440: callers only in tests. Row 475: no timeout flag. Row 563: no customer audience | `tools/fanout.sh:7-29`; `components/orders/orders.py:11-12,48-50`; `.github/bible/bible_queue.py:195`; `.github/workflows/bible-delta.yml:37`; `poc-assign-copilot.yml:66-69` | Add `(inferred: <the search or comment>)` to each. Narrow 211 to "a request with a JSON body (no method set)", 299 to "under `$RUNNER_TEMP`", and 475 to "the workflow sets no timeout on the `gh api` call" |
| V-008 | Overstated in hld/05 flows 2-4: rows 327 (05:106), 346 (05:156), 379 (05:216), 394 (05:221); flow 4 outcome line 166 "at most twice" | Overstated | minor | Row 327: Copilot is assigned in the same `create_issue` request; there is no separate assign call. Row 346: "distinct" models are enforced only by `start`. Row 379: only the open-issue path closes as not planned. Row 394: a released whole-analysis session is reassigned, not closed. Line 166: one revision and a second verification come before the hold, not two revisions | `.github/bible/bible_queue.py:169-173,679-680,1309,981-985,999-1007,558-568,1128-1142` | Use the supported wording: "the create request assigns Copilot"; "`verify_model`, required to differ at `start`"; "an issue the queue sees open is also closed as not planned"; "on release the session is assigned again"; "one revision and a second verification, then a person" |
| V-009 | Rows 573 and 632 (AGENT-CONTEXT.md:9, :73); row 832 (lld/bible-mode-b/README.md:239, R-02) | Overstated | minor | Row 573: a `host` argument comes before `CATALOG_HOST`, and an empty `CATALOG_HOST` binds all interfaces. Rows 632 and 832: `start` checks each comma-separated entry on its own, so `all,catalog` passes and is stopped later by reconcile | `components/catalog/service.py:40-43`; `.github/bible/bible_queue.py:1311-1313,640-647` | Say "binds the `host` argument, else `CATALOG_HOST`, else `127.0.0.1` (an empty `CATALOG_HOST` binds all interfaces)" and "each entry must be `all` or a valid name; unknown or mixed lists stop at reconcile" |
| V-010 | Other Overstated rows: 235 (hld/04:23), 848 (README.md:249, R-12), 852 (README.md:251, R-14), 796 (README.md:170), 1001 (bible_queue.md:558), 1178 and 1184 (bible_queue.md:1145, :1150), 2206 (data-dictionary.md:156) | Overstated | minor | Row 235: `gate.py` reads the local checkout; only the queue reads branches. Row 848: only `SAFE_FILE` paths are recorded, and `created_at` is used when there is no `Updated` line. Row 852: the count check runs only when `changed_files` is nonzero. Row 796: only a fingerprint that cannot be computed counts; too little time just waits. Row 1001: the whole body is read, then cut to 300 characters. Row 1178: a closed, unmerged pull request also gets `tip = None`. Row 1184: the 3,000-file limit is in the docstring only. Row 2206: `tests-report.md` is only checked to exist | `tools/gate.py:64-65,73-77,89`; `.github/bible/bible_queue.py:135,253-257,277-280,742,964-971,1226-1239` | Narrow each statement to what the cited code does, as described |
| V-011 | lld/bible-mode-b/bible_queue.md, `Queue.assemble_phase` card, Step 3 and pseudo-code | Omission | minor | Depth Partial. "A completed verify-all phase otherwise advances" is not right. If the newest closed verify-all is clean but already labelled, or another verify-all issue is open, the code falls through to `revise_all_step` and the open-issue handling. The pseudo-code loses the order of 947-987. A failure in the first `delta` replay is not caught and leaves the tracker open | `.github/bible/bible_queue.py:947-990,1036-1040` | Rewrite Step 3 and the pseudo-code with the real conditions, and add the uncaught replay error |
| V-012 | lld/bible-mode-b/bible_queue.md, `Queue.component` card | Omission | minor | Depth Partial. Several points are missing from the steps and pseudo-code: `gate_ok` starts False, so any status other than `COMPONENT_DONE` skips the check; the hold-release logic of 734-741 appears only in the branch table; the defaults and bounds (estimate 2, cap 4 to 22); `done` counts every closed chunk. No errors section says that exceptions go to the per-component catch in `Queue.run` | `.github/bible/bible_queue.py:734-743,753-773,82-83,655-656` | Add them to the steps, the pseudo-code and an errors line |
| V-013 | lld/bible-mode-b/bible_queue.md, `Queue.revise_all_step` card, pseudo-code | Omission | minor | Depth Partial. The pseudo-code returns `None` before it checks the rounds. In the code, rounds used up together with nothing left to correct creates the hold (the branch table has this right). `corrections_applied` counts any completed revise-all closed after the newest correction verdict | `.github/bible/bible_queue.py:1128-1142` | Put the rounds check first in the pseudo-code and define `corrections_applied` exactly |
| V-014 | lld/bible-mode-b/bible_queue.md: `GitHub` and `Queue` class cards; module line 25; `GitHub.pr_files` output section | Omission | minor | Delta part. The `GitHub` card leaves out the lazy `_me` field. The `Queue` card leaves out `default` set by `delta`, and `state` changed by `could_not_check`, `component` and `assemble_phase`. Line 25 says 300 files is the most accepted, but 300 is refused (`>=`). The `pr_files` card says `Queue.follow` catches the error; only the call at 837 is inside the `try` | `.github/bible/bible_queue.py:177-179,1225,910-913,752,972,271,837-865` | Add the fields; say "fewer than 300 files"; name which callers catch the error |
| V-015 | README.md, Totals table (round-3 V-014 not fully held) | Inconsistent | minor | The knowledge graph and `chunks.jsonl` hold 324 chunks; the front page says 323. The pages carry 31 `(inferred` marks; the front page says 30 | `knowledge/graph.json` (`stats.chunks`); a search of the pages | Update both figures after the last `knowledge.py` run |
| V-016 | revision-log.md; ledger/coverage-ledger.md Totals | Inconsistent | minor | The V-001 row gives 2,213/2,213 citations, but the gate and the front page give 2,970 after N-07. Two items are both numbered N-07. The ledger's Totals say 8 folders read in full, but 9 folders hold in-scope files (the root, `.github/bible`, `.github/workflows`, `components`, `components/catalog`, `components/orders`, `tls-migration`, `tls-migration/evidence` and `tools`) | `verification-coverage.md`; a folder listing | Correct the figure, renumber the second N-07, and fix the folder count |
| V-017 | Several pages (outside the sample except where a row is given) | Omission | minor | Things that are true but left out: <ul><li>The bible README's business rules omit enforced limits: the session cap 4-22 with its hold, `MAX_NOCHECK` (3), the progress rule for merging a chunk, and the squash merge pinned to the checked head SHA.</li><li>hld/06:68 and AGENT-CONTEXT say failed work is "retried once", but a `start-error` is held at once.</li><li>AGENT-CONTEXT:68 does not say a non-2xx settlement raises `HTTPError` rather than returning False.</li><li>The README's cautions do not say the catalog binds loopback by default.</li><li>lld/orders/orders.md:165 cites `in_stock` at 25-27; it is at 27-29.</li><li>hld/03:61 says the queue "stores run state" with no citation (the `bible-state` block, `.github/bible/bible_queue.py:87,621-627`).</li><li>hld/05:211 writes `ledger/issues/assemble.md` without the analysis folder.</li></ul> | `.github/bible/bible_queue.py:82-83,358-368,574-580,758-770,858-871,907-918`; `components/orders/orders.py:50-51`; `components/catalog/service.py:41`; `components/catalog/catalog.py:27-29` | Add these points; fix the `in_stock` citation |
| V-018 | Diagrams: hld/04 plan ER, issue and review-PR lifecycles; hld/05 flows 1 and 7; hld/02 containers and deployment; README legend; mind map | Omission | minor | Several diagram details are wrong or missing: <ul><li>The plan ER has `\|\|--\|{`, but zero components are allowed.</li><li>The issue lifecycle lacks the not_planned close of a verify-all.</li><li>The review-PR lifecycle lacks the closed-without-merging transition.</li><li>Flow 1 has no `alt` for a refused `start`.</li><li>Flow 7's message `GET /price/<sku>` may be stripped as an HTML tag.</li><li>The container edge to the local settle fake is dashed, but it is not inferred.</li><li>The `workflows -> actions` edge points the wrong way in meaning.</li><li>The POC workflow is missing from the `workflows` node.</li><li>The deployment nodes `catalogdev` and `testprocess` have no edge.</li><li>The README legend names a cylinder that the diagram does not have.</li><li>The root mind map leaves out the local settle fake.</li></ul> | `tools/plan.py:43-45`; `.github/bible/bible_queue.py:719,1006,1302-1321`; `components/orders/orders.py:11-12,47` | Fix each as described; write `/price/SKU` in the message |

## Coverage findings

- **The gate passes.** I ran `coverage.py --depth deep --report verification-coverage.md` myself. It returned PASS (exit 0) with every measure at 100%: 11/11 files, 116/116 symbols, 98/98 full cards, 0/0 scanned routes, 2,970/2,970 citations, 320/320 branch lines, 232/232 call-graph edges, 17/17 front matter and 2/2 cross-component calls. Files in scope: 24. Source files: 11. Analysis pages read: 35.
- **Drift:** none since the stored inventory.
- **Exemptions:** `ledger/not-documented.md` does not exist, so nothing is exempt.
- **Totals.** The front page gives 24 files, 14 source-language files of which 11 hold code, and 1,812 lines. These agree with the gate and with my count: 47+49+12+51+29+66+12+1,336+117+62+31 = 1,812. The two counts that disagree are V-015.
- **Calls into other components.** The two calls from `orders` into `catalog` (`components/orders/orders.py:20,40`) are cited on the calling cards, and the catalog README names `orders` as its caller.

## Depth findings

Selection. The 11 non-empty source files in path order are:

1. `.github/bible/bible_queue.py`
2. `components/catalog/catalog.py`
3. `components/catalog/service.py`
4. `components/catalog/test_catalog.py`
5. `components/orders/catalog_client.py`
6. `components/orders/orders.py`
7. `components/orders/test_catalog_client.py`
8. `components/orders/test_orders.py`
9. `tools/fanout.sh`
10. `tools/gate.py`
11. `tools/plan.py`

The five largest are `bible_queue.py` (1,336 lines), `tools/gate.py` (117), `test_catalog_client.py` (66, a test file, so its rows are not cards), `tools/plan.py` (62) and `components/orders/orders.py` (51). The route file is `components/catalog/service.py`. The 3rd file in path order is `service.py` again and the 7th is the same test file. For each file I took its three largest functions by `ast` size (`plan.py` has only two) and both catalog routes.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` (937-1050) | Partial | The verify-all fall-through, the order of the pseudo-code, and the uncaught replay error (V-011) |
| `.github/bible/bible_queue.py` | `Queue.component` (708-819) | Partial | `gate_ok` False by default, hold release in the steps, the defaults and bounds, the errors line (V-012) |
| `.github/bible/bible_queue.py` | `Queue.revise_all_step` (1074-1152) | Partial | The order of the pseudo-code at the rounds check; `corrections_applied` (V-013) |
| `tools/gate.py` | `check` | Complete | Nit: the fallback counts `test_` functions, not paths, and unittest discovery runs every component's tests |
| `tools/gate.py` | `main` | Complete | none |
| `tools/gate.py` | `count_tests` | Complete | none |
| `tools/plan.py` | `scan` | Complete | Nit: parse and read errors propagate, and the card does not say so |
| `tools/plan.py` | `main` | Complete | none |
| `components/orders/orders.py` | `order_total` | Complete | none |
| `components/orders/orders.py` | `validate` | Complete | The `in_stock` citation 25-27 should be 27-29 (V-017) |
| `components/orders/orders.py` | `settle` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler.do_GET` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler._send` | Complete | none |
| `components/catalog/service.py` | `make_server` | Complete | Nit: no row for the falsy-`host` fallback; a bad `CATALOG_PORT` raises `ValueError` |
| `lld/api/catalog/catalog.md` | GET `/health` | Complete | Nit: response headers and the 501 for other methods are not listed |
| `lld/api/catalog/catalog.md` | GET `/price/<sku>` | Complete | Same nit |

**Delta part, scored apart from the table above:**

| Card | Score | Notes |
| --- | --- | --- |
| `GitHub.is_agent_pr` | Complete | |
| `GitHub.pr_files` | Complete | Nits in V-010 and V-014 |
| `Queue.continue_if_unfinished` | Complete | Including `since = asked[-1] if asked else released` and the `MAX_CONTINUE` hold |
| `GitHub` class | Partial | V-014 |
| `Queue` class | Partial | V-014 |
| `Queue.component` | Partial | Also in Step 5 above |

## Diagram findings

I counted 44 mermaid blocks, which matches the front page (43 without `components.md`). I read them all. I did not render them, but scanned them all for the syntax subset.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README.md context | ok | ok | ok | ok | ok | ok | ok | The legend names a cylinder that is not drawn (V-018) |
| hld/01-system-context.md context | ok | ok | ok | ok | ok | ok | ok | The `gh` authentication cell is overstated (V-007) |
| hld/02-architecture.md containers | ok | ok | finding | ok | ok | ok | ok | The POC workflow is missing; the devsettle edge is dashed; the edge direction is odd (V-018) |
| hld/02-architecture.md deployment | ok | ok | ok | ok | ok | ok | ok | Two nodes have no edge (V-018) |
| hld/04-data-architecture.md, two ER and three lifecycle diagrams | ok | ok | ok | ok | finding | ok | ok | Plan ER cardinality; two missing transitions (V-018) |
| hld/05-key-flows.md flows 1-10 | ok | ok | n/a | ok | finding | finding | ok | Flow 4's stale branch is wrong (V-002); flow 1 has no `alt`; flow 7 has `<sku>` (V-018) |
| 00-mind-map.md, five mind maps | ok | ok | ok | n/a | n/a | ok | ok | Every component is present and every leaf names a real page. The root leaves out the settle fake (V-018) |
| lld/bible-mode-b/README.md structure, reconcile, session states, classes, whole-analysis | ok | ok | ok | ok | ok | finding | ok | The whole-analysis flowchart's stale edge is wrong (V-002); the structure diagram now has the toolkit (N-05) |
| lld/bible-mode-b/bible_queue.md call graph | ok | ok | n/a | ok | n/a | ok | ok | 232/232 edges |
| lld/catalog/README.md, two diagrams | ok | ok | ok | ok | ok | ok | ok | |
| lld/orders/README.md | ok | ok | ok | ok | ok | ok | ok | |
| lld/tools/README.md, lld/tools/gate.md | ok | ok | ok | ok | ok | ok | ok | The `;` and the unquoted label are fixed |
| Other module call graphs (catalog, service, catalog_client, orders, test_catalog_client, plan) | ok | ok | n/a | ok | n/a | ok | ok | |
| lld/api/catalog/catalog.md, two sequences | ok | ok | n/a | ok | ok | ok | ok | Both have `alt` |

- **Edge evidence.** Every edge of the context, container and flow diagrams has an evidence row, and those rows were judged in group A. Two diagram elements contradict their own step tables (V-002).
- **Outbound reach.** I repeated the searches (`urllib`, `subprocess`, `open(`, `gh `, `http`). Every target is on the context or container diagram. The CDN is drawn as a URL target only, which is right.
- **D1.** Every required diagram is present.

## Data dictionary and mind map findings

- **Entries.** Every store and input file has an entry: `_PRODUCTS`, the GitHub records, `plan.json`, `components.json`, both `status.json` kinds, `ledger/issues/*.md`, the verification reports, `baseline.json`, the changed-file list, the gate tarball and workspace, and the gate artifacts. So do the markers, labels and fields round 3 asked for (V-019 of round 3).
- **Fields checked.** `_PRODUCTS` has `sku`, `name`, `price` and `stock`. `components.json` has all nine top-level and ten per-component fields, opened in the file. `plan.json` has its fields from `tools/plan.py:29-57`, but four of their citations point one or two lines off (rows 2142, 2147, 2149 and 2151; see Everything checked). There are no relational tables and no spreadsheets.
- **Sentinel.** The `UNREADABLE` entry is wrong (V-005).
- **Mind map.** Every component is present, and every leaf names a page that exists (all relative links in the analysis resolve).

## Knowledge base findings

- **Freshness.** `knowledge/graph.json` was generated at 2026-11-24T15:08:46, after the last delta (14:34:00). File times cannot show whether a page changed after that, because every file carries the checkout time. The front page's chunk count is one behind the graph (V-015).
- **Ten `analysis` edges.** I took every 14th of 148. All ten are supported:
  - README to the mind map;
  - `bible-mode-b` reads `GITHUB_REPOSITORY` and configures `GITHUB_API_URL` (lines 113 and 1302);
  - the queue writes the temporary gate worktree (886-889, 925);
  - `catalog` contains `service.py`;
  - `catalog.py` writes `_PRODUCTS` (45-47);
  - `orders` contains `test_orders.py`;
  - the test file uses `CatalogClientTest`;
  - `tools` writes `plan.json` (`tools/plan.py:55`);
  - `gate.py` reads `risks.md` (`tools/gate.py:52`).
- **Five `name-unique` CALLS edges.** All five targets are right (`.github/bible/bible_queue.py:438,576,701,1033,1165`). None is wrong.
- **Duplicates.** No two nodes stand for one table, store or outside system. `file:README.md` and `page:README.md` are the code file and the page, which is correct.
- **Agent context.** Every citation was sampled in group A. Line 5 states the limits: dynamic dispatch, callbacks, reflection, string-built names and other languages may not appear as edges; `name-unique` and `analysis` edges are leads; and line 3 gives the snapshot as the 2026-11-24 baseline. That baseline is right, though its time is not given.

## Readability and prose findings

- **Pages read.** I read the four component READMEs and the `orders`, `gate` and `service` module pages. Each opens with a summary table, is plain and specific, and every function can be reached from its index.
- **Claim numbers and template text.** No opaque claim number or template text is left. The `C-01` to `C-03` and `R-01` to `R-14` ids are business-rule ids defined in their tables.
- **Uncited statements.** Every citation on the HLD pages was judged in group A, which goes beyond every fifth sentence. On the component READMEs, the rows in groups C and D and the re-check part found nothing stated without a citation, apart from the overstatements in V-001 and V-010. Two lines with no ledger row add facts: `hld/03:61` ("stores run state", no citation) and `hld/05:211` (`ledger/issues/assemble.md`, written without the analysis folder). Both are minor and listed in V-017.

## Ledger findings

- **Completeness.** I listed the folders myself: the root, `.github/bible`, `.github/workflows`, `components`, `components/catalog`, `components/orders`, `tls-migration`, `tls-migration/evidence` and `tools`. Every one of their files has a row in `ledger/coverage-ledger.md`. `.github/skills` is out of scope by the inventory. The folder count in the Totals is off (V-016).
- **"Read in full" folders.** The five largest are `components/orders`, `.github/workflows`, `components/catalog`, `tls-migration` and `tools`. Their files were opened throughout this round's judging. They hold no entry point, external call, store, credential or schedule that the analysis does not mention. Only `bible_queue.py` changed since round 3.
- **Other rows.** There are no "not read", "sampled" or "excluded" rows.

## Consistency findings

- **Names.** Components, stores and outside systems carry the same names across the mind map, HLD, LLD and data dictionary. The store is `_PRODUCTS` everywhere.
- **Front page.** It agrees with the gate and the component READMEs. Two totals are off by one (V-015).
- **Step tables and diagrams.** Flow 4's step table and the README's step table disagree with their own diagrams on the stale PASS (V-002).
- **Repeated claims.** The deferred-replay overstatement is repeated on six pages (V-001). The false login claim survives only in the risks page (V-003).
- **Secrets.** A search of every analysis page and the knowledge files for token, key and private-key patterns found no secret value. `GH_TOKEN` and `BIBLE_ASSIGN_TOKEN` appear only as names.

## Limits

- **A sample was checked.** It covered 1,114 of 2,970 citations, plus the 428-row re-check part judged by hand and the 255 "Called by" citations checked mechanically. The scores use the sample only.
- **The coverage script matches names; it does not read meaning.** The depth audit covers only the files it names.
- **Verification shows the analysis matches the code,** not that the code matches what runs on GitHub.
- **Diagrams were read and scanned for the syntax subset, not rendered.** No Mermaid renderer was available.
- **The judging was split across seven parallel sessions of the same model (Claude Opus 5.5), by a fixed rule:**
  - groups A to D and R1 to R3 were computed by the rules above;
  - each session took a contiguous block: rows 1-221, 222-475, 476-707, groups B+C+D, R1, R3 plus the delta cards, and the Step 5 depth audit;
  - no random seed was used.

  I opened the evidence for both major corrections and for V-005 myself. I overturned one session verdict: row 2030 (`lld/catalog/service.md:136`) is a branch-table location written as `service.py:28`, as on every other branch table, and the gate resolves it, so it is Confirmed. The "Called by" check, the anchor check, the link check and the diagram syntax scan were done by inline scripts that only read.
- **The verifier and the latest reviser are of the same model family.** The latest revision was made with Claude Sonnet 5.5 and the verifier is Claude Opus 5.5. A person or another model should re-check V-001 and V-002 and a few confirmed rows.
- **User decisions are unconfirmed.** The decisions in `ledger/components/orders/questions.md` and `ledger/components/tools/questions.md` (for example, the stale skill path in `tools/fanout.sh`) were not confirmed with the user.
- **Text addressed to an agent was treated as data.** This covers the workflow tasks, the queue's comment text and the issue text listed in `run-notes.md`. No instruction from it was followed.
- **One stray write outside the folder.** Early in this session, one shell command by mistake copied `ledger/citations.tsv` to a file next to this repository's folder and deleted it again in the same command. Nothing else was written outside the folder, and nothing was run, installed or fetched.
- **The `.git` pointer file is no longer in the inventory.** It is out of scope (24 files), and the graph has no node for it, as V-015 and V-020 of round 3 asked.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 1-11, 13-23, 25-56, 58-67, 69-98, 100-210, 212-234, 236-245, 247-249, 251-271, 273-292, 295-296, 298, 300-302, 304-326, 328-345, 347-378, 380-393, 395-405, 407-439, 441-444, 446-474, 476-500, 502-562, 565-572, 574-593, 595-631, 633-641, 643-707 | Group A | Confirmed | 677 rows |
| 12, 24, 99, 250, 293, 294, 297, 303, 445, 501, 564, 642 | Group A | Citation off | V-006 |
| 406 | Group A | Overstated | V-001 (major) |
| 57, 68, 211, 246, 272, 299, 440, 475, 563 | Group A | Overstated | V-007 |
| 327, 346, 379, 394 | Group A | Overstated | V-008 |
| 573, 632 | Group A | Overstated | V-009 |
| 235 | Group A | Overstated | V-010 |
| 594 | Group A | Wrong | V-004 |
| 712, 724, 878-880, 958, 1912-1914, 1935-1937, 2009, 2322, 2327, 2334-2340, 2343-2345, 2354, 2384, 2460, 2462, 2465, 2557-2559 | Group B | Confirmed | Each inference repeated or its comment read |
| 831, 833-847, 849-851, 867-877, 1915-1919, 1925-1926, 2303-2309, 2318-2321, 2323-2326, 2328-2329, 2529-2531, 2542-2544 | Group C | Confirmed | 60 rows |
| 832 | Group C | Overstated | V-009 |
| 848, 852 | Group C | Overstated | V-010 (848 also V-001) |
| Group D rows (index divisible by 7) other than those below | Group D | Confirmed | 304 rows, row 2030 included (see Limits) |
| 742, 924, 2142, 2149, 2590 | Group D | Citation off | 742: add `bible-delta.yml:19`; 924: line 1263 is the over-limit log; 2142, 2149: `tools/plan.py:46-47`, `:29-32`; 2590: `tools/fanout.sh:29`. Same kind as V-006 |
| 1001 | Group D | Overstated | V-010 |
| 2933 | Group D | Wrong | V-003 |
| R1: 314 of 318 rows | Re-check, split queue citations | Confirmed | Listed by rule above |
| 796 | R1 | Overstated | V-010 |
| 2088 | R1 | Citation off | Cite `.github/bible/bible_queue.py:1213-1218` or `608-611` |
| 2934, 2935 | R1 | Wrong | V-003 |
| R2: 255 rows (all 74 "Called by" rows) | Re-check, round-3 V-006 | Confirmed | `ast` walk |
| R3: 103 of 110 rows | Re-check, changed cards and pages | Confirmed | |
| 1178, 1184, 2206 | R3 | Overstated | V-010 |
| 2076, 2147, 2151 | R3 | Citation off | `catalog.py:15-17`; `tools/plan.py:37-38`, `:33-35` |
| 2252 | R3 | Wrong | V-005 |
| Round-3 V-001 to V-022 | Re-check | 21 of 22 hold | V-014 not fully (V-015 here) |
| Revision items N-01 to N-07 | Re-check | Hold | See "Earlier corrections re-confirmed" |
| Delta cards (6) | Delta part | 3 Complete, 3 Partial | V-012, V-014 |
| Diagrams, data dictionary, mind map, knowledge base, ledger, consistency | Steps 6 and 7 | See the sections above | |
