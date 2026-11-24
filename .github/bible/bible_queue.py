#!/usr/bin/env python3
"""Mode B: GitHub workflows drive the codebase analysis, one Copilot session at a time per component.

Called by the workflows in examples/github/workflows/ (copied to .github/workflows/ in the target
repository); never by a skill. Every run works the state out again from GitHub (issues, pull
requests, labels, branches) and from the files on the branches, so a run that fails or is skipped
loses nothing: the next one (every 15 minutes) carries on.

  python3 .github/bible/bible_queue.py start --components all --verify-model V [--model M] [--concurrency N]
  python3 .github/bible/bible_queue.py reconcile
  python3 .github/bible/bible_queue.py delta --changed-file FILE

The flow, which is the person's Mode A steps done by a workflow:
  1. start: a tracker issue holds the run's settings; the next reconcile assigns the plan issue to Copilot.
  2. The person merges the plan pull request (components.json is then on the default branch).
  3. Per selected component: branch bible/<name> (reset to the default branch at the run's start);
     one chunk issue at a time assigned to Copilot with base_branch bible/<name>. A finished chunk pull
     request by Copilot, from this repository, into bible/<name>, inside the component's folders (never
     its verification files), that makes progress, is merged into bible/<name>; then the next chunk.
  4. When the component's check passes on bible/<name> (coverage.py --component), a verify issue is
     assigned on the verification model. A PASS whose recorded fingerprint matches the pages: a pull
     request bible/<name> -> default branch for the person. Otherwise a revision chunk, then verify
     again, at most MAX_VERIFY_ROUNDS times; then a person.
  5. When every selected component's pull request is merged: the assemble issue, then the whole
     verification; the person merges each. The tracker closes itself.
  6. delta: after a push to the default branch, one update issue per component whose files changed.

Nothing is ever merged into the default branch by this script: a person merges those pull requests.
A session that fails is retried once; a second failure labels the issue bible-needs-human and
unassigns Copilot. Removing that label (a person) retries it. Copilot's questions (WAITING FOR ANSWERS)
label the issue bible-waiting-answer and pause that component only. Closing the tracker issue stops
the run. Every issue of a run carries the label bible-run-<tracker number>.

Environment: GITHUB_REPOSITORY (owner/name), GH_TOKEN (a user token allowed to assign Copilot),
GITHUB_API_URL (default https://api.github.com), BIBLE_SKILLS (default .github/skills),
BIBLE_AGENT_LOGINS (comma list; default Copilot,copilot-swe-agent[bot],copilot-swe-agent), BIBLE_AGENT_APP (default copilot-swe-agent), BIBLE_NOW (tests only).
Standard library only.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True

COPILOT = "copilot-swe-agent[bot]"
AGENT_LOGINS = {l.strip() for l in os.environ.get("BIBLE_AGENT_LOGINS", "Copilot,copilot-swe-agent[bot],copilot-swe-agent").split(",") if l.strip()}
# With a user token, GitHub records Copilot's pull requests and commits under the token owner's login. What only GitHub
# can set is the app on the pull request's timeline events: copilot_work_started / copilot_work_finished performed via
# this app. That marks a pull request as Copilot's; the session is still working while copilot_work_started is the last
# of its WORK_EVENTS (below).
AGENT_APP = os.environ.get("BIBLE_AGENT_APP", "copilot-swe-agent")
# A session that ends in an error is recorded as copilot_work_finished_failure. With no copilot_work_started before it,
# Copilot never ran (seen on github.com, 24 Nov 2026: the account's monthly AI credits were used up; every
# "@copilot continue" failed within seconds and used 0 premium requests): retrying cannot help, a person must act.
WORK_EVENTS = ("copilot_work_started", "copilot_work_finished", "copilot_work_finished_failure")
COMPARE_MAX = 300  # GitHub's comparison of two commits lists at most this many files
START_ERROR = re.compile(r"unable to start working", re.I)
FINAL_STATES = ("NEW_CHAT", "COMPONENT_DONE", "WAITING_ANSWER", "STOP")
NO_PR_AFTER = 30 * 60      # seconds after assignment with no pull request: the session did not start
IDLE_AFTER = 20 * 60       # seconds without a push: the session has ended
MAX_VERIFY_ROUNDS = 2
MAX_TARBALL = 512 << 20    # bytes of a branch's tarball the queue downloads to run the check
GATE_TIMEOUT = 300         # seconds for coverage.py / status.py on a branch; a timeout means "could not check", never a failure
MAX_UNPACKED = 2 << 30     # bytes a branch may unpack to, and at most MAX_MEMBERS files
MAX_MEMBERS = 200000
RUN_BUDGET = 19 * 60       # seconds per queue run (the job allows 20 minutes)
MAX_SESSION_CAP = 22       # work sessions per component, whatever the plan estimates (2 x 10 + 2)
MIN_SESSION_CAP = 4        # work sessions per component before a person decides: 2 x the estimate + 2, at least this
MAX_CONTINUE = 3           # continuation comments for one assembly or whole verification before a person decides
CONTINUE_MARK = "<!-- bible-continue -->"
SETTINGS = re.compile(r"<!--\s*bible-settings\s*(\{.*?\})\s*-->", re.S)
STATE = re.compile(r"<!--\s*bible-state\s*(\{.*?\})\s*-->", re.S)   # the queue's own counters, on its tracker
UPDATED = re.compile(r"^Updated (\d{4}-\d\d-\d\dT\d\d:\d\d)", re.M)
MAX_NOCHECK = 3            # checks in a row that could not run (time, size, a missing script), then a person
ATTEMPT = re.compile(r"^Attempt:\s*(\d+)", re.M)
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,39}\Z")
LABELS = {
    "bible-tracker": "One analysis run: settings and progress",
    "bible-replayed": "Closed run: its recorded code changes are in update issues",
    "bible-plan": "Copilot session: plan the components",
    "bible-chunk": "Copilot session: part of one component",
    "bible-verify": "Copilot session: verify one component",
    "bible-assemble": "Copilot session: whole-system pages",
    "bible-verify-all": "Copilot session: verify the whole analysis",
    "bible-revise-all": "Copilot session: apply the whole verification's corrections",
    "bible-needs-revision": "A whole verification that asked for corrections: a revision follows",
    "bible-stale-verdict": "A PASS not about the pages now, or not by this run: verified again",
    "bible-delta": "Copilot session: update after a code change",
    "bible-waiting-answer": "Copilot asked questions: answer on the pull request with @copilot",
    "bible-needs-human": "Failed twice: a person must look, then remove this label to retry",
}


# ---------------------------------------------------------------- GitHub ----------

class GitHub:
    def __init__(self, repo, token, api=None):
        self.repo, self.token = repo, token
        self.api = (api or os.environ.get("GITHUB_API_URL") or "https://api.github.com").rstrip("/")
        self.known_labels = None

    def request(self, method, url, body=None, timeout=60):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if self.token:
            req.add_header("Authorization", "Bearer " + self.token)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        return urllib.request.urlopen(req, timeout=timeout)

    def call(self, method, path, body=None, ok404=False):
        url = path if path.startswith("http") else "%s/repos/%s%s" % (self.api, self.repo, path)
        try:
            with self.request(method, url, body) as resp:
                payload = resp.read()
        except urllib.error.HTTPError as err:
            if err.code == 404 and ok404:
                return None
            detail = err.read().decode("utf-8", "replace")[:300]
            raise RuntimeError("GitHub %s %s: HTTP %d %s" % (method, path.split("?")[0], err.code, detail))
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            raise RuntimeError("GitHub %s %s: %s" % (method, path.split("?")[0], err))
        return json.loads(payload) if payload else {}

    def paged(self, path):
        out, page = [], 1
        while True:
            sep = "&" if "?" in path else "?"
            batch = self.call("GET", "%s%sper_page=100&page=%d" % (path, sep, page))
            out += batch
            if len(batch) < 100:
                return out
            page += 1

    def issues(self, labels, state="open"):
        q = urllib.parse.quote(",".join(labels))
        return [i for i in self.paged("/issues?state=%s&labels=%s" % (state, q)) if "pull_request" not in i]

    def ensure_label(self, name, why="Codebase analysis run"):
        if self.known_labels is None:
            self.known_labels = {l["name"] for l in self.paged("/labels")}
        if name not in self.known_labels:
            self.call("POST", "/labels", {"name": name, "color": "5319e7", "description": why[:100]})
            self.known_labels.add(name)

    def ensure_labels(self):
        for name, why in LABELS.items():
            self.ensure_label(name, why)

    def create_issue(self, title, body, labels, assign=None):
        for name in labels:
            self.ensure_label(name, LABELS.get(name, "Codebase analysis run"))
        payload = {"title": title, "body": body, "labels": labels}
        if assign is not None:
            payload["assignees"] = [COPILOT]
            payload["agent_assignment"] = assign
        return self.call("POST", "/issues", payload)

    def me(self):
        """The login of the token's owner: the identity of everything the queue writes (cached)."""
        if not getattr(self, "_me", None):
            self._me = (self.call("GET", self.api + "/user") or {}).get("login", "")
        return self._me

    def default_branch(self):
        return self.call("GET", "")["default_branch"]

    def branch_sha(self, branch):
        ref = self.call("GET", "/git/ref/heads/" + urllib.parse.quote(branch), ok404=True)
        return ref["object"]["sha"] if ref else None

    def create_branch(self, branch, sha):
        self.call("POST", "/git/refs", {"ref": "refs/heads/" + branch, "sha": sha})

    def reset_branch(self, branch, sha):
        self.call("PATCH", "/git/refs/heads/" + urllib.parse.quote(branch), {"sha": sha, "force": True})

    def file(self, path, ref):
        got = self.call("GET", "/contents/%s?ref=%s" % (urllib.parse.quote(path), urllib.parse.quote(ref)), ok404=True)
        if not got or isinstance(got, list) or "content" not in got:
            return None
        return base64.b64decode(got["content"]).decode("utf-8", "replace")

    def prs(self, base=None, state="open"):
        path = "/pulls?state=%s" % state + ("&base=" + urllib.parse.quote(base) if base else "")
        return self.paged(path)

    def timeline(self, number):
        return self.paged("/issues/%d/timeline" % number)

    def linked_prs(self, number):
        """Pull requests of this repository that mention the issue (a mention from another repository is ignored)."""
        nums = []
        for event in self.timeline(number):
            source = (event.get("source") or {}).get("issue") or {}
            where = ((source.get("repository") or {}).get("full_name")) or self.repo
            if event.get("event") == "cross-referenced" and source.get("pull_request") and where == self.repo:
                nums.append(source["number"])
        found = [self.call("GET", "/pulls/%d" % n, ok404=True) for n in sorted(set(nums))]
        return [p for p in found if p]

    def branch_prs(self, branch, base):
        """Pull requests from this repository's own branch into base (a fork's branch of the same name is not one)."""
        owner = self.repo.split("/")[0]
        return self.paged("/pulls?state=all&head=%s&base=%s" % (urllib.parse.quote(owner + ":" + branch), urllib.parse.quote(base)))

    def agent_events(self, number):
        """[(event, time)] of Copilot's work on a pull request: events GitHub records as performed via the agent's app."""
        return [(e.get("event"), e.get("created_at") or "") for e in self.timeline(number)
                if (e.get("performed_via_github_app") or {}).get("slug") == AGENT_APP
                and e.get("event") in WORK_EVENTS]

    def is_agent_pr(self, pr):
        """Copilot's pull request: by an agent login, or with Copilot's work recorded on its timeline by GitHub."""
        user = pr.get("user") or {}
        if user.get("login", "") in AGENT_LOGINS and user.get("type", "Bot") == "Bot":
            return True  # an agent login counts only on a Bot account: a person cannot take that name
        return bool(self.agent_events(pr["number"]))  # any WORK_EVENTS by the agent app: only GitHub can record those

    def start_error(self, issue):
        """Copilot's comment saying it could not start (a model not allowed, a policy) since the last assignment, or None."""
        since = self.assigned_at(issue)
        for e in self.timeline(issue["number"]):
            actor = (e.get("actor") or e.get("user")) or {}
            who = actor.get("login", "") if actor.get("type", "Bot") == "Bot" else ""
            if e.get("event") == "commented" and who in AGENT_LOGINS and (e.get("created_at") or "") >= since \
                    and START_ERROR.search(e.get("body") or ""):
                return (e.get("body") or "").strip().splitlines()[0][:300]
        return None

    def assigned_at(self, issue):
        """When Copilot was last assigned to the issue (the issue's creation when the timeline says nothing)."""
        times = [e.get("created_at") for e in self.timeline(issue["number"]) if e.get("event") == "assigned" and e.get("created_at")]
        return max(times) if times else issue["created_at"]

    def pr_files(self, number):
        """Every path a pull request touches, the old name of a renamed file included. GitHub lists at most 3,000
        files: a list shorter than the pull request's own count is refused, so no file escapes the scope checks."""
        pr = self.call("GET", "/pulls/%d" % number) or {}
        base, head = pr.get("base") or {}, (pr.get("head") or {}).get("sha")
        # only an open pull request: once merged, the tip contains it and the comparison is empty
        tip = (self.branch_sha(base["ref"]) if pr.get("state") == "open" and base.get("ref") and base.get("sha") and head
               else None)
        if tip and tip != base["sha"]:
            # GitHub lists a pull request's files against the base commit it last recorded. Seen on github.com, 24 Nov
            # 2026: main moved, the revision merged main, and its file list then held main's own changes, so the scope
            # check failed a clean pull request. Compare against the base branch as it is now (the merge base, as a
            # merge would see it). GitHub's comparison lists at most COMPARE_MAX files: a full list is refused.
            compared = self.call("GET", "/compare/%s...%s" % (tip, head))
            listed = compared.get("files") if isinstance(compared, dict) else None
            # fail closed: no file list, or none while GitHub counts changed files, is never read as "nothing changed"
            if not isinstance(listed, list) or (not listed and as_int(pr.get("changed_files"))):
                raise RuntimeError("the comparison of #%d with %s gave no file list: not checked, not merged"
                                   % (number, base["ref"]))
            if len(listed) >= COMPARE_MAX:
                raise RuntimeError("the file list of #%d is incomplete (%d files or more against %s): not checked, not merged"
                                   % (number, COMPARE_MAX, base["ref"]))
            expected = None
        else:
            listed = self.paged("/pulls/%d/files" % number)
            expected = as_int(pr.get("changed_files"))
        if expected and len(listed) != expected:
            raise RuntimeError("the file list of #%d is incomplete (%d of %d files): not checked, not merged"
                               % (number, len(listed), expected))
        out = []
        for f in listed:
            out.append(f["filename"])
            if f.get("previous_filename"):
                out.append(f["previous_filename"])
        return out

    def commit_time(self, sha):
        return self.call("GET", "/commits/" + sha)["commit"]["committer"]["date"]

    def tarball(self, ref, dest):
        """Unpack the tree of ref into dest (no git needed), streaming to a temporary file; links and
        paths that would leave dest are skipped."""
        url = "%s/repos/%s/tarball/%s" % (self.api, self.repo, urllib.parse.quote(ref))
        with tempfile.TemporaryFile() as buf:
            try:
                with self.request("GET", url, timeout=300) as resp:
                    total = 0
                    while True:
                        chunk = resp.read(1 << 20)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > MAX_TARBALL:
                            raise RuntimeError("GitHub tarball %s: larger than %d MB, not unpacked" % (ref, MAX_TARBALL >> 20))
                        buf.write(chunk)
            except (urllib.error.URLError, TimeoutError, OSError) as err:
                raise RuntimeError("GitHub tarball %s: %s" % (ref, err))
            buf.seek(0)
            root = os.path.abspath(dest)
            with tarfile.open(fileobj=buf, mode="r:gz") as tar:
                unpacked, members = 0, 0
                for member in tar:
                    members += 1
                    unpacked += max(member.size, 0)
                    if members > MAX_MEMBERS or unpacked > MAX_UNPACKED:
                        raise RuntimeError("GitHub tarball %s: more than %d files or %d MB unpacked, not checked"
                                           % (ref, MAX_MEMBERS, MAX_UNPACKED >> 20))
                    parts = member.name.split("/", 1)
                    if len(parts) < 2 or not parts[1] or not (member.isfile() or member.isdir()):
                        continue
                    target = os.path.normpath(os.path.join(root, parts[1]))
                    if not target.startswith(root + os.sep):
                        continue
                    if member.isdir():
                        os.makedirs(target, exist_ok=True)
                        continue
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with tar.extractfile(member) as src, open(target, "wb") as out:
                        shutil.copyfileobj(src, out)

    def label(self, number, name):
        self.ensure_label(name, LABELS.get(name, "Codebase analysis run"))
        self.call("POST", "/issues/%d/labels" % number, {"labels": [name]})

    def unlabel(self, number, name):
        self.call("DELETE", "/issues/%d/labels/%s" % (number, urllib.parse.quote(name)), ok404=True)

    def comment(self, number, text):
        self.call("POST", "/issues/%d/comments" % number, {"body": text})

    def close(self, number, reason="completed"):
        self.call("PATCH", "/issues/%d" % number, {"state": "closed", "state_reason": reason})

    def set_body(self, number, body):
        self.call("PATCH", "/issues/%d" % number, {"body": body})

    def unassign(self, number):
        self.call("DELETE", "/issues/%d/assignees" % number, {"assignees": [COPILOT]})

    def assign(self, number, assign):
        self.call("POST", "/issues/%d/assignees" % number, {"assignees": [COPILOT], "agent_assignment": assign})

    def ready(self, pr):
        """Copilot opens draft pull requests; a draft cannot be merged. Mark it ready (GraphQL only)."""
        query = "mutation($id: ID!) { markPullRequestReadyForReview(input: {pullRequestId: $id}) { clientMutationId } }"
        url = self.api + "/graphql" if not self.api.endswith("/api/v3") else self.api[:-len("/v3")] + "/graphql"
        try:
            with self.request("POST", url, {"query": query, "variables": {"id": pr["node_id"]}}) as resp:
                resp.read()
        except urllib.error.HTTPError as err:
            raise RuntimeError("GitHub GraphQL markPullRequestReadyForReview: HTTP %d" % err.code)

    def merge(self, pr, title):
        if pr.get("draft"):
            self.ready(pr)
        # The commit that was checked, and only that one: GitHub refuses the merge if anything was pushed since.
        self.call("PUT", "/pulls/%d/merge" % pr["number"], {"merge_method": "squash", "commit_title": title, "sha": pr["head"]["sha"]})

    def close_pr(self, number):
        self.call("PATCH", "/pulls/%d" % number, {"state": "closed"})

    def create_pr(self, head, base, title, body):
        return self.call("POST", "/pulls", {"head": head, "base": base, "title": title, "body": body})


