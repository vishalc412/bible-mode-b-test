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
  - file:temporary-gate-workspace
writes:
  - store:_PRODUCTS
  - store:GitHub
  - file:codebase-analysis/plan.json
  - file:temporary-gate-workspace
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
| `_PRODUCTS` (the catalog products) | In-process Python dictionary keyed by SKU; no database or cache | `components/catalog/catalog.py` module memory | `catalog` | `_PRODUCTS` is initialized from three products and `apply_feed` mutates matching entries (`components/catalog/catalog.py:8-12`, `components/catalog/catalog.py:42-47`). |
| GitHub workflow records | GitHub issues, labels, comments, pull requests, refs, commits, and repository files via REST and GraphQL | `GITHUB_API_URL`, default `https://api.github.com`; repository from `GITHUB_REPOSITORY` | `bible-mode-b` | API request construction and issue/PR helpers (`.github/bible/bible_queue.py:92-105`, `.github/bible/bible_queue.py:111-113`, `.github/bible/bible_queue.py:127-153`, `.github/bible/bible_queue.py:175-221`, `.github/bible/bible_queue.py:252-330`, `.github/bible/bible_queue.py:339-340`, `.github/bible/bible_queue.py:354-362`, `.github/bible/bible_queue.py:1302`). |
| Temporary gate workspace | Local temporary file and directory; tarball content is extracted, checked, and deleted | `tempfile.TemporaryFile`, `tempfile.mkdtemp(prefix="bible-gate-")`; the whole analysis's fingerprint uses a `bible-whole-` directory of the same kind | `bible-mode-b` | Archive extraction and cleanup (`.github/bible/bible_queue.py:291-330`, `.github/bible/bible_queue.py:886-905`, `.github/bible/bible_queue.py:920-935`). |
| Tools' analysis artifacts | Local repository files; JSON and Markdown, not a database | `codebase-analysis/` | `tools` and the analysis workflow | `plan.py` writes the plan; `gate.py` reads it and component artifacts (`tools/plan.py:41-58`, `tools/gate.py:42-78`, `tools/gate.py:81-108`). |

No relational database, schema, cache, object bucket, or durable local application store is declared in the in-scope source (inferred: a search of `components/` for `sqlite`, `redis`, `shelve`, `pickle`, `write_text` and `cache` finds 0 hits, and one for `open(` finds 4 hits, all `urlopen(` calls).

## `_PRODUCTS`: the catalog products

`_PRODUCTS` is keyed by SKU. The initial values are in `components/catalog/catalog.py:8-12`; the feed can update price and stock only for SKUs already present (`components/catalog/catalog.py:42-47`).

