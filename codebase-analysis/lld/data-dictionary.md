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
| `_PRODUCTS` (the catalog products) | In-process Python dictionary keyed by SKU; no database or cache | `components/catalog/catalog.py` module memory | `catalog` | `_PRODUCTS` is initialized from three products and `apply_feed` mutates matching entries (`components/catalog/catalog.py:11-15`, `components/catalog/catalog.py:58-63`). |
| GitHub workflow records | GitHub issues, labels, comments, pull requests, refs, commits, and repository files via REST and GraphQL | `GITHUB_API_URL`, default `https://api.github.com`; repository from `GITHUB_REPOSITORY` | `bible-mode-b` | API request construction and issue/PR helpers (`.github/bible/bible_queue.py:92-106`, `.github/bible/bible_queue.py:112-114`, `.github/bible/bible_queue.py:128-154`, `.github/bible/bible_queue.py:176-222`, `.github/bible/bible_queue.py:253-331`, `.github/bible/bible_queue.py:340-341`, `.github/bible/bible_queue.py:355-363`, `.github/bible/bible_queue.py:1400`). |
| Temporary gate workspace | Local temporary file and directory; tarball content is extracted, checked, and deleted | `tempfile.TemporaryFile`, `tempfile.mkdtemp(prefix="bible-gate-")`; the whole analysis's fingerprint uses a `bible-whole-` directory of the same kind | `bible-mode-b` | Archive extraction and cleanup (`.github/bible/bible_queue.py:292-331`, `.github/bible/bible_queue.py:976-995`, `.github/bible/bible_queue.py:1010-1025`). |
| Tools' analysis artifacts | Local repository files; JSON and Markdown, not a database | `codebase-analysis/` | `tools` and the analysis workflow | `plan.py` writes the plan; `gate.py` reads it and component artifacts (`tools/plan.py:41-58`, `tools/gate.py:42-78`, `tools/gate.py:81-108`). |

No relational database, schema, cache, object bucket, or durable local application store is declared in the in-scope source (inferred: a search of `components/` for `sqlite`, `redis`, `shelve`, `pickle`, `write_text` and `cache` finds 0 hits, and one for `open(` finds 4 hits, all `urlopen(` calls).

## `_PRODUCTS`: the catalog products

`_PRODUCTS` is keyed by SKU. The initial values are in `components/catalog/catalog.py:11-15`; the feed can update price and stock only for SKUs already present (`components/catalog/catalog.py:58-63`).

