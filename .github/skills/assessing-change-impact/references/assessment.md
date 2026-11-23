# Assessment

## Contents

- Kinds of change
- How sure each link is
- Risk
- A graph without an analysis
- Assessment template
- After the change

## Kinds of change

Name the kind first: it decides which dependents break.

| Kind | Example | Who breaks | Who usually does not |
| --- | --- | --- | --- |
| Signature | parameter added, removed, renamed or retyped; return type changed | every caller (`CALLS`), every route handler wrapper, every test calling it | code that only reads the same table |
| Behaviour | same signature, different result, side effect or error | callers that use the result or catch the error; routes it handles (their responses); tests asserting the old result | callers that ignore the result |
| Removal or rename | function, class, file or module deleted or moved | every caller and importer (`CALLS`, `IMPORTS`), string references found by search, documentation | nothing; this is the widest |
| Data | column added, removed, renamed, retyped; meaning or allowed values changed | every reader and writer of the table or file (data coupling), reports and exports, migrations | code touching other tables |
| Route contract | path, method, request field, response field, status code or auth changed | every client of the route (UI screens, other services, scripts) and its tests | internal callers of the handler |
| Configuration | key renamed, default changed, new required key | every reader of the key (`CONFIG`), deployment files and charts that set it, every environment | code that does not read it |
| Outside system | endpoint, version, credential or protocol of a dependency changed | every caller of that system, its timeout and retry handling, its tests and mocks | everything else |
| Internal refactor | structure changed, behaviour and signatures kept | the target's own tests; nothing else should change | all dependents (confirm with the tests) |

## How sure each link is

| Resolution in the report | Meaning | What to do |
| --- | --- | --- |
| `exact` | Parsed from the code: definitions, routes, handlers, imports | Trust, after opening level-1 links |
| `same-file`, `self`, `import` | A call resolved through the same file, the class or an import | Trust, after opening level-1 links |
| `name-unique` | Matched only because one method has that name | Always open; reject when the receiver is a different type |
| `analysis` | Written in an analysis page's front matter | Always open the code the page cites |
| found by search | Not in the graph | Open, and add to the assessment |

## Risk

The script's risk is distance only: level 1 high, level 2 medium, level 3 and beyond low. Raise it for a dependent that is an entry point (route, job, listener), touches money, security or personal data, writes a shared table, or has no test reaching it. Lower it for a dependent the change kind leaves unaffected. Say why in each changed row.

## A graph without an analysis

When the user needs a quick answer and agrees, run `analyzing-a-codebase`'s `scripts/inventory.py`, then its `scripts/knowledge.py`, on an empty `codebase-analysis/` folder. The graph then holds code edges only (definitions, routes, handlers, imports, calls): no components, tables, stores or outside systems. Say so at the top of the assessment, and lean on the step 5 searches for data and integration dependents.

## Assessment template

Write `impact/<name>-assessment.md`.

```markdown
# Change assessment: <name>

| | |
| --- | --- |
| Change | what will change, in one sentence |
| Kind | signature / behaviour / removal / data / route contract / configuration / outside system / refactor |
| Why | |
| Targets | |
| Graph | knowledge/graph.json of <date>; stale files: none / list |
| Radius report | impact/<name>.md |

## Summary
Five lines for the person approving the change: how wide it is, which components and entry
points it reaches, what breaks, what is untested, and the recommended order.

## Dependents
| Level | Dependent | Link | Resolution | Confirmed? | Effect of this change | Risk | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `search` (`app/api.py:12-25`) | calls target | name-unique | confirmed | breaks: passes 2 arguments | high | `app/api.py:21` |

## Found by search, not in the graph
| Where | What | Effect | Evidence |

## Data and contracts
Tables, files, routes and configuration keys whose shape or meaning changes, and every reader
and writer of each.

## Change order
Numbered steps, smallest safe order: leaves before callers for a removal; expand, migrate,
contract for data and route changes (add the new form, move every dependent, then remove the
old); configuration defaults before code that needs them.

## Tests
| Test | Reaches | Run because |
Tests to add, for every dependent the graph says no test reaches.

## Documentation to update
The analysis pages and cards from the radius report, plus the HLD pages whose diagrams or
tables name the changed thing.

## Rollback
How to undo each step, and which steps cannot be undone (data changes, published contracts).

## Questions
Owners to ask, dependents marked unclear.

## After the change
Filled in afterwards: what was done, what differed from the plan, the re-run radius.
```

## After the change

Whoever made the change (this skill itself only does step 1 and fills in step 3, both inside `impact/`):

1. Run `analyzing-a-codebase`'s `scripts/inventory.py`, then `impact.py` again with the same targets. A dependent that appeared or disappeared is a finding: record it.
2. Update every page the assessment lists, then run that skill's `scripts/coverage.py` and `scripts/knowledge.py`, so the analysis and the graph match the code again.
3. Fill in the assessment's "After the change" section: what was done, what differed from the plan, and the re-run radius.

