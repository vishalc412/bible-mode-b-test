---
id: lld/bible-mode-b/README
kind: component
component: bible-mode-b
source: [.github/bible/bible_queue.py, .github/workflows/bible-plan.yml, .github/workflows/bible-queue.yml, .github/workflows/bible-delta.yml, .github/workflows/poc-assign-copilot.yml]
summary: Coordinates Mode B codebase-analysis runs and their GitHub issue and pull-request lifecycle
reads: [file:changed-path-list, config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
writes: [file:temporary-gate-workspace]
calls: [external:GitHub, external:Analysis toolkit]
uses: [symbol:GitHub, symbol:Queue]
config: [config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
exposes: []
---

# bible-mode-b

| | |
| --- | --- |
| Kind | CLI and GitHub Actions workflow component |
| Folders and files | `.github/bible/bible_queue.py`; workflow adapters in `.github/workflows/bible-plan.yml`, `.github/workflows/bible-queue.yml`, and `.github/workflows/bible-delta.yml`; independent `.github/workflows/poc-assign-copilot.yml` |
| Technology | Python 3 standard library; GitHub Actions YAML |
| Starts by | Manual `bible-plan` workflow starts a run; `bible-queue` reconciles on a 15-minute schedule or manual dispatch; `bible-delta` handles default-branch pushes except those that change only `codebase-analysis/**` and `.github/skills/**`; code under `.github/workflows/` and `.github/bible/` is not ignored (assumed: GitHub's `paths-ignore` filter). (`.github/workflows/bible-plan.yml:7-8`, `.github/workflows/bible-queue.yml:7-10`, `.github/workflows/bible-delta.yml:6-12`, `.github/workflows/bible-delta.yml:19`) |
| Size | 1 Python source file, 1434 lines, 78 functions/methods (one more, `last_activity`, is nested in `Queue.delta`), 2 classes, 0 routes. (`.github/bible/bible_queue.py:1-1434`, `.github/bible/bible_queue.py:1324-1326`; component coverage: `ledger/components/bible-mode-b/coverage-report.md`) |
| Depth | Deep |

## Responsibility

This component coordinates the Mode B analysis workflow through a `start`, `reconcile`, or `delta` CLI command. `Queue` reads tracker and session state from GitHub, assigns work, handles retries and human holds, checks component completion, and opens review pull requests; `GitHub` wraps the REST and GraphQL operations. (`.github/bible/bible_queue.py:1386-1397`, `.github/bible/bible_queue.py:560-1381`, `.github/bible/bible_queue.py:111-375`). `reconcile` also replays, for closed trackers, the code changes that were recorded while a run was open (`.github/bible/bible_queue.py:676-679`, `.github/bible/bible_queue.py:681-697`).

The `bible-plan.yml` workflow starts a run from a manual dispatch, `bible-queue.yml` invokes reconciliation on demand or every 15 minutes, and `bible-delta.yml` writes changed paths to a file and starts delta processing after a default-branch push. (`.github/workflows/bible-plan.yml:7-8`, `.github/workflows/bible-plan.yml:50-54`, `.github/workflows/bible-queue.yml:7-10`, `.github/workflows/bible-queue.yml:34-37`, `.github/workflows/bible-delta.yml:6-10`, `.github/workflows/bible-delta.yml:19`, `.github/workflows/bible-delta.yml:31-38`)

`poc-assign-copilot.yml` independently creates an issue and assigns Copilot through its inline `gh api` command; it does not invoke the queue or check out repository code. Its required `task` input defaults to an instruction to create `docs/poc-hello.md` with one line, and the input becomes the issue body passed to Copilot. (`.github/workflows/poc-assign-copilot.yml:18-21`, `.github/workflows/poc-assign-copilot.yml:38-72`, `.github/workflows/poc-assign-copilot.yml:55-69`)

No other analysis component calls into this component or is called by it (inferred: repository search for `bible_queue|\.github/bible/` in `*.py` and `*.yml` returned seven references, including the toolkit's mirrored revision rule). The queue's `delta` method does call the analysis toolkit's `components` helpers, which are outside the component catalog. (`.github/bible/bible_queue.py:1345-1347`, `.github/bible/bible_queue.py:1350-1351`, `.github/bible/bible_queue.py:1365`)

## Structure

The diagram shows the three workflow entry paths and their shared queue/client path to GitHub, and the POC workflow's own `gh api` call; component internals are omitted.

```mermaid
flowchart TB
  planworkflow["bible-plan.yml"]
  queueworkflow["bible-queue.yml"]
  deltaworkflow["bible-delta.yml"]
  pocworkflow["poc-assign-copilot.yml"]
  changedfile[("changed-path file")]
  main["main<br/>CLI dispatcher"]
  queue["Queue<br/>run lifecycle"]
  client["GitHub<br/>REST and GraphQL client"]
  scripts["coverage.py and status.py<br/>toolkit scripts"]
  helpers["components module<br/>toolkit helpers"]
  api{{"GitHub API<br/>external"}}
  planworkflow -->|"start command"| main
  queueworkflow -->|"reconcile command"| main
  deltaworkflow -->|"delta command"| main
  deltaworkflow -->|"writes changed paths"| changedfile
  changedfile -->|"--changed-file input"| main
  main -->|"constructs and dispatches"| queue
  main -->|"constructs client"| client
  queue -->|"repository operations"| client
  queue -->|"python -I subprocess in check and whole_fingerprint"| scripts
  queue -->|"import in delta"| helpers
  client -->|"REST or GraphQL at configured API URL"| api
  pocworkflow -->|"gh api creates and assigns an issue"| api
```

| Element | Evidence |
| --- | --- |
| `bible-plan.yml` -> `main` | `.github/workflows/bible-plan.yml:50-54` |
| `bible-queue.yml` -> `main` | `.github/workflows/bible-queue.yml:34-37` |
| `bible-delta.yml` -> `main` and changed-path file | `.github/workflows/bible-delta.yml:31-38` |
| `main` -> `Queue`, `GitHub` | `.github/bible/bible_queue.py:1403-1404` |
| `Queue` -> `GitHub` | `.github/bible/bible_queue.py:561-563` |
| `Queue.check` -> toolkit scripts | `.github/bible/bible_queue.py:972-973`, `.github/bible/bible_queue.py:983-990` |
| `Queue.whole_fingerprint` -> `status.py --fingerprint` | `.github/bible/bible_queue.py:1012-1019` |
| `Queue.delta` -> toolkit `components` helpers | `.github/bible/bible_queue.py:1345-1346` |
| `GitHub` -> GitHub API | `.github/bible/bible_queue.py:114-126`, `.github/bible/bible_queue.py:358-361` |
| `poc-assign-copilot.yml` -> GitHub API (it starts no queue code) | `.github/workflows/poc-assign-copilot.yml:66-69` |

## Reconcile sequence

This sequence shows a tracker reconciliation and a failed session; other component branches and gate details are omitted.

```mermaid
sequenceDiagram
  autonumber
  participant Workflow as bible-queue.yml
  participant Queue
  participant GitHub
  participant API as GitHub API
  Workflow->>Queue: reconcile via main
  Queue->>GitHub: default_branch and issues
  GitHub->>API: repository and issue requests
  API-->>GitHub: tracker data
  GitHub-->>Queue: trackers
  Queue->>Queue: run and component
  Queue->>GitHub: linked_prs and session data
  GitHub->>API: timeline and PR requests
  API-->>GitHub: session data
  GitHub-->>Queue: session data
  alt no PR after assignment timeout
    Queue->>Queue: fail_or_retry
    Queue->>GitHub: close and retry, or label and unassign
    GitHub->>API: issue and PR updates
  else session running or finished
    Queue->>Queue: follow session state
  end
```

| Steps | Evidence |
| --- | --- |
| Workflow invokes reconcile | `.github/workflows/bible-queue.yml:34-37`, `.github/bible/bible_queue.py:1394`, `.github/bible/bible_queue.py:1423-1424` |
| Trackers fetched and processed | `.github/bible/bible_queue.py:152-154`, `.github/bible/bible_queue.py:182-183`, `.github/bible/bible_queue.py:664-675`, `.github/bible/bible_queue.py:705-715` |
| Session and API data | `.github/bible/bible_queue.py:205-217`, `.github/bible/bible_queue.py:565-593`, `.github/bible/bible_queue.py:799-807`, `.github/bible/bible_queue.py:914-924` |
| Failure retry or hold | `.github/bible/bible_queue.py:642-661`, `.github/bible/bible_queue.py:920-922` |

## Session classification

Each invocation of `Queue.session` classifies the current observation independently; the diagram does not assert persistent transitions between returned states.

```mermaid
stateDiagram-v2
  [*] --> Checking
  Checking --> waiting : no PR and within timeout
  Checking --> no_start : no PR after timeout
  Checking --> start_error : start error without PR
  Checking --> running : PR still working
  Checking --> finished : PR work finished
  waiting --> [*]
  no_start --> [*]
  start_error --> [*]
  running --> [*]
  finished --> [*]
```

| Element | Evidence |
| --- | --- |
| No PR: `waiting`, `no-start`, `start-error` | `.github/bible/bible_queue.py:579-583` |
| PR exists: `running`, `finished` (any work event of Copilot's app decides: only `copilot_work_started` as the newest gives `running`, so `copilot_work_finished_failure` gives `finished`; without work events, the head commit age and the PR's review state decide; for a chunk session, a `status.json` at the PR head whose state is in `FINAL_STATES` with review asked or the head idle for `IDLE_AFTER` gives `finished`, as does a head idle for three times `IDLE_AFTER`, and anything else gives `running`) | `.github/bible/bible_queue.py:584-593`, `.github/bible/bible_queue.py:73`, `.github/bible/bible_queue.py:75` |

The state IDs `no_start` and `start_error` represent the returned strings `no-start` and `start-error`. The diagrams were checked by reading, not rendered.

## Whole-analysis phase and deferred updates

When every wanted component's row is `merged`, `Queue.run` hands over to `Queue.assemble_phase` (`.github/bible/bible_queue.py:754-755`). It works through two issue kinds in order, the assembly (`bible-assemble`) and the whole verification (`bible-verify-all`), and the run ends only when both are done (inferred: a search of the queue for `close(tracker` finds 1 hit, at line 1137, in the Done step).

```mermaid
flowchart TB
  start(["all components merged"])
  assemble["assembly issue<br/>Copilot writes the whole-system pages"]
  contassemble["@copilot continue comment on the assembly pull request<br/>at most 3 times"]
  contverify["@copilot continue comment on the verification pull request<br/>at most 3 times"]
  contrevise["@copilot continue comment on the revision pull request<br/>at most 3 times"]
  verify["verify-all issue<br/>second model writes verification-report.md"]
  verdict["report read after merge"]
  revise["revise-all issue<br/>apply every correction, then verify again"]
  hold["hold issue for a person<br/>after 2 whole verifications without an accepted report"]
  done(["update issues for recorded paths, post Done, close tracker, late paths"])
  start -->|"queue creates the assembly issue"| assemble
  assemble -->|"status.json not yet written"| contassemble
  contassemble -->|"Copilot continues on the same pull request"| assemble
  verify -->|"verification-report.md not yet written"| contverify
  contverify -->|"Copilot continues on the same pull request"| verify
  revise -->|"status.json not yet written"| contrevise
  contrevise -->|"Copilot continues on the same pull request"| revise
  assemble -->|"merged by a person"| verify
  verify -->|"merged by a person"| verdict
  verdict -->|"accepted report (PASS, or PASS AFTER CORRECTIONS with a confirmed re-check), this run's PR, fingerprint equals the pages now"| done
  verdict -->|"corrections asked"| revise
  revise -->|"merged by a person"| verify
  verdict -->|"accepted report about other pages, or not by this run: labelled bible-stale-verdict, no revision"| verify
  verdict -->|"two verifications without an accepted, current report"| hold
```

| Step | What happens | Evidence |
| --- | --- | --- |
| Assembly session | The assembly issue is created from `ledger/issues/assemble.md`. When its session has finished but the pull request does not contain `status.json`, `continue_if_unfinished` comments `@copilot continue ...` (marked with `CONTINUE_MARK`), at most 3 times since a person last released the issue; a session that failed before starting any work is held for a person at once. The same continuation applies to the verify-all session (end marker `verification-report.md`) and to the revise-all session (end marker `status.json`). | `.github/bible/bible_queue.py:1119-1130`, `.github/bible/bible_queue.py:1114-1118`, `.github/bible/bible_queue.py:1252-1305`, `.github/bible/bible_queue.py:1215-1218`, `.github/bible/bible_queue.py:1260-1262` |
| Whole verification | The verify-all issue is created on `verify_model`. A person merges the pull request (inferred: the module docstring at line 28, and `merge` is called only at line 965, for session pull requests into the component branch); the queue then reads `verification-report.md` on the default branch. When the report now on the default branch is a `PASS AFTER CORRECTIONS` with an accuracy of at least 95, the new verification issue ends with `RECHECK_ASK`, the instruction to re-check what the last report flagged and what the revision changed instead of drawing a new sample. | `.github/bible/bible_queue.py:1029-1031`, `.github/bible/bible_queue.py:1119-1130`, `.github/bible/bible_queue.py:1083-1103`, `.github/bible/bible_queue.py:510-520` |
| Corrections asked | A missing, unreadable or not accepted report (`accepted` refuses `FAIL`, a major correction without a fully confirmed re-check, and a `PASS AFTER CORRECTIONS` without a re-check) labels the issue `bible-needs-revision`; an issue the queue sees still open is also closed as not planned, while one GitHub already closed as completed is only labelled and commented. At the next check `revise_all_step` creates a `bible-revise-all` issue (apply every correction without editing the report, finish with `status.py --write`). Its pull request may change only files under the analysis folder and never `verification-*` files. After a person merges it (inferred: the module docstring at line 28, and `merge` is called only at line 965, for session pull requests into the component branch) the next whole verification is created. | `.github/bible/bible_queue.py:1088-1099`, `.github/bible/bible_queue.py:523-542`, `.github/bible/bible_queue.py:1072-1076`, `.github/bible/bible_queue.py:1172-1250`, `.github/bible/bible_queue.py:1219-1224` |
| Stale or foreign `PASS` | An accepted report whose fingerprint does not equal the pages now, or whose report was not written by this run's own merged pull request, is labelled `bible-stale-verdict` and verified again. If too little of the run's time is left the check just waits for the next run; if the fingerprint cannot be computed (no `status.py`, a failed or oversized download, a timeout or no output) it is counted, and after 3 such checks in a row a person is asked. | `.github/bible/bible_queue.py:1037-1071`, `.github/bible/bible_queue.py:1055-1062`, `.github/bible/bible_queue.py:1010-1023`, `.github/bible/bible_queue.py:997-1008` |
| Round limit | `rounds` counts the whole verifications that asked for corrections or were stale since a person last released the run; at 2 the queue creates the hold issue of the whole analysis. Removing `bible-needs-human` from it starts new rounds. | `.github/bible/bible_queue.py:1187-1195`, `.github/bible/bible_queue.py:1234-1240`, `.github/bible/bible_queue.py:1164-1170`, `.github/bible/bible_queue.py:76` |
| End of the run | At the Done step the queue reads the paths recorded while the run was open and creates their update issues; then it comments that every component, the assembly and the whole verification are merged, closes the tracker, and reads the recorded paths once more for any that arrived after the first read. When the late step did not fail, it comments `Recorded code changes: <n>, in update issues.` with the hidden mark `REPLAYED_MARK` and labels the tracker `bible-replayed`. A tracker that a person closes, a run that never reaches Done, and a Done step whose late replay failed leave no mark and no label; at every check `Queue.replay_closed_runs` lists the closed trackers without `bible-replayed`, reads their recorded paths (`deferred_updates`), calls `delta` for them (which records them on a run that is open now, or creates the update issues), comments with the mark and adds the label; a tracker it cannot process is tried again at the next check. The replay goes through `delta`: with no `components.json` or no `ledger/baseline.json` on the default branch the recorded paths are dropped with only a log line, more than 10 touched components give one hold issue, unless such a hold issue (`bible-delta`, `bible-needs-human`) is already open, and a component that already has an open `bible-delta` issue is skipped. | `.github/bible/bible_queue.py:676-679`, `.github/bible/bible_queue.py:681-697`, `.github/bible/bible_queue.py:1131-1137`, `.github/bible/bible_queue.py:1138-1148`, `.github/bible/bible_queue.py:1371-1375`, `.github/bible/bible_queue.py:1341-1344`, `.github/bible/bible_queue.py:1353-1362`, `.github/bible/bible_queue.py:1368-1370` |

`Queue.delta` (the `delta` command after a push to the default branch) behaves differently while a run is open: it records the changed plain paths in comments of at most 200 paths on the first tracker whose own `Updated` line (its creation time when it has none) is no older than 14 days, each with a hidden `bible-deferred-update` marker, and creates no issue. `Queue.deferred_updates` reads those comments (only the queue's own, only plain paths); it is called at the Done step of `assemble_phase` (lines 1133 and 1138) and by `replay_closed_runs` (line 690) (inferred: a search of the file for `deferred_updates(` finds 4 hits, the definition and these three calls). A closed tracker that does not carry `bible-replayed` is read by `replay_closed_runs` at every `reconcile`, so paths recorded on a tracker that a person closes, or on a run that never finishes, are replayed once into update issues, or recorded on a run that is open then (`.github/bible/bible_queue.py:664-679`, `.github/bible/bible_queue.py:681-697`). With no open run, `delta` maps the changed paths (not the analysis folder, not the skills folder) to components; more than 10 components give one hold issue. (`.github/bible/bible_queue.py:1324-1362`, `.github/bible/bible_queue.py:1150-1162`)

## Modules

| Module page | Source file | Lines | Role | Main functions |
| --- | --- | --- | --- | --- |
| [bible_queue](bible_queue.md) | `.github/bible/bible_queue.py` | 1-1434 | CLI entry point, queue coordinator, and GitHub API client | `main`, `Queue.reconcile`, `Queue.run`, `Queue.component`, `Queue.follow`, `Queue.check`, `Queue.delta`, `GitHub.call` |

The workflow files listed above are adapters that invoke the module, not additional Python source modules. (`.github/workflows/bible-plan.yml:50-54`, `.github/workflows/bible-queue.yml:34-37`, `.github/workflows/bible-delta.yml:31-38`)

## Main types

The class diagram focuses on each type's configuration/state and principal orchestration methods; incidental REST helpers are omitted.

```mermaid
classDiagram
  class GitHub {
    +String repo
    +String token
    +String api
    +Set known_labels
    +call(method, path, body, ok404)
    +paged(path)
    +file(path, ref)
    +tarball(ref, dest)
    +merge(pr, title)
  }
  class Queue {
    +GitHub gh
    +Function log
    +String skills
    +run(tracker, settings)
    +reconcile()
    +component(analysis, name)
    +follow(analysis, name, issue)
    +check(analysis, name, branch)
    +delta(changed, settings_analysis)
  }
  Queue --> GitHub : delegates GitHub operations
```

| Element | Evidence |
| --- | --- |
| `GitHub` fields and methods | `.github/bible/bible_queue.py:112-126`, `.github/bible/bible_queue.py:128-140`, `.github/bible/bible_queue.py:142-150`, `.github/bible/bible_queue.py:156-161`, `.github/bible/bible_queue.py:195-199`, `.github/bible/bible_queue.py:292-331`, `.github/bible/bible_queue.py:365-369` |
| `Queue` fields and methods | `.github/bible/bible_queue.py:561-563`, `.github/bible/bible_queue.py:664-703`, `.github/bible/bible_queue.py:705-756`, `.github/bible/bible_queue.py:796-909`, `.github/bible/bible_queue.py:911-968`, `.github/bible/bible_queue.py:970-995`, `.github/bible/bible_queue.py:1321-1381` |
| `Queue` -> `GitHub` | `.github/bible/bible_queue.py:561-563`, `.github/bible/bible_queue.py:666-667` |

The field types shown in the diagram are inferred from constructor assignments and use; the source does not declare annotations. (`.github/bible/bible_queue.py:112-115`, `.github/bible/bible_queue.py:561-563`)

## Public interface

| Interface | Kind | Card or page | Evidence |
| --- | --- | --- | --- |
| `start [--components ...] --verify-model ... [--model ...] [--concurrency ...] [--analysis ...] [--depth ...]` | CLI command | [main](bible_queue.md#main) | `.github/bible/bible_queue.py:1415-1420`, `.github/bible/bible_queue.py:1387-1400` |
| `reconcile` | CLI command | [main](bible_queue.md#main) | `.github/bible/bible_queue.py:1394`, `.github/bible/bible_queue.py:1423-1424` |
| `delta --changed-file FILE [--analysis ...]` | CLI command | [main](bible_queue.md#main) | `.github/bible/bible_queue.py:1395-1397`, `.github/bible/bible_queue.py:1425-1428` |
| Other analysis components | Cross-component call | None found | (inferred: repository search described under Responsibility) |

`start` requires a verification model different from the normal model and validates component names; it stops rather than opening a second run when a tracker is already open. (`.github/bible/bible_queue.py:1407-1414`)

## Business rules

| # | Rule, in plain words | Enforced in | Triggered by | Evidence |
| --- | --- | --- | --- | --- |
| R-01 | Verification must use a nonempty model different from the analysis model. | `main` | `start` command | `.github/bible/bible_queue.py:1407-1408` |
| R-02 | `start` checks each comma-separated entry of the component selection on its own: it must be `all` or match `NAME`. A list with an unknown name, or `all` mixed with names, passes `start` and is stopped later by `reconcile`, which renders "stopped: unknown component(s) ...". | `main`, `Queue.run` | `start` command, then the next reconcile | `.github/bible/bible_queue.py:1409-1411`, `.github/bible/bible_queue.py:728-735` |
| R-03 | A second tracker cannot be opened while a tracker issue is already open. | `main` | `start` command | `.github/bible/bible_queue.py:1413-1414` |
| R-04 | A failed session is retried once; a second failure is labeled `bible-needs-human` and unassigned. A session whose start Copilot refused (`start-error`) is held at once, with no retry. | `Queue.fail_or_retry`, `Queue.hold_start_error` | Failed agent session, or a refused start | `.github/bible/bible_queue.py:642-661`, `.github/bible/bible_queue.py:634-641`, `.github/bible/bible_queue.py:917-919` |
| R-05 | Chunk and verification sessions may write only their respective component paths; a disallowed file fails/retries the session. | `Queue.follow` | Agent PR file validation | `.github/bible/bible_queue.py:931-940` |
| R-06 | A component PR is created only for a report that `accepted` counts as verified (a `PASS`, or a `PASS AFTER CORRECTIONS` with a confirmed re-check, see R-19) and whose fingerprint is nonempty and equal to the fingerprint of the checked pages. | `Queue.component` | Successful component gate and verification | `.github/bible/bible_queue.py:867-871` |
| R-07 | After the maximum verification rounds without a report that is accepted and about these pages, a human hold is created. | `Queue.component` | Verification remains unsuccessful | `.github/bible/bible_queue.py:886-894` |
| R-08 | An assembly or whole-analysis session that ended before its end marker (`status.json`, or `verification-report.md` for the whole verification) is continued on the same pull request at most `MAX_CONTINUE` (3) times since a person last released it, then held for a person; a session whose Copilot work ended in `copilot_work_finished_failure` without any `copilot_work_started` after the queue's last request (or, before any request, after the time a person last released the hold) is held for a person at once. | `Queue.continue_if_unfinished` | Finished session whose pull request lacks the end marker | `.github/bible/bible_queue.py:1260-1262`, `.github/bible/bible_queue.py:1277-1286`, `.github/bible/bible_queue.py:1289-1295` |
| R-09 | A whole verification that is missing, unreadable or not accepted (see R-19) does not end the run and does not wait for a person: the issue gets `bible-needs-revision`, and a revision of the whole analysis (`bible-revise-all` issue, on the analysis model) is assigned, then verified again. | `Queue.assemble_phase`, `Queue.revise_all_step` | Merged whole-verification pull request with such a report | `.github/bible/bible_queue.py:1088-1099`, `.github/bible/bible_queue.py:1072-1076`, `.github/bible/bible_queue.py:1172-1250` |
| R-10 | After `MAX_VERIFY_ROUNDS` (2) whole verifications without an accepted, current report since a person last released the run, the queue creates a hold issue (`bible-hold`, `bible-whole`, `bible-needs-human`) for a person. | `Queue.revise_all_step`, `Queue.whole_hold` | Second whole verification that is not an accepted current report | `.github/bible/bible_queue.py:1187-1195`, `.github/bible/bible_queue.py:1234-1240`, `.github/bible/bible_queue.py:1164-1170` |
| R-11 | The run ends only on an accepted report (see R-19; inferred: a search of the queue for `close(tracker` finds 1 hit, at line 1137, in the Done step) whose printed fingerprint equals the whole analysis's fingerprint on the default branch now and whose report was written by a merged pull request of this run's own verification issue; any other accepted report is labelled `bible-stale-verdict` and verified again. | `Queue.assemble_phase` | Closed whole-verification issue | `.github/bible/bible_queue.py:1037-1071` |
| R-12 | While a tracker is open (its own `Updated` line, or its creation time when it has none, no older than 14 days), a push to the default branch creates no update issue: the changed paths that match `SAFE_FILE` (other names are counted in the comment, not recorded) are recorded in `bible-deferred-update` comments on the tracker. They are turned into update issues when the run ends through its Done step, before the tracker is closed and once more for paths recorded after the first read; if a person closes the tracker, or the run never finishes, `replay_closed_runs` turns them into update issues at a later check (see R-20), and a later update issue for the same component asks its session for every change since the analysis's baseline. | `Queue.delta`, `Queue.deferred_updates`, `Queue.assemble_phase`, `Queue.replay_closed_runs` | Default-branch push while a run is open | `.github/bible/bible_queue.py:390`, `.github/bible/bible_queue.py:1324-1326`, `.github/bible/bible_queue.py:1327-1340`, `.github/bible/bible_queue.py:1150-1162`, `.github/bible/bible_queue.py:1131-1148`, `.github/bible/bible_queue.py:667`, `.github/bible/bible_queue.py:1371-1375`, `.github/bible/bible_queue.py:681-697` |
| R-13 | A push that touches more than `MAX_DELTA_ISSUES` (10) components starts no update session; one hold issue is opened for a person instead, unless such a hold issue (`bible-delta`, `bible-needs-human`) is already open. | `Queue.delta` | Default-branch push with no open run | `.github/bible/bible_queue.py:1353-1362` |
| R-14 | The file list a session pull request is checked on is never read as complete unless it is: for an open pull request whose base branch moved, the queue lists the comparison with the base branch's tip and refuses a missing list, an empty list while the pull request's own `changed_files` count is nonzero, or one of `COMPARE_MAX` (300) files or more; otherwise the list must match the pull request's own `changed_files` count when that count is nonzero (a pull request that reports none, or a value that is not a number, is not count-checked). | `GitHub.pr_files` | Every file-scope check of a pull request | `.github/bible/bible_queue.py:253-287` |
| R-15 | A component with no passing check yet (its `status.json` state is not `COMPONENT_DONE`, or its check fails) gets chunk sessions until the closed chunk issues of this run that were created at or after the later of the last hold release and the latest merge of the component branch into the default branch reach a cap: the estimate (`est_sessions` from `components.json`, 2 when missing or zero, clamped to 1-10) gives a cap of 2 x estimate + 2, at least 4 (`MIN_SESSION_CAP`) and at most 22 (`MAX_SESSION_CAP`). At the cap the queue creates a hold issue (`bible-hold`, `bible-needs-human`) for a person instead of another chunk. | `Queue.component` | A component without a passing check, at each reconcile | `.github/bible/bible_queue.py:82-83`, `.github/bible/bible_queue.py:842-858` |
| R-16 | A check that could not run is counted, not failed: for a component's check a branch tarball whose download fails or that is over the size limits, or a timeout; for the fingerprint of the whole analysis the same, and also a missing `status.py` or no output. After `MAX_NOCHECK` (3) in a row the queue creates a hold issue for a person; a check that runs resets the count. When too little of the run's time is left the check just waits for the next run and is not counted. | `Queue.could_not_check` | Check of a component, or fingerprint of the whole analysis, that cannot run | `.github/bible/bible_queue.py:89`, `.github/bible/bible_queue.py:833-840`, `.github/bible/bible_queue.py:980-982`, `.github/bible/bible_queue.py:991-993`, `.github/bible/bible_queue.py:997-1008`, `.github/bible/bible_queue.py:1013-1023`, `.github/bible/bible_queue.py:1055-1063` |
| R-17 | A chunk session's pull request is merged only if it made progress: its `status.json` must show more `packets_done` than the component branch has, or `COMPONENT_DONE`, and must not be `STOP`; a revision chunk must also change a page of the component and end at `COMPONENT_DONE`. Otherwise the session fails and is retried or held. | `Queue.follow` | Finished chunk session | `.github/bible/bible_queue.py:948-961` |
| R-18 | A session pull request is merged by a squash merge that names the head commit that was checked, and the comment says GitHub then refuses the merge if anything was pushed since (assumed: GitHub's merge API checks the `sha` it is given, as the comment at `.github/bible/bible_queue.py:368` says). | `GitHub.merge` | Accepted session pull request | `.github/bible/bible_queue.py:365-369` |
| R-19 | A report counts as verified (`accepted`) only when its verdict is `PASS` or `PASS AFTER CORRECTIONS`; a major correction needs a re-check whose confirmed count equals its flagged count; a re-check with a short count (or a count of 0) is accepted only for a `PASS` that has no major correction and is not itself a re-check; a `PASS AFTER CORRECTIONS` needs a re-check; and any report that has a re-check needs an accuracy of at least `RECHECK_MIN_ACCURACY` (95.0) over its chain of rounds. The queue's copy of `status.py`'s rule, apart from the fingerprint (inferred: per the docstring, `.github/bible/bible_queue.py:524-527`). | `accepted`, `report_facts` | Every read of a verification report by `Queue.component` and `Queue.assemble_phase` | `.github/bible/bible_queue.py:471-475`, `.github/bible/bible_queue.py:478-507`, `.github/bible/bible_queue.py:523-542` |
| R-20 | A closed tracker that does not carry the label `bible-replayed` has its recorded code changes replayed once: unless the queue's own mark comment is already on it, `Queue.delta` is called with the recorded paths (it records them on a run that is open now, or creates update issues), the queue comments with `REPLAYED_MARK`, and the tracker gets `bible-replayed`; a failure leaves the label off and is tried again at the next check. | `Queue.replay_closed_runs`, `Queue.replayed`, `Queue.reconcile` | Every `reconcile` | `.github/bible/bible_queue.py:676-679`, `.github/bible/bible_queue.py:681-703` |
| R-21 | When the last report's verdict is `PASS AFTER CORRECTIONS` with an accuracy of at least 95.0, the next verification issue, component or whole, carries `RECHECK_ASK`: the verifier judges only what that report flagged and what the revision changed, without drawing a new sample. | `recheck_due`, `Queue.component`, `Queue.assemble_phase` | A verification issue created after such a report | `.github/bible/bible_queue.py:510-520`, `.github/bible/bible_queue.py:907`, `.github/bible/bible_queue.py:1125-1127` |

## Data

| Store or file | Reads | Writes | Data dictionary entry |
| --- | --- | --- | --- |
| GitHub issues and labels | Tracker settings, issue state, labels, assignments, comments, and timelines | Tracker, plan/chunk/verify/assemble/verify-all/revise-all/hold/delta issues, issue body rewrites and closes, labels, comments, and assignment changes | Not applicable; GitHub-managed objects (`.github/bible/bible_queue.py:343-347`, `.github/bible/bible_queue.py:1128`, `.github/bible/bible_queue.py:1248`, `.github/bible/bible_queue.py:152-174`, `.github/bible/bible_queue.py:205-206`, `.github/bible/bible_queue.py:224-228`, `.github/bible/bible_queue.py:237-251`, `.github/bible/bible_queue.py:333-353`) |
| GitHub branches and pull requests | Branch refs, PR metadata/files, commit time, linked PRs | Component branch refs and PR lifecycle changes | Not applicable; GitHub-managed objects (`.github/bible/bible_queue.py:182-203`, `.github/bible/bible_queue.py:208-222`, `.github/bible/bible_queue.py:253-290`, `.github/bible/bible_queue.py:355-375`) |
| GitHub contents and archive | JSON/status/report files and branch tarball | Tarball extraction under the temporary gate directory | Not applicable (`.github/bible/bible_queue.py:195-199`, `.github/bible/bible_queue.py:292-331`, `.github/bible/bible_queue.py:976-986`) |
| `--changed-file` input | One changed path per line; blank lines are discarded | None | Input contract documented by the delta workflow (`.github/workflows/bible-delta.yml:37-38`, `.github/bible/bible_queue.py:1426-1428`) |

## Outbound calls

| Target | Purpose | Protocol and scheme | Address from | Timeout, retry, fallback | Evidence |
| --- | --- | --- | --- | --- | --- |
| GitHub API | Issues, labels, branches, contents, pull requests, timelines, commits, archives, and ready-for-review mutation | REST and GraphQL; configured API URL defaults to HTTPS | `GITHUB_API_URL`, default `https://api.github.com` | Request timeout defaults to 60 seconds; tarball request uses 300 seconds. HTTP and URL/timeout/OS errors become `RuntimeError`, except `ready` wraps only HTTP errors; API helper supports optional 404 fallback. | `.github/bible/bible_queue.py:114-126`, `.github/bible/bible_queue.py:128-140`, `.github/bible/bible_queue.py:298`, `.github/bible/bible_queue.py:355-363` |
| GitHub Issues API, from the POC workflow | Creates an issue and assigns Copilot | REST through `gh api`; the scheme and port are `gh`'s own (assumed: library behaviour) | `REPO` and `gh`'s API base | The job is limited to 5 minutes; no retry (inferred: a search of the workflow for `retry` finds 0 hits); no timeout option on the `gh api` call (inferred: lines 66-69 pass none) | `.github/workflows/poc-assign-copilot.yml:37`, `.github/workflows/poc-assign-copilot.yml:66-69` |
| Analysis toolkit `components` helpers | Maps changed paths to component rows during delta processing | In-process Python import | `BIBLE_SKILLS` path, default `.github/skills` | No fallback is defined for import or helper errors in `Queue.delta` itself (inferred: `delta` has no `try`, `.github/bible/bible_queue.py:1321-1381`); the first replay at the Done step does not catch them either, so the tracker stays open and the next check tries again (`.github/bible/bible_queue.py:1133-1137`, `.github/bible/bible_queue.py:672-675`), while the late replay after the tracker closes catches them and comments on the tracker (`.github/bible/bible_queue.py:1139-1145`); the replay of closed trackers calls `delta` inside a `try` that logs the failure and tries again at the next check (`.github/bible/bible_queue.py:688-697`). | `.github/bible/bible_queue.py:561-563`, `.github/bible/bible_queue.py:1345-1347` |
| Analysis toolkit `coverage.py` and `status.py` | Check component coverage and obtain page fingerprint | Local subprocess, `python -I` | `BIBLE_SKILLS` path, default `.github/skills` | Each subprocess is run with a 300-second timeout (`GATE_TIMEOUT`, `.github/bible/bible_queue.py:78`); `subprocess.TimeoutExpired` is logged and the check counts as could not run (`.github/bible/bible_queue.py:991-993`). | `.github/bible/bible_queue.py:561-563`, `.github/bible/bible_queue.py:972-990` |

The API client adds a bearer authorization header only when a token is present (`.github/bible/bible_queue.py:122-123`). It does not log the token value (inferred: a search of `bible_queue.py` for `token` finds 11 hits, only in the constructor, the header, the `GH_TOKEN` check in `main` and comments, `.github/bible/bible_queue.py:112-113`, `.github/bible/bible_queue.py:122-123`, `.github/bible/bible_queue.py:1400-1403`, and no `print` or `self.log` call is given it).

## Configuration read

| Key | Purpose | Default | Source | Evidence |
| --- | --- | --- | --- | --- |
| `GITHUB_REPOSITORY` | Repository owner/name for API calls | Required; none | Environment | `.github/bible/bible_queue.py:1400-1402` |
| `GH_TOKEN` | GitHub API bearer token | Required; none | Environment; workflow supplies `BIBLE_ASSIGN_TOKEN` | `.github/bible/bible_queue.py:1400-1402`, `.github/workflows/bible-plan.yml:44-49`, `.github/workflows/bible-queue.yml:31-36`, `.github/workflows/bible-delta.yml:26-33` |
| `GITHUB_API_URL` | GitHub API base | `https://api.github.com` | Environment | `.github/bible/bible_queue.py:114` |
| `BIBLE_AGENT_LOGINS` | Agent logins recognized as authors/commenters | `Copilot,copilot-swe-agent[bot],copilot-swe-agent` | Environment | `.github/bible/bible_queue.py:61` |
| `BIBLE_AGENT_APP` | GitHub app slug identifying agent work events | `copilot-swe-agent` | Environment | `.github/bible/bible_queue.py:66` |
| `BIBLE_NOW` | Test clock override | Current timezone-aware UTC time when unset | Environment | `.github/bible/bible_queue.py:380-382` |
| `BIBLE_SKILLS` | Analysis toolkit path | `.github/skills` | Environment | `.github/bible/bible_queue.py:561-563` |
| `--components` | Components for a new run | `all` | CLI/workflow input | `.github/bible/bible_queue.py:1388`, `.github/workflows/bible-plan.yml:9-13` |
| `--model` | Analysis session model | Empty string | CLI/workflow input | `.github/bible/bible_queue.py:1389`, `.github/workflows/bible-plan.yml:14-17` |
| `--verify-model` | Separate verification model | Required | CLI/workflow input | `.github/bible/bible_queue.py:1390`, `.github/workflows/bible-plan.yml:18-20` |
| `--concurrency` | Maximum active components; zero means no cap | `0` | CLI/workflow input | `.github/bible/bible_queue.py:1391`, `.github/workflows/bible-plan.yml:21-24`, `.github/bible/bible_queue.py:746-748` |
| `--analysis` | Analysis output folder | `codebase-analysis` | CLI input | `.github/bible/bible_queue.py:1392`, `.github/bible/bible_queue.py:1397` |
| `--depth` | Coverage depth | `deep` | CLI input | `.github/bible/bible_queue.py:1393`, `.github/bible/bible_queue.py:421-422` |

## Errors and resilience

`GitHub.call` returns `None` for an allowed 404, turns other HTTP errors and URL/timeout/OS errors into `RuntimeError`, and decodes empty responses as `{}`. `main` converts `RuntimeError` to `SystemExit`; `Queue.reconcile` catches exceptions per tracker, while `Queue.run` catches component errors individually and continues other selected components. (`.github/bible/bible_queue.py:128-140`, `.github/bible/bible_queue.py:1429-1430`, `.github/bible/bible_queue.py:672-675`, `.github/bible/bible_queue.py:740-745`)

Session failures retry once and then create a human hold (a start Copilot refused is held at once, with no retry); successful sessions are gated by allowed-file paths and state/fingerprint checks before their PR is merged or exposed for review. (`.github/bible/bible_queue.py:634-641`, `.github/bible/bible_queue.py:642-661`, `.github/bible/bible_queue.py:931-964`, `.github/bible/bible_queue.py:830-835`, `.github/bible/bible_queue.py:867-871`) A whole-analysis session (assembly, whole revision, whole verification) that ended before writing its end marker is not retried but continued, at most `MAX_CONTINUE` (3) times; when GitHub recorded `copilot_work_finished_failure` with no `copilot_work_started` after the queue's request, the queue holds the issue for a person at once instead of spending the remaining continuations. (`.github/bible/bible_queue.py:1260-1262`, `.github/bible/bible_queue.py:1277-1286`, `.github/bible/bible_queue.py:1289-1295`)

## Logging and monitoring

The queue logs missing/invalid tracker settings, per-tracker exceptions, component gate output, tracker state rows, the deferral of a push while a run is open, a push that finds no assembled analysis (no `components.json` or baseline) so that nothing is updated, a whole-analysis fingerprint that could not be computed, delta issue creation or duplicate detection, and the decision that more than 10 changed components need a person. (`.github/bible/bible_queue.py:670`, `.github/bible/bible_queue.py:675`, `.github/bible/bible_queue.py:974`, `.github/bible/bible_queue.py:981`, `.github/bible/bible_queue.py:986`, `.github/bible/bible_queue.py:992`, `.github/bible/bible_queue.py:1317-1318`, `.github/bible/bible_queue.py:1338-1339`, `.github/bible/bible_queue.py:1022`, `.github/bible/bible_queue.py:1343`, `.github/bible/bible_queue.py:1361`, `.github/bible/bible_queue.py:1369`, `.github/bible/bible_queue.py:1381`). A failed replay of the recorded updates of closed trackers is logged too, once for the whole replay and once per tracker (`.github/bible/bible_queue.py:678-679`, `.github/bible/bible_queue.py:696-697`).

## Tests

The repository search for `bible_queue` in test-named paths returned no matches (inferred: a search of the three `test_*.py` files for `bible_queue` finds 0 hits).

## Surprises

- `Queue.session`'s docstring omits the `start-error` state that the method returns. (`.github/bible/bible_queue.py:578`, `.github/bible/bible_queue.py:581-582`)
- `GitHub.prs` is unused (inferred: a search for `.prs(` in `.github/bible/bible_queue.py` finds 0 hits); the method is defined at `.github/bible/bible_queue.py:201-203`.
- The docstring of `report_facts` lists five returned values, while the function returns six; `accepted` reads the sixth. (`.github/bible/bible_queue.py:479-480`, `.github/bible/bible_queue.py:506-507`, `.github/bible/bible_queue.py:532`)
- The component pull request text says `verified (PASS, ...)` also when the accepted verdict was `PASS AFTER CORRECTIONS`. (`.github/bible/bible_queue.py:867-870`)
- The queue workflow checks out the default branch's scripts and unpacks the component branch as input data before running the coverage check. (`.github/workflows/bible-queue.yml:26-30`, `.github/bible/bible_queue.py:976-990`)

## For the whole-system pages

### Risks and surprises

- The queue workflow deliberately checks out its scripts from the default branch (inferred: the comment at `.github/workflows/bible-queue.yml:26-27`), while downloading branch tarballs as data for coverage, so branch content is not the code that performs the gate. (`.github/workflows/bible-queue.yml:26-30`, `.github/bible/bible_queue.py:976-990`)
- The `Queue.session` docstring omits the returned `start-error` state. (`.github/bible/bible_queue.py:578`, `.github/bible/bible_queue.py:581-582`)
- The docstring of `report_facts` lists five of the six values it returns. (`.github/bible/bible_queue.py:479-480`, `.github/bible/bible_queue.py:506-507`)

### Open questions

None found in this component.

### Glossary

| Term | Meaning | Evidence |
| --- | --- | --- |
| Tracker issue | Issue storing the settings and state for one analysis run. | `.github/bible/bible_queue.py:709-715`, `.github/bible/bible_queue.py:1415-1420` |
| Component branch | Branch named `bible/<component>` for component work. | `.github/bible/bible_queue.py:784-789` |
| Agent event | Timeline event whose GitHub app slug is `AGENT_APP` and whose name is in `WORK_EVENTS`: work started, work finished, or work finished with failure. | `.github/bible/bible_queue.py:70`, `.github/bible/bible_queue.py:224-228` |
| Pages fingerprint | Status output used to require verification to match the checked component pages. | `.github/bible/bible_queue.py:865-867`, `.github/bible/bible_queue.py:987-990` |
| Accepted report | A verification report that `accepted` counts as verified: a `PASS`, or a `PASS AFTER CORRECTIONS` with a confirmed re-check, by the rules of R-19. | `.github/bible/bible_queue.py:523-542` |
| Replayed tracker | A closed tracker labelled `bible-replayed`: its recorded code changes are in update issues or recorded on the run open at that time. | `.github/bible/bible_queue.py:94`, `.github/bible/bible_queue.py:681-697` |

<!-- cites .github/bible/bible_queue.py@a625b4c3353b1744b965b8bbee13e6b3ed5f72a6 -->

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->
