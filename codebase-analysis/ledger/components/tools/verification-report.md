# Verification report

| | |
| --- | --- |
| Verdict | PASS |
| Scope | component tools |
| Analysis fingerprint | 381f98a228eed7a1 (`status.py --fingerprint --component tools`, run when judging was done) |
| Analysis snapshot | 3 source files, 210 lines, 2026-11-23 (`components.md`, `tools` row) |
| Repository at verification | 3 source files, 210 lines (`tools/fanout.sh` 31, `tools/gate.py` 117, `tools/plan.py` 62); no drift |
| Depth stated / depth found | deep / deep (every function has a card with pseudo-code and a cited branch table; the shell script has a module-level flow) |
| Verified with | GitHub Copilot coding agent (model not stated by the runtime) |
| Analysis produced with | not stated |
| Sampling level | standard |
| Date | 2026-11-23 |

An earlier report of the same date is kept as `verification-report-2026-11-23.md`. This round re-ran the gate, re-selected and re-judged the sample, and re-opened the cited lines itself; it did not copy that report's verdicts.

## Summary

The `tools` analysis (`lld/tools/README.md`, `gate.md`, `plan.md`, `fanout.md`) is complete, accurate and deep. The gate passes at every measure (3/3 files, 7/7 symbols and cards, 273/273 citations resolve). Of 105 sampled citations, 104 are confirmed and 1 is true but cited at lines that do not show it. Five cards were audited: four are complete, one (the `fanout.sh` script flow) lacks failure behaviour. There is no major correction, no significant omission and no secret value. The weaknesses are minor: one citation range, one imprecise verb (`sys.path.insert(0, ...)` described as "appends"), missing failure cases for `fanout.sh`, two diagram-syntax slips, and a structure diagram that leaves out the artifact files `gate.py` reads. Depth is exactly at the 80% threshold for `PASS` (4 of 5), so one more partial card would have changed the verdict. One statement rests on a user answer recorded by the author (Q1 in `questions.md`) that I could not confirm with the user.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 3 / 3 (100.0%) |
| Symbols accounted for | 7 / 7 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 7 / 7 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 39 / 39; 6 / 6; 4 / 4 pages |
| Routes with an endpoint card | 0 / 0 (none declared) |
| Citations that resolve | 273 / 273 (100.0%) |
| Coverage gate | PASS (`verification-coverage.md`, run by me) |
| Citations in the analysis / checked | 273 / 105 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 104 / 1 / 0 / 0 / 0 (V-002, Overstated, is outside the sample) |
| Omissions (significant) / Inconsistent | 0 / 2 (4 minor omissions, none significant; the 2 inconsistencies are diagram syntax) |
| Accuracy / citation quality | 105 / 105 = 100.0% / 104 / 105 = 99.0% |
| Cards audited: Complete / Partial / Shallow / Wrong | 4 / 1 / 0 / 0 |
| Depth / depth, usable | 4 / 5 = 80.0% / 5 / 5 = 100.0% |

Gate measures: files 3/3, symbols 7/7, cards 7/7, citations resolve 273/273 (needs 98%), branch lines 39/39, same-file calls 6/6, front matter 4/4, calls into other components 0/0. Drift since the stored inventory: none. `ledger/not-documented.md` does not exist, so nothing is excluded. The regenerated `citations.tsv` is byte-identical to the author's copy.

## How the sample was selected

`ledger/components/tools/citations.tsv` (273 rows) at `standard` level:

- Group A (citations in the component `README.md`, standing in for `hld/`): all 77 rows, indexes 1-77.
- Group B (`inferred` or `assumed`): none; the label column is empty on every row.
- Group C (headings with rule, outbound, calls out, integration, security, secret, auth, permission): the matching sections (Business rules, Outbound calls) are on `README.md`, already in group A.
- Group D (all other rows with index divisible by 7): 28 rows, indexes 84, 91, 98, 105, 112, 119, 126, 133, 140, 147, 154, 161, 168, 175, 182, 189, 196, 203, 210, 217, 224, 231, 238, 245, 252, 259, 266, 273.
- Group E (calls into other components): none; the component calls into no other.

Total 105 rows. For each I read the sentence or table row and the cited lines in `tools/gate.py`, `tools/plan.py` or `tools/fanout.sh`.

## Earlier corrections re-confirmed

