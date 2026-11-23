# Revision mode

Use when the user gives a verification report. Do not start the analysis again.

## Component mode

When the report is a component's (`ledger/components/<name>/verification-report.md`), the same steps apply, with these changes, because the component writes only its own folders:

- Keep the log in `ledger/components/<name>/revision-log.md`, with the status line at its top (no front page yet).
- Do not re-run `inventory.py`, `knowledge.py` or `status.py --write`: they rewrite shared files. `coverage.py --component <name>` (run by `next.py --component <name>`) is the check; it has its own drift check.
- Findings about shared files (`progress.md`, `ledger/coverage-ledger.md`, reference pages) go in the README's `## For the whole-system pages` section for the assemble run.
- Number the report's corrections as it does (`V-001`), and your own items `N-01`, `N-02`, in the same log.
- Start with `next.py --component <name>`: while the corrections are not applied it prints `NEXT REVISION <name>`, never `COMPONENT DONE`. A passing gate is not a revision: the report's corrections are.
- Start the round's section of the log with `Applied from verification-report.md, fingerprint <the report's fingerprint>`, then record every correction (`V-001`, ...) under it, with what you changed or, when no page needs to change, why. Correction numbers restart in every report, so only the section under this report's fingerprint counts. `next.py` moves on once a page has changed since the verification, or once that section names every correction.
- Done when `next.py --component <name>` prints `COMPONENT DONE <name>` again. Only `major` corrections need a new verification.

## Work through every item

Every item counts, not only the numbered corrections: coverage, depth, diagram, readability and consistency findings, and small points made without asking for a change. Give unnumbered items your own numbers (`N-01`, `N-02`, ...).

For each item:

1. Re-open the cited code yourself. The verifier can be wrong; if the code disagrees with the correction, follow the code and say so in the log.
2. Apply it:

   | Item | Action |
   | --- | --- |
   | Wrong or unsupported statement | Remove it, or replace it with what the code shows. Log the old wording. |
   | Overstated statement | Narrow it to what the cited lines support, or mark it `(inferred: ...)`. |
   | Citation off | Correct the path or lines after opening the file. |
   | Shallow card | Rewrite the card from the code: every branch, value, field, call and error. |
   | Missing file, function, route, table or outside system | Add the page, card, row or diagram element where it belongs. |
   | Inconsistent summary, flow step, diagram label or count | Fix the text. |

3. Update everything that rested on a changed statement: diagrams and their evidence tables, summaries, flow steps, the mind map, the component READMEs and the questions.
4. Move questions the revision answers to a "Closed in revision" table in `reference/open-questions.md`, with the page that answers them. Their numbers are retired.

## Bookkeeping

- Re-run `inventory.py` and `coverage.py`; the gate must pass again.
- **Ledger:** files opened for the first time, changed statuses, totals.
- **Front page status:** `CORRECTED AFTER VERIFICATION (report of <date>; <n> statements added or changed since, not re-verified)` when every item is applied, otherwise `DRAFT, corrections outstanding`.
- **`revision-log.md`:** one row per item, from the template.
- **Status for other skills:** run `scripts/status.py --write`. The pages have changed since the report, so it reports the analysis as not verified until a verifier, in a new session on a different model, re-checks every corrected statement and records the new fingerprint (verifying skill, references/report.md).
- **`run-notes.md`:** any judgement made without the user.

Then run the depth audit, the diagram audit and the evidence audit from [quality-gate.md](quality-gate.md) on every added or changed page, card and diagram, and tell the user those parts are unverified.

## What comes next

| Report | Next |
| --- | --- |
| `FAIL` | Full verification again |
| `PASS AFTER CORRECTIONS` with a `major` correction | Verification of the added and changed parts |
| `PASS AFTER CORRECTIONS` with only `minor` corrections, or `PASS` | None required |

## An analysis made with an earlier version

Decide by what is on disk:

- Pages contain claim numbers like `C-154`, or `units/` or `components/` folders exist: start a new analysis from pass 1. Keep its open questions, and any fact you re-confirm with the code open. Tell the user the claim numbers will disappear.
- Otherwise, when `coverage.py --depth deep` lists missing front matter, pseudo-code, branch tables, call graphs or sequence diagrams: add them in place, then run pass 10.
