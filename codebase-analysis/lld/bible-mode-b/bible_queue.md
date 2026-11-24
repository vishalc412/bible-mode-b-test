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
| Lines | 1,291 |
| Role | Runs the Mode B analysis queue and its GitHub API client. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, subprocess, and filesystem modules used by the API client, queue, and CLI. (`.github/bible/bible_queue.py:42-56`) |
| Module-level state | `COPILOT`, `AGENT_LOGINS`, `AGENT_APP`, `START_ERROR`, verification/session limits, regexes, and `LABELS` are initialized at import; environment-backed values include `BIBLE_AGENT_LOGINS` and `BIBLE_AGENT_APP`. (`.github/bible/bible_queue.py:60-98`) |

## Summary

`main` exposes the `start`, `reconcile`, and `delta` CLI commands. It constructs `Queue` and `GitHub`; `Queue` coordinates tracker/session state and delegates repository operations to `GitHub`, whose methods build REST requests and a GraphQL ready-for-review mutation. `Queue.delta` also imports component-membership helpers from the analysis toolkit. (`.github/bible/bible_queue.py:1244-1290`, `.github/bible/bible_queue.py:473-1241`, `.github/bible/bible_queue.py:104-347`, `.github/bible/bible_queue.py:1205-1211`)

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| `GitHub` | class | 104-347 | [class](#github) |
| `GitHub.__init__` | method | 105-108 | [card](#github__init__repo-token-api-none) |
| `GitHub.request` | method | 110-119 | [card](#githubrequestmethod-url-body-none-timeout-60) |
| `GitHub.call` | method | 121-133 | [card](#githubcallmethod-path-body-none-ok404-false) |
| `GitHub.paged` | method | 135-143 | [card](#githubpagedpath) |
| `GitHub.issues` | method | 145-147 | [card](#githubissueslabels-state-open) |
| `GitHub.ensure_label` | method | 149-154 | [card](#githubensure_labelname-whycodebase-analysis) |
| `GitHub.ensure_labels` | method | 156-158 | [card](#githubensure_labels) |
| `GitHub.create_issue` | method | 160-167 | [card](#githubcreate_issuetitle-body-labels-assign-none) |
| `GitHub.me` | method | 169-173 | [card](#githubme) |
| `GitHub.default_branch` | method | 175-176 | [card](#githubdefault_branch) |
| `GitHub.branch_sha` | method | 178-180 | [card](#githubbranch_shabranch) |
| `GitHub.create_branch` | method | 182-183 | [card](#githubcreate_branchbranch-sha) |
| `GitHub.reset_branch` | method | 185-186 | [card](#githubreset_branchbranch-sha) |
| `GitHub.file` | method | 188-192 | [card](#githubfilepath-ref) |
| `GitHub.prs` | method | 194-196 | [card](#githubprsbase-none-state-open) |
| `GitHub.timeline` | method | 198-199 | [card](#githubtimelinenumber) |
| `GitHub.linked_prs` | method | 201-210 | [card](#githublinked_prsnumber) |
| `GitHub.branch_prs` | method | 212-215 | [card](#githubbranch_prsbranch-base) |
| `GitHub.agent_events` | method | 217-221 | [card](#githubagent_eventsnumber) |
| `GitHub.is_agent_pr` | method | 223-228 | [card](#githubis_agent_prpr) |
| `GitHub.start_error` | method | 230-239 | [card](#githubstart_errorissue) |
| `GitHub.assigned_at` | method | 241-244 | [card](#githubassigned_atissue) |
| `GitHub.pr_files` | method | 246-259 | [card](#githubpr_filesnumber) |
| `GitHub.commit_time` | method | 261-262 | [card](#githubcommit_timesha) |
| `GitHub.tarball` | method | 264-303 | [card](#githubtarballref-dest) |
| `GitHub.label` | method | 305-307 | [card](#githublabelnumber-name) |
| `GitHub.unlabel` | method | 309-310 | [card](#githubunlabelnumber-name) |
| `GitHub.comment` | method | 312-313 | [card](#githubcommentnumber-text) |
| `GitHub.close` | method | 315-316 | [card](#githubclosenumber-reason-completed) |
| `GitHub.set_body` | method | 318-319 | [card](#githubset_bodynumber-body) |
| `GitHub.unassign` | method | 321-322 | [card](#githubunassignnumber) |
| `GitHub.assign` | method | 324-325 | [card](#githubassignnumber-assign) |
| `GitHub.ready` | method | 327-335 | [card](#githubreadypr) |
| `GitHub.merge` | method | 337-341 | [card](#githubmergepr-title) |
| `GitHub.close_pr` | method | 343-344 | [card](#githubclose_prnumber) |
| `GitHub.create_pr` | method | 346-347 | [card](#githubcreate_prhead-base-title-body) |
| `now` | function | 352-354 | [card](#now) |
| `age` | function | 357-358 | [card](#age) |
| `shown_files` | function | 370-375 | [card](#shown_filespaths-limit10) |
| `settings_of` | function | 378-398 | [card](#settings_of) |
| `labels_of` | function | 401-402 | [card](#labels_of) |
| `comp_label` | function | 405-406 | [card](#comp_label) |
| `issue_text` | function | 409-415 | [card](#issue_textgh-path-ref-fallback_title) |
| `assignment` | function | 418-422 | [card](#assignmentgh-base-model) |
| `json_file` | function | 425-430 | [card](#json_filegh-path-ref) |
| `section` | function | 433-439 | [card](#sectiontext-title) |
| `report_facts` | function | 442-455 | [card](#report_factstext) |
| `as_int` | function | 458-462 | [card](#as_intvalue) |
| `status_of` | function | 465-468 | [card](#status_ofgh-path-ref) |
| `Queue` | class | 473-1241 | [class](#queue) |
| `Queue.__init__` | method | 474-476 | [card](#queue__init__gh-log-print) |
| `Queue.run_issues` | method | 478-479 | [card](#queue_run_issueslabels-state-open) |
| `Queue.agent_pr` | method | 481-487 | [card](#queue_agent_prissue-base) |
| `Queue.session` | method | 490-506 | [card](#queue_sessionissue-base-analysis-comp-none) |
| `Queue.held` | method | 508-541 | [card](#queue_heldissue) |
| `Queue.model_for` | method | 543-545 | [card](#queue_model_forissue) |
| `Queue.hold_start_error` | method | 547-553 | [card](#queue_hold_start_errorissue) |
| `Queue.fail_or_retry` | method | 555-574 | [card](#queue_fail_or_retryissue-pr-why) |
| `Queue.reconcile` | method | 577-588 | [card](#queue_reconcile) |
| `Queue.run` | method | 590-641 | [card](#queue_runtracker-settings) |
| `Queue.plan_phase` | method | 643-665 | [card](#queue_plan_phasetracker-settings-analysis) |
| `Queue.start_chunk` | method | 667-679 | [card](#queue_start_chunkanalysis-name-fresh-false-note) |
| `Queue.component` | method | 681-792 | [card](#queue_componentanalysis-name) |
| `Queue.follow` | method | 794-851 | [card](#queue_followanalysis-name-issue) |
| `Queue.check` | method | 853-878 | [card](#queue_checkanalysis-name-branch) |
| `Queue.could_not_check` | method | 880-891 | [card](#queuecould_not_checkkey-what-hold_labels-hold_title) |
| `Queue.whole_fingerprint` | method | 893-908 | [card](#queuewhole_fingerprintanalysis) |
| `Queue.assemble_phase` | method | 910-1023 | [card](#queue_assemble_phasetracker-settings-analysis) |
| `Queue.deferred_updates` | method | 1025-1037 | [card](#queuedeferred_updatestracker) |
| `Queue.whole_hold` | method | 1039-1045 | [card](#queuewhole_hold) |
| `Queue.revise_all_step` | method | 1047-1125 | [card](#queue_revise_all_steptracker-analysis) |
| `Queue.continue_if_unfinished` | method | 1127-1165 | [card](#queue_continue_if_unfinishedissue-pr-kind-analysis) |
| `Queue.render` | method | 1167-1178 | [card](#queue_rendertracker-settings-rows) |
| `Queue.delta` | method | 1181-1241 | [card](#queue_deltachanged-settings_analysiscodebase-analysis-recordtrue) |
| `main` | function | 1244-1290 | [card](#main) |

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
  shownfiles["shown_files"]
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
  couldnotcheck["Queue.could_not_check"]
  wholefingerprint["Queue.whole_fingerprint"]
  assemblephase["Queue.assemble_phase"]
  deferredupdates["Queue.deferred_updates"]
  wholehold["Queue.whole_hold"]
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
  component -->|"could_not_check"| couldnotcheck
  component -->|"report_facts"| reportfacts
  component -->|"comp_label"| complabel
  component -->|"as_int"| asint
  follow -->|"session"| session
  follow -->|"fail_or_retry"| failorretry
  follow -->|"labels_of"| labelsof
  follow -->|"shown_files"| shownfiles
  follow -->|"status_of"| statusof
  follow -->|"as_int"| asint
  check -->|"tarball"| tarball
  check -->|"subprocess.run"| subprocessrun
  wholefingerprint -->|"tarball"| tarball
  wholefingerprint -->|"subprocess.run"| subprocessrun
  couldnotcheck -->|"as_int"| asint
  couldnotcheck -->|"create_issue"| createissue
  deferredupdates -->|"me"| me
  deferredupdates -->|"timeline"| timeline
  wholehold -->|"run_issues"| runissues
  wholehold -->|"labels_of"| labelsof
  wholehold -->|"close"| close
  assemblephase -->|"run_issues"| runissues
  assemblephase -->|"session"| session
  assemblephase -->|"continue_if_unfinished"| continueunfinished
  assemblephase -->|"label"| label
  assemblephase -->|"labels_of"| labelsof
  assemblephase -->|"revise_all_step"| reviseall
  assemblephase -->|"whole_hold"| wholehold
  assemblephase -->|"whole_fingerprint"| wholefingerprint
  assemblephase -->|"could_not_check"| couldnotcheck
  assemblephase -->|"deferred_updates"| deferredupdates
  assemblephase -->|"delta"| delta
  assemblephase -->|"shown_files"| shownfiles
  assemblephase -->|"pr_files"| prfiles
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
  reviseall -->|"shown_files"| shownfiles
  assemblephase -->|"report_facts"| reportfacts
  assemblephase -->|"issue_text"| issuetext
  assemblephase -->|"held"| held
  assemblephase -->|"fail_or_retry"| failorretry
  render -->|"now"| now
  delta -->|"json_file"| jsonfile
  delta -->|"age"| age
  delta -->|"comment"| comment
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

Source: `.github/bible/bible_queue.py:104-347` <!-- code: fa8466d1289a -->

`GitHub` is a client for repository-scoped GitHub REST operations and the GraphQL ready-for-review mutation. Its instance fields are `repo`, `token`, normalized `api`, and `known_labels`; the last begins as `None` and is populated by `ensure_label`. (`.github/bible/bible_queue.py:105-108`, `.github/bible/bible_queue.py:149-154`)

No type annotations or factory are declared for the class; callers provide its constructor values. (inferred: `.github/bible/bible_queue.py:104-108`)

#### `GitHub.__init__(repo, token, api=None)`

Source: `.github/bible/bible_queue.py:105-108` <!-- code: b511658beb68 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1244`) |
| Calls | `os.environ.get`, `rstrip` |
| Purpose | Stores API credentials and a slash-trimmed API base URL, then initializes the label cache. |

**Steps**

1. Assigns `repo` and `token` to the instance. (`.github/bible/bible_queue.py:106`)
2. Selects `api`, then `GITHUB_API_URL`, then `https://api.github.com`, and removes trailing `/` characters. (`.github/bible/bible_queue.py:107`)
3. Initializes `known_labels` to `None`. (`.github/bible/bible_queue.py:108`)

**Pseudo-code**

```text
self.repo, self.token = repo, token
self.api = (api or GITHUB_API_URL or "https://api.github.com").rstrip("/")
self.known_labels = None
```

#### `GitHub.request(method, url, body=None, timeout=60)`

Source: `.github/bible/bible_queue.py:110-119` <!-- code: 1f8902892005 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.call` (`.github/bible/bible_queue.py:124`), `GitHub.tarball` (`.github/bible/bible_queue.py:270`), `GitHub.ready` (`.github/bible/bible_queue.py:332`) |
| Calls | `json.dumps`, `encode`, `urllib.request.Request`, `req.add_header`, `urllib.request.urlopen` |
| Purpose | Builds and opens an HTTP request with GitHub headers and an optional JSON body. |

**Steps**

1. Serializes a non-`None` body as encoded JSON; otherwise leaves request data unset. (`.github/bible/bible_queue.py:111`)
2. Creates a request using the supplied URL, method, and body bytes, and adds GitHub's JSON accept and API-version headers. (`.github/bible/bible_queue.py:112-114`)
3. Adds a bearer authorization header only when `token` is truthy, and adds JSON content type only when a body was serialized. (`.github/bible/bible_queue.py:115-118`)
4. Returns `urlopen`'s response using the supplied timeout. (`.github/bible/bible_queue.py:119`)

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
| `.github/bible/bible_queue.py:111` | conditional expression | `body is not None` | JSON is encoded; otherwise `data` is `None`. |
| `.github/bible/bible_queue.py:115` | if | `self.token` is truthy | Adds the bearer authorization header. |
| `.github/bible/bible_queue.py:117` | if | `data is not None` | Adds the JSON content-type header. |

#### `GitHub.call(method, path, body=None, ok404=False)`

Source: `.github/bible/bible_queue.py:121-133` <!-- code: 753c5f1a3922 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.paged` (`.github/bible/bible_queue.py:139`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:153`), `GitHub.create_issue` (`.github/bible/bible_queue.py:167`), `GitHub.default_branch` (`.github/bible/bible_queue.py:176`), `GitHub.branch_sha` (`.github/bible/bible_queue.py:179`), `GitHub.create_branch` (`.github/bible/bible_queue.py:183`), `GitHub.reset_branch` (`.github/bible/bible_queue.py:186`), `GitHub.file` (`.github/bible/bible_queue.py:189`), `GitHub.linked_prs` (`.github/bible/bible_queue.py:209`), `GitHub.commit_time` (`.github/bible/bible_queue.py:262`), `GitHub.label` (`.github/bible/bible_queue.py:307`), `GitHub.unlabel` (`.github/bible/bible_queue.py:310`), `GitHub.comment` (`.github/bible/bible_queue.py:313`), `GitHub.close` (`.github/bible/bible_queue.py:316`), `GitHub.set_body` (`.github/bible/bible_queue.py:319`), `GitHub.unassign` (`.github/bible/bible_queue.py:322`), `GitHub.assign` (`.github/bible/bible_queue.py:325`), `GitHub.merge` (`.github/bible/bible_queue.py:311`), `GitHub.close_pr` (`.github/bible/bible_queue.py:344`), `GitHub.create_pr` (`.github/bible/bible_queue.py:347`) |
| Calls | `path.startswith`, `GitHub.request`, response `read`, `json.loads`, `RuntimeError` |
| Purpose | Sends a REST request and converts response data and common request failures to Python values or a `RuntimeError`. |

**Steps**

1. Uses an absolute `path` beginning with `http` as-is; otherwise joins the API base, `/repos/`, repository, and path. (`.github/bible/bible_queue.py:122`)
2. Opens the request and reads its response bytes. (`.github/bible/bible_queue.py:123-125`)
3. On HTTP 404 with `ok404`, returns `None`; otherwise reads at most 300 decoded characters and raises a method/path/status/detail `RuntimeError`. (`.github/bible/bible_queue.py:126-130`)
4. Converts `URLError`, `TimeoutError`, and `OSError` to a `RuntimeError` containing the method, query-stripped path, and error. (`.github/bible/bible_queue.py:131-132`)
5. Decodes a nonempty payload as JSON; returns `{}` for an empty payload. (`.github/bible/bible_queue.py:133`)

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
| `.github/bible/bible_queue.py:122` | conditional expression | `path.startswith("http")` | Uses `path`; otherwise constructs a repository API URL. |
| `.github/bible/bible_queue.py:126` | except | Request raises `urllib.error.HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:127` | if | Status is 404 and `ok404` is true | Returns `None`. |
| `.github/bible/bible_queue.py:130` | raise | Other HTTP errors | Raises `RuntimeError` with method, path, status, and detail. |
| `.github/bible/bible_queue.py:131` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Enters network error handling. |
| `.github/bible/bible_queue.py:132` | raise | A listed network error occurred | Raises `RuntimeError` with method, path, and error. |
| `.github/bible/bible_queue.py:133` | conditional expression | Payload is nonempty | Decodes JSON; otherwise returns `{}`. |

#### `GitHub.paged(path)`

Source: `.github/bible/bible_queue.py:135-143` <!-- code: 1bb6c1899527 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.issues` (`.github/bible/bible_queue.py:147`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:151`), `GitHub.prs` (`.github/bible/bible_queue.py:196`), `GitHub.timeline` (`.github/bible/bible_queue.py:199`), `GitHub.branch_prs` (`.github/bible/bible_queue.py:215`), `GitHub.pr_files` (`.github/bible/bible_queue.py:234`) |
| Calls | `GitHub.call`, `len` |
| Purpose | Fetches successive pages of up to 100 results and returns their concatenation. |

**Steps**

1. Starts with an empty result and page number 1. (`.github/bible/bible_queue.py:136`)
2. Chooses `&` if `path` already contains `?`, otherwise `?`, then requests `per_page=100` and the current page with GET. (`.github/bible/bible_queue.py:137-139`)
3. Appends each batch; returns the accumulated list when a batch has fewer than 100 entries, otherwise increments the page and repeats. (`.github/bible/bible_queue.py:140-143`)

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
| `.github/bible/bible_queue.py:137` | while | Always | Repeats page requests until a short batch is returned. |
| `.github/bible/bible_queue.py:138` | conditional expression | `path` contains `?` | Chooses `&`; otherwise chooses `?`. |
| `.github/bible/bible_queue.py:141` | if | Batch length is less than 100 | Returns all accumulated entries; otherwise proceeds to the next page. |

#### `GitHub.issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:145-147` <!-- code: b3f969457f25 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run_issues` (`.github/bible/bible_queue.py:479`), `Queue.reconcile` (`.github/bible/bible_queue.py:570`), `Queue.delta` (`.github/bible/bible_queue.py:1176`), `main` (`.github/bible/bible_queue.py:1254`) |
| Calls | `urllib.parse.quote`, `join`, `GitHub.paged` |
| Purpose | Lists issues for encoded labels and a state, excluding pull requests. |

**Steps**

1. Joins labels with commas and URL-quotes the result. (`.github/bible/bible_queue.py:146`)
2. Pages `/issues` with the requested state and labels query, then keeps only objects without a `pull_request` key. (`.github/bible/bible_queue.py:147`)

**Pseudo-code**

```text
q = URL-quote(comma-joined labels)
return paged issues for state and q, excluding pull request objects
```

#### `GitHub.ensure_label(name, why="Codebase analysis run")`

Source: `.github/bible/bible_queue.py:149-154` <!-- code: c80387a5616e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.ensure_labels` (`.github/bible/bible_queue.py:158`), `GitHub.create_issue` (`.github/bible/bible_queue.py:162`), `GitHub.label` (`.github/bible/bible_queue.py:306`) |
| Calls | `GitHub.paged`, `GitHub.call`, `known_labels.add` |
| Purpose | Loads the known-label set on first use and creates a requested label if it is absent. |

**Steps**

1. If `known_labels` is `None`, pages `/labels` and caches their names. (`.github/bible/bible_queue.py:150-151`)
2. If `name` is missing, posts a label with the fixed color `5319e7` and `why` truncated to 100 characters, then adds the name to the cache. (`.github/bible/bible_queue.py:152-154`)

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
| `.github/bible/bible_queue.py:150` | if | `known_labels` is `None` | Fetches and caches current label names. |
| `.github/bible/bible_queue.py:152` | if | `name` is not in the cache | Creates the label and adds its name to the cache. |

#### `GitHub.ensure_labels()`

Source: `.github/bible/bible_queue.py:156-158` <!-- code: 3233fadcc4c0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1253`) |
| Calls | `LABELS.items`, `GitHub.ensure_label` |
| Purpose | Ensures each label defined in the module's `LABELS` mapping exists. |

**Steps**

1. Iterates each `(name, why)` pair in `LABELS` and invokes `ensure_label`. (`.github/bible/bible_queue.py:157-158`)

**Pseudo-code**

```text
for name, why in LABELS:
    ensure_label(name, why)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:157` | for | For each `(name, why)` in `LABELS.items()` | Calls `ensure_label` once for that pair. |

#### `GitHub.create_issue(title, body, labels, assign=None)`

Source: `.github/bible/bible_queue.py:160-167` <!-- code: c0db4afc186c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:563`), `Queue.plan_phase` (`.github/bible/bible_queue.py:643`), `Queue.start_chunk` (`.github/bible/bible_queue.py:669`), `Queue.component` (`.github/bible/bible_queue.py:751`, `.github/bible/bible_queue.py:765`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:793`), `Queue.delta` (`.github/bible/bible_queue.py:1179`), `main` (`.github/bible/bible_queue.py:1258`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures labels, optionally configures agent assignment, and creates an issue. |

**Steps**

1. Ensures every requested label, using its `LABELS` description or `Codebase analysis run` as the fallback. (`.github/bible/bible_queue.py:161-162`)
2. Builds a payload containing `title`, `body`, and `labels`; if `assign` is not `None`, adds the Copilot assignee and `agent_assignment`. (`.github/bible/bible_queue.py:163-166`)
3. Posts the payload to `/issues` and returns the result of `call`. (`.github/bible/bible_queue.py:167`)

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
| `.github/bible/bible_queue.py:161` | for | For each requested label | Calls `ensure_label` with its mapped or fallback description. |
| `.github/bible/bible_queue.py:164` | if | `assign` is not `None` | Adds `COPILOT` and the assignment value to the payload. |

#### `GitHub.me()`

Source: `.github/bible/bible_queue.py:169-173` <!-- code: 6c567c6be9c4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1138`) |
| Calls | `getattr`, `GitHub.call`, `get` |
| Purpose | Lazily fetches and caches the token owner's login. |

**Steps**

1. If `_me` is not already truthy, GETs the API `/user` URL and stores its `login`, defaulting to an empty string when the response is falsey or has no login. (`.github/bible/bible_queue.py:171-172`)
2. Returns the cached `_me` value. (`.github/bible/bible_queue.py:173`)

**Pseudo-code**

```text
if _me is falsey: _me = GET api/user.login or ""
return _me
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:171` | if | `_me` is falsey or absent | Fetches and caches the token owner's login. |

#### `GitHub.default_branch()`

Source: `.github/bible/bible_queue.py:175-176` <!-- code: 4eb167486c4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:569`), `Queue.delta` (`.github/bible/bible_queue.py:1014`) |
| Calls | `GitHub.call` |
| Purpose | Returns the repository's `default_branch` value. |

**Steps**

1. Gets the repository resource at the empty path and returns its `default_branch` field. (`.github/bible/bible_queue.py:176`)

**Pseudo-code**

```text
return GET repository["default_branch"]
```

#### `GitHub.branch_sha(branch)`

Source: `.github/bible/bible_queue.py:178-180` <!-- code: 446defb234bd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:661-662`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Returns a branch reference's object SHA or `None` when the reference is absent. |

**Steps**

1. Quotes `branch` and gets its head reference with `ok404=True`. (`.github/bible/bible_queue.py:179`)
2. Returns `ref["object"]["sha"]` if a reference was returned, otherwise `None`. (`.github/bible/bible_queue.py:180`)

**Pseudo-code**

```text
ref = GET quoted branch reference, allowing 404
return ref.object.sha if ref else None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:180` | conditional expression | A reference was returned | Returns its object SHA; otherwise returns `None`. |

#### `GitHub.create_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:182-183` <!-- code: b860758c1ca1 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:663`) |
| Calls | `GitHub.call` |
| Purpose | Creates a Git reference for a branch at a supplied SHA. |

**Steps**

1. Posts `ref: "refs/heads/" + branch` and `sha` to `/git/refs`. (`.github/bible/bible_queue.py:183`)

**Pseudo-code**

```text
POST /git/refs with ref "refs/heads/" + branch and sha
```

#### `GitHub.reset_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:185-186` <!-- code: 43e383793681 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:665`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Force-updates a branch reference to a supplied SHA. |

**Steps**

1. Quotes `branch` and PATCHes its head reference with the supplied SHA and `force: True`. (`.github/bible/bible_queue.py:186`)

**Pseudo-code**

```text
PATCH quoted head reference with sha and force=True
```

#### `GitHub.file(path, ref)`

Source: `.github/bible/bible_queue.py:188-192` <!-- code: e383f7bd9e38 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `issue_text` (`.github/bible/bible_queue.py:411`), `json_file` (`.github/bible/bible_queue.py:426`), `Queue.component` (`.github/bible/bible_queue.py:640`), `Queue.follow` (`.github/bible/bible_queue.py:826`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:772`), `Queue.delta` (`.github/bible/bible_queue.py:1023`) |
| Calls | `GitHub.call`, `urllib.parse.quote`, `isinstance`, `base64.b64decode`, `decode` |
| Purpose | Retrieves and decodes a text file from a repository reference. |

**Steps**

1. Quotes `path` and `ref` and GETs the contents endpoint with `ok404=True`. (`.github/bible/bible_queue.py:189`)
2. Returns `None` for a falsey response, a list response, or a response without `content`. (`.github/bible/bible_queue.py:190-191`)
3. Base64-decodes the content and decodes UTF-8 with replacement for invalid bytes. (`.github/bible/bible_queue.py:192`)

**Pseudo-code**

```text
got = GET quoted contents path at quoted ref, allowing 404
if got is falsey, a list, or lacks content: return None
return base64-decode content, then UTF-8 decode with replacement
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:190` | if | Response is falsey, a list, or has no `content` | Returns `None`. |

#### `GitHub.prs(base=None, state="open")`

Source: `.github/bible/bible_queue.py:194-196` <!-- code: e46dcb273277 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site found; unused (inferred: search for `.prs(` in `.github/bible/bible_queue.py` returned no matches). |
| Calls | `urllib.parse.quote`, `GitHub.paged` |
| Purpose | Lists pull requests by state and optional base branch. |

**Steps**

1. Builds `/pulls?state=<state>` and appends a URL-quoted base query only when `base` is truthy. (`.github/bible/bible_queue.py:195`)
2. Returns the paged results. (`.github/bible/bible_queue.py:196`)

**Pseudo-code**

```text
path = /pulls?state=state
if base is truthy: append quoted base query
return paged(path)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:195` | conditional expression | `base` is truthy | Appends `&base=` and the quoted base; otherwise appends nothing. |

#### `GitHub.timeline(number)`

Source: `.github/bible/bible_queue.py:198-199` <!-- code: 6df4539072ff -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.linked_prs` (`.github/bible/bible_queue.py:204`), `GitHub.agent_events` (`.github/bible/bible_queue.py:219`), `GitHub.start_error` (`.github/bible/bible_queue.py:233`), `GitHub.assigned_at` (`.github/bible/bible_queue.py:243`) |
| Calls | `GitHub.paged` |
| Purpose | Returns all paged timeline events for an issue number. |

**Steps**

1. Pages `/issues/<number>/timeline` and returns the result. (`.github/bible/bible_queue.py:199`)

**Pseudo-code**

```text
return paged /issues/<number>/timeline
```

#### `GitHub.linked_prs(number)`

Source: `.github/bible/bible_queue.py:201-210` <!-- code: 91e30cd14abd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:483`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:867`) |
| Calls | `GitHub.timeline`, `get`, `append`, `GitHub.call`, `sorted`, `set` |
| Purpose | Finds existing pull requests in this repository cross-referenced from an issue. |

**Steps**

1. Iterates the issue timeline and reads each event's source issue, defaulting missing source/repository values as shown. (`.github/bible/bible_queue.py:203-206`)
2. Collects the source number only for `cross-referenced` events whose source has a `pull_request` and whose repository full name equals this client's repository. (`.github/bible/bible_queue.py:207-208`)
3. Deduplicates and sorts numbers, GETs each pull request with `ok404=True`, and returns only non-`None` results. (`.github/bible/bible_queue.py:209-210`)

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
| `.github/bible/bible_queue.py:204` | for | For each issue timeline event | Inspects its source issue. |
| `.github/bible/bible_queue.py:207` | if | Event is a same-repository cross-reference with a pull request | Appends its source number. |

#### `GitHub.branch_prs(branch, base)`

Source: `.github/bible/bible_queue.py:212-215` <!-- code: fa42118d7d5a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:675`) |
| Calls | `split`, `GitHub.paged`, `urllib.parse.quote` |
| Purpose | Lists all-state pull requests from this repository's branch into a specified base. |

**Steps**

1. Takes the owner portion before `/` in `repo`. (`.github/bible/bible_queue.py:214`)
2. Pages `/pulls` with `state=all`, quoted `owner:branch` as `head`, and quoted `base`. (`.github/bible/bible_queue.py:215`)

**Pseudo-code**

```text
owner = first segment of repo
return paged /pulls with state=all, head=quoted(owner + ":" + branch), base=quoted(base)
```

#### `GitHub.agent_events(number)`

Source: `.github/bible/bible_queue.py:217-221` <!-- code: 23a18c0ca1f4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.is_agent_pr` (`.github/bible/bible_queue.py:228`), `Queue.session` (`.github/bible/bible_queue.py:497`) |
| Calls | `GitHub.timeline`, `get` |
| Purpose | Returns qualifying Copilot work timeline events as `(event, timestamp)` pairs. |

**Steps**

1. Reads the timeline and returns pairs containing each event name and `created_at`, defaulting a missing timestamp to the empty string. (`.github/bible/bible_queue.py:219`)
2. Includes only events whose performed-via-app slug equals `AGENT_APP` and whose event is `copilot_work_started` or `copilot_work_finished`. (`.github/bible/bible_queue.py:220-221`)

**Pseudo-code**

```text
return (event, created_at or "") for timeline events
    whose app slug is AGENT_APP and event is started or finished
```

#### `GitHub.is_agent_pr(pr)`

Source: `.github/bible/bible_queue.py:223-228` <!-- code: bad4f383c910 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:485`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:769`) |
| Calls | `get`, `GitHub.agent_events`, `any` |
| Purpose | Tests whether a pull request is attributed to a configured agent login or has a Copilot-start event. |

**Steps**

1. Reads `pr["user"]`, defaulting to an empty dictionary, and checks whether its login (defaulting to an empty string) is in `AGENT_LOGINS` and its type (defaulting to `"Bot"`) is `"Bot"`. (`.github/bible/bible_queue.py:225-226`)
2. Returns `True` immediately for that configured bot identity; otherwise checks the pull request timeline and returns whether any event is `copilot_work_started`. (`.github/bible/bible_queue.py:226-228`)

**Pseudo-code**

```text
if PR user's login is in AGENT_LOGINS and user type is Bot: return True
return any agent event is copilot_work_started
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:226` | if | PR user's login is in `AGENT_LOGINS` and user type is `"Bot"` | Returns `True` without checking the timeline. |

#### `GitHub.start_error(issue)`

Source: `.github/bible/bible_queue.py:230-239` <!-- code: 0287983c593a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:494`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:474`) |
| Calls | `GitHub.assigned_at`, `GitHub.timeline`, `get`, `START_ERROR.search`, `splitlines`, `strip` |
| Purpose | Returns the first matching agent start-error comment since the last assignment, or `None`. |

**Steps**

1. Gets the last assignment time using `assigned_at`, then scans the issue timeline. (`.github/bible/bible_queue.py:232-233`)
2. Chooses `actor` or `user`, then uses the actor login only when the actor type defaults to or is `"Bot"`. (`.github/bible/bible_queue.py:234-235`)
3. Requires a `commented` event by a configured agent at or after the assignment time and a body matching `START_ERROR`. (`.github/bible/bible_queue.py:236-237`)
4. Returns the stripped first body line, truncated to 300 characters, for the first qualifying event; returns `None` if no event qualifies. (`.github/bible/bible_queue.py:238-239`)

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
| `.github/bible/bible_queue.py:233` | for | For each issue timeline event | Checks actor, event time, and body. |
| `.github/bible/bible_queue.py:235` | conditional expression | Actor is a bot (or has no type) | Uses the actor login; otherwise uses an empty login. |
| `.github/bible/bible_queue.py:236` | if | Comment event from configured agent at/after assignment matches `START_ERROR` | Returns the bounded first line; otherwise continues scanning. |

#### `GitHub.assigned_at(issue)`

Source: `.github/bible/bible_queue.py:241-244` <!-- code: 8dec0d30b502 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.start_error` (`.github/bible/bible_queue.py:232`), `Queue.session` (`.github/bible/bible_queue.py:496`) |
| Calls | `GitHub.timeline`, `get`, `max` |
| Purpose | Returns the newest timestamp for an assignment event, falling back to issue creation time. |

**Steps**

1. Collects nonempty `created_at` values from `assigned` timeline events for the issue. (`.github/bible/bible_queue.py:243`)
2. Returns the maximum timestamp, or `issue["created_at"]` if there were none. (`.github/bible/bible_queue.py:244`)

**Pseudo-code**

```text
times = created_at for assigned events with a timestamp
return max(times) if any, otherwise issue.created_at
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:244` | conditional expression | At least one assignment timestamp exists | Returns the newest timestamp; otherwise uses issue creation time. |

#### `GitHub.pr_files(number)`

Source: `.github/bible/bible_queue.py:246-259` <!-- code: 58ad7fd72404 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:792`, `.github/bible/bible_queue.py:795`, `.github/bible/bible_queue.py:819`) |
| Calls | `GitHub.paged`, `as_int`, `GitHub.call`, `get`, `len`, `append`, `RuntimeError` |
| Purpose | Returns each changed filename and, when present, its previous name. |

**Steps**

1. Pages the pull request files endpoint and reads the pull request's `changed_files` count. (`.github/bible/bible_queue.py:249-250`)
2. If the expected count is nonzero and differs from the number listed, raises `RuntimeError` rather than accepting an incomplete file list. (`.github/bible/bible_queue.py:251-253`)
3. Appends each current `filename`, then appends `previous_filename` when truthy, and returns the list. (`.github/bible/bible_queue.py:254-259`)

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
| `.github/bible/bible_queue.py:251` | if | Expected count is nonzero and differs from listed count | Raises `RuntimeError` for an incomplete file list. |
| `.github/bible/bible_queue.py:252` | raise | Listed count differs from a nonzero expected count | Raises the incomplete-file-list `RuntimeError`. |
| `.github/bible/bible_queue.py:255` | for | For each paged pull request file | Appends its current filename. |
| `.github/bible/bible_queue.py:257` | if | `previous_filename` is truthy | Appends the previous filename. |

#### `GitHub.commit_time(sha)`

Source: `.github/bible/bible_queue.py:261-262` <!-- code: a3036655ce65 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:500`) |
| Calls | `GitHub.call` |
| Purpose | Returns the committer date for a commit SHA. |

**Steps**

1. GETs `/commits/<sha>` and returns `commit.committer.date`. (`.github/bible/bible_queue.py:262`)

**Pseudo-code**

```text
return GET /commits/<sha>.commit.committer.date
```

#### `GitHub.tarball(ref, dest)`

Source: `.github/bible/bible_queue.py:264-303` <!-- code: a84776e4e94b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.check` (`.github/bible/bible_queue.py:862`), `Queue.whole_fingerprint` (`.github/bible/bible_queue.py:900`) |
| Calls | `urllib.parse.quote`, `tempfile.TemporaryFile`, `self.request`, `resp.read`, `len`, `RuntimeError`, `buf.seek`, `os.path.abspath`, `tarfile.open`, `max`, `member.name.split`, `member.isfile`, `member.isdir`, `os.path.join`, `os.path.normpath`, `target.startswith`, `os.makedirs`, `os.path.dirname`, `tar.extractfile`, `open`, `shutil.copyfileobj` |
| Purpose | Downloads a compressed repository archive to a temporary file, enforces size/member limits, then unpacks only regular files and directories whose normalized paths stay below `dest`. |

**Steps**

1. Quotes `ref`, builds the repository tarball URL, then streams response chunks of `1 << 20` bytes into a temporary file with a 300-second request timeout. It increments `total` and raises `RuntimeError` once bytes exceed `MAX_TARBALL`; request URL, timeout, and OS errors are re-raised as `RuntimeError`. (`.github/bible/bible_queue.py:267-281`)
2. Seeks the buffer to its beginning, resolves `dest` as an absolute path, and opens it as a gzip tar archive. (`.github/bible/bible_queue.py:282-284`)
3. Counts each member and its nonnegative declared size; raises if member count exceeds `MAX_MEMBERS` or unpacked size exceeds `MAX_UNPACKED`. It splits member names once at `/` and skips names without a nonempty relative part or members that are not regular files/directories. (`.github/bible/bible_queue.py:285-294`)
4. Joins the relative part to the root, normalizes it, and skips paths not starting with `root + os.sep`. Directories are created recursively; files get a created parent and their extracted bytes are copied into a binary file. (`.github/bible/bible_queue.py:295-303`)

**Pseudo-code**

```text
stream request(GET, quoted tarball URL, timeout=300) to temporary file
raise RuntimeError on request URL/timeout/OS errors or total > MAX_TARBALL
seek; root = absolute(dest)
for each archive member:
    count members and max(member.size, 0); raise if either archive limit is exceeded
    split member.name once; skip absent relative path or non-file/non-directory
    target = normpath(join(root, relative path)); skip unless target starts root + separator
    if directory: mkdir(target)
    else: mkdir(parent); copy extracted member to open(target, "wb")
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:272` | while | Each read iteration | Reads the next response chunk. |
| `.github/bible/bible_queue.py:274` | if | The response chunk is empty | Stops streaming. |
| `.github/bible/bible_queue.py:277` | if | Accumulated response bytes exceed `MAX_TARBALL` | Enters the size-error path. |
| `.github/bible/bible_queue.py:278` | raise | Tarball exceeds `MAX_TARBALL` | Raises a reference-specific `RuntimeError`. |
| `.github/bible/bible_queue.py:280` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Converts the failure to `RuntimeError`. |
| `.github/bible/bible_queue.py:281` | raise | A listed request failure occurred | Raises `RuntimeError` with the reference and error. |
| `.github/bible/bible_queue.py:286` | for | Each tar member | Updates counts and validates the member. |
| `.github/bible/bible_queue.py:289` | if | Members exceed `MAX_MEMBERS` or unpacked bytes exceed `MAX_UNPACKED` | Enters the archive-limit error path. |
| `.github/bible/bible_queue.py:290` | raise | Either archive limit is exceeded | Raises `RuntimeError` before unpacking that member. |
| `.github/bible/bible_queue.py:293` | if | Missing relative path or member is neither file nor directory | Skips the member. |
| `.github/bible/bible_queue.py:296` | if | Normalized target is outside the root-prefix check | Skips the path. |
| `.github/bible/bible_queue.py:298` | if | Member is a directory | Creates it and continues without file extraction. |

#### `GitHub.label(number, name)`

Source: `.github/bible/bible_queue.py:305-307` <!-- code: 3c67a9360e66 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:541`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:553`), `Queue.follow` (`.github/bible/bible_queue.py:804-805`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures and adds one label to an issue. |

**Steps**

1. Ensures the label using its `LABELS` description or the default description. (`.github/bible/bible_queue.py:306`)
2. Posts `{"labels": [name]}` to the issue labels endpoint. (`.github/bible/bible_queue.py:307`)

**Pseudo-code**

```text
ensure label using mapped description or default
POST issue labels with [name]
```

#### `GitHub.unlabel(number, name)`

Source: `.github/bible/bible_queue.py:309-310` <!-- code: caf34958b931 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:830`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Removes a label from an issue and permits a missing-label response. |

**Steps**

1. URL-quotes `name` and sends DELETE to the issue label endpoint with `ok404=True`. (`.github/bible/bible_queue.py:310`)

**Pseudo-code**

```text
DELETE quoted issue label endpoint, allowing 404
```

#### `GitHub.comment(number, text)`

Source: `.github/bible/bible_queue.py:312-313` <!-- code: a05e7f494734 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:465`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:543`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:550`, `.github/bible/bible_queue.py:555`, `.github/bible/bible_queue.py:558`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:984`) |
| Calls | `GitHub.call` |
| Purpose | Creates an issue comment with the given body. |

**Steps**

1. Posts `{"body": text}` to `/issues/<number>/comments`. (`.github/bible/bible_queue.py:313`)

**Pseudo-code**

```text
POST issue comments with body=text
```

#### `GitHub.close(number, reason="completed")`

Source: `.github/bible/bible_queue.py:315-316` <!-- code: db2a40d380a0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:559`), `Queue.run` (`.github/bible/bible_queue.py:613`), `Queue.component` (`.github/bible/bible_queue.py:634`), `Queue.follow` (`.github/bible/bible_queue.py:831`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:909`, `.github/bible/bible_queue.py:985`) |
| Calls | `GitHub.call` |
| Purpose | Closes an issue with the supplied state reason. |

**Steps**

1. PATCHes `/issues/<number>` with `state: "closed"` and the supplied `state_reason`. (`.github/bible/bible_queue.py:316`)

**Pseudo-code**

```text
PATCH issue state=closed and state_reason=reason
```

#### `GitHub.set_body(number, body)`

Source: `.github/bible/bible_queue.py:318-319` <!-- code: 56545a0f998b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:462`), `Queue.render` (`.github/bible/bible_queue.py:1002`) |
| Calls | `GitHub.call` |
| Purpose | Replaces an issue's body. |

**Steps**

1. PATCHes `/issues/<number>` with `{"body": body}`. (`.github/bible/bible_queue.py:319`)

**Pseudo-code**

```text
PATCH issue body=body
```

#### `GitHub.unassign(number)`

Source: `.github/bible/bible_queue.py:321-322` <!-- code: 415484346894 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:542`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:554`) |
| Calls | `GitHub.call` |
| Purpose | Removes the configured Copilot assignee from an issue. |

**Steps**

1. Sends DELETE to `/issues/<number>/assignees` with `COPILOT` as the sole assignee. (`.github/bible/bible_queue.py:322`)

**Pseudo-code**

```text
DELETE issue assignees with [COPILOT]
```

#### `GitHub.assign(number, assign)`

Source: `.github/bible/bible_queue.py:324-325` <!-- code: 8fb2f09224db -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:464`) |
| Calls | `GitHub.call` |
| Purpose | Assigns Copilot to an issue with the provided agent-assignment data. |

**Steps**

1. Posts `COPILOT` as the sole assignee and includes the supplied `agent_assignment`. (`.github/bible/bible_queue.py:325`)

**Pseudo-code**

```text
POST issue assignees with [COPILOT] and agent_assignment=assign
```

#### `GitHub.ready(pr)`

Source: `.github/bible/bible_queue.py:327-335` <!-- code: ae31dacf00e7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.merge` (`.github/bible/bible_queue.py:339`) |
| Calls | `endswith`, `GitHub.request`, response `read`, `RuntimeError` |
| Purpose | Marks a draft pull request ready for review through GitHub GraphQL. |

**Steps**

1. Defines the `markPullRequestReadyForReview` mutation and chooses the GraphQL URL; for an API base ending `/api/v3`, removes `/v3` before adding `/graphql`. (`.github/bible/bible_queue.py:329-330`)
2. POSTs the query and `pr["node_id"]` as the `id` variable, then reads the response. (`.github/bible/bible_queue.py:331-333`)
3. Converts an `HTTPError` to a `RuntimeError` containing the GraphQL operation and HTTP status. (`.github/bible/bible_queue.py:334-335`)

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
| `.github/bible/bible_queue.py:330` | conditional expression | API URL ends with `/api/v3` | Removes `/v3` before appending `/graphql`; otherwise appends `/graphql` directly. |
| `.github/bible/bible_queue.py:334` | except | Request raises `HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:335` | raise | GraphQL request raises `HTTPError` | Raises `RuntimeError` with operation and HTTP status. |

#### `GitHub.merge(pr, title)`

Source: `.github/bible/bible_queue.py:337-341` <!-- code: cea69f3a2a18 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:829`) |
| Calls | `get`, `GitHub.ready`, `GitHub.call` |
| Purpose | Marks a draft ready, when needed, and requests a squash merge with the supplied title. |

**Steps**

1. Calls `ready` only when `pr["draft"]` is truthy. (`.github/bible/bible_queue.py:338-339`)
2. PUTs `/pulls/<number>/merge` with `merge_method: "squash"`, the supplied `commit_title`, and the current head SHA. (`.github/bible/bible_queue.py:340-341`)

**Pseudo-code**

```text
if PR is draft: mark it ready
PUT merge request with squash method and title
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:338` | if | `pr["draft"]` is truthy | Calls `ready` before requesting the merge. |

#### `GitHub.close_pr(number)`

Source: `.github/bible/bible_queue.py:343-344` <!-- code: c5e4b3b311ae -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:551`) |
| Calls | `GitHub.call` |
| Purpose | Closes a pull request. |

**Steps**

1. PATCHes `/pulls/<number>` with `state: "closed"`. (`.github/bible/bible_queue.py:344`)

**Pseudo-code**

```text
PATCH pull request state=closed
```

#### `GitHub.create_pr(head, base, title, body)`

Source: `.github/bible/bible_queue.py:346-347` <!-- code: 9b2aa4667c1c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:708`) |
| Calls | `GitHub.call` |
| Purpose | Creates a pull request and returns the API result. |

**Steps**

1. POSTs `head`, `base`, `title`, and `body` to `/pulls`, returning `call`'s result. (`.github/bible/bible_queue.py:347`)

**Pseudo-code**

```text
return POST /pulls with head, base, title, and body
```

### `Queue`

Source: `.github/bible/bible_queue.py:473-1241` <!-- code: c7b3115b36f1 -->

`Queue` coordinates tracker issues, component sessions, verification/revision cycles, assembly, and delta updates. Its constructor sets the GitHub client, logger, and skill directory; methods also populate run-specific fields such as `default`, `settings`, `tracker`, `run_label`, and `estimate` (`.github/bible/bible_queue.py:397-399,464-483,486-496,498-534`).

#### `Queue.__init__(gh, log=print)`

Source: `.github/bible/bible_queue.py:474-476` <!-- code: 11924208c0e9 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1245`) |
| Calls | `os.environ.get` |
| Purpose | Stores the GitHub client and logger, and selects the skills directory. |

**Steps**

1. Stores `gh` and `log` on the instance. (`.github/bible/bible_queue.py:475`)
2. Reads `BIBLE_SKILLS`, defaulting to `.github/skills`. (`.github/bible/bible_queue.py:476`)

**Pseudo-code**

```text
self.gh, self.log = gh, log
self.skills = BIBLE_SKILLS or ".github/skills"
```

#### `Queue.run_issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:478-479` <!-- code: 9186c4a33e43 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:530`), `Queue.plan_phase` (`.github/bible/bible_queue.py:636`), `Queue.start_chunk` (`.github/bible/bible_queue.py:664`), `Queue.component` (`.github/bible/bible_queue.py:684`, `.github/bible/bible_queue.py:693`, `.github/bible/bible_queue.py:700`, `.github/bible/bible_queue.py:703`, `.github/bible/bible_queue.py:635`, `.github/bible/bible_queue.py:637`, `.github/bible/bible_queue.py:639`, `.github/bible/bible_queue.py:712-713`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:858`, `.github/bible/bible_queue.py:860`) |
| Calls | `self.gh.issues` |
| Purpose | Queries issues for the requested labels plus this run's unique label. |

**Steps**

1. Appends `self.run_label` to the supplied labels and calls `gh.issues` with the requested state. (`.github/bible/bible_queue.py:479`)

**Pseudo-code**

```text
return gh.issues(labels + [run_label], state)
```

#### `Queue.agent_pr(issue, base)`

Source: `.github/bible/bible_queue.py:481-487` <!-- code: 471c772b908b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:492`) |
| Calls | `reversed`, `self.gh.linked_prs`, `get`, `self.gh.is_agent_pr` |
| Purpose | Finds the newest linked pull request that is open, same-repository, targets `base`, and is by the agent. |

**Steps**

1. Iterates linked pull requests in reverse order. (`.github/bible/bible_queue.py:483`)
2. Reads the head repository full name, defaulting missing nested values to `{}`. (`.github/bible/bible_queue.py:484`)
3. Returns the first PR whose state is `open`, head repository is `gh.repo`, base ref matches, and `is_agent_pr` is true. (`.github/bible/bible_queue.py:485-486`)
4. Returns `None` when no linked PR qualifies. (`.github/bible/bible_queue.py:487`)

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
| `.github/bible/bible_queue.py:483` | for | For each linked PR in reverse order | Checks newer linked PRs first. |
| `.github/bible/bible_queue.py:485` | if | PR is open, same-repository, targets `base`, and is an agent PR | Returns that PR. |

#### `Queue.session(issue, base, analysis, comp=None)`

Source: `.github/bible/bible_queue.py:490-506` <!-- code: 6fe9d410226f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:649`), `Queue.follow` (`.github/bible/bible_queue.py:778`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:913`) |
| Calls | `self.agent_pr`, `self.gh.start_error`, `age`, `self.gh.assigned_at`, `self.gh.agent_events`, `sorted`, `self.gh.commit_time`, `bool`, `status_of`, `labels_of`, `get` |
| Purpose | Classifies an issue's session as waiting, running, finished, no-start, or start-error and returns its PR if present. |

**Steps**

1. Looks up the agent PR. If absent, returns `("start-error", None)` for a detected start error; otherwise compares issue assignment age to `NO_PR_AFTER` and returns `no-start` or `waiting`. (`.github/bible/bible_queue.py:492-496`)
2. If agent work events exist, sorts them by timestamp and returns `finished` when the latest is `copilot_work_finished`, else `running`, together with the PR. (`.github/bible/bible_queue.py:497-499`)
3. Without work events, computes age from the PR head commit and marks `asked` when reviewers were requested or the PR is not draft. (`.github/bible/bible_queue.py:500-501`)
4. For a component chunk, reads status at the PR head SHA and considers it finished when final status plus an asked/idle condition holds, or when pushed age exceeds three times `IDLE_AFTER`. (`.github/bible/bible_queue.py:502-505`)
5. Otherwise returns `finished` when `asked` or pushed age exceeds `IDLE_AFTER`, else `running`; both paths include the PR. (`.github/bible/bible_queue.py:506`)

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
| `.github/bible/bible_queue.py:493` | if | No agent PR was found | Enters start-error/no-start/waiting classification. |
| `.github/bible/bible_queue.py:494` | if | `start_error(issue)` is truthy | Returns start-error without a PR. |
| `.github/bible/bible_queue.py:496` | conditional expression | Assignment age exceeds `NO_PR_AFTER` | Returns `no-start`; otherwise returns `waiting`. |
| `.github/bible/bible_queue.py:498` | if | Agent work events exist | Uses latest work event to classify session state. |
| `.github/bible/bible_queue.py:499` | conditional expression | Latest work event is `copilot_work_finished` | Returns finished; otherwise running. |
| `.github/bible/bible_queue.py:502` | if | `comp` is truthy and issue has `bible-chunk` label | Uses head status and component-specific age rules. |
| `.github/bible/bible_queue.py:505` | conditional expression | Final status and asked/idle condition holds, or pushed age exceeds `3 * IDLE_AFTER` | Returns finished; otherwise running. |
| `.github/bible/bible_queue.py:506` | conditional expression | `asked` or pushed age exceeds `IDLE_AFTER` | Returns finished; otherwise running. |

#### `Queue.held(issue)`

Source: `.github/bible/bible_queue.py:508-541` <!-- code: c519a460eab6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:656`), `Queue.component` (`.github/bible/bible_queue.py:696`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:985`) |
| Calls | `labels_of`, `any`, `get`, `issue.get`, `self.gh.timeline`, `max`, `e.get`, `self.gh.label`, `self.gh.comment`, `self.gh.close`, `l.startswith`, `ATTEMPT.sub`, `self.gh.set_body`, `re.search`, `self.gh.assign`, `assignment`, `self.model_for`, `base.group` |
| Purpose | Holds issues marked for a person, closes released component sessions, or reassigns other unassigned sessions to Copilot. |

**Steps**

1. Returns `True` when the labels include `bible-needs-human`. (`.github/bible/bible_queue.py:516`)
2. Otherwise returns `False` immediately when an assignee login belongs to `AGENT_LOGINS`. (`.github/bible/bible_queue.py:518`)
3. Reads issue timeline events and finds the latest added and removed timestamps for `bible-needs-human`; if removal is absent or not newer, labels and comments the issue for human review and returns `True`. (`.github/bible/bible_queue.py:519-531`)
4. If a `bible/` label exists after release, comments and closes the issue as `not_planned`, returning `released`. (`.github/bible/bible_queue.py:532-535`)
5. Otherwise resets the `Attempt:` marker, saves the body, extracts `Base branch:` or uses `self.default`, assigns Copilot with the selected model, comments, and returns `False`. (`.github/bible/bible_queue.py:536-541`)

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
| `.github/bible/bible_queue.py:516` | if | Labels contain `bible-needs-human` | Returns `True`. |
| `.github/bible/bible_queue.py:518` | if | An assignee login belongs to `AGENT_LOGINS` | Returns `False`. |
| `.github/bible/bible_queue.py:525` | if | The human-label removal is absent or not newer than its addition | Labels, comments, and returns `True`. |
| `.github/bible/bible_queue.py:531` | return | No valid release follows the human hold | Stops before reassignment. |
| `.github/bible/bible_queue.py:532` | if | A component label begins `bible/` after release | Closes and returns `released`; otherwise reassigns. |
| `.github/bible/bible_queue.py:539` | conditional expression | A `Base branch:` match exists | Uses its captured branch; otherwise uses `self.default`. |

#### `Queue.model_for(issue)`

Source: `.github/bible/bible_queue.py:543-545` <!-- code: 17f084589886 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:473`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:573`) |
| Calls | `labels_of`, `self.settings.get` |
| Purpose | Selects the verification model for verification issue types, otherwise the normal model. |

**Steps**

1. Gets the issue's label names. (`.github/bible/bible_queue.py:544`)
2. Returns `verify_model` when labels intersect `bible-verify` or `bible-verify-all`; otherwise returns `model`. (`.github/bible/bible_queue.py:545`)

**Pseudo-code**

```text
kinds = labels_of(issue)
return settings.verify_model if kinds intersects verify labels
       else settings.model
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:545` | conditional expression | `kinds` intersects the verification labels | Returns `verify_model`; otherwise returns `model`. |

#### `Queue.hold_start_error(issue)`

Source: `.github/bible/bible_queue.py:547-553` <!-- code: 510c0f07df06 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:660`), `Queue.follow` (`.github/bible/bible_queue.py:801`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:999`) |
| Calls | `self.gh.start_error`, `self.gh.label`, `self.gh.unassign`, `self.gh.comment` |
| Purpose | Holds a session with an agent start error for human intervention. |

**Steps**

1. Gets the start-error text or uses `Copilot could not start`. (`.github/bible/bible_queue.py:474`)
2. Adds `bible-needs-human`, unassigns Copilot, and posts a comment containing the reason and remediation guidance. (`.github/bible/bible_queue.py:541-544`)

**Pseudo-code**

```text
why = start_error(issue) or fallback message
label issue bible-needs-human
unassign Copilot
comment why and instructions for removing the hold
```

#### `Queue.fail_or_retry(issue, pr, why)`

Source: `.github/bible/bible_queue.py:555-574` <!-- code: c86515a02433 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase`, `Queue.component`, `Queue.assemble_phase`, `Queue.revise_all_step`, `Queue.delta` |
| Calls | `ATTEMPT.search`, `int`, `self.gh.comment`, `self.gh.close_pr`, `self.gh.label`, `self.gh.unassign`, `self.gh.close`, `ATTEMPT.sub`, `re.search`, `self.gh.create_issue`, `sorted`, `assignment`, `self.model_for`, `labels_of`, `startswith` |
| Purpose | Closes a failed attempt and opens its retry, or holds the issue after a second failure. |

**Steps**

1. Parses the attempt number from the issue body, defaulting to 1. (`.github/bible/bible_queue.py:548`)
2. If a PR was supplied, comments that it was not merged and closes it. (`.github/bible/bible_queue.py:549-551`)
3. When attempt is at least 2, labels and unassigns the issue, posts a human-action comment, and returns `False`. (`.github/bible/bible_queue.py:552-557`)
4. Otherwise comments that a new attempt will open, closes the issue with `not_planned`, updates or prepends the attempt marker, and extracts the base branch or uses `self.default`. (`.github/bible/bible_queue.py:558-562`)
5. Creates a replacement issue with only labels beginning `bible`, sorted, and assignment data for the chosen base and model; returns `True`. (`.github/bible/bible_queue.py:563-565`)

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
| `.github/bible/bible_queue.py:558` | if | `pr` is truthy | Comments that it was not merged and closes the PR; otherwise skips PR updates. |
| `.github/bible/bible_queue.py:561` | if | Attempt number is at least 2 | Labels and unassigns the issue, comments for human action, and returns `False`; otherwise opens a retry. |
| `.github/bible/bible_queue.py:569` | conditional expression | The issue body contains an attempt marker | Replaces it with the incremented attempt; otherwise prepends `Attempt: 2`. |
| `.github/bible/bible_queue.py:573` | conditional expression | A `Base branch:` match exists in the original body | Assigns the retry to that branch; otherwise uses `self.default`. |

#### `Queue.reconcile()`

Source: `.github/bible/bible_queue.py:577-588` <!-- code: 10e9886e081f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1261`) |
| Calls | `self.gh.default_branch`, `self.gh.issues`, `settings_of`, `self.log`, `self.run`, `type` |
| Purpose | Processes each open tracker independently so one failing tracker does not prevent others. |

**Steps**

1. Sets a monotonic run deadline and reads the default branch. (`.github/bible/bible_queue.py:578-579`)
2. Iterates open `bible-tracker` issues, parses each tracker with `settings_of`, logs and skips trackers with falsey settings, and invokes `run` for the rest. (`.github/bible/bible_queue.py:580-586`)
3. Catches any `Exception` raised while processing one tracker, logs its number, exception class, and message, then continues to the next tracker. (`.github/bible/bible_queue.py:585-588`)

**Pseudo-code**

```text
deadline = monotonic() + RUN_BUDGET
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
| `.github/bible/bible_queue.py:580` | for | For each open tracker | Loads settings and processes the tracker. |
| `.github/bible/bible_queue.py:582` | if | Settings are falsey | Logs and skips the tracker. |
| `.github/bible/bible_queue.py:587` | except | `run` raises an `Exception` | Logs the tracker and error; other trackers remain eligible. |

#### `Queue.run(tracker, settings)`

Source: `.github/bible/bible_queue.py:590-641` <!-- code: ab24ac87df39 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:586`) |
| Calls | `settings.get`, `json_file`, `catalog.get`, `self.plan_phase`, `isinstance`, `c.get`, `str.strip`, `asked.split`, `n.strip`, `join`, `self.render`, `self.run_issues`, `gh.close`, `self.component`, `str.endswith`, `str.startswith`, `as_int`, `self.start_chunk`, `type`, `str`, `all`, `rows.values`, `self.assemble_phase` |
| Purpose | Sends an incomplete catalog to planning; otherwise validates selected components, advances their queue states within the configured concurrency cap, and renders tracker status. |

**Steps**

1. Selects the analysis directory (default `codebase-analysis`), stores tracker/settings and a tracker-specific run label, then extracts JSON state from the tracker body. Invalid JSON and a non-dictionary state become `{}`. (`.github/bible/bible_queue.py:591-600`)
2. Reads `components.json` at the default branch. A non-dictionary, proposed catalog, or catalog without a list-valued `components` field sends the tracker to `plan_phase`. (`.github/bible/bible_queue.py:601-603`)
3. Converts dictionary entries' names to strings, filters names against `NAME`, and stops with a rendered error if any catalog entry has an invalid name. It strips the selection setting, selects all names for empty/`all`, otherwise splits comma-separated names, then stops if a requested name is unknown or the selection is empty. (`.github/bible/bible_queue.py:606-620`)
4. Closes open plan issues, builds session estimates, evaluates each wanted component independently, stores exceptions as bounded error rows, and counts rows in active/starting/merged/waiting states. (`.github/bible/bible_queue.py:621-630`)
5. Converts `concurrency` with `as_int`; starts each eligible `not started` component as a fresh chunk while unlimited (`cap == 0`) or below the cap. A start increments `active`; `RuntimeError` becomes a bounded error row. (`.github/bible/bible_queue.py:631-638`)
6. If all rows equal `merged`, adds the whole-analysis assembly result, then renders the tracker rows. (`.github/bible/bible_queue.py:639-641`)

**Pseudo-code**

```text
analysis = settings.get("analysis", "codebase-analysis")
store tracker/settings/run label; parse hidden state as a dict or {}
catalog = read components.json
if catalog is not a dict, is proposed, or components is not a list: return plan_phase(...)
listed = string names from dictionary entries; names = those matching NAME
if a listed name is invalid: render stopped-settings row; return
parse selection; if unknown names or no wanted names: render stopped-settings row; return
close open plan issues; record session estimates
for each wanted name: evaluate component; catch Exception as bounded row; count active states
cap = concurrency converted to integer
for each wanted name: if not started and cap permits, start fresh chunk
if every row is merged: add assembly status
render rows
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:596` | conditional expression | A state marker matched the tracker body | Decodes its JSON; otherwise initializes `{}`. |
| `.github/bible/bible_queue.py:597` | except | `json.loads` raises `ValueError` | Uses an empty state mapping. |
| `.github/bible/bible_queue.py:599` | if | Parsed state is not a dictionary | Replaces it with `{}`. |
| `.github/bible/bible_queue.py:602` | if | Catalog is invalid, proposed, or has no components list | Returns the planning phase. |
| `.github/bible/bible_queue.py:608` | if | Any listed component name fails `NAME` | Renders a stopped-settings status and returns. |
| `.github/bible/bible_queue.py:614` | conditional expression | Selection is empty or `all` | Selects all names; otherwise parses comma-separated names. |
| `.github/bible/bible_queue.py:616` | if | Requested names are unknown or selection is empty | Renders the stopped-settings status and returns. |
| `.github/bible/bible_queue.py:619` | conditional expression | Unknown names exist | Reports them; otherwise reports that no component was selected. |
| `.github/bible/bible_queue.py:621` | for | Each open plan issue | Closes the issue. |
| `.github/bible/bible_queue.py:625` | for | Each selected component | Evaluates its state. |
| `.github/bible/bible_queue.py:628` | except | Component evaluation raises `Exception` | Stores an error row, truncating its message to 160 characters. |
| `.github/bible/bible_queue.py:632` | for | Each selected component | Considers starting a component that is not started. |
| `.github/bible/bible_queue.py:633` | if | Row is `not started` and capacity is unlimited or available | Attempts to start a fresh chunk. |
| `.github/bible/bible_queue.py:637` | except | Starting the chunk raises `RuntimeError` | Stores a bounded error row. |
| `.github/bible/bible_queue.py:639` | if | Every component row is `merged` | Adds the whole-analysis assembly result. |

#### `Queue.plan_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:643-665` <!-- code: f5b3e835d2d7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:603`) |
| Calls | `self.run_issues`, `issue_text`, `self.gh.create_issue`, `self.render`, `assignment`, `settings.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry` |
| Purpose | Creates or tracks the plan issue and reports plan-session progress. |

**Steps**

1. Gets open plan issues for the tracker run. (`.github/bible/bible_queue.py:645`)
2. If none are open, reads the plan title and body from the analysis ledger; when the body is empty, supplies built-in instructions to run passes 1 and 2, write the Components table, and finish discovery without starting components. It then creates and assigns the plan issue and renders its assigned status. (`.github/bible/bible_queue.py:646-654`)
3. Otherwise selects the first plan issue; if held, renders its human-needed status. (`.github/bible/bible_queue.py:655-657`)
4. Classifies its session; if Copilot reports a start error, marks the issue for human action and renders that status. (`.github/bible/bible_queue.py:658-661`)
5. On `no-start`, requests a retry; then renders the pull-request review state when a PR exists, or the session state otherwise. (`.github/bible/bible_queue.py:662-665`)

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
| `.github/bible/bible_queue.py:646` | if | No open plan issue exists | Reads the planned issue text and creates an assigned plan issue. |
| `.github/bible/bible_queue.py:648` | if | The loaded body is falsey | Uses built-in plan and discovery instructions. |
| `.github/bible/bible_queue.py:656` | if | The first open plan issue is held | Renders that a person must act. |
| `.github/bible/bible_queue.py:659` | if | Session state is `start-error` | Holds the issue and renders human-needed state. |
| `.github/bible/bible_queue.py:662` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:664` | conditional expression | `pr` exists | Renders review/merge PR number; otherwise renders the session state. |

#### `Queue.start_chunk(analysis, name, fresh=False, note="")`

Source: `.github/bible/bible_queue.py:667-679` <!-- code: 7f612dd5f454 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:635`), `Queue.component` (`.github/bible/bible_queue.py:639`, `.github/bible/bible_queue.py:780`) |
| Calls | `self.gh.branch_sha`, `self.gh.create_branch`, `self.gh.reset_branch`, `self.run_issues`, `comp_label`, `issue_text`, `self.gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Creates the component branch when absent, optionally resets it for the first chunk, and opens the next assigned chunk issue. |

**Steps**

1. Sets branch to `bible/<name>` and reads the default branch SHA. (`.github/bible/bible_queue.py:669-670`)
2. Creates the component branch at that SHA when absent; otherwise resets it when `fresh` is true and there are no component issues in any state. (`.github/bible/bible_queue.py:671-674`)
3. Reads the component issue text from the default branch, formats the Component/Base branch/Attempt header, and creates a labeled chunk issue with optional note and model assignment. (`.github/bible/bible_queue.py:675-679`)

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
| `.github/bible/bible_queue.py:671` | if | The component branch has no SHA | Creates the branch at the default branch SHA. |
| `.github/bible/bible_queue.py:673` | elif | Branch exists, `fresh` is true, and no issue with the component label exists in any state | Resets the branch to the default branch SHA. |
| `.github/bible/bible_queue.py:678` | conditional expression | `note` is truthy | Adds the note and a newline before the body; otherwise adds no note prefix. |

#### `Queue.component(analysis, name)`

Source: `.github/bible/bible_queue.py:681-792` <!-- code: c0d9266497e6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:627`) |
| Calls | `gh.branch_prs`, `pr.get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `labels_of`, `gh.close`, `max`, `h.get`, `status_of`, `status.get`, `getattr`, `time.monotonic`, `float`, `self.check`, `self.could_not_check`, `as_int`, `min`, `len`, `self.start_chunk`, `i.get`, `report_facts`, `gh.file`, `bool`, `any`, `gh.create_pr`, `gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Advances a component through its tracker-specific pull requests and sessions, coverage gate, verification and revision rounds, and final review PR or human hold. |

**Steps**

1. Scans PRs from `bible/<name>` into the default branch, skipping another repository's PR, one created before this tracker, or one without its tracker reference. The first matching PR returns `merged`, review-needed, or closed-without-merge status. (`.github/bible/bible_queue.py:682-692`)
2. Combines open chunk and verification issues. For the first issue, returns released or human-needed status, or delegates to `follow`. (`.github/bible/bible_queue.py:693-704`)
3. If there are no open sessions, returns `not started` if the component has no issue in any state. It reads component status; on `COMPONENT_DONE`, first checks whether enough run time remains, then runs the component gate. A gate that cannot run increments the `nocheck:<name>` counter through `could_not_check`; a successful gate clears that counter. (`.github/bible/bible_queue.py:705-725`)
4. If the gate is not successful, determines the recent closed-session window, clamps the estimate to 1–10 (default 2), derives a bounded session cap, and creates a human-hold issue once that count is reached; otherwise starts another chunk. (`.github/bible/bible_queue.py:726-746`)
5. After a successful gate, reads completed verification issues since the last hold release and all completed verifications. It reads report facts only if any verification exists, then creates a final PR only for `PASS`, no major corrections, and a nonempty report fingerprint matching the gate's pages fingerprint. (`.github/bible/bible_queue.py:747-755`)
6. Determines whether a completed chunk followed the newest verification; after the verify-round limit it creates a human hold. If the report concerns current pages, requests revision, and no chunk followed, starts a revision chunk; otherwise it creates and assigns a verification issue. (`.github/bible/bible_queue.py:756-792`)

**Pseudo-code**

```text
for matching same-repository PR from this tracker:
    return merged, review, or needs-person state
if open chunk/verify issue:
    if held: return released or needs-person
    return follow(issue)
if no component issue ever existed: return not started
status = component status
if COMPONENT_DONE:
    if insufficient run time: return waiting
    gate_ok, pages = check(...)
    if gate cannot run: increment no-check counter; return or hold
if gate is not successful:
    calculate session cap; hold at cap, otherwise start another chunk
else:
    get current-round/all verification reports
    if clean PASS fingerprint matches pages: create final PR; return review status
    if verify limit reached without later chunk: create human hold; return
    if current report asks for revision and no later chunk: start revision; return
    create verification issue; return verifying
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:684` | for | Each branch PR | Checks repository, tracker age, and tracker reference. |
| `.github/bible/bible_queue.py:686` | if | PR fails any of those checks | Skips the PR. |
| `.github/bible/bible_queue.py:688` | if | Matching PR has `merged_at` | Returns `merged`. |
| `.github/bible/bible_queue.py:690` | if | Matching PR is open | Returns review status. |
| `.github/bible/bible_queue.py:694` | if | Open chunk or verification issues exist | Selects the first session. |
| `.github/bible/bible_queue.py:697` | if | The issue was released | Returns released status. |
| `.github/bible/bible_queue.py:699` | if | The issue remains held | Returns human-needed status. |
| `.github/bible/bible_queue.py:705` | if | No issue for this component exists in any state | Returns `not started`. |
| `.github/bible/bible_queue.py:709` | if | A component hold issue is open | Checks whether it remains held. |
| `.github/bible/bible_queue.py:710` | if | Open hold has `bible-needs-human` | Returns human-needed status; otherwise closes and reloads holds. |
| `.github/bible/bible_queue.py:717` | if | Component status is `COMPONENT_DONE` | Proceeds to time and gate checks. |
| `.github/bible/bible_queue.py:718` | if | Remaining run time is insufficient for the gate and reserve | Returns a wait status. |
| `.github/bible/bible_queue.py:721` | if | Gate could not run (`gate_ok is None`) | Increments no-check count and returns wait or hold status. |
| `.github/bible/bible_queue.py:726` | if | Gate is not successful | Starts another chunk or creates a human hold at its bounded session cap. |
| `.github/bible/bible_queue.py:734` | if | Closed chunk sessions since the relevant checkpoint reach the cap | Creates a human-hold issue. |
| `.github/bible/bible_queue.py:750` | conditional expression | A completed verification exists | Parses its report; otherwise facts are `None`. |
| `.github/bible/bible_queue.py:751` | if | Report is clean `PASS` and fingerprint matches checked pages | Creates the final PR. |
| `.github/bible/bible_queue.py:770` | if | No later chunk exists and the verify-round bound is reached | Creates a human-hold issue. |
| `.github/bible/bible_queue.py:779` | if | Current-page report needs revision and no chunk followed it | Starts a revision session. |

#### `Queue.follow(analysis, name, issue)`

Source: `.github/bible/bible_queue.py:794-851` <!-- code: 96d8861eb206 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:704`) |
| Calls | `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `str`, `str.startswith`, `f.startswith`, `os.path.basename`, `shown_files`, `status_of`, `as_int`, `status.get`, `issue.get`, `any`, `gh.label`, `gh.merge`, `gh.unlabel`, `gh.close` |
| Purpose | Checks an assigned chunk or verification session and its PR, then retries, holds, waits, or validates and merges it. |

**Steps**

1. Sets `kind` from issue labels and classifies the session for `bible/<name>`. Waiting returns `session starting`; start errors are held; no-start is retried; running returns `<kind> running`. (`.github/bible/bible_queue.py:795-807`)
2. Ensures the PR file list can be read; failure is passed to `fail_or_retry`. Chunk PRs may modify component LLD, matching API LLD, and the component ledger except `verification-*` basenames. Verification PRs may modify only `verification-*` files or `citations.tsv` in that ledger. Disallowed files are rendered with `shown_files` and retried/held. (`.github/bible/bible_queue.py:808-823`)
3. Reads `status.json` at the PR head. For a chunk, `WAITING_ANSWER` adds the waiting label to both issue and PR if needed and returns. Otherwise it compares head and branch packet counts; `STOP` or no progress is retried/held. (`.github/bible/bible_queue.py:824-836`)
4. A revision must change at least one allowed page/API page or `revision-log.md` and end in `COMPONENT_DONE`; otherwise it is retried/held. A verification PR without a report at its head is retried/held. A valid session is merged, its waiting label removed, and its issue closed. (`.github/bible/bible_queue.py:837-851`)

**Pseudo-code**

```text
kind = verify if verification label else chunk
state, pr = session(...)
if waiting/start-error/no-start/running: handle it and return
read PR file list; retry/hold if incomplete
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
| `.github/bible/bible_queue.py:796` | conditional expression | Issue has `bible-verify` | Selects verify; otherwise chunk. |
| `.github/bible/bible_queue.py:798` | if | Session is waiting | Returns `session starting`. |
| `.github/bible/bible_queue.py:800` | if | Session reports start error | Holds it and returns human-needed status. |
| `.github/bible/bible_queue.py:803` | if | Session has no PR after assignment | Calls `fail_or_retry`. |
| `.github/bible/bible_queue.py:805` | conditional expression | Retry succeeds | Returns `session starting`; otherwise needs-person. |
| `.github/bible/bible_queue.py:806` | if | Session is running | Returns `<kind> running`. |
| `.github/bible/bible_queue.py:811` | except | `gh.pr_files` raises `RuntimeError` | Retries or holds; an incomplete file list is not accepted. |
| `.github/bible/bible_queue.py:813` | conditional expression | Retry succeeds | Returns `session starting`; otherwise needs-person. |
| `.github/bible/bible_queue.py:814` | if | Session kind is chunk | Selects chunk allowlist; otherwise selects verification allowlist. |
| `.github/bible/bible_queue.py:821` | if | Any changed file is disallowed | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:823` | conditional expression | Retry succeeds | Returns `session starting`; otherwise needs-person. |
| `.github/bible/bible_queue.py:825` | if | Session kind is chunk | Validates chunk status; otherwise checks the verification report. |
| `.github/bible/bible_queue.py:826` | if | Chunk status is `WAITING_ANSWER` | Handles waiting labels and returns the answer-wait status. |
| `.github/bible/bible_queue.py:827` | if | Issue lacks `bible-waiting-answer` | Adds the label to both issue and PR. |
| `.github/bible/bible_queue.py:834` | if | Status is `STOP` or packet count did not progress | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:836` | conditional expression | Retry succeeds | Returns `session starting`; otherwise needs-person. |
| `.github/bible/bible_queue.py:838` | if | Revision PR changed no allowed page or revision log | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:841` | conditional expression | Retry succeeds | Returns `session starting`; otherwise needs-person. |
| `.github/bible/bible_queue.py:842` | if | Revision status is not `COMPONENT_DONE` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:844` | conditional expression | Retry succeeds | Returns `session starting`; otherwise needs-person. |
| `.github/bible/bible_queue.py:845` | elif | Verification report is absent at the PR head | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:847` | conditional expression | Retry succeeds | Returns `session starting`; otherwise needs-person. |

#### `Queue.check(analysis, name, branch)`

Source: `.github/bible/bible_queue.py:853-878` <!-- code: 4b957b96bfcc -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:720`) |
| Calls | `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `os.path.abspath`, `subprocess.run`, `self.settings.get`, `run.stdout.strip`, `().splitlines`, `printed.stdout.strip`, `shutil.rmtree` |
| Purpose | Runs the component coverage gate against an unpacked branch tarball and obtains its pages fingerprint. |

**Steps**

1. Builds the script directory; if `coverage.py` is missing, logs the omission and returns `(False, None)`. (`.github/bible/bible_queue.py:855-858`)
2. Creates a temporary workspace and unpacks the requested branch tarball. A tarball `RuntimeError` is logged and returns `(None, None)` to distinguish a check that could not run. (`.github/bible/bible_queue.py:859-865`)
3. Runs isolated `coverage.py` with repo, analysis, configured depth, component, and stdout-report arguments; logs the final output line or `no output`. Then runs isolated `status.py --fingerprint --component` and returns coverage success plus stripped fingerprint output or `None`. (`.github/bible/bible_queue.py:866-873`)
4. If either subprocess exceeds `GATE_TIMEOUT`, logs that it was not checked and returns `(None, None)`. The `finally` block removes the workspace, ignoring cleanup errors. (`.github/bible/bible_queue.py:874-878`)

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
on tarball RuntimeError: log and return None, None
on subprocess timeout: log and return None, None
finally: remove work directory
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:856` | if | `coverage.py` is not a file | Logs the missing checker and returns `(False, None)`. |
| `.github/bible/bible_queue.py:863` | except | Tarball extraction raises `RuntimeError` | Logs the error and returns `(None, None)`. |
| `.github/bible/bible_queue.py:874` | except | Either subprocess raises `TimeoutExpired` | Logs the timeout and returns `(None, None)`. |


#### `Queue.could_not_check(key, what, hold_labels, hold_title)`

Source: `.github/bible/bible_queue.py:880-891` <!-- code: d1918209875f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:722`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:941`) |
| Calls | `max`, `as_int`, `self.state.get`, `self.state.pop`, `self.gh.create_issue` |
| Purpose | Counts consecutive checks that could not run, then creates a human-hold issue at `MAX_NOCHECK`. |

**Steps**

1. Sets the keyed state count to `max(as_int(current), 0) + 1`, preventing a negative stored count from suppressing the hold. (`.github/bible/bible_queue.py:883`)
2. Returns `None` while the count is below `MAX_NOCHECK`. At the limit, removes the counter, creates a hold issue with tracker/context labels, and returns a human-needed status containing its issue number. (`.github/bible/bible_queue.py:884-891`)

**Pseudo-code**

```text
self.state[key] = max(as_int(self.state.get(key)), 0) + 1
if count < MAX_NOCHECK: return None
remove count
create hold issue; return "needs a person: see #<number>"
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:884` | if | Consecutive no-check count is below `MAX_NOCHECK` | Returns `None`; otherwise removes the count and creates a hold issue. |

#### `Queue.whole_fingerprint(analysis)`

Source: `.github/bible/bible_queue.py:893-908` <!-- code: c7fe54722506 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:939`) |
| Calls | `os.path.join`, `os.path.isfile`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `os.path.abspath`, `self.log`, `shutil.rmtree` |
| Purpose | Computes the whole-analysis page fingerprint from the current default branch using the analysis toolkit's `status.py`. |

**Steps**

1. Builds the toolkit script directory and returns `None` if `status.py` is absent. (`.github/bible/bible_queue.py:895-897`)
2. Creates a temporary directory, extracts the default-branch tarball, and runs isolated `status.py --fingerprint` with the repository and analysis paths. Returns stripped stdout or `None`. (`.github/bible/bible_queue.py:898-903`)
3. Logs `RuntimeError` or subprocess timeout and returns `None`; always removes the temporary directory, ignoring cleanup errors. (`.github/bible/bible_queue.py:904-908`)

**Pseudo-code**

```text
if status.py is missing: return None
work = temporary directory
try:
    unpack default-branch tarball
    run status.py --fingerprint in isolated Python
    return stripped stdout or None
on RuntimeError or timeout: log; return None
finally: remove work directory
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:896` | if | `status.py` is not a file | Returns `None` without starting a subprocess. |
| `.github/bible/bible_queue.py:904` | except | Tarball or subprocess raises `RuntimeError` or `TimeoutExpired` | Logs the error and returns `None`. |

#### `Queue.assemble_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:910-1023` <!-- code: 935f3bc6544e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:640`) |
| Calls | `self.run_issues`, `settings.get`, `self.whole_hold`, `report_facts`, `gh.file`, `max`, `i.get`, `any`, `p.get`, `gh.is_agent_pr`, `gh.pr_files`, `gh.linked_prs`, `bool`, `time.monotonic`, `getattr`, `float`, `self.whole_fingerprint`, `self.could_not_check`, `self.state.pop`, `labels_of`, `gh.label`, `gh.comment`, `issue.get`, `gh.close`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `issue_text`, `assignment`, `gh.create_issue`, `self.deferred_updates`, `self.delta`, `sorted`, `set`, `shown_files`, `type`, `str` |
| Purpose | Coordinates assembly then whole-analysis verification, retries whole-analysis updates and stale verdicts, and closes the tracker after deferred updates are handled. |

**Steps**

1. Processes assembly and whole-verification phase tuples in order. For verification, first checks for a whole-analysis hold. If a completed verification issue exists, reads its report and linked PRs; a clean `PASS` written by this run is accepted only when its report fingerprint matches a computed current page fingerprint. The fingerprint check is skipped when there is not enough run time; unavailable fingerprints increment a no-fingerprint counter and may create a hold. (`.github/bible/bible_queue.py:912-953`)
2. Marks a stale/non-current `PASS` or correction verdict on the newest completed verification and returns, unless corresponding labels or an open verification issue already make that action redundant. Then invokes `revise_all_step` before opening/following a new verification issue. (`.github/bible/bible_queue.py:954-964`)
3. For an open phase issue, identifies merged agent PRs from this repository into the default branch. For verification, a merged PR whose report is absent, not `PASS`, or has major corrections is labeled `bible-needs-revision`, commented, closed as not planned, and returns a correction status; otherwise closes and advances. (`.github/bible/bible_queue.py:965-984`)
4. Without a qualifying merged PR, returns for a held issue, handles start errors, retries a session with no start, and returns while the agent is running. A finished PR is passed to `continue_if_unfinished`; if complete, returns its review status or session state. (`.github/bible/bible_queue.py:985-999`)
5. If no phase issue is open, reads the assembly issue text or builds whole-verification instructions and assigns a new phase issue. Once both phases are complete, collects deferred updates, calls `delta` for them, comments and closes the tracker, then attempts late updates; late failures are reported in a tracker comment with paths rendered by `shown_files`. (`.github/bible/bible_queue.py:1000-1023`)

**Pseudo-code**

```text
for assemble and verify-all phase:
    if verify-all and whole hold exists: return hold status
    inspect completed verification report and linked PR
    accept clean PASS only if this run wrote it and its fingerprint matches current pages
    mark stale verdicts or corrections and return when a new round is needed
    step = revise_all_step(...); if step: return step
    if a completed assembly issue exists: continue
    if an open issue exists:
        find merged agent PR into default from this repo
        if found:
            if verify-all and report is not clean PASS: label/comment/close as not planned; return
            close issue; continue
        if held: return human-needed
        classify session; handle start-error/no-start/running
        if finished PR: request continuation if its marker is absent
        return review status or session state
    load assemble issue text or build verify-all instructions
    create assigned phase issue
    return phase assigned state
collect and apply deferred updates; comment and close tracker
try late deferred updates; report failure on tracker
return done
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:912` | for | Assembly and verify-all phase tuples | Processes phases in order. |
| `.github/bible/bible_queue.py:916` | if | Current phase is verify-all | Checks whole-analysis hold state. |
| `.github/bible/bible_queue.py:918` | if | A whole-analysis hold is active | Returns the hold status. |
| `.github/bible/bible_queue.py:920` | if | Verify-all has a completed closed issue | Checks whether the recorded verdict is still current. |
| `.github/bible/bible_queue.py:936` | if | Report is a clean PASS written by this run with a fingerprint | Checks run time before computing current pages. |
| `.github/bible/bible_queue.py:937` | if | Not enough run time remains for the gate and reserve | Returns a wait status. |
| `.github/bible/bible_queue.py:940` | if | Current page fingerprint could not be computed | Counts a no-fingerprint check and returns wait or hold. |
| `.github/bible/bible_queue.py:943` | conditional expression | `could_not_check` returns a hold | Prefixes its status; otherwise reports a next-check retry. |
| `.github/bible/bible_queue.py:946` | if | Report fingerprint equals current pages | Treats verification as current and continues to the next phase. |
| `.github/bible/bible_queue.py:948` | if | Clean PASS is stale/untrusted and no replacement verification is open | Labels and comments the stale verdict. |
| `.github/bible/bible_queue.py:954` | if | Verdict is not clean and no revision label/open verification already handles it | Labels and comments correction-needed, then returns. |
| `.github/bible/bible_queue.py:957` | conditional expression | Report facts exist | Includes the verdict; otherwise uses `missing`. |
| `.github/bible/bible_queue.py:958` | return | A whole-analysis correction verdict needs revision | Returns the revision-next status. |
| `.github/bible/bible_queue.py:959` | elif | Assembly already has a completed issue | Skips to verify-all. |
| `.github/bible/bible_queue.py:961` | if | Current phase is verify-all | Runs whole-analysis revision handling. |
| `.github/bible/bible_queue.py:963` | if | Revision handler returns a status | Returns it before processing a verification issue. |
| `.github/bible/bible_queue.py:966` | if | An open issue exists for the phase | Processes its first issue. |
| `.github/bible/bible_queue.py:970` | if | Linked merged agent PRs into the default branch exist | Validates and closes the phase issue. |
| `.github/bible/bible_queue.py:971` | if | Current phase is verify-all | Reads and validates the whole-analysis report. |
| `.github/bible/bible_queue.py:973` | if | Report is missing, not PASS, or has major corrections | Marks the issue for revision and closes it as not planned. |
| `.github/bible/bible_queue.py:978` | conditional expression | Report facts exist | Includes their verdict; otherwise reports `missing`. |
| `.github/bible/bible_queue.py:980` | return | Whole-analysis verification requested corrections | Returns that revision is next. |
| `.github/bible/bible_queue.py:982` | if | Current phase is verify-all after a valid merged PR | Returns verification-merged status. |
| `.github/bible/bible_queue.py:985` | if | Open issue is held | Returns human-needed status. |
| `.github/bible/bible_queue.py:988` | if | Session has a start error | Holds the issue and returns human-needed. |
| `.github/bible/bible_queue.py:991` | if | Session has no start | Attempts failure/retry handling. |
| `.github/bible/bible_queue.py:993` | if | Session PR exists and work is running | Returns running status with PR number. |
| `.github/bible/bible_queue.py:995` | if | Session PR exists and work is finished | Checks whether its completion marker is present or needs continuation. |
| `.github/bible/bible_queue.py:997` | if | Continuation helper returns a status | Returns it. |
| `.github/bible/bible_queue.py:999` | return | Open issue remains in progress or review | Returns review status when PR exists, otherwise session state. |
| `.github/bible/bible_queue.py:1000` | if | Phase tuple includes a text file | Loads issue title and body from the analysis ledger. |
| `.github/bible/bible_queue.py:1012` | if | Deferred changed paths exist | Creates update issues before closing the tracker. |
| `.github/bible/bible_queue.py:1017` | if | Paths changed after the first deferred-update snapshot | Attempts late update issue creation. |
| `.github/bible/bible_queue.py:1020` | except | Late update creation raises an exception | Comments the failure and safe path list on the tracker. |

#### `Queue.deferred_updates(tracker)`

Source: `.github/bible/bible_queue.py:1025-1037` <!-- code: faad993a4a62 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1011`, `.github/bible/bible_queue.py:1016`) |
| Calls | `self.gh.me`, `self.gh.timeline`, `re.findall`, `e.get`, `actor.get`, `json.loads`, `isinstance`, `SAFE_FILE.match`, `sorted`, `set` |
| Purpose | Reads the queue's own deferred-update comments from a tracker and returns the unique safe file paths they recorded. |

**Steps**

1. Gets the authenticated login, scans tracker timeline events, and uses `actor` or `user` as the event author object. It ignores events that are not comments from that login. (`.github/bible/bible_queue.py:1027-1031`)
2. Finds every `bible-deferred-update` JSON marker in each comment, parses its array, and appends only strings matching `SAFE_FILE`. Malformed JSON is ignored. (`.github/bible/bible_queue.py:1032-1036`)
3. Returns sorted unique paths. (`.github/bible/bible_queue.py:1037`)

**Pseudo-code**

```text
me = gh.me()
for timeline event:
    if not a comment by me: continue
    for JSON marker:
        try add each string path matching SAFE_FILE
        on ValueError: continue
return sorted unique paths
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1028` | for | Each tracker timeline event | Reads its author, event type, and body. |
| `.github/bible/bible_queue.py:1030` | if | Event is not a comment by the authenticated login | Skips its body. |
| `.github/bible/bible_queue.py:1032` | for | Each matching deferred-update marker in a comment | Parses and filters its path array. |
| `.github/bible/bible_queue.py:1035` | except | Marker JSON raises `ValueError` | Ignores that marker and continues. |

#### `Queue.whole_hold()`

Source: `.github/bible/bible_queue.py:1039-1045` <!-- code: 6ba23ffaa54f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:917`) |
| Calls | `self.run_issues`, `labels_of`, `self.gh.close` |
| Purpose | Returns an active whole-analysis human hold, closing hold issues whose human-needed label was removed. |

**Steps**

1. Iterates open issues labeled `bible-hold` and `bible-whole`. (`.github/bible/bible_queue.py:1041`)
2. Returns a verify-all human-needed status for the first issue still labeled `bible-needs-human`; otherwise closes each released hold and returns `None` after the loop. (`.github/bible/bible_queue.py:1042-1045`)

**Pseudo-code**

```text
for whole-analysis hold issue:
    if it has bible-needs-human: return verify-all needs-person status
    close released issue
return None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1041` | for | Each open whole-analysis hold issue | Checks whether it remains held. |
| `.github/bible/bible_queue.py:1042` | if | Hold retains `bible-needs-human` | Returns its human-needed status; otherwise closes it. |

#### `Queue.revise_all_step(tracker, analysis)`

Source: `.github/bible/bible_queue.py:1047-1125` <!-- code: 86a6e2d30283 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:962`) |
| Calls | `self.run_issues`, `labels_of`, `gh.close`, `max`, `h.get`, `sorted`, `i.get`, `len`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `gh.linked_prs`, `p.get`, `gh.is_agent_pr`, `gh.pr_files`, `f.startswith`, `os.path.basename`, `any`, `bool`, `gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Coordinates whole-analysis revision sessions after a verification requests corrections, with bounded retries and human holds. |

**Steps**

1. Loads all whole-analysis holds. An open hold with `bible-needs-human` returns a human-needed status; a released open hold is closed and the list is reloaded. It then finds closed correction-verdict and stale-verdict issues since the last release; if there is no correction request and the stale count is below the limit, no revision is needed. (`.github/bible/bible_queue.py:1052-1069`)
2. Finds all revision issues and handles an open one: a merged agent PR is closed; a held issue returns; start-error is held; no-start retries; a running PR returns running; a finished PR may be continued if incomplete, and any file outside the analysis folder or named `verification-*` triggers retry/hold. (`.github/bible/bible_queue.py:1070-1100`)
3. If there is no open revision, compares correction and stale-verdict rounds with completed revisions since the latest request. A completed revision or a newer stale verdict permits the next verification; when the round bound is exhausted it creates a human hold. Otherwise it creates and assigns a revision issue with the whole-analysis skill instructions. (`.github/bible/bible_queue.py:1101-1125`)

**Pseudo-code**

```text
close released hold or return human-needed
find correction and stale verdicts since release
if no correction and stale count below limit: return None
handle open revision issue and its merged/held/session/PR states
if revision completed or stale verdict is newer: return None for next verification
if rounds exhausted: create human hold
otherwise create assigned revision issue
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1054` | if | A whole-analysis hold is open | Checks whether it still needs a person. |
| `.github/bible/bible_queue.py:1055` | if | Open hold has `bible-needs-human` | Returns the human-needed status. |
| `.github/bible/bible_queue.py:1066` | if | No correction verdict exists and stale rounds remain below the limit | Returns `None`; no revision is due. |
| `.github/bible/bible_queue.py:1072` | if | A revision issue is open | Processes that issue. |
| `.github/bible/bible_queue.py:1076` | if | A merged agent PR is linked to the open revision | Closes the issue and returns `None`. |
| `.github/bible/bible_queue.py:1079` | if | Open revision issue is held | Returns a human-needed status. |
| `.github/bible/bible_queue.py:1082` | if | Session reports a start error | Holds the issue and returns. |
| `.github/bible/bible_queue.py:1085` | if | Session has no start | Retries, then reports session starting. |
| `.github/bible/bible_queue.py:1088` | if | Revision PR exists and work is running | Returns its running status. |
| `.github/bible/bible_queue.py:1090` | if | Revision PR exists and work is finished | Checks continuation/completion and file scope. |
| `.github/bible/bible_queue.py:1092` | if | Continuation helper returns a status | Returns that status. |
| `.github/bible/bible_queue.py:1096` | if | Revision PR includes files outside `analysis/` or a `verification-*` basename | Retries or holds it. |
| `.github/bible/bible_queue.py:1099` | conditional expression | Retry succeeds | Returns revise-all session starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:1100` | return | Open revision remains | Returns review status if PR exists, otherwise session state. |
| `.github/bible/bible_queue.py:1101` | conditional expression | A correction-request issue exists | Selects its latest close time; otherwise uses empty string. |
| `.github/bible/bible_queue.py:1105` | if | Round limit is reached and no correction/newer verification can proceed | Falls through to create a human hold. |
| `.github/bible/bible_queue.py:1107` | elif | No correction remains, revisions were completed, or a stale verdict is newer | Returns `None` for the next verification. |
| `.github/bible/bible_queue.py:1109` | if | Verification-round limit is reached | Creates and returns a human-hold issue. |

#### `Queue.continue_if_unfinished(issue, pr, kind, analysis)`

Source: `.github/bible/bible_queue.py:1127-1165` <!-- code: 607ef9d1096b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:996`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1091`) |
| Calls | `gh.pr_files`, `gh.me`, `max`, `e.get`, `gh.timeline`, `get`, `sorted`, `age`, `len`, `labels_of`, `gh.label`, `gh.comment`, `self.settings.get` |
| Purpose | Continues a finished session whose required marker file is absent, up to a bounded number of continuation requests. |

**Steps**

1. Returns `None` when the required status or verification report is already in the PR files. (`.github/bible/bible_queue.py:1135-1136`)
2. Reads release, finish, and prior continuation events, returning a continuing status when Copilot has been asked and has not started yet. (`.github/bible/bible_queue.py:1136-1147`)
3. Holds the issue after `MAX_CONTINUE` requests; otherwise comments a continuation command and returns the next session number. (`.github/bible/bible_queue.py:1149-1165`)

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
| `.github/bible/bible_queue.py:1135` | if | Required marker is present | Returns None. |
| `.github/bible/bible_queue.py:1136` | assignment | Marker is absent | Collects events. |
| `.github/bible/bible_queue.py:1147` | if | A recent continuation is pending | Returns continuing. |
| `.github/bible/bible_queue.py:1149` | if | Continuation count reaches the limit | Labels and holds the issue. |
| `.github/bible/bible_queue.py:1150` | if | Continuation is still allowed | Posts the continuation comment. |

#### `Queue.render(tracker, settings, rows)`

Source: `.github/bible/bible_queue.py:1167-1178` <!-- code: bc302114ec7d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` and `Queue.plan_phase` |
| Calls | `rows.items`, `json.dumps`, `now`, `().isoformat`, `join`, `body.split`, `tracker.get`, `self.gh.set_body`, `self.log` |
| Purpose | Renders tracker status rows and settings, updates the issue body when its non-time content differs, and logs each row. |

**Steps**

1. Builds an introduction and status table, then adds a row for each `(component, state)` pair. (`.github/bible/bible_queue.py:1168-1170`)
2. Adds a hidden `bible-state` JSON comment from `self.state`, an `Updated` timestamp to the minute, and a hidden `bible-settings` JSON comment, then joins the lines. (`.github/bible/bible_queue.py:1171-1174`)
3. Calls `set_body` only when text before `Updated` differs from the current tracker body's corresponding prefix. (`.github/bible/bible_queue.py:1175-1176`)
4. Logs every state row with its key padded to 20 characters. (`.github/bible/bible_queue.py:1177-1178`)

**Pseudo-code**

```text
lines = introduction + table header + rows + hidden bible-state JSON + Updated + hidden bible-settings JSON
body = join lines with newline
if body prefix before "Updated" differs from existing body prefix:
    set tracker body
for each row: log padded key and state
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1175` | if | Text before `Updated` differs | Replaces the tracker body. |
| `.github/bible/bible_queue.py:1177` | for | Each `(key, value)` row | Logs that row. |

#### `Queue.delta(changed, settings_analysis="codebase-analysis", record=True)`

Source: `.github/bible/bible_queue.py:1181-1241` <!-- code: 48ca17e0332c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` and `Queue.assemble_phase` |
| Calls | `gh.default_branch`, `UPDATED.search`, `t.get`, `found.group`, `gh.issues`, `age`, `last_activity`, `SAFE_FILE.match`, `max`, `range`, `gh.comment`, `json.dumps`, `self.log`, `json_file`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `components.component_map`, `sorted`, `p.startswith`, `NAME.match`, `len`, `gh.create_issue`, `components.assign`, `comp_label`, `assignment`, `join` |
| Purpose | Defers changed paths onto an active tracker, or maps them to components and creates bounded, assigned delta issues against an assembled baseline. |

**Steps**

1. Sets the default branch and defines tracker activity from the queue's `Updated` timestamp, falling back to issue creation time. With `record=True`, checks for non-abandoned trackers. If one is open, filters changed paths through `SAFE_FILE`, posts them in chunks of `DEFERRED_PER_COMMENT` with a machine-readable marker, logs, and returns. (`.github/bible/bible_queue.py:1182-1200`)
2. Reads the component catalog and confirms the baseline file exists; otherwise logs and returns. Imports the analysis component helpers, excludes analysis/toolkit paths, maps changed files to sorted touched component names, and keeps only `NAME`-valid names. (`.github/bible/bible_queue.py:1201-1212`)
3. If more than `MAX_DELTA_ISSUES` components changed, creates a human-decision issue only when one is not already open, logs, and returns. Otherwise, for each component, selects assigned files, includes only safe paths in issue text, and counts unusual names. (`.github/bible/bible_queue.py:1213-1227`)
4. Skips a component that already has an open delta issue; otherwise creates an assigned delta issue with the base branch, safe path list, and update/verification instructions, then logs its file count. (`.github/bible/bible_queue.py:1228-1241`)

**Pseudo-code**

```text
default = gh.default_branch()
if record: open_run = trackers whose queue Updated/created time is within ABANDONED_AFTER
if open_run:
    record SAFE_FILE paths in bounded deferred-update comments; log; return
catalog = json_file(components.json)
if catalog or baseline file is missing: log; return
load components toolkit
touched = sorted unique mapped valid component names for paths outside analysis and toolkit
if len(touched) > MAX_DELTA_ISSUES:
    create one human-decision issue if none exists; log; return
for each touched component:
    files = changed paths assigned to it
    shown = safe paths; count unusual paths
    if matching delta issue is open: log; continue
    create assigned delta issue with changed files and update instructions
    log file count
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1186` | conditional expression | An `Updated` timestamp matches | Returns it with seconds and UTC offset; otherwise uses tracker creation time. |
| `.github/bible/bible_queue.py:1187` | if | `record` is true | Finds recent open tracker issues; otherwise uses no active tracker. |
| `.github/bible/bible_queue.py:1188` | if | A non-abandoned tracker is open | Records changed paths on it and returns. |
| `.github/bible/bible_queue.py:1192` | for | Each deferred comment chunk | Posts up to `DEFERRED_PER_COMMENT` safe paths, including an empty chunk when necessary. |
| `.github/bible/bible_queue.py:1196` | conditional expression | First chunk has changed paths with unusual names | Adds a count warning to the comment. |
| `.github/bible/bible_queue.py:1202` | if | Catalog is falsey or baseline file is absent | Logs that no assembled analysis exists and returns. |
| `.github/bible/bible_queue.py:1213` | if | More than `MAX_DELTA_ISSUES` components are affected | Takes the human-decision path. |
| `.github/bible/bible_queue.py:1215` | if | No human-hold delta issue is already open | Creates the decision issue. |
| `.github/bible/bible_queue.py:1223` | for | Each touched component | Finds its changed files and creates or skips an issue. |
| `.github/bible/bible_queue.py:1228` | if | A delta issue for that component is already open | Logs and skips duplicate creation. |
| `.github/bible/bible_queue.py:1238` | conditional expression | Some assigned file names are not safe to quote | Adds the count of unusual file names to the issue's changed-file list. |

## Functions and methods

### `main()`

Source: `.github/bible/bible_queue.py:1244-1290` <!-- code: d5e645d7911f -->

| | |
| --- | --- |
| Kind | module entry point |
| Called by | Module guard (`.github/bible/bible_queue.py:1293-1294`) |
| Calls | `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str`, `args.verify_model.strip`, `args.components.split`, `json.dumps`, `issue.get`, `open`, `l.strip`, `NAME.match` |
| Purpose | Parses `start`, `reconcile`, and `delta` commands and dispatches to the queue workflow. |

**Steps**

1. Builds a required-subcommand parser from the module docstring's first line; defines `start` options including `--analysis` and `--depth`, `reconcile`, and `delta` options, then parses arguments. (`.github/bible/bible_queue.py:1245-1258`)
2. Reads `GITHUB_REPOSITORY` and `GH_TOKEN`; raises `SystemExit` if either is falsey, then constructs `GitHub` and `Queue`. (`.github/bible/bible_queue.py:1260-1264`)
3. For `start`, requires a nonempty verification model different from the normal model, parses component names, and requires at least one selection with each name either `all` or matching `NAME`. (`.github/bible/bible_queue.py:1266-1271`)
4. Ensures labels and exits if a tracker is already open. Builds settings, then calls `settings_of` on the generated marker; if validation rejects the settings, raises `SystemExit` explaining the allowed analysis path, depth, and model characters. Otherwise it creates a tracker issue with hidden settings JSON and prints its issue number and queue-start guidance. (`.github/bible/bible_queue.py:1272-1282`)
5. For `reconcile`, invokes `queue.reconcile`; otherwise reads nonempty stripped lines from the changed-file input and calls `queue.delta`. (`.github/bible/bible_queue.py:1283-1288`)
6. Converts `RuntimeError` from command handling to `SystemExit` with the error text. (`.github/bible/bible_queue.py:1289-1290`)

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
| `.github/bible/bible_queue.py:1261` | if | Repository or token is missing | Exits with an environment requirement. |
| `.github/bible/bible_queue.py:1262` | raise | Required environment is missing | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1266` | if | Command is `start` | Validates and starts a run. |
| `.github/bible/bible_queue.py:1267` | if | Verification model is empty or equals normal model | Exits with the model requirement. |
| `.github/bible/bible_queue.py:1268` | raise | Model validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1270` | if | No component names are supplied, or a name other than `all` fails `NAME` | Exits with component-selection guidance. |
| `.github/bible/bible_queue.py:1271` | raise | Selection validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1273` | if | Tracker already exists | Exits without starting another run. |
| `.github/bible/bible_queue.py:1274` | raise | Open tracker exists | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1277` | if | Generated settings fail `settings_of` validation | Exits with the settings requirement. |
| `.github/bible/bible_queue.py:1278-1279` | raise | Generated settings are unsafe or unsupported | Raises `SystemExit` with allowed path, depth, and model rules. |
| `.github/bible/bible_queue.py:1283` | elif | Command is `reconcile` | Calls `queue.reconcile`. |
| `.github/bible/bible_queue.py:1285` | else | Command is `delta` | Reads changed paths and calls `queue.delta`. |
| `.github/bible/bible_queue.py:1289` | except | Command handling raises `RuntimeError` | Converts it to `SystemExit`. |
| `.github/bible/bible_queue.py:1290` | raise | A `RuntimeError` was caught | Raises `SystemExit` with the error text. |
| `.github/bible/bible_queue.py:1293` | if | Module is run as a script | Calls `main`. |
| `.github/bible/bible_queue.py:1294` | call | Script guard is active | Dispatches the CLI entry point. |

### `now()`

Source: `.github/bible/bible_queue.py:352-354` <!-- code: 9fb56903ebfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `age` (`.github/bible/bible_queue.py:358`), `Queue.render` (`.github/bible/bible_queue.py:992`) |
| Calls | `os.environ.get`, `datetime.datetime.fromisoformat`, `datetime.datetime.now`, `replace` |
| Purpose | Returns the configured test time or the current UTC time. |

**Steps**

1. Reads `BIBLE_NOW`. (`.github/bible/bible_queue.py:353`)
2. If set, replaces `Z` with `+00:00` and parses the ISO timestamp; otherwise returns the current timezone-aware UTC datetime. (`.github/bible/bible_queue.py:354`)

**Pseudo-code**

```text
stamp = BIBLE_NOW
if stamp: parse ISO stamp after replacing Z with +00:00
else: return current UTC time
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:354` | conditional expression | `stamp` is truthy | Parses the configured time; otherwise obtains current UTC time. |

### `age(stamp)`

Source: `.github/bible/bible_queue.py:357-358` <!-- code: f2f8bb65e56f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:581`), `main` (`.github/bible/bible_queue.py:1277`) |
| Calls | `now`, `datetime.datetime.fromisoformat`, `replace`, `total_seconds` |
| Purpose | Returns elapsed seconds between `stamp` and `now()`. |

**Steps**

1. Replaces `Z` in `stamp` with `+00:00`, parses it as an ISO datetime, subtracts it from `now()`, and returns `total_seconds()`. (`.github/bible/bible_queue.py:358`)

**Pseudo-code**

```text
return (now() - parse ISO stamp after replacing Z with +00:00).total_seconds()
```

### `settings_of(tracker)`

Source: `.github/bible/bible_queue.py:378-398` <!-- code: 828d76009663 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:581`), `main` (`.github/bible/bible_queue.py:1277`) |
| Calls | `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group`, `isinstance`, `str`, `data.get`, `SAFE_PATH.match`, `analysis.split`, `SAFE_MODEL.match` |
| Purpose | Parses and validates the JSON settings marker from a tracker, returning `None` when absent, malformed, or unsafe. |

**Steps**

1. Searches the tracker body, defaulting a missing or falsey body to an empty string, and parses the marker's first capture group when present. (`.github/bible/bible_queue.py:384-385`)
2. Returns `None` for invalid JSON or a non-dictionary parsed value. (`.github/bible/bible_queue.py:386-387`)
3. Reads `analysis`, defaulting to `codebase-analysis`, and rejects paths that fail `SAFE_PATH` or contain `..` path segments. (`.github/bible/bible_queue.py:388-390`)
4. Rejects depths outside `DEPTH_VALUES`, and rejects nonempty `model` or `verify_model` values that fail `SAFE_MODEL`. (`.github/bible/bible_queue.py:391-396`)
5. Returns the validated settings dictionary. (`.github/bible/bible_queue.py:398`)

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
| `.github/bible/bible_queue.py:384` | conditional expression | A settings marker matched | Parses its first group; otherwise uses `None`. |
| `.github/bible/bible_queue.py:385` | except | JSON parsing raises `ValueError` | Returns `None`. |
| `.github/bible/bible_queue.py:387` | if | Parsed value is not a dictionary | Returns `None`. |
| `.github/bible/bible_queue.py:390` | if | Analysis path is unsafe | Returns `None`. |
| `.github/bible/bible_queue.py:392` | if | Depth is not an allowed value | Returns `None`. |
| `.github/bible/bible_queue.py:394` | for | For `model` and `verify_model` | Validates each configured model value. |
| `.github/bible/bible_queue.py:396` | if | A nonempty model fails `SAFE_MODEL` | Returns `None`. |

### `labels_of(item)`

Source: `.github/bible/bible_queue.py:401-402` <!-- code: 7a809f2b23af -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `item.get`, `isinstance` |
| Purpose | Returns a set of label names from strings or label objects. |

**Steps**

1. Reads `labels`, defaulting to an empty list; for each element, uses its `name` when it is a dictionary and otherwise keeps the element itself. (`.github/bible/bible_queue.py:402`)

**Pseudo-code**

```text
return {label["name"] if label is a dict else label
        for label in item.labels or []}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:402` | conditional expression | A label item is a dict | Uses `item["name"]`; otherwise preserves the item value. |

### `comp_label(name)`

Source: `.github/bible/bible_queue.py:405-406` <!-- code: 5ead08c5004d -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Prefixes a component name with `bible/`. |

**Steps**

1. Returns the string `bible/` followed by `name`. (`.github/bible/bible_queue.py:406`)

**Pseudo-code**

```text
return "bible/" + name
```

### `issue_text(gh, path, ref, fallback_title)`

Source: `.github/bible/bible_queue.py:409-415` <!-- code: 0533b3261be5 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `gh.file`, `splitlines`, `startswith`, `strip`, `join`, `len` |
| Purpose | Reads a title/body pair from a ledger issue file, with a fallback title when no header exists. |

**Steps**

1. Reads the file through `gh.file`, converting a falsey result to `""`, then splits it into lines. (`.github/bible/bible_queue.py:411-412`)
2. If the first line starts with `Title:`, returns its stripped suffix as the title and the stripped remaining lines joined by newlines as the body. (`.github/bible/bible_queue.py:413-414`)
3. Otherwise returns `fallback_title` and the stripped full text. (`.github/bible/bible_queue.py:415`)

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
| `.github/bible/bible_queue.py:413` | if | `lines` is nonempty and the first line starts with `Title:` | Returns header title and remaining body; otherwise returns fallback title and full text. |

### `assignment(gh, base, model)`

Source: `.github/bible/bible_queue.py:418-422` <!-- code: da5ca422ae7f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Builds the target repository and base-branch assignment, optionally including a model. |

**Steps**

1. Initializes the result with `target_repo: gh.repo` and `base_branch: base`. (`.github/bible/bible_queue.py:419`)
2. Adds `model` only when truthy, then returns the result. (`.github/bible/bible_queue.py:420-422`)

**Pseudo-code**

```text
out = {target_repo: gh.repo, base_branch: base}
if model: out.model = model
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:420` | if | `model` is truthy | Adds `model` to the assignment. |

### `json_file(gh, path, ref)`

Source: `.github/bible/bible_queue.py:425-430` <!-- code: 37acfbecddfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `status_of` (`.github/bible/bible_queue.py:467`), queue functions in later source packets. |
| Calls | `gh.file`, `json.loads` |
| Purpose | Reads a file and parses JSON, returning `None` for missing or invalid content. |

**Steps**

1. Reads the file using `gh.file`. (`.github/bible/bible_queue.py:426`)
2. Returns parsed JSON for truthy text, or `None` when the text is falsey. (`.github/bible/bible_queue.py:427-428`)
3. Returns `None` if parsing raises `ValueError`. (`.github/bible/bible_queue.py:429-430`)

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
| `.github/bible/bible_queue.py:428` | conditional expression | `text` is truthy | Parses JSON; otherwise returns `None`. |
| `.github/bible/bible_queue.py:429` | except | JSON parsing raises `ValueError` | Returns `None`. |

### `section(text, title)`

Source: `.github/bible/bible_queue.py:433-439` <!-- code: 55167fd6e3c2 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `report_facts` (`.github/bible/bible_queue.py:452`), queue functions in later source packets. |
| Calls | `re.search`, `re.escape`, `match.end`, `nxt.start` |
| Purpose | Returns a Markdown level-two section's text, or an empty string if its heading is absent. |

**Steps**

1. Searches for a line matching exactly a level-two heading with the escaped `title`. (`.github/bible/bible_queue.py:434`)
2. Returns `""` if no heading matches. (`.github/bible/bible_queue.py:435-436`)
3. Slices text after the matched heading through the next level-two heading, or through end of text when there is no next heading. (`.github/bible/bible_queue.py:437-439`)

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
| `.github/bible/bible_queue.py:435` | if | No heading matched | Returns an empty string. |
| `.github/bible/bible_queue.py:439` | conditional expression | A next level-two heading matched | Returns the section before it; otherwise returns the remaining text. |

### `report_facts(text)`

Source: `.github/bible/bible_queue.py:442-455` <!-- code: a367c151c5b0 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `re.sub`, `re.findall`, `len`, `sum`, `splitlines`, `startswith`, `re.search`, `section`, `lstrip`, `upper`, `printed.group` |
| Purpose | Extracts a verification verdict, major-correction count, and optional analysis fingerprint. |

**Steps**

1. Returns `None` for falsey `text`. (`.github/bible/bible_queue.py:445-446`)
2. Removes HTML comments and fenced code blocks, then finds visible `Verdict` values and rows. (`.github/bible/bible_queue.py:447-449`)
3. Returns `("UNREADABLE", 0, None)` unless exactly one accepted verdict and exactly one verdict row were found. (`.github/bible/bible_queue.py:450-451`)
4. Counts lines in the `Corrections` section that begin with `|` and contain a `major` cell. (`.github/bible/bible_queue.py:452-453`)
5. Searches for a 16-character lowercase hexadecimal fingerprint and returns the uppercased verdict, count, and captured fingerprint or `None`. (`.github/bible/bible_queue.py:454-455`)

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
| `.github/bible/bible_queue.py:445` | if | `text` is falsey | Returns `None`. |
| `.github/bible/bible_queue.py:450` | if | Verdict or verdict-row count is not exactly one | Returns `("UNREADABLE", 0, None)`. |
| `.github/bible/bible_queue.py:455` | conditional expression | Fingerprint regex matched | Returns its group 1; otherwise returns `None` in that tuple position. |

### `shown_files(paths, limit=10)`

Source: `.github/bible/bible_queue.py:370-375` <!-- code: 42118ce2fbc4 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.follow`, `Queue.assemble_phase`, `Queue.revise_all_step` |
| Calls | `SAFE_FILE.match`, `len`, `join` |
| Purpose | Formats safe paths as quoted names and reports counts for omitted or unusual names. |

**Steps**

1. Separates paths matching `SAFE_FILE` from all other paths and counts the unusual names. (`.github/bible/bible_queue.py:372-373`)
2. Quotes at most the first `limit` safe paths, appends the number of additional safe paths when there are more than `limit`, and appends the unusual-name count when nonzero. (`.github/bible/bible_queue.py:374-375`)

**Pseudo-code**

```text
plain = paths matching SAFE_FILE
other = len(paths) - len(plain)
return quoted plain[:limit] + optional count of remaining plain + optional count of other
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:374` | conditional expression | Safe path count is greater than `limit` | Adds the number of additional safe paths. |
| `.github/bible/bible_queue.py:375` | conditional expression | Unusual-name count is nonzero | Adds its count to the rendered text. |

### `as_int(value)`

Source: `.github/bible/bible_queue.py:458-462` <!-- code: bc184bba1eba -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `int` |
| Purpose | Converts a value to an integer, returning zero when conversion raises `TypeError`, `ValueError`, or `OverflowError`. |

**Steps**

1. Returns `int(value)` when conversion succeeds. (`.github/bible/bible_queue.py:459-460`)
2. Returns `0` when conversion raises any of the three caught conversion exceptions, including `OverflowError`. (`.github/bible/bible_queue.py:461-462`)

**Pseudo-code**

```text
try: return int(value)
on TypeError, ValueError, or OverflowError: return 0
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:461` | except | `int(value)` raises `TypeError`, `ValueError`, or `OverflowError` | Returns zero. |

### `status_of(gh, path, ref)`

Source: `.github/bible/bible_queue.py:465-468` <!-- code: ad9adb38e0f7 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `json_file`, `isinstance` |
| Purpose | Returns parsed component status only when the loaded JSON is a dictionary. |

**Steps**

1. Loads `path` at `ref` with `json_file`. (`.github/bible/bible_queue.py:467`)
2. Returns the loaded data if it is a dictionary; otherwise returns `{}`. (`.github/bible/bible_queue.py:468`)

**Pseudo-code**

```text
data = json_file(gh, path, ref)
return data if data is a dict, otherwise {}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:468` | conditional expression | `data` is a dictionary | Returns `data`; otherwise returns `{}`. |

## Module-level code

The module imports Python standard-library utilities and initializes queue labels, environment-derived agent settings, regexes, and timing/verification constants. (`.github/bible/bible_queue.py:42-98`)

It declares the `GitHub` API client (`.github/bible/bible_queue.py:104-347`), helper functions (`.github/bible/bible_queue.py:352-468`), and `Queue` coordinator (`.github/bible/bible_queue.py:473-1241`). The CLI `main` parses arguments, and the module guard calls it when executed as a script. (`.github/bible/bible_queue.py:1244-1294`)

## Surprises

`tarball` limits download size and archive member count/unpacked bytes, skips non-file/non-directory members, and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:267-303`)

The `Queue.session` docstring lists four result states, but the code also returns `start-error` when `GitHub.start_error` is truthy. (`.github/bible/bible_queue.py:490-495`)

`Queue.component` builds `closed_revise` after a human hold but does not use it later in the method; it separately builds and uses `all_revise`. (`.github/bible/bible_queue.py:637-641`, `.github/bible/bible_queue.py:755-761`)

<!-- cites .github/bible/bible_queue.py@9084f4915d286441c5b3a9a29a8df059bf76dacc -->
