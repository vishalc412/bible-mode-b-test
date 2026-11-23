---
id: lld/bible-mode-b/bible_queue
kind: module
component: bible-mode-b
source: .github/bible/bible_queue.py
summary: Wraps GitHub REST and GraphQL operations used by the Mode B analysis workflow
reads: [config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP]
writes: [file:destination tree passed to GitHub.tarball]
calls: [external:GitHub API]
uses: [symbol:GitHub]
config: [config:GITHUB_API_URL, config:BIBLE_AGENT_LOGINS, config:BIBLE_AGENT_APP]
exposes: []
---

# bible_queue

Source file: `.github/bible/bible_queue.py`

| | |
| --- | --- |
| Component | `bible-mode-b` (its design page is `README.md` in this folder) |
| Lines | 844 |
| Role | Defines the GitHub API client used by the queue workflow. |
| Imports that matter | Python standard-library JSON, URL, base64, temporary-file, archive, and filesystem modules used by `GitHub`. |
| Module-level state | `COPILOT`, `AGENT_LOGINS`, `AGENT_APP`, `START_ERROR`, `FINAL_STATES`, `NO_PR_AFTER`, `IDLE_AFTER`, `MAX_VERIFY_ROUNDS`, `SETTINGS`, `ATTEMPT`, `NAME`, and `LABELS` are initialized at import; the client reads the three agent/API environment settings while those constants initialize. (`.github/bible/bible_queue.py:59-83`) |

## Summary

`GitHub` stores the repository, token, API base URL, and a lazily populated label cache. Its methods cover request construction and pagination, issue/label operations, branch and file access, pull-request and timeline queries, archive download, and pull-request lifecycle operations. Read the cards in the same order as the class: low-level request helpers first, then query and mutation wrappers. (`.github/bible/bible_queue.py:88-302`)

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

## Call graph

```mermaid
flowchart LR
  init["GitHub.__init__"]
  request["GitHub.request"]
  call["GitHub.call"]
  paged["GitHub.paged"]
  ensure["GitHub.ensure_label"]
  ensure_all["GitHub.ensure_labels"]
  create_issue["GitHub.create_issue"]
  timeline["GitHub.timeline"]
  linked["GitHub.linked_prs"]
  agent_events["GitHub.agent_events"]
  is_agent["GitHub.is_agent_pr"]
  start_error["GitHub.start_error"]
  assigned["GitHub.assigned_at"]
  tarball["GitHub.tarball"]
  label["GitHub.label"]
  ready["GitHub.ready"]
  merge["GitHub.merge"]
  paged -->|"call"| call
  call -->|"request"| request
  ensure_all -->|"ensure_label"| ensure
  create_issue -->|"ensure_label"| ensure
  linked -->|"timeline"| timeline
  linked -->|"call"| call
  agent_events -->|"timeline"| timeline
  is_agent -->|"agent_events"| agent_events
  start_error -->|"assigned_at"| assigned
  start_error -->|"timeline"| timeline
  assigned -->|"timeline"| timeline
  label -->|"ensure_label"| ensure
  ready -->|"request"| request
  merge -->|"ready"| ready
  merge -->|"call"| call
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
if token: add ******
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

## Functions and methods

Covered by the class method cards above.

## Module-level code

The file declares standard-library imports, module configuration constants, a label-description mapping, and the `GitHub` class in this region. The remaining module-level workflow implementation is documented in the later source packets. (`.github/bible/bible_queue.py:1-87`, `.github/bible/bible_queue.py:88-302`)

## Surprises

`tarball` filters archive members to regular files and directories and checks normalized targets against the destination root before writing them. (`.github/bible/bible_queue.py:246-259`)