| Field | Type | Null | Key | Default | Meaning | Set by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sku` | string | no for seeded rows; no explicit feed validation | dictionary key | `SKU-1`, `SKU-2`, `SKU-3` | Identifies a product; unknown keys have no product | Module initialization; used to match feed items | `components/catalog/catalog.py:11-15`, `components/catalog/catalog.py:27-29`, `components/catalog/catalog.py:58-61` |
| `name` | string | no for seeded rows | | Product name | Display name; not changed by the feed | Module initialization | `components/catalog/catalog.py:11-15` |
| `price` | float | no for seeded rows; no explicit feed validation | | Seeded per SKU | Unit price read by `price_of` and `line_total` | Module initialization or `apply_feed` (`float(item["price"])`) | `components/catalog/catalog.py:11-15`, `components/catalog/catalog.py:32-37`, `components/catalog/catalog.py:58-63`; `components/orders/orders.py:19-20` |
| `stock` | integer | no for seeded rows; no explicit feed validation | | Seeded per SKU | Available quantity read by `in_stock` and `validate` | Module initialization or `apply_feed` (`int(item["stock"])`) | `components/catalog/catalog.py:11-15`, `components/catalog/catalog.py:39-41`, `components/catalog/catalog.py:58-63`; `components/orders/orders.py:35-42` |

## GitHub-backed workflow records

### Tracker issue settings

The `start` command serializes these fields as JSON inside a `<!-- bible-settings ... -->` comment in the tracker issue body. `reconcile` reads that block; invalid or missing JSON is treated as unreadable, and so is a block whose `analysis` is not a safe relative path, whose `depth` is not one of `deep`, `standard` and `survey`, or whose `model` or `verify_model` does not match the model-name pattern (`.github/bible/bible_queue.py:389`, `.github/bible/bible_queue.py:395-396`, `.github/bible/bible_queue.py:418-426`, `.github/bible/bible_queue.py:86`, `.github/bible/bible_queue.py:668-671`, `.github/bible/bible_queue.py:407-427`, `.github/bible/bible_queue.py:1415-1420`).

| Field | Type | Default or constraint | Meaning | Read or set by | Evidence |
| --- | --- | --- | --- | --- | --- |
| `components` | string | CLI default `all` | `all` or comma-separated component names | `main`, `Queue.run` | `.github/bible/bible_queue.py:1388`, `.github/bible/bible_queue.py:1409-1411`, `.github/bible/bible_queue.py:728-735` |
| `model` | string | Empty means agent default; a non-empty value must match `SAFE_MODEL` | Model for plan/chunk/assembly work | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:1389`, `.github/bible/bible_queue.py:447-451`, `.github/bible/bible_queue.py:630-632` |
| `verify_model` | string | Required and must differ from `model`; a non-empty value must match `SAFE_MODEL` | Model for component and whole-analysis verification | `main`, `Queue.model_for`, assignment helpers | `.github/bible/bible_queue.py:1390`, `.github/bible/bible_queue.py:1407-1408`, `.github/bible/bible_queue.py:447-451`, `.github/bible/bible_queue.py:630-632` |
| `concurrency` | integer | `0` means no limit | Maximum number of components worked at once | `main`, `Queue.run` | `.github/bible/bible_queue.py:1391`, `.github/bible/bible_queue.py:746-748` |
| `analysis` | string | `codebase-analysis`; must match `SAFE_PATH` and hold no `..` part | Analysis output directory | `main`, `Queue.run`, `Queue.delta` | `.github/bible/bible_queue.py:1392`, `.github/bible/bible_queue.py:1428`, `.github/bible/bible_queue.py:706`, `.github/bible/bible_queue.py:1135`, `.github/bible/bible_queue.py:1141`, `.github/bible/bible_queue.py:1341`, `.github/bible/bible_queue.py:418-420` |
| `depth` | string | `deep`; one of `deep`, `standard`, `survey` | Coverage depth passed to the component gate | `main`, `Queue.check` | `.github/bible/bible_queue.py:1393`, `.github/bible/bible_queue.py:421-422`, `.github/bible/bible_queue.py:983-985` |

### Component catalog JSON

The whole-system queue reads `components.json` from the default branch and requires a non-proposed catalog with a `components` array (`.github/bible/bible_queue.py:716-718`). Of its fields the queue itself uses `proposed`, `components`, each component's `name` and `est_sessions` (`.github/bible/bible_queue.py:717`, `.github/bible/bible_queue.py:721`, `.github/bible/bible_queue.py:738`); `delta` also reads each component's `paths` through the toolkit's `components.rows_of` (inferred: the toolkit's `rows_of`, outside the inventory; the queue only calls `rows_of(catalog)`, `.github/bible/bible_queue.py:1347`) (`.github/bible/bible_queue.py:1341-1351`). The file is written by the analysis toolkit's discover step, not by `tools/plan.py` (which writes `plan.json`, below) (inferred: `tools/plan.py:55-57` writes only `plan.json`, and the file's `tool` field names `discover.py`): its `tool` field names `analyzing-a-codebase/scripts/discover.py 1.10.0` (`codebase-analysis/components.json`, field `tool`). The fields below are those the file holds.

