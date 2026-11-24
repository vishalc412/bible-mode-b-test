# Verification report

| | |
| --- | --- |
| Verdict | PASS AFTER CORRECTIONS |
| Analysis fingerprint | c2be3c0916a66a73 |
| Analysis snapshot | 24 in-scope files, 1,606 current source lines, 2026-11-23, no version given (front page); `ledger/coverage-ledger.md` still says 20 files |
| Repository at verification | 24 files in scope, 11 source files (`coverage.py`), 2026-11-23, no version given. `.github/bible/bible_queue.py` is 1,291 lines; the inventory recorded 1,130 |
| Depth stated / depth found | deep / the deep gate returns GAPS |
| Verified with | GitHub Copilot coding agent; model not recorded |
| Analysis produced with | Copilot coding agent; model not recorded (front page) |
| Sampling level | quick, reduced (see "How the sample was selected") |
| Date | 2026-11-23 |

## Summary

The analysis is accurate for `catalog`, `orders` and `tools` and stale for `.github/bible/bible_queue.py`. Every statement I opened for those three components was true, and all 21 `inferred` statements were correctly marked, apart from one citation that points at the wrong lines. The `bible-mode-b` queue file grew from 1,130 to 1,291 lines after its pages were written. In my sample 15 of 17 citations to it point at the wrong lines, although the behaviour they describe mostly exists elsewhere in the file. The file holds 916 of the 1,886 citations (48%), so the `bible-mode-b` page cannot be navigated by line number until it is revised.

The front page says the coverage gate passes (111/111 symbols). When I ran it, it returned GAPS: 111/116 symbols, 21.8% of branch lines cited, 90.9% of same-file calls drawn, and 10 cards written from code that has since changed. I rate this PASS AFTER CORRECTIONS. File, symbol and route coverage are at least 95%, sampled accuracy is above 85%, the cards I audited are Complete or Partial, and there are four major corrections, each fixable by re-running the analysis on the one changed file. This verification and the earlier one (`verification-report-2026-11-23.md`) found the same problem.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 11 / 11 (100.0%) |
| Symbols accounted for | 111 / 116 (95.7%) |
| Functions with a full card (pseudo-code, branches cited) | 93 / 93 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 65 / 298 (21.8%); 210 / 231 (90.9%); 17 / 17 (100.0%) |
| Routes with an endpoint card | 0 / 0 by the scanner (100.0%); the two GET routes have cards by hand (`lld/api/catalog/catalog.md`) |
| Citations that resolve | 1886 / 1886 (100.0%): they resolve to lines that exist, not to the right lines |
| Coverage gate | GAPS |
| Citations in the analysis / checked | 1886 / 59 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 43 / 16 / 0 / 0 / 0 |
| Omissions (significant) / Inconsistent | 0 / 3 |
| Accuracy / citation quality | 100.0% / 72.9% |
| Cards audited: Complete / Partial / Shallow / Wrong | 2 / 1 / 0 / 0 |
| Depth / depth, usable | 66.7% / 100.0% (3 cards only; see Limits) |

Accuracy counts a `Citation off` as accurate, so 100% overstates the queue page: 15 of its 17 sampled citations are off. Citation quality is the fairer figure.

## How the sample was selected

Level `quick`, reduced. I did not judge the full group A, C and D rows from `ledger/citations.tsv` (1,886 rows).

- Group B: all 21 rows labelled `inferred` (299, 307, 466, 1274, 1398-1399, 1402-1408, 1411-1413, 1415, 1431, 1497, 1499, 1502).
- Group A and D, queue file: 17 rows citing `bible_queue.py`, every row whose index is divisible by 61 (122, 366, 427, 488, 549, 610, 671, 732, 793, 854, 915, 976, 1037, 1098, 1159, 1342, 1830).
- Group A and D, other files: 21 rows citing other files, every row whose index is divisible by 47 (47, 94, 141, 188, 235, 282, 329, 423, 1222, 1269, 1316, 1410, 1457, 1504, 1551, 1598, 1645, 1692, 1739, 1786, 1880).

I did not run group C (business rules, outbound calls, security) as a separate group. Its rows are covered only where they fall in the rows above.

## Earlier corrections re-confirmed

