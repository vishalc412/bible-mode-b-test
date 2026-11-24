---
id: lld/bible-mode-b/README
kind: component
component: bible-mode-b
source: [.github/bible/bible_queue.py, .github/workflows/bible-plan.yml, .github/workflows/bible-queue.yml, .github/workflows/bible-delta.yml, .github/workflows/poc-assign-copilot.yml]
summary: Coordinates Mode B codebase-analysis runs and their GitHub issue and pull-request lifecycle
reads: [file:changed-path list, config:GITHUB_REPOSITORY, config:GH_TOKEN, config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP, config:BIBLE_NOW, config:BIBLE_SKILLS]
writes: [file:temporary tarball tree]
calls: [external:GitHub API, external:Analysis toolkit]
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
| Starts by | Manual `bible-plan` workflow starts a run; `bible-queue` reconciles on a 15-minute schedule or manual dispatch; `bible-delta` handles default-branch pushes outside the ignored paths. (`.github/workflows/bible-plan.yml:7-8`, `.github/workflows/bible-queue.yml:7-10`, `.github/workflows/bible-delta.yml:6-10`) |
| Size | 1 Python source file, 1310 lines, 74 functions/methods (one more, `last_activity`, is nested in `Queue.delta`), 2 classes, 0 routes. (`.github/bible/bible_queue.py:1-1310`, `.github/bible/bible_queue.py:1200-1202`; component coverage: `ledger/components/bible-mode-b/coverage-report.md`) |
| Depth | Deep |

## Responsibility

This component coordinates the Mode B analysis workflow through a `start`, `reconcile`, or `delta` CLI command. `Queue` reads tracker and session state from GitHub, assigns work, handles retries and human holds, checks component completion, and opens review pull requests; `GitHub` wraps the REST and GraphQL operations. (`.github/bible/bible_queue.py:9-11`, `.github/bible/bible_queue.py:477-1257`, `.github/bible/bible_queue.py:108-351`)

The `bible-plan.yml` workflow starts a run from a manual dispatch, `bible-queue.yml` invokes reconciliation on demand or every 15 minutes, and `bible-delta.yml` writes changed paths to a file and starts delta processing after a default-branch push. (`.github/workflows/bible-plan.yml:7-8`, `.github/workflows/bible-plan.yml:50-54`, `.github/workflows/bible-queue.yml:7-10`, `.github/workflows/bible-queue.yml:34-37`, `.github/workflows/bible-delta.yml:6-10`, `.github/workflows/bible-delta.yml:31-38`)

`poc-assign-copilot.yml` independently creates an issue and assigns Copilot through its inline `gh api` command; it does not invoke the queue or check out repository code. Its required `task` input defaults to an instruction to create `docs/poc-hello.md` with one line, and the input becomes the issue body passed to Copilot. (`.github/workflows/poc-assign-copilot.yml:18-21,31-37,55-69`)

