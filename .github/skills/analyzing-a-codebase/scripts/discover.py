#!/usr/bin/env python3
"""Discovery: the component catalog a person picks from, before any component is analysed.

Reads the code (a fresh scan) and the plan under `## Components` in `<analysis>/progress.md`,
checks the plan, and writes:

  <analysis>/components.json         the catalog next.py --component and coverage.py --component read
  <analysis>/components.md           the same as a table, plus a Mermaid graph of calls between components
  <analysis>/ledger/issues/*.md      ready-to-paste issue texts: plan.md, one per component, assemble.md

With no `## Components` section yet, it proposes one component per top folder and marks the
catalog `proposed`; write the plan in progress.md (references/passes.md, Pass 2) and run it again.

  python3 -I <skill>/scripts/discover.py --repo . --analysis codebase-analysis [--budget 6] [--depth deep]
  python3 -I <skill>/scripts/discover.py --repo . --analysis codebase-analysis --migrate-layout [--undo]

`--migrate-layout` moves endpoint-card pages from lld/api/<group>.md to lld/api/<component>/<group>.md
(the layout component mode needs) and rewrites the links to them; `--undo` moves them back.

Exit 0 when the catalog is written, 1 when the plan has problems (listed), 2 on a usage error.
Read-only on the repository; writes only inside the analysis folder. Standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory  # noqa: E402
import coverage  # noqa: E402
import components  # noqa: E402
import next as work_loop  # noqa: E402  (next.py: packets_for, component_of)

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = "analyzing-a-codebase/scripts/discover.py 1.11.0"


def script_path(repo: str, name: str) -> str:
    """How an issue text should name a script: relative to the repository when the skill is installed in it."""
    full = os.path.join(HERE, name)
    rel = os.path.relpath(full, repo)
    return rel.replace(os.sep, "/") if not rel.startswith("..") else ".github/skills/analyzing-a-codebase/scripts/" + name


def node_id(name: str) -> str:
    return re.sub(r"\W", "_", name) if re.match(r"^[A-Za-z]", name) else "c_" + re.sub(r"\W", "_", name)


def write(repo: str, path: str, text: str) -> None:
    target = inventory.safe_target(repo, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(repo, analysis, files, rows, budget, depth, proposed):
    comp_of = components.component_map(files, rows)
    edges = [] if proposed else components.cross_calls(repo, files, comp_of, coverage.is_test_file)
    out = []
    for name, paths in rows:
        mine = [f for f in components.planned_files(files) if comp_of.get(f["path"]) == name]
        packets = sum(len(work_loop.packets_for(f)) for f in mine)
        out.append({
            "name": name,
            "paths": paths,
            "files": len(mine),
            "lines": sum(f["lines"] for f in mine),
            "packets": packets,
            "est_sessions": math.ceil(packets / max(budget, 1)) + 1,
            "routes": sum(len([r for r in f["routes"] if r["methods"] != ["UI"]]) for f in mine),
            "calls_into": sorted({e["target_component"] for e in edges if e["component"] == name}),
            "calls_detail": {t: sorted({e["name"] for e in edges if e["component"] == name and e["target_component"] == t})
                             for t in sorted({e["target_component"] for e in edges if e["component"] == name})},
            "called_by": sorted({e["component"] for e in edges if e["target_component"] == name}),
        })
    return {"schema": 1, "tool": TOOL, "generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "proposed": proposed, "analysis": analysis, "budget": budget, "depth": depth,
            "components": out, "cross_calls": len(edges)}


def catalog_markdown(repo, catalog):
    analysis, comps = catalog["analysis"], catalog["components"]
    nxt = script_path(repo, "next.py")
    lines = ["# Components", "",
             "Written by `discover.py` on %s from the plan under `## Components` in `progress.md`%s. "
             "%d components, %d packets; about %d sessions in all at %d packets per session (each component's packets in sessions, plus one for its page and check; depth `%s`)." % (
                 catalog["generated"][:10], " (proposed: no plan written yet)" if catalog["proposed"] else "",
                 len(comps), sum(c["packets"] for c in comps), sum(c["est_sessions"] for c in comps),
                 catalog["budget"], catalog["depth"]), "",
             "| Component | Paths | Source files | Lines | Packets | Sessions (est.) | Routes | Calls into | Called by |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in comps:
        lines.append("| `%s` | %s | %d | %d | %d | %d | %d | %s | %s |" % (
            c["name"], ", ".join("`%s`" % p for p in c["paths"]), c["files"], c["lines"], c["packets"], c["est_sessions"],
            c["routes"], ", ".join("`%s`" % x for x in c["calls_into"]) or "none",
            ", ".join("`%s`" % x for x in c["called_by"]) or "none"))
    lines += ["", "Sessions (est.) is the packets divided by the packets per session, rounded up, plus one for the component page "
              "and its check. Verification is one more session per component.", "", "## Calls between components", "",
              "```mermaid", "flowchart LR"]
    for c in comps:
        lines.append('  %s["%s"]' % (node_id(c["name"]), c["name"]))
    for c in comps:
        for target in c["calls_into"]:
            names = c.get("calls_detail", {}).get(target, [])
            label = ", ".join(names[:3]) + (" +%d more" % (len(names) - 3) if len(names) > 3 else "") or "calls"
            lines.append('  %s -->|"%s"| %s' % (node_id(c["name"]), label.replace('"', "'"), node_id(target)))
    lines += ["```", "", "## How to run", "",
              "- One component: `python3 -I %s --repo . --analysis %s --component NAME --new-session`, "
              "then follow what it prints until `COMPONENT DONE NAME`." % (nxt, analysis),
              "- Where every component stands: `python3 -I %s --repo . --analysis %s --board`." % (nxt, analysis),
              "- On GitHub without workflows: one issue per component from `ledger/issues/` (docs/github-guide.md, Part 4).",
              "- When every component is done: the assemble step (`ledger/issues/assemble.md`).", ""]
    return "\n".join(lines)


STOP_RULES = """Stop and end the session when next.py prints NEW CHAT, COMPONENT DONE, WAITING FOR ANSWERS,
STOP or DONE. Before you stop, write in the pull request description:
  - what you finished in this session,
  - the first line next.py printed last (for example "NEW CHAT" or "COMPONENT DONE {name}"),
  - any questions for the person, numbered.
