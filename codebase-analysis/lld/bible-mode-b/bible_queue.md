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
| Lines | 1310 |
| Role | Runs the Mode B analysis queue and its GitHub API client. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, subprocess, and filesystem modules used by the API client, queue, and CLI. (`.github/bible/bible_queue.py:42-56`) |
| Module-level state | Constants and labels are initialized at import; environment-backed values include `BIBLE_AGENT_LOGINS` and `BIBLE_AGENT_APP`; `WORK_EVENTS` names the three Copilot timeline events the queue reads (`copilot_work_started`, `copilot_work_finished`, `copilot_work_finished_failure`). (`.github/bible/bible_queue.py:60-103`, `.github/bible/bible_queue.py:61`, `.github/bible/bible_queue.py:65`, `.github/bible/bible_queue.py:69`) |

## Summary

`main` exposes the `start`, `reconcile`, and `delta` CLI commands. It constructs `Queue` and `GitHub`; `Queue` coordinates tracker/session state and delegates repository operations to `GitHub`, whose methods build REST requests and a GraphQL ready-for-review mutation. `Queue.delta` also imports component-membership helpers from the analysis toolkit. (`.github/bible/bible_queue.py:1260-1306`, `.github/bible/bible_queue.py:477-1257`, `.github/bible/bible_queue.py:108-351`, `.github/bible/bible_queue.py:1221-1222`)

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| `GitHub` | class | 108-351 | [class](#github) |
| `GitHub.__init__` | method | 109-112 | [card](#github__init__repo-token-api-none) |
| `GitHub.request` | method | 114-123 | [card](#githubrequestmethod-url-body-none-timeout-60) |
| `GitHub.call` | method | 125-137 | [card](#githubcallmethod-path-body-none-ok404-false) |
| `GitHub.paged` | method | 139-147 | [card](#githubpagedpath) |
| `GitHub.issues` | method | 149-151 | [card](#githubissueslabels-state-open) |
| `GitHub.ensure_label` | method | 153-158 | [card](#githubensure_labelname-whycodebase-analysis) |
| `GitHub.ensure_labels` | method | 160-162 | [card](#githubensure_labels) |
| `GitHub.create_issue` | method | 164-171 | [card](#githubcreate_issuetitle-body-labels-assign-none) |
| `GitHub.me` | method | 173-177 | [card](#githubme) |
| `GitHub.default_branch` | method | 179-180 | [card](#githubdefault_branch) |
| `GitHub.branch_sha` | method | 182-184 | [card](#githubbranch_shabranch) |
| `GitHub.create_branch` | method | 186-187 | [card](#githubcreate_branchbranch-sha) |
| `GitHub.reset_branch` | method | 189-190 | [card](#githubreset_branchbranch-sha) |
| `GitHub.file` | method | 192-196 | [card](#githubfilepath-ref) |
| `GitHub.prs` | method | 198-200 | [card](#githubprsbase-none-state-open) |
| `GitHub.timeline` | method | 202-203 | [card](#githubtimelinenumber) |
| `GitHub.linked_prs` | method | 205-214 | [card](#githublinked_prsnumber) |
| `GitHub.branch_prs` | method | 216-219 | [card](#githubbranch_prsbranch-base) |
| `GitHub.agent_events` | method | 221-225 | [card](#githubagent_eventsnumber) |
| `GitHub.is_agent_pr` | method | 227-232 | [card](#githubis_agent_prpr) |
| `GitHub.start_error` | method | 234-243 | [card](#githubstart_errorissue) |
| `GitHub.assigned_at` | method | 245-248 | [card](#githubassigned_atissue) |
| `GitHub.pr_files` | method | 250-263 | [card](#githubpr_filesnumber) |
| `GitHub.commit_time` | method | 265-266 | [card](#githubcommit_timesha) |
| `GitHub.tarball` | method | 268-307 | [card](#githubtarballref-dest) |
| `GitHub.label` | method | 309-311 | [card](#githublabelnumber-name) |
| `GitHub.unlabel` | method | 313-314 | [card](#githubunlabelnumber-name) |
| `GitHub.comment` | method | 316-317 | [card](#githubcommentnumber-text) |
| `GitHub.close` | method | 319-320 | [card](#githubclosenumber-reason-completed) |
| `GitHub.set_body` | method | 322-323 | [card](#githubset_bodynumber-body) |
| `GitHub.unassign` | method | 325-326 | [card](#githubunassignnumber) |
| `GitHub.assign` | method | 328-329 | [card](#githubassignnumber-assign) |
| `GitHub.ready` | method | 331-339 | [card](#githubreadypr) |
| `GitHub.merge` | method | 341-345 | [card](#githubmergepr-title) |
| `GitHub.close_pr` | method | 347-348 | [card](#githubclose_prnumber) |
| `GitHub.create_pr` | method | 350-351 | [card](#githubcreate_prhead-base-title-body) |
| `now` | function | 356-358 | [card](#now) |
| `age` | function | 361-362 | [card](#age) |
| `shown_files` | function | 374-379 | [card](#shown_filespaths-limit10) |
| `settings_of` | function | 382-402 | [card](#settings_of) |
| `labels_of` | function | 405-406 | [card](#labels_of) |
| `comp_label` | function | 409-410 | [card](#comp_label) |
| `issue_text` | function | 413-419 | [card](#issue_textgh-path-ref-fallback_title) |
| `assignment` | function | 422-426 | [card](#assignmentgh-base-model) |
| `json_file` | function | 429-434 | [card](#json_filegh-path-ref) |
| `section` | function | 437-443 | [card](#sectiontext-title) |
| `report_facts` | function | 446-459 | [card](#report_factstext) |
| `as_int` | function | 462-466 | [card](#as_intvalue) |
| `status_of` | function | 469-472 | [card](#status_ofgh-path-ref) |
| `Queue` | class | 477-1257 | [class](#queue) |
| `Queue.__init__` | method | 478-480 | [card](#queue__init__gh-log-print) |
| `Queue.run_issues` | method | 482-483 | [card](#queue_run_issueslabels-state-open) |
| `Queue.agent_pr` | method | 485-491 | [card](#queue_agent_prissue-base) |
| `Queue.session` | method | 494-510 | [card](#queue_sessionissue-base-analysis-comp-none) |
| `Queue.held` | method | 512-545 | [card](#queue_heldissue) |
| `Queue.model_for` | method | 547-549 | [card](#queue_model_forissue) |
| `Queue.hold_start_error` | method | 551-557 | [card](#queue_hold_start_errorissue) |
| `Queue.fail_or_retry` | method | 559-578 | [card](#queue_fail_or_retryissue-pr-why) |
| `Queue.reconcile` | method | 581-592 | [card](#queue_reconcile) |
| `Queue.run` | method | 594-645 | [card](#queue_runtracker-settings) |
| `Queue.plan_phase` | method | 647-669 | [card](#queue_plan_phasetracker-settings-analysis) |
| `Queue.start_chunk` | method | 671-683 | [card](#queue_start_chunkanalysis-name-fresh-false-note) |
| `Queue.component` | method | 685-796 | [card](#queue_componentanalysis-name) |
| `Queue.follow` | method | 798-855 | [card](#queue_followanalysis-name-issue) |
| `Queue.check` | method | 857-882 | [card](#queue_checkanalysis-name-branch) |
| `Queue.could_not_check` | method | 884-895 | [card](#queue_could_not_checkkey-what-hold_labels-hold_title) |
| `Queue.whole_fingerprint` | method | 897-912 | [card](#queue_whole_fingerprintanalysis) |
| `Queue.assemble_phase` | method | 914-1027 | [card](#queue_assemble_phasetracker-settings-analysis) |
| `Queue.deferred_updates` | method | 1029-1041 | [card](#queue_deferred_updatestracker) |
| `Queue.whole_hold` | method | 1043-1049 | [card](#queue_whole_hold) |
| `Queue.revise_all_step` | method | 1051-1129 | [card](#queue_revise_all_steptracker-analysis) |
| `Queue.continue_if_unfinished` | method | 1131-1181 | [card](#queue_continue_if_unfinishedissue-pr-kind-analysis) |
| `Queue.render` | method | 1183-1194 | [card](#queue_rendertracker-settings-rows) |
| `Queue.delta` | method | 1197-1257 | [card](#queue_deltachanged-settings_analysiscodebase-analysis-recordtrue) |
| `main` | function | 1260-1306 | [card](#main) |

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
  shownfiles["shown_files"]
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
  follow -->|"status_of"| statusof
  follow -->|"as_int"| asint
  follow -->|"shown_files"| shownfiles
  check -->|"tarball"| tarball
  check -->|"subprocess.run"| subprocessrun
  assemblephase -->|"run_issues"| runissues
  assemblephase -->|"whole_hold"| wholehold
  assemblephase -->|"whole_fingerprint"| wholefingerprint
  assemblephase -->|"could_not_check"| couldnotcheck
  assemblephase -->|"deferred_updates"| deferredupdates
  assemblephase -->|"shown_files"| shownfiles
  assemblephase -->|"delta"| delta
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
  couldnotcheck -->|"as_int"| asint
  couldnotcheck -->|"create_issue"| createissue
  wholefingerprint -->|"tarball"| tarball
  wholefingerprint -->|"subprocess.run"| subprocessrun
  wholehold -->|"run_issues"| runissues
  wholehold -->|"labels_of"| labelsof
  wholehold -->|"close"| close
  reviseall -->|"assignment"| assignment
  reviseall -->|"close"| close
  reviseall -->|"continue_if_unfinished"| continueunfinished
  reviseall -->|"create_issue"| createissue
  reviseall -->|"fail_or_retry"| failorretry
  reviseall -->|"held"| held
  reviseall -->|"hold_start_error"| holdstarterror
  reviseall -->|"shown_files"| shownfiles
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

Source: `.github/bible/bible_queue.py:108-351`

`GitHub` is a client for repository-scoped GitHub REST operations and the GraphQL ready-for-review mutation. Its instance fields are `repo`, `token`, normalized `api`, and `known_labels`; the last begins as `None` and is populated by `ensure_label`. (`.github/bible/bible_queue.py:109-112`, `.github/bible/bible_queue.py:153-158`)

No type annotations or factory are declared for the class; callers provide its constructor values. (inferred: `.github/bible/bible_queue.py:108-112`)

#### `GitHub.__init__(repo, token, api=None)`

Source: `.github/bible/bible_queue.py:109-112` <!-- code: b511658beb68 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1279`) |
| Calls | `os.environ.get`, `rstrip` |
| Purpose | Stores API credentials and a slash-trimmed API base URL, then initializes the label cache. |

**Steps**

1. Assigns `repo` and `token` to the instance. (`.github/bible/bible_queue.py:110`)
2. Selects `api`, then `GITHUB_API_URL`, then `https://api.github.com`, and removes trailing `/` characters. (`.github/bible/bible_queue.py:111`)
3. Initializes `known_labels` to `None`. (`.github/bible/bible_queue.py:112`)

**Pseudo-code**

```text
self.repo, self.token = repo, token
self.api = (api or GITHUB_API_URL or "https://api.github.com").rstrip("/")
self.known_labels = None
```

#### `GitHub.request(method, url, body=None, timeout=60)`

Source: `.github/bible/bible_queue.py:114-123` <!-- code: 1f8902892005 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.call` (`.github/bible/bible_queue.py:128`), `GitHub.tarball` (`.github/bible/bible_queue.py:274`), `GitHub.ready` (`.github/bible/bible_queue.py:336`) |
| Calls | `json.dumps`, `encode`, `urllib.request.Request`, `req.add_header`, `urllib.request.urlopen` |
| Purpose | Builds and opens an HTTP request with GitHub headers and an optional JSON body. |

**Steps**

1. Serializes a non-`None` body as encoded JSON; otherwise leaves request data unset. (`.github/bible/bible_queue.py:115`)
2. Creates a request using the supplied URL, method, and body bytes, and adds GitHub's JSON accept and API-version headers. (`.github/bible/bible_queue.py:116-118`)
3. Adds a bearer authorization header only when `token` is truthy, and adds JSON content type only when a body was serialized. (`.github/bible/bible_queue.py:119-122`)
4. Returns `urlopen`'s response using the supplied timeout. (`.github/bible/bible_queue.py:123`)

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
| `.github/bible/bible_queue.py:115` | conditional expression | `body is not None` | JSON is encoded; otherwise `data` is `None`. |
| `.github/bible/bible_queue.py:119` | if | `self.token` is truthy | Adds the bearer authorization header. |
| `.github/bible/bible_queue.py:121` | if | `data is not None` | Adds the JSON content-type header. |

#### `GitHub.call(method, path, body=None, ok404=False)`

Source: `.github/bible/bible_queue.py:125-137` <!-- code: 753c5f1a3922 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.paged` (`.github/bible/bible_queue.py:143`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:157`), `GitHub.create_issue` (`.github/bible/bible_queue.py:171`), `GitHub.default_branch` (`.github/bible/bible_queue.py:180`), `GitHub.branch_sha` (`.github/bible/bible_queue.py:183`), `GitHub.create_branch` (`.github/bible/bible_queue.py:187`), `GitHub.reset_branch` (`.github/bible/bible_queue.py:190`), `GitHub.file` (`.github/bible/bible_queue.py:193`), `GitHub.linked_prs` (`.github/bible/bible_queue.py:213`), `GitHub.commit_time` (`.github/bible/bible_queue.py:266`), `GitHub.label` (`.github/bible/bible_queue.py:311`), `GitHub.unlabel` (`.github/bible/bible_queue.py:314`), `GitHub.comment` (`.github/bible/bible_queue.py:317`), `GitHub.close` (`.github/bible/bible_queue.py:320`), `GitHub.set_body` (`.github/bible/bible_queue.py:323`), `GitHub.unassign` (`.github/bible/bible_queue.py:326`), `GitHub.assign` (`.github/bible/bible_queue.py:329`), `GitHub.merge` (`.github/bible/bible_queue.py:345`), `GitHub.close_pr` (`.github/bible/bible_queue.py:348`), `GitHub.create_pr` (`.github/bible/bible_queue.py:351`) |
| Calls | `path.startswith`, `GitHub.request`, response `read`, `json.loads`, `RuntimeError` |
| Purpose | Sends a REST request and converts response data and common request failures to Python values or a `RuntimeError`. |

**Steps**

1. Uses an absolute `path` beginning with `http` as-is; otherwise joins the API base, `/repos/`, repository, and path. (`.github/bible/bible_queue.py:126`)
2. Opens the request and reads its response bytes. (`.github/bible/bible_queue.py:127-129`)
3. On HTTP 404 with `ok404`, returns `None`; otherwise reads at most 300 decoded characters and raises a method/path/status/detail `RuntimeError`. (`.github/bible/bible_queue.py:130-134`)
4. Converts `URLError`, `TimeoutError`, and `OSError` to a `RuntimeError` containing the method, query-stripped path, and error. (`.github/bible/bible_queue.py:135-136`)
5. Decodes a nonempty payload as JSON; returns `{}` for an empty payload. (`.github/bible/bible_queue.py:137`)

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
| `.github/bible/bible_queue.py:126` | conditional expression | `path.startswith("http")` | Uses `path`; otherwise constructs a repository API URL. |
| `.github/bible/bible_queue.py:130` | except | Request raises `urllib.error.HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:131` | if | Status is 404 and `ok404` is true | Returns `None`. |
| `.github/bible/bible_queue.py:134` | raise | Other HTTP errors | Raises `RuntimeError` with method, path, status, and detail. |
| `.github/bible/bible_queue.py:135` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Enters network error handling. |
| `.github/bible/bible_queue.py:136` | raise | A listed network error occurred | Raises `RuntimeError` with method, path, and error. |
| `.github/bible/bible_queue.py:137` | conditional expression | Payload is nonempty | Decodes JSON; otherwise returns `{}`. |

#### `GitHub.paged(path)`

Source: `.github/bible/bible_queue.py:139-147` <!-- code: 1bb6c1899527 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.issues` (`.github/bible/bible_queue.py:151`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:155`), `GitHub.prs` (`.github/bible/bible_queue.py:200`), `GitHub.timeline` (`.github/bible/bible_queue.py:203`), `GitHub.branch_prs` (`.github/bible/bible_queue.py:219`), `GitHub.pr_files` (`.github/bible/bible_queue.py:253`) |
| Calls | `GitHub.call`, `len` |
| Purpose | Fetches successive pages of up to 100 results and returns their concatenation. |

**Steps**

1. Starts with an empty result and page number 1. (`.github/bible/bible_queue.py:140`)
2. Chooses `&` if `path` already contains `?`, otherwise `?`, then requests `per_page=100` and the current page with GET. (`.github/bible/bible_queue.py:141-143`)
3. Appends each batch; returns the accumulated list when a batch has fewer than 100 entries, otherwise increments the page and repeats. (`.github/bible/bible_queue.py:144-147`)

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
| `.github/bible/bible_queue.py:141` | while | Always | Repeats page requests until a short batch is returned. |
| `.github/bible/bible_queue.py:142` | conditional expression | `path` contains `?` | Chooses `&`; otherwise chooses `?`. |
| `.github/bible/bible_queue.py:145` | if | Batch length is less than 100 | Returns all accumulated entries; otherwise proceeds to the next page. |

#### `GitHub.issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:149-151` <!-- code: b3f969457f25 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run_issues` (`.github/bible/bible_queue.py:483`), `Queue.reconcile` (`.github/bible/bible_queue.py:584`), `Queue.delta` (`.github/bible/bible_queue.py:1203`, `.github/bible/bible_queue.py:1231`, `.github/bible/bible_queue.py:1244`), `main` (`.github/bible/bible_queue.py:1289`) |
| Calls | `urllib.parse.quote`, `join`, `GitHub.paged` |
| Purpose | Lists issues for encoded labels and a state, excluding pull requests. |

**Steps**

1. Joins labels with commas and URL-quotes the result. (`.github/bible/bible_queue.py:150`)
2. Pages `/issues` with the requested state and labels query, then keeps only objects without a `pull_request` key. (`.github/bible/bible_queue.py:151`)

**Pseudo-code**

```text
q = URL-quote(comma-joined labels)
return paged issues for state and q, excluding pull request objects
```

#### `GitHub.ensure_label(name, why="Codebase analysis run")`

Source: `.github/bible/bible_queue.py:153-158` <!-- code: c80387a5616e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.ensure_labels` (`.github/bible/bible_queue.py:162`), `GitHub.create_issue` (`.github/bible/bible_queue.py:166`), `GitHub.label` (`.github/bible/bible_queue.py:310`) |
| Calls | `GitHub.paged`, `GitHub.call`, `known_labels.add` |
| Purpose | Loads the known-label set on first use and creates a requested label if it is absent. |

**Steps**

1. If `known_labels` is `None`, pages `/labels` and caches their names. (`.github/bible/bible_queue.py:154-155`)
2. If `name` is missing, posts a label with the fixed color `5319e7` and `why` truncated to 100 characters, then adds the name to the cache. (`.github/bible/bible_queue.py:156-158`)

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
| `.github/bible/bible_queue.py:154` | if | `known_labels` is `None` | Fetches and caches current label names. |
| `.github/bible/bible_queue.py:156` | if | `name` is not in the cache | Creates the label and adds its name to the cache. |

#### `GitHub.ensure_labels()`

Source: `.github/bible/bible_queue.py:160-162` <!-- code: 3233fadcc4c0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1288`) |
| Calls | `LABELS.items`, `GitHub.ensure_label` |
| Purpose | Ensures each label defined in the module's `LABELS` mapping exists. |

**Steps**

1. Iterates each `(name, why)` pair in `LABELS` and invokes `ensure_label`. (`.github/bible/bible_queue.py:161-162`)

**Pseudo-code**

```text
for name, why in LABELS:
    ensure_label(name, why)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:161` | for | For each `(name, why)` in `LABELS.items()` | Calls `ensure_label` once for that pair. |

#### `GitHub.create_issue(title, body, labels, assign=None)`

Source: `.github/bible/bible_queue.py:164-171` <!-- code: c0db4afc186c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:576`), `Queue.plan_phase` (`.github/bible/bible_queue.py:656`), `Queue.start_chunk` (`.github/bible/bible_queue.py:682`), `Queue.component` (`.github/bible/bible_queue.py:741`, `.github/bible/bible_queue.py:775`, `.github/bible/bible_queue.py:788`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1010`), `Queue.delta` (`.github/bible/bible_queue.py:1232`, `.github/bible/bible_queue.py:1247`), `main` (`.github/bible/bible_queue.py:1296`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures labels, optionally configures agent assignment, and creates an issue. |

**Steps**

1. Ensures every requested label, using its `LABELS` description or `Codebase analysis run` as the fallback. (`.github/bible/bible_queue.py:165-166`)
2. Builds a payload containing `title`, `body`, and `labels`; if `assign` is not `None`, adds the Copilot assignee and `agent_assignment`. (`.github/bible/bible_queue.py:167-170`)
3. Posts the payload to `/issues` and returns the result of `call`. (`.github/bible/bible_queue.py:171`)

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
| `.github/bible/bible_queue.py:165` | for | For each requested label | Calls `ensure_label` with its mapped or fallback description. |
| `.github/bible/bible_queue.py:168` | if | `assign` is not `None` | Adds `COPILOT` and the assignment value to the payload. |

#### `GitHub.me()`

Source: `.github/bible/bible_queue.py:173-177` <!-- code: 6c567c6be9c4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1142`) |
| Calls | `getattr`, `GitHub.call`, `get` |
| Purpose | Lazily fetches and caches the token owner's login. |

**Steps**

1. If `_me` is not already truthy, GETs the API `/user` URL and stores its `login`, defaulting to an empty string when the response is falsey or has no login. (`.github/bible/bible_queue.py:175-176`)
2. Returns the cached `_me` value. (`.github/bible/bible_queue.py:177`)

**Pseudo-code**

```text
if _me is falsey: _me = GET api/user.login or ""
return _me
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:175` | if | `_me` is falsey or absent | Fetches and caches the token owner's login. |

#### `GitHub.default_branch()`

Source: `.github/bible/bible_queue.py:179-180` <!-- code: 4eb167486c4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:583`), `Queue.delta` (`.github/bible/bible_queue.py:1199`) |
| Calls | `GitHub.call` |
| Purpose | Returns the repository's `default_branch` value. |

**Steps**

1. Gets the repository resource at the empty path and returns its `default_branch` field. (`.github/bible/bible_queue.py:180`)

**Pseudo-code**

```text
return GET repository["default_branch"]
```

#### `GitHub.branch_sha(branch)`

Source: `.github/bible/bible_queue.py:182-184` <!-- code: 446defb234bd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:674`, `.github/bible/bible_queue.py:675`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Returns a branch reference's object SHA or `None` when the reference is absent. |

**Steps**

1. Quotes `branch` and gets its head reference with `ok404=True`. (`.github/bible/bible_queue.py:183`)
2. Returns `ref["object"]["sha"]` if a reference was returned, otherwise `None`. (`.github/bible/bible_queue.py:184`)

**Pseudo-code**

```text
ref = GET quoted branch reference, allowing 404
return ref.object.sha if ref else None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:184` | conditional expression | A reference was returned | Returns its object SHA; otherwise returns `None`. |

#### `GitHub.create_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:186-187` <!-- code: b860758c1ca1 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:676`) |
| Calls | `GitHub.call` |
| Purpose | Creates a Git reference for a branch at a supplied SHA. |

**Steps**

1. Posts `ref: "refs/heads/" + branch` and `sha` to `/git/refs`. (`.github/bible/bible_queue.py:187`)

**Pseudo-code**

```text
POST /git/refs with ref "refs/heads/" + branch and sha
```

#### `GitHub.reset_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:189-190` <!-- code: 43e383793681 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:678`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Force-updates a branch reference to a supplied SHA. |

**Steps**

1. Quotes `branch` and PATCHes its head reference with the supplied SHA and `force: True`. (`.github/bible/bible_queue.py:190`)

**Pseudo-code**

```text
PATCH quoted head reference with sha and force=True
```

#### `GitHub.file(path, ref)`

Source: `.github/bible/bible_queue.py:192-196` <!-- code: e383f7bd9e38 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `issue_text` (`.github/bible/bible_queue.py:415`), `json_file` (`.github/bible/bible_queue.py:430`), `Queue.component` (`.github/bible/bible_queue.py:754`), `Queue.follow` (`.github/bible/bible_queue.py:849`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:927`, `.github/bible/bible_queue.py:933`, `.github/bible/bible_queue.py:937`, `.github/bible/bible_queue.py:976`), `Queue.delta` (`.github/bible/bible_queue.py:1218`) |
| Calls | `GitHub.call`, `urllib.parse.quote`, `isinstance`, `base64.b64decode`, `decode` |
| Purpose | Retrieves and decodes a text file from a repository reference. |

**Steps**

1. Quotes `path` and `ref` and GETs the contents endpoint with `ok404=True`. (`.github/bible/bible_queue.py:193`)
2. Returns `None` for a falsey response, a list response, or a response without `content`. (`.github/bible/bible_queue.py:194-195`)
3. Base64-decodes the content and decodes UTF-8 with replacement for invalid bytes. (`.github/bible/bible_queue.py:196`)

**Pseudo-code**

```text
got = GET quoted contents path at quoted ref, allowing 404
if got is falsey, a list, or lacks content: return None
return base64-decode content, then UTF-8 decode with replacement
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:194` | if | Response is falsey, a list, or has no `content` | Returns `None`. |

#### `GitHub.prs(base=None, state="open")`

Source: `.github/bible/bible_queue.py:198-200` <!-- code: e46dcb273277 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site found; unused (inferred: search for `.prs(` in `.github/bible/bible_queue.py` returned no matches). |
| Calls | `urllib.parse.quote`, `GitHub.paged` |
| Purpose | Lists pull requests by state and optional base branch. |

**Steps**

1. Builds `/pulls?state=<state>` and appends a URL-quoted base query only when `base` is truthy. (`.github/bible/bible_queue.py:199`)
2. Returns the paged results. (`.github/bible/bible_queue.py:200`)

**Pseudo-code**

```text
path = /pulls?state=state
if base is truthy: append quoted base query
return paged(path)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:199` | conditional expression | `base` is truthy | Appends `&base=` and the quoted base; otherwise appends nothing. |

#### `GitHub.timeline(number)`

Source: `.github/bible/bible_queue.py:202-203` <!-- code: 6df4539072ff -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.linked_prs` (`.github/bible/bible_queue.py:208`), `GitHub.agent_events` (`.github/bible/bible_queue.py:223`), `GitHub.start_error` (`.github/bible/bible_queue.py:237`), `GitHub.assigned_at` (`.github/bible/bible_queue.py:247`) |
| Calls | `GitHub.paged` |
| Purpose | Returns all paged timeline events for an issue number. |

**Steps**

1. Pages `/issues/<number>/timeline` and returns the result. (`.github/bible/bible_queue.py:203`)

**Pseudo-code**

```text
return paged /issues/<number>/timeline
```

#### `GitHub.linked_prs(number)`

Source: `.github/bible/bible_queue.py:205-214` <!-- code: 91e30cd14abd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:487`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:938`, `.github/bible/bible_queue.py:972`) |
| Calls | `GitHub.timeline`, `get`, `append`, `GitHub.call`, `sorted`, `set` |
| Purpose | Finds existing pull requests in this repository cross-referenced from an issue. |

**Steps**

1. Iterates the issue timeline and reads each event's source issue, defaulting missing source/repository values as shown. (`.github/bible/bible_queue.py:207-210`)
2. Collects the source number only for `cross-referenced` events whose source has a `pull_request` and whose repository full name equals this client's repository. (`.github/bible/bible_queue.py:211-212`)
3. Deduplicates and sorts numbers, GETs each pull request with `ok404=True`, and returns only non-`None` results. (`.github/bible/bible_queue.py:213-214`)

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
| `.github/bible/bible_queue.py:208` | for | For each issue timeline event | Inspects its source issue. |
| `.github/bible/bible_queue.py:211` | if | Event is a same-repository cross-reference with a pull request | Appends its source number. |

#### `GitHub.branch_prs(branch, base)`

Source: `.github/bible/bible_queue.py:216-219` <!-- code: fa42118d7d5a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:688`, `.github/bible/bible_queue.py:731`) |
| Calls | `split`, `GitHub.paged`, `urllib.parse.quote` |
| Purpose | Lists all-state pull requests from this repository's branch into a specified base. |

**Steps**

1. Takes the owner portion before `/` in `repo`. (`.github/bible/bible_queue.py:218`)
2. Pages `/pulls` with `state=all`, quoted `owner:branch` as `head`, and quoted `base`. (`.github/bible/bible_queue.py:219`)

**Pseudo-code**

```text
owner = first segment of repo
return paged /pulls with state=all, head=quoted(owner + ":" + branch), base=quoted(base)
```

#### `GitHub.agent_events(number)`

Source: `.github/bible/bible_queue.py:221-225` <!-- code: 1e123ab3f131 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.is_agent_pr` (`.github/bible/bible_queue.py:232`), `Queue.session` (`.github/bible/bible_queue.py:501`) |
| Calls | `GitHub.timeline`, `get` |
| Purpose | Returns the timeline events GitHub records as performed by Copilot's app and named in `WORK_EVENTS` (work started, work finished, work finished with failure) as `(event, timestamp)` pairs. |

**Steps**

1. Reads the pull request's timeline with `self.timeline(number)` and builds one `(event, created_at)` pair per kept event, defaulting a missing `created_at` to the empty string. (`.github/bible/bible_queue.py:223`)
2. Keeps only events whose `performed_via_github_app.slug` equals `AGENT_APP` (default `copilot-swe-agent`, from the environment variable `BIBLE_AGENT_APP`). (`.github/bible/bible_queue.py:224`, `.github/bible/bible_queue.py:65`)
3. Keeps only events whose name is in `WORK_EVENTS`: `copilot_work_started`, `copilot_work_finished` or `copilot_work_finished_failure`. The failure event is the new member, so a session that ended in failure now shows up in the list. (`.github/bible/bible_queue.py:225`, `.github/bible/bible_queue.py:69`)

**Pseudo-code**

```text
return (event, created_at or "") for each timeline event of the pull request
    where the event was performed via the app AGENT_APP
      and the event name is in WORK_EVENTS
          (copilot_work_started, copilot_work_finished, copilot_work_finished_failure)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:224` | comprehension filter | the event's app slug is not `AGENT_APP`, or it has no app | the event is left out |
| `.github/bible/bible_queue.py:225` | comprehension filter | the event name is not in `WORK_EVENTS` | the event is left out |

**Output and side effects**: returns a list of `(event, created_at)` pairs in timeline order; no writes. `Queue.session` sorts it by timestamp and reads the newest pair (`.github/bible/bible_queue.py:503`); `GitHub.is_agent_pr` only tests for a `copilot_work_started` pair (`.github/bible/bible_queue.py:232`).

#### `GitHub.is_agent_pr(pr)`

Source: `.github/bible/bible_queue.py:227-232` <!-- code: bad4f383c910 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:489`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:934`, `.github/bible/bible_queue.py:973`) |
| Calls | `get`, `GitHub.agent_events`, `any` |
| Purpose | Tests whether a pull request is attributed to a configured agent login or has a Copilot-start event. |

**Steps**

1. Reads `pr["user"]`, defaulting to an empty dictionary, and checks whether its login (defaulting to an empty string) is in `AGENT_LOGINS` and its type (defaulting to `"Bot"`) is `"Bot"`. (`.github/bible/bible_queue.py:229-230`)
2. Returns `True` immediately for that configured bot identity; otherwise checks the pull request timeline and returns whether any event is `copilot_work_started`. (`.github/bible/bible_queue.py:230-232`)

**Pseudo-code**

```text
if PR user's login is in AGENT_LOGINS and user type is Bot: return True
return any agent event is copilot_work_started
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:230` | if | PR user's login is in `AGENT_LOGINS` and user type is `"Bot"` | Returns `True` without checking the timeline. |

#### `GitHub.start_error(issue)`

Source: `.github/bible/bible_queue.py:234-243` <!-- code: 0287983c593a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:498`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:553`) |
| Calls | `GitHub.assigned_at`, `GitHub.timeline`, `get`, `START_ERROR.search`, `splitlines`, `strip` |
| Purpose | Returns the first matching agent start-error comment since the last assignment, or `None`. |

**Steps**

1. Gets the last assignment time using `assigned_at`, then scans the issue timeline. (`.github/bible/bible_queue.py:236-237`)
2. Chooses `actor` or `user`, then uses the actor login only when the actor type defaults to or is `"Bot"`. (`.github/bible/bible_queue.py:238-239`)
3. Requires a `commented` event by a configured agent at or after the assignment time and a body matching `START_ERROR`. (`.github/bible/bible_queue.py:240-241`)
4. Returns the stripped first body line, truncated to 300 characters, for the first qualifying event; returns `None` if no event qualifies. (`.github/bible/bible_queue.py:242-243`)

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
| `.github/bible/bible_queue.py:237` | for | For each issue timeline event | Checks actor, event time, and body. |
| `.github/bible/bible_queue.py:239` | conditional expression | Actor is a bot (or has no type) | Uses the actor login; otherwise uses an empty login. |
| `.github/bible/bible_queue.py:240` | if | Comment event from configured agent at/after assignment matches `START_ERROR` | Returns the bounded first line; otherwise continues scanning. |

#### `GitHub.assigned_at(issue)`

Source: `.github/bible/bible_queue.py:245-248` <!-- code: 8dec0d30b502 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.start_error` (`.github/bible/bible_queue.py:236`), `Queue.session` (`.github/bible/bible_queue.py:500`) |
| Calls | `GitHub.timeline`, `get`, `max` |
| Purpose | Returns the newest timestamp for an assignment event, falling back to issue creation time. |

**Steps**

1. Collects nonempty `created_at` values from `assigned` timeline events for the issue. (`.github/bible/bible_queue.py:247`)
2. Returns the maximum timestamp, or `issue["created_at"]` if there were none. (`.github/bible/bible_queue.py:248`)

**Pseudo-code**

```text
times = created_at for assigned events with a timestamp
return max(times) if any, otherwise issue.created_at
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:248` | conditional expression | At least one assignment timestamp exists | Returns the newest timestamp; otherwise uses issue creation time. |

#### `GitHub.pr_files(number)`

Source: `.github/bible/bible_queue.py:250-263` <!-- code: 58ad7fd72404 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:814`, `.github/bible/bible_queue.py:820`, `.github/bible/bible_queue.py:823`, `.github/bible/bible_queue.py:842`) |
| Calls | `GitHub.paged`, `as_int`, `GitHub.call`, `get`, `len`, `append`, `RuntimeError` |
| Purpose | Returns each changed filename and, when present, its previous name. |

**Steps**

1. Pages the pull request files endpoint and reads the pull request's `changed_files` count. (`.github/bible/bible_queue.py:253-254`)
2. If the expected count is nonzero and differs from the number listed, raises `RuntimeError` rather than accepting an incomplete file list. (`.github/bible/bible_queue.py:255-257`)
3. Appends each current `filename`, then appends `previous_filename` when truthy, and returns the list. (`.github/bible/bible_queue.py:258-263`)

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
| `.github/bible/bible_queue.py:255` | if | Expected count is nonzero and differs from listed count | Raises `RuntimeError` for an incomplete file list. |
| `.github/bible/bible_queue.py:256` | raise | Listed count differs from a nonzero expected count | Raises the incomplete-file-list `RuntimeError`. |
| `.github/bible/bible_queue.py:259` | for | For each paged pull request file | Appends its current filename. |
| `.github/bible/bible_queue.py:261` | if | `previous_filename` is truthy | Appends the previous filename. |

#### `GitHub.commit_time(sha)`

Source: `.github/bible/bible_queue.py:265-266` <!-- code: a3036655ce65 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:504`) |
| Calls | `GitHub.call` |
| Purpose | Returns the committer date for a commit SHA. |

**Steps**

1. GETs `/commits/<sha>` and returns `commit.committer.date`. (`.github/bible/bible_queue.py:266`)

**Pseudo-code**

```text
return GET /commits/<sha>.commit.committer.date
```

#### `GitHub.tarball(ref, dest)`

Source: `.github/bible/bible_queue.py:268-307` <!-- code: a84776e4e94b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.check` (`.github/bible/bible_queue.py:866`), `Queue.whole_fingerprint` (`.github/bible/bible_queue.py:904`) |
| Calls | `urllib.parse.quote`, `tempfile.TemporaryFile`, `self.request`, `resp.read`, `len`, `buf.write`, `RuntimeError`, `buf.seek`, `os.path.abspath`, `tarfile.open`, `max`, `member.name.split`, `os.path.normpath`, `os.path.join`, `member.isdir`, `os.makedirs`, `os.path.dirname`, `tar.extractfile`, `open`, `shutil.copyfileobj` |
| Purpose | Downloads a bounded repository archive into a temporary file and extracts only regular files and directories whose normalized paths stay below `dest`. |

**Steps**

1. Quotes `ref`, builds the repository tarball URL and requests it with a 300-second timeout. Reads 1 MiB chunks into a `TemporaryFile`; an empty read ends the loop, while cumulative bytes above `MAX_TARBALL` raise `RuntimeError`. (`.github/bible/bible_queue.py:272-283`)
2. Converts request `URLError`, `TimeoutError` or `OSError` into `RuntimeError`, seeks the temporary file to the beginning, resolves `dest` to an absolute root, and opens it as a gzip tar archive. (`.github/bible/bible_queue.py:274-289`)
3. Counts members and their nonnegative uncompressed sizes; exceeding `MAX_MEMBERS` or `MAX_UNPACKED` raises `RuntimeError`. It splits each member name once at `/`, skipping a missing/empty path tail and non-file/non-directory members. (`.github/bible/bible_queue.py:290-298`)
4. Joins the tail to the root, normalizes it, and skips a target whose path does not start with `root + os.sep`. Directories are created recursively; files get a created parent and are copied from `tar.extractfile(member)` into a binary file. (`.github/bible/bible_queue.py:299-307`)

**Pseudo-code**

```text
stream GET tarball(ref) to temporary file in 1 MiB chunks
stop on empty; raise if compressed-size limit is exceeded
seek to start; root = absolute(dest); open gzip tar
for archive member:
    count members and nonnegative uncompressed sizes; raise if either limit exceeded
    skip invalid name or non-file/non-directory
    target = normalized join(root, member-relative path)
    skip target outside root
    if directory: mkdir target
    else: mkdir parent and copy extracted bytes to target
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:276` | while | Response chunks are being read | Reads the next chunk and exits when it is empty. |
| `.github/bible/bible_queue.py:278` | if | `resp.read` returns no bytes | Leaves the streaming loop. |
| `.github/bible/bible_queue.py:281` | if | Total compressed bytes exceed `MAX_TARBALL` | Raises `RuntimeError` without unpacking. |
| `.github/bible/bible_queue.py:282` | raise | Compressed-size limit exceeded | Reports the reference and configured maximum. |
| `.github/bible/bible_queue.py:284` | except | Request raises `URLError`, `TimeoutError` or `OSError` | Converts the error to a `RuntimeError` naming the reference. |
| `.github/bible/bible_queue.py:285` | raise | A listed request error occurred | Stops with the wrapped `RuntimeError`. |
| `.github/bible/bible_queue.py:290` | for | For each archive member | Counts the member and validates total limits before extraction. |
| `.github/bible/bible_queue.py:293` | if | Member count or uncompressed-size limit is exceeded | Raises `RuntimeError`; extraction stops. |
| `.github/bible/bible_queue.py:294` | raise | A tarball member limit was exceeded | Reports the member and uncompressed-size limits. |
| `.github/bible/bible_queue.py:297` | if | Missing path tail or member is neither regular file nor directory | Skips the member. |
| `.github/bible/bible_queue.py:300` | if | Normalized target does not start with the root plus separator | Skips the target. |
| `.github/bible/bible_queue.py:302` | if | Member is a directory | Creates it and continues to the next member. |

#### `GitHub.label(number, name)`

Source: `.github/bible/bible_queue.py:309-311` <!-- code: 3c67a9360e66 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:554`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:566`), `Queue.follow` (`.github/bible/bible_queue.py:832`, `.github/bible/bible_queue.py:833`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures and adds one label to an issue. |

**Steps**

1. Ensures the label using its `LABELS` description or the default description. (`.github/bible/bible_queue.py:310`)
2. Posts `{"labels": [name]}` to the issue labels endpoint. (`.github/bible/bible_queue.py:311`)

**Pseudo-code**

```text
ensure label using mapped description or default
POST issue labels with [name]
```

#### `GitHub.unlabel(number, name)`

Source: `.github/bible/bible_queue.py:313-314` <!-- code: caf34958b931 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:853`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Removes a label from an issue and permits a missing-label response. |

**Steps**

1. URL-quotes `name` and sends DELETE to the issue label endpoint with `ok404=True`. (`.github/bible/bible_queue.py:314`)

**Pseudo-code**

```text
DELETE quoted issue label endpoint, allowing 404
```

#### `GitHub.comment(number, text)`

Source: `.github/bible/bible_queue.py:316-317` <!-- code: a05e7f494734 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:532`, `.github/bible/bible_queue.py:536`, `.github/bible/bible_queue.py:544`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:556`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:563`, `.github/bible/bible_queue.py:568`, `.github/bible/bible_queue.py:571`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:955`, `.github/bible/bible_queue.py:960`, `.github/bible/bible_queue.py:981`, `.github/bible/bible_queue.py:1018`, `.github/bible/bible_queue.py:1025`) |
| Calls | `GitHub.call` |
| Purpose | Creates an issue comment with the given body. |

**Steps**

1. Posts `{"body": text}` to `/issues/<number>/comments`. (`.github/bible/bible_queue.py:317`)

**Pseudo-code**

```text
POST issue comments with body=text
```

#### `GitHub.close(number, reason="completed")`

Source: `.github/bible/bible_queue.py:319-320` <!-- code: db2a40d380a0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:572`), `Queue.run` (`.github/bible/bible_queue.py:626`), `Queue.component` (`.github/bible/bible_queue.py:716`), `Queue.follow` (`.github/bible/bible_queue.py:854`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:983`, `.github/bible/bible_queue.py:985`, `.github/bible/bible_queue.py:1019`) |
| Calls | `GitHub.call` |
| Purpose | Closes an issue with the supplied state reason. |

**Steps**

1. PATCHes `/issues/<number>` with `state: "closed"` and the supplied `state_reason`. (`.github/bible/bible_queue.py:320`)

**Pseudo-code**

```text
PATCH issue state=closed and state_reason=reason
```

#### `GitHub.set_body(number, body)`

Source: `.github/bible/bible_queue.py:322-323` <!-- code: 56545a0f998b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:541`), `Queue.render` (`.github/bible/bible_queue.py:1192`) |
| Calls | `GitHub.call` |
| Purpose | Replaces an issue's body. |

**Steps**

1. PATCHes `/issues/<number>` with `{"body": body}`. (`.github/bible/bible_queue.py:323`)

**Pseudo-code**

```text
PATCH issue body=body
```

#### `GitHub.unassign(number)`

Source: `.github/bible/bible_queue.py:325-326` <!-- code: 415484346894 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:555`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:567`) |
| Calls | `GitHub.call` |
| Purpose | Removes the configured Copilot assignee from an issue. |

**Steps**

1. Sends DELETE to `/issues/<number>/assignees` with `COPILOT` as the sole assignee. (`.github/bible/bible_queue.py:326`)

**Pseudo-code**

```text
DELETE issue assignees with [COPILOT]
```

#### `GitHub.assign(number, assign)`

Source: `.github/bible/bible_queue.py:328-329` <!-- code: 8fb2f09224db -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:543`) |
| Calls | `GitHub.call` |
| Purpose | Assigns Copilot to an issue with the provided agent-assignment data. |

**Steps**

1. Posts `COPILOT` as the sole assignee and includes the supplied `agent_assignment`. (`.github/bible/bible_queue.py:329`)

**Pseudo-code**

```text
POST issue assignees with [COPILOT] and agent_assignment=assign
```

#### `GitHub.ready(pr)`

Source: `.github/bible/bible_queue.py:331-339` <!-- code: ae31dacf00e7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.merge` (`.github/bible/bible_queue.py:343`) |
| Calls | `endswith`, `GitHub.request`, response `read`, `RuntimeError` |
| Purpose | Marks a draft pull request ready for review through GitHub GraphQL. |

**Steps**

1. Defines the `markPullRequestReadyForReview` mutation and chooses the GraphQL URL; for an API base ending `/api/v3`, removes `/v3` before adding `/graphql`. (`.github/bible/bible_queue.py:333-334`)
2. POSTs the query and `pr["node_id"]` as the `id` variable, then reads the response. (`.github/bible/bible_queue.py:335-337`)
3. Converts an `HTTPError` to a `RuntimeError` containing the GraphQL operation and HTTP status. (`.github/bible/bible_queue.py:338-339`)

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
| `.github/bible/bible_queue.py:334` | conditional expression | API URL ends with `/api/v3` | Removes `/v3` before appending `/graphql`; otherwise appends `/graphql` directly. |
| `.github/bible/bible_queue.py:338` | except | Request raises `HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:339` | raise | GraphQL request raises `HTTPError` | Raises `RuntimeError` with operation and HTTP status. |

#### `GitHub.merge(pr, title)`

Source: `.github/bible/bible_queue.py:341-345` <!-- code: cea69f3a2a18 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:852`) |
| Calls | `get`, `GitHub.ready`, `GitHub.call` |
| Purpose | Marks a draft ready, when needed, and requests a squash merge with the supplied title. |

**Steps**

1. Calls `ready` only when `pr["draft"]` is truthy. (`.github/bible/bible_queue.py:342-343`)
2. PUTs `/pulls/<number>/merge` with `merge_method: "squash"`, the supplied `commit_title`, and the current head SHA. (`.github/bible/bible_queue.py:344-345`)

**Pseudo-code**

```text
if PR is draft: mark it ready
PUT merge request with squash method and title
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:342` | if | `pr["draft"]` is truthy | Calls `ready` before requesting the merge. |

#### `GitHub.close_pr(number)`

Source: `.github/bible/bible_queue.py:347-348` <!-- code: c5e4b3b311ae -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:564`) |
| Calls | `GitHub.call` |
| Purpose | Closes a pull request. |

**Steps**

1. PATCHes `/pulls/<number>` with `state: "closed"`. (`.github/bible/bible_queue.py:348`)

**Pseudo-code**

```text
PATCH pull request state=closed
```

#### `GitHub.create_pr(head, base, title, body)`

Source: `.github/bible/bible_queue.py:350-351` <!-- code: 9b2aa4667c1c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:756`) |
| Calls | `GitHub.call` |
| Purpose | Creates a pull request and returns the API result. |

**Steps**

1. POSTs `head`, `base`, `title`, and `body` to `/pulls`, returning `call`'s result. (`.github/bible/bible_queue.py:351`)

**Pseudo-code**

```text
return POST /pulls with head, base, title, and body
```

### `Queue`

Source: `.github/bible/bible_queue.py:477-1257`

`Queue` coordinates tracker issues, component sessions, verification/revision cycles, assembly, and delta updates; since 24 Nov 2026 it also continues an assembly or whole-analysis session that ended before its end marker, and holds one whose Copilot session failed before starting (`Queue.continue_if_unfinished`, `.github/bible/bible_queue.py:1131-1181`). Its constructor sets the GitHub client, logger, and skill directory (`.github/bible/bible_queue.py:478-480`); methods also populate run-specific fields: `deadline` and `default` in `reconcile` (`.github/bible/bible_queue.py:582-583`), `settings`, `tracker`, `run_label` and `state` in `run` (`.github/bible/bible_queue.py:596-604`), and `estimate` (`.github/bible/bible_queue.py:627`).

#### `Queue.__init__(gh, log=print)`

Source: `.github/bible/bible_queue.py:478-480` <!-- code: 11924208c0e9 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1280`) |
| Calls | `os.environ.get` |
| Purpose | Stores the GitHub client and logger, and selects the skills directory. |

**Steps**

1. Stores `gh` and `log` on the instance. (`.github/bible/bible_queue.py:479`)
2. Reads `BIBLE_SKILLS`, defaulting to `.github/skills`. (`.github/bible/bible_queue.py:480`)

**Pseudo-code**

```text
self.gh, self.log = gh, log
self.skills = BIBLE_SKILLS or ".github/skills"
```

#### `Queue.run_issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:482-483` <!-- code: 9186c4a33e43 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:625`), `Queue.plan_phase` (`.github/bible/bible_queue.py:649`), `Queue.start_chunk` (`.github/bible/bible_queue.py:677`), `Queue.component` (`.github/bible/bible_queue.py:697`, `.github/bible/bible_queue.py:709`, `.github/bible/bible_queue.py:711`, `.github/bible/bible_queue.py:717`, `.github/bible/bible_queue.py:733`, `.github/bible/bible_queue.py:748`, `.github/bible/bible_queue.py:751`, `.github/bible/bible_queue.py:753`, `.github/bible/bible_queue.py:769`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:919`, `.github/bible/bible_queue.py:952`, `.github/bible/bible_queue.py:958`, `.github/bible/bible_queue.py:969`) |
| Calls | `self.gh.issues` |
| Purpose | Queries issues for the requested labels plus this run's unique label. |

**Steps**

1. Appends `self.run_label` to the supplied labels and calls `gh.issues` with the requested state. (`.github/bible/bible_queue.py:483`)

**Pseudo-code**

```text
return gh.issues(labels + [run_label], state)
```

#### `Queue.agent_pr(issue, base)`

Source: `.github/bible/bible_queue.py:485-491` <!-- code: 471c772b908b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:496`) |
| Calls | `reversed`, `self.gh.linked_prs`, `get`, `self.gh.is_agent_pr` |
| Purpose | Finds the newest linked pull request that is open, same-repository, targets `base`, and is by the agent. |

**Steps**

1. Iterates linked pull requests in reverse order. (`.github/bible/bible_queue.py:487`)
2. Reads the head repository full name, defaulting missing nested values to `{}`. (`.github/bible/bible_queue.py:488`)
3. Returns the first PR whose state is `open`, head repository is `gh.repo`, base ref matches, and `is_agent_pr` is true. (`.github/bible/bible_queue.py:489-490`)
4. Returns `None` when no linked PR qualifies. (`.github/bible/bible_queue.py:491`)

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
| `.github/bible/bible_queue.py:487` | for | For each linked PR in reverse order | Checks newer linked PRs first. |
| `.github/bible/bible_queue.py:489` | if | PR is open, same-repository, targets `base`, and is an agent PR | Returns that PR. |

#### `Queue.session(issue, base, analysis, comp=None)`

Source: `.github/bible/bible_queue.py:494-510` <!-- code: 287d4620c196 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:662`), `Queue.follow` (`.github/bible/bible_queue.py:801`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:991`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1085`) |
| Calls | `self.agent_pr`, `self.gh.start_error`, `age`, `self.gh.assigned_at`, `self.gh.agent_events`, `sorted`, `self.gh.commit_time`, `bool`, `pr.get`, `status_of`, `labels_of`, `status.get` |
| Purpose | Classifies an open session issue as start-error, no-start, waiting, running or finished and returns its pull request when there is one. |

**Steps**

1. Looks up the agent's open pull request for the issue with `self.agent_pr(issue, base)`. (`.github/bible/bible_queue.py:496`)
2. With no pull request: returns `("start-error", None)` when `gh.start_error(issue)` is truthy; otherwise returns `("no-start", None)` when the age of the issue's assignment exceeds `NO_PR_AFTER` (30 minutes), else `("waiting", None)`. (`.github/bible/bible_queue.py:497-500`, `.github/bible/bible_queue.py:72`)
3. With a pull request, reads `gh.agent_events` for it. When any event exists, GitHub's own record decides: the newest event by timestamp being `copilot_work_started` gives `"running"`, any other newest event (`copilot_work_finished` or, since `WORK_EVENTS` gained it, `copilot_work_finished_failure`) gives `"finished"`; the pull request is returned with it. (`.github/bible/bible_queue.py:501-503`)
4. With no work events, computes `pushed`, the age of the head commit, and `asked`, true when reviewers were requested or the pull request is not a draft. (`.github/bible/bible_queue.py:504-505`)
5. For a component chunk (`comp` given and the label `bible-chunk` on the issue), reads `<analysis>/ledger/components/<comp>/status.json` at the head SHA and sets `final` when its `state` is in `FINAL_STATES`; returns `"finished"` when `final` and (`asked` or `pushed` > `IDLE_AFTER`), or when `pushed` > 3 x `IDLE_AFTER`, else `"running"`. (`.github/bible/bible_queue.py:506-509`)
6. Otherwise returns `"finished"` when `asked` or `pushed` > `IDLE_AFTER`, else `"running"`. (`.github/bible/bible_queue.py:510`)

**Pseudo-code**

```text
pr = agent_pr(issue, base)
if no pr:
    if start_error(issue): return ("start-error", None)
    return ("no-start" if assignment age > NO_PR_AFTER else "waiting", None)
work = agent_events(pr)                  # started / finished / finished_failure by Copilot's app
if work:
    return ("running" if newest event is copilot_work_started else "finished", pr)
pushed = age(head commit time)
asked = requested reviewers or not draft
if comp and issue is bible-chunk:
    final = head status.json state in FINAL_STATES
    return ("finished" if (final and (asked or pushed > IDLE_AFTER))
            or pushed > 3 * IDLE_AFTER else "running", pr)
return ("finished" if asked or pushed > IDLE_AFTER else "running", pr)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:497` | if | no agent pull request was found | enters the start-error / no-start / waiting classification |
| `.github/bible/bible_queue.py:498` | if | `start_error(issue)` is truthy | returns `("start-error", None)` |
| `.github/bible/bible_queue.py:500` | conditional expression | assignment age exceeds `NO_PR_AFTER` | returns `no-start`; otherwise `waiting`; the pull request is `None` |
| `.github/bible/bible_queue.py:502` | if | `agent_events` returned at least one event | the newest event decides: `running` only for `copilot_work_started`, otherwise `finished` (a failure event counts as finished) |
| `.github/bible/bible_queue.py:503` | conditional expression | newest event is `copilot_work_started` | returns `running`; otherwise `finished` |
| `.github/bible/bible_queue.py:506` | if | `comp` is truthy and the issue has the label `bible-chunk` | uses the head `status.json` and the component-specific age rules |
| `.github/bible/bible_queue.py:509` | conditional expression | final status and (asked or idle), or pushed age exceeds `3 * IDLE_AFTER` | returns `finished`; otherwise `running` |
| `.github/bible/bible_queue.py:510` | conditional expression | `asked` or pushed age exceeds `IDLE_AFTER` | returns `finished`; otherwise `running` |

**Output and side effects**: returns a `(state, pr)` pair; reads only (timeline, commit time, `status.json` at the head SHA). The docstring lists four states and omits `start-error` (`.github/bible/bible_queue.py:495`).

#### `Queue.held(issue)`

Source: `.github/bible/bible_queue.py:512-545` <!-- code: c519a460eab6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:660`), `Queue.component` (`.github/bible/bible_queue.py:700`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:989`) |
| Calls | `labels_of`, `any`, `get`, `issue.get`, `self.gh.timeline`, `max`, `e.get`, `self.gh.label`, `self.gh.comment`, `self.gh.close`, `l.startswith`, `ATTEMPT.sub`, `self.gh.set_body`, `re.search`, `self.gh.assign`, `assignment`, `self.model_for`, `base.group` |
| Purpose | Holds issues marked for a person, closes released component sessions, or reassigns other unassigned sessions to Copilot. |

**Steps**

1. Returns `True` when the labels include `bible-needs-human`. (`.github/bible/bible_queue.py:520`)
2. Otherwise returns `False` immediately when an assignee login belongs to `AGENT_LOGINS`. (`.github/bible/bible_queue.py:522`)
3. Reads issue timeline events and finds the latest added and removed timestamps for `bible-needs-human`; if removal is absent or not newer, labels and comments the issue for human review and returns `True`. (`.github/bible/bible_queue.py:523-535`)
4. If a `bible/` label exists after release, comments and closes the issue as `not_planned`, returning `released`. (`.github/bible/bible_queue.py:536-539`)
5. Otherwise resets the `Attempt:` marker, saves the body, extracts `Base branch:` or uses `self.default`, assigns Copilot with the selected model, comments, and returns `False`. (`.github/bible/bible_queue.py:540-545`)

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
| `.github/bible/bible_queue.py:520` | if | Labels contain `bible-needs-human` | Returns `True`. |
| `.github/bible/bible_queue.py:522` | if | An assignee login belongs to `AGENT_LOGINS` | Returns `False`. |
| `.github/bible/bible_queue.py:529` | if | The human-label removal is absent or not newer than its addition | Labels, comments, and returns `True`. |
| `.github/bible/bible_queue.py:535` | return | No valid release follows the human hold | Stops before reassignment. |
| `.github/bible/bible_queue.py:536` | if | A component label begins `bible/` after release | Closes and returns `released`; otherwise reassigns. |
| `.github/bible/bible_queue.py:543` | conditional expression | A `Base branch:` match exists | Uses its captured branch; otherwise uses `self.default`. |

#### `Queue.model_for(issue)`

Source: `.github/bible/bible_queue.py:547-549` <!-- code: 17f084589886 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:543`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:577`) |
| Calls | `labels_of`, `self.settings.get` |
| Purpose | Selects the verification model for verification issue types, otherwise the normal model. |

**Steps**

1. Gets the issue's label names. (`.github/bible/bible_queue.py:548`)
2. Returns `verify_model` when labels intersect `bible-verify` or `bible-verify-all`; otherwise returns `model`. (`.github/bible/bible_queue.py:549`)

**Pseudo-code**

```text
kinds = labels_of(issue)
return settings.verify_model if kinds intersects verify labels
       else settings.model
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:549` | conditional expression | `kinds` intersects the verification labels | Returns `verify_model`; otherwise returns `model`. |

#### `Queue.hold_start_error(issue)`

Source: `.github/bible/bible_queue.py:551-557` <!-- code: 510c0f07df06 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:664`), `Queue.follow` (`.github/bible/bible_queue.py:805`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:993`) |
| Calls | `self.gh.start_error`, `self.gh.label`, `self.gh.unassign`, `self.gh.comment` |
| Purpose | Holds a session with an agent start error for human intervention. |

**Steps**

1. Gets the start-error text or uses `Copilot could not start`. (`.github/bible/bible_queue.py:553`)
2. Adds `bible-needs-human`, unassigns Copilot, and posts a comment containing the reason and remediation guidance. (`.github/bible/bible_queue.py:554-557`)

**Pseudo-code**

```text
why = start_error(issue) or fallback message
label issue bible-needs-human
unassign Copilot
comment why and instructions for removing the hold
```

#### `Queue.fail_or_retry(issue, pr, why)`

Source: `.github/bible/bible_queue.py:559-578` <!-- code: c86515a02433 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:667`), `Queue.follow` (`.github/bible/bible_queue.py:808`, `.github/bible/bible_queue.py:816`, `.github/bible/bible_queue.py:826`, `.github/bible/bible_queue.py:839`, `.github/bible/bible_queue.py:844`, `.github/bible/bible_queue.py:847`, `.github/bible/bible_queue.py:850`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:996`) |
| Calls | `ATTEMPT.search`, `int`, `self.gh.comment`, `self.gh.close_pr`, `self.gh.label`, `self.gh.unassign`, `self.gh.close`, `ATTEMPT.sub`, `re.search`, `self.gh.create_issue`, `sorted`, `assignment`, `self.model_for`, `labels_of`, `startswith` |
| Purpose | Closes a failed attempt and opens its retry, or holds the issue after a second failure. |

**Steps**

1. Parses the attempt number from the issue body, defaulting to 1. (`.github/bible/bible_queue.py:561`)
2. If a PR was supplied, comments that it was not merged and closes it. (`.github/bible/bible_queue.py:562-564`)
3. When attempt is at least 2, labels and unassigns the issue, posts a human-action comment, and returns `False`. (`.github/bible/bible_queue.py:565-570`)
4. Otherwise comments that a new attempt will open, closes the issue with `not_planned`, updates or prepends the attempt marker, and extracts the base branch or uses `self.default`. (`.github/bible/bible_queue.py:571-575`)
5. Creates a replacement issue with only labels beginning `bible`, sorted, and assignment data for the chosen base and model; returns `True`. (`.github/bible/bible_queue.py:576-578`)

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
| `.github/bible/bible_queue.py:562` | if | `pr` is truthy | Comments that it was not merged and closes the PR; otherwise skips PR updates. |
| `.github/bible/bible_queue.py:565` | if | Attempt number is at least 2 | Labels and unassigns the issue, comments for human action, and returns `False`; otherwise opens a retry. |
| `.github/bible/bible_queue.py:573` | conditional expression | The issue body contains an attempt marker | Replaces it with the incremented attempt; otherwise prepends `Attempt: 2`. |
| `.github/bible/bible_queue.py:577` | conditional expression | A `Base branch:` match exists in the original body | Assigns the retry to that branch; otherwise uses `self.default`. |

#### `Queue.reconcile()`

Source: `.github/bible/bible_queue.py:581-592` <!-- code: 10e9886e081f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1300`) |
| Calls | `self.gh.default_branch`, `self.gh.issues`, `settings_of`, `self.log`, `self.run`, `type` |
| Purpose | Processes each open tracker independently so one failing tracker does not prevent others. |

**Steps**

1. Sets a monotonic deadline at `now + RUN_BUDGET`, then stores the repository's default branch. (`.github/bible/bible_queue.py:582-583`)
2. Iterates open issues labeled `bible-tracker`; parses each settings block, logging and skipping trackers without readable settings. (`.github/bible/bible_queue.py:584-588`)
3. Runs each readable tracker independently; catches `Exception` and logs the tracker number, exception type and message, then continues with the next tracker. (`.github/bible/bible_queue.py:589-592`)

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
| `.github/bible/bible_queue.py:584` | for | For each open `bible-tracker` issue | Parses its settings and processes that tracker independently. |
| `.github/bible/bible_queue.py:586` | if | `settings_of` returns a falsey value | Logs the tracker number and skips it. |
| `.github/bible/bible_queue.py:589` | try | Settings are readable | Calls `run` for the tracker. |
| `.github/bible/bible_queue.py:591` | except | Processing the tracker raises `Exception` | Logs tracker number, exception type and message, then continues to the next tracker. |

#### `Queue.run(tracker, settings)`

Source: `.github/bible/bible_queue.py:594-645` <!-- code: ab24ac87df39 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:590`) |
| Calls | `settings.get`, `STATE.search`, `tracker.get`, `json.loads`, `found.group`, `isinstance`, `json_file`, `catalog.get`, `self.plan_phase`, `c.get`, `str`, `NAME.match`, `len`, `self.render`, `str.strip`, `asked.split`, `n.strip`, `join`, `self.run_issues`, `gh.close`, `self.component`, `str.endswith`, `str.startswith`, `as_int`, `self.start_chunk`, `type`, `all`, `rows.values`, `self.assemble_phase` |
| Purpose | Restores tracker state, validates the component catalog and selection, advances component states up to the configured concurrency, and renders the tracker. |

**Steps**

1. Selects `analysis` from settings or `codebase-analysis`, saves settings/tracker/run label, and parses the hidden state marker. Invalid JSON and non-dictionary state become `{}`. Reads `components.json` from the default branch. (`.github/bible/bible_queue.py:595-605`)
2. If the catalog is not a dict, is proposed, or lacks a list of components, returns the result of `plan_phase`. It stringifies each dict component's name, filters names with `NAME`, and renders a stopped settings row if any listed name is invalid. (`.github/bible/bible_queue.py:606-616`)
3. Strips the requested component selection; `all` or empty means all valid names, otherwise comma-splits and strips the names. Unknown or empty selection renders a stopped settings row and returns. (`.github/bible/bible_queue.py:617-624`)
4. Closes open plan issues, records catalog session estimates, evaluates each requested component, catches component exceptions into a 160-character error row, and counts rows ending in `running`, `starting`, or `merged`, or beginning with `waiting`. (`.github/bible/bible_queue.py:625-634`)
5. Converts `concurrency` with `as_int`; starts each `not started` component when the cap is zero or active count is below it. A `RuntimeError` becomes a 160-character error row. When every row is `merged`, adds whole-analysis assembly status; renders all rows. (`.github/bible/bible_queue.py:635-645`)

**Pseudo-code**

```text
analysis = settings.analysis or "codebase-analysis"; save settings, tracker, and run label
parse hidden state JSON; use {} if malformed or not a dict
catalog = components.json
if catalog invalid/proposed/no component list: return plan_phase
validate every component name; if any invalid: render stopped settings and return
parse selection; if unknown or empty: render stopped settings and return
close plan issues; record estimates; evaluate wanted components, bounding caught errors
count active rows; convert concurrency to integer
start not-started components while under the cap, recording start errors
if every row merged: add whole-analysis assembly status
render rows
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:600` | conditional expression | State marker matched | Parses its JSON group; otherwise uses `{}`. |
| `.github/bible/bible_queue.py:601` | except | State JSON raises `ValueError` | Replaces it with `{}`. |
| `.github/bible/bible_queue.py:603` | if | Parsed state is not a dict | Replaces it with `{}`. |
| `.github/bible/bible_queue.py:606` | if | Catalog is invalid, proposed, or has no component list | Returns the planning-phase result. |
| `.github/bible/bible_queue.py:612` | if | Any listed component name fails `NAME` | Renders a stopped settings row and returns. |
| `.github/bible/bible_queue.py:618` | conditional expression | Selection is `all` or empty | Uses all valid names; otherwise parses comma-separated names. |
| `.github/bible/bible_queue.py:620` | if | Selection contains unknown names or is empty | Renders stopped settings and returns. |
| `.github/bible/bible_queue.py:623` | conditional expression | Unknown names exist | Reports them; otherwise reports that no component was selected. |
| `.github/bible/bible_queue.py:625` | for | Open `bible-plan` issues exist | Closes each issue. |
| `.github/bible/bible_queue.py:629` | for | Each requested component | Evaluates its status. |
| `.github/bible/bible_queue.py:632` | except | Component evaluation raises `Exception` | Stores the exception type and at most 160 characters of its text. |
| `.github/bible/bible_queue.py:636` | for | Each requested component | Considers starting a `not started` row. |
| `.github/bible/bible_queue.py:637` | if | Row is `not started` and no cap or active count below cap | Attempts to start a fresh chunk. |
| `.github/bible/bible_queue.py:641` | except | Starting the chunk raises `RuntimeError` | Stores the exception text, capped at 160 characters. |
| `.github/bible/bible_queue.py:643` | if | Every row is `merged` | Adds whole-analysis assembly status. |

#### `Queue.plan_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:647-669` <!-- code: f5b3e835d2d7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:607`) |
| Calls | `self.run_issues`, `issue_text`, `self.gh.create_issue`, `self.render`, `assignment`, `settings.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry` |
| Purpose | Creates or tracks the plan issue and reports plan-session progress. |

**Steps**

1. Gets open plan issues for the tracker run. (`.github/bible/bible_queue.py:649`)
2. If none are open, reads the plan title and body from the analysis ledger; when the body is empty, supplies built-in instructions to run passes 1 and 2, write the Components table, and finish discovery without starting components. It then creates and assigns the plan issue and renders its assigned status. (`.github/bible/bible_queue.py:650-658`)
3. Otherwise selects the first plan issue; if held, renders its human-needed status. (`.github/bible/bible_queue.py:659-661`)
4. Classifies its session; if Copilot reports a start error, marks the issue for human action and renders that status. (`.github/bible/bible_queue.py:662-665`)
5. On `no-start`, requests a retry; then renders the pull-request review state when a PR exists, or the session state otherwise. (`.github/bible/bible_queue.py:666-669`)

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
| `.github/bible/bible_queue.py:650` | if | No open plan issue exists | Reads the planned issue text and creates an assigned plan issue. |
| `.github/bible/bible_queue.py:652` | if | The loaded body is falsey | Uses built-in plan and discovery instructions. |
| `.github/bible/bible_queue.py:660` | if | The first open plan issue is held | Renders that a person must act. |
| `.github/bible/bible_queue.py:663` | if | Session state is `start-error` | Holds the issue and renders human-needed state. |
| `.github/bible/bible_queue.py:666` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:668` | conditional expression | `pr` exists | Renders review/merge PR number; otherwise renders the session state. |

#### `Queue.start_chunk(analysis, name, fresh=False, note="")`

Source: `.github/bible/bible_queue.py:671-683` <!-- code: 7f612dd5f454 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:639`), `Queue.component` (`.github/bible/bible_queue.py:749`, `.github/bible/bible_queue.py:784`) |
| Calls | `self.gh.branch_sha`, `self.gh.create_branch`, `self.gh.reset_branch`, `self.run_issues`, `comp_label`, `issue_text`, `self.gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Creates the component branch when absent, optionally resets it for the first chunk, and opens the next assigned chunk issue. |

**Steps**

1. Sets branch to `bible/<name>` and reads the default branch SHA. (`.github/bible/bible_queue.py:673-674`)
2. Creates the component branch at that SHA when absent; otherwise resets it when `fresh` is true and there are no component issues in any state. (`.github/bible/bible_queue.py:675-678`)
3. Reads the component issue text from the default branch, formats the Component/Base branch/Attempt header, and creates a labeled chunk issue with optional note and model assignment. (`.github/bible/bible_queue.py:679-683`)

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
| `.github/bible/bible_queue.py:675` | if | The component branch has no SHA | Creates the branch at the default branch SHA. |
| `.github/bible/bible_queue.py:677` | elif | Branch exists, `fresh` is true, and no issue with the component label exists in any state | Resets the branch to the default branch SHA. |
| `.github/bible/bible_queue.py:682` | conditional expression | `note` is truthy | Adds the note and a newline before the body; otherwise adds no note prefix. |

#### `Queue.component(analysis, name)`

Source: `.github/bible/bible_queue.py:685-796` <!-- code: c0d9266497e6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:631`) |
| Calls | `gh.branch_prs`, `pr.get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `gh.close`, `labels_of`, `max`, `h.get`, `status_of`, `status.get`, `time.monotonic`, `getattr`, `float`, `self.check`, `self.could_not_check`, `self.state.pop`, `min`, `as_int`, `self.start_chunk`, `len`, `i.get`, `report_facts`, `gh.file`, `bool`, `any`, `gh.create_issue`, `gh.create_pr`, `assignment`, `self.settings.get` |
| Purpose | Advances one component through its pull requests, sessions, gate, verification/revision rounds, final review PR, or human hold. |

**Steps**

1. Scans PRs from `bible/<name>` to the default branch, skipping PRs from another repository, predating the tracker, or lacking its tracker reference. Returns `merged`, a review status for an open PR, or human-needed status for a matching closed-unmerged PR. (`.github/bible/bible_queue.py:688-696`)
2. Finds open chunk/verify issues. For the first, returns a released status, a human-needed status, or delegates to `follow`; with no open issue, returns `not started` if no component issue exists in any state. (`.github/bible/bible_queue.py:697-710`)
3. Reads the component status. For `COMPONENT_DONE`, waits for the next check if the run deadline cannot accommodate two gate timeouts plus 300 seconds; otherwise runs the gate. An un-runnable check increments its no-check count and may create a human hold; a runnable check clears that count. (`.github/bible/bible_queue.py:719-729`)
4. If the gate did not pass, counts closed chunks since the latest hold release or merge. Clamps the estimated sessions to 1–10, derives a bounded retry cap, creates a human hold when that cap is reached, otherwise starts the next chunk. (`.github/bible/bible_queue.py:730-750`)
5. After a passing gate, selects completed verifications since the last hold release and reads the report when any completed verification exists. A `PASS` with no major corrections and a matching nonempty page fingerprint creates a component-to-default PR. (`.github/bible/bible_queue.py:751-759`)
6. If no chunk completed after the latest verification and the count reaches `MAX_VERIFY_ROUNDS`, opens a human hold. If the verdict is about these pages and requests revision, starts a revision chunk; otherwise creates and assigns a verification issue and returns `verify running`. (`.github/bible/bible_queue.py:760-796`)

**Pseudo-code**

```text
for matching tracker PR: return merged, review, or needs-person status
if open chunk/verify issue: return released, needs-person, or follow(issue)
if no component issue ever existed: return not started
status = component status
if status is COMPONENT_DONE:
    if insufficient run time: wait for next check
    gate_ok, pages = check(...)
    if check could not run: count toward human hold; return/wait
if gate failed:
    if bounded chunk cap reached: create human hold
    else start next chunk; return
load completed verification/report facts after hold release
if clean matching PASS: create component PR; return review status
if verification-round limit reached: create human hold
if current report requests revision and no later chunk: start revision
else create verification issue; return verify running
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:688` | for | For each PR targeting the default branch | Checks repository, tracker age and body reference. |
| `.github/bible/bible_queue.py:690` | if | PR is foreign, predates the tracker, or lacks its reference | Skips it. |
| `.github/bible/bible_queue.py:692` | if | Matching PR is merged | Returns `merged`. |
| `.github/bible/bible_queue.py:694` | if | Matching PR is open | Returns its review status. |
| `.github/bible/bible_queue.py:698` | if | An open chunk or verify issue exists | Selects its first issue. |
| `.github/bible/bible_queue.py:701` | if | `held` reports release | Returns released status for the next check. |
| `.github/bible/bible_queue.py:703` | if | Issue remains held | Returns needs-person status. |
| `.github/bible/bible_queue.py:709` | if | No issue for this component exists in any state | Returns `not started`. |
| `.github/bible/bible_queue.py:713` | if | At least one hold issue is open | Checks its human-required label. |
| `.github/bible/bible_queue.py:714` | if | First open hold has `bible-needs-human` | Returns needs-person; otherwise closes the released hold. |
| `.github/bible/bible_queue.py:721` | if | Status state is `COMPONENT_DONE` | Runs or defers the component gate. |
| `.github/bible/bible_queue.py:722` | if | Remaining run time is insufficient for the gate budget | Returns a wait-until-next-check state. |
| `.github/bible/bible_queue.py:725` | if | Gate returned `None` because it could not run | Counts the failure and returns a hold or next-check status. |
| `.github/bible/bible_queue.py:730` | if | Gate did not pass | Applies the bounded chunk-session policy. |
| `.github/bible/bible_queue.py:738` | if | Closed chunks since the reset point reach the computed cap | Creates and returns a human hold. |
| `.github/bible/bible_queue.py:754` | conditional expression | A completed verification exists | Reads its report; otherwise leaves `facts` as `None`. |
| `.github/bible/bible_queue.py:755` | if | Report is a clean `PASS` with matching nonempty fingerprint | Creates the final component PR and returns review status. |
| `.github/bible/bible_queue.py:774` | if | Completed verification count reaches the limit and no later chunk exists | Creates a human hold. |
| `.github/bible/bible_queue.py:783` | if | Current report requests revision and no later chunk exists | Starts a revision chunk and returns `session starting`. |

#### `Queue.follow(analysis, name, issue)`

Source: `.github/bible/bible_queue.py:798-855` <!-- code: 96d8861eb206 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:708`) |
| Calls | `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `str`, `str.startswith`, `os.path.basename`, `shown_files`, `status_of`, `as_int`, `status.get`, `issue.get`, `any`, `gh.file`, `gh.label`, `gh.merge`, `gh.unlabel`, `gh.close` |
| Purpose | Checks an assigned chunk or verification session and its PR, then retries, holds, waits, or validates and merges it. |

**Steps**

1. Sets branch `bible/<name>`, derives `verify` or `chunk` from labels, and classifies the session. Waiting returns `session starting`; start errors are held; no-start retries; running returns `<kind> running`. (`.github/bible/bible_queue.py:799-811`)
2. Defines the component ledger base and requests PR file names. A listing `RuntimeError` is retried/held. Chunk PRs may change component LLD, component API LLD and ledger files except `verification-*`; verification PRs may change only `verification-*` files and `citations.tsv` within the ledger. Disallowed paths are summarized with `shown_files` and retried/held. (`.github/bible/bible_queue.py:812-827`)
3. Reads component status at the PR head SHA. For a chunk at `WAITING_ANSWER`, adds `bible-waiting-answer` to both issue and PR only when the issue lacks it, then returns the wait status. (`.github/bible/bible_queue.py:828-834`)
4. For other chunks, compares `packets_done` at PR head with the branch, recognizes a revision from `"\nRevision ("` in issue body, and treats increased packets or `COMPONENT_DONE` as progress. `STOP` or no progress is retried; a revision must change an allowed page or `revision-log.md` and finish in `COMPONENT_DONE`, or it is retried/held. (`.github/bible/bible_queue.py:835-848`)
5. For verification, retries/holds if the report is absent at the PR head. Otherwise merges the PR, removes the waiting-answer label, closes the issue, and returns `<kind> merged`. (`.github/bible/bible_queue.py:849-855`)

**Pseudo-code**

```text
kind = verify if issue has bible-verify, else chunk
state, pr = session(...)
handle waiting, start-error, no-start and running statuses
check PR file listing and kind-specific allowlist
if bad files: retry or return needs-person
status = component status at PR head
if chunk:
    if WAITING_ANSWER: label issue and PR if needed; return waiting
    compare packet counts; require progress and valid revision output
elif verification report missing at PR head: retry or hold
merge PR; remove waiting-answer label; close issue; return merged status
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:800` | conditional expression | Issue has `bible-verify` | Sets kind to `verify`; otherwise `chunk`. |
| `.github/bible/bible_queue.py:802` | if | Session state is `waiting` | Returns `session starting`. |
| `.github/bible/bible_queue.py:804` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:807` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:809` | conditional expression | Retry succeeds | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:810` | if | Session state is `running` | Returns `<kind> running`. |
| `.github/bible/bible_queue.py:815` | except | `gh.pr_files` raises `RuntimeError` | Retries or holds because the file list cannot be validated. |
| `.github/bible/bible_queue.py:817` | conditional expression | Retry succeeds after a file-list error | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:818` | if | Kind is `chunk` | Selects the chunk allowlist; otherwise selects the verify allowlist. |
| `.github/bible/bible_queue.py:825` | if | Any changed file is outside the selected allowlist | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:827` | conditional expression | Retry succeeds after disallowed files | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:829` | if | Kind is `chunk` | Checks chunk progress; otherwise checks the verification report. |
| `.github/bible/bible_queue.py:830` | if | Status is `WAITING_ANSWER` | Checks whether to add wait labels and returns the wait state. |
| `.github/bible/bible_queue.py:831` | if | Issue lacks `bible-waiting-answer` | Adds the label to issue and PR. |
| `.github/bible/bible_queue.py:838` | if | Status is `STOP` or packet count did not increase and state is not done | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:840` | conditional expression | Retry succeeds after no progress | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:842` | if | Revision has no changed allowed page or revision log | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:845` | conditional expression | Retry succeeds after an unchanged revision | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:846` | if | Revision did not finish in `COMPONENT_DONE` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:848` | conditional expression | Retry succeeds after an incomplete revision | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:849` | elif | Verification report is absent at the PR head SHA | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:851` | conditional expression | Retry succeeds after missing report | Returns starting; otherwise needs-person. |

#### `Queue.check(analysis, name, branch)`

Source: `.github/bible/bible_queue.py:857-882` <!-- code: 4b957b96bfcc -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:724`) |
| Calls | `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `printed.stdout.strip`, `().splitlines`, `run.stdout.strip` |
| Purpose | Runs the component coverage gate against an unpacked branch tarball and obtains its pages fingerprint. |

**Steps**

1. Builds the toolkit scripts directory. If `coverage.py` is absent, logs that the gate is skipped and treated as failing, then returns `(False, None)`. (`.github/bible/bible_queue.py:859-862`)
2. Creates a temporary work directory, downloads and extracts `branch`, then runs isolated `coverage.py` with `--repo`, `--analysis`, configured `--depth`, `--component` and `--report -`. Logs the final stripped output line or `no output`. (`.github/bible/bible_queue.py:863-873`)
3. Runs isolated `status.py --fingerprint --component` in the same work tree and returns `(run.returncode == 0, printed.stdout.strip() or None)`. (`.github/bible/bible_queue.py:874-877`)
4. On `RuntimeError` from tarball retrieval, logs the cause and returns `(None, None)`; on `TimeoutExpired`, logs the timeout and returns `(None, None)`. In either case, `finally` removes the temporary directory while ignoring cleanup errors. (`.github/bible/bible_queue.py:866-869,878-882`)

**Pseudo-code**

```text
if coverage.py is missing: log; return False, None
work = temporary directory
try:
    try: unpack branch tarball; on RuntimeError return None, None
    run coverage.py in isolated Python; log final output line
    run status.py --fingerprint --component
    return coverage succeeded, fingerprint output or None
except subprocess timeout: return None, None
finally: remove work directory, ignoring cleanup errors
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:860` | if | `coverage.py` is not a file | Logs and returns `(False, None)`. |
| `.github/bible/bible_queue.py:867` | except | Tarball retrieval raises `RuntimeError` | Logs the error and returns `(None, None)`; cleanup still runs. |
| `.github/bible/bible_queue.py:878` | except | Either subprocess exceeds `GATE_TIMEOUT` | Logs the timeout and returns `(None, None)`; cleanup still runs. |


#### `Queue.could_not_check(key, what, hold_labels, hold_title)`

Source: `.github/bible/bible_queue.py:884-895` <!-- code: d1918209875f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:726`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:945`) |
| Calls | `as_int`, `self.state.get`, `max`, `self.state.pop`, `self.gh.create_issue` |
| Purpose | Counts consecutive un-runnable checks and opens a human-hold issue after the configured threshold. |

**Steps**

1. Increments `self.state[key]` from the maximum of its existing integer value and zero, so a negative state cannot suppress the count. If the count is below `MAX_NOCHECK`, returns `None`. (`.github/bible/bible_queue.py:887-889`)
2. At the threshold, removes the count, creates a hold issue with tracker number, description, threshold, and the supplied hold labels plus `bible-hold`, `bible-needs-human` and the run label, then returns its issue number in a status string. (`.github/bible/bible_queue.py:890-895`)

**Pseudo-code**

```text
state[key] = max(as_int(state.get(key)), 0) + 1
if count < MAX_NOCHECK: return None
remove count; create labeled hold issue; return needs-person status
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:888` | if | Consecutive count is below `MAX_NOCHECK` | Returns `None` and waits for another check. |

#### `Queue.whole_fingerprint(analysis)`

Source: `.github/bible/bible_queue.py:897-912` <!-- code: c7fe54722506 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:943`) |
| Calls | `os.path.join`, `os.path.isfile`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `os.path.abspath`, `printed.stdout.strip`, `self.log`, `shutil.rmtree` |
| Purpose | Computes the analysis-page fingerprint from the default branch using the toolkit's `status.py`. |

**Steps**

1. Builds the toolkit scripts path and returns `None` if `status.py` is missing. Otherwise creates a temporary work directory and downloads the default-branch tarball. (`.github/bible/bible_queue.py:899-904`)
2. Runs isolated `status.py --fingerprint` for `analysis`, returning stripped stdout or `None` when empty. A tarball `RuntimeError` or process timeout is logged and returns `None`; `finally` removes the temporary tree. (`.github/bible/bible_queue.py:905-912`)

**Pseudo-code**

```text
if status.py missing: return None
work = temporary directory
try:
    unpack default branch
    run status.py --fingerprint
    return stripped output or None
except RuntimeError or timeout: log; return None
finally: remove work tree
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:900` | if | `status.py` is not a file | Returns `None` without creating a work directory. |
| `.github/bible/bible_queue.py:908` | except | Tarball download raises `RuntimeError` or fingerprint process times out | Logs the failure and returns `None`. |

#### `Queue.assemble_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:914-1027` <!-- code: 935f3bc6544e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:644`) |
| Calls | `settings.get`, `self.run_issues`, `i.get`, `self.whole_hold`, `report_facts`, `gh.file`, `max`, `any`, `p.get`, `gh.is_agent_pr`, `gh.pr_files`, `gh.linked_prs`, `bool`, `time.monotonic`, `getattr`, `self.whole_fingerprint`, `self.could_not_check`, `self.state.pop`, `labels_of`, `gh.label`, `gh.comment`, `self.revise_all_step`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `issue_text`, `assignment`, `gh.create_issue`, `self.deferred_updates`, `self.delta`, `sorted`, `set`, `shown_files`, `type`, `str` |
| Purpose | Coordinates assembly and whole-analysis verification, revision and deferred updates, then closes the tracker when all phases finish. |

**Steps**

1. Processes `bible-assemble` then `bible-verify-all`, using the corresponding model, title and optional issue-text file. Completed assembly issues skip assembly. In verify-all, first checks for a whole-run human hold. (`.github/bible/bible_queue.py:912-920,959-960`)
2. For closed verify-all issues, reads report facts from the default branch and picks the newest completed issue. A clean PASS is accepted only when a merged, same-repository, agent-authored PR linked to that issue wrote the identical report and its fingerprint matches the current pages fingerprint. If fingerprint computation cannot run, counts it toward a hold and waits or returns needs-person. (`.github/bible/bible_queue.py:927-951`)
3. If the closed verdict is a stale PASS or not a clean PASS, labels and comments the issue as stale or needing revision when no such label or open verifier issue exists; returns the corresponding status. A completed verify-all phase otherwise advances. (`.github/bible/bible_queue.py:952-964`)
4. Calls `revise_all_step` before opening another verify-all issue. For an open phase issue, searches its linked PRs for a merged same-repository agent PR into the default branch. An unclean verify-all report is labeled for revision and the issue is closed `not_planned`; otherwise it closes and advances (or asks for the next fingerprint check). (`.github/bible/bible_queue.py:965-988`)
5. Without a qualifying merged PR, returns needs-person for a held issue; classifies its session, holds start errors, retries no-start, reports running PRs, and asks `continue_if_unfinished` for unfinished completed sessions. It then returns review instructions or the session state. (`.github/bible/bible_queue.py:989-1003`)
6. With no open issue, loads `assemble.md` or constructs whole-analysis verification instructions, creates and assigns the issue, and returns its assigned status. Once both phases are complete, replays deferred updates before and after closing the tracker; failures on the late replay are commented on the closed tracker with safe filenames, then the method returns `done`. (`.github/bible/bible_queue.py:1004-1027`)

**Pseudo-code**

```text
for assemble and verify-all phase:
    skip completed phases
    before verify-all, handle whole-run human holds and closed verdicts
    accept a report only if clean, written by this run, and current-fingerprint
    request stale verification or revision as appropriate
    call revise_all_step; follow merged/open issue PRs and session states
    if no open issue: load phase text or build verify instructions; assign issue; return
replay deferred updates; comment done; close tracker; replay late changes safely
return done
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:916` | for | The assembly and verify-all phase tuples | Processes phases in order. |
| `.github/bible/bible_queue.py:920` | if | Current phase is verify-all | Checks for a whole-analysis hold first. |
| `.github/bible/bible_queue.py:922` | if | A whole-analysis hold status is returned | Stops and returns it. |
| `.github/bible/bible_queue.py:924` | if | Verify-all has completed closed issues | Validates the newest verdict. |
| `.github/bible/bible_queue.py:940` | if | Report is clean, written by this run, and has a fingerprint | Checks that fingerprint against current pages. |
| `.github/bible/bible_queue.py:941` | if | Remaining run time is insufficient for fingerprint check | Returns a wait-for-next-check status. |
| `.github/bible/bible_queue.py:944` | if | Current fingerprint could not be computed | Counts the failure and returns a hold or wait status. |
| `.github/bible/bible_queue.py:947` | conditional expression | No-check threshold was reached | Prefixes the human-hold status; otherwise returns the retry-at-next-check message. |
| `.github/bible/bible_queue.py:950` | if | Report fingerprint equals current pages fingerprint | Continues to the next phase. |
| `.github/bible/bible_queue.py:952` | if | PASS is stale/unverified, has no prior stale/revision label, and no open verifier issue exists | Labels/comments the issue as stale and returns. |
| `.github/bible/bible_queue.py:958` | if | Report is not clean and no revision label/open verifier exists | Marks the issue for revision and returns. |
| `.github/bible/bible_queue.py:961` | conditional expression | Report facts exist | Includes the report verdict in the issue comment; otherwise uses `missing`. |
| `.github/bible/bible_queue.py:962` | return | A completed verdict needs revision | Returns the corrections-requested status. |
| `.github/bible/bible_queue.py:963` | elif | A completed assembly issue exists | Skips assembly. |
| `.github/bible/bible_queue.py:965` | if | Current phase is verify-all | Runs whole-analysis revision handling. |
| `.github/bible/bible_queue.py:967` | if | Revision handler returned a status | Returns it. |
| `.github/bible/bible_queue.py:970` | if | An open issue exists for the phase | Follows its linked PR/session. |
| `.github/bible/bible_queue.py:974` | if | A qualifying merged PR exists | Closes or advances the phase. |
| `.github/bible/bible_queue.py:975` | if | The merged PR belongs to verify-all | Reads and validates the whole-analysis report. |
| `.github/bible/bible_queue.py:977` | if | Report missing, not PASS, or has major corrections | Marks the issue for revision and closes it as not planned. |
| `.github/bible/bible_queue.py:982` | conditional expression | Report facts exist | Reports the verdict; otherwise reports `missing`. |
| `.github/bible/bible_queue.py:984` | return | A merged verify-all report needs revision | Returns the corrections-requested status. |
| `.github/bible/bible_queue.py:986` | if | A merged verify-all PR passed basic report checks | Returns that fingerprint is checked on the next queue check. |
| `.github/bible/bible_queue.py:989` | if | Open issue is held | Returns needs-person status. |
| `.github/bible/bible_queue.py:992` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:995` | if | Session state is `no-start` | Requests retry. |
| `.github/bible/bible_queue.py:997` | if | PR exists and session is running | Returns running with PR number. |
| `.github/bible/bible_queue.py:999` | if | PR exists and session is finished | Checks for a missing completion marker. |
| `.github/bible/bible_queue.py:1001` | if | Continuation helper returns a status | Returns that status. |
| `.github/bible/bible_queue.py:1003` | conditional expression | PR exists | Returns PR review instruction; otherwise returns session state. |
| `.github/bible/bible_queue.py:1004` | if | Phase has an issue-text filename | Loads its title and body; otherwise builds verification instructions. |
| `.github/bible/bible_queue.py:1016` | if | Deferred changed paths exist | Creates delta issues before closing the tracker. |
| `.github/bible/bible_queue.py:1021` | if | New deferred paths arrived after the first replay | Attempts late replay after closing the tracker. |
| `.github/bible/bible_queue.py:1024` | except | Late replay raises `Exception` | Comments a manual-update notice with bounded error and safe path list. |

#### `Queue.deferred_updates(tracker)`

Source: `.github/bible/bible_queue.py:1029-1041` <!-- code: faad993a4a62 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1015`, `.github/bible/bible_queue.py:1020`) |
| Calls | `self.gh.me`, `self.gh.timeline`, `re.findall`, `e.get`, `actor.get`, `json.loads`, `isinstance`, `SAFE_FILE.match`, `sorted`, `set` |
| Purpose | Collects unique safe paths from this queue account's deferred-update comments on the tracker. |

**Steps**

1. Gets the current GitHub login and scans the tracker timeline. Ignores events that are not comments or whose actor/login is not the current account. (`.github/bible/bible_queue.py:1031-1034`)
2. Finds every `<!-- bible-deferred-update [...] -->` JSON list in each matching comment. Adds only string paths matching `SAFE_FILE`; malformed JSON is skipped. Returns a sorted list of unique paths. (`.github/bible/bible_queue.py:1035-1041`)

**Pseudo-code**

```text
for tracker event:
    skip unless comment by current queue login
    for each matching deferred-update JSON list:
        add safe string paths; skip malformed JSON
return sorted unique paths
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1032` | for | For each tracker timeline event | Extracts the actor and checks whether the queue authored a comment. |
| `.github/bible/bible_queue.py:1034` | if | Event is not a comment or actor login differs | Skips that event. |
| `.github/bible/bible_queue.py:1036` | for | Each embedded deferred-update marker | Parses its JSON list and filters the values. |
| `.github/bible/bible_queue.py:1039` | except | The embedded JSON is invalid | Ignores that marker and continues. |

#### `Queue.whole_hold()`

Source: `.github/bible/bible_queue.py:1043-1049` <!-- code: 6ba23ffaa54f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:921`) |
| Calls | `self.run_issues`, `labels_of`, `self.gh.close` |
| Purpose | Reports an active human hold for the whole analysis and closes holds whose human-required label was removed. |

**Steps**

1. Iterates open issues labeled `bible-hold` and `bible-whole`. If an issue has `bible-needs-human`, returns a status containing its issue number; otherwise closes it, then continues. Returns `None` if no active hold remains. (`.github/bible/bible_queue.py:1045-1049`)

**Pseudo-code**

```text
for open whole-analysis hold:
    if needs-human label: return status with issue number
    close released hold
return None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1045` | for | For each open whole-analysis hold | Checks whether it still needs a person. |
| `.github/bible/bible_queue.py:1046` | if | Hold has `bible-needs-human` | Returns the needs-person status; otherwise closes the released hold. |

#### `Queue.revise_all_step(tracker, analysis)`

Source: `.github/bible/bible_queue.py:1051-1129` <!-- code: 86a6e2d30283 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:966`) |
| Calls | `self.run_issues`, `h.get`, `labels_of`, `gh.close`, `max`, `sorted`, `i.get`, `len`, `self.held`, `gh.linked_prs`, `p.get`, `gh.is_agent_pr`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `gh.pr_files`, `str.startswith`, `os.path.basename`, `shown_files`, `bool`, `any`, `gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Applies a whole-analysis revision round after correction verdicts, including released holds, finished PRs, bounded retries and a final human hold. |

**Steps**

1. Loads all whole-run holds and identifies open ones. Returns needs-person when the first still has `bible-needs-human`; otherwise closes it and reloads holds. Uses the latest hold close time as the start of the current round. (`.github/bible/bible_queue.py:1056-1063`)
2. Finds closed whole-verification issues labeled needs-revision and stale-verdict. If there are no correction verdicts and stale rounds remain below `MAX_VERIFY_ROUNDS`, returns `None`; otherwise counts correction/stale rounds since the last release and finds revision issues. (`.github/bible/bible_queue.py:1066-1075`)
3. For an open revision issue, closes and returns when a qualifying linked agent PR is already merged. Otherwise a held issue returns needs-person; start-error is held, no-start requests retry, running returns its PR status, and a finished PR is passed to `continue_if_unfinished`, which may ask Copilot to continue or hold the issue for a person (also at once when Copilot's work failed before it started). (`.github/bible/bible_queue.py:1076-1097`)
4. A finished revision PR may change only files under `analysis/` whose basename does not start `verification-`; disallowed files are summarized and retried/held. If no revision is open, it decides whether corrections are already applied, creates a human hold at `MAX_VERIFY_ROUNDS`, or creates and assigns a revision issue carrying the verification-report instructions. (`.github/bible/bible_queue.py:1098-1129`)

**Pseudo-code**

```text
close released hold or return human-needed
find correction/stale verdicts since latest release and count rounds
if open revision: follow merged, held, start-error, no-start, running and finished session states
    require finished PR files under analysis, excluding verification-*; retry/hold if invalid
if revision followed latest verdict or no correction remains: return None
if rounds exhausted: create human hold
otherwise create and assign revision issue
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1058` | if | An open hold exists | Checks whether the person label remains. |
| `.github/bible/bible_queue.py:1059` | if | Open hold has `bible-needs-human` | Returns needs-person; otherwise closes it and refreshes holds. |
| `.github/bible/bible_queue.py:1070` | if | No correction verdict exists and stale rounds are below the limit | Returns `None`. |
| `.github/bible/bible_queue.py:1076` | if | An open revision issue exists | Follows its PR/session. |
| `.github/bible/bible_queue.py:1080` | if | A qualifying linked agent PR is merged | Closes the revision issue and returns `None`. |
| `.github/bible/bible_queue.py:1083` | if | Revision issue is held | Returns needs-person. |
| `.github/bible/bible_queue.py:1086` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:1089` | if | Session state is `no-start` | Requests retry and returns session starting. |
| `.github/bible/bible_queue.py:1092` | if | PR exists and session is running | Returns the running status. |
| `.github/bible/bible_queue.py:1094` | if | PR exists and session is finished | Checks for continuation and file-scope violations. |
| `.github/bible/bible_queue.py:1096` | if | Continuation helper returns a status | Returns it. |
| `.github/bible/bible_queue.py:1100` | if | Finished PR includes a file outside `analysis/` or a `verification-*` basename | Retries or holds. |
| `.github/bible/bible_queue.py:1103` | conditional expression | Retry succeeds | Returns session starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:1104` | conditional expression | PR exists | Returns review/merge instruction; otherwise the session state. |
| `.github/bible/bible_queue.py:1105` | conditional expression | A correction verdict exists | Uses the latest correction close time; otherwise uses an empty string. |
| `.github/bible/bible_queue.py:1109` | if | Round limit is reached and revision work is already complete or stale verdict is newer | Proceeds to human-hold handling. |
| `.github/bible/bible_queue.py:1111` | elif | No correction remains, a revision completed, or stale verdict is newer | Returns `None` so verification can proceed. |
| `.github/bible/bible_queue.py:1113` | if | Verification rounds reached `MAX_VERIFY_ROUNDS` | Creates and returns a whole-analysis human hold. |

#### `Queue.continue_if_unfinished(issue, pr, kind, analysis)`

Source: `.github/bible/bible_queue.py:1131-1181` <!-- code: 7a8cd9573644 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1000`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1095`) |
| Calls | `gh.pr_files`, `gh.me`, `max`, `e.get`, `gh.timeline`, `get`, `sorted`, `labels_of`, `gh.label`, `gh.comment`, `age`, `len`, `self.settings.get` |
| Purpose | For a session that ended before its end marker was written: holds the issue for a person at once when Copilot failed before starting, otherwise asks Copilot to continue on the same pull request, up to `MAX_CONTINUE` times. |

**Steps**

1. Chooses the end marker: `<analysis>/verification-report.md` when `kind` is `bible-verify-all`, otherwise `<analysis>/status.json`; returns `None` when the pull request's files already include it. (`.github/bible/bible_queue.py:1139-1141`)
2. Reads the queue's own login (`gh.me()`), then `released`: the latest `unlabeled` timeline event on the issue for the label `bible-needs-human`, or the empty string. (`.github/bible/bible_queue.py:1142-1144`)
3. Reads the pull request's timeline and builds `work`, the `(event, created_at)` pairs for events in `WORK_EVENTS` performed by the `AGENT_APP` app; `finished` is the latest timestamp among those that are not `copilot_work_started` (a failure counts). (`.github/bible/bible_queue.py:1145-1148`, `.github/bible/bible_queue.py:69`)
4. `asked` is the sorted timestamps of `commented` events by the queue's login that contain `CONTINUE_MARK` and are newer than `released`; anyone else's copy of the marker text is not counted. `after` is the names of the work events, in time order, that are newer than the last such comment (empty when nothing was asked). (`.github/bible/bible_queue.py:1149-1152`, `.github/bible/bible_queue.py:83`)
5. New early hold: when the last event after the request is `copilot_work_finished_failure` and no `copilot_work_started` is among the events after it, Copilot did not run at all. If the issue does not carry `bible-needs-human` yet, labels it and comments the likely causes (the account's Copilot AI credits or monthly budget, Copilot turned off for the repository) and tells a person to fix the cause and remove the label; returns `"<kind>: Copilot could not start: see #<issue>"` without using up another continuation. (`.github/bible/bible_queue.py:1153-1162`)
6. When a request exists, is newer than `finished` and is not older than `NO_PR_AFTER` (30 minutes), returns `"<kind>: continuing (pull request #<n>)"`: Copilot has been asked and has not picked it up yet. (`.github/bible/bible_queue.py:1163-1164`, `.github/bible/bible_queue.py:72`)
7. When `len(asked) >= MAX_CONTINUE` (3), labels the issue `bible-needs-human` and comments the count and the marker, unless the label is already there; returns `"<kind>: needs a person: see #<issue>"`. (`.github/bible/bible_queue.py:1165-1171`, `.github/bible/bible_queue.py:82`)
8. Otherwise comments on the pull request `@copilot continue: run next.py ... --new-session` with `--depth` from `settings["depth"]` (default `deep`) and an ending that depends on `kind` (assemble, revise-all or verify-all), followed by `CONTINUE_MARK`; returns `"<kind>: continuing, session <len(asked)+2> (pull request #<n>)"`. (`.github/bible/bible_queue.py:1172-1181`)

**Pseudo-code**

```text
marker = verification-report.md if kind == bible-verify-all else status.json   (under analysis)
if marker in files of the pull request: return None
released = latest time a person removed bible-needs-human from the issue
work     = timeline events of the pull request in WORK_EVENTS by Copilot's app
finished = latest work event that is not copilot_work_started
asked    = queue's own bible-continue comments newer than released
after    = work events newer than the last such comment
if after ends with copilot_work_finished_failure and has no copilot_work_started:
    label the issue bible-needs-human and comment why (once)
    return "Copilot could not start"
if asked and last request is newer than finished and younger than NO_PR_AFTER:
    return "continuing"                      # asked, Copilot has not started yet
if len(asked) >= MAX_CONTINUE:
    label the issue bible-needs-human and comment (once)
    return "needs a person"
comment "@copilot continue: ..." on the pull request, ending with CONTINUE_MARK
return "continuing, session N"
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1139` | conditional expression | `kind` is `bible-verify-all` | the marker is `verification-report.md`; otherwise `status.json` |
| `.github/bible/bible_queue.py:1140` | if | the marker is among the pull request's files | returns `None`: the work is done |
| `.github/bible/bible_queue.py:1153` | if | the last event after the latest request is `copilot_work_finished_failure` and none of the events after it is `copilot_work_started` | Copilot never started: enters the early hold |
| `.github/bible/bible_queue.py:1155` | if | the issue does not have `bible-needs-human` | labels it and posts the failed-before-start comment; with the label present only the return happens |
| `.github/bible/bible_queue.py:1163` | if | a request exists, is newer than the last finished event and is at most `NO_PR_AFTER` old | returns continuing (asked, not started) |
| `.github/bible/bible_queue.py:1165` | if | `MAX_CONTINUE` requests have been made since the last release | enters the hold for a person |
| `.github/bible/bible_queue.py:1166` | if | the issue does not have `bible-needs-human` | labels it and posts the count comment; with the label present only the return happens |

**Output and side effects**: returns `None` or a one-line status string; may add the label `bible-needs-human` and a comment on the issue (early hold, or limit reached), or a `@copilot continue` comment on the pull request. The `[kind]` dictionary lookup raises `KeyError` for a kind other than the three listed (`.github/bible/bible_queue.py:1176-1179`).

#### `Queue.render(tracker, settings, rows)`

Source: `.github/bible/bible_queue.py:1183-1194` <!-- code: bc302114ec7d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:614`, `.github/bible/bible_queue.py:621`, `.github/bible/bible_queue.py:645`), `Queue.plan_phase` (`.github/bible/bible_queue.py:658`, `.github/bible/bible_queue.py:661`, `.github/bible/bible_queue.py:665`, `.github/bible/bible_queue.py:668`) |
| Calls | `rows.items`, `json.dumps`, `getattr`, `now`, `().isoformat`, `join`, `body.split`, `tracker.get`, `self.gh.set_body`, `self.log` |
| Purpose | Builds tracker status rows with hidden state/settings markers, updates the body when its non-time content changes, and logs each row. |

**Steps**

1. Builds a fixed introduction and table header, then appends one formatted component/state row per `rows.items()`. (`.github/bible/bible_queue.py:1184-1186`)
2. Adds a hidden `bible-state` JSON comment from `self.state` (or `{}`), an `Updated` timestamp to minute precision, and a hidden `bible-settings` JSON comment; joins the lines with newlines. (`.github/bible/bible_queue.py:1187-1190`)
3. Compares each body's text before `Updated`; calls `set_body` only when that prefix differs. It then logs each row with a 20-character padded key. (`.github/bible/bible_queue.py:1191-1194`)

**Pseudo-code**

```text
lines = introduction + table header + rows
append hidden bible-state JSON from self.state, timestamp, and hidden bible-settings JSON
body = join lines with newline
if body prefix before "Updated" differs from existing body prefix:
    set tracker body
for each row: log padded key and state
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1191` | if | Text before `Updated` differs | Replaces the tracker body. |
| `.github/bible/bible_queue.py:1193` | for | For each `(key, value)` row | Logs the padded key and state. |

#### `Queue.delta(changed, settings_analysis="codebase-analysis", record=True)`

Source: `.github/bible/bible_queue.py:1197-1257` <!-- code: 48ca17e0332c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1304`) |
| Calls | `gh.default_branch`, `UPDATED.search`, `t.get`, `found.group`, `gh.issues`, `age`, `last_activity`, `range`, `max`, `len`, `SAFE_FILE.match`, `gh.comment`, `json.dumps`, `json_file`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `components.component_map`, `sorted`, `p.startswith`, `NAME.match`, `gh.create_issue`, `comp_label`, `assignment`, `components.assign` |
| Purpose | Defers changed paths onto an active tracker, or opens bounded component-update issues when the assembled analysis and baseline are available. |

**Steps**

1. Sets the default branch and defines `last_activity` from the tracker body's `Updated` marker or its creation time. With `record=True`, finds active tracker issues updated within `ABANDONED_AFTER`; with `record=False`, does not search for one. (`.github/bible/bible_queue.py:1198-1203`)
2. If a tracker is active, filters changed paths through `SAFE_FILE`, splits safe paths into `DEFERRED_PER_COMMENT` chunks (at least one loop iteration), posts a marker comment for each chunk, notes omitted unusual names, logs the deferral, and returns. (`.github/bible/bible_queue.py:1204-1216`)
3. Otherwise loads `components.json` and requires `ledger/baseline.json`; if either is absent, logs and returns. Adds the analysis toolkit scripts to `sys.path`, imports `components`, maps changed paths outside the analysis and skills directories to sorted touched component names, and filters them through `NAME`. (`.github/bible/bible_queue.py:1217-1228`)
4. If the number of touched components exceeds `MAX_DELTA_ISSUES`, creates one human-needed issue only when none is already open, logs and returns. For each touched component, gets the assigned files and safe display names; an existing component delta issue is logged and skipped. Otherwise creates an assigned issue with up to 20 shown file paths and the update instructions, then logs the file count. (`.github/bible/bible_queue.py:1229-1257`)

**Pseudo-code**

```text
default = gh.default_branch()
if record: find active tracker based on its Updated marker/created_at
if active tracker:
    comment with chunked safe changed paths; return
catalog = components.json
if catalog or baseline is absent: log; return
map changes outside analysis and skills directories to valid component names
if touched component count exceeds MAX_DELTA_ISSUES:
    create one human-needed issue if absent; return
for each touched component:
    if matching delta issue exists: log; continue
    create assigned update issue with paths and instructions; log
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1202` | conditional expression | An `Updated` marker matched | Uses the marker time; otherwise uses tracker creation time. |
| `.github/bible/bible_queue.py:1203` | conditional expression | `record` is true | Finds recently active trackers; otherwise uses an empty list. |
| `.github/bible/bible_queue.py:1204` | if | An active tracker exists | Records changes in a comment on its first issue and returns. |
| `.github/bible/bible_queue.py:1208` | for | Safe paths are chunked for comments | Posts each chunk; an empty safe list still enters one iteration. |
| `.github/bible/bible_queue.py:1212` | conditional expression | First chunk has unusual-name paths | Adds their count to the comment; otherwise adds no warning. |
| `.github/bible/bible_queue.py:1218` | if | Catalog or baseline is absent | Logs and returns without creating issues. |
| `.github/bible/bible_queue.py:1229` | if | Touched component count exceeds `MAX_DELTA_ISSUES` | Routes the change to human review and returns. |
| `.github/bible/bible_queue.py:1231` | if | No `bible-delta`/`bible-needs-human` issue exists | Creates the shared human-needed issue. |
| `.github/bible/bible_queue.py:1239` | for | For each valid touched component | Selects its changed files and issues. |
| `.github/bible/bible_queue.py:1244` | if | A component delta issue is already open | Logs and skips a duplicate. |
| `.github/bible/bible_queue.py:1254` | conditional expression | A file has an unusual name | Adds a count of hidden paths; otherwise no suffix is added. |

## Functions and methods

### `main()`

Source: `.github/bible/bible_queue.py:1260-1306` <!-- code: d5e645d7911f -->

| | |
| --- | --- |
| Kind | module entry point |
| Called by | Module guard (`.github/bible/bible_queue.py:1309-1310`) |
| Calls | `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str`, `args.verify_model.strip`, `args.components.split`, `json.dumps`, `issue.get`, `open`, `l.strip`, `NAME.match` |
| Purpose | Parses `start`, `reconcile`, and `delta` commands and dispatches to the queue workflow. |

**Steps**

1. Builds a required-subcommand parser from the module docstring's first line; defines `start` options including `--analysis` and `--depth`, `reconcile`, and `delta` options, then parses arguments. (`.github/bible/bible_queue.py:1261-1274`)
2. Reads `GITHUB_REPOSITORY` and `GH_TOKEN`; raises `SystemExit` if either is falsey, then constructs `GitHub` and `Queue`. (`.github/bible/bible_queue.py:1276-1280`)
3. For `start`, requires a nonempty verification model different from the normal model, parses component names, and requires at least one selection with each name either `all` or matching `NAME`. (`.github/bible/bible_queue.py:1282-1287`)
4. Ensures labels and exits if a tracker is already open. Builds settings, then calls `settings_of` on the generated marker; if validation rejects the settings, raises `SystemExit` explaining the allowed analysis path, depth, and model characters. Otherwise it creates a tracker issue with hidden settings JSON and prints its issue number and queue-start guidance. (`.github/bible/bible_queue.py:1288-1298`)
5. For `reconcile`, invokes `queue.reconcile`; otherwise reads nonempty stripped lines from the changed-file input and calls `queue.delta`. (`.github/bible/bible_queue.py:1299-1304`)
6. Converts `RuntimeError` from command handling to `SystemExit` with the error text. (`.github/bible/bible_queue.py:1305-1306`)

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
| `.github/bible/bible_queue.py:1277` | if | Repository or token is missing | Exits with an environment requirement. |
| `.github/bible/bible_queue.py:1278` | raise | Required environment is missing | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1282` | if | Command is `start` | Validates and starts a run. |
| `.github/bible/bible_queue.py:1283` | if | Verification model is empty or equals normal model | Exits with the model requirement. |
| `.github/bible/bible_queue.py:1284` | raise | Model validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1286` | if | No component names are supplied, or a name other than `all` fails `NAME` | Exits with component-selection guidance. |
| `.github/bible/bible_queue.py:1287` | raise | Selection validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1289` | if | Tracker already exists | Exits without starting another run. |
| `.github/bible/bible_queue.py:1290` | raise | Open tracker exists | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1293` | if | Generated settings fail `settings_of` validation | Exits with the settings requirement. |
| `.github/bible/bible_queue.py:1294-1295` | raise | Generated settings are unsafe or unsupported | Raises `SystemExit` with allowed path, depth, and model rules. |
| `.github/bible/bible_queue.py:1299` | elif | Command is `reconcile` | Calls `queue.reconcile`. |
| `.github/bible/bible_queue.py:1301` | else | Command is `delta` | Reads changed paths and calls `queue.delta`. |
| `.github/bible/bible_queue.py:1305` | except | Command handling raises `RuntimeError` | Converts it to `SystemExit`. |
| `.github/bible/bible_queue.py:1306` | raise | A `RuntimeError` was caught | Raises `SystemExit` with the error text. |
| `.github/bible/bible_queue.py:1309` | if | Module is run as a script | Calls `main`. |
| `.github/bible/bible_queue.py:1310` | call | Script guard is active | Dispatches the CLI entry point. |

### `now()`

Source: `.github/bible/bible_queue.py:356-358` <!-- code: 9fb56903ebfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `age` (`.github/bible/bible_queue.py:362`), `Queue.render` (`.github/bible/bible_queue.py:1188`) |
| Calls | `os.environ.get`, `datetime.datetime.fromisoformat`, `datetime.datetime.now`, `replace` |
| Purpose | Returns the configured test time or the current UTC time. |

**Steps**

1. Reads `BIBLE_NOW`. (`.github/bible/bible_queue.py:357`)
2. If set, replaces `Z` with `+00:00` and parses the ISO timestamp; otherwise returns the current timezone-aware UTC datetime. (`.github/bible/bible_queue.py:358`)

**Pseudo-code**

```text
stamp = BIBLE_NOW
if stamp: parse ISO stamp after replacing Z with +00:00
else: return current UTC time
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:358` | conditional expression | `stamp` is truthy | Parses the configured time; otherwise obtains current UTC time. |

### `age(stamp)`

Source: `.github/bible/bible_queue.py:361-362` <!-- code: f2f8bb65e56f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:500`, `.github/bible/bible_queue.py:504`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1163`), `Queue.delta` (`.github/bible/bible_queue.py:1203`) |
| Calls | `now`, `datetime.datetime.fromisoformat`, `replace`, `total_seconds` |
| Purpose | Returns elapsed seconds between `stamp` and `now()`. |

**Steps**

1. Replaces `Z` in `stamp` with `+00:00`, parses it as an ISO datetime, subtracts it from `now()`, and returns `total_seconds()`. (`.github/bible/bible_queue.py:362`)

**Pseudo-code**

```text
return (now() - parse ISO stamp after replacing Z with +00:00).total_seconds()
```

### `shown_files(paths, limit=10)`

Source: `.github/bible/bible_queue.py:374-379` <!-- code: 42118ce2fbc4 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:826`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1026`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1102`) |
| Calls | `SAFE_FILE.match`, `len`, `join` |
| Purpose | Formats safe paths for issue text and summarizes paths with unusual characters without quoting them. |

**Steps**

1. Partitions `paths` into names matching `SAFE_FILE` and the count that do not. Formats at most `limit` safe names in backticks, appending a count for additional safe names and a separate count for unusual names. (`.github/bible/bible_queue.py:375-379`)

**Pseudo-code**

```text
plain = paths matching SAFE_FILE
other = len(paths) - len(plain)
return quoted first limit names + counts of remaining safe and unusual names
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:378` | conditional expression | More safe names exist than `limit` | Adds the number of omitted safe names; otherwise adds nothing. |
| `.github/bible/bible_queue.py:379` | conditional expression | At least one path has unusual characters | Adds the count without including those paths; otherwise adds nothing. |

### `settings_of(tracker)`

Source: `.github/bible/bible_queue.py:382-402` <!-- code: 828d76009663 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:585`), `main` (`.github/bible/bible_queue.py:1293`) |
| Calls | `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group`, `isinstance`, `str`, `data.get`, `SAFE_PATH.match`, `analysis.split`, `SAFE_MODEL.match` |
| Purpose | Parses and validates the JSON settings marker from a tracker, returning `None` when absent, malformed, or unsafe. |

**Steps**

1. Searches the tracker body, defaulting a missing or falsey body to an empty string, and parses the marker's first capture group when present. (`.github/bible/bible_queue.py:388-389`)
2. Returns `None` for invalid JSON or a non-dictionary parsed value. (`.github/bible/bible_queue.py:390-391`)
3. Reads `analysis`, defaulting to `codebase-analysis`, and rejects paths that fail `SAFE_PATH` or contain `..` path segments. (`.github/bible/bible_queue.py:392-394`)
4. Rejects depths outside `DEPTH_VALUES`, and rejects nonempty `model` or `verify_model` values that fail `SAFE_MODEL`. (`.github/bible/bible_queue.py:395-400`)
5. Returns the validated settings dictionary. (`.github/bible/bible_queue.py:402`)

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
| `.github/bible/bible_queue.py:388` | conditional expression | A settings marker matched | Parses its first group; otherwise uses `None`. |
| `.github/bible/bible_queue.py:389` | except | JSON parsing raises `ValueError` | Returns `None`. |
| `.github/bible/bible_queue.py:391` | if | Parsed value is not a dictionary | Returns `None`. |
| `.github/bible/bible_queue.py:394` | if | Analysis path is unsafe | Returns `None`. |
| `.github/bible/bible_queue.py:396` | if | Depth is not an allowed value | Returns `None`. |
| `.github/bible/bible_queue.py:398` | for | For `model` and `verify_model` | Validates each configured model value. |
| `.github/bible/bible_queue.py:400` | if | A nonempty model fails `SAFE_MODEL` | Returns `None`. |

### `labels_of(item)`

Source: `.github/bible/bible_queue.py:405-406` <!-- code: 7a809f2b23af -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `item.get`, `isinstance` |
| Purpose | Returns a set of label names from strings or label objects. |

**Steps**

1. Reads `labels`, defaulting to an empty list; for each element, uses its `name` when it is a dictionary and otherwise keeps the element itself. (`.github/bible/bible_queue.py:406`)

**Pseudo-code**

```text
return {label["name"] if label is a dict else label
        for label in item.labels or []}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:406` | conditional expression | A label item is a dict | Uses `item["name"]`; otherwise preserves the item value. |

### `comp_label(name)`

Source: `.github/bible/bible_queue.py:409-410` <!-- code: 5ead08c5004d -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Prefixes a component name with `bible/`. |

**Steps**

1. Returns the string `bible/` followed by `name`. (`.github/bible/bible_queue.py:410`)

**Pseudo-code**

```text
return "bible/" + name
```

### `issue_text(gh, path, ref, fallback_title)`

Source: `.github/bible/bible_queue.py:413-419` <!-- code: 0533b3261be5 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `gh.file`, `splitlines`, `startswith`, `strip`, `join`, `len` |
| Purpose | Reads a title/body pair from a ledger issue file, with a fallback title when no header exists. |

**Steps**

1. Reads the file through `gh.file`, converting a falsey result to `""`, then splits it into lines. (`.github/bible/bible_queue.py:415-416`)
2. If the first line starts with `Title:`, returns its stripped suffix as the title and the stripped remaining lines joined by newlines as the body. (`.github/bible/bible_queue.py:417-418`)
3. Otherwise returns `fallback_title` and the stripped full text. (`.github/bible/bible_queue.py:419`)

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
| `.github/bible/bible_queue.py:417` | if | `lines` is nonempty and the first line starts with `Title:` | Returns header title and remaining body; otherwise returns fallback title and full text. |

### `assignment(gh, base, model)`

Source: `.github/bible/bible_queue.py:422-426` <!-- code: da5ca422ae7f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | None |
| Purpose | Builds the target repository and base-branch assignment, optionally including a model. |

**Steps**

1. Initializes the result with `target_repo: gh.repo` and `base_branch: base`. (`.github/bible/bible_queue.py:423`)
2. Adds `model` only when truthy, then returns the result. (`.github/bible/bible_queue.py:424-426`)

**Pseudo-code**

```text
out = {target_repo: gh.repo, base_branch: base}
if model: out.model = model
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:424` | if | `model` is truthy | Adds `model` to the assignment. |

### `json_file(gh, path, ref)`

Source: `.github/bible/bible_queue.py:429-434` <!-- code: 37acfbecddfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `status_of` (`.github/bible/bible_queue.py:471`), queue functions in later source packets. |
| Calls | `gh.file`, `json.loads` |
| Purpose | Reads a file and parses JSON, returning `None` for missing or invalid content. |

**Steps**

1. Reads the file using `gh.file`. (`.github/bible/bible_queue.py:430`)
2. Returns parsed JSON for truthy text, or `None` when the text is falsey. (`.github/bible/bible_queue.py:431-432`)
3. Returns `None` if parsing raises `ValueError`. (`.github/bible/bible_queue.py:433-434`)

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
| `.github/bible/bible_queue.py:432` | conditional expression | `text` is truthy | Parses JSON; otherwise returns `None`. |
| `.github/bible/bible_queue.py:433` | except | JSON parsing raises `ValueError` | Returns `None`. |

### `section(text, title)`

Source: `.github/bible/bible_queue.py:437-443` <!-- code: 55167fd6e3c2 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `report_facts` (`.github/bible/bible_queue.py:456`), queue functions in later source packets. |
| Calls | `re.search`, `re.escape`, `match.end`, `nxt.start` |
| Purpose | Returns a Markdown level-two section's text, or an empty string if its heading is absent. |

**Steps**

1. Searches for a line matching exactly a level-two heading with the escaped `title`. (`.github/bible/bible_queue.py:438`)
2. Returns `""` if no heading matches. (`.github/bible/bible_queue.py:439-440`)
3. Slices text after the matched heading through the next level-two heading, or through end of text when there is no next heading. (`.github/bible/bible_queue.py:441-443`)

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
| `.github/bible/bible_queue.py:439` | if | No heading matched | Returns an empty string. |
| `.github/bible/bible_queue.py:443` | conditional expression | A next level-two heading matched | Returns the section before it; otherwise returns the remaining text. |

### `report_facts(text)`

Source: `.github/bible/bible_queue.py:446-459` <!-- code: a367c151c5b0 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `re.sub`, `re.findall`, `len`, `sum`, `splitlines`, `startswith`, `re.search`, `section`, `lstrip`, `upper`, `printed.group` |
| Purpose | Extracts a verification verdict, major-correction count, and optional analysis fingerprint. |

**Steps**

1. Returns `None` for falsey `text`. (`.github/bible/bible_queue.py:449-450`)
2. Removes HTML comments and fenced code blocks, then finds visible `Verdict` values and rows. (`.github/bible/bible_queue.py:451-453`)
3. Returns `("UNREADABLE", 0, None)` unless exactly one accepted verdict and exactly one verdict row were found. (`.github/bible/bible_queue.py:454-455`)
4. Counts lines in the `Corrections` section that begin with `|` and contain a `major` cell. (`.github/bible/bible_queue.py:456-457`)
5. Searches for a 16-character lowercase hexadecimal fingerprint and returns the uppercased verdict, count, and captured fingerprint or `None`. (`.github/bible/bible_queue.py:458-459`)

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
| `.github/bible/bible_queue.py:449` | if | `text` is falsey | Returns `None`. |
| `.github/bible/bible_queue.py:454` | if | Verdict or verdict-row count is not exactly one | Returns `("UNREADABLE", 0, None)`. |
| `.github/bible/bible_queue.py:459` | conditional expression | Fingerprint regex matched | Returns its group 1; otherwise returns `None` in that tuple position. |

### `as_int(value)`

Source: `.github/bible/bible_queue.py:462-466` <!-- code: bc184bba1eba -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `int` |
| Purpose | Converts a value to an integer, returning zero for conversion type, value or overflow errors. |

**Steps**

1. Returns `int(value)` when conversion succeeds; catches `TypeError`, `ValueError` or `OverflowError` and returns `0`. (`.github/bible/bible_queue.py:463-466`)

**Pseudo-code**

```text
try: return int(value)
on TypeError, ValueError or OverflowError: return 0
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:465` | except | `int(value)` raises `TypeError`, `ValueError` or `OverflowError` | Returns zero. |

### `status_of(gh, path, ref)`

Source: `.github/bible/bible_queue.py:469-472` <!-- code: ad9adb38e0f7 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | Queue functions in later source packets. |
| Calls | `json_file`, `isinstance` |
| Purpose | Returns parsed component status only when the loaded JSON is a dictionary. |

**Steps**

1. Loads `path` at `ref` with `json_file`. (`.github/bible/bible_queue.py:471`)
2. Returns the loaded data if it is a dictionary; otherwise returns `{}`. (`.github/bible/bible_queue.py:472`)

**Pseudo-code**

```text
data = json_file(gh, path, ref)
return data if data is a dict, otherwise {}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:472` | conditional expression | `data` is a dictionary | Returns `data`; otherwise returns `{}`. |

## Module-level code

The module imports Python standard-library utilities and initializes queue labels, environment-derived agent settings, regexes, and timing/verification constants. (`.github/bible/bible_queue.py:42-103`). The tuple `WORK_EVENTS` lists the timeline events that count as Copilot's work: `copilot_work_started`, `copilot_work_finished` and `copilot_work_finished_failure` (`.github/bible/bible_queue.py:69`).

It declares the `GitHub` API client (`.github/bible/bible_queue.py:108-351`), helper functions (`.github/bible/bible_queue.py:356-472`), and `Queue` coordinator (`.github/bible/bible_queue.py:477-1257`). The CLI `main` parses arguments, and the module guard calls it when executed as a script. (`.github/bible/bible_queue.py:1260-1310`)

## Surprises

`tarball` limits download/member sizes, filters archive members to regular files and directories, and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:272-307`)

The `Queue.session` docstring lists four result states, but the code also returns `start-error` when `GitHub.start_error` is truthy. (`.github/bible/bible_queue.py:495`, `.github/bible/bible_queue.py:498-499`)

`Queue.component` builds `closed_revise` after a human hold but does not use it later in the method; it separately builds and uses `all_revise`. (`.github/bible/bible_queue.py:641-645`, `.github/bible/bible_queue.py:759-765`)

<!-- cites .github/bible/bible_queue.py@161344dc7ddde551f4020972e6d61c782a86d480 -->