No other analysis component calls into this component or is called by it (inferred: repository search for `bible_queue|\.github/bible/` in `*.py` and `*.yml` returned seven references, including the toolkit's mirrored revision rule). The queue's `delta` method does call the analysis toolkit's `components` helpers, which are outside the component catalog. (`.github/bible/bible_queue.py:1221-1223`, `.github/bible/bible_queue.py:1226-1227`, `.github/bible/bible_queue.py:1241`)

## Structure

The diagram shows the three workflow entry paths and their shared queue/client path to GitHub; component internals and unrelated workflow jobs are omitted.

```mermaid
flowchart TB
  planworkflow["bible-plan.yml"]
  queueworkflow["bible-queue.yml"]
  deltaworkflow["bible-delta.yml"]
  changedfile[("changed-path file")]
  main["main<br/>CLI dispatcher"]
  queue["Queue<br/>run lifecycle"]
  client["GitHub<br/>REST and GraphQL client"]
  scripts["coverage.py and status.py<br/>toolkit scripts"]
  api{{"GitHub API<br/>external"}}
  planworkflow -->|"start command"| main
  queueworkflow -->|"reconcile command"| main
  deltaworkflow -->|"delta command"| main
  deltaworkflow -->|"writes changed paths"| changedfile
  changedfile -->|"--changed-file input"| main
  main -->|"constructs and dispatches"| queue
  main -->|"constructs client"| client
  queue -->|"repository operations"| client
  queue -->|"python -I subprocess"| scripts
  client -->|"REST or GraphQL at configured API URL"| api
```

| Element | Evidence |
| --- | --- |
| `bible-plan.yml` -> `main` | `.github/workflows/bible-plan.yml:50-54` |
| `bible-queue.yml` -> `main` | `.github/workflows/bible-queue.yml:34-37` |
| `bible-delta.yml` -> `main` and changed-path file | `.github/workflows/bible-delta.yml:31-38` |
| `main` -> `Queue`, `GitHub` | `.github/bible/bible_queue.py:1279-1280` |
| `Queue` -> `GitHub` | `.github/bible/bible_queue.py:478-480` |
| `Queue.check` -> toolkit scripts | `.github/bible/bible_queue.py:859-860`, `.github/bible/bible_queue.py:870-877` |
| `GitHub` -> GitHub API | `.github/bible/bible_queue.py:111-123`, `.github/bible/bible_queue.py:334-337` |

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
| Workflow invokes reconcile | `.github/workflows/bible-queue.yml:34-37`, `.github/bible/bible_queue.py:1270`, `.github/bible/bible_queue.py:1299-1300` |
| Trackers fetched and processed | `.github/bible/bible_queue.py:149-151`, `.github/bible/bible_queue.py:179-180`, `.github/bible/bible_queue.py:581-592`, `.github/bible/bible_queue.py:594-604` |
| Session and API data | `.github/bible/bible_queue.py:202-214`, `.github/bible/bible_queue.py:482-510`, `.github/bible/bible_queue.py:688-696`, `.github/bible/bible_queue.py:801-811` |
| Failure retry or hold | `.github/bible/bible_queue.py:559-578`, `.github/bible/bible_queue.py:807-809` |

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
| No PR: `waiting`, `no-start`, `start-error` | `.github/bible/bible_queue.py:496-500` |
| PR exists: `running`, `finished` (any work event of Copilot's app decides: only `copilot_work_started` as the newest gives `running`, so `copilot_work_finished_failure` gives `finished`; without work events, the head commit age and the PR's review state decide) | `.github/bible/bible_queue.py:501-510` |

The state IDs `no_start` and `start_error` represent the returned strings `no-start` and `start-error`. The diagrams were checked by reading, not rendered.

## Modules

| Module page | Source file | Lines | Role | Main functions |
| --- | --- | --- | --- | --- |
| [bible_queue](bible_queue.md) | `.github/bible/bible_queue.py` | 1-1310 | CLI entry point, queue coordinator, and GitHub API client | `main`, `Queue.reconcile`, `Queue.run`, `Queue.component`, `Queue.follow`, `Queue.check`, `Queue.delta`, `GitHub.call` |

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
| `GitHub` fields and methods | `.github/bible/bible_queue.py:109-123`, `.github/bible/bible_queue.py:153-158`, `.github/bible/bible_queue.py:192-196`, `.github/bible/bible_queue.py:268-307`, `.github/bible/bible_queue.py:341-345` |
| `Queue` fields and methods | `.github/bible/bible_queue.py:478-480`, `.github/bible/bible_queue.py:581-592`, `.github/bible/bible_queue.py:594-645`, `.github/bible/bible_queue.py:685-796`, `.github/bible/bible_queue.py:798-855`, `.github/bible/bible_queue.py:857-882`, `.github/bible/bible_queue.py:1197-1257` |
| `Queue` -> `GitHub` | `.github/bible/bible_queue.py:478-480`, `.github/bible/bible_queue.py:583-584` |

The field types shown in the diagram are inferred from constructor assignments and use; the source does not declare annotations. (`.github/bible/bible_queue.py:109-112`, `.github/bible/bible_queue.py:478-480`)

## Public interface

| Interface | Kind | Card or page | Evidence |
| --- | --- | --- | --- |
| `start --components ... --verify-model ... [--model ...] [--concurrency ...] [--analysis ...] [--depth ...]` | CLI command | [main](bible_queue.md#main) | `.github/bible/bible_queue.py:1291-1296`, `.github/bible/bible_queue.py:1263-1276` |
| `reconcile` | CLI command | [main](bible_queue.md#main) | `.github/bible/bible_queue.py:1270`, `.github/bible/bible_queue.py:1299-1300` |
| `delta --changed-file FILE [--analysis ...]` | CLI command | [main](bible_queue.md#main) | `.github/bible/bible_queue.py:1271-1273`, `.github/bible/bible_queue.py:1301-1304` |
| Other analysis components | Cross-component call | None found | (inferred: repository search described under Responsibility) |

`start` requires a verification model different from the normal model and validates component names; it stops rather than opening a second run when a tracker is already open. (`.github/bible/bible_queue.py:1283-1290`)

## Business rules

| # | Rule, in plain words | Enforced in | Triggered by | Evidence |
| --- | --- | --- | --- | --- |
| R-01 | Verification must use a nonempty model different from the analysis model. | `main` | `start` command | `.github/bible/bible_queue.py:1283-1284` |
| R-02 | Component selection must be `all` or a comma-separated list of names matching `NAME`. | `main` | `start` command | `.github/bible/bible_queue.py:1285-1287` |
| R-03 | A second tracker cannot be opened while a tracker issue is already open. | `main` | `start` command | `.github/bible/bible_queue.py:1289-1290` |
| R-04 | A failed session is retried once; a second failure is labeled `bible-needs-human` and unassigned. | `Queue.fail_or_retry` | Failed agent session | `.github/bible/bible_queue.py:559-578` |
| R-05 | Chunk and verification sessions may write only their respective component paths; a disallowed file fails/retries the session. | `Queue.follow` | Agent PR file validation | `.github/bible/bible_queue.py:818-827` |
| R-06 | A component PR is created only for a PASS with no major corrections and a nonempty fingerprint matching the checked pages. | `Queue.component` | Successful component gate and verification | `.github/bible/bible_queue.py:755-759` |
| R-07 | After the maximum verification rounds without a clean matching PASS, a human hold is created. | `Queue.component` | Verification remains unsuccessful | `.github/bible/bible_queue.py:774-782` |
| R-08 | An assembly or whole-analysis session that ended before its end marker (`status.json`, or `verification-report.md` for the whole verification) is continued on the same pull request at most `MAX_CONTINUE` (3) times since a person last released it, then held for a person; a session whose Copilot work ended in `copilot_work_finished_failure` without any `copilot_work_started` after the queue's request is held for a person at once. | `Queue.continue_if_unfinished` | Finished session whose pull request lacks the end marker | `.github/bible/bible_queue.py:1139-1141`, `.github/bible/bible_queue.py:1153-1162`, `.github/bible/bible_queue.py:1165-1171` |

## Data

| Store or file | Reads | Writes | Data dictionary entry |
| --- | --- | --- | --- |
| GitHub issues and labels | Tracker settings, issue state, labels, assignments, comments, and timelines | Tracker, plan/chunk/verify/hold/delta issues, labels, comments, and assignment changes | Not applicable; GitHub-managed objects (`.github/bible/bible_queue.py:149-171`, `.github/bible/bible_queue.py:202-203`, `.github/bible/bible_queue.py:221-225`, `.github/bible/bible_queue.py:234-248`, `.github/bible/bible_queue.py:309-329`) |
| GitHub branches and pull requests | Branch refs, PR metadata/files, commit time, linked PRs | Component branch refs and PR lifecycle changes | Not applicable; GitHub-managed objects (`.github/bible/bible_queue.py:179-200`, `.github/bible/bible_queue.py:205-219`, `.github/bible/bible_queue.py:250-266`, `.github/bible/bible_queue.py:331-351`) |
| GitHub contents and archive | JSON/status/report files and branch tarball | Tarball extraction under the temporary gate directory | Not applicable (`.github/bible/bible_queue.py:192-196`, `.github/bible/bible_queue.py:268-307`, `.github/bible/bible_queue.py:863-873`) |
| `--changed-file` input | One changed path per line; blank lines are discarded | None | Input contract documented by the delta workflow (`.github/workflows/bible-delta.yml:37-38`, `.github/bible/bible_queue.py:1302-1304`) |

## Outbound calls

| Target | Purpose | Protocol and scheme | Address from | Timeout, retry, fallback | Evidence |
| --- | --- | --- | --- | --- | --- |
| GitHub API | Issues, labels, branches, contents, pull requests, timelines, commits, archives, and ready-for-review mutation | REST and GraphQL; configured API URL defaults to HTTPS | `GITHUB_API_URL`, default `https://api.github.com` | Request timeout defaults to 60 seconds; tarball request uses 300 seconds. HTTP and URL/timeout/OS errors become `RuntimeError`, except `ready` wraps only HTTP errors; API helper supports optional 404 fallback. | `.github/bible/bible_queue.py:111-123`, `.github/bible/bible_queue.py:125-137`, `.github/bible/bible_queue.py:274`, `.github/bible/bible_queue.py:331-339` |
| Analysis toolkit `components` helpers | Maps changed paths to component rows during delta processing | In-process Python import | `BIBLE_SKILLS` path, default `.github/skills` | No fallback is defined for import or helper errors in `Queue.delta`. | `.github/bible/bible_queue.py:478-480`, `.github/bible/bible_queue.py:1221-1223` |
| Analysis toolkit `coverage.py` and `status.py` | Check component coverage and obtain page fingerprint | Local subprocess, `python -I` | `BIBLE_SKILLS` path, default `.github/skills` | Each subprocess is run with a 300-second timeout (`GATE_TIMEOUT`, `.github/bible/bible_queue.py:76`); `subprocess.TimeoutExpired` is logged and the check counts as could not run (`.github/bible/bible_queue.py:878-880`). | `.github/bible/bible_queue.py:478-480`, `.github/bible/bible_queue.py:859-877` |

The API client does not log the token value; it adds a bearer authorization header only when a token is present. (`.github/bible/bible_queue.py:119-120`)

## Configuration read

| Key | Purpose | Default | Source | Evidence |
| --- | --- | --- | --- | --- |
| `GITHUB_REPOSITORY` | Repository owner/name for API calls | Required; none | Environment | `.github/bible/bible_queue.py:1276-1278` |
| `GH_TOKEN` | GitHub API bearer token | Required; none | Environment; workflow supplies `BIBLE_ASSIGN_TOKEN` | `.github/bible/bible_queue.py:1276-1278`, `.github/workflows/bible-plan.yml:44-49`, `.github/workflows/bible-queue.yml:31-36`, `.github/workflows/bible-delta.yml:26-33` |
| `GITHUB_API_URL` | GitHub API base | `https://api.github.com` | Environment | `.github/bible/bible_queue.py:111` |
| `BIBLE_AGENT_LOGINS` | Agent logins recognized as authors/commenters | `Copilot,copilot-swe-agent[bot],copilot-swe-agent` | Environment | `.github/bible/bible_queue.py:61` |
| `BIBLE_AGENT_APP` | GitHub app slug identifying agent work events | `copilot-swe-agent` | Environment | `.github/bible/bible_queue.py:65` |
| `BIBLE_NOW` | Test clock override | Current timezone-aware UTC time when unset | Environment | `.github/bible/bible_queue.py:356-358` |
| `BIBLE_SKILLS` | Analysis toolkit path | `.github/skills` | Environment | `.github/bible/bible_queue.py:478-480` |
| `--components` | Components for a new run | `all` | CLI/workflow input | `.github/bible/bible_queue.py:1264`, `.github/workflows/bible-plan.yml:9-13` |
| `--model` | Analysis session model | Empty string | CLI/workflow input | `.github/bible/bible_queue.py:1265`, `.github/workflows/bible-plan.yml:14-17` |
| `--verify-model` | Separate verification model | Required | CLI/workflow input | `.github/bible/bible_queue.py:1266`, `.github/workflows/bible-plan.yml:18-20` |
| `--concurrency` | Maximum active components; zero means no cap | `0` | CLI/workflow input | `.github/bible/bible_queue.py:1267`, `.github/workflows/bible-plan.yml:21-24`, `.github/bible/bible_queue.py:635-637` |
| `--analysis` | Analysis output folder | `codebase-analysis` | CLI input | `.github/bible/bible_queue.py:1268`, `.github/bible/bible_queue.py:1273` |
| `--depth` | Coverage depth | `deep` | CLI input | `.github/bible/bible_queue.py:1269`, `.github/bible/bible_queue.py:396-397` |

## Errors and resilience

`GitHub.call` returns `None` for an allowed 404, turns other HTTP errors and URL/timeout/OS errors into `RuntimeError`, and decodes empty responses as `{}`. `main` converts `RuntimeError` to `SystemExit`; `Queue.reconcile` catches exceptions per tracker, while `Queue.run` catches component errors individually and continues other selected components. (`.github/bible/bible_queue.py:125-137`, `.github/bible/bible_queue.py:1305-1306`, `.github/bible/bible_queue.py:589-592`, `.github/bible/bible_queue.py:629-634`)

Session failures retry once and then create a human hold; successful sessions are gated by allowed-file paths and state/fingerprint checks before their PR is merged or exposed for review. (`.github/bible/bible_queue.py:559-578`, `.github/bible/bible_queue.py:818-851`, `.github/bible/bible_queue.py:719-724`, `.github/bible/bible_queue.py:755-759`) A whole-analysis session (assembly, whole revision, whole verification) that ended before writing its end marker is not retried but continued, at most `MAX_CONTINUE` (3) times; when GitHub recorded `copilot_work_finished_failure` with no `copilot_work_started` after the queue's request, the queue holds the issue for a person at once instead of spending the remaining continuations. (`.github/bible/bible_queue.py:1139-1141`, `.github/bible/bible_queue.py:1153-1162`, `.github/bible/bible_queue.py:1165-1171`)

## Logging and monitoring

The queue logs missing/invalid tracker settings, per-tracker exceptions, component gate output, tracker state rows, and delta issue creation or duplicate detection. (`.github/bible/bible_queue.py:587`, `.github/bible/bible_queue.py:592`, `.github/bible/bible_queue.py:861`, `.github/bible/bible_queue.py:868`, `.github/bible/bible_queue.py:873`, `.github/bible/bible_queue.py:879`, `.github/bible/bible_queue.py:1193-1194`, `.github/bible/bible_queue.py:1214-1215`, `.github/bible/bible_queue.py:1219`, `.github/bible/bible_queue.py:1237`, `.github/bible/bible_queue.py:1245`, `.github/bible/bible_queue.py:1257`)

## Tests

The repository search for `bible_queue` in test-named paths returned no matches.

## Surprises

- `Queue.session`'s docstring omits the `start-error` state that the method returns. (`.github/bible/bible_queue.py:495`, `.github/bible/bible_queue.py:498-499`)
- The module docstring lists two default `BIBLE_AGENT_LOGINS`, whereas the code includes a third, `copilot-swe-agent`. (`.github/bible/bible_queue.py:36`, `.github/bible/bible_queue.py:61`)
- `GitHub.prs` is unused (inferred: search for `.prs(` in `.github/bible/bible_queue.py` returned no matches); the method is defined at `.github/bible/bible_queue.py:198-200`.
- The queue workflow checks out the default branch's scripts and unpacks the component branch as input data before running the coverage check. (`.github/workflows/bible-queue.yml:26-30`, `.github/bible/bible_queue.py:863-877`)

## For the whole-system pages

### Risks and surprises

- The queue workflow deliberately checks out its scripts from the default branch, while downloading branch tarballs as data for coverage, so branch content is not the code that performs the gate. (`.github/workflows/bible-queue.yml:26-30`, `.github/bible/bible_queue.py:863-877`)
- The `Queue.session` docstring omits the returned `start-error` state. (`.github/bible/bible_queue.py:495`, `.github/bible/bible_queue.py:498-499`)

### Open questions

None found in this component.

### Glossary

| Term | Meaning | Evidence |
| --- | --- | --- |
| Tracker issue | Issue storing the settings and state for one analysis run. | `.github/bible/bible_queue.py:598-604`, `.github/bible/bible_queue.py:1291-1296` |
| Component branch | Branch named `bible/<component>` for component work. | `.github/bible/bible_queue.py:673-678` |
| Agent event | Timeline event whose GitHub app slug is `AGENT_APP` and whose name is in `WORK_EVENTS`: work started, work finished, or work finished with failure. | `.github/bible/bible_queue.py:69`, `.github/bible/bible_queue.py:221-225` |
| Pages fingerprint | Status output used to require verification to match the checked component pages. | `.github/bible/bible_queue.py:754-755`, `.github/bible/bible_queue.py:874-877` |

<!-- cites .github/bible/bible_queue.py@161344dc7ddde551f4020972e6d61c782a86d480 -->

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->