If you hit a question only a person can answer, add it to {questions} as a line "- [ ] Q1. ...",
then run next.py: it prints WAITING FOR ANSWERS and you stop.
When this pull request already has answers from the person, write each under its question,
change "- [ ]" to "- [x]", then run next.py again.
A failed call is a stop, not a restart: if a command or model request fails twice, stop and say what failed."""


def issue_texts(repo, catalog):
    analysis = catalog["analysis"]
    nxt, disc = script_path(repo, "next.py"), script_path(repo, "discover.py")
    texts = {"plan.md": "\n".join([
        "Title: Codebase analysis - plan the components", "",
        "Use the analyzing-a-codebase skill (in .github/skills) for passes 1 and 2 only:",
        "  python3 -I %s --repo . --analysis %s --new-session" % (nxt, analysis),
        "Follow what it prints for pass 1 (inventory) and pass 2 (write the `## Components` table in %s/progress.md)." % analysis,
        "Then run:",
        "  python3 -I %s --repo . --analysis %s" % (disc, analysis),
        "and fix the plan until it exits 0. It writes components.json, components.md and the issue texts.",
        "Do not start on any component. Show the table from components.md to the person in the pull request description:",
        "they choose the components there (when it says to ask the user which components, this is how).",
        "Do not edit anything outside %s/." % analysis, ""])}
    for c in catalog["components"]:
        name = c["name"]
        questions = "%s/ledger/components/%s/questions.md" % (analysis, name)
        texts["%s.md" % name] = "\n".join([
            "Title: Codebase analysis - component %s" % name, "",
            "Use the analyzing-a-codebase skill (in .github/skills) in component mode for `%s` only." % name,
            "Size: %d source files, %d packets, about %d sessions. Calls into: %s. Called by: %s." % (
                c["files"], c["packets"], c["est_sessions"], ", ".join(c["calls_into"]) or "none", ", ".join(c["called_by"]) or "none"),
            "", "Start every session with:",
            "  python3 -I %s --repo . --analysis %s --depth %s --component %s --new-session" % (nxt, analysis, catalog["depth"], name),
            "and do exactly what it prints, running it again after each job, until it tells you to stop.", "",
            "Write only inside these folders (other components work in parallel on other pull requests):",
            "  %s" % "\n  ".join("%s/%s" % (analysis, p) for p in components.owned_prefixes(name)),
            "", STOP_RULES.replace("{name}", name).replace("{questions}", questions), "",
            "When it prints COMPONENT DONE, the next step is a verification of this component in a new session",
            "on a different model (the person asks for it with an @copilot comment on this pull request).", ""])
    texts["assemble.md"] = "\n".join([
        "Title: Codebase analysis - assemble the whole bible", "",
        "Every component pull request is merged. Use the analyzing-a-codebase skill (in .github/skills) without --component:",
        "  python3 -I %s --repo . --analysis %s --depth %s --new-session" % (nxt, analysis, catalog["depth"]),
        "It hands out the whole-system passes: sweep, data dictionary, HLD, mind map, front page, reference,",
        "knowledge base and the full quality gate, which also checks that each component's page names its callers.",
        "Continue until it prints DONE, then record the baseline as it says (delta.py --init).",
        "", STOP_RULES.replace("{name}", "").replace("{questions}", "%s/ledger/questions.md" % analysis), "",
        "After DONE, the person asks for a verification of the whole analysis in a new session on a different model", ""])
    return texts


def migrate(repo, analysis_abs, files, rows, undo):
    """Move lld/api/<group>.md to lld/api/<component>/<group>.md, or back with undo."""
    log_path = inventory.safe_target(repo, os.path.join(analysis_abs, "ledger", "layout-migration.json"))
    api = os.path.join(analysis_abs, "lld", "api")

    def rewrite_links(moves):
        for root, dirs, names in os.walk(analysis_abs):
            dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
            for name in names:
                if not name.endswith(".md"):
                    continue
                full = os.path.join(root, name)
                with open(full, encoding="utf-8", errors="replace") as handle:
                    text = original = handle.read()
                rel = os.path.relpath(full, analysis_abs).replace(os.sep, "/")
                for old, new in moves:
                    text = re.sub(r"(?<![\w-])%s(?=\.md\b|\b)" % re.escape(old[:-3]), new[:-3], text)
                    text = re.sub(r"(?<=\.\./)%s(?=\.md\b)" % re.escape(old[len("lld/"):-3]), new[len("lld/"):-3], text)
                    if rel == "lld/api/README.md":
                        o, n = old[len("lld/api/"):], new[len("lld/api/"):]
                        text = re.sub(r"\]\((?:\./)?%s\)" % re.escape(o), "](%s)" % n, text)
                if text != original:
                    with open(inventory.safe_target(repo, full), "w", encoding="utf-8") as handle:
                        handle.write(text)

    def deeper(path, levels):
        """Relative links in a moved page: one folder deeper (levels=1) or back up (levels=-1)."""
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        if levels > 0:
            text = re.sub(r"\]\((?!https?:|#|/)", "](../", text)
        else:
            text = re.sub(r"\]\(\.\./", "](", text)
        with open(inventory.safe_target(repo, path), "w", encoding="utf-8") as handle:
            handle.write(text)

    if undo:
        if not os.path.isfile(log_path):
            inventory.fail("nothing to undo: ledger/layout-migration.json not found")
        with open(log_path, encoding="utf-8") as handle:
            moves = [(m["from"], m["to"]) for m in json.load(handle)["moves"]]
        for old, new in moves:
            src, dst = os.path.join(analysis_abs, new), os.path.join(analysis_abs, old)
            if os.path.isfile(src) and not os.path.exists(dst):
                deeper(src, -1)
                shutil.move(src, inventory.safe_target(repo, dst))
        rewrite_links([(new, old) for old, new in moves])
        os.remove(log_path)
        return ["moved back %d pages; links rewritten; removed ledger/layout-migration.json" % len(moves)]
    if not os.path.isdir(api):
        return ["nothing to move: no lld/api/ folder"]
    comp_of = components.component_map(files, rows)
    routes = []
    for f in files:
        for r in f["routes"]:
            if r["methods"] != ["UI"] and comp_of.get(f["path"]):
                path = coverage.norm_route(r["path"])
                routes.append((re.compile(r"(?<![\w/{<:-])" + re.escape(path) + r"/?(?![\w/{<-])"),
                               [m for m in r["methods"] if m != "ANY"], comp_of[f["path"]]))
    moves, report = [], []
    for name in sorted(os.listdir(api)):
        full = os.path.join(api, name)
        if not name.endswith(".md") or name == "README.md" or not os.path.isfile(full):
            continue
        with open(full, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        owners = set()
        for title, level, _body, _line in coverage.sections(text):
            if level < 2:
                continue
            for pattern, methods, comp in routes:
                if pattern.search(title) and all(re.search(r"\b%s\b" % m, title) for m in methods):
                    owners.add(comp)
        if len(owners) != 1:
            report.append("left `lld/api/%s`: %s" % (name, "its endpoint cards belong to %s; split it by component first" % ", ".join(sorted(owners))
                                                       if owners else "no endpoint card matched a route in the code"))
            continue
        comp = owners.pop()
        old, new = "lld/api/%s" % name, "lld/api/%s/%s" % (comp, name)
        if os.path.exists(os.path.join(analysis_abs, new)):
            report.append("left `%s`: `%s` already exists" % (old, new))
            continue
        os.makedirs(inventory.safe_target(repo, os.path.join(api, comp)), exist_ok=True)
        shutil.move(full, inventory.safe_target(repo, os.path.join(analysis_abs, new)))
        deeper(os.path.join(analysis_abs, new), 1)
        moves.append((old, new))
    rewrite_links(moves)
    if moves:
        write(repo, log_path, json.dumps({"tool": TOOL, "when": datetime.datetime.now().isoformat(timespec="seconds"),
                                          "moves": [{"from": a, "to": b} for a, b in moves]}, indent=1))
    return ["moved %d pages to lld/api/<component>/ and rewrote links%s" % (len(moves), "; undo with --migrate-layout --undo" if moves else "")] + report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--depth", choices=sorted(coverage.DEPTHS), default="deep")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--budget", type=int, default=6, help="packets per session, for the session estimate (default 6)")
    parser.add_argument("--migrate-layout", action="store_true", help="move lld/api/<group>.md to lld/api/<component>/<group>.md")
    parser.add_argument("--undo", action="store_true", help="with --migrate-layout: move the pages back")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    analysis = work_loop.norm(args.analysis)
    if os.path.isabs(args.analysis) or ".." in analysis.split("/") or analysis in ("", "."):
        inventory.fail("--analysis must be a folder inside the repository, given relative to it")
    analysis_abs = os.path.join(repo, analysis)
    if not os.path.isdir(analysis_abs):
        inventory.fail("analysis folder not found: %s (run next.py first: it starts with the inventory)" % analysis)
    excludes = [work_loop.norm(e).strip("/") for e in args.exclude]
    files, _excluded = inventory.scan(repo, analysis, excludes)
    skips = coverage.load_skips(analysis_abs)
    rows = components.parse_plan(components.read_plan_text(analysis_abs))
    proposed = rows is None
    if proposed:
        tops = {}
        for f in components.planned_files(files):
            comp = work_loop.component_of(f["path"])
            tops.setdefault(comp, set()).add(f["path"] if comp == "root" else comp + "/")
        rows = [(name, sorted(paths)) for name, paths in sorted(tops.items())]
    else:
        try:
            components.check_plan(rows, files, lambda path: coverage.skipped(skips, path, "*"))
        except components.PlanError as problem:
            print("The plan under `## Components` in %s/progress.md has problems:" % analysis)
            print(str(problem))
            print("Fix the plan (references/passes.md, Pass 2), then run discover.py again.")
            sys.exit(1)

    if args.migrate_layout:
        if proposed:
            inventory.fail("--migrate-layout needs the plan under `## Components` in progress.md")
        for line in migrate(repo, analysis_abs, files, rows, args.undo):
            print(line)
        if args.undo:
            return

    catalog = build(repo, analysis, files, rows, args.budget, args.depth, proposed)
    write(repo, os.path.join(analysis_abs, components.CATALOG), json.dumps(catalog, indent=1) + "\n")
    write(repo, os.path.join(analysis_abs, "components.md"), catalog_markdown(repo, catalog))
    if not proposed:
        for name, body in issue_texts(repo, catalog).items():
            write(repo, os.path.join(analysis_abs, "ledger", "issues", name), body)

    comps = catalog["components"]
    print("%s %d components, %d packets, about %d sessions at %d packets per session" % (
        "PROPOSED" if proposed else "CATALOG", len(comps), sum(c["packets"] for c in comps),
        sum(c["est_sessions"] for c in comps), args.budget))
    width = max([len(c["name"]) for c in comps] + [9])
    print("  %-*s %7s %8s %9s  %s" % (width, "component", "files", "packets", "sessions", "calls into"))
    for c in comps:
        print("  %-*s %7d %8d %9d  %s" % (width, c["name"], c["files"], c["packets"], c["est_sessions"], ", ".join(c["calls_into"]) or "-"))
    if proposed:
        print("No `## Components` section in progress.md yet: this split by top folder is only a proposal.")
        print("Write the plan (references/passes.md, Pass 2), then run discover.py again.")
    else:
        print("wrote %s/components.json, %s/components.md and %s/ledger/issues/" % (analysis, analysis, analysis))
        print("Show the table to the user and ask which components to analyse: names, or all.")


if __name__ == "__main__":
    main()
