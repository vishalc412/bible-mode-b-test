---
id: lld/bible-mode-b/bible_queue
kind: module
component: bible-mode-b
source: .github/bible/bible_queue.py
summary: Coordinates Mode B issue workflows through GitHub REST and GraphQL
reads: [file:--changed-file list, config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
writes: [file:destination tree passed to GitHub.tarball]
calls: [external:GitHub API, external:Analysis toolkit]
uses: [symbol:GitHub, symbol:Queue]
config: [config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
exposes: []
---

# bible_queue

Source file: `.github/bible/bible_queue.py`

| | |
| --- | --- |
| Component | `bible-mode-b` (its design page is `README.md` in this folder) |
| Lines | 867 |
| Role | Runs the Mode B analysis queue and its GitHub API client. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, subprocess, and filesystem modules used by the API client, queue, and CLI. (`.github/bible/bible_queue.py:42-55`) |
| Module-level state | `COPILOT`, `AGENT_LOGINS`, `AGENT_APP`, `START_ERROR`, `FINAL_STATES`, `NO_PR_AFTER`, `IDLE_AFTER`, `MAX_VERIFY_ROUNDS`, `SETTINGS`, `ATTEMPT`, `NAME`, and `LABELS` are initialized at import; environment-backed values include `BIBLE_AGENT_LOGINS` and `BIBLE_AGENT_APP`. (`.github/bible/bible_queue.py:59-83`) |

## Summary

`main` exposes the `start`, `reconcile`, and `delta` CLI commands. It constructs `Queue` and `GitHub`; `Queue` coordinates tracker/session state and delegates repository operations to `GitHub`, whose methods build REST requests and a GraphQL ready-for-review mutation. `Queue.delta` also imports component-membership helpers from the analysis toolkit. (`.github/bible/bible_queue.py:820-863`, `.github/bible/bible_queue.py:396-817`, `.github/bible/bible_queue.py:88-302`, `.github/bible/bible_queue.py:798-802`)

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
| `GitHub.me` | method | 160-164 | [card](#githubme) |
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
| `GitHub.is_agent_pr` | method | 214-219 | [card](#githubis_agent_prpr) |
| `GitHub.start_error` | method | 221-230 | [card](#githubstart_errorissue) |
| `GitHub.assigned_at` | method | 217-220 | [card](#githubassigned_atissue) |
| `GitHub.pr_files` | method | 237-250 | [card](#githubpr_filesnumber) |
| `GitHub.commit_time` | method | 231-232 | [card](#githubcommit_timesha) |
| `GitHub.tarball` | method | 255-288 | [card](#githubtarballref-dest) |
| `GitHub.label` | method | 261-263 | [card](#githublabelnumber-name) |
| `GitHub.unlabel` | method | 265-266 | [card](#githubunlabelnumber-name) |
| `GitHub.comment` | method | 268-269 | [card](#githubcommentnumber-text) |
| `GitHub.close` | method | 271-272 | [card](#githubclosenumber-reason-completed) |
| `GitHub.set_body` | method | 274-275 | [card](#githubset_bodynumber-body) |
| `GitHub.unassign` | method | 277-278 | [card](#githubunassignnumber) |
| `GitHub.assign` | method | 280-281 | [card](#githubassignnumber-assign) |
| `GitHub.ready` | method | 283-291 | [card](#githubreadypr) |
| `GitHub.merge` | method | 322-326 | [card](#githubmergepr-title) |
| `GitHub.close_pr` | method | 298-299 | [card](#githubclose_prnumber) |
| `GitHub.create_pr` | method | 301-302 | [card](#githubcreate_prhead-base-title-body) |
| `now` | function | 307-309 | [card](#now) |
| `age` | function | 312-313 | [card](#age) |
| `settings_of` | function | 353-373 | [card](#settings_of) |
| `labels_of` | function | 324-325 | [card](#labels_of) |
| `comp_label` | function | 328-329 | [card](#comp_label) |
| `issue_text` | function | 332-338 | [card](#issue_textgh-path-ref-fallback_title) |
| `assignment` | function | 341-345 | [card](#assignmentgh-base-model) |
| `json_file` | function | 348-353 | [card](#json_filegh-path-ref) |
| `section` | function | 356-362 | [card](#sectiontext-title) |
| `report_facts` | function | 365-378 | [card](#report_factstext) |
| `as_int` | function | 381-385 | [card](#as_intvalue) |
| `status_of` | function | 388-391 | [card](#status_ofgh-path-ref) |
| `Queue` | class | 396-798 | [class](#queue) |
| `Queue.__init__` | method | 397-399 | [card](#queue__init__gh-log-print) |
| `Queue.run_issues` | method | 401-402 | [card](#queue_run_issueslabels-state-open) |
| `Queue.agent_pr` | method | 404-410 | [card](#queue_agent_prissue-base) |
| `Queue.session` | method | 413-429 | [card](#queue_sessionissue-base-analysis-comp-none) |
| `Queue.held` | method | 483-516 | [card](#queue_heldissue) |
| `Queue.model_for` | method | 452-454 | [card](#queue_model_forissue) |
| `Queue.hold_start_error` | method | 456-462 | [card](#queue_hold_start_errorissue) |
| `Queue.fail_or_retry` | method | 464-483 | [card](#queue_fail_or_retryissue-pr-why) |
| `Queue.reconcile` | method | 486-496 | [card](#queue_reconcile) |
| `Queue.run` | method | 564-608 | [card](#queue_runtracker-settings) |
| `Queue.plan_phase` | method | 536-558 | [card](#queue_plan_phasetracker-settings-analysis) |
| `Queue.start_chunk` | method | 560-572 | [card](#queue_start_chunkanalysis-name-fresh-false-note) |
| `Queue.component` | method | 648-751 | [card](#queue_componentanalysis-name) |
| `Queue.follow` | method | 753-810 | [card](#queue_followanalysis-name-issue) |
| `Queue.check` | method | 812-837 | [card](#queue_checkanalysis-name-branch) |
| `Queue.assemble_phase` | method | 839-907 | [card](#queue_assemble_phasetracker-settings-analysis) |
| `Queue.revise_all_step` | method | 909-979 | [card](#queue_revise_all_steptracker-analysis) |
| `Queue.continue_if_unfinished` | method | 981-1019 | [card](#queue_continue_if_unfinishedissue-pr-kind-analysis) |
| `Queue.render` | method | 778-788 | [card](#queue_rendertracker-settings-rows) |
| `Queue.delta` | method | 791-817 | [card](#queue_deltachanged-settings_analysiscodebase-analysis) |
| `main` | function | 820-863 | [card](#main) |

## Call graph

Edges are derived by matching calls to same-file function names; matching names alone can confuse methods with external calls, so consult the cited cards for the receiver.

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
  subprocessrun["subprocess.run"]
  planphase["Queue.plan_phase"]
  startchunk["Queue.start_chunk"]
  component["Queue.component"]
  follow["Queue.follow"]
  check["Queue.check"]
  assemblephase["Queue.assemble_phase"]
  reviseall["Queue.revise_all_step"]
  continueunfinished["Queue.continue_if_unfinished"]
  render["Queue.render"]
  delta["Queue.delta"]
  me["GitHub.me"]
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
  reportfacts -->|"section"| section
  statusof -->|"json_file"| jsonfile
  agentpr -->|"linked_prs"| linked
  agentpr -->|"is_agent_pr"| isagent
  session -->|"agent_pr"| agentpr
  session -->|"age"| age
  session -->|"labels_of"| labelsof
  held -->|"labels_of"| labelsof
  held -->|"assignment"| assignment
  held -->|"model_for"| modelfor
  held -->|"close (GitHub issue)"| close
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
  component -->|"as_int"| asint
  follow -->|"session"| session
  follow -->|"fail_or_retry"| failorretry
  follow -->|"labels_of"| labelsof
  follow -->|"status_of"| statusof
  follow -->|"as_int"| asint
  check -->|"tarball"| tarball
  check -->|"subprocess.run"| subprocessrun
  assemblephase -->|"run_issues"| runissues
  assemblephase -->|"session"| session
  assemblephase -->|"continue_if_unfinished"| continueunfinished
  assemblephase -->|"label"| label
  assemblephase -->|"labels_of"| labelsof
  assemblephase -->|"revise_all_step"| reviseall
  held -->|"label"| label
  held -->|"timeline"| timeline
  continueunfinished -->|"age"| age
  continueunfinished -->|"comment"| comment
  continueunfinished -->|"label"| label
  continueunfinished -->|"labels_of"| labelsof
  continueunfinished -->|"me"| me
  continueunfinished -->|"pr_files"| prfiles
  continueunfinished -->|"timeline"| timeline
  main -->|"settings_of"| settingsof
  me -->|"call"| call
  prfiles -->|"as_int"| asint
  prfiles -->|"call"| call
  reviseall -->|"assignment"| assignment
  reviseall -->|"close"| close
  reviseall -->|"continue_if_unfinished"| continueunfinished
  reviseall -->|"create_issue"| createissue
  reviseall -->|"fail_or_retry"| failorretry
  reviseall -->|"held"| held
  reviseall -->|"hold_start_error"| holdstarterror
  reviseall -->|"is_agent_pr"| isagent
  reviseall -->|"labels_of"| labelsof
  reviseall -->|"linked_prs"| linked
  reviseall -->|"pr_files"| prfiles
  reviseall -->|"run_issues"| runissues
  reviseall -->|"session"| session
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

Source: `.github/bible/bible_queue.py:96-99` <!-- code: b511658beb68 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1080`) |
| Calls | `os.environ.get`, `rstrip` |
| Purpose | Stores API credentials and a slash-trimmed API base URL, then initializes the label cache. |

**Steps**

1. Assigns `repo` and `token` to the instance. (`.github/bible/bible_queue.py:97`)
2. Selects `api`, then `GITHUB_API_URL`, then `https://api.github.com`, and removes trailing `/` characters. (`.github/bible/bible_queue.py:98`)
3. Initializes `known_labels` to `None`. (`.github/bible/bible_queue.py:99`)

**Pseudo-code**

```text
self.repo, self.token = repo, token
self.api = (api or GITHUB_API_URL or "https://api.github.com").rstrip("/")
self.known_labels = None
```

#### `GitHub.request(method, url, body=None, timeout=60)`

Source: `.github/bible/bible_queue.py:101-110` <!-- code: 1f8902892005 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.call` (`.github/bible/bible_queue.py:115`), `GitHub.tarball` (`.github/bible/bible_queue.py:261`), `GitHub.ready` (`.github/bible/bible_queue.py:317`) |
| Calls | `json.dumps`, `encode`, `urllib.request.Request`, `req.add_header`, `urllib.request.urlopen` |
| Purpose | Builds and opens an HTTP request with GitHub headers and an optional JSON body. |

**Steps**

1. Serializes a non-`None` body as encoded JSON; otherwise leaves request data unset. (`.github/bible/bible_queue.py:102`)
2. Creates a request using the supplied URL, method, and body bytes, and adds GitHub's JSON accept and API-version headers. (`.github/bible/bible_queue.py:103-105`)
3. Adds a bearer authorization header only when `token` is truthy, and adds JSON content type only when a body was serialized. (`.github/bible/bible_queue.py:106-109`)
4. Returns `urlopen`'s response using the supplied timeout. (`.github/bible/bible_queue.py:110`)

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
| `.github/bible/bible_queue.py:102` | conditional expression | `body is not None` | JSON is encoded; otherwise `data` is `None`. |
| `.github/bible/bible_queue.py:106` | if | `self.token` is truthy | Adds the bearer authorization header. |
| `.github/bible/bible_queue.py:108` | if | `data is not None` | Adds the JSON content-type header. |

#### `GitHub.call(method, path, body=None, ok404=False)`

Source: `.github/bible/bible_queue.py:112-124` <!-- code: 753c5f1a3922 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.paged` (`.github/bible/bible_queue.py:130`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:144`), `GitHub.create_issue` (`.github/bible/bible_queue.py:158`), `GitHub.default_branch` (`.github/bible/bible_queue.py:167`), `GitHub.branch_sha` (`.github/bible/bible_queue.py:170`), `GitHub.create_branch` (`.github/bible/bible_queue.py:174`), `GitHub.reset_branch` (`.github/bible/bible_queue.py:177`), `GitHub.file` (`.github/bible/bible_queue.py:180`), `GitHub.linked_prs` (`.github/bible/bible_queue.py:200`), `GitHub.commit_time` (`.github/bible/bible_queue.py:253`), `GitHub.label` (`.github/bible/bible_queue.py:292`), `GitHub.unlabel` (`.github/bible/bible_queue.py:295`), `GitHub.comment` (`.github/bible/bible_queue.py:298`), `GitHub.close` (`.github/bible/bible_queue.py:301`), `GitHub.set_body` (`.github/bible/bible_queue.py:304`), `GitHub.unassign` (`.github/bible/bible_queue.py:307`), `GitHub.assign` (`.github/bible/bible_queue.py:310`), `GitHub.merge` (`.github/bible/bible_queue.py:296`), `GitHub.close_pr` (`.github/bible/bible_queue.py:329`), `GitHub.create_pr` (`.github/bible/bible_queue.py:332`) |
| Calls | `path.startswith`, `GitHub.request`, response `read`, `json.loads`, `RuntimeError` |
| Purpose | Sends a REST request and converts response data and common request failures to Python values or a `RuntimeError`. |

**Steps**

1. Uses an absolute `path` beginning with `http` as-is; otherwise joins the API base, `/repos/`, repository, and path. (`.github/bible/bible_queue.py:113`)
2. Opens the request and reads its response bytes. (`.github/bible/bible_queue.py:114-116`)
3. On HTTP 404 with `ok404`, returns `None`; otherwise reads at most 300 decoded characters and raises a method/path/status/detail `RuntimeError`. (`.github/bible/bible_queue.py:117-121`)
4. Converts `URLError`, `TimeoutError`, and `OSError` to a `RuntimeError` containing the method, query-stripped path, and error. (`.github/bible/bible_queue.py:122-123`)
5. Decodes a nonempty payload as JSON; returns `{}` for an empty payload. (`.github/bible/bible_queue.py:124`)

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
| `.github/bible/bible_queue.py:113` | conditional expression | `path.startswith("http")` | Uses `path`; otherwise constructs a repository API URL. |
| `.github/bible/bible_queue.py:117` | except | Request raises `urllib.error.HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:118` | if | Status is 404 and `ok404` is true | Returns `None`. |
| `.github/bible/bible_queue.py:121` | raise | Other HTTP errors | Raises `RuntimeError` with method, path, status, and detail. |
| `.github/bible/bible_queue.py:122` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Enters network error handling. |
| `.github/bible/bible_queue.py:123` | raise | A listed network error occurred | Raises `RuntimeError` with method, path, and error. |
| `.github/bible/bible_queue.py:124` | conditional expression | Payload is nonempty | Decodes JSON; otherwise returns `{}`. |

#### `GitHub.paged(path)`

Source: `.github/bible/bible_queue.py:126-134` <!-- code: 1bb6c1899527 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.issues` (`.github/bible/bible_queue.py:138`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:142`), `GitHub.prs` (`.github/bible/bible_queue.py:187`), `GitHub.timeline` (`.github/bible/bible_queue.py:190`), `GitHub.branch_prs` (`.github/bible/bible_queue.py:206`), `GitHub.pr_files` (`.github/bible/bible_queue.py:225`) |
| Calls | `GitHub.call`, `len` |
| Purpose | Fetches successive pages of up to 100 results and returns their concatenation. |

**Steps**

1. Starts with an empty result and page number 1. (`.github/bible/bible_queue.py:127`)
2. Chooses `&` if `path` already contains `?`, otherwise `?`, then requests `per_page=100` and the current page with GET. (`.github/bible/bible_queue.py:128-130`)
3. Appends each batch; returns the accumulated list when a batch has fewer than 100 entries, otherwise increments the page and repeats. (`.github/bible/bible_queue.py:131-134`)

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
| `.github/bible/bible_queue.py:128` | while | Always | Repeats page requests until a short batch is returned. |
| `.github/bible/bible_queue.py:129` | conditional expression | `path` contains `?` | Chooses `&`; otherwise chooses `?`. |
| `.github/bible/bible_queue.py:132` | if | Batch length is less than 100 | Returns all accumulated entries; otherwise proceeds to the next page. |

#### `GitHub.issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:136-138` <!-- code: b3f969457f25 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run_issues` (`.github/bible/bible_queue.py:454`), `Queue.reconcile` (`.github/bible/bible_queue.py:545`), `Queue.delta` (`.github/bible/bible_queue.py:1029`), `main` (`.github/bible/bible_queue.py:1090`) |
| Calls | `urllib.parse.quote`, `join`, `GitHub.paged` |
| Purpose | Lists issues for encoded labels and a state, excluding pull requests. |

**Steps**

1. Joins labels with commas and URL-quotes the result. (`.github/bible/bible_queue.py:137`)
2. Pages `/issues` with the requested state and labels query, then keeps only objects without a `pull_request` key. (`.github/bible/bible_queue.py:138`)

**Pseudo-code**

```text
q = URL-quote(comma-joined labels)
return paged issues for state and q, excluding pull request objects
```

#### `GitHub.ensure_label(name, why="Codebase analysis run")`

Source: `.github/bible/bible_queue.py:140-145` <!-- code: c80387a5616e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.ensure_labels` (`.github/bible/bible_queue.py:149`), `GitHub.create_issue` (`.github/bible/bible_queue.py:153`), `GitHub.label` (`.github/bible/bible_queue.py:291`) |
| Calls | `GitHub.paged`, `GitHub.call`, `known_labels.add` |
| Purpose | Loads the known-label set on first use and creates a requested label if it is absent. |

**Steps**

1. If `known_labels` is `None`, pages `/labels` and caches their names. (`.github/bible/bible_queue.py:141-142`)
2. If `name` is missing, posts a label with the fixed color `5319e7` and `why` truncated to 100 characters, then adds the name to the cache. (`.github/bible/bible_queue.py:143-145`)

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
| `.github/bible/bible_queue.py:141` | if | `known_labels` is `None` | Fetches and caches current label names. |
| `.github/bible/bible_queue.py:143` | if | `name` is not in the cache | Creates the label and adds its name to the cache. |

#### `GitHub.ensure_labels()`

Source: `.github/bible/bible_queue.py:147-149` <!-- code: 3233fadcc4c0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1089`) |
| Calls | `LABELS.items`, `GitHub.ensure_label` |
| Purpose | Ensures each label defined in the module's `LABELS` mapping exists. |

**Steps**

1. Iterates each `(name, why)` pair in `LABELS` and invokes `ensure_label`. (`.github/bible/bible_queue.py:148-149`)

**Pseudo-code**

```text
for name, why in LABELS:
    ensure_label(name, why)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:148` | for | For each `(name, why)` in `LABELS.items()` | Calls `ensure_label` once for that pair. |

#### `GitHub.create_issue(title, body, labels, assign=None)`

Source: `.github/bible/bible_queue.py:151-158` <!-- code: c0db4afc186c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:538`), `Queue.plan_phase` (`.github/bible/bible_queue.py:610`), `Queue.start_chunk` (`.github/bible/bible_queue.py:636`), `Queue.component` (`.github/bible/bible_queue.py:710`, `.github/bible/bible_queue.py:724`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:752`), `Queue.delta` (`.github/bible/bible_queue.py:1032`), `main` (`.github/bible/bible_queue.py:1094`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures labels, optionally configures agent assignment, and creates an issue. |

**Steps**

1. Ensures every requested label, using its `LABELS` description or `Codebase analysis run` as the fallback. (`.github/bible/bible_queue.py:152-153`)
2. Builds a payload containing `title`, `body`, and `labels`; if `assign` is not `None`, adds the Copilot assignee and `agent_assignment`. (`.github/bible/bible_queue.py:154-157`)
3. Posts the payload to `/issues` and returns the result of `call`. (`.github/bible/bible_queue.py:158`)

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
| `.github/bible/bible_queue.py:152` | for | For each requested label | Calls `ensure_label` with its mapped or fallback description. |
| `.github/bible/bible_queue.py:155` | if | `assign` is not `None` | Adds `COPILOT` and the assignment value to the payload. |

#### `GitHub.me()`

Source: `.github/bible/bible_queue.py:160-164` <!-- code: 6c567c6be9c4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:992`) |
| Calls | `getattr`, `GitHub.call`, `get` |
| Purpose | Lazily fetches and caches the token owner's login. |

**Steps**

1. If `_me` is not already truthy, GETs the API `/user` URL and stores its `login`, defaulting to an empty string when the response is falsey or has no login. (`.github/bible/bible_queue.py:162-163`)
2. Returns the cached `_me` value. (`.github/bible/bible_queue.py:164`)

**Pseudo-code**

```text
if _me is falsey: _me = GET api/user.login or ""
return _me
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:162` | if | `_me` is falsey or absent | Fetches and caches the token owner's login. |

#### `GitHub.default_branch()`

Source: `.github/bible/bible_queue.py:166-167` <!-- code: 4eb167486c4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:544`), `Queue.delta` (`.github/bible/bible_queue.py:905`) |
| Calls | `GitHub.call` |
| Purpose | Returns the repository's `default_branch` value. |

**Steps**

1. Gets the repository resource at the empty path and returns its `default_branch` field. (`.github/bible/bible_queue.py:167`)

**Pseudo-code**

```text
return GET repository["default_branch"]
```

#### `GitHub.branch_sha(branch)`

Source: `.github/bible/bible_queue.py:169-171` <!-- code: 446defb234bd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:628-629`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Returns a branch reference's object SHA or `None` when the reference is absent. |

**Steps**

1. Quotes `branch` and gets its head reference with `ok404=True`. (`.github/bible/bible_queue.py:170`)
2. Returns `ref["object"]["sha"]` if a reference was returned, otherwise `None`. (`.github/bible/bible_queue.py:171`)

**Pseudo-code**

```text
ref = GET quoted branch reference, allowing 404
return ref.object.sha if ref else None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:171` | conditional expression | A reference was returned | Returns its object SHA; otherwise returns `None`. |

#### `GitHub.create_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:173-174` <!-- code: b860758c1ca1 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:630`) |
| Calls | `GitHub.call` |
| Purpose | Creates a Git reference for a branch at a supplied SHA. |

**Steps**

1. Posts `ref: "refs/heads/" + branch` and `sha` to `/git/refs`. (`.github/bible/bible_queue.py:174`)

**Pseudo-code**

```text
POST /git/refs with ref "refs/heads/" + branch and sha
```

#### `GitHub.reset_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:176-177` <!-- code: 43e383793681 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:632`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Force-updates a branch reference to a supplied SHA. |

**Steps**

1. Quotes `branch` and PATCHes its head reference with the supplied SHA and `force: True`. (`.github/bible/bible_queue.py:177`)

**Pseudo-code**

```text
PATCH quoted head reference with sha and force=True
```

#### `GitHub.file(path, ref)`

Source: `.github/bible/bible_queue.py:179-183` <!-- code: e383f7bd9e38 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `issue_text` (`.github/bible/bible_queue.py:386`), `json_file` (`.github/bible/bible_queue.py:401`), `Queue.component` (`.github/bible/bible_queue.py:607`), `Queue.follow` (`.github/bible/bible_queue.py:785`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:731`), `Queue.delta` (`.github/bible/bible_queue.py:907`) |
| Calls | `GitHub.call`, `urllib.parse.quote`, `isinstance`, `base64.b64decode`, `decode` |
| Purpose | Retrieves and decodes a text file from a repository reference. |

**Steps**

1. Quotes `path` and `ref` and GETs the contents endpoint with `ok404=True`. (`.github/bible/bible_queue.py:180`)
2. Returns `None` for a falsey response, a list response, or a response without `content`. (`.github/bible/bible_queue.py:181-182`)
3. Base64-decodes the content and decodes UTF-8 with replacement for invalid bytes. (`.github/bible/bible_queue.py:183`)

**Pseudo-code**

```text
got = GET quoted contents path at quoted ref, allowing 404
if got is falsey, a list, or lacks content: return None
return base64-decode content, then UTF-8 decode with replacement
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:181` | if | Response is falsey, a list, or has no `content` | Returns `None`. |

#### `GitHub.prs(base=None, state="open")`

Source: `.github/bible/bible_queue.py:185-187` <!-- code: e46dcb273277 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site found; unused (inferred: search for `.prs(` in `.github/bible/bible_queue.py` returned no matches). |
| Calls | `urllib.parse.quote`, `GitHub.paged` |
| Purpose | Lists pull requests by state and optional base branch. |

**Steps**

1. Builds `/pulls?state=<state>` and appends a URL-quoted base query only when `base` is truthy. (`.github/bible/bible_queue.py:186`)
2. Returns the paged results. (`.github/bible/bible_queue.py:187`)

**Pseudo-code**

```text
path = /pulls?state=state
if base is truthy: append quoted base query
return paged(path)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:186` | conditional expression | `base` is truthy | Appends `&base=` and the quoted base; otherwise appends nothing. |

#### `GitHub.timeline(number)`

Source: `.github/bible/bible_queue.py:189-190` <!-- code: 6df4539072ff -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.linked_prs` (`.github/bible/bible_queue.py:195`), `GitHub.agent_events` (`.github/bible/bible_queue.py:210`), `GitHub.start_error` (`.github/bible/bible_queue.py:224`), `GitHub.assigned_at` (`.github/bible/bible_queue.py:234`) |
| Calls | `GitHub.paged` |
| Purpose | Returns all paged timeline events for an issue number. |

**Steps**

1. Pages `/issues/<number>/timeline` and returns the result. (`.github/bible/bible_queue.py:190`)

**Pseudo-code**

```text
return paged /issues/<number>/timeline
```

#### `GitHub.linked_prs(number)`

Source: `.github/bible/bible_queue.py:192-201` <!-- code: 91e30cd14abd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:458`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:826`) |
| Calls | `GitHub.timeline`, `get`, `append`, `GitHub.call`, `sorted`, `set` |
| Purpose | Finds existing pull requests in this repository cross-referenced from an issue. |

**Steps**

1. Iterates the issue timeline and reads each event's source issue, defaulting missing source/repository values as shown. (`.github/bible/bible_queue.py:194-197`)
2. Collects the source number only for `cross-referenced` events whose source has a `pull_request` and whose repository full name equals this client's repository. (`.github/bible/bible_queue.py:198-199`)
3. Deduplicates and sorts numbers, GETs each pull request with `ok404=True`, and returns only non-`None` results. (`.github/bible/bible_queue.py:200-201`)

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
| `.github/bible/bible_queue.py:195` | for | For each issue timeline event | Inspects its source issue. |
| `.github/bible/bible_queue.py:198` | if | Event is a same-repository cross-reference with a pull request | Appends its source number. |

#### `GitHub.branch_prs(branch, base)`

Source: `.github/bible/bible_queue.py:203-206` <!-- code: fa42118d7d5a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:642`) |
| Calls | `split`, `GitHub.paged`, `urllib.parse.quote` |
| Purpose | Lists all-state pull requests from this repository's branch into a specified base. |

**Steps**

1. Takes the owner portion before `/` in `repo`. (`.github/bible/bible_queue.py:205`)
2. Pages `/pulls` with `state=all`, quoted `owner:branch` as `head`, and quoted `base`. (`.github/bible/bible_queue.py:206`)

**Pseudo-code**

```text
owner = first segment of repo
return paged /pulls with state=all, head=quoted(owner + ":" + branch), base=quoted(base)
```

#### `GitHub.agent_events(number)`

Source: `.github/bible/bible_queue.py:208-212` <!-- code: 23a18c0ca1f4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.is_agent_pr` (`.github/bible/bible_queue.py:219`), `Queue.session` (`.github/bible/bible_queue.py:472`) |
| Calls | `GitHub.timeline`, `get` |
| Purpose | Returns qualifying Copilot work timeline events as `(event, timestamp)` pairs. |

**Steps**

1. Reads the timeline and returns pairs containing each event name and `created_at`, defaulting a missing timestamp to the empty string. (`.github/bible/bible_queue.py:210`)
2. Includes only events whose performed-via-app slug equals `AGENT_APP` and whose event is `copilot_work_started` or `copilot_work_finished`. (`.github/bible/bible_queue.py:211-212`)

**Pseudo-code**

```text
return (event, created_at or "") for timeline events
    whose app slug is AGENT_APP and event is started or finished
```

#### `GitHub.is_agent_pr(pr)`

Source: `.github/bible/bible_queue.py:214-219` <!-- code: bad4f383c910 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:460`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:728`) |
| Calls | `get`, `GitHub.agent_events`, `any` |
| Purpose | Tests whether a pull request is attributed to a configured agent login or has a Copilot-start event. |

**Steps**

1. Reads `pr["user"]`, defaulting to an empty dictionary, and checks whether its login (defaulting to an empty string) is in `AGENT_LOGINS` and its type (defaulting to `"Bot"`) is `"Bot"`. (`.github/bible/bible_queue.py:216-217`)
2. Returns `True` immediately for that configured bot identity; otherwise checks the pull request timeline and returns whether any event is `copilot_work_started`. (`.github/bible/bible_queue.py:217-219`)

**Pseudo-code**

```text
if PR user's login is in AGENT_LOGINS and user type is Bot: return True
return any agent event is copilot_work_started
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:217` | if | PR user's login is in `AGENT_LOGINS` and user type is `"Bot"` | Returns `True` without checking the timeline. |

#### `GitHub.start_error(issue)`

Source: `.github/bible/bible_queue.py:221-230` <!-- code: 0287983c593a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:469`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:449`) |
| Calls | `GitHub.assigned_at`, `GitHub.timeline`, `get`, `START_ERROR.search`, `splitlines`, `strip` |
| Purpose | Returns the first matching agent start-error comment since the last assignment, or `None`. |

**Steps**

1. Gets the last assignment time using `assigned_at`, then scans the issue timeline. (`.github/bible/bible_queue.py:223-224`)
2. Chooses `actor` or `user`, then uses the actor login only when the actor type defaults to or is `"Bot"`. (`.github/bible/bible_queue.py:225-226`)
3. Requires a `commented` event by a configured agent at or after the assignment time and a body matching `START_ERROR`. (`.github/bible/bible_queue.py:227-228`)
4. Returns the stripped first body line, truncated to 300 characters, for the first qualifying event; returns `None` if no event qualifies. (`.github/bible/bible_queue.py:229-230`)

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
| `.github/bible/bible_queue.py:224` | for | For each issue timeline event | Checks actor, event time, and body. |
| `.github/bible/bible_queue.py:226` | conditional expression | Actor is a bot (or has no type) | Uses the actor login; otherwise uses an empty login. |
| `.github/bible/bible_queue.py:227` | if | Comment event from configured agent at/after assignment matches `START_ERROR` | Returns the bounded first line; otherwise continues scanning. |

#### `GitHub.assigned_at(issue)`

Source: `.github/bible/bible_queue.py:232-235` <!-- code: 8dec0d30b502 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.start_error` (`.github/bible/bible_queue.py:223`), `Queue.session` (`.github/bible/bible_queue.py:471`) |
| Calls | `GitHub.timeline`, `get`, `max` |
| Purpose | Returns the newest timestamp for an assignment event, falling back to issue creation time. |

**Steps**

1. Collects nonempty `created_at` values from `assigned` timeline events for the issue. (`.github/bible/bible_queue.py:234`)
2. Returns the maximum timestamp, or `issue["created_at"]` if there were none. (`.github/bible/bible_queue.py:235`)

**Pseudo-code**

```text
times = created_at for assigned events with a timestamp
return max(times) if any, otherwise issue.created_at
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:235` | conditional expression | At least one assignment timestamp exists | Returns the newest timestamp; otherwise uses issue creation time. |

#### `GitHub.pr_files(number)`

Source: `.github/bible/bible_queue.py:237-250` <!-- code: 58ad7fd72404 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:751`, `.github/bible/bible_queue.py:754`, `.github/bible/bible_queue.py:778`) |
| Calls | `GitHub.paged`, `as_int`, `GitHub.call`, `get`, `len`, `append`, `RuntimeError` |
| Purpose | Returns each changed filename and, when present, its previous name. |

**Steps**

1. Pages the pull request files endpoint and reads the pull request's `changed_files` count. (`.github/bible/bible_queue.py:240-241`)
2. If the expected count is nonzero and differs from the number listed, raises `RuntimeError` rather than accepting an incomplete file list. (`.github/bible/bible_queue.py:242-244`)
3. Appends each current `filename`, then appends `previous_filename` when truthy, and returns the list. (`.github/bible/bible_queue.py:245-250`)

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
| `.github/bible/bible_queue.py:242` | if | Expected count is nonzero and differs from listed count | Raises `RuntimeError` for an incomplete file list. |
| `.github/bible/bible_queue.py:243` | raise | Listed count differs from a nonzero expected count | Raises the incomplete-file-list `RuntimeError`. |
| `.github/bible/bible_queue.py:246` | for | For each paged pull request file | Appends its current filename. |
| `.github/bible/bible_queue.py:248` | if | `previous_filename` is truthy | Appends the previous filename. |

#### `GitHub.commit_time(sha)`

Source: `.github/bible/bible_queue.py:252-253` <!-- code: a3036655ce65 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:475`) |
| Calls | `GitHub.call` |
| Purpose | Returns the committer date for a commit SHA. |

**Steps**

1. GETs `/commits/<sha>` and returns `commit.committer.date`. (`.github/bible/bible_queue.py:253`)

**Pseudo-code**

```text
return GET /commits/<sha>.commit.committer.date
```

#### `GitHub.tarball(ref, dest)`

Source: `.github/bible/bible_queue.py:255-288` <!-- code: 2b7230566234 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.check` (`.github/bible/bible_queue.py:801`) |
| Calls | `urllib.parse.quote`, `tempfile.TemporaryFile`, `GitHub.request`, `shutil.copyfileobj`, `seek`, `os.path.abspath`, `tarfile.open`, `RuntimeError`, `split`, `len`, `isfile`, `isdir`, `os.path.normpath`, `os.path.join`, `startswith`, `os.makedirs`, `os.path.dirname`, `tar.extractfile`, `open` |
| Purpose | Downloads a repository archive to a temporary file and writes accepted regular files/directories under `dest`. |

**Steps**

1. Constructs an archive URL from the API base, repository, and quoted reference; streams the GET response into a temporary file with a 300-second timeout. (`.github/bible/bible_queue.py:258-270`)
2. Converts request `URLError`, `TimeoutError`, and `OSError` exceptions into `RuntimeError`; then seeks to the start and resolves `dest` to an absolute root. (`.github/bible/bible_queue.py:260-275`)
3. Iterates gzip tar members, splitting each name once at `/`; skips names without a nonempty second part and members that are neither files nor directories. (`.github/bible/bible_queue.py:275-279`)
4. Joins and normalizes each relative member path under `root`; skips targets outside the root prefix. (`.github/bible/bible_queue.py:280-282`)
5. Creates accepted directories recursively; for accepted files, creates the parent and copies extracted bytes to a binary output file. (`.github/bible/bible_queue.py:283-288`)

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
| `.github/bible/bible_queue.py:271` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Raises `RuntimeError` identifying the reference and error. |
| `.github/bible/bible_queue.py:272` | raise | A listed request error occurred | Stops with `RuntimeError`. |
| `.github/bible/bible_queue.py:263` | for | While response chunks remain | Reads the next chunk and stops when it is empty. |
| `.github/bible/bible_queue.py:265` | if | The response supplies no more bytes | Leaves the streaming loop. |
| `.github/bible/bible_queue.py:268` | if | Accumulated bytes exceed `MAX_TARBALL` | Raises `RuntimeError` without unpacking the archive. |
| `.github/bible/bible_queue.py:269` | raise | Tarball exceeds the configured maximum | Reports the reference and maximum size. |
| `.github/bible/bible_queue.py:276` | for | For each archive member | Checks whether to skip or unpack it. |
| `.github/bible/bible_queue.py:278` | if | Missing relative path or member is neither file nor directory | Skips the member. |
| `.github/bible/bible_queue.py:281` | if | Normalized target is not under the root prefix | Skips the member. |
| `.github/bible/bible_queue.py:283` | if | Member is a directory | Creates the directory and continues to the next member. |

#### `GitHub.label(number, name)`

Source: `.github/bible/bible_queue.py:290-292` <!-- code: 3c67a9360e66 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:516`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:528`), `Queue.follow` (`.github/bible/bible_queue.py:763-764`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures and adds one label to an issue. |

**Steps**

1. Ensures the label using its `LABELS` description or the default description. (`.github/bible/bible_queue.py:291`)
2. Posts `{"labels": [name]}` to the issue labels endpoint. (`.github/bible/bible_queue.py:292`)

**Pseudo-code**

```text
ensure label using mapped description or default
POST issue labels with [name]
```

#### `GitHub.unlabel(number, name)`

Source: `.github/bible/bible_queue.py:294-295` <!-- code: caf34958b931 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:789`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Removes a label from an issue and permits a missing-label response. |

**Steps**

1. URL-quotes `name` and sends DELETE to the issue label endpoint with `ok404=True`. (`.github/bible/bible_queue.py:295`)

**Pseudo-code**

```text
DELETE quoted issue label endpoint, allowing 404
```

#### `GitHub.comment(number, text)`

Source: `.github/bible/bible_queue.py:297-298` <!-- code: a05e7f494734 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:440`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:518`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:525`, `.github/bible/bible_queue.py:530`, `.github/bible/bible_queue.py:533`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:880`) |
| Calls | `GitHub.call` |
| Purpose | Creates an issue comment with the given body. |

**Steps**

1. Posts `{"body": text}` to `/issues/<number>/comments`. (`.github/bible/bible_queue.py:298`)

**Pseudo-code**

```text
POST issue comments with body=text
```

#### `GitHub.close(number, reason="completed")`

Source: `.github/bible/bible_queue.py:300-301` <!-- code: db2a40d380a0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:534`), `Queue.run` (`.github/bible/bible_queue.py:580`), `Queue.component` (`.github/bible/bible_queue.py:601`), `Queue.follow` (`.github/bible/bible_queue.py:790`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:838`, `.github/bible/bible_queue.py:881`) |
| Calls | `GitHub.call` |
| Purpose | Closes an issue with the supplied state reason. |

**Steps**

1. PATCHes `/issues/<number>` with `state: "closed"` and the supplied `state_reason`. (`.github/bible/bible_queue.py:301`)

**Pseudo-code**

```text
PATCH issue state=closed and state_reason=reason
```

#### `GitHub.set_body(number, body)`

Source: `.github/bible/bible_queue.py:303-304` <!-- code: 56545a0f998b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:437`), `Queue.render` (`.github/bible/bible_queue.py:898`) |
| Calls | `GitHub.call` |
| Purpose | Replaces an issue's body. |

**Steps**

1. PATCHes `/issues/<number>` with `{"body": body}`. (`.github/bible/bible_queue.py:304`)

**Pseudo-code**

```text
PATCH issue body=body
```

#### `GitHub.unassign(number)`

Source: `.github/bible/bible_queue.py:306-307` <!-- code: 415484346894 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:517`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:529`) |
| Calls | `GitHub.call` |
| Purpose | Removes the configured Copilot assignee from an issue. |

**Steps**

1. Sends DELETE to `/issues/<number>/assignees` with `COPILOT` as the sole assignee. (`.github/bible/bible_queue.py:307`)

**Pseudo-code**

```text
DELETE issue assignees with [COPILOT]
```

#### `GitHub.assign(number, assign)`

Source: `.github/bible/bible_queue.py:309-310` <!-- code: 8fb2f09224db -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:439`) |
| Calls | `GitHub.call` |
| Purpose | Assigns Copilot to an issue with the provided agent-assignment data. |

**Steps**

1. Posts `COPILOT` as the sole assignee and includes the supplied `agent_assignment`. (`.github/bible/bible_queue.py:310`)

**Pseudo-code**

```text
POST issue assignees with [COPILOT] and agent_assignment=assign
```

#### `GitHub.ready(pr)`

Source: `.github/bible/bible_queue.py:312-320` <!-- code: ae31dacf00e7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.merge` (`.github/bible/bible_queue.py:324`) |
| Calls | `endswith`, `GitHub.request`, response `read`, `RuntimeError` |
| Purpose | Marks a draft pull request ready for review through GitHub GraphQL. |

**Steps**

1. Defines the `markPullRequestReadyForReview` mutation and chooses the GraphQL URL; for an API base ending `/api/v3`, removes `/v3` before adding `/graphql`. (`.github/bible/bible_queue.py:314-315`)
2. POSTs the query and `pr["node_id"]` as the `id` variable, then reads the response. (`.github/bible/bible_queue.py:316-318`)
3. Converts an `HTTPError` to a `RuntimeError` containing the GraphQL operation and HTTP status. (`.github/bible/bible_queue.py:319-320`)

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
| `.github/bible/bible_queue.py:315` | conditional expression | API URL ends with `/api/v3` | Removes `/v3` before appending `/graphql`; otherwise appends `/graphql` directly. |
| `.github/bible/bible_queue.py:319` | except | Request raises `HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:320` | raise | GraphQL request raises `HTTPError` | Raises `RuntimeError` with operation and HTTP status. |

#### `GitHub.merge(pr, title)`

Source: `.github/bible/bible_queue.py:322-326` <!-- code: cea69f3a2a18 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:788`) |
| Calls | `get`, `GitHub.ready`, `GitHub.call` |
| Purpose | Marks a draft ready, when needed, and requests a squash merge with the supplied title. |

**Steps**

1. Calls `ready` only when `pr["draft"]` is truthy. (`.github/bible/bible_queue.py:323-324`)
2. PUTs `/pulls/<number>/merge` with `merge_method: "squash"`, the supplied `commit_title`, and the current head SHA. (`.github/bible/bible_queue.py:325-326`)

**Pseudo-code**

```text
if PR is draft: mark it ready
PUT merge request with squash method and title
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:323` | if | `pr["draft"]` is truthy | Calls `ready` before requesting the merge. |

#### `GitHub.close_pr(number)`

Source: `.github/bible/bible_queue.py:328-329` <!-- code: c5e4b3b311ae -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:526`) |
| Calls | `GitHub.call` |
| Purpose | Closes a pull request. |

**Steps**

1. PATCHes `/pulls/<number>` with `state: "closed"`. (`.github/bible/bible_queue.py:329`)

**Pseudo-code**

```text
PATCH pull request state=closed
```

#### `GitHub.create_pr(head, base, title, body)`

Source: `.github/bible/bible_queue.py:331-332` <!-- code: 9b2aa4667c1c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:675`) |
| Calls | `GitHub.call` |
| Purpose | Creates a pull request and returns the API result. |

**Steps**

1. POSTs `head`, `base`, `title`, and `body` to `/pulls`, returning `call`'s result. (`.github/bible/bible_queue.py:332`)

**Pseudo-code**

```text
return POST /pulls with head, base, title, and body
```

### `Queue`

Source: `.github/bible/bible_queue.py:396-817` <!-- code: c7b3115b36f1 -->

`Queue` coordinates tracker issues, component sessions, verification/revision cycles, assembly, and delta updates. Its constructor sets the GitHub client, logger, and skill directory; methods also populate run-specific fields such as `default`, `settings`, `tracker`, `run_label`, and `estimate` (`.github/bible/bible_queue.py:397-399,464-483,486-496,498-534`).

#### `Queue.__init__(gh, log=print)`

Source: `.github/bible/bible_queue.py:449-451` <!-- code: 11924208c0e9 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1081`) |
| Calls | `os.environ.get` |
| Purpose | Stores the GitHub client and logger, and selects the skills directory. |

**Steps**

1. Stores `gh` and `log` on the instance. (`.github/bible/bible_queue.py:450`)
2. Reads `BIBLE_SKILLS`, defaulting to `.github/skills`. (`.github/bible/bible_queue.py:451`)

**Pseudo-code**

```text
self.gh, self.log = gh, log
self.skills = BIBLE_SKILLS or ".github/skills"
```

#### `Queue.run_issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:453-454` <!-- code: 9186c4a33e43 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:505`), `Queue.plan_phase` (`.github/bible/bible_queue.py:603`), `Queue.start_chunk` (`.github/bible/bible_queue.py:631`), `Queue.component` (`.github/bible/bible_queue.py:651`, `.github/bible/bible_queue.py:660`, `.github/bible/bible_queue.py:667`, `.github/bible/bible_queue.py:670`, `.github/bible/bible_queue.py:602`, `.github/bible/bible_queue.py:604`, `.github/bible/bible_queue.py:606`, `.github/bible/bible_queue.py:679-680`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:817`, `.github/bible/bible_queue.py:819`) |
| Calls | `self.gh.issues` |
| Purpose | Queries issues for the requested labels plus this run's unique label. |

**Steps**

1. Appends `self.run_label` to the supplied labels and calls `gh.issues` with the requested state. (`.github/bible/bible_queue.py:454`)

**Pseudo-code**

```text
return gh.issues(labels + [run_label], state)
```

#### `Queue.agent_pr(issue, base)`

Source: `.github/bible/bible_queue.py:456-462` <!-- code: 471c772b908b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:467`) |
| Calls | `reversed`, `self.gh.linked_prs`, `get`, `self.gh.is_agent_pr` |
| Purpose | Finds the newest linked pull request that is open, same-repository, targets `base`, and is by the agent. |

**Steps**

1. Iterates linked pull requests in reverse order. (`.github/bible/bible_queue.py:458`)
2. Reads the head repository full name, defaulting missing nested values to `{}`. (`.github/bible/bible_queue.py:459`)
3. Returns the first PR whose state is `open`, head repository is `gh.repo`, base ref matches, and `is_agent_pr` is true. (`.github/bible/bible_queue.py:460-461`)
4. Returns `None` when no linked PR qualifies. (`.github/bible/bible_queue.py:462`)

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
| `.github/bible/bible_queue.py:458` | for | For each linked PR in reverse order | Checks newer linked PRs first. |
| `.github/bible/bible_queue.py:460` | if | PR is open, same-repository, targets `base`, and is an agent PR | Returns that PR. |

#### `Queue.session(issue, base, analysis, comp=None)`

Source: `.github/bible/bible_queue.py:465-481` <!-- code: 6fe9d410226f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:616`), `Queue.follow` (`.github/bible/bible_queue.py:737`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:842`) |
| Calls | `self.agent_pr`, `self.gh.start_error`, `age`, `self.gh.assigned_at`, `self.gh.agent_events`, `sorted`, `self.gh.commit_time`, `bool`, `status_of`, `labels_of`, `get` |
| Purpose | Classifies an issue's session as waiting, running, finished, no-start, or start-error and returns its PR if present. |

**Steps**

1. Looks up the agent PR. If absent, returns `("start-error", None)` for a detected start error; otherwise compares issue assignment age to `NO_PR_AFTER` and returns `no-start` or `waiting`. (`.github/bible/bible_queue.py:467-471`)
2. If agent work events exist, sorts them by timestamp and returns `finished` when the latest is `copilot_work_finished`, else `running`, together with the PR. (`.github/bible/bible_queue.py:472-474`)
3. Without work events, computes age from the PR head commit and marks `asked` when reviewers were requested or the PR is not draft. (`.github/bible/bible_queue.py:475-476`)
4. For a component chunk, reads status at the PR head SHA and considers it finished when final status plus an asked/idle condition holds, or when pushed age exceeds three times `IDLE_AFTER`. (`.github/bible/bible_queue.py:477-480`)
5. Otherwise returns `finished` when `asked` or pushed age exceeds `IDLE_AFTER`, else `running`; both paths include the PR. (`.github/bible/bible_queue.py:481`)

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
| `.github/bible/bible_queue.py:468` | if | No agent PR was found | Enters start-error/no-start/waiting classification. |
| `.github/bible/bible_queue.py:469` | if | `start_error(issue)` is truthy | Returns start-error without a PR. |
| `.github/bible/bible_queue.py:471` | conditional expression | Assignment age exceeds `NO_PR_AFTER` | Returns `no-start`; otherwise returns `waiting`. |
| `.github/bible/bible_queue.py:473` | if | Agent work events exist | Uses latest work event to classify session state. |
| `.github/bible/bible_queue.py:474` | conditional expression | Latest work event is `copilot_work_finished` | Returns finished; otherwise running. |
| `.github/bible/bible_queue.py:477` | if | `comp` is truthy and issue has `bible-chunk` label | Uses head status and component-specific age rules. |
| `.github/bible/bible_queue.py:480` | conditional expression | Final status and asked/idle condition holds, or pushed age exceeds `3 * IDLE_AFTER` | Returns finished; otherwise running. |
| `.github/bible/bible_queue.py:481` | conditional expression | `asked` or pushed age exceeds `IDLE_AFTER` | Returns finished; otherwise running. |

#### `Queue.held(issue)`

Source: `.github/bible/bible_queue.py:483-516` <!-- code: c519a460eab6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:623`), `Queue.component` (`.github/bible/bible_queue.py:663`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:881`) |
| Calls | `labels_of`, `any`, `get`, `issue.get`, `self.gh.timeline`, `max`, `e.get`, `self.gh.label`, `self.gh.comment`, `self.gh.close`, `l.startswith`, `ATTEMPT.sub`, `self.gh.set_body`, `re.search`, `self.gh.assign`, `assignment`, `self.model_for`, `base.group` |
| Purpose | Holds issues marked for a person, closes released component sessions, or reassigns other unassigned sessions to Copilot. |

**Steps**

1. Returns `True` when the labels include `bible-needs-human`. (`.github/bible/bible_queue.py:491`)
2. Otherwise returns `False` immediately when an assignee login belongs to `AGENT_LOGINS`. (`.github/bible/bible_queue.py:493`)
3. Reads issue timeline events and finds the latest added and removed timestamps for `bible-needs-human`; if removal is absent or not newer, labels and comments the issue for human review and returns `True`. (`.github/bible/bible_queue.py:494-506`)
4. If a `bible/` label exists after release, comments and closes the issue as `not_planned`, returning `released`. (`.github/bible/bible_queue.py:507-510`)
5. Otherwise resets the `Attempt:` marker, saves the body, extracts `Base branch:` or uses `self.default`, assigns Copilot with the selected model, comments, and returns `False`. (`.github/bible/bible_queue.py:511-516`)

**Pseudo-code**

```text
if issue labels include bible-needs-human: return True
if no assignee login belongs to AGENT_LOGINS:
    if any label starts with bible/:
        comment that the released session is closed
        close issue as not_planned; return released
    body = replace Attempt with 1; save body
    base = Base branch match or default
    assign Copilot with base and model_for(issue)
    comment that issue was reassigned
return False
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:491` | if | Labels contain `bible-needs-human` | Returns `True`. |
| `.github/bible/bible_queue.py:493` | if | An assignee login belongs to `AGENT_LOGINS` | Returns `False`. |
| `.github/bible/bible_queue.py:500` | if | The human-label removal is absent or not newer than its addition | Labels, comments, and returns `True`. |
| `.github/bible/bible_queue.py:506` | return | No valid release follows the human hold | Stops before reassignment. |
| `.github/bible/bible_queue.py:507` | if | A component label begins `bible/` after release | Closes and returns `released`; otherwise reassigns. |
| `.github/bible/bible_queue.py:514` | conditional expression | A `Base branch:` match exists | Uses its captured branch; otherwise uses `self.default`. |

#### `Queue.model_for(issue)`

Source: `.github/bible/bible_queue.py:518-520` <!-- code: 17f084589886 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:448`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:548`) |
| Calls | `labels_of`, `self.settings.get` |
| Purpose | Selects the verification model for verification issue types, otherwise the normal model. |

**Steps**

1. Gets the issue's label names. (`.github/bible/bible_queue.py:519`)
2. Returns `verify_model` when labels intersect `bible-verify` or `bible-verify-all`; otherwise returns `model`. (`.github/bible/bible_queue.py:520`)

**Pseudo-code**

```text
kinds = labels_of(issue)
return settings.verify_model if kinds intersects verify labels
       else settings.model
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:520` | conditional expression | `kinds` intersects the verification labels | Returns `verify_model`; otherwise returns `model`. |

#### `Queue.hold_start_error(issue)`

Source: `.github/bible/bible_queue.py:522-528` <!-- code: 510c0f07df06 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:627`), `Queue.follow` (`.github/bible/bible_queue.py:760`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:895`) |
| Calls | `self.gh.start_error`, `self.gh.label`, `self.gh.unassign`, `self.gh.comment` |
| Purpose | Holds a session with an agent start error for human intervention. |

**Steps**

1. Gets the start-error text or uses `Copilot could not start`. (`.github/bible/bible_queue.py:449`)
2. Adds `bible-needs-human`, unassigns Copilot, and posts a comment containing the reason and remediation guidance. (`.github/bible/bible_queue.py:516-519`)

**Pseudo-code**

```text
why = start_error(issue) or fallback message
label issue bible-needs-human
unassign Copilot
comment why and instructions for removing the hold
```

#### `Queue.fail_or_retry(issue, pr, why)`

Source: `.github/bible/bible_queue.py:530-549` <!-- code: c86515a02433 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:630`), `Queue.follow` (`.github/bible/bible_queue.py:763`, `.github/bible/bible_queue.py:781`, `.github/bible/bible_queue.py:794`, `.github/bible/bible_queue.py:799`, `.github/bible/bible_queue.py:802`, `.github/bible/bible_queue.py:805`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:898`) |
| Calls | `ATTEMPT.search`, `int`, `self.gh.comment`, `self.gh.close_pr`, `self.gh.label`, `self.gh.unassign`, `self.gh.close`, `ATTEMPT.sub`, `re.search`, `self.gh.create_issue`, `sorted`, `assignment`, `self.model_for`, `labels_of`, `startswith` |
| Purpose | Closes a failed attempt and opens its retry, or holds the issue after a second failure. |

**Steps**

1. Parses the attempt number from the issue body, defaulting to 1. (`.github/bible/bible_queue.py:523`)
2. If a PR was supplied, comments that it was not merged and closes it. (`.github/bible/bible_queue.py:524-526`)
3. When attempt is at least 2, labels and unassigns the issue, posts a human-action comment, and returns `False`. (`.github/bible/bible_queue.py:527-532`)
4. Otherwise comments that a new attempt will open, closes the issue with `not_planned`, updates or prepends the attempt marker, and extracts the base branch or uses `self.default`. (`.github/bible/bible_queue.py:533-537`)
5. Creates a replacement issue with only labels beginning `bible`, sorted, and assignment data for the chosen base and model; returns `True`. (`.github/bible/bible_queue.py:538-540`)

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
| `.github/bible/bible_queue.py:533` | if | `pr` is truthy | Comments that it was not merged and closes the PR; otherwise skips PR updates. |
| `.github/bible/bible_queue.py:536` | if | Attempt number is at least 2 | Labels and unassigns the issue, comments for human action, and returns `False`; otherwise opens a retry. |
| `.github/bible/bible_queue.py:544` | conditional expression | The issue body contains an attempt marker | Replaces it with the incremented attempt; otherwise prepends `Attempt: 2`. |
| `.github/bible/bible_queue.py:548` | conditional expression | A `Base branch:` match exists in the original body | Assigns the retry to that branch; otherwise uses `self.default`. |

#### `Queue.reconcile()`

Source: `.github/bible/bible_queue.py:552-562` <!-- code: 405a62c3c051 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1097`) |
| Calls | `self.gh.default_branch`, `self.gh.issues`, `settings_of`, `self.log`, `self.run`, `type` |
| Purpose | Processes each open tracker independently so one failing tracker does not prevent others. |

**Steps**

1. Reads and stores the repository default branch. (`.github/bible/bible_queue.py:544`)
2. Iterates open issues labeled `bible-tracker`, parses each settings block, and logs/skips trackers without readable settings. (`.github/bible/bible_queue.py:545-549`)
3. Calls `run` for each readable tracker; catches any `Exception` and logs the tracker number, exception type, and message. (`.github/bible/bible_queue.py:550-553`)

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
| `.github/bible/bible_queue.py:554` | for | For each open `bible-tracker` issue | Parses its settings and processes that tracker independently. |
| `.github/bible/bible_queue.py:556` | if | `settings_of` returns a falsey value | Logs the tracker number and skips it. |
| `.github/bible/bible_queue.py:559` | try | Settings are readable | Calls `run` for the tracker. |
| `.github/bible/bible_queue.py:561` | except | Processing the tracker raises `Exception` | Logs tracker number, exception type, and message, then continues with the next tracker. |

#### `Queue.run(tracker, settings)`

Source: `.github/bible/bible_queue.py:564-608` <!-- code: 16c88ca938a7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:560`) |
| Calls | `settings.get`, `json_file`, `catalog.get`, `self.plan_phase`, `isinstance`, `c.get`, `str.strip`, `asked.split`, `n.strip`, `join`, `self.render`, `self.run_issues`, `gh.close`, `self.component`, `str.endswith`, `str.startswith`, `as_int`, `self.start_chunk`, `type`, `str`, `all`, `rows.values`, `self.assemble_phase` |
| Purpose | Sends an incomplete catalog to planning; otherwise validates selected components, advances their queue states within the configured concurrency cap, and renders tracker status. |

**Steps**

1. Selects `analysis` from settings or `codebase-analysis`, stores settings, tracker, and run label, and reads `components.json` from the default branch. (`.github/bible/bible_queue.py:564-568`)
2. If the catalog is not a dict, is marked proposed, or lacks a components list, returns `plan_phase`. (`.github/bible/bible_queue.py:569-570`)
3. Extracts valid-looking component names, strips the configured selection, expands `all` or empty selection to all names, otherwise splits comma-separated names and strips each one; then computes unrecognized names. (`.github/bible/bible_queue.py:571-575`)
4. If any selected name is unknown or selection is empty, renders a stopped-settings row with the unknown names or empty-selection reason and all catalog names. (`.github/bible/bible_queue.py:576-581`)
5. Closes all open plan issues, records each component's session estimate, evaluates every requested component, catches per-component exceptions as bounded error strings, and counts active rows. (`.github/bible/bible_queue.py:583-595`)
6. Converts `concurrency` with `as_int`; for each `not started` component, starts a fresh chunk when the cap is zero or active count is below it. A start increments active count; `RuntimeError` is stored as a bounded row error. (`.github/bible/bible_queue.py:595-600`)
7. Adds whole-analysis assembly status when every row is `merged`, then renders the status rows. (`.github/bible/bible_queue.py:604-608`)

**Pseudo-code**

```text
analysis = settings.analysis or "codebase-analysis"
store settings, tracker, and run label; read components.json
if catalog is invalid, proposed, or has no components list: return plan_phase(...)
extract catalog names; parse selection into wanted and unknown
if unknown or wanted is empty: render stopped settings; return
close open plan issues; record session estimates
for each wanted name: evaluate component; store errors and count active states
cap = concurrency converted to integer
for each wanted name: if not started and cap permits, start fresh chunk
if every row is merged: add assembly status
render rows
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:569` | if | Catalog is not a dict, is marked proposed, or has no components list | Returns the planning-phase result. |
| `.github/bible/bible_queue.py:575` | conditional expression | Selection is `all` or empty | Uses all catalog names; otherwise parses comma-separated names. |
| `.github/bible/bible_queue.py:576` | if | Selection contains unknown names or is empty | Renders stopped settings and returns. |
| `.github/bible/bible_queue.py:581` | conditional expression | Unknown names exist | Reports unknown names; otherwise reports no selected component. |
| `.github/bible/bible_queue.py:583` | for | For each open plan issue | Closes that issue. |
| `.github/bible/bible_queue.py:586` | for | For each selected component | Evaluates the component state. |
| `.github/bible/bible_queue.py:588` | try | Evaluating a component | Stores its result or catches an exception. |
| `.github/bible/bible_queue.py:592` | except | Component evaluation raises `Exception` | Stores a per-component error status with the exception type and at most 160 characters of its text. |
| `.github/bible/bible_queue.py:595` | for | For each selected component | Considers whether to start a component whose status is `not started`. |
| `.github/bible/bible_queue.py:599` | if | Status is `not started` and cap is zero or active is below it | Attempts to start a fresh chunk. |
| `.github/bible/bible_queue.py:600` | try | Start conditions hold | Starts the chunk and increments active count. |
| `.github/bible/bible_queue.py:604` | except | Starting the chunk raises `RuntimeError` | Stores a bounded error status. |
| `.github/bible/bible_queue.py:606` | if | Every selected row is `merged` | Adds whole-analysis assembly status. |

#### `Queue.plan_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:610-632` <!-- code: f5b3e835d2d7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:570`) |
| Calls | `self.run_issues`, `issue_text`, `self.gh.create_issue`, `self.render`, `assignment`, `settings.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry` |
| Purpose | Creates or tracks the plan issue and reports plan-session progress. |

**Steps**

1. Gets open plan issues for the tracker run. (`.github/bible/bible_queue.py:612`)
2. If none are open, reads the plan title and body from the analysis ledger; when the body is empty, supplies built-in instructions to run passes 1 and 2, write the Components table, and finish discovery without starting components. It then creates and assigns the plan issue and renders its assigned status. (`.github/bible/bible_queue.py:613-621`)
3. Otherwise selects the first plan issue; if held, renders its human-needed status. (`.github/bible/bible_queue.py:622-624`)
4. Classifies its session; if Copilot reports a start error, marks the issue for human action and renders that status. (`.github/bible/bible_queue.py:625-628`)
5. On `no-start`, requests a retry; then renders the pull-request review state when a PR exists, or the session state otherwise. (`.github/bible/bible_queue.py:629-632`)

**Pseudo-code**

```text
open_plan = run_issues(bible-plan)
if none:
    title, body = issue_text(plan.md)
    if no body: use built-in instructions for planning and discovery only
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
| `.github/bible/bible_queue.py:613` | if | No open plan issue exists | Reads the planned issue text and creates an assigned plan issue. |
| `.github/bible/bible_queue.py:615` | if | The loaded body is falsey | Uses built-in plan and discovery instructions. |
| `.github/bible/bible_queue.py:623` | if | The first open plan issue is held | Renders that a person must act. |
| `.github/bible/bible_queue.py:626` | if | Session state is `start-error` | Holds the issue and renders human-needed state. |
| `.github/bible/bible_queue.py:629` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:631` | conditional expression | `pr` exists | Renders review/merge PR number; otherwise renders the session state. |

#### `Queue.start_chunk(analysis, name, fresh=False, note="")`

Source: `.github/bible/bible_queue.py:634-646` <!-- code: 7f612dd5f454 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:602`), `Queue.component` (`.github/bible/bible_queue.py:606`, `.github/bible/bible_queue.py:739`) |
| Calls | `self.gh.branch_sha`, `self.gh.create_branch`, `self.gh.reset_branch`, `self.run_issues`, `comp_label`, `issue_text`, `self.gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Creates the component branch when absent, optionally resets it for the first chunk, and opens the next assigned chunk issue. |

**Steps**

1. Sets branch to `bible/<name>` and reads the default branch SHA. (`.github/bible/bible_queue.py:636-637`)
2. Creates the component branch at that SHA when absent; otherwise resets it when `fresh` is true and there are no component issues in any state. (`.github/bible/bible_queue.py:638-641`)
3. Reads the component issue text from the default branch, formats the Component/Base branch/Attempt header, and creates a labeled chunk issue with optional note and model assignment. (`.github/bible/bible_queue.py:642-646`)

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
| `.github/bible/bible_queue.py:638` | if | The component branch has no SHA | Creates the branch at the default branch SHA. |
| `.github/bible/bible_queue.py:640` | elif | Branch exists, `fresh` is true, and no issue with the component label exists in any state | Resets the branch to the default branch SHA. |
| `.github/bible/bible_queue.py:645` | conditional expression | `note` is truthy | Adds the note and a newline before the body; otherwise adds no note prefix. |

#### `Queue.component(analysis, name)`

Source: `.github/bible/bible_queue.py:648-751` <!-- code: cf4c5894d38a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:594`) |
| Calls | `gh.branch_prs`, `pr.get`, `get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `status_of`, `status.get`, `self.check`, `len`, `self.start_chunk`, `self.estimate.get`, `gh.close`, `labels_of`, `max`, `h.get`, `i.get`, `report_facts`, `gh.file`, `gh.create_pr`, `gh.create_issue`, `assignment`, `self.settings.get`, `bool`, `any` |
| Purpose | Advances a component through its tracker-specific pull requests and sessions, coverage gate, verification and revision rounds, and final review PR or human hold. |

**Steps**

1. Scans PRs from `bible/<name>` into the default branch. Skips a PR when it comes from another repository, predates this tracker, or its body lacks this tracker's reference; for the first matching PR, returns `merged`, review status, or human-needed status if closed unmerged. (`.github/bible/bible_queue.py:575-585`)
2. Combines open chunk and verification issues. For the first issue, returns a released status, a human-needed status, or the result of following the session. (`.github/bible/bible_queue.py:586-597`)
3. If no session is open, returns `not started` when the component has no issue in any state; otherwise reads its status and runs the check only for `COMPONENT_DONE`. (`.github/bible/bible_queue.py:598-603`)
4. If the check did not pass, counts closed chunk issues, starts another chunk with its session estimate, and returns `session starting`. (`.github/bible/bible_queue.py:604-607`)
5. Loads all hold issues; if a hold is open, returns human-needed when it retains `bible-needs-human`, otherwise closes it and reloads the holds. (`.github/bible/bible_queue.py:608-614`)
6. Uses the latest hold close time to select completed verification issues for the current round, separately gathers all completed verifications, and reads/parses the report only when any such verification exists. (`.github/bible/bible_queue.py:615-619`)
7. Creates a component-to-default PR and returns review status only for a `PASS` with no major corrections and a nonempty report fingerprint equal to the checked page fingerprint. (`.github/bible/bible_queue.py:620-624`)
8. Compares the latest completed verification and chunk close times. If there is no later chunk and the post-hold completed-verification count reaches `MAX_VERIFY_ROUNDS`, creates a labeled human-hold issue and returns its status. (`.github/bible/bible_queue.py:633-647`)
9. When the report concerns these pages, has a failing verdict or major corrections, and no chunk has since run, starts a revision chunk and returns `session starting`. (`.github/bible/bible_queue.py:648-651`)
10. Otherwise creates and assigns a verification issue on the component branch and returns `verify running`. (`.github/bible/bible_queue.py:652-661`)

**Pseudo-code**

```text
for matching same-repository PR from this tracker:
    return merged, review, or needs-person state
if open chunk/verify issue:
    if held: return released or needs-person
    return follow(issue)
if no component issue ever existed: return not started
status = component status
if COMPONENT_DONE: run coverage gate
if gate fails: start next chunk; return session starting
handle first open hold (stop if human label remains; otherwise close it and reload)
closed_verify = completed verifications created since latest hold close
facts = report facts if any completed verification exists
if clean PASS and pages fingerprint matches: create final PR; return review state
if no chunk followed the latest verification and the round limit is reached: create human hold; return
if report concerns these pages, needs revision, and no chunk followed: start revision; return
create verification issue
return verify running
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:577` | for | For each PR targeting the default branch from the component branch | Checks whether that PR belongs to this repository and tracker. |
| `.github/bible/bible_queue.py:579` | if | PR is from another repository, predates the tracker, or lacks its reference | Skips the PR. |
| `.github/bible/bible_queue.py:581` | if | Matching PR has `merged_at` | Returns `merged`. |
| `.github/bible/bible_queue.py:583` | if | Matching PR is open | Returns its review status. |
| `.github/bible/bible_queue.py:587` | if | An open chunk or verification issue exists | Selects the first session issue. |
| `.github/bible/bible_queue.py:590` | if | The selected issue was released by a person | Returns a status to re-evaluate on the next check. |
| `.github/bible/bible_queue.py:592` | if | The selected issue remains held | Returns human-needed status. |
| `.github/bible/bible_queue.py:598` | if | No issue for this component exists in any state | Returns `not started`. |
| `.github/bible/bible_queue.py:602` | if | Component status is `COMPONENT_DONE` | Runs the coverage check. |
| `.github/bible/bible_queue.py:604` | if | Coverage gate did not pass | Starts another chunk and returns `session starting`. |
| `.github/bible/bible_queue.py:610` | if | At least one hold issue is open | Checks whether it still requires a person. |
| `.github/bible/bible_queue.py:611` | if | The first open hold has `bible-needs-human` | Returns human-needed status; otherwise closes that hold and refreshes the issue list. |
| `.github/bible/bible_queue.py:619` | conditional expression | At least one completed verification exists | Parses its report; otherwise `facts` is `None`. |
| `.github/bible/bible_queue.py:620` | if | Facts are `PASS`, have no major corrections, and contain a nonempty matching page fingerprint | Creates the final component PR. |
| `.github/bible/bible_queue.py:639` | if | Facts exist, no completed chunk follows the latest verification, and the post-hold verification count reaches `MAX_VERIFY_ROUNDS` | Creates a human hold. |
| `.github/bible/bible_queue.py:648` | if | Report concerns current pages, needs revision, and no completed chunk follows the latest verification | Starts a revision chunk; otherwise falls through to verification. |
| `.github/bible/bible_queue.py:651` | if | PR is not from this repository | Skips it. |
| `.github/bible/bible_queue.py:653` | if | PR predates the tracker | Skips it. |
| `.github/bible/bible_queue.py:655` | if | PR does not mention this tracker | Skips it. |
| `.github/bible/bible_queue.py:657` | if | PR is merged | Returns merged. |
| `.github/bible/bible_queue.py:661` | if | PR is open | Returns review status. |
| `.github/bible/bible_queue.py:664` | if | Open sessions exist | Follows the first one. |
| `.github/bible/bible_queue.py:666` | if | Session was released | Returns released status. |
| `.github/bible/bible_queue.py:672` | if | No component issue exists | Returns not started. |
| `.github/bible/bible_queue.py:676` | if | Component status is done | Runs the gate. |
| `.github/bible/bible_queue.py:677` | if | Gate fails | Starts another chunk. |
| `.github/bible/bible_queue.py:684` | if | Open hold exists | Handles the hold. |
| `.github/bible/bible_queue.py:686` | if | Hold still needs a person | Returns human-needed. |
| `.github/bible/bible_queue.py:693` | conditional expression | Completed verifications exist | Parses their report. |
| `.github/bible/bible_queue.py:709` | if | Clean matching PASS exists | Creates final PR. |
| `.github/bible/bible_queue.py:710` | if | Verification rounds are exhausted | Creates human hold. |
| `.github/bible/bible_queue.py:729` | if | Report requires revision | Starts a revision chunk. |
| `.github/bible/bible_queue.py:738` | return | Verification is needed | Creates verification issue and returns. |

#### `Queue.follow(analysis, name, issue)`

Source: `.github/bible/bible_queue.py:753-810` <!-- code: d30979e2d28a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:671`) |
| Calls | `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `str.startswith`, `os.path.basename`, `join`, `status_of`, `as_int`, `status.get`, `issue.get`, `any`, `gh.file`, `gh.label`, `gh.merge`, `gh.unlabel`, `gh.close` |
| Purpose | Checks an assigned chunk or verification session and its PR, then retries, holds, waits, or validates and merges it. |

**Steps**

1. Sets the branch to `bible/<name>`, derives `verify` versus `chunk` from issue labels, and classifies the session. Waiting returns `session starting`; start-error is held; no-start retries; running returns `<kind> running`. (`.github/bible/bible_queue.py:664-676`)
2. Builds the component ledger path. Chunk PRs may write component LLD, API LLD, and ledger files except basenames beginning `verification-`; verification PRs may write only verification-prefixed files and `citations.tsv` within that ledger. (`.github/bible/bible_queue.py:677-684`)
3. If any PR file is outside the session allowlist, retries or returns needs-person; otherwise loads component status at the PR head SHA. (`.github/bible/bible_queue.py:685-688`)
4. For chunk sessions, `WAITING_ANSWER` adds waiting labels to the issue and PR if the issue lacks the label, then returns the answer-wait state. Otherwise it compares packet counts on the PR and branch, identifies revisions from issue text, and considers either a larger packet count or `COMPONENT_DONE` as progress. (`.github/bible/bible_queue.py:689-697`)
5. A `STOP` status or lack of progress is retried/held. A revision must change an allowed page or `revision-log.md` and end at `COMPONENT_DONE`; otherwise it is retried/held. (`.github/bible/bible_queue.py:698-708`)
6. For verification sessions, a missing report at the PR head SHA is retried/held. If validation passes, merges the PR, removes the waiting label, closes the issue, and returns `<kind> merged`. (`.github/bible/bible_queue.py:709-715`)

**Pseudo-code**

```text
kind = verify if verification label else chunk
state, pr = session(...)
if waiting/start-error/no-start/running: handle it and return
find PR files outside this kind's allowed paths
if bad files: fail_or_retry; return starting or needs-person
status = component status at PR head
if chunk:
    if WAITING_ANSWER: label issue and PR if needed; return waiting for answers
    before = branch packet count
    if STOP or no packet progress: fail_or_retry; return
    if revision changed no page/log: fail_or_retry; return
    if revision did not reach COMPONENT_DONE: fail_or_retry; return
elif verification report missing: fail_or_retry; return
merge PR; remove waiting label; close issue
return kind + " merged"
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:665` | conditional expression | Issue labels include `bible-verify` | Sets kind to verify; otherwise chunk. |
| `.github/bible/bible_queue.py:667` | if | Session state is `waiting` | Returns `session starting`. |
| `.github/bible/bible_queue.py:669` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:672` | if | Session state is `no-start` | Retries and returns starting or needs-person. |
| `.github/bible/bible_queue.py:674` | conditional expression | Retry succeeded | Returns `session starting`; otherwise returns needs-person. |
| `.github/bible/bible_queue.py:675` | if | Session state is `running` | Returns `<kind> running`. |
| `.github/bible/bible_queue.py:678` | if | Kind is `chunk` | Applies the chunk allowlist; otherwise applies the verification allowlist. |
| `.github/bible/bible_queue.py:685` | if | At least one changed PR file is disallowed | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:687` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:689` | if | Kind is `chunk` | Validates chunk status; otherwise checks for a verification report. |
| `.github/bible/bible_queue.py:690` | if | Chunk status is `WAITING_ANSWER` | Checks whether waiting labels must be added. |
| `.github/bible/bible_queue.py:691` | if | Issue lacks `bible-waiting-answer` | Adds the label to issue and PR. |
| `.github/bible/bible_queue.py:698` | if | Status is `STOP` or packet progress is false | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:700` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:702` | if | A revision has no changed file under its allowed pages or revision log | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:705` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:706` | if | Issue is a revision and state is not `COMPONENT_DONE` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:708` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:709` | elif | Verification PR has no report at its head SHA | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:711` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:755` | if | Session is waiting | Returns session starting. |
| `.github/bible/bible_queue.py:757` | if | Session has start error | Holds it. |
| `.github/bible/bible_queue.py:759` | if | Session has no start | Retries it. |
| `.github/bible/bible_queue.py:762` | if | Session is running | Returns running. |
| `.github/bible/bible_queue.py:764` | if | PR file list is incomplete | Retries or holds. |
| `.github/bible/bible_queue.py:765` | except | File listing raises | Handles the retry. |
| `.github/bible/bible_queue.py:770` | if | A changed file is disallowed | Retries or holds. |
| `.github/bible/bible_queue.py:772` | conditional expression | Retry succeeds | Returns starting. |
| `.github/bible/bible_queue.py:773` | if | Chunk status is waiting | Adds waiting labels. |
| `.github/bible/bible_queue.py:780` | if | Status is stop or no progress | Retries or holds. |
| `.github/bible/bible_queue.py:782` | conditional expression | Retry succeeds | Returns starting. |
| `.github/bible/bible_queue.py:784` | if | Revision changed no allowed page | Retries or holds. |
| `.github/bible/bible_queue.py:785` | conditional expression | Retry succeeds | Returns starting. |
| `.github/bible/bible_queue.py:786` | if | Revision is not done | Retries or holds. |
| `.github/bible/bible_queue.py:793` | conditional expression | Retry succeeds | Returns starting. |
| `.github/bible/bible_queue.py:795` | elif | Verification report is absent | Retries or holds. |
| `.github/bible/bible_queue.py:797` | conditional expression | Retry succeeds | Returns starting. |
| `.github/bible/bible_queue.py:800` | if | Chunk is waiting for answers | Returns waiting. |
| `.github/bible/bible_queue.py:801` | if | Issue lacks waiting label | Adds labels. |
| `.github/bible/bible_queue.py:803` | if | Progress is absent | Retries or holds. |
| `.github/bible/bible_queue.py:804` | if | Revision lacks allowed changes | Retries or holds. |
| `.github/bible/bible_queue.py:806` | if | Verification has no report | Retries or holds. |

#### `Queue.check(analysis, name, branch)`

Source: `.github/bible/bible_queue.py:812-837` <!-- code: 181278d76a48 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:603`) |
| Calls | `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `printed.stdout.strip`, `().splitlines`, `run.stdout.strip` |
| Purpose | Runs the component coverage gate against an unpacked branch tarball and obtains its pages fingerprint. |

**Steps**

1. Builds the analysis script path. If `coverage.py` is absent, logs that the gate is skipped and treated as failing, then returns `(False, None)`. (`.github/bible/bible_queue.py:719-722`)
2. Creates a temporary directory, downloads and extracts the branch tarball there, and runs isolated `coverage.py` with repository, analysis, configured depth, component, and report arguments. (`.github/bible/bible_queue.py:723-728`)
3. Logs the last stripped coverage output line or `no output`, runs isolated `status.py --fingerprint --component`, then returns whether coverage exited successfully and the stripped fingerprint output or `None`. (`.github/bible/bible_queue.py:729-732`)
4. Removes the temporary directory in `finally`, ignoring removal errors. (`.github/bible/bible_queue.py:733-734`)

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
| `.github/bible/bible_queue.py:720` | if | `coverage.py` is not a file | Logs the missing checker and returns failure with no fingerprint. |
| `.github/bible/bible_queue.py:815` | if | Coverage script is absent | Logs and fails the gate. |
| `.github/bible/bible_queue.py:822` | try | Gate work is active | Downloads, runs coverage and reads fingerprint. |
| `.github/bible/bible_queue.py:833` | finally | Gate work ends | Removes the temporary directory. |


#### `Queue.assemble_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:839-907` <!-- code: 9aa48c7b485e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:607`) |
| Calls | `any`, `self.run_issues`, `gh.create_issue`, `settings.get`, `self.held`, `self.session`, `issue_text`, `assignment`, `gh.close`, `self.hold_start_error`, `self.fail_or_retry`, `i.get`, `gh.linked_prs`, `report_facts`, `p.get`, `gh.is_agent_pr`, `gh.file`, `get`, `gh.comment` |
| Purpose | Runs assembly and whole-analysis verification sessions after all selected components merge, then closes the tracker when both finish. |

**Steps**

1. Iterates the `bible-assemble` and `bible-verify-all` phases in order, selecting each phase's model, title, and optional issue-text filename. Skips a phase with any completed closed issue. (`.github/bible/bible_queue.py:738-742`)
2. For an open phase issue, finds linked PRs that are merged into the default branch, from this repository, and agent-authored. For a merged verify-all PR, reads the report and returns a human-needed message if it is missing, not PASS, or has major corrections; otherwise closes the issue and advances. (`.github/bible/bible_queue.py:743-755`)
3. If there is no qualifying merged PR, returns human-needed for a held issue; otherwise classifies its session. Holds start-error, requests retry for no-start, and returns PR-review status when a PR exists or the current session state. (`.github/bible/bible_queue.py:756-764`)
4. With no open issue, reads `assemble.md` for the assembly phase or builds whole-analysis verification instructions; creates an assigned issue and returns the phase's assigned status. (`.github/bible/bible_queue.py:765-773`)
5. After both phases complete, comments that the run is done, closes the tracker, and returns `done`. (`.github/bible/bible_queue.py:774-776`)

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
| `.github/bible/bible_queue.py:738` | for | For the assemble and verify-all phases | Processes the phases in order. |
| `.github/bible/bible_queue.py:741` | if | A completed closed issue exists for this phase | Skips to the next phase. |
| `.github/bible/bible_queue.py:744` | if | At least one open issue exists for the phase | Processes its first open issue. |
| `.github/bible/bible_queue.py:748` | if | A qualifying merged agent PR exists | Closes/advances, or validates verify-all results. |
| `.github/bible/bible_queue.py:749` | if | Current phase is `bible-verify-all` | Checks the whole-analysis verification report. |
| `.github/bible/bible_queue.py:751` | if | Report is missing, verdict is not PASS, or major corrections exist | Returns a human-needed verification message. |
| `.github/bible/bible_queue.py:753` | conditional expression | Report facts exist | Includes the verdict; otherwise reports `missing`. |
| `.github/bible/bible_queue.py:756` | if | Open issue is held | Returns the human-needed issue number. |
| `.github/bible/bible_queue.py:759` | if | Session state is `start-error` | Holds the issue and returns human-needed. |
| `.github/bible/bible_queue.py:762` | if | Session state is `no-start` | Invokes retry logic. |
| `.github/bible/bible_queue.py:764` | conditional expression | PR exists | Returns PR review instruction; otherwise returns session state. |
| `.github/bible/bible_queue.py:765` | if | Phase has a `text` filename | Loads issue title/body from that ledger file; otherwise uses verify-all instructions. |
| `.github/bible/bible_queue.py:841` | for | Assembly and verification phases | Processes each phase in order. |
| `.github/bible/bible_queue.py:845` | if | Completed phase exists | Skips that phase. |
| `.github/bible/bible_queue.py:850` | if | Verification phase has completed work | Invokes revision handling. |
| `.github/bible/bible_queue.py:852` | if | Open phase issue exists | Processes it. |
| `.github/bible/bible_queue.py:855` | if | Merged PR exists | Closes/advances the issue. |
| `.github/bible/bible_queue.py:856` | if | Verification report is not clean | Marks correction needed. |
| `.github/bible/bible_queue.py:857` | if | Report facts are absent | Reports missing verdict. |
| `.github/bible/bible_queue.py:859` | if | Issue is held | Returns human-needed. |
| `.github/bible/bible_queue.py:861` | if | Session has start error | Holds it. |
| `.github/bible/bible_queue.py:864` | if | Session has no start | Retries it. |
| `.github/bible/bible_queue.py:868` | if | Finished PR lacks final marker | Requests continuation. |
| `.github/bible/bible_queue.py:869` | if | Continuation returns a status | Returns it. |
| `.github/bible/bible_queue.py:871` | return | Open session has no PR | Returns session state. |
| `.github/bible/bible_queue.py:876` | if | Assembly issue text exists | Loads it. |
| `.github/bible/bible_queue.py:878` | else | No issue text file | Builds verification instructions. |
| `.github/bible/bible_queue.py:881` | call | Phase issue creation | Assigns the selected model. |
| `.github/bible/bible_queue.py:884` | return | Phase issue created | Reports assigned status. |
| `.github/bible/bible_queue.py:887` | call | All phases complete | Comments tracker completion. |
| `.github/bible/bible_queue.py:889` | call | All phases complete | Closes tracker. |
| `.github/bible/bible_queue.py:891` | return | All phases complete | Returns done. |
| `.github/bible/bible_queue.py:893` | if | Verification issue needs revision | Labels it. |
| `.github/bible/bible_queue.py:895` | if | Verification report exists | Reads facts. |
| `.github/bible/bible_queue.py:896` | return | Phase status is determined | Returns the phase status. |

#### `Queue.revise_all_step(tracker, analysis)`

Source: `.github/bible/bible_queue.py:909-979` <!-- code: ecf0e4db8193 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:860`) |
| Calls | `self.run_issues`, `gh.close`, `labels_of`, `max`, `h.get`, `sorted`, `i.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `gh.linked_prs`, `p.get`, `gh.is_agent_pr`, `gh.pr_files`, `get`, `startswith`, `os.path.basename`, `join` |
| Purpose | Coordinates whole-analysis revision sessions after a verification requests corrections, with bounded retries and human holds. |

**Steps**

1. Closes a released whole-analysis hold or returns a human-needed status for a held one. (`.github/bible/bible_queue.py:916-926`)
2. Finds completed whole-verification issues requesting revision, counts revisions since the last release, and handles an open revision issue through merged PR, hold, session, retry, continuation, and file-scope checks. (`.github/bible/bible_queue.py:931-951`)
3. Returns after a completed revision, creates a human hold at `MAX_VERIFY_ROUNDS`, or creates and assigns a revision issue with the skill instructions. (`.github/bible/bible_queue.py:955-979`)

**Pseudo-code**

```text
close released hold or return human-needed
find latest correction verdict and open revision
handle merged, held, running, retry and continuation states
if rounds exhausted: create human hold
otherwise create revision issue
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:916` | if | Open hold needs a person | Returns human-needed. |
| `.github/bible/bible_queue.py:917` | if | Hold was released | Closes it and reloads holds. |
| `.github/bible/bible_queue.py:926` | if | No correction verdict exists | Returns no work. |
| `.github/bible/bible_queue.py:931` | if | Revision issue is open | Processes it. |
| `.github/bible/bible_queue.py:935` | if | Revision PR is merged | Closes issue and returns. |
| `.github/bible/bible_queue.py:938` | if | Revision issue is held | Returns human-needed. |
| `.github/bible/bible_queue.py:941` | if | Revision session is running | Returns running. |
| `.github/bible/bible_queue.py:944` | if | Revision session has no start | Retries. |
| `.github/bible/bible_queue.py:947` | if | Revision PR is finished | Continues or validates it. |
| `.github/bible/bible_queue.py:949` | if | Revision writes disallowed files | Retries or holds. |
| `.github/bible/bible_queue.py:951` | conditional expression | Retry succeeds | Returns starting. |
| `.github/bible/bible_queue.py:955` | if | Corrections already applied | Returns no work. |
| `.github/bible/bible_queue.py:958` | if | Revision rounds exhausted | Creates human hold. |
| `.github/bible/bible_queue.py:959` | if | Revision round remains | Builds revision instructions. |
| `.github/bible/bible_queue.py:961` | call | Revision issue creation | Assigns the configured model. |
| `.github/bible/bible_queue.py:963` | return | Revision issue created | Reports assigned status. |

#### `Queue.continue_if_unfinished(issue, pr, kind, analysis)`

Source: `.github/bible/bible_queue.py:981-1019` <!-- code: 607ef9d1096b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:892`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:950`) |
| Calls | `gh.pr_files`, `gh.me`, `max`, `e.get`, `gh.timeline`, `get`, `sorted`, `age`, `len`, `labels_of`, `gh.label`, `gh.comment`, `self.settings.get` |
| Purpose | Continues a finished session whose required marker file is absent, up to a bounded number of continuation requests. |

**Steps**

1. Returns `None` when the required status or verification report is already in the PR files. (`.github/bible/bible_queue.py:989-990`)
2. Reads release, finish, and prior continuation events, returning a continuing status when Copilot has been asked and has not started yet. (`.github/bible/bible_queue.py:990-1001`)
3. Holds the issue after `MAX_CONTINUE` requests; otherwise comments a continuation command and returns the next session number. (`.github/bible/bible_queue.py:1003-1019`)

**Pseudo-code**

```text
if marker in PR files: return None
collect release, finish and continuation events
if pending continuation: return continuing
if continuation limit reached: label and hold
comment a continuation command; return continuing
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:989` | if | Required marker is present | Returns None. |
| `.github/bible/bible_queue.py:990` | assignment | Marker is absent | Collects events. |
| `.github/bible/bible_queue.py:1001` | if | A recent continuation is pending | Returns continuing. |
| `.github/bible/bible_queue.py:1003` | if | Continuation count reaches the limit | Labels and holds the issue. |
| `.github/bible/bible_queue.py:1004` | if | Continuation is still allowed | Posts the continuation comment. |

#### `Queue.render(tracker, settings, rows)`

Source: `.github/bible/bible_queue.py:1021-1031` <!-- code: 651906b39ffd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:584`, `.github/bible/bible_queue.py:608`), `Queue.plan_phase` (`.github/bible/bible_queue.py:621`, `.github/bible/bible_queue.py:624`, `.github/bible/bible_queue.py:628`, `.github/bible/bible_queue.py:631`) |
| Calls | `rows.items`, `().isoformat`, `json.dumps`, `now`, `join`, `self.gh.set_body`, `body.split`, `split`, `tracker.get`, `self.log` |
| Purpose | Renders tracker status rows and settings, updates the issue body when its non-time content differs, and logs each row. |

**Steps**

1. Builds the introductory text and table headings, then appends one formatted row for each component/state pair. (`.github/bible/bible_queue.py:1022-1024`)
2. Adds a minute-resolution timestamp from `now()` and the hidden JSON settings marker, then joins the lines into the issue body. (`.github/bible/bible_queue.py:1025-1027`)
3. Updates the tracker body only when the body prefix before `Updated` differs from the current tracker body prefix. (`.github/bible/bible_queue.py:1028-1029`)
4. Logs each row with a padded key and its state. (`.github/bible/bible_queue.py:1030-1031`)

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
| `.github/bible/bible_queue.py:1028` | if | Text before `Updated` differs | Replaces the tracker body. |
| `.github/bible/bible_queue.py:1030` | for | For each `(key, value)` row | Logs that row. |

#### `Queue.delta(changed, settings_analysis="codebase-analysis")`

Source: `.github/bible/bible_queue.py:1034-1077` <!-- code: 51236d758116 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1124`) |
| Calls | `gh.default_branch`, `json_file`, `self.log`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `sorted`, `().values`, `components.component_map`, `p.startswith`, `gh.issues`, `gh.create_issue`, `assignment`, `comp_label`, `join`, `len`, `components.assign` |
| Purpose | Creates one update issue for each analysis component affected by changed files when an assembled baseline exists. |

**Steps**

1. Reads the default branch, loads `components.json`, and checks for `ledger/baseline.json`; if the catalog or baseline is absent, logs and returns. (`.github/bible/bible_queue.py:1038-1049`)
2. Imports the component toolkit, maps changed paths outside the analysis and `.github/` folders to sorted touched components, and filters paths to safe issue-file syntax. (`.github/bible/bible_queue.py:1051-1059`)
3. For each touched component, selects assigned changed files and skips creating a duplicate when a matching delta issue is open. (`.github/bible/bible_queue.py:1064-1066`)
4. Creates a labeled delta issue with component/base/attempt context, changed file names, update instructions, and assignment, then logs its creation. (`.github/bible/bible_queue.py:1067-1077`)

**Pseudo-code**

```text
default = gh.default_branch()
catalog = json_file(components.json)
if catalog is falsey or baseline is missing/falsey: log; return
load components toolkit
touched = sorted unique mapped components for changed paths outside analysis and .github
for each touched component:
    files = changed paths assigned to it
    if any matching delta issue is open: log; continue
    create assigned delta issue with changed files and update instructions
    log file count
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1038` | if | Catalog or baseline is absent | Logs and returns. |
| `.github/bible/bible_queue.py:1049` | return | No assembled analysis exists | Stops without creating issues. |
| `.github/bible/bible_queue.py:1051` | call | Toolkit import is needed | Adds scripts to `sys.path`. |
| `.github/bible/bible_queue.py:1059` | for | Changed paths are mapped | Builds touched component names. |
| `.github/bible/bible_queue.py:1064` | for | Each touched component | Selects files and checks issues. |
| `.github/bible/bible_queue.py:1074` | if | Matching delta issue is open | Logs and skips a duplicate. |

## Functions and methods

### `main()`

Source: `.github/bible/bible_queue.py:1080-1126` <!-- code: d5e645d7911f -->

| | |
| --- | --- |
| Kind | module entry point |
| Called by | Module guard (`.github/bible/bible_queue.py:1129-1130`) |
| Calls | `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str`, `args.verify_model.strip`, `args.components.split`, `json.dumps`, `issue.get`, `open`, `l.strip`, `NAME.match` |
| Purpose | Parses `start`, `reconcile`, and `delta` commands and dispatches to the queue workflow. |

**Steps**

1. Builds a required-subcommand parser from the module docstring's first line; defines `start` options including `--analysis` and `--depth`, `reconcile`, and `delta` options, then parses arguments. (`.github/bible/bible_queue.py:1081-1094`)
2. Reads `GITHUB_REPOSITORY` and `GH_TOKEN`; raises `SystemExit` if either is falsey, then constructs `GitHub` and `Queue`. (`.github/bible/bible_queue.py:1096-1100`)
3. For `start`, requires a nonempty verification model different from the normal model, parses component names, and requires at least one selection with each name either `all` or matching `NAME`. (`.github/bible/bible_queue.py:1102-1107`)
4. Ensures labels and exits if a tracker is already open. Builds settings, then calls `settings_of` on the generated marker; if validation rejects the settings, raises `SystemExit` explaining the allowed analysis path, depth, and model characters. Otherwise it creates a tracker issue with hidden settings JSON and prints its issue number and queue-start guidance. (`.github/bible/bible_queue.py:1108-1118`)
5. For `reconcile`, invokes `queue.reconcile`; otherwise reads nonempty stripped lines from the changed-file input and calls `queue.delta`. (`.github/bible/bible_queue.py:1119-1124`)
6. Converts `RuntimeError` from command handling to `SystemExit` with the error text. (`.github/bible/bible_queue.py:1125-1126`)

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
        if settings_of(generated settings marker) is None:
            exit because analysis, depth, or model settings are unsafe or unsupported
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
| `.github/bible/bible_queue.py:1097` | if | Repository or token is missing | Exits with an environment requirement. |
| `.github/bible/bible_queue.py:1098` | raise | Required environment is missing | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1102` | if | Command is `start` | Validates and starts a run. |
| `.github/bible/bible_queue.py:1103` | if | Verification model is empty or equals normal model | Exits with the model requirement. |
| `.github/bible/bible_queue.py:1104` | raise | Model validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1106` | if | No component names are supplied, or a name other than `all` fails `NAME` | Exits with component-selection guidance. |
| `.github/bible/bible_queue.py:1107` | raise | Selection validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1109` | if | Tracker already exists | Exits without starting another run. |
| `.github/bible/bible_queue.py:1110` | raise | Open tracker exists | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1113` | if | Generated settings fail `settings_of` validation | Exits with the settings requirement. |
| `.github/bible/bible_queue.py:1114-1115` | raise | Generated settings are unsafe or unsupported | Raises `SystemExit` with allowed path, depth, and model rules. |
| `.github/bible/bible_queue.py:1119` | elif | Command is `reconcile` | Calls `queue.reconcile`. |
| `.github/bible/bible_queue.py:1121` | else | Command is `delta` | Reads changed paths and calls `queue.delta`. |
| `.github/bible/bible_queue.py:1125` | except | Command handling raises `RuntimeError` | Converts it to `SystemExit`. |
| `.github/bible/bible_queue.py:1126` | raise | A `RuntimeError` was caught | Raises `SystemExit` with the error text. |
| `.github/bible/bible_queue.py:1129` | if | Module is run as a script | Calls `main`. |
| `.github/bible/bible_queue.py:1130` | call | Script guard is active | Dispatches the CLI entry point. |

### `now()`

Source: `.github/bible/bible_queue.py:337-339` <!-- code: 9fb56903ebfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `age` (`.github/bible/bible_queue.py:343`), `Queue.render` (`.github/bible/bible_queue.py:888`) |
| Calls | `os.environ.get`, `datetime.datetime.fromisoformat`, `datetime.datetime.now`, `replace` |
| Purpose | Returns the configured test time or the current UTC time. |

**Steps**

1. Reads `BIBLE_NOW`. (`.github/bible/bible_queue.py:338`)
2. If set, replaces `Z` with `+00:00` and parses the ISO timestamp; otherwise returns the current timezone-aware UTC datetime. (`.github/bible/bible_queue.py:339`)

**Pseudo-code**

```text
stamp = BIBLE_NOW
if stamp: parse ISO stamp after replacing Z with +00:00
else: return current UTC time
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:339` | conditional expression | `stamp` is truthy | Parses the configured time; otherwise obtains current UTC time. |

### `age(stamp)`

Source: `.github/bible/bible_queue.py:342-343` <!-- code: f2f8bb65e56f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:555`), `main` (`.github/bible/bible_queue.py:1113`) |
| Calls | `now`, `datetime.datetime.fromisoformat`, `replace`, `total_seconds` |
| Purpose | Returns elapsed seconds between `stamp` and `now()`. |

**Steps**

1. Replaces `Z` in `stamp` with `+00:00`, parses it as an ISO datetime, subtracts it from `now()`, and returns `total_seconds()`. (`.github/bible/bible_queue.py:343`)

**Pseudo-code**

```text
return (now() - parse ISO stamp after replacing Z with +00:00).total_seconds()
```

### `settings_of(tracker)`

Source: `.github/bible/bible_queue.py:353-373` <!-- code: 828d76009663 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:555`), `main` (`.github/bible/bible_queue.py:1113`) |
| Calls | `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group`, `isinstance`, `str`, `data.get`, `SAFE_PATH.match`, `analysis.split`, `SAFE_MODEL.match` |
| Purpose | Parses and validates the JSON settings marker from a tracker, returning `None` when absent, malformed, or unsafe. |

**Steps**

1. Searches the tracker body, defaulting a missing or falsey body to an empty string, and parses the marker's first capture group when present. (`.github/bible/bible_queue.py:359-360`)
2. Returns `None` for invalid JSON or a non-dictionary parsed value. (`.github/bible/bible_queue.py:361-362`)
3. Reads `analysis`, defaulting to `codebase-analysis`, and rejects paths that fail `SAFE_PATH` or contain `..` path segments. (`.github/bible/bible_queue.py:363-365`)
4. Rejects depths outside `DEPTH_VALUES`, and rejects nonempty `model` or `verify_model` values that fail `SAFE_MODEL`. (`.github/bible/bible_queue.py:366-371`)
5. Returns the validated settings dictionary. (`.github/bible/bible_queue.py:373`)

**Pseudo-code**

```text
match = SETTINGS search in tracker.body or ""
try:
    data = parse match group 1 if matched, otherwise None
on ValueError: return None
if data is not a dict: return None
analysis = data.analysis or "codebase-analysis"
if analysis fails SAFE_PATH or contains ".." path segments: return None
if data.depth or "deep" is not in DEPTH_VALUES: return None
for model and verify_model:
    if nonempty value fails SAFE_MODEL: return None
return data
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:359` | conditional expression | A settings marker matched | Parses its first group; otherwise uses `None`. |
| `.github/bible/bible_queue.py:360` | except | JSON parsing raises `ValueError` | Returns `None`. |
| `.github/bible/bible_queue.py:362` | if | Parsed value is not a dictionary | Returns `None`. |
| `.github/bible/bible_queue.py:365` | if | Analysis path is unsafe | Returns `None`. |
| `.github/bible/bible_queue.py:367` | if | Depth is not an allowed value | Returns `None`. |
| `.github/bible/bible_queue.py:369` | for | For `model` and `verify_model` | Validates each configured model value. |
| `.github/bible/bible_queue.py:371` | if | A nonempty model fails `SAFE_MODEL` | Returns `None`. |

### `labels_of(item)`

Source: `.github/bible/bible_queue.py:376-377` <!-- code: 7a809f2b23af -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `item.get`, `isinstance` |
| Purpose | Returns a set of label names from strings or label objects. |

**Steps**

1. Reads `labels`, defaulting to an empty list; for each element, uses its `name` when it is a dictionary and otherwise keeps the element itself. (`.github/bible/bible_queue.py:377`)

**Pseudo-code**

```text
return {label["name"] if label is a dict else label
        for label in item.labels or []}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:377` | conditional expression | A label item is a dict | Uses `item["name"]`; otherwise preserves the item value. |

### `comp_label(name)`

Source: `.github/bible/bible_queue.py:380-381` <!-- code: 5ead08c5004d -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Prefixes a component name with `bible/`. |

**Steps**

1. Returns the string `bible/` followed by `name`. (`.github/bible/bible_queue.py:381`)

**Pseudo-code**

```text
return "bible/" + name
```

### `issue_text(gh, path, ref, fallback_title)`

Source: `.github/bible/bible_queue.py:384-390` <!-- code: 0533b3261be5 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `gh.file`, `splitlines`, `startswith`, `strip`, `join`, `len` |
| Purpose | Reads a title/body pair from a ledger issue file, with a fallback title when no header exists. |

**Steps**

1. Reads the file through `gh.file`, converting a falsey result to `""`, then splits it into lines. (`.github/bible/bible_queue.py:386-387`)
2. If the first line starts with `Title:`, returns its stripped suffix as the title and the stripped remaining lines joined by newlines as the body. (`.github/bible/bible_queue.py:388-389`)
3. Otherwise returns `fallback_title` and the stripped full text. (`.github/bible/bible_queue.py:390`)

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
| `.github/bible/bible_queue.py:388` | if | `lines` is nonempty and the first line starts with `Title:` | Returns header title and remaining body; otherwise returns fallback title and full text. |

### `assignment(gh, base, model)`

Source: `.github/bible/bible_queue.py:393-397` <!-- code: da5ca422ae7f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Builds the target repository and base-branch assignment, optionally including a model. |

**Steps**

1. Initializes the result with `target_repo: gh.repo` and `base_branch: base`. (`.github/bible/bible_queue.py:394`)
2. Adds `model` only when truthy, then returns the result. (`.github/bible/bible_queue.py:395-397`)

**Pseudo-code**

```text
out = {target_repo: gh.repo, base_branch: base}
if model: out.model = model
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:395` | if | `model` is truthy | Adds `model` to the assignment. |

### `json_file(gh, path, ref)`

Source: `.github/bible/bible_queue.py:400-405` <!-- code: 37acfbecddfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `status_of` (`.github/bible/bible_queue.py:442`), queue functions in later source packets. |
| Calls | `gh.file`, `json.loads` |
| Purpose | Reads a file and parses JSON, returning `None` for missing or invalid content. |

**Steps**

1. Reads the file using `gh.file`. (`.github/bible/bible_queue.py:401`)
2. Returns parsed JSON for truthy text, or `None` when the text is falsey. (`.github/bible/bible_queue.py:402-403`)
3. Returns `None` if parsing raises `ValueError`. (`.github/bible/bible_queue.py:404-405`)

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
| `.github/bible/bible_queue.py:403` | conditional expression | `text` is truthy | Parses JSON; otherwise returns `None`. |
| `.github/bible/bible_queue.py:404` | except | JSON parsing raises `ValueError` | Returns `None`. |

### `section(text, title)`

Source: `.github/bible/bible_queue.py:408-414` <!-- code: 55167fd6e3c2 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `report_facts` (`.github/bible/bible_queue.py:427`), queue functions in later source packets. |
| Calls | `re.search`, `re.escape`, `match.end`, `nxt.start` |
| Purpose | Returns a Markdown level-two section's text, or an empty string if its heading is absent. |

**Steps**

1. Searches for a line matching exactly a level-two heading with the escaped `title`. (`.github/bible/bible_queue.py:409`)
2. Returns `""` if no heading matches. (`.github/bible/bible_queue.py:410-411`)
3. Slices text after the matched heading through the next level-two heading, or through end of text when there is no next heading. (`.github/bible/bible_queue.py:412-414`)

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
| `.github/bible/bible_queue.py:410` | if | No heading matched | Returns an empty string. |
| `.github/bible/bible_queue.py:414` | conditional expression | A next level-two heading matched | Returns the section before it; otherwise returns the remaining text. |

### `report_facts(text)`

Source: `.github/bible/bible_queue.py:417-430` <!-- code: a367c151c5b0 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `re.sub`, `re.findall`, `len`, `sum`, `splitlines`, `startswith`, `re.search`, `section`, `lstrip`, `upper`, `printed.group` |
| Purpose | Extracts a verification verdict, major-correction count, and optional analysis fingerprint. |

**Steps**

1. Returns `None` for falsey `text`. (`.github/bible/bible_queue.py:420-421`)
2. Removes HTML comments and fenced code blocks, then finds visible `Verdict` values and rows. (`.github/bible/bible_queue.py:422-424`)
3. Returns `("UNREADABLE", 0, None)` unless exactly one accepted verdict and exactly one verdict row were found. (`.github/bible/bible_queue.py:425-426`)
4. Counts lines in the `Corrections` section that begin with `|` and contain a `major` cell. (`.github/bible/bible_queue.py:427-428`)
5. Searches for a 16-character lowercase hexadecimal fingerprint and returns the uppercased verdict, count, and captured fingerprint or `None`. (`.github/bible/bible_queue.py:429-430`)

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
| `.github/bible/bible_queue.py:420` | if | `text` is falsey | Returns `None`. |
| `.github/bible/bible_queue.py:425` | if | Verdict or verdict-row count is not exactly one | Returns `("UNREADABLE", 0, None)`. |
| `.github/bible/bible_queue.py:430` | conditional expression | Fingerprint regex matched | Returns its group 1; otherwise returns `None` in that tuple position. |

### `as_int(value)`

Source: `.github/bible/bible_queue.py:433-437` <!-- code: 8081107d37e4 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `int` |
| Purpose | Converts a value to an integer, returning zero for `TypeError` or `ValueError`. |

**Steps**

1. Returns `int(value)` when conversion succeeds. (`.github/bible/bible_queue.py:434-435`)
2. Returns `0` when conversion raises `TypeError` or `ValueError`. (`.github/bible/bible_queue.py:436-437`)

**Pseudo-code**

```text
try: return int(value)
on TypeError or ValueError: return 0
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:436` | except | `int(value)` raises `TypeError` or `ValueError` | Returns zero. |

### `status_of(gh, path, ref)`

Source: `.github/bible/bible_queue.py:440-443` <!-- code: ad9adb38e0f7 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `json_file`, `isinstance` |
| Purpose | Returns parsed component status only when the loaded JSON is a dictionary. |

**Steps**

1. Loads `path` at `ref` with `json_file`. (`.github/bible/bible_queue.py:442`)
2. Returns the loaded data if it is a dictionary; otherwise returns `{}`. (`.github/bible/bible_queue.py:443`)

**Pseudo-code**

```text
data = json_file(gh, path, ref)
return data if data is a dict, otherwise {}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:443` | conditional expression | `data` is a dictionary | Returns `data`; otherwise returns `{}`. |

## Module-level code

The module imports Python standard-library utilities and initializes queue labels, environment-derived agent settings, regexes, and timing/verification constants. (`.github/bible/bible_queue.py:42-83`)

It declares the `GitHub` API client (`.github/bible/bible_queue.py:88-302`), helper functions (`.github/bible/bible_queue.py:307-391`), and `Queue` coordinator (`.github/bible/bible_queue.py:396-817`). The CLI `main` parses arguments, and the module guard calls it when executed as a script. (`.github/bible/bible_queue.py:820-867`)

## Surprises

`tarball` filters archive members to regular files and directories and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:275-288`)

The `Queue.session` docstring lists four result states, but the code also returns `start-error` when `GitHub.start_error` is truthy. (`.github/bible/bible_queue.py:465-470`)

`Queue.component` builds `closed_revise` after a human hold but does not use it later in the method; it separately builds and uses `all_revise`. (`.github/bible/bible_queue.py:604-608`, `.github/bible/bible_queue.py:714-720`)

<!-- cites .github/bible/bible_queue.py@68e91ae09c53c283e7402334cfe2a715785b33ed -->
