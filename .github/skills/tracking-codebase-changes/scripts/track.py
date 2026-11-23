#!/usr/bin/env python3
"""Follow a codebase analysis along the branch's local Git history, and keep its changelog.

Reads the repository's own `.git` folder with gitlocal.py: never runs `git`, never connects
anywhere. Works with the analysis skill's scripts (installed next to this skill).

  python3 -I <skill>/scripts/track.py --repo . --analysis codebase-analysis                 status
  python3 -I <skill>/scripts/track.py --repo . --analysis codebase-analysis --apply         bring it in
  python3 -I <skill>/scripts/track.py --repo . --analysis codebase-analysis --apply --since <commit>
  python3 -I <skill>/scripts/track.py --repo . --analysis codebase-analysis --since auto    guess the commit
  python3 -I <skill>/scripts/track.py --repo . --analysis codebase-analysis --print-hook    hook text for a person
  python3 -I <skill>/scripts/track.py --repo . --analysis codebase-analysis --quiet         what a hook runs

Status (default) is quick: the commit the analysis matches, the commits since on this branch,
the files they changed, and files changed but not committed. Writes `ledger/track.md`.

--apply compares the code the analysis matches with the working tree, function by function,
through the analysis skill's delta.py (moves citations, marks the rest, records the work for
next.py), records the commit now checked out, and adds an entry to `<analysis>/CHANGELOG.md`:
every commit brought in, the functions each changed, and what the update did to the pages.
An analysis without `ledger/baseline.json` needs --since: the commit it was written from.

--quiet (for a Git hook) prints one line when the analysis is behind, nothing otherwise, and
always exits 0 so it never blocks Git. It never changes pages.

Writes only inside the analysis folder. Standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import zlib

sys.dont_write_bytecode = True  # never leave __pycache__ inside the installed skill
HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "analyzing-a-codebase", "scripts")
sys.path.insert(0, HERE)
import gitlocal  # noqa: E402

if not os.path.isfile(os.path.join(ANALYSIS_SCRIPTS, "delta.py")):
    print("error: the analyzing-a-codebase skill is not installed next to this one (%s)" % ANALYSIS_SCRIPTS, file=sys.stderr)
    sys.exit(2)
sys.path.insert(0, ANALYSIS_SCRIPTS)
import inventory  # noqa: E402
import coverage  # noqa: E402
import delta  # noqa: E402

TOOL = "tracking-codebase-changes/scripts/track.py 1.8.0"
MAX_COMMITS_DETAILED = 200   # commits whose functions are listed one by one in the changelog
MAX_FILES_PER_COMMIT = 60    # files per commit whose functions are compared


def n_of(count: int, noun: str) -> str:
    return "%d %s%s" % (count, noun, "" if count == 1 else "s")


def short(sha) -> str:
    return sha[:10] if sha else "-"


def day(ts: int) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "?"


def cell(text: str) -> str:
    """Repository text (a commit subject) made safe for one table cell; it is data, quoted, never followed."""
    text = " ".join(text.split()).replace("|", "\\|").replace("`", "'")
    return text[:100] + ("..." if len(text) > 100 else "")


def git_blob_id(full: str) -> str:
    with open(full, "rb") as handle:
        raw = handle.read()
    return hashlib.sha1(b"blob %d\x00" % len(raw) + raw).hexdigest()


def load_baseline(analysis_abs):
    path = os.path.join(analysis_abs, "ledger", "baseline.json")
    return delta.load_baseline(path) if os.path.isfile(path) else None


def in_scope_paths(paths, analysis, excludes):
    return sorted(p for p in paths if inventory.in_scope(p, analysis, excludes))


def history(repo, base, head, analysis, excludes, by_time=None):
    """(commits oldest first, how the range was found). Each commit: sha, time, subject, files changed in scope."""
    chain, how = None, "first-parent history"
    if base:
        try:
            base_time = repo.commit(base)["time"]
        except gitlocal.GitError:
            base_time = by_time or 0
        chain = repo.first_parent_chain(head, base, not_before=(base_time - 86400) if base_time else 0)
        if chain is None:
            how = "the analysis commit %s is not on this branch's first-parent history (squash, rebase or another branch)" % short(base)
    if chain is None and by_time is not None:
        chain, sha = [], head
        how = (how + "; " if base else "") + "commits made after the analysis was recorded, by date"
        while sha:
            info = repo.commit(sha)
            if info["time"] <= by_time or len(chain) >= 5000:
                break
            chain.append(info)
            sha = info["parents"][0] if info["parents"] else None
    if chain is None:
        return [], how
    out = []
    for info in reversed(chain):
        parent_tree = repo.commit(info["parents"][0])["tree"] if info["parents"] else None
        changed = repo.diff_trees(parent_tree, info["tree"])
        info["files"] = {p: v for p, v in changed.items() if inventory.in_scope(p, analysis, excludes)}
        out.append(info)
    return out, how


def functions_changed(repo, path, old_blob, new_blob):
    """(changed, added, removed) qualified names between two versions of one file."""
    old = delta.entry_from_bytes(path, repo.blob(old_blob)) if old_blob else {"symbols": []}
    new = delta.entry_from_bytes(path, repo.blob(new_blob)) if new_blob else {"symbols": []}
    pairs, added, removed = delta.pair_symbols(old.get("symbols", []), new.get("symbols", []))
    return ([b["qualname"] for a, b in pairs if a["stamp"] != b["stamp"] and b["kind"] != "class"],
            [s["qualname"] for s in added if s["kind"] != "class"],
            [s["qualname"] for s in removed if s["kind"] != "class"])


def version_hashes(repo, blob):
    """Line fingerprints of one version of a file, read from the object store; None when Git does not have it."""
    try:
        text = inventory.decode(repo.blob(blob))
    except (gitlocal.GitError, zlib.error):
        return None
    return inventory.line_hashes(text) if text is not None else None


def uncommitted(repo_path, head_files, analysis, excludes):
    files, _ = inventory.scan(repo_path, analysis, excludes)
    now = {f["path"] for f in files}
    out = []
    for path in sorted(now | {p for p in head_files if inventory.in_scope(p, analysis, excludes)}):
        full = os.path.join(repo_path, path)
        if path not in now:
            if path in head_files:
                out.append((path, "deleted"))
        elif path not in head_files:
            out.append((path, "new"))
        else:
            try:
                if git_blob_id(full) != head_files[path]:
                    out.append((path, "modified"))
            except OSError:
                pass
    return out


def status(args, repo, analysis_abs, baseline, head, branch):
    base = (baseline or {}).get("commit")
    excludes = (baseline or {}).get("excludes", args.exclude)
    recorded = None
    if baseline and baseline.get("recorded"):
        recorded = datetime.datetime.fromisoformat(baseline["recorded"]).timestamp()
    commits, how = history(repo, base, head, args.analysis, excludes, recorded) if (base or recorded) else ([], "no recorded commit")
    files = sorted({p for c in commits for p in c["files"]})
    if base and base != head and "not on this branch" in how:
        # The analysis commit is elsewhere (a squashed or rebased branch): the two trees say exactly what differs.
        try:
            files = in_scope_paths(repo.diff_trees(repo.commit(base)["tree"], repo.commit(head)["tree"]), args.analysis, excludes)
        except gitlocal.GitError:
            how += "; that commit is not in this repository"
    return {"base": base, "head": head, "branch": branch, "commits": commits, "files": files, "how": how}


def write_status(repo_path, analysis_abs, st, local_changes, baseline, guess, drift=None):
    out = ["# Where the analysis stands", "",
           "Written by `track.py` on %s from the local Git history (no Git command, no network)." % delta.now_iso(), "",
           "| | |", "| --- | --- |",
           "| Branch | %s |" % (st["branch"] or "(detached)"),
           "| Checked out | `%s` |" % short(st["head"]),
           "| Analysis matches | %s |" % ("`%s`" % short(st["base"]) if st["base"] else ("recorded %s, commit unknown" % baseline["recorded"] if baseline else "no baseline")),
           "| Commits since | %d (%s) |" % (len(st["commits"]), st["how"]),
           "| Files changed in those commits | %d |" % len(st["files"]),
           "| Files changed and not committed | %d |" % len(local_changes)]
    if drift is not None:
        out.append("| Analysed files that differ from what the analysis describes | %d |" % drift)
    out.append("")
    if guess:
        out += ["Guess for the commit the analysis was written from: `%s` %s (%s). Confirm it before using `--since`." % (short(guess["sha"]), day(guess["time"]), cell(guess["subject"])), ""]
    if st["commits"]:
        out += ["## Commits since the analysis", "", "| Commit | Date | Subject | Files |", "| --- | --- | --- | --- |"]
        out += ["| `%s` | %s | %s | %d |" % (short(c["sha"]), day(c["time"]), cell(c["subject"]), len(c["files"])) for c in reversed(st["commits"])]
        out.append("")
    if local_changes:
        out += ["## Not committed", ""] + ["- `%s` (%s)" % pc for pc in local_changes] + [""]
    delta.write(repo_path, os.path.join(analysis_abs, "ledger", "track.md"), "\n".join(out) + "\n")


def guess_base(repo, head, analysis_abs):
    """The newest commit on this branch made before the analysis inventory was first taken."""
    path = os.path.join(analysis_abs, "ledger", "inventory.json")
    try:
        with open(path, encoding="utf-8") as handle:
            when = datetime.datetime.fromisoformat(json.load(handle)["generated"]).timestamp()
    except (OSError, ValueError, KeyError):
        return None
    sha = head
    while sha:
        info = repo.commit(sha)
        if info["time"] <= when:
            return info
        sha = info["parents"][0] if info["parents"] else None
    return None


def changelog_entry(repo, st, local_changes, result, label, analysis, excludes):
    diff, stats, items = result["diff"], result["stats"], result["items"]
    commits = st["commits"]
    detail = commits[-MAX_COMMITS_DETAILED:]
    rows, totals = [], {"changed": set(), "added": set(), "removed": set()}
    for c in reversed(detail):
        parts = []
        gone = {v[0]: p for p, v in c["files"].items() if v[1] is None}
        moves = {p: gone[v[1]] for p, v in c["files"].items() if v[0] is None and v[1] in gone}
        for path in sorted(c["files"])[:MAX_FILES_PER_COMMIT]:
            old_blob, new_blob = c["files"][path]
            if path in moves:
                parts.append("`%s` renamed to `%s`" % (moves[path], path))
                continue
            if new_blob is None and path in moves.values():
                continue
            try:
                changed, added, removed = functions_changed(repo, path, old_blob, new_blob)
            except (gitlocal.GitError, zlib.error):
                changed, added, removed = [], [], []
            for key, names in (("changed", changed), ("added", added), ("removed", removed)):
                totals[key] |= {(path, n) for n in names}
            what = "; ".join("%s %s" % (", ".join("`%s`" % n for n in names[:6]) + (" ..." if len(names) > 6 else ""), key)
                             for key, names in (("changed", changed), ("added", added), ("removed", removed)) if names)
            state = "added" if not old_blob else ("removed" if not new_blob else "")
            parts.append("`%s`%s%s" % (path, " (%s)" % state if state else "", ": " + what if what else ""))
        if len(c["files"]) > MAX_FILES_PER_COMMIT:
            parts.append("and %d more files" % (len(c["files"]) - MAX_FILES_PER_COMMIT))
        rows.append("| `%s` | %s | %s | %s |" % (short(c["sha"]), day(c["time"]), cell(c["subject"]), "<br>".join(parts) or "outside the analysed files"))
    cards = sum(1 for i in items if i["kind"] in ("card", "endpoint"))
    removals = sum(1 for i in items if i["kind"].startswith("remove"))
    out = ["## %s · %s · `%s` → `%s`%s" % (delta.now_iso().replace("T", " ")[:16], st["branch"] or "(detached)",
                                           short(st["base"]) if st["base"] else "?", short(st["head"]), " · " + label if label else ""), "",
           "%s, %s changed in the analysed code; functions: %d changed, %d added, %d removed (%s)%s." % (
               n_of(len(commits), "commit"), n_of(len(st["files"]), "file"), len(totals["changed"]), len(totals["added"]), len(totals["removed"]), st["how"],
               ". Not committed: %d files" % len(local_changes) if local_changes else ""), ""]
    if rows:
        out += ["| Commit | Date | Subject | Code changed |", "| --- | --- | --- | --- |"] + rows
        if len(commits) > len(detail):
            out.append("| | | %d older commits | listed in `ledger/track.md` |" % (len(commits) - len(detail)))
        out.append("")
    if local_changes:
        out += ["Not committed: " + ", ".join("`%s` (%s)" % pc for pc in local_changes[:20]) + (" ..." if len(local_changes) > 20 else ""), ""]
    out += ["Analysis: %d citations moved to new lines, %d marked for a recheck, %d renamed paths; %d cards or endpoints to write or rewrite, %d removals. Details in `ledger/delta.md`." % (
        stats["moved"], stats["marked"], stats["renamed"], cards, removals), ""]
    return "\n".join(out)


def add_to_changelog(repo_path, analysis_abs, entry):
    path = os.path.join(analysis_abs, "CHANGELOG.md")
    head = ("# Changelog of the analysis\n\nNewest first. One entry per update: the commits brought in, the code each changed, "
            "and what the update did to the pages. Written by `tracking-codebase-changes`; commit subjects are quoted from the "
            "repository as written.\n")
    text = open(path, encoding="utf-8").read() if os.path.isfile(path) else head
    marker = text.find("\n## ")
    text = (text.rstrip("\n") + "\n\n" + entry) if marker < 0 else (text[:marker + 1] + entry + "\n" + text[marker + 1:])
    delta.write(repo_path, path, text.rstrip("\n") + "\n")


def print_hook(repo, args):
    hooks = os.path.join(repo.common_dir, "hooks")
    config = os.path.join(repo.common_dir, "config")
    if os.path.isfile(config):
        for line in open(config, encoding="utf-8", errors="replace"):
            if line.strip().lower().startswith("hookspath"):
                hooks = line.split("=", 1)[1].strip() + "   (core.hooksPath is set)"
    command = 'python3 -I "%s" --repo "$PWD" --analysis "%s" --quiet || true' % (os.path.join(HERE, "track.py"), args.analysis)
    print("Hook folder: %s" % hooks)
    print("A person adds these files (or appends the last line to an existing hook) and makes them executable.")
    print("They only report; they never change the analysis and never block Git.\n")
    for name, guard in (("post-merge", ""), ("post-rewrite", ""), ("post-checkout", '[ "$3" = "1" ] || exit 0  # branch switches only\n')):
        print("----- %s -----" % name)
        print("#!/bin/sh\n# tracking-codebase-changes: report what changed since the codebase analysis\n%s%s\n" % (guard, command))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--depth", choices=sorted(coverage.DEPTHS), default="deep")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--label", default="", help="a name for this update, as the person gives it")
    parser.add_argument("--since", default=None, help="commit the analysis was written from (id, branch, tag, HEAD~N), or auto to guess")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--quiet", action="store_true", help="for a Git hook: one line when behind, always exit 0")
    mode.add_argument("--print-hook", action="store_true")
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo)
    args.analysis = coverage.strip_dot(args.analysis.replace("\\", "/")).strip("/")
    if os.path.isabs(args.analysis) or ".." in args.analysis.split("/") or args.analysis in ("", "."):
        inventory.fail("--analysis must be a folder inside the repository, given relative to it")
    args.exclude = [coverage.strip_dot(e.replace("\\", "/")).strip("/") for e in args.exclude]
    analysis_abs = os.path.join(repo_path, args.analysis)
    try:
        repo = gitlocal.Repo(repo_path)
        if args.print_hook:
            return print_hook(repo, args)
        if not os.path.isdir(analysis_abs):
            if args.quiet:
                return
            inventory.fail("analysis folder not found: " + args.analysis)
        head, branch = repo.resolve("HEAD"), repo.branch()
        baseline = load_baseline(analysis_abs)
        if args.quiet:
            if baseline and baseline.get("commit") != head:
                st = status(args, repo, analysis_abs, baseline, head, branch)
                if not st["files"]:
                    return  # only the analysis itself, or files outside it, changed
                write_status(repo_path, analysis_abs, st, [], baseline, None)
                print("%s: %s, %s changed since the analysis (%s). Ask your assistant to update the codebase analysis."
                      % (args.analysis, n_of(len(st["commits"]), "commit"), n_of(len(st["files"]), "analysed file"),
                         short(st["base"]) if st["base"] else "date"))
            return

        since = None
        if args.since == "auto":
            guess = guess_base(repo, head, analysis_abs)
            if not guess:
                inventory.fail("cannot guess: no ledger/inventory.json date, or no commit before it")
            if not args.apply:
                print("guess: the analysis was written from %s %s (%s)" % (short(guess["sha"]), day(guess["time"]), guess["subject"][:80]))
                print("confirm with the person, then: --apply --since %s" % guess["sha"])
                return
            since = guess["sha"]
        elif args.since:
            since = repo.resolve(args.since)

        if baseline is None and since:
            baseline = {"commit": since, "excludes": args.exclude, "pending": [], "label": "", "recorded": delta.now_iso()}
        elif baseline is not None and since and args.apply:
            baseline["commit"] = since  # the person says which commit the analysis matches
        head_files = repo.tree_files(repo.commit(head)["tree"])
        excludes = (baseline or {}).get("excludes", args.exclude)
        local_changes = uncommitted(repo_path, head_files, args.analysis, excludes)

        if not args.apply:
            st = status(args, repo, analysis_abs, baseline, head, branch)
            guess = None if baseline else guess_base(repo, head, analysis_abs)
            drift = None
            if baseline and baseline.get("files"):
                now = delta.snapshot(repo_path, args.analysis, excludes)
                d = delta.compare(baseline["files"], now)
                behind = delta.stale_records(coverage.load_docs(analysis_abs), now)
                drift = len(d["changed"]) + len(d["added"]) + len(d["removed"]) + len(d["renamed"])
                if behind:
                    print("pages whose citations count lines in another version of the code: %d" % len({p for p, _ in behind}))
                    drift += len({p for p, _ in behind})
            write_status(repo_path, analysis_abs, st, local_changes, baseline, guess, drift)
            print("branch %s at %s; analysis matches %s" % (branch or "(detached)", short(head),
                                                             short(st["base"]) if st["base"] else ("recorded %s" % baseline["recorded"] if baseline else "nothing recorded")))
            print("commits since: %d (%s); analysed files changed in them: %d; not committed: %d"
                  % (len(st["commits"]), st["how"], len(st["files"]), len(local_changes)))
            if drift is not None:
                print("analysed files and pages that differ from what the analysis describes: %d" % drift)
            if guess:
                print("no baseline: the analysis may have been written from %s %s (%s); confirm, then --apply --since <that commit>"
                      % (short(guess["sha"]), day(guess["time"]), guess["subject"][:80]))
            print("wrote " + os.path.relpath(os.path.join(analysis_abs, "ledger", "track.md"), repo_path))
            if drift or (drift is None and (st["commits"] or st["files"] or local_changes)):
                print("next: run again with --apply")
            elif drift == 0:
                print("the analysis matches the code on disk")
            return

        if baseline is None:
            inventory.fail("no ledger/baseline.json: say which commit the analysis was written from with --since <commit> "
                           "(or --since auto to see a guess first)")
        # The code the analysis matches: the recorded fingerprint, or the files as they were in that commit.
        if baseline.get("files") and not since:
            old = baseline["files"]
        else:
            tree = repo.tree_files(repo.commit(baseline["commit"])["tree"])
            old = {p: delta.entry_from_bytes(p, repo.blob(b)) for p, b in tree.items() if inventory.in_scope(p, args.analysis, excludes)}
        st = status(args, repo, analysis_abs, baseline, head, branch)
        now = delta.snapshot(repo_path, args.analysis, excludes)
        result = delta.run_delta(repo_path, args.analysis, baseline, old, now, coverage.DEPTHS[args.depth], True,
                                 args.label or branch or "", extra={"commit": head, "branch": branch, "tool": TOOL},
                                 hashes_of=lambda blob: version_hashes(repo, blob))
        add_to_changelog(repo_path, analysis_abs, changelog_entry(repo, st, local_changes, result, args.label, args.analysis, excludes))
        write_status(repo_path, analysis_abs, status(args, repo, analysis_abs, delta.load_baseline(
            os.path.join(analysis_abs, "ledger", "baseline.json")), head, branch), local_changes, None, None)
        delta.print_summary(repo_path, args.analysis, result, True, args.depth)
        print("wrote " + os.path.relpath(os.path.join(analysis_abs, "CHANGELOG.md"), repo_path))
    except (gitlocal.GitError, zlib.error) as exc:
        if args.quiet:
            return
        inventory.fail("cannot read the Git history: %s. Without it, use analyzing-a-codebase's delta.py (fingerprints only)" % exc)


if __name__ == "__main__":
    main()
