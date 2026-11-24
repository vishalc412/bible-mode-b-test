---
id: lld/data-dictionary
kind: data-dictionary
source:
  - components/catalog/catalog.py
  - components/catalog/service.py
  - components/orders/orders.py
  - components/orders/catalog_client.py
  - .github/bible/bible_queue.py
  - tools/plan.py
  - tools/gate.py
  - tools/fanout.sh
  - tls-migration/tls-services.yaml
  - tls-migration/evidence/inventory.json
summary: In-memory product data, GitHub-backed workflow records, analysis artifacts, and transient files
reads:
  - store:catalog-products
  - store:GitHub
  - file:codebase-analysis/plan.json
  - file:codebase-analysis/components.json
  - file:codebase-analysis/components/*/status.json
  - file:codebase-analysis/ledger/components/*/status.json
  - file:codebase-analysis/ledger/issues/*.md
  - file:codebase-analysis/ledger/components/*/verification-report.md
  - file:codebase-analysis/ledger/baseline.json
  - file:changed-path-list
  - file:temporary-gate-worktree
writes:
  - store:catalog-products
  - store:GitHub
  - file:codebase-analysis/plan.json
  - file:temporary-gate-worktree
calls:
  - external:Supplier One
  - external:Payment partner
  - external:GitHub
config:
  - CATALOG_HOST
  - CATALOG_PORT
  - CATALOG_URL
  - BIBLE_AGENT_LOGINS
  - BIBLE_AGENT_APP
  - BIBLE_NOW
  - BIBLE_SKILLS
  - GITHUB_API_URL
  - GITHUB_REPOSITORY
  - GH_TOKEN
  - ENGINE
  - BIBLE_SKILLS
---
# Data dictionary

## Stores

| Store | Technology | Location or connection from | Owned by | Evidence |
| --- | --- | --- | --- | --- |
| Catalog products | In-process Python dictionary keyed by SKU; no database or cache | `components/catalog/catalog.py` module memory | `catalog` | `_PRODUCTS` is initialized from three products and `apply_feed` mutates matching entries (`components/catalog/catalog.py:8-12,42-47`). |
| GitHub workflow records | GitHub issues, labels, comments, pull requests, refs, commits, and repository files via REST and GraphQL | `GITHUB_API_URL`, default `https://api.github.com`; repository from `GITHUB_REPOSITORY` | `bible-mode-b` | API request construction and issue/PR helpers (`.github/bible/bible_queue.py:91-117,129-151,172-220,261-302`). |
| Temporary gate workspace | Local temporary file and directory; tarball content is extracted, checked, and deleted | `tempfile.TemporaryFile`, `tempfile.mkdtemp(prefix="bible-gate-")` | `bible-mode-b` | Archive extraction and cleanup (`.github/bible/bible_queue.py:237-260,723-735`). |
| Tools' analysis artifacts | Local repository files; JSON and Markdown, not a database | `codebase-analysis/` | `tools` and the analysis workflow | `plan.py` writes the plan; `gate.py` reads it and component artifacts (`tools/plan.py:41-58`, `tools/gate.py:42-78,81-108`). |

No relational database, schema, cache, object bucket, or durable local application store is declared in the in-scope source.

## Catalog products

`_PRODUCTS` is keyed by SKU. The initial values are in `components/catalog/catalog.py:8-12`; the feed can update price and stock only for SKUs already present (`components/catalog/catalog.py:42-47`).

