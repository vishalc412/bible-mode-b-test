#!/usr/bin/env python3
"""Components of a codebase analysis: the plan, which file belongs where, and calls between components.

Imported by discover.py, next.py and coverage.py; not run on its own.

- The plan is the table (or list) under `## Components` in `<analysis>/progress.md`, which a
  person approves in pass 2. Each component names its folders or files in backticks.
- `<analysis>/components.json` is the catalog discover.py writes from that plan. next.py and
  coverage.py read the catalog, never the free text, so every run agrees on who owns what.
- A file belongs to the component with the longest matching path: `services/` and
  `services/orders/` can both be components. The same path claimed by two components is an error.
- A call from one component into another is found from the code: a call token `name(` inside a
  function of component A, where `name` is defined in exactly one other component B and nowhere
  in A. Common names (`get`, `save`, ...) are ignored, so the list is precise rather than complete;
  a wrong match can be accounted for in `ledger/not-documented.md` as `calls:<name>`.

Standard library only; never imports or runs repository code.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys

sys.dont_write_bytecode = True

CATALOG = "components.json"
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$")  # the label bible/<name> must fit GitHub's 50 characters
WINDOWS_RESERVED = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}
RESERVED = {"api", "data-dictionary"}  # folders under lld/ that every component shares
BACKTICK = re.compile(r"`([^`\n]+)`")
CALL_TOKEN = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
DEFINITION = r"\b(?:def|function|func|fun|sub|class|interface|struct|void|static|public|private|protected)\s+%s\s*\("
COMMENT_LINE = ("#", "//", "/*", "*", "--", ";")
NOT_CALLABLE = ("imports", "table", "view", "paragraph")
# Names too common to say which component is meant. Besides these, a name is skipped when two
# components define it, or one component defines it twice: those are found from the code itself.
COMMON = set("""
get set put post delete patch head options update create remove add clear copy keys values items
append extend insert index count sort reverse pop push shift slice map filter reduce apply call
encode decode format split join strip replace lower upper parse load loads dump dumps read write
open close flush send recv connect disconnect run start stop wait cancel submit execute fetch
commit rollback save exists find search match handle render emit log info debug warning warn error
exception print len str int float bool list dict tuple range type super main init setup teardown
test toString equals hashCode valueOf then catch finally forEach some every require
process transform convert generate build make compute calculate validate check verify ensure
normalize sanitize clean cleanup reset refresh reload retry wrap wrapper decorator helper helpers
util utils configure config get_config load_config settings get_settings get_logger logger
to_dict from_dict to_json from_json as_dict serialize deserialize dict_to_obj read_json write_json
load_json save_json read_file write_file read_yaml load_yaml upload download request response
invoke dispatch notify publish subscribe listen health status ping version
get_client client session get_session get_db db connection get_connection close_connection
async_run run_async gather sleep now timestamp uuid4 hash merge diff clone deepcopy
useState useEffect useMemo useCallback useRef useContext useReducer useLayoutEffect useNavigate
useParams useLocation useSelector useDispatch setState navigate redirect axios json text
createSlice createStore configureStore createContext createRoot forwardRef memo lazy
describe expect beforeEach afterEach beforeAll afterAll mock jest spyOn vi
ref reactive computed watch watchEffect toRef toRefs unref isRef shallowRef readonly nextTick
onMounted onUnmounted onBeforeMount onBeforeUnmount onUpdated onActivated onDeactivated
defineComponent defineProps defineEmits defineExpose defineStore storeToRefs createApp createRouter
createWebHistory useRoute useRouter useStore provide inject mapState mapGetters mapActions mapMutations
mount shallowMount flushPromises
authenticate login logout get_credentials credentials get_token refresh_token deploy provision
migrate list_resources get_resource create_resource delete_resource
""".split())


class PlanError(Exception):
    """The plan in progress.md cannot be used as it is; the message says why."""


def norm(path: str) -> str:
    path = path.replace("\\", "/").strip().strip("`")
    path = path.split(":")[0] if re.search(r":\d", path) else path
    while path.startswith("./"):
        path = path[2:]
    return path


def owned_prefixes(name: str):
    """The analysis paths a component may write while it runs on its own."""
    return ("lld/%s/" % name, "lld/api/%s/" % name, "ledger/components/%s/" % name)


def read_plan_text(analysis_abs: str) -> str:
    """progress.md as text, whatever its encoding (UTF-8, or UTF-16 with a byte-order mark as Windows editors write)."""
    path = os.path.join(analysis_abs, "progress.md")
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError:
        return ""
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", "replace")
    return raw.decode("utf-8-sig", "replace")


def plan_section(text: str):
    match = re.search(r"^##\s+Components\s*$", text, re.M)
    if not match:
        return None
    rest = text[match.end():]
    nxt = re.search(r"^##\s", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def parse_plan(text: str):
    """[(name, [paths])] from the `## Components` section, or None when there is no such section.
    A table needs a column whose header says component and one that says folder, file or path;
    without a table, list lines `- `name`: `path`, `path`` are read instead."""
    section = plan_section(text)
    if section is None:
        return None
    table, bullets, header = [], [], None
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if header is None:
                header = [c.lower() for c in cells]
                continue
            if set("".join(cells)) <= set("-: "):
                continue
            name_col = next((i for i, h in enumerate(header) if "component" in h), None)
            path_col = next((i for i, h in enumerate(header) if any(w in h for w in ("folder", "file", "path"))), None)
            if name_col is None or path_col is None or max(name_col, path_col) >= len(cells):
                continue
            names = BACKTICK.findall(cells[name_col]) or [cells[name_col].strip("* ")]
            table.append((names[0].strip(), [norm(p) for p in BACKTICK.findall(cells[path_col])]))
            continue
        header = None
        match = re.match(r"^[-*]\s+\**`([^`]+)`\**\s*[:—-]\s*(.*)$", stripped)
        if match:
            bullets.append((match.group(1).strip(), [norm(p) for p in BACKTICK.findall(match.group(2))]))
    return table or bullets


def matches(path: str, pattern: str) -> int:
    """How specific the match is (the pattern's length), or -1 when the path is not covered."""
    pattern = pattern.rstrip("/")
    if not pattern:
        return -1
    if any(ch in pattern for ch in "*?["):
        return len(pattern) if fnmatch.fnmatchcase(path, pattern) or fnmatch.fnmatchcase(path, pattern + "/*") else -1
    return len(pattern) if path == pattern or path.startswith(pattern + "/") else -1


def assign(path: str, rows):
    """(component, [other components tied at the same specificity]) for one file."""
    best, ties, length = None, [], -1
    for name, paths in rows:
        score = max([matches(path, p) for p in paths] or [-1])
        if score < 0:
            continue
        if score > length:
            best, ties, length = name, [], score
        elif score == length and name != best:
            ties.append(name)
    return best, ties


def planned_files(files):
    """The files a component plan must place: source files that have lines and are not stylesheets or markup."""
    return [f for f in files if f["kind"] == "source" and not f["binary"] and f["lines"] > 0
            and f["lang"] not in ("css", "html")]


def check_plan(rows, files, skipped=lambda path: False):
    """Raise PlanError listing every problem: bad names, duplicates, overlaps, files with no component."""
    problems, seen = [], set()
    if not rows:
        problems.append("the `## Components` section has no table rows with a component name and its folders or files in backticks")
    for name, paths in rows:
        if not NAME.match(name) or ".." in name or name.endswith((".", ".lock")):
            problems.append("component name `%s`: use 1 to 40 letters, digits, dots, dashes or underscores, no `..`, not ending "
                            "in `.` or `.lock` (it becomes a folder, a branch and a label)" % name)
        if name.lower().split(".")[0] in WINDOWS_RESERVED:
            problems.append("component name `%s` is a reserved device name on Windows: choose another" % name)
        if name.lower() in RESERVED:
            problems.append("component name `%s` is reserved (`lld/%s/` holds every component's pages of that kind): "
                            "choose another, such as `%s-service`" % (name, name.lower(), name))
        if name.lower() in {n.lower() for n in seen} and name not in seen:
            problems.append("component `%s` differs from another only in letter case (folders clash on Windows and macOS)" % name)
        if name in seen:
            problems.append("component `%s` is listed twice" % name)
        seen.add(name)
        if not paths:
            problems.append("component `%s` names no folder or file in backticks" % name)
    owners = {}
    for name, paths in rows:
        for p in paths:
            owners.setdefault(p.rstrip("/"), []).append(name)
    for p, names in sorted(owners.items()):
        if len(set(names)) > 1:
            problems.append("`%s` is claimed by %s" % (p, " and ".join("`%s`" % n for n in sorted(set(names)))))
    unplaced = []
    for f in planned_files(files):
        best, ties = assign(f["path"], rows)
        if ties:
            problems.append("`%s` is claimed by %s at the same level" % (f["path"], " and ".join("`%s`" % n for n in [best] + ties)))
        elif best is None and not skipped(f["path"]):
            unplaced.append(f["path"])
    placed = {assign(f["path"], rows)[0] for f in planned_files(files)}
    for name, paths in rows:
        if paths and name not in placed:
            problems.append("component `%s` has no source file: its paths (%s) match nothing, or another component's longer path "
                            "takes every file" % (name, ", ".join("`%s`" % p for p in paths)))
    if unplaced:
        problems.append("%d source files are not in any component (add them to a component, or list them in "
                        "ledger/not-documented.md with a reason): %s" % (len(unplaced), ", ".join("`%s`" % p for p in unplaced[:20])
                                                                         + (" ..." if len(unplaced) > 20 else "")))
    if problems:
        raise PlanError("\n".join("- " + p for p in problems))


def load_catalog(analysis_abs: str):
    """The catalog dict, or None when discover.py has not written one (or it cannot be read)."""
    path = os.path.join(analysis_abs, CATALOG)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get("components"), list) else None


