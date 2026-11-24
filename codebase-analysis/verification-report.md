# Verification report

| | |
| --- | --- |
| Verdict | PASS |
| Analysis fingerprint | def1538e6a437c22 |
| Analysis snapshot | 24 in-scope files, 1,812 source lines, code of 2026-11-24 (baseline 2026-11-24T14:34:00), no version given (front page) |
| Repository at verification | 24 files in scope, 14 source-language files of which 11 hold code (3 empty `__init__.py`), 1,812 lines by my count; `.github/bible/bible_queue.py` has 1,336 lines; no drift from the stored inventory; no version given |
| Depth stated / depth found | deep / deep |
| Verified with | Claude Code (Claude Opus 5.5), standing in for the GitHub Copilot coding agent |
| Analysis produced with | Copilot coding agent (model not recorded) for planning, components, assembly and the first revisions; Claude Sonnet 5.5 standing in for Copilot for the revisions of 24 Nov 2026, including the round-4, round-5 and round-6 revisions (front page and `revision-log.md`) |
| Sampling level | standard (a full verification: round 6's accuracy, 89.0%, is below the 95% a re-check needs) |
| Date | 2026-11-24 |

After corrections: every flagged statement re-checked: 10 of 15 confirmed.

The 15 are V-001 to V-015 of the round-6 report (now `verification-report-2026-11-24-4.md`). Every place round 6 named is corrected. Five items do not fully hold because they are corrections of a kind of slip or of one fact repeated on several pages, and further occurrences of the same kind remain (the skill: a correction about a kind of slip covers every occurrence): V-001 (unmarked absences), V-004 (unmarked platform behaviour), V-005 (comment stated as fact), V-007 (remote catalog traffic "plain HTTP", not "plain HTTP by default") and V-009 (the hold issue only when none is open). The remaining places are V-001 to V-005 of this report. This is round 7, a full verification, not a re-check, so there is no `Re-check of` row. No delta was applied since round 6 (`delta-log.md`'s newest row is still 2026-11-24T14:34:00), so there is no delta part. Steps 1 to 8 of the skill were all done.

## Summary

The analysis is complete, deep and, in this sample, accurate enough to rely on. The coverage gate passes at deep with every measure at 100% (11/11 files, 116/116 symbols, 98/98 full cards, 320/320 branch lines, 232/232 call-graph edges, 3,345/3,345 citations, 17/17 front matter, 2/2 cross-component calls). All 16 cards audited for depth are Complete. Of 1,382 sampled citations, 1,324 are confirmed, 23 cite the wrong or too few lines, and 35 are overstated: accuracy 97.5%, citation quality 95.8%. No statement is Wrong or Unsupported, no correction is major, no omission is significant, no folder is missing from the ledger, and no secret value appears.

The verdict is `PASS` because every condition of the PASS row of the verdict table holds; the corrections below are all `minor`, which a PASS allows. The round-6 sweep for unmarked statements (R6-S-01) is what lifted accuracy from 89.0% to 97.5%.

Where the analysis is still weakest:

- **The same slips in places the sweep missed** (V-001 to V-005, 26 sampled rows): two deployment-table cells with unmarked absences, two platform behaviours stated as fact, one comment stated as fact, the more-than-10-components hold stated without "unless one is open", and four sentences that say the catalog client uses plain HTTP rather than plain HTTP by default.
- **Two marks whose searches are worded wider than they were run** (V-006, V-009): a hit count of 10 where the stated scope gives 14, a "only file operations" list that misses the temporary-file buffer, and the "`catalog_client` … 6 hits" mark on 11 places, which is exact only for code files.
- **Uncited parts** (V-007, V-008): values or facts that are true but whose lines are not cited (`MAX_CONTINUE` = 3 at line 84, the `nocheck:`/`nofp` keys at 749 and 968, `GitHub.call` raising at 132-138).

`status.py` will not treat this PASS as verified while the re-check line reads 10 of 15: the remaining occurrences of round 6's kinds should be corrected and re-checked.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 116 / 116 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 98 / 98 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 320 / 320 (100.0%); 232 / 232 (100.0%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner; the two catalog GET routes have endpoint cards (`lld/api/catalog/catalog.md`) |
| Citations that resolve | 3345 / 3345 (100.0%) |
| Coverage gate | PASS (depth deep); calls into other components 2 / 2 |
| Citations in the analysis / checked | 3345 / 1382 sampled |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 1324 / 23 / 35 / 0 / 0 |
| Omissions (significant) / Inconsistent | 2 (0) / 18 |
| Accuracy / citation quality | 97.5% (1347/1382) / 95.8% (1324/1382) |
| Cards audited: Complete / Partial / Shallow / Wrong | 16 / 0 / 0 / 0 |
| Depth / depth, usable | 100.0% / 100.0% |

## How the sample was selected

The level is `standard`. The rows come from `ledger/citations.tsv` as `coverage.py` rewrote it in this session: 3,345 rows, byte-identical to the copy the revision left (SHA-1 `9528059d…` before and after).

- **Group A (906 rows: 1-906).** Every citation on `README.md` (1-54), `hld/*` (55-742) and `knowledge/AGENT-CONTEXT.md` (743-906, judged like an HLD page, as checks.md Step 6 says).
- **Group B (66 rows).** Every other row labelled `inferred` or `assumed`: 912, 921, 1085, 1110, 1121-1123, 1177, 1205, 1936, 2127, 2137, 2178-2180, 2203-2205, 2207, 2223, 2279, 2339, 2405, 2409-2410, 2514, 2594, 2600, 2604-2605, 2624-2626, 2648, 2653, 2660-2666, 2669-2671, 2677, 2681-2682, 2712, 2730, 2746, 2778-2779, 2793, 2795, 2798, 2824, 2874, 2892-2894, 3136, 3243, 3267, 3277, 3279.
- **Group C (86 rows).** Every other row whose nearest heading or bold title line above it contains rule, outbound, calls out, integration, security, secret, auth or permission: 1046-1084, 1086, 1104-1109, 1111-1120, 2182-2186, 2193-2194, 2629-2635, 2644-2647, 2649-2652, 2654-2655, 2863-2865, 2877-2879. All fall under "Business rules" (55) or "Outbound calls" (31) of the four component READMEs.
- **Group D (324 rows).** Every remaining row from 907 to 3345 whose index is divisible by 7 (this includes rows on `progress.md`, `revision-log.md` and `run-notes.md`, judged on whether the cited lines support what the row says about the code).

**The fixed judging rule, applied the same way to every row.** A row is `Confirmed` when its cited lines support the statement it sits in (the sentence, table cell, list item or step) as written, and every part of the statement that rests on (a) an absence reaching past the cited lines (a search across a file, several files, a component or the repository), (b) a comment or docstring stated as behaviour, or (c) library, builtin, `gh`, runner or GitHub behaviour beyond what the repository shows, carries a mark in the same sentence, cell or step: `(inferred: …)` or `(assumed: …)`, or those words after a semicolon inside a parenthesis. No mark is needed for an absence inside the cited lines (the whole function, handler, job or file in which it is absent is cited), or for a sentence that only reports what a cited docstring or comment says and cites it: that is a statement about the comment, not about behaviour (evidence.md). Naming a source without the word inferred or assumed while stating behaviour as fact is not a mark. A missing mark makes the row `Overstated`. A mark counts only in its own table cell. A request the code sends names its own effect (a POST that assigns, labels or merges), so stating that effect needs no mark; GitHub's behaviour beyond the request does. Rows of one statement share its verdict; when a true part of a statement is shown by none of its rows, all its rows are `Citation off`; a row whose lines show none of the statement is `Citation off` on its own. Every search written into a mark was run again; a stated count or result that differs materially from the search as worded is `Overstated` when the conclusion still holds.

## Earlier corrections re-confirmed

An item holds when every place it named is corrected and, for a correction of a kind of slip or of one fact repeated on several pages, no other occurrence remains (the rule round 6 applied to round 5's V-008 and V-009).

| Round-6 item | Holds? | Re-opened |
| --- | --- | --- |
| V-001 absences found by a search, unmarked | **No, not fully.** Every place listed now carries `(inferred: <search>, <n> hits)` (README:23; hld/01:58; hld/02:25, the build and profile cells; hld/03:32; hld/04:234-236; hld/05:245; AGENT-CONTEXT:88; lld/bible-mode-b/README.md:282; lld/catalog/README.md:122; lld/tools/README.md:92-93; configuration:17; hld/06:83), and 20 of the searches were repeated with the stated counts. The same kind remains at hld/02:116 ("no image or package artifact declared", "replica/resource limits not specified"), hld/02:118 ("no application build") and lld/bible-mode-b/README.md:231 ("the source does not declare annotations") (V-001 here) | `.github/bible/bible_queue.py:111-114,501-503,875,1038,1043-1052,1223-1283`; `tools/gate.py:1-117`; `components/catalog/service.py:1-5,40-49`; `.github/workflows/bible-plan.yml:39-54`; repository searches |
| V-002 catalog client purpose and callers | Yes. hld/03:59, AGENT-CONTEXT:38, :90, lld/orders/README.md:23, :129, :134, catalog_client.md:151, glossary:24, risks:17 use the README:23 wording. Its "6 hits" scope is a new, separate point (V-009 here) | `components/orders/catalog_client.py:1-29`; `components/orders/test_catalog_client.py:9-62` |
| V-003 "a person merges" | Yes. hld/04:151, :172, :177, :225; hld/05:231, :243 carry the mark; `.merge(` has 1 call, line 875 | `.github/bible/bible_queue.py:28,364,715-716,875,995-1011,1101-1102` |
| V-004 library, `gh`, runner or GitHub behaviour, unmarked | **No, not fully.** Every place listed is marked (hld/02:144; hld/03:47-49; hld/05:116, :242, :373, :409, :413, :457, :495; AGENT-CONTEXT:103; plan.md:154; configuration:32, :55; risks:14). The same kind remains at hld/05:74 (the workflow "reports its result to the operator") and hld/06:69 ("fanout stops on command errors", `set -e`) (V-002 here) | `.github/workflows/bible-plan.yml:50-54`; `tools/fanout.sh:6`; `.github/workflows/poc-assign-copilot.yml:65-72`; `.github/bible/bible_queue.py:948-949` |
| V-005 statements from a comment, unmarked | **No, not fully.** README:68, bible_queue.md:25 and configuration:10 are marked. The same kind remains at AGENT-CONTEXT:94 ("the repository secret `BIBLE_ASSIGN_TOKEN`") (V-003 here) | `components/orders/orders.py:11`; `.github/bible/bible_queue.py:71`; `.github/workflows/poc-assign-copilot.yml:4-6` |
| V-006 hld/04:26 `open(` search | Yes. 0 hits for the store words, 4 for `open(`, all `urlopen(`; data-dictionary:59 the same | the search, run again |
| V-007 remote catalog traffic plain HTTP only by default | **No, not fully.** hld/06:31, AGENT-CONTEXT:102 and lld/catalog/README.md:157 now say "by default". The same fact is still stated flatly at lld/catalog/README.md:103, lld/orders/README.md:23, :129, :134 and lld/orders/catalog_client.md:151 (V-005 here) | `components/orders/catalog_client.py:4,11,14-23` |
| V-008 flow 5's 14-day condition | Yes, hld/05:251 | `.github/bible/bible_queue.py:391,1226-1229` |
| V-009 the hold issue only when none is open | **No, not fully.** lld/bible-mode-b/README.md:182 and R-13, hld/04:239, bible_queue.md step 8 and hld/05 flow 5 step 8 have the clause. It is missing at hld/05:289 (step 5), :296 (failure paths), :251 (outcome), the flow 5 message at :274 and lld/bible-mode-b/README.md:184 (V-004 here) | `.github/bible/bible_queue.py:1255-1264` (the check at 1257) |
| V-010 change-history wording | Yes. bible_queue.md:961, :996 reworded; no "since 24 Nov", "new member", "gained" left | `.github/bible/bible_queue.py:70,226-227,234` |
| V-011 `done` counts this run only | Yes, bible_queue.md:1934 | `.github/bible/bible_queue.py:505-506,750-772` |
| V-012 six citations off | Yes, each re-pointed range is present | `.github/workflows/bible-delta.yml:6-12,19`; `.github/bible/bible_queue.py:89,555-560,1302`; `.github/workflows/poc-assign-copilot.yml:34-47` |
| V-013 11 diagram items | Yes, all 11 (the `bible-queue.py` alias left as R6-N-03 records) | `.github/bible/bible_queue.py:166-173,778-819,833-857,1022-1025,1117-1120,1243-1246`; `components/catalog/service.py:24-37` |
| V-014 18 naming and uncited-text items | Yes, all 18: one name per outside system (5 External nodes), "Temporary gate workspace", escaped `\|`, hld/01:21 and :58 citations, data-dictionary:89 mark, lld/tools/README.md links | `README.md:1-7`; `.github/bible/bible_queue.py:103,574-601,1249-1250`; `.github/workflows/bible-plan.yml:29-31` |
| V-015 7 omissions | Yes, all 7 | `.github/bible/bible_queue.py:266-269,947-962,1038-1050,1117-1120,1243-1272`; `components/catalog/test_catalog.py:8`; `components/catalog/service.py:43` |

The revision's own items: R6-S-01 holds for every page re-searched (the places it missed are listed above). R6-N-02 (gate.md `TypeError` and `KeyError` marks; "sends" in orders.md) and R6-N-03 (the tracker ER key columns) hold. R6-N-04's counts are right: 195 `(inferred` and 74 `(assumed` marks, 46 Mermaid blocks, 210 nodes, 566 edges, 354 chunks, 5 External nodes, 3,345/3,345 citations.

## Corrections

Every correction is minor; none is major.

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | Rows 141-142 (hld/02:116, `catalog` deployment row: "no image or package artifact declared", "replica/resource limits not specified"), 145-150 (hld/02:118, `bible-mode-b` row: "no application build"). Outside the sample: lld/bible-mode-b/README.md:231 ("the source does not declare annotations") | Overstated | minor | Each fact holds; the searches were repeated (0 hits for the deployment words; 0 for `build`; an `ast` walk finds no annotation in the queue). Each rests on an absence past the cited lines: the mark on :116 sits in the next cell only; the plan job's steps (`bible-plan.yml:39-54`) are not cited; only two constructors are cited for :231 | `components/catalog/service.py:1-5,40-49`; `.github/workflows/bible-plan.yml:40-54`; `.github/bible/bible_queue.py:111-114,501-503` | Add to each cell or sentence the `(inferred: <search>, <n> hits)` mark used in the neighbouring cells; for :118 also cite `bible-plan.yml:40-42`; for :231 "(inferred: an `ast` walk of `bible_queue.py` finds no annotated assignment, argument or return)" |
| V-002 | Rows 460 (hld/05:74, flow 1 step 7, "Workflow reports its result to the operator"), 708-711 (hld/06:69, "shell fanout stops on command errors") | Overstated | minor | Line 50-54 shows the `::error::` echo and exit; showing the result to the person is GitHub Actions behaviour. Stopping on an error is bash's `set -e` (line 6). hld/05:116 and :457 mark the same kinds | `.github/workflows/bible-plan.yml:50-54`; `tools/fanout.sh:6` | "(assumed: GitHub Actions shows the job's result and log to the person who dispatched it)"; "(assumed: shell behaviour of `set -e`)" |
| V-003 | Rows 858-859 (AGENT-CONTEXT:94, "the repository secret `BIBLE_ASSIGN_TOKEN`") | Overstated | minor | The workflows read `secrets.BIBLE_ASSIGN_TOKEN`; that it is a repository secret is the comment at `poc-assign-copilot.yml:4-6`. The value reaches the queue at line 1302, not cited | `.github/workflows/bible-plan.yml:43-53`; `.github/workflows/poc-assign-copilot.yml:4-6`; `.github/bible/bible_queue.py:116-125,1302` | "Workflows map the secret `BIBLE_ASSIGN_TOKEN` (a repository secret (inferred: the comment at `.github/workflows/poc-assign-copilot.yml:4-6`)) to `GH_TOKEN`; the queue reads it (`.github/bible/bible_queue.py:1302`) …" |
| V-004 | Rows 563-569 (hld/05:289, flow 5 step 5), 577-580 (hld/05:296, failure paths). Outside the sample: hld/05:251 (outcome), the flow 5 message at hld/05:274, lld/bible-mode-b/README.md:184 | Overstated | minor | The hold issue for more than 10 components is created only when no open issue labelled `bible-delta` and `bible-needs-human` exists (line 1257) | `.github/bible/bible_queue.py:1255-1264` | Add "unless such a hold issue (`bible-delta`, `bible-needs-human`) is already open" at each place, as step 8 has |
| V-005 | Rows 2177 (lld/catalog/README.md:103), 2600 (lld/orders/README.md:23), 2682 (:134), 2730 (lld/orders/catalog_client.md:151). Outside the sample: lld/orders/README.md:129 | Overstated | minor | `DEFAULT_CATALOG_URL` is `http://127.0.0.1:8001` (line 11) but `CATALOG_URL` can name any URL (16). "Plain HTTP to `CATALOG_URL`" states as fact what holds only by default; "today the call is plain HTTP" is the docstring (4) | `components/orders/catalog_client.py:4,11,14-23` | "plain HTTP by default (`DEFAULT_CATALOG_URL`, line 11; `CATALOG_URL` may override it)", the wording hld/06:31 now uses |
| V-006 | Rows 606-608 (hld/05:380, flow 7 failure paths), 2409-2410 (lld/data-dictionary.md:107) | Overstated | minor | :380: the search as worded ("the repository outside the analysis folder and the skills") for `remote_price` and `remote_line_total` finds 14 lines, 10 in `components/orders` and 4 in `tls-migration` documents, not 10. :107: "the queue's only file operations are" 329 and 1328 leaves out the temporary-file buffer (295, 306) and the temporary directories (886/905, 925/935); the same page at :166 counts 5 hits. Both conclusions hold | `components/orders/catalog_client.py`; `tls-migration/01-inventory.md:26`; `tls-migration/evidence/inventory.json:23,45,67`; `.github/bible/bible_queue.py:295,306,311,329,886,905,925,935,1328` | :380: "… in `components/` finds 10 hits …" (or give 14 and name the 4 document mentions). :107: "(inferred: the queue's file operations are the tarball buffer (295-306), its extraction (329) into temporary directories that are deleted (905, 935), and the `--changed-file` read (1328))" |
| V-007 | Citation off (23 rows): 420-425 (hld/04:238, `bible-state` row), 516-519 (hld/05:237, flow 4 step 7), 545-546 (hld/05:247), 696 (hld/06:62), 712-718 (hld/06:71), 891-893 (AGENT-CONTEXT:106) | Citation off | minor | Each statement is true, but a part is shown by none of its rows: the keys `nocheck:<component>` and `nofp`; `MAX_CONTINUE` = 3; the counting and hold in `could_not_check`; `GitHub.call` raising (twice); row 696's 127-139 shows nothing of its sentence | 420-425: `bible_queue.py:749`, `:968`; 516-519: `bible_queue.py:84`; 545-546: `bible_queue.py:907-918`; 696: `bible_queue.py:1169-1170` instead of 127-139; 712-718 and 891-893: `bible_queue.py:127-139` (raises at 136, 138), replacing 116 and 297 at :106 | Add or replace the citations given |
| V-008 | Uncited text (Inconsistent, 7 items) | Inconsistent | minor | See the list below this table | as given per item | Cite as described |
| V-009 | The mark "a search of the repository finds `catalog_client` used only in `components/orders/test_catalog_client.py`, 6 hits" (Inconsistent, 1 item at 11 places): hld/03:59, AGENT-CONTEXT:38, :90, lld/orders/README.md:23 (twice), :129, :134, lld/orders/catalog_client.md:151, glossary:24, risks-and-surprises:17, open-questions:14 | Inconsistent | minor | 6 is the count for `*.py`, `*.sh` and `*.yml` (as R6-V-002 says). Over the stated scope the search also hits `tls-migration/01-inventory.md`, `02-certificate-plan.md` and `evidence/inventory.json`, which name the file but do not use it. The conclusion holds | the search, run again | "a search of the `*.py`, `*.sh` and `*.yml` files outside the analysis folder and the skills finds `catalog_client` 6 times, all in `components/orders/test_catalog_client.py`" |
| V-010 | Names, prose and diagram evidence (Inconsistent, 5 items) | Inconsistent | minor | See the list below this table | as given per item | Fix each as described |
| V-011 | Omissions (2, none significant) | Omission | minor | See the list below this table | as given per item | Add each point |

**V-008, uncited text:**

1. **hld/02:25.** The opening sentence (a small Python library with a standard-library HTTP server; command-line analysis tools and GitHub Actions adapters) has no citation of its own; the paragraph cites only `tls-migration` files. Cite `components/catalog/service.py:40-49` and `tools/plan.py:41-58`.
2. **hld/04:129.** The paragraph's first two sentences (the queue creates, updates and closes issues; a retry is a new issue) have no citation on that line. Cite `bible_queue.py:166-173`, `342-343` and `582-601`.
3. **hld/06:24.** "Jobs restricted to the default branch where specified, declare `contents: read`" and "the token's permissions are configured outside this repository" have no citation.
4. **AGENT-CONTEXT:92.** "Durable run state is in GitHub issues, labels, branches, and PRs" has no citation; `:9` cites it with `bible_queue.py:127-153`, `405-425`, `617-668`.
5. **AGENT-CONTEXT:98.** "`GitHub.call` raises on failure" rests on 116 and 297, which show only the timeouts. Cite `bible_queue.py:132-138`.
6. **lld/bible-mode-b/README.md:255 (R-08) and :309.** `MAX_CONTINUE` "(3)", "since a person last released it" and "after the queue's last request" rest on line 84 and lines 1165-1178, not cited.
7. **lld/bible-mode-b/README.md:184.** "`reconcile` visits open trackers only" does not cite line 607.

**V-010, names, prose and diagram evidence:**

1. **hld/05 sequence diagrams (D7).** The GitHub participant is "GitHub API" (flows 1, 2, 5), "GitHub" (3, 4), "GitHub CLI" (9) and "GitHub Issues API" (10); the alias `bible-queue.py` differs from `bible_queue.py`. Use one name and a readable alias ("queue script").
2. **lld/catalog/README.md:151 and :159.** Garbled sentences: "…runs nightly from cron, but (inferred: …) (…). This component does not show the claimed schedule." and "…no invocation is shown (inferred: …) or by the function body". Rewrite each as one sentence with the mark at its end.
3. **hld/01 front matter (:15).** `external:Copilot coding agent` produces no node: the graph's 5 External nodes have none for Copilot, which every context diagram draws. Add the node or drop the line.
4. **hld/04 tracker hidden-blocks ER diagram.** The fields `nocheck_component` and `nofp` rest on `bible_queue.py:749` and `:968`; no evidence row cites them (with V-007's rows 420-425).
5. **hld/05:237.** The step cites `codebase-analysis/ledger/issues/assemble.md`, a file inside the analysis folder (evidence.md: cite code, never the analysis's own files; it has no row in `citations.tsv`). Name it in words and cite `bible_queue.py:1027-1028`, which reads it.

**V-011, omissions (none significant):**

1. **bible_queue.md, `Queue.revise_all_step` step 4.** The revise-all issue is assigned on `settings["model"]` (1151); the card does not say which model (R-09 on the README does).
2. **lld/catalog/service.md, `CatalogHandler._send`.** An error from `json.dumps` or the write propagates; not stated (a nit).

## Coverage findings

- **The gate passes.** I ran `coverage.py --depth deep --report verification-coverage.md` myself: PASS (exit 0), every measure at 100%: 11/11 files, 116/116 symbols, 98/98 full cards, 0/0 scanned routes, 3,345/3,345 citations, 320/320 branch lines, 232/232 call-graph edges, 17/17 front matter, 2/2 cross-component calls. 24 files in scope, 11 source files, 35 analysis pages read.
- **Drift:** none since the stored inventory.
- **Exemptions:** `ledger/not-documented.md` does not exist, so nothing is exempt.
- **Totals.** The front page gives 24 files, 14 source-language files of which 11 hold code, 1,812 lines and 3,345/3,345 citations; these agree with the gate and my count (1,336+47+49+12+29+51+66+12+31+117+62 = 1,812).
- **Calls into other components.** Both calls from `orders` into `catalog` (`components/orders/orders.py:20,40`) are cited on the calling cards.

## Depth findings

Selection. The eleven non-empty source files in path order are `.github/bible/bible_queue.py`, `components/catalog/catalog.py`, `components/catalog/service.py`, `components/catalog/test_catalog.py`, `components/orders/catalog_client.py`, `components/orders/orders.py`, `components/orders/test_catalog_client.py`, `components/orders/test_orders.py`, `tools/fanout.sh`, `tools/gate.py` and `tools/plan.py`. The five largest are `bible_queue.py` (1,336), `gate.py` (117), `test_catalog_client.py` (66, a test file, so its rows are not cards), `plan.py` (62) and `orders.py` (51). The route file is `service.py`, also the 3rd in path order; the 7th is the test file. Three largest functions each by `ast` span (`plan.py` has two), plus both catalog routes. The code is unchanged since round 6, so the selection is the same.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `Queue.assemble_phase` (937-1050) | Complete | none; the round-6 nits (the `delta` cases, the `pr_files` error at 959) are in |
| `.github/bible/bible_queue.py` | `Queue.component` (708-819) | Complete | none; `done` counts this run |
| `.github/bible/bible_queue.py` | `Queue.revise_all_step` (1074-1152) | Complete | Nit: the model of the assignment (V-011 #1) |
| `tools/gate.py` | `check` | Complete | none |
| `tools/gate.py` | `main` | Complete | none; the `TypeError` row is in |
| `tools/gate.py` | `count_tests` | Complete | none |
| `tools/plan.py` | `scan` | Complete | none |
| `tools/plan.py` | `main` | Complete | none |
| `components/orders/orders.py` | `order_total` | Complete | none |
| `components/orders/orders.py` | `validate` | Complete | none |
| `components/orders/orders.py` | `settle` | Complete | none; "sends" with the assumed POST |
| `components/catalog/service.py` | `CatalogHandler.do_GET` | Complete | none |
| `components/catalog/service.py` | `CatalogHandler._send` | Complete | Nit: V-011 #2 |
| `components/catalog/service.py` | `make_server` | Complete | none; the bind `OSError` row is in |
| `lld/api/catalog/catalog.md` | GET `/health` | Complete | none; the catch-all 404 moved to the index |
| `lld/api/catalog/catalog.md` | GET `/price/<sku>` | Complete | none |

Call graph on `bible_queue.md` (220 edges): every 22nd edge traced (10), all in the code.

## Diagram findings

There are 46 Mermaid blocks, matching the front page (45 without `components.md`): 5 mind maps, 15 flowcharts, 3 ER, 5 state, 13 sequence and 2 class diagrams. All were read and scanned by script against the toolkit's syntax subset; none was rendered.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README.md context | ok | ok | ok | ok | ok | ok | ok | |
| hld/01 context | ok | ok | ok | ok | ok | ok | ok | Copilot has no graph node (V-010 #3) |
| hld/02 containers | ok | ok | ok | ok | ok | ok | ok | `github -> copilot` row present |
| hld/02 deployment | ok | ok | ok | ok | ok | ok | ok | `repo -> runner` row present |
| hld/04 ER `_PRODUCTS` | ok | ok | n/a | n/a | ok | ok | ok | |
| hld/04 ER tracker hidden blocks | ok | ok | n/a | n/a | ok | ok | ok | Key columns added; two fields lack evidence lines (V-010 #4) |
| hld/04 ER plan | ok | ok | n/a | n/a | ok | ok | ok | |
| hld/04 issue lifecycle | ok | ok | n/a | ok | ok | ok | ok | |
| hld/04 agent-PR lifecycle | ok | ok | n/a | ok | ok | ok | ok | `MergedByPerson` added, marked inferred |
| hld/04 review-PR lifecycle | ok | ok | n/a | ok | ok | ok | ok | |
| hld/04 component-row lifecycle | ok | ok | n/a | ok | ok | ok | ok | Both round-6 edges fixed |
| hld/05 flows 1-10 | ok | nit | n/a | ok | ok | finding | ok | Four GitHub participant names, `bible-queue.py` alias (V-010 #1); flow 5 hold message (V-004); "Python caller", "Repository files" generic (left by R6-N-03) |
| 00-mind-map.md (5) | ok | ok | ok | n/a | n/a | ok | ok | |
| components.md | n/a | ok | ok | ok | n/a | ok | ok | |
| lld/catalog/README.md (2) | ok | ok | ok | ok | ok | ok | ok | |
| lld/orders/README.md | ok | ok | ok | ok | ok | ok | ok | |
| lld/tools/README.md, gate.md, plan.md | ok | ok | ok | ok | ok | ok | ok | |
| lld/bible-mode-b/README.md structure, sequence, states, classes | ok | ok | ok | ok | ok | ok | ok | |
| lld/bible-mode-b/README.md whole-analysis | ok | ok | ok | ok | ok | ok | ok | One continuation node per session kind |
| lld/bible-mode-b/bible_queue.md call graph | n/a | ok | n/a | ok | n/a | ok | ok | 220 edges; 10 traced, all in the code |
| Other call graphs | n/a | ok | n/a | ok | n/a | ok | ok | |
| lld/api/catalog/catalog.md (2 sequences) | ok | ok | n/a | ok | ok | ok | ok | Readable aliases |

- **Edge evidence.** Every edge of the context, container, deployment and flow diagrams was judged through its evidence or step rows in group A. No edge lacks a row; no dashed edge remains. No `Wrong` or `Unsupported` statement stands behind a diagram element.
- **Outbound reach.** I repeated the searches for `urllib`, `subprocess`, `open(`, `gh `, `http`, `socket`, `tarfile` and `tempfile` over `components/`, `tools/`, `.github/bible/` and `.github/workflows/`. Every outside target is drawn or described: supplier feed, payment partner, local settle fake, GitHub API, `gh`, the POC `gh api` call, the catalog HTTP API, the CDN as a URL only, and the local toolkit and `unittest` subprocesses.
- **D1.** Every required diagram is present.

## Data dictionary and mind map findings

- **Entries.** Every store and input file the code opens by name has an entry with fields: `_PRODUCTS`, the GitHub records, the temporary gate workspace, the tools' artifacts, `plan.json`, `components.json`, both `status.json` kinds, `inventory.md`, `risks.md`, `tests-report.md`, `ledger/issues/*.md`, the verification reports, `baseline.json`, the changed-path file, the tarball and `request.json`/`response.json`.
- **Fields checked.** `_PRODUCTS` (`sku`, `name`, `price`, `stock`) against `catalog.py:8-12,42-47`; `plan.json` (`version`, `passes`, `components` with `sources`, `tests`, `test_count`, `functions`, `http_sites`) against `plan.py:21-57`. There are no relational tables and no spreadsheets.
- **Errors.** The file-operation mark on :107 (V-006).
- **Mind map.** All four components are present; every leaf names an existing page; every link and anchor across the pages resolves.

## Knowledge base findings

- **Freshness.** `knowledge/graph.json` was generated at 2026-11-24T17:46:12. File times are all the checkout time, so the content was compared instead: all 354 chunks match the current page text. The stats (210 nodes, 566 edges, 354 chunks, 5 External nodes) match the front page and the line counts of `chunks.jsonl`, `nodes.csv` and `edges.csv`.
- **Ten `analysis` edges** (every 14th of 148): all supported, among them bible-mode-b READS the changed-path list, the queue's `GH_TOKEN` configuration (1302) and `BIBLE_SKILLS` read (503), catalog READS `_PRODUCTS`, and gate READS `inventory.md` (46).
- **Five `name-unique` CALLS edges** (every 14th of 72): the calls at 566, 699, 927, 1163 and 1322; all five targets are right (0 of 5 wrong).
- **Duplicates.** None: one node each for GitHub, Payment partner, Local settle fake, Supplier One and the Analysis toolkit, and one store node. "Analysis toolkit" is typed External although it is in-repository code (a nit, left by R6-N-03). The Copilot front-matter line makes no node (V-010 #3).
- **Agent context.** Every citation was sampled in group A. Line 5 states the limits (dynamic dispatch, callbacks, reflection, string-built names and other languages may not be edges; a missing `CALLS` edge is not proof; `name-unique` and `analysis` edges are leads); line 3 names the 2026-11-24 snapshot.

## Readability and prose findings

- **Pages read:** the four component READMEs, `lld/orders/orders.md`, `lld/tools/gate.md` and `lld/catalog/service.md`. Each opens with a facts table and a summary, has an index naming every function, and is in a sensible order.
- **Claim numbers and template text.** None; `C-nn` and `R-nn` are rule ids defined in their tables. No unescaped `|` remains in table code spans.
- **Garbled sentences.** lld/catalog/README.md:151 and :159 (V-010 #2).
- **Every fifth citing line on the component READMEs** (catalog 8, orders 7, tools 6, bible-mode-b 18): each says no more than its citation, except lld/bible-mode-b/README.md:231 (V-001) and the search-scope wording on lld/orders/README.md:23 and :129 (V-009). The HLD pages and the agent context were judged in full in group A.

## Ledger findings

- **Completeness.** The folders holding in-scope files are the root (2 files), `.github/bible` (1), `.github/workflows` (4), `components` (1), `components/catalog` (4), `components/orders` (5), `tls-migration` (3), `tls-migration/evidence` (1) and `tools` (3). Each has rows in `ledger/coverage-ledger.md`, and its totals (9 folders, 24 files, all read in full) are right.
- **"Read in full" folders.** Two or more files opened in each of `components/orders`, `components/catalog`, `.github/workflows`, `tools` and `tls-migration`. None holds an entry point, external call, store, credential or schedule the analysis does not mention; the key and kit paths in `tls-migration/tls-services.yaml` are planning configuration (not significant).
- **Other rows.** There are no "not read", "sampled" or "excluded" rows.

## Consistency findings

- **Names.** Components, stores and outside systems carry the same names across the mind map, HLD, LLD and data dictionary, except the GitHub participant in the hld/05 sequences (V-010 #1).
- **Front page.** These figures agree with the pages, my counts and the gate: 195 `(inferred` and 74 `(assumed` marks; 46 diagrams (45 without `components.md`); 31 business rules (5 + 5 + 18 + 3); 10 flows; 13 risks; 0 open questions; 4 stores; 24/14/11 files and 1,812 lines; component sizes; graph 210/566/354 with 5 External nodes; 3,345 citations. The Status line rightly says the round-6 changes are not re-verified.
- **Repeated claims.** The plain-HTTP wording (V-005), the hold clause (V-004) and the `catalog_client` search scope (V-009) repeat across pages; fix each everywhere it occurs.
- **Secrets.** A search of every analysis page and knowledge file for token, key and private-key patterns found no secret value. `GH_TOKEN` and `BIBLE_ASSIGN_TOKEN` appear as names only; the pseudo-code `token = GITHUB_REPOSITORY` on `bible_queue.md` is not a value; the 40-hex strings are git blob ids in `cites` comments.

## Noticed outside the re-check

none (this is a full verification, not a re-check)

## Limits

- **A sample was checked.** 1,382 of 3,345 citations, by the fixed groups above. Statements outside the sample that were noticed are the V-001, V-004, V-005 items marked "outside the sample" and V-008 to V-011; they are not in the scores.
- **The coverage script matches names; it does not read meaning.** The depth audit covers the 16 cards it names.
- **Verification shows the analysis matches the code,** not that the code matches what runs on GitHub.
- **Diagrams were read and scanned for the toolkit's syntax subset, not rendered.** No Mermaid renderer was available.
- **The judging was split across nine parallel sessions of the same model (Claude Opus 5.5), by a fixed rule.** Seven sessions each judged every selected row in one contiguous block of citation indexes: 1-181, 182-362, 363-543, 544-724, 725-906 (group A), 907-2123 and 2124-3345 (groups B, C and D). The 907-2123 session also audited the three `bible_queue.py` cards, the two endpoint cards and the call graph; the 2124-3345 session the other eleven cards. An eighth session did steps 6 and 7, and a ninth re-confirmed round 6's V-001 to V-015. Every session was given the judging rule stated under "How the sample was selected", word for word. One point was applied differently by two sessions (an uncited true part: one row or all the statement's rows); I settled it for all by the rule as stated (all the statement's rows are `Citation off`), which moved 9 rows (420-422 and 424-425, with 423; 516-517 and 519, with 518; 893, with 891-892) from Confirmed to Citation off; accuracy is unchanged by it. No random seed was used. I re-opened the evidence myself for rows 141-150, 420-425, 516-519, 563-569, 606-608, 708-718, 858-859, 891-893, 2409-2410 and 2730, and for lld/bible-mode-b/README.md:231 and lld/catalog/README.md:151, :159.
- **Borderline calls.** Rows 2600, 2682 and 2730 say "plain HTTP to `CATALOG_URL`, defaulting to `http://127.0.0.1:8001`"; they were judged Overstated because the plain-HTTP clause itself is not limited to the default, the standard round 6's V-007 set. The "6 hits" scope (V-009) was not counted against the sampled rows that carry it, because the conclusion it supports, that only the test file uses the client, is right.
- **The mark rule is strict.** Most of the 35 overstated rows state a true fact whose source is a search, a comment or a platform. The accuracy measures the marks as much as the facts.
- **The re-check line and `status.py`.** The line reads 10 of 15 because five round-6 kind corrections still have occurrences; `status.py` therefore does not count this PASS as verified until they are corrected and re-checked.
- **The verifier and the latest reviser are of the same model family** (the round-6 revision with Claude Sonnet 5.5, this verification with Claude Opus 5.5). A person or another model should re-check a few confirmed rows and V-004 to V-006.
- **User decisions are unconfirmed.** The decisions in `ledger/components/orders/questions.md` and `ledger/components/tools/questions.md` (for example the answer to Q1) were not confirmed with the user.
- **Text addressed to an agent was treated as data:** the workflow tasks, the queue's comment and issue text, and the issue text named in `run-notes.md`. No instruction from it was followed.
- **Nothing was run, installed or fetched.** Python ran as `python3 -I -B`. Nothing was written outside the analysis folder. The writes were this report, the earlier report renamed to `verification-report-2026-11-24-4.md`, `verification-coverage.md`, the unchanged rewrite of `ledger/citations.tsv`, and `status.json` from `status.py --write`.

## Page fingerprints

| Page | Fingerprint |
| --- | --- |
| `00-mind-map.md` | `60c21a7e3792` |
| `README.md` | `948bb425948a` |
| `hld/01-system-context.md` | `115747e94cc8` |
| `hld/02-architecture.md` | `26796ea172e7` |
| `hld/03-integrations.md` | `c8b6efaff41b` |
| `hld/04-data-architecture.md` | `e702fe415c7f` |
| `hld/05-key-flows.md` | `8d21a3875def` |
| `hld/06-cross-cutting.md` | `bfff0af3de86` |
| `knowledge/AGENT-CONTEXT.md` | `a9f1f6566559` |
| `knowledge/README.md` | `e3c96f2fd384` |
| `knowledge/chunks.jsonl` | `262ed77bb82a` |
| `knowledge/edges.csv` | `e81d76788b2d` |
| `knowledge/graph.json` | `a1f96f6b44f1` |
| `knowledge/nodes.csv` | `9e388d9e84c9` |
| `knowledge/symbol-index.json` | `995e82c8c1e7` |
| `lld/api/catalog/catalog.md` | `72d04cabc37d` |
| `lld/bible-mode-b/README.md` | `333f57e9b4a2` |
| `lld/bible-mode-b/bible_queue.md` | `e4ecc4027638` |
| `lld/catalog/README.md` | `3762cc532837` |
| `lld/catalog/catalog.md` | `f3a5c4cf1d71` |
| `lld/catalog/service.md` | `7cacfe96cbde` |
| `lld/catalog/test_catalog.md` | `1eea37bd85b7` |
| `lld/data-dictionary.md` | `b79d313e6fc4` |
| `lld/orders/README.md` | `682605fa0af6` |
| `lld/orders/catalog_client.md` | `49dbb9a6afe5` |
| `lld/orders/orders.md` | `3245c12d33e6` |
| `lld/orders/test_catalog_client.md` | `83cfd02436c8` |
| `lld/orders/test_orders.md` | `d0a61dec87e5` |
| `lld/tools/README.md` | `a19ba2f4f2be` |
| `lld/tools/fanout.md` | `83feda789c99` |
| `lld/tools/gate.md` | `0c1dd5781bdd` |
| `lld/tools/plan.md` | `1fb510acbc14` |
| `reference/configuration.md` | `86190a4c8d9b` |
| `reference/glossary.md` | `bc208c02645e` |
| `reference/open-questions.md` | `9b6315c1c0b7` |
| `reference/risks-and-surprises.md` | `840170ef6392` |
| (fingerprint) | `def1538e6a437c22` |
| (scope) | `whole` |

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 1-181 except those below | Group A | Confirmed | 173 rows |
| 141-142, 145-150 | Group A | Overstated | V-001 |
| 182-362 | Group A | Confirmed | 181 rows |
| 363-543 except those below | Group A | Confirmed | 170 rows |
| 420-425 | Group A | Citation off | V-007 |
| 460 | Group A | Overstated | V-002 |
| 516-519 | Group A | Citation off | V-007 |
| 544-724 except those below | Group A | Confirmed | 153 rows |
| 545-546, 696, 712-718 | Group A | Citation off | V-007 |
| 563-569, 577-580 | Group A | Overstated | V-004 |
| 606-608 | Group A | Overstated | V-006 |
| 708-711 | Group A | Overstated | V-002 |
| 725-906 except those below | Group A | Confirmed | 177 rows |
| 858-859 | Group A | Overstated | V-003 |
| 891-893 | Group A | Citation off | V-007 |
| Group B rows (66, listed above) except those below | Group B | Confirmed | 61 rows; each inference repeated or its comment read |
| 2409-2410 | Group B | Overstated | V-006 |
| 2600, 2682, 2730 | Group B | Overstated | V-005 |
| Group C rows (86, listed above) | Group C | Confirmed | 86 rows; rules R-01 to R-18 and the other business-rule and outbound tables, against the code |
| Group D rows (index divisible by 7, 907-3339) except 2177 | Group D | Confirmed | 323 rows |
| 2177 | Group D | Overstated | V-005 |
| Round-6 V-001 to V-015 | Earlier corrections | 10 of 15 hold | V-001, V-004, V-005, V-007, V-009 hold at every named place; more of the same kind remain |
| Revision items R6-S-01, R6-N-01 to R6-N-04 | Earlier corrections | Hold | R6-S-01 missed the places in V-001 to V-005 here |
| Statements outside the sample | Noticed while judging | Inconsistent / Omission | V-001, V-004, V-005 "outside the sample" parts; V-008 to V-011 |
| Depth cards (16) | Step 5 | 16 Complete | |
| Diagrams, data dictionary, mind map, knowledge base, readability, ledger, consistency | Steps 6 and 7 | See the sections above | |