| Field | Type | Null | Key | Default | Meaning | Set by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sku` | string | no for seeded rows; no explicit feed validation | dictionary key | `SKU-1`, `SKU-2`, `SKU-3` | Identifies a product; unknown keys have no product | Module initialization; used to match feed items | `components/catalog/catalog.py:8-12`, `components/catalog/catalog.py:15-17`, `components/catalog/catalog.py:42-45` |
| `name` | string | no for seeded rows | | Product name | Display name; not changed by the feed | Module initialization | `components/catalog/catalog.py:8-12` |
| `price` | float | no for seeded rows; no explicit feed validation | | Seeded per SKU | Unit price read by `price_of` and `line_total` | Module initialization or `apply_feed` (`float(item["price"])`) | `components/catalog/catalog.py:8-12`, `components/catalog/catalog.py:20-25`, `components/catalog/catalog.py:42-47`; `components/orders/orders.py:19-20` |
| `stock` | integer | no for seeded rows; no explicit feed validation | | Seeded per SKU | Available quantity read by `in_stock` and `validate` | Module initialization or `apply_feed` (`int(item["stock"])`) | `components/catalog/catalog.py:8-12`, `components/catalog/catalog.py:27-29`, `components/catalog/catalog.py:42-47`; `components/orders/orders.py:35-42` |

## GitHub-backed workflow records

### Tracker issue settings

The `start` command serializes these fields as JSON inside a `<!-- bible-settings ... -->` comment in the tracker issue body. `reconcile` reads that block; invalid or missing JSON is treated as unreadable, and so is a block whose `analysis` is not a safe relative path, whose `depth` is not one of `deep`, `standard` and `survey`, or whose `model` or `verify_model` does not match the model-name pattern (`.github/bible/bible_queue.py:388`, `.github/bible/bible_queue.py:393-394`, `.github/bible/bible_queue.py:416-424`, `.github/bible/bible_queue.py:86`, `.github/bible/bible_queue.py:608-611`, `.github/bible/bible_queue.py:405-425`, `.github/bible/bible_queue.py:1317-1322`).

| Field | Type | Default or constraint | Meaning | Read or set by | Evidence |
| --- | --- | --- | --- | --- | --- |
| `components` | string | CLI default `all` | `all` or comma-separated component names | `main`, `Queue.run` | `.github/bible/bible_queue.py:1290`, `.github/bible/bible_queue.py:1311-1313`, `.github/bible/bible_queue.py:640-647` |
| `model` | string | Empty means agent default; a non-empty value must match `SAFE_MODEL` | Model for plan/chunk/assembly work | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:1291`, `.github/bible/bible_queue.py:445-449`, `.github/bible/bible_queue.py:570-572` |
| `verify_model` | string | Required and must differ from `model`; a non-empty value must match `SAFE_MODEL` | Model for component and whole-analysis verification | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:1292`, `.github/bible/bible_queue.py:1309-1310`, `.github/bible/bible_queue.py:445-449`, `.github/bible/bible_queue.py:570-572` |
| `concurrency` | integer | `0` means no limit | Maximum number of components worked at once | `main`, `Queue.run` | `.github/bible/bible_queue.py:1293`, `.github/bible/bible_queue.py:658-660` |
| `analysis` | string | `codebase-analysis`; must match `SAFE_PATH` and hold no `..` part | Analysis output directory | `main`, `Queue.run`, `Queue.delta` | `.github/bible/bible_queue.py:1294`, `.github/bible/bible_queue.py:1330`, `.github/bible/bible_queue.py:618`, `.github/bible/bible_queue.py:1040`, `.github/bible/bible_queue.py:1046`, `.github/bible/bible_queue.py:1243`, `.github/bible/bible_queue.py:416-418` |
| `depth` | string | `deep`; one of `deep`, `standard`, `survey` | Coverage depth passed to the component gate | `main`, `Queue.check` | `.github/bible/bible_queue.py:1295`, `.github/bible/bible_queue.py:419-420`, `.github/bible/bible_queue.py:893-895` |

### Component catalog JSON

The whole-system queue reads `components.json` from the default branch and requires a non-proposed catalog with a `components` array (`.github/bible/bible_queue.py:628-630`). Of its fields the queue itself uses `proposed`, `components`, each component's `name` and `est_sessions` (`.github/bible/bible_queue.py:629`, `.github/bible/bible_queue.py:633`, `.github/bible/bible_queue.py:650`); `delta` also reads each component's `paths` through the toolkit's `components.rows_of` (inferred: the toolkit's `rows_of`, outside the inventory; the queue only calls `rows_of(catalog)`, `.github/bible/bible_queue.py:1249`) (`.github/bible/bible_queue.py:1243-1253`). The file is written by the analysis toolkit's discover step, not by `tools/plan.py` (which writes `plan.json`, below) (inferred: `tools/plan.py:55-57` writes only `plan.json`, and the file's `tool` field names `discover.py`): its `tool` field names `analyzing-a-codebase/scripts/discover.py 1.10.0` (`codebase-analysis/components.json`, field `tool`). The fields below are those the file holds.

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

These are the fields the queue reads or writes on GitHub-managed objects; other response fields belong to GitHub and are not persisted by this repository code (inferred: the queue's only file operations are the tarball extraction at `.github/bible/bible_queue.py:329` and the `--changed-file` read at `.github/bible/bible_queue.py:1328`).

| Resource | Fields used | Meaning | Evidence |
| --- | --- | --- | --- |
| Issue | `number`, `title`, `body`, `state`, `state_reason`, `labels[].name`, `assignees[].login`, `created_at`, `closed_at`, `pull_request` | Tracker/session identity, settings and attempt text, state/labels, assignment and timing, and issue-to-PR distinction | `.github/bible/bible_queue.py:151-153`, `.github/bible/bible_queue.py:166-173`, `.github/bible/bible_queue.py:247-250`, `.github/bible/bible_queue.py:332-352`, `.github/bible/bible_queue.py:741`, `.github/bible/bible_queue.py:775` |
| Pull request | `number`, `state`, `user.login`, `user.type`, `head.repo.full_name`, `head.sha`, `base.ref`, `base.sha`, `draft`, `requested_reviewers`, `merged_at`, `created_at`, `changed_files`, `body`, `node_id`, and per file `filename` and `previous_filename` | Identifies session PRs (a login counts only on a `Bot` account), branch/ref, verification/review status, merge state, the run a PR belongs to (`created_at` against the tracker, `body` for the tracker reference), the PR's own file count (`changed_files`, which the pull request's own file list must match when that list is used and the count is nonzero), and the allowed changed files, a renamed file under both names | `.github/bible/bible_queue.py:229-234`, `.github/bible/bible_queue.py:252-286`, `.github/bible/bible_queue.py:508-514`, `.github/bible/bible_queue.py:528`, `.github/bible/bible_queue.py:713-715` |
| Timeline event | `event`, `created_at`, `performed_via_github_app.slug`, `actor.login` or `user.login`, `actor.type` or `user.type`, `label.name`, `body`, `source.issue.repository.full_name`, `source.issue.pull_request`, `source.issue.number` | Detects agent work (`copilot_work_started`, `copilot_work_finished`, `copilot_work_finished_failure`), start failures, assignments, the queue's own continuation comments and deferred-update comments, whether a commenter is a bot, the `bible-needs-human` label events that mark a hold and its release, and same-repository cross-referenced PRs | `.github/bible/bible_queue.py:241`, `.github/bible/bible_queue.py:548-551`, `.github/bible/bible_queue.py:1055-1061`, `.github/bible/bible_queue.py:1166-1167`, `.github/bible/bible_queue.py:204-216`, `.github/bible/bible_queue.py:223-227`, `.github/bible/bible_queue.py:236-250`, `.github/bible/bible_queue.py:1165-1178` |
| Repository/ref/commit response | `default_branch`, `object.sha`, file `content`, commit `committer.date`, pull-request `node_id` | Selects branch revisions, decodes repository files, measures session activity, and identifies a PR for the GraphQL ready mutation | `.github/bible/bible_queue.py:181-186`, `.github/bible/bible_queue.py:194-198`, `.github/bible/bible_queue.py:288-289`, `.github/bible/bible_queue.py:356-359` |
| Label | `name` | Name and description define queue/run/session markers | `.github/bible/bible_queue.py:92-105`, `.github/bible/bible_queue.py:155-164`, `.github/bible/bible_queue.py:332-334` |

### Component-analysis plan JSON

`tools/plan.py` creates `codebase-analysis/plan.json`; `tools/gate.py` and `tools/fanout.sh` read it (`tools/plan.py:41-58`, `tools/gate.py:86`, `tools/fanout.sh:9`).

| Field | Type | Meaning | Set by | Evidence |
| --- | --- | --- | --- | --- |
| `version` | integer | Plan format version, currently `1` | `plan.main` | `tools/plan.py:46-47` |
| `passes` | object of string values | Descriptions for inventory, risk, and test passes | `plan.main` | `tools/plan.py:47-51` |
| `components` | object keyed by component name | Per-component inventory | `plan.main` | `tools/plan.py:42-44`, `tools/plan.py:52-54` |
| `components[name].sources`, `tests` | arrays of paths | Python implementation and test files | `scan` | `tools/plan.py:21-27`, `tools/plan.py:37-38` |
| `components[name].test_count` | integer | Baseline number of test functions | `scan` | `tools/plan.py:36-38` |
| `components[name].functions` | array of `{name, at}` objects | Function names and source locations | `scan` | `tools/plan.py:29-32`, `tools/plan.py:37-38` |
| `components[name].http_sites` | array of `{url, at}` objects | Literal HTTP URLs and source locations | `scan` | `tools/plan.py:33-35`, `tools/plan.py:37-38` |

### Queue issues and component status

| Record or field | Type / values | Meaning | Set or read by | Evidence |
| --- | --- | --- | --- | --- |
| Tracker and child issue labels | The tracker carries `bible-tracker` only; every child issue carries `bible-run-<tracker number>` | Identifies a run and scopes its child issues | `Queue.run`, `LABELS` | `.github/bible/bible_queue.py:92-105`, `.github/bible/bible_queue.py:620`, `.github/bible/bible_queue.py:680`, `.github/bible/bible_queue.py:705`, `.github/bible/bible_queue.py:1034`, `.github/bible/bible_queue.py:1322` |
| Session issue labels | `bible-plan`, `bible-chunk`, `bible-verify`, `bible-assemble`, `bible-verify-all`, `bible-revise-all`, `bible-delta`, `bible-waiting-answer`, `bible-needs-human`, `bible-hold`, and `bible/<component>` | Session kind, component, answer-wait, and human-hold markers | Queue issue creation, labeling, and follow-up | `.github/bible/bible_queue.py:92-105`, `.github/bible/bible_queue.py:166-173`, `.github/bible/bible_queue.py:332-352`, `.github/bible/bible_queue.py:582-601`, `.github/bible/bible_queue.py:679-680`, `.github/bible/bible_queue.py:705-706`, `.github/bible/bible_queue.py:811-818` |
| Whole-analysis verification labels | `bible-needs-revision` (a whole verification that asked for corrections: a revision follows), `bible-stale-verdict` (a `PASS` that is not about the pages now or not by this run: verified again), `bible-whole` (with `bible-hold` and `bible-needs-human`: the whole analysis waits for a person); the first two are in `LABELS`, `bible-whole` is created when first used | Count the rounds of whole verification and mark the hold | `Queue.assemble_phase`, `Queue.revise_all_step`, `Queue.whole_hold` | `.github/bible/bible_queue.py:99-101`, `.github/bible/bible_queue.py:966-985`, `.github/bible/bible_queue.py:1074-1152`, `.github/bible/bible_queue.py:1066-1072` |
| Hidden `bible-state` block | `<!-- bible-state {...} -->` on the tracker: a JSON object of the queue's own counters, with keys `nocheck:<component>` and `nofp`; each counts checks in a row that could not run, and at `MAX_NOCHECK` (3) a person is asked | Lets a check that keeps timing out end in a hold instead of looping | `STATE`, `Queue.run`, `Queue.could_not_check`, `Queue.render` | `.github/bible/bible_queue.py:87`, `.github/bible/bible_queue.py:621-627`, `.github/bible/bible_queue.py:907-918`, `.github/bible/bible_queue.py:1213` |
| Comment marker `bible-deferred-update` | `<!-- bible-deferred-update ["path", ...] -->` in a comment by the queue's own login on the tracker, with at most 200 paths | Records changed files while a run is open; turned into update issues only when the run ends through its Done step (never if a person closes the tracker or the run does not finish (inferred: `deferred_updates` is called only at lines 1038 and 1043, and `reconcile` lists open trackers only); those paths get no update issue of their own, and the next update issue for the same component asks for every change since the baseline) | `Queue.delta` writes, `Queue.deferred_updates` reads (only the queue's own comments, only plain paths) | `.github/bible/bible_queue.py:1236-1239`, `.github/bible/bible_queue.py:1052-1064`, `.github/bible/bible_queue.py:1038-1050`, `.github/bible/bible_queue.py:607`, `.github/bible/bible_queue.py:1273-1277` |
| Comment marker `CONTINUE_MARK` | `<!-- bible-continue -->` at the end of a `@copilot continue` comment by the queue's own login on a pull request | Counts the continuations asked for one assembly, revision or whole verification (at most 3 since a person last released it) | `Queue.continue_if_unfinished` | `.github/bible/bible_queue.py:85`, `.github/bible/bible_queue.py:1172-1174`, `.github/bible/bible_queue.py:1198-1206` |
| Issue body fields | `Tracker`, `Component`, `Base branch`, `Attempt`; hidden settings JSON for tracker | Connects tasks and pull requests to a run and supports retry/model selection | `Queue.plan_phase`, `start_chunk`, `fail_or_retry`, `assemble_phase`, `main` | `.github/bible/bible_queue.py:86`, `.github/bible/bible_queue.py:90`, `.github/bible/bible_queue.py:584`, `.github/bible/bible_queue.py:596-600`, `.github/bible/bible_queue.py:679`, `.github/bible/bible_queue.py:704`, `.github/bible/bible_queue.py:1033`, `.github/bible/bible_queue.py:1317-1322` |
| `attempt` | positive integer text, initially `1`; retry changes to `2` | One retry is allowed before a human hold | `ATTEMPT`, `fail_or_retry`, `held` | `.github/bible/bible_queue.py:90`, `.github/bible/bible_queue.py:563-568`, `.github/bible/bible_queue.py:582-601` |
| Component `status.json.state` | `NEW_CHAT`, `COMPONENT_DONE`, `WAITING_ANSWER`, `STOP` | Component-session terminal/waiting states consumed by the queue | Toolkit status artifact; `Queue.session`, `Queue.component`, `Queue.follow` read it | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:492-495`, `.github/bible/bible_queue.py:531`, `.github/bible/bible_queue.py:742-744`, `.github/bible/bible_queue.py:851-861` |
| Component `status.json` counters | `component` string; `packets_done`, `packets_total` integers; `last_job_digest` string; `updated` timestamp | The component's name, progress, completion denominator, last job identity, and update time | Toolkit status artifact; queue reads `packets_done` | `.github/bible/bible_queue.py:858-860`; `codebase-analysis/ledger/components/catalog/status.json` |
| `status.json` for `tools/gate.py` | `passes_done` array of pass numbers; `open_questions` non-negative integer | Gate selection and blocked-work check; distinct from the main analysis ledger status above | `tools.gate.main` | `tools/gate.py:94-108` |
| `verification-report.md` | One `Verdict` row (`PASS`, `PASS AFTER CORRECTIONS`, or `FAIL`); `Corrections` rows may be `major`; optional 16-hex `Analysis fingerprint` | Verdict and page fingerprint decide whether a component PR is opened or revised | `report_facts`, `Queue.component`, `Queue.assemble_phase` | `.github/bible/bible_queue.py:469-482`, `.github/bible/bible_queue.py:777-782`, `.github/bible/bible_queue.py:950` |
| GitHub issue `state` and `state_reason` | `open` / `closed`; queue closes with `completed` or `not_planned` | External lifecycle used to select sessions and retries | `GitHub.close`, queue methods | `.github/bible/bible_queue.py:342-343`, `.github/bible/bible_queue.py:595`, `.github/bible/bible_queue.py:1006` |

