# Verification report

| | |
| --- | --- |
| Verdict | PASS |
| Scope | component bible-mode-b |
| Analysis fingerprint | 8d9c4cbe0922bf75 |
| Analysis snapshot | component row in `components.md`: 1 source file, 844 lines (2026-11-23); no version given |
| Repository at verification | 1 source file (`.github/bible/bible_queue.py`), 848 lines, plus 4 workflow files in `.github/workflows/`; coverage drift: `bible_queue.py` 844 -> 848 lines against the stored inventory (the pages already cite 848) |
| Depth stated / depth found | deep / deep (front matter, full cards with cited branch lines, call graph) |
| Verified with | GitHub Copilot coding agent (model not stated) |
| Analysis produced with | not stated |
| Sampling level | standard |
| Date | 2026-11-23 |

## Summary

The component's two pages (`lld/bible-mode-b/README.md`, `lld/bible-mode-b/bible_queue.md`) are complete and accurate. I re-ran the coverage gate: it passes (730 of 730 citations resolve, 66 of 66 functions have a full card, 161 of 161 branch lines are cited, 162 of 163 same-file call edges are drawn). The one missing edge, `check` -> `run`, is a name-matching artefact of the script: the code calls `subprocess.run` (`.github/bible/bible_queue.py:707`, `:711`), not `Queue.run`.

I judged 222 sampled citation rows and audited 9 of the largest cards. The corrections from earlier rounds (see `revision-log.md`) hold: the `Queue.component` card now matches the code, the five wrong graph edges are gone, and the `closed_revise` and `endswith` claims have been withdrawn. I found no major problems. Nine minor corrections remain (V-001 to V-009): a wrong count in the README, three wrong or incomplete "Called by" lines, a rule that drops one condition, vague "Called by" text on about ten helper cards, and one omission from the context diagram.

The verdict is `PASS`: the gate passes, accuracy is above 95%, every audited card is Complete, and no correction is major.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 1 / 1 (100.0%) |
| Symbols accounted for | 68 / 68 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 66 / 66 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 161 / 161, 162 / 163 (99.4%), 2 / 2 |
| Citations that resolve | 730 / 730 (100.0%) |
| Sampled rows checked | 222 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 216 / 3 / 2 / 1 / 0 (counts are from my notes; rows with a minor wording note count as Confirmed) |
| Accuracy (Confirmed + Citation off) | 219 / 222 (98.6%) |
| Citation quality (Confirmed) | 216 / 222 (97.3%) |
| Cards audited / Complete | 9 / 9 (100.0%) |
| Significant omissions | 0 |
| Major corrections | 0 |

## How the sample was selected

Standard level, component scope, from `ledger/components/bible-mode-b/citations.tsv` (730 rows).