# ---------------------------------------------------------------- helpers ---------

def now():
    stamp = os.environ.get("BIBLE_NOW")
    return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else datetime.datetime.now(datetime.timezone.utc)


def age(stamp):
    return (now() - datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))).total_seconds()


SAFE_PATH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(/[A-Za-z0-9][A-Za-z0-9._-]*)*\Z")
SAFE_FILE = re.compile(r"^(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9_.][A-Za-z0-9_./-]{0,250}\Z")  # quoted to Copilot: no spaces, @, '..' or leading '-'
REPLAYED_MARK = "<!-- bible-deferred-replayed -->"  # on a closed tracker: its recorded updates are in update issues
DEFERRED_PER_COMMENT = 200 # paths per deferred-update comment (GitHub's comment limit is 65,536 characters)
ABANDONED_AFTER = 14 * 24 * 3600  # a tracker untouched this long no longer holds back update issues
MAX_DELTA_ISSUES = 10      # update sessions one push may start; more, and a person decides
SAFE_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z")
DEPTH_VALUES = ("deep", "standard", "survey")  # coverage.DEPTHS


def shown_files(paths, limit=10):
    """File names for a comment or an issue Copilot reads: plain paths quoted, the others only counted."""
    plain = [p for p in paths if SAFE_FILE.match(p)]
    other = len(paths) - len(plain)
    return ", ".join("`%s`" % p for p in plain[:limit]) + (" and %d more" % (len(plain) - limit) if len(plain) > limit else "") + \
        (" and %d with unusual characters in their names" % other if other else "")


