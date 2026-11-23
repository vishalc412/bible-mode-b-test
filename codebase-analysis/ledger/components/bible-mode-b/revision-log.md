# Revision log

Status: CORRECTED AFTER VERIFICATION (report of 2026-11-23; revised pages not yet re-verified).

## Current revision

Applied the current `next.py` revision packet for `.github/bible/bible_queue.py` (17 cards). Reopened and rewrote `GitHub.me`, `GitHub.is_agent_pr`, `GitHub.start_error`, `GitHub.pr_files`, `GitHub.tarball`, `GitHub.merge`, `settings_of`, `Queue.held`, `Queue.run`, `Queue.component`, `Queue.follow`, `Queue.check`, `Queue.assemble_phase`, `Queue.revise_all_step`, `Queue.continue_if_unfinished`, `Queue.delta`, and `main`; updated source stamps, branch tables, call-graph edges, and the component README. Source lines: `.github/bible/bible_queue.py:160-1126`.

Applied from verification-report.md, fingerprint 26ea3631571ae969.

| Item | Location | What was changed |
| --- | --- | --- |
| V-001 | `bible_queue.md` | Rebased the `main` and `settings_of` cards to the current source line ranges and removed stale branch rows. |
| V-002 | `bible_queue.md`, `settings_of` | Documented non-object markers, safe analysis paths, allowed depths, and model-name validation in the pseudo-code and branch table. |
| V-003 | `bible_queue.md`, `main` | Rewrote the steps and branches for `--analysis`, `--depth`, settings refusal, reconcile, delta, and current error handling. |
| V-004 | `README.md`, `ledger/coverage-ledger.md` | Updated source-file totals and current deep-gate figures: 111 symbols, 274 branch lines, 1,884 citations, and a 1,130-line queue file. |
| V-005 | `bible_queue.md` | Corrected callers for `GitHub.me`, `Queue.continue_if_unfinished`, and `Queue.revise_all_step` to current call lines. |

## 2026-11-23

Applied from verification-report.md, fingerprint dee0a05d04621400, of 2026-11-23, verdict PASS AFTER CORRECTIONS.

| Item | Location | What was done | Code re-opened | Agrees with the report? |
| --- | --- | --- | --- | --- |
| V-001 | `bible_queue.md`, `Queue.component` | Replaced the alleged conditional return of `follow` with its unconditional return; removed the false branch and call. | `.github/bible/bible_queue.py:577-591` | Yes |
| V-002 | `bible_queue.md`, `GitHub` cards | Added actual callers and marked `prs` unused. | `.github/bible/bible_queue.py:88-302`, `.github/bible/bible_queue.py:334-349`, `.github/bible/bible_queue.py:396-848` | Except `assign` at 785: that is `components.assign`, not `GitHub.assign`; omitted it. |
| V-003 | `bible_queue.md`, call graph | Removed five name-matched edges with incorrect receivers. | `.github/bible/bible_queue.py:334`, `.github/bible/bible_queue.py:349`, `.github/bible/bible_queue.py:402`, `.github/bible/bible_queue.py:706-711`, `.github/bible/bible_queue.py:826-830` | Yes |
| V-004 | `README.md`, Surprises and whole-system risks | Withdrew the claim that `closed_revise` is built but unused. | `.github/bible/bible_queue.py:604-618` | Yes |
| V-005 | `README.md`, Size | Corrected 67 functions/methods to 66. | `.github/bible/bible_queue.py:88-848` | Yes |
| V-006 | `README.md`, Outbound calls | Distinguished `ready`'s HTTP-only wrapper from `call` and `tarball`. | `.github/bible/bible_queue.py:105-117`, `.github/bible/bible_queue.py:234-243`, `.github/bible/bible_queue.py:283-291` | Yes |
| V-007 | `README.md`, Outbound calls and Structure | Added the two toolkit subprocesses and their edge. | `.github/bible/bible_queue.py:698-711` | Yes |
| V-008 | `README.md`, front matter and Responsibility | Named the independent proof-of-concept workflow. | `.github/workflows/poc-assign-copilot.yml:10-69` | Yes |
| V-009 | `README.md`, diagrams | Added reconcile sequence and session classification diagrams with evidence; added subprocess edge. | `.github/bible/bible_queue.py:413-429`, `.github/bible/bible_queue.py:455-487`, `.github/bible/bible_queue.py:644-655` | Yes; classification is recalculated, so no persistent state transitions are asserted. |
| V-010 | `bible_queue.md`, caller rows | Added `Queue.session` to `agent_events` and `assigned_at`, and `Queue.render` to `now`. | `.github/bible/bible_queue.py:419-420`, `.github/bible/bible_queue.py:763` | Yes |
| V-011 | `README.md`, Configuration | Corrected option, environment and depth-use citations. | `.github/bible/bible_queue.py:707-708`, `.github/bible/bible_queue.py:805-819` | Yes |
| V-012 | Both pages, citations | Corrected changed-file, PASS, logging and `run_issues` citations; separated module-level citations by claim. | `.github/bible/bible_queue.py:608-614`, `.github/bible/bible_queue.py:722-724`, `.github/bible/bible_queue.py:768-769`, `.github/bible/bible_queue.py:839-841` | Yes |
| V-013 | `README.md`, Surprises | Added the login-default discrepancy and unused `GitHub.prs`. | `.github/bible/bible_queue.py:36`, `.github/bible/bible_queue.py:60`, `.github/bible/bible_queue.py:172-174` | Yes |
| V-014 | `bible_queue.md`, Call graph | Described name matching and its receiver ambiguity. | `.github/bible/bible_queue.py:334`, `.github/bible/bible_queue.py:402`, `.github/bible/bible_queue.py:708-711` | Yes |
| V-015 | `README.md`, Tests | Removed the analysis-process sentence, retaining the search result. | `.github/bible/bible_queue.py:1-848` | Yes |
| N-01 | Whole-system catalog | The 844-to-848 line inventory drift belongs to shared planning files; component README already reports 848. Shared files were not edited in component mode. | `.github/bible/bible_queue.py:1-848` | Yes |

## Statements added

Workflow independence, subprocess calls, caller lists, diagrams and the login-default and unused-method surprises are documented in the component pages.

## Statements corrected

The `Queue.component` flow, five graph edges, function count, exception scope and citations were corrected.

## Statements withdrawn

The `closed_revise` claim, false `endswith` branch and process-only test sentence were removed.

## Questions closed or narrowed

None.

## Items not applied, with the reason

The `GitHub.assign` caller reported at line 785 is `components.assign`, a different function; see V-002.