## Files read and written

| File or file set | Read / written | Format and contents | Evidence |
| --- | --- | --- | --- |
| `components/*/*.py` | Read by planning/gate tools | Python source; AST function definitions and test functions; no data file is written by these scans | `tools/plan.py:21-38`; `tools/gate.py:33-39`, `tools/gate.py:66-75` |
| `codebase-analysis/plan.json` | Written by `plan.py`; read by `gate.py` and `fanout.sh` | JSON plan described above | `tools/plan.py:41-58`; `tools/gate.py:86`; `tools/fanout.sh:9` |
| `request.json` and `response.json` in the POC workflow's runner workspace | Written by the POC job; `gh api` reads `request.json` and `jq` reads `response.json` | `request.json` holds `title`, `body`, `assignees` (`copilot-swe-agent[bot]`) and `agent_assignment` (`target_repo`, `base_branch`, and `model` only when one is given); `response.json` holds GitHub's issue response, of which the job prints `number`, `html_url` and the assignee logins | `.github/workflows/poc-assign-copilot.yml:53-71` |
| `codebase-analysis/components/<name>/status.json` | Read by `gate.py` | JSON object with `passes_done` and `open_questions` used by the gate | `tools/gate.py:89-108` |
| `codebase-analysis/components/<name>/inventory.md`, `risks.md`, `tests-report.md` | Read by `gate.py` | Markdown artifacts: `inventory.md` is searched for the name of each planned function, `risks.md` for a line per HTTP site with `CHANGE` or `KEEP` and no `ASK`, and `tests-report.md` is only checked to exist; the gate writes none of them (inferred: a search of `tools/gate.py` for `write` and `open(` finds 0 hits) | `tools/gate.py:45-62`, `tools/gate.py:64-65` |
| `codebase-analysis/components.json` | Read from GitHub by queue; written by the analysis toolkit's discover step (not by `tools/plan.py`) | Generated JSON component catalog described above (inferred: `tools/plan.py:55-57` writes only `plan.json`) | `.github/bible/bible_queue.py:628-630`; `codebase-analysis/components.json` |
| `codebase-analysis/ledger/issues/*.md` | Read from GitHub by queue | `Title:` first line optionally supplies the issue title; remaining text becomes the issue body | `.github/bible/bible_queue.py:436-442`, `.github/bible/bible_queue.py:674`, `.github/bible/bible_queue.py:702`, `.github/bible/bible_queue.py:1028` |
| `codebase-analysis/ledger/components/<name>/status.json` | Read from GitHub at a branch or PR head | Main analysis status and progress fields described above | `.github/bible/bible_queue.py:492-495`, `.github/bible/bible_queue.py:742`, `.github/bible/bible_queue.py:851` |
| `codebase-analysis/ledger/components/<name>/verification-report.md` and `codebase-analysis/verification-report.md` | Read from GitHub | Component or whole-analysis verdict, corrections, and fingerprint | `.github/bible/bible_queue.py:469-482`, `.github/bible/bible_queue.py:777`, `.github/bible/bible_queue.py:950` |
| `codebase-analysis/ledger/baseline.json` | Existence checked on default branch before delta issues are created | Baseline marker; this queue path does not parse its contents | `.github/bible/bible_queue.py:1243-1246` |
| `--changed-file` argument | Read by `main` | UTF-8 text with one changed repository path per line; blank lines are discarded before `Queue.delta` | `.github/bible/bible_queue.py:1298`, `.github/bible/bible_queue.py:1328-1330` |
| Temporary gate workspace | Written temporarily, then removed | GitHub tarball streams through a temporary file; regular files/directories are extracted under a temporary directory for coverage and fingerprint checks | `.github/bible/bible_queue.py:291-330`, `.github/bible/bible_queue.py:886-905` |