def settings_of(tracker):
    """The run's settings from the tracker, or None when they are missing or unsafe. Anyone with write access can edit
    the tracker, and the settings reach file paths, script arguments and the text of comments that start Copilot, so
    each value must have the form the workflow form allows."""
    match = SETTINGS.search(tracker.get("body") or "")
    try:
        data = json.loads(match.group(1)) if match else None
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    analysis = str(data.get("analysis", "codebase-analysis"))
    if not SAFE_PATH.match(analysis) or ".." in analysis.split("/"):
        return None
    if str(data.get("depth", "deep")) not in DEPTH_VALUES:
        return None
    for key in ("model", "verify_model"):
        value = str(data.get(key) or "")
        if value and not SAFE_MODEL.match(value):
            return None
    return data


def labels_of(item):
    return {l["name"] if isinstance(l, dict) else l for l in item.get("labels", [])}


def comp_label(name):
    return "bible/" + name


def issue_text(gh, path, ref, fallback_title):
    """(title, body) from a ledger/issues/*.md file written by discover.py."""
    text = gh.file(path, ref) or ""
    lines = text.splitlines()
    if lines and lines[0].startswith("Title:"):
        return lines[0][len("Title:"):].strip(), "\n".join(lines[1:]).strip()
    return fallback_title, text.strip()


def assignment(gh, base, model):
    out = {"target_repo": gh.repo, "base_branch": base}
    if model:
        out["model"] = model
    return out


def json_file(gh, path, ref):
    text = gh.file(path, ref)
    try:
        return json.loads(text) if text else None
    except ValueError:
        return None


def section(text, title):
    match = re.search(r"^##\s+%s\s*$" % re.escape(title), text, re.M)
    if not match:
        return ""
    rest = text[match.end():]
    nxt = re.search(r"^##\s", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


RECHECK_LINE = re.compile(r"After corrections:[^\n]*?(\d+)\s+of\s+(\d+)\s+confirmed", re.I)  # status.py's rule
ACCURACY_ROW = re.compile(r"^\|\s*Accuracy[^|]*\|\s*(\d+(?:\.\d+)?)\s*%", re.M | re.I)    # status.py's rule
RECHECK_MIN_ACCURACY = 95.0
RECHECK_OF_ROW = re.compile(r"^\|\s*Re-check of\s*\|\s*`?([^|`]+?)`?\s*\|\s*$", re.M | re.I)              # status.py's rule
REPORT_NAME = re.compile(r"^verification-report[\w.-]*\.md$")


def report_facts(text, fetch=None, depth=0):
    """(verdict, major corrections, fingerprint, (confirmed, flagged) or None, accuracy or None) of a verification report,
    by the same rules as status.py: exactly one Verdict row, holding one verdict, outside comments and code blocks."""
    if not text:
        return None
    visible = re.sub(r"<!--.*?-->|^```.*?^```", "", text, flags=re.S | re.M)
    verdicts = re.findall(r"^\|\s*Verdict\s*\|\s*\**\s*(PASS AFTER CORRECTIONS|PASS|FAIL)\s*\**\s*\|\s*$", visible, re.M | re.I)
    rows = re.findall(r"^\|\s*Verdict\s*\|", visible, re.M | re.I)
    if len(verdicts) != 1 or len(rows) != 1:
        return ("UNREADABLE", 0, None, None, None, False)
    majors = sum(1 for line in section(text, "Corrections").splitlines()  # status.py counts in the raw text too
                 if line.lstrip().startswith("|") and re.search(r"\|\s*major\s*\|", line, re.I))
    printed = re.search(r"^\|\s*Analysis fingerprint\s*\|\s*`?([0-9a-f]{16})`?", visible, re.M | re.I)
    recheck = RECHECK_LINE.search(visible)
    base = RECHECK_OF_ROW.search(visible)
    found = [float(v) for v in ACCURACY_ROW.findall(section(visible, "Scores"))]
    accuracy = min(found) if found else None  # every Accuracy row counts: the lowest one decides
    if base and recheck:
        # status.py's rule: the lowest Accuracy of this report and of every round its Re-check of row leads to (fetch
        # gives a sibling report's text); a broken chain, or a base that is not a report, gives no accuracy
        name = base.group(1).strip()
        older = fetch(name) if fetch and REPORT_NAME.match(name) and depth < 20 else None
        older_facts = report_facts(older, fetch, depth + 1) if older else None
        older_acc = older_facts[4] if older_facts and older_facts[0] != "UNREADABLE" else None
        accuracy = None if older_acc is None else (min(older_acc, accuracy) if accuracy is not None else older_acc)
    noted = [l for l in section(visible, "Noticed outside the re-check").splitlines()
             if l.lstrip().startswith("|") and not re.match(r"^\|\s*(#|-{3}|none\s*\|)", l.strip(), re.I)]
    # [5]: a re-check (it names its round, or lists items noticed outside it): never a full round
    return (verdicts[0].upper(), majors, printed.group(1) if printed else None,
            (int(recheck.group(1)), int(recheck.group(2))) if recheck else None, accuracy, bool(base or noted))


RECHECK_ASK = (" The last report's verdict is PASS AFTER CORRECTIONS and a revision has applied it: this is its re-check. "
               "Follow the skill's \"Re-check after a revision\": judge every statement that report flagged and every "
               "statement the revision changed, draw no new sample, and write the line \"After corrections: every flagged "
               "statement re-checked: X of Y confirmed.\"")


def recheck_due(facts):
    """True when the next verification is the re-check of a PASS AFTER CORRECTIONS (a bounded list, not a new sample:
    in the live run each full round drew a new sample and found new minor items, a target that kept moving)."""
    return bool(facts and facts[0] == "PASS AFTER CORRECTIONS" and len(facts) > 4 and facts[4] is not None
                and facts[4] >= RECHECK_MIN_ACCURACY)  # below a PASS's accuracy the next round is a full one


def accepted(facts):
    """True when a report counts as verified, by status.py's trusted() rule, step for step (the fingerprint apart):
    a major correction needs a re-check with X = Y exactly; a re-check short of Y (X < Y, or Y = 0) is accepted only for
    a full round's own PASS with no major, never for a re-check (it names its round or lists items noticed outside
    it); a PASS AFTER CORRECTIONS needs a re-check; any report with a re-check needs 95% accuracy on its chain."""
    if not facts or facts[0] not in ("PASS", "PASS AFTER CORRECTIONS"):
        return False
    verdict, majors = facts[0], facts[1]
    recheck = facts[3] if len(facts) > 3 else None
    is_recheck = bool(len(facts) > 5 and facts[5])
    if majors and not (recheck and recheck[0] == recheck[1]):
        return False
    if recheck and (recheck[1] == 0 or recheck[0] < recheck[1]):
        if verdict != "PASS" or majors or recheck[1] == 0 or is_recheck:
            return False
    if verdict == "PASS AFTER CORRECTIONS" and not recheck:
        return False
    if recheck and (len(facts) < 5 or facts[4] is None or facts[4] < RECHECK_MIN_ACCURACY):
        return False
    return True


def as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):  # 1e999 from a hand-edited block is not a number of sessions
        return 0


def status_of(gh, path, ref):
    """A component's status.json as a dict (an unreadable one counts as empty, never as a crash)."""
    data = json_file(gh, path, ref)
    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------- the queue -------