| Field | Type | Meaning | Evidence |
| --- | --- | --- | --- |
| `schema` | integer | Catalog schema version | `codebase-analysis/components.json` |
| `tool` | string | Generator identity and version | `codebase-analysis/components.json` |
| `generated` | timestamp string | Generation time | `codebase-analysis/components.json` |
| `proposed` | boolean | Whether the catalog still needs confirmation; the queue routes proposed catalogs to planning | `codebase-analysis/components.json`; `.github/bible/bible_queue.py:717` |
| `analysis` | string | Analysis directory | `codebase-analysis/components.json` |
| `budget`, `depth` | integer, string | Discovery budget and coverage depth | `codebase-analysis/components.json` |
| `components` | array of objects | Component inventory | `codebase-analysis/components.json` |
| `components[].name`, `paths` | string, array of strings | Component key and owned source paths | `codebase-analysis/components.json` |
| `components[].files`, `lines`, `packets`, `est_sessions`, `routes` | integers | Inventory counts and work estimates; the queue reads `est_sessions` for the session cap | `codebase-analysis/components.json`; `.github/bible/bible_queue.py:738`, `.github/bible/bible_queue.py:847-848` |
| `components[].calls_into`, `calls_detail`, `called_by` | arrays/object | Component dependency names and called symbols | `codebase-analysis/components.json` |
| `cross_calls` | integer | Number of discovered cross-component calls | `codebase-analysis/components.json` |

### GitHub API entity fields used