def rows_of(catalog):
    return [(c["name"], c.get("paths", [])) for c in catalog.get("components", [])]


def component_map(files, rows):
    """{path: component} for every file a component covers."""
    out = {}
    for f in files:
        best, _ties = assign(f["path"], rows)
        if best:
            out[f["path"]] = best
    return out


def cross_calls(repo: str, files, comp_of: dict, is_test=lambda path: False):
    """Calls from a function in one component to a function defined in exactly one other component.
    Each: {component, path, caller, line, target_component, target_path, target, name}."""
    defs = {}
    for f in files:
        comp = comp_of.get(f["path"])
        if not comp:
            continue
        for s in f["symbols"]:
            name = s["name"]
            if s["kind"] in NOT_CALLABLE or name.startswith("__") or len(name) < 3 or name in COMMON or name.lower() in COMMON:
                continue
            defs.setdefault(name, {}).setdefault(comp, []).append((f["path"], s["qualname"]))
    edges, seen = [], set()
    for f in planned_files(files):
        comp = comp_of.get(f["path"])
        if not comp or is_test(f["path"]):
            continue
        callers = [s for s in f["symbols"] if s["kind"] not in NOT_CALLABLE + ("class",)]
        if not callers:
            continue
        try:
            with open(os.path.join(repo, f["path"]), encoding="utf-8", errors="replace") as handle:
                lines = handle.read().splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            if line.lstrip().startswith(COMMENT_LINE):
                continue
            for match in CALL_TOKEN.finditer(line):
                name = match.group(1)
                owners = defs.get(name)
                if not owners or comp in owners:
                    continue
                others = [c for c in owners if c != comp]
                if len(others) != 1 or len(owners[others[0]]) != 1:
                    continue
                if re.search(DEFINITION % re.escape(name), line):
                    continue
                inside = [s for s in callers if s["start"] <= number <= s["end"]]
                if not inside:
                    continue
                caller = min(inside, key=lambda s: s["size"])
                key = (f["path"], caller["qualname"], name, number)
                if key in seen:
                    continue
                seen.add(key)
                target_path, target = owners[others[0]][0]
                edges.append({"component": comp, "path": f["path"], "caller": caller["qualname"], "line": number,
                              "target_component": others[0], "target_path": target_path, "target": target, "name": name})
    return edges
