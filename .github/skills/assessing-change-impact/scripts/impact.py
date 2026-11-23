#!/usr/bin/env python3
"""Blast radius of a planned change, from the analysis's knowledge graph.

Given one or more targets (a function, a file, a file and line range, a route, a
table or store, an outside system, a configuration key or a component), walks
`<analysis>/knowledge/graph.json` and reports:

  - dependents: what calls, handles, imports, reads or is configured by the target,
    level by level, with the path, the evidence and how each edge was resolved
  - data coupling: other code reading or writing the same tables and stores
  - dependencies: what the target itself relies on
  - the components, entry points (routes) and outside systems in the radius
  - tests that reach the radius, and targets no test reaches
  - the analysis pages and cards to update after the change
  - whether the graph is stale for the files involved

Writes `<analysis>/impact/<name>.md` and `.json`. Read-only on the repository
and on the graph. Standard library only; never imports or runs repository code.

  python3 -I <skill>/scripts/impact.py --repo . --analysis codebase-analysis \
      --target "AuditService.record" --target "app/upload.py:120-180" --name upload-audit
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from collections import deque

# Edge types along which a change propagates to the edge's source (source depends on target).
DEPENDS = {"CALLS", "HANDLED_BY", "IMPORTS", "USES", "READS", "WRITES", "CONFIG", "CONSUMES", "DEPENDS_ON"}
CODE_NODES = {"Function", "Method", "Class"}
TEST_PATH = re.compile(r"(^|/)(tests?|spec|specs|__tests__|test_[^/]*|[^/]*_test|[^/]*\.test|[^/]*\.spec|[^/]*Tests?)(\.|/|$)", re.I)


def fail(message: str, code: int = 2) -> None:
    print("error: " + message, file=sys.stderr)
    sys.exit(code)


def safe_target(repo: str, path: str) -> str:
    base = os.path.abspath(repo)
    full = os.path.abspath(path)
    rel = os.path.relpath(full, base)
    if rel == os.curdir or rel.startswith(os.pardir):
        fail("output must stay inside the repository: " + path)
    current = base
    for part in rel.split(os.sep):
        current = os.path.join(current, part)
        if os.path.islink(current):
            fail("refusing to write through a symbolic link: " + current)
    return full


def risk(distance: int) -> str:
    return "high" if distance <= 1 else ("medium" if distance == 2 else "low")


class Graph:
    def __init__(self, data):
        self.nodes = {n["id"]: n for n in data["nodes"]}
        self.edges = data["edges"]
        self.into, self.out = {}, {}
        for e in self.edges:
            self.into.setdefault(e["target"], []).append(e)
            self.out.setdefault(e["source"], []).append(e)
        self.generated = data.get("generated", "")

    def file_of(self, node_id: str):
        node = self.nodes.get(node_id, {})
        if node.get("type") == "File":
            return node_id
        if node.get("path") and ("file:" + node["path"]) in self.nodes and node.get("type") != "Page":
            return "file:" + node["path"]
        return None

    def components_of(self, node_id: str):
        file_id = self.file_of(node_id)
        if node_id.startswith("component:"):
            return [self.nodes[node_id]["name"]]
        if not file_id:
            return []
        return sorted({self.nodes[e["source"]]["name"] for e in self.into.get(file_id, [])
                       if e["type"] == "CONTAINS" and e["source"] in self.nodes})

    def symbols_in(self, file_id: str):
        return [e["target"] for e in self.out.get(file_id, []) if e["type"] == "DEFINES"] + \
               [e2["target"] for e in self.out.get(file_id, []) if e["type"] == "DEFINES"
                for e2 in self.out.get(e["target"], []) if e2["type"] == "DEFINES"]


def resolve(graph: Graph, target: str):
    """Target text -> (seed node ids, how it was matched)."""
    t = target.strip().strip("`")
    if t in graph.nodes:
        return [t], "node id"
    line_range = re.match(r"^(.+?):(\d+)(?:-(\d+))?$", t)
    if line_range and ("file:" + line_range.group(1)) in graph.nodes:
        path, start = line_range.group(1), int(line_range.group(2))
        end = int(line_range.group(3) or start)
        hits = [n for n in graph.symbols_in("file:" + path)
                if graph.nodes[n].get("start") and graph.nodes[n]["start"] <= end and graph.nodes[n]["end"] >= start]
        innermost = [n for n in hits if not any(
            h != n and graph.nodes[h]["start"] >= graph.nodes[n]["start"] and graph.nodes[h]["end"] <= graph.nodes[n]["end"] for h in hits)]
        return (innermost or ["file:" + path]), "symbols overlapping lines %d-%d" % (start, end)
    if ("file:" + t) in graph.nodes:
        return ["file:" + t] + graph.symbols_in("file:" + t), "file and the symbols it defines"
    ends = [n for n in graph.nodes if n.startswith("file:") and n.endswith("/" + t)]
    if len(ends) == 1:
        return [ends[0]] + graph.symbols_in(ends[0]), "file (matched by name) and its symbols"
    if ("component:" + t) in graph.nodes:
        files = [e["target"] for e in graph.out.get("component:" + t, []) if e["type"] == "CONTAINS"]
        seeds = list(files)
        for f in files:
            seeds += graph.symbols_in(f)
        return ["component:" + t] + seeds, "component, its files and their symbols"
    route = re.match(r"^(GET|POST|PUT|DELETE|PATCH|ANY|UI)\s+(\S+)$", t, re.I)
    if route:
        rid = "route:%s %s" % (route.group(1).upper(), route.group(2))
        matches = [n for n in graph.nodes if n.startswith("route:") and
                   (n == rid or (n.split(" ", 1)[1] == route.group(2) and route.group(1).upper() in n.split(" ")[0].split(":")[1].split("/")))]
        if matches:
            return matches, "route"
    for prefix in ("table:", "store:", "external:", "config:", "topic:", "queue:", "cache:", "job:"):
        if t.lower().startswith(prefix):
            name = t[len(prefix):]
            found = [n for n in graph.nodes if n.lower() == (prefix + name).lower()]
            if found:
                return found, prefix.rstrip(":")
    by_name = [n for n, v in graph.nodes.items() if v.get("type") in CODE_NODES and
               (v["name"] == t or v["name"].endswith("." + t))]
    if by_name:
        return by_name, "symbol name" + (" (%d matches: narrow it with the file path)" % len(by_name) if len(by_name) > 1 else "")
    loose = [n for n, v in graph.nodes.items() if v.get("name", "").lower() == t.lower() and v.get("type") not in ("Page",)]
    if loose:
        return loose, "name"
    return [], "no match"


def walk_dependents(graph: Graph, seeds, max_depth: int, limit: int, facts_only: bool = False):
    """Reverse BFS: who depends on the seeds. Returns {node: (distance, edge, parent)} and truncated flag."""
    seen = {s: (0, None, None) for s in seeds}
    queue = deque(seeds)
    truncated = False
    while queue:
        node = queue.popleft()
        distance = seen[node][0]
        if distance >= max_depth:
            continue
        nexts = []
        for e in graph.into.get(node, []):
            if e["type"] in DEPENDS:
                nexts.append((e["source"], e))
        # A change to a symbol reaches what its file declares and what depends on its file's data.
        node_type = graph.nodes.get(node, {}).get("type")
        if node_type in CODE_NODES:
            file_id = graph.file_of(node)
            if file_id:
                for e in graph.into.get(file_id, []):
                    if e["type"] == "IMPORTS":
                        nexts.append((e["source"], e))
        if node_type in ("Table", "Store", "Cache", "File") or node.startswith(("table:", "store:", "cache:")):
            for e in graph.into.get(node, []):
                if e["type"] in ("READS", "WRITES"):
                    nexts.append((e["source"], e))
        for source, e in nexts:
            if source in seen or (facts_only and e.get("resolution") in ("name-unique", "analysis")):
                continue
            if len(seen) >= limit:
                truncated = True
                break
            seen[source] = (distance + 1, e, node)
            queue.append(source)
    return seen, truncated


def data_coupling(graph: Graph, seeds):
    """Tables and stores the seeds (or their files) write or read, and who else touches them."""
    touched = {}
    owners = set(seeds) | {graph.file_of(s) for s in seeds if graph.file_of(s)}
    for owner in owners:
        for e in graph.out.get(owner, []):
            if e["type"] in ("READS", "WRITES") and graph.nodes.get(e["target"], {}).get("type") not in ("File",):
                touched.setdefault(e["target"], set()).add(e["type"])
            elif e["type"] in ("READS", "WRITES") and e["target"].startswith("file:"):
                touched.setdefault(e["target"], set()).add(e["type"])
    coupled = []
    for store, how in sorted(touched.items()):
        others = [(e["source"], e["type"], e["evidence"]) for e in graph.into.get(store, [])
                  if e["type"] in ("READS", "WRITES") and e["source"] not in owners]
        coupled.append({"store": store, "seed_access": sorted(how), "others": others})
    return coupled


def dependencies(graph: Graph, seeds):
    rows = []
    for s in seeds:
        for e in graph.out.get(s, []):
            if e["type"] in DEPENDS - {"HANDLED_BY"} or e["type"] in ("PUBLISHES", "EXPOSES"):
                rows.append((s, e))
        file_id = graph.file_of(s)
        if file_id and file_id != s:
            for e in graph.out.get(file_id, []):
                if e["type"] in ("READS", "WRITES", "CALLS", "USES", "CONFIG", "PUBLISHES", "CONSUMES"):
                    rows.append((file_id, e))
    unique, seen = [], set()
    for s, e in rows:
        key = (s, e["target"], e["type"])
        if key not in seen:
            seen.add(key)
            unique.append((s, e))
    return unique


def path_to_seed(seen, node):
    chain = [node]
    while seen[chain[-1]][2] is not None:
        chain.append(seen[chain[-1]][2])
    return chain


def label(graph: Graph, node_id: str) -> str:
    node = graph.nodes.get(node_id, {"name": node_id, "type": "?"})
    where = ""
    if node.get("path") and node.get("start"):
        where = " (`%s:%s-%s`)" % (node["path"], node["start"], node["end"])
    elif node.get("path") and node.get("line"):
        where = " (`%s:%s`)" % (node["path"], node["line"])
    return "%s `%s`%s" % (node.get("type", ""), node.get("name", node_id), where)


def stale_files(repo: str, graph: Graph, node_ids):
    stale = []
    for n in sorted({graph.file_of(x) for x in node_ids if graph.file_of(x)}):
        node = graph.nodes[n]
        full = os.path.join(repo, node["path"])
        if not os.path.isfile(full):
            stale.append("`%s` no longer exists" % node["path"])
            continue
        try:
            with open(full, "rb") as handle:
                raw = handle.read()
            lines = raw.count(b"\n") + (0 if raw.endswith(b"\n") or not raw else 1)
        except OSError:
            continue
        if node.get("lines") not in (None, "") and int(node["lines"]) != lines:
            stale.append("`%s` had %s lines in the graph, has %d now" % (node["path"], node["lines"], lines))
    return stale


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--target", action="append", required=True,
                        help="symbol, file, file:lines, 'METHOD /path', table:<name>, store:, external:, config:, component name, or node id")
    parser.add_argument("--name", default=None, help="report name (default from the first target)")
    parser.add_argument("--depth", type=int, default=4, help="levels of dependents to follow (default 4)")
    parser.add_argument("--limit", type=int, default=2000, help="most nodes to visit (default 2000)")
    parser.add_argument("--facts-only", action="store_true",
                        help="follow only edges the parser established; skip name-unique and analysis edges")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    if os.path.isabs(args.analysis) or ".." in args.analysis.split("/"):
        fail("--analysis must be a folder inside the repository, given relative to it")
    graph_path = os.path.join(repo, args.analysis, "knowledge", "graph.json")
    if not os.path.isfile(graph_path):
        fail("no %s: run analyzing-a-codebase's scripts/knowledge.py first" % os.path.relpath(graph_path, repo))
    with open(graph_path, encoding="utf-8") as handle:
        graph = Graph(json.load(handle))

    name = args.name or re.sub(r"[^A-Za-z0-9_.-]+", "-", args.target[0]).strip("-")[:60] or "change"
    if not re.match(r"^[A-Za-z0-9_.-]+$", name):
        fail("--name may hold letters, digits, dot, dash and underscore only")
    out_md = safe_target(repo, os.path.join(repo, args.analysis, "impact", name + ".md"))
    out_json = safe_target(repo, os.path.join(repo, args.analysis, "impact", name + ".json"))

    seeds, matched = [], []
    for t in args.target:
        found, how = resolve(graph, t)
        matched.append((t, how, found))
        seeds += [f for f in found if f not in seeds]
    if not seeds:
        fail("no target matched the graph: " + "; ".join("%s (%s)" % (t, h) for t, h, _ in matched), 1)

    seen, truncated = walk_dependents(graph, seeds, args.depth, args.limit, args.facts_only)
    impacted = {n: v for n, v in seen.items() if v[0] > 0}
    coupled = data_coupling(graph, seeds)
    deps = dependencies(graph, seeds)

    radius = set(seeds) | set(impacted)
    for c in coupled:
        radius |= {o[0] for o in c["others"]}
    components = {}
    for n in radius:
        for comp in graph.components_of(n):
            components.setdefault(comp, set()).add(n)
    routes = sorted(n for n in radius if n.startswith("route:"))
    externals = sorted({e["target"] for _, e in deps if e["target"].startswith("external:")} |
                       {n for n in radius if n.startswith("external:")})
    tests = sorted(n for n in radius if TEST_PATH.search(graph.nodes.get(n, {}).get("path", "") or ""))
    code_seeds = [s for s in seeds if graph.nodes.get(s, {}).get("type") in CODE_NODES]
    reached = set()
    for t in tests:
        for n in path_to_seed(seen, t) if t in seen else []:
            reached.add(n)
    untested = [s for s in code_seeds if s not in reached]
    pages = sorted({e["source"] for n in radius for f in [graph.file_of(n)] if f
                    for e in graph.into.get(f, []) if e["type"] == "DOCUMENTS"})
    weak = [n for n, (d, e, _p) in impacted.items() if e and e.get("resolution") in ("name-unique", "analysis")]
    stale = stale_files(repo, graph, radius)

    by_level = {}
    for n, (d, e, p) in impacted.items():
        by_level.setdefault(d, []).append((n, e, p))

    out = ["# Change impact: %s" % name, "",
           "Generated by `impact.py` on %s from `knowledge/graph.json` of %s. Depth %d, limit %d%s." % (
               datetime.datetime.now().isoformat(timespec="seconds"), graph.generated or "unknown date",
               args.depth, args.limit, (", **truncated: the radius is larger than shown**" if truncated else "") +
               (", facts only (name-unique and analysis edges not followed)" if args.facts_only else "")), "",
           "## Targets", "", "| Given | Matched as | Nodes |", "| --- | --- | --- |"]
    out += ["| `%s` | %s | %s |" % (t, how, ", ".join(label(graph, f) for f in found[:6]) + (" and %d more" % (len(found) - 6) if len(found) > 6 else ""))
            for t, how, found in matched]
    out += ["", "## Summary", "", "| Measure | Count |", "| --- | --- |",
            "| Dependents (levels 1 to %d) | %d |" % (args.depth, len(impacted)),
            "| High / medium / low (distance 1 / 2 / 3+) | %d / %d / %d |" % tuple(
                sum(1 for v in impacted.values() if risk(v[0]) == r) for r in ("high", "medium", "low")),
            "| Components in the radius | %d |" % len(components),
            "| Entry points (routes) in the radius | %d |" % len(routes),
            "| Tables and stores shared with other code | %d |" % sum(1 for c in coupled if c["others"]),
            "| Outside systems involved | %d |" % len(externals),
            "| Tests reaching the radius | %d |" % len(tests),
            "| Code targets no test reaches | %d |" % len(untested),
            "| Edges that are leads, not facts (name-unique, analysis) | %d |" % len(weak), ""]
    if stale:
        out += ["## The graph is stale for these files", "",
                "Line numbers and edges below may be wrong. Re-run the analysis scripts (inventory, coverage, knowledge) first.", ""] + \
               ["- " + s for s in stale] + [""]
    out += ["## Components", "", "| Component | Nodes in the radius |", "| --- | --- |"]
    out += ["| %s | %d |" % (c, len(v)) for c, v in sorted(components.items())] or ["| (none found: front matter has no `component`) | |"]
    out += ["", "## Entry points that may change behaviour", ""]
    out += ["- %s, %s" % (label(graph, r), "distance %d" % seen[r][0] if r in seen else "data-coupled") for r in routes] or ["None reached."]
    out += ["", "## Dependents, level by level", "",
            "| Level | Risk | Node | Via | Resolution | Evidence |", "| --- | --- | --- | --- | --- | --- |"]
    for d in sorted(by_level):
        for n, e, p in sorted(by_level[d], key=lambda x: x[0]):
            out.append("| %d | %s | %s | %s `%s` | %s | `%s` |" % (d, risk(d), label(graph, n), e["type"], graph.nodes.get(p, {}).get("name", p),
                                                               e.get("resolution", ""), e.get("evidence", "")))
    out += ["", "## Data coupling", ""]
    if coupled:
        out += ["| Store | Target | Other code touching it | Evidence |", "| --- | --- | --- | --- |"]
        for c in coupled:
            others = c["others"] or [("(none)", "", "")]
            for source, how, evidence in others:
                out.append("| `%s` | %s | %s %s | %s |" % (graph.nodes.get(c["store"], {}).get("name", c["store"]), "/".join(c["seed_access"]).lower(),
                                                          how.lower(), label(graph, source) if source != "(none)" else source, evidence))
    else:
        out.append("No table or store in the targets' front matter.")
    out += ["", "## What the targets rely on", "", "| From | Edge | To | Evidence |", "| --- | --- | --- | --- |"]
    out += ["| %s | %s | %s | `%s` |" % (graph.nodes.get(s, {}).get("name", s), e["type"], label(graph, e["target"]), e.get("evidence", "")) for s, e in deps] \
        or ["| (none recorded) | | | |"]
    out += ["", "## Outside systems", ""] + (["- " + label(graph, x) for x in externals] or ["None recorded."])
    out += ["", "## Tests", ""]
    out += ["- " + label(graph, t) for t in tests] or ["No test file reaches the radius through the graph."]
    if untested:
        out += ["", "Code targets no test reaches through the graph:", ""] + ["- " + label(graph, u) for u in untested]
    out += ["", "## Analysis pages to update after the change", ""] + \
           ["- `%s`" % graph.nodes[p_]["name"] for p_ in pages] + \
           ["- `lld/api/` cards for: " + ", ".join("`%s`" % graph.nodes[r]["name"] for r in routes) if routes else "- No endpoint card in the radius."]
    out += ["", "## Limits", "",
            "- Calls through dynamic dispatch, callbacks, reflection, string-built names, message queues or another language are not edges: an empty level is not proof of no dependents. Search for the target's name before concluding.",
            "- Edges marked `name-unique` or `analysis` are leads: open their evidence before relying on them.",
            "- The graph describes the code at the date above; the stale-file section lists what changed since.", ""]
    os.makedirs(os.path.dirname(out_md), exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out))
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump({"name": name, "targets": [{"given": t, "matched_as": h, "nodes": f} for t, h, f in matched],
                   "truncated": truncated, "stale": stale,
                   "dependents": [{"node": n, "distance": d, "risk": risk(d), "via": e["type"], "from": p,
                                   "resolution": e.get("resolution"), "evidence": e.get("evidence")}
                                  for n, (d, e, p) in sorted(impacted.items(), key=lambda x: (x[1][0], x[0]))],
                   "components": {c: sorted(v) for c, v in components.items()}, "routes": routes,
                   "data_coupling": [{"store": c["store"], "target_access": c["seed_access"],
                                      "others": [{"node": o[0], "access": o[1], "evidence": o[2]} for o in c["others"]]} for c in coupled],
                   "external": externals, "tests": tests, "untested_targets": untested,
                   "pages_to_update": [graph.nodes[p_]["name"] for p_ in pages]}, handle, indent=1)

    print("ok: %d dependents, %d components, %d routes, %d tests, %d untested targets%s"
          % (len(impacted), len(components), len(routes), len(tests), len(untested), ", TRUNCATED" if truncated else ""))
    if stale:
        print("warning: graph is stale for %d files" % len(stale))
    print("wrote " + os.path.relpath(out_md, repo))
    print("wrote " + os.path.relpath(out_json, repo))


if __name__ == "__main__":
    main()