These are the fields the queue reads or writes on GitHub-managed objects; other response fields belong to GitHub and are not persisted by this repository code (inferred: the queue's only file operations are the tarball extraction at `.github/bible/bible_queue.py:330` and the `--changed-file` read at `.github/bible/bible_queue.py:1426`).

| Resource | Fields used | Meaning | Evidence |
| --- | --- | --- | --- |
| Issue | `number`, `title`, `body`, `state`, `state_reason`, `labels[].name`, `assignees[].login`, `created_at`, `closed_at`, `pull_request` | Tracker/session identity, settings and attempt text, state/labels, assignment and timing, and issue-to-PR distinction | `.github/bible/bible_queue.py:152-154`, `.github/bible/bible_queue.py:167-174`, `.github/bible/bible_queue.py:248-251`, `.github/bible/bible_queue.py:333-353`, `.github/bible/bible_queue.py:829`, `.github/bible/bible_queue.py:863` |
| Pull request | `number`, `state`, `user.login`, `user.type`, `head.repo.full_name`, `head.sha`, `base.ref`, `base.sha`, `draft`, `requested_reviewers`, `merged_at`, `created_at`, `changed_files`, `body`, `node_id`, and per file `filename` and `previous_filename` | Identifies session PRs (a login counts only on a `Bot` account), branch/ref, verification/review status, merge state, the run a PR belongs to (`created_at` against the tracker, `body` for the tracker reference), the PR's own file count (`changed_files`, which the pull request's own file list must match when that list is used and the count is nonzero), and the allowed changed files, a renamed file under both names | `.github/bible/bible_queue.py:230-235`, `.github/bible/bible_queue.py:253-287`, `.github/bible/bible_queue.py:568-574`, `.github/bible/bible_queue.py:588`, `.github/bible/bible_queue.py:801-803` |
| Timeline event | `event`, `created_at`, `performed_via_github_app.slug`, `actor.login` or `user.login`, `actor.type` or `user.type`, `label.name`, `body`, `source.issue.repository.full_name`, `source.issue.pull_request`, `source.issue.number` | Detects agent work (`copilot_work_started`, `copilot_work_finished`, `copilot_work_finished_failure`), start failures, assignments, the queue's own continuation comments and deferred-update comments, whether a commenter is a bot, the `bible-needs-human` label events that mark a hold and its release, and same-repository cross-referenced PRs | `.github/bible/bible_queue.py:242`, `.github/bible/bible_queue.py:608-611`, `.github/bible/bible_queue.py:1153-1159`, `.github/bible/bible_queue.py:1264-1265`, `.github/bible/bible_queue.py:205-217`, `.github/bible/bible_queue.py:224-228`, `.github/bible/bible_queue.py:237-251`, `.github/bible/bible_queue.py:1263-1276` |
| Repository/ref/commit response | `default_branch`, `object.sha`, file `content`, commit `committer.date`, pull-request `node_id` | Selects branch revisions, decodes repository files, measures session activity, and identifies a PR for the GraphQL ready mutation | `.github/bible/bible_queue.py:182-187`, `.github/bible/bible_queue.py:195-199`, `.github/bible/bible_queue.py:289-290`, `.github/bible/bible_queue.py:357-360` |
| Label | `name` | Name and description define queue/run/session markers | `.github/bible/bible_queue.py:92-106`, `.github/bible/bible_queue.py:156-165`, `.github/bible/bible_queue.py:333-335` |

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
| Tracker and child issue labels | The tracker carries `bible-tracker` only; every child issue carries `bible-run-<tracker number>` | Identifies a run and scopes its child issues | `Queue.run`, `LABELS` | `.github/bible/bible_queue.py:92-106`, `.github/bible/bible_queue.py:708`, `.github/bible/bible_queue.py:768`, `.github/bible/bible_queue.py:793`, `.github/bible/bible_queue.py:1129`, `.github/bible/bible_queue.py:1420` |
| Session issue labels | `bible-plan`, `bible-chunk`, `bible-verify`, `bible-assemble`, `bible-verify-all`, `bible-revise-all`, `bible-delta`, `bible-waiting-answer`, `bible-needs-human`, `bible-hold`, and `bible/<component>` | Session kind, component, answer-wait, and human-hold markers | Queue issue creation, labeling, and follow-up | `.github/bible/bible_queue.py:92-106`, `.github/bible/bible_queue.py:167-174`, `.github/bible/bible_queue.py:333-353`, `.github/bible/bible_queue.py:642-661`, `.github/bible/bible_queue.py:767-768`, `.github/bible/bible_queue.py:793-794`, `.github/bible/bible_queue.py:900-908` |
| Whole-analysis verification labels | `bible-needs-revision` (a whole verification that asked for corrections: a revision follows), `bible-stale-verdict` (an accepted report that is not about the pages now or not by this run: verified again), `bible-whole` (with `bible-hold` and `bible-needs-human`: the whole analysis waits for a person); the first two are in `LABELS`, `bible-whole` is created when first used | Count the rounds of whole verification and mark the hold | `Queue.assemble_phase`, `Queue.revise_all_step`, `Queue.whole_hold` | `.github/bible/bible_queue.py:100-102`, `.github/bible/bible_queue.py:1057-1076`, `.github/bible/bible_queue.py:1172-1250`, `.github/bible/bible_queue.py:1164-1170` |
| Hidden `bible-state` block | `<!-- bible-state {...} -->` on the tracker: a JSON object of the queue's own counters, with keys `nocheck:<component>` and `nofp`; each counts checks in a row that could not run, and at `MAX_NOCHECK` (3) a person is asked | Lets a check that keeps timing out end in a hold instead of looping | `STATE`, `Queue.run`, `Queue.could_not_check`, `Queue.render` | `.github/bible/bible_queue.py:87`, `.github/bible/bible_queue.py:709-715`, `.github/bible/bible_queue.py:997-1008`, `.github/bible/bible_queue.py:1311` |
| Comment marker `bible-deferred-update` | `<!-- bible-deferred-update ["path", ...] -->` in a comment by the queue's own login on the tracker, with at most 200 paths | Records changed files while a run is open; turned into update issues when the run ends through its Done step, or, when a person closes the tracker or the run does not finish, by `replay_closed_runs` at a later check (inferred: `deferred_updates` is called at the Done step and by `replay_closed_runs`, and a search of the file for `deferred_updates(` finds 4 hits, the definition and three calls) | `Queue.delta` writes, `Queue.deferred_updates` reads (only the queue's own comments, only plain paths) | `.github/bible/bible_queue.py:1334-1337`, `.github/bible/bible_queue.py:1150-1162`, `.github/bible/bible_queue.py:1131-1148`, `.github/bible/bible_queue.py:681-697`, `.github/bible/bible_queue.py:667`, `.github/bible/bible_queue.py:1371-1375` |
| Comment marker `REPLAYED_MARK` and label `bible-replayed` | `<!-- bible-deferred-replayed -->` in a comment by the queue's own login on a closed tracker, and the label `bible-replayed`; the label is in `LABELS` | Marks a closed tracker whose recorded code changes are in update issues (or were recorded on the run open at that time); the mark comment says how many changes; the label makes the next checks skip the tracker | `Queue.assemble_phase` (Done step), `Queue.replay_closed_runs`, `Queue.replayed` | `.github/bible/bible_queue.py:94`, `.github/bible/bible_queue.py:391`, `.github/bible/bible_queue.py:681-703`, `.github/bible/bible_queue.py:1146-1147` |
| Comment marker `CONTINUE_MARK` | `<!-- bible-continue -->` at the end of a `@copilot continue` comment by the queue's own login on a pull request | Counts the continuations asked for one assembly, revision or whole verification (at most 3 since a person last released it) | `Queue.continue_if_unfinished` | `.github/bible/bible_queue.py:85`, `.github/bible/bible_queue.py:1270-1272`, `.github/bible/bible_queue.py:1296-1304` |
| Issue body fields | `Tracker`, `Component`, `Base branch`, `Attempt`; hidden settings JSON for tracker | Connects tasks and pull requests to a run and supports retry/model selection | `Queue.plan_phase`, `start_chunk`, `fail_or_retry`, `assemble_phase`, `main` | `.github/bible/bible_queue.py:86`, `.github/bible/bible_queue.py:90`, `.github/bible/bible_queue.py:644`, `.github/bible/bible_queue.py:656-660`, `.github/bible/bible_queue.py:767`, `.github/bible/bible_queue.py:792`, `.github/bible/bible_queue.py:1128`, `.github/bible/bible_queue.py:1415-1420` |
| `attempt` | positive integer text, initially `1`; retry changes to `2` | One retry is allowed before a human hold | `ATTEMPT`, `fail_or_retry`, `held` | `.github/bible/bible_queue.py:90`, `.github/bible/bible_queue.py:623-628`, `.github/bible/bible_queue.py:642-661` |
| Component `status.json.state` | `NEW_CHAT`, `COMPONENT_DONE`, `WAITING_ANSWER`, `STOP` | Component-session terminal/waiting states consumed by the queue | Toolkit status artifact; `Queue.session`, `Queue.component`, `Queue.follow` read it | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:552-555`, `.github/bible/bible_queue.py:591`, `.github/bible/bible_queue.py:830-832`, `.github/bible/bible_queue.py:941-951` |
| Component `status.json` counters | `component` string; `packets_done`, `packets_total` integers; `last_job_digest` string; `updated` timestamp | The component's name, progress, completion denominator, last job identity, and update time | Toolkit status artifact; queue reads `packets_done` | `.github/bible/bible_queue.py:948-950`; `codebase-analysis/ledger/components/catalog/status.json` |
| `status.json` for `tools/gate.py` | `passes_done` array of pass numbers; `open_questions` non-negative integer | Gate selection and blocked-work check; distinct from the main analysis ledger status above | `tools.gate.main` | `tools/gate.py:94-108` |
| `verification-report.md` | One `Verdict` row (`PASS`, `PASS AFTER CORRECTIONS`, or `FAIL`); `Corrections` rows may be `major`; optional 16-hex `Analysis fingerprint`; optional line `After corrections: ... X of Y confirmed`, row `Re-check of`, `Accuracy` rows in `Scores` and a `Noticed outside the re-check` section | Verdict, major corrections, re-check count, accuracy and page fingerprint decide whether a component PR is opened, revised, or verified again with a re-check ask | `report_facts`, `accepted`, `recheck_due`, `Queue.component`, `Queue.assemble_phase` | `.github/bible/bible_queue.py:471-475`, `.github/bible/bible_queue.py:478-507`, `.github/bible/bible_queue.py:510-542`, `.github/bible/bible_queue.py:865-867`, `.github/bible/bible_queue.py:1040-1041` |
| GitHub issue `state` and `state_reason` | `open` / `closed`; queue closes with `completed` or `not_planned` | External lifecycle used to select sessions and retries | `GitHub.close`, queue methods | `.github/bible/bible_queue.py:343-344`, `.github/bible/bible_queue.py:655`, `.github/bible/bible_queue.py:1098` |

## Files read and written

| File or file set | Read / written | Format and contents | Evidence |
| --- | --- | --- | --- |
| `components/*/*.py` | Read by planning/gate tools | Python source; AST function definitions and test functions; no data file is written by these scans | `tools/plan.py:21-38`; `tools/gate.py:33-39`, `tools/gate.py:66-75` |
| `codebase-analysis/plan.json` | Written by `plan.py`; read by `gate.py` and `fanout.sh` | JSON plan described above | `tools/plan.py:41-58`; `tools/gate.py:86`; `tools/fanout.sh:9` |
| `request.json` and `response.json` in the POC workflow's runner workspace | Written by the POC job; `gh api` reads `request.json` and `jq` reads `response.json` | `request.json` holds `title`, `body`, `assignees` (`copilot-swe-agent[bot]`) and `agent_assignment` (`target_repo`, `base_branch`, and `model` only when one is given); `response.json` holds GitHub's issue response, of which the job prints `number`, `html_url` and the assignee logins | `.github/workflows/poc-assign-copilot.yml:53-71` |
| `codebase-analysis/components/<name>/status.json` | Read by `gate.py` | JSON object with `passes_done` and `open_questions` used by the gate | `tools/gate.py:89-108` |
| `codebase-analysis/components/<name>/inventory.md`, `risks.md`, `tests-report.md` | Read by `gate.py` | Markdown artifacts: `inventory.md` is searched for the name of each planned function, `risks.md` for a line per HTTP site with `CHANGE` or `KEEP` and no `ASK`, and `tests-report.md` is only checked to exist; the gate writes none of them (inferred: a search of `tools/gate.py` for `write` and `open(` finds 0 hits) | `tools/gate.py:45-62`, `tools/gate.py:64-65` |
| `codebase-analysis/components.json` | Read from GitHub by queue; written by the analysis toolkit's discover step (not by `tools/plan.py`) | Generated JSON component catalog described above (inferred: `tools/plan.py:55-57` writes only `plan.json`) | `.github/bible/bible_queue.py:716-718`; `codebase-analysis/components.json` |
| `codebase-analysis/ledger/issues/*.md` | Read from GitHub by queue | `Title:` first line optionally supplies the issue title; remaining text becomes the issue body | `.github/bible/bible_queue.py:438-444`, `.github/bible/bible_queue.py:762`, `.github/bible/bible_queue.py:790`, `.github/bible/bible_queue.py:1120` |
| `codebase-analysis/ledger/components/<name>/status.json` | Read from GitHub at a branch or PR head | Main analysis status and progress fields described above | `.github/bible/bible_queue.py:552-555`, `.github/bible/bible_queue.py:830`, `.github/bible/bible_queue.py:941` |
| `codebase-analysis/ledger/components/<name>/verification-report.md` and `codebase-analysis/verification-report.md` | Read from GitHub | Component or whole-analysis verdict, corrections, re-check count, accuracy, and fingerprint; an earlier report of the same folder is read only when the report names it in a `Re-check of` row | `.github/bible/bible_queue.py:478-507`, `.github/bible/bible_queue.py:865-866`, `.github/bible/bible_queue.py:1040-1041` |
| `codebase-analysis/ledger/baseline.json` | Existence checked on default branch before delta issues are created | Baseline marker; this queue path does not parse its contents | `.github/bible/bible_queue.py:1341-1344` |
| `--changed-file` argument | Read by `main` | UTF-8 text with one changed repository path per line; blank lines are discarded before `Queue.delta` | `.github/bible/bible_queue.py:1396`, `.github/bible/bible_queue.py:1426-1428` |
| Temporary gate workspace | Written temporarily, then removed | GitHub tarball streams through a temporary file; regular files/directories are extracted under a temporary directory for coverage and fingerprint checks | `.github/bible/bible_queue.py:292-331`, `.github/bible/bible_queue.py:976-995` |

The queue writes workflow state through GitHub issue, label, comment, assignment, branch, pull-request, and repository-content APIs; it does not persist that state to a local database or application file (inferred: a search of `bible_queue.py` for `open(`, `write_text` and `.write(` finds 5 hits, `urlopen`, the tarball buffer write, `tarfile.open`, the unpacked-file write and the `--changed-file` read, and none opens a database) (`.github/bible/bible_queue.py:117-154`, `.github/bible/bible_queue.py:253-331`, `.github/bible/bible_queue.py:333-353`, `.github/bible/bible_queue.py:642-661`, `.github/bible/bible_queue.py:976-995`).

## External JSON payloads

| Payload | Fields | Meaning and handling | Evidence |
| --- | --- | --- | --- |
| Supplier feed response | Root `products` array; each item uses `sku`, `price`, and `stock` | Missing `products` defaults to an empty list; rows for unknown SKUs are ignored; price and stock are cast to `float` and `int`. No supplier response file is written. The response is read over HTTPS from `SUPPLIER_FEED_URL` | `components/catalog/catalog.py:8`, `components/catalog/catalog.py:48-63` |
| Catalog API health response | `status: "ok"` | Health endpoint response, HTTP 200 | `components/catalog/service.py:26-27` |
| Catalog API price response | `sku` string and `price` number; error response uses `error` string | Known SKU returns HTTP 200; unknown SKU and unmatched route return HTTP 404 | `components/catalog/service.py:28-34` |
| Settlement request | `order` from `order_id`, `amount` from the function argument | JSON body sent to the partner or local development endpoint with no method set (assumed: library behaviour, `urllib` then sends a POST); success is only HTTP status 200. No response body is persisted or parsed. | `components/orders/orders.py:45-51` |
| Remote catalog client response | Reads numeric `price` from JSON | `remote_price` converts the response field to `float`; transport errors are not translated here | `components/orders/catalog_client.py:19-23` |

## Status and enum values

| Field | Value | Set by | Meaning / use | Evidence |
| --- | --- | --- | --- | --- |
| Component-analysis state | `NEW_CHAT` | Analysis session status artifact | The analysis session stopped at its budget and the work continues in a new chat (the toolkit's `next.py` prints `NEW CHAT` and its `state_of` maps that to `NEW_CHAT`; the toolkit is outside the inventory, so those lines are not cited) | `.github/bible/bible_queue.py:73` |
| Component-analysis state | `COMPONENT_DONE` | Analysis session status artifact | Component work is complete; queue runs its coverage check | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:830-835` |
| Component-analysis state | `WAITING_ANSWER` | Analysis session status artifact | Queue labels the issue and PR as awaiting a human answer | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:943-947` |
| Component-analysis state | `STOP` | Analysis session status artifact | Stops progress and triggers retry/hold handling | `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:951-953` |
| Session observation | `waiting`, `running`, `finished`, `no-start`, `start-error` | `Queue.session` | Ephemeral classification returned from assignment, agent events (a newest event other than `copilot_work_started`, including `copilot_work_finished_failure`, gives `finished`), commit age, and status state | `.github/bible/bible_queue.py:577-593` |
| Tracker display state | `merged`, `not started`, `session starting`, `<kind> running`, `<kind> merged`, `waiting for answers on #<PR>`, `released: next step at the next check`, `needs a person: ...`, `review the pull request #<PR>`, `<phase> session assigned`, `<phase>: ...`, `done`, and, from other branches of the same methods, `error this run (retried next run): ...`, `waiting for the next check (not enough of this run's time left for its check)`, `check could not run this time: retried at the next check`, `verify running`, `stopped: ...` and the plan rows (`plan session assigned`, `needs a person: see #<n>`, `review and merge the plan pull request #<n>`, `plan session <state>`) | `Queue.component`, `follow`, and `assemble_phase` | Rendered in the tracker issue for a person; these are display strings, not persisted status enums | `.github/bible/bible_queue.py:804-807`, `.github/bible/bible_queue.py:812-815`, `.github/bible/bible_queue.py:820-821`, `.github/bible/bible_queue.py:826`, `.github/bible/bible_queue.py:834`, `.github/bible/bible_queue.py:839`, `.github/bible/bible_queue.py:858-861`, `.github/bible/bible_queue.py:871`, `.github/bible/bible_queue.py:894-898`, `.github/bible/bible_queue.py:909`, `.github/bible/bible_queue.py:914-924`, `.github/bible/bible_queue.py:947`, `.github/bible/bible_queue.py:968`, `.github/bible/bible_queue.py:1130`, `.github/bible/bible_queue.py:1148`, `.github/bible/bible_queue.py:725`, `.github/bible/bible_queue.py:732`, `.github/bible/bible_queue.py:744`, `.github/bible/bible_queue.py:753`, `.github/bible/bible_queue.py:769`, `.github/bible/bible_queue.py:772`, `.github/bible/bible_queue.py:779-780` |
| Verification verdict | `PASS`, `PASS AFTER CORRECTIONS`, `FAIL` | Verification report author; parsed by `report_facts` | Determines whether the verified pages need revision or can be accepted (`accepted`: `FAIL` never; `PASS AFTER CORRECTIONS` only with a confirmed re-check) | `.github/bible/bible_queue.py:478-507`, `.github/bible/bible_queue.py:523-542`, `.github/bible/bible_queue.py:867`, `.github/bible/bible_queue.py:877`, `.github/bible/bible_queue.py:1053` |
| Verification parser sentinel | `UNREADABLE` | `report_facts` | The report does not have exactly one `Verdict` row with one recognised verdict (a missing or empty report gives `None`, not `UNREADABLE`, and never counts toward a component's round hold) | `.github/bible/bible_queue.py:481-487`, `.github/bible/bible_queue.py:886` |
| GitHub issue state | `open`, `closed` | GitHub lifecycle, requested by queue | Selects active issues and completed/failed sessions | `.github/bible/bible_queue.py:152-154`, `.github/bible/bible_queue.py:343-344` |
| GitHub close reason | `completed`, `not_planned` | `GitHub.close` / retry and release paths | Normal completion or closed session not planned for completion | `.github/bible/bible_queue.py:343-344`, `.github/bible/bible_queue.py:655`, `.github/bible/bible_queue.py:1098` |
| Catalog HTTP health state | `ok` | `CatalogHandler.do_GET` | Successful health response | `components/catalog/service.py:26-27` |
| HTTP success condition for settlement | status code `200` | Payment partner response, checked by `settle` | Returns `True` only for `200`; other returned statuses are `False`, while `urlopen` HTTP errors propagate (assumed: library behaviour, `urlopen` raises `HTTPError` for an error status) | `components/orders/orders.py:50-51` |

<!-- cites .github/bible/bible_queue.py@a625b4c3353b1744b965b8bbee13e6b3ed5f72a6 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->

<!-- cites components/catalog/catalog.py@75bb1dc767dc16cad9a5ed5555a7293bc004275b -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
