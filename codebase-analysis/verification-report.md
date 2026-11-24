# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Analysis fingerprint | 70ed8b41d4d54c72 |
| Analysis snapshot | 24 in-scope files, 1,812 source lines, code of 2026-11-24 (baseline 2026-11-24T14:34:00), no version given (front page) |
| Repository at verification | 24 files in scope, 14 source-language files of which 11 hold code (3 empty `__init__.py`), 1,812 lines by my count; `.github/bible/bible_queue.py` has 1,336 lines; no drift from the stored inventory; no version given |
| Depth stated / depth found | deep / deep |
| Verified with | Claude Code (Claude Opus 5.5), standing in for the GitHub Copilot coding agent |
| Analysis produced with | Copilot coding agent (model not recorded) for planning, components, assembly and the first revisions; Claude Sonnet 5.5 standing in for Copilot for the revisions of 24 Nov 2026, including the round-4 revision (front page) |
| Sampling level | standard, plus the re-check part (every statement the round-4 report flagged and every page section the round-4 revision changed) |
| Date | 2026-11-24 |

After corrections: every flagged statement re-checked: 14 of 18 confirmed.

The 18 are V-001 to V-018 of the round-4 report (now `verification-report-2026-11-24-2.md`). V-001, V-014, V-017 and V-018 do not fully hold: part of the rewritten text is still not what the code does (V-001, V-003, V-002 and V-012 here). Round 5. No delta was applied since round 4 (`delta-log.md`'s newest row, 2026-11-24T14:34:00, was already audited then), so there is no delta part. Steps 1 to 8 of the skill were all done.

## Summary

The analysis is complete and, for its main statements, true. The coverage gate passes at deep with every measure at 100% (116/116 symbols, 98/98 full cards, 320/320 branch lines, 232/232 call-graph edges, 3,059/3,059 citations). The round-4 revision fixed both majors: the deferred-update replay is now described as happening only through the Done step, and both whole-analysis diagrams split the stale-PASS branch from the corrections branch. No correction in this report is major, no omission is significant, and no secret value appears.

It is not a PASS because accuracy is 92.3%, below the 95% a PASS needs. Of the 1,174 sampled citations, 1,072 are confirmed, 12 cite the wrong lines, 89 are overstated and 1 is wrong. Most of the overstatements are one kind of slip. A statement rests on an absence ("no retry", "no scheduler", "never replayed"), a comment or library behaviour, but carries no `(inferred` or `(assumed` mark, although the pages use those marks elsewhere. The facts behind them are almost always right.

This round applied the mark rule of the skill strictly to every sampled row. Round 4 confirmed several of these same unchanged statements (for example the "no retry" cells of `hld/03`). So the fall in accuracy from 97.9% is mainly a stricter reading, not new errors in the pages.

Where the analysis is weakest:

- **Text the revision wrote.** The new wording that recorded paths "must be updated by hand" goes past the code: a later update session of the same component covers every change since the baseline. The new rule R-15 counts chunk sessions created since the hold release, not sessions closed since then. The `pr_files` output section now says an error ends the tracker's run, but the per-component handler catches it. The new flow 1 `alt` puts "ensure labels" after the refusals, but the code ensures them first.
- **`Queue.component`.** The card still misses the run scope of "not started" and one condition of the revision trigger.
- **Two small wrong statements.** Answers go on the session pull request, not on the waiting issue. The `bible-run-<n>` label is on child issues, not on the tracker.
- **Diagram syntax.** Several departures from the toolkit's subset: underscore ids, unquoted ER labels, a rhombus, end states without `[*]`, and 53 duplicate edges in one call graph.

Every problem has a specific correction below. After they are applied, one re-check should be enough for a PASS.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 116 / 116 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 98 / 98 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 320 / 320 (100.0%); 232 / 232 (100.0%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner; the two catalog GET routes have endpoint cards (`lld/api/catalog/catalog.md`) |
| Citations that resolve | 3059 / 3059 (100.0%) |
| Coverage gate | PASS (depth deep); calls into other components 2 / 2 |
| Citations in the analysis / checked | 3059 / 1174 sampled; plus 879 re-check rows judged outside the sample |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 1072 / 12 / 89 / 1 / 0 (sample only) |
| Omissions (significant) / Inconsistent | 22 (0) / 27 |
| Accuracy / citation quality | 92.3% (1084/1174) / 91.3% (1072/1174) |
| Cards audited: Complete / Partial / Shallow / Wrong | 14 / 2 / 0 / 0 |
| Depth / depth, usable | 87.5% / 100.0% |

Re-check part, outside the scores: 879 rows, of which 847 are Confirmed, 9 Citation off, 22 Overstated and 1 Wrong.

## How the sample was selected

The level is `standard`. The rows come from `ledger/citations.tsv` as `coverage.py` rewrote it in this session: 3,059 rows, unchanged byte for byte from the copy the revision left.

- **Group A (746 rows: 1-746).** Every citation on `README.md`, `hld/*` and `knowledge/AGENT-CONTEXT.md`.
- **Group B (33 rows).** Every row labelled `inferred`: 751, 764, 940-942, 1022, 1988-1990, 2012-2014, 2086, 2407, 2412, 2419-2425, 2428-2430, 2439, 2469, 2545, 2547, 2550, 2642-2644. No row is labelled `assumed`.
- **Group C (80 rows).** Every other row whose nearest heading or bold title line above it contains rule, outbound, calls out, integration, security, secret, auth or permission. The rows are 876-914, 929-939, 1992-1996, 2002-2003, 2388-2394, 2403-2406, 2408-2411, 2413-2414, 2614-2616 and 2627-2629. All of them fall under "Business rules" (54) or "Outbound calls" (26).
- **Group D (315 rows).** Every remaining row from 747 to 3059 whose index is divisible by 7.

**Re-check part (879 rows), reported separately and not in the scores.** It covers every row outside the sample that lies in a place the round-4 report flagged or the revision changed. It has two parts.

- **Whole pages:**
  - `lld/bible-mode-b/README.md`;
  - `lld/data-dictionary.md`;
  - `lld/catalog/service.md`;
  - `lld/catalog/README.md`;
  - `lld/api/catalog/catalog.md`;
  - `lld/tools/fanout.md`;
  - `reference/configuration.md`;
  - `reference/risks-and-surprises.md`;
  - `ledger/coverage-ledger.md`;
  - `revision-log.md`;
  - `progress.md`.
- **Page line ranges:**
  - on `lld/bible-mode-b/bible_queue.md`:
    - module text, lines 1-111;
    - the `GitHub` class card, lines 473-505;
    - `GitHub.call`, lines 543-585;
    - `GitHub.pr_files`, lines 1131-1191;
    - the `Queue` class card, lines 1517-1545;
    - `Queue.component`, lines 1971-2042;
    - `Queue.assemble_phase`, lines 2212-2302;
    - `Queue.revise_all_step`, lines 2369-2425;
    - `Queue.delta`, lines 2522-2572;
    - Surprises, lines 3048-3056;
  - `lld/tools/gate.md` `check` (187-258);
  - `lld/tools/plan.md` `scan` (57-112);
  - `lld/orders/orders.md` lines 147 and 165.

The HLD pages, the front page and the agent context were rewritten too, but they are all in group A already.

## Earlier corrections re-confirmed

| Round-4 item | Holds? | Re-opened |
| --- | --- | --- |
| V-001 deferred-update replay (major) | **No, not fully.** The facts now hold: the paths are read only at lines 1038 and 1043, `reconcile` lists open trackers only (607), and the replay order is right. But the wording the revision used in all six places, "never replayed … must be updated by hand" (and "lost" on hld/05:274), overstates. A later update issue for the same component asks for "every change since the analysis's baseline (not only these files)". The wording also rests on an absence without a mark (V-001 here) | `.github/bible/bible_queue.py:607,1036-1064,1265-1282` |
| V-002 stale-PASS branch (major) | Yes. Both diagrams now have the two branches. "Corrections asked" leads to `bible-needs-revision` and then revise-all. "PASS about other pages, or not by this run" leads to `bible-stale-verdict` and then the next verify-all. The step tables agree | `.github/bible/bible_queue.py:975-985,1089-1094,1132-1142` |
| V-003 risk 8 | Yes. It now names the `Queue.session` docstring, and the login clause is gone | `.github/bible/bible_queue.py:36,61,518,521-522` |
| V-004 module name | Yes: `components.catalog.catalog` | `components/orders/orders.py:5` |
| V-005 `UNREADABLE` | Yes. `None` is returned for a missing or empty report, and `UNREADABLE` for the row count | `.github/bible/bible_queue.py:470-478,797` |
| V-006 twelve citations and the listed others | Yes. The re-pointed rows are confirmed in groups A, D and R, among them the `bible-delta.yml:19` row, the `tools/plan.py` field rows and the `bible-settings` read at 608-611. The logging paragraph now names line 1263, but it also cites 1245 without describing it (V-011 here, a new row) | as listed in revision row R4-V-006 |
| V-007 nine absence statements | Yes. All nine carry `(inferred: …)` and I repeated the searches. The same unmarked claims survive in other places that round 4 did not name (V-008 here) | `tools/fanout.sh:7-29`; `components/orders/orders.py:11-12,45-51`; `.github/workflows/poc-assign-copilot.yml:66-69` |
| V-008 flows 2-4 wording | Yes. The create request assigns Copilot, `verify_model` must differ at `start`, and the not-planned close, the reassignment on release and "one revision and a second verification" all match the code | `.github/bible/bible_queue.py:169-173,558-568,679-680,981-985,999-1007,1128-1142,1309-1310` |
| V-009 bind address and component selection | Yes, in AGENT-CONTEXT, R-02, `service.md`, the catalog README and `configuration.md`. The empty `CATALOG_HOST` case is marked assumed | `components/catalog/service.py:40-43`; `.github/bible/bible_queue.py:640-647,1311-1313` |
| V-010 narrowed statements | Yes. The gate reads the local checkout; only `SAFE_FILE` paths are recorded; the count check runs only for nonzero `changed_files`; only an uncomputable fingerprint counts; the 300-character cut; the closed, unmerged pull request; the docstring-only 3,000 limit; `tests-report.md` only checked to exist | `tools/gate.py:64-65,89`; `.github/bible/bible_queue.py:132-136,252-286,920-933,964-972,1226-1242` |
| V-011 `Queue.assemble_phase` | Yes. The card is now Complete: eight steps in code order, the fall-through, and the uncaught first replay | `.github/bible/bible_queue.py:937-1050` |
| V-012 `Queue.component` | Yes for every point listed: `gate_ok` starting False, the hold release, the defaults and bounds, `done`, and the Errors paragraph. The card is still Partial for two points round 4 did not name (V-004 here) | `.github/bible/bible_queue.py:708-819` |
| V-013 `Queue.revise_all_step` | Yes. The rounds check comes first and `corrections_applied` is defined exactly; the card is Complete | `.github/bible/bible_queue.py:1074-1152` |
| V-014 class cards, line 25, `pr_files` output | **No, not fully.** `_me`, `default`, `state` and "fewer than 300" hold. But the `pr_files` output section now says the uncaught errors of `follow`'s later calls end the tracker's run. They are caught by the per-component handler in `Queue.run` (V-003 here) | `.github/bible/bible_queue.py:177-179,271,653-656,837-865` |
| V-015 front-page counts | Yes. My counts agree with the front page: 41 `(inferred` and 10 `(assumed` marks, 31 business rules, 44 diagrams (43 without `components.md`), and 211 nodes, 566 edges and 336 chunks, the same as `knowledge/graph.json` and the 336 lines of `chunks.jsonl`. A different count on the same page, "3 stores", is off (V-014 here) | `knowledge/graph.json` stats; a search of the pages |
| V-016 revision log and ledger | Yes. The IDs are unique (`R4-`, `R3-`, `R2-`), and the ledger gives 9 folders and 24 files, which is my own count | `ledger/coverage-ledger.md`; `ledger/inventory.json` |
| V-017 omissions | **No, not fully.** R-16 to R-18, the R-04 start-error hold, the hld/06 "retried once" exception, rule 10, the catalog loopback sentence, the `in_stock` citation, the `bible-state` citation and the `assemble.md` path all hold. R-15 is overstated: it counts closed chunk issues created since the later of the hold release and the merge, not sessions closed since then (V-002 here) | `.github/bible/bible_queue.py:754-761` |
| V-018 diagram details | **No, not fully.** These hold: the plan ER `\|\|--o{`, the not-planned and `ClosedUnmerged` transitions, the flow 7 message `GET /price/SKU`, the solid settle-fake edge, the `actions` to `workflows` direction, the POC workflow node, the deployment edges, the README legend and the root mind map. Two do not. The new flow 1 `alt` draws "ensure labels" only in the accepted branch, but the code ensures labels before two of the refusals. The orders mind map has the settle fake, but the nested list on the same page does not (V-012, V-014 here) | `.github/bible/bible_queue.py:1314-1321`; `00-mind-map.md` |

The revision's own items R4-N-01 to R4-N-05 hold: the `check` test-count fallback, the `scan` errors, the `make_server` rows, the endpoint headers and 501, and the `progress.md` figures. In R4-N-01, the phrase "finds every `test_*.py` under ROOT" is unittest discovery behaviour stated without a mark (row 2741, V-009). R4-N-06 records limits only.

## Corrections

Every correction is minor; none is major.

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | Rows 312-317 (hld/04:161), 436-438 (hld/05:267), 845-847 (lld/bible-mode-b/README.md:173), 848-849 (README:175), 896-901 (README:250, R-12). Outside the rows, the same wording is at hld/05:233 and :274 ("is lost"), the data dictionary marker row and the `assemble_phase` and `delta` cards | Overstated | minor | That the paths are never replayed without the Done step is right. But the paths are not lost and need not be updated by hand: an update issue for the same component asks its session for "every change since the analysis's baseline (not only these files)". The statement also rests on an absence (no other caller of `deferred_updates`) without a mark. And the writer side leaves out the 14-day limit: a tracker whose `Updated` line is older than `ABANDONED_AFTER` does not defer | `.github/bible/bible_queue.py:391,607,1036-1064,1229,1273-1277` | Say: "never replayed if a person closes the tracker or the run does not finish (inferred: `deferred_updates` is called only at lines 1038 and 1043, and `reconcile` lists open trackers only). Those paths get no update issue of their own; a later update session of the same component, which covers every change since the baseline, or a person picks them up." Add "and its tracker was updated in the last 14 days" to the writer column. Use it everywhere the old phrase appears |
| V-002 | Rows 904-905 (lld/bible-mode-b/README.md:253, R-15) | Overstated | minor | The cap counts closed chunk issues of this run whose `created_at` is at or after `max(hold release, merge into the default branch)`, not sessions closed since then. The estimate and cap bounds are right | `.github/bible/bible_queue.py:754-761` | "at most a bounded number of closed chunk sessions created since the last hold release or merge into the default branch …" |
| V-003 | Row 1263 (lld/bible-mode-b/bible_queue.md:1190, `GitHub.pr_files` output) | Overstated | minor | Only the call at 837 is inside `follow`'s `try`. That part is right. But an error from the calls at 843, 846 and 865 does not end the tracker's run: `Queue.run` catches it per component, writes "error this run", and goes on with the other components. The page's own `Queue.component` Errors paragraph (line 2041) says so. This is also an Inconsistent between the two cards | `.github/bible/bible_queue.py:653-656,837-865` | "errors from the later calls are caught by the per-component handler in `Queue.run` (653-656); only errors from `assemble_phase`, `revise_all_step` and `continue_if_unfinished` reach `reconcile` (612-615)" |
| V-004 | Rows 1538 (bible_queue.md:1985), 1554 (:2027), 1533 (:1968), 1544 (:1989); also `start_chunk` step 2 and pseudo-code (:1949, :1958), outside the rows | Overstated | minor | "Not started" and the branch reset look only at issues of this run, because `run_issues` adds `self.run_label`. The revision chunk also needs `not chunk_since_verify`. This gap is why the card is still Partial | `.github/bible/bible_queue.py:505-506,700,732,806` | Say "no issue of this run (label `bible-run-<n>`) with the component label, in any state". Add "and no chunk session completed since the latest verification" to step 6 |
| V-005 | Row 53 (hld/01:58); the reviewer edge "reviews PRs and answers issues" in the context diagrams of README.md and hld/01 | Wrong | minor | Questions are answered on the session pull request with `@copilot`. The waiting label goes on both, but the state text and the label description point to the PR | `.github/bible/bible_queue.py:103,853-857` | "supplies answers on the session pull request (`@copilot`)". Label the edge "reviews PRs and answers on session PRs" |
| V-006 | Row 2235 (lld/data-dictionary.md:135, "Tracker issue labels") | Wrong | minor | The tracker is created with `bible-tracker` only. `bible-run-<n>` is put on its child issues | `.github/bible/bible_queue.py:620,680,705,1034,1322` | "Tracker: `bible-tracker`. Every child issue: `bible-run-<tracker number>`" |
| V-007 | Row 278 (hld/04:112); the `fail` edge of the issue lifecycle | Overstated | minor | Only a first failure closes the issue as not planned and opens attempt 2. A second failure leaves it open, labelled `bible-needs-human`, unassigned and commented | `.github/bible/bible_queue.py:584-596` | "A first failed attempt closes as `not_planned` and an attempt-2 issue is created; a second failure stays open, labelled `bible-needs-human` and unassigned." Label the edge "first failure" |
| V-008 | Absence, comment or library statements without a mark, on the front page, HLD and agent context: rows 4-9 (README:23), 62-66 (hld/01:61), 76-79 (hld/01:67), 130-131 (hld/02:120), 183-185 (hld/03:33), 192-193 and 197-207 (hld/03:42-48), 464 (hld/05:351), 565-570 (hld/06:71), 615 (AGENT-CONTEXT:9), 632-633 (:38), 678-681 (:88), 686-688 (:90), 711-718 (:98), 728 (:104), 731-733 (:106), 738 (:109) | Overstated | minor | Each fact holds, but it rests on a search, a docstring or library behaviour:<ul><li>Callers only in tests.</li><li>No direct Copilot call.</li><li>An OS-chosen port.</li><li>`gh`'s own credential.</li><li>No retry (hld/03 rows, hld/06:71, AGENT-CONTEXT:98, :106).</li><li>The `gh api` call has no timeout of its own (hld/03:48 repeats the wording round 4 fixed on hld/05).</li><li>`urlopen` with no body is a GET.</li><li>No order store.</li><li>A separately deployed service (docstring).</li><li>No package or deployment manifest.</li><li>No metrics.</li><li>No scheduler.</li><li>A skill folder that is missing.</li></ul> | `components/orders/catalog_client.py:1-4,19-23`; `components/orders/test_catalog_client.py:15-17,37-54`; `tools/fanout.sh:7-29`; `components/catalog/catalog.py:36-39`; `components/orders/orders.py:45-51`; `.github/bible/bible_queue.py:116-139,166-173,297`; `.github/workflows/poc-assign-copilot.yml:66-69`; repository searches | Add `(inferred: <the search, comment or docstring>)` or `(assumed: library behaviour)` to each. As a model, hld/01:60 already has one. For hld/03:47 also say "a failed component is tried again at the next queue run" (`bible_queue.py:653-656`). For hld/03:48, use "the workflow sets no timeout option on the `gh api` call (inferred)" |
| V-009 | The same kind of row in the LLD and reference pages: rows 1242, 1243, 1245, 1246 (bible_queue.md:1145-1148, GitHub's compare behaviour from comments at 71, 257, 261-264); 1948 (lld/catalog/README.md:28); 2023-2025 (catalog README:157, marked on :105 but not here); 2128-2129 (service.md:205, `int` raises `ValueError`); 2307-2311 (data-dictionary:165); 2741 (lld/tools/gate.md:214 and its pseudo-code, unittest discovery); 3016, 3023, 3028 (reference/risks-and-surprises.md:16, :18, :21) | Overstated | minor | Each rests on a comment, a library or builtin behaviour, or an absence across a file or component, and has no mark | `.github/bible/bible_queue.py:71,116-125,257,261-264,653-656`; `components/catalog/service.py:24-43`; `tools/gate.py:73-75`; `tools/fanout.sh:14`; `components/catalog/catalog.py:36-37` | Add the mark with its source to each. For risk 21, use: "no retry inside a GitHub request (inferred); a component that raises is tried again on the next scheduled run" |
| V-010 | Row 2205 (lld/data-dictionary.md:112, pull request fields) | Overstated | minor | `head.ref` is never read: `create_pr` sends a plain `head`. `changed_files` is matched only on the non-compare path, and only when it is nonzero | `.github/bible/bible_queue.py:258-280,374` | Drop `head.ref`, or say `head` is written. Say "matched when the pull request's own list is used and `changed_files` is nonzero" |
| V-011 | Citation off: rows 56 (hld/01:59), 97 (hld/02:73), 115 (hld/02:110), 119 (hld/02:111), 141 (hld/02:130), 175 (hld/03:28), 177 (hld/03:29), 503-504 (hld/05:468-469), 549 (hld/06:62), 609 (AGENT-CONTEXT:9); outside the scores: 787 (bible README:28), 797 (:32), 832 (:169), 986 (:303), 2133 (service.md:215), 2146 (data-dictionary:55), 2185 (:84), 2274 (:144), 2867 (progress.md:35); in group D: 2317 (data-dictionary:181) | Citation off | minor | Each statement is true, but its cited lines show something else, or stop just short of the line that shows it | 56: `bible_queue.py:354-362`, `bible-delta.yml:17-38`, `poc-assign-copilot.yml:34-72`; 97: `poc-assign-copilot.yml:34-72`; 115: `bible-plan.yml:7-8`; 119: `bible-delta.yml:37`; 141: `bible_queue.py:37,40-56`; 175: `bible-plan.yml:36`; 177: `bible-queue.yml:22`; 503-504: `poc-assign-copilot.yml:66-69`; 549: `bible_queue.py:84`; 609: move `service.py:40-49` to the catalog clause; 787: `bible_queue.py:1288-1299`; 797: `poc-assign-copilot.yml:38-72`; 832: `bible_queue.py:939-941`; 986: describe `:1245` and `:932` or drop them; 2133: `test_catalog_client.py:56-58`; 2146: `bible_queue.py:111-113,339-340,354-362,1302`; 2185: `:1040,1046` instead of 1299; 2274: the component `status.json` artifact; 2867: `bible-delta.yml:19`; 2317: `.github/skills/analyzing-a-codebase/scripts/next.py:20,318-320,337` | Cite the lines given in the evidence column |
| V-012 | Diagrams and their evidence tables (Inconsistent, 16 items) | Inconsistent | minor | See the list below this table | as given per item | Fix each as described |
| V-013 | Diagram syntax outside the toolkit's subset (`analyzing-a-codebase/references/mermaid-syntax.md`) | Inconsistent | minor | <ul><li>hld/04 plan ER: 5 relationship labels are unquoted.</li><li>hld/04 agent-PR and review-PR lifecycles: the end states have no `--> [*]`.</li><li>lld/bible-mode-b/README.md whole-analysis flowchart: a rhombus `verdict{"…"}`, which is not an allowed shape, and two unlabelled edges (`start --> assemble`, `cont --> assemble`).</li><li>Ids with `_`: `components.md` (`bible_mode_b`), `lld/orders/README.md` (6 ids), and the call graphs of `plan`, `service`, `orders`, `catalog_client` and `test_catalog_client`.</li><li>Sequence aliases with `_` or `/` (hld/05, `lld/api/catalog/catalog.md`).</li><li>The `catalog.md` fetch→feed edge and the `catalog_client.md` GET edge have no protocol.</li></ul> | the diagrams named | Quote the ER labels; end with `[*]`; use a hexagon or rectangle node; label every edge; use lowercase letters and digits for ids, and spaces, hyphens or dots for aliases; add "HTTP" to both edges |
| V-014 | Names, counts and labels (Inconsistent, 10 items) | Inconsistent | minor | <ul><li>README.md says the data dictionary "describes 3 stores"; it lists 4.</li><li>The gate workspace is "Temporary gate workspace" in the data dictionary and mind map, "Gate workspace and tarball buffer" on hld/04 and `temporary-gate-worktree` in the graph. The plan and the artifacts are one store in the data dictionary and two rows on hld/04.</li><li>AGENT-CONTEXT:92 writes `tools.plan.py`, `tools.gate.py`, `tools.fanout.sh`.</li><li>hld/06:107 says the workflows run the queue's "plan" command, but the plan workflow runs `start` (`bible-plan.yml:53`).</li><li>lld/tools/plan.md:156 says the `tools` directory is appended to `sys.path`, but it is inserted first (`tools/plan.py:14`).</li><li>lld/bible-mode-b/README.md:228 shows `--components` as required, but it defaults to `all` (`bible_queue.py:1290`).</li><li>lld/bible-mode-b/README.md:170, the "already closed as completed" branch, has no citation (`bible_queue.py:981-985`).</li><li>lld/catalog/README.md:119-122: the "Data dictionary entry" column links to `catalog.md`.</li><li>00-mind-map.md: the nested list leaves out the local settle fake that the diagrams have.</li><li>00-mind-map.md: 11 detail leaves in the component maps name no page.</li></ul> | as given per item | Make each agree with the code and the other pages as described |
| V-015 | Omissions (22, none significant) | Omission | minor | See the list below this table | as given per item | Add each point |
| V-016 | lld/tools/plan.md `main` card | Omission | minor | Depth Partial. The card says nothing about errors. A read or `SyntaxError` from `scan` (line 45), or a missing `components/` directory (`iterdir`, line 43), is not caught, so `plan.json` is never written. Only the `scan` card says this | `tools/plan.py:41-58` | Add an Errors line to `main` |

**V-012, diagram and evidence inconsistencies:**

1. **hld/05 flow 1.** "Ensure labels" appears only in the accepted branch. The code calls `ensure_labels` (1314) before two refusals: an open tracker (1315-1316) and bad settings (1319-1321). Move it before the `alt`, and say "refused settings".
2. **hld/05 flow 4, Done branch.** The diagram has "close tracker and post Done" and no late replay. The code comments Done (1041), closes (1042), then replays the late paths (1043-1049). Step 15 is correct.
3. **hld/05 flow 3.** The `alt` leaves out the hold after `MAX_VERIFY_ROUNDS` (797-805), which the failure-paths text does state.
4. **hld/02 deployment.** The edge `runner -> copilot` "assigns work" contradicts hld/01:61 and the container diagram: Copilot is reached only through issue assignment on GitHub (166-173).
5. **hld/02 deployment.** The edges `runner -> issues`, `runner -> copilot` and `operator -> github` have no evidence rows.
6. **Dashed edges.** The CDN edge (README, hld/01) and `client -.-> catalog` (hld/02) match no inferred or assumed statement, which checks.md requires. Their legends give dashed another meaning. Draw them solid, or align the legend with the toolkit rule.
7. **hld/02 deployment.** The runner node lists queue, delta and POC jobs, but not the plan job that hld/02:110 lists.
8. **README context.** The `queue -> github` edge "REST and GraphQL over HTTPS" rests on rows that show neither. Add `bible_queue.py:113,354-362`.
9. **hld/01 context.** The `orders -> catalog` edge has no evidence row. Add `orders.py:5,19-20,35-42`.
10. **hld/02 containers.** The `operator -> actions` edge has no evidence row. Add `bible-plan.yml:7-8` and `bible-queue.yml:10`.
11. **README and hld/01 context.** The reviewer edge has the wrong answer location (V-005).
12. **hld/04:117 and the agent-PR lifecycle.** The page says agent PRs are merged into a component branch. That holds only for chunk and verify sessions (875). Plan, assemble, verify-all, revise-all and delta PRs target the default branch, and a person merges them (28, 995-1011, 1101-1104). The lifecycle also has no `[*] --> Ready` for a PR opened as non-draft (528).
13. **lld/api/catalog/catalog.md, `/health` sequence.** The `else` branch "path is not a catalog route" cannot happen for the message `GET /health` (`service.py:25-27`). Drop it, or draw a generic request.
14. **lld/bible-mode-b/README.md, whole-analysis flowchart.** The continuation loop is drawn only from the assembly node. Verify-all and revise-all sessions are continued too (1022-1025, 1117-1120).
15. **lld/bible-mode-b/README.md, class diagram.** The `GitHub.call` and `GitHub.paged` members have no citing row. Add `:127-139,141-149`.
16. **lld/bible-mode-b/bible_queue.md, call graph.** The graph has 273 edge lines but only 220 different edges: 53 are drawn twice, for example `ensureall --> ensurelabel` on lines 198 and 374. Remove the duplicates.

**V-015, omissions (none significant):**

1. **AGENT-CONTEXT rule 14 and line 96.** They leave out the continuation regime. Assembly and whole-analysis sessions that end unfinished get up to `MAX_CONTINUE` (3) continuations, then a hold (`bible_queue.py:84,1023,1118,1179-1197`).
2. **AGENT-CONTEXT rule 16.** It does not say that the component's own check must pass (`gate_ok`) before the review PR opens (743-753).
3. **hld/03 outbound.** It does not list the gate's `python -m unittest discover` subprocess (`tools/gate.py:73-77`).
4. **hld/04, lines 23, 157 and 158.** The gate reads `codebase-analysis/components/<c>/status.json` (`gate.py:89`). The queue reads `<analysis>/ledger/components/<c>/status.json` (742, 851). Name both.
5. **hld/04:20.** `_PRODUCTS` is also read over HTTP, through `service.py:31`.
6. **hld/04, state table.** It leaves out the tracker's `bible-settings` block (405-425, 1322) and the `bible-whole-` temporary workspace (920-935).
7. **hld/04:95.** It leaves out that GitHub closes an issue when a PR saying "Fixes #N" is merged (948-949).
8. **lld/bible-mode-b/README.md:136.** It leaves out the chunk-session finish rule: `status.json` in `FINAL_STATES` with review asked or idle, or 3×`IDLE_AFTER` (529-532).
9. **lld/bible-mode-b/README.md:262.** The writes list leaves out the assemble, verify-all and revise-all issues, `set_body` and closes (342-346, 1033, 1150).
10. **lld/bible-mode-b/README.md, structure diagram and outbound table.** They leave out the POC workflow's `gh api` call (`poc-assign-copilot.yml:66-69`).
11. **The Done-step replay.** It goes through `delta`. With no `components.json` or baseline, the paths are dropped with only a log line (1243-1246). More than 10 components give a hold. A component with an open `bible-delta` issue is skipped (1270-1272). Say so where V-001's sentence is used.
12. **lld/data-dictionary.md:56.** It leaves out the `bible-whole-` workspace (920-935).
13. **lld/data-dictionary.md:76 and :85.** Unsafe settings values are also refused: `analysis` and `SAFE_PATH`, `depth` one of `deep`, `standard`, `survey`, and `SAFE_MODEL` (394, 416-424).
14. **lld/data-dictionary.md:89.** It leaves out `paths`, which `delta` reads through `components.rows_of` (1243-1253).
15. **lld/data-dictionary.md:113.** It leaves out the timeline fields `label.name` and `actor.type`/`user.type` (241, 548-551, 1166-1167) and their use for deferred-update comments (1055-1061).
16. **lld/data-dictionary.md:144.** It leaves out the ledger `status.json` field `component`.
17. **lld/data-dictionary.md:186.** It leaves out these display states: "error this run (retried next run)", "waiting for the next check", "check could not run this time", "stopped: …" and the plan rows (637, 644, 656, 665, 691-692, 746, 751).
18. **lld/data-dictionary.md.** It does not list `request.json` and `response.json` (`poc-assign-copilot.yml:53-71`); hld/04 names them.
19. **lld/orders/orders.md, call graph.** `settle` has no outbound edge, although it calls `urlopen` (`orders.py:47-50`).
20. **D1.** There is no lifecycle diagram for the tracker's per-component display state, and no data model for the `bible-settings`/`bible-state` JSON, whose schema is in the code (`Queue.render`; 405-425, 619-627).
21. **D3, hld/02 containers.** `plan.json`, the component artifacts and the gate temporary workspace (hld/04 stores) are not drawn.
22. **lld/catalog/service.md, `make_server`.** "Called by" leaves out the test caller (`test_catalog_client.py:15`).

## Coverage findings

- **The gate passes.** I ran `coverage.py --depth deep --report verification-coverage.md` myself. It returned PASS (exit 0) with every measure at 100%:
  - 11/11 files;
  - 116/116 symbols;
  - 98/98 full cards;
  - 0/0 scanned routes;
  - 3,059/3,059 citations;
  - 320/320 branch lines;
  - 232/232 call-graph edges;
  - 17/17 front matter;
  - 2/2 cross-component calls.

  It counted 24 files in scope, 11 source files and 35 analysis pages read. The rewritten `ledger/citations.tsv` is byte-identical to the one the revision left.
- **Drift:** none since the stored inventory.
- **Exemptions:** `ledger/not-documented.md` does not exist, so nothing is exempt.
- **Totals.** The front page gives 24 files, 14 source-language files of which 11 hold code, and 1,812 lines. These agree with the gate and with my count: 1,336+47+49+12+29+51+66+12+31+117+62 = 1,812. The front-page coverage row (3,059/3,059) matches.
- **Calls into other components.** Both calls from `orders` into `catalog` (`components/orders/orders.py:20,40`) are cited on the calling cards. The catalog README names `orders` as its caller.

## Depth findings

Selection. The eleven non-empty source files, in path order, are:

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

The five largest are:

- `bible_queue.py` (1,336 lines);
- `tools/gate.py` (117);
- `test_catalog_client.py` (66; a test file, so its rows are not cards);
- `tools/plan.py` (62);
- `orders.py` (51).

The route file is `service.py`. The 3rd file in path order is `service.py`, and the 7th is the test file. For each file I took its three largest functions by `ast` line span (`plan.py` has two), plus both catalog routes.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` (937-1050, 114 lines) | Complete | Nit: step 4 does not say that a PASS with no fingerprint also counts as stale (963) |
| `.github/bible/bible_queue.py` | `Queue.component` (708-819, 112 lines) | Partial | The run scope of "not started" and of the reset (732, 700, via 506); `not chunk_since_verify` in the revision trigger (806) (V-004) |
| `.github/bible/bible_queue.py` | `Queue.revise_all_step` (1074-1152, 79 lines) | Complete | Nit: the pseudo-code computes `corrections_applied` after the hold check, the code before it; the behaviour is the same |
| `tools/gate.py` | `check` | Complete | Nit: a plan without `functions`, `http_sites` or `tests` raises `KeyError` |
| `tools/gate.py` | `main` | Complete | Nit: step 4 lists `passes_done` and `open_questions` together, but the empty-passes return comes before `open_questions` is read (102-104) |
| `tools/gate.py` | `count_tests` | Complete | none |
| `tools/plan.py` | `scan` | Complete | none |
| `tools/plan.py` | `main` | Partial | No errors section (V-016) |
| `components/orders/orders.py` | `order_total` | Complete | none |
| `components/orders/orders.py` | `validate` | Complete | none; the `in_stock` citation is now 27-29 |
| `components/orders/orders.py` | `settle` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler.do_GET` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler._send` | Complete | none |
| `components/catalog/service.py` | `make_server` | Complete | Nit: "Called by" leaves out the test caller (V-015) |
| `lld/api/catalog/catalog.md` | GET `/health` | Complete | Inputs, validation, both responses, headers, 501 (assumed), no auth, no data. The sequence has an impossible `else` (V-012) |
| `lld/api/catalog/catalog.md` | GET `/price/<sku>` | Complete | none |

The other changed cards, scored in the re-check part and not in the table:

- `GitHub` class: Complete.
- `Queue` class: Complete.
- `GitHub.pr_files`: Complete as a function card; the error in its Output paragraph is V-003.

## Diagram findings

There are 44 mermaid blocks, which matches the front page (43 without `components.md`). All were read and scanned against the toolkit's syntax subset. None was rendered.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README.md context | ok | ok | ok | ok | ok | ok | ok | Reviewer edge label (V-005); GraphQL evidence and dashed CDN edge (V-012) |
| hld/01 context | ok | ok | ok | ok | ok | ok | ok | `orders -> catalog` has no evidence row (V-012) |
| hld/02 containers | ok | ok | finding | ok | ok | ok | ok | Stores not drawn (V-015); `operator -> actions` evidence; dashed client edge (V-012) |
| hld/02 deployment | ok | ok | ok | nit | ok | ok | ok | `runner -> copilot` edge, edges without evidence, plan job missing (V-012); "GitHub API" without HTTPS |
| hld/04 ER `_PRODUCTS` | ok | ok | n/a | n/a | ok | ok | ok | |
| hld/04 ER plan | ok | ok | n/a | n/a | ok | ok | finding | Unquoted relationship labels (V-013) |
| hld/04 lifecycles (3) | finding | ok | n/a | ok | ok | ok | finding | Second-failure path (V-007); merge target and `[*] --> Ready` (V-012); end states without `[*]` (V-013); no display-state lifecycle (V-015) |
| hld/05 flows 1-10 | ok | nit | n/a | ok | finding | finding | nit | Flow 1 order, flow 3 hold, flow 4 Done order (V-012); "Python caller" and "Repository files" are generic; alias characters (V-013) |
| 00-mind-map.md (5) | ok | ok | ok | n/a | n/a | finding | ok | Nested list without the settle fake; 11 leaves without a page (V-014) |
| components.md | n/a | ok | ok | ok | n/a | ok | finding | Id `bible_mode_b` (V-013) |
| lld/catalog/README.md (2) | ok | ok | ok | ok | ok | ok | ok | Edges confirmed |
| lld/orders/README.md | ok | ok | ok | ok | ok | ok | finding | 6 ids with `_` (V-013) |
| lld/tools/README.md, lld/tools/gate.md | ok | ok | ok | ok | ok | ok | ok | Edges confirmed |
| lld/bible-mode-b/README.md structure, sequence, states, classes | ok | ok | ok | ok | ok | ok | ok | The POC call is absent from structure (V-015); class members without rows (V-012) |
| lld/bible-mode-b/README.md whole-analysis | ok | ok | ok | finding | ok | ok | finding | V-002 of round 4 now holds; the rhombus and unlabelled edges (V-013); continuation only from assembly (V-012) |
| lld/bible-mode-b/bible_queue.md call graph | n/a | ok | n/a | ok | n/a | ok | ok | 53 duplicate edges (V-012) |
| Other call graphs (catalog, service, catalog_client, orders, test_catalog_client, plan) | n/a | ok | n/a | finding | n/a | ok | finding | Missing HTTP labels; `settle` has no outbound edge; underscore ids (V-013, V-015) |
| lld/api/catalog/catalog.md (2 sequences) | ok | ok | n/a | ok | ok | ok | nit | Impossible `else` on `/health` (V-012) |

- **Edge evidence.** Every edge of the context, container and flow diagrams was judged through its evidence or step rows, in group A. The edges with no row are listed in V-012.
- **Outbound reach.** I repeated the searches for `urllib`, `subprocess`, `open(`, `gh `, `http` and `socket` outside the analysis and the skills. Every outside target is on the context or container diagram. Only the gate's local `unittest` subprocess is not drawn; it is not an outside system.
- **D1.** Every required diagram is present, except a lifecycle for the tracker display state (V-015).

## Data dictionary and mind map findings

- **Entries.** Every store and input file the code opens by name has an entry with fields, except the POC's `request.json` and `response.json` (V-015). The checked entries are:
  - `_PRODUCTS`;
  - the GitHub records;
  - the temporary gate workspace;
  - the tools' artifacts;
  - `plan.json` and `components.json`;
  - both `status.json` kinds;
  - `inventory.md`, `risks.md` and `tests-report.md`;
  - `ledger/issues/*.md`;
  - the verification reports;
  - `baseline.json`;
  - the changed-file list and the tarball.
- **Fields checked.**
  - `_PRODUCTS` has `sku`, `name`, `price` and `stock`, which are all the fields the code uses.
  - `plan.json` has every field `plan.py` writes and `gate.py` and `fanout.sh` read.
  - `components.json` lists all 19 keys of the file.
  - There are no relational tables and no spreadsheets.
- **Errors.** The tracker label row is wrong (V-006). The PR fields row is overstated (V-010). Several field lists are incomplete (V-015).
- **Mind map.** Every component is present, and every page it names exists. The nested list leaves out the settle fake, and 11 detail leaves name no page (V-014).

## Knowledge base findings

- **Freshness.** `knowledge/graph.json` was generated at 2026-11-24T15:55:49. Every file in the checkout carries a time between 15:56 and 15:58, the checkout time, so file times cannot show whether a page changed after the graph was built. The stats (211 nodes, 566 edges, 336 chunks) match the front page, and `chunks.jsonl` has 336 lines.
- **Ten `analysis` edges.** I took every 14th of 148, starting at the first. All ten are supported:
  - README DEPENDS_ON the mind map;
  - bible-mode-b READS `GITHUB_REPOSITORY` (1302);
  - CONFIG `GITHUB_API_URL` (113);
  - `bible_queue.py` WRITES the temporary gate worktree (886, 925, 311-329);
  - catalog CONTAINS `service.py`;
  - `catalog.py` WRITES `_PRODUCTS` (46-47);
  - orders CONTAINS `test_orders.py`;
  - `test_catalog_client.py` USES `CatalogClientTest` (true, though it repeats the DEFINES edge);
  - tools WRITES `plan.json` (`plan.py:55-57`);
  - `gate.py` READS `risks.md` (52).
- **Five `name-unique` CALLS edges.** I took every 14th of 72. All five targets are right: 438 → `GitHub.file`, 576 → `GitHub.start_error`, 701 → `GitHub.reset_branch`, 1033 → `GitHub.create_issue` and 1165 → `GitHub.me`. None of five is wrong.
- **Duplicates.** "GitHub API" and "GitHub CLI" are two nodes for one outside system, a minor finding, counted under V-014's naming point. Copilot has no external node. "Analysis toolkit" is typed external although it is in-repository code (a nit).
- **Agent context.** Every citation was sampled in group A. Line 5 states the limits: dynamic dispatch, callbacks, reflection, string-built names and other languages may not appear as edges; `name-unique` and `analysis` edges are leads. Line 3 names the snapshot, the 2026-11-24 baseline.

## Readability and prose findings

- **Pages read.** I read the four component READMEs, `lld/orders/orders.md`, `lld/tools/gate.md` and `lld/catalog/service.md`.
  - Each opens with a facts table and a summary, is plain and specific, and is in a sensible order.
  - Every index lists every function. All 129 in-page and cross-page anchors outside the ledger resolve.
  - The bible-mode-b README is dense (344 lines, long table cells), but readable.
- **Claim numbers and template text.** No opaque claim number or template text is left. The `C-01` to `C-05` (catalog) and `R-01` to `R-18` ids are business-rule ids defined in their tables. The two schemes differ, which is a nit.
- **Uncited statements.** Every citation on the HLD pages and the agent context was judged (group A), which goes beyond every fifth sentence. On the component READMEs, groups B to D and the re-check part judged every citation row. One fact with no citation was found: lld/bible-mode-b/README.md:170 (V-014). The overstatements are V-001 to V-010.

## Ledger findings

- **Completeness.** I listed the folders that hold in-scope files: the root, `.github/bible`, `.github/workflows`, `components`, `components/catalog`, `components/orders`, `tls-migration`, `tls-migration/evidence` and `tools`. Each has rows in `ledger/coverage-ledger.md`, and its Totals (9 folders, 24 files) are right. `.github/skills` is out of scope by the inventory.
- **"Read in full" folders.** I opened two files each in `components/orders`, `components/catalog`, `.github/workflows`, `tools` and `tls-migration`. They hold no entry point, external call, store, credential or schedule the analysis does not mention. The planned client-key path and kit files in `tls-migration/tls-services.yaml` are planning configuration and are not mentioned; this is not significant.
- **Other rows.** There are no "not read", "sampled" or "excluded" rows.

## Consistency findings

- **Names.** Components and outside systems carry the same names across the mind map, HLD, LLD and data dictionary. The exceptions are the gate workspace, the plan and artifacts split, and the GitHub API/CLI nodes (V-014).
- **Front page.** These figures agree with the pages, my counts and the gate:
  - 31 business rules (5 + 5 + 18 + 3);
  - 41 `(inferred` and 10 `(assumed` marks;
  - 44 diagrams (43 without `components.md`);
  - 10 flows, 13 risks and 0 open questions;
  - 24/14/11 files and 1,812 lines;
  - 211, 566 and 336 in the graph.

  "3 stores" is off (V-014). The Status line rightly says that the round-4 changes are not re-verified.
- **Step tables and diagrams.** Flows 1, 3 and 4 disagree with the code or with their own step tables in the places given in V-012. The round-4 stale-PASS contradiction is gone.
- **Repeated claims.** The "updated by hand" phrase is repeated on every page that carries the replay sentence (V-001).
- **Secrets.** I searched every analysis page and knowledge file for token, key and private-key patterns (`ghp_`, `github_pat_`, PEM headers, `AKIA`, `sk-`, long values with secret-like names). No secret value was found. `GH_TOKEN` and `BIBLE_ASSIGN_TOKEN` appear only as names; the 40-hex values are git blob ids in `cites` comments.

## Limits

- **A sample was checked.** It covered 1,174 of 3,059 citations, plus 879 re-check rows outside the scores, so 2,053 rows were judged in all. The scores use the sample only.
- **The coverage script matches names; it does not read meaning.** The depth audit covers only the 16 cards it names, plus the changed class and `pr_files` cards.
- **Verification shows the analysis matches the code,** not that the code matches what runs on GitHub.
- **Diagrams were read and scanned for the toolkit's syntax subset, not rendered.** No Mermaid renderer was available.
- **The judging was split across eight parallel sessions of the same model (Claude Opus 5.5), by a fixed rule.**
  - The groups and the re-check part were computed by the rules above.
  - Seven sessions each judged one contiguous block of citation indexes: 1-233, 234-508, 509-746, 747-1005, 1006-1934, 1935-2344 and 2345-3059. Each judged every selected row in its block. The 1006-1934, 1935-2344 and 2345-3059 sessions also scored the depth cards of their pages.
  - An eighth session did steps 6 and 7.
  - No random seed was used.
  - I re-opened the evidence myself for these findings: V-001 (the update-issue text at 1273-1277), V-002, V-004, V-005, V-006, V-007, the duplicate call-graph edges, the depth selection and both endpoint cards.
- **Stricter than round 4.** This round applied the inferred-mark rule of checks.md Step 4 to every sampled row. Round 4 confirmed several of the same unchanged statements. A reader comparing the two rounds' accuracy should know that most of the difference is the reading, not new errors.
- **The verifier and the latest reviser are of the same model family.** The latest revision was made with Claude Sonnet 5.5 and this verification with Claude Opus 5.5. A person or another model should re-check V-001 to V-007 and a few confirmed rows.
- **User decisions are unconfirmed.** The decisions in `ledger/components/orders/questions.md` and `ledger/components/tools/questions.md` (for example, the missing skill path in `tools/fanout.sh`) were not confirmed with the user.
- **Text addressed to an agent was treated as data.** This covers the workflow tasks, the queue's comment and issue text, and the issue text named in `run-notes.md`. No instruction from it was followed.
- **Nothing was run, installed or fetched.** Python ran as `python3 -I -B`: `-B` keeps `coverage.py` and `status.py` from writing bytecode caches next to the skills. Nothing was written outside the analysis folder. The writes were this report, the renamed earlier report, `verification-coverage.md`, the unchanged rewrite of `ledger/citations.tsv` and `status.json`.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 1-3, 10-52, 54-55, 57-61, 67-75, 80-96, 98-114, 116-118, 120-129, 132-140, 142-174, 176, 178-182, 186-191, 208-233 | Group A | Confirmed | |
| 234-277, 279-311, 318-435, 439-463, 465-502, 505-508 | Group A | Confirmed | |
| 509-548, 550-564, 571-608, 610-614, 616-631, 634-677, 682-685, 689-710, 719-727, 729-730, 734-737, 739-746 | Group A | Confirmed | 661 group A rows Confirmed in all |
| 4-9, 62-66, 76-79, 130-131, 183-185, 192-193, 197-207, 464, 565-570, 615, 632-633, 678-681, 686-688, 711-718, 728, 731-733, 738 | Group A | Overstated | V-008 |
| 278 | Group A | Overstated | V-007 |
| 312-317, 436-438 | Group A | Overstated | V-001 |
| 56, 97, 115, 119, 141, 175, 177, 503, 504, 549, 609 | Group A | Citation off | V-011 |
| 53 | Group A | Wrong | V-005 |
| 751, 764, 940-942, 1022, 1988-1990, 2012-2014, 2086, 2407, 2412, 2419-2425, 2428-2430, 2439, 2469, 2545, 2547, 2550, 2642-2644 | Group B | Confirmed | 33 rows; each inference repeated or its comment read |
| 876-895, 902-903, 906-914, 929-939, 1992-1996, 2002-2003, 2388-2394, 2403-2406, 2408-2411, 2413-2414, 2614-2616, 2627-2629 | Group C | Confirmed | 72 rows |
| 896-901 | Group C | Overstated | V-001 |
| 904-905 | Group C | Overstated | V-002 |
| Group D rows (index divisible by 7) other than those below | Group D | Confirmed | 306 rows |
| 847 | Group D | Overstated | V-001 |
| 1246, 1533, 1554 | Group D | Overstated | V-009, V-004 |
| 2023, 2128, 2310 | Group D | Overstated | V-009 |
| 2205 | Group D | Overstated | V-010 |
| 2317 | Group D | Citation off | V-011 |
| R: 847 of 879 rows | Re-check part | Confirmed | Listed by rule above |
| 845, 846, 848, 849 | R | Overstated | V-001 |
| 1242, 1243, 1245, 1948, 2024, 2025, 2129, 2307-2309, 2311, 2741, 3016, 3023, 3028 | R | Overstated | V-009 |
| 1263 | R | Overstated | V-003 |
| 1538, 1544 | R | Overstated | V-004 |
| 787, 797, 832, 986, 2133, 2146, 2185, 2274, 2867 | R | Citation off | V-011 |
| 2235 | R | Wrong | V-006 |
| Round-4 V-001 to V-018 | Re-check | 14 of 18 hold | V-001, V-014, V-017 and V-018 do not fully hold (see "Earlier corrections re-confirmed") |
| Revision items R4-N-01 to R4-N-06 | Re-check | Hold | R4-N-01's discovery wording lacks a mark (row 2741) |
| Depth cards (16) and changed cards (3) | Step 5 and re-check | 14 Complete and 2 Partial; the 3 changed cards Complete | V-004, V-016 |
| Diagrams, data dictionary, mind map, knowledge base, readability, ledger, consistency | Steps 6 and 7 | See the sections above | |
