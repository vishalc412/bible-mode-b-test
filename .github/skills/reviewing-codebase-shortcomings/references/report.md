# Finding format, review template and self-check

## Finding format

```markdown
### F-007: Outbound calls to the issue host have no timeout

| | |
| --- | --- |
| Area | Reliability |
| Severity | High |
| Confidence | High: every call site read |
| Evidence | src/server/issues/client.ts:31-58; src/server/issues/batch.ts:112 |
| Checks | R1, I1 |
| Related | H-03 (confirmed), C-041 |

**What the code does.** Two or three factual sentences.

**Why it matters.** The concrete harm: what fails, for whom, when.

**Suggested fix.** The smallest change that removes the harm, then a better one if different.

**Effort.** S (hours), M (days) or L (weeks), and what drives it.
```

## Review template

Write `shortcomings-review.md` in the analysis folder.

```markdown
# Shortcomings review: <system name>

| | |
| --- | --- |
| Based on analysis | <snapshot, date, verification verdict> |
| Reviewed with | <assistant and model> |
| Date | |

## Summary
Overall state, the two or three findings that matter most, what is in good shape, and how far the system is from what its owners want.

## Scorecard
| Area | Critical | High | Medium | Low |
| --- | --- | --- | --- | --- |

Rubric checks by outcome (one finding can answer several checks):

| Area | Finding | Sound | Could not determine | Not applicable |
| --- | --- | --- | --- | --- |

## Hypotheses
| # | Hypothesis, as stated | Verdict | Evidence | Finding |
| --- | --- | --- | --- | --- |

## Findings
Ordered by severity, then area.

## Root causes
## Checked and found sound
| Area | Check | Scope looked at | Evidence |
| --- | --- | --- | --- |

## Not applicable
| Check | Why |
| --- | --- |

## Gaps in the rubric
## Could not determine
| Check or suspicion | Why | What would settle it |
| --- | --- | --- |

## Improvement plan
| Order | Change | Findings it closes | Effort | Depends on |
| --- | --- | --- | --- | --- |

## Limits of this review
```

## Self-check

Check, fix, and check again until every item passes:

1. Every finding has evidence you opened during this review.
2. Every rubric check appears exactly once (or once per part): finding, sound, could not determine, or not applicable.
3. Every hypothesis has a verdict and evidence.
4. Severity follows the table.
5. No names of people or teams; no secret values.
6. The limits say: a static review of one copy of the code; nothing was run; which areas the ledger marks unread; no second reviewer has checked it; Critical and High findings need re-checking.
