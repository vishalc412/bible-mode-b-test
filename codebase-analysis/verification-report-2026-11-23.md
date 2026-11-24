# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Analysis fingerprint | 26ea3631571ae969 |
| Analysis snapshot | 20 in-scope files (14 source files, 1,343 source lines), 2026-11-23, no version given |
| Repository at verification | 24 files in scope per `coverage.py` (11 source files with symbols), 2026-11-23, no version given. `.github/bible/bible_queue.py` is now 943 lines and has changed since the cards were written |
| Depth stated / depth found | deep / deep gate returns GAPS (see Scores) |
| Verified with | GitHub Copilot coding agent; model not recorded |
| Analysis produced with | Copilot coding agent; model not recorded (front page) |
| Sampling level | quick, reduced (see "How the sample was selected") |
| Date | 2026-11-23 |

## Summary

The analysis is accurate where it can be checked and shallow in one place. Every sampled statement about `catalog`, `orders` and `tools` is right, and every `inferred` statement I opened is marked correctly. The weak point is `.github/bible/bible_queue.py`. The file changed after its cards were written, so most line citations to it (783 of 1,754, 45% of all citations) no longer point at the cited code. Two cards (`main`, `settings_of`) describe older behaviour, and two methods (`GitHub.me`, `Queue.continue_if_unfinished`) have no card.

