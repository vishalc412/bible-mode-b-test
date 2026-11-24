# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Analysis fingerprint | 71e3cf441e367765 |
| Analysis snapshot | 30 in-scope files, 1,962 source lines, code of 2026-11-24 (baseline 2026-11-24T20:00:32, claude/update-125-126), no version given (front page) |
| Repository at verification | 30 files in scope, 14 source-language files of which 11 hold code (3 empty `__init__.py`), 1,962 lines by my count; `.github/bible/bible_queue.py` has 1,434 lines; no drift from the stored inventory; no version given |
| Depth stated / depth found | deep / deep |
| Verified with | Claude Code (Claude Opus 5.5), standing in for the GitHub Copilot coding agent |
| Analysis produced with | Copilot coding agent (model not recorded) for planning, components, assembly and the first revisions; Claude Sonnet 5.5 standing in for Copilot for the revisions of 24 Nov 2026 (front page); the delta update of 24 Nov 2026 20:00 by `tracking-codebase-changes` (`CHANGELOG.md`, model not recorded) |
| Sampling level | standard, after a full audit of the delta (see "How the sample was selected") |
| Date | 2026-11-25 |

After corrections: every flagged statement re-checked: 0 of 11 confirmed.

The 11 are round 7's V-001 to V-011 (that report is now `verification-report-2026-11-24-5.md`). No revision of them was made (`revision-log.md` has no round-7 entry); the delta update rewrote most of the pages they name but applied none of them. I re-checked all 11; each is re-listed below as a minor correction (V-013). This is round 8, a full verification after a delta update, not a re-check, so there is no `Re-check of` row. Steps 1 to 8 of the skill were all done.

## Summary

The analysis is complete and deep, and most of it is accurate, but the delta update of 24 Nov introduced errors in the queue's replay and acceptance rules and left round 7's corrections unapplied. The coverage gate passes at deep with every measure at 100% (11/11 files, 124/124 symbols, 103/103 full cards, 344/344 branch lines, 247/247 call-graph edges, 3,588/3,588 citations, 17/17 front matter, 2/2 cross-component calls). Of 1,962 judged citations, 1,643 are confirmed, 150 cite the wrong or too few lines, 122 are overstated and 47 are wrong; none is unsupported. Accuracy 91.4%, citation quality 83.7%. Of 26 cards audited, 24 are Complete and 2 Partial.

The verdict is `PASS AFTER CORRECTIONS`, not `PASS`, because accuracy is below 95% and there are two `major` corrections. It is not `FAIL`: coverage is 100%, accuracy is above 85%, depth usable is 100%, there are two majors (at most five allowed), and every problem has a specific correction.

**The delta part and the rest, separately.** The delta audit (960 rows: every citation on the 11 rewritten cards, on the 200 page lines `ledger/delta.md` marks for a recheck, and every citation on a changed page that points into a changed or added function or into `https-migration/`) scored 90.4% accuracy (770 confirmed, 98 citation off, 55 overstated, 37 wrong). The standard sample of the rest (1,002 rows) scored 92.3% (873 confirmed, 52 citation off, 67 overstated, 10 wrong). Both majors are in the delta part.

Where the analysis is weakest:

