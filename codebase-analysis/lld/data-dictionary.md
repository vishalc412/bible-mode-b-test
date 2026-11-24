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
summary: In-memory product data, GitHub-backed workflow records, analysis artifacts, and transient files
reads:
  - store:_PRODUCTS
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
  - store:_PRODUCTS
  - store:GitHub
  - file:codebase-analysis/plan.json
  - file:temporary-gate-worktree
calls:
  - external:Supplier One
  - external:Payment partner
  - external:GitHub
config:
  - config:CATALOG_HOST
  - config:CATALOG_PORT
  - config:CATALOG_URL
  - config:BIBLE_AGENT_LOGINS
  - config:BIBLE_AGENT_APP
  - config:BIBLE_NOW
  - config:BIBLE_SKILLS
  - config:GITHUB_API_URL
  - config:GITHUB_REPOSITORY
  - config:GH_TOKEN
  - config:ENGINE
---
# Data dictionary

## Stores

| Store | Technology | Location or connection from | Owned by | Evidence |
| --- | --- | --- | --- | --- |
| `_PRODUCTS` (the catalog products) | In-process Python dictionary keyed by SKU; no database or cache | `components/catalog/catalog.py` module memory | `catalog` | `_PRODUCTS` is initialized from three products and `apply_feed` mutates matching entries (`components/catalog/catalog.py:8-12,42-47`). |
| GitHub workflow records | GitHub issues, labels, comments, pull requests, refs, commits, and repository files via REST and GraphQL | `GITHUB_API_URL`, default `https://api.github.com`; repository from `GITHUB_REPOSITORY` | `bible-mode-b` | API request construction and issue/PR helpers (`.github/bible/bible_queue.py:92-105,116-153,175-221,252-330`). |
| Temporary gate workspace | Local temporary file and directory; tarball content is extracted, checked, and deleted | `tempfile.TemporaryFile`, `tempfile.mkdtemp(prefix="bible-gate-")` | `bible-mode-b` | Archive extraction and cleanup (`.github/bible/bible_queue.py:291-330,886-905`). |
| Tools' analysis artifacts | Local repository files; JSON and Markdown, not a database | `codebase-analysis/` | `tools` and the analysis workflow | `plan.py` writes the plan; `gate.py` reads it and component artifacts (`tools/plan.py:41-58`, `tools/gate.py:42-78,81-108`). |

No relational database, schema, cache, object bucket, or durable local application store is declared in the in-scope source.

## `_PRODUCTS`: the catalog products

`_PRODUCTS` is keyed by SKU. The initial values are in `components/catalog/catalog.py:8-12`; the feed can update price and stock only for SKUs already present (`components/catalog/catalog.py:42-47`).