The queue writes workflow state through GitHub issue, label, comment, assignment, branch, pull-request, and repository-content APIs; it does not persist that state to a local database or application file (inferred: a search of `bible_queue.py` for `open(`, `write_text` and `.write(` finds 5 hits, `urlopen`, the tarball buffer write, `tarfile.open`, the unpacked-file write and the `--changed-file` read, and none opens a database) (`.github/bible/bible_queue.py:116-153`, `.github/bible/bible_queue.py:252-330`, `.github/bible/bible_queue.py:332-352`, `.github/bible/bible_queue.py:582-601`, `.github/bible/bible_queue.py:886-905`).

## External JSON payloads

| Payload | Fields | Meaning and handling | Evidence |
| --- | --- | --- | --- |
| Supplier feed response | Root `products` array; each item uses `sku`, `price`, and `stock` | Missing `products` defaults to an empty list; rows for unknown SKUs are ignored; price and stock are cast to `float` and `int`. No supplier response file is written. | `components/catalog/catalog.py:36-47` |
| Catalog API health response | `status: "ok"` | Health endpoint response, HTTP 200 | `components/catalog/service.py:26-27` |
| Catalog API price response | `sku` string and `price` number; error response uses `error` string | Known SKU returns HTTP 200; unknown SKU and unmatched route return HTTP 404 | `components/catalog/service.py:28-34` |
| Settlement request | `order` from `order_id`, `amount` from the function argument | JSON body sent to the partner or local development endpoint with no method set (assumed: library behaviour, `urllib` then sends a POST); success is only HTTP status 200. No response body is persisted or parsed. | `components/orders/orders.py:45-51` |
| Remote catalog client response | Reads numeric `price` from JSON | `remote_price` converts the response field to `float`; transport errors are not translated here | `components/orders/catalog_client.py:19-23` |

