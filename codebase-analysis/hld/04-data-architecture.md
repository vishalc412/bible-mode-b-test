---
id: hld/04-data-architecture
kind: hld
source:
  - components/catalog/catalog.py
  - components/orders/orders.py
  - .github/bible/bible_queue.py
  - tools/plan.py
  - tools/gate.py
depends_on:
  - lld/data-dictionary
summary: Product data is process memory; workflow state is kept in GitHub; planning and gate artifacts are files
---
# Data architecture

## Stores and ownership

| Store | Technology | Owned by | Read by | Schema in | Evidence |
| --- | --- | --- | --- | --- | --- |
| `_PRODUCTS` | Python dictionary in process memory, keyed by SKU | `catalog` | Catalog lookups and `orders` direct imports | `components/catalog/catalog.py` | `components/catalog/catalog.py:8-12,15-29,42-47`; `components/orders/orders.py:5,19-20,35-42` |
| GitHub issues, labels, branches, PRs and repository files | GitHub-managed records and content | `bible-mode-b` | Queue and agent sessions | Only selected fields and workflow conventions are defined by repository code; GitHub owns the complete schema | `.github/bible/bible_queue.py:91-117,129-151,153-220,261-302` |
| `codebase-analysis/plan.json` | Local JSON file | `tools` | `tools/gate.py`, `tools/fanout.sh` | `tools/plan.py` constructs its schema | `tools/plan.py:41-58`; `tools/gate.py:86`; `tools/fanout.sh:9` |
| Component analysis artifacts | JSON and Markdown files stored on GitHub branches | Analysis workflow | `tools/gate.py` or `bible-mode-b` | Field formats used by each reader are described in [the data dictionary](../lld/data-dictionary.md) | `tools/gate.py:42-78,81-108`; `.github/bible/bible_queue.py:388-389,425-429,600-603,688-697` |
| Gate workspace and tarball buffer | Temporary local file/directory | `bible-mode-b` | `coverage.py` and `status.py` subprocesses | No durable schema | `.github/bible/bible_queue.py:237-260,723-735` |

No relational database, cache, object store, or durable application-side order record is declared. Catalog contents disappear when the process exits; the queue's durable run state lives in GitHub issues, labels, branches and PRs (`components/catalog/catalog.py:8-12`; `.github/bible/bible_queue.py:129-151,261-302`).

## Data models

### Catalog products

`_PRODUCTS` is a map whose key is the SKU. The diagram shows the record fields seeded by the module and updated from a supplier feed; there are no other product relationships.

```mermaid
erDiagram
  PRODUCT {
    string sku PK
    string name
    float price
    int stock
  }
```

| Element | Evidence |
| --- | --- |
| `PRODUCT.sku` is the dictionary key | `components/catalog/catalog.py:8-12,15` |
| `name`, `price`, and `stock` are the product values | `components/catalog/catalog.py:8-12` |
| Feed updates `price` and `stock` for known SKUs only | `components/catalog/catalog.py:42-47` |

### Component plan file

The JSON arrays are shown as child records to make the plan's shape readable; this is a file schema, not a relational database.

```mermaid
erDiagram
  ANALYSIS_PLAN ||--|{ COMPONENT : catalogs
  COMPONENT ||--o{ SOURCE_FILE : scans
  COMPONENT ||--o{ TEST_FILE : counts
  COMPONENT ||--o{ FUNCTION : inventories
  COMPONENT ||--o{ HTTP_SITE : records
  ANALYSIS_PLAN {
    int version
    object passes
  }
  COMPONENT {
    string name PK
    int test_count
  }
  SOURCE_FILE {
    string path
  }
  TEST_FILE {
    string path
  }
  FUNCTION {
    string name
    string at
  }
  HTTP_SITE {
    string url
    string at
  }
```

| Element | Evidence |
| --- | --- |
| Plan contains version, pass descriptions and component inventory | `tools/plan.py:42-54` |
| Component source and test paths plus test-count baseline | `tools/plan.py:21-27,35-38` |
| Function and HTTP-site records | `tools/plan.py:29-38` |

## Record lifecycles

### GitHub issue

The queue creates an open issue, updates its body/labels/assignment while it is active, and closes it either as completed or not planned. A retry is a new issue with an incremented attempt, not a reopening of the failed issue.