class Queue:
    def __init__(self, gh, log=print):
        self.gh, self.log = gh, log
        self.skills = os.environ.get("BIBLE_SKILLS", ".github/skills")

    def run_issues(self, labels, state="open"):
        return self.gh.issues(labels + [self.run_label], state=state)

    def agent_pr(self, issue, base):
        """The open pull request Copilot opened for this issue: by the agent, from this repository, into base."""
        for pr in reversed(self.gh.linked_prs(issue["number"])):
            head_repo = ((pr.get("head") or {}).get("repo") or {}).get("full_name")
            if pr["state"] == "open" and head_repo == self.gh.repo and pr["base"]["ref"] == base and self.gh.is_agent_pr(pr):
                return pr
        return None

    # -- one session (any kind): has it started, finished, failed?
    def session(self, issue, base, analysis, comp=None):
        """('waiting'|'running'|'finished'|'no-start', pr) for an open session issue."""
        pr = self.agent_pr(issue, base)
        if pr is None:
            if self.gh.start_error(issue):
                return "start-error", None
            return ("no-start" if age(self.gh.assigned_at(issue)) > NO_PR_AFTER else "waiting"), None
        work = self.gh.agent_events(pr["number"])
        if work:  # GitHub says exactly whether Copilot is still working
            return ("running" if sorted(work, key=lambda w: w[1])[-1][0] == "copilot_work_started" else "finished"), pr
        pushed = age(self.gh.commit_time(pr["head"]["sha"]))
        asked = bool(pr.get("requested_reviewers")) or not pr.get("draft", False)
        if comp and "bible-chunk" in labels_of(issue):
            status = status_of(self.gh, "%s/ledger/components/%s/status.json" % (analysis, comp), pr["head"]["sha"])
            final = status.get("state") in FINAL_STATES
            return ("finished" if (final and (asked or pushed > IDLE_AFTER)) or pushed > 3 * IDLE_AFTER else "running"), pr
        return ("finished" if asked or pushed > IDLE_AFTER else "running"), pr

    def held(self, issue):
        """True: a session a person must look at. "released": a component session a person released (they removed the
        label bible-needs-human), closed so the next check decides the component's next step from fresh state.
        False: go on (a released plan or assembly session is assigned to Copilot again).

        Released means the label was removed after it was last added: Copilot missing from the assignees alone is not
        a release (unassigning Copilot by hand would otherwise start a new session every check, found in the audit).
        Copilot itself must be on the issue: with a user token GitHub also lists the token owner (seen on github.com)."""
        if "bible-needs-human" in labels_of(issue):
            return True
        if any((a or {}).get("login") in AGENT_LOGINS for a in issue.get("assignees") or []):
            return False
        events = self.gh.timeline(issue["number"])
        added = max([e.get("created_at") or "" for e in events if e.get("event") == "labeled"
                     and (e.get("label") or {}).get("name") == "bible-needs-human"] + [""])
        removed = max([e.get("created_at") or "" for e in events if e.get("event") == "unlabeled"
                       and (e.get("label") or {}).get("name") == "bible-needs-human"] + [""])
        if not (removed and removed > added):
            # Copilot was taken off the session by hand, not released after a hold: stop for a person, once
            self.gh.label(issue["number"], "bible-needs-human")
            self.gh.comment(issue["number"], "Copilot is no longer assigned to this session and no person released it. "
                            "A person must look; to continue, remove the label `bible-needs-human`.")
            return True
        if any(l.startswith("bible/") for l in labels_of(issue)):
            self.gh.comment(issue["number"], "The label `bible-needs-human` was removed: this session is closed and the "
                            "next check decides the component's next step from its current state.")
            self.gh.close(issue["number"], "not_planned")
            return "released"
        body = ATTEMPT.sub("Attempt: 1", issue.get("body") or "")
        self.gh.set_body(issue["number"], body)
        base = re.search(r"^Base branch:\s*(\S+)", body, re.M)
        self.gh.assign(issue["number"], assignment(self.gh, base.group(1) if base else self.default, self.model_for(issue)))
        self.gh.comment(issue["number"], "The label `bible-needs-human` was removed: assigned to Copilot again (attempt 1).")
        return False

    def model_for(self, issue):
        kinds = labels_of(issue)
        return self.settings.get("verify_model") if kinds & {"bible-verify", "bible-verify-all"} else self.settings.get("model")

    def hold_start_error(self, issue):
        """Copilot refused to start (a retry would fail the same way): hold the session for a person at once."""
        why = self.gh.start_error(issue) or "Copilot could not start"
        self.gh.label(issue["number"], "bible-needs-human")
        self.gh.unassign(issue["number"])
        self.gh.comment(issue["number"], "Copilot could not start: %s\n\nFix the cause (often the model name in the tracker's "
                        "settings: leave it empty for Copilot's default), then remove the label `bible-needs-human`." % why)

    def fail_or_retry(self, issue, pr, why):
        """Close a failed session and open attempt 2, or hold the second failure for a person. True when retried."""
        attempt = int((ATTEMPT.search(issue.get("body") or "") or [None, "1"])[1])
        if pr:
            self.gh.comment(pr["number"], "Not merged: %s." % why)
            self.gh.close_pr(pr["number"])
        if attempt >= 2:
            self.gh.label(issue["number"], "bible-needs-human")
            self.gh.unassign(issue["number"])
            self.gh.comment(issue["number"], "Second attempt failed: %s. A person must look. To retry, fix the cause (or this issue's "
                            "text), then remove the label `bible-needs-human`." % why)
            return False
        self.gh.comment(issue["number"], "Attempt %d failed: %s. Opening attempt %d." % (attempt, why, attempt + 1))
        self.gh.close(issue["number"], "not_planned")
        body = ATTEMPT.sub("Attempt: %d" % (attempt + 1), issue["body"]) if ATTEMPT.search(issue["body"] or "") else \
            "Attempt: 2\n\n" + (issue["body"] or "")
        base = re.search(r"^Base branch:\s*(\S+)", issue["body"] or "", re.M)
        self.gh.create_issue(issue["title"], body, sorted(l for l in labels_of(issue) if l.startswith("bible")),
                             assignment(self.gh, base.group(1) if base else self.default, self.model_for(issue)))
        return True

    # -- the whole run for one tracker
    def reconcile(self):
        self.deadline = time.monotonic() + RUN_BUDGET
        self.default = self.gh.default_branch()
        for tracker in self.gh.issues(["bible-tracker"]):
            settings = settings_of(tracker)
            if not settings:
                self.log("tracker #%d has no readable bible-settings block: skipped" % tracker["number"])
                continue
            try:
                self.run(tracker, settings)
            except Exception as err:  # one bad tracker never stops the others
                self.log("tracker #%d: %s: %s" % (tracker["number"], type(err).__name__, err))
        try:
            self.replay_closed_runs()
        except Exception as err:
            self.log("updates recorded on closed runs: %s: %s (tried again at the next check)" % (type(err).__name__, err))

    def replay_closed_runs(self):
        """Updates recorded on a run that ended without its Done step (a person closed the tracker, or an error after
        closing): opened as update issues once, or recorded on the run open now, so none is lost (live run, 24 Nov 2026:
        the round-4 verifier found that only the Done step replayed them)."""
        for tracker in self.gh.issues(["bible-tracker"], state="closed"):
            if "bible-replayed" in labels_of(tracker):
                continue  # done before: no timeline calls, so the cost does not grow with every run (review of #124)
            try:
                if not self.replayed(tracker):
                    paths = self.deferred_updates(tracker)
                    if paths:
                        self.delta(paths, (settings_of(tracker) or {}).get("analysis", "codebase-analysis"))
                    self.gh.comment(tracker["number"], "The %d code change(s) recorded while this run was open are now in "
                                    "update issues, or recorded on the run open now.\n%s" % (len(paths), REPLAYED_MARK))
                self.gh.label(tracker["number"], "bible-replayed")
            except Exception as err:  # one tracker that fails never blocks the others; it is tried again at the next check
                self.log("tracker #%d: replaying its recorded updates: %s: %s" % (tracker["number"], type(err).__name__, err))

    def replayed(self, tracker):
        """True when the queue itself marked this closed tracker's recorded updates as replayed."""
        me = self.gh.me()
        return any(e.get("event") == "commented" and ((e.get("actor") or e.get("user")) or {}).get("login") == me
                   and REPLAYED_MARK in (e.get("body") or "") for e in self.gh.timeline(tracker["number"]))

    def run(self, tracker, settings):
        gh, analysis = self.gh, settings.get("analysis", "codebase-analysis")
        self.settings, self.tracker = settings, tracker
        self.run_label = "bible-run-%d" % tracker["number"]
        found = STATE.search(tracker.get("body") or "")
        try:
            self.state = json.loads(found.group(1)) if found else {}
        except ValueError:
            self.state = {}
        if not isinstance(self.state, dict):
            self.state = {}
        catalog = json_file(gh, analysis + "/components.json", self.default)
        if not isinstance(catalog, dict) or catalog.get("proposed") or not isinstance(catalog.get("components"), list):
            return self.plan_phase(tracker, settings, analysis)
        # components.json is written by the plan session and merged by a person; its names still reach labels,
        # branch names and issue text, so the plan's own name rule is applied again here
        listed = [str(c.get("name") or "") for c in catalog["components"] if isinstance(c, dict)]
        names = [n for n in listed if NAME.match(n)]
        if len(names) != len(listed):
            # never a silent skip: a run that left a component out could close as done without analysing it
            return self.render(tracker, settings, {"(settings)": "stopped: components.json holds %d component name(s) that do not "
                                                   "follow the plan's name rule. Fix the plan (pass 2), run discover.py again, "
                                                   "then start a new run." % (len(listed) - len(names))})
        asked = settings.get("components", "all").strip()
        wanted = names if asked in ("all", "") else [n.strip() for n in asked.split(",") if n.strip()]
        unknown = [n for n in wanted if n not in names]
        if unknown or not wanted:
            return self.render(tracker, settings, {"(settings)": "stopped: %s; components.json has %s. Close this tracker and start "
                                                   "a new run with the right names." % (
                                                       "unknown component(s) " + ", ".join(unknown) if unknown else "no component selected",
                                                       ", ".join(names))})
        for issue in self.run_issues(["bible-plan"]):  # the plan is merged: its session is over
            gh.close(issue["number"])
        self.estimate = {c["name"]: c.get("est_sessions", "?") for c in catalog["components"]}
        rows, active = {}, 0
        for name in wanted:
            try:
                rows[name] = self.component(analysis, name)
            except Exception as err:  # kept to this component; the next run tries again
                rows[name] = "error this run (retried next run): %s: %s" % (type(err).__name__, str(err)[:160])
            active += rows[name].endswith(("running", "starting", "merged")) or rows[name].startswith("waiting")
        cap = as_int(settings.get("concurrency"))
        for name in wanted:  # start components that are still waiting, up to the cap
            if rows[name] == "not started" and (not cap or active < cap):
                try:
                    self.start_chunk(analysis, name, fresh=True)
                    rows[name], active = "session starting", active + 1
                except RuntimeError as err:
                    rows[name] = "error this run (retried next run): %s" % str(err)[:160]
        if all(r == "merged" for r in rows.values()):
            rows["(whole analysis)"] = self.assemble_phase(tracker, settings, analysis)
        self.render(tracker, settings, rows)

    def plan_phase(self, tracker, settings, analysis):
        gh = self.gh
        open_plan = self.run_issues(["bible-plan"])
        if not open_plan:
            title, body = issue_text(gh, analysis + "/ledger/issues/plan.md", self.default, "Codebase analysis - plan the components")
            if not body:
                body = ("Use the analyzing-a-codebase skill (in %s) for passes 1 and 2 only: run next.py --new-session, write the "
                        "`## Components` table in %s/progress.md, then run discover.py until it exits 0. Do not start any "
                        "component." % (self.skills, analysis))
            gh.create_issue(title, "Tracker: #%d\nBase branch: %s\nAttempt: 1\n\n%s" % (tracker["number"], self.default, body),
                            ["bible-plan", self.run_label], assignment(gh, self.default, settings.get("model")))
            return self.render(tracker, settings, {"(plan)": "plan session assigned"})
        issue = open_plan[0]
        if self.held(issue):
            return self.render(tracker, settings, {"(plan)": "needs a person: see #%d" % issue["number"]})
        state, pr = self.session(issue, self.default, analysis)
        if state == "start-error":
            self.hold_start_error(issue)
            return self.render(tracker, settings, {"(plan)": "needs a person: see #%d" % issue["number"]})
        if state == "no-start":
            self.fail_or_retry(issue, None, "no pull request %d minutes after assignment" % (NO_PR_AFTER // 60))
        self.render(tracker, settings, {"(plan)": "review and merge the plan pull request #%d" % pr["number"]
                                        if pr else "plan session %s" % state})

    def start_chunk(self, analysis, name, fresh=False, note=""):
        """Assign the next chunk. At the run's first chunk for a component, its branch starts again from the default branch."""
        gh, branch = self.gh, "bible/" + name
        head_sha = gh.branch_sha(self.default)
        if not gh.branch_sha(branch):
            gh.create_branch(branch, head_sha)
        elif fresh and not self.run_issues([comp_label(name)], state="all"):
            gh.reset_branch(branch, head_sha)
        title, body = issue_text(gh, "%s/ledger/issues/%s.md" % (analysis, name), self.default,
                                 "Codebase analysis - component %s" % name)
        head = "Component: %s\nBase branch: %s\nAttempt: 1\n" % (name, branch)
        gh.create_issue(title, head + (note + "\n" if note else "") + "\n" + body, ["bible-chunk", comp_label(name), self.run_label],
                        assignment(gh, branch, self.settings.get("model")))

    def component(self, analysis, name):
        gh, branch = self.gh, "bible/" + name
        since = self.tracker["created_at"]
        for pr in gh.branch_prs(branch, self.default):
            same_repo = ((pr.get("head") or {}).get("repo") or {}).get("full_name") == gh.repo
            if not same_repo or pr.get("created_at", "") < since or "Tracker: #%d" % self.tracker["number"] not in (pr.get("body") or ""):
                continue  # a fork's branch of the same name, an older run's, or one this run did not open
            if pr.get("merged_at"):
                return "merged"
            if pr["state"] == "open":
                return "review the pull request #%d" % pr["number"]
            return "needs a person: its pull request #%d was closed without merging; reopen it, or start a new run" % pr["number"]
        open_sessions = self.run_issues(["bible-chunk", comp_label(name)]) + self.run_issues(["bible-verify", comp_label(name)])
        if open_sessions:
            issue = open_sessions[0]
            hold = self.held(issue)
            if hold == "released":
                return "released: next step at the next check"
            if hold:
                return "needs a person: see #%d" % issue["number"]
            # A merge is the end of this run's work for the component. Right after a merge GitHub can still return the
            # branch's files from before it (seen on github.com, 24 Nov 2026), so the next step is decided at the next
            # check, from fresh data.
            return self.follow(analysis, name, issue)
        if not self.run_issues([comp_label(name)], state="all"):
            return "not started"
        holds = self.run_issues(["bible-hold", comp_label(name)], state="all")
        open_hold = [h for h in holds if h["state"] == "open"]
        if open_hold:
            if "bible-needs-human" in labels_of(open_hold[0]):
                return "needs a person: see #%d" % open_hold[0]["number"]
            gh.close(open_hold[0]["number"])  # the person removed the label: new rounds from here
            holds = self.run_issues(["bible-hold", comp_label(name)], state="all")
        after = max([h.get("closed_at") or "" for h in holds] + [""])
        status = status_of(gh, "%s/ledger/components/%s/status.json" % (analysis, name), branch)
        gate_ok, pages = (False, None)
        if status.get("state") == "COMPONENT_DONE":
            if time.monotonic() + 2 * GATE_TIMEOUT + 300 > getattr(self, "deadline", float("inf")):
                return "waiting for the next check (not enough of this run's time left for its check)"
            gate_ok, pages = self.check(analysis, name, branch)
            if gate_ok is None:  # the check could not run (time, size, network): try again, start nothing
                return self.could_not_check("nocheck:" + name, "The check of component %s" % name, [comp_label(name)],
                                            "Codebase analysis - component %s needs a person" % name) or \
                    "check could not run this time: retried at the next check"
            self.state.pop("nocheck:" + name, None)
        if not gate_ok:
            merged_into_default = max([p.get("merged_at") or "" for p in gh.branch_prs(branch, self.default)] + [""])
            since = max(after, merged_into_default)  # a component merged earlier and now drifting starts a fresh count
            sessions = [i for i in self.run_issues(["bible-chunk", comp_label(name)], state="closed")
                        if (i.get("created_at") or "") >= since]
            # the estimate comes from components.json (written by the plan session): clamped, and the cap has a ceiling
            estimate = min(max(as_int(self.estimate.get(name)) or 2, 1), 10)
            cap = min(max(MIN_SESSION_CAP, 2 * estimate + 2), MAX_SESSION_CAP)
            if len(sessions) >= cap:
                # Found in the audit: a session that reports COMPONENT_DONE while the queue's own check fails would
                # otherwise get a new session at every check, with no limit.
                hold = gh.create_issue("Codebase analysis - component %s needs a person" % name,
                                       "Component: %s\nTracker: #%d\n\n%d work sessions and the component's check on %s still "
                                       "does not pass (about %d were expected). Run coverage.py --component %s on the branch "
                                       "to see why, fix the cause, then remove the label `bible-needs-human` from this issue."
                                       % (name, self.tracker["number"], len(sessions), branch, estimate, name),
                                       ["bible-hold", "bible-needs-human", comp_label(name), self.run_label])
                return "needs a person: see #%d" % hold["number"]
            done = len(self.run_issues(["bible-chunk", comp_label(name)], state="closed"))
            self.start_chunk(analysis, name, note="Session %d of about %d." % (done + 1, estimate))
            return "session starting"
        closed_verify = [i for i in self.run_issues(["bible-verify", comp_label(name)], state="closed")
                         if i.get("state_reason") == "completed" and i.get("created_at", "") >= after]
        any_verify = [i for i in self.run_issues(["bible-verify", comp_label(name)], state="closed") if i.get("state_reason") == "completed"]
        facts = report_facts(gh.file("%s/ledger/components/%s/verification-report.md" % (analysis, name), branch),
                             lambda n: gh.file("%s/ledger/components/%s/%s" % (analysis, name, n), branch)) if any_verify else None
        if accepted(facts) and facts[2] and facts[2] == pages:
            pr = gh.create_pr(branch, self.default, "Codebase analysis: component %s" % name,
                              "Component `%s`, verified (PASS, pages fingerprint %s). Tracker: #%d. Review the pages under "
                              "`%s/lld/%s/`, then merge." % (name, pages, self.tracker["number"], analysis, name))
            return "review the pull request #%d" % pr["number"]
        # Revise or verify is decided by the fingerprint, as next.py decides it: a verdict whose fingerprint equals the
        # pages now is about these pages (its corrections are not applied yet); any other verdict is about pages that
        # have changed since, so they are verified again. Issue titles are not used: on github.com a session started
        # for another reason also changed the pages (24 Nov 2026).
        about_these_pages = bool(facts and facts[2] and facts[2] == pages)
        needs_revision = bool(facts and not accepted(facts))
        # After any chunk session merged since the last verification (a revision, or a session started for drift or
        # gaps) the pages are verified first: so no revision follows another, and every round ends in a verdict.
        last_verify = max([i.get("closed_at") or "" for i in any_verify] + [""])
        chunk_since_verify = any((i.get("closed_at") or "") > last_verify for i in self.run_issues(
            ["bible-chunk", comp_label(name)], state="closed") if i.get("state_reason") == "completed")
        # Each verification counts, so the rounds always end: after MAX_VERIFY_ROUNDS without a clean PASS on these
        # pages (an unreadable report, a missing or wrong fingerprint and a verdict asking for corrections alike),
        # a person decides.
        if facts and not chunk_since_verify and len(closed_verify) >= MAX_VERIFY_ROUNDS:
            hold = gh.create_issue("Codebase analysis - component %s needs a person" % name,
                                   "Component: %s\nTracker: #%d\n\n%d verifications without a clean PASS (last verdict: %s). Read "
                                   "%s/ledger/components/%s/verification-report.md on branch %s. Fix the cause (edit the pages on "
                                   "the branch, or the issue texts), then remove the label `bible-needs-human` from this issue: the "
                                   "queue then starts new rounds of revision and verification." % (
                                       name, self.tracker["number"], len(closed_verify), facts[0], analysis, name, branch),
                                   ["bible-hold", "bible-needs-human", comp_label(name), self.run_label])
            return "needs a person: see #%d" % hold["number"]
        if about_these_pages and needs_revision and not chunk_since_verify:  # its corrections are not applied yet
            self.start_chunk(analysis, name, note="Revision (verdict %s): apply %s/ledger/components/%s/verification-report.md "
                             "(references/revision.md, Component mode), then run next.py --component %s." % (facts[0], analysis, name, name))
            return "session starting"
        # no report yet, a PASS that does not match the pages (missing or old fingerprint), or a revision just merged: verify
        gh.create_issue("Codebase analysis - verify component %s" % name,
                        "Component: %s\nBase branch: %s\nAttempt: 1\n\nUse the verifying-a-codebase-analysis skill (in %s), scope: "
                        "component %s, in this new session. Record the fingerprint of the pages you judge in the report's header "
                        "(analyzing-a-codebase's scripts/status.py --fingerprint --component %s). Write "
                        "%s/ledger/components/%s/verification-report.md and nothing outside %s/ledger/components/%s/. "
                        "Summarise the verdict in the pull request description.%s" % (
                            name, branch, self.skills, name, name, analysis, name, analysis, name,
                            RECHECK_ASK if recheck_due(facts) else ""),
                        ["bible-verify", comp_label(name), self.run_label], assignment(gh, branch, self.settings.get("verify_model")))
        return "verify running"

    def follow(self, analysis, name, issue):
        gh, branch = self.gh, "bible/" + name
        kind = "verify" if "bible-verify" in labels_of(issue) else "chunk"
        state, pr = self.session(issue, branch, analysis, name)
        if state == "waiting":
            return "session starting"
        if state == "start-error":
            self.hold_start_error(issue)
            return "needs a person: see #%d" % issue["number"]
        if state == "no-start":
            retried = self.fail_or_retry(issue, None, "no pull request from Copilot into %s %d minutes after assignment" % (branch, NO_PR_AFTER // 60))
            return "session starting" if retried else "needs a person: see #%d" % issue["number"]
        if state == "running":
            return "%s running" % kind
        base = "%s/ledger/components/%s/" % (analysis, name)
        try:
            gh.pr_files(pr["number"])
        except RuntimeError as err:  # an incomplete file list cannot be checked: the session fails, it is never merged
            retried = self.fail_or_retry(issue, pr, str(err))
            return "session starting" if retried else "needs a person: see #%d" % issue["number"]
        if kind == "chunk":
            allowed = ("%s/lld/%s/" % (analysis, name), "%s/lld/api/%s/" % (analysis, name), base)
            bad = [f for f in gh.pr_files(pr["number"])
                   if not f.startswith(allowed) or os.path.basename(f).startswith("verification-")]
        else:
            bad = [f for f in gh.pr_files(pr["number"])
                   if not (f.startswith(base) and (os.path.basename(f).startswith("verification-") or os.path.basename(f) == "citations.tsv"))]
        if bad:
            retried = self.fail_or_retry(issue, pr, "files this kind of session may not write: " + shown_files(bad))
            return "session starting" if retried else "needs a person: see #%d" % issue["number"]
        status = status_of(gh, base + "status.json", pr["head"]["sha"])
        if kind == "chunk":
            if status.get("state") == "WAITING_ANSWER":
                if "bible-waiting-answer" not in labels_of(issue):
                    gh.label(issue["number"], "bible-waiting-answer")
                    gh.label(pr["number"], "bible-waiting-answer")
                return "waiting for answers on #%d" % pr["number"]
            before = as_int(status_of(gh, base + "status.json", branch).get("packets_done"))
            revision = "\nRevision (" in (issue.get("body") or "")
            progressed = as_int(status.get("packets_done")) > before or status.get("state") == "COMPONENT_DONE"
            if status.get("state") == "STOP" or not progressed:
                retried = self.fail_or_retry(issue, pr, "no progress (state %s, packets %s -> %s)" % (status.get("state"), before, status.get("packets_done")))
                return "session starting" if retried else "needs a person: see #%d" % issue["number"]
            pages = ("%s/lld/%s/" % (analysis, name), "%s/lld/api/%s/" % (analysis, name), base + "revision-log.md")
            if revision and not any(f.startswith(pages) for f in gh.pr_files(pr["number"])):
                # seen on github.com (24 Nov 2026): a revision that ran next.py, saw the gate pass and changed nothing
                retried = self.fail_or_retry(issue, pr, "the revision changed no page and recorded no correction")
                return "session starting" if retried else "needs a person: see #%d" % issue["number"]
            if revision and status.get("state") != "COMPONENT_DONE":
                retried = self.fail_or_retry(issue, pr, "the revision did not end at COMPONENT DONE")
                return "session starting" if retried else "needs a person: see #%d" % issue["number"]
        elif not gh.file(base + "verification-report.md", pr["head"]["sha"]):
            retried = self.fail_or_retry(issue, pr, "no verification report written")
            return "session starting" if retried else "needs a person: see #%d" % issue["number"]
        gh.merge(pr, "bible(%s): %s session #%d" % (name, kind, issue["number"]))
        gh.unlabel(issue["number"], "bible-waiting-answer")
        gh.close(issue["number"])
        return "%s merged" % kind

    def check(self, analysis, name, branch):
        """(gate passes, pages fingerprint) of the component on its branch, with the default branch's own scripts."""
        scripts = os.path.join(self.skills, "analyzing-a-codebase", "scripts")
        if not os.path.isfile(os.path.join(scripts, "coverage.py")):
            self.log("no %s/coverage.py in this checkout: check skipped, treated as failing" % scripts)
            return False, None
        work = tempfile.mkdtemp(prefix="bible-gate-")
        try:
            try:
                self.gh.tarball(branch, work)
            except RuntimeError as err:  # too large, unreadable: the check could not run (no session is started for it)
                self.log("gate %s: %s" % (name, err))
                return None, None
            run = subprocess.run([sys.executable, "-I", os.path.abspath(os.path.join(scripts, "coverage.py")), "--repo", work,
                                  "--analysis", analysis, "--depth", self.settings.get("depth", "deep"), "--component", name,
                                  "--report", "-"], capture_output=True, text=True, timeout=GATE_TIMEOUT)
            self.log("gate %s: %s" % (name, (run.stdout.strip().splitlines() or ["no output"])[-1]))
            printed = subprocess.run([sys.executable, "-I", os.path.abspath(os.path.join(scripts, "status.py")), "--repo", work,
                                      "--analysis", analysis, "--fingerprint", "--component", name], capture_output=True, text=True,
                                     timeout=GATE_TIMEOUT)
            return run.returncode == 0, (printed.stdout.strip() or None)
        except subprocess.TimeoutExpired:
            self.log("gate %s: the check took longer than %d seconds: not checked this run" % (name, GATE_TIMEOUT))
            return None, None
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def could_not_check(self, key, what, hold_labels, hold_title):
        """A check that could not run counts; after MAX_NOCHECK in a row a person decides (it could fail the same way
        forever: always too slow, too large, a missing script). Returns the tracker row, or None to just wait."""
        self.state[key] = max(as_int(self.state.get(key)), 0) + 1  # a forged negative count cannot suppress the hold
        if self.state[key] < MAX_NOCHECK:
            return None
        self.state.pop(key, None)
        hold = self.gh.create_issue(hold_title, "Tracker: #%d\n\n%s could not run %d times in a row (the queue's log says why: a "
                                    "timeout, a branch over the size limits, a missing script). Fix the cause, then remove the "
                                    "label `bible-needs-human` from this issue." % (self.tracker["number"], what, MAX_NOCHECK),
                                    hold_labels + ["bible-hold", "bible-needs-human", self.run_label])
        return "needs a person: see #%d" % hold["number"]

    def whole_fingerprint(self, analysis):
        """The whole analysis's pages fingerprint on the default branch now (status.py --fingerprint), or None."""
        scripts = os.path.join(self.skills, "analyzing-a-codebase", "scripts")
        if not os.path.isfile(os.path.join(scripts, "status.py")):
            return None
        work = tempfile.mkdtemp(prefix="bible-whole-")
        try:
            self.gh.tarball(self.default, work)
            printed = subprocess.run([sys.executable, "-I", os.path.abspath(os.path.join(scripts, "status.py")), "--repo", work,
                                      "--analysis", analysis, "--fingerprint"], capture_output=True, text=True, timeout=GATE_TIMEOUT)
            return printed.stdout.strip() or None
        except (RuntimeError, subprocess.TimeoutExpired) as err:
            self.log("whole fingerprint: %s" % err)
            return None
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def assemble_phase(self, tracker, settings, analysis):
        gh = self.gh
        for kind, model, title, text in (
                ("bible-assemble", settings.get("model"), "Codebase analysis - assemble the whole bible", "assemble.md"),
                ("bible-verify-all", settings.get("verify_model"), "Codebase analysis - verify the whole analysis", None)):
            closed_done = [i for i in self.run_issues([kind], state="closed") if i.get("state_reason") == "completed"]
            if kind == "bible-verify-all":
                held_whole = self.whole_hold()
                if held_whole:  # consulted before any check of the whole analysis (review: a hold was never read here)
                    return held_whole
            if kind == "bible-verify-all" and closed_done:
                # GitHub closes the issue itself when the pull request that says "Fixes #N" is merged: a closed
                # verification is done only when the report on the default branch is a clean PASS (seen in review).
                facts = report_facts(gh.file("%s/verification-report.md" % analysis, self.default),
                                     lambda n: gh.file("%s/%s" % (analysis, n), self.default))
                newest = max(closed_done, key=lambda i: i.get("closed_at") or "")
                # Done means: a clean PASS, about the pages on the default branch now (its fingerprint), written by this
                # run's own verification pull request (found in the second audit: a PASS left by an earlier run, or an
                # issue closed by hand, would otherwise end the run with no verification).
                report_path = "%s/verification-report.md" % analysis
                on_default = gh.file(report_path, self.default)
                by_this_run = any(p.get("merged_at") and p["base"]["ref"] == self.default and gh.is_agent_pr(p)
                                  and ((p.get("head") or {}).get("repo") or {}).get("full_name") == gh.repo
                                  and report_path in gh.pr_files(p["number"])
                                  and gh.file(report_path, p["head"]["sha"]) == on_default  # the report as the session wrote it
                                  for p in gh.linked_prs(newest["number"]))
                clean = accepted(facts)
                if clean and by_this_run and facts[2]:
                    if time.monotonic() + GATE_TIMEOUT + 300 > getattr(self, "deadline", float("inf")):
                        return "verify-all: waiting for the next check (not enough of this run's time left)"
                    pages_now = self.whole_fingerprint(analysis)
                    if pages_now is None:  # could not compute it now: no verification round is used; counted, then a person
                        held = self.could_not_check("nofp", "The fingerprint of the whole analysis", ["bible-whole"],
                                                    "Codebase analysis - the whole analysis needs a person")
                        return ("verify-all: " + held) if held else \
                            "verify-all: the pages' fingerprint could not be computed now: checked again at the next check"
                    self.state.pop("nofp", None)
                    if facts[2] == pages_now:
                        continue
                if clean and not ({"bible-needs-revision", "bible-stale-verdict"} & labels_of(newest)) and not self.run_issues([kind]):
                    # a PASS about other pages, or not written by this run: nothing to correct, verify again (a round)
                    gh.label(newest["number"], "bible-stale-verdict")
                    gh.comment(newest["number"], "The PASS on %s is not about the pages there now, or was not written by this "
                               "run's verification: a new verification follows." % self.default)
                    return "verify-all: the PASS is not about the pages now: verifying again"
                if not clean and "bible-needs-revision" not in labels_of(newest) and not self.run_issues([kind]):
                    gh.label(newest["number"], "bible-needs-revision")
                    gh.comment(newest["number"], "Verdict %s: a revision of the whole analysis follows, then a new "
                               "verification." % (facts[0] if facts else "missing"))
                    return "verify-all: corrections asked (verdict %s): revision next" % (facts[0] if facts else "missing")
            elif closed_done:
                continue
            if kind == "bible-verify-all":
                step = self.revise_all_step(tracker, analysis)
                if step:
                    return step
            open_ = self.run_issues([kind])
            if open_:
                issue = open_[0]
                merged = [p for p in gh.linked_prs(issue["number"]) if p.get("merged_at") and p["base"]["ref"] == self.default
                          and ((p.get("head") or {}).get("repo") or {}).get("full_name") == gh.repo and gh.is_agent_pr(p)]
                if merged:
                    if kind == "bible-verify-all":
                        facts = report_facts(gh.file("%s/verification-report.md" % analysis, self.default),
                                     lambda n: gh.file("%s/%s" % (analysis, n), self.default))
                        if not accepted(facts):
                            # a record of corrections asked: not the end of the run; a revision of the whole analysis
                            # follows, then a new verification (revise_all_step)
                            gh.label(issue["number"], "bible-needs-revision")
                            gh.comment(issue["number"], "Verdict %s: a revision of the whole analysis follows, then a new "
                                       "verification." % (facts[0] if facts else "missing"))
                            gh.close(issue["number"], "not_planned")
                            return "verify-all: corrections asked (verdict %s): revision next" % (facts[0] if facts else "missing")
                    gh.close(issue["number"])
                    if kind == "bible-verify-all":
                        return "verify-all: merged; checked against the pages at the next check"  # the strict rule decides done
                    continue
                if self.held(issue):
                    return "%s: needs a person: see #%d" % (kind[6:], issue["number"])
                state, pr = self.session(issue, self.default, analysis)
                if state == "start-error":
                    self.hold_start_error(issue)
                    return "%s: needs a person: see #%d" % (kind[6:], issue["number"])
                if state == "no-start":
                    self.fail_or_retry(issue, None, "no pull request after assignment")
                if pr and state == "running":  # Copilot is still working on it: not ready for review yet
                    return "%s: running (pull request #%d)" % (kind[6:], pr["number"])
                if pr and state == "finished":
                    unfinished = self.continue_if_unfinished(issue, pr, kind, analysis)
                    if unfinished:
                        return unfinished
                return "%s: %s" % (kind[6:], "review and merge pull request #%d" % pr["number"] if pr else state)
            if text:
                title, body = issue_text(gh, "%s/ledger/issues/%s" % (analysis, text), self.default, title)
            else:
                body = ("Use the verifying-a-codebase-analysis skill (in %s) on the whole analysis in %s/, in this new session. "
                        "Record the pages' fingerprint (analyzing-a-codebase's scripts/status.py --fingerprint) in the report's "
                        "header, write verification-report.md, then run status.py --write." % (self.skills, analysis))
                if recheck_due(report_facts(gh.file("%s/verification-report.md" % analysis, self.default),
                                     lambda n: gh.file("%s/%s" % (analysis, n), self.default))):
                    body += RECHECK_ASK
            gh.create_issue(title, "Tracker: #%d\nBase branch: %s\nAttempt: 1\n\n%s" % (tracker["number"], self.default, body),
                            [kind, self.run_label], assignment(gh, self.default, model))
            return "%s session assigned" % kind[6:]
        # Code that changed during the run: its update issues first, while the tracker is still open (an error leaves it
        # open and the next check tries again), then once more after closing for a push that came in between.
        deferred = self.deferred_updates(tracker)
        if deferred:
            self.delta(deferred, analysis, record=False)
        gh.comment(tracker["number"], "Every component, the assembly and the whole verification are merged. Done.")
        gh.close(tracker["number"])
        late = sorted(set(self.deferred_updates(tracker)) - set(deferred))
        if late:
            try:
                self.delta(late, analysis, record=False)
            except Exception as err:  # the tracker is closed: say so where a person reads it; the next check tries again
                gh.comment(tracker["number"], "Code that changed at the end of this run could not get its update issues yet "
                           "(%s: %s); the next check tries again: %s" % (type(err).__name__, str(err)[:160], shown_files(late)))
                return "done"
        gh.comment(tracker["number"], "Recorded code changes: %d, in update issues.\n%s" % (len(deferred) + len(late), REPLAYED_MARK))
        gh.label(tracker["number"], "bible-replayed")
        return "done"

    def deferred_updates(self, tracker):
        """Paths of pushes recorded on the tracker while the run was open (only the queue's own marks count)."""
        me, paths = self.gh.me(), []
        for e in self.gh.timeline(tracker["number"]):
            actor = (e.get("actor") or e.get("user")) or {}
            if e.get("event") != "commented" or actor.get("login") != me:
                continue
            for raw in re.findall(r"<!-- bible-deferred-update (\[.*?\]) -->", e.get("body") or ""):
                try:
                    paths += [p for p in json.loads(raw) if isinstance(p, str) and SAFE_FILE.match(p)]
                except ValueError:
                    continue
        return sorted(set(paths))

    def whole_hold(self):
        """The row while a hold on the whole analysis waits for a person; a released one (label removed) is closed."""
        for h in self.run_issues(["bible-hold", "bible-whole"]):
            if "bible-needs-human" in labels_of(h):
                return "verify-all: needs a person: see #%d" % h["number"]
            self.gh.close(h["number"])  # the person removed the label: new rounds from here
        return None

    def revise_all_step(self, tracker, analysis):
        """After a whole verification that asked for corrections: one revision session of the whole analysis, then a
        new verification (the loop below opens it). Bounded like the components: after MAX_VERIFY_ROUNDS such
        verifications since a person last released the run, a person decides. None when nothing is to be done here."""
        gh = self.gh
        holds = self.run_issues(["bible-hold", "bible-whole"], state="all")
        open_hold = [h for h in holds if h["state"] == "open"]
        if open_hold:
            if "bible-needs-human" in labels_of(open_hold[0]):
                return "verify-all: needs a person: see #%d" % open_hold[0]["number"]
            gh.close(open_hold[0]["number"])  # the person removed the label: new rounds from here
            holds = self.run_issues(["bible-hold", "bible-whole"], state="all")
        after = max([h.get("closed_at") or "" for h in holds] + [""])
        # What to do next comes from the newest verdict that asked for corrections; the rounds count only those since a
        # person last released the run (a release gives new rounds, starting with a revision of that verdict).
        asked_all = sorted(self.run_issues(["bible-verify-all", "bible-needs-revision"], state="closed"),
                           key=lambda i: i.get("closed_at") or "")
        stale = [i for i in self.run_issues(["bible-verify-all", "bible-stale-verdict"], state="closed")
                 if (i.get("created_at") or "") >= after]
        if not asked_all and len(stale) < MAX_VERIFY_ROUNDS:
            return None
        asked = [i for i in asked_all if (i.get("created_at") or "") >= after]
        rounds = len(asked) + len(stale)  # every verification without a clean, current PASS counts
        revisions = self.run_issues(["bible-revise-all"], state="all")
        open_rev = [i for i in revisions if i["state"] == "open"]
        if open_rev:
            issue = open_rev[0]
            merged = [p for p in gh.linked_prs(issue["number"]) if p.get("merged_at") and p["base"]["ref"] == self.default
                      and ((p.get("head") or {}).get("repo") or {}).get("full_name") == gh.repo and gh.is_agent_pr(p)]
            if merged:
                gh.close(issue["number"])
                return None  # revised: the loop opens the next whole verification
            if self.held(issue):
                return "revise-all: needs a person: see #%d" % issue["number"]
            state, pr = self.session(issue, self.default, analysis)
            if state == "start-error":
                self.hold_start_error(issue)
                return "revise-all: needs a person: see #%d" % issue["number"]
            if state == "no-start":
                self.fail_or_retry(issue, None, "no pull request after assignment")
                return "revise-all: session starting"
            if pr and state == "running":
                return "revise-all: running (pull request #%d)" % pr["number"]
            if pr and state == "finished":
                unfinished = self.continue_if_unfinished(issue, pr, "bible-revise-all", analysis)
                if unfinished:
                    return unfinished
                bad = [f for f in gh.pr_files(pr["number"]) if not f.startswith(analysis + "/")
                       or os.path.basename(f).startswith("verification-")]
                if bad:
                    retried = self.fail_or_retry(issue, pr, "files a revision may not write (only %s/, never verification-*): %s"
                                                 % (analysis, shown_files(bad)))
                    return "revise-all: session starting" if retried else "revise-all: needs a person: see #%d" % issue["number"]
            return "revise-all: %s" % ("review and merge pull request #%d" % pr["number"] if pr else state)
        last_asked = asked_all[-1].get("closed_at") if asked_all else ""
        newest_stale = max([i.get("closed_at") or "" for i in stale] + [""])
        corrections_applied = bool(asked_all) and any((i.get("closed_at") or "") > (last_asked or "")
                                                      and i.get("state_reason") == "completed" for i in revisions)
        if rounds >= MAX_VERIFY_ROUNDS and (not asked_all or corrections_applied or newest_stale > (last_asked or "")):
            pass  # rounds used up: a person decides (below)
        elif not asked_all or corrections_applied or newest_stale > (last_asked or ""):
            return None  # nothing to correct now: the loop opens the next whole verification
        if rounds >= MAX_VERIFY_ROUNDS:
            hold = gh.create_issue("Codebase analysis - the whole analysis needs a person",
                                   "Tracker: #%d\n\n%d whole verifications without a clean, current PASS. Read %s/verification-report.md "
                                   "on %s, then remove the label `bible-needs-human` from this issue for new rounds."
                                   % (tracker["number"], rounds, analysis, self.default),
                                   ["bible-hold", "bible-needs-human", "bible-whole", self.run_label])
            return "verify-all: needs a person: see #%d" % hold["number"]
        body = ("Tracker: #%d\nBase branch: %s\nAttempt: 1\n\nUse the analyzing-a-codebase skill (in %s) in revision mode "
                "(references/revision.md) on the whole analysis in %s/: apply every correction in %s/verification-report.md. "
                "Start with\n  python3 -I %s/analyzing-a-codebase/scripts/next.py --repo . --analysis %s --depth %s --new-session\n"
                "and do exactly what it prints (when the code changed since the baseline it prints NEXT DELTA first), until it "
                "prints DONE, then finish with status.py --write. Do not edit the verification report."
                % (tracker["number"], self.default, self.skills, analysis, analysis, self.skills, analysis,
                   self.settings.get("depth", "deep")))
        gh.create_issue("Codebase analysis - revise the whole analysis", body, ["bible-revise-all", self.run_label],
                        assignment(gh, self.default, self.settings.get("model")))
        return "revise-all session assigned"

    def continue_if_unfinished(self, issue, pr, kind, analysis):
        """A session that ended before its work was done (seen on github.com, 24 Nov 2026: the assembly stopped at
        Copilot's session limit after 52 minutes). Done means this pull request wrote the end marker: the assembly's
        status.json (status.py --write, the last step of the Finish order), the whole verification's report. Otherwise
        ask Copilot to continue on the same pull request, at most MAX_CONTINUE times since a person last released the
        session, then a person. Only the queue's own marked comments count (anyone can post the marker text); a request
        Copilot has not picked up after NO_PR_AFTER counts as used. None when the work is done."""
        gh = self.gh
        marker = "%s/verification-report.md" % analysis if kind == "bible-verify-all" else "%s/status.json" % analysis
        if marker in gh.pr_files(pr["number"]):
            return None
        me = gh.me()
        released = max([e.get("created_at") or "" for e in gh.timeline(issue["number"]) if e.get("event") == "unlabeled"
                        and (e.get("label") or {}).get("name") == "bible-needs-human"] + [""])
        events = gh.timeline(pr["number"])
        work = [(e.get("event"), e.get("created_at") or "") for e in events if e.get("event") in WORK_EVENTS
                and (e.get("performed_via_github_app") or {}).get("slug") == AGENT_APP]
        finished = max([t for ev, t in work if ev != "copilot_work_started"] + [""])
        asked = sorted(e.get("created_at") or "" for e in events if e.get("event") == "commented"
                       and ((e.get("actor") or e.get("user")) or {}).get("login") == me and CONTINUE_MARK in (e.get("body") or "")
                       and (e.get("created_at") or "") > released)
        # the work since the queue's last request, or, before any request, since a person last released the hold (the
        # whole history when nobody has): a first session that fails before starting is held without a continuation
        since = asked[-1] if asked else released
        after = [ev for ev, t in sorted(work, key=lambda w: w[1]) if t > since]
        if after and after[-1] == "copilot_work_finished_failure" and "copilot_work_started" not in after:
            # Copilot did not run at all: holding now keeps the queue from spending the remaining continuations on it
            if "bible-needs-human" not in labels_of(issue):
                gh.label(issue["number"], "bible-needs-human")
                gh.comment(issue["number"], "Copilot's session on #%d failed before it started any work (GitHub recorded "
                           "copilot_work_finished_failure with no copilot_work_started). The usual causes are the account's "
                           "Copilot AI credits or budget for the month, or Copilot turned off for this repository; open the "
                           "session on the pull request to read GitHub's reason. Fix the cause, then remove the label "
                           "`bible-needs-human`." % pr["number"])
            return "%s: Copilot could not start: see #%d" % (kind[6:], issue["number"])
        if asked and asked[-1] > finished and age(asked[-1]) <= NO_PR_AFTER:
            return "%s: continuing (pull request #%d)" % (kind[6:], pr["number"])  # asked; Copilot has not started yet
        if len(asked) >= MAX_CONTINUE:
            if "bible-needs-human" not in labels_of(issue):
                gh.label(issue["number"], "bible-needs-human")
                gh.comment(issue["number"], "%d continuations and %s is still not written by #%d. A person must look: read the "
                           "pull request's last summary, then remove the label `bible-needs-human` to give %d more sessions."
                           % (len(asked), marker, pr["number"], MAX_CONTINUE))
            return "%s: needs a person: see #%d" % (kind[6:], issue["number"])
        gh.comment(pr["number"], "@copilot continue: run `python3 -I %s/analyzing-a-codebase/scripts/next.py --repo . --analysis %s "
                   "--depth %s --new-session` and do exactly what it prints until it prints DONE%s. Then summarise in a "
                   "comment what you finished and the last line next.py printed.\n%s"
                   % (self.skills, analysis, self.settings.get("depth", "deep"),
                      {"bible-assemble": ", and finish its Finish order (the last step is status.py --write)",
                       "bible-revise-all": ", applying every correction of verification-report.md (do not edit it), and end "
                                           "with status.py --write",
                       "bible-verify-all": ", or for the whole verification until verification-report.md is written"}[kind],
                      CONTINUE_MARK))
        return "%s: continuing, session %d (pull request #%d)" % (kind[6:], len(asked) + 2, pr["number"])

    def render(self, tracker, settings, rows):
        lines = ["Codebase analysis run, kept up to date by the Bible - queue workflow every 15 minutes. Close this issue to stop "
                 "the run. Settings are in the hidden block below.", "", "| Component | State |", "| --- | --- |"]
        lines += ["| `%s` | %s |" % (k, v) for k, v in rows.items()]
        lines += ["", "<!-- bible-state %s -->" % json.dumps(getattr(self, "state", {}) or {}, sort_keys=True),
                  "Updated %s." % now().isoformat(timespec="minutes"), "",
                  "<!-- bible-settings %s -->" % json.dumps(settings)]
        body = "\n".join(lines)
        if body.split("Updated")[0] != (tracker.get("body") or "").split("Updated")[0]:
            self.gh.set_body(tracker["number"], body)
        for k, v in rows.items():
            self.log("%-20s %s" % (k, v))

    # -- after a push: update issues for the components whose files changed
    def delta(self, changed, settings_analysis="codebase-analysis", record=True):
        gh = self.gh
        self.default = gh.default_branch()
        def last_activity(t):  # the queue's own "Updated" line, not GitHub's updated_at (which every comment moves)
            found = UPDATED.search(t.get("body") or "")
            return found.group(1) + ":00+00:00" if found else t.get("created_at")  # render() writes it in UTC
        open_run = [t for t in gh.issues(["bible-tracker"]) if age(last_activity(t)) <= ABANDONED_AFTER] if record else []
        if open_run:
            # Seen live (24 Nov 2026): an update session and the run's own revision edited the same pages at once. While
            # a run is open the change is recorded on its tracker, and replayed into update issues when the run ends.
            plain = [p for p in changed if SAFE_FILE.match(p)]
            for start in range(0, max(len(plain), 1), DEFERRED_PER_COMMENT):  # chunked: a large push fits GitHub's limit
                part = plain[start:start + DEFERRED_PER_COMMENT]
                gh.comment(open_run[0]["number"], "Code changed while this run is open: the update follows when the run ends "
                           "(%d file(s)%s).\n<!-- bible-deferred-update %s -->" % (
                               len(part), "; %d with unusual names not recorded: update those by hand" % (len(changed) - len(plain))
                               if start == 0 and len(changed) != len(plain) else "", json.dumps(part)))
            self.log("an analysis run is open (#%d): the change is recorded there and replayed when it ends"
                     % open_run[0]["number"])
            return
        catalog = json_file(gh, settings_analysis + "/components.json", self.default)
        if not catalog or not gh.file(settings_analysis + "/ledger/baseline.json", self.default):
            self.log("no assembled analysis (components.json and ledger/baseline.json) on %s: nothing to update" % self.default)
            return
        sys.path.insert(0, os.path.abspath(os.path.join(self.skills, "analyzing-a-codebase", "scripts")))
        import components  # noqa: E402  (the toolkit's own membership rules)
        rows = components.rows_of(catalog)
        # The same rule as bible-delta.yml's paths-ignore: only the analysis itself and the skills are left out; code
        # under .github/ (workflows, scripts) can belong to a component.
        touched = sorted({c for c in components.component_map([{"path": p} for p in changed
                                                                if not p.startswith((settings_analysis + "/", self.skills.rstrip("/") + "/"))], rows).values()})
        touched = [n for n in touched if NAME.match(n)]  # names from components.json: the same rule as the plan
        if len(touched) > MAX_DELTA_ISSUES:
            # One push that touches many components would start as many Copilot sessions: a person decides instead.
            if not gh.issues(["bible-delta", "bible-needs-human"]):
                gh.create_issue("Codebase analysis - a change touches %d components" % len(touched),
                                "One push changed the code of %d components (more than %d). No update session was started. "
                                "Decide which to update first; for each, open an update issue as Bible - update after code "
                                "changes does, or start a new analysis run." % (len(touched), MAX_DELTA_ISSUES),
                                ["bible-delta", "bible-needs-human"])
            self.log("%d components changed: more than %d, a person decides" % (len(touched), MAX_DELTA_ISSUES))
            return
        for name in touched:
            # File names come from a push and reach Copilot as text: only plain paths are quoted, the others counted.
            files = [p for p in changed if components.assign(p, rows)[0] == name]
            shown = [p for p in files if SAFE_FILE.match(p)]
            hidden = len(files) - len(shown)  # quoted below through the same rule as shown_files
            if gh.issues(["bible-delta", comp_label(name)]):
                self.log("update issue for %s already open: its session covers every change since the baseline when it runs" % name)
                continue
            gh.create_issue("Codebase analysis - update component %s after a code change" % name,
                            "Component: %s\nBase branch: %s\nAttempt: 1\n\nThe code of component `%s` changed: %s.\n\n"
                            "Use the tracking-codebase-changes skill (in %s) to bring %s/ in line with every change since the "
                            "analysis's baseline (not only these files), then run analyzing-a-codebase's scripts/status.py --write: "
                            "it reports STALE until the changed parts are verified in a new session on a different model "
                            "(verifying-a-codebase-analysis, scope: component %s)." % (
                                name, self.default, name, ", ".join("`%s`" % f for f in shown[:20])
                                + (" and %d file(s) with unusual characters in their names" % hidden if hidden else ""), self.skills,
                                settings_analysis, name),
                            ["bible-delta", comp_label(name)], assignment(gh, self.default, None))
            self.log("update issue for %s (%d files)" % (name, len(files)))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    start = sub.add_parser("start")
    start.add_argument("--components", default="all")
    start.add_argument("--model", default="")
    start.add_argument("--verify-model", required=True)
    start.add_argument("--concurrency", type=int, default=0)
    start.add_argument("--analysis", default="codebase-analysis")
    start.add_argument("--depth", default="deep")
    sub.add_parser("reconcile")
    d = sub.add_parser("delta")
    d.add_argument("--changed-file", required=True, help="file with one changed path per line")
    d.add_argument("--analysis", default="codebase-analysis")
    args = parser.parse_args()

    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GH_TOKEN")
    if not repo or not token:
        raise SystemExit("GITHUB_REPOSITORY and GH_TOKEN must be set (GH_TOKEN from the BIBLE_ASSIGN_TOKEN secret)")
    gh = GitHub(repo, token)
    queue = Queue(gh)
    try:
        if args.cmd == "start":
            if not args.verify_model.strip() or args.model == args.verify_model:
                raise SystemExit("--verify-model must name a model different from --model: the verification is a second opinion")
            names = [n.strip() for n in args.components.split(",") if n.strip()]
            if not names or any(n != "all" and not NAME.match(n) for n in names):
                raise SystemExit("--components: 'all', or component names separated by commas, as in components.md")
            gh.ensure_labels()
            if gh.issues(["bible-tracker"]):
                raise SystemExit("an analysis run is already open (label bible-tracker): close it first")
            settings = {"components": args.components, "model": args.model, "verify_model": args.verify_model,
                        "concurrency": args.concurrency, "analysis": args.analysis, "depth": args.depth}
            if settings_of({"body": "<!-- bible-settings %s -->" % json.dumps(settings)}) is None:
                raise SystemExit("settings refused: --analysis must be a folder name inside the repository, --depth one of %s, "
                                 "--model and --verify-model letters, digits, '.', '_', ':' or '-' only" % ", ".join(DEPTH_VALUES))
            issue = gh.create_issue("Codebase analysis run", "<!-- bible-settings %s -->" % json.dumps(settings), ["bible-tracker"])
            print("Opened the tracker issue #%d. The queue workflow (Bible - queue) assigns the planning session at its next run "
                  "(every 15 minutes); run it by hand to start now." % issue.get("number", 0))
        elif args.cmd == "reconcile":
            queue.reconcile()
        else:
            with open(args.changed_file, encoding="utf-8") as handle:
                changed = [l.strip() for l in handle if l.strip()]
            queue.delta(changed, args.analysis)
    except RuntimeError as err:
        raise SystemExit(str(err))


if __name__ == "__main__":
    main()