- **The closed-run replay (V-001, major).** Five places say that paths recorded on "a run that never finishes" are replayed by `replay_closed_runs`; the code reads closed trackers only, so a tracker left open is never replayed.
- **The acceptance rule R-19 (V-002, major).** It says a re-check with a flagged count of 0 is accepted for a full round's `PASS`; the code refuses every such re-check (`bible_queue.py:536`). The docstring says otherwise, a disagreement the pages do not record.
- **Unapplied round-7 items (V-013)** and the same kinds of slip in new text: unmarked library behaviour (the urllib redirect, V-007), searches whose scope the new `https-migration/` files widened (V-008), and uncited constants (`MAX_CONTINUE`, `MAX_NOCHECK`, `MAX_DELTA_ISSUES`, V-010).

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 124 / 124 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 103 / 103 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 344 / 344 (100.0%); 247 / 247 (100.0%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner; the two catalog GET routes have endpoint cards (`lld/api/catalog/catalog.md`) |
| Citations that resolve | 3588 / 3588 (100.0%) |
| Coverage gate | PASS (depth deep); calls into other components 2 / 2 |
| Citations in the analysis / checked | 3588 / 1962 (960 delta audit, 1002 standard sample) |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 1643 / 150 / 122 / 47 / 0 |
| Delta audit: Confirmed / Citation off / Overstated / Wrong / Unsupported | 770 / 98 / 55 / 37 / 0 (accuracy 90.4%) |
| Standard sample: Confirmed / Citation off / Overstated / Wrong / Unsupported | 873 / 52 / 67 / 10 / 0 (accuracy 92.3%) |
| Omissions (significant) / Inconsistent | 9 (0) / 11 |
| Accuracy / citation quality | 91.4% (1793/1962) / 83.7% (1643/1962) |
| Cards audited: Complete / Partial / Shallow / Wrong | 24 / 2 / 0 / 0 |
| Depth / depth, usable | 92.3% / 100.0% |

## How the sample was selected

`ledger/citations.tsv` as `coverage.py` rewrote it in this session: 3,588 rows, byte-identical to the copy the delta update left (SHA-1 `27d4930d…` before and after).

**Delta part (the skill's "After a delta update"), 960 rows.** `delta-log.md` has a row (2026-11-24T20:00:32) newer than round 7's report, and `status.py --pages-changed-since verification-report.md` (run on round 7's report before it was renamed) lists 26 changed pages: `README.md`, `hld/01`-`06`, `knowledge/AGENT-CONTEXT.md`, the six `knowledge/` data files, `lld/api/catalog/catalog.md`, `lld/bible-mode-b/README.md`, `lld/bible-mode-b/bible_queue.md`, `lld/catalog/README.md`, `catalog.md`, `test_catalog.md`, `lld/data-dictionary.md`, `lld/orders/README.md`, `orders.md`, `reference/configuration.md`, `glossary.md`, `risks-and-surprises.md`. A row is in the delta part when any of these holds:

1. it sits on a card `ledger/delta.md` names: `lld/catalog/catalog.md` lines 66-112 (`NoHTTPRedirectHandler`, `redirect_request`) and 245-281 (`fetch_supplier_feed`); `lld/catalog/test_catalog.md` lines 37-38 and 46-47 (the two new tests); `lld/bible-mode-b/bible_queue.md` lines 1488-1493 (`Queue`), 1767-1877 (`reconcile`, `replay_closed_runs`, `replayed`), 2016-2090 (`component`), 2260-2353 (`assemble_phase`), 2997-3142 (`report_facts`, `recheck_due`, `accepted`): 231 rows;
2. its page line is one of the 200 lines `ledger/delta.md` lists under "Citations waiting for a recheck": 433 rows;
3. it is on a changed page and cites `https-migration/`, or a range overlapping a changed or added function (`bible_queue.py` 478-507, 516-520, 523-542, 664-679, 681-697, 699-703, 796-909, 1027-1148; `catalog.py` 18-24, 48-55; `test_catalog.py` 14-44): 632 rows.

The union is 960 rows, listed per block under "Everything checked". The six `knowledge/` data files have no citation rows; they were checked in step 6.

**Standard sample of the rest, 1,002 rows.** Group A: every row on `README.md`, `hld/*` and `knowledge/AGENT-CONTEXT.md` (rows 1-931; 320 of them are also delta rows, counted there). Group B: every other row labelled `inferred` or `assumed` (79 rows; 20 in the delta part). Group C: every other row whose nearest heading or bold title line above contains rule, outbound, calls out, integration, security, secret, auth or permission (98 rows, all under "Business rules" (65) or "Outbound calls" (33) of the component READMEs; 31 in the delta part). Group D: every remaining row whose index is divisible by 7 (349 rows; 84 in the delta part). A row in the delta part is not judged twice; its verdict counts in the delta figures.

**The marks rule, stated once and applied the same to every row** (from `references/evidence.md`, "How sure you are", and `checks.md` Step 4). A row is `Confirmed` when its cited lines support the statement it sits in (sentence, table cell, list item, step or diagram-evidence row) as written, and every part of the statement that rests on (a) an absence reaching past the cited lines, (b) a comment, docstring or non-acting document stated as behaviour, or (c) library, builtin, shell, `gh`, runner or GitHub behaviour beyond what the repository shows, carries `(inferred: …)` or `(assumed: …)` in the same sentence, cell or step. No mark is needed for an absence inside the cited lines, or for a sentence that only reports what a cited comment or document says. A missing mark makes the row `Overstated` (minor). A mark counts only in its own table cell. A request the code sends names its own effect; GitHub's behaviour beyond it does not. Rows of one statement share its verdict; when a true part is shown by none of its rows, all its rows are `Citation off`. Every search written into a mark was run again over its stated scope; a materially different count is `Overstated` when the conclusion holds, `Wrong` when it does not.

## Earlier corrections re-confirmed

An item holds when every place it named is corrected and, for a correction of a kind of slip, no other occurrence remains. All 11 were re-checked.

| Round-7 item | Holds? | Delta touched the place? | Re-opened |
| --- | --- | --- | --- |
| V-001 unmarked absences (hld/02:116, :118; lld/bible-mode-b/README.md:231) | No: all three unmarked, `bible-plan.yml:40-42` not cited | yes | `components/catalog/service.py:1-5,40-49`; `.github/workflows/bible-plan.yml:25-54`; `.github/bible/bible_queue.py:112-115,561-563` |
| V-002 platform behaviour (hld/05:74, hld/06:69) | No: both unmarked | yes | `.github/workflows/bible-plan.yml:50-54`; `tools/fanout.sh:6` |
| V-003 "repository secret" (AGENT-CONTEXT:94) | No: unmarked; the token read is now line 1400, not cited | yes | `.github/workflows/poc-assign-copilot.yml:4-6`; `.github/bible/bible_queue.py:117-126,1400-1403` |
| V-004 hold only when none is open | No: missing at hld/05:252, :274-275, :290, :297, lld/bible-mode-b/README.md:184 (the check is now line 1355) | yes | `.github/bible/bible_queue.py:1353-1362` |
| V-005 plain HTTP by default | No: lld/orders/README.md:23, :129, :134, lld/orders/catalog_client.md:151, lld/catalog/README.md:103 | partly | `components/orders/catalog_client.py:4,11,14-23` |
| V-006 search counts (hld/05:381 "10 hits"; data-dictionary:107 file operations) | No: 14 lines over the stated scope; the buffer and temp directories still left out | yes | the search; `.github/bible/bible_queue.py:296,307,327,330,976,1015,1426` |
| V-007 citations off (hld/04:238, hld/05:238, :248, hld/06:62, :71, AGENT-CONTEXT:106) | No: none re-pointed (now `:837`, `:1059`, `:84`, `:997-1008`, `:128-140`) | yes | `.github/bible/bible_queue.py:84,128-140,837,997-1008,1059` |
| V-008 uncited text (7 items) | No: #7 holds; #1-#6 remain | yes | as for V-007; `.github/bible/bible_queue.py:1264-1276` |
| V-009 `catalog_client` "6 hits" scope (11 places) | No: all 11 remain; the new `https-migration/https-inventory.md` adds 3 more hits | partly | the search, run again |
| V-010 names and prose (5 items) | No: #2 half fixed (lld/catalog/README.md:149); #1, #3, #4, #5 and the :159 sentence remain | yes | `knowledge/nodes.csv`; `.github/bible/bible_queue.py:837,1059,1029-1030` |
| V-011 omissions (2) | No: neither added | partly | `.github/bible/bible_queue.py:1249`; `components/catalog/service.py:16-22` |

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | Rows 569-572 (hld/05:252, flow 5 outcome), 580-588 (hld/05:290, step 5), 600-601 (hld/05:297, failure paths), 1045-1046 (lld/bible-mode-b/README.md:184), 1097-1104 (:259, R-12) | Wrong | major | `replay_closed_runs` iterates `gh.issues(["bible-tracker"], state="closed")` only; nothing in the queue closes an unfinished tracker, and `delta` merely stops recording on a tracker idle more than 14 days. Paths recorded on a run that never finishes stay on its open tracker and are never replayed until someone closes it. The docstring names the two cases: a person closed it, or an error after closing | `.github/bible/bible_queue.py:681-697`, `.github/bible/bible_queue.py:1327`, `.github/bible/bible_queue.py:393` | At each place: "if the tracker is closed without its Done step completing (by a person, or after the late update step failed), `replay_closed_runs` creates them at a later check; paths recorded on a tracker left open stay there until it is closed" |
| V-002 | Rows 1119-1122 (lld/bible-mode-b/README.md:266, R-19) | Wrong | major | A re-check with a flagged count of 0 is refused in every case (`recheck[1] == 0` in the refusal); only X < Y with Y > 0 is accepted for a full round's `PASS` with no major. The docstring (524-527) says Y = 0 is accepted: docstring and code disagree, and no Surprises row says so | `.github/bible/bible_queue.py:535-537`, `.github/bible/bible_queue.py:524-527` | "a re-check with fewer confirmed than flagged (X < Y, Y > 0) is accepted only for a `PASS` with no major correction that is not itself a re-check; a re-check with a flagged count of 0 is never accepted"; add the docstring disagreement to the README's Surprises and to `reference/risks-and-surprises.md` |
| V-003 | Rows 553-556 (hld/05:246), 1950 (bible_queue.md:2352, `assemble_phase` branch row); outside the sample: bible_queue.md:2309 pseudo-code | Wrong | minor | The late-step error comment says the update "could not get its update issues yet … the next check tries again" and returns without the mark or label, so `replay_closed_runs` retries it; it is not a request to update by hand | `.github/bible/bible_queue.py:1140-1145`, `.github/bible/bible_queue.py:685-695` | "comments that the late files could not get update issues yet and that the next check tries again, with the file list; returns `done` without the mark and label, so `replay_closed_runs` replays them later" |
| V-004 | Rows 2772-2781, 2785-2786, 2793 (lld/data-dictionary.md:188) | Wrong | minor | The `stopped: …` and `error this run …` row strings come from `Queue.run`, the plan rows from `Queue.plan_phase`, not "other branches of the same methods" | `.github/bible/bible_queue.py:725`, `.github/bible/bible_queue.py:732`, `.github/bible/bible_queue.py:744`, `.github/bible/bible_queue.py:769-780` | Name `Queue.run` and `Queue.plan_phase` in the source column |
| V-005 | Rows 516-517 (hld/05:173; also the diagram at :149), 849-851 (AGENT-CONTEXT:77), 3467 (glossary:20); 401-404 (hld/04:225, Citation off) | Overstated | minor | "a `PASS`, or a `PASS AFTER CORRECTIONS` with a confirmed re-check" is looser than `accepted`: a major needs a re-check with X = Y, and any report with a re-check needs 95% on its chain | `.github/bible/bible_queue.py:523-542`, `.github/bible/bible_queue.py:473` | "an accepted report as `accepted` defines it (a `PASS` with no unconfirmed major, or a `PASS AFTER CORRECTIONS` whose re-check confirmed every flagged statement; any re-check needs at least 95% accuracy)"; cite 523-542 at hld/04:225 |
| V-006 | Rows 1024-1028 (lld/bible-mode-b/README.md:179), 1029-1032 (:180), 1090-1092 (:256, R-09), 1096 (:258, R-11), 1116 (:264, R-17) | Overstated | minor | At `MAX_VERIFY_ROUNDS` the queue creates the whole-analysis hold issue instead of a revision or another verification; R-17 also accepts a change to `revision-log.md` only, and `WAITING_ANSWER` waits rather than fails | `.github/bible/bible_queue.py:1189-1194`, `.github/bible/bible_queue.py:1230-1240`, `.github/bible/bible_queue.py:1119-1130`, `.github/bible/bible_queue.py:89`, `.github/bible/bible_queue.py:943-955` | Add "unless the round limit is reached (R-10), when a hold issue is created" at :179, :180, R-09, R-11, and cite 1119-1130; R-17: "a page of the component or its `revision-log.md`; a `WAITING_ANSWER` status is labelled `bible-waiting-answer` and waits" |
| V-007 | Rows 2304-2306 (lld/catalog/README.md:28), 2359 (:116, C-06), 2366-2368 (:129), 2374-2375 (:140), 2423-2424 (lld/catalog/catalog.md:109) | Overstated | minor | The handler raises `HTTPError` when called; that urllib calls it on a redirect, so the fetch "refuses" the redirect, is library behaviour. `catalog.md:79` itself marks it assumed | `components/catalog/catalog.py:18-24`, `components/catalog/catalog.py:48-55` | Add "(assumed: urllib calls the installed handler's `redirect_request` on a redirect)" at each place |
| V-008 | Search marks whose result differs from the search as worded: rows 148-151, 162-167 (hld/02:116, :117, :120, :121, `build` "0 hits": 6, all `build_opener`); 279-280 (hld/03:60, `cron`/`schedul`: the scope must exclude the skills); 625-627 (hld/05:381, 14 lines, not 10); 2624-2625 (data-dictionary:107, file operations); the `catalog_client` "6 hits" mark at rows 273-278, 803-805, 869-874, 2824, 2828, 2830, 2907, 2912, 2960-2961, 3476, 3479, 3516, 3521. Outside the rows: hld/06:89 (`build`) | Overstated | minor | Each conclusion holds; the counts are for a narrower scope than stated (code files only), and the HTTPS change added `build_opener` and `https-migration/` mentions | the searches, run again; `components/catalog/catalog.py:51`; `components/catalog/test_catalog.py:15-28`; `.github/bible/bible_queue.py:296,307,327,330,976,1015,1426` | State the scope that gives the count ("search of the `*.py` files …: 6 hits, all in `components/orders/test_catalog_client.py`"; "`build` finds only `urllib.request.build_opener` in `catalog.py` and its test"; "… outside the analysis folder and the skills …"; "14 lines: 10 in code, 4 in `tls-migration/` documents"; list the tarball buffer and temporary directories at :107) |
| V-009 | Unmarked absence, document or platform statements: rows 1 (README:23, first sentence), 57 (hld/01:21), 79-84 (hld/01:61, also `@copilot continue` comments reach Copilot, `bible_queue.py:1296`), 227-228, 233-234 (hld/03:28, :31), 252-254 (hld/03:44, "separate-service mode" from the docstring), 302-305 (hld/04:21, "read by agent sessions"), 462-464 (hld/04:243, runner workspace), 666-669 (hld/06:28, checkout default ref), 749-751 (hld/06:93), 765-766 (AGENT-CONTEXT:9), 853 (AGENT-CONTEXT:78), 875-876 (AGENT-CONTEXT:92), 1512-1513 (bible_queue.md:1161), 2207 (bible_queue.md:3024, the "header rows" filter skips only `#`, `---` and `none` rows), 2290 (bible_queue.md:3218, only when not already `replayed`), 2576 (data-dictionary:68, `name` is read by no code), 2666-2671 (data-dictionary:135, `bible-replayed` is added later), 2870 (lld/orders/README.md:89), 3129 (lld/tools/README.md:126), 3507 (risks-and-surprises:14, Why cell) | Overstated | minor | Each fact holds as far as the repository shows, but rests on a search, a comment or document, or platform behaviour without a mark in its own cell, or says slightly more than the code (2207, 2290, 2576, 2666-2671, 853) | `README.md:1-7`; `components/orders/catalog_client.py:1-4`; `.github/bible/bible_queue.py:503-504`, `.github/bible/bible_queue.py:689-695`, `.github/bible/bible_queue.py:1296`, `.github/bible/bible_queue.py:1327-1340`, `.github/bible/bible_queue.py:1420`; `.github/workflows/bible-delta.yml:23-25`; `.github/workflows/poc-assign-copilot.yml:4-6` | Add `(inferred: <search or source>)` or `(assumed: <platform>)` in the same cell, as the judges' notes give per row; at 2207, 2290, 2576, 2666-2671 and 853 narrow the wording to what the code does |
| V-010 | Citation off (150 rows; each true, a part shown by none of its rows): 20 (README:23, other workflows' `runs-on`), 104-107 (hld/02:25, `tests-after.txt:3-5`), 127-130 and 2408 (hld/02:78, catalog.md:24, verification shown by `test_catalog.py:25-27`), 362-363, 364-365, 379-380, 424-428, 429-434 (hld/04:147, :151, :177, :237, :238), 508-510 (`RECHECK_MIN_ACCURACY`, 473), 531-534 (`MAX_CONTINUE`, 84), 546-549, 561-568, 596-599 (hld/05:244, :248, :297), 678-685, 717, 734-740, 882-883, 897-901, 902-910, 916-918 (hld/06, AGENT-CONTEXT: `CATALOG_URL` override 14-16, `GH_TOKEN` read 1400-1403, `GitHub.call` 128-140), 952, 1015-1019, 1037-1044, 1086, 1087-1089, 1093-1095, 1105-1108 (lld/bible-mode-b/README.md: constants 76, 84, 71, 394; 676-677; 829-841), 1245-1251, 1260, 1750, 1759-1760 (bible_queue.md:25, :448, :1823, :1851), 1905, 1911-1913, 2206 (bible_queue.md:2275, :2280, :3023), 2401-2402, 2672-2678, 2687-2692 (catalog README:159, data-dictionary:136, :139), 3458, 3465-3466, 3486, 3563 (glossary:15, :19, :30; revision-log:27, a stale line) | Citation off | minor | The right lines are named in the cell; all are in the code | as given per row | Add or replace the citations given |
| V-011 | Diagram, naming and bookkeeping (Inconsistent, 11 items): see the list below | Inconsistent | minor | | as given per item | Fix each as described |
| V-012 | Omissions (9, none significant): see the list below | Omission | minor | | as given per item | Add each point |
| V-013 | Round 7's V-001 to V-011, not applied (see "Earlier corrections re-confirmed") | as in round 7 | minor | Each remains at the places given in the table above | as given there | Apply round 7's corrections at the current line numbers |

**V-011, diagrams, names and bookkeeping:**

1. **lld/catalog/README.md:78 (D1).** The class diagram lacks the new `NoHTTPRedirectHandler` (`components/catalog/catalog.py:18-24`); add it with its evidence row.
2. **hld/05:46, :86, :130, :187, :259 (D7).** Participant alias `bible-queue.py` for `bible_queue.py`; the GitHub participant has four names (round 7's V-010 #1).
3. **hld/02:40 (D7).** The analysis toolkit is drawn inside the repository; the graph and hld/03 call it the External "Analysis toolkit".
4. **00-mind-map.md:32, :54, :152 (D7).** The store is "In-memory products" and "Product map"; every other page says `_PRODUCTS`.
5. **README.md:55, hld/01:51, hld/02:64 (D4).** The edge to the local settle fake lacks `:8099` (`components/orders/orders.py:12`); hld/02:61 lacks `:8001` and the route (`components/orders/catalog_client.py:11`, `:21`).
6. **knowledge/chunks.jsonl.** The front page's chunk says 3,583 citations; the page says 3,588: rerun `knowledge.py` after the last page edit.
7. **ledger/coverage-ledger.md:45 and README.md:93.** "excluded 0" disagrees with the 8 excluded paths in `ledger/inventory.json`; the front page's Files list omits `CHANGELOG.md`, `delta-log.md`, `ledger/delta.md`, `revision-log.md` and the verification reports it cites.
8. **knowledge/AGENT-CONTEXT.md:54.** "Rules the code enforces, Catalog" lists 5 rules and leaves out the new C-06 (the redirect refusal, `components/catalog/catalog.py:19-24`).
9. **README.md:52, hld/01:48.** orders is labelled "HTTP client", but no orders-to-catalog HTTP edge is drawn there (hld/02:61 draws it).
10. **lld/orders/README.md:71, :73; lld/orders/orders.md:134.** The `validate` and `remote_price|remote_line_total` counts in `*.py` are 4 and 8, not 1 and 10 (conclusions hold).
11. **lld/bible-mode-b/bible_queue.md:2473.** The `revise_all_step` row at line 1230 points to "the hold at line 1136"; the hold is at `bible_queue.py:1234-1240`.

**V-012, omissions (none significant):**

1. hld/01:61, hld/02:58: the queue also reaches Copilot through `@copilot continue` comments on its pull requests (`bible_queue.py:1296`).
2. bible_queue.md:1034 (`is_agent_pr` branches): a user record with no `type` counts as `Bot` (`bible_queue.py:233`).
3. lld/catalog/README.md and hld/02:25: the planned mutual-TLS move of the catalog HTTP link recorded in `tls-migration/` and `https-migration/https-migration-summary.md:5,17,68` is not named.
4. lld/orders/catalog_client.md:80: the `remote_price` Called by list omits the test at `components/orders/test_catalog_client.py:51-54`.
5. lld/tools/fanout.md:86: the `component:$c` label output is discarded too (`tools/fanout.sh:12`).
6. bible_queue.md, `revise_all_step`: it returns "session starting" even when `fail_or_retry` held the issue (`bible_queue.py:1210-1212`).
7. bible_queue.md, `replay_closed_runs`: `delta` records only on open trackers active in the last 14 days (`bible_queue.py:1327`, `ABANDONED_AFTER` 393).
8. lld/orders/orders.md, `settle`: a non-2xx response raises `HTTPError` (assumed: urllib) rather than returning `False`.
9. lld/bible-mode-b/README.md Surprises: the `accepted` docstring disagrees with the code on Y = 0 (with V-002).

## Coverage findings

- **The gate passes.** I ran `coverage.py --depth deep --report verification-coverage.md` myself: PASS, every measure at 100% (11/11 files, 124/124 symbols, 103/103 full cards, 0/0 scanned routes, 3,588/3,588 citations, 344/344 branch lines, 247/247 call-graph edges, 17/17 front matter, 2/2 cross-component calls). 30 files in scope, 11 source files, 35 pages read.
- **Drift:** none since the stored inventory; `ledger/track.md` shows 0 commits and 0 changed files since the analysis matched.
- **Exemptions:** `ledger/not-documented.md` does not exist, so nothing is exempt.
- **Totals.** The front page's 30 files, 14 source-language files (11 with code), 1,962 lines and 3,588 citations agree with the gate and my count (1,434 + 63 + 49 + 48 + 29 + 51 + 66 + 12 + 31 + 117 + 62 = 1,962).
- **Calls into other components.** Both calls from `orders` into `catalog` (`components/orders/orders.py:20`, `:40`) are cited on the calling cards.

## Depth findings

Selection (checks.md Step 5, by my own line counts). Five largest source files: `bible_queue.py` (1,434), `gate.py` (117), `test_catalog_client.py` (66, a test file, no cards), `catalog.py` (63), `plan.py` (62). Route file: `service.py`, also the 3rd non-empty source file in path order; the 7th is `test_catalog_client.py`. Three largest functions each, the two catalog routes, plus, for the delta part, every card `ledger/delta.md` names.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `report_facts` (delta) | Partial | The "noticed outside" filter skips only `#`, `---` and `none` rows, not header rows (row 2207); `REPORT_NAME` (475) uncited |
| `.github/bible/bible_queue.py` | `recheck_due` (delta) | Complete | none |
| `.github/bible/bible_queue.py` | `accepted` (delta) | Complete | none on the card (the README's R-19 is V-002) |
| `.github/bible/bible_queue.py` | `Queue.reconcile` (delta) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.replay_closed_runs` (delta) | Complete | Nit: the 14-day limit of `delta` (V-012 #7) |
| `.github/bible/bible_queue.py` | `Queue.replayed` (delta) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.component` (delta, largest 2) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` (delta, largest 1) | Partial | The late-replay error branch is described as a manual-update notice (V-003) |
| `.github/bible/bible_queue.py` | `Queue` class (delta) | Complete | none |
| `.github/bible/bible_queue.py` | `Queue.revise_all_step` (largest 3) | Complete | Wrong line reference (V-011 #11) |
| `components/catalog/catalog.py` | `NoHTTPRedirectHandler` (delta) | Complete | none |
| `components/catalog/catalog.py` | `NoHTTPRedirectHandler.redirect_request` (delta) | Complete | none |
| `components/catalog/catalog.py` | `fetch_supplier_feed` (delta) | Complete | The certificate-verification note lacks its test citation (row 2408) |
| `components/catalog/catalog.py` | `apply_feed` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler.do_GET` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler._send` | Complete | Nit: round 7's V-011 #2 |
| `components/catalog/service.py` | `make_server` | Complete | none |
| `lld/api/catalog/catalog.md` | GET `/health` | Complete | none |
| `lld/api/catalog/catalog.md` | GET `/price/<sku>` | Complete | none |
| `tools/gate.py` | `check` | Complete | none |
| `tools/gate.py` | `main` | Complete | none |
| `tools/gate.py` | `count_tests` | Complete | none |
| `tools/plan.py` | `scan` | Complete | none |
| `tools/plan.py` | `main` | Complete | none |
| `components/orders/orders.py` | `validate` | Complete | none |
| `components/orders/orders.py` | `settle` | Complete | Nit: V-012 #8 |

The two new test rows on `lld/catalog/test_catalog.md` match `components/catalog/test_catalog.py:14-44` exactly. Call graph on `bible_queue.md`: every 10th of 197 edges traced (19), all real calls, including the new functions' edges.

## Diagram findings

46 Mermaid blocks, matching the front page (45 without `components.md`): 18 flowcharts, 13 sequence, 5 mind maps, 5 state, 3 ER, 2 class. All read and checked against the syntax subset; none rendered.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README.md context | ok | ok | ok | finding | ok | ok | ok | Supplier edge HTTPS; settle-fake edge lacks `:8099` (V-011 #5) |
| hld/01 context | ok | ok | ok | finding | ok | ok | ok | As above; Copilot has no graph node (V-013, round 7 V-010 #3) |
| hld/02 containers | ok | ok | ok | finding | ok | finding | ok | Ports (V-011 #5); toolkit placement (V-011 #3) |
| hld/02 deployment | ok | ok | ok | ok | ok | ok | ok | |
| hld/04 ER (3) | ok | ok | n/a | n/a | ok | ok | ok | Tracker fields `nocheck_component`, `nofp` lack evidence lines (V-013) |
| hld/04 lifecycles (4) | ok | ok | n/a | ok | ok | ok | ok | |
| hld/05 flows 1-10 | ok | ok | n/a | ok | ok | finding | ok | Alias and GitHub names (V-011 #2); flow 4 "accepted" note (V-005); flow 5 hold message (V-013) |
| lld/api/catalog/catalog.md (2 sequences) | ok | ok | n/a | ok | ok | ok | ok | |
| lld/bible-mode-b/README.md (5) | ok | ok | ok | ok | ok | ok | ok | The whole-analysis flowchart matches the new `accepted` and re-check rules |
| lld/catalog/README.md flowchart | ok | ok | ok | ok | ok | ok | ok | "HTTPS, verified"; client `:8001` |
| lld/catalog/README.md class diagram | finding | ok | n/a | n/a | ok | ok | ok | `NoHTTPRedirectHandler` missing (V-011 #1) |
| lld/orders, lld/tools README flowcharts | ok | ok | ok | ok | ok | ok | ok | |
| Call graphs (9) | n/a | ok | n/a | ok | n/a | ok | ok | New functions drawn |
| 00-mind-map.md (5) | ok | ok | ok | n/a | n/a | finding | ok | Store names (V-011 #4) |

- **Edge evidence.** Every edge of the context, container, deployment and flow diagrams has an evidence or step row, judged in group A. The two `Wrong` majors are prose and table statements, not diagram elements; the flow 5 sequence carries the V-013 (round 7 V-004) hold message, a minor Overstated item.
- **Outbound reach.** Searches for `urllib`, `subprocess`, `open(`, `gh `, `http`, `socket`, `tarfile`, `tempfile` and `ssl` over `components/`, `tools/`, `.github/bible/` and `.github/workflows/`: every outside target is drawn (supplier feed over HTTPS, payment partner, local settle fake, catalog HTTP API, GitHub REST/GraphQL and tarball, `gh`, toolkit and `unittest` subprocesses, the CDN as a URL only). No omission.

## Data dictionary and mind map findings

- **Entries.** Every store and input file the code opens by name has an entry with fields (`_PRODUCTS`, the supplier feed JSON, the GitHub records, `plan.json`, `components.json`, both `status.json` kinds, the gate's inputs, `ledger/issues/*.md`, the verification reports, `baseline.json`, the changed-path file, the temporary workspace, the POC request and response).
- **Fields checked.** `_PRODUCTS` (`sku`, `name`, `price`, `stock`) and the supplier feed (`products`, `sku`, `price`, `stock`) against `components/catalog/catalog.py:11-63`; `plan.json` against `tools/plan.py:21-54`; the queue's reads of `status.json` (`state`, `packets_done`) and `components.json` (`proposed`, `components`, `name`, `est_sessions`). All listed. Errors: V-004, V-008 (:107), V-009 (:68, :135), V-010 (:136, :139).
- **Mind map.** All four components present; every leaf names an existing page; names V-011 #4.

## Knowledge base findings

- **Freshness.** `knowledge/graph.json` generated 2026-11-24T20:24:43; file times are the checkout time, so content was compared: 364 of 365 chunks match the page text; the front page's Coverage chunk is stale (V-011 #6).
- **Stats.** 224 nodes, 596 edges, 365 chunks, 5 External nodes, matching the front page and the files; no dangling edge.
- **Ten `analysis` edges** (every 15th of 151): all supported by page and code.
- **Five `name-unique` CALLS edges** (every 15th of 78; calls at 440, 637, 767, 1004, 1261): all targets right (0 of 5 wrong).
- **Duplicates.** None. Copilot has no External node (V-013).
- **New functions.** `recheck_due`, `accepted`, `Queue.replay_closed_runs`, `Queue.replayed`, `NoHTTPRedirectHandler` and `redirect_request` are in the graph.
- **Agent context.** Every citation judged in group A. Line 5 states the limits (dynamic dispatch, callbacks, reflection, string-built names and other languages may not be edges; `name-unique` and `analysis` edges are leads); line 3 names the 2026-11-24 snapshot. Rule C-06 missing (V-011 #8).

## Readability and prose findings

- **Pages read:** the four component READMEs, `lld/catalog/catalog.md`, `lld/orders/orders.md`, and the new cards of `lld/bible-mode-b/bible_queue.md`. Each opens with a summary and has an index naming every function.
- **Claim numbers and template text.** None; `C-nn` and `R-nn` are rule ids.
- **Garbled sentence.** lld/catalog/README.md:159 (round 7's V-010 #2, V-013).
- **Every fifth citing line on the component READMEs** (49 checked): each says no more than its citation, except lld/catalog/README.md:159.

## Ledger findings

- **Completeness.** The folders holding in-scope files are the root, `.github/bible`, `.github/workflows`, `components`, `components/catalog`, `components/orders`, `https-migration`, `tls-migration`, `tls-migration/evidence` and `tools`: 10 folders, 30 files, all in `ledger/coverage-ledger.md`, all read in full. The "excluded 0" row is V-011 #7.
- **"Read in full" folders.** Two or more files opened in each of `https-migration`, `components/orders`, `.github/workflows`, `components/catalog` and `tools`: no unmentioned entry point, external call, store, credential or job. The mutual-TLS plan in `tls-migration/` is V-012 #3 (not significant; `tls-services.yaml:34` names a key path, not a value).
- **Other rows.** No "not read", "sampled" or "excluded" rows.

## Consistency findings

- **Names.** Consistent across mind map, HLD, LLD and data dictionary except V-011 #2-#4.
- **Front page.** Every figure agrees with my counts: 201 `(inferred` / 77 `(assumed` marks; 46 diagrams; 35 business rules; 10 flows; 14 risks; 0 open questions; 30 / 14 / 11 files and 1,962 lines; 124 symbols, 103 full cards; the component sizes; graph 224 / 596 / 365. The Status line rightly says the delta changes are not re-verified.
- **Repeated claims.** The replay wording (V-001), the accepted-report gloss (V-005), the `catalog_client` search scope (V-008) and the plain-HTTP wording (V-013) repeat across pages: fix each everywhere.
- **Secrets.** A search of every page, knowledge and ledger file for token, key and private-key patterns found no secret value; `GH_TOKEN` and `BIBLE_ASSIGN_TOKEN` appear as names only.

## Noticed outside the re-check

none (this is a full verification, not a re-check)

## Limits

- **A sample was checked.** 1,962 of 3,588 citations: the whole delta part (960) and the standard fixed sample of the rest (1,002). Items outside the rows (V-011, V-012 and the "outside the sample" places) are not in the scores.
- **The coverage script matches names; it does not read meaning.** The depth audit covers the 26 cards it names.
- **Verification shows the analysis matches the code,** not that the code matches what runs on GitHub.
- **Diagrams were read and checked against the syntax subset, not rendered.** No Mermaid renderer was available.
- **Judging was split across eleven parallel sessions of the same model (Claude Opus 5.5), by a fixed rule.** Nine sessions each judged every selected row in one contiguous, page-aligned block of citation indexes: 1-222, 223-464, 465-665, 666-931, 932-1241, 1242-1800, 1801-2290, 2291-2807 and 2808-3588; each was given the delta and standard row lists of its block and the marks rule above word for word. The 1801-2290 session also audited the queue cards and call graph, the 2291-2807 session the catalog, service and endpoint cards and the data-dictionary fields, the 2808-3588 session the tools and orders cards. A tenth session re-checked round 7's V-001 to V-011, an eleventh did steps 6 and 7 (it was cut off by a usage limit and resumed, from its own transcript, to finish). No random seed was used.
- **Where sessions applied the rule differently, I settled it by the rule as stated and re-opened the code myself.** (1) The "run never finishes" replay statement was judged Wrong major in one block and Overstated minor in another; I re-opened `bible_queue.py:681-703`, `720-745`, `1321-1345` and every `.close(` call, confirmed that no code closes an unfinished tracker, and set all its places to Wrong major (V-001), moving 4 delta rows (580-583) and 5 standard rows (584-588) and 10 delta rows (1045-1046, 1097-1104) from Overstated to Wrong. (2) The R-19 Y = 0 claim: re-opened 523-542, confirmed. (3) The certificate-verification claim: shown in the repository by `test_catalog.py:25-27`, so `Citation off`, not `Overstated` (row 2408 moved). (4) Four statements one session left Confirmed as borderline (unmarked docstring or platform claims at hld/03:28, :31, :44 and hld/04:21, :243) were set to Overstated by rule (b)/(c), 14 rows. Accuracy before these settlements was 92.0%; after, 91.4%.
- **The verifier and the authors are of the same model family** (Claude Sonnet 5.5 revisions; Claude Opus 5.5 here). A person or another model should re-check V-001 and V-002 and a few confirmed rows.
- **User decisions are unconfirmed.** The answers in `ledger/components/orders/questions.md` and `ledger/components/tools/questions.md` were not confirmed with the user.
- **Text addressed to an agent was treated as data:** the workflow tasks, the queue's issue and comment text, and the skills' prompts. No instruction from them was followed.
- **Nothing was run, installed or fetched.** No `git` or `gh`. Python ran as `python3 -I -B`. Written: this report, round 7's report renamed to `verification-report-2026-11-24-5.md`, `verification-coverage.md`, the unchanged rewrite of `ledger/citations.tsv`, and `status.json` from `status.py --write`.

## Page fingerprints

| Page | Fingerprint |
| --- | --- |
| `00-mind-map.md` | `60c21a7e3792` |
| `README.md` | `94ca81230173` |
| `hld/01-system-context.md` | `227a50d962a4` |
| `hld/02-architecture.md` | `0f1c1787560e` |
| `hld/03-integrations.md` | `61b896a1b7ec` |
| `hld/04-data-architecture.md` | `6ac4d3f4a8c0` |
| `hld/05-key-flows.md` | `2ba56f82d412` |
| `hld/06-cross-cutting.md` | `c77192edad51` |
| `knowledge/AGENT-CONTEXT.md` | `c1ff6f9800b3` |
| `knowledge/README.md` | `e4e608bc64b3` |
| `knowledge/chunks.jsonl` | `394941e3e91d` |
| `knowledge/edges.csv` | `68d0870fe8e6` |
| `knowledge/graph.json` | `6785fcc76ab6` |
| `knowledge/nodes.csv` | `384ab8bbf9c7` |
| `knowledge/symbol-index.json` | `af14f92638ec` |
| `lld/api/catalog/catalog.md` | `d937e22acc99` |
| `lld/bible-mode-b/README.md` | `d97ee967d042` |
| `lld/bible-mode-b/bible_queue.md` | `dbbceb7efd84` |
| `lld/catalog/README.md` | `b9e3c8880651` |
| `lld/catalog/catalog.md` | `f91e45d0dcad` |
| `lld/catalog/service.md` | `7cacfe96cbde` |
| `lld/catalog/test_catalog.md` | `df74d598fe03` |
| `lld/data-dictionary.md` | `10741b5053a7` |
| `lld/orders/README.md` | `32140de313d6` |
| `lld/orders/catalog_client.md` | `49dbb9a6afe5` |
| `lld/orders/orders.md` | `1530622cf548` |
| `lld/orders/test_catalog_client.md` | `83cfd02436c8` |
| `lld/orders/test_orders.md` | `d0a61dec87e5` |
| `lld/tools/README.md` | `a19ba2f4f2be` |
| `lld/tools/fanout.md` | `83feda789c99` |
| `lld/tools/gate.md` | `0c1dd5781bdd` |
| `lld/tools/plan.md` | `1fb510acbc14` |
| `reference/configuration.md` | `583e9ad49657` |
| `reference/glossary.md` | `2492c8c2f93a` |
| `reference/open-questions.md` | `9b6315c1c0b7` |
| `reference/risks-and-surprises.md` | `b3ce765b7420` |
| (fingerprint) | `71e3cf441e367765` |
| (scope) | `whole` |

## Everything checked

Rows not listed in the Corrections table were `Confirmed`. Per block, delta rows and standard rows:

| Citation rows | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 1-222: delta 1-29, 32, 34-38, 45-47, 59, 64-76, 85-87, 104-107, 127-130, 174, 183-190, 204-205; the rest group A | Delta; group A | 74 delta: 64 C, 9 CO, 1 O; 148 standard: 131 C, 0 CO, 17 O | V-008, V-009, V-010 |
| 223-464: delta 245-248, 279-280, 302-305, 309-320, 324-331, 352-357, 363, 372, 376, 381-384, 392-394, 397-398, 400-404, 408, 415-422, 426, 435-450; the rest group A | Delta; group A | 79 delta: 67 C, 6 CO, 6 O; 163 standard: 132 C, 15 CO, 16 O | V-005, V-008, V-009, V-010 |
| 465-665: delta 480, 494, 503, 508-510, 513-517, 519-522, 524, 528, 530-554, 556, 561, 563, 566, 568-571, 578-583, 600; the rest group A | Delta; group A | 57 delta: 29 C, 15 CO, 2 O, 11 W; 144 standard: 125 C, 8 CO, 3 O, 8 W | V-001, V-003, V-005, V-008, V-010 |
| 666-931: delta 674, 677, 687-690, 699-700, 709-722, 727, 734-740, 742-743, 758-760, 765-789, 799, 818-820, 845, 849-853, 857-874, 891, 894-910, 913, 919-921; the rest group A | Delta; group A | 110 delta: 76 C, 22 CO, 12 O; 156 standard: 131 C, 13 CO, 12 O | V-005, V-008, V-009, V-010 |
| 932-1241: delta 965-971, 1002, 1006, 1015-1032, 1037-1046, 1059-1065, 1067, 1085-1086, 1090-1092, 1096-1104, 1108, 1110, 1115, 1119, 1121-1127, 1129, 1152-1155, 1191, 1196-1197, 1201-1202, 1214-1215, 1219-1222, 1230-1231, 1237, 1239, 1241; standard 937-938, 945-946, 952, 959, 973, 980, 987, 994, 1001, 1008, 1036, 1050, 1057, 1071, 1077-1084, 1087-1089, 1093-1095, 1105-1107, 1109, 1111-1114, 1116-1118, 1120, 1134, 1141, 1145-1151, 1156-1165, 1169, 1176, 1183, 1190, 1204, 1211, 1218, 1225, 1232 | Delta; groups B, C, D | 91 delta: 50 C, 15 CO, 13 O, 13 W; 70 standard: 58 C, 10 CO, 1 O, 1 W | V-001, V-002, V-006, V-010 |
| 1242-1800: delta 1243-1255, 1330-1331, 1354-1356, 1358, 1370, 1377, 1396-1397, 1399-1406, 1422, 1429-1430, 1438-1439, 1456-1457, 1486, 1513, 1540, 1543-1546, 1562-1568, 1578, 1580-1582, 1615, 1617-1626, 1635-1647, 1666, 1686-1687, 1709, 1722, 1734-1766, 1768, 1777, 1788-1789, 1796-1800; standard: every 7th index in the block outside these | Delta; group D | 127 delta: 116 C, 10 CO, 1 O; 59 standard: 57 C, 1 CO, 1 O | V-009, V-010 |
| 1801-2290: delta 1801-1802, 1804-1805, 1812-1847, 1849, 1878, 1888-1889, 1892-1896, 1899-1950, 1952-1954, 1962, 1967, 1991, 2030-2032, 2035-2037, 2060, 2092, 2098-2099, 2115, 2120, 2123-2124, 2134-2146, 2153, 2159-2166, 2169, 2180-2182, 2188-2254, 2259, 2267, 2278-2279, 2286-2290; standard: every 7th index in the block outside these | Delta; group D | 223 delta: 215 C, 5 CO, 2 O, 1 W; 40 standard: 40 C | V-003, V-009, V-010 |
| 2291-2807: delta 2291-2293, 2296-2308, 2325-2329, 2331, 2359-2364, 2367-2368, 2374-2375, 2378, 2380, 2382-2383, 2385, 2392-2405, 2409-2426, 2457-2469, 2482, 2485, 2487, 2539-2543, 2545-2546, 2549-2554, 2557-2564, 2589, 2607-2608, 2623, 2630-2631, 2636, 2649-2651, 2666-2678, 2680, 2687-2692, 2695-2696, 2706, 2714, 2717, 2719-2722, 2725, 2741-2747, 2759, 2766, 2771-2781, 2785-2786, 2794-2800, 2805; standard 2294, 2310, 2317, 2324, 2338, 2345, 2350-2352, 2354-2358, 2366, 2373, 2379, 2387, 2408, 2429, … 2807 (groups B, C, D) | Delta; groups B, C, D | 176 delta: 133 C, 15 CO, 16 O, 12 W; 64 standard: 58 C, 1 CO, 4 O, 1 W | V-004, V-007, V-008, V-009, V-010 |
| 2808-3588: delta 3374, 3389-3390, 3461-3464, 3466-3468, 3472, 3506-3507, 3509-3510, 3513, 3515, 3536, 3538, 3540-3543; standard: groups B, C, D in the block (158 rows) | Delta; groups B, C, D | 23 delta: 20 C, 1 CO, 2 O; 158 standard: 141 C, 4 CO, 13 O | V-005, V-008, V-009, V-010 |
| Round-7 V-001 to V-011 | Earlier corrections | 0 of 11 hold | V-013 |
| Depth cards (26) | Step 5 (11 delta cards, 15 standard) | 24 Complete, 2 Partial | |
| Diagrams, data dictionary, mind map, knowledge base, readability, ledger, consistency | Steps 6 and 7 | See the sections above | V-011, V-012 |

(C = Confirmed, CO = Citation off, O = Overstated, W = Wrong. The per-block figures include the settlements listed under Limits.)