- Group A: all 137 rows from the component README (#1-#137).
- Group B: the inferred claim at row #147.
- Group C: the rows that carry diagram edges fall inside the README rows already in group A.
- Group D: 84 rows from `bible_queue.md` whose index is divisible by 7.
- Group E: none. The component makes no calls into other components (`components.rows_of`, `component_map` and `assign` are in-process imports of the toolkit; the gate reports 0 of 0 calls).

Not applicable in component scope: the whole-system HLD, data dictionary, mind map and knowledge base.

## Earlier corrections re-confirmed

| Earlier correction (`revision-log.md`) | Result |
| --- | --- |
| `Queue.component` flow after `follow` | Fixed: the card returns the `follow` result unconditionally (`.github/bible/bible_queue.py:582-585`), with no `endswith` branch |
| Five wrong graph edges | Fixed: I checked every drawn edge in the `bible_queue.md` call graph against the calling body; only the two `main` -> `__init__` edges are not literal calls (constructor calls `GitHub(...)` and `Queue(...)`), which is acceptable |
| Function count 66, two classes | Confirmed by the gate and the source |
| `closed_revise` claim | Withdrawn; no mention remains in README Surprises |
| Unused `GitHub.prs` | Confirmed: no `.prs(` call site exists in the source |

## Corrections

| ID | Severity | Page / card | Problem | Fix |
| --- | --- | --- | --- | --- |
| V-001 | minor | README line 34 | Says the search for `bible_queue` or `.github/bible/` in `*.py` and `*.yml` returned six references. It returns seven: three in the source (lines 9-11), three in the workflows, and a comment at `.github/skills/analyzing-a-codebase/scripts/next.py:628` that mirrors the queue's revision rule. The conclusion (no component calls it) holds, but the coupling is not mentioned. | Correct the count and name the comment as a rule mirror, not a call |
| V-002 | minor | README R-07 | Omits the condition `verdict_is_newest` (`.github/bible/bible_queue.py:619`); the cited range 615-623 is slightly off (the hold is created at 619-627). The card has it right. | Add the condition and fix the range |
| V-003 | minor | `Queue.held` card, Called by | Lists lines 580, 599 and 733; the calls are at 540, 580 and 737. | Correct the lines |
| V-004 | minor | `Queue.reconcile` card, Called by | Cites `main` at 834 (a `gh.create_issue` call); the call is at 838. | Correct the line |
| V-005 | minor | `Queue.render` card, Called by | Misses the `plan_phase` call at 548. | Add it |
| V-006 | minor | `Queue.start_chunk` card | A multi-line call is cited as 631; it starts at 630. | Cite 630-631 |
| V-007 | minor | About ten helper cards (`labels_of`, `comp_label`, `issue_text`, `assignment`, `json_file`, `report_facts`, `as_int`, `status_of`, `age`, `settings_of`, `now`) | "Called by" says only "Queue functions in later source packets", with no lines. | List the real callers with lines (for example `labels_of` at 425, 433, 444, 472, 599, 646, 672) |
| V-008 | minor | README, context diagram | No node for the in-process `components` helpers (`rows_of`, `component_map`, `assign`) or the temporary tarball tree, although the outbound-calls table lists them. | Add the nodes, or say they are omitted |
| V-009 | minor | README R-02 and `GitHub.tarball` card | R-02 says the selection must be `all` or a list; the code lets `all` mix with names. The tarball card implies tar errors are wrapped; only the request errors are. | Reword both |

## Coverage findings

- Gate result: PASS.
- Missing edge `check` -> `run`: a name-matching artefact (see Summary), not a defect.
- Drift: 844 lines in the stored inventory, 848 now; the pages already cite 848. Refresh the inventory when the next analysis run records it.
- `ledger/not-documented.md` does not exist, which means nothing is excluded.

## Depth findings

| Card | Score | Reason |
| --- | --- | --- |
| `Queue.component` (565-642) | Complete | Steps, pseudo-code and branch table match the code |
| `Queue.follow` (644-696) | Complete | Every branch line checked |
| `Queue.check` (698-715) | Complete | |
| `Queue.assemble_phase` (717-757) | Complete | |
| `Queue.render` (759-769) | Complete | Caller list misses line 548 (V-005) |
| `Queue.run` (489-525) | Complete | |
| `GitHub.tarball` (234-259) | Complete | Minor wording (V-009) |
| `Queue.delta` (772-798) | Complete | Steps, pseudo-code and the three branch rows match |
| `main` (801-844) | Complete | Steps and cited lines match; the `SystemExit` conditions are all listed |

I also checked all 165 branch-table rows in `bible_queue.md` against their source line: the kind (if, for, try, return and so on) fits the cited line in 164 of 165. The one apparent mismatch (line 548, "conditional expression") is a multi-line call that does contain a conditional expression, so it holds.

## Diagram findings

| Diagram | Findings |
| --- | --- |
| README flowchart (context and structure) | D3 minor: see V-008. Edges and labels match the evidence rows. |
| README sequence diagram | Steps match the cited code; the `alt` blocks cover the hold and retry paths (D5). |
| README state diagram | States and transitions match the labels and rules. |
| README class diagram | `GitHub`, `Queue` and their relations match the source. |
| `bible_queue.md` call graph | Every edge checked against the caller's body; no wrong edge. Names are readable. |

Not rendered, only read (see Limits). Outside systems: the GitHub REST and GraphQL APIs, the tarball download, and the temporary directory are all drawn or tabled; no urllib, subprocess or tarfile use is missing.

## Data dictionary and mind map findings

Not applicable in component scope.

## Knowledge base findings

Not applicable in component scope.

## Readability findings

Both pages open with a summary and an index. No leftover claim numbers were seen. The "later source packets" wording in V-007 is a writing leftover.

## Ledger findings

No whole-system ledger checks apply in component scope. `ledger/not-documented.md` is absent, which means none.

## Consistency findings

Totals agree across the pages: 1 file, 848 lines, 66 functions, 2 classes. Names agree. No secret value appears; the token is referred to only by its variable name. Calls into other components: none.

## Limits

- I judged a sample (222 of 730 rows), not every citation. The gate matches names, not meaning.
- Diagrams were read, not rendered.
- The tally counts come from my working notes and may be off by one or two rows.
- The model that wrote the analysis is not stated; a person should re-check the card text for the two cards most changed in earlier rounds (`Queue.component`, `Queue.follow`).
- I did not run the code.

## Everything checked

All 137 README rows; row #147; 84 `bible_queue.md` rows (index divisible by 7); every "Called by" line citation (script check); 165 branch-table rows against their source lines; every call-graph edge in `bible_queue.md`; 9 cards in full; the four workflow files against the README rows that cite them. Fingerprint recorded: 8d9c4cbe0922bf75.