The front page and the coverage ledger say the coverage gate passes. When I ran it, it returned GAPS. I rate this PASS AFTER CORRECTIONS because the statements I could check are true, coverage of files, symbols and routes is at least 95%, and the problems are specific and fixable by re-running the analysis on the one changed file. Do not rely on the `bible-mode-b` page's line numbers until it is revised.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 108 / 110 (98.2%) |
| Functions with a full card (pseudo-code, branches cited) | 90 / 90 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 66 / 227 (29.1%); 179 / 189 (94.7%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner (100.0%); the two GET routes have cards by hand, `lld/api/catalog/catalog.md` |
| Citations that resolve | 1741 / 1754 (99.3%) |
| Coverage gate | GAPS |
| Citations in the analysis / checked | 1,754 / 88 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 70 / 18 / 0 / 0 / 0 |
| Omissions (significant) / Inconsistent | 3 (1 significant) / 3 |
| Accuracy / citation quality | 100.0% / 79.5% |
| Cards audited: Complete / Partial / Shallow / Wrong | 5 / 1 / 0 / 1 |
| Depth / depth, usable | 71.4% / 85.7% |

Gate GAPS: symbols 98.2% (needs 100%), branch lines cited 29.1% (needs 95%), call-graph edges 94.7% (needs 95%), two data or config files not mentioned, four cards written from code that has since changed. The verdict table asks for at least 95% on files, symbols and routes only for PASS AFTER CORRECTIONS, and that holds. The depth, usable figure is above 80%.

## How the sample was selected

Level `quick`, scaled down because of the amount of code to read. The rows are indexes in `ledger/citations.tsv`.

- Group A (hld/ and README.md, even index): 2, 22, 42, 62, 82, 102, 122, 142, 162, 182, 202 (every tenth of the 105 even rows). Also checked through group D: 20, 40, 60, 80, 100, 120, 140, 160, 180, 200.
- Group B (inferred): 297, 305, 464, 1140, 1266, 1270, 1272, 1274, 1276, 1280, 1283, 1299, 1365, 1370 (14 of the 21; the rest are the same kind of "no handler found" statement).
- Group C (rules, outbound, security, auth headings, even index): 294, 1110, 1190 only. This group was not completed.
- Group D (index divisible by 20): 20 to 600 in steps of 20 (30 rows), then every row from 1060 to 1640 in steps of 20 (30 rows). Rows 620 to 1040 (all in `lld/bible-mode-b/`) and 1660 to 1740 were not judged.

The scores use only these rows. The sample is not the full `quick` rule: groups A and C are partial and group D skips two ranges. Treat the figures as an estimate.

## Earlier corrections re-confirmed

none (first verification of the whole analysis; the four component reports under `ledger/components/` are earlier, separate checks and their fingerprints no longer match, see `status.json`).

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/bible-mode-b/bible_queue.md` (591 citations), `lld/bible-mode-b/README.md` (110), `hld/05-key-flows.md` (28), `knowledge/AGENT-CONTEXT.md` (17), others (37) | Citation off | major | Of 59 card `Source:` lines checked mechanically, only 8 start on the `def` of the card's function. Example: `GitHub.assigned_at` is cited at 217, defined at 225; `Queue.session` at 413, `status_of` is at 416. In my sample 15 of 30 rows in the first batch and rows 100, 120, 200 were off. | `.github/bible/bible_queue.py:136` <!-- recheck: was .github/bible/bible_queue.py:136, version of the page unknown --> (`known_labels`, cited 134), `:225`, `:416`, `:893` (`main`, cited 820) | Re-read `bible_queue.py` and re-number every citation and card `Source:` line; re-stamp the cards; then re-run `coverage.py`. |
| V-002 | `lld/bible-mode-b/bible_queue.md:2228` card `settings_of` | Wrong | major | The function now rejects a missing or non-object marker, an unsafe `analysis` path, a `depth` outside `DEPTH_VALUES` and an unsafe model name, returning `None`. The card says it only parses the JSON and returns `None` on `ValueError`. | `.github/bible/bible_queue.py:329-349` <!-- recheck: was .github/bible/bible_queue.py:329-349, version of the page unknown --> | Rewrite the card with the four checks, their branch lines and the security reason in the docstring; stamp `828d76009663`. |
| V-003 | `lld/bible-mode-b/bible_queue.md:2120` card `main` | Overstated | major | `main` now has `--analysis` and `--depth` options, and refuses settings that `settings_of` rejects; the card omits all three, and its step 4 ("builds settings") hides a failure exit. | `.github/bible/bible_queue.py:893-939` <!-- recheck: was .github/bible/bible_queue.py:893-939, version of the page unknown --> | Rewrite the card (call list, steps, branches 910-939) and stamp `d5e645d7911f`. Same for the other two cards the gate lists, `Queue.assemble_phase` and `Queue.delta` (stamps `65f9f5e822c9`, `3f36a2609939`); I did not audit those two. |
| V-004 | `README.md` "Status" table; `ledger/coverage-ledger.md` last section | Inconsistent | major | Both say the gate passes ("PASS at deep", "all 217 branch lines are cited"). The gate returns GAPS with 29.1% of branch lines cited. | `verification-coverage.md` | State the real gate result, or fix the cards and re-run. |
| V-005 | `lld/bible-mode-b/bible_queue.md` | Omission | major | `Queue.continue_if_unfinished` (a method that re-asks Copilot to continue and checks the timeline) and `GitHub.me` have no card or helper row. `assemble_phase` calls the first. | `.github/bible/bible_queue.py:155-159` <!-- recheck: was .github/bible/bible_queue.py:155-159, version of the page unknown -->, `:812-847` | Add a full card for each and the call-graph edges the gate lists (10 missing). |
| V-006 | `hld/` pages and `lld/data-dictionary.md` | Omission | minor | `tls-migration/tls-services.yaml` and `tls-migration/evidence/inventory.json` are never mentioned. They record a planned HTTPS migration for the catalog calls, which the HLD security pages say nothing about. Not significant: nothing there is deployed yet (`migrator_model: null`). | `tls-migration/tls-services.yaml:1-20` | Describe them in `reference/configuration.md` and `hld/06-cross-cutting.md`, or add them to `ledger/not-documented.md` with a reason. |
| V-007 | `lld/data-dictionary.md:90-104,140-141`, `knowledge/AGENT-CONTEXT.md:115` | Citation off | minor | 13 citations name analysis files (`codebase-analysis/components.json`, `.../status.json`, `reference/open-questions.md`) that the gate does not accept as targets; the files exist except the `open-questions.md` path, which is written as `codebase-analysis/reference/open-questions.md` from inside the folder. Cite the generating code or drop the citation. | `ledger/coverage-report.md` "Citations that do not resolve" | Replace with citations to the code that writes those files. |
| V-008 | `lld/bible-mode-b/bible_queue.md` (card `settings_of` area, helper cards) | Inconsistent | minor | Many "Called by: Queue functions in later source packets" rows are placeholders, not call sites (`age`, `settings_of`, `labels_of`, `comp_label`). | `lld/bible-mode-b/bible_queue.md:2208,2243` | Replace with the real callers. |
| V-009 | Branch tables of `bible_queue.md` | Omission | minor | 43 functions have uncited branch lines (gate list), for example `Queue.run` (11 lines), `Queue.follow` (17), `main` (14). | `verification-coverage.md` "Branches not cited" | Add one row per branch. |

## Coverage findings

- The gate result is GAPS (table above). The file, route and card measures are 100%; the gaps are two symbols (V-005), 161 uncited branch lines in 43 functions (V-009), five call-graph edges short of 95% (V-005) and two unmentioned files (V-006).
- Four cards were written from code that has since changed: `settings_of`, `Queue.assemble_phase`, `Queue.delta`, `main` (V-002, V-003).
- `ledger/not-documented.md` does not exist, so nothing was excluded from the gate.
- Inventory totals: `README.md` says 14 source files and 1,343 lines; the gate counts 11 source files with symbols and my count of the changed file is 943 lines for `bible_queue.py` alone (the front-page total predates the change). This is part of V-004. The component rows (3, 4, 1 and 3 files) add up to the README's 14 by counting the workflow files and tests differently; I did not reconcile them.

## Depth findings

Files chosen: the five largest (`bible_queue.py` 943, `gate.py` 117, `plan.py` 62, `orders.py` 51, `service.py` 49), the file with the most routes (`service.py`), and the 3rd and 7th by path. Only these cards were opened:

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `components/orders/orders.py` | `order_total` | Complete | |
| `components/orders/orders.py` | `validate` | Complete | |
| `components/orders/orders.py` | `settle` | Complete | |
| `components/orders/catalog_client.py` | `remote_line_total` | Complete | |
| `tools/gate.py` | `main` | Complete | |
| `.github/bible/bible_queue.py` | `main` | Partial | `--analysis`, `--depth`, the `settings_of` refusal, the exit text (V-003) |
| `.github/bible/bible_queue.py` | `settings_of` | Wrong | The four safety checks (V-002) |

The three largest functions of `bible_queue.py` (`Queue.follow`, `Queue.assemble_phase`, `Queue.component`) were not audited because their line citations are off (V-001); audit them after the revision. The depth figure is therefore from seven cards only.

## Diagram findings

43 diagrams. I read the context diagram, the mind map and the front-page evidence table; I did not render any diagram.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README context | ok | ok | ok | ok | ok | ok | not rendered | Every edge has a protocol or purpose; the CDN edge is dashed and marked "no request", matching `catalog.py:32-33`. |
| Mind map | ok | ok | ok | n/a | n/a | ok | not rendered | Every leaf names an existing page. |
| Data model / lifecycle | present (`hld/04-data-architecture.md:35,55,98`) | not checked | not checked | not checked | not checked | not checked | not checked | |
| Remaining 40 | not checked | | | | | | | |

No `Wrong` or `Unsupported` statement stands behind a diagram element I checked. The `tls-migration` files are the one outside-system omission (V-006).

## Data dictionary and mind map findings

- Mind map: every leaf names a page that exists; all four components are on it.
- Data dictionary: I did not open the schema-level check for every store. Its `components.json` and `status.json` citations are off (V-007).

## Knowledge base findings

- `graph.json` carries `generated: 2026-11-23T22:52:29`. The checkout gives every file the same time, so I cannot say it is newer than the pages. Because the pages' line numbers are stale (V-001), regenerate it after the revision.
- I did not take the ten `analysis` and five `name-unique` edges, so the share of wrong edges is unknown.
- `AGENT-CONTEXT.md` states the three required limits (dynamic dispatch, `name-unique` and `analysis` leads, snapshot date). Seventeen of its citations point at `bible_queue.py`; the sampled ones are off (row 260 held, 280 held).

## Readability and prose findings

I read the front page, one HLD page and the `catalog` card pages: they open with a summary, are plain and in a sensible order. No claim numbers (`C-154` style) and no template text found. The only readability issue is V-008. I checked only a few sentences of the HLD pages against their citations: no sentence went beyond its citation.

## Ledger findings

- Completeness: all seven folders and 20 files in scope are in `ledger/coverage-ledger.md`.
- "Read in full": every file is listed as read in full; for `bible_queue.py` the ledger is not true of the current file (V-001, V-005).
- No "not read", "sampled" or "excluded" rows exist.

## Consistency findings

- V-004 (gate result stated as PASS), V-008.
- The README, `status.json` and the component reports all place `tools`, `catalog`, `orders` and `bible-mode-b` consistently; names agree across the mind map, HLD and LLD pages I opened.
- No secret value found in the pages I read; the token is named only as `secrets.BIBLE_ASSIGN_TOKEN`.

## Limits

- A reduced sample was checked, not every citation, and groups A and C were only partly covered; rows 620 to 1040 and 1660 to 1740 were not judged.
- The coverage script matches names; it does not read meaning. The depth audit covers seven cards.
- Verification shows the analysis matches the code, not that the code matches what runs in production.
- Diagrams were read, not rendered. The knowledge-graph edge checks were not done, so the graph is a lead only.
- If the same model wrote and verified the analysis (the author's model is not recorded), a person or another model should re-check V-001 to V-005 and a few confirmed statements.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 2, 22, 42, 62, 82, 142, 162, 182, 202 | A | Confirmed | |
| 102, 122 | A | Citation off | `bible_queue.py` lines moved (V-001) |
| 297, 305, 464, 1140, 1266, 1270, 1272, 1274, 1276, 1280, 1283, 1299, 1365, 1370 | B | Confirmed | inferred marks are right |
| 294, 1110, 1190 | C | Confirmed | |
| 20, 40, 60, 80, 140, 160, 180, 220, 240, 260, 280, 300, 320, 340, 360 | D | Confirmed | |
| 100, 120, 200, 380, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600 | D | Citation off | `bible_queue.py` lines moved (V-001) |
| 1060 to 1180, 1220 to 1640 step 20 | D | Confirmed | |
| 1200 | D | Citation off | analysis file as target (V-007) |

<!-- cites .github/bible/bible_queue.py@9084f4915d286441c5b3a9a29a8df059bf76dacc -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites tls-migration/tls-services.yaml@b494ef963f852e6359ef12c79eed00a71427eaf0 -->