The earlier report (`verification-report-2026-11-23.md`) lists five major corrections. They are not re-confirmed. The cards that report called out (`main`, `settings_of`) were not re-read. `GitHub.me` and `Queue.continue_if_unfinished` now have cards (`lld/bible-mode-b/bible_queue.md:2231`); the `Queue.render` card is stamped, but its lines are still old (V-003).

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/bible-mode-b/bible_queue.md`, `lld/bible-mode-b/README.md`, `hld/05-key-flows.md`, `reference/configuration.md`, `lld/data-dictionary.md`: rows 122, 427, 488, 610, 671, 732, 793, 854, 915, 976, 1037, 1098, 1159, 1342, 1830 | Citation off | major | The queue file is 1,291 lines and the cited lines now hold other code: row 488 cites line 170 (a docstring) for a call site, 671 cites line 281 (a `raise`) for a tar path check, 1098 cites line 1126 (`def continue_if_unfinished`) for a `SystemExit`, 1830 cites 96-110 (label text) for `GITHUB_API_URL`, which is at line 107 | `.github/bible/bible_queue.py:170,281,1126,107` | Re-run the delta update for the file and re-cite every row to the current lines; the sampled rows suggest about 900 are off |
| V-002 | `lld/bible-mode-b/bible_queue.md` Index | Omission | major | Five symbols have no card or helper row: `shown_files`, `Queue.could_not_check`, `Queue.whole_fingerprint`, `Queue.deferred_updates`, `Queue.whole_hold` | `.github/bible/bible_queue.py:369-374,879-890,892-907,1024-1036,1038-1044` | Add cards and call-graph edges. `assemble_phase` calls all of them |
| V-003 | `lld/bible-mode-b/bible_queue.md:2268-2303` (`Queue.render`) | Overstated | minor | The card is stamped `651906b39ffd` and cites lines 1021-1031; the method is at 1166-1177. It omits the hidden `<!-- bible-state ... -->` block built from `self.state` | `.github/bible/bible_queue.py:1166-1177` | Rewrite from the code. The gate lists nine more cards written from changed code: `GitHub.tarball`, `Queue.reconcile`, `run`, `component`, `follow`, `check`, `assemble_phase`, `revise_all_step`, `delta` |
| V-004 | `README.md` front page, Coverage row, and `Status: DRAFT` line | Inconsistent | major | Front page says "PASS at deep: 111/111 symbols, 274/274 branch lines". The gate I ran returns GAPS at 111/116 symbols and 65/298 branch lines | `verification-coverage.md` | Replace the line with the gate's figures after revision |
| V-005 | `lld/bible-mode-b/bible_queue.md` Index and "Lines" row | Inconsistent | major | The page says 867 lines and indexes `Queue.render` at 778-788, but the file has 1,291 lines and `render` is at 1166-1177. 46 branches are not cited in their cards (21.8% cited) and 21 call-graph edges are missing | `.github/bible/bible_queue.py:1166`; `verification-coverage.md` | Update the line count and index with the rewrite. Cite every branch line |
| V-006 | `lld/bible-mode-b/bible_queue.md:447` (row 466) | Citation off | minor | `GitHub` starts at line 104 and sets its fields at 105-108. Lines 88-92 are label text. The same stale line range is cited at `:445` | `.github/bible/bible_queue.py:104-108` | Cite 104-108 |
| V-007 | `ledger/coverage-ledger.md` | Inconsistent | minor | The ledger says 20 files. Four files under `tls-migration/` (`01-inventory.md`, `02-certificate-plan.md`, `tls-services.yaml`, `evidence/inventory.json`) are in scope and have no row | `ledger/delta.md` "Files added" | Add rows. The coverage gate still lists 24 files in scope |

## Coverage findings

- `coverage.py` run by me at depth deep returned `GAPS`: symbols 95.7%, branch lines 21.8%, same-file calls 90.9%, 10 cards from changed code. All the gaps are in `.github/bible/bible_queue.py`. The other ten source files have no gaps.
- `ledger/not-documented.md` does not exist, so nothing is listed as exempt.
- Totals: front page says 24 files and 1,606 source lines; the coverage report counts 24 files. The ledger says 20 (V-007). The two calls from `orders` into `catalog` (`line_total` to `price_of`, `validate` to `in_stock`) are cited on their cards.

## Depth findings

Only three cards were audited, so the figures above are a sample of a sample.

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `components/orders/orders.py` | `order_total` | Complete | none. Steps, both branches and the propagating `KeyError` match lines 23-32 |
| `components/orders/orders.py` | `validate` | Complete | none. The `elif` and the unknown-SKU case match lines 35-42 |
| `.github/bible/bible_queue.py` | `Queue.render` | Partial | the `bible-state` block; lines are stale (V-003) |

I did not audit the five largest files, the route file or the 3rd and 7th files as the rule requires.

## Diagram findings

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` context diagram | ok | ok | ok | ok | ok | ok | not rendered | Read only. Edges carry protocol labels. The CDN edge is dashed and the image URL is not fetched, which matches `catalog.py` |
| Other diagrams (`hld/`, `lld/`) | not checked | not checked | not checked | not checked | not checked | not checked | not checked | Not reviewed in this session |

## Data dictionary and mind map findings

Not checked in this session.

## Knowledge base findings

Not checked in this session. The gate reports front matter on 17 of 17 LLD pages. `knowledge/graph.json` was not compared with the page times; given the stale pages, treat the graph's `bible_queue.py` edges as leads.

## Readability and prose findings

Not checked beyond the pages opened for sampling. Those pages read plainly and the `orders` and `tools` cards were easy to follow.

## Ledger findings

- V-007: `tls-migration/` is missing from `ledger/coverage-ledger.md`.
- "Read in full", "not read" and "excluded" rows were not sampled.

## Consistency findings

V-004, V-005 and V-007. The status line says DRAFT while the front page claims PASS. Nothing resembling a secret value appeared in the pages I opened.

## Limits

- A sample of 59 of 1,886 citations was checked, and three cards were audited. Group C was not run as a group. Diagrams, the data dictionary, the mind map, knowledge base, readability and ledger checks were not done. The verdict rests on the gate figures and the sample only.
- The coverage script matches names; it does not read meaning.
- Verification shows the analysis matches the code, not what runs in production.
- Diagrams were read, not rendered.
- The same kind of model wrote and verified the analysis. A person or another model should re-check the major corrections and a few confirmed statements.
- Citations to `bible_queue.py` are mostly off; whoever uses `knowledge/graph.json` should treat its edges from that file as leads.

## Everything checked

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 299, 307, 1274, 1398-1399, 1402-1408, 1411-1413, 1415, 1431, 1497, 1499, 1502 | Group B, inferred | Confirmed | Each inferred note rests on code or a comment that says so |
| 466 | Group B | Citation off | V-006 |
| 47, 94, 141, 188, 235, 282, 329, 423, 1222, 1269, 1316, 1410, 1457, 1504, 1551, 1598, 1645, 1692, 1739, 1786, 1880 | Index divisible by 47, not the queue file | Confirmed | |
| 366, 549 | Index divisible by 61, queue file | Confirmed | |
| 122, 427, 488, 610, 671, 732, 793, 854, 915, 976, 1037, 1098, 1159, 1342, 1830 | Index divisible by 61, queue file | Citation off | V-001 |
