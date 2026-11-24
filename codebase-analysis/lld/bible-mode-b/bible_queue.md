---
id: lld/bible-mode-b/bible_queue
kind: module
component: bible-mode-b
source: .github/bible/bible_queue.py
summary: Coordinates Mode B issue workflows through GitHub REST and GraphQL
reads: [file:changed-path-list, config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
writes: [file:temporary-gate-workspace]
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
| Lines | 1336 |
| Role | Runs the Mode B analysis queue and its GitHub API client. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, subprocess, and filesystem modules used by the API client, queue, and CLI. (`.github/bible/bible_queue.py:42-56`) |
| Module-level state | Constants and labels are initialized at import; environment-backed values include `BIBLE_AGENT_LOGINS` and `BIBLE_AGENT_APP`; `WORK_EVENTS` names the three Copilot timeline events the queue reads (`copilot_work_started`, `copilot_work_finished`, `copilot_work_finished_failure`). `COMPARE_MAX` (300) is the number of files GitHub's comparison of two commits lists at most (line 71's comment); the queue refuses a comparison that lists 300 files or more, so it accepts fewer than 300. (`.github/bible/bible_queue.py:60-105`, `.github/bible/bible_queue.py:61`, `.github/bible/bible_queue.py:66`, `.github/bible/bible_queue.py:70`, `.github/bible/bible_queue.py:71`) |

## Summary

