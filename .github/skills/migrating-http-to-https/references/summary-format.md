# The summary

Write `https-migration/https-migration-summary.md` after the final scan. Its core headings match the summary of `migrating-service-calls-to-tls`, so one reader can compare both; that summary adds Timing and Consumers, and its results come from `check.sh`. No script checks this file: every line must still rest on the verification output.

```markdown
# HTTPS Migration Summary Report: <application>, <environment>, <date>

Overall result: <pass | pass, pending sign-off | not proven | fail>

## Successfully Migrated Endpoints
| Endpoint | Role | Certificate (issuer, expires) | Renewal | Evidence |
| --- | --- | --- | --- | --- |
| https://<host>/<path> | we serve / we call | <issuer>, <date> | <who renews it> | <check in verification.md, with its output> |

## Endpoints Remaining on HTTP
| Endpoint URL | Reason | Priority | Action Required | Owner | Review date |
| --- | --- | --- | --- | --- | --- |

## Endpoints with Warnings
| Endpoint URL | Warning | Recommended Action |
| --- | --- | --- |

## Not proven
| Endpoint | Check | Reason not run | Who can run it |
| --- | --- | --- | --- |

## Rollback
How to undo each change: the termination point, the redirect, HSTS, the application change.

## Statistics
- Total endpoints identified: X
- Successfully migrated: Y (Z%)
- Remaining on HTTP: A (B%)
- Blocked by infrastructure: C
- Not proven: D
```

Rules:

- **"Migrated" needs evidence.** A row counts only when its Evidence cell names a check from [verification.md](verification.md) that passed for that endpoint. A URL that was merely edited is not migrated.
- **Remaining on HTTP** lists every endpoint that stays on plain HTTP, each with an owner and a review date. Keep the section even when it is empty.
- **Endpoints with Warnings:** an endpoint that answers on HTTPS with a problem a person must look at: a self-signed or expired certificate, a certificate that expires within 30 days, a name mismatch.
- **Blocked by infrastructure:** the rows of "Remaining on HTTP" whose reason is that the other side, or the infrastructure in between, has no HTTPS.
- **Statistics are counted from the tables,** not estimated. Percentages are of the total.
- **The overall result never claims more than the checks.** A check that was not run makes it "not proven".
