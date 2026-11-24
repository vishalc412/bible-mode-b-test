# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Analysis fingerprint | 6d2968d3765eaeee |
| Analysis snapshot | 24 in-scope files, 1,812 source lines, code of 2026-11-24 (baseline 2026-11-24T14:34:00), no version given (front page) |
| Repository at verification | 24 files in scope, 14 source-language files of which 11 hold code (3 empty `__init__.py`), 1,812 lines by my count; `.github/bible/bible_queue.py` has 1,336 lines; no drift from the stored inventory; no version given |
| Depth stated / depth found | deep / deep |
| Verified with | Claude Code (Claude Opus 5.5), standing in for the GitHub Copilot coding agent |
| Analysis produced with | Copilot coding agent (model not recorded) for planning, components, assembly and the first revisions; Claude Sonnet 5.5 standing in for Copilot for the revisions of 24 Nov 2026, including the round-4 and round-5 revisions (front page) |
| Sampling level | standard (a full verification: round 5's accuracy, 92.3%, is below the 95% a re-check needs) |
| Date | 2026-11-24 |

After corrections: every flagged statement re-checked: 14 of 16 confirmed.

The 16 are V-001 to V-016 of the round-5 report (now `verification-report-2026-11-24-3.md`). V-008 and V-009 do not fully hold: the listed places are fixed, but statements of the same kind remain on other pages (V-001, V-002 and V-004 here). This is round 6, a full verification, not a re-check, so there is no `Re-check of` row. No delta was applied since round 5 (`delta-log.md`'s newest row, 2026-11-24T14:34:00, was audited in round 4), so there is no delta part. Steps 1 to 8 of the skill were all done.

## Summary

The analysis is complete and its facts are, almost without exception, true. The coverage gate passes at deep with every measure at 100% (116/116 symbols, 98/98 full cards, 320/320 branch lines, 232/232 call-graph edges, 3,225/3,225 citations). Every one of the 16 cards audited for depth is Complete. No statement in the sample is Wrong or Unsupported, no correction is major, no omission is significant, and no secret value appears. The round-5 revision fixed what it was asked to fix: 14 of its 16 corrections hold in full, and the other two hold at every place round 5 named.

It is not a PASS because accuracy is 89.0%, below the 95% a PASS needs. Of the 1,285 sampled citations, 1,137 are confirmed, 6 cite the wrong lines and 142 are overstated. Almost all of the overstatements are one kind of slip, the one round 5 named. A statement rests on an absence across a file or the repository ("no build step", "only callers are tests", "a person merges it"), on a docstring or comment, or on library, `gh` or GitHub behaviour, and carries no `(inferred` or `(assumed` mark. The fact behind it is right in every case I or the judging sessions checked; the searches were repeated. Round 5 listed the places it found; the revision marked those places but did not sweep the other pages for the same kind, so the same slip is found again in places round 5's sample did not reach.

The fall from 92.3% to 89.0% is therefore not new errors: this round's sample has more HLD rows (848 in group A, against 746) and found the same unmarked kind in them.

Where the analysis is weakest:

- **Unmarked absences, docstrings and library behaviour** (V-001 to V-005, 119 of the 142 overstated rows). The correction is one sweep of every page, not a list of places.
- **Narrow wording slips** (V-007 to V-011): remote catalog traffic is plain HTTP only by default; the flow 5 outcome leaves out the 14-day condition; the delta hold issue is not opened again when one is open; two change-history phrases on `bible_queue.md`; `done` in `Queue.component` counts only this run.
- **Diagrams** (V-013): the agent-PR lifecycle has no merge by a person; flow 3 draws the review PR after the hold branch; flow 4 and the whole-analysis flowchart draw continuation as if any session could resume another; three edges have no evidence row.

Every problem has a specific correction below. Because the accuracy is below 95%, the next round must again be a full verification, not a re-check (`status.py` refuses a re-check below 95%). A page-wide sweep for the mark rule before then is what would lift the accuracy.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 116 / 116 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 98 / 98 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 320 / 320 (100.0%); 232 / 232 (100.0%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner; the two catalog GET routes have endpoint cards (`lld/api/catalog/catalog.md`) |
| Citations that resolve | 3225 / 3225 (100.0%) |
| Coverage gate | PASS (depth deep); calls into other components 2 / 2 |
| Citations in the analysis / checked | 3225 / 1285 sampled |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 1137 / 6 / 142 / 0 / 0 |
| Omissions (significant) / Inconsistent | 7 (0) / 30 |
| Accuracy / citation quality | 89.0% (1143/1285) / 88.5% (1137/1285) |
| Cards audited: Complete / Partial / Shallow / Wrong | 16 / 0 / 0 / 0 |
| Depth / depth, usable | 100.0% / 100.0% |

## How the sample was selected

The level is `standard`. The rows come from `ledger/citations.tsv` as `coverage.py` rewrote it in this session: 3,225 rows, byte-identical to the copy the revision left (SHA-1 `f798ec6a…` before and after).

- **Group A (848 rows: 1-848).** Every citation on `README.md`, `hld/*` and `knowledge/AGENT-CONTEXT.md` (judged like an HLD page, as checks.md Step 6 says).
- **Group B (34 rows).** Every other row labelled `inferred` or `assumed`: 853, 866, 1062-1064, 1145, 1873, 2114-2116, 2138-2140, 2212, 2566, 2571, 2578-2584, 2587-2589, 2598, 2628, 2704, 2706, 2709, 2801-2803.
- **Group C (83 rows).** Every other row whose nearest heading or bold title line above it contains rule, outbound, calls out, integration, security, secret, auth or permission: 992-1031, 1049-1061, 2118-2122, 2128-2129, 2547-2553, 2562-2565, 2567-2570, 2572-2573, 2773-2775, 2786-2788. All fall under "Business rules" (55) or "Outbound calls" (28) of the four component READMEs.
- **Group D (320 rows).** Every remaining row from 849 to 3225 whose index is divisible by 7.

**The fixed judging rule, applied the same way to every row.** A row is `Confirmed` when its cited lines support the statement as written and every part of the statement that rests on an absence found by a search across a file, several files, a component or the repository, on a comment or docstring, or on library, builtin, `gh`, runner or GitHub behaviour carries a mark in the same sentence, table cell or step. A mark is `inferred` or `assumed` with its source, inside parentheses: `(inferred: …)`, `(assumed: …)`, or the same words after a semicolon inside a parenthesis (as on `bible_queue.md:1092` and `plan.md:154`). Naming the source without one of these words ("line 71's comment", "as its docstring says") is not a mark. An absence that the cited lines show in full (the whole handler, function or job is cited) rests on code and needs no mark. Such a part without a mark makes the row `Overstated`. Rows of one statement share its verdict, except a row whose lines show none of the statement, which is `Citation off`. Every absence was searched again.

## Earlier corrections re-confirmed

| Round-5 item | Holds? | Re-opened |
| --- | --- | --- |
| V-001 replay wording | Yes. All the replay sites (hld/04:228, hld/05:242, :276, :283, lld/bible-mode-b/README.md:180, :182, R-12 at :257, bible_queue.md:2179, :2483, data-dictionary:139) now say "never replayed if a person closes the tracker or the run does not finish", with the inferred mark, the 14-day writer limit and the update-issue text. The two remaining "by hand" phrases match the code's comment at 1049 | `.github/bible/bible_queue.py:385-391,600-616,1036-1064,1226-1282` |
| V-002 R-15 | Yes. R-15 counts closed chunk issues of the run created since the later of the hold release and the merge into the default branch | `.github/bible/bible_queue.py:736-770` |
| V-003 `pr_files` output | Yes. The Output paragraph says `Queue.run` catches the error per component; it agrees with the `Queue.component` Errors paragraph | `.github/bible/bible_queue.py:612-615,645-656,836-870` |
| V-004 `Queue.component` run scope | Yes for steps 2 and 6 and `start_chunk`. Step 4's `done` still reads "every closed chunk issue of the component" (V-011 here, a new row) | `.github/bible/bible_queue.py:500-507,695-735,786-812` |
| V-005 answers on the session PR | Yes, on README.md, hld/01 and AGENT-CONTEXT. The `@copilot` detail on hld/01:58 rests on line 103, which is not cited (V-014 here) | `.github/bible/bible_queue.py:100-104,850-858` |
| V-006 tracker labels | Yes | `.github/bible/bible_queue.py:618-622,1320-1324` and every `create_issue` call |
| V-007 first failure | Yes, hld/04:130 and :140 | `.github/bible/bible_queue.py:580-602` |
| V-008 unmarked statements on the front page, HLD and agent context | **No, not fully.** Every place listed is now marked. The same kind remains elsewhere on those pages: README:23, hld/01:58, hld/02:115-152, hld/03:32, :48, :49, :59, hld/04:145, :163, :214, :223-225, hld/05:171-236, :360, :400, :444, :482, AGENT-CONTEXT:38, :88, :90, :103 (V-001 to V-004 here) | `components/orders/catalog_client.py:1-29`; `tools/fanout.sh:1-31`; `.github/workflows/poc-assign-copilot.yml:66-69`; `.github/bible/bible_queue.py:28,875`; repository searches |
| V-009 the same on LLD and reference pages | **No, not fully.** Every place listed is now marked. The same kind remains: lld/orders/README.md:23, :129, catalog_client.md:151, glossary.md:24, :31, risks-and-surprises.md:13, :15, :17, :22, lld/tools/README.md:23, :30, :68, plan.md:111, configuration.md:10, :17, :32, :55, lld/catalog/README.md:147, :159 (V-001, V-002, V-004, V-005 here) | `.github/bible/bible_queue.py:71,252-286`; `components/catalog/service.py:42`; `tools/gate.py:73-77`; `components/catalog/catalog.py:36-47` |
| V-010 pull request fields | Yes, data-dictionary:112 | `.github/bible/bible_queue.py:252-286,374` |
| V-011 citation off | Yes, every listed citation is re-pointed. data-dictionary:182 names the toolkit's `next.py` in words and says why its lines are not cited, which I accept as a stated limit | the ranges cited in revision row R5-V-011 |
| V-012 16 diagram items | Yes, all 16: flow 1 order, flow 4 Done order, flow 3 hold, no `runner -> copilot`, the evidence rows, solid edges with legends, the plan job, `[*] --> Ready`, `/health` without the impossible `else`, the continuation for verify-all and revise-all, the class rows, and 220 distinct call-graph edges with no duplicates | `.github/bible/bible_queue.py:166-173,354-368,528,797-805,1018-1050,1114-1121,1160-1207,1305-1325`; `components/catalog/service.py:25-27` |
| V-013 diagram syntax | Yes. All 46 blocks scanned against `mermaid-syntax.md`: nothing left | `.github/skills/analyzing-a-codebase/references/mermaid-syntax.md` |
| V-014 10 naming and count items | Yes, all 10 | `tools/plan.py:14`; `.github/bible/bible_queue.py:981-985,1288-1300`; `.github/workflows/bible-plan.yml:53` |
| V-015 22 omissions | Yes, all 22, including the two new hld/04 diagrams (checked against 405-425 and 619-627) and the container stores. Item 11 (the `delta` caveats) is on the V-001 sites but not on hld/04:228 or the `assemble_phase` step 8 (V-015 here) | `.github/bible/bible_queue.py:405-425,524-533,619-628,1243-1272,1288-1300`; `tools/gate.py:73-77` |
| V-016 `plan.md` `main` errors | Yes, `plan.md:154`, marked assumed | `tools/plan.py:21-62` |

The revision's own items hold. R5-N-02's counts are right: 88 `(inferred` and 19 `(assumed` marks on the pages, 46 Mermaid blocks, 211 nodes, 566 edges and 346 chunks, 346 lines in `chunks.jsonl`, 3,225/3,225 citations. R5-N-03's four depth nits were applied (bible_queue.md:2175, :2344-2346; gate.md:257, :282). R5-N-04 records points left as they are.

## Corrections

Every correction is minor; none is major.

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | Absences found by a search, with no mark (65 rows): 20 (README:23, "no production deployment topology"), 21-25 (README:23, "no source evidence for the nightly schedule"), 54-56 (hld/01:58, "no application authentication layer"), 131-132 (hld/02:115), 133-134 (:116), 146-148 (:120, "no build step"), 182-200 (hld/02:149-152, four "no profiles" cells), 213 (hld/03:32, "no HTTP route" in `orders`), 366-367 (hld/04:223, "not written by `tools/gate.py`"), 368-375 (:224), 376 (:225, `baseline.json` not written), 493-496 (hld/05:236, "only here, at the Done step"), 782-785 (AGENT-CONTEXT:88, "not as a general workflow step"), 1055-1056 (lld/bible-mode-b/README.md:280, "no fallback"), 1372 (bible_queue.md:1097, "no constant holds it"), 2142 (lld/catalog/README.md:147), 2737 (lld/tools/README.md:23), 2751 (:30), 2765 (:68), 3052 (configuration.md:17), 3164 (glossary.md:31, the image is "not fetched"), 3199 (risks-and-surprises.md:22). Outside the sample, the same kind: hld/02:25, hld/06:83, lld/catalog/README.md:159, risks-and-surprises.md:13 | Overstated | minor | Each fact holds; the searches were repeated. But each rests on an absence across a file, a component or the repository, which the cited lines cannot show. For 1055-1056, the late replay after Done does catch the error and comments on the tracker (1045-1049) | `.github/bible/bible_queue.py:875,1038,1043,1045-1049,1223-1283,1244-1245`; `tools/gate.py:42-117`; `components/catalog/catalog.py:6,32-39`; repository searches for build, profile, route, `write`, `open(`, `baseline.json`, `deferred_updates(`, `image_url`, `unittest` and `fetch_supplier_feed` | Add `(inferred: <the search and what it found>)` to each, in the same sentence or cell. For 1055-1056 also say that the late replay catches it (1045-1049). Then search every page for "no ", "not ", "only ", "never" and "none" and mark each absence the cited lines do not show in full |
| V-002 | The catalog client's purpose and callers, from its docstring or a search, with no mark (17 rows): 248-252 (hld/03:59), 727-728 (AGENT-CONTEXT:38), 789-793 (:90), 2527 (lld/orders/README.md:23), 2597 (:129), 2646 (lld/orders/catalog_client.md:151), 3150 (glossary.md:24), 3185 (risks-and-surprises.md:17) | Overstated | minor | The docstring (lines 1-4) names the separate-service use; a search finds `catalog_client` imported only by the test file. README.md:23 already marks this correctly | `components/orders/catalog_client.py:1-4,29`; `components/orders/test_catalog_client.py:37-62` | Use the README.md:23 wording: "(inferred: its docstring, `catalog_client.py:1-4`, names the separate-service use, and a search finds `catalog_client` imported only by `test_catalog_client.py`)" |
| V-003 | "A person merges" and "the queue never merges into the default branch", with no mark (17 rows): 333-337 (hld/04:163), 356-357 (hld/04:214), 459-460 (hld/05:171), 464-465 (:222), 476 (:229), 483 (:232), 487-490 (:234). Outside the sample: hld/04:145 | Overstated | minor | The code only reads `merged_at` (715-716, 995-1011). That a person merges rests on the module docstring (line 28) and on `gh.merge` being called only at line 875, for session PRs into the component branch | `.github/bible/bible_queue.py:28,715-716,875,995-1011` | Add "(inferred: the module docstring at line 28, and `merge` is called only at line 875, for session pull requests into the component branch)" |
| V-004 | Library, builtin, `gh`, runner or GitHub behaviour with no mark (21 rows): 176-178 (hld/02:142, managed runner image), 239-240 (hld/03:48, HTTPS 443), 484-486 (hld/05:233, GitHub closes the issue), 553 (hld/05:360, `urlopen` sends GET), 572 (:400, `urlopen` raises `HTTPError`), 585-589 (:444, file, AST and JSON errors), 828-829 (AGENT-CONTEXT:103, `apply_feed` raises), 3003 (plan.md:111), 3073 (configuration.md:32, `gh` reads `GH_TOKEN`), 3108 (:55, `RUNNER_TEMP`), 3178 (risks-and-surprises.md:15). Outside the sample: hld/03:49 (`gh` configuration), hld/05:482 (`set -euo pipefail`) | Overstated | minor | Each behaviour is right but belongs to a library or service, not to the repository's code. For 585-589 it also says more: an invalid `status.json` is caught by the gate and printed as FAIL | `.github/workflows/poc-assign-copilot.yml:66-69`; `components/orders/catalog_client.py:22`; `components/orders/orders.py:50-51`; `components/catalog/catalog.py:42-47`; `tools/plan.py:28-45`; `tools/gate.py:95-98`; `.github/bible/bible_queue.py:942,948-949` | Add `(assumed: <library or service> behaviour)`, and for 484-486 "(assumed: GitHub closes it when the PR saying 'Fixes #N' is merged, as the comment at lines 948-949 says)". For 585-589 add "an invalid `status.json` makes the gate print FAIL (95-98)" |
| V-005 | Statements from a comment, with no mark (4 rows): 47-48 (README:68, the settle fake is "development only"), 1134 (bible_queue.md:25, `COMPARE_MAX` is GitHub's limit "(line 71's comment)"), 3045 (configuration.md:10, a repository secret) | Overstated | minor | Each rests on a comment: `orders.py:11`, `bible_queue.py:71`, `poc-assign-copilot.yml:4-6`. hld/01:64 marks the first correctly | `components/orders/orders.py:11`; `.github/bible/bible_queue.py:71,271`; `.github/workflows/poc-assign-copilot.yml:4-6` | Add "(inferred: the comment at …)" to each |
| V-006 | hld/04:26 (outside the sample; the sentence has no citation row) | Inconsistent | minor | The sentence says a search of `components/` for `open(` "finds none". Repeating it finds four `urlopen(` calls. The conclusion, no file store, still holds | `components/catalog/catalog.py:38`; `components/orders/orders.py:50`; `components/orders/catalog_client.py:22`; `components/orders/test_catalog_client.py:32` | "a search of `components/` for `open(` finds only `urlopen` calls (inferred)" |
| V-007 | Rows 609-611 (hld/06:31), 821-827 (AGENT-CONTEXT:102) | Overstated | minor | Settlement is plain HTTP. Remote catalog requests are plain HTTP only by default: `DEFAULT_CATALOG_URL` is `http://127.0.0.1:8001`, and `CATALOG_URL` can name any URL. Line 11 is not cited | `components/orders/catalog_client.py:11,14-23` | "remote catalog requests use plain HTTP by default (`DEFAULT_CATALOG_URL`, line 11; `CATALOG_URL` may override it)"; cite line 11 |
| V-008 | Rows 509-511 (hld/05:242, flow 5 outcome) | Overstated | minor | A tracker whose `Updated` line is older than 14 days does not hold the change back; update issues are created at once. Step 4 and the diagram say so; the outcome sentence does not | `.github/bible/bible_queue.py:391,1226-1229` | "While an analysis run is open (its tracker updated in the last 14 days) …" |
| V-009 | Rows 959 (lld/bible-mode-b/README.md:180), 1019 (:258, R-13) | Overstated | minor | The hold issue for more than 10 touched components is created only when no open issue labelled `bible-delta` and `bible-needs-human` exists | `.github/bible/bible_queue.py:1255-1264` (the check at 1257) | Add "unless such a hold issue (`bible-delta`, `bible-needs-human`) is already open" |
| V-010 | Rows 1323 (bible_queue.md:961), 1337 (:996). Outside the sample: :424 ("Since 24 Nov 2026 …") | Overstated | minor | The members of `WORK_EVENTS` and the `AGENT_APP` test are right, but "the new member", "this is the change that lets" and "since 24 Nov 2026" are change history no code line shows | `.github/bible/bible_queue.py:70,226-227,234` | Describe what the code does now: "a session that ended in failure also shows up"; "so a pull request on which Copilot only failed, or only finished, is still recognised as Copilot's". Drop the date |
| V-011 | Row 1666 (bible_queue.md:1934, `Queue.component` step 4) | Overstated | minor | `done` counts the closed chunk issues of this run only, because `run_issues` adds `bible-run-<n>` | `.github/bible/bible_queue.py:505-506,756,771` | "where `done` counts every closed chunk issue of this run (label `bible-run-<n>`) for the component" |
| V-012 | Citation off (6 rows): 209 (hld/03:30), 237 (hld/03:47), 384 (hld/04:227), 406 (hld/04:232), 896 (lld/bible-mode-b/README.md:30), 1568 (bible_queue.md:1643) | Citation off | minor | Each statement is true, but its cited lines show something else or stop short | 209: `bible-delta.yml:11-12` (`paths-ignore`); 237: `bible_queue.py:1302` (`GH_TOKEN`); 384: `bible_queue.py:89` (`MAX_NOCHECK`); 406: `poc-assign-copilot.yml:34-47`; 896: `bible-delta.yml:19`; 1568: `bible_queue.py:557` | Cite the lines given; for 1568 also re-cite the next row (:1644) as 558 |
| V-013 | Diagrams and their evidence tables (Inconsistent, 11 items) | Inconsistent | minor | See the list below this table | as given per item | Fix each as described |
| V-014 | Names, uncited text and other inconsistencies (Inconsistent, 18 items) | Inconsistent | minor | See the list below this table | as given per item | Fix each as described |
| V-015 | Omissions (7, none significant) | Omission | minor | See the list below this table | as given per item | Add each point |

**V-013, diagram and evidence inconsistencies:**

1. **hld/02 containers.** The edge `github -->|assigns issues| copilot` has no row in the evidence table. Add `bible_queue.py:166-173`, as the deployment table has.
2. **hld/02 deployment.** The edge `repo --> runner` has no row in the edge table. Add `bible-plan.yml:40-42`, `bible-queue.yml:28-30` and `bible-delta.yml:23-25`.
3. **hld/04, agent-session PR lifecycle.** The paragraph above it says plan, assemble, verify-all, revise-all and update PRs target the default branch and a person merges them. The diagram's only merge state is `MergedToComponentBranch`. Add `Ready --> MergedByPerson` and `MergedByPerson --> [*]` (`bible_queue.py:28,680,1034,1151,1282`).
4. **hld/04, component-row lifecycle.** `SESSION_MERGED --> SESSION_STARTING` also covers "assigns a verification", but a verification is shown at once as `verify running` (`bible_queue.py:811-819`).
5. **hld/04, component-row lifecycle.** `WAITING_ANSWERS --> RUNNING` has no evidence row (`bible_queue.py:850-865`).
6. **hld/05 flow 3.** The review PR is drawn after the hold and revision `alt` with no condition. The code checks a clean PASS whose fingerprints match first (778-782), then the hold (797), then the revision (806), then verifies (811). Make the clean PASS the first branch.
7. **hld/05 flow 4.** The continuation `alt` is drawn only for the assembly PR. Step 10 and the code continue verify-all and revise-all PRs too (1022-1025, 1117-1120).
8. **hld/05 flow 5.** No branch for "no `components.json` or `baseline.json`: log only" (1243-1246), which step 6 and the failure paths state (a D5 nit).
9. **lld/bible-mode-b/README.md, whole-analysis flowchart.** One shared `cont` node has edges back to `assemble`, `verify` and `revise`, so the drawing allows verify → continue → assemble. A continuation returns to the same session's PR (1022-1025, 1117-1120, 1158-1206). Draw one continuation per session kind.
10. **lld/api/catalog/catalog.md:40, :57, :87.** Both route cards list the handler's catch-all 404 "not found". Neither route can return it: a `/health` or `/price/…` path never reaches `service.py:34`. Move it to the endpoint index or the handler card.
11. **Sequence aliases** (lld/api/catalog/catalog.md:48, :95-96; hld/05 flows 7 and 9). `do-GET`, `catalog-client.py`, `remote-price` and `price-of` differ from the real names because the alias rule bans underscores. Use a readable alias such as "price lookup" (a D7 nit).

**V-014, names, uncited text and other inconsistencies:**

1. **hld/06:62.** The opening clause and "one retry before a human hold" have no citation on that line. Cite `bible_queue.py:574-601` and the rows at :66-67.
2. **hld/02:117.** Only the queue's concurrency group is cited; add `bible-plan.yml:29-31` (a nit).
3. **lld/tools/README.md:91-92.** The "Data dictionary entry" column says there is none for `plan.json` and the artifacts, but `lld/data-dictionary.md` has both. Link them, as round 5 did for the catalog README.
4. **Knowledge graph and front matter.** One outside system has several names: `external:GitHub API`, `external:GitHub CLI` and `external:GitHub`; "Payment partner" and `external:partner-legacy.internal/settle`; "Local settle fake" and `external:localhost:8099/settle`. Use one name each.
5. **hld/04 and lld/data-dictionary.md Files tables.** The store named "Temporary gate workspace" elsewhere is "Gate tarball and extracted worktree" there. Use one name.
6. **Unescaped `|` in table code spans** split the cells on GitHub: lld/catalog/README.md:59, lld/tools/README.md:24, :76, :99. Escape as `\|`.
7. **hld/01:21.** "Not one deployed service" has no citation; cite `README.md:1-7` as README.md:23 does.
8. **hld/01:58.** The `@copilot` detail rests on `bible_queue.py:103`, which is not cited.
9. **lld/data-dictionary.md:89.** "`delta` also reads each component's `paths` through `components.rows_of`" rests on toolkit code outside the inventory, uncited and unmarked; line 1250 only calls `rows_of(catalog)`. Add "(inferred: the toolkit's `rows_of`, outside the inventory)".
10. **bible_queue.md:1644.** The second `Queue.held` branch row cites 559 for the test at 558 (with V-012's row 1568).
11-18. **Unmarked statements outside the sample** (the V-001, V-003, V-004 and V-010 kinds): hld/02:25, hld/06:83, lld/catalog/README.md:159, risks-and-surprises.md:13, hld/04:145, hld/03:49, hld/05:482 and bible_queue.md:424. Fix them with the sweep in V-001.

**V-015, omissions (none significant):**

1. **hld/04:228.** "Replayed into update issues" leaves out the `delta` cases: with no `components.json` or baseline the paths are dropped with only a log line (1243-1246); more than 10 components give a hold (1255-1264); a component with an open `bible-delta` issue is skipped (1270-1272). Round 5's V-015 item 11 asked for this wherever the replay sentence is used.
2. **bible_queue.md:2172 (`Queue.assemble_phase` step 8).** The same `delta` cases.
3. **hld/05:234 (flow 4 step 13).** A finished revise-all PR that ends unfinished is continued as in step 7 (1117-1120).
4. **lld/bible-mode-b/README.md:259 (R-14).** An empty comparison list is refused too, when GitHub counts changed files (268).
5. **lld/catalog/catalog.md:98.** `price_of`'s "Called by" leaves out `CatalogTest.test_price_of_known_sku` (`test_catalog.py:8`).
6. **bible_queue.md, `Queue.assemble_phase`.** The `pr_files` error inside `by_this_run` (959), uncaught and handled by `reconcile`, is not named (a nit).
7. **lld/catalog/service.md, `make_server`.** The bind `OSError` from the constructor is not mentioned (a nit).

## Coverage findings

- **The gate passes.** I ran `coverage.py --depth deep --report verification-coverage.md` myself. It returned PASS (exit 0) with every measure at 100%: 11/11 files, 116/116 symbols, 98/98 full cards, 0/0 scanned routes, 3,225/3,225 citations, 320/320 branch lines, 232/232 call-graph edges, 17/17 front matter and 2/2 cross-component calls. It counted 24 files in scope, 11 source files and 35 analysis pages read.
- **Drift:** none since the stored inventory.
- **Exemptions:** `ledger/not-documented.md` does not exist, so nothing is exempt.
- **Totals.** The front page gives 24 files, 14 source-language files of which 11 hold code, 1,812 lines and 3,225/3,225 citations. These agree with the gate and my count (1,336+47+49+12+29+51+66+12+31+117+62 = 1,812).
- **Calls into other components.** Both calls from `orders` into `catalog` (`components/orders/orders.py:20,40`) are cited on the calling cards.

## Depth findings

Selection. The eleven non-empty source files in path order are `.github/bible/bible_queue.py`, `components/catalog/catalog.py`, `components/catalog/service.py`, `components/catalog/test_catalog.py`, `components/orders/catalog_client.py`, `components/orders/orders.py`, `components/orders/test_catalog_client.py`, `components/orders/test_orders.py`, `tools/fanout.sh`, `tools/gate.py` and `tools/plan.py`. The five largest are `bible_queue.py` (1,336), `gate.py` (117), `test_catalog_client.py` (66, a test file, so its rows are not cards), `plan.py` (62) and `orders.py` (51). The route file is `service.py`, which is also the 3rd in path order; the 7th is the test file. Three largest functions each by `ast` span (`plan.py` has two), plus both catalog routes.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` (937-1050) | Complete | Nits: step 8 leaves out the `delta` cases (V-015 #2); the `pr_files` error at 959 is not named (V-015 #6) |
| `.github/bible/bible_queue.py` | `Queue.component` (708-819) | Complete | Step 4's `done` scope is too wide (V-011); every branch, bound, hold and choice matches |
| `.github/bible/bible_queue.py` | `Queue.revise_all_step` (1074-1152) | Complete | none |
| `tools/gate.py` | `check` | Complete | none |
| `tools/gate.py` | `main` | Complete | Nit: a truthy non-list `passes_done` raises `TypeError` at 109 |
| `tools/gate.py` | `count_tests` | Complete | none |
| `tools/plan.py` | `scan` | Complete | none |
| `tools/plan.py` | `main` | Complete | none; the Errors paragraph is present |
| `components/orders/orders.py` | `order_total` | Complete | none |
| `components/orders/orders.py` | `validate` | Complete | none |
| `components/orders/orders.py` | `settle` | Complete | Nit: "Posts" is library behaviour without a mark |
| `components/catalog/service.py` | `CatalogHandler.do_GET` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler._send` | Complete | none |
| `components/catalog/service.py` | `make_server` | Complete | Nit: the bind `OSError` (V-015 #7) |
| `lld/api/catalog/catalog.md` | GET `/health` | Complete | The catch-all 404 is listed although the route cannot return it (V-013 #10) |
| `lld/api/catalog/catalog.md` | GET `/price/<sku>` | Complete | The same 404 point |

## Diagram findings

There are 46 Mermaid blocks, which matches the front page (45 without `components.md`). All were read and scanned by script against the toolkit's syntax subset; none was rendered.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README.md context | ok | ok | ok | ok | ok | ok | ok | Round-5 edge and evidence fixes hold |
| hld/01 context | ok | ok | ok | ok | ok | ok | ok | |
| hld/02 containers | ok | ok | ok | ok | ok | ok | ok | Stores drawn; `github -> copilot` has no row (V-013 #1) |
| hld/02 deployment | ok | ok | ok | ok | ok | ok | ok | `repo -> runner` has no row (V-013 #2) |
| hld/04 ER `_PRODUCTS` | ok | ok | n/a | n/a | ok | ok | ok | |
| hld/04 ER tracker hidden blocks (new) | ok | ok | n/a | n/a | nit | ok | ok | No key column; matches 405-425, 1317-1322 |
| hld/04 ER plan | ok | ok | n/a | n/a | ok | ok | ok | Labels quoted |
| hld/04 issue lifecycle | ok | ok | n/a | ok | ok | ok | ok | "first failure" |
| hld/04 agent-PR lifecycle | finding | ok | n/a | ok | ok | ok | ok | No merge by a person (V-013 #3) |
| hld/04 review-PR lifecycle | ok | ok | n/a | ok | ok | ok | ok | |
| hld/04 component-row lifecycle (new) | ok | ok | n/a | ok | ok | finding | ok | Two edges (V-013 #4, #5) |
| hld/05 flows 1-10 | ok | nit | n/a | ok | finding | nit | ok | Flow 3 order, flow 4 continuation, flow 5 log-only branch (V-013 #6-#8); "Python caller", "Repository files" generic; renamed aliases |
| 00-mind-map.md (5) | ok | ok | ok | n/a | n/a | ok | ok | |
| components.md | n/a | ok | ok | ok | n/a | ok | ok | |
| lld/catalog/README.md (2) | ok | ok | ok | ok | ok | ok | ok | |
| lld/orders/README.md | ok | ok | ok | ok | ok | ok | ok | |
| lld/tools/README.md, gate.md, plan.md | ok | ok | ok | ok | ok | ok | ok | |
| lld/bible-mode-b/README.md structure, sequence, states, classes | ok | ok | ok | ok | ok | ok | ok | POC node added |
| lld/bible-mode-b/README.md whole-analysis | ok | ok | ok | ok | finding | ok | ok | Shared continuation node (V-013 #9) |
| lld/bible-mode-b/bible_queue.md call graph | n/a | ok | n/a | ok | n/a | ok | ok | 220 edges, no duplicates; 16 traced edges all in the code |
| Other call graphs | n/a | ok | n/a | ok | n/a | ok | ok | HTTP labels; `settle -> urlopen` drawn |
| lld/api/catalog/catalog.md (2 sequences) | ok | ok | n/a | ok | ok | nit | ok | Renamed aliases (V-013 #11) |

- **Edge evidence.** Every edge of the context, container, deployment and flow diagrams was judged through its evidence or step rows, in group A. The edges with no row are V-013 #1, #2 and #5. No dashed edge remains.
- **Outbound reach.** I repeated the searches for `urllib`, `subprocess`, `open(`, `gh `, `http`, `socket`, `tarfile` and `tempfile` over `components/`, `tools/`, `.github/bible/` and `.github/workflows/`. Every outside target is drawn: supplier feed, payment partner, local settle fake, GitHub API, `gh`, the POC `gh api` call, the catalog HTTP API and the CDN as a URL only. The gate's `unittest` subprocess is local and is in hld/03.
- **D1.** Every required diagram is present.

## Data dictionary and mind map findings

- **Entries.** Every store and input file the code opens by name has an entry with fields: `_PRODUCTS`, the GitHub records, the temporary gate workspace (with `bible-whole-`), `plan.json`, `components.json`, both `status.json` kinds, `inventory.md`, `risks.md`, `tests-report.md`, `ledger/issues/*.md`, the verification reports, `baseline.json`, the changed-path file, the tarball, and `request.json`/`response.json`.
- **Fields checked.** `_PRODUCTS` has `sku`, `name`, `price` and `stock`. `plan.json` has `version`, `passes`, `components` and each component's `sources`, `tests`, `test_count`, `functions` and `http_sites` (`plan.py:21-54`). `components.json` lists all 19 keys. There are no relational tables and no spreadsheets.
- **Errors.** The `paths` field read is uncited toolkit behaviour (V-014 #9); the Files-table name differs (V-014 #5).
- **Mind map.** All four components are present; every leaf names an existing page; the nested list matches the root map.

## Knowledge base findings

- **Freshness.** `knowledge/graph.json` was generated at 2026-11-24T16:54:03. Every file carries the checkout time (16:56), so file times cannot show whether a page changed after the graph was built. The stats (211 nodes, 566 edges, 346 chunks) match the front page, and `chunks.jsonl` has 346 lines.
- **Ten `analysis` edges** (every 14th of 148): all supported, among them `bible_queue.py` WRITES the temporary gate workspace (886, 295), `catalog.py` WRITES `_PRODUCTS` (46-47), tools WRITES `plan.json` (`plan.py:55-57`) and `gate.py` READS `risks.md` (52).
- **Five `name-unique` CALLS edges** (every 14th of 72): the calls at 438, 576, 701, 1033 and 1165; all five targets are right (0 of 5 wrong).
- **Duplicates.** One outside system under several names (V-014 #4). "Analysis toolkit" is typed external although it is in-repository code (a nit).
- **Agent context.** Every citation was sampled in group A. Line 5 states the limits (dynamic dispatch, callbacks, reflection, string-built names and other languages may not be edges; `name-unique` and `analysis` edges are leads); line 3 names the 2026-11-24 snapshot.

## Readability and prose findings

- **Pages read:** the four component READMEs, `lld/orders/orders.md`, `lld/tools/gate.md` and `lld/catalog/service.md`. Each opens with a facts table and a summary, has an index listing every function, and is in a sensible order. Every in-page and cross-page anchor resolves.
- **Claim numbers and template text.** None. `C-nn` and `R-nn` are rule ids defined in their tables.
- **Table cells.** Unescaped `|` in code spans breaks four rows on GitHub (V-014 #6).
- **Every fifth citing sentence on the component READMEs** (catalog 10 of 51, orders 8 of 42, tools 8 of 40, bible-mode-b 18 of 94): each says no more than its citation, except two unmarked absences (lld/catalog/README.md:159, lld/bible-mode-b/README.md:280; V-001). The HLD pages and the agent context were judged in full in group A.

## Ledger findings

- **Completeness.** The folders holding in-scope files are the root, `.github/bible`, `.github/workflows`, `components`, `components/catalog`, `components/orders`, `tls-migration`, `tls-migration/evidence` and `tools`. Each has rows in `ledger/coverage-ledger.md`, and its totals (9 folders, 24 files) are right.
- **"Read in full" folders.** I opened two or more files each in `components/orders`, `components/catalog`, `.github/workflows`, `tools` and `tls-migration`. None holds an entry point, external call, store, credential or schedule the analysis does not mention. The client-key and kit paths in `tls-migration/tls-services.yaml` are planning configuration (not significant).
- **Other rows.** There are no "not read", "sampled" or "excluded" rows.

## Consistency findings

- **Names.** Components and outside systems carry the same names across the mind map, HLD, LLD and data dictionary, except the graph's outside-system nodes and the gate workspace's Files-table name (V-014 #4, #5).
- **Front page.** These figures agree with the pages, my counts and the gate: 4 stores; 31 business rules (5 + 5 + 18 + 3); 88 `(inferred` and 19 `(assumed` marks; 46 diagrams (45 without `components.md`); 10 flows, 13 risks and 0 open questions; 24/14/11 files and 1,812 lines; 211, 566 and 346 in the graph. The Status line rightly says that the round-5 changes are not re-verified.
- **Repeated claims.** The unmarked absence and docstring statements repeat across pages (V-001 to V-003); a sweep fixes them all.
- **Secrets.** I searched every analysis page and knowledge file for token, key and private-key patterns. No secret value was found. `GH_TOKEN` and `BIBLE_ASSIGN_TOKEN` appear as names only; the 40-hex values are git blob ids in `cites` comments and `progress.md`.

## Noticed outside the re-check

none (this is a full verification, not a re-check)

## Limits

- **A sample was checked.** 1,285 of 3,225 citations, by the fixed groups above. Statements outside the sample that were noticed are V-001, V-003, V-004, V-010 and V-014 items marked "outside the sample"; they are not in the scores.
- **The coverage script matches names; it does not read meaning.** The depth audit covers the 16 cards it names.
- **Verification shows the analysis matches the code,** not that the code matches what runs on GitHub.
- **Diagrams were read and scanned for the toolkit's syntax subset, not rendered.** No Mermaid renderer was available.
- **The judging was split across nine parallel sessions of the same model (Claude Opus 5.5), by a fixed rule.** Seven sessions each judged every selected row in one contiguous block of citation indexes: 1-200, 201-407, 408-599, 600-848, 849-1128, 1129-2060 and 2061-3225. The 1129-2060 session also audited the three `bible_queue.py` cards and the call graph; the 849-1128 session the two endpoint cards; the 2061-3225 session the other eleven cards. An eighth session did steps 6 and 7, and a ninth re-confirmed round 5's V-001 to V-016. Every session applied the judging rule stated under "How the sample was selected"; the one borderline mark form (row 1365, "; assumed:" inside a parenthesis at `bible_queue.md:1092`) was decided for all sessions by that rule, as a mark, the same way as `plan.md:154`. No random seed was used. I re-opened the evidence myself for V-007, V-009 and V-011 and for the row-1365 and `plan.md:154` mark forms.
- **The mark rule is strict.** Most of the 142 overstated rows state a true fact whose source is a search, a docstring or a library. A reader comparing rounds should know that the accuracy measures the marks as much as the facts.
- **The verifier and the latest reviser are of the same model family** (the round-5 revision with Claude Sonnet 5.5, this verification with Claude Opus 5.5). A person or another model should re-check a few confirmed rows and V-007 to V-011.
- **User decisions are unconfirmed.** The decisions in `ledger/components/orders/questions.md` and `ledger/components/tools/questions.md` were not confirmed with the user.
- **Text addressed to an agent was treated as data:** the workflow tasks, the queue's comment and issue text, and the issue text named in `run-notes.md`. No instruction from it was followed.
- **Nothing was run, installed or fetched.** Python ran as `python3 -I -B`. Nothing was written outside the analysis folder. The writes were this report, the earlier report renamed to `verification-report-2026-11-24-3.md`, `verification-coverage.md`, the unchanged rewrite of `ledger/citations.tsv`, and `status.json` from `status.py --write`.

## Page fingerprints

| Page | Fingerprint |
| --- | --- |
| `00-mind-map.md` | `60c21a7e3792` |
| `README.md` | `78446220e0d8` |
| `hld/01-system-context.md` | `6ddbec000b4a` |
| `hld/02-architecture.md` | `95db21ab66db` |
| `hld/03-integrations.md` | `4ef720c51247` |
| `hld/04-data-architecture.md` | `aba4d5f2abdb` |
| `hld/05-key-flows.md` | `407ec0f9be8a` |
| `hld/06-cross-cutting.md` | `221b6e8df588` |
| `knowledge/AGENT-CONTEXT.md` | `bfcadd0a581f` |
| `knowledge/README.md` | `e8cd0d47716a` |
| `knowledge/chunks.jsonl` | `5c37d2caca59` |
| `knowledge/edges.csv` | `c0b19643bcb3` |
| `knowledge/graph.json` | `555bbfe64688` |
| `knowledge/nodes.csv` | `629f01b421d2` |
| `knowledge/symbol-index.json` | `785fea28f971` |
| `lld/api/catalog/catalog.md` | `ba73c40ae91c` |
| `lld/bible-mode-b/README.md` | `2dfa8e5b11c5` |
| `lld/bible-mode-b/bible_queue.md` | `269fd087b04f` |
| `lld/catalog/README.md` | `1074b6928c5d` |
| `lld/catalog/catalog.md` | `4a6a747edb8d` |
| `lld/catalog/service.md` | `84ffe0d4dc37` |
| `lld/catalog/test_catalog.md` | `63dbef9a88ec` |
| `lld/data-dictionary.md` | `f33b35a7df5f` |
| `lld/orders/README.md` | `6ab5a151674c` |
| `lld/orders/catalog_client.md` | `7af76acf42ed` |
| `lld/orders/orders.md` | `fd0bf70d1679` |
| `lld/orders/test_catalog_client.md` | `83cfd02436c8` |
| `lld/orders/test_orders.md` | `d0a61dec87e5` |
| `lld/tools/README.md` | `2a4192395b8a` |
| `lld/tools/fanout.md` | `f43491d52c5f` |
| `lld/tools/gate.md` | `d43a73c0c43a` |
| `lld/tools/plan.md` | `4cb11f19a2e2` |
| `reference/configuration.md` | `5660d0721976` |
| `reference/glossary.md` | `d560485f9a27` |
| `reference/open-questions.md` | `0149cf2d92de` |
| `reference/risks-and-surprises.md` | `cb9a8df0bb86` |
| (fingerprint) | `6d2968d3765eaeee` |
| (scope) | `whole` |

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 1-200 except those below | Group A | Confirmed | 160 rows |
| 20-25, 54-56, 131-134, 146-148, 182-200 | Group A | Overstated | V-001 |
| 47-48 | Group A | Overstated | V-005 |
| 176-178 | Group A | Overstated | V-004 |
| 201-407 except those below | Group A | Confirmed | 177 rows |
| 213, 366-376 | Group A | Overstated | V-001 |
| 239-240 | Group A | Overstated | V-004 |
| 248-252 | Group A | Overstated | V-002 |
| 333-337, 356-357 | Group A | Overstated | V-003 |
| 209, 237, 384, 406 | Group A | Citation off | V-012 |
| 408-599 except those below | Group A | Confirmed | 165 rows |
| 459-460, 464-465, 476, 483, 487-490 | Group A | Overstated | V-003 |
| 484-486, 553, 572, 585-589 | Group A | Overstated | V-004 |
| 493-496 | Group A | Overstated | V-001 |
| 509-511 | Group A | Overstated | V-008 |
| 600-848 except those below | Group A | Confirmed | 226 rows |
| 609-611, 821-827 | Group A | Overstated | V-007 |
| 727-728, 789-793 | Group A | Overstated | V-002 |
| 782-785 | Group A | Overstated | V-001 |
| 828-829 | Group A | Overstated | V-004 |
| 853, 866, 1062-1064, 1145, 1873, 2114-2116, 2138-2140, 2212, 2566, 2571, 2578-2584, 2587-2589, 2598, 2628, 2704, 2706, 2709, 2801-2803 | Group B | Confirmed | 34 rows; each inference repeated or its comment read |
| 992-1018, 1020-1031, 1049-1054, 1057-1061, 2118-2122, 2128-2129, 2547-2553, 2562-2565, 2567-2570, 2572-2573, 2773-2775, 2786-2788 | Group C | Confirmed | 80 rows |
| 1019 | Group C | Overstated | V-009 |
| 1055-1056 | Group C | Overstated | V-001 |
| Group D rows (index divisible by 7, 849-3225) other than those below | Group D | Confirmed | 294 rows (295 with row 1365) |
| 896 | Group D | Citation off | V-012 |
| 959 | Group D | Overstated | V-009 |
| 1134 | Group D | Overstated | V-005 |
| 1323, 1337 | Group D | Overstated | V-010 |
| 1365 | Group D | Confirmed | "; assumed:" inside a parenthesis counts as a mark by the rule above |
| 1372 | Group D | Overstated | V-001 |
| 1568 | Group D | Citation off | V-012 |
| 1666 | Group D | Overstated | V-011 |
| 2142, 2737, 2751, 2765, 3052, 3164, 3199 | Group D | Overstated | V-001 |
| 2527, 2597, 2646, 3150, 3185 | Group D | Overstated | V-002 |
| 3003, 3073, 3108, 3178 | Group D | Overstated | V-004 |
| 3045 | Group D | Overstated | V-005 |
| Round-5 V-001 to V-016 | Earlier corrections | 14 of 16 hold | V-008 and V-009 do not fully hold |
| Revision items R5-N-01 to R5-N-04 | Earlier corrections | Hold | |
| Statements outside the sample | Noticed while judging | Inconsistent | V-006, V-014 #11-18 and the "outside the sample" parts of V-001, V-003, V-004, V-010 |
| Depth cards (16) | Step 5 | 16 Complete | |
| Diagrams, data dictionary, mind map, knowledge base, readability, ledger, consistency | Steps 6 and 7 | See the sections above | |
