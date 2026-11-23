#!/usr/bin/env python3
"""The work loop: print the one next job of the analysis, from the code and the pages on disk.

Each run scans the repository and the analysis folder fresh, works out which
packet (a source file, or a slice of a large one) is not yet documented to the
chosen depth, and prints exactly what to do next: the file and lines to read,
the page to write, every function to card with its branch lines and calls, and
every route declared there. When every packet is done it names the next pass,
and finally runs the gate. Nothing is remembered between runs except the
session counter, so the answer is always what the files show.

  python3 -I <skill>/scripts/next.py --repo . --analysis codebase-analysis [--depth deep] [--new-session]
  python3 -I <skill>/scripts/next.py --repo . --analysis codebase-analysis --component NAME [--new-session]
  python3 -I <skill>/scripts/next.py --repo . --analysis codebase-analysis --board

Prints one of:
  NEXT DELTA ...         the code changed since the analysis matched it: do the job, then run next.py again
  NEXT PACKET ...        do it, then run next.py again
  NEXT PASS ...          do it, then run next.py again
  NEW CHAT               stop; tell the user to continue in a new chat
  STOP: no progress      the same job came back with nothing written: stop and tell the user why
  DONE                   the coverage gate passes; finish as SKILL.md says
  NEXT REVISION NAME ... (--component) the component's verification asked for corrections not applied yet: apply them
  COMPONENT DONE NAME    (--component) the component's pages are written and its check passes: stop
  WAITING FOR ANSWERS    (--component) questions.md has open questions: stop and ask the person

Without --component: writes `<analysis>/ledger/next.md` (the same text) and `<analysis>/ledger/session.json`.
With --component (after discover.py wrote components.json): only that component's packets, its page and
its check; writes next.md, session.json and status.json under `<analysis>/ledger/components/NAME/`, so
components can run in parallel on separate branches. --board prints where every component stands.
Read-only on the repository. Standard library only; never imports or runs repository code.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ inside the installed skill
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory  # noqa: E402
import coverage  # noqa: E402
import delta  # noqa: E402
import components  # noqa: E402
import status  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ABS = None  # set by main(); commands are printed relative to it


def shown(name):
    """A script's path as printed and saved in ledger/next.md: relative to the repository when the skill sits
    inside it, under ~ when it sits in the home folder, so no machine-specific path lands in a committed file."""
    path = os.path.join(HERE, name)
    for base, prefix in ((REPO_ABS, ""), (os.path.expanduser("~"), "~/")):
        if base and os.path.commonpath([path, base]) == base:
            return prefix + os.path.relpath(path, base)
    return path
PACKET_LINES = 400
PACKET_FUNCTIONS = 25
NOT_CARDED = ("class", "table", "view", "paragraph", "imports")
STOP_AFTER_REPEATS = 2  # the same job printed this many more times, nothing written in between: STOP
JOB_HEADS = ("NEXT PACKET", "NEXT PASS", "NEXT DELTA")
CLOSING_HEADS = ("NEW CHAT", "DONE", "COMPONENT DONE", "WAITING FOR ANSWERS")
OPEN_QUESTION = re.compile(r"^\s*[-*]\s+\[ \]\s+\S", re.M)
# One chat's session, shared by main() and finish(): path, state, max_steps, note; and, in component
# mode, where next.md and status.json go and the packet counts for status.json.
SESSION = {"path": None, "state": None, "max_steps": 8, "note": [], "next_path": None, "status_path": None, "status": None}


def norm(path: str) -> str:
    return coverage.strip_dot(path.replace("\\", "/").strip().strip("`"))


def pages_by_source(docs):
    page_for = {}
    for doc, text in docs.items():
        declared = coverage.front_matter(text).get("source", [])
        for path in ([declared] if isinstance(declared, str) else declared):
            if path:
                page_for.setdefault(norm(path.split(":")[0]), []).append(doc)
        for decl in coverage.SOURCE_DECL.findall(text):
            for token in coverage.BACKTICK.findall(decl):
                page_for.setdefault(norm(token.split(":")[0]), []).append(doc)
    return page_for


def packets_for(f):
    """Split one file into packets at symbol boundaries: about 400 lines or 25 functions each.
    A class longer than one packet is split between its methods."""
    units = []
    for top in sorted((x for x in f["symbols"] if x["kind"] != "imports" and "." not in x["qualname"]), key=lambda x: x["start"]):
        members = [m for m in f["symbols"] if m["qualname"].startswith(top["qualname"] + ".")]
        if top["size"] > PACKET_LINES and members:
            units += [(m["start"], m["end"], 1) for m in sorted(members, key=lambda m: m["start"]) if m["qualname"].count(".") == 1]
        else:
            units.append((top["start"], top["end"], 1 + len(members)))
    if not units:
        return [(1, max(f["lines"], 1))]
    starts, first, count = [], None, 0
    for a, b, n in units:
        if first is not None and (b - first + 1 > PACKET_LINES or count + n > PACKET_FUNCTIONS):
            starts.append(first)
            first, count = None, 0
        if first is None:
            first = a
        count += n
    starts.append(first)
    starts[0] = 1
    return [(starts[i], (starts[i + 1] - 1) if i + 1 < len(starts) else max(f["lines"], starts[i])) for i in range(len(starts))]


def component_of(path: str) -> str:
    parts = path.split("/")
    return parts[0] if len(parts) > 1 else "root"


def module_page(path: str, component: str, siblings=()) -> str:
    """lld/<component>/<file name>.md; when another file of the component has the same name, the page is
    named from the path instead (app/a/index.py -> lld/<component>/app-a-index.md), so pages never collide."""
    stem = os.path.splitext(os.path.basename(path))[0]
    if sum(1 for s in siblings if os.path.splitext(os.path.basename(s))[0] == stem) > 1:
        stem = path.replace("/", "__")  # the whole path, extension kept: src/Foo.h and src/Foo.cpp stay apart
    return "lld/%s/%s.md" % (component, stem)


def packet_gaps(f, start, end, docs, pages, rules, skips, all_sections, stamps=None):
    """What is still missing for the symbols and routes declared in lines start..end."""
    gaps = []
    if not pages and not coverage.skipped(skips, f["path"], "*"):
        gaps.append(("page", None, "no page declares this file"))
    page_text = "\n".join(docs[p] for p in pages)
    page_sections = [sec for p in pages for sec in coverage.sections(docs[p])]
    for p in pages:
        if rules["frontmatter"] and not (coverage.front_matter(docs[p]).get("id") and coverage.front_matter(docs[p]).get("kind")):
            gaps.append(("frontmatter", None, "page %s has no front matter" % p))
    symbols = [s for s in f["symbols"] if s["kind"] != "imports"]
    test_file = coverage.is_test_file(f["path"])
    base = os.path.basename(f["path"])
    for s in symbols:
        if not (start <= s["start"] <= end):
            continue
        if coverage.skipped(skips, f["path"], s["qualname"]) or coverage.skipped(skips, f["path"], s["name"]):
            continue
        if rules["card_lines"] is None:
            continue
        if not (page_text and coverage.mentions(page_text, s["name"])):
            gaps.append(("symbol", s, "not named on the page"))
            continue
        if s["kind"] in NOT_CARDED or s["size"] < rules["card_lines"] or test_file:
            continue
        body = coverage.find_card(page_sections, s, symbols, base)
        if body is None:
            gaps.append(("card", s, "no card (heading naming it, Steps, a `%s:<lines>` citation)" % base))
            continue
        written_from = coverage.STAMP.search(body)
        if written_from and stamps is not None and written_from.group(1) != inventory.stamp(stamps, s["start"], s["end"]):
            gaps.append(("card", s, "the code changed since the card was written: rewrite it and replace its stamp"))
            continue
        if rules["pseudo"] and not coverage.pseudo_ok(body, s["size"]):
            gaps.append(("card", s, "card has no pseudo-code block"))
        lines = sorted({b["line"] for b in s.get("branches", [])})
        if rules["branches"] and lines:
            ranges = []
            for row in coverage.branch_table_rows(body):
                for cited, a, b in coverage.CITE_IN_LINE.findall(row):
                    if cited == base and int(b or a) - int(a) <= 3:
                        ranges.append((int(a), int(b or a)))
            missing = [n for n in lines if not any(a <= n <= b for a, b in ranges)]
            if missing:
                gaps.append(("card", s, "branch lines not in its Branches and errors table: %s" % ", ".join(map(str, missing))))
    for r in f["routes"]:
        if not (start <= r["line"] <= end) or r["methods"] == ["UI"] or coverage.skipped(skips, f["path"], r["path"]):
            continue
        path = coverage.norm_route(r["path"])
        pattern = re.compile(r"(?<![\w/{<:-])" + re.escape(path) + r"/?(?![\w/{<-])")
        wanted = [m for m in r["methods"] if m != "ANY"]
        ok = False
        for _doc, title, body, level in all_sections:
            if level > 1 and pattern.search(title) and all(re.search(r"\b%s\b" % m, title) for m in wanted):
                ok = re.search(r"\brequest\b", body, re.I) and re.search(r"\bresponses?\b", body, re.I) and \
                    (not rules["sequence"] or "sequenceDiagram" in body)
                break
        if not ok:
            gaps.append(("route", r, "no endpoint card in lld/api/ (heading with method and path, Request, Response%s)"
                         % (", sequence diagram" if rules["sequence"] else "")))
    return gaps


def describe_symbol(s, hashes=None):
    branches = ", ".join(str(b["line"]) for b in s.get("branches", [])) or "none"
    every = s.get("calls", [])
    calls = (", ".join("`%s`" % c["name"] for c in every[:20]) + (" and %d more (ledger/symbol-checklist.md)" % (len(every) - 20) if len(every) > 20 else "")) or "none"
    stamp = "; stamp `<!-- code: %s -->`" % inventory.stamp(hashes, s["start"], s["end"]) if hashes else ""
    return "`%s` (%s, lines %d-%d) - branch lines to cite: %s; calls: %s%s" % (s["qualname"], s["kind"], s["start"], s["end"], branches, calls, stamp)


def file_hashes(repo, path):
    text = inventory.read_text(os.path.join(repo, path))
    return inventory.line_hashes(text) if text is not None else None


def delta_job(repo, analysis, excludes, files, depth):
    """The next job of a delta update, or None when there is none."""
    work = delta.pending_work(repo, analysis, excludes)
    if work is None:
        return None
    here = shown("delta.py")
    if work["drift"] or work["behind_pages"]:
        why = ("the code changed since the analysis last matched it" if work["drift"] else
               "%d pages count lines in another version of the code (after a merge or a page restored from Git): %s"
               % (len({d for d, _ in work["behind_pages"]}), ", ".join(sorted({d for d, _ in work["behind_pages"]})[:5])))
        return ["NEXT DELTA: " + why,
                "Run: python3 -I %s --repo . --analysis %s --depth %s --apply" % (here, analysis, depth),
                "(or tracking-codebase-changes' track.py --apply when the repository has a .git folder)",
                "It moves each citation from the version its page or card was written against, marks the rest for a recheck and records the work.",
                "Then run next.py again: it hands that work out file by file."]
    delta.record_new_pages(repo, os.path.join(repo, analysis), work["docs"], work["now"])
    by_path = {f["path"]: f for f in files}
    if work["items"]:
        path = work["items"][0]["path"]
        group = [i for i in work["items"] if i["path"] == path]
        pages = sorted(work["page_for"].get(path, set()))
        f = by_path.get(path)
        hashes = file_hashes(repo, path) if f else None
        out = ["NEXT DELTA %s (%d items open in %d files)" % (path, len(work["items"]), len({i["path"] for i in work["items"]})),
               "Pages:     %s" % (", ".join("%s/%s" % (analysis, p) for p in pages) or "none declares this file"),
               "Templates: references/output-templates.md - Function card%s" % (", lld/api/<group>.md" if any(i["kind"] in ("endpoint", "remove-route") for i in group) else ""),
               "", "To do (%d):" % len(group)]
        for item in group:
            kind = item["kind"]
            if kind == "card" and f:
                s = next(x for x in f["symbols"] if x["qualname"] == item["qualname"])
                out.append("  - %s the card %s (%s): read the lines, write every part from the code, put the stamp on its Source line"
                           % ("write" if item["why"] == "added" else "rewrite", describe_symbol(s, hashes), item["why"]))
            elif kind == "endpoint" and f:
                live = [r for r in f["routes"] if delta.route_key(r) == delta.route_key({"methods": item["methods"], "path": item["route"]})]
                handler = [x for x in f["symbols"] if live and x["qualname"] == live[0]["handler"]]
                span = (handler[0]["start"], handler[0]["end"]) if handler else ((live[0]["line"],) * 2 if live else (1, 1))
                out.append("  - endpoint %s %s -> `%s` (%s): rewrite or write its card in lld/api/, stamp `<!-- code: %s -->`"
                           % ("/".join(item["methods"]), item["route"], item.get("handler", ""), item["why"], inventory.stamp(hashes or [], *span)))
            elif kind == "remove-card":
                out.append("  - `%s` is gone from the code: delete its card, its call-graph edges and every row that names it" % item["qualname"])
            elif kind == "remove-route":
                out.append("  - endpoint %s %s is gone: delete its card and its row in lld/api/README.md" % ("/".join(item["methods"]), item["route"]))
            elif kind == "remove-file":
                out.append("  - the file is gone: delete its page (or its `Source file:` line), its rows in the component README and the indexes")
        out += ["", "Every citation with a `<!-- recheck ... -->` marker on these pages: open the code, fix the citation and its sentence, delete the marker.",
                "Then update the component README and the HLD pages that describe what changed, and run next.py again."]
        return out
    if work["markers"]:
        doc = work["markers"][0][0]
        rows = [m for m in work["markers"] if m[0] == doc]
        out = ["NEXT DELTA recheck %s/%s (%d citations waiting in %d pages)" % (analysis, doc, len(work["markers"]), len({m[0] for m in work["markers"]})), "",
               "Each line below cites code that changed. Open the code, correct the citation and the sentence it supports, then delete the marker:"]
        out += ["  - line %d: %s" % (n, text[:200]) for _d, n, text in rows[:40]]
        return out + ["", "Then run next.py again."]
    if work["knowledge"]:
        return ["NEXT DELTA: rebuild the knowledge base",
                "Run: python3 -I %s --repo . --analysis %s" % (shown("knowledge.py"), analysis),
                "Then update knowledge/AGENT-CONTEXT.md where the change touches it, and run next.py again."]
    return None


def load_session(path, new_session):
    """The chat's counters. `--new-session` starts fresh only when the last chat ended
    (NEW CHAT or DONE); otherwise its counts carry over, so an agent that restarts the
    skill inside the same chat cannot reset the budget and loop forever."""
    state = {}
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as handle:
                state = json.load(handle)
        except (OSError, ValueError):
            state = {}
    if not isinstance(state, dict):
        state = {}
    note = []
    if new_session:
        if state.get("closed", True):  # a file from before 1.8.1 has no "closed": treat as ended
            state = {"closed": False}
        else:
            note = ["",
                    "Note: --new-session ran before the last chat reached NEW CHAT or DONE, so its count carries over "
                    "(%d other jobs so far). In the same chat this keeps the loop bounded; in a new chat after a failure "
                    "it only means NEW CHAT comes sooner. A person can delete ledger/session.json for a full budget." % state.get("steps", 0)]
    state.setdefault("closed", False)
    return state, note


def record_job(lines):
    """Count the job, catch a job printed again with nothing written, and close the chat on NEW CHAT or DONE."""
    state = SESSION["state"]
    head = lines[0] if lines else ""
    if head.startswith(JOB_HEADS):
        digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]
        packet = head.startswith("NEXT PACKET")
        if digest == state.get("last"):
            state["repeat"] = state.get("repeat", 0) + 1
        else:
            state["last"], state["repeat"] = digest, 0
            if not packet and state.get("steps", 0) <= SESSION["max_steps"]:
                state["steps"] = state.get("steps", 0) + 1
        if not packet and state.get("steps", 0) > SESSION["max_steps"]:
            state["closed"] = True
            return ["NEW CHAT",
                    "%d jobs other than packets done in this chat (budget %d). Stop now and tell the user:" % (SESSION["max_steps"], SESSION["max_steps"]),
                    "  continue the codebase analysis in a new chat",
                    "The next chat starts with next.py --new-session; it picks up this job: " + head]
        if state["repeat"] >= STOP_AFTER_REPEATS:
            state["closed"] = True  # a new chat (--new-session) starts fresh after a STOP; this one must end
            return ["STOP: no progress",
                    "next.py printed the same job %d times in a row and nothing on disk changed:" % (state["repeat"] + 1),
                    "  " + head,
                    "Stop now. Do not start over, and do not run --new-session in this chat. Tell the user which item "
                    "could not be written and why (a failed model request, a file that cannot be read, a template that "
                    "does not fit). The next run continues from the pages on disk."]
    elif head.startswith(CLOSING_HEADS):
        state["closed"] = True
    return lines


def state_of(head: str) -> str:
    for prefix, state in (("COMPONENT DONE", "COMPONENT_DONE"), ("WAITING FOR ANSWERS", "WAITING_ANSWER"),
                          ("NEW CHAT", "NEW_CHAT"), ("STOP", "STOP")):
        if head.startswith(prefix):
            return state
    return "NEXT"


def open_questions(comp_dir: str):
    path = os.path.join(comp_dir, "questions.md")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as handle:
        return [line.strip() for line in handle if OPEN_QUESTION.match(line)]


def board(analysis: str, analysis_abs: str) -> None:
    catalog = components.load_catalog(analysis_abs)
    if catalog is None:
        print("No component catalog yet: run discover.py (after pass 2), then --board again.")
        return
    comps = catalog["components"]
    width = max([len(c["name"]) for c in comps] + [9])
    print("Components of %s (%s%d):" % (analysis, "proposed, " if catalog.get("proposed") else "", len(comps)))
    print("  %-*s  %-15s %9s  %s" % (width, "component", "state", "packets", "updated"))
    finished = 0
    for c in comps:
        status = {}
        path = os.path.join(analysis_abs, "ledger", "components", c["name"], "status.json")
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as handle:
                    status = json.load(handle)
            except (OSError, ValueError):
                status = {}
        state = status.get("state", "NOT_STARTED")
        finished += state == "COMPONENT_DONE"
        print("  %-*s  %-15s %4s/%-4s  %s" % (width, c["name"], state, status.get("packets_done", 0),
                                             status.get("packets_total", c["packets"]), status.get("updated", "-")))
    print("%d of %d components done. States come from the last next.py run on this copy of the analysis;" % (finished, len(comps)))
    print("a component analysed on another branch shows here once that branch is merged.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--depth", choices=sorted(coverage.DEPTHS), default="deep")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--priority", action="append", default=[], help="folder to do first (repeatable)")
    parser.add_argument("--new-session", action="store_true", help="start of a new chat: reset the packet budget")
    parser.add_argument("--budget", type=int, default=6, help="packets per chat before NEW CHAT (default 6)")
    parser.add_argument("--max-steps", type=int, default=8, help="other jobs (passes, delta work) per chat before NEW CHAT (default 8)")
    parser.add_argument("--component", default=None, help="work on this component only (needs components.json from discover.py)")
    parser.add_argument("--board", action="store_true", help="print where every component stands, then stop")
    args = parser.parse_args()

    global REPO_ABS
    repo = os.path.abspath(args.repo)
    REPO_ABS = repo
    analysis = norm(args.analysis)
    if os.path.isabs(args.analysis) or ".." in analysis.split("/") or analysis in ("", "."):
        inventory.fail("--analysis must be a folder inside the repository, given relative to it")
    analysis_abs = os.path.join(repo, analysis)
    if not os.path.isdir(analysis_abs):
        os.makedirs(inventory.safe_target(repo, analysis_abs), exist_ok=True)
    if args.board:
        return board(analysis, analysis_abs)
    catalog = components.load_catalog(analysis_abs)
    comp = args.component
    if comp is not None:
        if catalog is None or catalog.get("proposed"):
            sys.stdout.write("\n".join([
                "NEXT PASS: discovery (--component needs the component catalog)",
                "Run next.py without --component until pass 2 is done (the `## Components` plan in progress.md), then run:",
                "  python3 -I %s --repo . --analysis %s" % (shown("discover.py"), analysis),
                "and show its table to the user. Then run this command again."]) + "\n")
            return
        names = [c["name"] for c in catalog["components"]]
        if comp not in names:
            inventory.fail("unknown component %r; components.json has: %s" % (comp, ", ".join(names)))
        comp_dir = inventory.safe_target(repo, os.path.join(analysis_abs, "ledger", "components", comp))
        session_path = os.path.join(comp_dir, "session.json")
        SESSION.update(next_path=os.path.join(comp_dir, "next.md"), status_path=os.path.join(comp_dir, "status.json"))
    else:
        session_path = inventory.safe_target(repo, os.path.join(analysis_abs, "ledger", "session.json"))
    state, note = load_session(session_path, args.new_session)
    SESSION.update(path=session_path, state=state, max_steps=args.max_steps, note=note)
    rows = components.rows_of(catalog) if catalog and not catalog.get("proposed") else None
    rules = coverage.DEPTHS[args.depth]
    excludes = [norm(e).strip("/") for e in args.exclude]
    files, _excluded = inventory.scan(repo, analysis, excludes)
    docs = coverage.load_docs(analysis_abs)
    page_for = pages_by_source(docs)
    skips = coverage.load_skips(analysis_abs)
    all_sections = [(doc, t, b, lvl) for doc, text in docs.items() for t, lvl, b, _ in coverage.sections(text)]

    comp_of = components.component_map(files, rows) if rows else {}

    def comp_name(path):
        return comp_of.get(path) or component_of(path)

    flag = " --component %s" % comp if comp else ""
    api_page = "lld/api/%s/<group>.md" % comp if comp else ("lld/api/<component>/<group>.md" if rows else "lld/api/<group>.md")
    out = []
    if comp:
        pass  # the plan, the inventory and the catalog exist: discover.py checked them
    elif not os.path.isfile(os.path.join(analysis_abs, "ledger", "inventory.json")):
        out = ["NEXT PASS 1: inventory",
               "Run: python3 -I %s --repo . --analysis %s%s" % (shown("inventory.py"), analysis, "".join(" --exclude " + e for e in excludes)),
               "Then write ledger/coverage-ledger.md (references/passes.md, Pass 1), then run next.py again."]
    elif components.plan_section(components.read_plan_text(analysis_abs)) is None:
        comps = {}
        for f in files:
            if f["kind"] == "source" and not f["binary"] and f["lines"] > 0 and f["lang"] not in ("css", "html"):
                c = comps.setdefault(component_of(f["path"]), [0, 0, 0])
                c[0] += 1
                c[1] += len(packets_for(f))
                c[2] += len(f["routes"])
        out = ["NEXT PASS 2: components and plan",
               "Write progress.md with a '## Components' section (references/passes.md, Pass 2). Suggested split by top folder:"]
        out += ["  - %s: %d source files, %d packets, %d routes" % (c, v[0], v[1], v[2]) for c, v in sorted(comps.items(), key=lambda x: -x[1][1])]
        out += ["Total packets: %d. Split a large folder into the areas its routes, packages and services show." % sum(v[1] for v in comps.values()),
                "Then run discover.py, which checks the plan and writes the component catalog and its table:",
                "  python3 -I %s --repo . --analysis %s" % (shown("discover.py"), analysis),
                "Show its table to the user once and ask: which components (names, or all)? For one component, continue with",
                "next.py --component NAME. For all of them in this chat, run next.py again: it hands you packets in priority order."]
    if out:
        return finish(out, analysis_abs, repo)
    job = None if comp else delta_job(repo, analysis, excludes, files, args.depth)
    if job:
        return finish(job, analysis_abs, repo)

    source = [f for f in files if f["kind"] == "source" and not f["binary"] and f["lines"] > 0
              and f["lang"] not in ("css", "html") and not coverage.skipped(skips, f["path"], "*")
              and (comp is None or comp_of.get(f["path"]) == comp)]
    priority = [norm(p).strip("/") for p in args.priority]

    def order(f):
        first = 0 if any(f["path"] == p or f["path"].startswith(p + "/") for p in priority) else 1
        mine = comp_name(f["path"])
        comp_routes = -sum(len(g["routes"]) for g in source if comp_name(g["path"]) == mine)
        return (first, comp_routes, mine, 0 if f["routes"] else 1, coverage.is_test_file(f["path"]), -f["lines"], f["path"])

    source.sort(key=order)
    queue = [(f, a, b) for f in source for a, b in packets_for(f)]
    total = len(queue)
    if total == 0 and not comp:
        return finish(["STOP: nothing to analyse",
                       "The repository has no source file with content in scope (check --exclude and the folder). Tell the user."],
                      analysis_abs, repo)
    pending = None
    done = 0
    for f, a, b in queue:
        pages = sorted(set(page_for.get(f["path"], [])))
        gaps = packet_gaps(f, a, b, docs, pages, rules, skips, all_sections, file_hashes(repo, f["path"]))
        if gaps:
            if pending is None:
                pending = (f, a, b, pages, gaps)
        else:
            done += 1

    state.setdefault("start_done", done)
    in_session = max(0, done - state["start_done"])
    if not comp and not rows and done == 0 and total > 0:
        out = ["NEXT PASS 2b: discovery",
               "The plan is written; check it and build the component catalog before the first packet:",
               "  python3 -I %s --repo . --analysis %s" % (shown("discover.py"), analysis),
               "Fix the plan until it exits 0, show its table to the user (on GitHub: in the pull request description) and ask",
               "which components: names, or all. Then run next.py again (with --component NAME for one component)."]
        return finish(out, analysis_abs, repo)
    waiting = open_questions(comp_dir) if comp else []
    if comp:
        SESSION["status"] = {"component": comp, "packets_done": done, "packets_total": total}
        if waiting and pending is None:
            out = ["WAITING FOR ANSWERS (%d open in %s/ledger/components/%s/questions.md)" % (len(waiting), analysis, comp)]
            out += ["  " + q for q in waiting[:20]]
            out += ["", "Stop now. Put these questions to the person (on GitHub: in the pull request description) and end the session.",
                    "When the answers are here, write each one under its question, change \"- [ ]\" to \"- [x]\", and run next.py again.",
                    "The next session starts with: python3 -I %s --repo . --analysis %s --depth %s%s --new-session" % (shown("next.py"), analysis, args.depth, flag)]
            return finish(out, analysis_abs, repo)

    if pending is not None:
        f, a, b, pages, gaps = pending
        if in_session >= args.budget:
            out = ["NEW CHAT",
                   "%d packets done in this chat (%d of %d %s, %d%%). Stop now and tell the user:" % (
                       in_session, done, total, "in component %s" % comp if comp else "overall", 100 * done // max(total, 1)),
                   "  continue the codebase analysis%s in %s" % (" of component %s" % comp if comp else "", analysis),
                   "The next chat starts with: python3 -I %s --repo . --analysis %s --depth %s%s --new-session" % (shown("next.py"), analysis, args.depth, flag)]
            return finish(out, analysis_abs, repo)
        owner = comp_name(f["path"])
        page = pages[0] if pages else module_page(f["path"], owner, [g["path"] for g in source if comp_name(g["path"]) == owner])
        index = next(i for i, q in enumerate(queue) if q[0] is f and q[1] == a) + 1
        out = ["NEXT PACKET %d of %d (%d done, %d%%; %d in this chat, budget %d)" % (index, total, done, 100 * done // max(total, 1), in_session, args.budget),
               "Component: %s" % owner,
               "Read:      %s lines %d-%d (of %d), in full" % (f["path"], a, b, f["lines"]),
               "Write:     %s/%s (%s)" % (analysis, page, "extend" if pages else "create; right under its title: Source file: `%s`" % f["path"]),
               "Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card%s" % (", " + api_page if any(g[0] == "route" for g in gaps) else ""),
               "", "To do in this packet (%d):" % len(gaps)]
        hashes = file_hashes(repo, f["path"])
        for kind, item, why in gaps:
            if kind == "symbol" and coverage.is_test_file(f["path"]):
                out.append("  - test `%s` (lines %d-%d): name it in the page's tests table with what it checks" % (item["qualname"], item["start"], item["end"]))
            elif kind == "symbol" or kind == "card":
                out.append("  - card %s: %s" % (describe_symbol(item, hashes), why))
            elif kind == "route":
                out.append("  - endpoint %s %s -> `%s` (line %d): %s" % ("/".join(item["methods"]), item["path"], item["handler"], item["line"], why))
            else:
                out.append("  - %s" % why)
        if waiting:
            out += ["", "%d open question(s) in ledger/components/%s/questions.md: carry on with the work that does not depend on them; "
                    "next.py stops to ask once the packets are done." % (len(waiting), comp)]
        out += ["", "When every item is written, %swrite one line to the user, and run next.py again." % ("" if comp else "tick the packet in progress.md, "),
                "Keep going: run next.py after every packet until it prints NEW CHAT or %s. Do not end your turn in between." % ("COMPONENT DONE" if comp else "DONE"),
                "Command: python3 -I %s --repo . --analysis %s --depth %s%s" % (shown("next.py"), analysis, args.depth, flag)]
        if comp:
            out.insert(-2, "Write only under lld/%s/, lld/api/%s/ and ledger/components/%s/: other components run in parallel." % (comp, comp, comp))
        return finish(out, analysis_abs, repo)

    if comp:
        return finish(component_end(repo, analysis, analysis_abs, comp, docs, total, args.depth, excludes), analysis_abs, repo)

    # Every packet is done: the remaining passes, in order.
    comps_in_pages = sorted({coverage.front_matter(t).get("component") for d, t in docs.items()
                             if d.startswith("lld/") and coverage.front_matter(t).get("component")})
    missing_readme = [c for c in comps_in_pages if "lld/%s/README.md" % c not in docs]
    progress = docs.get("progress.md", "")
    steps = [
        ("5: component design", missing_readme, "Write lld/<component>/README.md for: " + ", ".join(missing_readme)),
        ("6: sweep", [] if "## Sweep" in progress else ["sweep"], "Run the searches in references/search-sweep.md; record them under '## Sweep' in progress.md"),
        ("7: data dictionary", [] if "lld/data-dictionary.md" in docs else ["dd"], "Write lld/data-dictionary.md"),
        ("8: HLD", [h for h in ("hld/01-system-context.md", "hld/02-architecture.md", "hld/03-integrations.md",
                                "hld/04-data-architecture.md", "hld/05-key-flows.md", "hld/06-cross-cutting.md") if h not in docs], "Write: "),
        ("9: mind map, front page, reference", [h for h in ("00-mind-map.md", "README.md", "reference/glossary.md", "reference/configuration.md",
                                                           "reference/risks-and-surprises.md", "reference/open-questions.md") if h not in docs], "Write: "),
        ("10: knowledge base", [h for h in ("knowledge/AGENT-CONTEXT.md",) if h not in docs] +
         ([] if os.path.isfile(os.path.join(analysis_abs, "knowledge", "graph.json")) else ["run python3 -I %s --repo . --analysis %s" % (shown("knowledge.py"), analysis)]), "Do: "),
    ]
    for name, missing, text in steps:
        if missing:
            detail = text + (", ".join(missing) if text.endswith(": ") else "")
            out = ["NEXT PASS %s" % name, "All %d packets are done." % total, detail,
                   "Read that pass's section in references/passes.md first. Then run next.py again."]
            return finish(out, analysis_abs, repo)

    gate = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage.py"),
                           "--repo", repo, "--analysis", analysis, "--depth", args.depth] +
                          sum((["--exclude", e] for e in excludes), []), capture_output=True, text=True)
    if gate.returncode == 0:
        out = ["DONE", "coverage.py: result PASS at depth %s (pass 11, the gate, is done). Now, in this order:" % args.depth,
               "  1. the checks in references/quality-gate.md;"]
        if not os.path.isfile(os.path.join(analysis_abs, "ledger", "baseline.json")):
            out.append("  2. record the code this analysis describes, so later changes are a delta (it adds a cites line to each page): "
                       "python3 -I %s --repo . --analysis %s --init --label NAME" % (shown("delta.py"), analysis))
        out += ["  3. knowledge.py, on the final pages: python3 -I %s --repo . --analysis %s" % (shown("knowledge.py"), analysis),
                "  4. status.py --write, then finish as SKILL.md says (the bible stays unverified until verifying-a-codebase-analysis passes)."]
    else:
        out = ["NEXT PASS 11: quality gate", "coverage.py reports gaps; fix them from ledger/coverage-report.md, then run next.py again.", ""] + \
              [line for line in gate.stdout.splitlines() if line.startswith("  - ")][:15]
    return finish(out, analysis_abs, repo)


def component_end(repo, analysis, analysis_abs, comp, docs, total, depth, excludes):
    """Every packet of the component is done: its design page, then its check, then COMPONENT DONE."""
    if "lld/%s/README.md" % comp not in docs:
        return ["NEXT PASS 5: component design for %s" % comp, "All %d packets of %s are done." % (total, comp),
                "Write lld/%s/README.md (references/passes.md, Pass 5). Its outbound calls table names every call into another "
                "component; its inbound part names the components that call it (components.md lists both)." % comp,
                "Then run next.py again."]
    gate = subprocess.run([sys.executable, "-I", os.path.join(HERE, "coverage.py"), "--repo", repo, "--analysis", analysis,
                           "--depth", depth, "--component", comp] + sum((["--exclude", e] for e in excludes), []),
                          capture_output=True, text=True)
    if gate.returncode == 0:
        pending = revision_pending(analysis, analysis_abs, comp)
        if pending:
            return pending
        return ["COMPONENT DONE %s" % comp,
                "coverage.py --component %s: result PASS at depth %s (%d packets). Stop now and tell the user:" % (comp, depth, total),
                "  component %s is analysed and its check passes (report: %s/ledger/components/%s/coverage-report.md)" % (comp, analysis, comp),
                "  next: verify it in a new session on a different model (verifying-a-codebase-analysis, scope: component %s)" % comp,
                "Where the other components stand: python3 -I %s --repo . --analysis %s --board" % (shown("next.py"), analysis)]
    return ["NEXT PASS: component check for %s" % comp,
            "coverage.py --component %s reports gaps; fix them from %s/ledger/components/%s/coverage-report.md, then run next.py again." % (comp, analysis, comp),
            ""] + [line for line in gate.stdout.splitlines() if line.startswith("  - ")][:15]


def revision_pending(analysis, analysis_abs, comp):
    """NEXT REVISION when the component's verification asked for corrections that are not applied yet: its verdict is
    FAIL or PASS AFTER CORRECTIONS (not re-checked), and its fingerprint still equals the pages, so no page has
    changed since. Without this, a revision session sees the gate pass and stops with nothing applied."""
    rel = "%s/ledger/components/%s/verification-report.md" % (analysis, comp)
    facts = status.report_facts(os.path.join(analysis_abs, "ledger", "components", comp, "verification-report.md"))
    if not facts or facts["verdict"] not in ("FAIL", "PASS AFTER CORRECTIONS"):
        return None
    recheck = facts.get("recheck")
    if recheck and recheck[1] > 0 and recheck[0] == recheck[1]:
        return None
    if not facts["fingerprint"] or facts["fingerprint"] != status.fingerprint(analysis_abs, comp):
        return None  # the pages changed after the verification: applied, or under way; verify again
    report = status.read(os.path.join(analysis_abs, "ledger", "components", comp, "verification-report.md")) or ""
    ids = set(re.findall(r"^\|\s*(V-\d+)\s*\|", status.section(report, "Corrections"), re.M))
    log = status.read(os.path.join(analysis_abs, "ledger", "components", comp, "revision-log.md")) or ""
    if ids and all(re.search(r"\b%s\b" % re.escape(i), log) for i in ids):
        return None  # every correction is answered in the log (some need no page change, with the reason written there)
    return ["NEXT REVISION %s: apply the verification's corrections" % comp,
            "%s gives verdict %s (%d major) and its fingerprint %s equals the pages now: no correction is applied yet."
            % (rel, facts["verdict"], facts["majors"], facts["fingerprint"]),
            "Apply every row of its Corrections table, majors first (references/revision.md, Component mode): change the pages "
            "under %s/lld/%s/ and %s/lld/api/%s/, and record each item in %s/ledger/components/%s/revision-log.md."
            % (analysis, comp, analysis, comp, analysis, comp),
            "Do not edit the verification report. Then run next.py again."]


def finish(lines, analysis_abs, repo):
    if SESSION["path"]:
        lines = record_job(lines) + SESSION["note"]
        os.makedirs(os.path.dirname(SESSION["path"]), exist_ok=True)
        with open(SESSION["path"], "w", encoding="utf-8") as handle:
            json.dump(SESSION["state"], handle)
    if SESSION["status_path"] and SESSION["status"]:
        status = dict(SESSION["status"], state=state_of(lines[0] if lines else ""),
                      last_job_digest=SESSION["state"].get("last", "") if SESSION["state"] else "",
                      updated=datetime.datetime.now().isoformat(timespec="seconds"))
        with open(inventory.safe_target(repo, SESSION["status_path"]), "w", encoding="utf-8") as handle:
            json.dump(status, handle, indent=1)
    text = "\n".join(lines) + "\n"
    target = inventory.safe_target(repo, SESSION["next_path"] or os.path.join(analysis_abs, "ledger", "next.md"))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("```text\n" + text + "```\n")
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
