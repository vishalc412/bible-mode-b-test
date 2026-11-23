---
id: lld/bible-mode-b/bible_queue
kind: module
component: bible-mode-b
source: .github/bible/bible_queue.py
summary: Coordinates Mode B issue workflows through GitHub REST and GraphQL
reads: [file:--changed-file list, config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
writes: [file:destination tree passed to GitHub.tarball]
calls: [external:GitHub API, symbol:components.rows_of, symbol:components.component_map, symbol:components.assign]
uses: [symbol:GitHub, symbol:Queue]
config: [config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
exposes: []
---

# bible_queue

Source file: `.github/bible/bible_queue.py`

| | |
| --- | --- |
| Component | `bible-mode-b` (its design page is `README.md` in this folder) |
| Lines | 844 |
| Role | Runs the Mode B analysis queue and its GitHub API client. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, subprocess, and filesystem modules used by the API client, queue, and CLI. (`.github/bible/bible_queue.py:42-55`) |
| Module-level state | `COPILOT`, `AGENT_LOGINS`, `AGENT_APP`, `START_ERROR`, `FINAL_STATES`, `NO_PR_AFTER`, `IDLE_AFTER`, `MAX_VERIFY_ROUNDS`, `SETTINGS`, `ATTEMPT`, `NAME`, and `LABELS` are initialized at import; environment-backed values include `BIBLE_AGENT_LOGINS` and `BIBLE_AGENT_APP`. (`.github/bible/bible_queue.py:59-83`) |

## Summary

`main` exposes the `start`, `reconcile`, and `delta` CLI commands. It constructs `Queue` and `GitHub`; `Queue` coordinates tracker/session state and delegates repository operations to `GitHub`, whose methods build REST requests and a GraphQL ready-for-review mutation. `Queue.delta` also imports component-membership helpers from the analysis toolkit. (`.github/bible/bible_queue.py:797-840`, `.github/bible/bible_queue.py:396-794`, `.github/bible/bible_queue.py:88-302`, `.github/bible/bible_queue.py:775-781`)

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| `GitHub` | class | 88-302 | [class](#github) |
| `GitHub.__init__` | method | 89-92 | [card](#github__init__repo-token-api-none) |
| `GitHub.request` | method | 94-103 | [card](#githubrequestmethod-url-body-none-timeout-60) |
| `GitHub.call` | method | 105-117 | [card](#githubcallmethod-path-body-none-ok404-false) |
| `GitHub.paged` | method | 119-127 | [card](#githubpagedpath) |
| `GitHub.issues` | method | 129-131 | [card](#githubissueslabels-state-open) |
| `GitHub.ensure_label` | method | 133-138 | [card](#githubensure_labelname-whycodebase-analysis) |
| `GitHub.ensure_labels` | method | 140-142 | [card](#githubensure_labels) |
| `GitHub.create_issue` | method | 144-151 | [card](#githubcreate_issuetitle-body-labels-assign-none) |
| `GitHub.default_branch` | method | 153-154 | [card](#githubdefault_branch) |
| `GitHub.branch_sha` | method | 156-158 | [card](#githubbranch_shabranch) |
| `GitHub.create_branch` | method | 160-161 | [card](#githubcreate_branchbranch-sha) |
| `GitHub.reset_branch` | method | 163-164 | [card](#githubreset_branchbranch-sha) |
| `GitHub.file` | method | 166-170 | [card](#githubfilepath-ref) |
| `GitHub.prs` | method | 172-174 | [card](#githubprsbase-none-state-open) |
| `GitHub.timeline` | method | 176-177 | [card](#githubtimelinenumber) |
| `GitHub.linked_prs` | method | 179-188 | [card](#githublinked_prsnumber) |
| `GitHub.branch_prs` | method | 190-193 | [card](#githubbranch_prsbranch-base) |
| `GitHub.agent_events` | method | 195-199 | [card](#githubagent_eventsnumber) |
| `GitHub.is_agent_pr` | method | 201-205 | [card](#githubis_agent_prpr) |
| `GitHub.start_error` | method | 207-215 | [card](#githubstart_errorissue) |
| `GitHub.assigned_at` | method | 217-220 | [card](#githubassigned_atissue) |
| `GitHub.pr_files` | method | 222-229 | [card](#githubpr_filesnumber) |
| `GitHub.commit_time` | method | 231-232 | [card](#githubcommit_timesha) |
| `GitHub.tarball` | method | 234-259 | [card](#githubtarballref-dest) |
| `GitHub.label` | method | 261-263 | [card](#githublabelnumber-name) |
| `GitHub.unlabel` | method | 265-266 | [card](#githubunlabelnumber-name) |
| `GitHub.comment` | method | 268-269 | [card](#githubcommentnumber-text) |
| `GitHub.close` | method | 271-272 | [card](#githubclosenumber-reason-completed) |
| `GitHub.set_body` | method | 274-275 | [card](#githubset_bodynumber-body) |
| `GitHub.unassign` | method | 277-278 | [card](#githubunassignnumber) |
| `GitHub.assign` | method | 280-281 | [card](#githubassignnumber-assign) |
| `GitHub.ready` | method | 283-291 | [card](#githubreadypr) |
| `GitHub.merge` | method | 293-296 | [card](#githubmergepr-title) |
| `GitHub.close_pr` | method | 298-299 | [card](#githubclose_prnumber) |
| `GitHub.create_pr` | method | 301-302 | [card](#githubcreate_prhead-base-title-body) |
| `now` | function | 307-309 | [card](#now) |
| `age` | function | 312-313 | [card](#age) |
| `settings_of` | function | 316-321 | [card](#settings_of) |
| `labels_of` | function | 324-325 | [card](#labels_of) |
| `comp_label` | function | 328-329 | [card](#comp_label) |
| `issue_text` | function | 332-338 | [card](#issue_textgh-path-ref-fallback_title) |
| `assignment` | function | 341-345 | [card](#assignmentgh-base-model) |
| `json_file` | function | 348-353 | [card](#json_filegh-path-ref) |
| `section` | function | 356-362 | [card](#sectiontext-title) |
| `report_facts` | function | 365-378 | [card](#report_factstext) |
| `as_int` | function | 381-385 | [card](#as_intvalue) |
| `status_of` | function | 388-391 | [card](#status_ofgh-path-ref) |
| `Queue` | class | 396-794 | [class](#queue) |
| `Queue.__init__` | method | 397-399 | [card](#queue__init__gh-log-print) |
| `Queue.run_issues` | method | 401-402 | [card](#queue_run_issueslabels-state-open) |
| `Queue.agent_pr` | method | 404-410 | [card](#queue_agent_prissue-base) |
| `Queue.session` | method | 413-429 | [card](#queue_sessionissue-base-analysis-comp-none) |
| `Queue.held` | method | 431-441 | [card](#queue_heldissue) |
| `Queue.model_for` | method | 443-445 | [card](#queue_model_forissue) |
| `Queue.hold_start_error` | method | 447-453 | [card](#queue_hold_start_errorissue) |
| `Queue.fail_or_retry` | method | 455-474 | [card](#queue_fail_or_retryissue-pr-why) |
| `Queue.reconcile` | method | 477-487 | [card](#queue_reconcile) |
| `Queue.run` | method | 489-525 | [card](#queue_runtracker-settings) |
| `Queue.plan_phase` | method | 527-549 | [card](#queue_plan_phasetracker-settings-analysis) |
| `Queue.start_chunk` | method | 551-563 | [card](#queue_start_chunkanalysis-name-fresh-false-note) |
| `Queue.component` | method | 565-643 | [card](#queue_componentanalysis-name) |
| `Queue.follow` | method | 645-692 | [card](#queue_followanalysis-name-issue) |
| `Queue.check` | method | 694-711 | [card](#queue_checkanalysis-name-branch) |
| `Queue.assemble_phase` | method | 713-753 | [card](#queue_assemble_phasetracker-settings-analysis) |
| `Queue.render` | method | 755-765 | [card](#queue_rendertracker-settings-rows) |
| `Queue.delta` | method | 768-794 | [card](#queue_deltachanged-settings_analysiscodebase-analysis) |
| `main` | function | 797-840 | [card](#main) |

## Call graph

```mermaid
flowchart LR
  init["GitHub.__init__"]
  request["GitHub.request"]
  call["GitHub.call"]
  paged["GitHub.paged"]
  ensurelabel["ensure_label"]
  ensureall["ensure_labels"]
  createissue["create_issue"]
  timeline["GitHub.timeline"]
  linked["GitHub.linked_prs"]
  agentevents["agent_events"]
  isagent["is_agent_pr"]
  starterror["start_error"]
  assigned["GitHub.assigned_at"]
  tarball["GitHub.tarball"]
  label["GitHub.label"]
  ready["GitHub.ready"]
  merge["GitHub.merge"]
  now["now"]
  age["age"]
  settingsof["settings_of"]
  issuetext["issue_text"]
  jsonfile["json_file"]
  section["section"]
  reportfacts["report_facts"]
  statusof["status_of"]
  labelsof["labels_of"]
  complabel["comp_label"]
  assignment["assignment"]
  asint["as_int"]
  queueinit["Queue.__init__"]
  runissues["Queue.run_issues"]
  agentpr["Queue.agent_pr"]
  session["Queue.session"]
  held["Queue.held"]
  modelfor["Queue.model_for"]
  holdstarterror["Queue.hold_start_error"]
  failorretry["Queue.fail_or_retry"]
  reconcile["Queue.reconcile"]
  run["Queue.run"]
  planphase["Queue.plan_phase"]
  startchunk["Queue.start_chunk"]
  component["Queue.component"]
  follow["Queue.follow"]
  check["Queue.check"]
  assemblephase["Queue.assemble_phase"]
  render["Queue.render"]
  delta["Queue.delta"]
  main["main"]
  cmprows["components.rows_of"]
  cmpmap["components.component_map"]
  cmpassign["components.assign"]
  assign["assign"]
  branchprs["branch_prs"]
  branchsha["branch_sha"]
  close["close"]
  closepr["close_pr"]
  comment["comment"]
  committime["commit_time"]
  createbranch["create_branch"]
  createpr["create_pr"]
  defaultbranch["default_branch"]
  file["file"]
  issues["issues"]
  unassign["unassign"]
  unlabel["unlabel"]
  prfiles["pr_files"]
  prs["prs"]
  resetbranch["reset_branch"]
  setbody["set_body"]
  paged -->|"call"| call
  call -->|"request"| request
  ensureall -->|"ensure_label"| ensurelabel
  createissue -->|"ensure_label"| ensurelabel
  linked -->|"timeline"| timeline
  linked -->|"call"| call
  agentevents -->|"timeline"| timeline
  isagent -->|"agent_events"| agentevents
  starterror -->|"assigned_at"| assigned
  starterror -->|"timeline"| timeline
  assigned -->|"timeline"| timeline
  label -->|"ensure_label"| ensurelabel
  ready -->|"request"| request
  merge -->|"ready"| ready
  merge -->|"call"| call
  age -->|"now"| now
  issuetext -->|"file"| call
  jsonfile -->|"file"| call
  reportfacts -->|"section"| section
  statusof -->|"json_file"| jsonfile
  runissues -->|"issues"| call
  agentpr -->|"linked_prs"| linked
  agentpr -->|"is_agent_pr"| isagent
  session -->|"agent_pr"| agentpr
  session -->|"age"| age
  session -->|"labels_of"| labelsof
  held -->|"labels_of"| labelsof
  held -->|"assignment"| assignment
  held -->|"model_for"| modelfor
  modelfor -->|"labels_of"| labelsof
  holdstarterror -->|"start_error"| starterror
  failorretry -->|"model_for"| modelfor
  failorretry -->|"labels_of"| labelsof
  reconcile -->|"settings_of"| settingsof
  reconcile -->|"run"| run
  run -->|"json_file"| jsonfile
  run -->|"plan_phase"| planphase
  run -->|"component"| component
  run -->|"as_int"| asint
  run -->|"start_chunk"| startchunk
  run -->|"assemble_phase"| assemblephase
  planphase -->|"run_issues"| runissues
  planphase -->|"issue_text"| issuetext
  planphase -->|"session"| session
  planphase -->|"held"| held
  planphase -->|"hold_start_error"| holdstarterror
  planphase -->|"fail_or_retry"| failorretry
  startchunk -->|"branch_sha"| branchsha
  startchunk -->|"comp_label"| complabel
  startchunk -->|"issue_text"| issuetext
  component -->|"branch_prs"| branchprs
  component -->|"run_issues"| runissues
  component -->|"follow"| follow
  component -->|"status_of"| statusof
  component -->|"check"| check
  component -->|"report_facts"| reportfacts
  component -->|"comp_label"| complabel
  follow -->|"session"| session
  follow -->|"fail_or_retry"| failorretry
  follow -->|"labels_of"| labelsof
  follow -->|"status_of"| statusof
  follow -->|"as_int"| asint
  check -->|"tarball"| tarball
  assemblephase -->|"run_issues"| runissues
  assemblephase -->|"session"| session
  assemblephase -->|"report_facts"| reportfacts
  assemblephase -->|"issue_text"| issuetext
  assemblephase -->|"held"| held
  assemblephase -->|"fail_or_retry"| failorretry
  render -->|"now"| now
  delta -->|"json_file"| jsonfile
  delta -->|"comp_label"| complabel
  delta -->|"assignment"| assignment
  delta -->|"rows_of"| cmprows
  delta -->|"component_map"| cmpmap
  delta -->|"assign"| cmpassign
  main -->|"GitHub"| init
  main -->|"Queue"| queueinit
  main -->|"ensure_labels"| ensureall
  main -->|"issues"| paged
  main -->|"create_issue"| createissue
  main -->|"reconcile"| reconcile
  main -->|"delta"| delta
  agentevents -->|"timeline"| timeline
  agentpr -->|"is_agent_pr"| isagent
  agentpr -->|"linked_prs"| linked
  assemblephase -->|"assignment"| assignment
  assemblephase -->|"close"| close
  assemblephase -->|"comment"| comment
  assemblephase -->|"create_issue"| createissue
  assemblephase -->|"fail_or_retry"| failorretry
  assemblephase -->|"file"| file
  assemblephase -->|"held"| held
  assemblephase -->|"hold_start_error"| holdstarterror
  assemblephase -->|"is_agent_pr"| isagent
  assemblephase -->|"issue_text"| issuetext
  assemblephase -->|"linked_prs"| linked
  assemblephase -->|"report_facts"| reportfacts
  assemblephase -->|"run_issues"| runissues
  assemblephase -->|"session"| session
  assign -->|"call"| call
  branchprs -->|"paged"| paged
  branchsha -->|"call"| call
  check -->|"run"| run
  close -->|"call"| call
  closepr -->|"call"| call
  comment -->|"call"| call
  committime -->|"call"| call
  component -->|"assignment"| assignment
  component -->|"branch_prs"| branchprs
  component -->|"close"| close
  component -->|"comp_label"| complabel
  component -->|"create_issue"| createissue
  component -->|"create_pr"| createpr
  component -->|"file"| file
  component -->|"held"| held
  component -->|"labels_of"| labelsof
  component -->|"report_facts"| reportfacts
  component -->|"run_issues"| runissues
  component -->|"start_chunk"| startchunk
  component -->|"status_of"| statusof
  createbranch -->|"call"| call
  createissue -->|"call"| call
  createissue -->|"ensure_label"| ensurelabel
  createpr -->|"call"| call
  defaultbranch -->|"call"| call
  delta -->|"assign"| cmpassign
  delta -->|"comp_label"| complabel
  delta -->|"create_issue"| createissue
  delta -->|"default_branch"| defaultbranch
  delta -->|"issues"| issues
  delta -->|"json_file"| jsonfile
  ensurelabel -->|"call"| call
  ensurelabel -->|"paged"| paged
  ensureall -->|"ensure_label"| ensurelabel
  failorretry -->|"assignment"| assignment
  failorretry -->|"close"| close
  failorretry -->|"close_pr"| closepr
  failorretry -->|"comment"| comment
  failorretry -->|"create_issue"| createissue
  failorretry -->|"label"| label
  failorretry -->|"labels_of"| labelsof
  failorretry -->|"model_for"| modelfor
  failorretry -->|"unassign"| unassign
  file -->|"call"| call
  follow -->|"as_int"| asint
  follow -->|"close"| close
  follow -->|"fail_or_retry"| failorretry
  follow -->|"file"| file
  follow -->|"hold_start_error"| holdstarterror
  follow -->|"label"| label
  follow -->|"labels_of"| labelsof
  follow -->|"merge"| merge
  follow -->|"pr_files"| prfiles
  follow -->|"status_of"| statusof
  follow -->|"unlabel"| unlabel
  held -->|"assign"| assign
  held -->|"comment"| comment
  held -->|"labels_of"| labelsof
  held -->|"model_for"| modelfor
  held -->|"set_body"| setbody
  holdstarterror -->|"comment"| comment
  holdstarterror -->|"label"| label
  holdstarterror -->|"start_error"| starterror
  holdstarterror -->|"unassign"| unassign
  isagent -->|"agent_events"| agentevents
  issuetext -->|"file"| file
  issues -->|"paged"| paged
  jsonfile -->|"file"| file
  label -->|"call"| call
  main -->|"create_issue"| createissue
  main -->|"ensure_labels"| ensureall
  main -->|"issues"| issues
  modelfor -->|"labels_of"| labelsof
  planphase -->|"assignment"| assignment
  planphase -->|"create_issue"| createissue
  planphase -->|"fail_or_retry"| failorretry
  planphase -->|"held"| held
  planphase -->|"hold_start_error"| holdstarterror
  planphase -->|"issue_text"| issuetext
  planphase -->|"render"| render
  planphase -->|"run_issues"| runissues
  planphase -->|"session"| session
  prfiles -->|"paged"| paged
  prs -->|"paged"| paged
  reconcile -->|"default_branch"| defaultbranch
  reconcile -->|"issues"| issues
  reconcile -->|"settings_of"| settingsof
  render -->|"set_body"| setbody
  reportfacts -->|"section"| section
  resetbranch -->|"call"| call
  run -->|"as_int"| asint
  run -->|"assemble_phase"| assemblephase
  run -->|"close"| close
  run -->|"json_file"| jsonfile
  run -->|"plan_phase"| planphase
  run -->|"render"| render
  run -->|"run_issues"| runissues
  run -->|"start_chunk"| startchunk
  runissues -->|"issues"| issues
  session -->|"agent_events"| agentevents
  session -->|"agent_pr"| agentpr
  session -->|"assigned_at"| assigned
  session -->|"commit_time"| committime
  session -->|"labels_of"| labelsof
  session -->|"start_error"| starterror
  session -->|"status_of"| statusof
  setbody -->|"call"| call
  startchunk -->|"assignment"| assignment
  startchunk -->|"branch_sha"| branchsha
  startchunk -->|"comp_label"| complabel
  startchunk -->|"create_branch"| createbranch
  startchunk -->|"create_issue"| createissue
  startchunk -->|"issue_text"| issuetext
  startchunk -->|"reset_branch"| resetbranch
  startchunk -->|"run_issues"| runissues
  starterror -->|"assigned_at"| assigned
  starterror -->|"timeline"| timeline
  statusof -->|"json_file"| jsonfile
  tarball -->|"request"| request
  timeline -->|"paged"| paged
  unassign -->|"call"| call
  unlabel -->|"call"| call
```

## Classes

### `GitHub`

Source: `.github/bible/bible_queue.py:88-302` <!-- code: fa8466d1289a -->

`GitHub` is a client for repository-scoped GitHub REST operations and the GraphQL ready-for-review mutation. Its instance fields are `repo`, `token`, normalized `api`, and `known_labels`; the last begins as `None` and is populated by `ensure_label`. (`.github/bible/bible_queue.py:89-92`, `.github/bible/bible_queue.py:133-138`)

No type annotations or factory are declared for the class; callers provide its constructor values. (inferred: `.github/bible/bible_queue.py:88-92`)

#### `GitHub.__init__(repo, token, api=None)`

Source: `.github/bible/bible_queue.py:89-92` <!-- code: b511658beb68 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | No call site is in this source range. |
| Calls | `os.environ.get`, `rstrip` |
| Purpose | Stores API credentials and a slash-trimmed API base URL, then initializes the label cache. |

**Steps**

1. Assigns `repo` and `token` to the instance. (`.github/bible/bible_queue.py:90`)
2. Selects `api`, then `GITHUB_API_URL`, then `https://api.github.com`, and removes trailing `/` characters. (`.github/bible/bible_queue.py:91`)
3. Initializes `known_labels` to `None`. (`.github/bible/bible_queue.py:92`)

**Pseudo-code**

```text
self.repo, self.token = repo, token
self.api = (api or GITHUB_API_URL or "https://api.github.com").rstrip("/")
self.known_labels = None
```

#### `GitHub.request(method, url, body=None, timeout=60)`

Source: `.github/bible/bible_queue.py:94-103` <!-- code: 1f8902892005 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.call` (`.github/bible/bible_queue.py:108`), `GitHub.tarball` (`.github/bible/bible_queue.py:240`), `GitHub.ready` (`.github/bible/bible_queue.py:288`) |
| Calls | `json.dumps`, `encode`, `urllib.request.Request`, `req.add_header`, `urllib.request.urlopen` |
| Purpose | Builds and opens an HTTP request with GitHub headers and an optional JSON body. |

**Steps**

1. Serializes a non-`None` body as encoded JSON; otherwise leaves request data unset. (`.github/bible/bible_queue.py:95`)
2. Creates a request using the supplied URL, method, and body bytes, and adds GitHub's JSON accept and API-version headers. (`.github/bible/bible_queue.py:96-98`)
3. Adds a bearer authorization header only when `token` is truthy, and adds JSON content type only when a body was serialized. (`.github/bible/bible_queue.py:99-102`)
4. Returns `urlopen`'s response using the supplied timeout. (`.github/bible/bible_queue.py:103`)

**Pseudo-code**

```text
data = encode JSON body if body is not None, otherwise None
create request(method, url, data)
add Accept and API-version headers
if token: add bearer Authorization header
if data is not None: add JSON content type
return urlopen(request, timeout)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:95` | conditional expression | `body is not None` | JSON is encoded; otherwise `data` is `None`. |
| `.github/bible/bible_queue.py:99` | if | `self.token` is truthy | Adds the bearer authorization header. |
| `.github/bible/bible_queue.py:101` | if | `data is not None` | Adds the JSON content-type header. |

#### `GitHub.call(method, path, body=None, ok404=False)`

Source: `.github/bible/bible_queue.py:105-117` <!-- code: 753c5f1a3922 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.paged` (`.github/bible/bible_queue.py:123`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:137`), `GitHub.create_issue` (`.github/bible/bible_queue.py:151`), `GitHub.default_branch` (`.github/bible/bible_queue.py:154`), `GitHub.branch_sha` (`.github/bible/bible_queue.py:157`), `GitHub.create_branch` (`.github/bible/bible_queue.py:161`), `GitHub.reset_branch` (`.github/bible/bible_queue.py:164`), `GitHub.file` (`.github/bible/bible_queue.py:167`), `GitHub.linked_prs` (`.github/bible/bible_queue.py:187`), `GitHub.commit_time` (`.github/bible/bible_queue.py:232`), `GitHub.label` (`.github/bible/bible_queue.py:263`), `GitHub.unlabel` (`.github/bible/bible_queue.py:266`), `GitHub.comment` (`.github/bible/bible_queue.py:269`), `GitHub.close` (`.github/bible/bible_queue.py:272`), `GitHub.set_body` (`.github/bible/bible_queue.py:275`), `GitHub.unassign` (`.github/bible/bible_queue.py:278`), `GitHub.assign` (`.github/bible/bible_queue.py:281`), `GitHub.merge` (`.github/bible/bible_queue.py:296`), `GitHub.close_pr` (`.github/bible/bible_queue.py:299`), `GitHub.create_pr` (`.github/bible/bible_queue.py:302`) |
| Calls | `path.startswith`, `GitHub.request`, response `read`, `json.loads`, `RuntimeError` |
| Purpose | Sends a REST request and converts response data and common request failures to Python values or a `RuntimeError`. |

**Steps**

1. Uses an absolute `path` beginning with `http` as-is; otherwise joins the API base, `/repos/`, repository, and path. (`.github/bible/bible_queue.py:106`)
2. Opens the request and reads its response bytes. (`.github/bible/bible_queue.py:107-109`)
3. On HTTP 404 with `ok404`, returns `None`; otherwise reads at most 300 decoded characters and raises a method/path/status/detail `RuntimeError`. (`.github/bible/bible_queue.py:110-114`)
4. Converts `URLError`, `TimeoutError`, and `OSError` to a `RuntimeError` containing the method, query-stripped path, and error. (`.github/bible/bible_queue.py:115-116`)
5. Decodes a nonempty payload as JSON; returns `{}` for an empty payload. (`.github/bible/bible_queue.py:117`)

**Pseudo-code**

```text
url = path if path starts with "http", otherwise API/repository/path
try request and read payload
on HTTPError:
    if status is 404 and ok404: return None
    raise RuntimeError with bounded response detail
on URL, timeout, or OS error: raise RuntimeError
return decoded JSON if payload, otherwise {}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:106` | conditional expression | `path.startswith("http")` | Uses `path`; otherwise constructs a repository API URL. |
| `.github/bible/bible_queue.py:110` | except | Request raises `urllib.error.HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:111` | if | Status is 404 and `ok404` is true | Returns `None`. |
| `.github/bible/bible_queue.py:114` | raise | Other HTTP errors | Raises `RuntimeError` with method, path, status, and detail. |
| `.github/bible/bible_queue.py:115` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Enters network error handling. |
| `.github/bible/bible_queue.py:116` | raise | A listed network error occurred | Raises `RuntimeError` with method, path, and error. |
| `.github/bible/bible_queue.py:117` | conditional expression | Payload is nonempty | Decodes JSON; otherwise returns `{}`. |

#### `GitHub.paged(path)`

Source: `.github/bible/bible_queue.py:119-127` <!-- code: 1bb6c1899527 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.issues` (`.github/bible/bible_queue.py:131`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:135`), `GitHub.prs` (`.github/bible/bible_queue.py:174`), `GitHub.timeline` (`.github/bible/bible_queue.py:177`), `GitHub.branch_prs` (`.github/bible/bible_queue.py:193`), `GitHub.pr_files` (`.github/bible/bible_queue.py:225`) |
| Calls | `GitHub.call`, `len` |
| Purpose | Fetches successive pages of up to 100 results and returns their concatenation. |

**Steps**

1. Starts with an empty result and page number 1. (`.github/bible/bible_queue.py:120`)
2. Chooses `&` if `path` already contains `?`, otherwise `?`, then requests `per_page=100` and the current page with GET. (`.github/bible/bible_queue.py:121-123`)
3. Appends each batch; returns the accumulated list when a batch has fewer than 100 entries, otherwise increments the page and repeats. (`.github/bible/bible_queue.py:124-127`)

**Pseudo-code**

```text
out = []
page = 1
repeat:
    request next page using ? or &
    append batch
    if batch has fewer than 100 entries: return out
    page += 1
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:121` | while | Always | Repeats page requests until a short batch is returned. |
| `.github/bible/bible_queue.py:122` | conditional expression | `path` contains `?` | Chooses `&`; otherwise chooses `?`. |
| `.github/bible/bible_queue.py:125` | if | Batch length is less than 100 | Returns all accumulated entries; otherwise proceeds to the next page. |

#### `GitHub.issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:129-131` <!-- code: b3f969457f25 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `urllib.parse.quote`, `join`, `GitHub.paged` |
| Purpose | Lists issues for encoded labels and a state, excluding pull requests. |

**Steps**

1. Joins labels with commas and URL-quotes the result. (`.github/bible/bible_queue.py:130`)
2. Pages `/issues` with the requested state and labels query, then keeps only objects without a `pull_request` key. (`.github/bible/bible_queue.py:131`)

**Pseudo-code**

```text
q = URL-quote(comma-joined labels)
return paged issues for state and q, excluding pull request objects
```

#### `GitHub.ensure_label(name, why="Codebase analysis run")`

Source: `.github/bible/bible_queue.py:133-138` <!-- code: c80387a5616e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.ensure_labels` (`.github/bible/bible_queue.py:142`), `GitHub.create_issue` (`.github/bible/bible_queue.py:146`), `GitHub.label` (`.github/bible/bible_queue.py:262`) |
| Calls | `GitHub.paged`, `GitHub.call`, `known_labels.add` |
| Purpose | Loads the known-label set on first use and creates a requested label if it is absent. |

**Steps**

1. If `known_labels` is `None`, pages `/labels` and caches their names. (`.github/bible/bible_queue.py:134-135`)
2. If `name` is missing, posts a label with the fixed color `5319e7` and `why` truncated to 100 characters, then adds the name to the cache. (`.github/bible/bible_queue.py:136-138`)

**Pseudo-code**

```text
if label cache is None: cache names from paged /labels
if name is not cached:
    POST label(name, color 5319e7, description why[:100])
    add name to cache
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:134` | if | `known_labels` is `None` | Fetches and caches current label names. |
| `.github/bible/bible_queue.py:136` | if | `name` is not in the cache | Creates the label and adds its name to the cache. |

#### `GitHub.ensure_labels()`

Source: `.github/bible/bible_queue.py:140-142` <!-- code: 3233fadcc4c0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `LABELS.items`, `GitHub.ensure_label` |
| Purpose | Ensures each label defined in the module's `LABELS` mapping exists. |

**Steps**

1. Iterates each `(name, why)` pair in `LABELS` and invokes `ensure_label`. (`.github/bible/bible_queue.py:141-142`)

**Pseudo-code**

```text
for name, why in LABELS:
    ensure_label(name, why)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:141` | for | For each `(name, why)` in `LABELS.items()` | Calls `ensure_label` once for that pair. |

#### `GitHub.create_issue(title, body, labels, assign=None)`

Source: `.github/bible/bible_queue.py:144-151` <!-- code: c0db4afc186c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures labels, optionally configures agent assignment, and creates an issue. |

**Steps**

1. Ensures every requested label, using its `LABELS` description or `Codebase analysis run` as the fallback. (`.github/bible/bible_queue.py:145-146`)
2. Builds a payload containing `title`, `body`, and `labels`; if `assign` is not `None`, adds the Copilot assignee and `agent_assignment`. (`.github/bible/bible_queue.py:147-150`)
3. Posts the payload to `/issues` and returns the result of `call`. (`.github/bible/bible_queue.py:151`)

**Pseudo-code**

```text
for label in labels: ensure_label(label, mapped description or default)
payload = {title, body, labels}
if assign is not None: add Copilot assignee and agent_assignment
return POST /issues(payload)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:145` | for | For each requested label | Calls `ensure_label` with its mapped or fallback description. |
| `.github/bible/bible_queue.py:148` | if | `assign` is not `None` | Adds `COPILOT` and the assignment value to the payload. |

#### `GitHub.default_branch()`

Source: `.github/bible/bible_queue.py:153-154` <!-- code: 4eb167486c4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Returns the repository's `default_branch` value. |

**Steps**

1. Gets the repository resource at the empty path and returns its `default_branch` field. (`.github/bible/bible_queue.py:154`)

**Pseudo-code**

```text
return GET repository["default_branch"]
```

#### `GitHub.branch_sha(branch)`

Source: `.github/bible/bible_queue.py:156-158` <!-- code: 446defb234bd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Returns a branch reference's object SHA or `None` when the reference is absent. |

**Steps**

1. Quotes `branch` and gets its head reference with `ok404=True`. (`.github/bible/bible_queue.py:157`)
2. Returns `ref["object"]["sha"]` if a reference was returned, otherwise `None`. (`.github/bible/bible_queue.py:158`)

**Pseudo-code**

```text
ref = GET quoted branch reference, allowing 404
return ref.object.sha if ref else None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:158` | conditional expression | A reference was returned | Returns its object SHA; otherwise returns `None`. |

#### `GitHub.create_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:160-161` <!-- code: b860758c1ca1 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Creates a Git reference for a branch at a supplied SHA. |

**Steps**

1. Posts `ref: "refs/heads/" + branch` and `sha` to `/git/refs`. (`.github/bible/bible_queue.py:161`)

**Pseudo-code**

```text
POST /git/refs with ref "refs/heads/" + branch and sha
```

#### `GitHub.reset_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:163-164` <!-- code: 43e383793681 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Force-updates a branch reference to a supplied SHA. |

**Steps**

1. Quotes `branch` and PATCHes its head reference with the supplied SHA and `force: True`. (`.github/bible/bible_queue.py:164`)

**Pseudo-code**

```text
PATCH quoted head reference with sha and force=True
```

#### `GitHub.file(path, ref)`

Source: `.github/bible/bible_queue.py:166-170` <!-- code: e383f7bd9e38 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call`, `urllib.parse.quote`, `isinstance`, `base64.b64decode`, `decode` |
| Purpose | Retrieves and decodes a text file from a repository reference. |

**Steps**

1. Quotes `path` and `ref` and GETs the contents endpoint with `ok404=True`. (`.github/bible/bible_queue.py:167`)
2. Returns `None` for a falsey response, a list response, or a response without `content`. (`.github/bible/bible_queue.py:168-169`)
3. Base64-decodes the content and decodes UTF-8 with replacement for invalid bytes. (`.github/bible/bible_queue.py:170`)

**Pseudo-code**

```text
got = GET quoted contents path at quoted ref, allowing 404
if got is falsey, a list, or lacks content: return None
return base64-decode content, then UTF-8 decode with replacement
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:168` | if | Response is falsey, a list, or has no `content` | Returns `None`. |

#### `GitHub.prs(base=None, state="open")`

Source: `.github/bible/bible_queue.py:172-174` <!-- code: e46dcb273277 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `urllib.parse.quote`, `GitHub.paged` |
| Purpose | Lists pull requests by state and optional base branch. |

**Steps**

1. Builds `/pulls?state=<state>` and appends a URL-quoted base query only when `base` is truthy. (`.github/bible/bible_queue.py:173`)
2. Returns the paged results. (`.github/bible/bible_queue.py:174`)

**Pseudo-code**

```text
path = /pulls?state=state
if base is truthy: append quoted base query
return paged(path)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:173` | conditional expression | `base` is truthy | Appends `&base=` and the quoted base; otherwise appends nothing. |

#### `GitHub.timeline(number)`

Source: `.github/bible/bible_queue.py:176-177` <!-- code: 6df4539072ff -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.linked_prs` (`.github/bible/bible_queue.py:182`), `GitHub.agent_events` (`.github/bible/bible_queue.py:197`), `GitHub.start_error` (`.github/bible/bible_queue.py:210`), `GitHub.assigned_at` (`.github/bible/bible_queue.py:219`) |
| Calls | `GitHub.paged` |
| Purpose | Returns all paged timeline events for an issue number. |

**Steps**

1. Pages `/issues/<number>/timeline` and returns the result. (`.github/bible/bible_queue.py:177`)

**Pseudo-code**

```text
return paged /issues/<number>/timeline
```

#### `GitHub.linked_prs(number)`

Source: `.github/bible/bible_queue.py:179-188` <!-- code: 91e30cd14abd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.timeline`, `get`, `append`, `GitHub.call`, `sorted`, `set` |
| Purpose | Finds existing pull requests in this repository cross-referenced from an issue. |

**Steps**

1. Iterates the issue timeline and reads each event's source issue, defaulting missing source/repository values as shown. (`.github/bible/bible_queue.py:181-184`)
2. Collects the source number only for `cross-referenced` events whose source has a `pull_request` and whose repository full name equals this client's repository. (`.github/bible/bible_queue.py:185-186`)
3. Deduplicates and sorts numbers, GETs each pull request with `ok404=True`, and returns only non-`None` results. (`.github/bible/bible_queue.py:187-188`)

**Pseudo-code**

```text
nums = []
for timeline event:
    if cross-referenced PR belongs to this repository: append source number
found = GET each sorted unique number, allowing 404
return non-None pull requests
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:182` | for | For each issue timeline event | Inspects its source issue. |
| `.github/bible/bible_queue.py:185` | if | Event is a same-repository cross-reference with a pull request | Appends its source number. |

#### `GitHub.branch_prs(branch, base)`

Source: `.github/bible/bible_queue.py:190-193` <!-- code: fa42118d7d5a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `split`, `GitHub.paged`, `urllib.parse.quote` |
| Purpose | Lists all-state pull requests from this repository's branch into a specified base. |

**Steps**

1. Takes the owner portion before `/` in `repo`. (`.github/bible/bible_queue.py:192`)
2. Pages `/pulls` with `state=all`, quoted `owner:branch` as `head`, and quoted `base`. (`.github/bible/bible_queue.py:193`)

**Pseudo-code**

```text
owner = first segment of repo
return paged /pulls with state=all, head=quoted(owner + ":" + branch), base=quoted(base)
```

#### `GitHub.agent_events(number)`

Source: `.github/bible/bible_queue.py:195-199` <!-- code: 23a18c0ca1f4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.is_agent_pr` (`.github/bible/bible_queue.py:205`) |
| Calls | `GitHub.timeline`, `get` |
| Purpose | Returns qualifying Copilot work timeline events as `(event, timestamp)` pairs. |

**Steps**

1. Reads the timeline and returns pairs containing each event name and `created_at`, defaulting a missing timestamp to the empty string. (`.github/bible/bible_queue.py:197`)
2. Includes only events whose performed-via-app slug equals `AGENT_APP` and whose event is `copilot_work_started` or `copilot_work_finished`. (`.github/bible/bible_queue.py:198-199`)

**Pseudo-code**

```text
return (event, created_at or "") for timeline events
    whose app slug is AGENT_APP and event is started or finished
```

#### `GitHub.is_agent_pr(pr)`

Source: `.github/bible/bible_queue.py:201-205` <!-- code: 5e675426c513 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `get`, `GitHub.agent_events`, `any` |
| Purpose | Tests whether a pull request is attributed to a configured agent login or has a Copilot-start event. |

**Steps**

1. Returns `True` if the pull request user's login (defaulting to an empty string) is in `AGENT_LOGINS`. (`.github/bible/bible_queue.py:203-204`)
2. Otherwise returns whether any event for the pull request number is `copilot_work_started`. (`.github/bible/bible_queue.py:205`)

**Pseudo-code**

```text
if PR user's login is in AGENT_LOGINS: return True
return any agent event is copilot_work_started
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:203` | if | PR user's login is in `AGENT_LOGINS` | Returns `True` without checking the timeline. |

#### `GitHub.start_error(issue)`

Source: `.github/bible/bible_queue.py:207-215` <!-- code: d25f1505b57a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.assigned_at`, `GitHub.timeline`, `get`, `START_ERROR.search`, `splitlines`, `strip` |
| Purpose | Returns the first matching agent start-error comment since the last assignment, or `None`. |

**Steps**

1. Gets the last assignment time using `assigned_at`, then scans the issue timeline. (`.github/bible/bible_queue.py:209-210`)
2. Selects a commenter login from `actor` or `user`; requires a `commented` event by a configured agent at or after the assignment time and a body matching `START_ERROR`. (`.github/bible/bible_queue.py:211-213`)
3. Returns the stripped first body line, truncated to 300 characters, for the first qualifying event; returns `None` if no event qualifies. (`.github/bible/bible_queue.py:214-215`)

**Pseudo-code**

```text
since = assigned_at(issue)
for timeline event:
    if commented by an agent at/after since and body matches START_ERROR:
        return stripped first body line[:300]
return None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:210` | for | For each issue timeline event | Checks actor, event time, and body. |
| `.github/bible/bible_queue.py:212` | if | Comment event from configured agent at/after assignment matches `START_ERROR` | Returns the bounded first line; otherwise continues scanning. |

#### `GitHub.assigned_at(issue)`

Source: `.github/bible/bible_queue.py:217-220` <!-- code: 8dec0d30b502 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.start_error` (`.github/bible/bible_queue.py:209`) |
| Calls | `GitHub.timeline`, `get`, `max` |
| Purpose | Returns the newest timestamp for an assignment event, falling back to issue creation time. |

**Steps**

1. Collects nonempty `created_at` values from `assigned` timeline events for the issue. (`.github/bible/bible_queue.py:219`)
2. Returns the maximum timestamp, or `issue["created_at"]` if there were none. (`.github/bible/bible_queue.py:220`)

**Pseudo-code**

```text
times = created_at for assigned events with a timestamp
return max(times) if any, otherwise issue.created_at
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:220` | conditional expression | At least one assignment timestamp exists | Returns the newest timestamp; otherwise uses issue creation time. |

#### `GitHub.pr_files(number)`

Source: `.github/bible/bible_queue.py:222-229` <!-- code: 4c64f0e6b538 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.paged`, `append`, `get` |
| Purpose | Returns each changed filename and, when present, its previous name. |

**Steps**

1. Pages the pull request files endpoint and appends each `filename`. (`.github/bible/bible_queue.py:224-226`)
2. Appends `previous_filename` when the field is truthy, then returns the list. (`.github/bible/bible_queue.py:227-229`)

**Pseudo-code**

```text
out = []
for paged pull request file:
    append filename
    if previous_filename: append it
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:225` | for | For each paged pull request file | Appends its current filename. |
| `.github/bible/bible_queue.py:227` | if | `previous_filename` is truthy | Appends the previous filename. |

#### `GitHub.commit_time(sha)`

Source: `.github/bible/bible_queue.py:231-232` <!-- code: a3036655ce65 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Returns the committer date for a commit SHA. |

**Steps**

1. GETs `/commits/<sha>` and returns `commit.committer.date`. (`.github/bible/bible_queue.py:232`)

**Pseudo-code**

```text
return GET /commits/<sha>.commit.committer.date
```

#### `GitHub.tarball(ref, dest)`

Source: `.github/bible/bible_queue.py:234-259` <!-- code: 37cdbd678a08 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `urllib.parse.quote`, `tempfile.TemporaryFile`, `GitHub.request`, `shutil.copyfileobj`, `seek`, `os.path.abspath`, `tarfile.open`, `RuntimeError`, `split`, `len`, `isfile`, `isdir`, `os.path.normpath`, `os.path.join`, `startswith`, `os.makedirs`, `os.path.dirname`, `tar.extractfile`, `open` |
| Purpose | Downloads a repository archive to a temporary file and writes accepted regular files/directories under `dest`. |

**Steps**

1. Constructs an archive URL from the API base, repository, and quoted reference; streams the GET response into a temporary file with a 300-second timeout. (`.github/bible/bible_queue.py:237-241`)
2. Converts `URLError`, `TimeoutError`, and `OSError` from the request into `RuntimeError`; then seeks to the start and resolves `dest` to an absolute root. (`.github/bible/bible_queue.py:239-245`)
3. Iterates the gzip tar members, splitting each name once at `/`; skips names without a nonempty second part and members that are neither files nor directories. (`.github/bible/bible_queue.py:246-250`)
4. Joins and normalizes the relative member path under `root`; skips targets that do not start with `root + os.sep`. (`.github/bible/bible_queue.py:251-253`)
5. Creates accepted directories recursively; for accepted files, creates the parent directory and copies extracted bytes to a binary output file. (`.github/bible/bible_queue.py:254-259`)

**Pseudo-code**

```text
stream GET tarball(ref) to temporary file
seek to start; root = absolute(dest)
for archive member:
    skip invalid name or non-file/non-directory
    target = normalized join(root, member-relative path)
    skip target outside root
    if directory: mkdir target
    else: mkdir parent and copy extracted bytes to target
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:242` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Raises `RuntimeError` identifying the reference and error. |
| `.github/bible/bible_queue.py:243` | raise | A listed request error occurred | Stops with `RuntimeError`. |
| `.github/bible/bible_queue.py:247` | for | For each archive member | Checks whether to skip or unpack it. |
| `.github/bible/bible_queue.py:249` | if | Missing relative path or member is neither file nor directory | Skips the member. |
| `.github/bible/bible_queue.py:252` | if | Normalized target is not under the root prefix | Skips the member. |
| `.github/bible/bible_queue.py:254` | if | Member is a directory | Creates the directory and continues to the next member. |

#### `GitHub.label(number, name)`

Source: `.github/bible/bible_queue.py:261-263` <!-- code: 3c67a9360e66 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures and adds one label to an issue. |

**Steps**

1. Ensures the label using its `LABELS` description or the default description. (`.github/bible/bible_queue.py:262`)
2. Posts `{"labels": [name]}` to the issue labels endpoint. (`.github/bible/bible_queue.py:263`)

**Pseudo-code**

```text
ensure label using mapped description or default
POST issue labels with [name]
```

#### `GitHub.unlabel(number, name)`

Source: `.github/bible/bible_queue.py:265-266` <!-- code: caf34958b931 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Removes a label from an issue and permits a missing-label response. |

**Steps**

1. URL-quotes `name` and sends DELETE to the issue label endpoint with `ok404=True`. (`.github/bible/bible_queue.py:266`)

**Pseudo-code**

```text
DELETE quoted issue label endpoint, allowing 404
```

#### `GitHub.comment(number, text)`

Source: `.github/bible/bible_queue.py:268-269` <!-- code: a05e7f494734 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Creates an issue comment with the given body. |

**Steps**

1. Posts `{"body": text}` to `/issues/<number>/comments`. (`.github/bible/bible_queue.py:269`)

**Pseudo-code**

```text
POST issue comments with body=text
```

#### `GitHub.close(number, reason="completed")`

Source: `.github/bible/bible_queue.py:271-272` <!-- code: db2a40d380a0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Closes an issue with the supplied state reason. |

**Steps**

1. PATCHes `/issues/<number>` with `state: "closed"` and the supplied `state_reason`. (`.github/bible/bible_queue.py:272`)

**Pseudo-code**

```text
PATCH issue state=closed and state_reason=reason
```

#### `GitHub.set_body(number, body)`

Source: `.github/bible/bible_queue.py:274-275` <!-- code: 56545a0f998b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Replaces an issue's body. |

**Steps**

1. PATCHes `/issues/<number>` with `{"body": body}`. (`.github/bible/bible_queue.py:275`)

**Pseudo-code**

```text
PATCH issue body=body
```

#### `GitHub.unassign(number)`

Source: `.github/bible/bible_queue.py:277-278` <!-- code: 415484346894 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Removes the configured Copilot assignee from an issue. |

**Steps**

1. Sends DELETE to `/issues/<number>/assignees` with `COPILOT` as the sole assignee. (`.github/bible/bible_queue.py:278`)

**Pseudo-code**

```text
DELETE issue assignees with [COPILOT]
```

#### `GitHub.assign(number, assign)`

Source: `.github/bible/bible_queue.py:280-281` <!-- code: 8fb2f09224db -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Assigns Copilot to an issue with the provided agent-assignment data. |

**Steps**

1. Posts `COPILOT` as the sole assignee and includes the supplied `agent_assignment`. (`.github/bible/bible_queue.py:281`)

**Pseudo-code**

```text
POST issue assignees with [COPILOT] and agent_assignment=assign
```

#### `GitHub.ready(pr)`

Source: `.github/bible/bible_queue.py:283-291` <!-- code: ae31dacf00e7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.merge` (`.github/bible/bible_queue.py:295`) |
| Calls | `endswith`, `GitHub.request`, response `read`, `RuntimeError` |
| Purpose | Marks a draft pull request ready for review through GitHub GraphQL. |

**Steps**

1. Defines the `markPullRequestReadyForReview` mutation and chooses the GraphQL URL; for an API base ending `/api/v3`, removes `/v3` before adding `/graphql`. (`.github/bible/bible_queue.py:285-286`)
2. POSTs the query and `pr["node_id"]` as the `id` variable, then reads the response. (`.github/bible/bible_queue.py:287-289`)
3. Converts an `HTTPError` to a `RuntimeError` containing the GraphQL operation and HTTP status. (`.github/bible/bible_queue.py:290-291`)

**Pseudo-code**

```text
query = markPullRequestReadyForReview(pr.node_id)
url = GraphQL endpoint adjusted for /api/v3
try POST query and read response
on HTTPError: raise RuntimeError with status
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:286` | conditional expression | API URL ends with `/api/v3` | Removes `/v3` before appending `/graphql`; otherwise appends `/graphql` directly. |
| `.github/bible/bible_queue.py:290` | except | Request raises `HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:291` | raise | GraphQL request raises `HTTPError` | Raises `RuntimeError` with operation and HTTP status. |

#### `GitHub.merge(pr, title)`

Source: `.github/bible/bible_queue.py:293-296` <!-- code: 68adaed91bed -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `get`, `GitHub.ready`, `GitHub.call` |
| Purpose | Marks a draft ready, when needed, and requests a squash merge with the supplied title. |

**Steps**

1. Calls `ready` only when `pr["draft"]` is truthy. (`.github/bible/bible_queue.py:294-295`)
2. PUTs `/pulls/<number>/merge` with `merge_method: "squash"` and `commit_title: title`. (`.github/bible/bible_queue.py:296`)

**Pseudo-code**

```text
if PR is draft: mark it ready
PUT merge request with squash method and title
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:294` | if | `pr["draft"]` is truthy | Calls `ready` before requesting the merge. |

#### `GitHub.close_pr(number)`

Source: `.github/bible/bible_queue.py:298-299` <!-- code: c5e4b3b311ae -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Closes a pull request. |

**Steps**

1. PATCHes `/pulls/<number>` with `state: "closed"`. (`.github/bible/bible_queue.py:299`)

**Pseudo-code**

```text
PATCH pull request state=closed
```

#### `GitHub.create_pr(head, base, title, body)`

Source: `.github/bible/bible_queue.py:301-302` <!-- code: 9b2aa4667c1c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site is in this source range. |
| Calls | `GitHub.call` |
| Purpose | Creates a pull request and returns the API result. |

**Steps**

1. POSTs `head`, `base`, `title`, and `body` to `/pulls`, returning `call`'s result. (`.github/bible/bible_queue.py:302`)

**Pseudo-code**

```text
return POST /pulls with head, base, title, and body
```

### `Queue`

Source: `.github/bible/bible_queue.py:396-794` <!-- code: 0f494b4769c4 -->

`Queue` coordinates tracker issues, component sessions, verification/revision cycles, assembly, and delta updates. Its constructor sets the GitHub client, logger, and skill directory; methods also populate run-specific fields such as `default`, `settings`, `tracker`, `run_label`, and `estimate`. (`.github/bible/bible_queue.py:397-399`, `.github/bible/bible_queue.py:478`, `.github/bible/bible_queue.py:491-492`, `.github/bible/bible_queue.py:507`)

#### `Queue.__init__(gh, log=print)`

Source: `.github/bible/bible_queue.py:397-399` <!-- code: 11924208c0e9 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:817`) |
| Calls | `os.environ.get` |
| Purpose | Stores the GitHub client and logger, and selects the skills directory. |

**Steps**

1. Stores `gh` and `log` on the instance. (`.github/bible/bible_queue.py:398`)
2. Reads `BIBLE_SKILLS`, defaulting to `.github/skills`. (`.github/bible/bible_queue.py:399`)

**Pseudo-code**

```text
self.gh, self.log = gh, log
self.skills = BIBLE_SKILLS or ".github/skills"
```

#### `Queue.run_issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:401-402` <!-- code: 9186c4a33e43 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:505`), `Queue.plan_phase` (`.github/bible/bible_queue.py:529`), `Queue.start_chunk` (`.github/bible/bible_queue.py:557`), `Queue.component` (`.github/bible/bible_queue.py:577`, `.github/bible/bible_queue.py:586`, `.github/bible/bible_queue.py:593`, `.github/bible/bible_queue.py:596`, `.github/bible/bible_queue.py:602`, `.github/bible/bible_queue.py:604`, `.github/bible/bible_queue.py:606`, `.github/bible/bible_queue.py:608`, `.github/bible/bible_queue.py:624`, `.github/bible/bible_queue.py:625`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:718`, `.github/bible/bible_queue.py:720`) |
| Calls | `self.gh.issues` |
| Purpose | Queries issues for the requested labels plus this run's unique label. |

**Steps**

1. Appends `self.run_label` to the supplied labels and calls `gh.issues` with the requested state. (`.github/bible/bible_queue.py:402`)

**Pseudo-code**

```text
return gh.issues(labels + [run_label], state)
```

#### `Queue.agent_pr(issue, base)`

Source: `.github/bible/bible_queue.py:404-410` <!-- code: 471c772b908b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:415`) |
| Calls | `reversed`, `self.gh.linked_prs`, `get`, `self.gh.is_agent_pr` |
| Purpose | Finds the newest linked pull request that is open, same-repository, targets `base`, and is by the agent. |

**Steps**

1. Iterates linked pull requests in reverse order. (`.github/bible/bible_queue.py:406`)
2. Reads the head repository full name, defaulting missing nested values to `{}`. (`.github/bible/bible_queue.py:407`)
3. Returns the first PR whose state is `open`, head repository is `gh.repo`, base ref matches, and `is_agent_pr` is true. (`.github/bible/bible_queue.py:408-409`)
4. Returns `None` when no linked PR qualifies. (`.github/bible/bible_queue.py:410`)

**Pseudo-code**

```text
for PR in reversed(linked_prs(issue.number)):
    head_repo = nested head.repo.full_name or None
    if open, same repository, matching base, and agent PR: return PR
return None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:406` | for | For each linked PR in reverse order | Checks newer linked PRs first. |
| `.github/bible/bible_queue.py:408` | if | PR is open, same-repository, targets `base`, and is an agent PR | Returns that PR. |

#### `Queue.session(issue, base, analysis, comp=None)`

Source: `.github/bible/bible_queue.py:413-429` <!-- code: 6fe9d410226f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:542`), `Queue.follow` (`.github/bible/bible_queue.py:648`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:735`) |
| Calls | `self.agent_pr`, `self.gh.start_error`, `age`, `self.gh.assigned_at`, `self.gh.agent_events`, `sorted`, `self.gh.commit_time`, `bool`, `status_of`, `labels_of`, `get` |
| Purpose | Classifies an issue's session as waiting, running, finished, no-start, or start-error and returns its PR if present. |

**Steps**

1. Looks up the agent PR. If absent, returns `("start-error", None)` for a detected start error; otherwise compares issue assignment age to `NO_PR_AFTER` and returns `no-start` or `waiting`. (`.github/bible/bible_queue.py:415-419`)
2. If agent work events exist, sorts them by timestamp and returns `finished` when the latest is `copilot_work_finished`, else `running`, together with the PR. (`.github/bible/bible_queue.py:420-422`)
3. Without work events, computes age from the PR head commit and marks `asked` when reviewers were requested or the PR is not draft. (`.github/bible/bible_queue.py:423-424`)
4. For a component chunk, reads status at the PR head SHA and considers it finished when final status plus an asked/idle condition holds, or when pushed age exceeds three times `IDLE_AFTER`. (`.github/bible/bible_queue.py:425-428`)
5. Otherwise returns `finished` when `asked` or pushed age exceeds `IDLE_AFTER`, else `running`; both paths include the PR. (`.github/bible/bible_queue.py:429`)

**Pseudo-code**

```text
pr = agent_pr(issue, base)
if no pr:
    if start_error(issue): return ("start-error", None)
    return ("no-start" if assignment age > NO_PR_AFTER else "waiting", None)
if work events:
    return ("finished" if newest event is finished else "running", pr)
pushed = age(head commit time)
asked = requested reviewers or not draft
if comp and issue is bible-chunk:
    final = head status state in FINAL_STATES
    return ("finished" if (final and (asked or pushed > IDLE_AFTER))
            or pushed > 3 * IDLE_AFTER else "running", pr)
return ("finished" if asked or pushed > IDLE_AFTER else "running", pr)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:416` | if | No agent PR was found | Enters start-error/no-start/waiting classification. |
| `.github/bible/bible_queue.py:417` | if | `start_error(issue)` is truthy | Returns start-error without a PR. |
| `.github/bible/bible_queue.py:419` | conditional expression | Assignment age exceeds `NO_PR_AFTER` | Returns `no-start`; otherwise returns `waiting`. |
| `.github/bible/bible_queue.py:421` | if | Agent work events exist | Uses latest work event to classify session state. |
| `.github/bible/bible_queue.py:422` | conditional expression | Latest work event is `copilot_work_finished` | Returns finished; otherwise running. |
| `.github/bible/bible_queue.py:425` | if | `comp` is truthy and issue has `bible-chunk` label | Uses head status and component-specific age rules. |
| `.github/bible/bible_queue.py:428` | conditional expression | Final status and asked/idle condition holds, or pushed age exceeds `3 * IDLE_AFTER` | Returns finished; otherwise running. |
| `.github/bible/bible_queue.py:429` | conditional expression | `asked` or pushed age exceeds `IDLE_AFTER` | Returns finished; otherwise running. |

#### `Queue.held(issue)`

Source: `.github/bible/bible_queue.py:431-441` <!-- code: 3727ef4cd11f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:540`), `Queue.component` (`.github/bible/bible_queue.py:580`, `.github/bible/bible_queue.py:599`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:733`) |
| Calls | `labels_of`, `ATTEMPT.sub`, `issue.get`, `re.search`, `self.gh.set_body`, `assignment`, `self.model_for`, `self.gh.assign`, `self.gh.comment` |
| Purpose | Stops work for a human-held issue or restarts an unassigned issue after the hold label is removed. |

**Steps**

1. Returns `True` immediately when `bible-needs-human` is among the issue's labels. (`.github/bible/bible_queue.py:433-434`)
2. If there are no assignees, resets the attempt marker to 1, writes the body, finds a `Base branch:` value, reassigns Copilot using that branch or `self.default` and `model_for`, and posts a retry comment. (`.github/bible/bible_queue.py:435-440`)
3. Returns `False` when it does not return early. (`.github/bible/bible_queue.py:441`)

**Pseudo-code**

```text
if issue has bible-needs-human: return True
if issue has no assignees:
    reset Attempt to 1 and save body
    base = Base branch match or default
    assign Copilot with base and model_for(issue)
    comment that the issue was reassigned
return False
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:433` | if | Issue has `bible-needs-human` | Returns `True`. |
| `.github/bible/bible_queue.py:435` | if | Issue has no assignees | Resets attempt, assigns, and comments; otherwise skips retry work. |
| `.github/bible/bible_queue.py:439` | conditional expression | A base-branch match exists | Passes the captured branch to `assignment`; otherwise passes `self.default`. |

#### `Queue.model_for(issue)`

Source: `.github/bible/bible_queue.py:443-445` <!-- code: 17f084589886 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:439`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:473`) |
| Calls | `labels_of`, `self.settings.get` |
| Purpose | Selects the verification model for verification issue types, otherwise the normal model. |

**Steps**

1. Gets the issue's label names. (`.github/bible/bible_queue.py:444`)
2. Returns `verify_model` when labels intersect `bible-verify` or `bible-verify-all`; otherwise returns `model`. (`.github/bible/bible_queue.py:445`)

**Pseudo-code**

```text
kinds = labels_of(issue)
return settings.verify_model if kinds intersects verify labels
       else settings.model
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:445` | conditional expression | `kinds` intersects the verification labels | Returns `verify_model`; otherwise returns `model`. |

#### `Queue.hold_start_error(issue)`

Source: `.github/bible/bible_queue.py:447-453` <!-- code: 510c0f07df06 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:544`), `Queue.follow` (`.github/bible/bible_queue.py:652`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:737`) |
| Calls | `self.gh.start_error`, `self.gh.label`, `self.gh.unassign`, `self.gh.comment` |
| Purpose | Holds a session with an agent start error for human intervention. |

**Steps**

1. Gets the start-error text or uses `Copilot could not start`. (`.github/bible/bible_queue.py:449`)
2. Adds `bible-needs-human`, unassigns Copilot, and posts a comment containing the reason and remediation guidance. (`.github/bible/bible_queue.py:450-453`)

**Pseudo-code**

```text
why = start_error(issue) or fallback message
label issue bible-needs-human
unassign Copilot
comment why and instructions for removing the hold
```

#### `Queue.fail_or_retry(issue, pr, why)`

Source: `.github/bible/bible_queue.py:455-474` <!-- code: c86515a02433 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:547`), `Queue.follow` (`.github/bible/bible_queue.py:655`, `.github/bible/bible_queue.py:668`, `.github/bible/bible_queue.py:681`, `.github/bible/bible_queue.py:684`, `.github/bible/bible_queue.py:687`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:740`) |
| Calls | `ATTEMPT.search`, `int`, `self.gh.comment`, `self.gh.close_pr`, `self.gh.label`, `self.gh.unassign`, `self.gh.close`, `ATTEMPT.sub`, `re.search`, `self.gh.create_issue`, `sorted`, `assignment`, `self.model_for`, `labels_of`, `startswith` |
| Purpose | Closes a failed attempt and opens its retry, or holds the issue after a second failure. |

**Steps**

1. Parses the attempt number from the issue body, defaulting to 1. (`.github/bible/bible_queue.py:457`)
2. If a PR was supplied, comments that it was not merged and closes it. (`.github/bible/bible_queue.py:458-460`)
3. When attempt is at least 2, labels and unassigns the issue, posts a human-action comment, and returns `False`. (`.github/bible/bible_queue.py:461-466`)
4. Otherwise comments that a new attempt will open, closes the issue with `not_planned`, updates or prepends the attempt marker, and extracts the base branch or uses `self.default`. (`.github/bible/bible_queue.py:467-471`)
5. Creates a replacement issue with only labels beginning `bible`, sorted, and assignment data for the chosen base and model; returns `True`. (`.github/bible/bible_queue.py:472-474`)

**Pseudo-code**

```text
attempt = parsed Attempt or 1
if PR: comment not merged; close PR
if attempt >= 2:
    label needs-human; unassign; comment; return False
comment retry; close issue not_planned
update Attempt marker; base = Base branch match or default
create replacement issue with bible labels and assignment
return True
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:458` | if | A PR was supplied | Comments on it and closes it. |
| `.github/bible/bible_queue.py:461` | if | Attempt is at least 2 | Holds the issue for a person and returns `False`. |
| `.github/bible/bible_queue.py:469` | conditional expression | Attempt marker is present | Replaces it; otherwise prepends `Attempt: 2`. |
| `.github/bible/bible_queue.py:473` | conditional expression | Base-branch regex matched | Uses captured branch; otherwise uses `self.default`. |

#### `Queue.reconcile()`

Source: `.github/bible/bible_queue.py:477-487` <!-- code: 405a62c3c051 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:834`) |
| Calls | `self.gh.default_branch`, `self.gh.issues`, `settings_of`, `self.log`, `self.run`, `type` |
| Purpose | Processes each open tracker independently so one failing tracker does not prevent others. |

**Steps**

1. Reads and stores the repository default branch. (`.github/bible/bible_queue.py:478`)
2. Iterates open issues labeled `bible-tracker`, parses each settings block, and logs/skips trackers without readable settings. (`.github/bible/bible_queue.py:479-483`)
3. Calls `run` for each readable tracker; catches any `Exception` and logs the tracker number, exception type, and message. (`.github/bible/bible_queue.py:484-487`)

**Pseudo-code**

```text
default = gh.default_branch()
for tracker in open bible-tracker issues:
    settings = settings_of(tracker)
    if not settings: log and continue
    try run(tracker, settings)
    except Exception: log and continue to next tracker
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:479` | for | For each open tracker issue | Parses settings and processes that tracker independently. |
| `.github/bible/bible_queue.py:481` | if | No readable settings block | Logs and skips the tracker. |
| `.github/bible/bible_queue.py:484` | try | Readable settings are present | Runs the tracker. |
| `.github/bible/bible_queue.py:486` | except | Tracker processing raises `Exception` | Logs the error and continues the tracker loop. |

#### `Queue.run(tracker, settings)`

Source: `.github/bible/bible_queue.py:489-525` <!-- code: 810b772ee155 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:485`) |
| Calls | `settings.get`, `json_file`, `self.plan_phase`, `isinstance`, `self.render`, `self.run_issues`, `self.component`, `as_int`, `self.start_chunk`, `self.assemble_phase`, `str`, `endswith`, `startswith`, `all` |
| Purpose | Dispatches a tracker to planning or runs selected components within a concurrency limit, then renders their state. |

**Steps**

1. Selects `analysis` from settings or `codebase-analysis`, stores settings/tracker/run label, and loads `components.json` from the default branch. (`.github/bible/bible_queue.py:490-493`)
2. If the catalog is missing/not a dict, proposed, or lacks a components list, delegates to `plan_phase` and returns. (`.github/bible/bible_queue.py:494-495`)
3. Extracts named component entries, reads the requested component selection, expands `all`/empty to every catalog name or splits and strips the comma-separated selection, and finds unknown names. (`.github/bible/bible_queue.py:496-499`)
4. If there are unknown names or no selected names, renders a stopped settings message and returns. (`.github/bible/bible_queue.py:500-504`)
5. Closes open plan issues, records estimated sessions, calls `component` per selected name, catches errors per component into a bounded status string, and counts active/waiting states. (`.github/bible/bible_queue.py:505-514`)
6. Parses concurrency; starts `not started` components while capacity remains, recording runtime errors as bounded statuses. (`.github/bible/bible_queue.py:515-522`)
7. If every component state is `merged`, adds whole-analysis assembly status; renders the resulting rows. (`.github/bible/bible_queue.py:523-525`)

**Pseudo-code**

```text
analysis = settings.analysis or "codebase-analysis"
store run fields; catalog = json_file(components.json)
if catalog is invalid/proposed: return plan_phase(...)
names = catalog component names
wanted = all names or parsed requested names
if unknown names or no wanted names: render stopped status; return
close open plan issues
for wanted name: component(name), record per-component error, count active
cap = concurrency as integer
for wanted name: if not started and capacity available, start chunk
if every row is merged: add assembly status
render rows
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:494` | if | Catalog is invalid, proposed, or components is not a list | Returns the planning-phase result. |
| `.github/bible/bible_queue.py:498` | conditional expression | Requested selection is `all` or empty | Uses all names; otherwise parses comma-separated names. |
| `.github/bible/bible_queue.py:500` | if | Selection contains unknown names or is empty | Renders stopped settings and returns. |
| `.github/bible/bible_queue.py:503` | conditional expression | At least one unknown component exists | Reports unknown names; otherwise reports no component selected. |
| `.github/bible/bible_queue.py:505` | for | For each open plan issue | Closes the issue. |
| `.github/bible/bible_queue.py:509` | for | For each requested component | Evaluates component state. |
| `.github/bible/bible_queue.py:510` | try | Component evaluation is invoked | Records the result or catches component failure. |
| `.github/bible/bible_queue.py:512` | except | Component evaluation raises `Exception` | Stores a per-component error status. |
| `.github/bible/bible_queue.py:514` | augmented assignment | For each component result | Increments active count when state ends in running/starting or begins waiting. |
| `.github/bible/bible_queue.py:516` | for | For each requested component | Considers starting a waiting component. |
| `.github/bible/bible_queue.py:517` | if | Component is not started and cap is zero or active is below cap | Attempts to start the next chunk. |
| `.github/bible/bible_queue.py:518` | try | Start conditions hold | Starts the component and increments active. |
| `.github/bible/bible_queue.py:521` | except | Starting the chunk raises `RuntimeError` | Records a bounded error status. |
| `.github/bible/bible_queue.py:523` | if | Every component row equals `merged` | Adds whole-analysis phase state. |

#### `Queue.plan_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:527-549` <!-- code: f5b3e835d2d7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:495`) |
| Calls | `self.run_issues`, `issue_text`, `self.gh.create_issue`, `self.render`, `assignment`, `settings.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry` |
| Purpose | Creates or tracks the plan issue and reports plan-session progress. |

**Steps**

1. Gets open plan issues for this run. (`.github/bible/bible_queue.py:528-529`)
2. With no open plan, loads plan title/body from the ledger; if body is empty, uses built-in instructions for planning and discovery, then creates the assigned plan issue and renders its assigned state. (`.github/bible/bible_queue.py:530-538`)
3. Otherwise selects the first issue; if held, renders the human-needed state. (`.github/bible/bible_queue.py:539-541`)
4. Classifies the session; on start-error, holds it and renders human-needed state. (`.github/bible/bible_queue.py:542-545`)
5. On no-start, invokes retry logic; renders the PR-review state if a PR exists or the current session state otherwise. (`.github/bible/bible_queue.py:546-549`)

**Pseudo-code**

```text
open_plan = run_issues(bible-plan)
if none:
    title, body = issue_text(plan.md)
    if no body: use built-in plan instructions
    create assigned plan issue
    return render assigned state
issue = first open plan
if held(issue): render human-needed state
state, pr = session(...)
if start-error: hold_start_error; render human-needed state
if no-start: fail_or_retry
render PR review state if pr exists, otherwise session state
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:530` | if | No open plan issue exists | Creates and assigns the plan issue. |
| `.github/bible/bible_queue.py:532` | if | Loaded issue body is falsey | Uses built-in plan instructions. |
| `.github/bible/bible_queue.py:540` | if | First open plan issue is held | Renders that a person must act. |
| `.github/bible/bible_queue.py:543` | if | Session state is `start-error` | Holds the issue and renders human-needed state. |
| `.github/bible/bible_queue.py:546` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:548` | conditional expression | `pr` exists | Renders review/merge PR number; otherwise renders session state. |

#### `Queue.start_chunk(analysis, name, fresh=False, note="")`

Source: `.github/bible/bible_queue.py:551-563` <!-- code: 7f612dd5f454 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:519`), `Queue.component` (`.github/bible/bible_queue.py:594`, `.github/bible/bible_queue.py:631`) |
| Calls | `self.gh.branch_sha`, `self.gh.create_branch`, `self.gh.reset_branch`, `self.run_issues`, `comp_label`, `issue_text`, `self.gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Creates the component branch when absent, optionally resets it for the first chunk, and opens the next assigned chunk issue. |

**Steps**

1. Sets branch to `bible/<name>` and reads the default branch SHA. (`.github/bible/bible_queue.py:553-554`)
2. Creates the component branch if it does not exist; otherwise, when `fresh` and no issue for that component exists in any state, resets it to the default SHA. (`.github/bible/bible_queue.py:555-558`)
3. Reads the component issue text from the default branch, sets component/base/attempt header, and creates a labeled chunk issue with optional note and model assignment. (`.github/bible/bible_queue.py:559-563`)

**Pseudo-code**

```text
branch = "bible/" + name
head_sha = default branch SHA
if branch missing: create branch at head_sha
elif fresh and no component issue in any state: reset branch to head_sha
title, body = issue_text(component issue file)
create assigned chunk issue with component/base/attempt header and optional note
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:555` | if | Branch SHA is falsey | Creates the branch at the default branch SHA. |
| `.github/bible/bible_queue.py:557` | elif | Branch exists, `fresh` is truthy, and no component issue exists in any state | Resets the branch to the default branch SHA. |
| `.github/bible/bible_queue.py:562` | conditional expression | `note` is truthy | Adds `note` and a newline before the body; otherwise adds no note prefix. |

#### `Queue.component(analysis, name)`

Source: `.github/bible/bible_queue.py:565-643` <!-- code: 3a16b7371216 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:511`) |
| Calls | `self.gh.branch_prs`, `get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `endswith`, `status_of`, `self.check`, `len`, `self.start_chunk`, `self.estimate.get`, `self.gh.close`, `labels_of`, `max`, `report_facts`, `self.gh.create_pr`, `self.gh.create_issue` |
| Purpose | Advances a component's queue from branch/chunk work through coverage, component verification/revision, and a final PR. |

**Steps**

1. Scans branch PRs into the default branch. Ignores a different repository, a PR predating the tracker, or a PR lacking this tracker reference; returns merged, review, or human-needed status for the first matching PR. (`.github/bible/bible_queue.py:566-576`)
2. Combines open chunk and verification issues. For the first open session, returns human-needed if held; otherwise follows it and returns unless it merged. (`.github/bible/bible_queue.py:577-585`)
3. If this run has no component issue in any state, returns `not started`; otherwise loads component status and runs the component gate only for `COMPONENT_DONE`. (`.github/bible/bible_queue.py:586-591`)
4. If the gate fails, counts closed chunk issues, starts the next chunk with a session estimate, and returns `session starting`. (`.github/bible/bible_queue.py:592-595`)
5. Loads hold issues; an open human-held issue returns human-needed, while an open hold whose label was removed is closed and the hold list refreshed. (`.github/bible/bible_queue.py:596-602`)
6. Gets the newest hold close time and selects completed verification and revision issues from after that point; also finds all completed verifications. `closed_revise` is collected but is not read later in this method. (`.github/bible/bible_queue.py:603-608`)
7. Reads verification facts only when at least one completed verification exists. A `PASS` with no major corrections and matching nonempty page fingerprint creates the component-to-default PR and returns its review status. (`.github/bible/bible_queue.py:609-614`)
8. After `MAX_VERIFY_ROUNDS` completed verification issues, if the last facts are not a clean matching PASS, creates a human hold and returns its issue number. (`.github/bible/bible_queue.py:615-623`)
9. Finds all completed verifications/revisions, compares their latest close times, and starts a revision chunk when the verification verdict is not PASS or has major corrections and the last revision is older than the verification. (`.github/bible/bible_queue.py:624-633`)
10. Otherwise creates a verification issue on the component branch and returns `verify running`. (`.github/bible/bible_queue.py:634-643`)

**Pseudo-code**

```text
for matching same-repository PR from this tracker:
    return merged, review, or needs-person state
if open chunk/verify issue:
    if held: return needs-person
    result = follow(issue)
    if not merged: return result
if no component issue ever existed: return not started
status = component status
if COMPONENT_DONE: run coverage gate
if gate fails: start next chunk; return session starting
handle open hold (stop for human label, otherwise close removed-label hold)
facts = verification report when a completed verification exists
if clean PASS and pages fingerprint matches: create final PR; return review state
if max verification rounds reached without clean PASS: create human hold; return
if corrections are unapplied: start revision chunk; return session starting
create verification issue
return verify running
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:568` | for | For each PR from the component branch into default | Checks whether it belongs to this tracker and repository. |
| `.github/bible/bible_queue.py:570` | if | PR is from another repo, predates tracker, or body lacks tracker reference | Skips that PR. |
| `.github/bible/bible_queue.py:572` | if | Matching PR has `merged_at` | Returns `merged`. |
| `.github/bible/bible_queue.py:574` | if | Matching PR state is `open` | Returns its review status. |
| `.github/bible/bible_queue.py:578` | if | An open chunk or verification issue exists | Selects its first issue for processing. |
| `.github/bible/bible_queue.py:580` | if | Selected issue is held | Returns human-needed state. |
| `.github/bible/bible_queue.py:583` | if | Following the session did not return a state ending `merged` | Returns that session result. |
| `.github/bible/bible_queue.py:586` | if | No component issue exists in any state | Returns `not started`. |
| `.github/bible/bible_queue.py:590` | if | Status state is `COMPONENT_DONE` | Runs the coverage check. |
| `.github/bible/bible_queue.py:592` | if | Gate did not pass | Starts the next component chunk. |
| `.github/bible/bible_queue.py:598` | if | At least one hold issue is open | Checks whether it still needs human attention. |
| `.github/bible/bible_queue.py:599` | if | Open hold has `bible-needs-human` | Returns human-needed state. |
| `.github/bible/bible_queue.py:609` | conditional expression | Any completed verification exists | Parses the report; otherwise facts are `None`. |
| `.github/bible/bible_queue.py:610` | if | Facts are PASS, have no major corrections, and nonempty fingerprint matches pages | Creates final component PR. |
| `.github/bible/bible_queue.py:615` | if | Verification count reached maximum and facts are not a clean matching PASS | Creates a human hold issue. |
| `.github/bible/bible_queue.py:629` | if | Facts indicate a non-PASS verdict or major corrections | Considers whether revision is needed. |
| `.github/bible/bible_queue.py:630` | if | Last revision close time is older than last verification close time | Starts a revision chunk. |

#### `Queue.follow(analysis, name, issue)`

Source: `.github/bible/bible_queue.py:645-692` <!-- code: b53cde36011d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:582`) |
| Calls | `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.gh.pr_files`, `startswith`, `os.path.basename`, `join`, `status_of`, `as_int`, `self.gh.file`, `self.gh.label`, `self.gh.merge`, `self.gh.unlabel`, `self.gh.close` |
| Purpose | Validates and completes an agent session PR, or holds/retries it when the session is incomplete or out of scope. |

**Steps**

1. Sets branch and session kind from labels, then classifies the session. Waiting returns `session starting`; start-error is held; no-start retries or returns needs-person; running returns the kind's running state. (`.github/bible/bible_queue.py:646-658`)
2. Builds component output path. For chunk PRs allows component LLD, component API LLD, and component ledger paths, excluding `verification-*` basenames; for verification PRs allows only verification files and `citations.tsv` under the component ledger. (`.github/bible/bible_queue.py:659-666`)
3. If any PR file is disallowed, retries or returns needs-person. Otherwise reads status at the PR head SHA. (`.github/bible/bible_queue.py:667-670`)
4. For chunks, `WAITING_ANSWER` adds waiting labels to issue and PR only when the issue lacks the label, then returns waiting-for-answers. Otherwise compares packet count to the branch baseline and checks whether the issue is a revision. (`.github/bible/bible_queue.py:671-679`)
5. A chunk in `STOP` or with no progress is retried/held; a revision not ending at `COMPONENT_DONE` is also retried/held. (`.github/bible/bible_queue.py:680-685`)
6. For verification, a missing report is retried/held. If validation passes, merges the PR, removes the waiting label, closes the issue, and returns `<kind> merged`. (`.github/bible/bible_queue.py:686-692`)

**Pseudo-code**

```text
kind = verify if verification label else chunk
state, pr = session(...)
if waiting/start-error/no-start/running: return corresponding status
find PR files outside this session kind's allowed paths
if bad files: fail_or_retry; return starting or needs-person
status = component status at PR head
if chunk:
    if WAITING_ANSWER: label issue and PR if needed; return waiting for answers
    before = branch packet count
    if STOP or no packet progress: fail_or_retry; return
    if revision and not COMPONENT_DONE: fail_or_retry; return
elif verification report missing: fail_or_retry; return
merge PR; remove waiting label; close issue
return kind + " merged"
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:647` | conditional expression | Issue has `bible-verify` | Sets kind to verify; otherwise chunk. |
| `.github/bible/bible_queue.py:649` | if | Session state is `waiting` | Returns `session starting`. |
| `.github/bible/bible_queue.py:651` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:654` | if | Session state is `no-start` | Retries and returns starting or needs-person. |
| `.github/bible/bible_queue.py:656` | conditional expression | Retry succeeded | Returns `session starting`; otherwise returns needs-person. |
| `.github/bible/bible_queue.py:657` | if | Session state is `running` | Returns `<kind> running`. |
| `.github/bible/bible_queue.py:660` | if | Kind is `chunk` | Applies chunk-specific file allowlist; otherwise verification allowlist. |
| `.github/bible/bible_queue.py:662` | list comprehension | For each changed PR file | Collects paths that violate the chunk allowlist. |
| `.github/bible/bible_queue.py:667` | if | At least one changed file is disallowed | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:669` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:671` | if | Kind is `chunk` | Validates component packet state; otherwise checks verification report. |
| `.github/bible/bible_queue.py:672` | if | Chunk status is `WAITING_ANSWER` | Adds waiting labels when necessary and returns waiting-for-answers. |
| `.github/bible/bible_queue.py:673` | if | Issue lacks `bible-waiting-answer` | Adds the label to issue and PR. |
| `.github/bible/bible_queue.py:680` | if | Status is `STOP` or packet progress is false | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:682` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:683` | if | Issue is a revision and state is not `COMPONENT_DONE` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:685` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:686` | elif | Verification-kind PR has no report at its head SHA | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:688` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |

#### `Queue.check(analysis, name, branch)`

Source: `.github/bible/bible_queue.py:694-711` <!-- code: 4357020a3cd5 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:591`) |
| Calls | `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `strip`, `splitlines` |
| Purpose | Runs the component coverage gate against an unpacked branch tarball and obtains its pages fingerprint. |

**Steps**

1. Locates the analysis skill scripts. If `coverage.py` is absent, logs that the check is skipped/failing and returns `(False, None)`. (`.github/bible/bible_queue.py:696-699`)
2. Creates a temporary work directory, unpacks the branch tarball, and runs isolated `coverage.py` with repository, analysis, depth, component, and report arguments. (`.github/bible/bible_queue.py:700-705`)
3. Logs the final coverage output line or `no output`, runs isolated `status.py --fingerprint --component`, and returns coverage exit success plus stripped fingerprint output or `None`. (`.github/bible/bible_queue.py:706-709`)
4. Removes the temporary directory in `finally`, ignoring errors. (`.github/bible/bible_queue.py:710-711`)

**Pseudo-code**

```text
if coverage.py is missing: log; return False, None
work = temporary directory
try:
    unpack branch tarball into work
    run coverage.py in isolated Python
    log final output line
    run status.py --fingerprint
    return coverage succeeded, fingerprint output or None
finally: remove work directory
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:697` | if | `coverage.py` is not a file | Logs the missing checker and returns failure with no fingerprint. |


#### `Queue.assemble_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:713-753` <!-- code: 73a196189485 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:524`) |
| Calls | `any`, `self.run_issues`, `self.gh.create_issue`, `settings.get`, `self.held`, `self.session`, `issue_text`, `assignment`, `self.gh.close`, `self.hold_start_error`, `self.fail_or_retry`, `get`, `self.gh.linked_prs`, `report_facts`, `self.gh.file`, `self.gh.is_agent_pr`, `self.gh.comment` |
| Purpose | Runs assembly and whole-analysis verification sessions after all selected components merge, then closes the tracker when both finish. |

**Steps**

1. Iterates assembly then verify-all phases, selecting their model, title, and optional issue-text filename. Skips a phase with any completed closed issue. (`.github/bible/bible_queue.py:715-719`)
2. For an open phase issue, finds linked PRs that are merged into the default branch, from this repo, and agent-authored. If found, verify-all reads the report and returns human-needed when absent, non-PASS, or major corrections exist; otherwise closes the issue and advances. (`.github/bible/bible_queue.py:720-732`)
3. If no qualifying merged PR, returns human-needed for a held issue; otherwise classifies the session. Start-error is held; no-start invokes retry; then returns review status when a PR exists or session state. (`.github/bible/bible_queue.py:733-741`)
4. With no open issue, uses `assemble.md` for the assemble phase or builds whole-analysis verification instructions; creates the assigned issue and returns the phase's assigned status. (`.github/bible/bible_queue.py:742-750`)
5. After both phases are skipped/completed, comments on the tracker, closes it, and returns `done`. (`.github/bible/bible_queue.py:751-753`)

**Pseudo-code**

```text
for assemble and verify-all phase:
    if a completed phase issue exists: continue
    if an open issue exists:
        find merged agent PR into default from this repo
        if found:
            if verify-all and report is not clean PASS: return human-needed
            close issue; continue
        if held: return human-needed
        classify session; handle start-error/no-start
        return review status or session state
    load assemble issue text or build verify-all instructions
    create assigned phase issue
    return phase assigned state
comment tracker done; close tracker; return done
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:715` | for | For assemble and verify-all | Processes each phase in order. |
| `.github/bible/bible_queue.py:718` | if | A completed closed issue exists for this phase | Skips to the next phase. |
| `.github/bible/bible_queue.py:721` | if | At least one open issue exists for the phase | Processes its first open issue. |
| `.github/bible/bible_queue.py:725` | if | A qualifying merged agent PR exists | Closes/advances, or validates verify-all results. |
| `.github/bible/bible_queue.py:726` | if | Current phase is `bible-verify-all` | Checks the whole-analysis verification report. |
| `.github/bible/bible_queue.py:728` | if | Report is missing, verdict is not PASS, or major corrections exist | Returns a human-needed verification message. |
| `.github/bible/bible_queue.py:730` | conditional expression | Report facts exist | Includes the verdict; otherwise reports `missing`. |
| `.github/bible/bible_queue.py:733` | if | Open issue is held | Returns the human-needed issue number. |
| `.github/bible/bible_queue.py:736` | if | Session state is `start-error` | Holds the issue and returns human-needed. |
| `.github/bible/bible_queue.py:739` | if | Session state is `no-start` | Invokes retry logic. |
| `.github/bible/bible_queue.py:741` | conditional expression | PR exists | Returns PR review instruction; otherwise returns session state. |
| `.github/bible/bible_queue.py:742` | if | Phase has a `text` filename | Loads issue title/body from that ledger file; otherwise uses verify-all instructions. |

#### `Queue.render(tracker, settings, rows)`

Source: `.github/bible/bible_queue.py:755-765` <!-- code: 651906b39ffd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:501`, `.github/bible/bible_queue.py:525`), `Queue.plan_phase` (`.github/bible/bible_queue.py:538`, `.github/bible/bible_queue.py:541`, `.github/bible/bible_queue.py:545`) |
| Calls | `items`, `now`, `isoformat`, `json.dumps`, `join`, `self.gh.set_body`, `split`, `self.log` |
| Purpose | Renders tracker status rows and settings, updates the issue body when its non-time content differs, and logs each row. |

**Steps**

1. Builds introductory text, table headings, and one row per component/state pair. (`.github/bible/bible_queue.py:756-758`)
2. Adds a minute-resolution UTC timestamp and hidden JSON settings block, then joins lines into the body. (`.github/bible/bible_queue.py:759-761`)
3. Updates the tracker body only when the text preceding `Updated` differs from its current body prefix. (`.github/bible/bible_queue.py:762-763`)
4. Logs every row as a padded key and state. (`.github/bible/bible_queue.py:764-765`)

**Pseudo-code**

```text
lines = introduction + table header + rows
append updated timestamp and hidden bible-settings JSON
body = join lines with newline
if body prefix before "Updated" differs from existing body prefix:
    set tracker body
for each row: log padded key and state
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:762` | if | Text before `Updated` differs | Replaces the tracker body. |
| `.github/bible/bible_queue.py:764` | for | For each `(key, value)` row | Logs that row. |

#### `Queue.delta(changed, settings_analysis="codebase-analysis")`

Source: `.github/bible/bible_queue.py:768-794` <!-- code: 173a0090e878 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:838`) |
| Calls | `self.gh.default_branch`, `json_file`, `self.log`, `self.gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `components.component_map`, `sorted`, `startswith`, `components.assign`, `self.gh.issues`, `self.gh.create_issue`, `assignment`, `comp_label`, `len` |
| Purpose | Creates one update issue for each analysis component affected by changed files when an assembled baseline exists. |

**Steps**

1. Reads/stores the default branch, loads `components.json`, and checks that `ledger/baseline.json` exists. If either analysis catalog or baseline is falsey, logs and returns. (`.github/bible/bible_queue.py:769-774`)
2. Adds toolkit scripts to `sys.path`, imports `components`, builds component rows, and maps changed paths excluding analysis-folder and `.github/` paths to sorted touched component names. (`.github/bible/bible_queue.py:775-779`)
3. For each touched component, selects changed files assigned to it. If a matching open delta issue already exists, logs and skips creating another. (`.github/bible/bible_queue.py:780-784`)
4. Otherwise creates a labeled delta issue with component/base/attempt context, changed file names (up to 20), update instructions, and an assignment; then logs the component and number of changed files. (`.github/bible/bible_queue.py:785-794`)

**Pseudo-code**

```text
default = gh.default_branch()
catalog = json_file(components.json)
if catalog or baseline is missing: log; return
load components toolkit
touched = sorted mapped components for changed paths outside analysis and .github
for each touched component:
    files = changed paths assigned to it
    if matching delta issue is open: log; continue
    create assigned delta issue with changed files and update instructions
    log file count
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:772` | if | Catalog is falsey or baseline file is missing/falsey | Logs that no assembled analysis exists and returns. |
| `.github/bible/bible_queue.py:780` | for | For each touched component | Selects its changed files and update issue state. |
| `.github/bible/bible_queue.py:782` | if | A matching delta issue is already open | Logs and skips creating a duplicate issue. |

## Functions and methods

### `main()`

Source: `.github/bible/bible_queue.py:797-840` <!-- code: f407f91f47e7 -->

| | |
| --- | --- |
| Kind | module entry point |
| Called by | Module guard (`.github/bible/bible_queue.py:843-844`) |
| Calls | `argparse.ArgumentParser`, `add_subparsers`, `add_parser`, `add_argument`, `parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `ensure_labels`, `issues`, `create_issue`, `print`, `strip`, `split`, `any`, `Queue.reconcile`, `open`, `Queue.delta`, `str` |
| Purpose | Parses `start`, `reconcile`, and `delta` commands and dispatches to the queue workflow. |

**Steps**

1. Builds the command parser from the module docstring's first line; defines `start` options (`--components`, `--model`, required `--verify-model`, concurrency, analysis, depth), `reconcile`, and `delta` (`--changed-file` required, analysis), then parses arguments. (`.github/bible/bible_queue.py:798-811`)
2. Reads `GITHUB_REPOSITORY` and `GH_TOKEN`; raises `SystemExit` if either is missing. Creates `GitHub` and `Queue` clients. (`.github/bible/bible_queue.py:813-817`)
3. For `start`, requires a nonempty verification model different from the normal model; parses component names and requires either `all` or names matching `NAME`. (`.github/bible/bible_queue.py:819-824`)
4. Ensures labels and exits if a tracker issue is already open. Builds settings from arguments, creates a labeled tracker issue containing the hidden settings JSON, and prints its number and queue start guidance. (`.github/bible/bible_queue.py:825-832`)
5. For `reconcile`, calls `queue.reconcile`. Otherwise reads nonempty, stripped changed-file lines from the specified file and calls `queue.delta(changed, args.analysis)`. (`.github/bible/bible_queue.py:833-838`)
6. Converts `RuntimeError` from command handling to `SystemExit(str(err))`. (`.github/bible/bible_queue.py:839-840`)

**Pseudo-code**

```text
parse required subcommand and its arguments
repo, token = GITHUB_REPOSITORY, GH_TOKEN
if either is missing: exit
gh = GitHub(repo, token); queue = Queue(gh)
try:
    if start:
        require distinct nonempty verify model
        parse and validate component selection
        ensure labels; exit if a tracker is already open
        create tracker with settings; print issue number
    elif reconcile: queue.reconcile()
    else:
        read nonempty changed paths from file
        queue.delta(changed, analysis)
on RuntimeError: exit with its text
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:814` | if | Repository or token environment value is missing | Exits with a required-environment message. |
| `.github/bible/bible_queue.py:815` | raise | Either required environment value is missing | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:819` | if | Command is `start` | Validates and starts an analysis run. |
| `.github/bible/bible_queue.py:820` | if | Verification model is empty or equals normal model | Exits with the distinct-model requirement. |
| `.github/bible/bible_queue.py:821` | raise | Verification model validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:823` | if | No names or any name other than `all` fails `NAME` | Exits with component-selection guidance. |
| `.github/bible/bible_queue.py:824` | raise | Component selection fails validation | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:826` | if | An open tracker issue exists | Exits rather than opening another run. |
| `.github/bible/bible_queue.py:827` | raise | An open tracker exists | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:833` | elif | Command is `reconcile` | Calls `queue.reconcile`; other command is handled by the `else`. |
| `.github/bible/bible_queue.py:839` | except | Command handling raises `RuntimeError` | Enters error conversion. |
| `.github/bible/bible_queue.py:840` | raise | A `RuntimeError` was caught | Raises `SystemExit` with the error text. |

### `now()`

Source: `.github/bible/bible_queue.py:307-309` <!-- code: 9fb56903ebfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `age` (`.github/bible/bible_queue.py:313`) |
| Calls | `os.environ.get`, `datetime.datetime.fromisoformat`, `datetime.datetime.now`, `replace` |
| Purpose | Returns the configured test time or the current UTC time. |

**Steps**

1. Reads `BIBLE_NOW`. (`.github/bible/bible_queue.py:308`)
2. If set, replaces `Z` with `+00:00` and parses the ISO timestamp; otherwise returns the current timezone-aware UTC datetime. (`.github/bible/bible_queue.py:309`)

**Pseudo-code**

```text
stamp = BIBLE_NOW
if stamp: parse ISO stamp after replacing Z with +00:00
else: return current UTC time
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:309` | conditional expression | `stamp` is truthy | Parses the configured time; otherwise obtains current UTC time. |

### `age(stamp)`

Source: `.github/bible/bible_queue.py:312-313` <!-- code: f2f8bb65e56f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `now`, `datetime.datetime.fromisoformat`, `replace`, `total_seconds` |
| Purpose | Returns elapsed seconds between `stamp` and `now()`. |

**Steps**

1. Replaces `Z` in `stamp` with `+00:00`, parses it as an ISO datetime, subtracts it from `now()`, and returns `total_seconds()`. (`.github/bible/bible_queue.py:313`)

**Pseudo-code**

```text
return (now() - parse ISO stamp after replacing Z with +00:00).total_seconds()
```

### `settings_of(tracker)`

Source: `.github/bible/bible_queue.py:316-321` <!-- code: a2abeca733b5 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group` |
| Purpose | Parses the JSON settings marker from a tracker's body, returning `None` when absent or invalid. |

**Steps**

1. Searches the tracker body, defaulting a missing or falsey body to an empty string. (`.github/bible/bible_queue.py:317`)
2. Returns parsed JSON from capture group 1 when a marker matched, or `None` when no match was found. (`.github/bible/bible_queue.py:318-319`)
3. Returns `None` if JSON parsing raises `ValueError`. (`.github/bible/bible_queue.py:320-321`)

**Pseudo-code**

```text
match = SETTINGS search in tracker.body or ""
try:
    return parse match group 1 if matched, otherwise None
on ValueError: return None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:319` | conditional expression | A settings marker matched | Parses its first group; otherwise returns `None`. |
| `.github/bible/bible_queue.py:320` | except | JSON parsing raises `ValueError` | Returns `None`. |

### `labels_of(item)`

Source: `.github/bible/bible_queue.py:324-325` <!-- code: 7a809f2b23af -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `item.get`, `isinstance` |
| Purpose | Returns a set of label names from strings or label objects. |

**Steps**

1. Reads `labels`, defaulting to an empty list; for each element, uses its `name` when it is a dictionary and otherwise keeps the element itself. (`.github/bible/bible_queue.py:325`)

**Pseudo-code**

```text
return {label["name"] if label is a dict else label
        for label in item.labels or []}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:325` | conditional expression | A label item is a dict | Uses `item["name"]`; otherwise preserves the item value. |

### `comp_label(name)`

Source: `.github/bible/bible_queue.py:328-329` <!-- code: 5ead08c5004d -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Prefixes a component name with `bible/`. |

**Steps**

1. Returns the string `bible/` followed by `name`. (`.github/bible/bible_queue.py:329`)

**Pseudo-code**

```text
return "bible/" + name
```

### `issue_text(gh, path, ref, fallback_title)`

Source: `.github/bible/bible_queue.py:332-338` <!-- code: 0533b3261be5 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `gh.file`, `splitlines`, `startswith`, `strip`, `join`, `len` |
| Purpose | Reads a title/body pair from a ledger issue file, with a fallback title when no header exists. |

**Steps**

1. Reads the file through `gh.file`, converting a falsey result to `""`, then splits it into lines. (`.github/bible/bible_queue.py:334-335`)
2. If the first line starts with `Title:`, returns its stripped suffix as the title and the stripped remaining lines joined by newlines as the body. (`.github/bible/bible_queue.py:336-337`)
3. Otherwise returns `fallback_title` and the stripped full text. (`.github/bible/bible_queue.py:338`)

**Pseudo-code**

```text
text = gh.file(path, ref) or ""
lines = split text into lines
if first line starts with "Title:":
    return stripped header suffix, stripped remaining lines joined by newline
return fallback_title, stripped text
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:336` | if | `lines` is nonempty and the first line starts with `Title:` | Returns header title and remaining body; otherwise returns fallback title and full text. |

### `assignment(gh, base, model)`

Source: `.github/bible/bible_queue.py:341-345` <!-- code: da5ca422ae7f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Builds the target repository and base-branch assignment, optionally including a model. |

**Steps**

1. Initializes the result with `target_repo: gh.repo` and `base_branch: base`. (`.github/bible/bible_queue.py:342`)
2. Adds `model` only when truthy, then returns the result. (`.github/bible/bible_queue.py:343-345`)

**Pseudo-code**

```text
out = {target_repo: gh.repo, base_branch: base}
if model: out.model = model
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:343` | if | `model` is truthy | Adds `model` to the assignment. |

### `json_file(gh, path, ref)`

Source: `.github/bible/bible_queue.py:348-353` <!-- code: 37acfbecddfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `status_of` (`.github/bible/bible_queue.py:390`), queue functions in later source packets. |
| Calls | `gh.file`, `json.loads` |
| Purpose | Reads a file and parses JSON, returning `None` for missing or invalid content. |

**Steps**

1. Reads the file using `gh.file`. (`.github/bible/bible_queue.py:349`)
2. Returns parsed JSON for truthy text, or `None` when the text is falsey. (`.github/bible/bible_queue.py:350-351`)
3. Returns `None` if parsing raises `ValueError`. (`.github/bible/bible_queue.py:352-353`)

**Pseudo-code**

```text
text = gh.file(path, ref)
try:
    return parse JSON if text, otherwise None
on ValueError: return None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:351` | conditional expression | `text` is truthy | Parses JSON; otherwise returns `None`. |
| `.github/bible/bible_queue.py:352` | except | JSON parsing raises `ValueError` | Returns `None`. |

### `section(text, title)`

Source: `.github/bible/bible_queue.py:356-362` <!-- code: 55167fd6e3c2 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `report_facts` (`.github/bible/bible_queue.py:375`), queue functions in later source packets. |
| Calls | `re.search`, `re.escape`, `match.end`, `nxt.start` |
| Purpose | Returns a Markdown level-two section's text, or an empty string if its heading is absent. |

**Steps**

1. Searches for a line matching exactly a level-two heading with the escaped `title`. (`.github/bible/bible_queue.py:357`)
2. Returns `""` if no heading matches. (`.github/bible/bible_queue.py:358-359`)
3. Slices text after the matched heading through the next level-two heading, or through end of text when there is no next heading. (`.github/bible/bible_queue.py:360-362`)

**Pseudo-code**

```text
match = search exact "## title" heading
if no match: return ""
rest = text after heading
find next level-two heading
return before next heading if found, otherwise all rest
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:358` | if | No heading matched | Returns an empty string. |
| `.github/bible/bible_queue.py:362` | conditional expression | A next level-two heading matched | Returns the section before it; otherwise returns the remaining text. |

### `report_facts(text)`

Source: `.github/bible/bible_queue.py:365-378` <!-- code: a367c151c5b0 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `re.sub`, `re.findall`, `len`, `sum`, `splitlines`, `startswith`, `re.search`, `section`, `lstrip`, `upper`, `printed.group` |
| Purpose | Extracts a verification verdict, major-correction count, and optional analysis fingerprint. |

**Steps**

1. Returns `None` for falsey `text`. (`.github/bible/bible_queue.py:368-369`)
2. Removes HTML comments and fenced code blocks, then finds visible `Verdict` values and rows. (`.github/bible/bible_queue.py:370-372`)
3. Returns `("UNREADABLE", 0, None)` unless exactly one accepted verdict and exactly one verdict row were found. (`.github/bible/bible_queue.py:373-374`)
4. Counts lines in the `Corrections` section that begin with `|` and contain a `major` cell. (`.github/bible/bible_queue.py:375-376`)
5. Searches for a 16-character lowercase hexadecimal fingerprint and returns the uppercased verdict, count, and captured fingerprint or `None`. (`.github/bible/bible_queue.py:377-378`)

**Pseudo-code**

```text
if text is falsey: return None
visible = remove comments and fenced code blocks
find accepted verdict values and verdict rows
if either count is not exactly one: return ("UNREADABLE", 0, None)
majors = count major rows in Corrections section
fingerprint = optional 16-hex Analysis fingerprint
return verdict.upper(), majors, fingerprint or None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:368` | if | `text` is falsey | Returns `None`. |
| `.github/bible/bible_queue.py:373` | if | Verdict or verdict-row count is not exactly one | Returns `("UNREADABLE", 0, None)`. |
| `.github/bible/bible_queue.py:378` | conditional expression | Fingerprint regex matched | Returns its group 1; otherwise returns `None` in that tuple position. |

### `as_int(value)`

Source: `.github/bible/bible_queue.py:381-385` <!-- code: 8081107d37e4 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `int` |
| Purpose | Converts a value to an integer, returning zero for `TypeError` or `ValueError`. |

**Steps**

1. Returns `int(value)` when conversion succeeds. (`.github/bible/bible_queue.py:382-383`)
2. Returns `0` when conversion raises `TypeError` or `ValueError`. (`.github/bible/bible_queue.py:384-385`)

**Pseudo-code**

```text
try: return int(value)
on TypeError or ValueError: return 0
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:384` | except | `int(value)` raises `TypeError` or `ValueError` | Returns zero. |

### `status_of(gh, path, ref)`

Source: `.github/bible/bible_queue.py:388-391` <!-- code: ad9adb38e0f7 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `json_file`, `isinstance` |
| Purpose | Returns parsed component status only when the loaded JSON is a dictionary. |

**Steps**

1. Loads `path` at `ref` with `json_file`. (`.github/bible/bible_queue.py:390`)
2. Returns the loaded data if it is a dictionary; otherwise returns `{}`. (`.github/bible/bible_queue.py:391`)

**Pseudo-code**

```text
data = json_file(gh, path, ref)
return data if data is a dict, otherwise {}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:391` | conditional expression | `data` is a dictionary | Returns `data`; otherwise returns `{}`. |

## Module-level code

The module imports Python standard-library utilities and initializes queue labels, environment-derived agent settings, regexes, and timing/verification constants. (`.github/bible/bible_queue.py:42-83`)

It declares the `GitHub` API client, helper functions, and `Queue` coordinator; the CLI `main` parses arguments, and the module guard calls it when executed as a script. (`.github/bible/bible_queue.py:88-302`, `.github/bible/bible_queue.py:307-391`, `.github/bible/bible_queue.py:396-794`, `.github/bible/bible_queue.py:797-844`)

## Surprises

`tarball` filters archive members to regular files and directories and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:246-259`)

The `Queue.session` docstring lists four result states, but the code also returns `start-error` when `GitHub.start_error` is truthy. (`.github/bible/bible_queue.py:413-418`)

`Queue.component` builds `closed_revise` after a human hold but does not use it later in the method; it separately builds and uses `all_revise`. (`.github/bible/bible_queue.py:604-608`, `.github/bible/bible_queue.py:624-630`)
