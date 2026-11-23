# Method

## Analysis inputs

Read these from the analysis folder in step 1, and list any that are missing:

- `README.md` (front page and totals)
- `hld/03-integrations.md` and `hld/06-cross-cutting.md`
- `reference/risks-and-surprises.md` and `reference/open-questions.md`
- `ledger/coverage-ledger.md`
- `verification-report.md` and, when present, `revision-log.md`

## Working through the rubric

For each check in [rubric.md](rubric.md): look in the code, then record one outcome: a finding, `sound`, `could not determine`, or `not applicable`.

- The order is yours; one file often settles checks in several areas. Keep `review-progress.md` in the analysis folder current, build the review from it, and leave it in place.
- A check with two parts that end differently is two lines, `X3a` and `X3b`.
- One finding may answer several checks. List them all; its area is where the harm is greatest.
- A real weakness that no check covers is still a finding. Give it the nearest area, mark its check "none (from H-xx)", and list it under "Gaps in the rubric".
- Where only a search or listing can answer (a count, an absence), give the pattern, scope and number of hits.
- General engineering knowledge may explain why something matters. The fact about this system must still come from the code.

## Limited coverage

A rubric check that depends on an area the ledger marks `not read` or `sampled` gets up to about five file reads, weighted to the areas the user asked for. If that does not settle it, record `could not determine` and what would.

If the verification verdict was `PASS AFTER CORRECTIONS`, check that `revision-log.md` shows the corrections applied, and state in the limits that revised claims were not verified again.

## Hypotheses

| Verdict | Use when |
| --- | --- |
| `Confirmed` | Evidence shows it. Link the finding. |
| `Partly confirmed` | True in some places. Say where it is and is not. |
| `Refuted` | Evidence shows the opposite. Cite it. |
| `Not determinable from the code` | Say what would settle it. |

- Judge the most natural reading. If it is false, the verdict is `Refuted`, even when a related weakness exists; report that weakness as its own finding. "Passwords are stored in plain text" is refuted when user passwords are hashed, even if a service credential sits in a configuration file.
- When a hypothesis has two natural readings, judge each and give both verdicts.
- `Refuted` means as far as the code can show. Say what the code cannot show.

## Severity

Use the table in [rubric.md](rubric.md). When the answer depends on deployment, rate the code as it is with its default configuration and state the condition: "High if the script is deployed". "When unsure, choose the lower" applies only to doubt about what the code does.

Confidence: `High` (all relevant code read), `Medium` (a representative part), `Low` (seen once, extent unknown).

## Root causes and plan

Group findings that share one cause: fixing a cause once beats fixing ten symptoms. Order the plan by most harm removed for least effort, with anything later work depends on first. Mark the first one to three items as the place to start.
