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
| Lines | 1130 |
| Role | Runs the Mode B analysis queue and its GitHub API client. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, subprocess, and filesystem modules used by the API client, queue, and CLI. (`.github/bible/bible_queue.py:42-55`) |
| Module-level state | `COPILOT`, agent settings, regexes, labels, timeout and continuation limits, archive limit, and verification limits are initialized at import. Environment-backed values include `BIBLE_AGENT_LOGINS`, `BIBLE_AGENT_APP`, and `GITHUB_API_URL`; delta validation uses `SAFE_PATH`, `SAFE_FILE`, `SAFE_MODEL`, and `DEPTH_VALUES`. (`.github/bible/bible_queue.py:59-90`, `.github/bible/bible_queue.py:346-350`) |

## Summary

`main` exposes the `start`, `reconcile`, and `delta` CLI commands. It constructs `Queue` and `GitHub`; `Queue` coordinates tracker/session state and delegates repository operations to `GitHub`, whose methods build REST requests and a GraphQL ready-for-review mutation. `Queue.delta` also imports component-membership helpers from the analysis toolkit. (`.github/bible/bible_queue.py:1080-1130`, `.github/bible/bible_queue.py:448-1078`, `.github/bible/bible_queue.py:88-332`, `.github/bible/bible_queue.py:1034-1077`)

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| `GitHub` | class | 88-332 | [class](#github) |
| `GitHub.__init__` | method | 96-99 | [card](#github__init__repo-token-api-none) |
| `GitHub.request` | method | 101-110 | [card](#githubrequestmethod-url-body-none-timeout-60) |
| `GitHub.call` | method | 112-124 | [card](#githubcallmethod-path-body-none-ok404-false) |
| `GitHub.paged` | method | 126-134 | [card](#githubpagedpath) |
| `GitHub.issues` | method | 136-138 | [card](#githubissueslabels-state-open) |
| `GitHub.ensure_label` | method | 140-145 | [card](#githubensure_labelname-whycodebase-analysis) |
| `GitHub.ensure_labels` | method | 147-149 | [card](#githubensure_labels) |
| `GitHub.create_issue` | method | 151-158 | [card](#githubcreate_issuetitle-body-labels-assign-none) |
| `GitHub.me` | method | 160-164 | [card](#githubme) |
| `GitHub.default_branch` | method | 166-167 | [card](#githubdefault_branch) |
| `GitHub.branch_sha` | method | 169-171 | [card](#githubbranch_shabranch) |
| `GitHub.create_branch` | method | 173-174 | [card](#githubcreate_branchbranch-sha) |
| `GitHub.reset_branch` | method | 176-177 | [card](#githubreset_branchbranch-sha) |
| `GitHub.file` | method | 179-183 | [card](#githubfilepath-ref) |
| `GitHub.prs` | method | 185-187 | [card](#githubprsbase-none-state-open) |
| `GitHub.timeline` | method | 189-190 | [card](#githubtimelinenumber) |
| `GitHub.linked_prs` | method | 192-201 | [card](#githublinked_prsnumber) |
| `GitHub.branch_prs` | method | 203-206 | [card](#githubbranch_prsbranch-base) |
| `GitHub.agent_events` | method | 208-212 | [card](#githubagent_eventsnumber) |
| `GitHub.is_agent_pr` | method | 214-219 | [card](#githubis_agent_prpr) |
| `GitHub.start_error` | method | 221-230 | [card](#githubstart_errorissue) |
| `GitHub.assigned_at` | method | 232-235 | [card](#githubassigned_atissue) |
| `GitHub.pr_files` | method | 237-250 | [card](#githubpr_filesnumber) |
| `GitHub.commit_time` | method | 252-253 | [card](#githubcommit_timesha) |
| `GitHub.tarball` | method | 255-288 | [card](#githubtarballref-dest) |
| `GitHub.label` | method | 290-292 | [card](#githublabelnumber-name) |
| `GitHub.unlabel` | method | 294-295 | [card](#githubunlabelnumber-name) |
| `GitHub.comment` | method | 297-298 | [card](#githubcommentnumber-text) |
| `GitHub.close` | method | 300-301 | [card](#githubclosenumber-reason-completed) |
| `GitHub.set_body` | method | 303-304 | [card](#githubset_bodynumber-body) |
| `GitHub.unassign` | method | 306-307 | [card](#githubunassignnumber) |
| `GitHub.assign` | method | 309-310 | [card](#githubassignnumber-assign) |
| `GitHub.ready` | method | 312-320 | [card](#githubreadypr) |
| `GitHub.merge` | method | 322-326 | [card](#githubmergepr-title) |
| `GitHub.close_pr` | method | 328-329 | [card](#githubclose_prnumber) |
| `GitHub.create_pr` | method | 331-332 | [card](#githubcreate_prhead-base-title-body) |
| `now` | function | 337-339 | [card](#now) |
| `age` | function | 342-343 | [card](#age) |
| `settings_of` | function | 353-373 | [card](#settings_of) |
| `labels_of` | function | 376-377 | [card](#labels_of) |
| `comp_label` | function | 380-381 | [card](#comp_label) |
| `issue_text` | function | 384-390 | [card](#issue_textgh-path-ref-fallback_title) |
| `assignment` | function | 393-397 | [card](#assignmentgh-base-model) |
| `json_file` | function | 400-405 | [card](#json_filegh-path-ref) |
| `section` | function | 408-414 | [card](#sectiontext-title) |
| `report_facts` | function | 417-430 | [card](#report_factstext) |
| `as_int` | function | 433-437 | [card](#as_intvalue) |
| `status_of` | function | 440-443 | [card](#status_ofgh-path-ref) |
| `Queue` | class | 448-1078 | [class](#queue) |
| `Queue.__init__` | method | 449-451 | [card](#queue__init__gh-log-print) |
| `Queue.run_issues` | method | 453-454 | [card](#queue_run_issueslabels-state-open) |
| `Queue.agent_pr` | method | 456-462 | [card](#queue_agent_prissue-base) |
| `Queue.session` | method | 465-481 | [card](#queue_sessionissue-base-analysis-comp-none) |
| `Queue.held` | method | 483-516 | [card](#queue_heldissue) |
| `Queue.model_for` | method | 518-520 | [card](#queue_model_forissue) |
| `Queue.hold_start_error` | method | 522-528 | [card](#queue_hold_start_errorissue) |
| `Queue.fail_or_retry` | method | 530-549 | [card](#queue_fail_or_retryissue-pr-why) |
| `Queue.reconcile` | method | 552-562 | [card](#queue_reconcile) |
| `Queue.run` | method | 564-608 | [card](#queue_runtracker-settings) |
| `Queue.plan_phase` | method | 610-632 | [card](#queue_plan_phasetracker-settings-analysis) |
| `Queue.start_chunk` | method | 634-646 | [card](#queue_start_chunkanalysis-name-fresh-false-note) |
| `Queue.component` | method | 648-751 | [card](#queue_componentanalysis-name) |
| `Queue.follow` | method | 753-810 | [card](#queue_followanalysis-name-issue) |
| `Queue.check` | method | 812-837 | [card](#queue_checkanalysis-name-branch) |
| `Queue.assemble_phase` | method | 839-907 | [card](#queue_assemble_phasetracker-settings-analysis) |
| `Queue.revise_all_step` | method | 909-979 | [card](#queue_revise_all_steptracker-analysis) |
| `Queue.continue_if_unfinished` | method | 981-1019 | [card](#queue_continue_if_unfinishedissue-pr-kind-analysis) |
| `Queue.render` | method | 1021-1031 | [card](#queue_rendertracker-settings-rows) |
| `Queue.delta` | method | 1034-1077 | [card](#queue_deltachanged-settings_analysiscodebase-analysis) |
| `main` | function | 1080-1126 | [card](#main) |

## Call graph

Edges are derived by matching calls to same-file function names; matching names alone can confuse methods with external calls, so consult the cited cards for the receiver.

```mermaid
flowchart LR
  init["GitHub.__init__"]
  me["GitHub.me"]
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
  reviseallstep["Queue.revise_all_step"]
  continueunfinished["Queue.continue_if_unfinished"]
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
  prfiles["GitHub.pr_files"]
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
  held -->|"label"| label
  held -->|"timeline"| timeline
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
  component -->|"as_int"| asint
  component -->|"check"| check
  component -->|"report_facts"| reportfacts
  component -->|"comp_label"| complabel
  follow -->|"session"| session
  follow -->|"fail_or_retry"| failorretry
  follow -->|"labels_of"| labelsof
  follow -->|"status_of"| statusof
  follow -->|"as_int"| asint
  check -->|"tarball"| tarball
  check -->|"subprocess.run"| subprocessrun
  assemblephase -->|"run_issues"| runissues
  assemblephase -->|"continue_if_unfinished"| continueunfinished
  assemblephase -->|"label"| label
  assemblephase -->|"labels_of"| labelsof
  assemblephase -->|"revise_all_step"| reviseallstep
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
  main -->|"create_issue"| createissue
  main -->|"reconcile"| reconcile
  main -->|"delta"| delta
  main -->|"settings_of"| settingsof
  me -->|"call"| call
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
  prfiles -->|"as_int"| asint
  prfiles -->|"call"| call
  prs -->|"paged"| paged
  reconcile -->|"default_branch"| defaultbranch
  reconcile -->|"issues"| issues
  reconcile -->|"settings_of"| settingsof
  render -->|"set_body"| setbody
  reviseallstep -->|"assignment"| assignment
  reviseallstep -->|"close"| close
  reviseallstep -->|"continue_if_unfinished"| continueunfinished
  reviseallstep -->|"create_issue"| createissue
  reviseallstep -->|"fail_or_retry"| failorretry
  reviseallstep -->|"held"| held
  reviseallstep -->|"hold_start_error"| holdstarterror
  reviseallstep -->|"is_agent_pr"| isagent
  reviseallstep -->|"labels_of"| labelsof
  reviseallstep -->|"linked_prs"| linked
  reviseallstep -->|"pr_files"| prfiles
  reviseallstep -->|"run_issues"| runissues
  reviseallstep -->|"session"| session
  continueunfinished -->|"age"| age
  continueunfinished -->|"comment"| comment
  continueunfinished -->|"label"| label
  continueunfinished -->|"labels_of"| labelsof
  continueunfinished -->|"me"| me
  continueunfinished -->|"pr_files"| prfiles
  continueunfinished -->|"timeline"| timeline
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

Source: `.github/bible/bible_queue.py:88-332` <!-- code: fa8466d1289a -->

`GitHub` is a client for repository-scoped GitHub REST operations and the GraphQL ready-for-review mutation. Its instance fields are `repo`, `token`, normalized `api`, and `known_labels`; the last begins as `None` and is populated by `ensure_label`. (`.github/bible/bible_queue.py:89-99`, `.github/bible/bible_queue.py:140-145`)

No type annotations or factory are declared for the class; callers provide its constructor values. (inferred: `.github/bible/bible_queue.py:88-99`)

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
| Called by | `GitHub.paged` (`.github/bible/bible_queue.py:130`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:144`), `GitHub.create_issue` (`.github/bible/bible_queue.py:158`), `GitHub.default_branch` (`.github/bible/bible_queue.py:167`), `GitHub.branch_sha` (`.github/bible/bible_queue.py:170`), `GitHub.create_branch` (`.github/bible/bible_queue.py:174`), `GitHub.reset_branch` (`.github/bible/bible_queue.py:177`), `GitHub.file` (`.github/bible/bible_queue.py:180`), `GitHub.linked_prs` (`.github/bible/bible_queue.py:200`), `GitHub.commit_time` (`.github/bible/bible_queue.py:253`), `GitHub.label` (`.github/bible/bible_queue.py:292`), `GitHub.unlabel` (`.github/bible/bible_queue.py:295`), `GitHub.comment` (`.github/bible/bible_queue.py:298`), `GitHub.close` (`.github/bible/bible_queue.py:301`), `GitHub.set_body` (`.github/bible/bible_queue.py:304`), `GitHub.unassign` (`.github/bible/bible_queue.py:307`), `GitHub.assign` (`.github/bible/bible_queue.py:310`), `GitHub.merge` (`.github/bible/bible_queue.py:322-326`), `GitHub.close_pr` (`.github/bible/bible_queue.py:329`), `GitHub.create_pr` (`.github/bible/bible_queue.py:332`) |
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
| Called by | `GitHub.issues` (`.github/bible/bible_queue.py:138`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:142`), `GitHub.prs` (`.github/bible/bible_queue.py:187`), `GitHub.timeline` (`.github/bible/bible_queue.py:190`), `GitHub.branch_prs` (`.github/bible/bible_queue.py:206`), `GitHub.pr_files` (`.github/bible/bible_queue.py:240`) |
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
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:547`), `Queue.plan_phase` (`.github/bible/bible_queue.py:619`), `Queue.start_chunk` (`.github/bible/bible_queue.py:645`), `Queue.component` (`.github/bible/bible_queue.py:696`, `.github/bible/bible_queue.py:730`, `.github/bible/bible_queue.py:743`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:902`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:964`, `.github/bible/bible_queue.py:977`), `Queue.delta` (`.github/bible/bible_queue.py:1052`, `.github/bible/bible_queue.py:1067`), `main` (`.github/bible/bible_queue.py:1116`) |
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
| Called by | `Queue.delta` (`.github/bible/bible_queue.py:992`) |
| Calls | `getattr`, `GitHub.call`, `get` |
| Purpose | Returns and caches the login of the GitHub token's owner. |

**Steps**

1. If `_me` is missing or falsey, GETs the API's `/user` endpoint and stores its `login`, defaulting to an empty string when the response or field is absent. (`.github/bible/bible_queue.py:162-163`)
2. Returns `_me`; if the stored login is empty, the next call repeats the request because the cache check remains falsey. (`.github/bible/bible_queue.py:162-164`)

**Pseudo-code**

```text
if _me is missing or falsey:
    _me = GET api/user.login, default ""
return _me
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:162` | if | `_me` is missing or falsey | Requests the token owner's login and caches the result. |

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
| Called by | `issue_text` (`.github/bible/bible_queue.py:386`), `json_file` (`.github/bible/bible_queue.py:401`), `Queue.component` (`.github/bible/bible_queue.py:709`), `Queue.follow` (`.github/bible/bible_queue.py:804`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:848`, `.github/bible/bible_queue.py:870`), `Queue.delta` (`.github/bible/bible_queue.py:1038`) |
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
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:460`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:867`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:934`) |
| Calls | `get`, `GitHub.agent_events`, `any` |
| Purpose | Tests whether a pull request is attributed to a configured agent login or has a Copilot-start event. |

**Steps**

1. Uses `pr["user"]` or an empty mapping. It returns `True` immediately only when the user's login is configured and the user's type is `"Bot"` (defaulting a missing type to `"Bot"`). (`.github/bible/bible_queue.py:216-218`)
2. Otherwise returns whether any agent event for `pr["number"]` is `copilot_work_started`. (`.github/bible/bible_queue.py:219`)

**Pseudo-code**

```text
if PR user's login is configured and user type (default "Bot") is "Bot": return True
return any agent event is copilot_work_started
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:217` | if | Login is in `AGENT_LOGINS` and the user type defaults to or equals `"Bot"` | Returns `True` without checking the timeline. |

#### `GitHub.start_error(issue)`

Source: `.github/bible/bible_queue.py:221-230` <!-- code: 0287983c593a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:469`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:524`) |
| Calls | `GitHub.assigned_at`, `GitHub.timeline`, `get`, `START_ERROR.search`, `splitlines`, `strip` |
| Purpose | Returns the first matching agent start-error comment since the last assignment, or `None`. |

**Steps**

1. Gets the latest assignment time with `assigned_at`, then scans the issue timeline. (`.github/bible/bible_queue.py:223-224`)
2. Uses `actor` or `user` as the event actor, and accepts a login only when the actor type is `"Bot"` (default when absent). It requires a `commented` event by a configured agent, at or after the assignment time, whose body matches `START_ERROR`. (`.github/bible/bible_queue.py:225-228`)
3. Returns the stripped first body line, truncated to 300 characters, for the first matching event; returns `None` if none matches. (`.github/bible/bible_queue.py:229-230`)

**Pseudo-code**

```text
since = assigned_at(issue)
for timeline event:
    if commented by an agent bot at/after since and body matches START_ERROR:
        return stripped first body line[:300]
return None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:224` | for | For each issue timeline event | Checks actor, event time, and body. |
| `.github/bible/bible_queue.py:226` | conditional expression | Actor type is `"Bot"` (default when absent) | Uses the actor login; otherwise treats the login as empty. |
| `.github/bible/bible_queue.py:227-228` | if | Comment event from configured bot at/after assignment matches `START_ERROR` | Returns the bounded first line; otherwise continues scanning. |

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
| Calls | `GitHub.paged`, `as_int`, `GitHub.call`, `len`, `append`, `get`, `RuntimeError` |
| Purpose | Returns every changed filename and rename source, rejecting a pull request whose returned file count is incomplete. |

**Steps**

1. Retrieves all pages of the pull request file list, then reads `changed_files` from the pull request and converts it with `as_int`. (`.github/bible/bible_queue.py:240-241`)
2. If the reported count is truthy and differs from the listed count, raises `RuntimeError` rather than returning an incomplete list. (`.github/bible/bible_queue.py:242-244`)
3. Appends each current `filename`, plus `previous_filename` when present, and returns the list. (`.github/bible/bible_queue.py:245-250`)

**Pseudo-code**

```text
out = []
listed = paged pull request files
expected = pull request changed_files converted to int
if expected and len(listed) != expected: raise RuntimeError
for listed pull request file:
    append filename
    if previous_filename: append it
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:242` | if | `changed_files` is truthy and differs from the number of listed files | Raises `RuntimeError` to refuse an incomplete file list. |
| `.github/bible/bible_queue.py:243` | raise | The reported and listed file counts differ | Raises `RuntimeError` with the pull request number and both counts. |
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
| Calls | `urllib.parse.quote`, `tempfile.TemporaryFile`, `GitHub.request`, `read`, `len`, `RuntimeError`, `write`, `seek`, `os.path.abspath`, `tarfile.open`, `split`, `isfile`, `isdir`, `os.path.normpath`, `os.path.join`, `startswith`, `os.makedirs`, `os.path.dirname`, `tar.extractfile`, `open`, `shutil.copyfileobj` |
| Purpose | Streams a bounded repository archive to a temporary file and writes accepted regular files/directories under `dest`. |

**Steps**

1. Builds the tarball URL with a quoted reference and streams the GET response, in 1 MiB chunks with a 300-second timeout, into a temporary file. (`.github/bible/bible_queue.py:258-265`)
2. Counts received bytes and raises `RuntimeError` when the total exceeds `MAX_TARBALL` (512 MiB); wraps `URLError`, `TimeoutError`, and `OSError` as `RuntimeError`. (`.github/bible/bible_queue.py:70,267-272`)
3. Rewinds the temporary file, resolves `dest` to an absolute root, and iterates gzip tar members. It skips members without a nonempty path after the first `/` and members that are neither regular files nor directories. (`.github/bible/bible_queue.py:273-279`)
4. Normalizes each member path under the root and skips targets that do not start with `root + os.sep`. (`.github/bible/bible_queue.py:280-282`)
5. Creates accepted directories recursively; for files, creates the parent directory and copies extracted bytes to a binary output file. (`.github/bible/bible_queue.py:283-288`)

**Pseudo-code**

```text
stream GET tarball(ref) to temporary file in chunks
if total bytes > MAX_TARBALL (512 MiB): raise RuntimeError
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
| `.github/bible/bible_queue.py:263` | while | A response chunk remains | Reads the next chunk; stops on an empty chunk. |
| `.github/bible/bible_queue.py:265` | if | The response returns an empty chunk | Ends the download loop. |
| `.github/bible/bible_queue.py:268` | if | Downloaded total exceeds `MAX_TARBALL` | Raises `RuntimeError` without unpacking the archive. |
| `.github/bible/bible_queue.py:269` | raise | The downloaded byte limit has been exceeded | Raises `RuntimeError` with the reference and maximum size. |
| `.github/bible/bible_queue.py:271` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Raises `RuntimeError` identifying the reference and error. |
| `.github/bible/bible_queue.py:272` | raise | A listed request error occurred | Stops with `RuntimeError`. |
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
| Called by | `Queue.held` (`.github/bible/bible_queue.py:503`, `.github/bible/bible_queue.py:507`, `.github/bible/bible_queue.py:515`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:527`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:534`, `.github/bible/bible_queue.py:539`, `.github/bible/bible_queue.py:542`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:854`, `.github/bible/bible_queue.py:875`, `.github/bible/bible_queue.py:905`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:977`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1006`, `.github/bible/bible_queue.py:1010`) |
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
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:543`), `Queue.run` (`.github/bible/bible_queue.py:589`), `Queue.component` (`.github/bible/bible_queue.py:679`), `Queue.follow` (`.github/bible/bible_queue.py:809`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:877`, `.github/bible/bible_queue.py:879`, `.github/bible/bible_queue.py:906`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:919`, `.github/bible/bible_queue.py:936`) |
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
| Called by | `Queue.held` (`.github/bible/bible_queue.py:512`), `Queue.render` (`.github/bible/bible_queue.py:1029`) |
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
| Called by | `Queue.held` (`.github/bible/bible_queue.py:514`) |
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
2. PUTs `/pulls/<number>/merge` with `merge_method: "squash"`, `commit_title: title`, and the current `pr["head"]["sha"]` as `sha`, so GitHub rejects the merge if the checked head has changed. (`.github/bible/bible_queue.py:325-326`)

**Pseudo-code**

```text
if PR is draft: mark it ready
PUT merge request with squash method, title, and the checked PR head SHA
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

Source: `.github/bible/bible_queue.py:448-1078` <!-- code: c7b3115b36f1 -->

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
| Called by | `Queue.run` (`.github/bible/bible_queue.py:588`), `Queue.plan_phase` (`.github/bible/bible_queue.py:612`), `Queue.start_chunk` (`.github/bible/bible_queue.py:640`), `Queue.component` (`.github/bible/bible_queue.py:660`, `.github/bible/bible_queue.py:672`, `.github/bible/bible_queue.py:674`, `.github/bible/bible_queue.py:680`, `.github/bible/bible_queue.py:689`, `.github/bible/bible_queue.py:703`, `.github/bible/bible_queue.py:706`, `.github/bible/bible_queue.py:708`, `.github/bible/bible_queue.py:724`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:844`, `.github/bible/bible_queue.py:863`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:914`, `.github/bible/bible_queue.py:924`, `.github/bible/bible_queue.py:929`) |
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
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:623`), `Queue.component` (`.github/bible/bible_queue.py:663`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:881`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:938`) |
| Calls | `labels_of`, `any`, `issue.get`, `self.gh.timeline`, `max`, `e.get`, `self.gh.label`, `self.gh.comment`, `self.gh.close`, `l.startswith`, `ATTEMPT.sub`, `self.gh.set_body`, `re.search`, `self.gh.assign`, `assignment`, `self.model_for`, `base.group` |
| Purpose | Holds issues needing a person, recognizes a release after the latest hold, closes released component issues, and reassigns released non-component issues. |

**Steps**

1. Returns `True` immediately when labels contain `bible-needs-human`; returns `False` if any assignee login belongs to `AGENT_LOGINS`. (`.github/bible/bible_queue.py:491-494`)
2. Reads the issue timeline and finds the latest `labeled` and `unlabeled` timestamps for `bible-needs-human`. If no removal exists or it is not later than the latest addition, adds the human label, comments that a person must act, and returns `True`. (`.github/bible/bible_queue.py:495-505`)
3. If the hold was removed after it was added and any issue label begins `bible/`, comments that the component session is closed, closes the issue with `not_planned`, and returns `"released"`. (`.github/bible/bible_queue.py:506-510`)
4. Otherwise replaces any `Attempt:` marker with `Attempt: 1`, saves the body, extracts a `Base branch:` value or uses `self.default`, assigns Copilot with that branch and the selected model, posts a reassignment comment, and returns `False`. (`.github/bible/bible_queue.py:511-516`)

**Pseudo-code**

```text
if issue labels include bible-needs-human: return True
if any assignee login belongs to AGENT_LOGINS: return False
find latest added and removed bible-needs-human timeline events
if no removal or removal is not later than addition:
    relabel and comment for a person; return True
if any label starts with bible/:
    comment, close as not_planned; return released
reset Attempt to 1; save body; assign Copilot with Base branch or default and model
comment that issue was reassigned; return False
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:491` | if | Labels contain `bible-needs-human` | Returns `True`; otherwise checks assignees. |
| `.github/bible/bible_queue.py:493` | if | Any assignee login belongs to `AGENT_LOGINS` | Returns `False` without changing the issue. |
| `.github/bible/bible_queue.py:500` | if | No removal event exists or the newest removal is not later than the newest addition | Labels and comments for a person, then returns `True`. |
| `.github/bible/bible_queue.py:506` | if | Any label begins with `bible/` after a valid release | Comments, closes as `not_planned`, and returns `"released"`. |
| `.github/bible/bible_queue.py:514` | conditional expression | A `Base branch:` match exists in the reset body | Assigns to its captured branch; otherwise uses `self.default`. |

#### `Queue.model_for(issue)`

Source: `.github/bible/bible_queue.py:518-520` <!-- code: 17f084589886 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:514`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:548`) |
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

1. Gets the start-error text or uses `Copilot could not start`. (`.github/bible/bible_queue.py:524`)
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
| Calls | `settings.get`, `json_file`, `catalog.get`, `self.plan_phase`, `isinstance`, `c.get`, `str`, `NAME.match`, `len`, `str.strip`, `asked.split`, `n.strip`, `join`, `self.render`, `self.run_issues`, `gh.close`, `self.component`, `str.endswith`, `str.startswith`, `as_int`, `self.start_chunk`, `type`, `all`, `rows.values`, `self.assemble_phase` |
| Purpose | Sends an incomplete catalog to planning; otherwise validates selected components, advances their queue states within the configured concurrency cap, and renders tracker status. |

**Steps**

1. Selects the analysis folder from settings or `codebase-analysis`, stores the settings/tracker/run label, and reads the component catalog from the default branch. (`.github/bible/bible_queue.py:565-568`)
2. Returns the planning-phase result when the catalog is not a dict, is marked proposed, or lacks a component list. Otherwise extracts names from dict entries and rejects any name that fails `NAME` by rendering a stopped status. (`.github/bible/bible_queue.py:569-579`)
3. Parses `components` as all names when the setting is `"all"` or empty; otherwise splits and trims comma-separated names, then finds unknown selections. It renders and returns a stopped status for unknown names or an empty selection. (`.github/bible/bible_queue.py:580-587`)
4. Closes all open plan issues, stores session estimates, evaluates each selected component, records component exceptions as bounded status strings, and counts active/waiting results. (`.github/bible/bible_queue.py:588-597`)
5. Converts the concurrency cap with `as_int`; starts fresh chunks for `not started` components when capacity is available, recording start errors as bounded statuses. (`.github/bible/bible_queue.py:598-605`)
6. Adds whole-analysis assembly status when every component row is `"merged"` and renders all rows. (`.github/bible/bible_queue.py:606-608`)

**Pseudo-code**

```text
analysis = settings.analysis or "codebase-analysis"
store settings, tracker, and run label; read components.json from default branch
if catalog is invalid, proposed, or has no components list: return plan_phase(...)
extract valid names; if any catalog name fails NAME: render stopped status and return
parse requested components; if unknown names or none: render stopped status and return
close plan issues; store estimates; evaluate selected components and count active rows
cap = concurrency converted to integer
for each selected component: start a fresh chunk if not started and capacity permits
if every component row is merged: add whole-analysis assembly status
render rows
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:569` | if | Catalog is not a dict, is marked proposed, or has no components list | Returns the planning-phase result. |
| `.github/bible/bible_queue.py:575` | if | Any catalog component name fails `NAME` | Renders a stopped status explaining the invalid names and returns. |
| `.github/bible/bible_queue.py:581` | conditional expression | Selection is `"all"` or empty | Uses all catalog names; otherwise parses comma-separated names. |
| `.github/bible/bible_queue.py:583` | if | Selection contains unknown names or is empty | Renders stopped settings and returns. |
| `.github/bible/bible_queue.py:586` | conditional expression | Unknown names exist | Reports unknown names; otherwise reports no selected component. |
| `.github/bible/bible_queue.py:588` | for | For each open plan issue | Closes that issue. |
| `.github/bible/bible_queue.py:592` | for | For each selected component | Evaluates its component state. |
| `.github/bible/bible_queue.py:595` | except | Component evaluation raises `Exception` | Stores a per-component error status with exception type and at most 160 characters of text. |
| `.github/bible/bible_queue.py:599` | for | For each selected component | Considers whether to start a component whose status is `not started`. |
| `.github/bible/bible_queue.py:600` | if | Status is `not started` and the cap is zero or active count is below it | Attempts to start a fresh chunk. |
| `.github/bible/bible_queue.py:604` | except | Starting the chunk raises `RuntimeError` | Stores a bounded error status. |
| `.github/bible/bible_queue.py:606` | if | Every selected row is `"merged"` | Adds whole-analysis assembly status. |

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
| Called by | `Queue.run` (`.github/bible/bible_queue.py:602`), `Queue.component` (`.github/bible/bible_queue.py:704`, `.github/bible/bible_queue.py:739`) |
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
| Calls | `gh.branch_prs`, `pr.get`, `get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `gh.close`, `labels_of`, `max`, `h.get`, `status_of`, `status.get`, `self.check`, `len`, `self.start_chunk`, `as_int`, `self.estimate.get`, `gh.create_issue`, `report_facts`, `gh.file`, `gh.create_pr`, `bool`, `any`, `assignment`, `self.settings.get` |
| Purpose | Advances a tracker-scoped component through sessions, gate checks, bounded verification/revision rounds, and a final review PR or human hold. |

**Steps**

1. Scans PRs from `bible/<name>` into the default branch. Ignores another repository's PRs, PRs created before the tracker, and PRs without this tracker reference; for the first matching PR, returns merged, review, or needs-person status. (`.github/bible/bible_queue.py:651-659`)
2. Combines open chunk and verification issues. For the first issue, returns a next-check status if released, needs-person if held, or delegates to `follow`. (`.github/bible/bible_queue.py:660-671`)
3. If there has never been a component issue, returns `not started`. Otherwise it loads branch status and runs `check` only for `COMPONENT_DONE`. (`.github/bible/bible_queue.py:672-685`)
4. If the gate fails, finds closed chunk sessions since the last hold or merged component PR. It caps those sessions at `max(MIN_SESSION_CAP, 2 * estimate + 2)`; at the cap it opens a human-hold issue, otherwise starts another chunk and returns `session starting`. (`.github/bible/bible_queue.py:686-705`)
5. After a passing gate, gathers completed verification issues and report facts. It opens the final PR only for a `PASS` with no major corrections and a nonempty report fingerprint equal to the checked page fingerprint. (`.github/bible/bible_queue.py:706-714`)
6. If the verdict is about the current pages, records whether completed chunk work followed the latest verification. After the verification-round limit without such work, opens a human hold. (`.github/bible/bible_queue.py:715-737`)
7. Starts a revision chunk when the matching verdict needs corrections and no chunk has since run; otherwise creates and assigns a verification issue and returns `verify running`. (`.github/bible/bible_queue.py:738-751`)

**Pseudo-code**

```text
for PR from component branch into default:
    skip another repo, older tracker, or PR without tracker reference
    return merged, review, or needs-person state
if open chunk/verify issue:
    if held: return released or needs-person
    return follow(issue)
if no component issue ever existed: return not started
status = component status
if COMPONENT_DONE: run coverage gate
if gate fails:
    find closed chunk sessions since latest hold or merged PR
    if session cap reached: open human hold; return
    start next chunk; return session starting
handle open hold; stop if human label remains, otherwise close and reload
closed_verify = completed verifications created since latest hold close
facts = latest verification report facts if any completed verification exists
if clean PASS and pages fingerprint matches: create final PR; return review state
if no chunk followed latest verification and verification limit reached: create human hold; return
if report concerns these pages, needs revision, and no chunk followed: start revision; return
create verification issue
return verify running
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:651` | for | For each PR from the component branch into the default branch | Checks repository, tracker age, and tracker reference. |
| `.github/bible/bible_queue.py:653` | if | PR is from another repository, predates this tracker, or lacks its reference | Skips the PR. |
| `.github/bible/bible_queue.py:655` | if | Matching PR has `merged_at` | Returns `"merged"`. |
| `.github/bible/bible_queue.py:657` | if | Matching PR is open | Returns its review status. |
| `.github/bible/bible_queue.py:661` | if | An open chunk or verification issue exists | Selects the first session issue. |
| `.github/bible/bible_queue.py:664` | if | The selected issue was released by a person | Returns a status to re-evaluate on the next check. |
| `.github/bible/bible_queue.py:666` | if | The selected issue remains held | Returns human-needed status. |
| `.github/bible/bible_queue.py:672` | if | No issue for this component exists in any state | Returns `"not started"`. |
| `.github/bible/bible_queue.py:676` | if | At least one hold issue is open | Checks whether it still requires a person. |
| `.github/bible/bible_queue.py:677` | if | The first open hold has `bible-needs-human` | Returns human-needed status; otherwise closes that hold and reloads the list. |
| `.github/bible/bible_queue.py:684` | if | Component status is `COMPONENT_DONE` | Runs the coverage check. |
| `.github/bible/bible_queue.py:686` | if | Coverage gate did not pass | Counts recent closed chunk sessions and either opens a human hold or starts another chunk. |
| `.github/bible/bible_queue.py:693` | if | Closed chunk session count reaches the computed cap | Creates a human-hold issue. |
| `.github/bible/bible_queue.py:709` | conditional expression | Any completed verification exists | Reads and parses its report; otherwise sets `facts` to `None`. |
| `.github/bible/bible_queue.py:710` | if | PASS has no major corrections and a nonempty fingerprint matching the gated pages | Creates the final component PR. |
| `.github/bible/bible_queue.py:729` | if | Facts exist, no completed chunk follows the latest verification, and verification count reaches `MAX_VERIFY_ROUNDS` | Creates a human hold. |
| `.github/bible/bible_queue.py:738` | if | Report concerns current pages, needs revision, and no completed chunk follows the latest verification | Starts a revision chunk; otherwise proceeds to verification. |

#### `Queue.follow(analysis, name, issue)`

Source: `.github/bible/bible_queue.py:753-810` <!-- code: d30979e2d28a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:671`) |
| Calls | `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `str.startswith`, `os.path.basename`, `join`, `status_of`, `as_int`, `status.get`, `issue.get`, `any`, `gh.file`, `gh.label`, `gh.merge`, `gh.unlabel`, `gh.close` |
| Purpose | Checks an assigned chunk or verification session and its PR, then retries, holds, waits, or validates and merges it. |

**Steps**

1. Derives `verify` or `chunk` from issue labels and classifies the session. Waiting returns `session starting`; start-error creates a human hold; no-start retries; running returns `<kind> running`. (`.github/bible/bible_queue.py:755-766`)
2. Checks that the complete PR file list can be read; an incomplete list raises `RuntimeError` and is retried or held. Chunk PRs may touch component LLD, API LLD, and ledger files except `verification-*`; verification PRs may touch only `verification-*` and `citations.tsv` within the component ledger. (`.github/bible/bible_queue.py:767-782`)
3. Reads component status at the PR head SHA. For a chunk, `WAITING_ANSWER` adds waiting labels to the issue and PR only if the issue lacks the label, then returns the answer-wait state. (`.github/bible/bible_queue.py:783-789`)
4. Otherwise compares packet count on the PR with the branch, recognizes a revision from `"\nRevision "` in the issue body, and treats increased packets or `COMPONENT_DONE` as progress. A `STOP` status or no progress is retried/held. (`.github/bible/bible_queue.py:790-795`)
5. A revision must change an allowed component page, API page, or `revision-log.md`, and must end with `COMPONENT_DONE`; otherwise it is retried/held. A verification session with no report at the PR head is retried/held. (`.github/bible/bible_queue.py:796-806`)
6. On success, merges the PR, removes the waiting-answer label, closes the issue, and returns `<kind> merged`. (`.github/bible/bible_queue.py:807-810`)

**Pseudo-code**

```text
kind = verify if verification label else chunk
state, pr = session(...)
if waiting/start-error/no-start/running: handle it and return
if PR file list is incomplete: fail_or_retry; return
find PR files outside this kind's allowed paths
if bad files: fail_or_retry; return starting or needs-person
status = component status at PR head
if chunk:
    if WAITING_ANSWER: label issue and PR if needed; return waiting for answers
    before = branch packet count
    if STOP or no packet progress: fail_or_retry; return
    if revision changed no allowed page/log: fail_or_retry; return
    if revision did not reach COMPONENT_DONE: fail_or_retry; return
elif verification report missing: fail_or_retry; return
merge PR; remove waiting label; close issue
return kind + " merged"
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:755` | conditional expression | Issue labels include `bible-verify` | Sets kind to verify; otherwise chunk. |
| `.github/bible/bible_queue.py:757` | if | Session state is `waiting` | Returns `session starting`. |
| `.github/bible/bible_queue.py:759` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:762` | if | Session state is `no-start` | Retries and returns starting or needs-person. |
| `.github/bible/bible_queue.py:764` | conditional expression | Retry succeeded | Returns `session starting`; otherwise needs-person. |
| `.github/bible/bible_queue.py:765` | if | Session state is `running` | Returns `<kind> running`. |
| `.github/bible/bible_queue.py:769` | try | Before validating files | Calls `pr_files` so an incomplete list cannot be mistaken for an allowed list. |
| `.github/bible/bible_queue.py:770` | except | File-list validation raises `RuntimeError` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:772` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:773` | if | Kind is `chunk` | Applies the chunk allowlist; otherwise applies the verification allowlist. |
| `.github/bible/bible_queue.py:780` | if | At least one changed PR file is disallowed | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:782` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:784` | if | Kind is `chunk` | Validates chunk status; otherwise checks for a verification report. |
| `.github/bible/bible_queue.py:785` | if | Chunk status is `WAITING_ANSWER` | Checks whether waiting labels must be added. |
| `.github/bible/bible_queue.py:786` | if | Issue lacks `bible-waiting-answer` | Adds the label to issue and PR. |
| `.github/bible/bible_queue.py:793` | if | Status is `STOP` or packet progress is false | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:795` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:797` | if | A revision changed no allowed page or revision log | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:800` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:801` | if | Issue is a revision and state is not `COMPONENT_DONE` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:803` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:804` | elif | Verification PR has no report at its head SHA | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:806` | conditional expression | Retry succeeded | Returns starting; otherwise needs-person. |

#### `Queue.check(analysis, name, branch)`

Source: `.github/bible/bible_queue.py:812-837` <!-- code: 181278d76a48 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:685`) |
| Calls | `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `printed.stdout.strip`, `().splitlines`, `run.stdout.strip` |
| Purpose | Runs the component coverage gate against an unpacked branch tarball and obtains its pages fingerprint. |

**Steps**

1. Builds the toolkit scripts path; if `coverage.py` is absent, logs that the gate is skipped and treated as failing, then returns `(False, None)`. (`.github/bible/bible_queue.py:814-817`)
2. Creates a temporary directory and extracts the branch tarball. A tarball `RuntimeError` is logged and returns `(False, None)`. (`.github/bible/bible_queue.py:818-824`)
3. Runs isolated `coverage.py` with the repository, analysis, depth, component, and report arguments; logs its last output line or `no output`. Then runs isolated `status.py --fingerprint --component` and returns coverage success plus stripped fingerprint output or `None`. (`.github/bible/bible_queue.py:825-832`)
4. On `TimeoutExpired`, logs the timeout and returns `(False, None)`. The `finally` block removes the temporary directory and ignores cleanup errors. (`.github/bible/bible_queue.py:833-837`)

**Pseudo-code**

```text
if coverage.py is missing: log; return False, None
work = temporary directory
try:
    try unpack branch tarball into work
    on RuntimeError: log; return False, None
    run coverage.py in isolated Python
    log final output line
    run status.py --fingerprint
    return coverage succeeded, fingerprint output or None
on TimeoutExpired: log; return False, None
finally: remove work directory
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:815` | if | `coverage.py` is not a file | Logs the missing checker and returns failure with no fingerprint. |
| `.github/bible/bible_queue.py:822` | except | Tarball extraction raises `RuntimeError` | Logs the failure and returns a failing gate with no fingerprint. |
| `.github/bible/bible_queue.py:833` | except | Either subprocess exceeds `GATE_TIMEOUT` | Logs the timeout and returns a failing gate with no fingerprint. |


#### `Queue.assemble_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:839-907` <!-- code: 9aa48c7b485e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:607`) |
| Calls | `self.run_issues`, `settings.get`, `report_facts`, `gh.file`, `max`, `self.revise_all_step`, `gh.linked_prs`, `p.get`, `get`, `gh.is_agent_pr`, `gh.label`, `gh.comment`, `gh.close`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `issue_text`, `assignment`, `gh.create_issue` |
| Purpose | Runs assembly and whole-analysis verification/revision cycles after all components merge, then closes the tracker when those phases finish. |

**Steps**

1. Iterates `bible-assemble` then `bible-verify-all`, selecting each phase's model, title, and optional issue-text file. A completed closed assembly issue skips that phase. For completed whole-verification issues, reads the default-branch report and skips only when it is a clean `PASS`; otherwise, if no revision is already required or open, labels/comments the latest verification and returns that corrections are next. (`.github/bible/bible_queue.py:841-858`)
2. Before opening or processing a verify-all issue, runs `revise_all_step`; a returned state stops the phase. It then finds open issues and linked PRs merged into the default branch from this repository by an agent. (`.github/bible/bible_queue.py:859-867`)
3. If such a PR exists for verify-all, reads the report; a missing/non-PASS report or major corrections labels the issue for revision, comments, closes it as `not_planned`, and returns. Otherwise closes the issue and proceeds to the next phase. (`.github/bible/bible_queue.py:868-880`)
4. For an unmerged open issue, returns needs-person if held; otherwise classifies the session, holds a start-error, retries a no-start, reports running work, and checks whether a finished session needs continuation before returning review/state. (`.github/bible/bible_queue.py:881-895`)
5. If no issue is open, loads the assembly issue text or builds whole-analysis verification instructions, creates and assigns the issue, and returns its assigned status. When both phases are complete, comments and closes the tracker and returns `done`. (`.github/bible/bible_queue.py:896-907`)

**Pseudo-code**

```text
for assemble and verify-all phase:
    inspect completed closed issues
    if assembly is complete or whole verification report is clean PASS: continue
    if whole verification needs corrections and no revision is open: mark it; return
    if kind is verify-all and revise_all_step has work: return that state
    if an open issue exists:
        find merged agent PR into default from this repo
        if found:
            if verify-all and report is not clean PASS: mark revision, close issue; return
            close issue; continue
        if held: return human-needed
        classify session; handle start-error/no-start
        if finished PR needs continuation: return continuation state
        return review status or session state
    load assemble issue text or build verify-all instructions
    create assigned phase issue
    return phase assigned state
comment tracker done; close tracker; return done
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:841` | for | For the assemble and verify-all phases | Processes the phases in order. |
| `.github/bible/bible_queue.py:845` | if | Current phase is verify-all and a completed issue exists | Rechecks the default-branch report. |
| `.github/bible/bible_queue.py:850` | if | Report is a clean PASS | Skips to the next phase. |
| `.github/bible/bible_queue.py:852` | if | No revision label exists and no verify-all issue is open | Labels/comments the verdict and returns that revision is next. |
| `.github/bible/bible_queue.py:855-856` | conditional expression | Report facts exist | Includes the verdict; otherwise reports `"missing"`. |
| `.github/bible/bible_queue.py:857` | elif | Another phase has a completed closed issue | Skips to the next phase. |
| `.github/bible/bible_queue.py:859` | if | Current phase is verify-all | Runs the whole-analysis revision step. |
| `.github/bible/bible_queue.py:861` | if | Revision step returns a state | Returns that state. |
| `.github/bible/bible_queue.py:864` | if | At least one open issue exists for the phase | Processes its first open issue. |
| `.github/bible/bible_queue.py:868` | if | A qualifying merged agent PR exists | Closes/advances or validates verify-all results. |
| `.github/bible/bible_queue.py:869` | if | Current phase is verify-all | Checks the whole-analysis verification report. |
| `.github/bible/bible_queue.py:871` | if | Report is missing, not PASS, or has major corrections | Marks the issue for revision, closes it, and returns. |
| `.github/bible/bible_queue.py:876-878` | conditional expression | Report facts exist | Includes verdict or `"missing"` in the correction status. |
| `.github/bible/bible_queue.py:881` | if | Open issue is held | Returns the human-needed issue number. |
| `.github/bible/bible_queue.py:884` | if | Session state is `start-error` | Holds the issue and returns human-needed. |
| `.github/bible/bible_queue.py:887` | if | Session state is `no-start` | Invokes retry logic. |
| `.github/bible/bible_queue.py:889` | if | PR exists and state is running | Returns running status with PR number. |
| `.github/bible/bible_queue.py:891` | if | PR exists and state is finished | Checks whether the session needs continuation. |
| `.github/bible/bible_queue.py:893` | if | Continuation helper returns a state | Returns that state. |
| `.github/bible/bible_queue.py:895` | conditional expression | PR exists | Returns PR review instruction; otherwise returns session state. |
| `.github/bible/bible_queue.py:896` | if | Phase has a `text` filename | Loads issue title/body from that ledger file; otherwise uses verify-all instructions. |

#### `Queue.revise_all_step(tracker, analysis)`

Source: `.github/bible/bible_queue.py:909-979` <!-- code: ecf0e4db8193 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:860`) |
| Calls | `self.run_issues`, `max`, `h.get`, `gh.close`, `labels_of`, `sorted`, `i.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `gh.linked_prs`, `p.get`, `gh.is_agent_pr`, `gh.pr_files`, `os.path.basename`, `f.startswith`, `join`, `gh.create_issue`, `assignment`, `self.settings.get`, `len`, `any` |
| Purpose | Runs a bounded whole-analysis revision after a verification requests corrections, or creates a human hold when repeated verification rounds do not resolve them. |

**Steps**

1. Loads whole-analysis hold issues. An open hold with `bible-needs-human` returns needs-person; otherwise closes the released hold and reloads the list. Uses the latest hold close time to scope correction rounds. (`.github/bible/bible_queue.py:914-921`)
2. Sorts closed verify-all issues marked `bible-needs-revision`; returns `None` if there are none. Restricts the current round count to those created since the latest hold release, then loads revision issues. (`.github/bible/bible_queue.py:924-930`)
3. For an open revision issue, closes it and returns `None` if an agent PR from this repository merged into the default branch. Otherwise handles human hold, start-error, no-start, running, and continuation states. (`.github/bible/bible_queue.py:931-952`)
4. For a finished PR, rejects files outside the analysis folder or whose basename starts `verification-`; a violation is retried or held. Otherwise returns review status. (`.github/bible/bible_queue.py:953-959`)
5. With no open revision, returns `None` if a completed revision was closed after the latest corrections verdict. At `MAX_VERIFY_ROUNDS`, creates a whole-analysis human hold; otherwise creates and assigns a revision issue with instructions to apply the report without editing it. (`.github/bible/bible_queue.py:960-979`)

**Pseudo-code**

```text
close released whole-analysis hold; after = latest hold close
asked_all = closed verify-all issues marked bible-needs-revision, oldest first
if none: return None
asked = verdicts created since after
if an open revision exists:
    if merged agent PR into default from this repo: close; return None
    handle hold, start-error, no-start, running
    if finished: continue session if needed; reject disallowed files
    return review status or session state
if a completed revision followed the latest verdict: return None
if len(asked) >= MAX_VERIFY_ROUNDS: create human hold; return its state
create assigned whole-analysis revision issue
return "revise-all session assigned"
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:916` | if | At least one whole-analysis hold is open | Checks whether it still needs a person. |
| `.github/bible/bible_queue.py:917` | if | First open hold has `bible-needs-human` | Returns needs-person; otherwise closes and refreshes the holds. |
| `.github/bible/bible_queue.py:926` | if | No closed verification asks for revision | Returns `None`. |
| `.github/bible/bible_queue.py:931` | if | A revision issue is open | Processes it. |
| `.github/bible/bible_queue.py:935` | if | A qualifying merged agent PR exists | Closes the revision issue and returns `None`. |
| `.github/bible/bible_queue.py:938` | if | Open revision is held | Returns needs-person. |
| `.github/bible/bible_queue.py:941` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:944` | if | Session state is `no-start` | Retries and returns session-starting. |
| `.github/bible/bible_queue.py:947` | if | PR exists and state is running | Returns running status. |
| `.github/bible/bible_queue.py:949` | if | PR exists and state is finished | Checks whether continuation is needed. |
| `.github/bible/bible_queue.py:951` | if | Continuation helper returns a state | Returns that state. |
| `.github/bible/bible_queue.py:955` | if | Revision files leave the analysis folder or include a `verification-*` basename | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:958` | conditional expression | Retry succeeded | Returns session-starting; otherwise returns needs-person. |
| `.github/bible/bible_queue.py:959` | conditional expression | An open revision PR exists | Returns review status; otherwise returns session state. |
| `.github/bible/bible_queue.py:961` | if | A completed revision issue closed after the latest verdict | Returns `None` so verification can proceed. |
| `.github/bible/bible_queue.py:963` | if | Revision-requesting verifications since release reach `MAX_VERIFY_ROUNDS` | Creates a human hold. |

#### `Queue.continue_if_unfinished(issue, pr, kind, analysis)`

Source: `.github/bible/bible_queue.py:981-1019` <!-- code: 607ef9d1096b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:892`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:950`) |
| Calls | `gh.pr_files`, `gh.me`, `max`, `e.get`, `gh.timeline`, `get`, `sorted`, `age`, `len`, `labels_of`, `gh.label`, `gh.comment`, `self.settings.get` |
| Purpose | Detects an unfinished assembly/revision/verification pull request and requests bounded continuation sessions or human review. |

**Steps**

1. Chooses the end marker: `verification-report.md` for `bible-verify-all`, otherwise `status.json`. If the marker is already in the PR file list, returns `None`. (`.github/bible/bible_queue.py:989-991`)
2. Gets the API token owner's login, the latest removal time of `bible-needs-human` from the issue timeline, and PR timeline events. It counts only continuation comments by that login, containing `CONTINUE_MARK`, posted after the last release. (`.github/bible/bible_queue.py:992-1000`)
3. If the newest continuation request is newer than the latest Copilot-finished event and is within `NO_PR_AFTER`, returns a continuing status. (`.github/bible/bible_queue.py:1001-1002`)
4. If continuation count reaches `MAX_CONTINUE`, labels/comments for a person when not already held and returns needs-person. Otherwise posts a kind-specific continuation prompt and returns the next session count and PR number. (`.github/bible/bible_queue.py:1003-1019`)

**Pseudo-code**

```text
marker = verification report for verify-all, otherwise status.json
if marker in PR files: return None
me = token owner's login
released = latest issue unlabeled event for bible-needs-human
asked = sorted own marked continuation comments after release
if newest ask is newer than latest agent-finished event and within NO_PR_AFTER:
    return continuing
if len(asked) >= MAX_CONTINUE:
    if not already held: label and comment for a person
    return needs-person
comment on PR with next.py continuation instructions specific to kind
return continuing session number and PR number
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:989` | conditional expression | Kind is `bible-verify-all` | Uses the verification report marker; otherwise uses `status.json`. |
| `.github/bible/bible_queue.py:990` | if | Marker is already present in the PR file list | Returns `None` because the session is complete. |
| `.github/bible/bible_queue.py:1001` | if | A continuation request follows the latest finished event and is within `NO_PR_AFTER` | Returns a continuing status without posting another request. |
| `.github/bible/bible_queue.py:1003` | if | Continuation count reaches `MAX_CONTINUE` | Checks/creates a human hold. |
| `.github/bible/bible_queue.py:1004` | if | Issue does not already have `bible-needs-human` | Adds the label and explanatory comment. |

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
| Calls | `gh.default_branch`, `json_file`, `self.log`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `components.component_map`, `sorted`, `dict.values`, `str.startswith`, `self.skills.rstrip`, `NAME.match`, `len`, `MAX_DELTA_ISSUES`, `gh.issues`, `gh.create_issue`, `components.assign`, `SAFE_FILE.match`, `comp_label`, `join`, `assignment` |
| Purpose | Maps changed paths to component update issues, while bounding automatic fan-out and keeping unusual filenames out of issue text. |

**Steps**

1. Gets the default branch, loads `components.json`, and checks for `ledger/baseline.json`; if either is falsey, logs that there is no assembled analysis and returns. (`.github/bible/bible_queue.py:1035-1040`)
2. Adds the analysis toolkit scripts to `sys.path`, imports component-mapping helpers, and maps changed paths outside both the analysis tree and `BIBLE_SKILLS` tree to sorted valid component names. (`.github/bible/bible_queue.py:1041-1048`)
3. If more than `MAX_DELTA_ISSUES` (10) components were touched, creates a single human-review issue only when one is not already open, logs, and returns without component issues. (`.github/bible/bible_queue.py:1049-1058`)
4. For each touched component, selects its changed files and divides them into SAFE_FILE paths to show (at most 20) and a count of unusual paths to omit. If an update issue for that component is already open, logs and skips; otherwise creates an assigned issue containing tracking-skill and `status.py --write` instructions, then logs the file count. (`.github/bible/bible_queue.py:1059-1077`)

**Pseudo-code**

```text
default = gh.default_branch()
catalog = json_file(components.json)
if catalog is falsey or baseline is missing/falsey: log; return
load components toolkit
touched = sorted valid component names for paths outside analysis and toolkit trees
if touched count > MAX_DELTA_ISSUES:
    create one human-review issue if none is already open
    log and return
for each touched component:
    files = changed paths assigned to it
    show up to 20 SAFE_FILE paths; count and omit the others
    if a matching delta issue is open: log; continue
    create assigned delta issue with paths and tracking/status instructions
    log file count
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1038` | if | Catalog is falsey or baseline file is missing/falsey | Logs that no assembled analysis exists and returns. |
| `.github/bible/bible_queue.py:1049` | if | More than `MAX_DELTA_ISSUES` components are touched | Creates a human-review issue if none is open, logs, and returns. |
| `.github/bible/bible_queue.py:1051` | if | No `bible-delta`/`bible-needs-human` issue is open | Creates the single human-review issue. |
| `.github/bible/bible_queue.py:1059` | for | For each touched component | Selects its changed files and checks issue state. |
| `.github/bible/bible_queue.py:1064` | if | A matching component delta issue is already open | Logs and skips creating a duplicate issue. |
| `.github/bible/bible_queue.py:1074` | conditional expression | Unusual-character paths were excluded from the visible list | Adds a count of those paths to the issue body. |

## Functions and methods

### `main()`

Source: `.github/bible/bible_queue.py:1080-1126` <!-- code: d5e645d7911f -->

| | |
| --- | --- |
| Kind | module entry point |
| Called by | Module guard (`.github/bible/bible_queue.py:1129-1130`) |
| Calls | `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `args.verify_model.strip`, `args.components.split`, `n.strip`, `any`, `NAME.match`, `gh.ensure_labels`, `gh.issues`, `json.dumps`, `settings_of`, `gh.create_issue`, `issue.get`, `print`, `queue.reconcile`, `open`, `l.strip`, `queue.delta`, `RuntimeError`, `str` |
| Purpose | Parses `start`, `reconcile`, and `delta` commands and dispatches to the queue workflow. |

**Steps**

1. Builds a required-subcommand parser from the module docstring and defines the `start`, `reconcile`, and `delta` arguments before parsing. (`.github/bible/bible_queue.py:1081-1094`)
2. Reads `GITHUB_REPOSITORY` and `GH_TOKEN`; exits if either is missing, then constructs `GitHub` and `Queue`. (`.github/bible/bible_queue.py:1096-1100`)
3. For `start`, requires a nonempty verification model different from the normal model, parses component names, and requires a nonempty selection of `all` or names matching `NAME`. It ensures labels and refuses to open a second tracker. (`.github/bible/bible_queue.py:1102-1110`)
4. Builds settings and validates them through `settings_of`; invalid settings exit with guidance. Otherwise creates the tracker issue with a hidden JSON settings marker and prints its number and queue-start instructions. (`.github/bible/bible_queue.py:1111-1118`)
5. For `reconcile`, invokes `queue.reconcile`; for `delta`, reads nonempty stripped paths from the changed-file input and calls `queue.delta`. A command `RuntimeError` becomes `SystemExit` with its text. (`.github/bible/bible_queue.py:1119-1126`)

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
        validate settings with settings_of
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
| `.github/bible/bible_queue.py:1097` | if | Repository or token environment value is missing | Exits with a required-environment message. |
| `.github/bible/bible_queue.py:1098` | raise | Either required environment value is missing | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1102` | if | Command is `start` | Validates and starts an analysis run. |
| `.github/bible/bible_queue.py:1103` | if | Verification model is empty or equals normal model | Exits with the distinct-model requirement. |
| `.github/bible/bible_queue.py:1104` | raise | Verification model validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1106` | if | No component names or a name other than `all` fails `NAME` | Exits with component-selection guidance. |
| `.github/bible/bible_queue.py:1107` | raise | Component selection fails validation | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1109` | if | An open tracker issue exists | Exits rather than opening another run. |
| `.github/bible/bible_queue.py:1110` | raise | An open tracker exists | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1113` | if | The settings round-trip fails `settings_of` validation | Exits with settings guidance. |
| `.github/bible/bible_queue.py:1114` | raise | Settings validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1119` | elif | Command is `reconcile` | Calls `queue.reconcile`; otherwise reads changed paths and runs delta. |
| `.github/bible/bible_queue.py:1125` | except | Command handling raises `RuntimeError` | Enters error conversion. |
| `.github/bible/bible_queue.py:1126` | raise | A `RuntimeError` was caught | Raises `SystemExit` with the error text. |

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
| Called by | Queue functions in later source packets. |
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
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:555`) and `main` (`.github/bible/bible_queue.py:1113`) |
| Calls | `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group`, `ValueError`, `isinstance`, `str`, `SAFE_PATH.match`, `analysis.split`, `DEPTH_VALUES`, `SAFE_MODEL.match` |
| Purpose | Parses tracker settings and rejects malformed JSON, non-object data, unsafe analysis paths, unsupported depths, or malformed nonempty model names. |

**Steps**

1. Searches the tracker body (or `""`) for the settings marker and loads its capture group as JSON; no match yields `None`, and `ValueError` returns `None`. (`.github/bible/bible_queue.py:357-361`)
2. Rejects data that is not a dictionary. Converts `analysis` to a string with default `codebase-analysis` and rejects it unless it matches `SAFE_PATH` and has no `..` path segment. (`.github/bible/bible_queue.py:362-366`)
3. Converts `depth` to a string with default `"deep"` and rejects values outside `DEPTH_VALUES`. For `model` and `verify_model`, converts falsey values to an empty string and rejects nonempty values that fail `SAFE_MODEL`; otherwise returns the original dictionary. (`.github/bible/bible_queue.py:367-373`)

**Pseudo-code**

```text
match = SETTINGS search in tracker.body or ""
try:
    data = parse match group 1 if matched, otherwise None
except ValueError: return None
if data is not a dict: return None
if string analysis is not a safe path or contains a ".." segment: return None
if string depth is not supported: return None
if either nonempty model name is malformed: return None
return data
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:359` | conditional expression | A settings marker matched | Parses its first group; otherwise uses `None`. |
| `.github/bible/bible_queue.py:360` | except | JSON parsing raises `ValueError` | Returns `None`. |
| `.github/bible/bible_queue.py:362` | if | Parsed data is not a dictionary | Returns `None`. |
| `.github/bible/bible_queue.py:365` | if | Analysis path fails `SAFE_PATH` or contains a `..` segment | Returns `None`. |
| `.github/bible/bible_queue.py:367` | if | Depth is not in `DEPTH_VALUES` | Returns `None`. |
| `.github/bible/bible_queue.py:369` | for | Checks `model` and `verify_model` | Validates each setting's string form. |
| `.github/bible/bible_queue.py:371` | if | A nonempty model value fails `SAFE_MODEL` | Returns `None`. |

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

The module imports Python standard-library utilities and initializes queue labels, environment-derived agent settings, regexes, and timing/verification constants. (`.github/bible/bible_queue.py:42-90`, `.github/bible/bible_queue.py:346-350`)

It declares the `GitHub` API client (`.github/bible/bible_queue.py:88-332`), helper functions (`.github/bible/bible_queue.py:337-443`), and `Queue` coordinator (`.github/bible/bible_queue.py:448-1078`). The CLI `main` parses arguments, and the module guard calls it when executed as a script. (`.github/bible/bible_queue.py:1080-1130`)

## Surprises

`tarball` filters archive members to regular files and directories and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:275-288`)

The `Queue.session` docstring lists four result states, but the code also returns `start-error` when `GitHub.start_error` is truthy. (`.github/bible/bible_queue.py:465-470`)

<!-- cites .github/bible/bible_queue.py@68e91ae09c53c283e7402334cfe2a715785b33ed -->