none (first round with corrections from this checker; the previous same-day report's eight findings V-001 to V-008 were each re-opened below and all still hold).

## Corrections

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `lld/tools/README.md:23`, row 3 (`tools/fanout.sh:1-6`) | Citation off | minor | Lines 1-6 are the shebang, header comments and `set -euo pipefail`; the first use of `gh` is at line 10 | `tools/fanout.sh:10` | Add `tools/fanout.sh:10` to the citation for "external `gh` command" |
| V-002 | `lld/tools/plan.md:156`, row 273 area (citation `tools/plan.py:14-18`) | Overstated | minor | The module calls `sys.path.insert(0, ...)`, which puts the `tools` directory first; it does not append | `tools/plan.py:14` | Write "inserts the resolved `tools` directory at the front of `sys.path`" |
| V-003 | `lld/tools/fanout.md` Module-level code step 4 | Omission | minor | Both `gh label create` commands send standard output to `/dev/null` (line 10 and line 12); the page and README Logging mention only line 10 | `tools/fanout.sh:10`, `tools/fanout.sh:12` | Say that both label commands discard standard output |
| V-004 | `lld/tools/fanout.md` Module-level code, Branches and errors | Omission | minor | Under `set -euo pipefail` the script stops at the first failing command: `repo="$1"` fails with an unbound-variable error when no argument is given; a missing or invalid `plan.json` stops at the `components=$(python3 ...)` assignment; a failing `gh` call stops the loop part-way after earlier components already have issues. The plan path is relative to the working directory | `tools/fanout.sh:6`, `tools/fanout.sh:7`, `tools/fanout.sh:9`, `tools/fanout.sh:10-12` | Add these failure cases and the working-directory requirement |
| V-005 | `lld/tools/gate.md:211` (`check` step 3) and branch rows 57-61 | Omission | minor | Pass 2 matches by substring: `site["at"] in l` lets `x.py:1` match a row for `x.py:12`; `"ASK" in r` matches any case-sensitive occurrence; an `ASK` match takes precedence over `CHANGE`/`KEEP` on the same row. Pass 1 likewise tests the function name as a substring of the whole inventory text | `tools/gate.py:49-50`, `tools/gate.py:56`, `tools/gate.py:59`, `tools/gate.py:61` | State that these are substring tests |
| V-006 | `lld/tools/README.md:47` (edge `fanout --> gh`) | Inconsistent | minor | The label contains `;`, which the diagram syntax subset forbids (D9) | `lld/tools/README.md:47` | Replace `;` with a comma or dash |
| V-007 | `lld/tools/gate.md:49` (node `ct[count_tests]`) | Inconsistent | minor | Unquoted label while the other nodes are quoted (D9) | `lld/tools/gate.md:49` | Write `ct["count_tests"]` |
| V-008 | `lld/tools/README.md` Structure diagram | Omission | minor | The Data section lists `status.json`, `inventory.md`, `risks.md`, `tests-report.md` (read by `gate.py`) and `components/*/*.py` (read by `plan.py`), and `gate.py` starts a `python -m unittest` subprocess; none is in the diagram | `tools/gate.py:46`, `tools/gate.py:52`, `tools/gate.py:64`, `tools/gate.py:73-75`, `tools/plan.py:23` | Add them as nodes or note why they are left out |

None is `major`. V-003, V-004, V-005 and V-008 are omissions of detail, not significant omissions.

## Coverage findings

None. Gate result `PASS`; every measure is 100%. No drift (31 + 117 + 62 = 210 lines, 3 files). No `not-documented.md`, so no hand-written code is excluded. No `C-` claim numbers and no old-layout folders.

## Depth findings

The component has fewer than seven files, so the largest card of each non-test file was audited, plus each Python `main`. Each was read next to the code (branches, compared values, fields, calls, errors).

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `tools/gate.py` | `check` (37 lines) | Complete | Nothing a reader needs; the substring matching (V-005) is a wording gap, and "other values of `n` return no errors" is stated |
| `tools/gate.py` | `main` | Complete | Nothing; `--pass 0` (falsy), absent status file and non-object status are all stated |
| `tools/plan.py` | `scan` | Complete | Nothing; test files are read but not scanned, non-recursive glob stated |
| `tools/plan.py` | `main` | Complete | Nothing |
| `tools/fanout.sh` | script flow (Module-level code) | Partial | Failure behaviour under `set -euo pipefail` and the discarded output of the component-label command (V-003, V-004) |

## Diagram findings

Diagrams were read, not rendered.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` Structure (flowchart) | ok | ok | minor (V-008) | ok | ok | ok | minor (V-006) | Every edge has an evidence row and the cited lines show it (rows 19-25 confirmed). Searching `tools/` for outside reach finds only `gh` (shown) and the unittest subprocess (not shown) |
| `gate.md` Call graph | ok | ok | ok | ok | ok | ok | minor (V-007) | Edges match the code: `check` to `read` (46, 52, 64), `check` to `count_tests` (69-70), `main` to `fail`, `read`, `check` |
| `plan.md` Call graph | ok | ok | ok | ok | ok | ok | ok | `main` to `scan` (45), `scan` to `gate.count_tests` (36) |

D1: a component with no routes, no store schema and no record lifecycle needs the structure diagram and a call graph per module; both are present. No sequence diagram is expected (no endpoint with three or more participants).

## Data dictionary and mind map findings

Not applicable in component scope. Data this component owns: `plan.json` is written by `plan.py` with `version`, `passes` and per-component `sources`, `tests`, `test_count`, `functions`, `http_sites` (`tools/plan.py:46-54`, `tools/plan.py:39-40`); the pages list them correctly. No finding.

## Knowledge base findings

Not applicable in component scope (`knowledge/` does not exist yet). The four pages carry the front matter the gate requires (4/4).

## Readability and prose findings

- `README.md` and the three module pages open with a header table and a summary, follow a sensible order, and the index lets a reader find every function. Nothing blocks understanding.
- No claim numbers, no evidence-bullet lists standing in for explanation, no template text.
- Every sentence or row on `README.md` that cites lines was in the sample (rows 1-77); none says more than its citation apart from V-001.

## Ledger findings

Not applicable in component scope. `status.json` says `COMPONENT_DONE` with 3 of 3 packets, the precondition for this check.

## Consistency findings

- Names agree across the four pages (`gate`, `plan`, `fanout`, `plan.json`, `ENGINE`, `gh`).
- Counts agree with the code and `components.md`: 3 files, 210 lines, 7 Python functions, 0 routes.
- Line anchors on the pages match the sources today in every sampled row and in the branch tables I read for `check`, `main` and `scan`.
- No secret value in the pages (search for password, secret, token, api key found none).

## Limits

- A sample was checked (105 of 273 citations); the depth audit covers five cards, not every card.
- The coverage script matches names; it does not read meaning.
- Verification shows the analysis matches the code, not that the code matches what runs in production. Nothing was run except the coverage script.
- Diagrams were read, not rendered.
- That `component-analysis` in `tools/fanout.sh:13-15` is "a stale reference left over from an earlier experiment" and that "no external skill is intended" (`README.md:122`, `fanout.md:90`) rests on the author's recorded answer to Q1 in `questions.md`. I could not confirm it with the user: it is **unconfirmed**. The repository itself confirms the path is in the generated issue body and `.github/skills/` has no `component-analysis` directory.
- The analysis and this check were both made by assistants; the author's model is not stated. A person should re-check V-001 to V-008 and a few confirmed statements. Depth is exactly at the 80% line.
- Whole-system checks (HLD, mind map, data dictionary, knowledge graph, calls between components) were not part of this scope. `status.py --write` was not run, as component scope requires.

## Everything checked

Rows not simply confirmed:

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 3 (`README.md:23`, `tools/fanout.sh:1-6`) | group A | Citation off | V-001 |
| 273 (`plan.md:156`, `tools/plan.py:61-62`) | group D | Confirmed | The row itself holds; the neighbouring `plan.py:14-18` statement is V-002 (Overstated) |

Confirmed, by group:

- Group A: rows 1-2 and 4-77. Rows 73 and 74 confirm the `component-analysis` path at `tools/fanout.sh:14`; the "earlier experiment" history is unconfirmed (Limits).
- Group D: rows 84, 91, 98, 105 (repository part only), 112, 119, 126, 133, 140, 147, 154, 161, 168, 175, 182, 189, 196, 203, 210, 217, 224, 231, 238, 245, 252, 259, 266.

Statements checked outside the sample: `check` "other values return no errors" (`tools/gate.py:45-78`); `fail` callers (88, 98, 100, 103, 113); `.github/skills/component-analysis` absent; totals 3 files, 210 lines, 7 functions equal `components.md`.