| Field | Type | Null | Key | Default | Meaning | Set by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sku` | string | no for seeded rows; no explicit feed validation | dictionary key | `SKU-1`, `SKU-2`, `SKU-3` | Identifies a product; unknown keys have no product | Module initialization; used to match feed items | `components/catalog/catalog.py:8-12,15,42-45` |
| `name` | string | no for seeded rows | | Product name | Display name; not changed by the feed | Module initialization | `components/catalog/catalog.py:8-12` |
| `price` | float | no for seeded rows; no explicit feed validation | | Seeded per SKU | Unit price read by `price_of` and `line_total` | Module initialization or `apply_feed` (`float(item["price"])`) | `components/catalog/catalog.py:8-12,20-25,42-47`; `components/orders/orders.py:19-20` |
| `stock` | integer | no for seeded rows; no explicit feed validation | | Seeded per SKU | Available quantity read by `in_stock` and `validate` | Module initialization or `apply_feed` (`int(item["stock"])`) | `components/catalog/catalog.py:8-12,27-29,42-47`; `components/orders/orders.py:35-42` |

## GitHub-backed workflow records

### Tracker issue settings

The `start` command serializes these fields as JSON inside a `<!-- bible-settings ... -->` comment in the tracker issue body. `reconcile` reads that block; invalid or missing JSON is treated as unreadable (`.github/bible/bible_queue.py:86,339-346,405-425,1317-1322`).

| Field | Type | Default or constraint | Meaning | Read or set by | Evidence |
| --- | --- | --- | --- | --- | --- |
| `components` | string | CLI default `all` | `all` or comma-separated component names | `main`, `Queue.run` | `.github/bible/bible_queue.py:1290,1311-1313,640-647` |
| `model` | string | Empty means agent default | Model for plan/chunk/assembly work | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:1291,445-449,570-572` |
| `verify_model` | string | Required and must differ from `model` | Model for component and whole-analysis verification | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:1292,1309-1310,445-449,570-572` |
| `concurrency` | integer | `0` means no limit | Maximum number of components worked at once | `main`, `Queue.run` | `.github/bible/bible_queue.py:1293,658-660` |
| `analysis` | string | `codebase-analysis` | Analysis output directory | `main`, `Queue.run`, `Queue.delta` | `.github/bible/bible_queue.py:1294,1299,618,1243` |
| `depth` | string | `deep` | Coverage depth passed to the component gate | `main`, `Queue.check` | `.github/bible/bible_queue.py:1295,419-420,893-895` |

### Component catalog JSON

The whole-system queue reads `components.json` from the default branch and requires a non-proposed catalog with a `components` array (`.github/bible/bible_queue.py:628-630`). Of its fields the queue itself uses `proposed`, `components`, each component's `name` and `est_sessions` (`.github/bible/bible_queue.py:629`, `.github/bible/bible_queue.py:633`, `.github/bible/bible_queue.py:650`). The file is written by the analysis toolkit's discover step, not by `tools/plan.py` (which writes `plan.json`, below): its `tool` field names `analyzing-a-codebase/scripts/discover.py 1.10.0` (`codebase-analysis/components.json`, field `tool`). The fields below are those the file holds.

| Field | Type | Meaning | Evidence |
| --- | --- | --- | --- |
| `schema` | integer | Catalog schema version | `codebase-analysis/components.json` |
| `tool` | string | Generator identity and version | `codebase-analysis/components.json` |
| `generated` | timestamp string | Generation time | `codebase-analysis/components.json` |
| `proposed` | boolean | Whether the catalog still needs confirmation; the queue routes proposed catalogs to planning | `codebase-analysis/components.json`; `.github/bible/bible_queue.py:629` |
| `analysis` | string | Analysis directory | `codebase-analysis/components.json` |
| `budget`, `depth` | integer, string | Discovery budget and coverage depth | `codebase-analysis/components.json` |
| `components` | array of objects | Component inventory | `codebase-analysis/components.json` |
| `components[].name`, `paths` | string, array of strings | Component key and owned source paths | `codebase-analysis/components.json` |
| `components[].files`, `lines`, `packets`, `est_sessions`, `routes` | integers | Inventory counts and work estimates; the queue reads `est_sessions` for the session cap | `codebase-analysis/components.json`; `.github/bible/bible_queue.py:650`, `.github/bible/bible_queue.py:759-760` |
| `components[].calls_into`, `calls_detail`, `called_by` | arrays/object | Component dependency names and called symbols | `codebase-analysis/components.json` |
| `cross_calls` | integer | Number of discovered cross-component calls | `codebase-analysis/components.json` |

### GitHub API entity fields used

These are the fields the queue reads or writes on GitHub-managed objects; other response fields belong to GitHub and are not persisted by this repository code.

| Resource | Fields used | Meaning | Evidence |
| --- | --- | --- | --- |
| Issue | `number`, `title`, `body`, `state`, `state_reason`, `labels[].name`, `assignees[].login`, `created_at`, `closed_at`, `pull_request` | Tracker/session identity, settings and attempt text, state/labels, assignment and timing, and issue-to-PR distinction | `.github/bible/bible_queue.py:151-153,166-173,247-250,332-352,741,775` |
| Pull request | `number`, `state`, `user.login`, `user.type`, `head.repo.full_name`, `head.ref`, `head.sha`, `base.ref`, `base.sha`, `draft`, `requested_reviewers`, `merged_at`, `created_at`, `changed_files`, `body`, `node_id`, and per file `filename` and `previous_filename` | Identifies session PRs (a login counts only on a `Bot` account), branch/ref, verification/review status, merge state, the run a PR belongs to (`created_at` against the tracker, `body` for the tracker reference), the PR's own file count (`changed_files`, which a file list must match), and the allowed changed files, a renamed file under both names | `.github/bible/bible_queue.py:229-234`, `.github/bible/bible_queue.py:252-286`, `.github/bible/bible_queue.py:508-514,528`, `.github/bible/bible_queue.py:713-715` |
| Timeline event | `event`, `created_at`, `performed_via_github_app.slug`, `actor.login` or `user.login`, `body`, `source.issue.repository.full_name`, `source.issue.pull_request`, `source.issue.number` | Detects agent work (`copilot_work_started`, `copilot_work_finished`, `copilot_work_finished_failure`), start failures, assignments, the queue's own continuation comments, and same-repository cross-referenced PRs | `.github/bible/bible_queue.py:204-216`, `.github/bible/bible_queue.py:223-227`, `.github/bible/bible_queue.py:236-250`, `.github/bible/bible_queue.py:1165-1178` |
| Repository/ref/commit response | `default_branch`, `object.sha`, file `content`, commit `committer.date`, pull-request `node_id` | Selects branch revisions, decodes repository files, measures session activity, and identifies a PR for the GraphQL ready mutation | `.github/bible/bible_queue.py:181-186,194-198,288-289,356-359` |
| Label | `name` | Name and description define queue/run/session markers | `.github/bible/bible_queue.py:92-105,155-164,332-334` |

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
| Tracker issue labels | Label names, including `bible-tracker` and `bible-run-<number>` | Identifies a run and scopes its child issues | `Queue.run`, `LABELS` | `.github/bible/bible_queue.py:92-105,620` |
| Session issue labels | `bible-plan`, `bible-chunk`, `bible-verify`, `bible-assemble`, `bible-verify-all`, `bible-revise-all`, `bible-delta`, `bible-waiting-answer`, `bible-needs-human`, `bible-hold`, and `bible/<component>` | Session kind, component, answer-wait, and human-hold markers | Queue issue creation, labeling, and follow-up | `.github/bible/bible_queue.py:92-105,166-173,332-352,582-601,679-680,705-706,811-818` |
| Whole-analysis verification labels | `bible-needs-revision` (a whole verification that asked for corrections: a revision follows), `bible-stale-verdict` (a `PASS` that is not about the pages now or not by this run: verified again), `bible-whole` (with `bible-hold` and `bible-needs-human`: the whole analysis waits for a person); the first two are in `LABELS`, `bible-whole` is created when first used | Count the rounds of whole verification and mark the hold | `Queue.assemble_phase`, `Queue.revise_all_step`, `Queue.whole_hold` | `.github/bible/bible_queue.py:99-101`, `.github/bible/bible_queue.py:966-985`, `.github/bible/bible_queue.py:1074-1152`, `.github/bible/bible_queue.py:1066-1072` |
| Hidden `bible-state` block | `<!-- bible-state {...} -->` on the tracker: a JSON object of the queue's own counters, with keys `nocheck:<component>` and `nofp`; each counts checks in a row that could not run, and at `MAX_NOCHECK` (3) a person is asked | Lets a check that keeps timing out end in a hold instead of looping | `STATE`, `Queue.run`, `Queue.could_not_check`, `Queue.render` | `.github/bible/bible_queue.py:87`, `.github/bible/bible_queue.py:621-627`, `.github/bible/bible_queue.py:907-918`, `.github/bible/bible_queue.py:1213` |
| Comment marker `bible-deferred-update` | `<!-- bible-deferred-update ["path", ...] -->` in a comment by the queue's own login on the tracker, with at most 200 paths | Records changed files while a run is open; replayed into update issues when the run ends | `Queue.delta` writes, `Queue.deferred_updates` reads (only the queue's own comments, only plain paths) | `.github/bible/bible_queue.py:1236-1239`, `.github/bible/bible_queue.py:1052-1064` |
| Comment marker `CONTINUE_MARK` | `<!-- bible-continue -->` at the end of a `@copilot continue` comment by the queue's own login on a pull request | Counts the continuations asked for one assembly, revision or whole verification (at most 3 since a person last released it) | `Queue.continue_if_unfinished` | `.github/bible/bible_queue.py:85`, `.github/bible/bible_queue.py:1172-1174,1198-1206` |
| Issue body fields | `Tracker`, `Component`, `Base branch`, `Attempt`; hidden settings JSON for tracker | Connects tasks and pull requests to a run and supports retry/model selection | `Queue.plan_phase`, `start_chunk`, `fail_or_retry`, `assemble_phase`, `main` | `.github/bible/bible_queue.py:86,90,584,596-600,679,704,1033,1317-1322` |
| `attempt` | positive integer text, initially `1`; retry changes to `2` | One retry is allowed before a human hold | `ATTEMPT`, `fail_or_retry`, `held` | `.github/bible/bible_queue.py:90,563-568,582-601` |
| Component `status.json.state` | `NEW_CHAT`, `COMPONENT_DONE`, `WAITING_ANSWER`, `STOP` | Component-session terminal/waiting states consumed by the queue | Toolkit status artifact; `Queue.session`, `Queue.component`, `Queue.follow` read it | `.github/bible/bible_queue.py:73,492-495,531,742-744,851-861` |
| Component `status.json` counters | `packets_done`, `packets_total` integers; `last_job_digest` string; `updated` timestamp | Progress, completion denominator, last job identity, and update time | Toolkit status artifact; queue reads `packets_done` | `.github/bible/bible_queue.py:858-860` |
| `status.json` for `tools/gate.py` | `passes_done` array of pass numbers; `open_questions` non-negative integer | Gate selection and blocked-work check; distinct from the main analysis ledger status above | `tools.gate.main` | `tools/gate.py:94-108` |
| `verification-report.md` | One `Verdict` row (`PASS`, `PASS AFTER CORRECTIONS`, or `FAIL`); `Corrections` rows may be `major`; optional 16-hex `Analysis fingerprint` | Verdict and page fingerprint decide whether a component PR is opened or revised | `report_facts`, `Queue.component`, `Queue.assemble_phase` | `.github/bible/bible_queue.py:469-482,777-782,950` |
| GitHub issue `state` and `state_reason` | `open` / `closed`; queue closes with `completed` or `not_planned` | External lifecycle used to select sessions and retries | `GitHub.close`, queue methods | `.github/bible/bible_queue.py:342-343,595,1006` |

## Files read and written

| File or file set | Read / written | Format and contents | Evidence |
| --- | --- | --- | --- |
| `components/*/*.py` | Read by planning/gate tools | Python source; AST function definitions and test functions; no data file is written by these scans | `tools/plan.py:21-38`; `tools/gate.py:33-39,66-75` |
| `codebase-analysis/plan.json` | Written by `plan.py`; read by `gate.py` and `fanout.sh` | JSON plan described above | `tools/plan.py:41-58`; `tools/gate.py:86`; `tools/fanout.sh:9` |
| `codebase-analysis/components/<name>/status.json` | Read by `gate.py` | JSON object with `passes_done` and `open_questions` used by the gate | `tools/gate.py:89-108` |
| `codebase-analysis/components/<name>/inventory.md`, `risks.md`, `tests-report.md` | Read by `gate.py` | Markdown artifacts checked for function coverage, HTTP decisions, and test results; not written by the gate | `tools/gate.py:45-78` |
| `codebase-analysis/components.json` | Read from GitHub by queue; written by the analysis toolkit's discover step (not by `tools/plan.py`) | Generated JSON component catalog described above | `.github/bible/bible_queue.py:628-630`; `codebase-analysis/components.json` |
| `codebase-analysis/ledger/issues/*.md` | Read from GitHub by queue | `Title:` first line optionally supplies the issue title; remaining text becomes the issue body | `.github/bible/bible_queue.py:436-442,674,702,1028` |
| `codebase-analysis/ledger/components/<name>/status.json` | Read from GitHub at a branch or PR head | Main analysis status and progress fields described above | `.github/bible/bible_queue.py:492-495,742,851` |
| `codebase-analysis/ledger/components/<name>/verification-report.md` and `codebase-analysis/verification-report.md` | Read from GitHub | Component or whole-analysis verdict, corrections, and fingerprint | `.github/bible/bible_queue.py:469-482,777,950` |
| `codebase-analysis/ledger/baseline.json` | Existence checked on default branch before delta issues are created | Baseline marker; this queue path does not parse its contents | `.github/bible/bible_queue.py:1243-1246` |
| `--changed-file` argument | Read by `main` | UTF-8 text with one changed repository path per line; blank lines are discarded before `Queue.delta` | `.github/bible/bible_queue.py:1298,1328-1330` |
| Gate tarball and extracted worktree | Written temporarily, then removed | GitHub tarball streams through a temporary file; regular files/directories are extracted under a temporary directory for coverage and fingerprint checks | `.github/bible/bible_queue.py:291-330,886-905` |

The queue writes workflow state through GitHub issue, label, comment, assignment, branch, pull-request, and repository-content APIs; it does not persist that state to a local database or application file (`.github/bible/bible_queue.py:116-153,252-330,332-352,582-601,886-905`).

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
| Component-analysis state | `NEW_CHAT` | Analysis session status artifact | Start or resume a new session | `.github/bible/bible_queue.py:73` |
| Component-analysis state | `COMPONENT_DONE` | Analysis session status artifact | Component work is complete; queue runs its coverage check | `.github/bible/bible_queue.py:73,742-747` |
| Component-analysis state | `WAITING_ANSWER` | Analysis session status artifact | Queue labels the issue and PR as awaiting a human answer | `.github/bible/bible_queue.py:73,853-857` |
| Component-analysis state | `STOP` | Analysis session status artifact | Stops progress and triggers retry/hold handling | `.github/bible/bible_queue.py:73,861-863` |
| Session observation | `waiting`, `running`, `finished`, `no-start`, `start-error` | `Queue.session` | Ephemeral classification returned from assignment, agent events (a newest event other than `copilot_work_started`, including `copilot_work_finished_failure`, gives `finished`), commit age, and status state | `.github/bible/bible_queue.py:517-533` |
| Tracker display state | `merged`, `not started`, `session starting`, `<kind> running`, `<kind> merged`, `waiting for answers on #<PR>`, `released: next step at the next check`, `needs a person: ...`, `review the pull request #<PR>`, `<phase> session assigned`, `<phase>: ...`, and `done` | `Queue.component`, `follow`, and `assemble_phase` | Rendered in the tracker issue for a person; these are display strings, not persisted status enums | `.github/bible/bible_queue.py:716-738,770-782,805-819,824-834,857,878,1035,1050` |
| Verification verdict | `PASS`, `PASS AFTER CORRECTIONS`, `FAIL` | Verification report author; parsed by `report_facts` | Determines whether the verified pages need revision or can be accepted | `.github/bible/bible_queue.py:469-482,777-782,950` |
| Verification parser sentinel | `UNREADABLE` | `report_facts` | Report is missing, malformed, or has other than one recognized verdict row | `.github/bible/bible_queue.py:477-478` |
| GitHub issue state | `open`, `closed` | GitHub lifecycle, requested by queue | Selects active issues and completed/failed sessions | `.github/bible/bible_queue.py:151-153,342-343` |
| GitHub close reason | `completed`, `not_planned` | `GitHub.close` / retry and release paths | Normal completion or closed session not planned for completion | `.github/bible/bible_queue.py:342-343,595,1006` |
| Catalog HTTP health state | `ok` | `CatalogHandler.do_GET` | Successful health response | `components/catalog/service.py:26-27` |
| HTTP success condition for settlement | status code `200` | Payment partner response, checked by `settle` | Returns `True` only for `200`; other returned statuses are `False`, while `urlopen` HTTP errors propagate | `components/orders/orders.py:50-51` |

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
