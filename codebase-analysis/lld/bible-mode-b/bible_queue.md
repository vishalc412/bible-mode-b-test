---
id: lld/bible-mode-b/bible_queue
kind: module
component: bible-mode-b
source: .github/bible/bible_queue.py
summary: Coordinates Mode B issue workflows through GitHub REST and GraphQL
reads: [file:changed-path-list, config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
writes: [file:temporary-gate-workspace]
calls: [external:GitHub, external:Analysis toolkit]
uses: [symbol:GitHub, symbol:Queue]
config: [config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
exposes: []
---

# bible_queue

Source file: `.github/bible/bible_queue.py`

| | |
| --- | --- |
| Component | `bible-mode-b` (its design page is `README.md` in this folder) |
| Lines | 1434 |
| Role | Runs the Mode B analysis queue and its GitHub API client. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, subprocess, and filesystem modules used by the API client, queue, and CLI. (`.github/bible/bible_queue.py:42-56`) |
| Module-level state | Constants and labels are initialized at import; environment-backed values include `BIBLE_AGENT_LOGINS` and `BIBLE_AGENT_APP`; `WORK_EVENTS` names the three Copilot timeline events the queue reads (`copilot_work_started`, `copilot_work_finished`, `copilot_work_finished_failure`). `COMPARE_MAX` (300) is the number of files GitHub's comparison of two commits lists at most (assumed: GitHub behaviour, stated in the comment at line 71); the queue refuses a comparison that lists 300 files or more, so it accepts fewer than 300. The closed-run replay mark `REPLAYED_MARK` (`<!-- bible-deferred-replayed -->`) is a module constant, and `LABELS` includes `bible-replayed` (`.github/bible/bible_queue.py:94`, `.github/bible/bible_queue.py:391`). The report-reading rules are module constants too: the regexes `RECHECK_LINE`, `ACCURACY_ROW`, `RECHECK_OF_ROW` and `REPORT_NAME`, the threshold `RECHECK_MIN_ACCURACY` (95.0) and the text `RECHECK_ASK` that a verification issue carries when a re-check is due (`.github/bible/bible_queue.py:471-475`, `.github/bible/bible_queue.py:510-513`). (`.github/bible/bible_queue.py:60-106`, `.github/bible/bible_queue.py:61`, `.github/bible/bible_queue.py:66`, `.github/bible/bible_queue.py:70`, `.github/bible/bible_queue.py:71`) |

## Summary

`main` exposes the `start`, `reconcile`, and `delta` CLI commands. It constructs `Queue` and `GitHub`; `Queue` coordinates tracker/session state and delegates repository operations to `GitHub`, whose methods build REST requests and a GraphQL ready-for-review mutation. `Queue.delta` also imports component-membership helpers from the analysis toolkit. (`.github/bible/bible_queue.py:1384-1430`, `.github/bible/bible_queue.py:560-1381`, `.github/bible/bible_queue.py:111-375`, `.github/bible/bible_queue.py:1345-1346`)

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| `GitHub` | class | 111-375 | [class](#github) |
| `GitHub.__init__` | method | 112-115 | [card](#github__init__repo-token-apinone) |
| `GitHub.request` | method | 117-126 | [card](#githubrequestmethod-url-bodynone-timeout60) |
| `GitHub.call` | method | 128-140 | [card](#githubcallmethod-path-bodynone-ok404false) |
| `GitHub.paged` | method | 142-150 | [card](#githubpagedpath) |
| `GitHub.issues` | method | 152-154 | [card](#githubissueslabels-stateopen) |
| `GitHub.ensure_label` | method | 156-161 | [card](#githubensure_labelname-whycodebase-analysis-run) |
| `GitHub.ensure_labels` | method | 163-165 | [card](#githubensure_labels) |
| `GitHub.create_issue` | method | 167-174 | [card](#githubcreate_issuetitle-body-labels-assignnone) |
| `GitHub.me` | method | 176-180 | [card](#githubme) |
| `GitHub.default_branch` | method | 182-183 | [card](#githubdefault_branch) |
| `GitHub.branch_sha` | method | 185-187 | [card](#githubbranch_shabranch) |
| `GitHub.create_branch` | method | 189-190 | [card](#githubcreate_branchbranch-sha) |
| `GitHub.reset_branch` | method | 192-193 | [card](#githubreset_branchbranch-sha) |
| `GitHub.file` | method | 195-199 | [card](#githubfilepath-ref) |
| `GitHub.prs` | method | 201-203 | [card](#githubprsbasenone-stateopen) |
| `GitHub.timeline` | method | 205-206 | [card](#githubtimelinenumber) |
| `GitHub.linked_prs` | method | 208-217 | [card](#githublinked_prsnumber) |
| `GitHub.branch_prs` | method | 219-222 | [card](#githubbranch_prsbranch-base) |
| `GitHub.agent_events` | method | 224-228 | [card](#githubagent_eventsnumber) |
| `GitHub.is_agent_pr` | method | 230-235 | [card](#githubis_agent_prpr) |
| `GitHub.start_error` | method | 237-246 | [card](#githubstart_errorissue) |
| `GitHub.assigned_at` | method | 248-251 | [card](#githubassigned_atissue) |
| `GitHub.pr_files` | method | 253-287 | [card](#githubpr_filesnumber) |
| `GitHub.commit_time` | method | 289-290 | [card](#githubcommit_timesha) |
| `GitHub.tarball` | method | 292-331 | [card](#githubtarballref-dest) |
| `GitHub.label` | method | 333-335 | [card](#githublabelnumber-name) |
| `GitHub.unlabel` | method | 337-338 | [card](#githubunlabelnumber-name) |
| `GitHub.comment` | method | 340-341 | [card](#githubcommentnumber-text) |
| `GitHub.close` | method | 343-344 | [card](#githubclosenumber-reasoncompleted) |
| `GitHub.set_body` | method | 346-347 | [card](#githubset_bodynumber-body) |
| `GitHub.unassign` | method | 349-350 | [card](#githubunassignnumber) |
| `GitHub.assign` | method | 352-353 | [card](#githubassignnumber-assign) |
| `GitHub.ready` | method | 355-363 | [card](#githubreadypr) |
| `GitHub.merge` | method | 365-369 | [card](#githubmergepr-title) |
| `GitHub.close_pr` | method | 371-372 | [card](#githubclose_prnumber) |
| `GitHub.create_pr` | method | 374-375 | [card](#githubcreate_prhead-base-title-body) |
| `now` | function | 380-382 | [card](#now) |
| `age` | function | 385-386 | [card](#agestamp) |
| `shown_files` | function | 399-404 | [card](#shown_filespaths-limit10) |
| `settings_of` | function | 407-427 | [card](#settings_oftracker) |
| `labels_of` | function | 430-431 | [card](#labels_ofitem) |
| `comp_label` | function | 434-435 | [card](#comp_labelname) |
| `issue_text` | function | 438-444 | [card](#issue_textgh-path-ref-fallback_title) |
| `assignment` | function | 447-451 | [card](#assignmentgh-base-model) |
| `json_file` | function | 454-459 | [card](#json_filegh-path-ref) |
| `section` | function | 462-468 | [card](#sectiontext-title) |
| `report_facts` | function | 478-507 | [card](#report_factstext-fetchnone-depth0) |
| `recheck_due` | function | 516-520 | [card](#recheck_duefacts) |
| `accepted` | function | 523-542 | [card](#acceptedfacts) |
| `as_int` | function | 545-549 | [card](#as_intvalue) |
| `status_of` | function | 552-555 | [card](#status_ofgh-path-ref) |
| `Queue` | class | 560-1381 | [class](#queue) |
| `Queue.__init__` | method | 561-563 | [card](#queue__init__gh-logprint) |
| `Queue.run_issues` | method | 565-566 | [card](#queuerun_issueslabels-stateopen) |
| `Queue.agent_pr` | method | 568-574 | [card](#queueagent_prissue-base) |
| `Queue.session` | method | 577-593 | [card](#queuesessionissue-base-analysis-compnone) |
| `Queue.held` | method | 595-628 | [card](#queueheldissue) |
| `Queue.model_for` | method | 630-632 | [card](#queuemodel_forissue) |
| `Queue.hold_start_error` | method | 634-640 | [card](#queuehold_start_errorissue) |
| `Queue.fail_or_retry` | method | 642-661 | [card](#queuefail_or_retryissue-pr-why) |
| `Queue.reconcile` | method | 664-679 | [card](#queuereconcile) |
| `Queue.replay_closed_runs` | method | 681-697 | [card](#queuereplay_closed_runs) |
| `Queue.replayed` | method | 699-703 | [card](#queuereplayedtracker) |
| `Queue.run` | method | 705-756 | [card](#queueruntracker-settings) |
| `Queue.plan_phase` | method | 758-780 | [card](#queueplan_phasetracker-settings-analysis) |
| `Queue.start_chunk` | method | 782-794 | [card](#queuestart_chunkanalysis-name-freshfalse-note) |
| `Queue.component` | method | 796-909 | [card](#queuecomponentanalysis-name) |
| `Queue.follow` | method | 911-968 | [card](#queuefollowanalysis-name-issue) |
| `Queue.check` | method | 970-995 | [card](#queuecheckanalysis-name-branch) |
| `Queue.could_not_check` | method | 997-1008 | [card](#queuecould_not_checkkey-what-hold_labels-hold_title) |
| `Queue.whole_fingerprint` | method | 1010-1025 | [card](#queuewhole_fingerprintanalysis) |
| `Queue.assemble_phase` | method | 1027-1148 | [card](#queueassemble_phasetracker-settings-analysis) |
| `Queue.deferred_updates` | method | 1150-1162 | [card](#queuedeferred_updatestracker) |
| `Queue.whole_hold` | method | 1164-1170 | [card](#queuewhole_hold) |
| `Queue.revise_all_step` | method | 1172-1250 | [card](#queuerevise_all_steptracker-analysis) |
| `Queue.continue_if_unfinished` | method | 1252-1305 | [card](#queuecontinue_if_unfinishedissue-pr-kind-analysis) |
| `Queue.render` | method | 1307-1318 | [card](#queuerendertracker-settings-rows) |
| `Queue.delta` | method | 1321-1381 | [card](#queuedeltachanged-settings_analysiscodebase-analysis-recordtrue) |
| `main` | function | 1384-1430 | [card](#main) |

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
  recheckdue["recheck_due"]
  accepted["accepted"]
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
  replayclosed["Queue.replay_closed_runs"]
  replayed["Queue.replayed"]
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
  reportfacts -->|"report_facts"| reportfacts
  reconcile -->|"replay_closed_runs"| replayclosed
  replayclosed -->|"issues"| issues
  replayclosed -->|"labels_of"| labelsof
  replayclosed -->|"replayed"| replayed
  replayclosed -->|"deferred_updates"| deferredupdates
  replayclosed -->|"settings_of"| settingsof
  replayclosed -->|"delta"| delta
  replayclosed -->|"comment"| comment
  replayclosed -->|"label"| label
  replayed -->|"me"| me
  replayed -->|"timeline"| timeline
  component -->|"accepted"| accepted
  component -->|"recheck_due"| recheckdue
  assemblephase -->|"accepted"| accepted
  assemblephase -->|"recheck_due"| recheckdue
```

## Classes

### `GitHub`

Source: `.github/bible/bible_queue.py:111-375`

`GitHub` is a client for repository-scoped GitHub REST operations and the GraphQL ready-for-review mutation. Its instance fields are `repo`, `token`, normalized `api`, and `known_labels`; the last begins as `None` and is populated by `ensure_label`. A fifth field, `_me`, is not set in the constructor: `me` creates it on its first call (`getattr(self, "_me", None)`) and caches the login of the token's owner. (`.github/bible/bible_queue.py:112-115`, `.github/bible/bible_queue.py:156-161`, `.github/bible/bible_queue.py:176-180`) `pr_files` also uses the comparison endpoint (`/compare/<base tip>...<head>`) for an open pull request whose base branch has moved, and `is_agent_pr` accepts any of the three `WORK_EVENTS` as proof that a pull request is Copilot's. (`.github/bible/bible_queue.py:230-235`, `.github/bible/bible_queue.py:253-287`)

No type annotations or factory are declared for the class; callers provide its constructor values. (inferred: `.github/bible/bible_queue.py:111-115`)

#### `GitHub.__init__(repo, token, api=None)`

Source: `.github/bible/bible_queue.py:112-115` <!-- code: b511658beb68 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1403`) |
| Calls | `os.environ.get`, `rstrip` |
| Purpose | Stores API credentials and a slash-trimmed API base URL, then initializes the label cache. |

**Steps**

1. Assigns `repo` and `token` to the instance. (`.github/bible/bible_queue.py:113`)
2. Selects `api`, then `GITHUB_API_URL`, then `https://api.github.com`, and removes trailing `/` characters. (`.github/bible/bible_queue.py:114`)
3. Initializes `known_labels` to `None`. (`.github/bible/bible_queue.py:115`)

**Pseudo-code**

```text
self.repo, self.token = repo, token
self.api = (api or GITHUB_API_URL or "https://api.github.com").rstrip("/")
self.known_labels = None
```

#### `GitHub.request(method, url, body=None, timeout=60)`

Source: `.github/bible/bible_queue.py:117-126` <!-- code: 1f8902892005 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.call` (`.github/bible/bible_queue.py:131`), `GitHub.tarball` (`.github/bible/bible_queue.py:298`), `GitHub.ready` (`.github/bible/bible_queue.py:360`) |
| Calls | `json.dumps`, `encode`, `urllib.request.Request`, `req.add_header`, `urllib.request.urlopen` |
| Purpose | Builds and opens an HTTP request with GitHub headers and an optional JSON body. |

**Steps**

1. Serializes a non-`None` body as encoded JSON; otherwise leaves request data unset. (`.github/bible/bible_queue.py:118`)
2. Creates a request using the supplied URL, method, and body bytes, and adds GitHub's JSON accept and API-version headers. (`.github/bible/bible_queue.py:119-121`)
3. Adds a bearer authorization header only when `token` is truthy, and adds JSON content type only when a body was serialized. (`.github/bible/bible_queue.py:122-125`)
4. Returns `urlopen`'s response using the supplied timeout. (`.github/bible/bible_queue.py:126`)

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
| `.github/bible/bible_queue.py:118` | conditional expression | `body is not None` | JSON is encoded; otherwise `data` is `None`. |
| `.github/bible/bible_queue.py:122` | if | `self.token` is truthy | Adds the bearer authorization header. |
| `.github/bible/bible_queue.py:124` | if | `data is not None` | Adds the JSON content-type header. |

#### `GitHub.call(method, path, body=None, ok404=False)`

Source: `.github/bible/bible_queue.py:128-140` <!-- code: 753c5f1a3922 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.paged` (`.github/bible/bible_queue.py:146`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:160`), `GitHub.create_issue` (`.github/bible/bible_queue.py:174`), `GitHub.me` (`.github/bible/bible_queue.py:179`), `GitHub.default_branch` (`.github/bible/bible_queue.py:183`), `GitHub.branch_sha` (`.github/bible/bible_queue.py:186`), `GitHub.create_branch` (`.github/bible/bible_queue.py:190`), `GitHub.reset_branch` (`.github/bible/bible_queue.py:193`), `GitHub.file` (`.github/bible/bible_queue.py:196`), `GitHub.linked_prs` (`.github/bible/bible_queue.py:216`), `GitHub.pr_files` (`.github/bible/bible_queue.py:256`, `.github/bible/bible_queue.py:266`), `GitHub.commit_time` (`.github/bible/bible_queue.py:290`), `GitHub.label` (`.github/bible/bible_queue.py:335`), `GitHub.unlabel` (`.github/bible/bible_queue.py:338`), `GitHub.comment` (`.github/bible/bible_queue.py:341`), `GitHub.close` (`.github/bible/bible_queue.py:344`), `GitHub.set_body` (`.github/bible/bible_queue.py:347`), `GitHub.unassign` (`.github/bible/bible_queue.py:350`), `GitHub.assign` (`.github/bible/bible_queue.py:353`), `GitHub.merge` (`.github/bible/bible_queue.py:369`), `GitHub.close_pr` (`.github/bible/bible_queue.py:372`), `GitHub.create_pr` (`.github/bible/bible_queue.py:375`) |
| Calls | `path.startswith`, `GitHub.request`, response `read`, `json.loads`, `RuntimeError` |
| Purpose | Sends a REST request and converts response data and common request failures to Python values or a `RuntimeError`. |

**Steps**

1. Uses an absolute `path` beginning with `http` as-is; otherwise joins the API base, `/repos/`, repository, and path. (`.github/bible/bible_queue.py:129`)
2. Opens the request and reads its response bytes. (`.github/bible/bible_queue.py:130-132`)
3. On HTTP 404 with `ok404`, returns `None`; otherwise reads the whole error body, decodes it, keeps its first 300 characters and raises a method/path/status/detail `RuntimeError`. (`.github/bible/bible_queue.py:133-137`)
4. Converts `URLError`, `TimeoutError`, and `OSError` to a `RuntimeError` containing the method, query-stripped path, and error. (`.github/bible/bible_queue.py:138-139`)
5. Decodes a nonempty payload as JSON; returns `{}` for an empty payload. (`.github/bible/bible_queue.py:140`)

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
| `.github/bible/bible_queue.py:129` | conditional expression | `path.startswith("http")` | Uses `path`; otherwise constructs a repository API URL. |
| `.github/bible/bible_queue.py:133` | except | Request raises `urllib.error.HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:134` | if | Status is 404 and `ok404` is true | Returns `None`. |
| `.github/bible/bible_queue.py:137` | raise | Other HTTP errors | Raises `RuntimeError` with method, path, status, and detail. |
| `.github/bible/bible_queue.py:138` | except | Request raises `URLError`, `TimeoutError`, or `OSError` | Enters network error handling. |
| `.github/bible/bible_queue.py:139` | raise | A listed network error occurred | Raises `RuntimeError` with method, path, and error. |
| `.github/bible/bible_queue.py:140` | conditional expression | Payload is nonempty | Decodes JSON; otherwise returns `{}`. |

#### `GitHub.paged(path)`

Source: `.github/bible/bible_queue.py:142-150` <!-- code: 1bb6c1899527 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.issues` (`.github/bible/bible_queue.py:154`), `GitHub.ensure_label` (`.github/bible/bible_queue.py:158`), `GitHub.prs` (`.github/bible/bible_queue.py:203`), `GitHub.timeline` (`.github/bible/bible_queue.py:206`), `GitHub.branch_prs` (`.github/bible/bible_queue.py:222`), `GitHub.pr_files` (`.github/bible/bible_queue.py:277`) |
| Calls | `GitHub.call`, `len` |
| Purpose | Fetches successive pages of up to 100 results and returns their concatenation. |

**Steps**

1. Starts with an empty result and page number 1. (`.github/bible/bible_queue.py:143`)
2. Chooses `&` if `path` already contains `?`, otherwise `?`, then requests `per_page=100` and the current page with GET. (`.github/bible/bible_queue.py:144-146`)
3. Appends each batch; returns the accumulated list when a batch has fewer than 100 entries, otherwise increments the page and repeats. (`.github/bible/bible_queue.py:147-150`)

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
| `.github/bible/bible_queue.py:144` | while | Always | Repeats page requests until a short batch is returned. |
| `.github/bible/bible_queue.py:145` | conditional expression | `path` contains `?` | Chooses `&`; otherwise chooses `?`. |
| `.github/bible/bible_queue.py:148` | if | Batch length is less than 100 | Returns all accumulated entries; otherwise proceeds to the next page. |

#### `GitHub.issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:152-154` <!-- code: b3f969457f25 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run_issues` (`.github/bible/bible_queue.py:566`), `Queue.reconcile` (`.github/bible/bible_queue.py:667`), `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:685`), `Queue.delta` (`.github/bible/bible_queue.py:1327`, `.github/bible/bible_queue.py:1355`, `.github/bible/bible_queue.py:1368`), `main` (`.github/bible/bible_queue.py:1413`) |
| Calls | `urllib.parse.quote`, `join`, `GitHub.paged` |
| Purpose | Lists issues for encoded labels and a state, excluding pull requests. |

**Steps**

1. Joins labels with commas and URL-quotes the result. (`.github/bible/bible_queue.py:153`)
2. Pages `/issues` with the requested state and labels query, then keeps only objects without a `pull_request` key. (`.github/bible/bible_queue.py:154`)

**Pseudo-code**

```text
q = URL-quote(comma-joined labels)
return paged issues for state and q, excluding pull request objects
```

#### `GitHub.ensure_label(name, why="Codebase analysis run")`

Source: `.github/bible/bible_queue.py:156-161` <!-- code: c80387a5616e -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.ensure_labels` (`.github/bible/bible_queue.py:165`), `GitHub.create_issue` (`.github/bible/bible_queue.py:169`), `GitHub.label` (`.github/bible/bible_queue.py:334`) |
| Calls | `GitHub.paged`, `GitHub.call`, `known_labels.add` |
| Purpose | Loads the known-label set on first use and creates a requested label if it is absent. |

**Steps**

1. If `known_labels` is `None`, pages `/labels` and caches their names. (`.github/bible/bible_queue.py:157-158`)
2. If `name` is missing, posts a label with the fixed color `5319e7` and `why` truncated to 100 characters, then adds the name to the cache. (`.github/bible/bible_queue.py:159-161`)

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
| `.github/bible/bible_queue.py:157` | if | `known_labels` is `None` | Fetches and caches current label names. |
| `.github/bible/bible_queue.py:159` | if | `name` is not in the cache | Creates the label and adds its name to the cache. |

#### `GitHub.ensure_labels()`

Source: `.github/bible/bible_queue.py:163-165` <!-- code: 3233fadcc4c0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1412`) |
| Calls | `LABELS.items`, `GitHub.ensure_label` |
| Purpose | Ensures each label defined in the module's `LABELS` mapping exists. |

**Steps**

1. Iterates each `(name, why)` pair in `LABELS` and invokes `ensure_label`. (`.github/bible/bible_queue.py:164-165`)

**Pseudo-code**

```text
for name, why in LABELS:
    ensure_label(name, why)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:164` | for | For each `(name, why)` in `LABELS.items()` | Calls `ensure_label` once for that pair. |

#### `GitHub.create_issue(title, body, labels, assign=None)`

Source: `.github/bible/bible_queue.py:167-174` <!-- code: c0db4afc186c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:659`), `Queue.plan_phase` (`.github/bible/bible_queue.py:767`), `Queue.start_chunk` (`.github/bible/bible_queue.py:793`), `Queue.component` (`.github/bible/bible_queue.py:852`, `.github/bible/bible_queue.py:887`, `.github/bible/bible_queue.py:900`), `Queue.could_not_check` (`.github/bible/bible_queue.py:1004`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1128`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1235`, `.github/bible/bible_queue.py:1248`), `Queue.delta` (`.github/bible/bible_queue.py:1356`, `.github/bible/bible_queue.py:1371`), `main` (`.github/bible/bible_queue.py:1420`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures labels, optionally configures agent assignment, and creates an issue. |

**Steps**

1. Ensures every requested label, using its `LABELS` description or `Codebase analysis run` as the fallback. (`.github/bible/bible_queue.py:168-169`)
2. Builds a payload containing `title`, `body`, and `labels`; if `assign` is not `None`, adds the Copilot assignee and `agent_assignment`. (`.github/bible/bible_queue.py:170-173`)
3. Posts the payload to `/issues` and returns the result of `call`. (`.github/bible/bible_queue.py:174`)

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
| `.github/bible/bible_queue.py:168` | for | For each requested label | Calls `ensure_label` with its mapped or fallback description. |
| `.github/bible/bible_queue.py:171` | if | `assign` is not `None` | Adds `COPILOT` and the assignment value to the payload. |

#### `GitHub.me()`

Source: `.github/bible/bible_queue.py:176-180` <!-- code: 6c567c6be9c4 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.replayed` (`.github/bible/bible_queue.py:701`), `Queue.deferred_updates` (`.github/bible/bible_queue.py:1152`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1263`) |
| Calls | `getattr`, `GitHub.call`, `get` |
| Purpose | Lazily fetches and caches the token owner's login. |

**Steps**

1. If `_me` is not already truthy, GETs the API `/user` URL and stores its `login`, defaulting to an empty string when the response is falsey or has no login. (`.github/bible/bible_queue.py:178-179`)
2. Returns the cached `_me` value. (`.github/bible/bible_queue.py:180`)

**Pseudo-code**

```text
if _me is falsey: _me = GET api/user.login or ""
return _me
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:178` | if | `_me` is falsey or absent | Fetches and caches the token owner's login. |

#### `GitHub.default_branch()`

Source: `.github/bible/bible_queue.py:182-183` <!-- code: 4eb167486c4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:666`), `Queue.delta` (`.github/bible/bible_queue.py:1323`) |
| Calls | `GitHub.call` |
| Purpose | Returns the repository's `default_branch` value. |

**Steps**

1. Gets the repository resource at the empty path and returns its `default_branch` field. (`.github/bible/bible_queue.py:183`)

**Pseudo-code**

```text
return GET repository["default_branch"]
```

#### `GitHub.branch_sha(branch)`

Source: `.github/bible/bible_queue.py:185-187` <!-- code: 446defb234bd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.pr_files` (`.github/bible/bible_queue.py:259`), `Queue.start_chunk` (`.github/bible/bible_queue.py:785`, `.github/bible/bible_queue.py:786`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Returns a branch reference's object SHA or `None` when the reference is absent. |

**Steps**

1. Quotes `branch` and gets its head reference with `ok404=True`. (`.github/bible/bible_queue.py:186`)
2. Returns `ref["object"]["sha"]` if a reference was returned, otherwise `None`. (`.github/bible/bible_queue.py:187`)

**Pseudo-code**

```text
ref = GET quoted branch reference, allowing 404
return ref.object.sha if ref else None
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:187` | conditional expression | A reference was returned | Returns its object SHA; otherwise returns `None`. |

#### `GitHub.create_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:189-190` <!-- code: b860758c1ca1 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:787`) |
| Calls | `GitHub.call` |
| Purpose | Creates a Git reference for a branch at a supplied SHA. |

**Steps**

1. Posts `ref: "refs/heads/" + branch` and `sha` to `/git/refs`. (`.github/bible/bible_queue.py:190`)

**Pseudo-code**

```text
POST /git/refs with ref "refs/heads/" + branch and sha
```

#### `GitHub.reset_branch(branch, sha)`

Source: `.github/bible/bible_queue.py:192-193` <!-- code: 43e383793681 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:789`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Force-updates a branch reference to a supplied SHA. |

**Steps**

1. Quotes `branch` and PATCHes its head reference with the supplied SHA and `force: True`. (`.github/bible/bible_queue.py:193`)

**Pseudo-code**

```text
PATCH quoted head reference with sha and force=True
```

#### `GitHub.file(path, ref)`

Source: `.github/bible/bible_queue.py:195-199` <!-- code: e383f7bd9e38 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `issue_text` (`.github/bible/bible_queue.py:440`), `json_file` (`.github/bible/bible_queue.py:455`), `Queue.component` (`.github/bible/bible_queue.py:865`, `.github/bible/bible_queue.py:866`), `Queue.follow` (`.github/bible/bible_queue.py:962`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1040`, `.github/bible/bible_queue.py:1041`, `.github/bible/bible_queue.py:1047`, `.github/bible/bible_queue.py:1051`, `.github/bible/bible_queue.py:1090`, `.github/bible/bible_queue.py:1091`, `.github/bible/bible_queue.py:1125`, `.github/bible/bible_queue.py:1126`), `Queue.delta` (`.github/bible/bible_queue.py:1342`) |
| Calls | `GitHub.call`, `urllib.parse.quote`, `isinstance`, `base64.b64decode`, `decode` |
| Purpose | Retrieves and decodes a text file from a repository reference. |

**Steps**

1. Quotes `path` and `ref` and GETs the contents endpoint with `ok404=True`. (`.github/bible/bible_queue.py:196`)
2. Returns `None` for a falsey response, a list response, or a response without `content`. (`.github/bible/bible_queue.py:197-198`)
3. Base64-decodes the content and decodes UTF-8 with replacement for invalid bytes. (`.github/bible/bible_queue.py:199`)

**Pseudo-code**

```text
got = GET quoted contents path at quoted ref, allowing 404
if got is falsey, a list, or lacks content: return None
return base64-decode content, then UTF-8 decode with replacement
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:197` | if | Response is falsey, a list, or has no `content` | Returns `None`. |

#### `GitHub.prs(base=None, state="open")`

Source: `.github/bible/bible_queue.py:201-203` <!-- code: e46dcb273277 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | No call site found; unused (inferred: a search of the repository outside the analysis folder and the skills for `.prs(` finds 0 hits). |
| Calls | `urllib.parse.quote`, `GitHub.paged` |
| Purpose | Lists pull requests by state and optional base branch. |

**Steps**

1. Builds `/pulls?state=<state>` and appends a URL-quoted base query only when `base` is truthy. (`.github/bible/bible_queue.py:202`)
2. Returns the paged results. (`.github/bible/bible_queue.py:203`)

**Pseudo-code**

```text
path = /pulls?state=state
if base is truthy: append quoted base query
return paged(path)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:202` | conditional expression | `base` is truthy | Appends `&base=` and the quoted base; otherwise appends nothing. |

#### `GitHub.timeline(number)`

Source: `.github/bible/bible_queue.py:205-206` <!-- code: 6df4539072ff -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.linked_prs` (`.github/bible/bible_queue.py:211`), `GitHub.agent_events` (`.github/bible/bible_queue.py:226`), `GitHub.start_error` (`.github/bible/bible_queue.py:240`), `GitHub.assigned_at` (`.github/bible/bible_queue.py:250`), `Queue.held` (`.github/bible/bible_queue.py:607`), `Queue.replayed` (`.github/bible/bible_queue.py:703`), `Queue.deferred_updates` (`.github/bible/bible_queue.py:1153`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1264`, `.github/bible/bible_queue.py:1266`) |
| Calls | `GitHub.paged` |
| Purpose | Returns all paged timeline events for an issue number. |

**Steps**

1. Pages `/issues/<number>/timeline` and returns the result. (`.github/bible/bible_queue.py:206`)

**Pseudo-code**

```text
return paged /issues/<number>/timeline
```

#### `GitHub.linked_prs(number)`

Source: `.github/bible/bible_queue.py:208-217` <!-- code: 91e30cd14abd -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:570`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1052`, `.github/bible/bible_queue.py:1086`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1199`) |
| Calls | `GitHub.timeline`, `get`, `append`, `GitHub.call`, `sorted`, `set` |
| Purpose | Finds existing pull requests in this repository cross-referenced from an issue. |

**Steps**

1. Iterates the issue timeline and reads each event's source issue, defaulting missing source/repository values as shown. (`.github/bible/bible_queue.py:210-213`)
2. Collects the source number only for `cross-referenced` events whose source has a `pull_request` and whose repository full name equals this client's repository. (`.github/bible/bible_queue.py:214-215`)
3. Deduplicates and sorts numbers, GETs each pull request with `ok404=True`, and returns only non-`None` results. (`.github/bible/bible_queue.py:216-217`)

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
| `.github/bible/bible_queue.py:211` | for | For each issue timeline event | Inspects its source issue. |
| `.github/bible/bible_queue.py:214` | if | Event is a same-repository cross-reference with a pull request | Appends its source number. |

#### `GitHub.branch_prs(branch, base)`

Source: `.github/bible/bible_queue.py:219-222` <!-- code: fa42118d7d5a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:799`, `.github/bible/bible_queue.py:842`) |
| Calls | `split`, `GitHub.paged`, `urllib.parse.quote` |
| Purpose | Lists all-state pull requests from this repository's branch into a specified base. |

**Steps**

1. Takes the owner portion before `/` in `repo`. (`.github/bible/bible_queue.py:221`)
2. Pages `/pulls` with `state=all`, quoted `owner:branch` as `head`, and quoted `base`. (`.github/bible/bible_queue.py:222`)

**Pseudo-code**

```text
owner = first segment of repo
return paged /pulls with state=all, head=quoted(owner + ":" + branch), base=quoted(base)
```

#### `GitHub.agent_events(number)`

Source: `.github/bible/bible_queue.py:224-228` <!-- code: 1e123ab3f131 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.is_agent_pr` (`.github/bible/bible_queue.py:235`), `Queue.session` (`.github/bible/bible_queue.py:584`) |
| Calls | `GitHub.timeline`, `get` |
| Purpose | Returns the timeline events GitHub records as performed by Copilot's app and named in `WORK_EVENTS` (work started, work finished, work finished with failure) as `(event, timestamp)` pairs. |

**Steps**

1. Reads the pull request's timeline with `self.timeline(number)` and builds one `(event, created_at)` pair per kept event, defaulting a missing `created_at` to the empty string. (`.github/bible/bible_queue.py:226`)
2. Keeps only events whose `performed_via_github_app.slug` equals `AGENT_APP` (default `copilot-swe-agent`, from the environment variable `BIBLE_AGENT_APP`). (`.github/bible/bible_queue.py:227`, `.github/bible/bible_queue.py:66`)
3. Keeps only events whose name is in `WORK_EVENTS`: `copilot_work_started`, `copilot_work_finished` or `copilot_work_finished_failure`. The failure event is one of the three, so a session that ended in failure also shows up in the list. (`.github/bible/bible_queue.py:228`, `.github/bible/bible_queue.py:70`)

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
| `.github/bible/bible_queue.py:227` | comprehension filter | the event's app slug is not `AGENT_APP`, or it has no app | the event is left out |
| `.github/bible/bible_queue.py:228` | comprehension filter | the event name is not in `WORK_EVENTS` | the event is left out |

**Output and side effects**: returns a list of `(event, created_at)` pairs in timeline order; no writes. `Queue.session` sorts it by timestamp and reads the newest pair (`.github/bible/bible_queue.py:586`); `GitHub.is_agent_pr` only tests that the list is not empty, so any of the three `WORK_EVENTS` counts (`.github/bible/bible_queue.py:235`).

#### `GitHub.is_agent_pr(pr)`

Source: `.github/bible/bible_queue.py:230-235` <!-- code: 399d25734d4d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.agent_pr` (`.github/bible/bible_queue.py:572`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1048`, `.github/bible/bible_queue.py:1087`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1200`) |
| Calls | `get`, `GitHub.agent_events`, `bool` |
| Purpose | Tests whether a pull request is Copilot's: opened by a configured agent login on a Bot account, or carrying any Copilot work event that GitHub recorded on its timeline. |

**Steps**

1. Reads `pr["user"]`, defaulting to an empty dictionary. (`.github/bible/bible_queue.py:232`)
2. Returns `True` at once when its login (default empty string) is in `AGENT_LOGINS` and its type (default `"Bot"`) is `"Bot"`: a person cannot take an agent's name on a Bot account (assumed: GitHub behaviour, stated in the comment at line 234). (`.github/bible/bible_queue.py:233-234`)
3. Otherwise calls `agent_events` for the pull request's number and returns whether that list is nonempty. Any event of `WORK_EVENTS` (`copilot_work_started`, `copilot_work_finished` or `copilot_work_finished_failure`) performed via `AGENT_APP` counts, not only `copilot_work_started`; so a pull request on which Copilot only failed, or only finished, is still recognised as Copilot's. (`.github/bible/bible_queue.py:235`, `.github/bible/bible_queue.py:70`)

**Pseudo-code**

```text
user = pr.user or {}
if user.login in AGENT_LOGINS and user.type (default Bot) == Bot: return True
return bool(agent_events(pr.number))      # any WORK_EVENTS member by the agent app
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:233` | if | The user's login is in `AGENT_LOGINS` and the user's type is `"Bot"` | Returns `True` without reading the timeline. |
| `.github/bible/bible_queue.py:235` | return | Any other user | Returns whether the pull request's timeline holds at least one agent work event; no event gives `False`. A failing timeline call raises the `RuntimeError` of `GitHub.call`. |

#### `GitHub.start_error(issue)`

Source: `.github/bible/bible_queue.py:237-246` <!-- code: 0287983c593a -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:581`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:636`) |
| Calls | `GitHub.assigned_at`, `GitHub.timeline`, `get`, `START_ERROR.search`, `splitlines`, `strip` |
| Purpose | Returns the first matching agent start-error comment since the last assignment, or `None`. |

**Steps**

1. Gets the last assignment time using `assigned_at`, then scans the issue timeline. (`.github/bible/bible_queue.py:239-240`)
2. Chooses `actor` or `user`, then uses the actor login only when the actor type defaults to or is `"Bot"`. (`.github/bible/bible_queue.py:241-242`)
3. Requires a `commented` event by a configured agent at or after the assignment time and a body matching `START_ERROR`. (`.github/bible/bible_queue.py:243-244`)
4. Returns the stripped first body line, truncated to 300 characters, for the first qualifying event; returns `None` if no event qualifies. (`.github/bible/bible_queue.py:245-246`)

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
| `.github/bible/bible_queue.py:240` | for | For each issue timeline event | Checks actor, event time, and body. |
| `.github/bible/bible_queue.py:242` | conditional expression | Actor is a bot (or has no type) | Uses the actor login; otherwise uses an empty login. |
| `.github/bible/bible_queue.py:243` | if | Comment event from configured agent at/after assignment matches `START_ERROR` | Returns the bounded first line; otherwise continues scanning. |

#### `GitHub.assigned_at(issue)`

Source: `.github/bible/bible_queue.py:248-251` <!-- code: 8dec0d30b502 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.start_error` (`.github/bible/bible_queue.py:239`), `Queue.session` (`.github/bible/bible_queue.py:583`) |
| Calls | `GitHub.timeline`, `get`, `max` |
| Purpose | Returns the newest timestamp for an assignment event, falling back to issue creation time. |

**Steps**

1. Collects nonempty `created_at` values from `assigned` timeline events for the issue. (`.github/bible/bible_queue.py:250`)
2. Returns the maximum timestamp, or `issue["created_at"]` if there were none. (`.github/bible/bible_queue.py:251`)

**Pseudo-code**

```text
times = created_at for assigned events with a timestamp
return max(times) if any, otherwise issue.created_at
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:251` | conditional expression | At least one assignment timestamp exists | Returns the newest timestamp; otherwise uses issue creation time. |

#### `GitHub.pr_files(number)`

Source: `.github/bible/bible_queue.py:253-287` <!-- code: a075ee350785 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:927`, `.github/bible/bible_queue.py:933`, `.github/bible/bible_queue.py:936`, `.github/bible/bible_queue.py:955`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1050`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1219`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1261`) |
| Calls | `GitHub.call`, `get`, `pr.get`, `GitHub.branch_sha`, `base.get`, `GitHub.paged`, `as_int`, `isinstance`, `compared.get`, `RuntimeError`, `len`, `append` |
| Purpose | Returns every path a pull request touches (the old name of a renamed file too) and refuses, with a `RuntimeError`, any list that may be incomplete, so no file escapes the scope checks. |

**Steps**

1. GETs `/pulls/<number>` (an empty dictionary when the body is empty), then reads `base` and the head commit's `sha`. (`.github/bible/bible_queue.py:256-257`)
2. Looks up the tip of the base branch only for an open pull request whose base has a `ref` and a recorded `sha` and whose head has a `sha`: `tip = branch_sha(base["ref"])`; for any other pull request `tip` is `None`: a merged one (the tip already contains it, so a comparison would be empty; assumed: GitHub behaviour, stated in the comment at line 258) and also one closed without merging (the check then uses the pull request's own file list). (`.github/bible/bible_queue.py:258-260`)
3. When `tip` exists and differs from the base commit the pull request recorded, GitHub's own file list is against that stale base (assumed: GitHub behaviour, stated in the comment at lines 262-265; seen on github.com on 24 Nov 2026: `main` moved, the revision merged it, and the list then held `main`'s own changes). The method then GETs `/compare/<tip>...<head>` (the base branch as it is now, the merge base as a merge would see it) and takes its `files` list when the response is a dictionary. (`.github/bible/bible_queue.py:261-267`)
4. Fails closed: it raises `RuntimeError("the comparison of #<n> with <base ref> gave no file list: not checked, not merged")` when `files` is not a list, or is empty while the pull request's own `changed_files` is nonzero (`as_int`). (`.github/bible/bible_queue.py:268-271`)
5. Raises `RuntimeError("the file list of #<n> is incomplete (300 files or more against <base ref>): not checked, not merged")` when the list holds `COMPARE_MAX` (300) files or more, because GitHub's comparison lists at most that many (assumed: GitHub behaviour, stated in the comments at lines 71 and 265). In this branch `expected` is `None`, so the pull request's own `changed_files` count is not compared with the list. (`.github/bible/bible_queue.py:272-275`, `.github/bible/bible_queue.py:71`)
6. In every other case (not open, no tip, or the tip equals the recorded base) it pages `/pulls/<number>/files` and sets `expected` to `as_int(pr["changed_files"])`. (`.github/bible/bible_queue.py:276-278`)
7. When `expected` is nonzero and differs from the list's length, raises `RuntimeError("the file list of #<n> is incomplete (<listed> of <expected> files): not checked, not merged")`. The 3,000-file limit of GitHub's own list is stated only in the method's docstring (lines 254-255; assumed: GitHub behaviour); no constant in the code holds it (inferred: a search of the queue for `3000` and `3,000` finds 1 hit, the docstring at line 254), and the effect is the same check: a list shorter than the pull request's own count is refused. (`.github/bible/bible_queue.py:254-255`, `.github/bible/bible_queue.py:279-281`)
8. For each listed file appends `filename`, then `previous_filename` when truthy, and returns the list. (`.github/bible/bible_queue.py:282-287`)

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
| `.github/bible/bible_queue.py:259` | conditional expression | The pull request is open, its base has a `ref` and a `sha`, and its head has a `sha` | Reads the base branch's current tip; otherwise `tip` is `None`. |
| `.github/bible/bible_queue.py:261` | if | `tip` exists and differs from the base commit the pull request recorded | Compares the head with the tip; otherwise pages the pull request's own files (the `else` at `.github/bible/bible_queue.py:276`). |
| `.github/bible/bible_queue.py:267` | conditional expression | The comparison's response is a dictionary | Takes its `files`; otherwise `listed` is `None`. |
| `.github/bible/bible_queue.py:269` | if | `listed` is not a list, or is empty while `changed_files` is nonzero | Raises the no-file-list `RuntimeError` (next row). |
| `.github/bible/bible_queue.py:270` | raise | The comparison gave no usable list | `RuntimeError`: the comparison gave no file list; not checked, not merged. |
| `.github/bible/bible_queue.py:272` | if | The comparison lists `COMPARE_MAX` (300) files or more | Raises the incomplete-list `RuntimeError` (next row). |
| `.github/bible/bible_queue.py:273` | raise | The comparison may have been cut at 300 files | `RuntimeError`: the file list is incomplete (300 files or more); not checked, not merged. |
| `.github/bible/bible_queue.py:279` | if | `expected` is nonzero and differs from the number listed (only in the paged branch, where `expected` is not `None`) | Raises the incomplete-list `RuntimeError` (next row). |
| `.github/bible/bible_queue.py:280` | raise | The paged list is shorter or longer than the pull request's own count | `RuntimeError`: the file list is incomplete (n of m files); not checked, not merged. |
| `.github/bible/bible_queue.py:283` | for | For each listed file | Appends its current `filename`. |
| `.github/bible/bible_queue.py:285` | if | `previous_filename` is truthy | Appends the previous filename too. |

**Output and side effects**: returns a list of paths (renamed files appear twice, under both names); no writes. Callers react to the errors differently: in `Queue.follow` only the first call, at line 927, is inside the `try` that catches `RuntimeError` and fails or retries the session with the error text as the reason (`.github/bible/bible_queue.py:926-930`); its later calls (lines 933, 936 and 955, reached only after the first succeeded) are not inside it, but `Queue.run` catches an error from them per component, shows "error this run (retried next run)" for that component and goes on with the other components (`.github/bible/bible_queue.py:741-744`); `assemble_phase`, `revise_all_step` and `continue_if_unfinished` do not catch the error, so an error from their calls ends that tracker's run, and `Queue.reconcile` logs it and tries again at the next check (`.github/bible/bible_queue.py:672-675`).

#### `GitHub.commit_time(sha)`

Source: `.github/bible/bible_queue.py:289-290` <!-- code: a3036655ce65 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:587`) |
| Calls | `GitHub.call` |
| Purpose | Returns the committer date for a commit SHA. |

**Steps**

1. GETs `/commits/<sha>` and returns `commit.committer.date`. (`.github/bible/bible_queue.py:290`)

**Pseudo-code**

```text
return GET /commits/<sha>.commit.committer.date
```

#### `GitHub.tarball(ref, dest)`

Source: `.github/bible/bible_queue.py:292-331` <!-- code: a84776e4e94b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.check` (`.github/bible/bible_queue.py:979`), `Queue.whole_fingerprint` (`.github/bible/bible_queue.py:1017`) |
| Calls | `urllib.parse.quote`, `tempfile.TemporaryFile`, `self.request`, `resp.read`, `len`, `buf.write`, `RuntimeError`, `buf.seek`, `os.path.abspath`, `tarfile.open`, `max`, `member.name.split`, `os.path.normpath`, `os.path.join`, `member.isdir`, `os.makedirs`, `os.path.dirname`, `tar.extractfile`, `open`, `shutil.copyfileobj` |
| Purpose | Downloads a bounded repository archive into a temporary file and extracts only regular files and directories whose normalized paths stay below `dest`. |

**Steps**

1. Quotes `ref`, builds the repository tarball URL and requests it with a 300-second timeout. Reads 1 MiB chunks into a `TemporaryFile`; an empty read ends the loop, while cumulative bytes above `MAX_TARBALL` raise `RuntimeError`. (`.github/bible/bible_queue.py:296-307`)
2. Converts request `URLError`, `TimeoutError` or `OSError` into `RuntimeError`, seeks the temporary file to the beginning, resolves `dest` to an absolute root, and opens it as a gzip tar archive. (`.github/bible/bible_queue.py:298-313`)
3. Counts members and their nonnegative uncompressed sizes; exceeding `MAX_MEMBERS` or `MAX_UNPACKED` raises `RuntimeError`. It splits each member name once at `/`, skipping a missing/empty path tail and non-file/non-directory members. (`.github/bible/bible_queue.py:314-322`)
4. Joins the tail to the root, normalizes it, and skips a target whose path does not start with `root + os.sep`. Directories are created recursively; files get a created parent and are copied from `tar.extractfile(member)` into a binary file. (`.github/bible/bible_queue.py:323-331`)

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
| `.github/bible/bible_queue.py:300` | while | Response chunks are being read | Reads the next chunk and exits when it is empty. |
| `.github/bible/bible_queue.py:302` | if | `resp.read` returns no bytes | Leaves the streaming loop. |
| `.github/bible/bible_queue.py:305` | if | Total compressed bytes exceed `MAX_TARBALL` | Raises `RuntimeError` without unpacking. |
| `.github/bible/bible_queue.py:306` | raise | Compressed-size limit exceeded | Reports the reference and configured maximum. |
| `.github/bible/bible_queue.py:308` | except | Request raises `URLError`, `TimeoutError` or `OSError` | Converts the error to a `RuntimeError` naming the reference. |
| `.github/bible/bible_queue.py:309` | raise | A listed request error occurred | Stops with the wrapped `RuntimeError`. |
| `.github/bible/bible_queue.py:314` | for | For each archive member | Counts the member and validates total limits before extraction. |
| `.github/bible/bible_queue.py:317` | if | Member count or uncompressed-size limit is exceeded | Raises `RuntimeError`; extraction stops. |
| `.github/bible/bible_queue.py:318` | raise | A tarball member limit was exceeded | Reports the member and uncompressed-size limits. |
| `.github/bible/bible_queue.py:321` | if | Missing path tail or member is neither regular file nor directory | Skips the member. |
| `.github/bible/bible_queue.py:324` | if | Normalized target does not start with the root plus separator | Skips the target. |
| `.github/bible/bible_queue.py:326` | if | Member is a directory | Creates it and continues to the next member. |

#### `GitHub.label(number, name)`

Source: `.github/bible/bible_queue.py:333-335` <!-- code: 3c67a9360e66 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:614`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:637`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:649`), `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:695`), `Queue.follow` (`.github/bible/bible_queue.py:945`, `.github/bible/bible_queue.py:946`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1068`, `.github/bible/bible_queue.py:1073`, `.github/bible/bible_queue.py:1095`, `.github/bible/bible_queue.py:1147`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1280`, `.github/bible/bible_queue.py:1291`) |
| Calls | `GitHub.ensure_label`, `LABELS.get`, `GitHub.call` |
| Purpose | Ensures and adds one label to an issue. |

**Steps**

1. Ensures the label using its `LABELS` description or the default description. (`.github/bible/bible_queue.py:334`)
2. Posts `{"labels": [name]}` to the issue labels endpoint. (`.github/bible/bible_queue.py:335`)

**Pseudo-code**

```text
ensure label using mapped description or default
POST issue labels with [name]
```

#### `GitHub.unlabel(number, name)`

Source: `.github/bible/bible_queue.py:337-338` <!-- code: caf34958b931 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:966`) |
| Calls | `GitHub.call`, `urllib.parse.quote` |
| Purpose | Removes a label from an issue and permits a missing-label response. |

**Steps**

1. URL-quotes `name` and sends DELETE to the issue label endpoint with `ok404=True`. (`.github/bible/bible_queue.py:338`)

**Pseudo-code**

```text
DELETE quoted issue label endpoint, allowing 404
```

#### `GitHub.comment(number, text)`

Source: `.github/bible/bible_queue.py:340-341` <!-- code: a05e7f494734 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:615`, `.github/bible/bible_queue.py:619`, `.github/bible/bible_queue.py:627`), `Queue.hold_start_error` (`.github/bible/bible_queue.py:639`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:646`, `.github/bible/bible_queue.py:651`, `.github/bible/bible_queue.py:654`), `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:693`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1069`, `.github/bible/bible_queue.py:1074`, `.github/bible/bible_queue.py:1096`, `.github/bible/bible_queue.py:1136`, `.github/bible/bible_queue.py:1143`, `.github/bible/bible_queue.py:1146`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1281`, `.github/bible/bible_queue.py:1292`, `.github/bible/bible_queue.py:1296`), `Queue.delta` (`.github/bible/bible_queue.py:1334`) |
| Calls | `GitHub.call` |
| Purpose | Creates an issue comment with the given body. |

**Steps**

1. Posts `{"body": text}` to `/issues/<number>/comments`. (`.github/bible/bible_queue.py:341`)

**Pseudo-code**

```text
POST issue comments with body=text
```

#### `GitHub.close(number, reason="completed")`

Source: `.github/bible/bible_queue.py:343-344` <!-- code: db2a40d380a0 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:621`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:655`), `Queue.run` (`.github/bible/bible_queue.py:737`), `Queue.component` (`.github/bible/bible_queue.py:827`), `Queue.follow` (`.github/bible/bible_queue.py:967`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1098`, `.github/bible/bible_queue.py:1100`, `.github/bible/bible_queue.py:1137`), `Queue.whole_hold` (`.github/bible/bible_queue.py:1169`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1182`, `.github/bible/bible_queue.py:1202`) |
| Calls | `GitHub.call` |
| Purpose | Closes an issue with the supplied state reason. |

**Steps**

1. PATCHes `/issues/<number>` with `state: "closed"` and the supplied `state_reason`. (`.github/bible/bible_queue.py:344`)

**Pseudo-code**

```text
PATCH issue state=closed and state_reason=reason
```

#### `GitHub.set_body(number, body)`

Source: `.github/bible/bible_queue.py:346-347` <!-- code: 56545a0f998b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:624`), `Queue.render` (`.github/bible/bible_queue.py:1316`) |
| Calls | `GitHub.call` |
| Purpose | Replaces an issue's body. |

**Steps**

1. PATCHes `/issues/<number>` with `{"body": body}`. (`.github/bible/bible_queue.py:347`)

**Pseudo-code**

```text
PATCH issue body=body
```

#### `GitHub.unassign(number)`

Source: `.github/bible/bible_queue.py:349-350` <!-- code: 415484346894 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.hold_start_error` (`.github/bible/bible_queue.py:638`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:650`) |
| Calls | `GitHub.call` |
| Purpose | Removes the configured Copilot assignee from an issue. |

**Steps**

1. Sends DELETE to `/issues/<number>/assignees` with `COPILOT` as the sole assignee. (`.github/bible/bible_queue.py:350`)

**Pseudo-code**

```text
DELETE issue assignees with [COPILOT]
```

#### `GitHub.assign(number, assign)`

Source: `.github/bible/bible_queue.py:352-353` <!-- code: 8fb2f09224db -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:626`) |
| Calls | `GitHub.call` |
| Purpose | Assigns Copilot to an issue with the provided agent-assignment data. |

**Steps**

1. Posts `COPILOT` as the sole assignee and includes the supplied `agent_assignment`. (`.github/bible/bible_queue.py:353`)

**Pseudo-code**

```text
POST issue assignees with [COPILOT] and agent_assignment=assign
```

#### `GitHub.ready(pr)`

Source: `.github/bible/bible_queue.py:355-363` <!-- code: ae31dacf00e7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `GitHub.merge` (`.github/bible/bible_queue.py:367`) |
| Calls | `endswith`, `GitHub.request`, response `read`, `RuntimeError` |
| Purpose | Marks a draft pull request ready for review through GitHub GraphQL. |

**Steps**

1. Defines the `markPullRequestReadyForReview` mutation and chooses the GraphQL URL; for an API base ending `/api/v3`, removes `/v3` before adding `/graphql`. (`.github/bible/bible_queue.py:357-358`)
2. POSTs the query and `pr["node_id"]` as the `id` variable, then reads the response. (`.github/bible/bible_queue.py:359-361`)
3. Converts an `HTTPError` to a `RuntimeError` containing the GraphQL operation and HTTP status. (`.github/bible/bible_queue.py:362-363`)

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
| `.github/bible/bible_queue.py:358` | conditional expression | API URL ends with `/api/v3` | Removes `/v3` before appending `/graphql`; otherwise appends `/graphql` directly. |
| `.github/bible/bible_queue.py:362` | except | Request raises `HTTPError` | Enters HTTP error handling. |
| `.github/bible/bible_queue.py:363` | raise | GraphQL request raises `HTTPError` | Raises `RuntimeError` with operation and HTTP status. |

#### `GitHub.merge(pr, title)`

Source: `.github/bible/bible_queue.py:365-369` <!-- code: cea69f3a2a18 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:965`) |
| Calls | `get`, `GitHub.ready`, `GitHub.call` |
| Purpose | Marks a draft ready, when needed, and requests a squash merge with the supplied title. |

**Steps**

1. Calls `ready` only when `pr["draft"]` is truthy. (`.github/bible/bible_queue.py:366-367`)
2. PUTs `/pulls/<number>/merge` with `merge_method: "squash"`, the supplied `commit_title`, and the current head SHA. (`.github/bible/bible_queue.py:368-369`)

**Pseudo-code**

```text
if PR is draft: mark it ready
PUT merge request with squash method and title
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:366` | if | `pr["draft"]` is truthy | Calls `ready` before requesting the merge. |

#### `GitHub.close_pr(number)`

Source: `.github/bible/bible_queue.py:371-372` <!-- code: c5e4b3b311ae -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.fail_or_retry` (`.github/bible/bible_queue.py:647`) |
| Calls | `GitHub.call` |
| Purpose | Closes a pull request. |

**Steps**

1. PATCHes `/pulls/<number>` with `state: "closed"`. (`.github/bible/bible_queue.py:372`)

**Pseudo-code**

```text
PATCH pull request state=closed
```

#### `GitHub.create_pr(head, base, title, body)`

Source: `.github/bible/bible_queue.py:374-375` <!-- code: 9b2aa4667c1c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:868`) |
| Calls | `GitHub.call` |
| Purpose | Creates a pull request and returns the API result. |

**Steps**

1. POSTs `head`, `base`, `title`, and `body` to `/pulls`, returning `call`'s result. (`.github/bible/bible_queue.py:375`)

**Pseudo-code**

```text
return POST /pulls with head, base, title, and body
```

### `Queue`

Source: `.github/bible/bible_queue.py:560-1381`

`Queue` coordinates tracker issues, component sessions, verification/revision cycles, assembly, and delta updates; it also continues an assembly or whole-analysis session that ended before its end marker, and holds one whose Copilot session failed before starting (`Queue.continue_if_unfinished`, `.github/bible/bible_queue.py:1252-1305`). Its constructor sets the GitHub client, logger, and skill directory (`.github/bible/bible_queue.py:561-563`); methods also populate run-specific fields: `deadline` and `default` in `reconcile` (`.github/bible/bible_queue.py:665-666`), `settings`, `tracker`, `run_label` and `state` in `run` (`.github/bible/bible_queue.py:707-715`), and `estimate` (`.github/bible/bible_queue.py:738`); `delta` also sets `default` (`.github/bible/bible_queue.py:1323`), and `could_not_check`, `component` and `assemble_phase` change the `state` counters (`.github/bible/bible_queue.py:1000-1003`, `.github/bible/bible_queue.py:840`, `.github/bible/bible_queue.py:1063`).

#### `Queue.__init__(gh, log=print)`

Source: `.github/bible/bible_queue.py:561-563` <!-- code: 11924208c0e9 -->

| | |
| --- | --- |
| Kind | instance initializer |
| Called by | `main` (`.github/bible/bible_queue.py:1404`) |
| Calls | `os.environ.get` |
| Purpose | Stores the GitHub client and logger, and selects the skills directory. |

**Steps**

1. Stores `gh` and `log` on the instance. (`.github/bible/bible_queue.py:562`)
2. Reads `BIBLE_SKILLS`, defaulting to `.github/skills`. (`.github/bible/bible_queue.py:563`)

**Pseudo-code**

```text
self.gh, self.log = gh, log
self.skills = BIBLE_SKILLS or ".github/skills"
```

#### `Queue.run_issues(labels, state="open")`

Source: `.github/bible/bible_queue.py:565-566` <!-- code: 9186c4a33e43 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:736`), `Queue.plan_phase` (`.github/bible/bible_queue.py:760`), `Queue.start_chunk` (`.github/bible/bible_queue.py:788`), `Queue.component` (`.github/bible/bible_queue.py:808`, `.github/bible/bible_queue.py:820`, `.github/bible/bible_queue.py:822`, `.github/bible/bible_queue.py:828`, `.github/bible/bible_queue.py:844`, `.github/bible/bible_queue.py:859`, `.github/bible/bible_queue.py:862`, `.github/bible/bible_queue.py:864`, `.github/bible/bible_queue.py:881`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1032`, `.github/bible/bible_queue.py:1066`, `.github/bible/bible_queue.py:1072`, `.github/bible/bible_queue.py:1083`), `Queue.whole_hold` (`.github/bible/bible_queue.py:1166`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1177`, `.github/bible/bible_queue.py:1183`, `.github/bible/bible_queue.py:1187`, `.github/bible/bible_queue.py:1189`, `.github/bible/bible_queue.py:1195`) |
| Calls | `self.gh.issues` |
| Purpose | Queries issues for the requested labels plus this run's unique label. |

**Steps**

1. Appends `self.run_label` to the supplied labels and calls `gh.issues` with the requested state. (`.github/bible/bible_queue.py:566`)

**Pseudo-code**

```text
return gh.issues(labels + [run_label], state)
```

#### `Queue.agent_pr(issue, base)`

Source: `.github/bible/bible_queue.py:568-574` <!-- code: 471c772b908b -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:579`) |
| Calls | `reversed`, `self.gh.linked_prs`, `get`, `self.gh.is_agent_pr` |
| Purpose | Finds the newest linked pull request that is open, same-repository, targets `base`, and is by the agent. |

**Steps**

1. Iterates linked pull requests in reverse order. (`.github/bible/bible_queue.py:570`)
2. Reads the head repository full name, defaulting missing nested values to `{}`. (`.github/bible/bible_queue.py:571`)
3. Returns the first PR whose state is `open`, head repository is `gh.repo`, base ref matches, and `is_agent_pr` is true. (`.github/bible/bible_queue.py:572-573`)
4. Returns `None` when no linked PR qualifies. (`.github/bible/bible_queue.py:574`)

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
| `.github/bible/bible_queue.py:570` | for | For each linked PR in reverse order | Checks newer linked PRs first. |
| `.github/bible/bible_queue.py:572` | if | PR is open, same-repository, targets `base`, and is an agent PR | Returns that PR. |

#### `Queue.session(issue, base, analysis, comp=None)`

Source: `.github/bible/bible_queue.py:577-593` <!-- code: 287d4620c196 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:773`), `Queue.follow` (`.github/bible/bible_queue.py:914`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1106`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1206`) |
| Calls | `self.agent_pr`, `self.gh.start_error`, `age`, `self.gh.assigned_at`, `self.gh.agent_events`, `sorted`, `self.gh.commit_time`, `bool`, `pr.get`, `status_of`, `labels_of`, `status.get` |
| Purpose | Classifies an open session issue as start-error, no-start, waiting, running or finished and returns its pull request when there is one. |

**Steps**

1. Looks up the agent's open pull request for the issue with `self.agent_pr(issue, base)`. (`.github/bible/bible_queue.py:579`)
2. With no pull request: returns `("start-error", None)` when `gh.start_error(issue)` is truthy; otherwise returns `("no-start", None)` when the age of the issue's assignment exceeds `NO_PR_AFTER` (30 minutes), else `("waiting", None)`. (`.github/bible/bible_queue.py:580-583`, `.github/bible/bible_queue.py:74`)
3. With a pull request, reads `gh.agent_events` for it. When any event exists, GitHub's own record decides: the newest event by timestamp being `copilot_work_started` gives `"running"`, any other newest event (`copilot_work_finished` or `copilot_work_finished_failure`) gives `"finished"`; the pull request is returned with it. (`.github/bible/bible_queue.py:584-586`)
4. With no work events, computes `pushed`, the age of the head commit, and `asked`, true when reviewers were requested or the pull request is not a draft. (`.github/bible/bible_queue.py:587-588`)
5. For a component chunk (`comp` given and the label `bible-chunk` on the issue), reads `<analysis>/ledger/components/<comp>/status.json` at the head SHA and sets `final` when its `state` is in `FINAL_STATES`; returns `"finished"` when `final` and (`asked` or `pushed` > `IDLE_AFTER`), or when `pushed` > 3 x `IDLE_AFTER`, else `"running"`. (`.github/bible/bible_queue.py:589-592`)
6. Otherwise returns `"finished"` when `asked` or `pushed` > `IDLE_AFTER`, else `"running"`. (`.github/bible/bible_queue.py:593`)

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
| `.github/bible/bible_queue.py:580` | if | no agent pull request was found | enters the start-error / no-start / waiting classification |
| `.github/bible/bible_queue.py:581` | if | `start_error(issue)` is truthy | returns `("start-error", None)` |
| `.github/bible/bible_queue.py:583` | conditional expression | assignment age exceeds `NO_PR_AFTER` | returns `no-start`; otherwise `waiting`; the pull request is `None` |
| `.github/bible/bible_queue.py:585` | if | `agent_events` returned at least one event | the newest event decides: `running` only for `copilot_work_started`, otherwise `finished` (a failure event counts as finished) |
| `.github/bible/bible_queue.py:586` | conditional expression | newest event is `copilot_work_started` | returns `running`; otherwise `finished` |
| `.github/bible/bible_queue.py:589` | if | `comp` is truthy and the issue has the label `bible-chunk` | uses the head `status.json` and the component-specific age rules |
| `.github/bible/bible_queue.py:592` | conditional expression | final status and (asked or idle), or pushed age exceeds `3 * IDLE_AFTER` | returns `finished`; otherwise `running` |
| `.github/bible/bible_queue.py:593` | conditional expression | `asked` or pushed age exceeds `IDLE_AFTER` | returns `finished`; otherwise `running` |

**Output and side effects**: returns a `(state, pr)` pair; reads only (timeline, commit time, `status.json` at the head SHA). The docstring lists four states and omits `start-error` (`.github/bible/bible_queue.py:578`).

#### `Queue.held(issue)`

Source: `.github/bible/bible_queue.py:595-628` <!-- code: c519a460eab6 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:771`), `Queue.component` (`.github/bible/bible_queue.py:811`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1104`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1204`) |
| Calls | `labels_of`, `any`, `get`, `issue.get`, `self.gh.timeline`, `max`, `e.get`, `self.gh.label`, `self.gh.comment`, `self.gh.close`, `l.startswith`, `ATTEMPT.sub`, `self.gh.set_body`, `re.search`, `self.gh.assign`, `assignment`, `self.model_for`, `base.group` |
| Purpose | Holds issues marked for a person, closes released component sessions, or reassigns other unassigned sessions to Copilot. |

**Steps**

1. Returns `True` when the labels include `bible-needs-human`. (`.github/bible/bible_queue.py:603`)
2. Otherwise returns `False` immediately when an assignee login belongs to `AGENT_LOGINS`. (`.github/bible/bible_queue.py:605`)
3. Reads issue timeline events and finds the latest added and removed timestamps for `bible-needs-human`; if removal is absent or not newer, labels and comments the issue for human review and returns `True`. (`.github/bible/bible_queue.py:606-618`)
4. If a `bible/` label exists after release, comments and closes the issue as `not_planned`, returning `released`. (`.github/bible/bible_queue.py:619-622`)
5. Otherwise resets the `Attempt:` marker, saves the body, extracts `Base branch:` or uses `self.default`, assigns Copilot with the selected model, comments, and returns `False`. (`.github/bible/bible_queue.py:623-628`)

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
| `.github/bible/bible_queue.py:603` | if | Labels contain `bible-needs-human` | Returns `True`. |
| `.github/bible/bible_queue.py:605` | if | An assignee login belongs to `AGENT_LOGINS` | Returns `False`. |
| `.github/bible/bible_queue.py:612` | if | The human-label removal is absent or not newer than its addition | Labels, comments, and returns `True`. |
| `.github/bible/bible_queue.py:617` | return | No valid release follows the human hold | Stops before reassignment. |
| `.github/bible/bible_queue.py:618` | if | A component label begins `bible/` after release | Closes and returns `released`; otherwise reassigns. |
| `.github/bible/bible_queue.py:626` | conditional expression | A `Base branch:` match exists | Uses its captured branch; otherwise uses `self.default`. |

#### `Queue.model_for(issue)`

Source: `.github/bible/bible_queue.py:630-632` <!-- code: 17f084589886 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:626`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:660`) |
| Calls | `labels_of`, `self.settings.get` |
| Purpose | Selects the verification model for verification issue types, otherwise the normal model. |

**Steps**

1. Gets the issue's label names. (`.github/bible/bible_queue.py:631`)
2. Returns `verify_model` when labels intersect `bible-verify` or `bible-verify-all`; otherwise returns `model`. (`.github/bible/bible_queue.py:632`)

**Pseudo-code**

```text
kinds = labels_of(issue)
return settings.verify_model if kinds intersects verify labels
       else settings.model
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:632` | conditional expression | `kinds` intersects the verification labels | Returns `verify_model`; otherwise returns `model`. |

#### `Queue.hold_start_error(issue)`

Source: `.github/bible/bible_queue.py:634-640` <!-- code: 510c0f07df06 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:775`), `Queue.follow` (`.github/bible/bible_queue.py:918`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1108`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1208`) |
| Calls | `self.gh.start_error`, `self.gh.label`, `self.gh.unassign`, `self.gh.comment` |
| Purpose | Holds a session with an agent start error for human intervention. |

**Steps**

1. Gets the start-error text or uses `Copilot could not start`. (`.github/bible/bible_queue.py:636`)
2. Adds `bible-needs-human`, unassigns Copilot, and posts a comment containing the reason and remediation guidance. (`.github/bible/bible_queue.py:637-640`)

**Pseudo-code**

```text
why = start_error(issue) or fallback message
label issue bible-needs-human
unassign Copilot
comment why and instructions for removing the hold
```

#### `Queue.fail_or_retry(issue, pr, why)`

Source: `.github/bible/bible_queue.py:642-661` <!-- code: c86515a02433 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:778`), `Queue.follow` (`.github/bible/bible_queue.py:921`, `.github/bible/bible_queue.py:929`, `.github/bible/bible_queue.py:939`, `.github/bible/bible_queue.py:952`, `.github/bible/bible_queue.py:957`, `.github/bible/bible_queue.py:960`, `.github/bible/bible_queue.py:963`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1111`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1211`, `.github/bible/bible_queue.py:1222`) |
| Calls | `ATTEMPT.search`, `int`, `self.gh.comment`, `self.gh.close_pr`, `self.gh.label`, `self.gh.unassign`, `self.gh.close`, `ATTEMPT.sub`, `re.search`, `self.gh.create_issue`, `sorted`, `assignment`, `self.model_for`, `labels_of`, `startswith` |
| Purpose | Closes a failed attempt and opens its retry, or holds the issue after a second failure. |

**Steps**

1. Parses the attempt number from the issue body, defaulting to 1. (`.github/bible/bible_queue.py:644`)
2. If a PR was supplied, comments that it was not merged and closes it. (`.github/bible/bible_queue.py:645-647`)
3. When attempt is at least 2, labels and unassigns the issue, posts a human-action comment, and returns `False`. (`.github/bible/bible_queue.py:648-653`)
4. Otherwise comments that a new attempt will open, closes the issue with `not_planned`, updates or prepends the attempt marker, and extracts the base branch or uses `self.default`. (`.github/bible/bible_queue.py:654-658`)
5. Creates a replacement issue with only labels beginning `bible`, sorted, and assignment data for the chosen base and model; returns `True`. (`.github/bible/bible_queue.py:659-661`)

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
| `.github/bible/bible_queue.py:645` | if | `pr` is truthy | Comments that it was not merged and closes the PR; otherwise skips PR updates. |
| `.github/bible/bible_queue.py:648` | if | Attempt number is at least 2 | Labels and unassigns the issue, comments for human action, and returns `False`; otherwise opens a retry. |
| `.github/bible/bible_queue.py:656` | conditional expression | The issue body contains an attempt marker | Replaces it with the incremented attempt; otherwise prepends `Attempt: 2`. |
| `.github/bible/bible_queue.py:660` | conditional expression | A `Base branch:` match exists in the original body | Assigns the retry to that branch; otherwise uses `self.default`. |

#### `Queue.reconcile()`

Source: `.github/bible/bible_queue.py:664-679` <!-- code: 8d7782bcd3d5 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `main` (`.github/bible/bible_queue.py:1424`) |
| Calls | `time.monotonic`, `self.gh.default_branch`, `self.gh.issues`, `settings_of`, `self.log`, `self.run`, `type`, `self.replay_closed_runs` |
| Purpose | Processes each open tracker independently so one failing tracker does not prevent others, then replays the recorded updates of closed trackers. |

**Steps**

1. Sets `self.deadline` to `time.monotonic() + RUN_BUDGET` (19 minutes, `.github/bible/bible_queue.py:81`), then stores the repository's default branch in `self.default` (`.github/bible/bible_queue.py:665-666`).
2. Iterates the open issues labelled `bible-tracker`; for each it calls `settings_of`, and a falsey result logs "tracker #<n> has no readable bible-settings block: skipped" and moves to the next tracker (`.github/bible/bible_queue.py:667-671`).
3. Calls `self.run(tracker, settings)` inside a `try`; any `Exception` is logged with the tracker number, the exception type name and its message, and the loop goes on (`.github/bible/bible_queue.py:672-675`).
4. After the loop, even when no tracker is open, calls `self.replay_closed_runs()` in a second `try`; an `Exception` is logged with the text "updates recorded on closed runs", the exception type name, its message and the note "(tried again at the next check)", and is not raised (`.github/bible/bible_queue.py:676-679`).

**Pseudo-code**

```text
deadline = now + RUN_BUDGET
default = gh.default_branch()
for tracker in open bible-tracker issues:
    settings = settings_of(tracker)
    if not settings: log and continue
    try run(tracker, settings)
    except Exception: log and continue to next tracker
try replay_closed_runs()
except Exception: log (tried again at the next check)
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:667` | for | For each open `bible-tracker` issue | Parses its settings and processes that tracker independently. |
| `.github/bible/bible_queue.py:669` | if | `settings_of` returns a falsey value | Logs the tracker number and skips it. |
| `.github/bible/bible_queue.py:674` | except | `run` raises `Exception` | Logs tracker number, exception type and message, then continues with the next tracker. |
| `.github/bible/bible_queue.py:678` | except | `replay_closed_runs` raises `Exception` | Logs the type and message with the note that the next check tries again; `reconcile` returns normally. |

#### `Queue.replay_closed_runs()`

Source: `.github/bible/bible_queue.py:681-697` <!-- code: 35fc841c3d75 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:677`) |
| Calls | `self.gh.issues`, `labels_of`, `self.replayed`, `self.deferred_updates`, `self.delta`, `settings_of`, `self.gh.comment`, `self.gh.label`, `self.log`, `len`, `type`, `get` |
| Purpose | Turns the code changes recorded on closed trackers into update issues, once per tracker: the paths recorded while a run was open that its Done step never replayed (a person closed the tracker, or an error followed the closing) (inferred: per `.github/bible/bible_queue.py:682-684`, the docstring). |

**Steps**

1. Lists the closed issues labelled `bible-tracker` (`.github/bible/bible_queue.py:685`).
2. Skips a tracker that already carries `bible-replayed`, before any timeline call (`.github/bible/bible_queue.py:686-687`).
3. For each other tracker, in a `try`: when `replayed(tracker)` is false, reads its recorded paths with `deferred_updates`; when there are paths, calls `self.delta(paths, <the tracker's settings analysis folder, else "codebase-analysis">)` with the default `record=True`, so the change is recorded on a run that is open now, or becomes update issues (`.github/bible/bible_queue.py:689-692`). It then comments "The <n> code change(s) recorded while this run was open are now in update issues, or recorded on the run open now." followed by `REPLAYED_MARK` (`.github/bible/bible_queue.py:693-694`); the comment is written even when there are no paths.
4. Adds the label `bible-replayed`, also when `replayed` was already true and nothing else was done (`.github/bible/bible_queue.py:695`).
5. An `Exception` for one tracker is logged with the tracker number, the text "replaying its recorded updates", the exception type name and its message; the label is then not added, so the next check tries that tracker again, and the loop goes on with the others (`.github/bible/bible_queue.py:696-697`).

**Pseudo-code**

```text
for tracker in closed bible-tracker issues:
    if tracker has label bible-replayed: continue
    try:
        if not replayed(tracker):
            paths = deferred_updates(tracker)
            if paths: delta(paths, settings analysis or "codebase-analysis")      # record=True
            comment "<n> code change(s) ... update issues, or recorded on the run open now" + REPLAYED_MARK
        label tracker bible-replayed
    except Exception: log and go on
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:685` | for | For each closed `bible-tracker` issue | Processes it on its own. |
| `.github/bible/bible_queue.py:686` | if | The tracker has `bible-replayed` | Skips it with no further call. |
| `.github/bible/bible_queue.py:689` | if | The queue's own mark comment is not on the tracker | Reads the recorded paths and replays them. |
| `.github/bible/bible_queue.py:691` | if | The tracker has recorded paths | Calls `delta` with them. |
| `.github/bible/bible_queue.py:696` | except | Any step for this tracker raises `Exception` | Logs it; the tracker keeps no label and is tried again at the next check. |

**Notes**: `deferred_updates` returns every path recorded on the tracker, including those a Done step already passed to `delta` before its late replay failed; `delta` skips a component that already has an open `bible-delta` issue (`.github/bible/bible_queue.py:690`, `.github/bible/bible_queue.py:1368-1370`). A tracker closed by a Done step that finished cleanly already carries the mark comment and the label (`.github/bible/bible_queue.py:1146-1147`).

#### `Queue.replayed(tracker)`

Source: `.github/bible/bible_queue.py:699-703` <!-- code: 5736ec800bfb -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:689`) |
| Calls | `self.gh.me`, `self.gh.timeline`, `any`, `e.get`, `get` |
| Purpose | Says whether the queue itself has already marked a closed tracker's recorded updates as replayed. |

**Steps**

1. Gets the login of the token's owner with `self.gh.me()` (`.github/bible/bible_queue.py:701`).
2. Returns `True` when some event of the tracker's timeline is a `commented` event whose actor (`actor`, else `user`) has that login and whose body contains `REPLAYED_MARK`; otherwise `False` (`.github/bible/bible_queue.py:702-703`). A comment by another account carrying the same text does not count.

**Pseudo-code**

```text
me = gh.me()
return any(event is a comment by me and REPLAYED_MARK in its body for event in timeline(tracker))
```

**Output and side effects**: returns a bool; reads the timeline, writes nothing (`.github/bible/bible_queue.py:699-703`).

#### `Queue.run(tracker, settings)`

Source: `.github/bible/bible_queue.py:705-756` <!-- code: ab24ac87df39 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:673`) |
| Calls | `settings.get`, `STATE.search`, `tracker.get`, `json.loads`, `found.group`, `isinstance`, `json_file`, `catalog.get`, `self.plan_phase`, `c.get`, `str`, `NAME.match`, `len`, `self.render`, `str.strip`, `asked.split`, `n.strip`, `join`, `self.run_issues`, `gh.close`, `self.component`, `str.endswith`, `str.startswith`, `as_int`, `self.start_chunk`, `type`, `all`, `rows.values`, `self.assemble_phase` |
| Purpose | Restores tracker state, validates the component catalog and selection, advances component states up to the configured concurrency, and renders the tracker. |

**Steps**

1. Selects `analysis` from settings or `codebase-analysis`, saves settings/tracker/run label, and parses the hidden state marker. Invalid JSON and non-dictionary state become `{}`. Reads `components.json` from the default branch. (`.github/bible/bible_queue.py:706-716`)
2. If the catalog is not a dict, is proposed, or lacks a list of components, returns the result of `plan_phase`. It stringifies each dict component's name, filters names with `NAME`, and renders a stopped settings row if any listed name is invalid. (`.github/bible/bible_queue.py:717-727`)
3. Strips the requested component selection; `all` or empty means all valid names, otherwise comma-splits and strips the names. Unknown or empty selection renders a stopped settings row and returns. (`.github/bible/bible_queue.py:728-735`)
4. Closes open plan issues, records catalog session estimates, evaluates each requested component, catches component exceptions into a 160-character error row, and counts rows ending in `running`, `starting`, or `merged`, or beginning with `waiting`. (`.github/bible/bible_queue.py:736-745`)
5. Converts `concurrency` with `as_int`; starts each `not started` component when the cap is zero or active count is below it. A `RuntimeError` becomes a 160-character error row. When every row is `merged`, adds whole-analysis assembly status; renders all rows. (`.github/bible/bible_queue.py:746-756`)

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
| `.github/bible/bible_queue.py:711` | conditional expression | State marker matched | Parses its JSON group; otherwise uses `{}`. |
| `.github/bible/bible_queue.py:712` | except | State JSON raises `ValueError` | Replaces it with `{}`. |
| `.github/bible/bible_queue.py:714` | if | Parsed state is not a dict | Replaces it with `{}`. |
| `.github/bible/bible_queue.py:717` | if | Catalog is invalid, proposed, or has no component list | Returns the planning-phase result. |
| `.github/bible/bible_queue.py:723` | if | Any listed component name fails `NAME` | Renders a stopped settings row and returns. |
| `.github/bible/bible_queue.py:729` | conditional expression | Selection is `all` or empty | Uses all valid names; otherwise parses comma-separated names. |
| `.github/bible/bible_queue.py:731` | if | Selection contains unknown names or is empty | Renders stopped settings and returns. |
| `.github/bible/bible_queue.py:734` | conditional expression | Unknown names exist | Reports them; otherwise reports that no component was selected. |
| `.github/bible/bible_queue.py:736` | for | Open `bible-plan` issues exist | Closes each issue. |
| `.github/bible/bible_queue.py:740` | for | Each requested component | Evaluates its status. |
| `.github/bible/bible_queue.py:743` | except | Component evaluation raises `Exception` | Stores the exception type and at most 160 characters of its text. |
| `.github/bible/bible_queue.py:747` | for | Each requested component | Considers starting a `not started` row. |
| `.github/bible/bible_queue.py:748` | if | Row is `not started` and no cap or active count below cap | Attempts to start a fresh chunk. |
| `.github/bible/bible_queue.py:752` | except | Starting the chunk raises `RuntimeError` | Stores the exception text, capped at 160 characters. |
| `.github/bible/bible_queue.py:754` | if | Every row is `merged` | Adds whole-analysis assembly status. |

#### `Queue.plan_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:758-780` <!-- code: f5b3e835d2d7 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:718`) |
| Calls | `self.run_issues`, `issue_text`, `self.gh.create_issue`, `self.render`, `assignment`, `settings.get`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry` |
| Purpose | Creates or tracks the plan issue and reports plan-session progress. |

**Steps**

1. Gets open plan issues for the tracker run. (`.github/bible/bible_queue.py:760`)
2. If none are open, reads the plan title and body from the analysis ledger; when the body is empty, supplies built-in instructions to run passes 1 and 2, write the Components table, and finish discovery without starting components. It then creates and assigns the plan issue and renders its assigned status. (`.github/bible/bible_queue.py:761-769`)
3. Otherwise selects the first plan issue; if held, renders its human-needed status. (`.github/bible/bible_queue.py:770-772`)
4. Classifies its session; if Copilot reports a start error, marks the issue for human action and renders that status. (`.github/bible/bible_queue.py:773-776`)
5. On `no-start`, requests a retry; then renders the pull-request review state when a PR exists, or the session state otherwise. (`.github/bible/bible_queue.py:777-780`)

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
| `.github/bible/bible_queue.py:761` | if | No open plan issue exists | Reads the planned issue text and creates an assigned plan issue. |
| `.github/bible/bible_queue.py:763` | if | The loaded body is falsey | Uses built-in plan and discovery instructions. |
| `.github/bible/bible_queue.py:771` | if | The first open plan issue is held | Renders that a person must act. |
| `.github/bible/bible_queue.py:774` | if | Session state is `start-error` | Holds the issue and renders human-needed state. |
| `.github/bible/bible_queue.py:777` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:779` | conditional expression | `pr` exists | Renders review/merge PR number; otherwise renders the session state. |

#### `Queue.start_chunk(analysis, name, fresh=False, note="")`

Source: `.github/bible/bible_queue.py:782-794` <!-- code: 7f612dd5f454 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:750`), `Queue.component` (`.github/bible/bible_queue.py:860`, `.github/bible/bible_queue.py:896`) |
| Calls | `self.gh.branch_sha`, `self.gh.create_branch`, `self.gh.reset_branch`, `self.run_issues`, `comp_label`, `issue_text`, `self.gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Creates the component branch when absent, optionally resets it for the first chunk, and opens the next assigned chunk issue. |

**Steps**

1. Sets branch to `bible/<name>` and reads the default branch SHA. (`.github/bible/bible_queue.py:784-785`)
2. Creates the component branch at that SHA when absent; otherwise resets it when `fresh` is true and no issue of this run (the label `bible-run-<tracker number>` that `run_issues` adds) carries the component label, in any state. (`.github/bible/bible_queue.py:786-789`)
3. Reads the component issue text from the default branch, formats the Component/Base branch/Attempt header, and creates a labeled chunk issue with optional note and model assignment. (`.github/bible/bible_queue.py:790-794`)

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
| `.github/bible/bible_queue.py:786` | if | The component branch has no SHA | Creates the branch at the default branch SHA. |
| `.github/bible/bible_queue.py:788` | elif | Branch exists, `fresh` is true, and no issue of this run (label `bible-run-<n>`) with the component label exists, in any state | Resets the branch to the default branch SHA. |
| `.github/bible/bible_queue.py:793` | conditional expression | `note` is truthy | Adds the note and a newline before the body; otherwise adds no note prefix. |

#### `Queue.component(analysis, name)`

Source: `.github/bible/bible_queue.py:796-909` <!-- code: 8a269938c6be -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:742`) |
| Calls | `gh.branch_prs`, `pr.get`, `get`, `self.run_issues`, `comp_label`, `self.held`, `self.follow`, `gh.close`, `labels_of`, `max`, `h.get`, `status_of`, `status.get`, `time.monotonic`, `getattr`, `float`, `self.check`, `self.could_not_check`, `self.state.pop`, `min`, `as_int`, `self.estimate.get`, `self.start_chunk`, `len`, `i.get`, `gh.create_issue`, `report_facts`, `gh.file`, `accepted`, `gh.create_pr`, `bool`, `any`, `recheck_due`, `assignment`, `self.settings.get` |
| Purpose | Advances one component through its pull requests, sessions, gate, verification and revision rounds, final review pull request, or human hold, and returns the row shown in the tracker. |

**Steps**

1. Scans the pull requests from `bible/<name>` into the default branch. It skips one whose head repository is not this repository, that was created before the tracker, or whose body lacks `Tracker: #<n>`. The first matching pull request decides: merged returns `merged`; open returns `review the pull request #<n>`; closed without merging returns `needs a person: its pull request #<n> was closed without merging; reopen it, or start a new run` (`.github/bible/bible_queue.py:797-807`).
2. Takes the open `bible-chunk` and `bible-verify` issues of this run for the component. For the first one, `held` returns `released` (row `released: next step at the next check`), a truthy value (row `needs a person: see #<n>`), or a falsey value, and then `follow` decides the row (`.github/bible/bible_queue.py:808-819`).
3. With no issue of this run carrying the component label, in any state, returns `not started` (`.github/bible/bible_queue.py:820-821`).
4. Reads the run's `bible-hold` issues for the component in any state. An open hold that still has `bible-needs-human` returns the needs-person row; an open hold whose label a person removed is closed and the list is read again; `after` is the latest `closed_at` among the holds, or an empty string (`.github/bible/bible_queue.py:822-829`).
5. Reads the component's `status.json` on the branch, with `gate_ok, pages = (False, None)`. Only for the state `COMPONENT_DONE`: when `time.monotonic() + 2 * GATE_TIMEOUT + 300` exceeds the run deadline it returns `waiting for the next check (not enough of this run's time left for its check)`; otherwise it runs `check`. A `None` from `check` returns the `could_not_check` row (key `nocheck:<name>`) or `check could not run this time: retried at the next check`; a result clears that count (`.github/bible/bible_queue.py:830-840`).
6. When the gate did not pass (or was not run), counts the closed chunk issues created since the later of `after` and the latest merge of a pull request from the branch into the default branch. The estimate is `est_sessions` from `components.json`, a missing, zero or non-numeric value counting as 2, clamped to 1-10; the cap is `2 * estimate + 2`, at least `MIN_SESSION_CAP` (4) and at most `MAX_SESSION_CAP` (22). At or over the cap it creates a hold issue (`bible-hold`, `bible-needs-human`) and returns needs-person; otherwise it starts the next chunk with the note "Session `done` + 1 of about `estimate`", where `done` counts all closed chunk issues of this run for the component, and returns `session starting` (`.github/bible/bible_queue.py:841-861`, `.github/bible/bible_queue.py:82-83`).
7. After a passing gate, selects the completed closed verification issues since `after` (`closed_verify`) and all completed ones (`any_verify`); when any exists, reads the branch's component `verification-report.md` with `report_facts`, giving it a reader for sibling reports on the same branch. A report that `accepted` counts as verified, with a nonempty fingerprint equal to the pages' fingerprint, creates the pull request from the branch into the default branch and returns `review the pull request #<n>`. The pull request text says `verified (PASS, pages fingerprint <fp>)` also when the accepted verdict was `PASS AFTER CORRECTIONS` (`.github/bible/bible_queue.py:862-871`).
8. Decides between revision and verification. The report is about these pages when its fingerprint equals the pages' fingerprint; it needs revision when it exists and is not accepted. `chunk_since_verify` is true when a completed chunk issue closed after the last completed verification. With a report, no chunk since it, and `MAX_VERIFY_ROUNDS` (2) or more `closed_verify` issues, it creates a hold issue naming the last verdict and returns needs-person. When the report is about these pages, needs revision and no chunk followed it, it starts a revision chunk (note: `Revision (verdict <v>): apply <analysis>/ledger/components/<name>/verification-report.md ...`) and returns `session starting` (`.github/bible/bible_queue.py:872-898`, `.github/bible/bible_queue.py:76`).
9. Otherwise (no report, a report about other pages, or a revision just merged) it creates the issue `Codebase analysis - verify component <name>`, labelled `bible-verify`, assigned on `settings["verify_model"]`. When `recheck_due(facts)` is true the text ends with `RECHECK_ASK`, which asks for the re-check of a `PASS AFTER CORRECTIONS`. It returns `verify running` (`.github/bible/bible_queue.py:899-909`, `.github/bible/bible_queue.py:510-513`).

**Pseudo-code**

```text
for matching tracker PR: return merged, review, or needs-person status
if open chunk/verify issue: return released, needs-person, or follow(issue)
if no issue of this run with the component label ever existed: return not started
if a hold issue is open: return needs-person, or close it (label removed)
status = component status
gate_ok, pages = False, None
if status is COMPONENT_DONE:
    if insufficient run time: wait for next check
    gate_ok, pages = check(...)
    if check could not run: count toward human hold; return/wait
if not gate_ok:
    cap = min(max(4, 2 * min(max(est_sessions or 2, 1), 10) + 2), 22)
    if closed chunks since the reset point >= cap: create human hold; return
    else start next chunk; return
facts = report_facts(report on the branch, sibling reader) if a completed verification exists
if accepted(facts) and facts[2] == pages: create component PR; return review status
if facts and no chunk since the last verification and verifications >= 2: create human hold
if facts are about these pages and not accepted and no chunk since: start revision chunk
create verification issue (with RECHECK_ASK when recheck_due(facts)); return verify running
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:799` | for | For each pull request from `bible/<name>` into the default branch | Checks repository, tracker age and body reference. |
| `.github/bible/bible_queue.py:801` | if | The pull request is foreign, predates the tracker, or lacks its reference | Skips it. |
| `.github/bible/bible_queue.py:803` | if | The matching pull request is merged | Returns `merged`. |
| `.github/bible/bible_queue.py:805` | if | The matching pull request is open | Returns its review row. |
| `.github/bible/bible_queue.py:807` | return | The matching pull request is closed without merging | Returns the needs-person row for it. |
| `.github/bible/bible_queue.py:809` | if | An open chunk or verify issue exists | Takes its first issue. |
| `.github/bible/bible_queue.py:812` | if | `held` returns `released` | Returns the released row. |
| `.github/bible/bible_queue.py:814` | if | `held` returns another truthy value | Returns the needs-person row. |
| `.github/bible/bible_queue.py:820` | if | No issue of this run carries the component label, in any state | Returns `not started`. |
| `.github/bible/bible_queue.py:824` | if | At least one hold issue is open | Checks its human-required label. |
| `.github/bible/bible_queue.py:825` | if | The first open hold has `bible-needs-human` | Returns needs-person; otherwise closes that hold. |
| `.github/bible/bible_queue.py:832` | if | The status state is `COMPONENT_DONE` | Runs or defers the component gate. |
| `.github/bible/bible_queue.py:833` | if | The remaining run time is below the gate budget | Returns the wait-for-next-check row. |
| `.github/bible/bible_queue.py:836` | if | `check` returned `None` | Counts it and returns a hold or retry row. |
| `.github/bible/bible_queue.py:841` | if | The gate did not pass | Applies the bounded chunk-session policy. |
| `.github/bible/bible_queue.py:849` | if | Closed chunks since the reset point reach the cap | Creates and returns a human hold. |
| `.github/bible/bible_queue.py:865` | conditional expression | A completed verification exists | Reads its report; otherwise `facts` is `None`. |
| `.github/bible/bible_queue.py:867` | if | The report is accepted and its fingerprint is nonempty and equals the pages' | Creates the final component pull request and returns the review row. |
| `.github/bible/bible_queue.py:886` | if | A report was read, no chunk completed after the last verification, and the verifications since the hold release reach `MAX_VERIFY_ROUNDS` | Creates a human hold. |
| `.github/bible/bible_queue.py:895` | if | The report is about these pages, is not accepted, and no chunk completed after the last verification | Starts a revision chunk and returns `session starting`. |
| `.github/bible/bible_queue.py:907` | conditional expression | `recheck_due(facts)` is true | Appends `RECHECK_ASK` to the verification issue; otherwise an empty string. |

**Errors**: `component` has no handler of its own. An exception from it (a failed GitHub call, or the `RuntimeError` of an incomplete pull-request file list) goes to the per-component handler in `Queue.run`, which records `error this run (retried next run): <type>: <first 160 characters>` as that component's row and carries on with the others (`.github/bible/bible_queue.py:741-744`).

#### `Queue.follow(analysis, name, issue)`

Source: `.github/bible/bible_queue.py:911-968` <!-- code: 96d8861eb206 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:819`) |
| Calls | `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `str`, `str.startswith`, `os.path.basename`, `shown_files`, `status_of`, `as_int`, `status.get`, `issue.get`, `any`, `gh.file`, `gh.label`, `gh.merge`, `gh.unlabel`, `gh.close` |
| Purpose | Checks an assigned chunk or verification session and its PR, then retries, holds, waits, or validates and merges it. |

**Steps**

1. Sets branch `bible/<name>`, derives `verify` or `chunk` from labels, and classifies the session. Waiting returns `session starting`; start errors are held; no-start retries; running returns `<kind> running`. (`.github/bible/bible_queue.py:912-924`)
2. Defines the component ledger base and requests PR file names. A listing `RuntimeError` is retried/held. Chunk PRs may change component LLD, component API LLD and ledger files except `verification-*`; verification PRs may change only `verification-*` files and `citations.tsv` within the ledger. Disallowed paths are summarized with `shown_files` and retried/held. (`.github/bible/bible_queue.py:925-940`)
3. Reads component status at the PR head SHA. For a chunk at `WAITING_ANSWER`, adds `bible-waiting-answer` to both issue and PR only when the issue lacks it, then returns the wait status. (`.github/bible/bible_queue.py:941-947`)
4. For other chunks, compares `packets_done` at PR head with the branch, recognizes a revision from `"\nRevision ("` in issue body, and treats increased packets or `COMPONENT_DONE` as progress. `STOP` or no progress is retried; a revision must change an allowed page or `revision-log.md` and finish in `COMPONENT_DONE`, or it is retried/held. (`.github/bible/bible_queue.py:948-961`)
5. For verification, retries/holds if the report is absent at the PR head. Otherwise merges the PR, removes the waiting-answer label, closes the issue, and returns `<kind> merged`. (`.github/bible/bible_queue.py:962-968`)

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
| `.github/bible/bible_queue.py:913` | conditional expression | Issue has `bible-verify` | Sets kind to `verify`; otherwise `chunk`. |
| `.github/bible/bible_queue.py:915` | if | Session state is `waiting` | Returns `session starting`. |
| `.github/bible/bible_queue.py:917` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:920` | if | Session state is `no-start` | Calls retry logic. |
| `.github/bible/bible_queue.py:922` | conditional expression | Retry succeeds | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:923` | if | Session state is `running` | Returns `<kind> running`. |
| `.github/bible/bible_queue.py:928` | except | `gh.pr_files` raises `RuntimeError` | Retries or holds because the file list cannot be validated. |
| `.github/bible/bible_queue.py:930` | conditional expression | Retry succeeds after a file-list error | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:931` | if | Kind is `chunk` | Selects the chunk allowlist; otherwise selects the verify allowlist. |
| `.github/bible/bible_queue.py:938` | if | Any changed file is outside the selected allowlist | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:940` | conditional expression | Retry succeeds after disallowed files | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:942` | if | Kind is `chunk` | Checks chunk progress; otherwise checks the verification report. |
| `.github/bible/bible_queue.py:943` | if | Status is `WAITING_ANSWER` | Checks whether to add wait labels and returns the wait state. |
| `.github/bible/bible_queue.py:944` | if | Issue lacks `bible-waiting-answer` | Adds the label to issue and PR. |
| `.github/bible/bible_queue.py:951` | if | Status is `STOP` or packet count did not increase and state is not done | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:953` | conditional expression | Retry succeeds after no progress | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:955` | if | Revision has no changed allowed page or revision log | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:958` | conditional expression | Retry succeeds after an unchanged revision | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:959` | if | Revision did not finish in `COMPONENT_DONE` | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:961` | conditional expression | Retry succeeds after an incomplete revision | Returns starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:962` | elif | Verification report is absent at the PR head SHA | Retries or returns needs-person. |
| `.github/bible/bible_queue.py:964` | conditional expression | Retry succeeds after missing report | Returns starting; otherwise needs-person. |

#### `Queue.check(analysis, name, branch)`

Source: `.github/bible/bible_queue.py:970-995` <!-- code: 4b957b96bfcc -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:835`) |
| Calls | `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `printed.stdout.strip`, `().splitlines`, `run.stdout.strip` |
| Purpose | Runs the component coverage gate against an unpacked branch tarball and obtains its pages fingerprint. |

**Steps**

1. Builds the toolkit scripts directory. If `coverage.py` is absent, logs that the gate is skipped and treated as failing, then returns `(False, None)`. (`.github/bible/bible_queue.py:972-975`)
2. Creates a temporary work directory, downloads and extracts `branch`, then runs isolated `coverage.py` with `--repo`, `--analysis`, configured `--depth`, `--component` and `--report -`. Logs the final stripped output line or `no output`. (`.github/bible/bible_queue.py:976-986`)
3. Runs isolated `status.py --fingerprint --component` in the same work tree and returns `(run.returncode == 0, printed.stdout.strip() or None)`. (`.github/bible/bible_queue.py:987-990`)
4. On `RuntimeError` from tarball retrieval, logs the cause and returns `(None, None)`; on `TimeoutExpired`, logs the timeout and returns `(None, None)`. In either case, `finally` removes the temporary directory while ignoring cleanup errors. (`.github/bible/bible_queue.py:979-982`, `.github/bible/bible_queue.py:991-995`)

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
| `.github/bible/bible_queue.py:973` | if | `coverage.py` is not a file | Logs and returns `(False, None)`. |
| `.github/bible/bible_queue.py:980` | except | Tarball retrieval raises `RuntimeError` | Logs the error and returns `(None, None)`; cleanup still runs. |
| `.github/bible/bible_queue.py:991` | except | Either subprocess exceeds `GATE_TIMEOUT` | Logs the timeout and returns `(None, None)`; cleanup still runs. |


#### `Queue.could_not_check(key, what, hold_labels, hold_title)`

Source: `.github/bible/bible_queue.py:997-1008` <!-- code: d1918209875f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:837`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1059`) |
| Calls | `as_int`, `self.state.get`, `max`, `self.state.pop`, `self.gh.create_issue` |
| Purpose | Counts consecutive un-runnable checks and opens a human-hold issue after the configured threshold. |

**Steps**

1. Increments `self.state[key]` from the maximum of its existing integer value and zero, so a negative state cannot suppress the count. If the count is below `MAX_NOCHECK`, returns `None`. (`.github/bible/bible_queue.py:1000-1002`)
2. At the threshold, removes the count, creates a hold issue with tracker number, description, threshold, and the supplied hold labels plus `bible-hold`, `bible-needs-human` and the run label, then returns its issue number in a status string. (`.github/bible/bible_queue.py:1003-1008`)

**Pseudo-code**

```text
state[key] = max(as_int(state.get(key)), 0) + 1
if count < MAX_NOCHECK: return None
remove count; create labeled hold issue; return needs-person status
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1001` | if | Consecutive count is below `MAX_NOCHECK` | Returns `None` and waits for another check. |

#### `Queue.whole_fingerprint(analysis)`

Source: `.github/bible/bible_queue.py:1010-1025` <!-- code: c7fe54722506 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1057`) |
| Calls | `os.path.join`, `os.path.isfile`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `os.path.abspath`, `printed.stdout.strip`, `self.log`, `shutil.rmtree` |
| Purpose | Computes the analysis-page fingerprint from the default branch using the toolkit's `status.py`. |

**Steps**

1. Builds the toolkit scripts path and returns `None` if `status.py` is missing. Otherwise creates a temporary work directory and downloads the default-branch tarball. (`.github/bible/bible_queue.py:1012-1017`)
2. Runs isolated `status.py --fingerprint` for `analysis`, returning stripped stdout or `None` when empty. A tarball `RuntimeError` or process timeout is logged and returns `None`; `finally` removes the temporary tree. (`.github/bible/bible_queue.py:1018-1025`)

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
| `.github/bible/bible_queue.py:1013` | if | `status.py` is not a file | Returns `None` without creating a work directory. |
| `.github/bible/bible_queue.py:1021` | except | Tarball download raises `RuntimeError` or fingerprint process times out | Logs the failure and returns `None`. |

#### `Queue.assemble_phase(tracker, settings, analysis)`

Source: `.github/bible/bible_queue.py:1027-1148` <!-- code: 03058c41ff07 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:755`) |
| Calls | `settings.get`, `self.run_issues`, `i.get`, `self.whole_hold`, `report_facts`, `gh.file`, `max`, `any`, `p.get`, `gh.is_agent_pr`, `gh.pr_files`, `gh.linked_prs`, `accepted`, `time.monotonic`, `getattr`, `self.whole_fingerprint`, `self.could_not_check`, `self.state.pop`, `labels_of`, `gh.label`, `gh.comment`, `self.revise_all_step`, `gh.close`, `self.held`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `issue_text`, `recheck_due`, `assignment`, `gh.create_issue`, `self.deferred_updates`, `self.delta`, `sorted`, `set`, `shown_files`, `type`, `str`, `len` |
| Purpose | Coordinates assembly and whole-analysis verification, revision and deferred updates, then closes the tracker and marks its recorded updates as replayed when all phases finish. |

**Steps**

1. Processes the phases `bible-assemble` (model `settings["model"]`, issue text `assemble.md`) and `bible-verify-all` (model `settings["verify_model"]`, no text file) in that order; `closed_done` holds the phase's closed issues whose reason is `completed`. For verify-all it first returns the row of a whole-analysis hold that waits for a person (`whole_hold`), before any check of the whole analysis (`.github/bible/bible_queue.py:1029-1036`).
2. When verify-all has closed completed issues, it reads the report on the default branch with `report_facts` (the second argument reads sibling reports on the default branch) and takes the newest closed issue. `by_this_run` is true when some pull request linked to that issue is merged, into the default branch, by the agent, from this repository, touches the report, and holds the same report text at its head as the default branch now. `clean` is `accepted(facts)`: a `PASS`, or a `PASS AFTER CORRECTIONS` with a re-check, by the rules of `accepted` (`.github/bible/bible_queue.py:1037-1053`). `gh.pr_files` is called for each candidate pull request inside `by_this_run` (`.github/bible/bible_queue.py:1050`): its `RuntimeError` for an incomplete file list is not caught in this method, so it goes to `reconcile`, which logs it, and the next check tries again (`.github/bible/bible_queue.py:672-675`).
3. A clean report that is by this run and carries a fingerprint is checked against the pages now. It waits for the next check when too little of the run's time is left; a fingerprint that cannot be computed is counted toward a hold (`could_not_check`, key `nofp`, a person after 3 in a row) or waits for the next check; otherwise the `nofp` count is cleared, and when the report's fingerprint equals the pages' fingerprint the phase is done (`continue`) (`.github/bible/bible_queue.py:1054-1065`).
4. If the phase was not accepted in step 3 and no verify-all issue is open: a clean report (a stale one, one not by this run, or one with no fingerprint) on a newest issue that has neither the `bible-needs-revision` nor the `bible-stale-verdict` label gets `bible-stale-verdict` and a comment, and the row says the whole analysis is verified again; a report that is not accepted, on a newest issue without `bible-needs-revision`, gets that label and a comment, and the row says corrections are asked, naming the verdict or `missing`. In every other case the method falls through to step 5; a completed verify-all phase never advances except through step 3. For the assembly phase, a closed completed issue skips the phase (`.github/bible/bible_queue.py:1066-1078`).
5. For verify-all it calls `revise_all_step` and returns its row when it gives one (`.github/bible/bible_queue.py:1079-1082`). For an open phase issue it searches the linked pull requests for a merged, same-repository, agent-authored one into the default branch. For verify-all it reads the report again; a report that is not accepted gets `bible-needs-revision`, a comment, and the issue is closed as `not_planned`; otherwise the issue is closed, verify-all returns that its fingerprint is checked at the next check, and assembly moves on (`.github/bible/bible_queue.py:1083-1103`).
6. Without a merged pull request, it returns needs-person for a held issue; classifies the session, holds start errors, retries a session that did not start, reports a running pull request, and asks `continue_if_unfinished` about a finished one. It then returns review instructions or the session state (`.github/bible/bible_queue.py:1104-1118`).
7. With no open issue, it loads `assemble.md` or builds the whole-verification instructions. For the whole verification, when `recheck_due` is true for the report now on the default branch, it appends `RECHECK_ASK`. It creates and assigns the issue and returns its assigned row (`.github/bible/bible_queue.py:1119-1130`).
8. When both phases are done, it reads the paths recorded on the tracker (`deferred_updates`) and, if there are any, hands them to `delta` with `record=False`, which creates their update issues (or one hold issue when more than 10 components are touched, unless such a hold issue is already open). In that replay `delta` drops the paths with only a log line when `components.json` or `ledger/baseline.json` is missing on the default branch, and skips a component that already has an open `bible-delta` issue. An exception here is not caught in this method: the tracker stays open, `reconcile` logs it and the next check tries again. It then comments "Every component, the assembly and the whole verification are merged. Done." and closes the tracker, reads the recorded paths once more, and runs `delta` for those that were not in the first read; an error in that late step is commented on the closed tracker with the safe file names and the method returns `done` without the mark or the label below (`.github/bible/bible_queue.py:1131-1145`, `.github/bible/bible_queue.py:1341-1344`, `.github/bible/bible_queue.py:1368-1370`).
9. When the late step did not fail, it comments `Recorded code changes: <n>, in update issues.` with `REPLAYED_MARK`, where `n` is the number of paths in the first and the late read together, labels the tracker `bible-replayed` and returns `done` (`.github/bible/bible_queue.py:1146-1148`). A tracker that a person closes, or that was closed with a failed late step, is picked up later by `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:676-679`).

**Pseudo-code**

```text
for phase in (assemble, verify-all):
    closed_done = the phase's closed issues with reason completed
    if verify-all:
        if a whole-run hold waits for a person: return it
        if closed_done:
            newest, facts = latest closed issue, the report on the default branch
            clean = accepted(facts); by_this_run = written by this run's merged pull request
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
    create the phase issue (verify-all: RECHECK_ASK when recheck_due(report)); return "session assigned"
deferred = deferred_updates(tracker)
if deferred: delta(deferred, record=False)        # an error is not caught: the tracker stays open
comment Done; close the tracker
late = deferred_updates(tracker) - deferred
if late: try delta(late) except: comment the files to update by hand; return done
comment "Recorded code changes: n" + REPLAYED_MARK; label the tracker bible-replayed
return done
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:1029` | for | The assembly and verify-all phase tuples | Processes phases in order. |
| `.github/bible/bible_queue.py:1033` | if | The current phase is verify-all | Checks for a whole-analysis hold first. |
| `.github/bible/bible_queue.py:1035` | if | A whole-analysis hold row is returned | Stops and returns it. |
| `.github/bible/bible_queue.py:1037` | if | Verify-all has completed closed issues | Validates the newest report. |
| `.github/bible/bible_queue.py:1054` | if | The report is accepted, written by this run, and has a fingerprint | Checks that fingerprint against the current pages. |
| `.github/bible/bible_queue.py:1055` | if | Too little of the run's time is left for the fingerprint check | Returns a wait-for-next-check row. |
| `.github/bible/bible_queue.py:1058` | if | The current fingerprint could not be computed | Counts the failure and returns a hold or wait row. |
| `.github/bible/bible_queue.py:1061` | conditional expression | The no-check threshold was reached | Prefixes the human-hold row; otherwise returns the retry-at-next-check message. |
| `.github/bible/bible_queue.py:1064` | if | The report's fingerprint equals the current pages' fingerprint | Continues to the next phase. |
| `.github/bible/bible_queue.py:1066` | if | The report is accepted, the newest issue has neither label, and no verify-all issue is open | Labels it `bible-stale-verdict`, comments and returns. |
| `.github/bible/bible_queue.py:1072` | if | The report is not accepted, the newest issue lacks `bible-needs-revision`, and no verify-all issue is open | Marks the issue for revision and returns. |
| `.github/bible/bible_queue.py:1075` | conditional expression | Report facts exist | Puts the report's verdict in the comment; otherwise `missing`. |
| `.github/bible/bible_queue.py:1076` | conditional expression | Report facts exist | Puts the verdict in the returned row; otherwise `missing`. |
| `.github/bible/bible_queue.py:1077` | elif | A completed assembly issue exists | Skips assembly. |
| `.github/bible/bible_queue.py:1079` | if | The current phase is verify-all | Runs whole-analysis revision handling. |
| `.github/bible/bible_queue.py:1081` | if | The revision handler returned a row | Returns it. |
| `.github/bible/bible_queue.py:1084` | if | An open issue exists for the phase | Follows its linked pull request or session. |
| `.github/bible/bible_queue.py:1088` | if | A qualifying merged pull request exists | Closes or advances the phase. |
| `.github/bible/bible_queue.py:1089` | if | The merged pull request belongs to verify-all | Reads the whole-analysis report. |
| `.github/bible/bible_queue.py:1092` | if | The report is not accepted | Marks the issue for revision and closes it as not planned. |
| `.github/bible/bible_queue.py:1097` | conditional expression | Report facts exist | Puts the verdict in the comment; otherwise `missing`. |
| `.github/bible/bible_queue.py:1099` | conditional expression | Report facts exist | Puts the verdict in the returned row; otherwise `missing`. |
| `.github/bible/bible_queue.py:1101` | if | The merged pull request belongs to verify-all and the report was accepted | Returns that its fingerprint is checked at the next check. |
| `.github/bible/bible_queue.py:1104` | if | The open issue is held | Returns the needs-person row. |
| `.github/bible/bible_queue.py:1107` | if | The session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:1110` | if | The session state is `no-start` | Requests a retry. |
| `.github/bible/bible_queue.py:1112` | if | A pull request exists and the session is running | Returns running with the pull request number. |
| `.github/bible/bible_queue.py:1114` | if | A pull request exists and the session is finished | Checks for a missing completion marker. |
| `.github/bible/bible_queue.py:1116` | if | The continuation helper returns a row | Returns it. |
| `.github/bible/bible_queue.py:1118` | conditional expression | A pull request exists | Returns the review instruction; otherwise the session state. |
| `.github/bible/bible_queue.py:1119` | if | The phase has an issue-text file name | Loads its title and body; otherwise builds the verification instructions. |
| `.github/bible/bible_queue.py:1125` | if | `recheck_due` is true for the report on the default branch | Appends `RECHECK_ASK` to the verification issue text. |
| `.github/bible/bible_queue.py:1134` | if | Deferred changed paths exist | Creates update issues before closing the tracker; an exception from `delta` here is not caught and leaves the tracker open. |
| `.github/bible/bible_queue.py:1139` | if | New deferred paths arrived after the first replay | Attempts the late replay after closing the tracker. |
| `.github/bible/bible_queue.py:1142` | except | The late replay raises `Exception` | Comments a manual-update notice with a bounded error and the safe path list, and returns `done` without the mark or label. |

#### `Queue.deferred_updates(tracker)`

Source: `.github/bible/bible_queue.py:1150-1162` <!-- code: faad993a4a62 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:690`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1133`, `.github/bible/bible_queue.py:1138`) |
| Calls | `self.gh.me`, `self.gh.timeline`, `re.findall`, `e.get`, `actor.get`, `json.loads`, `isinstance`, `SAFE_FILE.match`, `sorted`, `set` |
| Purpose | Collects unique safe paths from this queue account's deferred-update comments on the tracker. |

**Steps**

1. Gets the current GitHub login and scans the tracker timeline. Ignores events that are not comments or whose actor/login is not the current account. (`.github/bible/bible_queue.py:1152-1155`)
2. Finds every `<!-- bible-deferred-update [...] -->` JSON list in each matching comment. Adds only string paths matching `SAFE_FILE`; malformed JSON is skipped. Returns a sorted list of unique paths. (`.github/bible/bible_queue.py:1156-1162`)

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
| `.github/bible/bible_queue.py:1153` | for | For each tracker timeline event | Extracts the actor and checks whether the queue authored a comment. |
| `.github/bible/bible_queue.py:1155` | if | Event is not a comment or actor login differs | Skips that event. |
| `.github/bible/bible_queue.py:1157` | for | Each embedded deferred-update marker | Parses its JSON list and filters the values. |
| `.github/bible/bible_queue.py:1160` | except | The embedded JSON is invalid | Ignores that marker and continues. |

#### `Queue.whole_hold()`

Source: `.github/bible/bible_queue.py:1164-1170` <!-- code: 6ba23ffaa54f -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1034`) |
| Calls | `self.run_issues`, `labels_of`, `self.gh.close` |
| Purpose | Reports an active human hold for the whole analysis and closes holds whose human-required label was removed. |

**Steps**

1. Iterates open issues labeled `bible-hold` and `bible-whole`. If an issue has `bible-needs-human`, returns a status containing its issue number; otherwise closes it, then continues. Returns `None` if no active hold remains. (`.github/bible/bible_queue.py:1166-1170`)

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
| `.github/bible/bible_queue.py:1166` | for | For each open whole-analysis hold | Checks whether it still needs a person. |
| `.github/bible/bible_queue.py:1167` | if | Hold has `bible-needs-human` | Returns the needs-person status; otherwise closes the released hold. |

#### `Queue.revise_all_step(tracker, analysis)`

Source: `.github/bible/bible_queue.py:1172-1250` <!-- code: 86a6e2d30283 -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1080`) |
| Calls | `self.run_issues`, `h.get`, `labels_of`, `gh.close`, `max`, `sorted`, `i.get`, `len`, `self.held`, `gh.linked_prs`, `p.get`, `gh.is_agent_pr`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `self.continue_if_unfinished`, `gh.pr_files`, `str.startswith`, `os.path.basename`, `shown_files`, `bool`, `any`, `gh.create_issue`, `assignment`, `self.settings.get` |
| Purpose | Applies a whole-analysis revision round after correction verdicts, including released holds, finished PRs, bounded retries and a final human hold. |

**Steps**

1. Loads all whole-run holds and identifies open ones. Returns needs-person when the first still has `bible-needs-human`; otherwise closes it and reloads holds. Uses the latest hold close time as the start of the current round. (`.github/bible/bible_queue.py:1177-1184`)
2. Finds closed whole-verification issues labeled needs-revision and stale-verdict. If there are no correction verdicts and stale rounds remain below `MAX_VERIFY_ROUNDS`, returns `None`; otherwise counts correction/stale rounds since the last release and finds revision issues. (`.github/bible/bible_queue.py:1187-1196`)
3. For an open revision issue, closes and returns when a qualifying linked agent PR is already merged. Otherwise a held issue returns needs-person; start-error is held, no-start requests retry, running returns its PR status, and a finished PR is passed to `continue_if_unfinished`, which may ask Copilot to continue or hold the issue for a person (also at once when Copilot's work failed before it started). (`.github/bible/bible_queue.py:1197-1218`)
4. A finished revision PR may change only files under `analysis/` whose basename does not start `verification-`; disallowed files are summarized and retried/held. If no revision is open, it first computes `last_asked` (the `closed_at` of the newest closed correction verdict), `newest_stale` and `corrections_applied`, which is true when a correction verdict exists and any `bible-revise-all` issue of the run, in any state, was closed as `completed` after `last_asked`. Then, in this order: when `rounds` has reached `MAX_VERIFY_ROUNDS` it creates the whole-analysis human hold and returns the needs-person row, whether or not corrections were applied; otherwise it returns `None` when there is no correction verdict, or `corrections_applied`, or a stale verdict is newer than `last_asked` (the loop then opens the next verification); otherwise it creates and assigns a revision issue carrying the verification-report instructions. (`.github/bible/bible_queue.py:1219-1250`)

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
| `.github/bible/bible_queue.py:1179` | if | An open hold exists | Checks whether the person label remains. |
| `.github/bible/bible_queue.py:1180` | if | Open hold has `bible-needs-human` | Returns needs-person; otherwise closes it and refreshes holds. |
| `.github/bible/bible_queue.py:1191` | if | No correction verdict exists and stale rounds are below the limit | Returns `None`. |
| `.github/bible/bible_queue.py:1197` | if | An open revision issue exists | Follows its PR/session. |
| `.github/bible/bible_queue.py:1201` | if | A qualifying linked agent PR is merged | Closes the revision issue and returns `None`. |
| `.github/bible/bible_queue.py:1204` | if | Revision issue is held | Returns needs-person. |
| `.github/bible/bible_queue.py:1207` | if | Session state is `start-error` | Holds the issue and returns needs-person. |
| `.github/bible/bible_queue.py:1210` | if | Session state is `no-start` | Requests retry and returns session starting. |
| `.github/bible/bible_queue.py:1213` | if | PR exists and session is running | Returns the running status. |
| `.github/bible/bible_queue.py:1215` | if | PR exists and session is finished | Checks for continuation and file-scope violations. |
| `.github/bible/bible_queue.py:1217` | if | Continuation helper returns a status | Returns it. |
| `.github/bible/bible_queue.py:1221` | if | Finished PR includes a file outside `analysis/` or a `verification-*` basename | Retries or holds. |
| `.github/bible/bible_queue.py:1224` | conditional expression | Retry succeeds | Returns session starting; otherwise needs-person. |
| `.github/bible/bible_queue.py:1225` | conditional expression | PR exists | Returns review/merge instruction; otherwise the session state. |
| `.github/bible/bible_queue.py:1226` | conditional expression | A correction verdict exists | Uses the latest correction close time; otherwise uses an empty string. |
| `.github/bible/bible_queue.py:1230` | if | `rounds` has reached `MAX_VERIFY_ROUNDS` and (there is no correction verdict, or corrections are applied, or a stale verdict is newer) | Only `pass`: control goes on to the hold at line 1136. |
| `.github/bible/bible_queue.py:1232` | elif | The same three conditions hold with `rounds` below the limit | Returns `None` so verification can proceed. |
| `.github/bible/bible_queue.py:1234` | if | `rounds` has reached `MAX_VERIFY_ROUNDS` (also when corrections are still pending) | Creates and returns a whole-analysis human hold. |

#### `Queue.continue_if_unfinished(issue, pr, kind, analysis)`

Source: `.github/bible/bible_queue.py:1252-1305` <!-- code: 076e7947548c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.assemble_phase` (`.github/bible/bible_queue.py:1115`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1216`) |
| Calls | `gh.pr_files`, `gh.me`, `max`, `e.get`, `gh.timeline`, `get`, `sorted`, `labels_of`, `gh.label`, `gh.comment`, `age`, `len`, `self.settings.get` |
| Purpose | For a session that ended before its end marker was written: holds the issue for a person at once when Copilot failed before starting, otherwise asks Copilot to continue on the same pull request, up to `MAX_CONTINUE` times. |

**Steps**

1. Chooses the end marker: `<analysis>/verification-report.md` when `kind` is `bible-verify-all`, otherwise `<analysis>/status.json`; returns `None` when the pull request's files (`pr_files`, which can raise) already include it. (`.github/bible/bible_queue.py:1260-1262`)
2. Reads the queue's own login (`gh.me()`), then `released`: the latest `unlabeled` timeline event on the issue for the label `bible-needs-human`, or the empty string. (`.github/bible/bible_queue.py:1263-1265`)
3. Reads the pull request's timeline and builds `work`, the `(event, created_at)` pairs for events in `WORK_EVENTS` performed by the `AGENT_APP` app; `finished` is the latest timestamp among those that are not `copilot_work_started` (a failure counts). (`.github/bible/bible_queue.py:1266-1269`, `.github/bible/bible_queue.py:70`)
4. `asked` is the sorted timestamps of `commented` events by the queue's login that contain `CONTINUE_MARK` and are newer than `released`; anyone else's copy of the marker text is not counted. (`.github/bible/bible_queue.py:1270-1272`, `.github/bible/bible_queue.py:85`)
5. `since` is the latest request when there is one (`asked[-1]`), otherwise `released`: the work since the queue's last request, or, before any request, since a person last released the hold (the whole history when nobody has). `after` is the names of the work events, in time order, newer than `since`. So a first session that fails before it starts is judged here too, without a continuation having been asked. (`.github/bible/bible_queue.py:1273-1276`)
6. Early hold: when the last event of `after` is `copilot_work_finished_failure` and no `copilot_work_started` is among `after`, Copilot did not run at all. If the issue does not carry `bible-needs-human` yet, labels it and comments the likely causes (the account's Copilot AI credits or monthly budget, Copilot turned off for the repository) and tells a person to fix the cause and remove the label; returns `"<kind>: Copilot could not start: see #<issue>"` without using up another continuation. (`.github/bible/bible_queue.py:1277-1286`)
7. When a request exists, is newer than `finished` and is not older than `NO_PR_AFTER` (30 minutes), returns `"<kind>: continuing (pull request #<n>)"`: Copilot has been asked and has not picked it up yet. (`.github/bible/bible_queue.py:1287-1288`, `.github/bible/bible_queue.py:74`)
8. When `len(asked) >= MAX_CONTINUE` (3), labels the issue `bible-needs-human` and comments the count and the marker, unless the label is already there; returns `"<kind>: needs a person: see #<issue>"`. (`.github/bible/bible_queue.py:1289-1295`, `.github/bible/bible_queue.py:84`)
9. Otherwise comments on the pull request `@copilot continue: run next.py ... --new-session` with `--depth` from `settings["depth"]` (default `deep`) and an ending that depends on `kind` (assemble, revise-all or verify-all), followed by `CONTINUE_MARK`; returns `"<kind>: continuing, session <len(asked)+2> (pull request #<n>)"`. (`.github/bible/bible_queue.py:1296-1305`)

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
| `.github/bible/bible_queue.py:1260` | conditional expression | `kind` is `bible-verify-all` | the marker is `verification-report.md`; otherwise `status.json` |
| `.github/bible/bible_queue.py:1261` | if | the marker is among the pull request's files | returns `None`: the work is done |
| `.github/bible/bible_queue.py:1275` | conditional expression | at least one request of the queue is newer than the last release | `since` is the latest request; otherwise it is the release time (or the empty string) |
| `.github/bible/bible_queue.py:1277` | if | the last event after `since` is `copilot_work_finished_failure` and none of the events after `since` is `copilot_work_started` | Copilot never started: enters the early hold |
| `.github/bible/bible_queue.py:1279` | if | the issue does not have `bible-needs-human` | labels it and posts the failed-before-start comment; with the label present only the return happens |
| `.github/bible/bible_queue.py:1287` | if | a request exists, is newer than the last finished event and is at most `NO_PR_AFTER` old | returns continuing (asked, not started) |
| `.github/bible/bible_queue.py:1289` | if | `MAX_CONTINUE` requests have been made since the last release | enters the hold for a person |
| `.github/bible/bible_queue.py:1290` | if | the issue does not have `bible-needs-human` | labels it and posts the count comment; with the label present only the return happens |

**Output and side effects**: returns `None` or a one-line status string; may add the label `bible-needs-human` and a comment on the issue (early hold, or limit reached), or a `@copilot continue` comment on the pull request. The `[kind]` dictionary lookup raises `KeyError` for a kind other than the three listed (assumed: Python builtin behaviour of a missing key) (`.github/bible/bible_queue.py:1300-1303`). `pr_files` can raise the `RuntimeError` of an incomplete file list, which this method does not catch (`.github/bible/bible_queue.py:1261`).

#### `Queue.render(tracker, settings, rows)`

Source: `.github/bible/bible_queue.py:1307-1318` <!-- code: bc302114ec7d -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.run` (`.github/bible/bible_queue.py:725`, `.github/bible/bible_queue.py:732`, `.github/bible/bible_queue.py:756`), `Queue.plan_phase` (`.github/bible/bible_queue.py:769`, `.github/bible/bible_queue.py:772`, `.github/bible/bible_queue.py:776`, `.github/bible/bible_queue.py:779`) |
| Calls | `rows.items`, `json.dumps`, `getattr`, `now`, `().isoformat`, `join`, `body.split`, `tracker.get`, `self.gh.set_body`, `self.log` |
| Purpose | Builds tracker status rows with hidden state/settings markers, updates the body when its non-time content changes, and logs each row. |

**Steps**

1. Builds a fixed introduction and table header, then appends one formatted component/state row per `rows.items()`. (`.github/bible/bible_queue.py:1308-1310`)
2. Adds a hidden `bible-state` JSON comment from `self.state` (or `{}`), an `Updated` timestamp to minute precision, and a hidden `bible-settings` JSON comment; joins the lines with newlines. (`.github/bible/bible_queue.py:1311-1314`)
3. Compares each body's text before `Updated`; calls `set_body` only when that prefix differs. It then logs each row with a 20-character padded key. (`.github/bible/bible_queue.py:1315-1318`)

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
| `.github/bible/bible_queue.py:1315` | if | Text before `Updated` differs | Replaces the tracker body. |
| `.github/bible/bible_queue.py:1317` | for | For each `(key, value)` row | Logs the padded key and state. |

#### `Queue.delta(changed, settings_analysis="codebase-analysis", record=True)`

Source: `.github/bible/bible_queue.py:1321-1381` <!-- code: 48ca17e0332c -->

| | |
| --- | --- |
| Kind | instance method |
| Called by | `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:692`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1135`, `.github/bible/bible_queue.py:1141`), `main` (`.github/bible/bible_queue.py:1428`) |
| Calls | `gh.default_branch`, `UPDATED.search`, `t.get`, `found.group`, `gh.issues`, `age`, `last_activity`, `range`, `max`, `len`, `SAFE_FILE.match`, `gh.comment`, `json.dumps`, `json_file`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `components.component_map`, `sorted`, `p.startswith`, `NAME.match`, `gh.create_issue`, `comp_label`, `assignment`, `components.assign` |
| Purpose | Defers changed paths onto an active tracker, or opens bounded component-update issues when the assembled analysis and baseline are available. |

**Steps**

1. Sets the default branch and defines `last_activity` from the tracker body's `Updated` marker or its creation time. With `record=True`, finds active tracker issues updated within `ABANDONED_AFTER`; with `record=False`, does not search for one. (`.github/bible/bible_queue.py:1322-1327`)
2. If a tracker is active, filters changed paths through `SAFE_FILE`, splits safe paths into `DEFERRED_PER_COMMENT` chunks (at least one loop iteration), posts a marker comment for each chunk, notes omitted unusual names, logs the deferral, and returns. The recorded paths become update issues in two ways: `assemble_phase` calls `delta` again with `record=False` at its Done step (`.github/bible/bible_queue.py:1133-1141`), and `replay_closed_runs` calls it with the default `record=True` for a closed tracker that does not yet carry `bible-replayed`, which covers a tracker a person closed and a run that never reached Done (`.github/bible/bible_queue.py:685-692`, `.github/bible/bible_queue.py:1146-1147`). If a run is open at that time, the replayed paths are recorded on it again instead (`.github/bible/bible_queue.py:1327-1340`). (`.github/bible/bible_queue.py:1328-1340`)
3. Otherwise loads `components.json` and requires `ledger/baseline.json`; if either is absent, logs and returns. Adds the analysis toolkit scripts to `sys.path`, imports `components`, maps changed paths outside the analysis and skills directories to sorted touched component names, and filters them through `NAME`. (`.github/bible/bible_queue.py:1341-1352`)
4. If the number of touched components exceeds `MAX_DELTA_ISSUES`, creates one human-needed issue only when none is already open, logs and returns. For each touched component, gets the assigned files and safe display names; an existing component delta issue is logged and skipped. Otherwise creates an assigned issue with up to 20 shown file paths and the update instructions, then logs the file count. (`.github/bible/bible_queue.py:1353-1381`)

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
| `.github/bible/bible_queue.py:1326` | conditional expression | An `Updated` marker matched | Uses the marker time; otherwise uses tracker creation time. |
| `.github/bible/bible_queue.py:1327` | conditional expression | `record` is true | Finds recently active trackers; otherwise uses an empty list. |
| `.github/bible/bible_queue.py:1328` | if | An active tracker exists | Records changes in a comment on its first issue and returns. |
| `.github/bible/bible_queue.py:1332` | for | Safe paths are chunked for comments | Posts each chunk; an empty safe list still enters one iteration. |
| `.github/bible/bible_queue.py:1336` | conditional expression | First chunk has unusual-name paths | Adds their count to the comment; otherwise adds no warning. |
| `.github/bible/bible_queue.py:1342` | if | Catalog or baseline is absent | Logs and returns without creating issues. |
| `.github/bible/bible_queue.py:1353` | if | Touched component count exceeds `MAX_DELTA_ISSUES` | Routes the change to human review and returns. |
| `.github/bible/bible_queue.py:1355` | if | No `bible-delta`/`bible-needs-human` issue exists | Creates the shared human-needed issue. |
| `.github/bible/bible_queue.py:1363` | for | For each valid touched component | Selects its changed files and issues. |
| `.github/bible/bible_queue.py:1368` | if | A component delta issue is already open | Logs and skips a duplicate. |
| `.github/bible/bible_queue.py:1378` | conditional expression | A file has an unusual name | Adds a count of hidden paths; otherwise no suffix is added. |

## Functions and methods

### `main()`

Source: `.github/bible/bible_queue.py:1384-1430` <!-- code: d5e645d7911f -->

| | |
| --- | --- |
| Kind | module entry point |
| Called by | Module guard (`.github/bible/bible_queue.py:1433-1434`) |
| Calls | `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str`, `args.verify_model.strip`, `args.components.split`, `json.dumps`, `issue.get`, `open`, `l.strip`, `NAME.match` |
| Purpose | Parses `start`, `reconcile`, and `delta` commands and dispatches to the queue workflow. |

**Steps**

1. Builds a required-subcommand parser from the module docstring's first line; defines `start` options including `--analysis` and `--depth`, `reconcile`, and `delta` options, then parses arguments. (`.github/bible/bible_queue.py:1385-1398`)
2. Reads `GITHUB_REPOSITORY` and `GH_TOKEN`; raises `SystemExit` if either is falsey, then constructs `GitHub` and `Queue`. (`.github/bible/bible_queue.py:1400-1404`)
3. For `start`, requires a nonempty verification model different from the normal model, parses component names, and requires at least one selection with each name either `all` or matching `NAME`. (`.github/bible/bible_queue.py:1406-1411`)
4. Ensures labels and exits if a tracker is already open. Builds settings, then calls `settings_of` on the generated marker; if validation rejects the settings, raises `SystemExit` explaining the allowed analysis path, depth, and model characters. Otherwise it creates a tracker issue with hidden settings JSON and prints its issue number and queue-start guidance. (`.github/bible/bible_queue.py:1412-1422`)
5. For `reconcile`, invokes `queue.reconcile`; otherwise reads nonempty stripped lines from the changed-file input and calls `queue.delta`. (`.github/bible/bible_queue.py:1423-1428`)
6. Converts `RuntimeError` from command handling to `SystemExit` with the error text. (`.github/bible/bible_queue.py:1429-1430`)

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
| `.github/bible/bible_queue.py:1401` | if | Repository or token is missing | Exits with an environment requirement. |
| `.github/bible/bible_queue.py:1402` | raise | Required environment is missing | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1406` | if | Command is `start` | Validates and starts a run. |
| `.github/bible/bible_queue.py:1407` | if | Verification model is empty or equals normal model | Exits with the model requirement. |
| `.github/bible/bible_queue.py:1408` | raise | Model validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1410` | if | No component names are supplied, or a name other than `all` fails `NAME` | Exits with component-selection guidance. |
| `.github/bible/bible_queue.py:1411` | raise | Selection validation fails | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1413` | if | Tracker already exists | Exits without starting another run. |
| `.github/bible/bible_queue.py:1414` | raise | Open tracker exists | Raises `SystemExit`. |
| `.github/bible/bible_queue.py:1417` | if | Generated settings fail `settings_of` validation | Exits with the settings requirement. |
| `.github/bible/bible_queue.py:1418-1419` | raise | Generated settings are unsafe or unsupported | Raises `SystemExit` with allowed path, depth, and model rules. |
| `.github/bible/bible_queue.py:1423` | elif | Command is `reconcile` | Calls `queue.reconcile`. |
| `.github/bible/bible_queue.py:1425` | else | Command is `delta` | Reads changed paths and calls `queue.delta`. |
| `.github/bible/bible_queue.py:1429` | except | Command handling raises `RuntimeError` | Converts it to `SystemExit`. |
| `.github/bible/bible_queue.py:1430` | raise | A `RuntimeError` was caught | Raises `SystemExit` with the error text. |
| `.github/bible/bible_queue.py:1433` | if | Module is run as a script | Calls `main`. |
| `.github/bible/bible_queue.py:1434` | call | Script guard is active | Dispatches the CLI entry point. |

### `now()`

Source: `.github/bible/bible_queue.py:380-382` <!-- code: 9fb56903ebfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `age` (`.github/bible/bible_queue.py:386`), `Queue.render` (`.github/bible/bible_queue.py:1312`) |
| Calls | `os.environ.get`, `datetime.datetime.fromisoformat`, `datetime.datetime.now`, `replace` |
| Purpose | Returns the configured test time or the current UTC time. |

**Steps**

1. Reads `BIBLE_NOW`. (`.github/bible/bible_queue.py:381`)
2. If set, replaces `Z` with `+00:00` and parses the ISO timestamp; otherwise returns the current timezone-aware UTC datetime. (`.github/bible/bible_queue.py:382`)

**Pseudo-code**

```text
stamp = BIBLE_NOW
if stamp: parse ISO stamp after replacing Z with +00:00
else: return current UTC time
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:382` | conditional expression | `stamp` is truthy | Parses the configured time; otherwise obtains current UTC time. |

### `age(stamp)`

Source: `.github/bible/bible_queue.py:385-386` <!-- code: f2f8bb65e56f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:583`, `.github/bible/bible_queue.py:587`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1287`), `Queue.delta` (`.github/bible/bible_queue.py:1327`) |
| Calls | `now`, `datetime.datetime.fromisoformat`, `replace`, `total_seconds` |
| Purpose | Returns elapsed seconds between `stamp` and `now()`. |

**Steps**

1. Replaces `Z` in `stamp` with `+00:00`, parses it as an ISO datetime, subtracts it from `now()`, and returns `total_seconds()`. (`.github/bible/bible_queue.py:386`)

**Pseudo-code**

```text
return (now() - parse ISO stamp after replacing Z with +00:00).total_seconds()
```

### `shown_files(paths, limit=10)`

Source: `.github/bible/bible_queue.py:399-404` <!-- code: 42118ce2fbc4 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.follow` (`.github/bible/bible_queue.py:939`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1144`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1223`) |
| Calls | `SAFE_FILE.match`, `len`, `join` |
| Purpose | Formats safe paths for issue text and summarizes paths with unusual characters without quoting them. |

**Steps**

1. Partitions `paths` into names matching `SAFE_FILE` and the count that do not. Formats at most `limit` safe names in backticks, appending a count for additional safe names and a separate count for unusual names. (`.github/bible/bible_queue.py:400-404`)

**Pseudo-code**

```text
plain = paths matching SAFE_FILE
other = len(paths) - len(plain)
return quoted first limit names + counts of remaining safe and unusual names
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:403` | conditional expression | More safe names exist than `limit` | Adds the number of omitted safe names; otherwise adds nothing. |
| `.github/bible/bible_queue.py:404` | conditional expression | At least one path has unusual characters | Adds the count without including those paths; otherwise adds nothing. |

### `settings_of(tracker)`

Source: `.github/bible/bible_queue.py:407-427` <!-- code: 828d76009663 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.reconcile` (`.github/bible/bible_queue.py:668`), `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:692`), `main` (`.github/bible/bible_queue.py:1417`) |
| Calls | `SETTINGS.search`, `tracker.get`, `json.loads`, `match.group`, `isinstance`, `str`, `data.get`, `SAFE_PATH.match`, `analysis.split`, `SAFE_MODEL.match` |
| Purpose | Parses and validates the JSON settings marker from a tracker, returning `None` when absent, malformed, or unsafe. |

**Steps**

1. Searches the tracker body, defaulting a missing or falsey body to an empty string, and parses the marker's first capture group when present. (`.github/bible/bible_queue.py:413-414`)
2. Returns `None` for invalid JSON or a non-dictionary parsed value. (`.github/bible/bible_queue.py:415-416`)
3. Reads `analysis`, defaulting to `codebase-analysis`, and rejects paths that fail `SAFE_PATH` or contain `..` path segments. (`.github/bible/bible_queue.py:417-419`)
4. Rejects depths outside `DEPTH_VALUES`, and rejects nonempty `model` or `verify_model` values that fail `SAFE_MODEL`. (`.github/bible/bible_queue.py:420-425`)
5. Returns the validated settings dictionary. (`.github/bible/bible_queue.py:427`)

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
| `.github/bible/bible_queue.py:413` | conditional expression | A settings marker matched | Parses its first group; otherwise uses `None`. |
| `.github/bible/bible_queue.py:414` | except | JSON parsing raises `ValueError` | Returns `None`. |
| `.github/bible/bible_queue.py:416` | if | Parsed value is not a dictionary | Returns `None`. |
| `.github/bible/bible_queue.py:419` | if | Analysis path is unsafe | Returns `None`. |
| `.github/bible/bible_queue.py:421` | if | Depth is not an allowed value | Returns `None`. |
| `.github/bible/bible_queue.py:423` | for | For `model` and `verify_model` | Validates each configured model value. |
| `.github/bible/bible_queue.py:425` | if | A nonempty model fails `SAFE_MODEL` | Returns `None`. |

### `labels_of(item)`

Source: `.github/bible/bible_queue.py:430-431` <!-- code: 7a809f2b23af -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:589`), `Queue.replay_closed_runs` (`.github/bible/bible_queue.py:686`), `Queue.held` (`.github/bible/bible_queue.py:603`, `.github/bible/bible_queue.py:618`), `Queue.model_for` (`.github/bible/bible_queue.py:631`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:659`), `Queue.component` (`.github/bible/bible_queue.py:825`), `Queue.follow` (`.github/bible/bible_queue.py:913`, `.github/bible/bible_queue.py:944`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1066`, `.github/bible/bible_queue.py:1072`), `Queue.whole_hold` (`.github/bible/bible_queue.py:1167`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1180`), `Queue.continue_if_unfinished` (`.github/bible/bible_queue.py:1279`, `.github/bible/bible_queue.py:1290`) |
| Calls | `item.get`, `isinstance` |
| Purpose | Returns a set of label names from strings or label objects. |

**Steps**

1. Reads `labels`, defaulting to an empty list; for each element, uses its `name` when it is a dictionary and otherwise keeps the element itself. (`.github/bible/bible_queue.py:431`)

**Pseudo-code**

```text
return {label["name"] if label is a dict else label
        for label in item.labels or []}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:431` | conditional expression | A label item is a dict | Uses `item["name"]`; otherwise preserves the item value. |

### `comp_label(name)`

Source: `.github/bible/bible_queue.py:434-435` <!-- code: 5ead08c5004d -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.start_chunk` (`.github/bible/bible_queue.py:788`, `.github/bible/bible_queue.py:793`), `Queue.component` (`.github/bible/bible_queue.py:808`, `.github/bible/bible_queue.py:820`, `.github/bible/bible_queue.py:822`, `.github/bible/bible_queue.py:828`, `.github/bible/bible_queue.py:837`, `.github/bible/bible_queue.py:844`, `.github/bible/bible_queue.py:857`, `.github/bible/bible_queue.py:859`, `.github/bible/bible_queue.py:862`, `.github/bible/bible_queue.py:864`, `.github/bible/bible_queue.py:882`, `.github/bible/bible_queue.py:893`, `.github/bible/bible_queue.py:908`), `Queue.delta` (`.github/bible/bible_queue.py:1368`, `.github/bible/bible_queue.py:1380`) |
| Calls | None |
| Purpose | Prefixes a component name with `bible/`. |

**Steps**

1. Returns the string `bible/` followed by `name`. (`.github/bible/bible_queue.py:435`)

**Pseudo-code**

```text
return "bible/" + name
```

### `issue_text(gh, path, ref, fallback_title)`

Source: `.github/bible/bible_queue.py:438-444` <!-- code: 0533b3261be5 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.plan_phase` (`.github/bible/bible_queue.py:762`), `Queue.start_chunk` (`.github/bible/bible_queue.py:790`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1120`) |
| Calls | `gh.file`, `splitlines`, `startswith`, `strip`, `join`, `len` |
| Purpose | Reads a title/body pair from a ledger issue file, with a fallback title when no header exists. |

**Steps**

1. Reads the file through `gh.file`, converting a falsey result to `""`, then splits it into lines. (`.github/bible/bible_queue.py:440-441`)
2. If the first line starts with `Title:`, returns its stripped suffix as the title and the stripped remaining lines joined by newlines as the body. (`.github/bible/bible_queue.py:442-443`)
3. Otherwise returns `fallback_title` and the stripped full text. (`.github/bible/bible_queue.py:444`)

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
| `.github/bible/bible_queue.py:442` | if | `lines` is nonempty and the first line starts with `Title:` | Returns header title and remaining body; otherwise returns fallback title and full text. |

### `assignment(gh, base, model)`

Source: `.github/bible/bible_queue.py:447-451` <!-- code: da5ca422ae7f -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.held` (`.github/bible/bible_queue.py:626`), `Queue.fail_or_retry` (`.github/bible/bible_queue.py:660`), `Queue.plan_phase` (`.github/bible/bible_queue.py:768`), `Queue.start_chunk` (`.github/bible/bible_queue.py:794`), `Queue.component` (`.github/bible/bible_queue.py:908`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1129`), `Queue.revise_all_step` (`.github/bible/bible_queue.py:1249`), `Queue.delta` (`.github/bible/bible_queue.py:1380`) |
| Calls | None |
| Purpose | Builds the target repository and base-branch assignment, optionally including a model. |

**Steps**

1. Initializes the result with `target_repo: gh.repo` and `base_branch: base`. (`.github/bible/bible_queue.py:448`)
2. Adds `model` only when truthy, then returns the result. (`.github/bible/bible_queue.py:449-451`)

**Pseudo-code**

```text
out = {target_repo: gh.repo, base_branch: base}
if model: out.model = model
return out
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:449` | if | `model` is truthy | Adds `model` to the assignment. |

### `json_file(gh, path, ref)`

Source: `.github/bible/bible_queue.py:454-459` <!-- code: 37acfbecddfa -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `status_of` (`.github/bible/bible_queue.py:554`), `Queue.run` (`.github/bible/bible_queue.py:716`), `Queue.delta` (`.github/bible/bible_queue.py:1341`) |
| Calls | `gh.file`, `json.loads` |
| Purpose | Reads a file and parses JSON, returning `None` for missing or invalid content. |

**Steps**

1. Reads the file using `gh.file`. (`.github/bible/bible_queue.py:455`)
2. Returns parsed JSON for truthy text, or `None` when the text is falsey. (`.github/bible/bible_queue.py:456-457`)
3. Returns `None` if parsing raises `ValueError`. (`.github/bible/bible_queue.py:458-459`)

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
| `.github/bible/bible_queue.py:457` | conditional expression | `text` is truthy | Parses JSON; otherwise returns `None`. |
| `.github/bible/bible_queue.py:458` | except | JSON parsing raises `ValueError` | Returns `None`. |

### `section(text, title)`

Source: `.github/bible/bible_queue.py:462-468` <!-- code: 55167fd6e3c2 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `report_facts` (`.github/bible/bible_queue.py:488`, `.github/bible/bible_queue.py:493`, `.github/bible/bible_queue.py:503`) |
| Calls | `re.search`, `re.escape`, `match.end`, `nxt.start` |
| Purpose | Returns a Markdown level-two section's text, or an empty string if its heading is absent. |

**Steps**

1. Searches for a line matching exactly a level-two heading with the escaped `title`. (`.github/bible/bible_queue.py:463`)
2. Returns `""` if no heading matches. (`.github/bible/bible_queue.py:464-465`)
3. Slices text after the matched heading through the next level-two heading, or through end of text when there is no next heading. (`.github/bible/bible_queue.py:466-468`)

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
| `.github/bible/bible_queue.py:464` | if | No heading matched | Returns an empty string. |
| `.github/bible/bible_queue.py:468` | conditional expression | A next level-two heading matched | Returns the section before it; otherwise returns the remaining text. |

### `report_facts(text, fetch=None, depth=0)`

Source: `.github/bible/bible_queue.py:478-507` <!-- code: 3d07b38a73bb -->

| | |
| --- | --- |
| Kind | module function, recursive |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:865`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1040`, `.github/bible/bible_queue.py:1090`, `.github/bible/bible_queue.py:1125`), and itself (`.github/bible/bible_queue.py:500`) |
| Calls | `re.sub`, `re.findall`, `len`, `sum`, `section`, `splitlines`, `lstrip`, `startswith`, `re.search`, `re.match`, `RECHECK_LINE.search`, `RECHECK_OF_ROW.search`, `ACCURACY_ROW.findall`, `float`, `min`, `strip`, `fetch`, `REPORT_NAME.match`, `base.group`, `printed.group`, `recheck.group`, `int`, `bool`, `upper`, `report_facts` |
| Purpose | Reads a verification report into a six-value tuple: the verdict, the number of major corrections, the pages fingerprint, the re-check count, the lowest accuracy, and whether the report is itself a re-check. |

**Inputs**

| Name | Type | Meaning | Checked how |
| --- | --- | --- | --- |
| `text` | string or `None` | The report's text, as read from GitHub | A falsey value returns `None` (`.github/bible/bible_queue.py:481-482`). |
| `fetch` | callable or `None` | Reads a sibling report by file name (the callers pass a lambda over `gh.file`) | Used only when the report names an earlier round and `fetch` is given (`.github/bible/bible_queue.py:499`). |
| `depth` | int, default `0` | How many earlier reports the chain has followed | The chain stops at depth 20 (`.github/bible/bible_queue.py:499`). |

**Steps**

1. Returns `None` for a falsey `text` (`.github/bible/bible_queue.py:481-482`).
2. Builds `visible`, the text without HTML comments and fenced code blocks (`.github/bible/bible_queue.py:483`). It finds the `Verdict` rows whose cell holds `PASS AFTER CORRECTIONS`, `PASS` or `FAIL` (optionally in bold) and, separately, every row that starts with `Verdict` (`.github/bible/bible_queue.py:484-485`).
3. Unless there is exactly one of each, returns `("UNREADABLE", 0, None, None, None, False)` (`.github/bible/bible_queue.py:486-487`).
4. Counts the lines of the `Corrections` section of the raw `text` (not `visible`) that start with `|` and hold a `major` cell (`.github/bible/bible_queue.py:488-489`).
5. Reads the 16-hex `Analysis fingerprint` row (`.github/bible/bible_queue.py:490`), the "After corrections: ... X of Y confirmed" line (`.github/bible/bible_queue.py:491`), the `Re-check of` row (`.github/bible/bible_queue.py:492`), and every `Accuracy` percentage in the `Scores` section; the accuracy is the lowest of them, or `None` when there are none (`.github/bible/bible_queue.py:493-494`).
6. When the report has both a `Re-check of` row and a confirmed-count line, it follows the chain: the base name is the row's cell, the earlier report is fetched only when `fetch` is given, the name matches `verification-report` followed by word, dot or hyphen characters and `.md`, and `depth` is below 20; the earlier report is parsed by a recursive call; its accuracy counts unless it is missing or `UNREADABLE`. The result is `None` when the earlier accuracy is missing, otherwise the lower of the two accuracies (or the earlier one when this report has none) (`.github/bible/bible_queue.py:495-502`).
7. Collects the table lines of the `Noticed outside the re-check` section of `visible` that are not a header, a separator or a `none` row (`.github/bible/bible_queue.py:503-504`).
8. Returns `(verdict.upper(), majors, fingerprint or None, (X, Y) or None, accuracy, bool(base or noted))` (`.github/bible/bible_queue.py:506-507`). The last value is true when the report names its round or lists items noticed outside the re-check.

**Pseudo-code**

```text
if not text: return None
visible = text without comments and fenced code
one verdict row holding one verdict, else return ("UNREADABLE", 0, None, None, None, False)
majors = count of "major" rows in the raw Corrections section
fingerprint, X-of-Y line, "Re-check of" row, lowest Accuracy in Scores
if "Re-check of" row and X-of-Y line:
    older = fetch(name) when fetch, name is a report file name, depth < 20
    accuracy = None if the chain is broken else min(older accuracy, this accuracy)
noted = rows of "Noticed outside the re-check"
return (verdict, majors, fingerprint, (X, Y) or None, accuracy, bool("Re-check of" row or noted))
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:481` | if | `text` is falsey | Returns `None`. |
| `.github/bible/bible_queue.py:486` | if | The verdict count or the verdict-row count is not exactly one | Returns the `UNREADABLE` tuple. |
| `.github/bible/bible_queue.py:494` | conditional expression | At least one `Accuracy` row was found | Uses the lowest; otherwise `None`. |
| `.github/bible/bible_queue.py:495` | if | The report has a `Re-check of` row and a confirmed-count line | Follows the chain of earlier reports. |
| `.github/bible/bible_queue.py:499` | conditional expression | `fetch` is given, the name looks like a report file, and `depth` is below 20 | Fetches the earlier report; otherwise `None`. |
| `.github/bible/bible_queue.py:500` | conditional expression | An earlier report text was fetched | Parses it with a recursive call; otherwise `None`. |
| `.github/bible/bible_queue.py:501` | conditional expression | The earlier facts exist and are not `UNREADABLE` | Uses their accuracy (`older_facts[4]`); otherwise `None`. |
| `.github/bible/bible_queue.py:502` | conditional expression | The earlier accuracy is missing; otherwise this report's accuracy is missing | A missing earlier accuracy makes the result `None`; a missing own accuracy takes the earlier one; otherwise the minimum of the two. |
| `.github/bible/bible_queue.py:506` | conditional expression | The fingerprint row matched | Returns its 16 hex characters; otherwise `None`. |
| `.github/bible/bible_queue.py:507` | conditional expression | The confirmed-count line matched | Returns `(X, Y)` as integers; otherwise `None`; the last value is `bool(base or noted)`. |

**Output and side effects**: returns the tuple; reads no file itself (the earlier report comes through `fetch`) and writes nothing (`.github/bible/bible_queue.py:478-507`).

**Notes**: The docstring lists five values (`.github/bible/bible_queue.py:479-480`) while the function returns six (`.github/bible/bible_queue.py:506-507`); the sixth is read by `accepted` (`.github/bible/bible_queue.py:532`). The docstring says the rules are status.py's (inferred: per `.github/bible/bible_queue.py:479-480`); the page does not compare them with that script.

### `recheck_due(facts)`

Source: `.github/bible/bible_queue.py:516-520` <!-- code: 39469d1fcf8a -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:907`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1125`) |
| Calls | `bool`, `len` |
| Purpose | Says whether the next verification is the re-check of a `PASS AFTER CORRECTIONS` rather than a new full round. |

**Inputs**

| Name | Type | Meaning | Checked how |
| --- | --- | --- | --- |
| `facts` | tuple or `None` | The result of `report_facts` | Truthiness, length greater than 4 and a non-`None` accuracy are tested (`.github/bible/bible_queue.py:519-520`). |

**Steps**

1. Returns `bool(...)` of a conjunction: `facts` is truthy, `facts[0]` equals `PASS AFTER CORRECTIONS`, `len(facts) > 4`, `facts[4]` is not `None`, and `facts[4] >= RECHECK_MIN_ACCURACY` (95.0) (`.github/bible/bible_queue.py:519-520`, `.github/bible/bible_queue.py:473`).

**Pseudo-code**

```text
return facts and verdict == "PASS AFTER CORRECTIONS" and accuracy is not None and accuracy >= 95.0
```

**Output and side effects**: returns a bool; no side effects. The comment on the last condition says that below a PASS's accuracy the next round is a full one (inferred: per `.github/bible/bible_queue.py:520`). The function reads only `facts`: it does not test whether a revision has followed the report (`.github/bible/bible_queue.py:516-520`).

### `accepted(facts)`

Source: `.github/bible/bible_queue.py:523-542` <!-- code: ec72133acd61 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.component` (`.github/bible/bible_queue.py:867`, `.github/bible/bible_queue.py:877`), `Queue.assemble_phase` (`.github/bible/bible_queue.py:1053`, `.github/bible/bible_queue.py:1092`) |
| Calls | `len`, `bool` |
| Purpose | Says whether a report counts as verified: the queue's copy of the rule that `status.py` applies, apart from the fingerprint (inferred: per `.github/bible/bible_queue.py:524-527`, the docstring). |

**Inputs**

| Name | Type | Meaning | Checked how |
| --- | --- | --- | --- |
| `facts` | tuple or `None` | The result of `report_facts` | Falsey, or a verdict other than `PASS` or `PASS AFTER CORRECTIONS`, is refused (`.github/bible/bible_queue.py:528-529`). |

**Steps**

1. Returns `False` when `facts` is falsey or `facts[0]` is neither `PASS` nor `PASS AFTER CORRECTIONS`; so `FAIL` and `UNREADABLE` are never accepted (`.github/bible/bible_queue.py:528-529`).
2. Reads `verdict`, `majors`, the re-check pair (`facts[3]` when the tuple is longer than 3, else `None`) and `is_recheck` (`facts[5]` when the tuple is longer than 5) (`.github/bible/bible_queue.py:530-532`).
3. Returns `False` when there are major corrections and no re-check with X equal to Y (`.github/bible/bible_queue.py:533-534`).
4. When a re-check pair exists with Y equal to 0 or X below Y, returns `False` unless the verdict is `PASS`, there are no major corrections, Y is not 0 and the report is not itself a re-check (`.github/bible/bible_queue.py:535-537`).
5. Returns `False` for `PASS AFTER CORRECTIONS` without a re-check pair (`.github/bible/bible_queue.py:538-539`).
6. Returns `False` when a re-check pair exists and the tuple has no accuracy, or the accuracy is below 95.0 (`.github/bible/bible_queue.py:540-541`).
7. Otherwise returns `True` (`.github/bible/bible_queue.py:542`). A plain `PASS` with no re-check line and no major correction is therefore accepted whatever its accuracy (`.github/bible/bible_queue.py:528-542`).

**Pseudo-code**

```text
if facts is falsey or verdict not in (PASS, PASS AFTER CORRECTIONS): return False
if majors and not (re-check and X == Y): return False
if re-check and (Y == 0 or X < Y):
    if verdict != PASS or majors or Y == 0 or report is itself a re-check: return False
if verdict == PASS AFTER CORRECTIONS and no re-check: return False
if re-check and (no accuracy or accuracy < 95.0): return False
return True
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:528` | if | `facts` is falsey, or the verdict is not `PASS` or `PASS AFTER CORRECTIONS` | Returns `False`. |
| `.github/bible/bible_queue.py:531` | conditional expression | `facts` has more than 3 values | Takes `facts[3]` as the re-check pair; otherwise `None`. |
| `.github/bible/bible_queue.py:533` | if | Major corrections exist and there is no re-check with X equal to Y | Returns `False`. |
| `.github/bible/bible_queue.py:535` | if | A re-check pair exists with Y equal to 0 or X below Y | Applies the narrower test on the next line. |
| `.github/bible/bible_queue.py:536` | if | The verdict is not `PASS`, or majors exist, or Y is 0, or the report is itself a re-check | Returns `False`. |
| `.github/bible/bible_queue.py:538` | if | The verdict is `PASS AFTER CORRECTIONS` and there is no re-check pair | Returns `False`. |
| `.github/bible/bible_queue.py:540` | if | A re-check pair exists and the accuracy is missing or below 95.0 | Returns `False`. |

**Output and side effects**: returns a bool; no side effects (`.github/bible/bible_queue.py:523-542`).

### `as_int(value)`

Source: `.github/bible/bible_queue.py:545-549` <!-- code: bc184bba1eba -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `GitHub.pr_files` (`.github/bible/bible_queue.py:269`, `.github/bible/bible_queue.py:278`), `Queue.run` (`.github/bible/bible_queue.py:746`), `Queue.component` (`.github/bible/bible_queue.py:847`), `Queue.follow` (`.github/bible/bible_queue.py:948`, `.github/bible/bible_queue.py:950`), `Queue.could_not_check` (`.github/bible/bible_queue.py:1000`) |
| Calls | `int` |
| Purpose | Converts a value to an integer, returning zero for conversion type, value or overflow errors. |

**Steps**

1. Returns `int(value)` when conversion succeeds; catches `TypeError`, `ValueError` or `OverflowError` and returns `0`. (`.github/bible/bible_queue.py:546-549`)

**Pseudo-code**

```text
try: return int(value)
on TypeError, ValueError or OverflowError: return 0
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:548` | except | `int(value)` raises `TypeError`, `ValueError` or `OverflowError` | Returns zero. |

### `status_of(gh, path, ref)`

Source: `.github/bible/bible_queue.py:552-555` <!-- code: ad9adb38e0f7 -->

| | |
| --- | --- |
| Kind | module function |
| Called by | `Queue.session` (`.github/bible/bible_queue.py:590`), `Queue.component` (`.github/bible/bible_queue.py:830`), `Queue.follow` (`.github/bible/bible_queue.py:941`, `.github/bible/bible_queue.py:948`) |
| Calls | `json_file`, `isinstance` |
| Purpose | Returns parsed component status only when the loaded JSON is a dictionary. |

**Steps**

1. Loads `path` at `ref` with `json_file`. (`.github/bible/bible_queue.py:554`)
2. Returns the loaded data if it is a dictionary; otherwise returns `{}`. (`.github/bible/bible_queue.py:555`)

**Pseudo-code**

```text
data = json_file(gh, path, ref)
return data if data is a dict, otherwise {}
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `.github/bible/bible_queue.py:555` | conditional expression | `data` is a dictionary | Returns `data`; otherwise returns `{}`. |

## Module-level code

The module imports Python standard-library utilities and initializes queue labels, environment-derived agent settings, regexes, and timing/verification constants. (`.github/bible/bible_queue.py:42-106`, `.github/bible/bible_queue.py:391`, `.github/bible/bible_queue.py:471-475`). The tuple `WORK_EVENTS` lists the timeline events that count as Copilot's work: `copilot_work_started`, `copilot_work_finished` and `copilot_work_finished_failure` (`.github/bible/bible_queue.py:70`).

It declares the `GitHub` API client (`.github/bible/bible_queue.py:111-375`), helper functions (`.github/bible/bible_queue.py:380-555`), and `Queue` coordinator (`.github/bible/bible_queue.py:560-1381`). The CLI `main` parses arguments, and the module guard calls it when executed as a script. (`.github/bible/bible_queue.py:1384-1434`)

## Surprises

`tarball` limits download/member sizes, filters archive members to regular files and directories, and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:296-331`)

The `Queue.session` docstring lists four result states, but the code also returns `start-error` when `GitHub.start_error` is truthy. (`.github/bible/bible_queue.py:578`, `.github/bible/bible_queue.py:581-582`)

`GitHub.pr_files` does not trust the file list GitHub gives for an open pull request whose base branch has moved: it compares the head with the base branch's tip (`/compare/<tip>...<head>`) and refuses a comparison with no list, or with `COMPARE_MAX` (300) files or more. (`.github/bible/bible_queue.py:259-274`, `.github/bible/bible_queue.py:71`)

The docstring of `report_facts` lists five returned values, while the function returns six; `accepted` reads the sixth, the flag that the report is itself a re-check. (`.github/bible/bible_queue.py:479-480`, `.github/bible/bible_queue.py:506-507`, `.github/bible/bible_queue.py:532`)

The pull request text that `Queue.component` writes says `verified (PASS, pages fingerprint <fp>)` also when the accepted verdict was `PASS AFTER CORRECTIONS`. (`.github/bible/bible_queue.py:867-870`)

`Queue.replay_closed_runs` does not look at the age of a closed tracker: any closed tracker from an earlier run that has no `bible-replayed` label is read at the next check, and when it holds recorded paths they are passed to `delta`, then the tracker is labelled. (`.github/bible/bible_queue.py:685-695`)

<!-- cites .github/bible/bible_queue.py@a625b4c3353b1744b965b8bbee13e6b3ed5f72a6 -->