```mermaid
stateDiagram-v2
  [*] --> Open : create_issue
  Open --> Open : assign, comment, label, update body
  Open --> ClosedCompleted : close(reason=completed)
  Open --> ClosedNotPlanned : fail or release
  ClosedCompleted --> [*]
  ClosedNotPlanned --> [*] : retry creates a new issue
```

| Element | Evidence |
| --- | --- |
| `create_issue` starts tracker and session records | `.github/bible/bible_queue.py:144-151,538-571,640-660` |
| Issue body, assignment and label updates | `.github/bible/bible_queue.py:261-281,431-450` |
| Normal close reason defaults to `completed` | `.github/bible/bible_queue.py:272-273` |
| Failed attempts close as `not_planned`; a later attempt is newly created | `.github/bible/bible_queue.py:455-483` |

### Agent session pull request

Agent PRs are merged into a component branch after path and status checks; failed PRs are closed. The separate component review PR targets the default branch and is merged by a person, not by this queue.

```mermaid
stateDiagram-v2
  [*] --> Draft : Copilot opens session PR
  Draft --> Ready : ready(pr)
  Ready --> MergedToComponentBranch : merge(pr)
  Draft --> Closed : failure closes PR
  Ready --> Closed : failure closes PR
```

| Element | Evidence |
| --- | --- |
| Agent may open draft; queue marks it ready before merge | `.github/bible/bible_queue.py:284-291` |
| Queue validates changed files and status before merging session PR | `.github/bible/bible_queue.py:659-713` |
| Failed session closes its PR | `.github/bible/bible_queue.py:455-474` |

### Component review pull request

The separate component review PR targets the default branch and is merged by a person, not by this queue.

```mermaid
stateDiagram-v2
  [*] --> ReviewOpen : create component PR
  ReviewOpen --> MergedByPerson : human merges to default branch
```

| Element | Evidence |
| --- | --- |
| Component review PR is opened for a person to review | `.github/bible/bible_queue.py:608-612`; module docstring `.github/bible/bible_queue.py:28` |

The component status artifact also carries `NEW_CHAT`, `COMPONENT_DONE`, `WAITING_ANSWER`, and `STOP`; this repository code reads these values to decide queue behavior but does not write their transitions (`.github/bible/bible_queue.py:65-66,425-429,688-708`). The transitions belong to the analysis toolkit and are not inferred here.

## Files, caches and other state

| State | Reads | Writes | Lifecycle | Evidence |
| --- | --- | --- | --- | --- |
| `plan.json` | Gate and fanout tools | Planning tool | Regenerated from component Python files | `tools/plan.py:21-58`; `tools/gate.py:86`; `tools/fanout.sh:9` |
| Component `status.json`, `inventory.md`, `risks.md`, `tests-report.md` | Gate tool | Not written by `tools/gate.py` | Read for validation; absent files fail the relevant pass | `tools/gate.py:42-78,89-108` |
| `components.json`, issue templates, status and verification reports | Queue reads from GitHub default or component branch | Queue changes GitHub issue/PR state, not these local files | Component artifacts move with their branches; whole-system files are read from the default branch | `.github/bible/bible_queue.py:332-389,502-510,538-571,619-627,739-774` |
| `baseline.json` | Queue checks its presence before delta work | Not written by the queue | Missing baseline prevents delta issue creation | `.github/bible/bible_queue.py:794-798` |
| Changed-path list | `delta` reads one UTF-8 path per line | Workflow writes it to `$RUNNER_TEMP/changed.txt` | Removed with the runner workspace | `.github/workflows/bible-delta.yml:29-36`; `.github/bible/bible_queue.py:858-861` |
| Gate tarball and extracted worktree | Coverage and status subprocesses | Queue streams and extracts under a temporary location | Temporary buffer closes; worktree is removed in `finally` | `.github/bible/bible_queue.py:237-260,723-735` |
| POC `request.json`, `response.json` | `gh api` receives request file; `jq` reads response fields | POC job writes both in runner workspace | No checkout or repository commit; runner workspace is ephemeral | `.github/workflows/poc-assign-copilot.yml:55-69` |

See [the data dictionary](../lld/data-dictionary.md) for field meanings and status values.