`main` exposes the `start`, `reconcile`, and `delta` CLI commands. It constructs `Queue` and `GitHub`; `Queue` coordinates tracker/session state and delegates repository operations to `GitHub`, whose methods build REST requests and a GraphQL ready-for-review mutation. `Queue.delta` also imports component-membership helpers from the analysis toolkit. (`.github/bible/bible_queue.py:1286-1332`, `.github/bible/bible_queue.py:500-1283`, `.github/bible/bible_queue.py:110-374`, `.github/bible/bible_queue.py:1247-1248`)

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| `GitHub` | class | 110-374 | [class](#github) |
| `GitHub.__init__` | method | 111-114 | [card](#github__init__repo-token-apinone) |
| `GitHub.request` | method | 116-125 | [card](#githubrequestmethod-url-bodynone-timeout60) |
| `GitHub.call` | method | 127-139 | [card](#githubcallmethod-path-bodynone-ok404false) |
| `GitHub.paged` | method | 141-149 | [card](#githubpagedpath) |
| `GitHub.issues` | method | 151-153 | [card](#githubissueslabels-stateopen) |
| `GitHub.ensure_label` | method | 155-160 | [card](#githubensure_labelname-whycodebase-analysis-run) |
| `GitHub.ensure_labels` | method | 162-164 | [card](#githubensure_labels) |
| `GitHub.create_issue` | method | 166-173 | [card](#githubcreate_issuetitle-body-labels-assignnone) |
| `GitHub.me` | method | 175-179 | [card](#githubme) |
| `GitHub.default_branch` | method | 181-182 | [card](#githubdefault_branch) |
| `GitHub.branch_sha` | method | 184-186 | [card](#githubbranch_shabranch) |
| `GitHub.create_branch` | method | 188-189 | [card](#githubcreate_branchbranch-sha) |
| `GitHub.reset_branch` | method | 191-192 | [card](#githubreset_branchbranch-sha) |
| `GitHub.file` | method | 194-198 | [card](#githubfilepath-ref) |
| `GitHub.prs` | method | 200-202 | [card](#githubprsbasenone-stateopen) |
| `GitHub.timeline` | method | 204-205 | [card](#githubtimelinenumber) |
| `GitHub.linked_prs` | method | 207-216 | [card](#githublinked_prsnumber) |
| `GitHub.branch_prs` | method | 218-221 | [card](#githubbranch_prsbranch-base) |
| `GitHub.agent_events` | method | 223-227 | [card](#githubagent_eventsnumber) |
| `GitHub.is_agent_pr` | method | 229-234 | [card](#githubis_agent_prpr) |
| `GitHub.start_error` | method | 236-245 | [card](#githubstart_errorissue) |
| `GitHub.assigned_at` | method | 247-250 | [card](#githubassigned_atissue) |
| `GitHub.pr_files` | method | 252-286 | [card](#githubpr_filesnumber) |
| `GitHub.commit_time` | method | 288-289 | [card](#githubcommit_timesha) |
| `GitHub.tarball` | method | 291-330 | [card](#githubtarballref-dest) |
| `GitHub.label` | method | 332-334 | [card](#githublabelnumber-name) |
| `GitHub.unlabel` | method | 336-337 | [card](#githubunlabelnumber-name) |
| `GitHub.comment` | method | 339-340 | [card](#githubcommentnumber-text) |
| `GitHub.close` | method | 342-343 | [card](#githubclosenumber-reasoncompleted) |
| `GitHub.set_body` | method | 345-346 | [card](#githubset_bodynumber-body) |
| `GitHub.unassign` | method | 348-349 | [card](#githubunassignnumber) |
| `GitHub.assign` | method | 351-352 | [card](#githubassignnumber-assign) |
| `GitHub.ready` | method | 354-362 | [card](#githubreadypr) |
| `GitHub.merge` | method | 364-368 | [card](#githubmergepr-title) |
| `GitHub.close_pr` | method | 370-371 | [card](#githubclose_prnumber) |
| `GitHub.create_pr` | method | 373-374 | [card](#githubcreate_prhead-base-title-body) |
| `now` | function | 379-381 | [card](#now) |
| `age` | function | 384-385 | [card](#agestamp) |
| `shown_files` | function | 397-402 | [card](#shown_filespaths-limit10) |
| `settings_of` | function | 405-425 | [card](#settings_oftracker) |
| `labels_of` | function | 428-429 | [card](#labels_ofitem) |
| `comp_label` | function | 432-433 | [card](#comp_labelname) |
| `issue_text` | function | 436-442 | [card](#issue_textgh-path-ref-fallback_title) |
| `assignment` | function | 445-449 | [card](#assignmentgh-base-model) |
| `json_file` | function | 452-457 | [card](#json_filegh-path-ref) |
| `section` | function | 460-466 | [card](#sectiontext-title) |
| `report_facts` | function | 469-482 | [card](#report_factstext) |
| `as_int` | function | 485-489 | [card](#as_intvalue) |
| `status_of` | function | 492-495 | [card](#status_ofgh-path-ref) |
| `Queue` | class | 500-1283 | [class](#queue) |
| `Queue.__init__` | method | 501-503 | [card](#queue__init__gh-logprint) |
| `Queue.run_issues` | method | 505-506 | [card](#queuerun_issueslabels-stateopen) |
| `Queue.agent_pr` | method | 508-514 | [card](#queueagent_prissue-base) |
| `Queue.session` | method | 517-533 | [card](#queuesessionissue-base-analysis-compnone) |
| `Queue.held` | method | 535-568 | [card](#queueheldissue) |
| `Queue.model_for` | method | 570-572 | [card](#queuemodel_forissue) |
| `Queue.hold_start_error` | method | 574-580 | [card](#queuehold_start_errorissue) |
| `Queue.fail_or_retry` | method | 582-601 | [card](#queuefail_or_retryissue-pr-why) |
| `Queue.reconcile` | method | 604-615 | [card](#queuereconcile) |
| `Queue.run` | method | 617-668 | [card](#queueruntracker-settings) |
| `Queue.plan_phase` | method | 670-692 | [card](#queueplan_phasetracker-settings-analysis) |
| `Queue.start_chunk` | method | 694-706 | [card](#queuestart_chunkanalysis-name-freshfalse-note) |
| `Queue.component` | method | 708-819 | [card](#queuecomponentanalysis-name) |
| `Queue.follow` | method | 821-878 | [card](#queuefollowanalysis-name-issue) |
| `Queue.check` | method | 880-905 | [card](#queuecheckanalysis-name-branch) |
| `Queue.could_not_check` | method | 907-918 | [card](#queuecould_not_checkkey-what-hold_labels-hold_title) |
| `Queue.whole_fingerprint` | method | 920-935 | [card](#queuewhole_fingerprintanalysis) |
| `Queue.assemble_phase` | method | 937-1050 | [card](#queueassemble_phasetracker-settings-analysis) |
| `Queue.deferred_updates` | method | 1052-1064 | [card](#queuedeferred_updatestracker) |
| `Queue.whole_hold` | method | 1066-1072 | [card](#queuewhole_hold) |
| `Queue.revise_all_step` | method | 1074-1152 | [card](#queuerevise_all_steptracker-analysis) |
| `Queue.continue_if_unfinished` | method | 1154-1207 | [card](#queuecontinue_if_unfinishedissue-pr-kind-analysis) |
| `Queue.render` | method | 1209-1220 | [card](#queuerendertracker-settings-rows) |
| `Queue.delta` | method | 1223-1283 | [card](#queuedeltachanged-settings_analysiscodebase-analysis-recordtrue) |
| `main` | function | 1286-1332 | [card](#main) |

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
  assemblephase -->|"assignment"| assignment
  assemblephase -->|"close"| close
  assemblephase -->|"comment"| comment
  assemblephase -->|"create_issue"| createissue
  assemblephase -->|"file"| file
  assemblephase -->|"hold_start_error"| holdstarterror
  assemblephase -->|"is_agent_pr"| isagent
  assemblephase -->|"linked_prs"| linked
  assign -->|"call"| call
  branchprs -->|"paged"| paged
  branchsha -->|"call"| call
  close -->|"call"| call
  closepr -->|"call"| call
  comment -->|"call"| call
  committime -->|"call"| call
  component -->|"assignment"| assignment
  component -->|"close"| close
  component -->|"create_issue"| createissue
  component -->|"create_pr"| createpr
  component -->|"file"| file
  component -->|"held"| held
  component -->|"labels_of"| labelsof
  component -->|"start_chunk"| startchunk
  createbranch -->|"call"| call
  createissue -->|"call"| call
  createpr -->|"call"| call
  defaultbranch -->|"call"| call
  delta -->|"create_issue"| createissue
  delta -->|"default_branch"| defaultbranch
  delta -->|"issues"| issues
  ensurelabel -->|"call"| call
  ensurelabel -->|"paged"| paged
  failorretry -->|"assignment"| assignment
  failorretry -->|"close"| close
  failorretry -->|"close_pr"| closepr
  failorretry -->|"comment"| comment
  failorretry -->|"create_issue"| createissue
  failorretry -->|"label"| label
  failorretry -->|"unassign"| unassign
  file -->|"call"| call
  follow -->|"close"| close
  follow -->|"file"| file
  follow -->|"hold_start_error"| holdstarterror
  follow -->|"label"| label
  follow -->|"merge"| merge
  follow -->|"pr_files"| prfiles
  follow -->|"unlabel"| unlabel
  held -->|"assign"| assign
  held -->|"comment"| comment
  held -->|"set_body"| setbody
  holdstarterror -->|"comment"| comment
  holdstarterror -->|"label"| label
  holdstarterror -->|"unassign"| unassign
  issuetext -->|"file"| file
  issues -->|"paged"| paged
  jsonfile -->|"file"| file
  label -->|"call"| call
  main -->|"issues"| issues
  planphase -->|"assignment"| assignment
  planphase -->|"create_issue"| createissue
  planphase -->|"render"| render
  prfiles -->|"paged"| paged
  prs -->|"paged"| paged
  reconcile -->|"default_branch"| defaultbranch
  reconcile -->|"issues"| issues
  render -->|"set_body"| setbody
  resetbranch -->|"call"| call
  run -->|"close"| close
  run -->|"render"| render
  run -->|"run_issues"| runissues
  runissues -->|"issues"| issues
  session -->|"agent_events"| agentevents
  session -->|"assigned_at"| assigned
  session -->|"commit_time"| committime
  session -->|"start_error"| starterror
  session -->|"status_of"| statusof
  setbody -->|"call"| call
  startchunk -->|"assignment"| assignment
  startchunk -->|"create_branch"| createbranch
  startchunk -->|"create_issue"| createissue
  startchunk -->|"reset_branch"| resetbranch
  startchunk -->|"run_issues"| runissues
  tarball -->|"request"| request
  timeline -->|"paged"| paged
  unassign -->|"call"| call
  unlabel -->|"call"| call
  assemblephase -->|"pr_files"| prfiles
  deferredupdates -->|"me"| me
  deferredupdates -->|"timeline"| timeline
  delta -->|"age"| age
  delta -->|"comment"| comment
  prfiles -->|"branch_sha"| branchsha
```

## Classes

### `GitHub`

Source: `.github/bible/bible_queue.py:110-374`

`GitHub` is a client for repository-scoped GitHub REST operations and the GraphQL ready-for-review mutation. Its instance fields are `repo`, `token`, normalized `api`, and `known_labels`; the last begins as `None` and is populated by `ensure_label`. A fifth field, `_me`, is not set in the constructor: `me` creates it on its first call (`getattr(self, "_me", None)`) and caches the login of the token's owner. (`.github/bible/bible_queue.py:111-114`, `.github/bible/bible_queue.py:155-160`, `.github/bible/bible_queue.py:175-179`) Since 24 Nov 2026 `pr_files` also uses the comparison endpoint (`/compare/<base tip>...<head>`) for an open pull request whose base branch has moved, and `is_agent_pr` accepts any of the three `WORK_EVENTS` as proof that a pull request is Copilot's. (`.github/bible/bible_queue.py:229-234`, `.github/bible/bible_queue.py:252-286`)

No type annotations or factory are declared for the class; callers provide its constructor values. (inferred: `.github/bible/bible_queue.py:110-114`)

#### `GitHub.__init__(repo, token, api=None)`

Source: `.github/bible/bible_queue.py:111-114` <!-- code: b511658beb68 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1305`) |
| Calls | `os.environ.get`, `rstrip` |
| Purpose | Stores API credentials and a slash-trimmed API base URL, then initializes the label cache. |

**Steps**

1. Assigns `repo` and `token` to the instance. (`.github/bible/bible_queue.py:112`)
2. Selects `api`, then `GITHUB_API_URL`, then `https://api.github.com`, and removes trailing `/` characters. (`.github/bible/bible_queue.py:113`)
3. Initializes `known_labels` to `None`. (`.github/bible/bible_queue.py:114`)

**Pseudo-code**

```text
self.repo, self.token = repo, token
self.api = (api or GITHUB_API_URL or "https://api.github.com").rstrip("/")
self.known_labels = None
```

#### `GitHub.request(method, url, body=None, timeout=60)`

Source: `.github/bible/bible_queue.py:116-125` <!-- code: 1f8902892005 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.call` (`.github/bible/bible_queue.py:130`), `GitHub.tarball` (`.github/bible/bible_queue.py:297`), `GitHub.ready` (`.github/bible/bible_queue.py:359`) |
| Calls | `json.dumps`, `encode`, `urllib.request.Request`, `req.add_header`, `urllib.request.urlopen` |
| Purpose | Builds and opens an HTTP request with GitHub headers and an optional JSON body. |

**Steps**

1. Serializes a non-`None` body as encoded JSON; otherwise leaves request data unset. (`.github/bible/bible_queue.py:117`)
2. Creates a request using the supplied URL, method, and body bytes, and adds GitHub's JSON accept and API-version headers. (`.github/bible/bible_queue.py:118-120`)
3. Adds a bearer authorization header only when `token` is truthy, and adds JSON content type only when a body was serialized. (`.github/bible/bible_queue.py:121-124`)
4. Returns `urlopen`'s response using the supplied timeout. (`.github/bible/bible_queue.py:125`)

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
| `.github/bible/bible_queue.py:117` | conditional expression | `body is not None` | JSON is encoded; otherwise `data` is `None`. |
| `.github/bible/bible_queue.py:121` | if | `self.token` is truthy | Adds the bearer authorization header. |
| `.github/bible/bible_queue.py:123` | if | `data is not None` | Adds the JSON content-type header. |

#### `GitHub.call(method, path, body=None, ok404=False)`

Source: `.github/bible/bible_queue.py:127-139` <!-- code: 753c5f1a3922 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.paged` (`.github/bible/bible_queue.py:145`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:159`), `GitHub.create_issue` (`.github/bible/bible_queue.py:173`), `GitHub.me` (`.github/bible/bible_queue.py:178`), `GitHub.default_branch` (`.github/bible/bible_queue.py:182`), `GitHub.branch_sha` (`.github/bible/bible_queue.py:185`), `GitHub.create_branch` (`.github/bible/bible_queue.py:189`), `GitHub.reset_branch` (`.github/bible/bible_queue.py:192`), `GitHub.file` (`.github/bible/bible_queue.py:195`), `GitHub.linked_prs` (`.github/bible/bible_queue.py:215`), `GitHub.pr_files` (`.github/bible/bible_queue.py:255`, `.github/bible/bible_queue.py:265`), `GitHub.commit_time` (`.github/bible/bible_queue.py:289`), `GitHub.label` (`.github/bible/bible_queue.py:334`), `GitHub.unlabel` (`.github/bible/bible_queue.py:337`), `GitHub.comment` (`.github/bible/bible_queue.py:340`), `GitHub.close` (`.github/bible/bible_queue.py:343`), `GitHub.set_body` (`.github/bible/bible_queue.py:346`), `GitHub.unassign` (`.github/bible/bible_queue.py:349`), `GitHub.assign` (`.github/bible/bible_queue.py:352`), `GitHub.merge` (`.github/bible/bible_queue.py:368`), `GitHub.close_pr` (`.github/bible/bible_queue.py:371`), `GitHub.create_pr` (`.github/bible/bible_queue.py:374`) |
| Calls | `path.startswith`, `GitHub.request`, response `read`, `json.loads`, `RuntimeError` |
| Purpose | Sends a REST request and converts response data and common request failures to Python values or a `RuntimeError`. |

**Steps**

1. Uses an absolute `path` beginning with `http` as-is; otherwise joins the API base, `/repos/`, repository, and path. (`.github/bible/bible_queue.py:128`)
2. Opens the request and reads its response bytes. (`.github/bible/bible_queue.py:129-131`)
3. On HTTP 404 with `ok404`, returns `None`; otherwise reads the whole error body, decodes it, keeps its first 300 characters and raises a method/path/status/detail `RuntimeError`. (`.github/bible/bible_queue.py:132-136`)
4. Converts `URLError`, `TimeoutError`, and `OSError` to a `RuntimeError` containing the method, query-stripped path, and error. (`.github/bible/bible_queue.py:137-138`)
5. Decodes a nonempty payload as JSON; returns `{}` for an empty payload. (`.github/bible/bible_queue.py:139`)

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
| `.github/bible/bible_queue.py:128` | conditional expression | `path.startswith("http")` | Uses `path`; otherwise constructs a repository API URL. |
| `.github/bible/bible_queue.py:132` | except | Request raises `urllib.error.HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:133` | if | Status is 404 and `ok404` is true | Returns `None`. |
| `.github/bible/bible_queue.py:136` | raise | Other HTTP errors | Raises `RuntimeError` with method, path, status, and detail. |
| `.github/bible/bible_queue.py:137` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Enters network error handling. |
| `.github/bible/bible_queue.py:138` | raise | A listed network error occurred | Raises `RuntimeError` with method, path, and error. |
| `.github/bible/bible_queue.py:139` | conditional expression | Payload is nonempty | Decodes JSON; otherwise returns `{}`. |

#### `GitHub.paged(path)`

Source: `.github/bible/bible_queue.py:141-149` <!-- code: 1bb6c1899527 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.issues` (`.github/bible/bible_queue.py:153`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:157`), `GitHub.prs` (`.github/bible/bible_queue.py:202`), `GitHub.timeline` (`.github/bible/bible_queue.py:205`), `GitHub.branch_prs` (`.github/bible/bible_queue.py:221`), `GitHub.pr_files` (`.github/bible/bible_queue.py:276`) |
| Calls | `GitHub.call`, `len` |
| Purpose | Fetches successive pages of up to 100 results and returns their concatenation. |

**Steps**

1. Starts with an empty result and page number 1. (`.github/bible/bible_queue.py:142`)
2. Chooses `&` if `path` already contains `?`, otherwise `?`, then requests `per_page=100` and the current page with GET. (`.github/bible/bible_queue.py:143-145`)
3. Appends each batch; returns the accumulated list when a batch has fewer than 100 entries, otherwise increments the page and repeats. (`.github/bible/bible_queue.py:146-149`)

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
| `.github/bible/bible_queue.py:143` | while | Always | Repeats page requests until a short batch is returned. |
| `.github/bible/bible_queue.py:144` | conditional expression | `path` contains `?` | Chooses `&`; otherwise chooses `?`. |
| `.github/bible/bible_queue.py:147` | if | Batch length is less than 100 | Returns all accumulated entries; otherwise proceeds to the next page. |

#### `GitHub.issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:151-153` <!-- code: b3f969457f25 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run_issues` (`.github/bible/bible_queue.py:506`), `Queue.reconcile` (`.github/bible/bible_queue.py:607`), `Queue.delta` (`.github/bible/bible_queue.py:1229`, `.github/bible/bible_queue.py:1257`, `.github/bible/bible_queue.py:1270`), `main` (`.github/bible/bible_queue.py:1315`) |
| Calls | `urllib.parse.quote`, `join`, `GitHub.paged` |
| Purpose | Lists issues for encoded labels and a state, excluding pull requests. |

**Steps**

1. Joins labels with commas and URL-quotes the result. (`.github/bible/bible_queue.py:152`)
2. Pages `/issues` with the requested state and labels query, then keeps only objects without a `pull_request` key. (`.github/bible/bible_queue.py:153`)

**Pseudo-code**

```text
q = URL-quote(comma-joined labels)
return paged issues for state and q, excluding pull request objects
```

#### `GitHub.ensure_label(name, why="Codebase analysis run")`

Source: `.github/bible/bible_queue.py:155-160` <!-- code: c80387a5616e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.ensure_labels` (`.github/bible/bible_queue.py:164`), `GitHub.create_issue` (`.github/bible/bible_queue.py:168`), `GitHub.label` (`.github/bible/bible_queue.py:333`) |
| Calls | `GitHub.paged`, `GitHub.call`, `known_labels.add` |
| Purpose | Loads the known-label set on first use and creates a requested label if it is absent. |

**Steps**

1. If `known_labels` is `None`, pages `/labels` and caches their names. (`.github/bible/bible_queue.py:156-157`)
2. If `name` is missing, posts a label with the fixed color `5319e7` and `why` truncated to 100 characters, then adds the name to the cache. (`.github/bible/bible_queue.py:158-160`)

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
| `.github/bible/bible_queue.py:156` | if | `known_labels` is `None` | Fetches and caches current label names. |
| `.github/bible/bible_queue.py:158` | if | `name` is not in the cache | Creates the label and adds its name to the cache. |

#### `GitHub.ensure_labels()`

Source: `.github/bible/bible_queue.py:162-164` <!-- code: 3233fadcc4c0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1314`) |
| Calls | `LABELS.items`, `GitHub.ensure_label` |
| Purpose | Ensures each label defined in the module's `LABELS` mapping exists. |

**Steps**

1. Iterates each `(name, why)` pair in `LABELS` and invokes `ensure_label`. (`.github/bible/bible_queue.py:163-164`)

**Pseudo-code**

```text
for name, why in LABELS:
    ensure_label(name, why)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:163` | for | For each `(name, why)` in `LABELS.items()` | Calls `ensure_label` once for that pair. |

#### `GitHub.create_issue(title, body, labels, assign=None)`

Source: `.github/bible/bible_queue.py:166-173` <!-- code: c0db4afc186c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:599`), `Queue.plan_phase` (`.github/bible/bible_queue.py:679`), `Queue.start_chunk` (`.github/bible/bible_queue.py:705`), `Queue.component` (`.github/bible/bible_queue.py:764`, `.github/bible/bible_queue.py:798`, `.github/bible/bible_queue.py:811`), `Queue.could_not_check` (`.github/bible/bible_queue.py:914`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1033`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1137`, `.github/bible/bible_queue.py:1150`), `Queue.delta` (`.github/bible/bible_queue.py:1258`, `.github/bible/bible_queue.py:1273`), `main` (`.github/bible/bible_queue.py:1322`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures labels, optionally configures agent assignment, and creates an issue. |

**Steps**

1. Ensures every requested label, using its `LABELS` description or `Codebase analysis run` as the fallback. (`.github/bible/bible_queue.py:167-168`)
2. Builds a payload containing `title`, `body`, and `labels`; if `assign` is not `None`, adds the Copilot assignee and `agent_assignment`. (`.github/bible/bible_queue.py:169-172`)
3. Posts the payload to `/issues` and returns the result of `call`. (`.github/bible/bible_queue.py:173`)

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
| `.github/bible/bible_queue.py:167` | for | For each requested label | Calls `ensure_label` with its mapped or fallback description. |
| `.github/bible/bible_queue.py:170` | if | `assign` is not `None` | Adds `COPILOT` and the assignment value to the payload. |

#### `GitHub.me()`

Source: `.github/bible/bible_queue.py:175-179` <!-- code: 6c567c6be9c4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.deferred_updates` (`.github/bible/bible_queue.py:1054`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1165`) |
| Calls | `getattr`, `GitHub.call`, `get` |
| Purpose | Lazily fetches and caches the token owner's login. |

**Steps**

1. If `_me` is not already truthy, GETs the API `/user` URL and stores its `login`, defaulting to an empty string when the response is falsey or has no login. (`.github/bible/bible_queue.py:177-178`)
2. Returns the cached `_me` value. (`.github/bible/bible_queue.py:179`)

**Pseudo-code**

```text
if _me is falsey: _me = GET api/user.login or ""
return _me
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:177` | if | `_me` is falsey or absent | Fetches and caches the token owner's login. |

#### `GitHub.default_branch()`

Source: `.github/bible/bible_queue.py:181-182` <!-- code: 4eb167486c4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:606`), `Queue.delta` (`.github/bible/bible_queue.py:1225`) |
| Calls | `GitHub.call` |
| Purpose | Returns the repository's `default_branch` value. |

**Steps**

1. Gets the repository resource at the empty path and returns its `default_branch` field. (`.github/bible/bible_queue.py:182`)

**Pseudo-code**

```text
return GET repository["default_branch"]
```

#### `GitHub.branch_sha(branch)`

Source: `.github/bible/bible_queue.py:184-186` <!-- code: 446defb234bd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.pr_files` (`.github/bible/bible_queue.py:258`), `Queue.start_chunk` (`.github/bible/bible_queue.py:697`, `.github/bible/bible_queue.py:698`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Returns a branch reference's object SHA or `None` when the reference is absent. |

**Steps**

1. Quotes `branch` and gets its head reference with `ok404=True`. (`.github/bible/bible_queue.py:185`)
2. Returns `ref["object"]["sha"]` if a reference was returned, otherwise `None`. (`.github/bible/bible_queue.py:186`)

**Pseudo-code**

```text
ref = GET quoted branch reference, allowing 404
return ref.object.sha if ref else None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:186` | conditional expression | A reference was returned | Returns its object SHA; otherwise returns `None`. |

#### `GitHub.create_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:188-189` <!-- code: b860758c1ca1 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:699`) |
| Calls | `GitHub.call` |
| Purpose | Creates a Git reference for a branch at a supplied SHA. |

**Steps**

1. Posts `ref: "refs/heads/" + branch` and `sha` to `/git/refs`. (`.github/bible/bible_queue.py:189`)

**Pseudo-code**

```text
POST /git/refs with ref "refs/heads/" + branch and sha
```

#### `GitHub.reset_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:191-192` <!-- code: 43e383793681 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:701`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Force-updates a branch reference to a supplied SHA. |

**Steps**

1. Quotes `branch` and PATCHes its head reference with the supplied SHA and `force: True`. (`.github/bible/bible_queue.py:192`)

**Pseudo-code**

```text
PATCH quoted head reference with sha and force=True
```

#### `GitHub.file(path, ref)`

Source: `.github/bible/bible_queue.py:194-198` <!-- code: e383f7bd9e38 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `issue_text` (`.github/bible/bible_queue.py:438`), `json_file` (`.github/bible/bible_queue.py:453`), `Queue.component` (`.github/bible/bible_queue.py:777`), `Queue.follow` (`.github/bible/bible_queue.py:872`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:950`, `.github/bible/bible_queue.py:956`, `.github/bible/bible_queue.py:960`, `.github/bible/bible_queue.py:999`), `Queue.delta` (`.github/bible/bible_queue.py:1244`) |
| Calls | `GitHub.call`, `urllib.parse.quote`, `isinstance`, `base64.b64decode`, `decode` |
| Purpose | Retrieves and decodes a text file from a repository reference. |

**Steps**

1. Quotes `path` and `ref` and GETs the contents endpoint with `ok404=True`. (`.github/bible/bible_queue.py:195`)
2. Returns `None` for a falsey response, a list response, or a response without `content`. (`.github/bible/bible_queue.py:196-197`)
3. Base64-decodes the content and decodes UTF-8 with replacement for invalid bytes. (`.github/bible/bible_queue.py:198`)

**Pseudo-code**

```text
got = GET quoted contents path at quoted ref, allowing 404
if got is falsey, a list, or lacks content: return None
return base64-decode content, then UTF-8 decode with replacement
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:196` | if | Response is falsey, a list, or has no `content` | Returns `None`. |

#### `GitHub.prs(base=None, state="open")`

Source: `.github/bible/bible_queue.py:200-202` <!-- code: e46dcb273277 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site found; unused (inferred: search for `.prs(` in `.github/bible/bible_queue.py` returned no matches). |
| Calls | `urllib.parse.quote`, `GitHub.paged` |
| Purpose | Lists pull requests by state and optional base branch. |

**Steps**

1. Builds `/pulls?state=<state>` and appends a URL-quoted base query only when `base` is truthy. (`.github/bible/bible_queue.py:201`)
2. Returns the paged results. (`.github/bible/bible_queue.py:202`)

**Pseudo-code**

```text
path = /pulls?state=state
if base is truthy: append quoted base query
return paged(path)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:201` | conditional expression | `base` is truthy | Appends `&base=` and the quoted base; otherwise appends nothing. |

#### `GitHub.timeline(number)`

Source: `.github/bible/bible_queue.py:204-205` <!-- code: 6df4539072ff -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.linked_prs` (`.github/bible/bible_queue.py:210`), `GitHub.agent_events` (`.github/bible/bible_queue.py:225`), `GitHub.start_error` (`.github/bible/bible_queue.py:239`), `GitHub.assigned_at` (`.github/bible/bible_queue.py:249`), `Queue.held` (`.github/bible/bible_queue.py:547`), `Queue.deferred_updates` (`.github/bible/bible_queue.py:1055`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1166`, `.github/bible/bible_queue.py:1168`) |
| Calls | `GitHub.paged` |
| Purpose | Returns all paged timeline events for an issue number. |

**Steps**

1. Pages `/issues/<number>/timeline` and returns the result. (`.github/bible/bible_queue.py:205`)

**Pseudo-code**

```text
return paged /issues/<number>/timeline
```

#### `GitHub.linked_prs(number)`

Source: `.github/bible/bible_queue.py:207-216` <!-- code: 91e30cd14abd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:510`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:961`, `.github/bible/bible_queue.py:995`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1101`) |
| Calls | `GitHub.timeline`, `get`, `append`, `GitHub.call`, `sorted`, `set` |
| Purpose | Finds existing pull requests in this repository cross-referenced from an issue. |

**Steps**

1. Iterates the issue timeline and reads each event's source issue, defaulting missing source/repository values as shown. (`.github/bible/bible_queue.py:209-212`)
2. Collects the source number only for `cross-referenced` events whose source has a `pull_request` and whose repository full name equals this client's repository. (`.github/bible/bible_queue.py:213-214`)
3. Deduplicates and sorts numbers, GETs each pull request with `ok404=True`, and returns only non-`None` results. (`.github/bible/bible_queue.py:215-216`)

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
| `.github/bible/bible_queue.py:210` | for | For each issue timeline event | Inspects its source issue. |
| `.github/bible/bible_queue.py:213` | if | Event is a same-repository cross-reference with a pull request | Appends its source number. |

#### `GitHub.branch_prs(branch, base)`

Source: `.github/bible/bible_queue.py:218-221` <!-- code: fa42118d7d5a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:711`, `.github/bible/bible_queue.py:754`) |
| Calls | `split`, `GitHub.paged`, `urllib.parse.quote` |
| Purpose | Lists all-state pull requests from this repository's branch into a specified base. |

**Steps**

1. Takes the owner portion before `/` in `repo`. (`.github/bible/bible_queue.py:220`)
2. Pages `/pulls` with `state=all`, quoted `owner:branch` as `head`, and quoted `base`. (`.github/bible/bible_queue.py:221`)

**Pseudo-code**

```text
owner = first segment of repo
return paged /pulls with state=all, head=quoted(owner + ":" + branch), base=quoted(base)
```

#### `GitHub.agent_events(number)`

Source: `.github/bible/bible_queue.py:223-227` <!-- code: 1e123ab3f131 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.is_agent_pr` (`.github/bible/bible_queue.py:234`), `Queue.session` (`.github/bible/bible_queue.py:524`) |
| Calls | `GitHub.timeline`, `get` |
| Purpose | Returns the timeline events GitHub records as performed by Copilot's app and named in `WORK_EVENTS` (work started, work finished, work finished with failure) as `(event, timestamp)` pairs. |

**Steps**

1. Reads the pull request's timeline with `self.timeline(number)` and builds one `(event, created_at)` pair per kept event, defaulting a missing `created_at` to the empty string. (`.github/bible/bible_queue.py:225`)
2. Keeps only events whose `performed_via_github_app.slug` equals `AGENT_APP` (default `copilot-swe-agent`, from the environment variable `BIBLE_AGENT_APP`). (`.github/bible/bible_queue.py:226`, `.github/bible/bible_queue.py:66`)
3. Keeps only events whose name is in `WORK_EVENTS`: `copilot_work_started`, `copilot_work_finished` or `copilot_work_finished_failure`. The failure event is the new member, so a session that ended in failure now shows up in the list. (`.github/bible/bible_queue.py:227`, `.github/bible/bible_queue.py:70`)

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
| `.github/bible/bible_queue.py:226` | comprehension filter | the event's app slug is not `AGENT_APP`, or it has no app | the event is left out |
| `.github/bible/bible_queue.py:227` | comprehension filter | the event name is not in `WORK_EVENTS` | the event is left out |

**Output and side effects**: returns a list of `(event, created_at)` pairs in timeline order; no writes. `Queue.session` sorts it by timestamp and reads the newest pair (`.github/bible/bible_queue.py:526`); `GitHub.is_agent_pr` only tests that the list is not empty, so any of the three `WORK_EVENTS` counts (`.github/bible/bible_queue.py:234`).

#### `GitHub.is_agent_pr(pr)`

Source: `.github/bible/bible_queue.py:229-234` <!-- code: 399d25734d4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:512`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:957`, `.github/bible/bible_queue.py:996`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1102`) |
| Calls | `get`, `GitHub.agent_events`, `bool` |
| Purpose | Tests whether a pull request is Copilot's: opened by a configured agent login on a Bot account, or carrying any Copilot work event that GitHub recorded on its timeline. |

**Steps**

1. Reads `pr["user"]`, defaulting to an empty dictionary. (`.github/bible/bible_queue.py:231`)
2. Returns `True` at once when its login (default empty string) is in `AGENT_LOGINS` and its type (default `"Bot"`) is `"Bot"`: a person cannot take an agent's name on a Bot account. (`.github/bible/bible_queue.py:232-233`)
3. Otherwise calls `agent_events` for the pull request's number and returns whether that list is nonempty. Any event of `WORK_EVENTS` (`copilot_work_started`, `copilot_work_finished` or `copilot_work_finished_failure`) performed via `AGENT_APP` counts, not only `copilot_work_started`; this is the change that lets a pull request on which Copilot only failed (or only finished) still be recognised as Copilot's. (`.github/bible/bible_queue.py:234`, `.github/bible/bible_queue.py:70`)

**Pseudo-code**

```text
user = pr.user or {}
if user.login in AGENT_LOGINS and user.type (default Bot) == Bot: return True
return bool(agent_events(pr.number))      # any WORK_EVENTS member by the agent app
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:232` | if | The user's login is in `AGENT_LOGINS` and the user's type is `"Bot"` | Returns `True` without reading the timeline. |
| `.github/bible/bible_queue.py:234` | return | Any other user | Returns whether the pull request's timeline holds at least one agent work event; no event gives `False`. A failing timeline call raises the `RuntimeError` of `GitHub.call`. |

#### `GitHub.start_error(issue)`

Source: `.github/bible/bible_queue.py:236-245` <!-- code: 0287983c593a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:521`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:576`) |
| Calls | `GitHub.assigned_at`, `GitHub.timeline`, `get`, `START_ERROR.search`, `splitlines`, `strip` |
| Purpose | Returns the first matching agent start-error comment since the last assignment, or `None`. |

**Steps**

1. Gets the last assignment time using `assigned_at`, then scans the issue timeline. (`.github/bible/bible_queue.py:238-239`)
2. Chooses `actor` or `user`, then uses the actor login only when the actor type defaults to or is `"Bot"`. (`.github/bible/bible_queue.py:240-241`)
3. Requires a `commented` event by a configured agent at or after the assignment time and a body matching `START_ERROR`. (`.github/bible/bible_queue.py:242-243`)
4. Returns the stripped first body line, truncated to 300 characters, for the first qualifying event; returns `None` if no event qualifies. (`.github/bible/bible_queue.py:244-245`)

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
| `.github/bible/bible_queue.py:239` | for | For each issue timeline event | Checks actor, event time, and body. |
| `.github/bible/bible_queue.py:241` | conditional expression | Actor is a bot (or has no type) | Uses the actor login; otherwise uses an empty login. |
| `.github/bible/bible_queue.py:242` | if | Comment event from configured agent at/after assignment matches `START_ERROR` | Returns the bounded first line; otherwise continues scanning. |

#### `GitHub.assigned_at(issue)`

Source: `.github/bible/bible_queue.py:247-250` <!-- code: 8dec0d30b502 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.start_error` (`.github/bible/bible_queue.py:238`), `Queue.session` (`.github/bible/bible_queue.py:523`) |
| Calls | `GitHub.timeline`, `get`, `max` |
| Purpose | Returns the newest timestamp for an assignment event, falling back to issue creation time. |

**Steps**

1. Collects nonempty `created_at` values from `assigned` timeline events for the issue. (`.github/bible/bible_queue.py:249`)
2. Returns the maximum timestamp, or `issue["created_at"]` if there were none. (`.github/bible/bible_queue.py:250`)

**Pseudo-code**

```text
times = created_at for assigned events with a timestamp
return max(times) if any, otherwise issue.created_at
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:250` | conditional expression | At least one assignment timestamp exists | Returns the newest timestamp; otherwise uses issue creation time. |

#### `GitHub.pr_files(number)`

Source: `.github/bible/bible_queue.py:252-286` <!-- code: a075ee350785 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:837`, `.github/bible/bible_queue.py:843`, `.github/bible/bible_queue.py:846`, `.github/bible/bible_queue.py:865`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:959`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1121`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1163`) |
| Calls | `GitHub.call`, `get`, `pr.get`, `GitHub.branch_sha`, `base.get`, `GitHub.paged`, `as_int`, `isinstance`, `compared.get`, `RuntimeError`, `len`, `append` |
| Purpose | Returns every path a pull request touches (the old name of a renamed file too) and refuses, with a `RuntimeError`, any list that may be incomplete, so no file escapes the scope checks. |

**Steps**

1. GETs `/pulls/<number>` (an empty dictionary when the body is empty), then reads `base` and the head commit's `sha`. (`.github/bible/bible_queue.py:255-256`)
2. Looks up the tip of the base branch only for an open pull request whose base has a `ref` and a recorded `sha` and whose head has a `sha`: `tip = branch_sha(base["ref"])`; for any other pull request `tip` is `None`: a merged one (the tip already contains it, so a comparison would be empty; assumed: GitHub behaviour, stated in the comment at line 257) and also one closed without merging (the check then uses the pull request's own file list). (`.github/bible/bible_queue.py:257-259`)
3. When `tip` exists and differs from the base commit the pull request recorded, GitHub's own file list is against that stale base (assumed: GitHub behaviour, stated in the comment at lines 261-264; seen on github.com on 24 Nov 2026: `main` moved, the revision merged it, and the list then held `main`'s own changes). The method then GETs `/compare/<tip>...<head>` (the base branch as it is now, the merge base as a merge would see it) and takes its `files` list when the response is a dictionary. (`.github/bible/bible_queue.py:260-266`)
4. Fails closed: it raises `RuntimeError("the comparison of #<n> with <base ref> gave no file list: not checked, not merged")` when `files` is not a list, or is empty while the pull request's own `changed_files` is nonzero (`as_int`). (`.github/bible/bible_queue.py:267-270`)
5. Raises `RuntimeError("the file list of #<n> is incomplete (300 files or more against <base ref>): not checked, not merged")` when the list holds `COMPARE_MAX` (300) files or more, because GitHub's comparison lists at most that many (assumed: GitHub behaviour, stated in the comments at lines 71 and 264). In this branch `expected` is `None`, so the pull request's own `changed_files` count is not compared with the list. (`.github/bible/bible_queue.py:271-274`, `.github/bible/bible_queue.py:71`)
6. In every other case (not open, no tip, or the tip equals the recorded base) it pages `/pulls/<number>/files` and sets `expected` to `as_int(pr["changed_files"])`. (`.github/bible/bible_queue.py:275-277`)
7. When `expected` is nonzero and differs from the list's length, raises `RuntimeError("the file list of #<n> is incomplete (<listed> of <expected> files): not checked, not merged")`. The 3,000-file limit of GitHub's own list is stated only in the method's docstring (lines 253-254); no constant in the code holds it, and the effect is the same check: a list shorter than the pull request's own count is refused. (`.github/bible/bible_queue.py:253-254`, `.github/bible/bible_queue.py:278-280`)
8. For each listed file appends `filename`, then `previous_filename` when truthy, and returns the list. (`.github/bible/bible_queue.py:281-286`)

**Pseudo-code**

```text
pr = GET /pulls/<number> or {}
base, head = pr.base or {}, pr.head.sha
tip = branch_sha(base.ref) if pr.state == open and base.ref and base.sha and head else None
if tip and tip != base.sha:
    compared = GET /compare/<tip>...<head>
    listed = compared.files if compared is a dict else None
    if listed is not a list or (listed is empty and pr.changed_files != 0): raise "gave no file list"
    if len(listed) >= COMPARE_MAX: raise "incomplete (300 files or more)"
    expected = None
else:
    listed = paged /pulls/<number>/files
    expected = as_int(pr.changed_files)
if expected and len(listed) != expected: raise "incomplete (n of m files)"
out = []
for f in listed: out += [f.filename] + ([f.previous_filename] if set)
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:258` | conditional expression | The pull request is open, its base has a `ref` and a `sha`, and its head has a `sha` | Reads the base branch's current tip; otherwise `tip` is `None`. |
| `.github/bible/bible_queue.py:260` | if | `tip` exists and differs from the base commit the pull request recorded | Compares the head with the tip; otherwise pages the pull request's own files (the `else` at `.github/bible/bible_queue.py:275`). |
| `.github/bible/bible_queue.py:266` | conditional expression | The comparison's response is a dictionary | Takes its `files`; otherwise `listed` is `None`. |
| `.github/bible/bible_queue.py:268` | if | `listed` is not a list, or is empty while `changed_files` is nonzero | Raises the no-file-list `RuntimeError` (next row). |
| `.github/bible/bible_queue.py:269` | raise | The comparison gave no usable list | `RuntimeError`: the comparison gave no file list; not checked, not merged. |
| `.github/bible/bible_queue.py:271` | if | The comparison lists `COMPARE_MAX` (300) files or more | Raises the incomplete-list `RuntimeError` (next row). |
| `.github/bible/bible_queue.py:272` | raise | The comparison may have been cut at 300 files | `RuntimeError`: the file list is incomplete (300 files or more); not checked, not merged. |
| `.github/bible/bible_queue.py:278` | if | `expected` is nonzero and differs from the number listed (only in the paged branch, where `expected` is not `None`) | Raises the incomplete-list `RuntimeError` (next row). |
| `.github/bible/bible_queue.py:279` | raise | The paged list is shorter or longer than the pull request's own count | `RuntimeError`: the file list is incomplete (n of m files); not checked, not merged. |
| `.github/bible/bible_queue.py:282` | for | For each listed file | Appends its current `filename`. |
| `.github/bible/bible_queue.py:284` | if | `previous_filename` is truthy | Appends the previous filename too. |

**Output and side effects**: returns a list of paths (renamed files appear twice, under both names); no writes. Callers react to the errors differently: in `Queue.follow` only the first call, at line 837, is inside the `try` that catches `RuntimeError` and fails or retries the session with the error text as the reason (`.github/bible/bible_queue.py:836-840`); its later calls (lines 843, 846 and 865, reached only after the first succeeded) are not inside it, but `Queue.run` catches an error from them per component, shows "error this run (retried next run)" for that component and goes on with the other components (`.github/bible/bible_queue.py:653-656`); `assemble_phase`, `revise_all_step` and `continue_if_unfinished` do not catch the error, so an error from their calls ends that tracker's run, and `Queue.reconcile` logs it and tries again at the next check (`.github/bible/bible_queue.py:612-615`).

#### `GitHub.commit_time(sha)`

Source: `.github/bible/bible_queue.py:288-289` <!-- code: a3036655ce65 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:527`) |
| Calls | `GitHub.call` |
| Purpose | Returns the committer date for a commit SHA. |

**Steps**

1. GETs `/commits/<sha>` and returns `commit.committer.date`. (`.github/bible/bible_queue.py:289`)

**Pseudo-code**

```text
return GET /commits/<sha>.commit.committer.date
```

#### `GitHub.tarball(ref, dest)`

Source: `.github/bible/bible_queue.py:291-330` <!-- code: a84776e4e94b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.check` (`.github/bible/bible_queue.py:889`), `Queue.whole_fingerprint` (`.github/bible/bible_queue.py:927`) |
| Calls | `urllib.parse.quote`, `tempfile.TemporaryFile`, `self.request`, `resp.read`, `len`, `buf.write`, `RuntimeError`, `buf.seek`, `os.path.abspath`, `tarfile.open`, `max`, `member.name.split`, `os.path.normpath`, `os.path.join`, `member.isdir`, `os.makedirs`, `os.path.dirname`, `tar.extractfile`, `open`, `shutil.copyfileobj` |
| Purpose | Downloads a bounded repository archive into a temporary file and extracts only regular files and directories whose normalized paths stay below `dest`. |

**Steps**

1. Quotes `ref`, builds the repository tarball URL and requests it with a 300-second timeout. Reads 1 MiB chunks into a `TemporaryFile`; an empty read ends the loop, while cumulative bytes above `MAX_TARBALL` raise `RuntimeError`. (`.github/bible/bible_queue.py:295-306`)
2. Converts request `URLError`, `TimeoutError` or `OSError` into `RuntimeError`, seeks the temporary file to the beginning, resolves `dest` to an absolute root, and opens it as a gzip tar archive. (`.github/bible/bible_queue.py:297-312`)
3. Counts members and their nonnegative uncompressed sizes; exceeding `MAX_MEMBERS` or `MAX_UNPACKED` raises `RuntimeError`. It splits each member name once at `/`, skipping a missing/empty path tail and non-file/non-directory members. (`.github/bible/bible_queue.py:313-321`)
4. Joins the tail to the root, normalizes it, and skips a target whose path does not start with `root + os.sep`. Directories are created recursively; files get a created parent and are copied from `tar.extractfile(member)` into a binary file. (`.github/bible/bible_queue.py:322-330`)

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
| `.github/bible/bible_queue.py:299` | while | Response chunks are being read | Reads the next chunk and exits when it is empty. |
| `.github/bible/bible_queue.py:301` | if | `resp.read` returns no bytes | Leaves the streaming loop. |
| `.github/bible/bible_queue.py:304` | if | Total compressed bytes exceed `MAX_TARBALL` | Raises `RuntimeError` without unpacking. |
| `.github/bible/bible_queue.py:305` | raise | Compressed-size limit exceeded | Reports the reference and configured maximum. |
| `.github/bible/bible_queue.py:307` | except | Request raises `URLError`, `TimeoutError` or `OSError` | Converts the error to a `RuntimeError` naming the reference. |
| `.github/bible/bible_queue.py:308` | raise | A listed request error occurred | Stops with the wrapped `RuntimeError`. |
| `.github/bible/bible_queue.py:313` | for | For each archive member | Counts the member and validates total limits before extraction. |
| `.github/bible/bible_queue.py:316` | if | Member count or uncompressed-size limit is exceeded | Raises `RuntimeError`; extraction stops. |
| `.github/bible/bible_queue.py:317` | raise | A tarball member limit was exceeded | Reports the member and uncompressed-size limits. |
| `.github/bible/bible_queue.py:320` | if | Missing path tail or member is neither regular file nor directory | Skips the member. |
| `.github/bible/bible_queue.py:323` | if | Normalized target does not start with the root plus separator | Skips the target. |
| `.github/bible/bible_queue.py:325` | if | Member is a directory | Creates it and continues to the next member. |

#### `GitHub.label(number, name)`

Source: `.github/bible/bible_queue.py:332-334` <!-- code: 3c67a9360e66 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:554`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:577`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:589`), `Queue.follow` (`.github/bible/bible_queue.py:855`, `.github/bible/bible_queue.py:856`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:977`, `.github/bible/bible_queue.py:982`, `.github/bible/bible_queue.py:1003`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1182`, `.github/bible/bible_queue.py:1193`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures and adds one label to an issue. |

**Steps**

1. Ensures the label using its `LABELS` description or the default description. (`.github/bible/bible_queue.py:333`)
2. Posts `{"labels": [name]}` to the issue labels endpoint. (`.github/bible/bible_queue.py:334`)

**Pseudo-code**

```text
ensure label using mapped description or default
POST issue labels with [name]
```

#### `GitHub.unlabel(number, name)`

Source: `.github/bible/bible_queue.py:336-337` <!-- code: caf34958b931 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:876`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Removes a label from an issue and permits a missing-label response. |

**Steps**

1. URL-quotes `name` and sends DELETE to the issue label endpoint with `ok404=True`. (`.github/bible/bible_queue.py:337`)

**Pseudo-code**

```text
DELETE quoted issue label endpoint, allowing 404
```

#### `GitHub.comment(number, text)`

Source: `.github/bible/bible_queue.py:339-340` <!-- code: a05e7f494734 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:555`, `.github/bible/bible_queue.py:559`, `.github/bible/bible_queue.py:567`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:579`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:586`, `.github/bible/bible_queue.py:591`, `.github/bible/bible_queue.py:594`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:978`, `.github/bible/bible_queue.py:983`, `.github/bible/bible_queue.py:1004`, `.github/bible/bible_queue.py:1041`, `.github/bible/bible_queue.py:1048`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1183`, `.github/bible/bible_queue.py:1194`, `.github/bible/bible_queue.py:1198`), `Queue.delta` (`.github/bible/bible_queue.py:1236`) |
| Calls | `GitHub.call` |
| Purpose | Creates an issue comment with the given body. |

**Steps**

1. Posts `{"body": text}` to `/issues/<number>/comments`. (`.github/bible/bible_queue.py:340`)

**Pseudo-code**

```text
POST issue comments with body=text
```

#### `GitHub.close(number, reason="completed")`

Source: `.github/bible/bible_queue.py:342-343` <!-- code: db2a40d380a0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:561`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:595`), `Queue.run` (`.github/bible/bible_queue.py:649`), `Queue.component` (`.github/bible/bible_queue.py:739`), `Queue.follow` (`.github/bible/bible_queue.py:877`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1006`, `.github/bible/bible_queue.py:1008`, `.github/bible/bible_queue.py:1042`), `Queue.whole_hold` (`.github/bible/bible_queue.py:1071`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1084`, `.github/bible/bible_queue.py:1104`) |
| Calls | `GitHub.call` |
| Purpose | Closes an issue with the supplied state reason. |

**Steps**

1. PATCHes `/issues/<number>` with `state: "closed"` and the supplied `state_reason`. (`.github/bible/bible_queue.py:343`)

**Pseudo-code**

```text
PATCH issue state=closed and state_reason=reason
```

#### `GitHub.set_body(number, body)`

Source: `.github/bible/bible_queue.py:345-346` <!-- code: 56545a0f998b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:564`), `Queue.render` (`.github/bible/bible_queue.py:1218`) |
| Calls | `GitHub.call` |
| Purpose | Replaces an issue's body. |

**Steps**

1. PATCHes `/issues/<number>` with `{"body": body}`. (`.github/bible/bible_queue.py:346`)

**Pseudo-code**

```text
PATCH issue body=body
```

#### `GitHub.unassign(number)`

Source: `.github/bible/bible_queue.py:348-349` <!-- code: 415484346894 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:578`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:590`) |
| Calls | `GitHub.call` |
| Purpose | Removes the configured Copilot assignee from an issue. |

**Steps**

1. Sends DELETE to `/issues/<number>/assignees` with `COPILOT` as the sole assignee. (`.github/bible/bible_queue.py:349`)

**Pseudo-code**

```text
DELETE issue assignees with [COPILOT]
```

#### `GitHub.assign(number, assign)`

Source: `.github/bible/bible_queue.py:351-352` <!-- code: 8fb2f09224db -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:566`) |
| Calls | `GitHub.call` |
| Purpose | Assigns Copilot to an issue with the provided agent-assignment data. |

**Steps**

1. Posts `COPILOT` as the sole assignee and includes the supplied `agent_assignment`. (`.github/bible/bible_queue.py:352`)

**Pseudo-code**

```text
POST issue assignees with [COPILOT] and agent_assignment=assign
```

#### `GitHub.ready(pr)`

Source: `.github/bible/bible_queue.py:354-362` <!-- code: ae31dacf00e7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.merge` (`.github/bible/bible_queue.py:366`) |
| Calls | `endswith`, `GitHub.request`, response `read`, `RuntimeError` |
| Purpose | Marks a draft pull request ready for review through GitHub GraphQL. |

**Steps**

1. Defines the `markPullRequestReadyForReview` mutation and chooses the GraphQL URL; for an API base ending `/api/v3`, removes `/v3` before adding `/graphql`. (`.github/bible/bible_queue.py:356-357`)
2. POSTs the query and `pr["node_id"]` as the `id` variable, then reads the response. (`.github/bible/bible_queue.py:358-360`)
3. Converts an `HTTPError` to a `RuntimeError` containing the GraphQL operation and HTTP status. (`.github/bible/bible_queue.py:361-362`)

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
| `.github/bible/bible_queue.py:357` | conditional expression | API URL ends with `/api/v3` | Removes `/v3` before appending `/graphql`; otherwise appends `/graphql` directly. |
| `.github/bible/bible_queue.py:361` | except | Request raises `HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:362` | raise | GraphQL request raises `HTTPError` | Raises `RuntimeError` with operation and HTTP status. |

#### `GitHub.merge(pr, title)`

Source: `.github/bible/bible_queue.py:364-368` <!-- code: cea69f3a2a18 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:875`) |
| Calls | `get`, `GitHub.ready`, `GitHub.call` |
| Purpose | Marks a draft ready, when needed, and requests a squash merge with the supplied title. |

**Steps**

1. Calls `ready` only when `pr["draft"]` is truthy. (`.github/bible/bible_queue.py:365-366`)
2. PUTs `/pulls/<number>/merge` with `merge_method: "squash"`, the supplied `commit_title`, and the current head SHA. (`.github/bible/bible_queue.py:367-368`)

**Pseudo-code**

```text
if PR is draft: mark it ready
PUT merge request with squash method and title
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:365` | if | `pr["draft"]` is truthy | Calls `ready` before requesting the merge. |

#### `GitHub.close_pr(number)`

Source: `.github/bible/bible_queue.py:370-371` <!-- code: c5e4b3b311ae -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:587`) |
| Calls | `GitHub.call` |
| Purpose | Closes a pull request. |

**Steps**

1. PATCHes `/pulls/<number>` with `state: "closed"`. (`.github/bible/bible_queue.py:371`)

**Pseudo-code**

```text
PATCH pull request state=closed
```

#### `GitHub.create_pr(head, base, title, body)`

Source: `.github/bible/bible_queue.py:373-374` <!-- code: 9b2aa4667c1c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:779`) |
| Calls | `GitHub.call` |
| Purpose | Creates a pull request and returns the API result. |

**Steps**

1. POSTs `head`, `base`, `title`, and `body` to `/pulls`, returning `call`'s result. (`.github/bible/bible_queue.py:374`)

**Pseudo-code**

```text
return POST /pulls with head, base, title, and body
```

### `Queue`

Source: `.github/bible/bible_queue.py:500-1283`

`Queue` coordinates tracker issues, component sessions, verification/revision cycles, assembly, and delta updates; since 24 Nov 2026 it also continues an assembly or whole-analysis session that ended before its end marker, and holds one whose Copilot session failed before starting (`Queue.continue_if_unfinished`, `.github/bible/bible_queue.py:1154-1207`). Its constructor sets the GitHub client, logger, and skill directory (`.github/bible/bible_queue.py:501-503`); methods also populate run-specific fields: `deadline` and `default` in `reconcile` (`.github/bible/bible_queue.py:605-606`), `settings`, `tracker`, `run_label` and `state` in `run` (`.github/bible/bible_queue.py:619-627`), and `estimate` (`.github/bible/bible_queue.py:650`); `delta` also sets `default` (`.github/bible/bible_queue.py:1225`), and `could_not_check`, `component` and `assemble_phase` change the `state` counters (`.github/bible/bible_queue.py:910-913`, `.github/bible/bible_queue.py:752`, `.github/bible/bible_queue.py:972`).

#### `Queue.__init__(gh, log=print)`

Source: `.github/bible/bible_queue.py:501-503` <!-- code: 11924208c0e9 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1306`) |
| Calls | `os.environ.get` |
| Purpose | Stores the GitHub client and logger, and selects the skills directory. |

**Steps**

1. Stores `gh` and `log` on the instance. (`.github/bible/bible_queue.py:502`)
2. Reads `BIBLE_SKILLS`, defaulting to `.github/skills`. (`.github/bible/bible_queue.py:503`)

**Pseudo-code**

```text
self.gh, self.log = gh, log
self.skills = BIBLE_SKILLS or ".github/skills"
```

#### `Queue.run_issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:505-506` <!-- code: 9186c4a33e43 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:648`), `Queue.plan_phase` (`.github/bible/bible_queue.py:672`), `Queue.start_chunk` (`.github/bible/bible_queue.py:700`), `Queue.component` (`.github/bible/bible_queue.py:720`, `.github/bible/bible_queue.py:732`, `.github/bible/bible_queue.py:734`, `.github/bible/bible_queue.py:740`, `.github/bible/bible_queue.py:756`, `.github/bible/bible_queue.py:771`, `.github/bible/bible_queue.py:774`, `.github/bible/bible_queue.py:776`, `.github/bible/bible_queue.py:792`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:942`, `.github/bible/bible_queue.py:975`, `.github/bible/bible_queue.py:981`, `.github/bible/bible_queue.py:992`), `Queue.whole_hold` (`.github/bible/bible_queue.py:1068`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1079`, `.github/bible/bible_queue.py:1085`, `.github/bible/bible_queue.py:1089`, `.github/bible/bible_queue.py:1091`, `.github/bible/bible_queue.py:1097`) |
| Calls | `self.gh.issues` |
| Purpose | Queries issues for the requested labels plus this run's unique label. |

**Steps**

1. Appends `self.run_label` to the supplied labels and calls `gh.issues` with the requested state. (`.github/bible/bible_queue.py:506`)

**Pseudo-code**

```text
return gh.issues(labels + [run_label], state)
```

#### `Queue.agent_pr(issue, base)`

Source: `.github/bible/bible_queue.py:508-514` <!-- code: 471c772b908b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:519`) |
| Calls | `reversed`, `self.gh.linked_prs`, `get`, `self.gh.is_agent_pr` |
| Purpose | Finds the newest linked pull request that is open, same-repository, targets `base`, and is by the agent. |

**Steps**

1. Iterates linked pull requests in reverse order. (`.github/bible/bible_queue.py:510`)
2. Reads the head repository full name, defaulting missing nested values to `{}`. (`.github/bible/bible_queue.py:511`)
3. Returns the first PR whose state is `open`, head repository is `gh.repo`, base ref matches, and `is_agent_pr` is true. (`.github/bible/bible_queue.py:512-513`)
4. Returns `None` when no linked PR qualifies. (`.github/bible/bible_queue.py:514`)

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
| `.github/bible/bible_queue.py:510` | for | For each linked PR in reverse order | Checks newer linked PRs first. |
| `.github/bible/bible_queue.py:512` | if | PR is open, same-repository, targets `base`, and is an agent PR | Returns that PR. |

#### `Queue.session(issue, base, analysis, comp=None)`

Source: `.github/bible/bible_queue.py:517-533` <!-- code: 287d4620c196 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:685`), `Queue.follow` (`.github/bible/bible_queue.py:824`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1014`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1108`) |
| Calls | `self.agent_pr`, `self.gh.start_error`, `age`, `self.gh.assigned_at`, `self.gh.agent_events`, `sorted`, `self.gh.commit_time`, `bool`, `pr.get`, `status_of`, `labels_of`, `status.get` |
| Purpose | Classifies an open session issue as start-error, no-start, waiting, running or finished and returns its pull request when there is one. |

**Steps**

1. Looks up the agent's open pull request for the issue with `self.agent_pr(issue, base)`. (`.github/bible/bible_queue.py:519`)
2. With no pull request: returns `("start-error", None)` when `gh.start_error(issue)` is truthy; otherwise returns `("no-start", None)` when the age of the issue's assignment exceeds `NO_PR_AFTER` (30 minutes), else `("waiting", None)`. (`.github/bible/bible_queue.py:520-523`, `.github/bible/bible_queue.py:74`)
3. With a pull request, reads `gh.agent_events` for it. When any event exists, GitHub's own record decides: the newest event by timestamp being `copilot_work_started` gives `"running"`, any other newest event (`copilot_work_finished` or, since `WORK_EVENTS` gained it, `copilot_work_finished_failure`) gives `"finished"`; the pull request is returned with it. (`.github/bible/bible_queue.py:524-526`)
4. With no work events, computes `pushed`, the age of the head commit, and `asked`, true when reviewers were requested or the pull request is not a draft. (`.github/bible/bible_queue.py:527-528`)
5. For a component chunk (`comp` given and the label `bible-chunk` on the issue), reads `<analysis>/ledger/components/<comp>/status.json` at the head SHA and sets `final` when its `state` is in `FINAL_STATES`; returns `"finished"` when `final` and (`asked` or `pushed` > `IDLE_AFTER`), or when `pushed` > 3 x `IDLE_AFTER`, else `"running"`. (`.github/bible/bible_queue.py:529-532`)
6. Otherwise returns `"finished"` when `asked` or `pushed` > `IDLE_AFTER`, else `"running"`. (`.github/bible/bible_queue.py:533`)

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
| `.github/bible/bible_queue.py:520` | if | no agent pull request was found | enters the start-error / no-start / waiting classification |
| `.github/bible/bible_queue.py:521` | if | `start_error(issue)` is truthy | returns `("start-error", None)` |
| `.github/bible/bible_queue.py:523` | conditional expression | assignment age exceeds `NO_PR_AFTER` | returns `no-start`; otherwise `waiting`; the pull request is `None` |
| `.github/bible/bible_queue.py:525` | if | `agent_events` returned at least one event | the newest event decides: `running` only for `copilot_work_started`, otherwise `finished` (a failure event counts as finished) |
| `.github/bible/bible_queue.py:526` | conditional expression | newest event is `copilot_work_started` | returns `running`; otherwise `finished` |
| `.github/bible/bible_queue.py:529` | if | `comp` is truthy and the issue has the label `bible-chunk` | uses the head `status.json` and the component-specific age rules |
| `.github/bible/bible_queue.py:532` | conditional expression | final status and (asked or idle), or pushed age exceeds `3 * IDLE_AFTER` | returns `finished`; otherwise `running` |
| `.github/bible/bible_queue.py:533` | conditional expression | `asked` or pushed age exceeds `IDLE_AFTER` | returns `finished`; otherwise `running` |

**Output and side effects**: returns a `(state, pr)` pair; reads only (timeline, commit time, `status.json` at the head SHA). The docstring lists four states and omits `start-error` (`.github/bible/bible_queue.py:518`).

#### `Queue.held(issue)`

Source: `.github/bible/bible_queue.py:535-568` <!-- code: c519a460eab6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:683`), `Queue.component` (`.github/bible/bible_queue.py:723`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1012`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1106`) |
| Calls | `labels_of`, `any`, `get`, `issue.get`, `self.gh.timeline`, `max`, `e.get`, `self.gh.label`, `self.gh.comment`, `self.gh.close`, `l.startswith`, `ATTEMPT.sub`, `self.gh.set_body`, `re.search`, `self.gh.assign`, `assignment`, `self.model_for`, `base.group` |
| Purpose | Holds issues marked for a person, closes released component sessions, or reassigns other unassigned sessions to Copilot. |

**Steps**

1. Returns `True` when the labels include `bible-needs-human`. (`.github/bible/bible_queue.py:543`)
2. Otherwise returns `False` immediately when an assignee login belongs to `AGENT_LOGINS`. (`.github/bible/bible_queue.py:545`)
3. Reads issue timeline events and finds the latest added and removed timestamps for `bible-needs-human`; if removal is absent or not newer, labels and comments the issue for human review and returns `True`. (`.github/bible/bible_queue.py:546-558`)
4. If a `bible/` label exists after release, comments and closes the issue as `not_planned`, returning `released`. (`.github/bible/bible_queue.py:559-562`)
5. Otherwise resets the `Attempt:` marker, saves the body, extracts `Base branch:` or uses `self.default`, assigns Copilot with the selected model, comments, and returns `False`. (`.github/bible/bible_queue.py:563-568`)

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
| `.github/bible/bible_queue.py:543` | if | Labels contain `bible-needs-human` | Returns `True`. |
| `.github/bible/bible_queue.py:545` | if | An assignee login belongs to `AGENT_LOGINS` | Returns `False`. |
| `.github/bible/bible_queue.py:552` | if | The human-label removal is absent or not newer than its addition | Labels, comments, and returns `True`. |
| `.github/bible/bible_queue.py:558` | return | No valid release follows the human hold | Stops before reassignment. |
| `.github/bible/bible_queue.py:559` | if | A component label begins `bible/` after release | Closes and returns `released`; otherwise reassigns. |
| `.github/bible/bible_queue.py:566` | conditional expression | A `Base branch:` match exists | Uses its captured branch; otherwise uses `self.default`. |

#### `Queue.model_for(issue)`

Source: `.github/bible/bible_queue.py:570-572` <!-- code: 17f084589886 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:566`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:600`) |
| Calls | `labels_of`, `self.settings.get` |
| Purpose | Selects the verification model for verification issue types, otherwise the normal model. |

**Steps**

1. Gets the issue's label names. (`.github/bible/bible_queue.py:571`)
2. Returns `verify_model` when labels intersect `bible-verify` or `bible-verify-all`; otherwise returns `model`. (`.github/bible/bible_queue.py:572`)

**Pseudo-code**

```text
kinds = labels_of(issue)
return settings.verify_model if kinds intersects verify labels
       else settings.model
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:572` | conditional expression | `kinds` intersects the verification labels | Returns `verify_model`; otherwise returns `model`. |

#### `Queue.hold_start_error(issue)`

Source: `.github/bible/bible_queue.py:574-580` <!-- code: 510c0f07df06 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:687`), `Queue.follow` (`.github/bible/bible_queue.py:828`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1016`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1110`) |
| Calls | `self.gh.start_error`, `self.gh.label`, `self.gh.unassign`, `self.gh.comment` |
| Purpose | Holds a session with an agent start error for human intervention. |

**Steps**

1. Gets the start-error text or uses `Copilot could not start`. (`.github/bible/bible_queue.py:576`)
2. Adds `bible-needs-human`, unassigns Copilot, and posts a comment containing the reason and remediation guidance. (`.github/bible/bible_queue.py:577-580`)

**Pseudo-code**

```text
why = start_error(issue) or fallback message
label issue bible-needs-human
unassign Copilot
comment why and instructions for removing the hold
```

#### `Queue.fail_or_retry(issue, pr, why)`

Source: `.github/bible/bible_queue.py:582-601` <!-- code: c86515a02433 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:690`), `Queue.follow` (`.github/bible/bible_queue.py:831`, `.github/bible/bible_queue.py:839`, `.github/bible/bible_queue.py:849`, `.github/bible/bible_queue.py:862`, `.github/bible/bible_queue.py:867`, `.github/bible/bible_queue.py:870`, `.github/bible/bible_queue.py:873`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1019`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1113`, `.github/bible/bible_queue.py:1124`) |
| Calls | `ATTEMPT.search`, `int`, `self.gh.comment`, `self.gh.close_pr`, `self.gh.label`, `self.gh.unassign`, `self.gh.close`, `ATTEMPT.sub`, `re.search`, `self.gh.create_issue`, `sorted`, `assignment`, `self.model_for`, `labels_of`, `startswith` |
| Purpose | Closes a failed attempt and opens its retry, or holds the issue after a second failure. |

**Steps**

1. Parses the attempt number from the issue body, defaulting to 1. (`.github/bible/bible_queue.py:584`)
2. If a PR was supplied, comments that it was not merged and closes it. (`.github/bible/bible_queue.py:585-587`)
3. When attempt is at least 2, labels and unassigns the issue, posts a human-action comment, and returns `False`. (`.github/bible/bible_queue.py:588-593`)
4. Otherwise comments that a new attempt will open, closes the issue with `not_planned`, updates or prepends the attempt marker, and extracts the base branch or uses `self.default`. (`.github/bible/bible_queue.py:594-598`)
5. Creates a replacement issue with only labels beginning `bible`, sorted, and assignment data for the chosen base and model; returns `True`. (`.github/bible/bible_queue.py:599-601`)

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
| `.github/bible/bible_queue.py:585` | if | `pr` is truthy | Comments that it was not merged and closes the PR; otherwise skips PR updates. |
| `.github/bible/bible_queue.py:588` | if | Attempt number is at least 2 | Labels and unassigns the issue, comments for human action, and returns `False`; otherwise opens a retry. |
| `.github/bible/bible_queue.py:596` | conditional expression | The issue body contains an attempt marker | Replaces it with the incremented attempt; otherwise prepends `Attempt: 2`. |
| `.github/bible/bible_queue.py:600` | conditional expression | A `Base branch:` match exists in the original body | Assigns the retry to that branch; otherwise uses `self.default`. |

#### `Queue.reconcile()`

Source: `.github/bible/bible_queue.py:604-615` <!-- code: 10e9886e081f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1326`) |
| Calls | `self.gh.default_branch`, `self.gh.issues`, `settings_of`, `self.log`, `self.run`, `type` |
| Purpose | Processes each open tracker independently so one failing tracker does not prevent others. |

**Steps**

1. Sets a monotonic deadline at `now + RUN_BUDGET`, then stores the repository's default branch. (`.github/bible/bible_queue.py:605-606`)
2. Iterates open issues labeled `bible-tracker`; parses each settings block, logging and skipping trackers without readable settings. (`.github/bible/bible_queue.py:607-611`)
3. Runs each readable tracker independently; catches `Exception` and logs the tracker number, exception type and message, then continues with the next tracker. (`.github/bible/bible_queue.py:612-615`)

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
| `.github/bible/bible_queue.py:607` | for | For each open `bible-tracker` issue | Parses its settings and processes that tracker independently. |
| `.github/bible/bible_queue.py:609` | if | `settings_of` returns a falsey value | Logs the tracker number and skips it. |
| `.github/bible/bible_queue.py:612` | try | Settings are readable | Calls `run` for the tracker. |
| `.github/bible/bible_queue.py:614` | except | Processing the tracker raises `Exception` | Logs tracker number, exception type and message, then continues to the next tracker. |

#### `Queue.run(tracker, settings)`

Source: `.github/bible/bible_queue.py:617-668` <!-- code: ab24ac87df39 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:613`) |
| Calls | `settings.get`, `STATE.search`, `tracker.get`, `json.loads`, `found.group`, `isinstance`, `json_file`, `catalog.get`, `self.plan_phase`, `c.get`, `str`, `NAME.match`, `len`, `self.render`, `str.strip`, `asked.split`, `n.strip`, `join`, `self.run_issues`, `gh.close`, `self.component`, `str.endswith`, `str.startswith`, `as_int`, `self.start_chunk`, `type`, `all`, `rows.values`, `self.assemble_phase` |
| Purpose | Restores tracker state, validates the component catalog and selection, advances component states up to the configured concurrency, and renders the tracker. |

**Steps**

1. Selects `analysis` from settings or `codebase-analysis`, saves settings/tracker/run label, and parses the hidden state marker. Invalid JSON and non-dictionary state become `{}`. Reads `components.json` from the default branch. (`.github/bible/bible_queue.py:618-628`)
2. If the catalog is not a dict, is proposed, or lacks a list of components, returns the result of `plan_phase`. It stringifies each dict component's name, filters names with `NAME`, and renders a stopped settings row if any listed name is invalid. (`.github/bible/bible_queue.py:629-639`)
3. Strips the requested component selection; `all` or empty means all valid names, otherwise comma-splits and strips the names. Unknown or empty selection renders a stopped settings row and returns. (`.github/bible/bible_queue.py:640-647`)
4. Closes open plan issues, records catalog session estimates, evaluates each requested component, catches component exceptions into a 160-character error row, and counts rows ending in `running`, `starting`, or `merged`, or beginning with `waiting`. (`.github/bible/bible_queue.py:648-657`)
5. Converts `concurrency` with `as_int`; starts each `not started` component when the cap is zero or active count is below it. A `RuntimeError` becomes a 160-character error row. When every row is `merged`, adds whole-analysis assembly status; renders all rows. (`.github/bible/bible_queue.py:658-668`)

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
| `.github/bible/bible_queue.py:623` | conditional expression | State marker matched | Parses its JSON group; otherwise uses `{}`. |
| `.github/bible/bible_queue.py:624` | except | State JSON raises `ValueError` | Replaces it with `{}`. |
| `.github/bible/bible_queue.py:626` | if | Parsed state is not a dict | Replaces it with `{}`. |
| `.github/bible/bible_queue.py:629` | if | Catalog is invalid, proposed, or has no component list | Returns the planning-phase result. |
| `.github/bible/bible_queue.py:635` | if | Any listed component name fails `NAME` | Renders a stopped settings row and returns. |
| `.github/bible/bible_queue.py:641` | conditional expression | Selection is `all` or empty | Uses all valid names; otherwise parses comma-separated names. |
| `.github/bible/bible_queue.py:643` | if | Selection contains unknown names or is empty | Renders stopped settings and returns. |
| `.github/bible/bible_queue.py:646` | conditional expression | Unknown names exist | Reports them; otherwise reports that no component was selected. |
| `.github/bible/bible_queue.py:648` | for | Open `bible-plan` issues exist | Closes each issue. |
| `.github/bible/bible_queue.py:652` | for | Each requested component | Evaluates its status. |
| `.github/bible/bible_queue.py:655` | except | Component evaluation raises `Exception` | Stores the exception type and at most 160 characters of its text. |
| `.github/bible/bible_queue.py:659` | for | Each requested component | Considers starting a `not started` row. |
| `.github/bible/bible_queue.py:660` | if | Row is `not started` and no cap or active count below cap | Attempts to start a fresh chunk. |
| `.github/bible/bible_queue.py:664` | except | Starting the chunk raises `RuntimeError` | Stores the exception text, capped at 160 characters. |
| `.github/bible/bible_queue.py:666` | if | Every row is `merged` | Adds whole-analysis assembly status. |

#### `Queue.plan_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:670-692` <!-- code: f5b3e835d2d7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:630`) |
| Calls | `self.run_issues`, `issue_text`, `self.gh.create_issue`, `self.render`, `assignment`, `settings.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry` |
| Purpose | Creates or tracks the plan issue and reports plan-session progress. |

**Steps**

1. Gets open plan issues for the tracker run. (`.github/bible/bible_queue.py:672`)
2. If none are open, reads the plan title and body from the analysis ledger; when the body is empty, supplies built-in instructions to run passes 1 and 2, write the Components table, and finish discovery without starting components. It then creates and assigns the plan issue and renders its assigned status. (`.github/bible/bible_queue.py:673-681`)
3. Otherwise selects the first plan issue; if held, renders its human-needed status. (`.github/bible/bible_queue.py:682-684`)
4. Classifies its session; if Copilot reports a start error, marks the issue for human action and renders that status. (`.github/bible/bible_queue.py:685-688`)
5. On `no-start`, requests a retry; then renders the pull-request review state when a PR exists, or the session state otherwise. (`.github/bible/bible_queue.py:689-692`)

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
| `.github/bible/bible_queue.py:673` | if | No open plan issue exists | Reads the planned issue text and creates an assigned plan issue. |
| `.github/bible/bible_queue.py:675` | if | The loaded body is falsey | Uses built-in plan and discovery instructions. |
| `.github/bible/bible_queue.py:683` | if | The first open plan issue is held | Renders that a person must act. |
| `.github/bible/bible_queue.py:686` | if | Session state is `start-error` | Holds the issue and renders human-needed state. |
| `.github/bible/bible_queue.py:689` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:691` | conditional expression | `pr` exists | Renders review/merge PR number; otherwise renders the session state. |

#### `Queue.start_chunk(analysis, name, fresh=False, note="")`

Source: `.github/bible/bible_queue.py:694-706` <!-- code: 7f612dd5f454 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:662`), `Queue.component` (`.github/bible/bible_queue.py:772`, `.github/bible/bible_queue.py:807`) |
| Calls | `self.gh.branch_sha`, `self.gh.create_branch`, `self.gh.reset_branch`, `self.run_issues`, `comp_label`, `issue_text`, `self.gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Creates the component branch when absent, optionally resets it for the first chunk, and opens the next assigned chunk issue. |

**Steps**

1. Sets branch to `bible/<name>` and reads the default branch SHA. (`.github/bible/bible_queue.py:696-697`)
2. Creates the component branch at that SHA when absent; otherwise resets it when `fresh` is true and no issue of this run (the label `bible-run-<tracker number>` that `run_issues` adds) carries the component label, in any state. (`.github/bible/bible_queue.py:698-701`)
3. Reads the component issue text from the default branch, formats the Component/Base branch/Attempt header, and creates a labeled chunk issue with optional note and model assignment. (`.github/bible/bible_queue.py:702-706`)

**Pseudo-code**

```text
branch = "bible/" + name
head_sha = default branch SHA
if branch missing: create branch at head_sha
elif fresh and no issue of this run with the component label, in any state: reset branch to head_sha
title, body = issue_text(component issue file)
create assigned chunk issue with component/base/attempt header and optional note
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:698` | if | The component branch has no SHA | Creates the branch at the default branch SHA. |
| `.github/bible/bible_queue.py:700` | elif | Branch exists, `fresh` is true, and no issue of this run (label `bible-run-<n>`) with the component label exists, in any state | Resets the branch to the default branch SHA. |
| `.github/bible/bible_queue.py:705` | conditional expression | `note` is truthy | Adds the note and a newline before the body; otherwise adds no note prefix. |

#### `Queue.component(analysis, name)`

Source: `.github/bible/bible_queue.py:708-819` <!-- code: c0d9266497e6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:654`) |
| Calls | `gh.branch_prs`, `pr.get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `gh.close`, `labels_of`, `max`, `h.get`, `status_of`, `status.get`, `time.monotonic`, `getattr`, `float`, `self.check`, `self.could_not_check`, `self.state.pop`, `min`, `as_int`, `self.start_chunk`, `len`, `i.get`, `report_facts`, `gh.file`, `bool`, `any`, `gh.create_issue`, `gh.create_pr`, `assignment`, `self.settings.get` |
| Purpose | Advances one component through its pull requests, sessions, gate, verification/revision rounds, final review PR, or human hold. |

**Steps**

1. Scans PRs from `bible/<name>` to the default branch, skipping PRs from another repository, predating the tracker, or lacking its tracker reference. Returns `merged`, a review status for an open PR, or, for a matching PR that was closed without merging, the status `needs a person: its pull request #<n> was closed without merging; reopen it, or start a new run`. (`.github/bible/bible_queue.py:711-719`)
2. Finds open chunk/verify issues. For the first, returns a released status, a human-needed status, or delegates to `follow`; with no open issue, returns `not started` if no issue of this run (label `bible-run-<n>`) with the component label exists, in any state. (`.github/bible/bible_queue.py:720-733`) It then reads the component's hold issues in any state: an open hold that still carries `bible-needs-human` returns the needs-person row; an open hold whose label a person removed is closed, and `after`, the latest `closed_at` among the holds, starts new rounds. (`.github/bible/bible_queue.py:734-741`)
3. Reads the component status. `gate_ok` starts as `False` and `pages` as `None`, so any state other than `COMPONENT_DONE` skips the check and goes straight to step 4. For `COMPONENT_DONE`, waits for the next check if the run deadline cannot accommodate two gate timeouts plus 300 seconds; otherwise runs the gate. An un-runnable check increments its no-check count and may create a human hold; a runnable check clears that count. (`.github/bible/bible_queue.py:742-752`)
4. If the gate did not pass (or was not run, see step 3), counts the closed chunk issues created since the later of the latest hold release and the latest merge into the default branch. The estimate is `est_sessions` from `components.json`; a missing, zero or non-numeric value counts as 2, and the result is clamped to 1-10. The cap is 2 x estimate + 2, at least `MIN_SESSION_CAP` (4) and at most `MAX_SESSION_CAP` (22). When the count reaches the cap it creates a human hold (`bible-hold`, `bible-needs-human`); otherwise it starts the next chunk, whose note says "Session `done` + 1 of about `estimate`", where `done` counts every closed chunk issue of the component, not only those since the reset point. (`.github/bible/bible_queue.py:82-83`, `.github/bible/bible_queue.py:753-773`)
5. After a passing gate, selects completed verifications since the last hold release and reads the report when any completed verification exists. A `PASS` with no major corrections and a matching nonempty page fingerprint creates a component-to-default PR. (`.github/bible/bible_queue.py:774-782`)
6. When a report exists, no chunk completed after the latest verification and the completed verifications since the last hold release reach `MAX_VERIFY_ROUNDS` (2), opens a human hold (a hold needs a report to have been read: with no report the next step is always a verification). If the verdict is about these pages (its fingerprint equals the pages' now), is not a clean `PASS` and no chunk session completed since the latest verification, starts a revision chunk; otherwise creates a verification issue and assigns it on the verification model, `settings["verify_model"]`, not on `model`, and returns `verify running`. (`.github/bible/bible_queue.py:783-819`, `.github/bible/bible_queue.py:818`)

**Pseudo-code**

```text
for matching tracker PR: return merged, review, or needs-person status
if open chunk/verify issue: return released, needs-person, or follow(issue)
if no issue of this run with the component label ever existed: return not started
if a hold issue is open: return needs-person, or close it (label removed) and restart the round count
status = component status
gate_ok, pages = False, None
if status is COMPONENT_DONE:
    if insufficient run time: wait for next check
    gate_ok, pages = check(...)
    if check could not run: count toward human hold; return/wait
if not gate_ok (a failed check, or any state other than COMPONENT_DONE):
    cap = min(max(4, 2 * min(max(est_sessions or 2, 1), 10) + 2), 22)
    if closed chunks since the reset point >= cap: create human hold; return
    else start next chunk; return
load completed verification/report facts after hold release
if clean matching PASS: create component PR; return review status
if a report was read and the verification-round limit is reached: create human hold
if current report requests revision and no later chunk: start revision
else create verification issue; return verify running
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:711` | for | For each PR targeting the default branch | Checks repository, tracker age and body reference. |
| `.github/bible/bible_queue.py:713` | if | PR is foreign, predates the tracker, or lacks its reference | Skips it. |
| `.github/bible/bible_queue.py:715` | if | Matching PR is merged | Returns `merged`. |
| `.github/bible/bible_queue.py:717` | if | Matching PR is open | Returns its review status. |
| `.github/bible/bible_queue.py:719` | return | Matching PR is neither merged nor open (closed without merging) | Returns `needs a person: its pull request #<n> was closed without merging; reopen it, or start a new run`; no later check of this component runs. |
| `.github/bible/bible_queue.py:721` | if | An open chunk or verify issue exists | Selects its first issue. |
| `.github/bible/bible_queue.py:724` | if | `held` reports release | Returns released status for the next check. |
| `.github/bible/bible_queue.py:726` | if | Issue remains held | Returns needs-person status. |
| `.github/bible/bible_queue.py:732` | if | No issue of this run (label `bible-run-<n>`) with the component label exists, in any state | Returns `not started`. |
| `.github/bible/bible_queue.py:736` | if | At least one hold issue is open | Checks its human-required label. |
| `.github/bible/bible_queue.py:737` | if | First open hold has `bible-needs-human` | Returns needs-person; otherwise closes the released hold. |
| `.github/bible/bible_queue.py:744` | if | Status state is `COMPONENT_DONE` | Runs or defers the component gate. |
| `.github/bible/bible_queue.py:745` | if | Remaining run time is insufficient for the gate budget | Returns a wait-until-next-check state. |
| `.github/bible/bible_queue.py:748` | if | Gate returned `None` because it could not run | Counts the failure and returns a hold or next-check status. |
| `.github/bible/bible_queue.py:753` | if | Gate did not pass | Applies the bounded chunk-session policy. |
| `.github/bible/bible_queue.py:761` | if | Closed chunks since the reset point reach the computed cap | Creates and returns a human hold. |
| `.github/bible/bible_queue.py:777` | conditional expression | A completed verification exists | Reads its report; otherwise leaves `facts` as `None`. |
| `.github/bible/bible_queue.py:778` | if | Report is a clean `PASS` with matching nonempty fingerprint | Creates the final component PR and returns review status. |
| `.github/bible/bible_queue.py:797` | if | A report was read (`facts` is not `None`), no chunk completed after the latest verification, and the completed verifications since the last hold release reach `MAX_VERIFY_ROUNDS` | Creates a human hold. |
| `.github/bible/bible_queue.py:806` | if | The report's fingerprint equals the pages now, its verdict is not a clean `PASS`, and no chunk completed since the verification | Starts a revision chunk and returns `session starting`. |
| `.github/bible/bible_queue.py:811-818` | call | Otherwise (no report, an old fingerprint, or a revision just merged) | Creates the verification issue and assigns it on `settings["verify_model"]`, then returns `verify running`. |

**Errors**: `component` has no handler of its own. An exception from it (a failed GitHub call, or the `RuntimeError` of an incomplete pull-request file list) goes to the per-component handler in `Queue.run`, which records `error this run (retried next run): <type>: <first 160 characters>` as that component's row and carries on with the others (`.github/bible/bible_queue.py:654-656`).

#### `Queue.follow(analysis, name, issue)`

Source: `.github/bible/bible_queue.py:821-878` <!-- code: 96d8861eb206 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:731`) |
| Calls | `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `str`, `str.startswith`, `os.path.basename`, `shown_files`, `status_of`, `as_int`, `status.get`, `issue.get`, `any`, `gh.file`, `gh.label`, `gh.merge`, `gh.unlabel`, `gh.close` |
| Purpose | Checks an assigned chunk or verification session and its PR, then retries, holds, waits, or validates and merges it. |

**Steps**

1. Sets branch `bible/<name>`, derives `verify` or `chunk` from labels, and classifies the session. Waiting returns `session starting`; start errors are held; no-start retries; running returns `<kind> running`. (`.github/bible/bible_queue.py:822-834`)
2. Defines the component ledger base and requests PR file names. A listing `RuntimeError` is retried/held. Chunk PRs may change component LLD, component API LLD and ledger files except `verification-*`; verification PRs may change only `verification-*` files and `citations.tsv` within the ledger. Disallowed paths are summarized with `shown_files` and retried/held. (`.github/bible/bible_queue.py:835-850`)
3. Reads component status at the PR head SHA. For a chunk at `WAITING_ANSWER`, adds `bible-waiting-answer` to both issue and PR only when the issue lacks it, then returns the wait status. (`.github/bible/bible_queue.py:851-857`)
4. For other chunks, compares `packets_done` at PR head with the branch, recognizes a revision from `"\nRevision ("` in issue body, and treats increased packets or `COMPONENT_DONE` as progress. `STOP` or no progress is retried; a revision must change an allowed page or `revision-log.md` and finish in `COMPONENT_DONE`, or it is retried/held. (`.github/bible/bible_queue.py:858-871`)
5. For verification, retries/holds if the report is absent at the PR head. Otherwise merges the PR, removes the waiting-answer label, closes the issue, and returns `<kind> merged`. (`.github/bible/bible_queue.py:872-878`)

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
| `.github/bible/bible_queue.py:823` | conditional expression | Issue has `bible-verify` | Sets kind to `verify`; otherwise `chunk`. |
| `.github/bible/bible_queue.py:825` | if | Session state is `waiting` | Returns `session starting`. |
| `.github/bible/bible_queue.py:827` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:830` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:832` | conditional expression | Retry succeeds | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:833` | if | Session state is `running` | Returns `<kind> running`. |
| `.github/bible/bible_queue.py:838` | except | `gh.pr_files` raises `RuntimeError` | Retries or holds because the file list cannot be validated. |
| `.github/bible/bible_queue.py:840` | conditional expression | Retry succeeds after a file-list error | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:841` | if | Kind is `chunk` | Selects the chunk allowlist; otherwise selects the verify allowlist. |
| `.github/bible/bible_queue.py:848` | if | Any changed file is outside the selected allowlist | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:850` | conditional expression | Retry succeeds after disallowed files | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:852` | if | Kind is `chunk` | Checks chunk progress; otherwise checks the verification report. |
| `.github/bible/bible_queue.py:853` | if | Status is `WAITING_ANSWER` | Checks whether to add wait labels and returns the wait state. |
| `.github/bible/bible_queue.py:854` | if | Issue lacks `bible-waiting-answer` | Adds the label to issue and PR. |
| `.github/bible/bible_queue.py:861` | if | Status is `STOP` or packet count did not increase and state is not done | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:863` | conditional expression | Retry succeeds after no progress | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:865` | if | Revision has no changed allowed page or revision log | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:868` | conditional expression | Retry succeeds after an unchanged revision | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:869` | if | Revision did not finish in `COMPONENT_DONE` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:871` | conditional expression | Retry succeeds after an incomplete revision | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:872` | elif | Verification report is absent at the PR head SHA | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:874` | conditional expression | Retry succeeds after missing report | Returns starting; otherwise needs-person. |

#### `Queue.check(analysis, name, branch)`

Source: `.github/bible/bible_queue.py:880-905` <!-- code: 4b957b96bfcc -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:747`) |
| Calls | `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `printed.stdout.strip`, `().splitlines`, `run.stdout.strip` |
| Purpose | Runs the component coverage gate against an unpacked branch tarball and obtains its pages fingerprint. |

**Steps**

1. Builds the toolkit scripts directory. If `coverage.py` is absent, logs that the gate is skipped and treated as failing, then returns `(False, None)`. (`.github/bible/bible_queue.py:882-885`)
2. Creates a temporary work directory, downloads and extracts `branch`, then runs isolated `coverage.py` with `--repo`, `--analysis`, configured `--depth`, `--component` and `--report -`. Logs the final stripped output line or `no output`. (`.github/bible/bible_queue.py:886-896`)
3. Runs isolated `status.py --fingerprint --component` in the same work tree and returns `(run.returncode == 0, printed.stdout.strip() or None)`. (`.github/bible/bible_queue.py:897-900`)
4. On `RuntimeError` from tarball retrieval, logs the cause and returns `(None, None)`; on `TimeoutExpired`, logs the timeout and returns `(None, None)`. In either case, `finally` removes the temporary directory while ignoring cleanup errors. (`.github/bible/bible_queue.py:889-892`, `.github/bible/bible_queue.py:901-905`)

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
| `.github/bible/bible_queue.py:883` | if | `coverage.py` is not a file | Logs and returns `(False, None)`. |
| `.github/bible/bible_queue.py:890` | except | Tarball retrieval raises `RuntimeError` | Logs the error and returns `(None, None)`; cleanup still runs. |
| `.github/bible/bible_queue.py:901` | except | Either subprocess exceeds `GATE_TIMEOUT` | Logs the timeout and returns `(None, None)`; cleanup still runs. |


#### `Queue.could_not_check(key, what, hold_labels, hold_title)`

Source: `.github/bible/bible_queue.py:907-918` <!-- code: d1918209875f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:749`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:968`) |
| Calls | `as_int`, `self.state.get`, `max`, `self.state.pop`, `self.gh.create_issue` |
| Purpose | Counts consecutive un-runnable checks and opens a human-hold issue after the configured threshold. |

**Steps**

1. Increments `self.state[key]` from the maximum of its existing integer value and zero, so a negative state cannot suppress the count. If the count is below `MAX_NOCHECK`, returns `None`. (`.github/bible/bible_queue.py:910-912`)
2. At the threshold, removes the count, creates a hold issue with tracker number, description, threshold, and the supplied hold labels plus `bible-hold`, `bible-needs-human` and the run label, then returns its issue number in a status string. (`.github/bible/bible_queue.py:913-918`)

**Pseudo-code**

```text
state[key] = max(as_int(state.get(key)), 0) + 1
if count < MAX_NOCHECK: return None
remove count; create labeled hold issue; return needs-person status
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:911` | if | Consecutive count is below `MAX_NOCHECK` | Returns `None` and waits for another check. |

#### `Queue.whole_fingerprint(analysis)`

Source: `.github/bible/bible_queue.py:920-935` <!-- code: c7fe54722506 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:966`) |
| Calls | `os.path.join`, `os.path.isfile`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `os.path.abspath`, `printed.stdout.strip`, `self.log`, `shutil.rmtree` |
| Purpose | Computes the analysis-page fingerprint from the default branch using the toolkit's `status.py`. |

**Steps**

1. Builds the toolkit scripts path and returns `None` if `status.py` is missing. Otherwise creates a temporary work directory and downloads the default-branch tarball. (`.github/bible/bible_queue.py:922-927`)
2. Runs isolated `status.py --fingerprint` for `analysis`, returning stripped stdout or `None` when empty. A tarball `RuntimeError` or process timeout is logged and returns `None`; `finally` removes the temporary tree. (`.github/bible/bible_queue.py:928-935`)

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
| `.github/bible/bible_queue.py:923` | if | `status.py` is not a file | Returns `None` without creating a work directory. |
| `.github/bible/bible_queue.py:931` | except | Tarball download raises `RuntimeError` or fingerprint process times out | Logs the failure and returns `None`. |

#### `Queue.assemble_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:937-1050` <!-- code: 935f3bc6544e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:667`) |
| Calls | `settings.get`, `self.run_issues`, `i.get`, `self.whole_hold`, `report_facts`, `gh.file`, `max`, `any`, `p.get`, `gh.is_agent_pr`, `gh.pr_files`, `gh.linked_prs`, `bool`, `time.monotonic`, `getattr`, `self.whole_fingerprint`, `self.could_not_check`, `self.state.pop`, `labels_of`, `gh.label`, `gh.comment`, `self.revise_all_step`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `issue_text`, `assignment`, `gh.create_issue`, `self.deferred_updates`, `self.delta`, `sorted`, `set`, `shown_files`, `type`, `str` |
| Purpose | Coordinates assembly and whole-analysis verification, revision and deferred updates, then closes the tracker when all phases finish. |

**Steps**

1. Processes the phases `bible-assemble` (model `settings["model"]`, issue text `assemble.md`) and `bible-verify-all` (model `settings["verify_model"]`, no text file) in that order; `closed_done` holds the phase's closed issues whose reason is `completed`. For verify-all it first returns the row of a whole-analysis hold that waits for a person (`whole_hold`), before any check of the whole analysis. (`.github/bible/bible_queue.py:939-946`)
2. When verify-all has closed completed issues, it reads the report on the default branch and takes the newest closed issue. `by_this_run` is true when a merged, same-repository, agent-authored pull request into the default branch, linked to that issue, touched the report and has the same report text at its head; `clean` is a `PASS` with no major correction. (`.github/bible/bible_queue.py:947-962`)
3. A clean report that is by this run and carries a fingerprint is checked against the pages now. It waits for the next check when too little of the run's time is left; a fingerprint that cannot be computed is counted toward a hold (`could_not_check`, key `nofp`, a person after 3 in a row) or waits for the next check; otherwise the `nofp` count is cleared, and when the report's fingerprint equals the pages' fingerprint the phase is done (`continue`). (`.github/bible/bible_queue.py:963-974`)
4. If the phase was not accepted in step 3 and no verify-all issue is open: a clean report (a stale `PASS`, one not by this run, or one with no fingerprint) on a newest issue that has neither the `bible-needs-revision` nor the `bible-stale-verdict` label gets `bible-stale-verdict` and a comment, and the row says the whole analysis is verified again; a report that is not clean, on a newest issue without `bible-needs-revision`, gets that label and a comment, and the row says corrections are asked. In every other case (the newest issue already carries the label, or a verify-all issue is open) the method returns nothing here and falls through to step 5; a completed verify-all phase never advances except through step 3. For the assembly phase, a closed completed issue skips the phase. (`.github/bible/bible_queue.py:975-987`)
5. For verify-all it calls `revise_all_step` and returns its row when it gives one. For an open phase issue it searches the linked pull requests for a merged, same-repository, agent-authored one into the default branch. A merged verify-all report that is not a clean `PASS` gets `bible-needs-revision`, a comment, and the issue is closed as `not_planned`; otherwise the issue is closed, and verify-all returns that its fingerprint is checked at the next check while assembly moves on. (`.github/bible/bible_queue.py:988-1011`)
6. Without a merged pull request, it returns needs-person for a held issue; classifies the session, holds start errors, retries a session that did not start, reports a running pull request, and asks `continue_if_unfinished` about a finished one. It then returns review instructions or the session state. (`.github/bible/bible_queue.py:1012-1026`)
7. With no open issue, it loads `assemble.md` or builds the whole-verification instructions, creates and assigns the issue, and returns its assigned row. (`.github/bible/bible_queue.py:1027-1035`)
8. When both phases are done, it reads the paths recorded on the tracker (`deferred_updates`) and, if there are any, hands them to `delta` with `record=False`, which creates their update issues (or one hold issue when more than 10 components are touched). An exception here is not caught in this method: the tracker stays open, `reconcile` logs it and the next check tries again. Then it comments "Done" and closes the tracker, reads the recorded paths once more and runs `delta` for those that were not in the first read; an error in that late step is commented on the closed tracker with the safe file names, and the method returns `done`. Nothing else reads the recorded paths (inferred: `deferred_updates` is called only at lines 1038 and 1043), so a tracker a person closes, or a run that never gets here, is never replayed: those paths get no update issue of their own, and the next update issue for the same component asks its session for every change since the analysis's baseline. (`.github/bible/bible_queue.py:1036-1050`, `.github/bible/bible_queue.py:607`, `.github/bible/bible_queue.py:612-615`, `.github/bible/bible_queue.py:1273-1277`)

**Pseudo-code**

```text
for phase in (assemble, verify-all):
    closed_done = the phase's closed issues with reason completed
    if verify-all:
        if a whole-run hold waits for a person: return it
        if closed_done:
            newest, facts = latest closed issue, the report on the default branch
            clean, by_this_run = PASS without majors, written by this run's merged pull request
            if clean and by_this_run and the report has a fingerprint:
                if too little run time: return wait
                pages_now = fingerprint of the default branch
                if pages_now is None: count it (hold at 3) or wait; return
                if report fingerprint == pages_now: next phase
            if clean and newest has neither label and no verify-all issue is open: label stale-verdict; return "verifying again"
            if not clean and newest lacks the revision label and no verify-all issue is open: label needs-revision; return "corrections asked"
            (any other case falls through)
    elif closed_done: next phase
    if verify-all: step = revise_all_step(); if step: return step
    if an issue of this phase is open: follow its pull request or session; return
    create the phase issue; return "session assigned"
deferred = deferred_updates(tracker)
if deferred: delta(deferred, record=False)        # an error is not caught: the tracker stays open
comment Done; close the tracker
late = deferred_updates(tracker) - deferred
if late: try delta(late) except: comment the files to update by hand
return done
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:939` | for | The assembly and verify-all phase tuples | Processes phases in order. |
| `.github/bible/bible_queue.py:943` | if | Current phase is verify-all | Checks for a whole-analysis hold first. |
| `.github/bible/bible_queue.py:945` | if | A whole-analysis hold status is returned | Stops and returns it. |
| `.github/bible/bible_queue.py:947` | if | Verify-all has completed closed issues | Validates the newest verdict. |
| `.github/bible/bible_queue.py:963` | if | Report is clean, written by this run, and has a fingerprint | Checks that fingerprint against current pages. |
| `.github/bible/bible_queue.py:964` | if | Remaining run time is insufficient for fingerprint check | Returns a wait-for-next-check status. |
| `.github/bible/bible_queue.py:967` | if | Current fingerprint could not be computed | Counts the failure and returns a hold or wait status. |
| `.github/bible/bible_queue.py:970` | conditional expression | No-check threshold was reached | Prefixes the human-hold status; otherwise returns the retry-at-next-check message. |
| `.github/bible/bible_queue.py:973` | if | Report fingerprint equals current pages fingerprint | Continues to the next phase. |
| `.github/bible/bible_queue.py:975` | if | PASS is stale/unverified, has no prior stale/revision label, and no open verifier issue exists | Labels/comments the issue as stale and returns. |
| `.github/bible/bible_queue.py:981` | if | Report is not clean and no revision label/open verifier exists | Marks the issue for revision and returns. |
| `.github/bible/bible_queue.py:984` | conditional expression | Report facts exist | Includes the report verdict in the issue comment; otherwise uses `missing`. |
| `.github/bible/bible_queue.py:985` | return | A completed verdict needs revision | Returns the corrections-requested status. |
| `.github/bible/bible_queue.py:986` | elif | A completed assembly issue exists | Skips assembly. |
| `.github/bible/bible_queue.py:988` | if | Current phase is verify-all | Runs whole-analysis revision handling. |
| `.github/bible/bible_queue.py:990` | if | Revision handler returned a status | Returns it. |
| `.github/bible/bible_queue.py:993` | if | An open issue exists for the phase | Follows its linked PR/session. |
| `.github/bible/bible_queue.py:997` | if | A qualifying merged PR exists | Closes or advances the phase. |
| `.github/bible/bible_queue.py:998` | if | The merged PR belongs to verify-all | Reads and validates the whole-analysis report. |
| `.github/bible/bible_queue.py:1000` | if | Report missing, not PASS, or has major corrections | Marks the issue for revision and closes it as not planned. |
| `.github/bible/bible_queue.py:1005` | conditional expression | Report facts exist | Reports the verdict; otherwise reports `missing`. |
| `.github/bible/bible_queue.py:1007` | return | A merged verify-all report needs revision | Returns the corrections-requested status. |
| `.github/bible/bible_queue.py:1009` | if | A merged verify-all PR passed basic report checks | Returns that fingerprint is checked on the next queue check. |
| `.github/bible/bible_queue.py:1012` | if | Open issue is held | Returns needs-person status. |
| `.github/bible/bible_queue.py:1015` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:1018` | if | Session state is `no-start` | Requests retry. |
| `.github/bible/bible_queue.py:1020` | if | PR exists and session is running | Returns running with PR number. |
| `.github/bible/bible_queue.py:1022` | if | PR exists and session is finished | Checks for a missing completion marker. |
| `.github/bible/bible_queue.py:1024` | if | Continuation helper returns a status | Returns that status. |
| `.github/bible/bible_queue.py:1026` | conditional expression | PR exists | Returns PR review instruction; otherwise returns session state. |
| `.github/bible/bible_queue.py:1027` | if | Phase has an issue-text filename | Loads its title and body; otherwise builds verification instructions. |
| `.github/bible/bible_queue.py:1039` | if | Deferred changed paths exist | Creates delta issues before closing the tracker; an exception from `delta` here is not caught and leaves the tracker open. |
| `.github/bible/bible_queue.py:1044` | if | New deferred paths arrived after the first replay | Attempts late replay after closing the tracker. |
| `.github/bible/bible_queue.py:1047` | except | Late replay raises `Exception` | Comments a manual-update notice with bounded error and safe path list. |

#### `Queue.deferred_updates(tracker)`

Source: `.github/bible/bible_queue.py:1052-1064` <!-- code: faad993a4a62 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1038`, `.github/bible/bible_queue.py:1043`) |
| Calls | `self.gh.me`, `self.gh.timeline`, `re.findall`, `e.get`, `actor.get`, `json.loads`, `isinstance`, `SAFE_FILE.match`, `sorted`, `set` |
| Purpose | Collects unique safe paths from this queue account's deferred-update comments on the tracker. |

**Steps**

1. Gets the current GitHub login and scans the tracker timeline. Ignores events that are not comments or whose actor/login is not the current account. (`.github/bible/bible_queue.py:1054-1057`)
2. Finds every `<!-- bible-deferred-update [...] -->` JSON list in each matching comment. Adds only string paths matching `SAFE_FILE`; malformed JSON is skipped. Returns a sorted list of unique paths. (`.github/bible/bible_queue.py:1058-1064`)

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
| `.github/bible/bible_queue.py:1055` | for | For each tracker timeline event | Extracts the actor and checks whether the queue authored a comment. |
| `.github/bible/bible_queue.py:1057` | if | Event is not a comment or actor login differs | Skips that event. |
| `.github/bible/bible_queue.py:1059` | for | Each embedded deferred-update marker | Parses its JSON list and filters the values. |
| `.github/bible/bible_queue.py:1062` | except | The embedded JSON is invalid | Ignores that marker and continues. |

#### `Queue.whole_hold()`

Source: `.github/bible/bible_queue.py:1066-1072` <!-- code: 6ba23ffaa54f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:944`) |
| Calls | `self.run_issues`, `labels_of`, `self.gh.close` |
| Purpose | Reports an active human hold for the whole analysis and closes holds whose human-required label was removed. |

**Steps**

1. Iterates open issues labeled `bible-hold` and `bible-whole`. If an issue has `bible-needs-human`, returns a status containing its issue number; otherwise closes it, then continues. Returns `None` if no active hold remains. (`.github/bible/bible_queue.py:1068-1072`)

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
| `.github/bible/bible_queue.py:1068` | for | For each open whole-analysis hold | Checks whether it still needs a person. |
| `.github/bible/bible_queue.py:1069` | if | Hold has `bible-needs-human` | Returns the needs-person status; otherwise closes the released hold. |

#### `Queue.revise_all_step(tracker, analysis)`

Source: `.github/bible/bible_queue.py:1074-1152` <!-- code: 86a6e2d30283 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:989`) |
| Calls | `self.run_issues`, `h.get`, `labels_of`, `gh.close`, `max`, `sorted`, `i.get`, `len`, `self.held`, `gh.linked_prs`, `p.get`, `gh.is_agent_pr`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `gh.pr_files`, `str.startswith`, `os.path.basename`, `shown_files`, `bool`, `any`, `gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Applies a whole-analysis revision round after correction verdicts, including released holds, finished PRs, bounded retries and a final human hold. |

**Steps**

1. Loads all whole-run holds and identifies open ones. Returns needs-person when the first still has `bible-needs-human`; otherwise closes it and reloads holds. Uses the latest hold close time as the start of the current round. (`.github/bible/bible_queue.py:1079-1086`)
2. Finds closed whole-verification issues labeled needs-revision and stale-verdict. If there are no correction verdicts and stale rounds remain below `MAX_VERIFY_ROUNDS`, returns `None`; otherwise counts correction/stale rounds since the last release and finds revision issues. (`.github/bible/bible_queue.py:1089-1098`)
3. For an open revision issue, closes and returns when a qualifying linked agent PR is already merged. Otherwise a held issue returns needs-person; start-error is held, no-start requests retry, running returns its PR status, and a finished PR is passed to `continue_if_unfinished`, which may ask Copilot to continue or hold the issue for a person (also at once when Copilot's work failed before it started). (`.github/bible/bible_queue.py:1099-1120`)
4. A finished revision PR may change only files under `analysis/` whose basename does not start `verification-`; disallowed files are summarized and retried/held. If no revision is open, it first computes `last_asked` (the `closed_at` of the newest closed correction verdict), `newest_stale` and `corrections_applied`, which is true when a correction verdict exists and any `bible-revise-all` issue of the run, in any state, was closed as `completed` after `last_asked`. Then, in this order: when `rounds` has reached `MAX_VERIFY_ROUNDS` it creates the whole-analysis human hold and returns the needs-person row, whether or not corrections were applied; otherwise it returns `None` when there is no correction verdict, or `corrections_applied`, or a stale verdict is newer than `last_asked` (the loop then opens the next verification); otherwise it creates and assigns a revision issue carrying the verification-report instructions. (`.github/bible/bible_queue.py:1121-1152`)

**Pseudo-code**

```text
close released hold or return human-needed
asked_all = closed verify-all issues labelled needs-revision; stale = those labelled stale-verdict since the latest release
if no correction verdict and fewer than MAX_VERIFY_ROUNDS stale ones: return None
rounds = correction verdicts since the latest release + stale ones
if open revision: follow merged, held, start-error, no-start, running and finished session states
    require finished PR files under analysis, excluding verification-*; retry/hold if invalid
    return its row (a merged revision closes it and returns None)
corrections_applied = a correction verdict exists and a revise-all issue closed as completed after the newest one
if rounds >= MAX_VERIFY_ROUNDS: create human hold; return needs-person     # whether or not corrections were applied
if no correction verdict, or corrections_applied, or a stale verdict is newer: return None   # verify again
otherwise create and assign revision issue
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1081` | if | An open hold exists | Checks whether the person label remains. |
| `.github/bible/bible_queue.py:1082` | if | Open hold has `bible-needs-human` | Returns needs-person; otherwise closes it and refreshes holds. |
| `.github/bible/bible_queue.py:1093` | if | No correction verdict exists and stale rounds are below the limit | Returns `None`. |
| `.github/bible/bible_queue.py:1099` | if | An open revision issue exists | Follows its PR/session. |
| `.github/bible/bible_queue.py:1103` | if | A qualifying linked agent PR is merged | Closes the revision issue and returns `None`. |
| `.github/bible/bible_queue.py:1106` | if | Revision issue is held | Returns needs-person. |
| `.github/bible/bible_queue.py:1109` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:1112` | if | Session state is `no-start` | Requests retry and returns session starting. |
| `.github/bible/bible_queue.py:1115` | if | PR exists and session is running | Returns the running status. |
| `.github/bible/bible_queue.py:1117` | if | PR exists and session is finished | Checks for continuation and file-scope violations. |
| `.github/bible/bible_queue.py:1119` | if | Continuation helper returns a status | Returns it. |
| `.github/bible/bible_queue.py:1123` | if | Finished PR includes a file outside `analysis/` or a `verification-*` basename | Retries or holds. |
| `.github/bible/bible_queue.py:1126` | conditional expression | Retry succeeds | Returns session starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:1127` | conditional expression | PR exists | Returns review/merge instruction; otherwise the session state. |
| `.github/bible/bible_queue.py:1128` | conditional expression | A correction verdict exists | Uses the latest correction close time; otherwise uses an empty string. |
| `.github/bible/bible_queue.py:1132` | if | `rounds` has reached `MAX_VERIFY_ROUNDS` and (there is no correction verdict, or corrections are applied, or a stale verdict is newer) | Only `pass`: control goes on to the hold at line 1136. |
| `.github/bible/bible_queue.py:1134` | elif | The same three conditions hold with `rounds` below the limit | Returns `None` so verification can proceed. |
| `.github/bible/bible_queue.py:1136` | if | `rounds` has reached `MAX_VERIFY_ROUNDS` (also when corrections are still pending) | Creates and returns a whole-analysis human hold. |

#### `Queue.continue_if_unfinished(issue, pr, kind, analysis)`

Source: `.github/bible/bible_queue.py:1154-1207` <!-- code: 076e7947548c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1023`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1118`) |
| Calls | `gh.pr_files`, `gh.me`, `max`, `e.get`, `gh.timeline`, `get`, `sorted`, `labels_of`, `gh.label`, `gh.comment`, `age`, `len`, `self.settings.get` |
| Purpose | For a session that ended before its end marker was written: holds the issue for a person at once when Copilot failed before starting, otherwise asks Copilot to continue on the same pull request, up to `MAX_CONTINUE` times. |

**Steps**

1. Chooses the end marker: `<analysis>/verification-report.md` when `kind` is `bible-verify-all`, otherwise `<analysis>/status.json`; returns `None` when the pull request's files (`pr_files`, which can raise) already include it. (`.github/bible/bible_queue.py:1162-1164`)
2. Reads the queue's own login (`gh.me()`), then `released`: the latest `unlabeled` timeline event on the issue for the label `bible-needs-human`, or the empty string. (`.github/bible/bible_queue.py:1165-1167`)
3. Reads the pull request's timeline and builds `work`, the `(event, created_at)` pairs for events in `WORK_EVENTS` performed by the `AGENT_APP` app; `finished` is the latest timestamp among those that are not `copilot_work_started` (a failure counts). (`.github/bible/bible_queue.py:1168-1171`, `.github/bible/bible_queue.py:70`)
4. `asked` is the sorted timestamps of `commented` events by the queue's login that contain `CONTINUE_MARK` and are newer than `released`; anyone else's copy of the marker text is not counted. (`.github/bible/bible_queue.py:1172-1174`, `.github/bible/bible_queue.py:85`)
5. `since` is the latest request when there is one (`asked[-1]`), otherwise `released`: the work since the queue's last request, or, before any request, since a person last released the hold (the whole history when nobody has). `after` is the names of the work events, in time order, newer than `since`. So a first session that fails before it starts is judged here too, without a continuation having been asked. (`.github/bible/bible_queue.py:1175-1178`)
6. Early hold: when the last event of `after` is `copilot_work_finished_failure` and no `copilot_work_started` is among `after`, Copilot did not run at all. If the issue does not carry `bible-needs-human` yet, labels it and comments the likely causes (the account's Copilot AI credits or monthly budget, Copilot turned off for the repository) and tells a person to fix the cause and remove the label; returns `"<kind>: Copilot could not start: see #<issue>"` without using up another continuation. (`.github/bible/bible_queue.py:1179-1188`)
7. When a request exists, is newer than `finished` and is not older than `NO_PR_AFTER` (30 minutes), returns `"<kind>: continuing (pull request #<n>)"`: Copilot has been asked and has not picked it up yet. (`.github/bible/bible_queue.py:1189-1190`, `.github/bible/bible_queue.py:74`)
8. When `len(asked) >= MAX_CONTINUE` (3), labels the issue `bible-needs-human` and comments the count and the marker, unless the label is already there; returns `"<kind>: needs a person: see #<issue>"`. (`.github/bible/bible_queue.py:1191-1197`, `.github/bible/bible_queue.py:84`)
9. Otherwise comments on the pull request `@copilot continue: run next.py ... --new-session` with `--depth` from `settings["depth"]` (default `deep`) and an ending that depends on `kind` (assemble, revise-all or verify-all), followed by `CONTINUE_MARK`; returns `"<kind>: continuing, session <len(asked)+2> (pull request #<n>)"`. (`.github/bible/bible_queue.py:1198-1207`)

**Pseudo-code**

```text
marker = verification-report.md if kind == bible-verify-all else status.json   (under analysis)
if marker in files of the pull request: return None
released = latest time a person removed bible-needs-human from the issue
work     = timeline events of the pull request in WORK_EVENTS by Copilot's app
finished = latest work event that is not copilot_work_started
asked    = queue's own bible-continue comments newer than released
since    = asked[-1] if asked else released
after    = work events newer than since
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
| `.github/bible/bible_queue.py:1162` | conditional expression | `kind` is `bible-verify-all` | the marker is `verification-report.md`; otherwise `status.json` |
| `.github/bible/bible_queue.py:1163` | if | the marker is among the pull request's files | returns `None`: the work is done |
| `.github/bible/bible_queue.py:1177` | conditional expression | at least one request of the queue is newer than the last release | `since` is the latest request; otherwise it is the release time (or the empty string) |
| `.github/bible/bible_queue.py:1179` | if | the last event after `since` is `copilot_work_finished_failure` and none of the events after `since` is `copilot_work_started` | Copilot never started: enters the early hold |
| `.github/bible/bible_queue.py:1181` | if | the issue does not have `bible-needs-human` | labels it and posts the failed-before-start comment; with the label present only the return happens |
| `.github/bible/bible_queue.py:1189` | if | a request exists, is newer than the last finished event and is at most `NO_PR_AFTER` old | returns continuing (asked, not started) |
| `.github/bible/bible_queue.py:1191` | if | `MAX_CONTINUE` requests have been made since the last release | enters the hold for a person |
| `.github/bible/bible_queue.py:1192` | if | the issue does not have `bible-needs-human` | labels it and posts the count comment; with the label present only the return happens |

**Output and side effects**: returns `None` or a one-line status string; may add the label `bible-needs-human` and a comment on the issue (early hold, or limit reached), or a `@copilot continue` comment on the pull request. The `[kind]` dictionary lookup raises `KeyError` for a kind other than the three listed (`.github/bible/bible_queue.py:1202-1205`). `pr_files` can raise the `RuntimeError` of an incomplete file list, which this method does not catch (`.github/bible/bible_queue.py:1163`).

#### `Queue.render(tracker, settings, rows)`

Source: `.github/bible/bible_queue.py:1209-1220` <!-- code: bc302114ec7d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:637`, `.github/bible/bible_queue.py:644`, `.github/bible/bible_queue.py:668`), `Queue.plan_phase` (`.github/bible/bible_queue.py:681`, `.github/bible/bible_queue.py:684`, `.github/bible/bible_queue.py:688`, `.github/bible/bible_queue.py:691`) |
| Calls | `rows.items`, `json.dumps`, `getattr`, `now`, `().isoformat`, `join`, `body.split`, `tracker.get`, `self.gh.set_body`, `self.log` |
| Purpose | Builds tracker status rows with hidden state/settings markers, updates the body when its non-time content changes, and logs each row. |

**Steps**

1. Builds a fixed introduction and table header, then appends one formatted component/state row per `rows.items()`. (`.github/bible/bible_queue.py:1210-1212`)
2. Adds a hidden `bible-state` JSON comment from `self.state` (or `{}`), an `Updated` timestamp to minute precision, and a hidden `bible-settings` JSON comment; joins the lines with newlines. (`.github/bible/bible_queue.py:1213-1216`)
3. Compares each body's text before `Updated`; calls `set_body` only when that prefix differs. It then logs each row with a 20-character padded key. (`.github/bible/bible_queue.py:1217-1220`)

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
| `.github/bible/bible_queue.py:1217` | if | Text before `Updated` differs | Replaces the tracker body. |
| `.github/bible/bible_queue.py:1219` | for | For each `(key, value)` row | Logs the padded key and state. |

#### `Queue.delta(changed, settings_analysis="codebase-analysis", record=True)`

Source: `.github/bible/bible_queue.py:1223-1283` <!-- code: 48ca17e0332c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1040`, `.github/bible/bible_queue.py:1046`), `main` (`.github/bible/bible_queue.py:1330`) |
| Calls | `gh.default_branch`, `UPDATED.search`, `t.get`, `found.group`, `gh.issues`, `age`, `last_activity`, `range`, `max`, `len`, `SAFE_FILE.match`, `gh.comment`, `json.dumps`, `json_file`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `components.component_map`, `sorted`, `p.startswith`, `NAME.match`, `gh.create_issue`, `comp_label`, `assignment`, `components.assign` |
| Purpose | Defers changed paths onto an active tracker, or opens bounded component-update issues when the assembled analysis and baseline are available. |

**Steps**

1. Sets the default branch and defines `last_activity` from the tracker body's `Updated` marker or its creation time. With `record=True`, finds active tracker issues updated within `ABANDONED_AFTER`; with `record=False`, does not search for one. (`.github/bible/bible_queue.py:1224-1229`)
2. If a tracker is active, filters changed paths through `SAFE_FILE`, splits safe paths into `DEFERRED_PER_COMMENT` chunks (at least one loop iteration), posts a marker comment for each chunk, notes omitted unusual names, logs the deferral, and returns. The recorded paths become update issues only when `assemble_phase` reaches its Done step and calls `delta` again with `record=False` (`.github/bible/bible_queue.py:1038-1046`); `reconcile` visits open trackers only, so a tracker that a person closes is never replayed (inferred: `deferred_updates` is called only at lines 1038 and 1043; `.github/bible/bible_queue.py:607`); those paths get no update issue of their own, and the next update issue for the same component asks its session for every change since the analysis's baseline (`.github/bible/bible_queue.py:1273-1277`). (`.github/bible/bible_queue.py:1230-1242`)
3. Otherwise loads `components.json` and requires `ledger/baseline.json`; if either is absent, logs and returns. Adds the analysis toolkit scripts to `sys.path`, imports `components`, maps changed paths outside the analysis and skills directories to sorted touched component names, and filters them through `NAME`. (`.github/bible/bible_queue.py:1243-1254`)
4. If the number of touched components exceeds `MAX_DELTA_ISSUES`, creates one human-needed issue only when none is already open, logs and returns. For each touched component, gets the assigned files and safe display names; an existing component delta issue is logged and skipped. Otherwise creates an assigned issue with up to 20 shown file paths and the update instructions, then logs the file count. (`.github/bible/bible_queue.py:1255-1283`)

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
| `.github/bible/bible_queue.py:1228` | conditional expression | An `Updated` marker matched | Uses the marker time; otherwise uses tracker creation time. |
| `.github/bible/bible_queue.py:1229` | conditional expression | `record` is true | Finds recently active trackers; otherwise uses an empty list. |
| `.github/bible/bible_queue.py:1230` | if | An active tracker exists | Records changes in a comment on its first issue and returns. |
| `.github/bible/bible_queue.py:1234` | for | Safe paths are chunked for comments | Posts each chunk; an empty safe list still enters one iteration. |
| `.github/bible/bible_queue.py:1238` | conditional expression | First chunk has unusual-name paths | Adds their count to the comment; otherwise adds no warning. |
| `.github/bible/bible_queue.py:1244` | if | Catalog or baseline is absent | Logs and returns without creating issues. |
| `.github/bible/bible_queue.py:1255` | if | Touched component count exceeds `MAX_DELTA_ISSUES` | Routes the change to human review and returns. |
| `.github/bible/bible_queue.py:1257` | if | No `bible-delta`/`bible-needs-human` issue exists | Creates the shared human-needed issue. |
| `.github/bible/bible_queue.py:1265` | for | For each valid touched component | Selects its changed files and issues. |
| `.github/bible/bible_queue.py:1270` | if | A component delta issue is already open | Logs and skips a duplicate. |
| `.github/bible/bible_queue.py:1280` | conditional expression | A file has an unusual name | Adds a count of hidden paths; otherwise no suffix is added. |

## Functions and methods

### `main()`

Source: `.github/bible/bible_queue.py:1286-1332` <!-- code: d5e645d7911f -->

| | |
| --- | --- |
| Kind | module entry point |
| Called by | Module guard (`.github/bible/bible_queue.py:1335-1336`) |
| Calls | `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str`, `args.verify_model.strip`, `args.components.split`, `json.dumps`, `issue.get`, `open`, `l.strip`, `NAME.match` |
| Purpose | Parses `start`, `reconcile`, and `delta` commands and dispatches to the queue workflow. |

**Steps**

1. Builds a required-subcommand parser from the module docstring's first line; defines `start` options including `--analysis` and `--depth`, `reconcile`, and `delta` options, then parses arguments. (`.github/bible/bible_queue.py:1287-1300`)
2. Reads `GITHUB_REPOSITORY` and `GH_TOKEN`; raises `SystemExit` if either is falsey, then constructs `GitHub` and `Queue`. (`.github/bible/bible_queue.py:1302-1306`)
3. For `start`, requires a nonempty verification model different from the normal model, parses component names, and requires at least one selection with each name either `all` or matching `NAME`. (`.github/bible/bible_queue.py:1308-1313`)
4. Ensures labels and exits if a tracker is already open. Builds settings, then calls `settings_of` on the generated marker; if validation rejects the settings, raises `SystemExit` explaining the allowed analysis path, depth, and model characters. Otherwise it creates a tracker issue with hidden settings JSON and prints its issue number and queue-start guidance. (`.github/bible/bible_queue.py:1314-1324`)
5. For `reconcile`, invokes `queue.reconcile`; otherwise reads nonempty stripped lines from the changed-file input and calls `queue.delta`. (`.github/bible/bible_queue.py:1325-1330`)
6. Converts `RuntimeError` from command handling to `SystemExit` with the error text. (`.github/bible/bible_queue.py:1331-1332`)

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
| `.github/bible/bible_queue.py:1303` | if | Repository or token is missing | Exits with an environment requirement. |
| `.github/bible/bible_queue.py:1304` | raise | Required environment is missing | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1308` | if | Command is `start` | Validates and starts a run. |
| `.github/bible/bible_queue.py:1309` | if | Verification model is empty or equals normal model | Exits with the model requirement. |
| `.github/bible/bible_queue.py:1310` | raise | Model validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1312` | if | No component names are supplied, or a name other than `all` fails `NAME` | Exits with component-selection guidance. |
| `.github/bible/bible_queue.py:1313` | raise | Selection validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1315` | if | Tracker already exists | Exits without starting another run. |
| `.github/bible/bible_queue.py:1316` | raise | Open tracker exists | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1319` | if | Generated settings fail `settings_of` validation | Exits with the settings requirement. |
| `.github/bible/bible_queue.py:1320-1321` | raise | Generated settings are unsafe or unsupported | Raises `SystemExit` with allowed path, depth, and model rules. |
| `.github/bible/bible_queue.py:1325` | elif | Command is `reconcile` | Calls `queue.reconcile`. |
| `.github/bible/bible_queue.py:1327` | else | Command is `delta` | Reads changed paths and calls `queue.delta`. |
| `.github/bible/bible_queue.py:1331` | except | Command handling raises `RuntimeError` | Converts it to `SystemExit`. |
| `.github/bible/bible_queue.py:1332` | raise | A `RuntimeError` was caught | Raises `SystemExit` with the error text. |
| `.github/bible/bible_queue.py:1335` | if | Module is run as a script | Calls `main`. |
| `.github/bible/bible_queue.py:1336` | call | Script guard is active | Dispatches the CLI entry point. |

### `now()`

Source: `.github/bible/bible_queue.py:379-381` <!-- code: 9fb56903ebfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `age` (`.github/bible/bible_queue.py:385`), `Queue.render` (`.github/bible/bible_queue.py:1214`) |
| Calls | `os.environ.get`, `datetime.datetime.fromisoformat`, `datetime.datetime.now`, `replace` |
| Purpose | Returns the configured test time or the current UTC time. |

**Steps**

1. Reads `BIBLE_NOW`. (`.github/bible/bible_queue.py:380`)
2. If set, replaces `Z` with `+00:00` and parses the ISO timestamp; otherwise returns the current timezone-aware UTC datetime. (`.github/bible/bible_queue.py:381`)

**Pseudo-code**

```text
stamp = BIBLE_NOW
if stamp: parse ISO stamp after replacing Z with +00:00
else: return current UTC time
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:381` | conditional expression | `stamp` is truthy | Parses the configured time; otherwise obtains current UTC time. |

### `age(stamp)`

Source: `.github/bible/bible_queue.py:384-385` <!-- code: f2f8bb65e56f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:523`, `.github/bible/bible_queue.py:527`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1189`), `Queue.delta` (`.github/bible/bible_queue.py:1229`) |
| Calls | `now`, `datetime.datetime.fromisoformat`, `replace`, `total_seconds` |
| Purpose | Returns elapsed seconds between `stamp` and `now()`. |

**Steps**

1. Replaces `Z` in `stamp` with `+00:00`, parses it as an ISO datetime, subtracts it from `now()`, and returns `total_seconds()`. (`.github/bible/bible_queue.py:385`)

**Pseudo-code**

```text
return (now() - parse ISO stamp after replacing Z with +00:00).total_seconds()
```

### `shown_files(paths, limit=10)`

Source: `.github/bible/bible_queue.py:397-402` <!-- code: 42118ce2fbc4 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:849`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1049`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1125`) |
| Calls | `SAFE_FILE.match`, `len`, `join` |
| Purpose | Formats safe paths for issue text and summarizes paths with unusual characters without quoting them. |

**Steps**

1. Partitions `paths` into names matching `SAFE_FILE` and the count that do not. Formats at most `limit` safe names in backticks, appending a count for additional safe names and a separate count for unusual names. (`.github/bible/bible_queue.py:398-402`)

**Pseudo-code**

```text
plain = paths matching SAFE_FILE
other = len(paths) - len(plain)
return quoted first limit names + counts of remaining safe and unusual names
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:401` | conditional expression | More safe names exist than `limit` | Adds the number of omitted safe names; otherwise adds nothing. |
| `.github/bible/bible_queue.py:402` | conditional expression | At least one path has unusual characters | Adds the count without including those paths; otherwise adds nothing. |

### `settings_of(tracker)`

Source: `.github/bible/bible_queue.py:405-425` <!-- code: 828d76009663 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:608`), `main` (`.github/bible/bible_queue.py:1319`) |
| Calls | `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group`, `isinstance`, `str`, `data.get`, `SAFE_PATH.match`, `analysis.split`, `SAFE_MODEL.match` |
| Purpose | Parses and validates the JSON settings marker from a tracker, returning `None` when absent, malformed, or unsafe. |

**Steps**

1. Searches the tracker body, defaulting a missing or falsey body to an empty string, and parses the marker's first capture group when present. (`.github/bible/bible_queue.py:411-412`)
2. Returns `None` for invalid JSON or a non-dictionary parsed value. (`.github/bible/bible_queue.py:413-414`)
3. Reads `analysis`, defaulting to `codebase-analysis`, and rejects paths that fail `SAFE_PATH` or contain `..` path segments. (`.github/bible/bible_queue.py:415-417`)
4. Rejects depths outside `DEPTH_VALUES`, and rejects nonempty `model` or `verify_model` values that fail `SAFE_MODEL`. (`.github/bible/bible_queue.py:418-423`)
5. Returns the validated settings dictionary. (`.github/bible/bible_queue.py:425`)

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
| `.github/bible/bible_queue.py:411` | conditional expression | A settings marker matched | Parses its first group; otherwise uses `None`. |
| `.github/bible/bible_queue.py:412` | except | JSON parsing raises `ValueError` | Returns `None`. |
| `.github/bible/bible_queue.py:414` | if | Parsed value is not a dictionary | Returns `None`. |
| `.github/bible/bible_queue.py:417` | if | Analysis path is unsafe | Returns `None`. |
| `.github/bible/bible_queue.py:419` | if | Depth is not an allowed value | Returns `None`. |
| `.github/bible/bible_queue.py:421` | for | For `model` and `verify_model` | Validates each configured model value. |
| `.github/bible/bible_queue.py:423` | if | A nonempty model fails `SAFE_MODEL` | Returns `None`. |

### `labels_of(item)`

Source: `.github/bible/bible_queue.py:428-429` <!-- code: 7a809f2b23af -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:529`), `Queue.held` (`.github/bible/bible_queue.py:543`, `.github/bible/bible_queue.py:558`), `Queue.model_for` (`.github/bible/bible_queue.py:571`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:599`), `Queue.component` (`.github/bible/bible_queue.py:737`), `Queue.follow` (`.github/bible/bible_queue.py:823`, `.github/bible/bible_queue.py:854`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:975`, `.github/bible/bible_queue.py:981`), `Queue.whole_hold` (`.github/bible/bible_queue.py:1069`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1082`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1181`, `.github/bible/bible_queue.py:1192`) |
| Calls | `item.get`, `isinstance` |
| Purpose | Returns a set of label names from strings or label objects. |

**Steps**

1. Reads `labels`, defaulting to an empty list; for each element, uses its `name` when it is a dictionary and otherwise keeps the element itself. (`.github/bible/bible_queue.py:429`)

**Pseudo-code**

```text
return {label["name"] if label is a dict else label
        for label in item.labels or []}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:429` | conditional expression | A label item is a dict | Uses `item["name"]`; otherwise preserves the item value. |

### `comp_label(name)`

Source: `.github/bible/bible_queue.py:432-433` <!-- code: 5ead08c5004d -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:700`, `.github/bible/bible_queue.py:705`), `Queue.component` (`.github/bible/bible_queue.py:720`, `.github/bible/bible_queue.py:732`, `.github/bible/bible_queue.py:734`, `.github/bible/bible_queue.py:740`, `.github/bible/bible_queue.py:749`, `.github/bible/bible_queue.py:756`, `.github/bible/bible_queue.py:769`, `.github/bible/bible_queue.py:771`, `.github/bible/bible_queue.py:774`, `.github/bible/bible_queue.py:776`, `.github/bible/bible_queue.py:793`, `.github/bible/bible_queue.py:804`, `.github/bible/bible_queue.py:818`), `Queue.delta` (`.github/bible/bible_queue.py:1270`, `.github/bible/bible_queue.py:1282`) |
| Calls | None |
| Purpose | Prefixes a component name with `bible/`. |

**Steps**

1. Returns the string `bible/` followed by `name`. (`.github/bible/bible_queue.py:433`)

**Pseudo-code**

```text
return "bible/" + name
```

### `issue_text(gh, path, ref, fallback_title)`

Source: `.github/bible/bible_queue.py:436-442` <!-- code: 0533b3261be5 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:674`), `Queue.start_chunk` (`.github/bible/bible_queue.py:702`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1028`) |
| Calls | `gh.file`, `splitlines`, `startswith`, `strip`, `join`, `len` |
| Purpose | Reads a title/body pair from a ledger issue file, with a fallback title when no header exists. |

**Steps**

1. Reads the file through `gh.file`, converting a falsey result to `""`, then splits it into lines. (`.github/bible/bible_queue.py:438-439`)
2. If the first line starts with `Title:`, returns its stripped suffix as the title and the stripped remaining lines joined by newlines as the body. (`.github/bible/bible_queue.py:440-441`)
3. Otherwise returns `fallback_title` and the stripped full text. (`.github/bible/bible_queue.py:442`)

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
| `.github/bible/bible_queue.py:440` | if | `lines` is nonempty and the first line starts with `Title:` | Returns header title and remaining body; otherwise returns fallback title and full text. |

### `assignment(gh, base, model)`

Source: `.github/bible/bible_queue.py:445-449` <!-- code: da5ca422ae7f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:566`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:600`), `Queue.plan_phase` (`.github/bible/bible_queue.py:680`), `Queue.start_chunk` (`.github/bible/bible_queue.py:706`), `Queue.component` (`.github/bible/bible_queue.py:818`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1034`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1151`), `Queue.delta` (`.github/bible/bible_queue.py:1282`) |
| Calls | None |
| Purpose | Builds the target repository and base-branch assignment, optionally including a model. |

**Steps**

1. Initializes the result with `target_repo: gh.repo` and `base_branch: base`. (`.github/bible/bible_queue.py:446`)
2. Adds `model` only when truthy, then returns the result. (`.github/bible/bible_queue.py:447-449`)

**Pseudo-code**

```text
out = {target_repo: gh.repo, base_branch: base}
if model: out.model = model
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:447` | if | `model` is truthy | Adds `model` to the assignment. |

### `json_file(gh, path, ref)`

Source: `.github/bible/bible_queue.py:452-457` <!-- code: 37acfbecddfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `status_of` (`.github/bible/bible_queue.py:494`), `Queue.run` (`.github/bible/bible_queue.py:628`), `Queue.delta` (`.github/bible/bible_queue.py:1243`) |
| Calls | `gh.file`, `json.loads` |
| Purpose | Reads a file and parses JSON, returning `None` for missing or invalid content. |

**Steps**

1. Reads the file using `gh.file`. (`.github/bible/bible_queue.py:453`)
2. Returns parsed JSON for truthy text, or `None` when the text is falsey. (`.github/bible/bible_queue.py:454-455`)
3. Returns `None` if parsing raises `ValueError`. (`.github/bible/bible_queue.py:456-457`)

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
| `.github/bible/bible_queue.py:455` | conditional expression | `text` is truthy | Parses JSON; otherwise returns `None`. |
| `.github/bible/bible_queue.py:456` | except | JSON parsing raises `ValueError` | Returns `None`. |

### `section(text, title)`

Source: `.github/bible/bible_queue.py:460-466` <!-- code: 55167fd6e3c2 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `report_facts` (`.github/bible/bible_queue.py:479`) |
| Calls | `re.search`, `re.escape`, `match.end`, `nxt.start` |
| Purpose | Returns a Markdown level-two section's text, or an empty string if its heading is absent. |

**Steps**

1. Searches for a line matching exactly a level-two heading with the escaped `title`. (`.github/bible/bible_queue.py:461`)
2. Returns `""` if no heading matches. (`.github/bible/bible_queue.py:462-463`)
3. Slices text after the matched heading through the next level-two heading, or through end of text when there is no next heading. (`.github/bible/bible_queue.py:464-466`)

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
| `.github/bible/bible_queue.py:462` | if | No heading matched | Returns an empty string. |
| `.github/bible/bible_queue.py:466` | conditional expression | A next level-two heading matched | Returns the section before it; otherwise returns the remaining text. |

### `report_facts(text)`

Source: `.github/bible/bible_queue.py:469-482` <!-- code: a367c151c5b0 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:777`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:950`, `.github/bible/bible_queue.py:999`) |
| Calls | `re.sub`, `re.findall`, `len`, `sum`, `splitlines`, `startswith`, `re.search`, `section`, `lstrip`, `upper`, `printed.group` |
| Purpose | Extracts a verification verdict, major-correction count, and optional analysis fingerprint. |

**Steps**

1. Returns `None` for falsey `text`. (`.github/bible/bible_queue.py:472-473`)
2. Removes HTML comments and fenced code blocks, then finds visible `Verdict` values and rows. (`.github/bible/bible_queue.py:474-476`)
3. Returns `("UNREADABLE", 0, None)` unless exactly one accepted verdict and exactly one verdict row were found. (`.github/bible/bible_queue.py:477-478`)
4. Counts lines in the `Corrections` section that begin with `|` and contain a `major` cell. (`.github/bible/bible_queue.py:479-480`)
5. Searches for a 16-character lowercase hexadecimal fingerprint and returns the uppercased verdict, count, and captured fingerprint or `None`. (`.github/bible/bible_queue.py:481-482`)

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
| `.github/bible/bible_queue.py:472` | if | `text` is falsey | Returns `None`. |
| `.github/bible/bible_queue.py:477` | if | Verdict or verdict-row count is not exactly one | Returns `("UNREADABLE", 0, None)`. |
| `.github/bible/bible_queue.py:482` | conditional expression | Fingerprint regex matched | Returns its group 1; otherwise returns `None` in that tuple position. |

### `as_int(value)`

Source: `.github/bible/bible_queue.py:485-489` <!-- code: bc184bba1eba -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `GitHub.pr_files` (`.github/bible/bible_queue.py:268`, `.github/bible/bible_queue.py:277`), `Queue.run` (`.github/bible/bible_queue.py:658`), `Queue.component` (`.github/bible/bible_queue.py:759`), `Queue.follow` (`.github/bible/bible_queue.py:858`, `.github/bible/bible_queue.py:860`), `Queue.could_not_check` (`.github/bible/bible_queue.py:910`) |
| Calls | `int` |
| Purpose | Converts a value to an integer, returning zero for conversion type, value or overflow errors. |

**Steps**

1. Returns `int(value)` when conversion succeeds; catches `TypeError`, `ValueError` or `OverflowError` and returns `0`. (`.github/bible/bible_queue.py:486-489`)

**Pseudo-code**

```text
try: return int(value)
on TypeError, ValueError or OverflowError: return 0
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:488` | except | `int(value)` raises `TypeError`, `ValueError` or `OverflowError` | Returns zero. |

### `status_of(gh, path, ref)`

Source: `.github/bible/bible_queue.py:492-495` <!-- code: ad9adb38e0f7 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:530`), `Queue.component` (`.github/bible/bible_queue.py:742`), `Queue.follow` (`.github/bible/bible_queue.py:851`, `.github/bible/bible_queue.py:858`) |
| Calls | `json_file`, `isinstance` |
| Purpose | Returns parsed component status only when the loaded JSON is a dictionary. |

**Steps**

1. Loads `path` at `ref` with `json_file`. (`.github/bible/bible_queue.py:494`)
2. Returns the loaded data if it is a dictionary; otherwise returns `{}`. (`.github/bible/bible_queue.py:495`)

**Pseudo-code**

```text
data = json_file(gh, path, ref)
return data if data is a dict, otherwise {}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:495` | conditional expression | `data` is a dictionary | Returns `data`; otherwise returns `{}`. |

## Module-level code

The module imports Python standard-library utilities and initializes queue labels, environment-derived agent settings, regexes, and timing/verification constants. (`.github/bible/bible_queue.py:42-105`). The tuple `WORK_EVENTS` lists the timeline events that count as Copilot's work: `copilot_work_started`, `copilot_work_finished` and `copilot_work_finished_failure` (`.github/bible/bible_queue.py:70`).

It declares the `GitHub` API client (`.github/bible/bible_queue.py:110-374`), helper functions (`.github/bible/bible_queue.py:379-495`), and `Queue` coordinator (`.github/bible/bible_queue.py:500-1283`). The CLI `main` parses arguments, and the module guard calls it when executed as a script. (`.github/bible/bible_queue.py:1286-1336`)

## Surprises

`tarball` limits download/member sizes, filters archive members to regular files and directories, and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:295-330`)

The `Queue.session` docstring lists four result states, but the code also returns `start-error` when `GitHub.start_error` is truthy. (`.github/bible/bible_queue.py:518`, `.github/bible/bible_queue.py:521-522`)

`GitHub.pr_files` does not trust the file list GitHub gives for an open pull request whose base branch has moved: it compares the head with the base branch's tip (`/compare/<tip>...<head>`) and refuses a comparison with no list, or with `COMPARE_MAX` (300) files or more. (`.github/bible/bible_queue.py:258-273`, `.github/bible/bible_queue.py:71`)

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->