| Field | Type | Null | Key | Default | Meaning | Set by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sku` | string | no for seeded rows; no explicit feed validation | dictionary key | `SKU-1`, `SKU-2`, `SKU-3` | Identifies a product; unknown keys have no product | Module initialization; used to match feed items | `components/catalog/catalog.py:8-12,15,42-45` |
| `name` | string | no for seeded rows | | Product name | Display name; not changed by the feed | Module initialization | `components/catalog/catalog.py:8-12` |
| `price` | float | no for seeded rows; no explicit feed validation | | Seeded per SKU | Unit price read by `price_of` and `line_total` | Module initialization or `apply_feed` (`float(item["price"])`) | `components/catalog/catalog.py:8-12,20-25,42-47`; `components/orders/orders.py:19-20` |
| `stock` | integer | no for seeded rows; no explicit feed validation | | Seeded per SKU | Available quantity read by `in_stock` and `validate` | Module initialization or `apply_feed` (`int(item["stock"])`) | `components/catalog/catalog.py:8-12,27-29,42-47`; `components/orders/orders.py:35-42` |

## GitHub-backed workflow records

### Tracker issue settings

The `start` command serializes these fields as JSON inside a `<!-- bible-settings ... -->` comment in the tracker issue body. `reconcile` reads that block; invalid or missing JSON is treated as unreadable (`.github/bible/bible_queue.py:70,316-323,828-854`).

| Field | Type | Default or constraint | Meaning | Read or set by | Evidence |
| --- | --- | --- | --- | --- | --- |
| `components` | string | CLI default `all` | `all` or comma-separated component names | `main`, `Queue.run` | `.github/bible/bible_queue.py:823,829,835,502-510` |
| `model` | string | Empty means agent default | Model for plan/chunk/assembly work | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:824-825,341-345,451-454` |
| `verify_model` | string | Required and must differ from `model` | Model for component and whole-analysis verification | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:824-825,341-345,451-454` |
| `concurrency` | integer | `0` means no limit | Maximum number of components worked at once | `main`, `Queue.run` | `.github/bible/bible_queue.py:826,524-526` |
| `analysis` | string | `codebase-analysis` | Analysis output directory | `main`, `Queue.run`, `Queue.delta` | `.github/bible/bible_queue.py:827,501-502,794-799` |
| `depth` | string | `deep` | Coverage depth passed to the component gate | `main`, `Queue.check` | `.github/bible/bible_queue.py:828,726-728` |

### Component catalog JSON consumed by the queue

The whole-system queue reads `components.json` from the default branch. It enters planning if the value is not an object, is marked proposed, or lacks a `components` array; it then reads component names and session estimates (`.github/bible/bible_queue.py:601-623`).

| Field | Type | Meaning | Evidence |
| --- | --- | --- | --- |
| `proposed` | boolean | Whether the catalog still needs confirmation; a truthy value routes the queue to planning | `.github/bible/bible_queue.py:601-603` |
| `components` | array of objects | Selected component inventory; queue requires a list | `.github/bible/bible_queue.py:601-603` |
| `components[].name` | string | Component name used for selection and queue operations | `.github/bible/bible_queue.py:606-620` |
| `components[].est_sessions` | integer-like estimate | Clamped by the queue and used to set a bounded work-session cap | `.github/bible/bible_queue.py:723-726` |

### GitHub API entity fields used

These are the fields the queue reads or writes on GitHub-managed objects; other response fields belong to GitHub and are not persisted by this repository code.

| Resource | Fields used | Meaning | Evidence |
| --- | --- | --- | --- |
| Issue | `number`, `title`, `body`, `state`, `state_reason`, `labels[].name`, `assignees[].login`, `created_at`, `closed_at`, `pull_request` | Tracker/session identity, settings and attempt text, state/labels, assignment and timing, and issue-to-PR distinction | `.github/bible/bible_queue.py:129-151,272-281,316-329,435-449,488-514` |
| Pull request | `number`, `state`, `user.login`, `head.repo.full_name`, `head.ref`, `head.sha`, `base.ref`, `draft`, `requested_reviewers`, `merged_at`, `body`, file `filename` | Identifies session PRs, branch/ref, verification/review status, merge state, tracker relation, and allowed changed files | `.github/bible/bible_queue.py:172-220,404-429,578-585,659-687` |
| Timeline event | `event`, `created_at`, `performed_via_github_app.slug`, `actor.login` or `user.login`, `body`, `source.issue.repository.full_name`, `source.issue.pull_request`, `source.issue.number` | Detects agent work, start failures, assignments, and same-repository cross-referenced PRs | `.github/bible/bible_queue.py:185-229` |
| Repository/ref/commit response | `default_branch`, `object.sha`, file `content`, commit `committer.date`, pull-request `node_id` | Selects branch revisions, decodes repository files, measures session activity, and identifies a PR for the GraphQL ready mutation | `.github/bible/bible_queue.py:153-170,186-194,196-220,276-291` |
| Label | `name` | Name and description define queue/run/session markers | `.github/bible/bible_queue.py:73-83,133-151,261-266` |

### Component-analysis plan JSON

`tools/plan.py` creates `codebase-analysis/plan.json`; `tools/gate.py` and `tools/fanout.sh` read it (`tools/plan.py:41-58`, `tools/gate.py:86`, `tools/fanout.sh:9`).

| Field | Type | Meaning | Set by | Evidence |
| --- | --- | --- | --- | --- |
| `version` | integer | Plan format version, currently `1` | `plan.main` | `tools/plan.py:43-46` |
| `passes` | object of string values | Descriptions for inventory, risk, and test passes | `plan.main` | `tools/plan.py:47-51` |
| `components` | object keyed by component name | Per-component inventory | `plan.main` | `tools/plan.py:42-44,52-54` |
| `components[name].sources`, `tests` | arrays of paths | Python implementation and test files | `scan` | `tools/plan.py:21-27,35` |
| `components[name].test_count` | integer | Baseline number of test functions | `scan` | `tools/plan.py:36-38` |
| `components[name].functions` | array of `{name, at}` objects | Function names and source locations | `scan` | `tools/plan.py:29-31,37-38` |
| `components[name].http_sites` | array of `{url, at}` objects | Literal HTTP URLs and source locations | `scan` | `tools/plan.py:32-34,37-38` |

### Queue issues and component status

| Record or field | Type / values | Meaning | Set or read by | Evidence |
| --- | --- | --- | --- | --- |
| Tracker issue labels | Label names, including `bible-tracker` and `bible-run-<number>` | Identifies a run and scopes its child issues | `Queue.run`, `LABELS` | `.github/bible/bible_queue.py:73-83,488-502` |
| Session issue labels | `bible-plan`, `bible-chunk`, `bible-verify`, `bible-assemble`, `bible-verify-all`, `bible-delta`, `bible-waiting-answer`, `bible-needs-human`, `bible-hold`, and `bible/<component>` | Session kind, component, answer-wait, and human-hold markers | Queue issue creation, labeling, and follow-up | `.github/bible/bible_queue.py:73-83,449-474,538-571,640-660,688-713,739-774` |
| Issue body fields | `Tracker`, `Component`, `Base branch`, `Attempt`; hidden settings JSON for tracker | Connects tasks and pull requests to a run and supports retry/model selection | `Queue.plan_phase`, `start_chunk`, `fail_or_retry`, `assemble_phase`, `main` | `.github/bible/bible_queue.py:70-72,481-487,538-571,473-485,739-774,828-854` |
| `attempt` | positive integer text, initially `1`; retry changes to `2` | One retry is allowed before a human hold | `ATTEMPT`, `fail_or_retry`, `held` | `.github/bible/bible_queue.py:71,438-449,455-483` |
| Component `status.json.state` | `NEW_CHAT`, `COMPONENT_DONE`, `WAITING_ANSWER`, `STOP` | Component-session terminal/waiting states consumed by the queue | Queue reads the status artifact and branches on these values | `.github/bible/bible_queue.py:490-506,681-793` |
| Component `status.json` counters | `packets_done` integer and other progress fields | Queue compares `packets_done` to detect progress | Queue reads progress counters | `.github/bible/bible_queue.py:831-844` |
| `status.json` for `tools/gate.py` | `passes_done` array of pass numbers; `open_questions` non-negative integer | Gate selection and blocked-work check; distinct from the main analysis ledger status above | `tools.gate.main` | `tools/gate.py:94-108` |
| `verification-report.md` | One `Verdict` row (`PASS`, `PASS AFTER CORRECTIONS`, or `FAIL`); `Corrections` rows may be `major`; optional 16-hex `Analysis fingerprint` | Verdict and page fingerprint decide whether a component PR is opened or revised | `report_facts`, `Queue.component`, `Queue.assemble_phase` | `.github/bible/bible_queue.py:365-379,619-627,749-753` |
| GitHub issue `state` and `state_reason` | `open` / `closed`; queue closes with `completed` or `not_planned` | External lifecycle used to select sessions and retries | `GitHub.close`, queue methods | `.github/bible/bible_queue.py:272-273,441-448,472-483` |

## Files read and written

| File or file set | Read / written | Format and contents | Evidence |
| --- | --- | --- | --- |
| `components/*/*.py` | Read by planning/gate tools | Python source; AST function definitions and test functions; no data file is written by these scans | `tools/plan.py:21-38`; `tools/gate.py:33-39,66-75` |
| `codebase-analysis/plan.json` | Written by `tools/plan.py`; read by `gate.py` and `fanout.sh` | JSON plan described above | `tools/plan.py:41-58`; `tools/gate.py:86`; `tools/fanout.sh:9` |
| `codebase-analysis/components/<name>/status.json` | Read by `gate.py` | JSON object with `passes_done` and `open_questions` used by the gate | `tools/gate.py:89-108` |
| `codebase-analysis/components/<name>/inventory.md`, `risks.md`, `tests-report.md` | Read by `gate.py` | Markdown artifacts checked for function coverage, HTTP decisions, and test results; not written by the gate | `tools/gate.py:45-78` |
| `codebase-analysis/components.json` | Read from GitHub by queue | JSON component catalog; only the fields listed above are part of the queue's documented contract | `.github/bible/bible_queue.py:601-623` |
| `codebase-analysis/ledger/issues/*.md` | Read from GitHub by queue | `Title:` first line optionally supplies the issue title; remaining text becomes the issue body | `.github/bible/bible_queue.py:332-339,538-545,568-571,739-774` |
| `codebase-analysis/ledger/components/<name>/status.json` | Read from GitHub at a branch or PR head | Main analysis status and progress fields described above | `.github/bible/bible_queue.py:490-506,681-793` |
| `codebase-analysis/ledger/components/<name>/verification-report.md` and `codebase-analysis/verification-report.md` | Read from GitHub | Component or whole-analysis verdict, corrections, and fingerprint | `.github/bible/bible_queue.py:619-627,749-753` |
| `codebase-analysis/ledger/baseline.json` | Existence checked on default branch before delta issues are created | Baseline marker; this queue path does not parse its contents | `.github/bible/bible_queue.py:1201-1205` |
| `tls-migration/tls-services.yaml` | Read as repository planning data | YAML manifest for the local catalog–orders TLS migration; `migrator_model: null` and producer stage `0` mean no implementation stage is recorded | `tls-migration/tls-services.yaml:1-4,18-26,30-49` |
| `tls-migration/evidence/inventory.json` | Read as repository planning data | Scanner output recording HTTP URL locations and host/port details; it is not live probe evidence | `tls-migration/evidence/inventory.json:1-16` |
| `--changed-file` argument | Read by `main` | UTF-8 text with one changed repository path per line; blank lines are discarded before `Queue.delta` | `.github/bible/bible_queue.py:812-814,858-861` |
| Gate tarball and extracted worktree | Written temporarily, then removed | GitHub tarball streams through a temporary file; regular files/directories are extracted under a temporary directory for coverage and fingerprint checks | `.github/bible/bible_queue.py:237-260,723-735` |

The queue writes workflow state through GitHub issue, label, comment, assignment, branch, pull-request, and repository-content APIs; it does not persist that state to a local database or application file (`.github/bible/bible_queue.py:91-117,129-151,261-302,538-571,723-817`).

## External JSON payloads

| Payload | Fields | Meaning and handling | Evidence |
| --- | --- | --- | --- |
| Supplier feed response | Root `products` array; each item uses `sku`, `price`, and `stock` | Missing `products` defaults to an empty list; rows for unknown SKUs are ignored; price and stock are cast to `float` and `int`. No supplier response file is written. | `components/catalog/catalog.py:36-47` |
| Catalog API health response | `status: "ok"` | Health endpoint response, HTTP 200 | `components/catalog/service.py:26-27` |
| Catalog API price response | `sku` string and `price` number; error response uses `error` string | Known SKU returns HTTP 200; unknown SKU and unmatched route return HTTP 404 | `components/catalog/service.py:28-34` |
| Settlement request | `order` from `order_id`, `amount` from the function argument | JSON POST to the partner or local development endpoint; success is only HTTP status 200. No response body is persisted or parsed. | `components/orders/orders.py:45-51` |
| Remote catalog client response | Reads numeric `price` from JSON | `remote_price` converts the response field to `float`; transport errors are not translated here | `components/orders/catalog_client.py:19-23` |

## Status and enum values

| Field | Value | Set by | Meaning / use | Evidence |
| --- | --- | --- | --- | --- |
| Component-analysis state | `NEW_CHAT` | Analysis session status artifact | Start or resume a new session | `.github/bible/bible_queue.py:65-66,425-428` |
| Component-analysis state | `COMPONENT_DONE` | Analysis session status artifact | Component work is complete; queue runs its coverage check | `.github/bible/bible_queue.py:65-66,600-603,695-697` |
| Component-analysis state | `WAITING_ANSWER` | Analysis session status artifact | Queue labels the issue and PR as awaiting a human answer | `.github/bible/bible_queue.py:65-66,688-693` |
| Component-analysis state | `STOP` | Analysis session status artifact | Stops progress and triggers retry/hold handling | `.github/bible/bible_queue.py:65-66,697-700` |
| Session observation | `waiting`, `running`, `finished`, `no-start`, `start-error` | `Queue.session` | Ephemeral classification returned from assignment, agent events, commit age, and report state | `.github/bible/bible_queue.py:490-506` |
| Tracker display state | `merged`, `not started`, `session starting`, `<kind> running`, `<kind> merged`, `waiting for answers on #<PR>`, `released: next step at the next check`, `needs a person: ...`, `review the pull request #<PR>`, `<phase> session assigned`, `<phase>: ...`, and `done` | `Queue.component`, `follow`, and `assemble_phase` | Rendered in the tracker issue for a person; these are display strings, not persisted status enums | `.github/bible/bible_queue.py:577-660,663-718,738-775` |
| Verification verdict | `PASS`, `PASS AFTER CORRECTIONS`, `FAIL` | Verification report author; parsed by `report_facts` | Determines whether the verified pages need revision or can be accepted | `.github/bible/bible_queue.py:365-379,619-627,749-753` |
| Verification parser sentinel | `UNREADABLE` | `report_facts` | Report is missing, malformed, or has other than one recognized verdict row | `.github/bible/bible_queue.py:442-452` |
| GitHub issue state | `open`, `closed` | GitHub lifecycle, requested by queue | Selects active issues and completed/failed sessions | `.github/bible/bible_queue.py:129-131,272-273` |
| GitHub close reason | `completed`, `not_planned` | `GitHub.close` / retry and release paths | Normal completion or closed session not planned for completion | `.github/bible/bible_queue.py:272-273,441-448,472-483` |
| Catalog HTTP health state | `ok` | `CatalogHandler.do_GET` | Successful health response | `components/catalog/service.py:26-27` |
| HTTP success condition for settlement | status code `200` | Payment partner response, checked by `settle` | Returns `True` only for `200`; other returned statuses are `False`, while `urlopen` HTTP errors propagate | `components/orders/orders.py:50-51` |

<!-- cites .github/bible/bible_queue.py@9084f4915d286441c5b3a9a29a8df059bf76dacc -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tls-migration/evidence/inventory.json@2d46a3e849f9c1688bd72d8e4add3feeb368314e -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