## Status and enum values

| Field | Value | Set by | Meaning / use | Evidence |
| --- | --- | --- | --- | --- |
| Component-analysis state | `NEW_CHAT` | Analysis session status artifact | The analysis session stopped at its budget and the work continues in a new chat (the toolkit's `next.py` prints `NEW CHAT` and its `state_of` maps that to `NEW_CHAT`; the toolkit is outside the inventory, so those lines are not cited) | `.github/bible/bible_queue.py:73` |
| Component-analysis state | `COMPONENT_DONE` | Analysis session status artifact | Component work is complete; queue runs its coverage check | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:742-747` |
| Component-analysis state | `WAITING_ANSWER` | Analysis session status artifact | Queue labels the issue and PR as awaiting a human answer | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:853-857` |
| Component-analysis state | `STOP` | Analysis session status artifact | Stops progress and triggers retry/hold handling | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:861-863` |
| Session observation | `waiting`, `running`, `finished`, `no-start`, `start-error` | `Queue.session` | Ephemeral classification returned from assignment, agent events (a newest event other than `copilot_work_started`, including `copilot_work_finished_failure`, gives `finished`), commit age, and status state | `.github/bible/bible_queue.py:517-533` |
| Tracker display state | `merged`, `not started`, `session starting`, `<kind> running`, `<kind> merged`, `waiting for answers on #<PR>`, `released: next step at the next check`, `needs a person: ...`, `review the pull request #<PR>`, `<phase> session assigned`, `<phase>: ...`, `done`, and, from other branches of the same methods, `error this run (retried next run): ...`, `waiting for the next check (not enough of this run's time left for its check)`, `check could not run this time: retried at the next check`, `stopped: ...` and the plan rows (`plan session assigned`, `needs a person: see #<n>`, `review and merge the plan pull request #<n>`, `plan session <state>`) | `Queue.component`, `follow`, and `assemble_phase` | Rendered in the tracker issue for a person; these are display strings, not persisted status enums | `.github/bible/bible_queue.py:716-738`, `.github/bible/bible_queue.py:770-782`, `.github/bible/bible_queue.py:805-819`, `.github/bible/bible_queue.py:824-834`, `.github/bible/bible_queue.py:857`, `.github/bible/bible_queue.py:878`, `.github/bible/bible_queue.py:1035`, `.github/bible/bible_queue.py:1050`, `.github/bible/bible_queue.py:637`, `.github/bible/bible_queue.py:644`, `.github/bible/bible_queue.py:656`, `.github/bible/bible_queue.py:665`, `.github/bible/bible_queue.py:681`, `.github/bible/bible_queue.py:684`, `.github/bible/bible_queue.py:691-692`, `.github/bible/bible_queue.py:746`, `.github/bible/bible_queue.py:751` |
| Verification verdict | `PASS`, `PASS AFTER CORRECTIONS`, `FAIL` | Verification report author; parsed by `report_facts` | Determines whether the verified pages need revision or can be accepted | `.github/bible/bible_queue.py:469-482`, `.github/bible/bible_queue.py:777-782`, `.github/bible/bible_queue.py:950` |
| Verification parser sentinel | `UNREADABLE` | `report_facts` | The report does not have exactly one `Verdict` row with one recognised verdict (a missing or empty report gives `None`, not `UNREADABLE`, and never counts toward a component's round hold) | `.github/bible/bible_queue.py:470-478`, `.github/bible/bible_queue.py:797` |
| GitHub issue state | `open`, `closed` | GitHub lifecycle, requested by queue | Selects active issues and completed/failed sessions | `.github/bible/bible_queue.py:151-153`, `.github/bible/bible_queue.py:342-343` |
| GitHub close reason | `completed`, `not_planned` | `GitHub.close` / retry and release paths | Normal completion or closed session not planned for completion | `.github/bible/bible_queue.py:342-343`, `.github/bible/bible_queue.py:595`, `.github/bible/bible_queue.py:1006` |
| Catalog HTTP health state | `ok` | `CatalogHandler.do_GET` | Successful health response | `components/catalog/service.py:26-27` |
| HTTP success condition for settlement | status code `200` | Payment partner response, checked by `settle` | Returns `True` only for `200`; other returned statuses are `False`, while `urlopen` HTTP errors propagate (assumed: library behaviour, `urlopen` raises `HTTPError` for an error status) | `components/orders/orders.py:50-51` |

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
