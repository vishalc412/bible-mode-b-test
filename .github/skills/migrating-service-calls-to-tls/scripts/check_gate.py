"""The deterministic gate for a TLS migration: writes check-result.json.

usage: check_gate.py --repo <repo> [--manifest tls-migration/tls-services.yaml]
                     [--out tls-migration/evidence/check-result.json]
                     [--live [--live-target <host:port> ...]]   (once per endpoint; required outside local)
                     [--policy <tls-policy.yaml>]      (or the environment variable TLS_POLICY)
                     [--tags-file <file>]              (with --live: where the probes' tags go)

It does not trust the run that produced the evidence:
  - certificates are re-checked from the files, not read from certs.json; the
    server certificate must carry every in-scope name;
  - every probe result is re-derived from what was observed, so an edited
    "result" field fails; the set of probes must match the stage, and P7
    (plain HTTP closed) is required at stage 6 on every port plain HTTP was
    ever served on (the manifest's and the ones discovery recorded);
  - recorded probes must be bound to every config source, the producer's code
    and build files, the allowlist, the plans and the certificates as they
    are now (SHA-256), and the chain the
    server presented must be the planned server certificate. Outside the
    local environment, recorded probes never prove anything: re-run with
    --live, which there only accepts an in-scope host as its target;
  - readiness is rebuilt from the access log; a run that relies on a sign-off
    is at best "pass with exceptions"; outside local the policy that sets the
    window comes from the operator (--policy), never from the manifest;
  - the producer config is read the way Spring reads it: every config file of
    the module with its precedence (inside the jar, then outside it; profile
    files in activation order; an import above its importer), profile
    documents, imports, relaxed names, boolean spellings, placeholders and
    deployment overrides; profiles in Spring's order (included ones first, a
    deployment's active list replacing the files'); a resources file nothing
    loads is not read. Where the order Spring applies is not known, every
    value an active source sets is judged. What cannot be read is "not
    proven", never a pass;
  - the report's tables and statistics are checked against the evidence: a
    migrated row counts only on a probe E6 re-derived (or a verify-result),
    for the endpoint the row names;
  - a consumer kit is held against the toolkit (its files re-rendered from
    kit-template) and the plan (endpoint in scope, the planned CAs), never
    only against the manifest that travels with it; every file that is
    trusted is read strictly (CERTIFICATE blocks and nothing else);
  - test reports older than the code they claim to test are stale, and a
    module whose tests were all skipped has not been tested; a service of
    another stack is held against every code and settings file of its folder;
  - every plain-HTTP host the scan finds now must be in the discovery record
    (W4); a server-only row (client_certificate: none) is proven by its own
    evidence file (W1); the report's Total line, percentages, Blocked count,
    Warnings rows and sections are checked (W2, W3); a service E12 cannot read
    (not Spring Boot) is "not run: stack not read (<stack>)" (W5).
A check that crashes is a fail. The result file is written as "fail" before
the first check runs and replaced at the end, so a run that never finishes
cannot leave an older pass behind. Nothing is skipped silently: every file
the scans did not read is listed in the result.

Each check is pass, fail, not run or not applicable. The result:
  fail          any check failed
  not proven    nothing failed, something did not run (never a pass)
  pass with exceptions   all ran and passed; endpoints left on HTTP by
                exception, or consumers accepted by sign-off
  pass
Exit status: 0 pass or pass with exceptions, 1 fail, 2 not proven, 3 bad input.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import os
import re
import shutil
import signal
import sys
import tempfile
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_kit  # noqa: E402
import probe_tls  # noqa: E402
import readiness  # noqa: E402
import scan_rules  # noqa: E402
import tlslib  # noqa: E402

GATE_VERSION = "2.6.0"
HERE = Path(__file__).resolve().parent
TEST_PATH = re.compile(r"(^|/)(src/test|test|tests|__tests__|spec|testdata)/|[._-](test|spec)\.[a-z]+$|Tests?\.java$|IT\.java$")
# Test SOURCE files only. A deployment descriptor called values-test.yaml, or
# kept under deploy/test/, is a deployment descriptor.
SOURCE_TEST = re.compile(r"(^|/)(src/test|__tests__|testdata)/|Tests?\.(java|kt|groovy|scala)$|IT\.(java|kt)$"
                         r"|[._-](test|spec)\.(js|jsx|ts|tsx|mjs|py|go|rb|cs)$|(^|/)test_[^/]+\.py$")
BUILD_FILES = ("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
               "package.json", "go.mod", "pyproject.toml")
LOCALHOSTS = {"localhost", "127.0.0.1", "[::1]", "::1", "0.0.0.0", "host.docker.internal"}
UNREADABLE = "\0unreadable"       # a value the gate can see is set but cannot read


class Check:
    def __init__(self, check_id: str, title: str):
        self.id, self.title = check_id, title
        self.result, self.detail, self.evidence = "not run", "", []
        self.signed_off = 0
        self.live_probes: dict[str, str] | None = None
        # E6's own judgement of each probe the stage requires (re-derived from what was
        # observed), and the host they probed: the only probe results E11 accepts.
        self.derived_probes: dict[str, str] | None = None
        self.probe_target: str | None = None
        # What E6 observed for each probe it judged (timing, protocol, cipher, end date):
        # E11 derives the report's warnings from it.
        self.observed_probes: dict[str, dict[str, Any]] = {}
        # Server-only rows (W1): evidence file -> (host, E6's result, what was observed).
        self.server_only: dict[str, tuple[str, str, dict[str, Any]]] | None = None

    def set(self, result: str, detail: str, evidence: list[Any] | None = None) -> "Check":
        self.result, self.detail = result, detail
        if evidence:
            self.evidence = evidence[:60]
        return self

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "result": self.result, "detail": self.detail, "evidence": self.evidence}


def _p(repo: Path, value: Any, private: bool = False) -> Path:
    """A path a repository file (manifest, plan) names: inside the repository only
    (D3), or under the exported TLS_PRIVATE_DIR for keys (private=True). Raises
    tlslib.OutsideRepo (a ValueError) for ~, an absolute path elsewhere, a .. out
    of the repository or a symbolic link out of it."""
    return tlslib.repo_path(repo, value, private)


def _op(repo: Path, value: Any) -> Path:
    """A path the operator gave on the command line (--policy, --manifest, --out):
    trusted, taken as given; a relative one is relative to the repository."""
    text = os.path.expanduser(str(value))
    return Path(text) if Path(text).is_absolute() else repo / text


def _read(path: Path) -> str:
    """The text of a regular file. A named pipe, socket, device or folder where a
    file is expected raises ValueError instead of blocking the gate."""
    return tlslib.read_regular(path, errors="replace")


def _not_regular(path: Path) -> bool:
    """Something is there, but it is not a regular file (or a link to one)."""
    return os.path.lexists(path) and not path.is_file()


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _rel(repo: Path, path: Path) -> str:
    """A path as evidence shows it: repository-relative, or $TLS_PRIVATE_DIR/...,
    never an absolute path with a user name in it (D5)."""
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return tlslib.shown_path(path, repo)


def _producer(manifest: dict[str, Any]) -> dict[str, Any]:
    value = manifest.get("producer")
    return value if isinstance(value, dict) else {}


def _stage(manifest: dict[str, Any]) -> int:
    return int(_producer(manifest).get("stage", 0))


def _evidence(manifest: dict[str, Any]) -> dict[str, Any]:
    value = manifest.get("evidence")
    return value if isinstance(value, dict) else {}


def quoted(text: Any, limit: int = 120) -> str:
    """Text copied from the repository, marked as such and cut short: it is data
    for a person to look at, never an instruction to whoever reads the result."""
    flat = " ".join(str(text).split())
    return "repo text «" + flat[:limit] + ("…" if len(flat) > limit else "") + "»"


def guarded(check_id: str, title: str, run: Callable[[], Check]) -> Check:
    """A check that raises is a fail with the reason, never a missing line."""
    try:
        return run()
    except Exception as problem:  # noqa: BLE001 - every crash becomes a reported fail
        where = traceback.extract_tb(problem.__traceback__)[-1]
        return Check(check_id, title).set(
            "fail", f"the check could not complete: {type(problem).__name__}: {problem} (line {where.lineno})")


# ---------------------------------------------------------------- scope

class Scope:
    """The in-scope hosts, and the other names the same services answer to."""

    def __init__(self, manifest: dict[str, Any]):
        self.hosts = {str(h).lower().rstrip(".") for h in _list(manifest.get("in_scope_hosts"))}
        self.services: set[tuple[str, str | None]] = set()
        for host in self.hosts:
            parsed = self._service(host)
            if parsed:
                self.services.add(parsed)
        self.namespaces = {namespace for _, namespace in self.services if namespace}
        self.short = {name for name, namespace in self.services if namespace is None}
        self.out_hosts, self.out_files = set(), set()
        for entry in _list(manifest.get("out_of_scope")):
            if isinstance(entry, dict) and entry.get("reason"):
                if entry.get("host"):
                    self.out_hosts.add(str(entry["host"]).lower().rstrip("."))
                if entry.get("file"):
                    self.out_files.add(str(entry["file"]))

    @staticmethod
    def _service(host: str) -> tuple[str, str | None] | None:
        match = re.fullmatch(r"([a-z0-9-]+)(?:\.([a-z0-9-]+)(\.svc(?:\.cluster\.local)?)?)?", host)
        return (match.group(1), match.group(2)) if match else None

    def covers(self, host: Any) -> bool:
        """True for an in-scope host under any of its names: a trailing dot, the
        Kubernetes forms name.namespace, name.namespace.svc and the full one."""
        host = str(host).lower().rstrip(".")
        if host in self.hosts:
            return True
        parsed = self._service(host)
        if not parsed:
            return False
        name, namespace = parsed
        if (name, namespace) in self.services:
            return True
        if name in self.short and namespace:
            return namespace in self.namespaces or ".svc" in host
        return namespace is None and any(name == other for other, _ in self.services)


# ---------------------------------------------------------------- E1 tests

def _module_of(folder: Path, repo: Path) -> Path:
    """The nearest folder above the reports that holds a build file."""
    current = folder if folder.is_dir() else folder.parent
    while True:
        if any((current / name).exists() for name in BUILD_FILES) or any(current.glob("*.csproj")):
            return current
        if current == repo or current.parent == current:
            return folder.parent
        current = current.parent


JAVA_BUILD = {"pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"}
ECOSYSTEM_BUILD = [JAVA_BUILD, {"package.json"}, {"go.mod"}, {"pyproject.toml"}]


def _build_files(module: Path, repo: Path) -> list[Path]:
    """The module's build files and those of every folder above it, up to the
    repository, of the module's own kind: a Java module's tests see the parent
    pom or settings.gradle, never a package.json at the root."""
    own = {name for name in BUILD_FILES if (module / name).is_file()}
    kinds = set().union(*[group for group in ECOSYSTEM_BUILD if group & own]) if own else set(BUILD_FILES)
    found, current = [], module
    while True:
        found += [current / name for name in BUILD_FILES if name in kinds and (current / name).is_file()]
        if current == repo or current.parent == current or repo not in current.parents:
            return found
        current = current.parent


def _xml_root(path: Path) -> ET.Element | None:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None
    for element in root.iter():
        if isinstance(element.tag, str) and "}" in element.tag:
            element.tag = element.tag.split("}", 1)[1]
    return root


_MODULE_INDEX: dict[str, dict[str, Any]] = {}


def module_index(repo: Path) -> dict[str, Any]:
    """The build modules of the repository: Maven modules by the artifactId in
    their own pom.xml (not the folder name), Gradle projects by their path
    (':a:b', nested ones included, projectDir overrides read), and each
    module's groupId."""
    key = str(repo.resolve())
    if key in _MODULE_INDEX:
        return _MODULE_INDEX[key]
    maven: dict[str, Path] = {}
    gradle: dict[str, Path] = {}
    groups: dict[Path, str] = {}
    settings_roots: list[Path] = []
    for path in scan_rules.iter_files(repo):
        if path.name == "pom.xml":
            root = _xml_root(path)
            if root is None:
                continue
            artifact = (root.findtext("artifactId") or "").strip()
            group = (root.findtext("groupId") or root.findtext("parent/groupId") or "").strip()
            if artifact:
                maven.setdefault(artifact, path.parent.resolve())
                groups[path.parent.resolve()] = group
        elif path.name in ("settings.gradle", "settings.gradle.kts"):
            settings_roots.append(path.parent.resolve())
            text = scan_rules.read_text(path) or ""
            for listed in re.findall(r"""(?m)^[ \t]*include\s*(?:\(\s*)?([^\n)]+)""", text):
                for name in re.findall(r"""["']([^"']+)["']""", listed):
                    project = ":" + name.lstrip(":")
                    gradle.setdefault(project, (path.parent / project.strip(":").replace(":", "/")).resolve())
            for project, folder in re.findall(r"""project\(\s*["'](:[^"']+)["']\s*\)\.projectDir\s*=\s*(?:file|new\s+File)\(\s*["']([^"']+)["']""", text):
                gradle[project] = (path.parent / folder).resolve()
    for path in scan_rules.iter_files(repo):
        if path.name in ("build.gradle", "build.gradle.kts"):
            folder = path.parent.resolve()
            root = next((r for r in sorted(settings_roots, key=lambda r: -len(r.parts)) if r == folder or r in folder.parents), None)
            if root is not None and folder != root:
                gradle.setdefault(":" + folder.relative_to(root).as_posix().replace("/", ":"), folder)
    _MODULE_INDEX[key] = {"maven": maven, "gradle": gradle, "groups": groups}
    return _MODULE_INDEX[key]


def module_dependencies(module: Path, repo: Path) -> tuple[list[Path], list[str]]:
    """Modules of this repository the module's build file depends on, directly
    or through each other: (their folders, names that look like a module of
    this repository but cannot be found in it). A Maven <dependency> maps to
    the module whose own pom.xml has that artifactId; Gradle project(':x')
    and projects.x to the project at that path."""
    index = module_index(repo)
    found: list[Path] = []
    unknown: list[str] = []
    queue = [module.resolve()]
    seen = {module.resolve()}
    while queue:
        current = queue.pop(0)
        wanted: list[Path] = []
        pom = current / "pom.xml"
        if pom.is_file():
            root = _xml_root(pom)
            own_group = index["groups"].get(current, "")
            if root is not None:
                for dependency in root.iter("dependency"):
                    artifact = (dependency.findtext("artifactId") or "").strip()
                    group = (dependency.findtext("groupId") or "").strip()
                    if artifact in index["maven"]:
                        wanted.append(index["maven"][artifact])
                    elif artifact and group and (group == own_group or group in ("${project.groupId}", "${groupId}")):
                        unknown.append(f"{_rel(repo, current)} depends on {group}:{artifact}, a module of its own group that is not in "
                                       "the repository")
                for listed in root.iter("module"):
                    folder = (current / (listed.text or "").strip()).resolve()
                    if (folder / "pom.xml").is_file():
                        wanted.append(folder)
            else:
                unknown.append(f"{_rel(repo, pom)} could not be read as XML, so the modules it depends on are not known")
        for name in ("build.gradle", "build.gradle.kts"):
            build = current / name
            if not build.is_file():
                continue
            text = scan_rules.read_text(build) or ""
            projects = re.findall(r"""project\(\s*(?:path\s*[:=]\s*)?["'](:?[^"']+)["']""", text)
            projects += [":" + accessor.replace(".", ":") for accessor in re.findall(r"\bprojects\.([A-Za-z0-9_.]+)", text)]
            for project in projects:
                project = ":" + project.lstrip(":")
                folder = index["gradle"].get(project)
                if folder is None:
                    # Type-safe accessors are camelCase for kebab-case names.
                    folder = next((f for p, f in index["gradle"].items() if tlslib.canonical(p) == tlslib.canonical(project)), None)
                if folder is None:
                    unknown.append(f"{_rel(repo, build)} depends on project {project}, which is not found in the repository")
                else:
                    wanted.append(folder)
        for folder in wanted:
            if folder not in seen:
                seen.add(folder)
                found.append(folder)
                queue.append(folder)
    return found, list(dict.fromkeys(unknown))


def _depended_modules(module: Path, repo: Path) -> list[Path]:
    """Sibling modules this module's build file names: their code is tested by its tests too."""
    return [folder for folder in module_dependencies(module, repo)[0] if (folder / "src").is_dir()]


# The build file that says which stack a service folder is (W5). A JVM build is
# "spring" when Spring Boot is named in it or a build file above it, or when the
# module keeps Spring's application config under src/main/resources.
STACK_MARKERS = (("package.json", "node"), ("go.mod", "go"), ("pyproject.toml", "python"), ("requirements.txt", "python"),
                 ("setup.py", "python"), ("Pipfile", "python"))
JVM_BUILDS = ("pom.xml", "build.gradle", "build.gradle.kts")
DOTNET_GLOBS = ("*.csproj", "*.fsproj", "*.vbproj", "*.sln")
# Files that hold a non-JVM service's code or settings: what its tests must be newer than.
SERVICE_SOURCE = re.compile(r"(?i)\.(js|mjs|cjs|jsx|ts|tsx|py|go|cs|fs|vb|razor|rb|php|rs|json|ya?ml|toml|cfg|ini|properties|"
                            r"env|xml|config|csproj|fsproj|sln|mod|sum|lock|txt)$")
SPRING_STACKS = ("spring",)
STACK_PAGES = {"node": "node.md", "python": "python.md", "go": "go.md", "dotnet": "dotnet.md", "java": "jdk-client.md"}


def _has_stack_marker(folder: Path) -> bool:
    return any((folder / name).is_file() for name in JVM_BUILDS) or any((folder / name).is_file() for name, _ in STACK_MARKERS) \
        or any(True for pattern in DOTNET_GLOBS for _ in folder.glob(pattern))


def service_folder(path: Path, repo: Path) -> Path | None:
    """The nearest folder at or above `path` (inside the repository) with a build
    file of any stack, or None when there is none."""
    current = path if path.is_dir() else path.parent
    repo = repo.resolve()
    current = current.resolve()
    while current == repo or repo in current.parents:
        if _has_stack_marker(current):
            return current
        if current == repo:
            return None
        current = current.parent
    return None


def service_stack(folder: Path, repo: Path) -> str:
    """spring, java (a JVM build without Spring Boot), node, go, python, dotnet, or unknown."""
    if any((folder / name).is_file() for name in JVM_BUILDS):
        resources = folder / "src" / "main" / "resources"
        if resources.is_dir() and any(tlslib.CONFIG_NAME.match(p.name) for p in resources.iterdir()):
            return "spring"
        current = folder.resolve()
        while True:
            for name in JVM_BUILDS:
                text = (scan_rules.read_text(current / name) or "") if (current / name).is_file() else ""
                if "spring-boot" in text or "org.springframework.boot" in text:
                    return "spring"
            if current == repo.resolve() or current.parent == current or repo.resolve() not in current.parents:
                return "java"
            current = current.parent
    if any(True for pattern in DOTNET_GLOBS for _ in folder.glob(pattern)):
        return "dotnet"
    for name, stack in STACK_MARKERS:
        if (folder / name).is_file():
            return stack
    return "unknown"


def producer_stack(repo: Path, manifest: dict[str, Any]) -> tuple[str, Path | None]:
    """The stack of the producer's service folder (that of its first config file)."""
    for item in _list(_producer(manifest).get("config_files")):
        module = _resources_module(repo, item)
        folder = module if module is not None else service_folder(_p(repo, item), repo)
        if folder is not None:
            return service_stack(folder, repo), folder
    return "unknown", None


def other_stack_callers(repo: Path, manifest: dict[str, Any]) -> dict[Path, str]:
    """Service folders of a stack E12 does not read (not Spring) whose code or
    settings call an in-scope host over https: {folder: stack}. In a run with a
    producer, the producer's own names are left out for its own folder."""
    if manifest.get("role") not in ("consumer", "both"):
        return {}
    scope = Scope(manifest)
    stack_of: dict[Path, str] = {}
    found: dict[Path, str] = {}
    _, own_folder = producer_stack(repo, manifest) if manifest.get("role") == "both" else ("", None)
    own = _own_names(manifest)
    for hit in scan_rules.find_https_urls(repo):
        relative = str(hit.get("file", ""))
        if hit.get("doc") or hit.get("comment") or TEST_PATH.search(relative) or relative.startswith(WORKING_PREFIX):
            continue
        host = str(hit.get("host", "")).lower().rstrip(".")
        if not scope.covers(host):
            continue
        folder = service_folder(_p(repo, relative), repo)
        if folder is None or not _service_call_file(relative, folder, repo):
            continue
        if folder not in stack_of:
            stack_of[folder] = service_stack(folder, repo)
        if stack_of[folder] in SPRING_STACKS or stack_of[folder] == "unknown":
            continue
        if own_folder is not None and folder == own_folder.resolve() and own.covers(host):
            continue                                    # the producer naming itself is not a call to a producer
        found.setdefault(folder, stack_of[folder])
    return found


CODE_FILE = re.compile(r"(?i)\.(js|mjs|cjs|jsx|ts|tsx|py|go|cs|fs|vb|rb|php|rs)$")


def _service_call_file(relative: str, folder: Path, repo: Path) -> bool:
    """Whether a file can be a service's own call: its code, or its settings. At the
    repository root (a package.json beside other services, say) only settings at the
    root or in config/ count: deploy files, scripts and docs elsewhere are not that service."""
    if CODE_FILE.search(relative):
        return True
    if folder.resolve() != repo.resolve():
        return True
    parts = Path(relative).parts
    return len(parts) == 1 or (len(parts) == 2 and parts[0] in ("config", "settings"))


def _service_sources(module: Path, repo: Path, reports: list[Path]) -> list[Path]:
    """A non-JVM service's own code and settings: every file under its folder the
    code scan reads (dependency installs and build output are not), but its test
    reports and the run's own records."""
    module = module.resolve()
    held = [r.resolve() for r in reports]
    files = []
    for path in scan_rules.iter_files(repo):
        resolved = path.resolve()
        if module not in resolved.parents or not SERVICE_SOURCE.search(path.name):
            continue
        relative = _rel(repo, path)
        if relative.startswith(WORKING_PREFIX) or any(r == resolved or r in resolved.parents for r in held):
            continue
        files.append(path)
    return files


def _newest_source(module: Path, repo: Path, reports: list[Path] | None = None) -> tuple[float, str]:
    """The newest thing the tests should have seen: the module's sources, its
    build files, and the sources of the sibling modules it depends on. For a
    service of another stack (no src/ tree, or no JVM build): every file of its
    folder that holds code or settings."""
    newest, name = 0.0, ""
    folders = [module] + _depended_modules(module, repo)
    files = list(_build_files(module, repo))
    for folder in folders:
        if (folder / "src").is_dir():
            files += [p for p in (folder / "src").rglob("*") if p.is_file() and not p.name.startswith(".")]
    if not any((module / name).is_file() for name in JVM_BUILDS) and _has_stack_marker(module):
        files += _service_sources(module, repo, reports or [])
    for path in files:
        try:
            moment = path.stat().st_mtime
        except OSError:
            continue
        if moment > newest:
            newest, name = moment, _rel(repo, path)
    return newest, name


def _test_class_exists(report: Path, root: ET.Element, module: Path) -> bool | None:
    """Whether the test class a JUnit-style report names is still in the module.
    None when the report does not name a class this reader can look for."""
    if not report.name.startswith("TEST-"):
        return None
    simple = report.name[5:-4].rsplit(".", 1)[-1]
    if not re.fullmatch(r"[A-Za-z_]\w*", simple) or not (module / "src").is_dir():
        return None
    return any(True for suffix in ("java", "kt", "groovy", "scala") for _ in (module / "src").rglob(f"{simple}.{suffix}"))


REPORT_FOLDERS = ("target/surefire-reports", "target/failsafe-reports", "build/test-results")


def in_scope_modules(repo: Path, manifest: dict[str, Any]) -> list[Path]:
    """The modules whose tests must be in the evidence: the producer's (the
    module of its config files) and every consumer module E12 finds calling an
    in-scope host. The manifest's own list never narrows this."""
    modules: list[Path] = []
    if manifest.get("role") in ("producer", "both"):
        for item in _list(_producer(manifest).get("config_files")):
            module = _resources_module(repo, item)
            if module is not None and module not in modules:
                modules.append(module)
    if manifest.get("role") in ("producer", "both"):
        stack, folder = producer_stack(repo, manifest)
        if stack not in SPRING_STACKS and folder is not None and folder.resolve() not in modules:
            modules.append(folder.resolve())             # another stack: its reports are found through evidence.tests
    if manifest.get("role") in ("consumer", "both"):
        for module, config in consumer_configs(repo, manifest):
            folder = _p(repo, module).resolve()
            if _calls_in_scope(config, client_scope(repo, manifest, module)) and folder not in modules:
                modules.append(folder)
        for folder in other_stack_callers(repo, manifest):
            if folder not in modules:
                modules.append(folder)
    return modules


def check_tests(repo: Path, manifest: dict[str, Any]) -> Check:
    check = Check("E1", "The services' own tests pass, and ran after the last code change")
    folders = [_p(repo, f) for f in _list(_evidence(manifest).get("tests"))]
    total = failed = skipped = 0
    stale, missing, ignored = [], [], []
    # Every in-scope module needs its reports, whether the manifest lists them or not:
    # a module left out of evidence.tests is read from its usual report folders.
    added = []
    try:
        required = in_scope_modules(repo, manifest)
    except Exception as problem:  # noqa: BLE001 - which modules are in scope is E12's finding; here it must not hide the reports
        required = []
        missing.append(f"(the in-scope modules could not be worked out: {type(problem).__name__})")
    for module in required:
        listed = [f for f in folders if f.resolve() == module or module in f.resolve().parents]
        if listed:
            continue
        found = [module / sub for sub in REPORT_FOLDERS if (module / sub).is_dir()]
        if found:
            folders += found
            added += [_rel(repo, f) for f in found]
        else:
            missing.append(f"{_rel(repo, module)} (an in-scope module; the manifest lists no reports for it and none are in "
                           f"{', '.join(REPORT_FOLDERS)})")
    if not folders:
        return check.set("not run", "the manifest lists no test report folders" + (f"; {missing}" if missing else ""))
    executed: dict[Path, int] = {}                 # tests that ran (not skipped), per module
    skipped_names: list[str] = []
    for folder in folders:
        reports = sorted(r for r in folder.rglob("*.xml") if r.is_file()) if folder.is_dir() else ([folder] if folder.is_file() else [])
        if not reports:
            missing.append(_rel(repo, folder))
            continue
        module = _module_of(folder, repo)
        newest_report = max(r.stat().st_mtime for r in reports)
        current = []
        for report in reports:
            try:
                root = ET.parse(report).getroot()
            except ET.ParseError:
                return check.set("fail", f"unreadable test report {report.name}")
            # A report is a leftover only when it is from an earlier run AND the test
            # it names is gone from the module (surefire keeps it until a clean
            # build). Age alone says nothing: a long suite, or one class run again,
            # leaves old reports that still count, failures included.
            if report.stat().st_mtime < newest_report - 600 and _test_class_exists(report, root, module) is False:
                ignored.append(_rel(repo, report))
                continue
            current.append(report)
            suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
            for suite in suites:
                cases = suite.findall("testcase")
                # A skipped test never ran: counted from the attributes or the testcases'
                # own <skipped/> (or <disabled/>), whichever says more.
                skipped_cases = [case for case in cases if case.find("skipped") is not None or case.find("disabled") is not None]
                suite_total = max(_count(suite.get("tests")), len(cases))
                suite_skipped = min(suite_total, max(_count(suite.get("skipped")) + _count(suite.get("disabled")), len(skipped_cases)))
                total += suite_total
                failed += _count(suite.get("failures")) + _count(suite.get("errors"))
                skipped += suite_skipped
                executed[module.resolve()] = executed.get(module.resolve(), 0) + suite_total - suite_skipped
                skipped_names += [f"{case.get('classname') or suite.get('name')}.{case.get('name')}" for case in skipped_cases]
        if not current:
            continue
        newest_source, newest_name = _newest_source(module, repo, [folder])
        if newest_source > min(r.stat().st_mtime for r in current):
            stale.append(f"{module.name} ({newest_name} is newer than its reports)")
    evidence = [f"ignored, the test class is no longer in the module: {', '.join(ignored)}"] if ignored else []
    if added:
        evidence.append(f"read although the manifest does not list them (in-scope modules): {', '.join(added)}")
    evidence.append("the reports' counts are read as written; the XML itself is not verified")
    if skipped:
        evidence.append(f"skipped, not counted as passed ({skipped}): " + ", ".join(skipped_names[:20])
                        + (" …" if len(skipped_names) > 20 else ""))
    # Every in-scope module must have run at least one test: a module whose tests were all
    # skipped (@Disabled, -DskipTests leaving old reports aside) proves nothing about it.
    idle = [_rel(repo, module) for module in required if module in executed and executed[module] == 0]
    if stale:
        return check.set("fail", f"test reports are older than the code or build files in {stale}; run the tests again", evidence)
    if failed:
        return check.set("fail", f"{failed} of {total} tests failed", evidence)
    if missing:
        return check.set("not run", f"no test reports in {missing}", evidence)
    if total == 0:
        return check.set("fail", "the reports hold no tests", evidence)
    if idle:
        return check.set("fail", f"no test ran in the in-scope module(s) {idle}: every test there was skipped", evidence)
    if total - skipped <= 0:
        return check.set("fail", f"no test ran: all {total} were skipped", evidence)
    return check.set("pass", f"{total - skipped} tests ran and passed ({skipped} skipped, not counted)", evidence)


def _count(value: Any) -> int:
    """A count attribute of a test report; one that is not a number raises (a crash is a fail)."""
    return 0 if value is None or str(value).strip() == "" else int(str(value).strip())


# ---------------------------------------------------------------- exceptions, E2

EXCEPTION_URL = re.compile(r"(?i)^http://(?P<host>[a-z0-9_.\-]+|\[[0-9a-f:]+\])(?::(?P<port>\d+))?(?P<path>/[^\s]*)?$")


def load_exceptions(repo: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    path = _p(repo, manifest.get("exceptions", "tls-migration/exceptions.yaml"))
    if not path.exists():
        return [], []
    try:
        data = tlslib.load_yaml(path) or {}
    except ValueError as problem:
        return [], [f"exceptions.yaml unreadable: {problem}"]
    entries = data.get("exceptions") if isinstance(data, dict) else data
    scope = Scope(manifest)
    producer_run = manifest.get("role") in ("producer", "both")
    try:
        old_ports = legacy_ports(repo, manifest) if producer_run else []
    except Exception:  # noqa: BLE001 - this runs outside the guarded checks: never crash, keep the default port
        old_ports = ["8080"]
    own = _own_names(manifest) if producer_run else Scope({})
    try:
        stage = _stage(manifest) if producer_run else 0
    except (TypeError, ValueError):
        stage = 0                                     # E0 fails a stage that is not a number
    valid, problems = [], []
    today = tlslib.now_utc().date()
    for entry in _list(entries):
        if not isinstance(entry, dict):
            problems.append(f"not a mapping: {entry!r}")
            continue
        missing = [k for k in ("url", "reason", "owner", "review_date") if not entry.get(k)]
        if missing:
            problems.append(f"{entry.get('url', '?')}: missing {missing}")
            continue
        match = EXCEPTION_URL.match(str(entry["url"]).strip())
        if not match:
            problems.append(f"{entry['url']}: an exception must name one http:// host (and optionally a port and path)")
            continue
        host, port = match.group("host").lower().rstrip("."), match.group("port") or ""
        # The producer's old plain-HTTP address on this machine is the producer, as E2 reads it.
        old_address = host in LOCALHOSTS and bool(old_ports) and port in old_ports + [""]
        # The plan's own names for the producer (its probe target, its certificate's names), in every environment.
        if producer_run and not old_address:
            try:
                old_address = producer_answers(repo, manifest, host, port)
            except Exception:  # noqa: BLE001 - this runs outside the guarded checks: never crash
                old_address = False
        approver = str(entry.get("approved_by") or "").strip()
        if (scope.covers(host) or old_address) and not approver:
            problems.append(f"{entry['url']}: an in-scope host left on HTTP also needs approved_by, a second person")
            continue
        if approver and approver.lower() == str(entry["owner"]).strip().lower():
            problems.append(f"{entry['url']}: approved_by is the owner; the approval must come from a second person")
            continue
        if stage >= 6 and (own.covers(host) or old_address):
            problems.append(f"{entry['url']}: at stage 6 the producer serves no plain HTTP (P7 proves it closed); an exception "
                            "cannot leave the producer itself on HTTP")
            continue
        try:
            review = dt.date.fromisoformat(str(entry["review_date"]))
        except ValueError:
            problems.append(f"{entry['url']}: review_date is not YYYY-MM-DD")
            continue
        if review < today:
            problems.append(f"{entry['url']}: review date {review} has passed")
            continue
        valid.append(dict(entry, _host=match.group("host").lower().rstrip("."), _port=match.group("port") or "",
                          _path=match.group("path") or "/"))
    return valid, problems


def _own_names(manifest: dict[str, Any]) -> Scope:
    """The producer's own names among in_scope_hosts: those whose first label is
    producer.name (all of them in a producer run, or when no name is given)."""
    scope = Scope(manifest)
    name = str(_producer(manifest).get("name") or "").lower()
    own = [h for h in scope.hosts if h.split(".")[0] == name] if name else []
    if not own and (manifest.get("role") == "producer" or not name):
        own = sorted(scope.hosts)
    return Scope({"in_scope_hosts": own})


def _excepted(hit: dict[str, Any], exceptions: list[dict[str, Any]]) -> bool:
    path = str(hit.get("url", ""))
    path = "/" + path.split("://", 1)[1].split("/", 1)[1] if "/" in path.split("://", 1)[-1] else "/"
    for entry in exceptions:
        if hit["host"] != entry["_host"] or (entry["_port"] and str(hit.get("port") or "") != entry["_port"]):
            continue
        if not path.startswith(entry["_path"]):
            continue
        if not entry.get("files") or hit["file"] in [str(f) for f in _list(entry["files"])]:
            return True
    return False


def _discovery(repo: Path, manifest: dict[str, Any]) -> list[dict[str, Any]] | None:
    """The plain-HTTP addresses tls-inventory.sh recorded before anything changed."""
    path = _p(repo, _evidence(manifest).get("inventory", "tls-migration/evidence/inventory.json"))
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except ValueError:
        return None
    urls = data.get("http_urls") if isinstance(data, dict) else None
    return [u for u in urls if isinstance(u, dict) and u.get("host")] if isinstance(urls, list) else None


def legacy_ports(repo: Path, manifest: dict[str, Any]) -> list[str]:
    """Every port plain HTTP may still be served on, the manifest's (or the
    config's, or 8080) first, then the ports discovery recorded for in-scope
    hosts. The manifest alone never decides which port P7 proves closed."""
    producer = _producer(manifest)
    ports: list[str] = []
    if producer.get("legacy_http_port"):
        ports.append(str(producer["legacy_http_port"]))
    try:
        configured = producer_settings(repo, manifest)[0].find("tls.migration.legacy-http.port")
    except Exception:  # noqa: BLE001 - an unreadable config is E12's finding; here it only means "no port from config"
        configured = ""
    if str(configured).isdigit() and str(configured) not in ports:
        ports.append(str(configured))
    if not ports:
        ports.append("8080")
    scope = Scope(manifest)
    for found in _discovery(repo, manifest) or []:
        port = str(found.get("port") or "")
        if port.isdigit() and port not in ports and scope.covers(found.get("host")) and not found.get("doc") \
                and not TEST_PATH.search(str(found.get("file", ""))):
            ports.append(port)
    return ports


def _legacy_port(repo: Path, manifest: dict[str, Any]) -> str:
    return legacy_ports(repo, manifest)[0]


def _own_port(repo: Path, manifest: dict[str, Any], relative: str) -> str | None:
    """The port a service's own image serves, for a Dockerfile in a Spring module that
    is not the producer's: its server.port (Spring's 8080 when none is set). A
    HEALTHCHECK there calls the container itself on localhost. None otherwise:
    anywhere else, localhost on the producer's old port may be the producer."""
    name = Path(relative).name.lower()
    if not name.startswith(("dockerfile", "containerfile")):
        return None
    module = _module_of(_p(repo, relative), repo).resolve()
    if module == repo.resolve():
        return None
    for item in _list(_producer(manifest).get("config_files")):
        if _resources_module(repo, item) == module:
            return None
    resources = module / "src" / "main" / "resources"
    files = sorted(p for p in resources.iterdir() if tlslib.CONFIG_NAME.match(p.name)) if resources.is_dir() else []
    plain = [p for p in files if "-" not in p.name] or files
    if not plain:
        return None
    try:
        config = ProducerConfig(repo, manifest, listed=[_rel(repo, plain[0])])
        settings = config.resolve(config.base_profiles, config.base_order if config.base_orders else None)
    except Exception:  # noqa: BLE001 - when the module's config cannot be read, nothing is excused
        return None
    if config.unreadable:
        return None
    value = str(settings.find("server.port") or "8080").strip()
    return value if value.isdigit() else None


def check_http_left(repo: Path, manifest: dict[str, Any], exceptions: list[dict[str, Any]]) -> Check:
    check = Check("E2", "No plain http:// to an in-scope endpoint left, except those in exceptions.yaml")
    scope = Scope(manifest)
    if not scope.hosts:
        return check.set("fail", "the manifest lists no in_scope_hosts; the gate cannot tell which endpoints had to move")
    old_ports = legacy_ports(repo, manifest) if manifest.get("role") in ("producer", "both") else []
    failing, review = [], []
    hits = scan_rules.find_http_urls(repo)
    for hit in hits:
        if _excepted(hit, exceptions):
            continue
        host = str(hit["host"]).split(":")[0] if not str(hit["host"]).startswith("[") else str(hit["host"])
        port = str(hit.get("port") or "")
        where = f"{hit['file']}:{hit['line']} {quoted(hit['url'], 90)}"
        kind = hit.get("kind", "url")
        soft = bool(TEST_PATH.search(str(hit["file"]))) or hit.get("doc") or hit.get("comment") or hit["file"] in scope.out_files
        if kind in ("url", "scheme-key") and scope.covers(host):
            failing.append(where)                      # an endpoint that had to move, anywhere, docs included
        elif soft or host in scope.out_hosts:
            review.append(where)
        elif kind == "templated":
            failing.append(where + "  (the host is filled in at run time: cannot be told from an in-scope endpoint)")
        elif kind == "built":
            failing.append(where + "  (a plain-HTTP address put together at run time: cannot be told from an in-scope endpoint)")
        elif host in LOCALHOSTS and old_ports and port in old_ports + [""] and _own_port(repo, manifest, str(hit["file"])) == port:
            review.append(where + "  (the image's own port: this module's server.port is " + port + ")")
        elif host in LOCALHOSTS and old_ports and port in old_ports + [""]:
            failing.append(where + "  (cannot be told from the producer's old HTTP address)")
        else:
            review.append(where)
    # in_scope_hosts is written by the run itself. What discovery recorded before
    # anything changed says which hosts were called over plain HTTP: each must be
    # in scope, an exception, or named out_of_scope with a reason.
    discovered = _discovery(repo, manifest)
    excepted_hosts = {entry["_host"] for entry in exceptions}
    left_out: dict[str, str] = {}
    for found in discovered or []:
        host = str(found["host"]).lower().rstrip(".")
        if found.get("doc") or found.get("comment") or TEST_PATH.search(str(found.get("file", ""))) or host[:1] in "${%[" \
                or host in LOCALHOSTS:
            continue
        if not (scope.covers(host) or host in scope.out_hosts or host in excepted_hosts):
            left_out.setdefault(host, f"{found.get('file')}:{found.get('line')}")
    for host, where in sorted(left_out.items()):
        failing.append(f"discovery recorded plain HTTP to {host} ({where}); it is not in in_scope_hosts, not an exception, "
                       "and not listed under out_of_scope with a reason")
    # W4 (Q-08): every plain-HTTP host the scan finds now must be in the record made
    # before anything changed, or the comparison above never saw it. Excepted and
    # out-of-scope hosts too: an exception does not stand in for the inventory.
    if discovered is not None:
        recorded = {str(found["host"]).lower().rstrip(".") for found in discovered}
        unrecorded: dict[str, str] = {}
        for hit in hits:
            host = str(hit["host"]).lower().rstrip(".")
            if host not in recorded:
                host = host.split(":")[0] if not host.startswith("[") else host
            if hit.get("kind", "url") not in ("url", "scheme-key") or hit.get("doc") or hit.get("comment") \
                    or TEST_PATH.search(str(hit.get("file", ""))) or host[:1] in "${%[" or host in LOCALHOSTS \
                    or host in recorded or scope.covers(host):
                continue
            unrecorded.setdefault(host, f"{hit['file']}:{hit['line']}")
        for host, where in sorted(unrecorded.items()):
            failing.append(f"found by scan, missing from inventory: {host} ({where}); every plain-HTTP host must be in "
                           "the discovery record (evidence/inventory.json) and classified there")
    if failing:
        return check.set("fail", f"{len(failing)} plain http:// finding(s) for in-scope endpoints outside exceptions.yaml", failing + review)
    if discovered is None:
        return check.set("not run", "no readable discovery record (tls-migration/evidence/inventory.json from tls-inventory.sh): "
                         "in_scope_hosts cannot be compared with what was found before the migration", review)
    detail = "none left to in-scope hosts" + (f"; {len(review)} other http:// URL(s) listed for review" if review else "")
    return check.set("pass", detail, review)


# ---------------------------------------------------------------- E3, E4

def check_verify_off(repo: Path) -> Check:
    check = Check("E3", "No known way of switching certificate checking off is in the code or config")
    hits = scan_rules.find_verify_off(repo)
    failing = [f"{h['file']}:{h['line']} [{h['rule']}] {quoted(h['text'])}" for h in hits if h["severity"] == "fail"]
    review = [f"{h['file']}:{h['line']} [{h['rule']}, review] {quoted(h['text'])}" for h in hits if h["severity"] != "fail"]
    if failing:
        return check.set("fail", f"{len(failing)} place(s) switch checking off or allow old protocols", failing + review)
    detail = ("none of the known patterns (trust-all, hostname check off, verify=False, -k and the like) found; "
              "pattern matching cannot prove checking is on, the verification judge reads the code")
    return check.set("pass", detail + (f"; {len(review)} mention(s) in docs or comments listed for review" if review else ""), review)


def check_keys(repo: Path) -> Check:
    check = Check("E4", "No private key or key store in the repository")
    hits = scan_rules.find_private_keys(repo)
    failing = [f"{h['file']}:{h['line']} {h['reason']}" for h in hits if h.get("severity", "fail") == "fail"]
    # A third-party package's own test key, inside a recognisable dependency
    # install and matching nothing the migration planned: listed, never hidden.
    review = [f"{h['file']}:{h['line']} [review] {h['reason']}" for h in hits if h.get("severity", "fail") != "fail"]
    if failing:
        return check.set("fail", f"{len(failing)} key or key-store file(s) in the tree", failing + review)
    return check.set("pass", "no key files, key stores or encoded PRIVATE KEY blocks anywhere but .git: dependency folders, "
                     "build output, archives and tls-migration/ included"
                     + (f"; {len(review)} key(s) shipped inside installed dependencies listed for review" if review else ""), review)


# ---------------------------------------------------------------- E5, E7

LOCAL_RENEW_FLOOR_DAYS = 7          # local-tls-up.sh plans 7; a local plan never goes below it
DEFAULT_RENEW_BEFORE_DAYS = 21
DEFAULT_LIFETIME_DAYS = 90


def cert_limits(repo: Path, manifest: dict[str, Any], operator_policy: str | None) -> tuple[dict[str, int], str]:
    """The renewal margin and lifetimes E5 holds certificates to, and where they come
    from. Outside local they come from the operator's policy (--policy), as E8's
    window does: certificates.renew_before_days, server_lifetime_days and
    client_lifetime_days, or the toolkit's defaults (21, 90) without one. In local,
    from the policy the manifest names, with a floor of 7 days. The run's own
    certificate plan may be stricter, never looser."""
    local = manifest.get("environment") == "local"
    path = None
    if local:
        path = _op(repo, operator_policy) if operator_policy else _p(repo, manifest.get("policy", "tls-policy.yaml"))
    elif operator_policy:
        path = Path(os.path.expanduser(operator_policy))
    certificates: dict[str, Any] = {}
    source = "the toolkit's defaults"
    if path is not None and path.is_file():
        try:
            policy = tlslib.load_yaml(path) or {}
        except ValueError:
            policy = {}
        if isinstance(policy, dict) and isinstance(policy.get("certificates"), dict):
            certificates = policy["certificates"]
            source = f"the policy {_rel(repo, path)}"

    def number(key: str, default: int) -> int:
        try:
            return int(certificates.get(key, default))
        except (TypeError, ValueError):
            return default
    # Local certificates live 30 days (local-tls-up.sh), so a laptop keeps the 7-day floor, not the policy's margin.
    renew = LOCAL_RENEW_FLOOR_DAYS if local else max(number("renew_before_days", DEFAULT_RENEW_BEFORE_DAYS), 0)
    return {"min_renew_before_days": renew,
            "max_server_lifetime_days": number("server_lifetime_days", DEFAULT_LIFETIME_DAYS),
            "max_client_lifetime_days": number("client_lifetime_days", DEFAULT_LIFETIME_DAYS)}, source


def rerun_cert_check(repo: Path, manifest: dict[str, Any], operator_policy: str | None = None) -> dict[str, Any] | None:
    plan = manifest.get("cert_plan")
    if not plan or not _p(repo, plan).exists():
        return None
    limits, source = cert_limits(repo, manifest, operator_policy)
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "certs.json"
        code, stdout, stderr = tlslib.run(
            [sys.executable, "-I", "-B", str(HERE / "cert_check.py"), "--repo", str(repo), "--plan", str(plan), "--out", str(out),
             "--environment", str(manifest.get("environment")),
             "--min-renew-before-days", str(limits["min_renew_before_days"]),
             "--max-server-lifetime-days", str(limits["max_server_lifetime_days"]),
             "--max-client-lifetime-days", str(limits["max_client_lifetime_days"])],
            timeout=180,
        )
        if not out.exists():
            return {"error": (stderr or stdout).strip()[:300]}
        data = json.loads(out.read_text())
        data["limits_source"] = source
        return data


def _cert_plan(repo: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    plan = manifest.get("cert_plan")
    if not plan or not _p(repo, plan).is_file():
        return {}
    try:
        data = tlslib.load_yaml(_p(repo, plan)) or {}
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _wrong_environment_ca(names: list[Any], environment: Any) -> str | None:
    """A throw-away CA outside the environment it was made for."""
    for name in names:
        text = str(name or "")
        if text.startswith("local-dev-") and environment != "local":
            return text
        if text.startswith("test-") and environment not in ("local", "test"):
            return text
    return None


def _names_to_cover(repo: Path, manifest: dict[str, Any]) -> list[str]:
    """The names the producer's server certificate must carry: the in-scope hosts
    (those of this producer, when the manifest names it) and every in-scope
    address the tree is configured to call over https."""
    scope = Scope(manifest)
    name = str(_producer(manifest).get("name") or "").lower()
    own = sorted(h for h in scope.hosts if h.split(".")[0] == name) or sorted(scope.hosts)
    dialled = sorted({str(hit["host"]) for hit in scan_rules.find_https_urls(repo)
                      if scope.covers(hit["host"]) and not hit.get("doc") and not hit.get("comment")
                      and (not name or str(hit["host"]).split(".")[0] == name)})
    return list(dict.fromkeys(own + dialled))


def check_certificates(repo: Path, manifest: dict[str, Any], rerun: dict[str, Any] | None) -> Check:
    check = Check("E5", "Every certificate is right for its role (re-checked from the files)")
    if rerun is None:
        return check.set("not run", "no cert_plan in the manifest, or the plan file is missing; for staging and production, "
                         "export the public certificates from the platform (verify-and-report.md)")
    if "error" in rerun:
        return check.set("fail", f"the certificate plan could not be checked: {rerun['error']}")
    role = manifest.get("role")
    environment = manifest.get("environment")
    roles = {c.get("role") for c in rerun.get("certificates", [])}
    gaps = []
    if rerun.get("plan_environment") != environment:
        gaps.append(f"the certificate plan says environment {rerun.get('plan_environment')}, "
                    f"the manifest says {environment}")
    if role in ("producer", "both") and "server" not in roles:
        gaps.append("no server certificate in the plan for the producer")
    if role in ("consumer", "both") and "client" not in roles:
        gaps.append("no client certificate in the plan for the consumer")
    problems = [
        f"{item['path']}: {name}: {c['detail']}"
        for item in rerun.get("certificates", []) + rerun.get("trust_stores", [])
        for name, c in item["checks"].items() if c["result"] == "fail" and name not in ("scope", "all_ca", "planned_ca")
    ]
    # A CA made for a laptop or a test run never vouches for another environment.
    for item in rerun.get("certificates", []):
        wrong = _wrong_environment_ca([item.get("issuer_cn"), item.get("subject_cn")], environment)
        if wrong:
            problems.append(f"{item['path']}: issued by {wrong}, a throw-away CA that is not valid in {environment}")
    for item in rerun.get("trust_stores", []):
        wrong = _wrong_environment_ca(_list(item.get("contains")), environment)
        if wrong:
            problems.append(f"{item['path']}: holds {wrong}, a throw-away CA that is not valid in {environment}")
    # The server certificate must carry every name consumers use, not only the
    # names the plan chose to list.
    if role in ("producer", "both"):
        needed = _names_to_cover(repo, manifest)
        for item in rerun.get("certificates", []):
            if item.get("role") != "server" or "readable" in item["checks"] and item["checks"]["readable"]["result"] == "fail":
                continue
            try:
                san = tlslib.cert_info(_p(repo, item["path"]))["san"]
            except (OSError, ValueError):
                continue
            uncovered = [n for n in needed if not tlslib.name_covered(n, san)]
            if uncovered:
                problems.append(f"{item['path']}: does not carry the in-scope name(s) {uncovered} that consumers call")
    recorded_path = _p(repo, _evidence(manifest).get("certs", "tls-migration/evidence/certs.json"))
    if recorded_path.is_file():
        try:
            recorded = json.loads(_read(recorded_path))
        except ValueError:
            recorded = {}
        if isinstance(recorded, dict) and recorded.get("failures", 0) == 0 and problems:
            problems.insert(0, "recorded certs.json says no failures, but the re-check finds some")
    if gaps or problems:
        return check.set("fail", "; ".join(gaps) or f"{len(problems)} certificate problem(s)", gaps + problems)
    limits = rerun.get("limits") or {}
    return check.set("pass", f"{rerun.get('certificate_count')} certificate(s) re-checked: usage, names (every in-scope name), "
                     "chain, validity, key", [f"limits: more than {limits.get('renew_before_days')} day(s) left, lifetime at most "
                                              f"{limits.get('max_server_lifetime_days')} (server) / {limits.get('max_client_lifetime_days')} "
                                              f"(client) days, from {rerun.get('limits_source')}; the plan can be stricter, not looser"])


def check_trust_scope(repo: Path, manifest: dict[str, Any], rerun: dict[str, Any] | None) -> Check:
    check = Check("E7", "Trust stores hold only the planned CA, and each service is configured to trust its planned store")
    if rerun is None or "error" in rerun:
        return check.set("not run", "no certificate plan could be checked")
    if not rerun.get("trust_stores"):
        return check.set("not run", "the plan lists no trust stores")
    violations = [
        f"{item['path']}: {c['detail']}" for item in rerun["trust_stores"]
        for name, c in item["checks"].items() if name in ("scope", "all_ca", "planned_ca", "readable") and c["result"] == "fail"
    ]
    if any("planned_ca" not in item["checks"] for item in rerun["trust_stores"] if "readable" not in item["checks"]
           or item["checks"]["readable"]["result"] == "pass"):
        violations.append("the certificate check did not compare the trust stores by fingerprint (an older cert_check.py?)")
    # A store the plan lists is only half of it: the store each service's own
    # configuration names, under every profile and override, must be the planned
    # one for its side - not a system store, not the other side's CA.
    configured, evidence = configured_trust_problems(repo, manifest, rerun)
    if violations or configured:
        return check.set("fail", "; ".join(([f"{len(violations)} trust store(s) wider than planned"] if violations else [])
                                           + configured[:2]), violations + configured + evidence)
    return check.set("pass", f"{len(rerun['trust_stores'])} trust store(s) hold exactly the planned CA, by name and fingerprint; "
                     f"{len(evidence)} configured trust setting(s) point at the planned store for their side", evidence)


# ---------------------------------------------------------------- E6

def _probe_plan(repo: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    plan = manifest.get("probe_plan")
    if plan and os.path.lexists(_p(repo, plan)):
        return tlslib.load_yaml(_p(repo, plan)) or {}
    return {}


def _server_fingerprints(rerun: dict[str, Any] | None) -> set[str]:
    return {str(c.get("fingerprint_sha256")) for c in (rerun or {}).get("certificates", [])
            if c.get("role") == "server" and c.get("fingerprint_sha256")}


def _is_loopback(host: Any) -> bool:
    """True for a name or address of this machine (probe_tls.is_loopback)."""
    return probe_tls.is_loopback(host)


is_loopback = _is_loopback


def live_host_allowed(manifest: dict[str, Any], host: Any) -> bool:
    """The gate's rule for any host --live connects to, the same one probe-tls.sh
    applies on every run (probe_tls.host_problem): one of in_scope_hosts (under
    any of its names) that is not this machine, or, in a local run only, this
    machine; never a link-local or cloud metadata address. Pure: reads nothing,
    connects to nothing."""
    return probe_tls.host_problem(host, manifest, manifest.get("environment")) is None


def parse_live_target(value: Any) -> tuple[str, int] | None:
    """--live-target host:port ([v6 address]:port), or None when it cannot be read."""
    text = str(value or "").strip()
    match = re.fullmatch(r"\[([0-9A-Fa-f:.]+)\]:(\d{1,5})|([A-Za-z0-9.\-]+):(\d{1,5})", text)
    if not match:
        return None
    host = (match.group(1) or match.group(3)).lower().rstrip(".")
    port = int(match.group(2) or match.group(4))
    return (host, port) if 1 <= port <= 65535 else None


def live_target_problem(manifest: dict[str, Any], live_target: str | list[str] | None, host: Any, port: Any,
                        what: str) -> str | None:
    """Outside local the operator confirms where --live connects: --live-target
    host:port must be given and equal the target the repository's files name
    (A-09). In local it is optional; given, it must match too. The option may be
    given once per endpoint the run connects to (a producer's probe plan target,
    a kit's endpoint, a server-only row); each connection must equal one of them."""
    environment = manifest.get("environment")
    given = [str(value) for value in _list(live_target) if str(value or "").strip()]
    if not given:
        if environment == "local":
            return None
        return (f"outside a local run --live connects only where the operator says: run check.sh --live "
                f"--live-target <host:port> after checking that {what} is the endpoint; no probe was sent")
    parsed = []
    for value in given:
        target = parse_live_target(value)
        if target is None:
            return f"--live-target {quoted(value, 60)} is not host:port; no probe was sent"
        parsed.append(target)
    try:
        wanted = (str(host).lower().strip("[]").rstrip("."), int(str(port)))
    except ValueError:
        return f"{what} has no usable port; no probe was sent"
    if wanted not in parsed:
        shown = ", ".join(f"{h}:{p}" for h, p in parsed)
        return (f"--live-target {shown} is not the target the repository names ({what}: "
                f"{wanted[0]}:{wanted[1]}); no probe was sent")
    return None


def _live_url_problem(manifest: dict[str, Any], url: Any) -> str | None:
    """Why --live must not fetch this URL (the probe plan's health.url), or None:
    only http or https, no user-info, and a host the target rule allows."""
    from urllib.parse import urlsplit  # noqa: PLC0415

    text = str(url or "")
    if not text or re.search(r"\s", text):
        return f"health.url {quoted(text, 60)} is empty or holds white space"
    try:
        parts = urlsplit(text)
        host = parts.hostname or ""
        parts.port  # noqa: B018 - raises ValueError for a port that is not a number
    except ValueError:
        return f"health.url {quoted(text, 60)} is not a URL"
    if parts.scheme not in ("http", "https"):
        return f"health.url uses '{parts.scheme or '?'}'; only http and https are fetched"
    if parts.username is not None or "@" in parts.netloc:
        return "health.url carries user-info before the host"
    if not live_host_allowed(manifest, host):
        return (f"health.url host '{host}' is not one of in_scope_hosts"
                + (" (or this machine, in a local run)" if manifest.get("environment") == "local" else ""))
    return None


def _p1_problems(repo: Path, plan: dict[str, Any], p1: dict[str, Any] | None, rerun: dict[str, Any] | None) -> list[str]:
    """P1 proves the allowed consumer is served: a 2xx answer, the same answer as
    the baseline recorded before the migration for that path, and a client
    certificate that is a planned client certificate or the probe identity
    tls-probe-allowed."""
    if p1 is None:
        return []
    problems = []
    expected = str(p1.get("expected", ""))
    observed = p1.get("observed") or {}
    if not re.fullmatch(r"status:2\d\d", expected):
        problems.append(f"P1 expects '{expected}': the allowed consumer must get a 2xx answer")
    if observed.get("body_matches_baseline") is not True:
        problems.append("P1 was not compared with a baseline covering its path (probe plan 'baseline:', recorded before "
                        "anything changed)" if "body_matches_baseline" not in observed else "P1 differs from the baseline")
    cert = (plan.get("allowed_client") or {}).get("cert")
    if not cert:
        problems.append("the probe plan names no allowed_client certificate for P1")
        return problems
    try:
        info = tlslib.cert_info(_p(repo, cert, private=True))
    except (OSError, ValueError) as problem:
        problems.append(f"P1's client certificate {cert} cannot be read: {problem}")
        return problems
    if info["fingerprint_sha256"] not in _client_fingerprints(rerun) and info.get("subject_cn") != "tls-probe-allowed":
        problems.append(f"P1's client certificate {cert} (CN={info.get('subject_cn')}) is neither a planned client "
                        "certificate nor the probe identity tls-probe-allowed")
    used = observed.get("client_cert_sha256")
    if used and used != info["fingerprint_sha256"]:
        problems.append("P1 was sent with another client certificate than the probe plan names")
    return problems


def _probe_cert_problems(repo: Path, plan: dict[str, Any], data: dict[str, Any], seen: dict[str, dict[str, Any]]) -> list[str]:
    """The probe certificates the run says it used (probe_certificates, and P3's and
    P4's client_cert_sha256) against the plan's own: the probe-untrusted.crt and
    probe-unlisted.crt in its probe_certs folder, when that folder is here."""
    folder = plan.get("probe_certs")
    try:
        if not folder or not _p(repo, folder, private=True).is_dir():
            return []
    except ValueError:
        return []
    problems = []
    recorded = data.get("probe_certificates") if isinstance(data.get("probe_certificates"), dict) else {}
    for name, case_id in (("probe-untrusted", "P3"), ("probe-unlisted", "P4")):
        path = _p(repo, folder, private=True) / f"{name}.crt"
        if not path.is_file():
            continue
        try:
            planned = tlslib.cert_info(path)["fingerprint_sha256"]
        except (OSError, ValueError):
            continue
        listed = (recorded.get(name) or {}).get("sha256") if isinstance(recorded.get(name), dict) else None
        used = ((seen.get(case_id) or {}).get("observed") or {}).get("client_cert_sha256")
        if listed and listed != planned:
            problems.append(f"probe_certificates says {name} was {listed[:16]}…, not the plan's {name}.crt; probe again")
        if used and used != planned:
            problems.append(f"{case_id} was sent with another certificate than the plan's {name}.crt; probe again")
    return problems


def server_only_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Consumer-side rows for an HTTPS endpoint that asks for no client certificate
    (W1): consumers_of_others entries with client_certificate: none."""
    return [entry for entry in _list(manifest.get("consumers_of_others"))
            if isinstance(entry, dict) and str(entry.get("client_certificate", "")).strip().lower() == "none"]


def producer_addresses(repo: Path, manifest: dict[str, Any]) -> tuple[Scope, set[str], set[str]]:
    """The producer's names beyond _own_names, in every environment: (host names,
    addresses, ports). Host names: the DNS names of the producer's planned server
    certificate (cert plan, role server) and the probe plan's expected_names and
    target host. Addresses (IP literals and this machine's names): the same
    sources; they count only on the producer's own ports (the probe plan's
    https_port and every plain-HTTP port it served), since other services can
    share a machine."""
    names: list[str] = []
    for entry in _list(_cert_plan(repo, manifest).get("certificates")):
        if isinstance(entry, dict) and str(entry.get("role", "")).lower() == "server":
            names += [str(n) for n in _list(entry.get("names"))]
    ports: set[str] = set()
    try:
        target = _probe_plan(repo, manifest).get("target") or {}
    except ValueError:
        target = {}
    if isinstance(target, dict):
        names += [str(n) for n in _list(target.get("expected_names"))]
        if target.get("host"):
            names.append(str(target["host"]))
        if str(target.get("https_port") or "").isdigit():
            ports.add(str(target["https_port"]))
        if str(target.get("http_port") or "").isdigit():
            ports.add(str(target["http_port"]))
    try:
        ports.update(legacy_ports(repo, manifest))
    except Exception:  # noqa: BLE001 - this runs outside the guarded checks: never crash, keep what is known
        ports.add("8080")
    hosts, addresses = set(), set()
    for name in names:
        name = name.lower().strip().strip("[]").rstrip(".")
        if not name:
            continue
        if probe_tls._address(name) is not None or _is_loopback(name):
            addresses.add(tlslib._normalise_ip(name))
        else:
            hosts.add(name)
    return Scope({"in_scope_hosts": sorted(hosts)}), addresses, ports


def producer_answers(repo: Path, manifest: dict[str, Any], host: str, port: Any) -> bool:
    """True when host:port is this repository's producer by the plan's own names
    (producer_addresses): any port of one of its host names, or one of its
    addresses on one of its ports. port "" is the scheme's default (http: 80)."""
    host = str(host).lower().strip("[]").rstrip(".")
    names, addresses, ports = producer_addresses(repo, manifest)
    if names.covers(host):
        return True
    return tlslib._normalise_ip(host) in addresses and (str(port) or "80") in ports


def _producer_serves(repo: Path, manifest: dict[str, Any], host: str, port: int) -> bool:
    """True when this repository's producer answers at host:port: one of its own
    names, one of the plan's names for it (producer_answers: the probe plan's
    target and the planned server certificate), or, in a local run, this machine
    on the probe plan's HTTPS port."""
    if manifest.get("role") not in ("producer", "both"):
        return False
    if _own_names(manifest).covers(host) or producer_answers(repo, manifest, host, port):
        return True
    if manifest.get("environment") == "local" and _is_loopback(host):
        try:
            target = _probe_plan(repo, manifest).get("target") or {}
        except ValueError:
            return True                                   # an unreadable plan: assume it is the producer
        return str(target.get("https_port") or "") == str(port)
    return False


def check_server_only(repo: Path, manifest: dict[str, Any], live: bool,
                      live_target: str | list[str] | None = None) -> tuple[list[str], list[str], list[str], dict[str, Any]]:
    """E6's part for server-only rows: (problems, not run, evidence, {file: (host, result, observed)}).
    Recorded evidence (probe-tls.sh --server-only) counts in local only; elsewhere
    --live probes each row, at a --live-target the operator confirmed. A row for an
    endpoint this repository's producer serves is a fail: the producer asks for
    client certificates, so a server-only probe cannot stand for it."""
    problems, not_run, evidence = [], [], []
    judged: dict[str, Any] = {}
    environment = manifest.get("environment")
    for entry in server_only_rows(manifest):
        endpoint = str(entry.get("endpoint") or "")
        parsed = probe_tls.parse_endpoint(endpoint)
        label = f"server-only row {quoted(endpoint or entry.get('calls') or '?', 60)}"
        if parsed is None:
            problems.append(f"{label}: endpoint must be host:port")
            continue
        host, port = parsed
        wrong = probe_tls.host_problem(host, manifest, environment)
        if wrong:
            problems.append(f"{label}: {wrong}; no probe was sent")
            continue
        if _producer_serves(repo, manifest, host, port):
            problems.append(f"{label}: {host}:{port} is served by this repository's producer, which must ask for client "
                            "certificates; a server-only probe cannot stand for it")
            continue
        name = probe_tls.server_only_file(host, port)
        if live:
            wrong = live_target_problem(manifest, live_target, host, port, label)
            if wrong:
                problems.append(wrong)
                continue
            ca = None
            if entry.get("ca") and environment == "local":
                ca = _p(repo, entry["ca"])                # a repository's CA is honoured on a laptop only
            observed = probe_tls.server_only_probe(host, port, ca)
            source = "live"
        else:
            if environment != "local":
                not_run.append(f"{label}: recorded server-only evidence never proves a test, staging or production run; "
                               f"run check.sh --live --live-target {host}:{port}")
                continue
            path = _p(repo, name)
            if not path.is_file():
                not_run.append(f"{label}: no {name}; run probe-tls.sh --server-only {host}:{port}")
                continue
            try:
                data = json.loads(_read(path))
            except ValueError:
                problems.append(f"{label}: {name} is not valid JSON, or not a regular file")
                continue
            observed = data.get("observed") if isinstance(data, dict) and isinstance(data.get("observed"), dict) else {}
            if str(data.get("target", "")).lower() != f"{host}:{port}" or str(observed.get("target", "")).lower() \
                    not in (f"{host}:{port}", f"[{host}]:{port}"):
                problems.append(f"{label}: {name} records another target ({quoted(data.get('target'), 40)})")
                continue
            source = "recorded"
        result, detail = probe_tls.judge_server_only(observed, host)
        if not live and data.get("result") != result:
            problems.append(f"{label}: {name} is recorded as '{data.get('result')}' but what was observed means '{result}': {detail}")
        judged[name] = (host, result, observed)
        evidence.append(f"{name} ({source}) {result}: {detail}")
        if result == "fail":
            problems.append(f"{label}: {detail}")
        elif result == "not run":
            not_run.append(f"{label}: {detail}")
    return problems, not_run, evidence, judged


def _with_server_only(check: Check, repo: Path, manifest: dict[str, Any], live: bool,
                      live_target: str | list[str] | None) -> Check:
    """Adds the server-only rows to E6's result: a fail fails E6, a row not run makes it not run."""
    if not server_only_rows(manifest):
        return check
    problems, not_run, evidence, judged = check_server_only(repo, manifest, live, live_target)
    check.server_only = judged
    part = ("server-only: " + "; ".join(problems[:3]) if problems else
            "server-only: " + "; ".join(not_run[:3]) if not_run else
            f"server-only: {len(judged)} endpoint(s) verified without a client certificate")
    if check.result == "fail" or problems:
        result = "fail"
    elif check.result == "not run" or not_run:
        result = "not run"
    else:
        result = "pass"
    return check.set(result, f"{check.detail}; {part}" if check.detail else part, problems + not_run + list(check.evidence) + evidence)


def check_probes(repo: Path, manifest: dict[str, Any], live: bool, rerun: dict[str, Any] | None,
                 tags_file: str | None = None, live_target: str | list[str] | None = None) -> Check:
    check = Check("E6", "Live probes pass, refusals included (results re-derived from what was observed)")
    if manifest.get("role") == "consumer":
        if server_only_rows(manifest) and not _needs_kit_verify(manifest):
            check.set("pass", "")
            check = _with_server_only(check, repo, manifest, live, live_target)
            return check
        return _with_server_only(check_consumer_verify(repo, manifest, check, live, rerun, live_target),
                                 repo, manifest, live, live_target)
    return _with_server_only(_check_producer_probes(check, repo, manifest, live, rerun, tags_file, live_target),
                             repo, manifest, live, live_target)


def _needs_kit_verify(manifest: dict[str, Any]) -> bool:
    """A consumer run needs a kit's verify-result unless every call it names is a server-only row."""
    rows = _list(manifest.get("consumers_of_others"))
    mutual = [row for row in rows if not (isinstance(row, dict) and str(row.get("client_certificate", "")).strip().lower() == "none")]
    return bool(mutual) or not rows or bool(_list((manifest.get("consumer") or {}).get("live_verify"))) \
        or bool(_list(_evidence(manifest).get("consumer_verify")))


def _check_producer_probes(check: Check, repo: Path, manifest: dict[str, Any], live: bool, rerun: dict[str, Any] | None,
                           tags_file: str | None, live_target: str | list[str] | None) -> Check:
    plan = dict(_probe_plan(repo, manifest))
    stage = _stage(manifest)
    environment = manifest.get("environment")
    target = dict(plan.get("target") or {})
    settings, _ = producer_settings(repo, manifest)
    ports = legacy_ports(repo, manifest)
    problems, not_run = [], []
    # P7 is required at stage 6 whatever the plan says, on every port plain HTTP
    # was served on; P10 whenever the producer has a management port.
    if target.get("http_port") and str(target["http_port"]) not in ports:
        problems.append(f"the probe plan checks plain HTTP on port {target['http_port']}; the producer's old port(s): {ports}")
    has_http_port = bool(target.get("http_port")) or stage >= 6
    has_health = bool(plan.get("health")) or bool(settings.find("management.server.port"))
    if live:
        if not plan:
            return check.set("not run", "--live needs a probe_plan in the manifest")
        # The probes must reach the service itself: one of the in-scope hosts, in
        # every environment. This machine stands in for it on a laptop only.
        # Decided before any connection is made.
        host = str(target.get("host", ""))
        if not live_host_allowed(manifest, host):
            return check.set("fail", f"--live must probe one of in_scope_hosts"
                             + (" (or this machine, in a local run)" if environment == "local" else "")
                             + f"; the probe plan's target is '{host}'"
                             + (", this machine" if _is_loopback(host) else "") + ". No probe was sent")
        wrong = live_target_problem(manifest, live_target, host, target.get("https_port"), "the probe plan's target")
        if wrong:
            return check.set("fail", wrong)
        health = plan.get("health")
        if health:
            wrong = _live_url_problem(manifest, health.get("url") if isinstance(health, dict) else None) \
                if isinstance(health, dict) else "health must be a mapping with a url"
            if wrong:
                return check.set("fail", f"--live will not fetch the probe plan's health check: {wrong}. No probe was sent")
            if _list(live_target) and isinstance(health, dict):
                from urllib.parse import urlsplit  # noqa: PLC0415

                hosts = [target[0] for target in (parse_live_target(v) for v in _list(live_target)) if target]
                health_host = (urlsplit(str(health.get("url"))).hostname or "").lower().rstrip(".")
                if hosts and health_host not in hosts and not (environment == "local" and _is_loopback(health_host)):
                    return check.set("fail", f"the probe plan's health check goes to {health_host}, not to the --live-target "
                                     f"host {', '.join(hosts)}; no probe was sent")
        if stage >= 6:
            if not target.get("http_port"):
                target["http_port"] = int(ports[0])
            target["http_ports"] = sorted({int(p) for p in ports} | {int(target["http_port"])})
            plan["target"] = target
        plan["stage"] = stage
        try:
            data = probe_tls.run_plan(repo, plan, manifest)
        except (KeyError, ValueError) as problem:
            return check.set("fail", f"probe plan unusable: {problem}")
        if tags_file:
            probe_tls.record_tags(Path(os.path.expanduser(tags_file)).parent, data, Path(os.path.expanduser(tags_file)).name)
        else:
            probe_tls.record_tags(_p(repo, _evidence(manifest).get("probes", "tls-migration/evidence/probes.json")).parent, data,
                                  repo=repo)
        source = "live re-run"
    else:
        if environment != "local":
            return check.set("not run", "recorded probes never prove a test, staging or production run; "
                             "run check.sh --live from the probe location")
        path = _p(repo, _evidence(manifest).get("probes", "tls-migration/evidence/probes.json"))
        if not path.exists():
            return check.set("not run", "no probes.json; run probe-tls.sh from the probe location")
        try:
            data = json.loads(_read(path))
        except ValueError:
            return check.set("fail", "probes.json is not valid JSON (truncated or edited?), or not a regular file")
        source = "recorded probes.json"
        recorded_bindings = data.get("bound_inputs")
        if not isinstance(recorded_bindings, dict) or not recorded_bindings:
            problems.append("probes.json is not bound to the config and certificates (bound_inputs missing); probe again")
        else:
            current = probe_tls.bound_inputs(repo, manifest)
            changed = sorted(k for k in set(current) | set(recorded_bindings) if current.get(k) != recorded_bindings.get(k))
            code = {name for name in producer_code_names(repo, manifest) if "/src/main/resources/" not in f"/{name}"}
            if code and not code & set(recorded_bindings):
                problems.append("probes.json is not bound to the producer's code and build files (recorded by an older "
                                "probe-tls.py); probe again")
            elif changed:
                problems.append(f"probes.json was recorded against other files than the ones there now: {changed[:6]}; probe again")
    if int(data.get("stage", -1)) != stage:
        problems.append(f"probes ran at stage {data.get('stage')}, the manifest says stage {stage}")
    required = probe_tls.expected_cases(stage, has_http_port, has_health) if plan else None
    cases = data.get("cases") or []
    seen: dict[str, dict[str, Any]] = {}
    for case in cases:
        if case.get("id") in seen:
            problems.append(f"{case.get('id')} appears twice")
        seen[str(case.get("id"))] = case
    if required is None:
        problems.append("no probe_plan in the manifest, so the required probes cannot be checked")
        required = {}
    check.derived_probes, check.probe_target = {}, str(target.get("host") or "")
    for case_id, expectation in required.items():
        case = seen.get(case_id)
        if case is None:
            problems.append(f"{case_id} is missing" + (" (stage 6 must prove plain HTTP is closed)" if case_id == "P7" else ""))
            continue
        recorded_expected = str(case.get("expected", ""))
        ok_expectation = recorded_expected.startswith("status:") if expectation == "status" else recorded_expected == expectation
        if not ok_expectation:
            problems.append(f"{case_id} expected '{recorded_expected}', but stage {stage} requires '{expectation}'")
            continue
        result, detail = probe_tls.judge(recorded_expected, case.get("observed") or {},
                                         {"expected_issuer": target.get("expected_issuer")})
        check.derived_probes[case_id] = result
        check.observed_probes[case_id] = dict(case.get("observed") or {})
        if result != case.get("result"):
            problems.append(f"{case_id} is recorded as '{case.get('result')}' but what was observed means '{result}': {detail}")
        if result == "fail":
            problems.append(f"{case_id} failed: {detail}")
        elif result == "not run":
            not_run.append(f"{case_id}: {detail}")
    if stage >= 6 and seen.get("P7"):
        observed = seen["P7"].get("observed") or {}
        tried = set((observed.get("ports") or {}).keys())
        match = re.search(r":(\d+)(?:/|$)", str(observed.get("url", "")).split("://", 1)[-1])
        if match:
            tried.add(match.group(1))
        untried = [p for p in ports if p not in tried]
        if untried:
            problems.append(f"P7 did not try plain HTTP on port(s) {untried}, where it was served before the migration; probe again")
    problems += _p1_problems(repo, plan, seen.get("P1"), rerun) if plan else []
    problems += _probe_cert_problems(repo, plan, data, seen) if plan else []
    p9 = (seen.get("P9") or {}).get("observed") or {}
    if target.get("expected_issuer") and p9.get("expected_issuer") not in (None, target.get("expected_issuer")):
        problems.append("P9 was judged against a different issuer from the probe plan")
    planned = _server_fingerprints(rerun)
    if seen.get("P9") and planned and p9.get("fingerprint_sha256") not in planned:
        problems.append("the certificate the server presented (P9) is not the planned server certificate")
    wrong = _wrong_environment_ca([p9.get("issuer_cn"), p9.get("subject_cn")], environment) if seen.get("P9") else None
    if wrong:
        problems.append(f"the server presented a certificate from {wrong}, a throw-away CA that is not valid in {environment}")
    summary = data.get("summary") or {}
    recount = {k: sum(1 for c in cases if c.get("result") == k) for k in ("pass", "fail", "not run")}
    if any(int(summary.get(k, 0)) != v for k, v in recount.items()):
        problems.append(f"summary {summary} does not match the cases {recount}")
    evidence = [f"{c.get('id')} {c.get('result')}: {c.get('detail')}" for c in cases]
    if live:
        check.live_probes = {str(c.get("id")): str(c.get("result")) for c in cases}
    if problems:
        return check.set("fail", f"{source}: " + "; ".join(problems[:5]), problems + evidence)
    if not_run:
        return check.set("not run", f"{source}: " + "; ".join(not_run), evidence)
    return check.set("pass", f"{source}: {len(required)} probes for stage {stage}, all as required", evidence)


def _client_fingerprints(rerun: dict[str, Any] | None) -> set[str]:
    return {str(c.get("fingerprint_sha256")) for c in (rerun or {}).get("certificates", [])
            if c.get("role") == "client" and c.get("fingerprint_sha256")}


def _trusted_fingerprints(rerun: dict[str, Any] | None) -> set[str]:
    return {str(fp) for store in (rerun or {}).get("trust_stores", []) for fp in store.get("fingerprints") or []}


def _live_consumer_verify(repo: Path, manifest: dict[str, Any], rerun: dict[str, Any] | None, scratch: Path,
                          live_target: str | None = None) -> list[Path]:
    """Re-runs the handshake check for each kit against the producer; returns the
    fresh result files, in `scratch` (the caller's temporary folder, which it
    removes). The script that runs is the TOOLKIT's own verify.sh, with the
    kit's data files beside it: nothing from the repository under review is
    ever executed."""
    results = []
    template = HERE / "kit-template" / "verify.sh"
    for index, entry in enumerate(_list((manifest.get("consumer") or {}).get("live_verify"))):
        if not isinstance(entry, dict) or not entry.get("kit") or not entry.get("key"):
            continue
        kit = _p(repo, entry["kit"])
        # Where verify.sh will connect, decided before anything is copied or sent: the
        # same host rule as every --live connection.
        fields = dict(line.split("=", 1) for line in _read(kit / "endpoint.txt").splitlines() if "=" in line) \
            if (kit / "endpoint.txt").is_file() else {}
        url = fields.get("url", "").strip()
        from urllib.parse import urlsplit  # noqa: PLC0415

        try:
            host = urlsplit(url).hostname or ""
        except ValueError:
            host = ""
        if not url.startswith("https://") or not live_host_allowed(manifest, host):
            raise ValueError(f"verify.sh not run, nothing sent: {_rel(repo, kit / 'endpoint.txt')} names {quoted(url, 60)}, "
                             "not an https URL to one of in_scope_hosts"
                             + (" (or this machine, in a local run)" if manifest.get("environment") == "local" else ""))
        try:
            port = urlsplit(url).port or 443
        except ValueError:
            port = None
        wrong = live_target_problem(manifest, live_target, host, port, f"{_rel(repo, kit / 'endpoint.txt')}'s url")
        if wrong:
            raise ValueError(f"verify.sh not run: {wrong}")
        bundle = kit / "ca-bundle.pem"
        fingerprints = [tlslib.cert_info_from_pem(pem)["fingerprint_sha256"] for pem in tlslib.split_bundle(bundle)]
        if not fingerprints or any(fp not in _trusted_fingerprints(rerun) for fp in fingerprints):
            raise ValueError(f"{_rel(repo, bundle)} holds a CA that is not in a trust store of the certificate plan")
        try:
            overlap = json.loads(_read(kit / "KIT-MANIFEST.json")).get("ca_overlap") is True
        except (OSError, ValueError):
            overlap = False
        # verify.sh takes the CA's own fingerprint for a one-CA kit; during a server CA
        # rotation overlap (two CAs) only the SHA-256 of the whole file.
        expected = tlslib.sha256_file(bundle) if overlap else fingerprints[0]
        if not template.is_file():
            raise ValueError("the toolkit's kit-template/verify.sh is missing; the gate never runs the repository's copy")
        work = scratch / f"kit-{index}"
        work.mkdir()
        shutil.copy(template, work / "verify.sh")
        # Data only. verify.sh checks the client certificate against consumer-ca.crt
        # before it connects, so the kit's copy goes beside it.
        for name in ("endpoint.txt", "ca-bundle.pem", "consumer-ca.crt", "client.crt"):
            if (kit / name).is_file():
                shutil.copy(kit / name, work / name)
        out = scratch / f"verify-{index}.json"
        cmd = ["bash", str(work / "verify.sh"), "--expect-fingerprint", expected,
               "--key", str(_p(repo, entry["key"], private=True)), "--out", str(out)]
        if entry.get("cert"):
            cmd += ["--cert", str(_p(repo, entry["cert"], private=True))]
        tlslib.run(cmd, timeout=90)
        results.append(out)
    return results


def check_consumer_verify(repo: Path, manifest: dict[str, Any], check: Check, live: bool,
                          rerun: dict[str, Any] | None, live_target: str | None = None) -> Check:
    environment = manifest.get("environment")
    if live:
        # The kits' copies and the fresh results live in a folder of their own, removed on
        # every way out: a result, a failure, an exception, and a stop signal (see main).
        with tempfile.TemporaryDirectory(prefix="tls-consumer-live-") as scratch:
            files = _live_consumer_verify(repo, manifest, rerun, Path(scratch), live_target)
            if not files:
                return check.set("not run", "--live on a consumer needs consumer.live_verify: [{kit, key, cert}] in the manifest")
            return _judge_consumer_verify(manifest, check, files, "live re-run of the toolkit's verify.sh", live, rerun)
    if environment != "local":
        return check.set("not run", "a recorded verify-result.json never proves a test, staging or production run; "
                         "run check.sh --live where the consumer runs")
    files = [_p(repo, f) for f in _list(_evidence(manifest).get("consumer_verify"))]
    if not files:
        return check.set("not run", "no verify-result.json listed for this consumer")
    return _judge_consumer_verify(manifest, check, files, "recorded verify-result.json", live, rerun)


def _judge_consumer_verify(manifest: dict[str, Any], check: Check, files: list[Path], source: str, live: bool,
                           rerun: dict[str, Any] | None) -> Check:
    environment = manifest.get("environment")
    scope = Scope(manifest)
    clients, trusted = _client_fingerprints(rerun), _trusted_fingerprints(rerun)
    problems, evidence = [], []
    for path in files:
        if not path.exists():
            problems.append(f"{path.name} missing")
            continue
        try:
            data = json.loads(_read(path))
        except ValueError:
            problems.append(f"{path.name} is not valid JSON, or not a regular file")
            continue
        host = re.sub(r"^https://([^/:]+).*$", r"\1", str(data.get("endpoint", ""))).lower()
        # verify.sh 2.2 names the field for what it shows (openssl refusing a wrong name);
        # older kits wrote wrong_name_refused.
        wrong_name = data.get("openssl_wrong_name_refused", data.get("wrong_name_refused"))
        evidence.append(f"{path.name}: ok={data.get('ok')} status={data.get('http_status')} tls={data.get('tls_version')} "
                        f"wrong name refused={wrong_name}")
        if not (data.get("ok") is True and str(data.get("http_status", "")).startswith("2")
                and data.get("tls_version") in ("TLSv1.2", "TLSv1.3")):
            problems.append(f"{path.name}: the mutual TLS call did not succeed")
        if wrong_name is not True:
            problems.append(f"{path.name}: P8 not shown: the client must refuse a server certificate for another name")
        if not scope.covers(host):
            problems.append(f"{path.name}: endpoint host {host or '?'} is not in in_scope_hosts")
        elif live and environment != "local" and _is_loopback(host):
            problems.append(f"{path.name}: --live in {environment} must call the producer, not this machine")
        if data.get("client_cert_sha256") not in clients:
            problems.append(f"{path.name}: the client certificate used is not one in the certificate plan")
        if data.get("ca_fingerprint_sha256") not in trusted:
            problems.append(f"{path.name}: the CA bundle used is not a trust store in the certificate plan")
        if data.get("ca_overlap") is True and data.get("previous_ca_fingerprint_sha256") not in trusted:
            problems.append(f"{path.name}: the previous server CA in the bundle used is not in a trust store of the certificate plan")
    if problems:
        return check.set("fail", f"{source}: " + "; ".join(problems[:4]), problems + evidence)
    return check.set("pass", f"{source}: {len(files)} mutual TLS call(s) bound to the planned certificates", evidence)


# ---------------------------------------------------------------- E8

MIN_DAYS_OUTSIDE_LOCAL = 7


def _policy(repo: Path, manifest: dict[str, Any], operator_policy: str | None) -> tuple[int, str, str | None]:
    """(observation days, sign-off roles, why the policy cannot be used).
    In local the manifest may name the policy. Anywhere else the policy that sets
    the window and the sign-off roles is the operator's (--policy or TLS_POLICY):
    the run under review does not choose its own rules."""
    environment = manifest.get("environment")
    roles = "producer service owner"
    if environment == "local":
        path = _op(repo, operator_policy) if operator_policy else _p(repo, manifest.get("policy", "tls-policy.yaml"))
        days = 0
    else:
        if not operator_policy:
            return 14, roles, ("outside local the policy comes from the operator: run check.sh --policy <tls-policy.yaml> "
                               "(or set TLS_POLICY); the manifest's own 'policy:' line is not used")
        path = Path(os.path.expanduser(operator_policy))
        if not path.is_file():
            return 14, roles, f"the operator's policy file {operator_policy} does not exist"
        days = 14
    if path.is_file():
        policy = tlslib.load_yaml(path) or {}
        env_block = (policy.get("environments") or {}).get(environment) or {}
        cutover = policy.get("cutover") or {}
        days = int(env_block.get("min_observation_days", cutover.get("min_observation_days", days)))
        roles = ",".join(str(r) for r in _list(cutover.get("signoff_roles"))) or roles
    # Floors no policy file can lower: never negative, and a week outside a laptop.
    days = max(days, 0 if environment == "local" else MIN_DAYS_OUTSIDE_LOCAL)
    return days, roles, None


def _yaml_documents(text: str) -> list[Any] | None:
    """Every document of a YAML or JSON text, or None when it does not parse."""
    try:
        return yaml_documents_of(text)
    except Exception:  # noqa: BLE001 - templates and odd files simply do not parse
        return None


def _properties_map(text: str) -> dict[str, str]:
    """A .properties text (a file kept in a ConfigMap) as one map, documents in order."""
    flat: dict[str, str] = {}
    for _, layer in parse_properties(text):
        flat.update(layer)
    return flat


def _walk(value: Any, path: str = "") -> Any:
    """Every node of a parsed document with its dotted path; a multi-line string
    that is itself YAML (a file kept in a ConfigMap) is walked too, and a value
    under a key named *.properties is read the way Spring reads a .properties file."""
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and str(key).lower().endswith(".properties"):
                yield from _walk(_properties_map(child), f"{path}.{key}" if path else str(key))
                continue
            yield from _walk(child, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child, path)
    elif isinstance(value, str) and "\n" in value and ":" in value:
        for document in _yaml_documents(value) or []:
            if isinstance(document, (dict, list)):
                yield from _walk(document, path)


def _allowlist_nodes(document: Any) -> list[set[str]]:
    return [{str(c["id"]) for c in node["consumers"]} for _, node in _walk(document)
            if isinstance(node, dict) and isinstance(node.get("consumers"), list) and node["consumers"]
            and all(isinstance(c, dict) and c.get("id") for c in node["consumers"])]


def deployed_allowlists(repo: Path, manifest: dict[str, Any]) -> tuple[list[tuple[str, set[str]]], list[str]]:
    """Allowlists shipped with the service: every YAML or JSON in the tree that
    holds consumers: [{id: ...}] anywhere (a ConfigMap, a values file, a config
    folder), outside the manifest's own file, plus the files the manifest names
    as producer.deployed_allowlist. (found, why some cannot be compared): a file
    that mentions consumers but does not parse, or a named file without one."""
    producer = _producer(manifest)
    own = _p(repo, producer.get("allowlist", "")).resolve() if producer.get("allowlist") else None
    named = {_p(repo, f).resolve() for f in _list(producer.get("deployed_allowlist"))}
    found, problems = [], []
    seen_named = set()
    for path in scan_rules.iter_files(repo):
        if path.suffix.lower() not in (".yml", ".yaml", ".json") or path.resolve() == own:
            continue
        relative = _rel(repo, path)
        if (relative.startswith("tls-migration/kits/") or SOURCE_TEST.search(relative)) and path.resolve() not in named:
            continue
        text = scan_rules.read_text(path)
        if not text or "consumers" not in text:
            continue
        documents = _yaml_documents(text)
        if documents is None:
            if re.search(r"(?m)consumers[\"']?\s*:", text):
                reason = ("mentions consumers: but does not parse as YAML" + ("" if tlslib._pyyaml is not None else " without PyYAML")  # noqa: SLF001
                          + ", so a deployed allowlist in it cannot be compared")
                scan_rules.note_skip(relative, reason, blocking=True)
                problems.append(f"{relative} {reason}")
            continue
        lists = [ids for document in documents for ids in _allowlist_nodes(document)]
        if lists and path.resolve() in named:
            seen_named.add(path.resolve())
        found += [(relative, ids) for ids in lists]
    for path in sorted(named - seen_named):
        if path == own:
            continue
        if not path.is_file():
            problems.append(f"{_rel(repo, path)}: named as producer.deployed_allowlist, but there is no such file")
            continue
        try:
            lists = [ids for document in (_yaml_documents(_read(path)) or []) for ids in _allowlist_nodes(document)]
        except ValueError:
            lists = []
        if lists:
            found += [(_rel(repo, path), ids) for ids in lists]
        else:
            problems.append(f"{_rel(repo, path)}: named as producer.deployed_allowlist, but no consumers: [{{id: ...}}] list "
                            "could be read in it")
    return found, problems


def check_readiness(repo: Path, manifest: dict[str, Any], operator_policy: str | None = None,
                    tags_file: str | None = None) -> Check:
    check = Check("E8", "Client certificates required / HTTP closed only with every consumer ready, or a sign-off")
    if manifest.get("role") == "consumer":
        return check.set("not applicable", "consumer run")
    producer = _producer(manifest)
    stage = _stage(manifest)
    if stage < 5:
        return check.set("not applicable", f"stage {stage}: client certificates are not required yet")
    log = producer.get("access_log")
    allowlist = producer.get("allowlist")
    odd = [str(f) for f in (log, allowlist, producer.get("signoff", "tls-migration/cutover-signoff.yaml"))
           if f and _not_regular(_p(repo, f))]
    if odd:
        return check.set("fail", f"not a regular file where the run's records should be: {odd}")
    if not log or not _p(repo, log).is_file() or not allowlist or not _p(repo, allowlist).is_file():
        return check.set("not run", "stage 5+ needs the producer's access log and the allowlist to rebuild readiness")
    # The allowlist the service is deployed with must be the one readiness is built for.
    planned_ids = {str(c["id"]) for c in (tlslib.load_yaml(_p(repo, allowlist)) or {}).get("consumers") or []
                   if isinstance(c, dict) and c.get("id")}
    deployed, uncompared = deployed_allowlists(repo, manifest)
    differing = [f"{where} allows {sorted(ids)}; {allowlist} allows {sorted(planned_ids)}"
                 for where, ids in deployed if ids != planned_ids]
    if differing:
        return check.set("fail", "the allowlist deployed with the service is not the one readiness was checked for: "
                         + "; ".join(differing[:2]), differing + uncompared)
    if uncompared:
        return check.set("not run", "a deployed allowlist cannot be compared with the manifest's: " + "; ".join(uncompared[:2]),
                         uncompared)
    min_days, roles, unusable = _policy(repo, manifest, operator_policy)
    if unusable:
        return check.set("not run", unusable)
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "readiness.json"
        cmd = [sys.executable, "-I", "-B", str(HERE / "readiness.py"), "--log", str(_p(repo, log)), "--allowlist", str(_p(repo, allowlist)),
               "--out", str(out), "--min-observation-days", str(min_days), "--signoff-roles", roles]
        signoff = producer.get("signoff", "tls-migration/cutover-signoff.yaml")
        if _p(repo, signoff).is_file():
            cmd += ["--signoff", str(_p(repo, signoff))]
        tags = _p(repo, _evidence(manifest).get("probes", "tls-migration/evidence/probes.json")).parent / "probe-tags.log"
        own_tags = [path for path in (tags, Path(os.path.expanduser(tags_file)) if tags_file else None) if path and path.is_file()]
        if len(own_tags) > 1:
            # The run's recorded tags and the ones --tags-file kept for this gate's own live probes.
            merged = Path(scratch) / "probe-tags.log"
            merged.write_text("".join(_read(path) for path in own_tags))
            cmd += ["--probe-tags", str(merged)]
        elif own_tags:
            cmd += ["--probe-tags", str(own_tags[0])]
        code, stdout, stderr = tlslib.run(cmd, timeout=120)
        if not out.exists():
            return check.set("fail", "readiness could not be rebuilt from the log: " + (stderr or stdout).strip()[-200:])
        data = json.loads(out.read_text())
    evidence = [f"{c['id']}: {c['status']} ({c['reason']})" for c in data["consumers"]]
    evidence.append(f"plain-HTTP calls in window: {data['http_calls_in_window']}")
    evidence.append(f"HTTPS calls without a client certificate in window: {data.get('https_calls_without_certificate_in_window', 0)}")
    evidence.append(f"observation window: {min_days} day(s); the log is a file in the repository, read as written")
    evidence.append(f"log lines with the access marker that are not an exact access record (rejected, never read): "
                    f"{data.get('rejected_lines', 0)}" + (f" ({', '.join(str(r) for r in data.get('rejected_line_refs', [])[:5])})"
                                                          if data.get("rejected_lines") else ""))
    bad_signoff = [f"the sign-off is refused: {p}" for p in (data.get("signoff") or {}).get("problems") or []]
    evidence += bad_signoff
    if not data["ready_for_stage_5"]:
        reasons = list(bad_signoff)
        if data.get("unready_without_signoff"):
            reasons.append(f"consumers not ready and not signed off: {[c['id'] for c in data['consumers'] if c['status'] != 'ready' and not c['accepted_by_signoff']]}")
        if data.get("https_calls_without_certificate_in_window") and not data.get("certless_calls_accepted_by_signoff"):
            reasons.append(f"{data['https_calls_without_certificate_in_window']} HTTPS call(s) without a client certificate in the window")
        return check.set("fail", f"stage {stage}, but " + "; ".join(reasons or ["no consumer in the allowlist"]), evidence)
    if stage >= 6 and not data["ready_for_stage_6"]:
        return check.set("fail", f"HTTP closed while {data['http_calls_in_window']} plain-HTTP calls arrived in the window, with no "
                         + ("valid sign-off (" + "; ".join(bad_signoff) + ")" if bad_signoff else "sign-off"), evidence)
    accepted = [c["id"] for c in data["consumers"] if c["accepted_by_signoff"]]
    if data.get("http_calls_accepted_by_signoff") and data["http_calls_in_window"]:
        accepted.append(f"{data['http_calls_in_window']} plain-HTTP call(s)")
    if data.get("certless_calls_accepted_by_signoff") and data.get("https_calls_without_certificate_in_window"):
        accepted.append(f"{data['https_calls_without_certificate_in_window']} call(s) without a certificate")
    if accepted:
        check.signed_off = len(accepted)
        signer = data.get("signoff") or {}
        return check.set("pass", f"accepted by a sign-off from {signer.get('signed_by')} ({signer.get('role')}, {signer.get('date')}): "
                         f"{accepted}; the sign-off is written inside the session, so the run is at best pass with exceptions", evidence)
    return check.set("pass", "every consumer seen on mutual TLS", evidence)


# ---------------------------------------------------------------- E9, E10

def _planned_server_cas(repo: Path, manifest: dict[str, Any]) -> set[str]:
    """Fingerprints of the CAs that issue the planned server certificates."""
    found = set()
    for entry in _list(_cert_plan(repo, manifest).get("certificates")):
        if isinstance(entry, dict) and entry.get("role") == "server" and entry.get("issuer_ca"):
            try:
                found.add(tlslib.cert_info(_p(repo, entry["issuer_ca"]))["fingerprint_sha256"])
            except (OSError, ValueError):
                continue
    return found


CONSUMER_DATA_FILES = {"client.crt", "client.crt.next", "client.crt.previous", "verify-result.json"}


def _consumer_data_problem(repo: Path, manifest: dict[str, Any], path: Path) -> str | None:
    """Why a consumer's own data file in a kit folder is not what it should be:
    client.crt must be one client certificate (no key) issued by a CA that
    issues the planned client certificates; verify-result.json must be JSON."""
    if not path.is_file():
        return "not a regular file"
    try:
        text = _read(path)
    except ValueError as problem:
        return str(problem)
    if tlslib.PRIVATE_KEY_MARKER.search(text):
        return "holds a private key"
    if path.name == "verify-result.json":
        try:
            json.loads(text)
        except ValueError:
            return "not valid JSON"
        return None
    try:
        pems = tlslib.split_bundle(path)
        info = tlslib.cert_info_from_pem(pems[0]) if pems else None
    except (OSError, ValueError) as problem:
        return f"cannot be read as a certificate: {problem}"
    if info is None or len(pems) != 1:
        return "must hold exactly one certificate"
    if info["is_ca"] or info["extended_key_usage"] != ["clientAuth"]:
        return "is not a client certificate (CA:FALSE, extended key usage clientAuth only)"
    issuers = [entry["issuer_ca"] for entry in _list(_cert_plan(repo, manifest).get("certificates"))
               if isinstance(entry, dict) and entry.get("role") == "client" and entry.get("issuer_ca")]
    for issuer in dict.fromkeys(issuers):
        try:
            if tlslib.verify_chain(path, _p(repo, issuer), "sslclient")[0]:
                return None
        except (OSError, ValueError):
            continue
    return "is not issued by the planned consumer CA (the issuer_ca of the plan's client certificates)"


def _previous_server_cas(repo: Path, manifest: dict[str, Any]) -> set[str]:
    """Fingerprints of the declared previous server CAs: <name>.previous.crt beside
    the issuer_ca of each planned server certificate (certgen-test-ca.sh keeps the
    replaced CA there during a rotation overlap)."""
    found = set()
    for entry in _list(_cert_plan(repo, manifest).get("certificates")):
        if isinstance(entry, dict) and entry.get("role") == "server" and entry.get("issuer_ca"):
            issuer = _p(repo, entry["issuer_ca"])
            stem = issuer.name[:-len(".crt")] if issuer.name.endswith(".crt") else issuer.stem
            for path in (issuer.parent / f"{stem}.previous.crt",):
                try:
                    found |= {tlslib.cert_info_from_pem(pem)["fingerprint_sha256"] for pem in tlslib.split_bundle(path)}
                except (OSError, ValueError):
                    continue
    return found


def _kit_bundle_problems(repo: Path, manifest: dict[str, Any], kit: Path, data: dict[str, Any], pems: list[str],
                         planned_cas: set[str], rerun: dict[str, Any] | None) -> list[str]:
    """What the consumer will trust, compared with the plan directly: exactly one
    certificate, the planned server CA; or, for a kit built during a server CA
    rotation (KIT-MANIFEST ca_overlap: true), exactly two CAs with the same name,
    the planned server CA first and the declared previous one second, both in the
    plan's trust stores."""
    problems = []
    infos = [tlslib.cert_info_from_pem(pem) for pem in pems]
    fingerprints = [info["fingerprint_sha256"] for info in infos]
    if not fingerprints or fingerprints[0] != data.get("ca_fingerprint_sha256"):
        problems.append(f"{kit.name}: ca-bundle.pem does not match the fingerprint in the manifest")
    if not planned_cas:
        return problems + [f"{kit.name}: the certificate plan names no server CA to compare ca-bundle.pem with"]
    if data.get("ca_overlap") is True and len(fingerprints) == 2:
        previous = _previous_server_cas(repo, manifest)
        trusted = _trusted_fingerprints(rerun)
        if fingerprints[0] not in planned_cas:
            problems.append(f"{kit.name}: the first CA in ca-bundle.pem is not the planned server CA")
        if fingerprints[1] not in previous:
            problems.append(f"{kit.name}: the second CA in ca-bundle.pem is not the declared previous server CA "
                            "(server-ca.previous.crt beside the plan's server CA)")
        if data.get("previous_ca_fingerprint_sha256") != fingerprints[1]:
            problems.append(f"{kit.name}: the manifest's previous_ca_fingerprint_sha256 is not the second CA in ca-bundle.pem")
        if infos[0]["subject"] != infos[1]["subject"] or not (infos[0]["is_ca"] and infos[1]["is_ca"]):
            problems.append(f"{kit.name}: the two certificates in ca-bundle.pem are not two CAs with the same name")
        if trusted and any(fp not in trusted for fp in fingerprints):
            problems.append(f"{kit.name}: a CA in ca-bundle.pem is not in a trust store of the certificate plan")
        return problems
    if len(fingerprints) != 1:
        problems.append(f"{kit.name}: ca-bundle.pem holds {len(fingerprints)} certificates; a kit carries exactly one, the server CA"
                        + (" (two only for a kit built during a server CA rotation, ca_overlap: true)" if len(fingerprints) == 2 else ""))
    if any(fp not in planned_cas for fp in fingerprints):
        problems.append(f"{kit.name}: ca-bundle.pem holds a CA that does not issue the planned server certificate")
    return problems


KIT_DATA_FILES = {"ca-bundle.pem", "consumer-ca.crt", "endpoint.txt", "client.crt", "SHA256SUMS"}
SUMS_LINE = re.compile(r"([0-9a-f]{64})  ([^\n]{1,300})")


def _kit_sums_problems(kit: Path, data: dict[str, Any]) -> list[str]:
    """SHA256SUMS against the files (D7): every line well formed, every file it
    lists present with that SHA-256, every file the kit was built with listed
    (all but SHA256SUMS and KIT-MANIFEST.json), and the kit fingerprint the
    manifest records equal to the SHA-256 of SHA256SUMS."""
    sums = kit / build_kit.SUMS
    if not sums.is_file():
        return []                                   # reported as missing against build_kit.REQUIRED
    try:
        text = _read(sums)
    except ValueError:
        return [f"{kit.name}: SHA256SUMS is not a regular file"]
    problems, listed = [], {}
    for number, line in enumerate(text.splitlines(), 1):
        match = SUMS_LINE.fullmatch(line)
        if not match or match.group(2) in listed or ".." in match.group(2).split("/") or match.group(2).startswith("/"):
            problems.append(f"{kit.name}: SHA256SUMS line {number} is not '<sha256>  <file in the kit>'")
            continue
        listed[match.group(2)] = match.group(1)
    for name, digest in listed.items():
        target = kit / name
        if not target.is_file() or target.is_symlink():
            problems.append(f"{kit.name}: SHA256SUMS lists {name}, which is not in the kit")
        elif tlslib.sha256_file(target) != digest:
            problems.append(f"{kit.name}: {name} does not match its line in SHA256SUMS")
    built = set(data.get("files") or {}) - build_kit.NOT_SUMMED
    missing = sorted(built - set(listed))
    if missing:
        problems.append(f"{kit.name}: SHA256SUMS does not cover {missing}")
    recorded = data.get("kit_fingerprint_sha256")
    if not recorded:
        problems.append(f"{kit.name}: KIT-MANIFEST.json records no kit_fingerprint_sha256 (an older build_kit.py); rebuild the kit")
    elif recorded != tlslib.sha256_file(sums):
        problems.append(f"{kit.name}: the kit fingerprint in KIT-MANIFEST.json is not the SHA-256 of SHA256SUMS")
    return problems
KIT_FREE_TEXT = {"CUTOVER": r"[^\x00-\x1f\x7f|]*", "CONTACT": r"[^\x00-\x1f\x7f|]*", "LIFETIME": r"\d{1,4}"}
KIT_FILLED = ("PRODUCER", "CONSUMER", "ENDPOINT", "ENDPOINT_BASE", "NAMES", "KEY_SUBPATH", "ENVIRONMENT")


def kit_template_files() -> dict[str, Path]:
    """What build_kit.py copies into every kit from the toolkit, by the path in the
    kit: the kit-template files (filled in) and make-csr.sh with _key_folder.sh (as they are)."""
    files = {source.relative_to(build_kit.TEMPLATE).as_posix(): source for source in sorted(build_kit.TEMPLATE.rglob("*"))
             if not source.is_dir() and source.name != ".DS_Store" and not source.name.endswith(".Tests.ps1")}
    files["make-csr.sh"] = HERE / "make-csr.sh"
    files["_key_folder.sh"] = HERE / "_key_folder.sh"
    return files


def _template_pattern(text: str, values: dict[str, str], flags: dict[str, bool]) -> re.Pattern[str]:
    """The kit file build_kit.fill() makes from a template, as a pattern: the values
    the kit's own data gives are filled in exactly; the free text build_kit does not
    record (cut-over date, contact, lifetime) may be any one line of plain text,
    the same wherever it recurs."""
    text = build_kit.BLOCK.sub(lambda m: m.group(2) if flags.get(m.group(1)) else "", text)
    pieces, seen = [], set()
    for index, piece in enumerate(re.split(r"\{\{([A-Z_]+)\}\}", text)):
        if index % 2 == 0:
            pieces.append(re.escape(piece))
        elif piece in values:
            pieces.append(re.escape(values[piece]))
        elif piece in KIT_FREE_TEXT:
            pieces.append(f"(?P={piece})" if piece in seen else f"(?P<{piece}>{KIT_FREE_TEXT[piece]})")
            seen.add(piece)
        else:
            pieces.append(re.escape("{{" + piece + "}}"))
    return re.compile("".join(pieces))


def _kit_endpoint_problems(repo: Path, manifest: dict[str, Any], kit: Path, data: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    """endpoint.txt and the kit manifest's endpoint, held to the toolkit's rules and
    the run's manifest: exactly the lines build_kit.py writes, an https URL to one
    of in_scope_hosts (this machine too, in a local run), the producer's own kit.
    Returns the problems and the values the templates are filled with."""
    problems = []
    endpoint, consumer, producer = (str(data.get(k) or "") for k in ("endpoint", "consumer", "producer"))
    environment = data.get("environment")
    try:
        lines = _read(kit / "endpoint.txt").splitlines()
    except (OSError, ValueError):
        return [f"{kit.name}: endpoint.txt unreadable"], {}
    fields = dict(line.split("=", 1) for line in lines if "=" in line)
    names = [n for n in fields.get("names", "").split(",") if n]
    expected = (f"url={endpoint}\nconsumer={consumer}\nproducer={producer}\nnames={','.join(names)}\n"
                + (f"environment={environment}\n" if environment else ""))
    if _read(kit / "endpoint.txt") != expected:
        problems.append(f"{kit.name}: endpoint.txt is not what build_kit.py wrote for the kit's manifest "
                        f"(url, consumer, producer, names, environment)")
    try:
        base = build_kit.checked_endpoint(endpoint)
    except SystemExit as refused:
        return problems + [f"{kit.name}: the kit's endpoint {quoted(endpoint, 80)} is refused: {refused}"], {}
    from urllib.parse import urlsplit  # noqa: PLC0415

    host = urlsplit(endpoint).hostname or ""
    if not live_host_allowed(manifest, host):
        problems.append(f"{kit.name}: the kit sends consumers to {host}, which is not one of in_scope_hosts"
                        + (" (or this machine, in a local run)" if manifest.get("environment") == "local" else ""))
    if not (build_kit.ID_PATTERN.match(producer) and build_kit.ID_PATTERN.match(consumer)):
        problems.append(f"{kit.name}: the kit manifest's producer and consumer are not plain names")
    own = str(_producer(manifest).get("name") or "")
    if own and producer != own:
        problems.append(f"{kit.name}: built for producer {quoted(producer, 40)}, but this run's producer is {own}")
    if not names or not all(build_kit.is_host(n, wildcard=True) for n in names):
        problems.append(f"{kit.name}: endpoint.txt names no server certificate names, or ones that are not host names")
    values = {"PRODUCER": producer, "CONSUMER": consumer, "ENDPOINT": endpoint, "ENDPOINT_BASE": base,
              "NAMES": ", ".join(f"`{n}`" for n in names), "ENVIRONMENT": str(environment or "not stated"),
              "KEY_SUBPATH": "/".join(part for part in (environment, producer, consumer) if part)}
    return problems, values


def _kit_toolkit_problems(kit: Path, data: dict[str, Any], values: dict[str, str]) -> list[str]:
    """Every file build_kit.py takes from the toolkit, compared with the toolkit
    itself (re-rendered from kit-template), never with the kit's own manifest."""
    problems = []
    flags = {"ROUTE_A": data.get("route") != "B", "ROUTE_B": data.get("route") == "B"}
    for name, source in kit_template_files().items():
        target = kit / name
        if not target.is_file():
            continue                                   # a missing file is reported against build_kit.REQUIRED
        try:
            text = _read(target)
        except ValueError:
            problems.append(f"{kit.name}: {name} is not a regular file")
            continue
        if not _template_pattern(source.read_text(), values, flags).fullmatch(text):
            problems.append(f"{kit.name}: {name} is not the toolkit's {name} (re-rendered from kit-template for this kit); "
                            "rebuild the kit with build_kit.py")
    return problems


def _ca_file_fingerprints(path: Path) -> set[str]:
    """Fingerprints of every certificate in a CA file and in the <name>.previous.crt beside it."""
    found = set()
    stem = path.name[:-len(".crt")] if path.name.endswith(".crt") else path.stem
    for candidate in (path, path.parent / f"{stem}.previous.crt"):
        try:
            found |= {tlslib.cert_info_from_pem(pem)["fingerprint_sha256"] for pem in tlslib.split_bundle(candidate)}
        except (OSError, ValueError):
            continue
    return found


def _planned_consumer_cas(repo: Path, manifest: dict[str, Any]) -> set[str]:
    """Fingerprints of the CAs that issue the plan's client certificates (every
    certificate in their issuer_ca files, and the <name>.previous.crt beside one).

    A producer-only plan may list no client certificate at all: the consumers hold
    them, signed by their own issuer. The consumer CA is then the CA in the plan's
    trust stores that is not a server certificate's issuer: what the producer trusts
    for client certificates."""
    plan = _cert_plan(repo, manifest)
    entries = [entry for entry in _list(plan.get("certificates")) if isinstance(entry, dict)]
    client_issuers = [entry["issuer_ca"] for entry in entries if entry.get("role") == "client" and entry.get("issuer_ca")]
    if client_issuers:
        return set().union(*(_ca_file_fingerprints(_p(repo, issuer)) for issuer in client_issuers))
    if any(entry.get("role") == "client" for entry in entries):
        return set()
    server_cas = set().union(set(), *(_ca_file_fingerprints(_p(repo, entry["issuer_ca"])) for entry in entries
                                      if entry.get("role") == "server" and entry.get("issuer_ca")))
    if not server_cas:
        return set()                                   # nothing to tell the two sides apart by
    stores = set().union(set(), *(_ca_file_fingerprints(_p(repo, store["path"])) for store in _list(plan.get("trust_stores"))
                                  if isinstance(store, dict) and store.get("path")))
    return stores - server_cas


def _kit_consumer_ca_problems(repo: Path, manifest: dict[str, Any], kit: Path) -> list[str]:
    """consumer-ca.crt is what the consumer checks its own certificate against: the
    plan's consumer CA (two of the same name during a rotation), nothing else."""
    path = kit / "consumer-ca.crt"
    if not path.is_file():
        return []
    try:
        infos = [tlslib.cert_info_from_pem(pem) for pem in tlslib.split_bundle(path)]
    except (OSError, ValueError) as problem:
        return [f"{kit.name}: consumer-ca.crt unreadable: {str(problem).replace(str(kit) + os.sep, '')}"]
    planned = _planned_consumer_cas(repo, manifest)
    if not planned:
        return [f"{kit.name}: the certificate plan names no consumer CA to compare consumer-ca.crt with (the issuer_ca of a "
                "client certificate, or in a plan without client certificates the trust store the producer checks them with)"]
    if not infos or len(infos) > 2 or not all(info["is_ca"] for info in infos) or len({info["subject"] for info in infos}) != 1:
        return [f"{kit.name}: consumer-ca.crt must hold the producer's consumer CA (one certificate; two with the same name "
                "during a rotation)"]
    if any(info["fingerprint_sha256"] not in planned for info in infos):
        return [f"{kit.name}: consumer-ca.crt holds a CA that is not the plan's consumer CA (the issuer_ca of its client certificates)"]
    return []


def check_kits(repo: Path, manifest: dict[str, Any], rerun: dict[str, Any] | None = None) -> Check:
    check = Check("E9", "Consumer kits are complete, untampered, and hold no key or key bundle")
    if manifest.get("role") == "consumer":
        return check.set("not applicable", "consumer run")
    folder = _p(repo, manifest.get("kits", "tls-migration/kits"))
    kits = sorted(p for p in folder.glob("kit-*") if p.is_dir()) if folder.is_dir() else []
    if not kits:
        if manifest.get("environment") == "local":
            return check.set("not applicable", "local run: consumers took their certificates from local-tls-up.sh")
        return check.set("not run", f"no kits in {_rel(repo, folder)}")
    planned_cas = _planned_server_cas(repo, manifest)
    problems = []
    for kit in kits:
        manifest_file = kit / "KIT-MANIFEST.json"
        if not manifest_file.exists():
            problems.append(f"{kit.name}: no KIT-MANIFEST.json")
            continue
        try:
            data = json.loads(_read(manifest_file))
        except ValueError:
            problems.append(f"{kit.name}: KIT-MANIFEST.json is not valid JSON, or not a regular file")
            continue
        if not isinstance(data, dict):
            problems.append(f"{kit.name}: KIT-MANIFEST.json is not a mapping")
            continue
        # What a kit holds is the toolkit's list, not the kit's own: the manifest travels with the kit.
        for name in dict.fromkeys(build_kit.REQUIRED + [str(n) for n in _list(data.get("required_files"))]):
            if not (kit / name).is_file():
                problems.append(f"{kit.name}: {name} missing")
        if "consumer-ca.crt" not in _list(data.get("required_files")):
            problems.append(f"{kit.name}: built by an older build_kit.py without consumer-ca.crt; rebuild it")
        endpoint_problems, values = _kit_endpoint_problems(repo, manifest, kit, data)
        problems += endpoint_problems
        if values:
            problems += _kit_toolkit_problems(kit, data, values)
        problems += _kit_consumer_ca_problems(repo, manifest, kit)
        problems += _kit_sums_problems(kit, data)
        for name, digest in (data.get("files") or {}).items():
            if not (kit / name).is_file() or tlslib.sha256_file(kit / name) != digest:
                problems.append(f"{kit.name}: {name} changed after the kit was built")
        actual = {p.relative_to(kit).as_posix() for p in kit.rglob("*") if p.is_file() or _not_regular(p) and not p.is_dir()} \
            - {"KIT-MANIFEST.json"}
        extra = actual - set(data.get("files") or {})
        if manifest.get("role") == "both":
            # In a run that is also a consumer, its own kit folder holds the two data files the
            # consumer adds: the client certificate it got back, and verify.sh's result.
            for name in sorted(extra & CONSUMER_DATA_FILES):
                problem = _consumer_data_problem(repo, manifest, kit / name)
                if problem:
                    problems.append(f"{kit.name}: {name}: {problem}")
                extra.discard(name)
        if extra:
            problems.append(f"{kit.name}: files not in the manifest: {sorted(extra)}")
        foreign = actual - set(kit_template_files()) - KIT_DATA_FILES - (CONSUMER_DATA_FILES if manifest.get("role") == "both" else set())
        if foreign:
            problems.append(f"{kit.name}: files build_kit.py never writes: {sorted(foreign)}")
        keys = [k["file"] for k in scan_rules.find_private_keys(kit) if k.get("severity", "fail") == "fail"]
        if keys:
            problems.append(f"{kit.name}: key or key bundle in the kit (a route B bundle travels separately): {keys}")
        # The kit's own manifest travels with the kit and can be re-written with
        # it. What the consumer will trust is compared with the plan directly:
        # exactly one certificate, and it is the planned server CA.
        try:
            pems = tlslib.split_bundle(kit / "ca-bundle.pem")
            problems += _kit_bundle_problems(repo, manifest, kit, data, pems, planned_cas, rerun)
        except (OSError, ValueError) as problem:
            problems.append(f"{kit.name}: ca-bundle.pem unreadable: {str(problem).replace(str(kit) + os.sep, '')}")
            continue
    if problems:
        return check.set("fail", f"{len(problems)} kit problem(s)", problems)
    route_b = [k.name for k in kits if json.loads(_read(k / "KIT-MANIFEST.json")).get("route") == "B"]
    return check.set("pass", f"{len(kits)} kit(s) complete, the toolkit's own files, sending consumers to an in-scope host, "
                     "trusting only the planned server CA and naming the planned consumer CA"
                     + (f"; route B (key travelled): {route_b}" if route_b else ""))


def check_local_dev(repo: Path, manifest: dict[str, Any]) -> Check:
    check = Check("E10", "No local-dev CA in shared config, code or kits (by name, fingerprint or parsed certificate)")
    fingerprint_file = repo / "tls-migration" / "local" / "ca-fingerprints.txt"
    fingerprints = set()
    if fingerprint_file.is_file():
        fingerprints = {line.split()[0].lower() for line in _read(fingerprint_file).splitlines() if line.strip()}
    hits = scan_rules.find_local_dev_refs(repo, fingerprints, local_run=manifest.get("environment") == "local")
    if hits:
        return check.set("fail", f"{len(hits)} reference(s) to a local-dev CA in shared config or code",
                         [f"{h['file']}:{h['line']} {quoted(h['text'])}" for h in hits])
    return check.set("pass", "local-dev CAs appear only in local-only files")


# ---------------------------------------------------------------- E11

TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")


def _section_rows(text: str, heading: str) -> list[list[str]] | None:
    """Rows of the first table after a line starting with `heading`."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip().lower().lstrip("#").strip().startswith(heading.lower()):
            rows: list[list[str]] = []
            for following in lines[index + 1:]:
                if not following.strip():
                    if rows:
                        break
                    continue
                match = TABLE_ROW.match(following.strip())
                if not match:
                    if rows:
                        break
                    if following.lstrip().startswith("#"):
                        break
                    continue
                cells = [c.strip() for c in match.group(1).split("|")]
                if all(set(c) <= set("-: ") for c in cells):
                    continue
                rows.append(cells)
            return rows[1:] if rows else []
    return None


def _endpoint_key(text: Any) -> str:
    """A URL as written in the report or in exceptions.yaml, compared without
    Markdown marks, case in the scheme and host, or a trailing slash."""
    url = str(text).strip().strip("`<>*_ ")
    match = re.match(r"(?i)^([a-z][a-z0-9+.-]*://)([^/?#]*)(.*)$", url)
    if match:
        url = match.group(1).lower() + match.group(2).lower().rstrip(".") + match.group(3)
    return url.rstrip("/")


def _stat(text: str, label: str) -> int | None:
    match = re.search(rf"{re.escape(label)}\s*:\s*\**\s*(\d+)", text, re.I)
    return int(match.group(1)) if match else None


URL_IN_CELL = re.compile(r"(?i)\b[a-z][a-z0-9+.-]*://(?:[^@/\s|]*@)?(\[[0-9a-f:]+\]|[^/\s:|`<>*?#]+)")
_SCHEME_RUN = re.compile(r"(?i)[a-z0-9+.\-]+")
_SCHEME_START = re.compile(r"(?i)\b[a-z]")


def urls_in_cell(cell: str) -> list[re.Match[str]]:
    """URL_IN_CELL.finditer(cell), in one pass (S-04): a scheme ends where its
    run of scheme characters ends, so only the first possible start of each
    run that is followed by :// is tried, never every letter of a long run."""
    found, position = [], 0
    for run in _SCHEME_RUN.finditer(cell):
        if run.start() < position or not cell.startswith("://", run.end()):
            continue
        # Every start in the run shares what follows the run, so the first one decides.
        for start in range(run.start(), run.end()):
            if _SCHEME_START.match(cell, start):
                match = URL_IN_CELL.match(cell, start)
                if match:
                    found.append(match)
                    position = match.end()
                break
    return found
HOST_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.\-]*")


def _row_hosts(cell: str) -> tuple[list[str], bool]:
    """The hosts a migrated row names: those of the URLs in its endpoint cell, or,
    for a row written in words ("orders to inventory"), each word. (hosts, from URLs)."""
    urls = [m.group(1).lower().strip("[]").rstrip(".") for m in urls_in_cell(cell)]
    if urls:
        return urls, True
    return [token.lower().rstrip(".") for token in HOST_TOKEN.findall(cell)], False


def _same_service(host: str, target: str, manifest: dict[str, Any]) -> bool:
    """True when `host` names the service `target` stands for: the same name, one
    of its Kubernetes forms, this machine for this machine, or, in a local run
    probed on this machine, the producer under any of its names."""
    host, target = host.lower().strip("[]").rstrip("."), str(target or "").lower().strip("[]").rstrip(".")
    if not host or not target:
        return False
    if host == target or (_is_loopback(host) and _is_loopback(target)):
        return True
    if Scope({"in_scope_hosts": [target]}).covers(host):
        return True
    name = str(_producer(manifest).get("name") or "").lower()
    return manifest.get("environment") == "local" and _is_loopback(target) and bool(name) \
        and Scope({"in_scope_hosts": [name]}).covers(host)


def _row_names(cell: str, target: str, manifest: dict[str, Any]) -> bool:
    hosts, from_urls = _row_hosts(cell)
    matches = [_same_service(host, target, manifest) for host in hosts]
    return bool(hosts) and (all(matches) if from_urls else any(matches))


BLOCKED_TODO = "TODO: HTTPS not supported - requires infrastructure update"
EXPIRY_WARNING_DAYS = 30
SERVER_ONLY_REF = re.compile(r"(?:tls-migration/)?(?:evidence/)?server-only/([A-Za-z0-9.\-]+_\d{1,5}\.json)")


def warning_settings(repo: Path, manifest: dict[str, Any], operator_policy: str | None) -> dict[str, Any]:
    """What turns a passing endpoint into a Warnings row (W2, W3), from the same
    policy E5 reads: max_latency_increase_pct (not set: timing is only reported),
    certificates.preferred_tls_version and certificates.preferred_ciphers. They
    only ever add Warnings rows; nothing here fails a check."""
    local = manifest.get("environment") == "local"
    path = None
    if local:
        path = _op(repo, operator_policy) if operator_policy else _p(repo, manifest.get("policy", "tls-policy.yaml"))
    elif operator_policy:
        path = Path(os.path.expanduser(operator_policy))
    policy: dict[str, Any] = {}
    if path is not None and path.is_file():
        try:
            loaded = tlslib.load_yaml(path) or {}
        except ValueError:
            loaded = {}
        policy = loaded if isinstance(loaded, dict) else {}
    certificates = policy.get("certificates") if isinstance(policy.get("certificates"), dict) else {}
    try:
        latency = float(policy["max_latency_increase_pct"]) if policy.get("max_latency_increase_pct") is not None else None
    except (TypeError, ValueError):
        latency = None
    preferred = str(certificates.get("preferred_tls_version") or "").strip() or None
    ciphers = [str(c) for c in _list(certificates.get("preferred_ciphers"))] or None
    return {"max_latency_increase_pct": latency, "preferred_tls_version": preferred, "preferred_ciphers": ciphers}


def _endpoint_warnings(observed: dict[str, Any], cert: dict[str, Any], settings: dict[str, Any], local: bool) -> list[str]:
    """The warnings one passing endpoint carries: a certificate ending within 30 days
    (a local-dev certificate on a laptop lives 30 days by design and is left out),
    TLS 1.2 where the policy prefers 1.3, a cipher outside the preferred list."""
    found = []
    issuer = str(cert.get("issuer_cn") or observed.get("issuer_cn") or "")
    if cert.get("not_after") and not (local and issuer.startswith("local-dev-")):
        try:
            left = tlslib.days_left({"not_after": cert["not_after"]})
        except (TypeError, ValueError):
            left = None
        if left is not None and 0 < left <= EXPIRY_WARNING_DAYS:
            found.append(f"certificate expires in {left:.0f} days (on {str(cert['not_after'])[:10]})")
    preferred = str(settings.get("preferred_tls_version") or "")
    if preferred in ("1.3", "TLSv1.3") and observed.get("protocol") == "TLSv1.2":
        found.append("TLS 1.2 only, where 1.3 is planned")
    ciphers = settings.get("preferred_ciphers")
    if ciphers and observed.get("cipher") and observed.get("cipher") not in ciphers:
        found.append(f"cipher {observed.get('cipher')} is outside the policy's preferred list")
    return found


def expected_warnings(repo: Path, manifest: dict[str, Any], e6: Check | None, settings: dict[str, Any]) -> list[tuple[str, str]]:
    """(host, warning) for every endpoint E6 passed with a warning, from what E6 observed."""
    if e6 is None:
        return []
    local = manifest.get("environment") == "local"
    found: list[tuple[str, str]] = []
    derived = e6.derived_probes or {}
    p9 = e6.observed_probes.get("P9") if derived.get("P9") == "pass" else None
    if p9 is not None:
        found += [(e6.probe_target or "", text) for text in _endpoint_warnings(p9, p9, settings, local)]
    p1 = e6.observed_probes.get("P1") if derived.get("P1") == "pass" else None
    limit = settings.get("max_latency_increase_pct")
    if p1 is not None and limit is not None and p1.get("total_ms"):
        before = _baseline_ms(repo, manifest)
        if before:
            increase = (float(p1["total_ms"]) - before) / before * 100
            if increase > limit:
                found.append((e6.probe_target or "", f"{increase:.0f}% slower than before ({before:.0f} ms to "
                              f"{float(p1['total_ms']):.0f} ms), over the policy's {limit:g}%"))
    for _name, (host, result, observed) in sorted((e6.server_only or {}).items()):
        if result == "pass":
            cert = observed.get("certificate") if isinstance(observed.get("certificate"), dict) else {}
            found += [(host, text) for text in _endpoint_warnings(observed, cert, settings, local)]
    return found


def _baseline_ms(repo: Path, manifest: dict[str, Any]) -> float | None:
    """The total time the baseline recorded for P1's path, before the migration."""
    try:
        plan = _probe_plan(repo, manifest)
        path = str((plan.get("target") or {}).get("path") or "/")
        data = json.loads(_read(_p(repo, plan["baseline"]))) if plan.get("baseline") else {}
        value = (data.get(path) or {}).get("total_ms") if isinstance(data, dict) else None
        return float(value) if value else None
    except (KeyError, OSError, TypeError, ValueError):
        return None


def _tables(text: str) -> list[list[list[str]]]:
    """Every Markdown table of a text, each a list of rows (header first, no separator rows)."""
    tables, current = [], []
    for line in text.splitlines() + [""]:
        match = TABLE_ROW.match(line.strip())
        if match:
            cells = [c.strip() for c in match.group(1).split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                current.append(cells)
            continue
        if current:
            tables.append(current)
            current = []
    return tables


def blocked_endpoints(repo: Path, manifest: dict[str, Any], exceptions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """The exceptions whose endpoint the inventory (01-inventory.md, column
    Decision) marks blocked, and the problems: a blocked row that no exception
    leaves on HTTP, or a blocked endpoint's plain-HTTP line without the TODO comment."""
    path = _p(repo, manifest.get("inventory_report", "tls-migration/01-inventory.md"))
    if not path.is_file():
        return [], []
    rows: list[str] = []
    for table in _tables(_read(path)):
        header = [cell.lower() for cell in table[0]]
        if "decision" not in header:
            continue
        decision = header.index("decision")
        endpoint = header.index("endpoint") if "endpoint" in header else 0
        rows += [row[endpoint] for row in table[1:] if len(row) > max(decision, endpoint)
                 and row[decision].strip("`*_ ").lower().startswith("blocked")]
    blocked, problems = [], []
    for cell in rows:
        hosts, _ = _row_hosts(cell)
        matching = [entry for entry in exceptions if any(_same_service(h, entry["_host"], {}) for h in hosts)]
        if not matching:
            problems.append(f"the inventory marks {quoted(cell, 60)} blocked, but exceptions.yaml does not leave it on HTTP")
        blocked += [entry for entry in matching if entry not in blocked]
    if blocked:
        for hit in scan_rules.find_http_urls(repo):
            host = str(hit["host"]).lower().rstrip(".")
            if hit.get("doc") or TEST_PATH.search(str(hit.get("file", ""))) or not any(_same_service(host, e["_host"], {}) for e in blocked):
                continue
            try:
                lines = _read(_p(repo, hit["file"])).splitlines()
            except (OSError, ValueError):
                continue
            near = "\n".join(lines[max(0, int(hit["line"]) - 4):int(hit["line"])]).lower()
            if BLOCKED_TODO.lower() not in near:
                problems.append(f"{hit['file']}:{hit['line']} calls the blocked endpoint {host} without the comment "
                                f"'{BLOCKED_TODO}' on that line or the three above")
    return blocked, problems


def _section_body(text: str, heading: str) -> str | None:
    """The text under the first heading line that starts with `heading`, up to the next heading."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") and stripped.lstrip("#").strip().lower().startswith(heading.lower()):
            body = []
            for following in lines[index + 1:]:
                if following.strip().startswith("#"):
                    break
                body.append(following)
            return "\n".join(body)
    return None


def _total_line(text: str) -> int | None:
    match = re.search(r"(?im)^[ \t]*(?:[-*][ \t]*)?\**Total\**[ \t]*:[ \t]*\**[ \t]*(\d+)[ \t]*\**[ \t]+endpoints?\b", text)
    return int(match.group(1)) if match else None


def _percent(text: str, label: str) -> float | None:
    match = re.search(rf"{re.escape(label)}\s*:\s*\**\s*\d+\s*\**\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)", text, re.I)
    return float(match.group(1)) if match else None


def report_format_problems(repo: Path, manifest: dict[str, Any], text: str, migrated: list[list[str]],
                           exceptions: list[dict[str, Any]], not_proven: list[list[str]] | None,
                           e6: Check | None, settings: dict[str, Any]) -> list[str]:
    """W2: the Total line, the percentages, Blocked by infrastructure, the Warnings
    table, and the Warnings, Consumers and Rollback sections."""
    problems = []
    for names, what in ((("Endpoints with Warnings", "Warnings"), "Warnings"), (("Consumers",), "Consumers"), (("Rollback",), "Rollback")):
        body = next((b for b in (_section_body(text, n) for n in names) if b is not None), None)
        if body is None:
            problems.append(f"no '{what}' section (the report format keeps it)")
        elif what != "Warnings" and not any(line.strip() for line in body.splitlines()):
            problems.append(f"the '{what}' section is empty")
    blocked, blocked_problems = blocked_endpoints(repo, manifest, exceptions)
    problems += blocked_problems
    stats = {"Successfully migrated": len(migrated), "Remaining on HTTP": len(exceptions) - len(blocked),
             "Not proven": len(not_proven or []), "Blocked by infrastructure": len(blocked)}
    total = sum(stats.values())
    stated_total = _total_line(text)
    if stated_total is None:
        problems.append("statistics: no 'Total: <n> endpoints' line")
    elif stated_total != total:
        problems.append(f"statistics: 'Total: {stated_total} endpoints' is not migrated + remaining + not proven + blocked ({total})")
    older = _stat(text, "Total endpoints identified")
    if older is not None and older != total:
        problems.append(f"statistics: total {older} is not migrated + remaining + not proven + blocked ({total})")
    for label, expected in stats.items():
        stated = _stat(text, label)
        if stated is None:
            problems.append(f"statistics: no '{label}' line")
        elif stated != expected:
            problems.append(f"statistics: '{label}: {stated}' but the tables and evidence give {expected}")
    for label in ("Successfully migrated", "Remaining on HTTP"):
        percent = _percent(text, label)
        wanted = 100.0 * stats[label] / total if total else 0.0
        if percent is None:
            problems.append(f"statistics: '{label}' needs its share of the total in per cent, as '(<n>%)'")
        elif abs(percent - wanted) > 1:
            problems.append(f"statistics: '{label}' says {percent:g}%, but {stats[label]} of {total} is {wanted:.0f}%")
    rows = next((r for r in (_section_rows(text, n) for n in ("Endpoints with Warnings", "Warnings")) if r is not None), None)
    body = next((b for b in (_section_body(text, n) for n in ("Endpoints with Warnings", "Warnings")) if b is not None), "")
    none_said = any(line.strip().strip("`*_-| ").lower() == "none" for line in body.splitlines()) \
        or any(row and row[0].strip("`*_ ").lower() == "none" for row in rows or [])
    warning_rows = [row for row in rows or [] if row and row[0].strip("`*_ ").lower() != "none"]
    if rows is not None or body:
        if not warning_rows and not none_said:
            problems.append("the Warnings table has no row: write 'none' when no endpoint passed with a warning")
        for host, warning in expected_warnings(repo, manifest, e6, settings):
            if not any(_row_names(row[0], host, manifest) for row in warning_rows):
                problems.append(f"E6 shows a warning for {host or '?'} ({warning}), but the Warnings table has no row for it")
        for row in warning_rows:
            hosts, _ = _row_hosts(row[0])
            if not any(_row_names(m[0], h, manifest) for m in migrated if m for h in hosts):
                problems.append(f"Warnings row {quoted(row[0], 60)} is not a migrated endpoint: a Warnings row is counted inside "
                                "'Successfully migrated'")
    return problems


CONSUMER_ROLE = re.compile(r"(?i)^\W*we consume\b(?:\s*\(\s*([A-Za-z0-9][A-Za-z0-9_.\-]*))?")


def _row_consumer(role_cell: str, manifest: dict[str, Any]) -> str | None:
    """The consumer in this repository a migrated "we consume" row stands for: the
    name in its Role cell ("we consume (orders, CN=orders)"), or the only
    consumer of the manifest's consumers_of_others that needs a client
    certificate. "" for a "we consume" row that names neither; None for any other row."""
    match = CONSUMER_ROLE.match(role_cell or "")
    if not match:
        return None
    if match.group(1) and match.group(1).lower() not in ("internal", "no"):
        return match.group(1).lower()
    services = {str(entry.get("service") or "").lower() for entry in _list(manifest.get("consumers_of_others"))
                if isinstance(entry, dict) and entry not in server_only_rows(manifest) and entry.get("service")}
    return services.pop() if len(services) == 1 else ""


def consumer_own_evidence(repo: Path, manifest: dict[str, Any], consumer: str) -> str | None:
    """Evidence that the consumer's OWN client certificate worked, outside local, where
    P1 is sent with the probe certificate (tls-probe-allowed): a verify-result from
    its kit (evidence/verify-result-<consumer>.json, a file listed in
    consumer_verify, or <kits>/<kit>/verify-result.json) that shows ok for that
    consumer's CN; or the producer's access log with that CN let through over
    mutual TLS, untagged (a call that can only happen once the producer serves
    HTTPS, so after the cutover started). None when there is neither."""
    candidates = [_p(repo, f) for f in _list(_evidence(manifest).get("consumer_verify"))]
    candidates.append(_p(repo, f"tls-migration/evidence/verify-result-{consumer}.json"))
    kits = _p(repo, manifest.get("kits", "tls-migration/kits"))
    if kits.is_dir() and not kits.is_symlink():
        candidates += sorted(kits.glob("*/verify-result.json"))
    for path in candidates:
        if not path.is_file() or path.is_symlink():
            continue
        try:
            data = json.loads(_read(path))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("ok") is True and data.get("client_cn_matches_consumer") is not False \
                and str(data.get("client_cn") or "").lower() == consumer \
                and str(data.get("consumer") or consumer).lower() == consumer:
            return f"{_rel(repo, path)} shows ok for CN={consumer}"
    log = _producer(manifest).get("access_log") if manifest.get("role") in ("producer", "both") else None
    if log and _p(repo, log).is_file() and not _not_regular(_p(repo, log)):
        try:
            events = readiness.read_events([str(_p(repo, log))], set(), [])
        except (OSError, ValueError):
            events = []
        seen = [e for e in events if str(e.get("cn") or "").lower() == consumer and readiness.moved(e)]
        if seen:
            return f"{_rel(repo, _p(repo, log))}: {len(seen)} call(s) from cn={consumer} let through over mutual TLS"
    return None


def check_report(repo: Path, manifest: dict[str, Any], probes_path: Path, gate_result: str,
                 live_probes: dict[str, str] | None = None, probe_target: str | None = None, live: bool = False,
                 e6: Check | None = None, settings: dict[str, Any] | None = None) -> Check:
    """live_probes: the probe results E6 re-derived (live or recorded), and
    probe_target the host they probed. A cited probe counts only when E6 judged
    it; what probes.json says on its own is never read here. e6 is E6 itself
    (server-only rows, what it observed), settings the warning settings."""
    check = Check("E11", "The summary report matches the evidence")
    path = _p(repo, manifest.get("report", "tls-migration/03-migration-summary.md"))
    if _not_regular(path):
        return check.set("fail", f"{_rel(repo, path)} is not a regular file (a pipe, socket, device or folder): not read")
    if not path.exists():
        stage = int(_producer(manifest).get("stage", 6))
        if manifest.get("role") != "consumer" and stage < 6:
            return check.set("not run", f"no summary report yet; the run is at stage {stage}")
        return check.set("fail", "no summary report (tls-migration/03-migration-summary.md)")
    text = _read(path)
    probe_results: dict[str, str] = dict(live_probes or {})
    verify_files = {Path(str(f)).name: _p(repo, f) for f in _list(_evidence(manifest).get("consumer_verify"))}
    problems, unproven = [], []
    migrated = _section_rows(text, "Successfully Migrated")
    remaining = _section_rows(text, "Endpoints Remaining on HTTP")
    not_proven = _section_rows(text, "Not proven")
    if migrated is None:
        problems.append("no 'Successfully Migrated Endpoints' table")
        migrated = []
    for row in migrated:
        evidence_cell = row[-1] if row else ""
        refs = re.findall(r"probes\.json#(P\d+)", evidence_cell)
        verify_refs = [name for name in verify_files if name in evidence_cell]
        server_refs = [f"{probe_tls.SERVER_ONLY_FOLDER}/{name}" for name in SERVER_ONLY_REF.findall(evidence_cell)]
        if not refs and not verify_refs and not server_refs:
            problems.append(f"migrated row '{row[0]}' cites no probe, verify-result or server-only evidence")
        consumer = _row_consumer(row[1], manifest) if len(row) > 2 else None
        if consumer is not None and not server_refs and manifest.get("environment") != "local" \
                and manifest.get("role") in ("consumer", "both"):
            # Outside local P1 is sent with the probe certificate, not the consumer's own (E11, consumer rows).
            if not consumer:
                problems.append(f"migrated row '{row[0]}' is a consumer row that does not name its consumer "
                                "(Role: we consume (<consumer>))")
            elif consumer_own_evidence(repo, manifest, consumer) is None:
                problems.append(f"migrated row '{row[0]}': no evidence that {consumer}'s own certificate was used "
                                f"(P1 outside local uses the probe certificate); keep verify-result-{consumer}.json from "
                                f"its kit, or the producer's access log must show cn={consumer} let through over mutual TLS")
        planned_server_only = {probe_tls.server_only_file(*parsed) for parsed in
                               (probe_tls.parse_endpoint(entry.get("endpoint")) for entry in server_only_rows(manifest)) if parsed}
        for name in server_refs:
            judged = (e6.server_only or {}) if e6 is not None else {}
            if name not in planned_server_only:
                problems.append(f"migrated row '{row[0]}' cites {name}, which is not a server-only row of the manifest "
                                "(consumers_of_others with client_certificate: none and its endpoint)")
            elif name not in judged:
                unproven.append(f"migrated row '{row[0]}' cites {name}, which E6 did not judge (not run)")
            elif judged[name][1] != "pass":
                problems.append(f"migrated row '{row[0]}' cites {name}, which is '{judged[name][1]}'")
            elif not _row_names(row[0], judged[name][0], manifest):
                problems.append(f"migrated row '{row[0]}' cites {name}, which probed {judged[name][0]}, not that endpoint")
        for ref in refs:
            if live_probes is None:
                (unproven if manifest.get("role") != "consumer" else problems).append(
                    f"migrated row '{row[0]}' cites {ref}, but E6 re-derived no probe results to hold it against")
            elif ref not in probe_results:
                problems.append(f"migrated row '{row[0]}' cites {ref}, which E6 did not re-derive (not a probe the stage "
                                "requires, or not recorded)")
            elif probe_results[ref] != "pass":
                problems.append(f"migrated row '{row[0]}' cites {ref}, which is '{probe_results[ref]}'")
            elif not _row_names(row[0], probe_target or "", manifest):
                problems.append(f"migrated row '{row[0]}' cites {ref}, which probed {probe_target or '?'}, not that endpoint")
        for name in verify_refs:
            try:
                data = json.loads(_read(verify_files[name])) if verify_files[name].is_file() else {}
            except ValueError:
                data = {}
            if not isinstance(data, dict) or data.get("ok") is not True:
                problems.append(f"migrated row '{row[0]}' cites {name}, which does not show ok")
                continue
            called = re.sub(r"(?i)^https://(?:[^@/]*@)?(\[[^\]]+\]|[^/:]+).*$", r"\1", str(data.get("endpoint", "")))
            if not str(data.get("endpoint", "")).lower().startswith("https://") or not _row_names(row[0], called, manifest):
                problems.append(f"migrated row '{row[0]}' cites {name}, which called {quoted(data.get('endpoint', '?'), 60)}, "
                                "not that endpoint")
    exceptions, _ = load_exceptions(repo, manifest)
    if remaining is None:
        # The heading is part of the report's format: an empty table says nothing stays on HTTP.
        problems.append("no 'Endpoints Remaining on HTTP' table (keep it, empty when exceptions.yaml leaves nothing on HTTP)"
                        + (f"; exceptions.yaml leaves {len(exceptions)} endpoint(s) on HTTP" if exceptions else ""))
    if remaining is not None:
        # The same endpoints, not merely as many: each row's URL against exceptions.yaml.
        listed = {_endpoint_key(row[0]) for row in remaining if row}
        excepted = {_endpoint_key(entry["url"]) for entry in exceptions}
        if len(remaining) != len(exceptions):
            problems.append(f"'Remaining on HTTP' lists {len(remaining)} endpoint(s); exceptions.yaml has {len(exceptions)}")
        for url in sorted(listed - excepted):
            problems.append(f"'Remaining on HTTP' lists {quoted(url, 80)}, which is not in exceptions.yaml")
        for url in sorted(excepted - listed):
            problems.append(f"exceptions.yaml leaves {quoted(url, 80)} on HTTP, but 'Remaining on HTTP' does not list it")
    problems += report_format_problems(repo, manifest, text, migrated, exceptions, not_proven, e6, settings or {})
    claimed = re.search(r"Overall result\s*:\s*\**\s*(pass with exceptions|pass|not proven|fail)", text, re.I)
    order = ["fail", "not proven", "pass with exceptions", "pass"]
    if not claimed:
        problems.append("no 'Overall result:' line")
    elif order.index(claimed.group(1).lower()) > order.index(gate_result):
        problems.append(f"the report claims '{claimed.group(1)}' but the checks give '{gate_result}'")
    if re.search(r"not run[^\n|]*\|\s*✅", text):
        problems.append("a check marked not run is shown with ✅")
    if problems:
        return check.set("fail", f"{len(problems)} mismatch(es) between the report and the evidence", problems + unproven)
    if unproven:
        return check.set("not run", f"{len(unproven)} cited probe(s) could not be held against re-derived results", unproven)
    source = "the live probes" if live else "the recorded probes as E6 re-derived them"
    return check.set("pass", f"{len(migrated)} migrated row(s) each cite passing evidence from {source}, for the endpoint "
                     "it names; statistics, percentages and warnings add up")


# ---------------------------------------------------------------- E12: the producer's configuration, the way Spring reads it

STAGE_KEYS = ("server.ssl.client-auth", "server.ssl.enabled", "tls.migration.legacy-http.enabled",
              "tls.migration.allowlist.enforce", "server.ssl.enabled-protocols")
STAGE_CANON = {tlslib.canonical(key): key for key in STAGE_KEYS}
BOOLEAN_KEYS = {"server.ssl.enabled", "tls.migration.legacy-http.enabled", "tls.migration.allowlist.enforce"}
# spring.config.import and additional-location add files; spring.config.location
# adds them too here, and with spring.config.name it REPLACES the files Spring
# reads by default (application.* in the usual places): see ProducerConfig.
# Inside a config file only spring.config.import is followed: Spring Boot 3.4
# takes spring.config.location and additional-location from the environment,
# system properties and the command line only (checked on the reference pair:
# written in application.yml, both are ignored).
IMPORT_CANON = {tlslib.canonical(k) for k in ("spring.config.import", "spring.config.location", "spring.config.additional-location")}
FILE_IMPORT_CANON = tlslib.canonical("spring.config.import")
LOCATION_CANON = tlslib.canonical("spring.config.location")
NAME_CANON = tlslib.canonical("spring.config.name")
# Names gate code looks up: a file spelling binds to one only with the same dotted parts.
KNOWN_KEYS = STAGE_KEYS + ("server.ssl.bundle", "server.ssl.trust-store", "server.ssl.trust-certificate", "server.port",
                           "management.server.port", "tls.migration.legacy-http.port", "spring.profiles.active",
                           "spring.profiles.include", "spring.config.import", "spring.config.location",
                           "spring.config.additional-location", "spring.config.name", "spring.config.activate.on-profile")
KNOWN_SHAPES = {tlslib.canonical(k): [tlslib.canonical(p) for p in k.split(".")] for k in KNOWN_KEYS}
PROFILE_CANON = {tlslib.canonical(k) for k in ("spring.profiles.active", "spring.profiles.include")}
INCLUDE_CANON = tlslib.canonical("spring.profiles.include")
JSON_CANON = tlslib.canonical("spring.application.json")
PLACEHOLDER = re.compile(r"\$\{([^:}]+)(?::([^}]*))?\}")


def placeholders(text: str) -> list[re.Match[str]]:
    """PLACEHOLDER.finditer(text), in one pass (S-04): a start with no } after it
    can never match, and neither can any later one, so the search stops there."""
    found, position = [], 0
    while True:
        start = text.find("${", position)
        if start < 0 or text.find("}", start) < 0:
            return found
        match = PLACEHOLDER.match(text, start)
        if match:
            found.append(match)
            position = match.end()
        else:
            position = start + 1


def replace_placeholders(text: str, replace: Callable[[re.Match[str]], str]) -> str:
    """PLACEHOLDER.sub(replace, text), in one pass."""
    out, position = [], 0
    for match in placeholders(text):
        out += [text[position:match.start()], replace(match)]
        position = match.end()
    return "".join(out) + text[position:]
# Where a service takes its certificate, key and trust from.
TLS_PREFIXES = ("springsslbundle", "serverssltrust")
BUNDLE_KEY = re.compile(r"^springsslbundle(pem|jks)(.+?)(truststore|keystore)(certificate|privatekey|location)$")
SYSTEM_STORE = re.compile(r"(?i)(^|/)(etc/ssl|etc/pki|usr/(local/)?share/ca-certificates|usr/lib/ssl|lib/security)/"
                          r"|(^|/)(cacerts|ca-certificates\.crt|ca-bundle\.crt|tls-ca-bundle\.pem)$")


class Settings(dict):
    """Config values under their written keys. find() also sees the relaxed
    spellings Spring binds: client-auth, clientAuth, client_auth, CLIENT_AUTH."""

    def __init__(self) -> None:
        super().__init__()
        self.canon: dict[str, str] = {}
        self.origin: dict[str, str] = {}
        self.ignored: list[str] = []      # file keys Spring does not bind (an environment-variable spelling)

    def put(self, key: str, value: str, origin: str = "") -> None:
        self[key] = value
        self.canon[tlslib.canonical(key)] = value
        self.origin[tlslib.canonical(key)] = origin

    def find(self, key: str, default: str = "") -> str:
        return self.canon.get(tlslib.canonical(key), default)

    def copy_with(self, key: str, value: str, origin: str) -> "Settings":
        other = Settings()
        other.update(self)
        other.canon, other.origin = dict(self.canon), dict(self.origin)
        other.ignored = list(self.ignored)
        other.put(key, value, origin)
        return other


def binds_in_file(key: str) -> bool:
    """Whether a key written in a config file (YAML, .properties, JSON) binds a
    dotted property. Spring's relaxed binding accepts kebab, camel and
    underscore spellings of each dotted part in a file, but the upper-case
    environment-variable form (SERVER_SSL_CLIENTAUTH) only from the
    environment: inside a file it is another, unused name, and must never stand
    in for (or hide) the real one."""
    if "." not in key:
        return False
    shape = KNOWN_SHAPES.get(tlslib.canonical(key))
    return shape is None or [tlslib.canonical(part) for part in key.split(".")] == shape


def profile_active(expression: Any, profiles: set[str]) -> bool:
    """Spring's profile expressions: a list or commas mean "any of"; ! & | and
    brackets as Spring reads them. One this reader cannot follow counts as
    ACTIVE: a document that may apply must satisfy the stage."""
    for item in _list(expression):
        for part in str(item).split(","):
            tokens = re.findall(r"[!&|()]|[^\s!&|()]+", part)
            if not tokens:
                continue
            position = 0

            def parse_or() -> bool:
                nonlocal position
                value = parse_and()
                while position < len(tokens) and tokens[position] == "|":
                    position += 1
                    value = parse_and() or value
                return value

            def parse_and() -> bool:
                nonlocal position
                value = parse_not()
                while position < len(tokens) and tokens[position] == "&":
                    position += 1
                    value = parse_not() and value
                return value

            def parse_not() -> bool:
                nonlocal position
                if position >= len(tokens):
                    raise ValueError("incomplete")
                token = tokens[position]
                position += 1
                if token == "!":
                    return not parse_not()
                if token == "(":
                    value = parse_or()
                    if position >= len(tokens) or tokens[position] != ")":
                        raise ValueError("unbalanced")
                    position += 1
                    return value
                if token in "&|)":
                    raise ValueError("misplaced operator")
                return token in profiles

            try:
                value = parse_or()
                if position != len(tokens):
                    raise ValueError("trailing text")
            except ValueError:
                return True
            if value:
                return True
    return False


def _expression_profiles(expression: Any) -> set[str]:
    return {token for item in _list(expression) for token in re.findall(r"[^\s!&|(),]+", str(item))}


# The separator is one of three forms tried in turn, never two runs of white
# space that could share the same characters (S-04: no overlapping quantifiers).
PROPERTIES_LINE = re.compile(r"(?P<key>(?:\\.|[^=:\s\\])+)(?:\s*[=:]\s*|\s+|$)(?P<value>.*)$")


def parse_properties(text: str) -> list[tuple[Any, dict[str, str]]]:
    """A .properties text as Spring reads it, as documents: (profile guard or None,
    keys with their raw values). Values continued with a trailing backslash are
    joined first; key and value are separated by '=', ':' or white space; "#---"
    or "!---" on a line of its own starts a new document (Spring Boot 2.4+), each
    with its own on-profile guard. A byte-order mark at the start is not part of
    the first key (Spring Boot 3.4 binds that key: checked on the reference pair)."""
    text = scan_rules.join_continuations(text.lstrip("\ufeff"))
    documents: list[tuple[Any, dict[str, str]]] = []
    flat: dict[str, str] = {}
    for line in text.splitlines() + ["#---"]:
        line = line.strip()
        if line in ("#---", "!---"):
            if flat:
                canon = {tlslib.canonical(k): v for k, v in flat.items()}
                documents.append((canon.get(tlslib.canonical("spring.config.activate.on-profile"))
                                  or canon.get(tlslib.canonical("spring.profiles")), flat))
            flat = {}
            continue
        if not line or line.startswith(("#", "!")):
            continue
        match = PROPERTIES_LINE.match(line)
        if match:
            flat[re.sub(r"\\(.)", r"\1", match.group("key"))] = match.group("value").strip()
    return documents or [(None, {})]


# A YAML document separator: "---" alone, or followed by a comment.
DOC_SEPARATOR = re.compile(r"(?m)^---[ \t]*(?:#[^\n]*)?$")


def yaml_documents_of(text: str) -> list[Any]:
    """Every document of a YAML text, the way SnakeYAML (Spring's reader) splits
    them: PyYAML's safe_load_all when present, else the subset reader on each
    part between separators ("--- # a comment" included). Raises on bad YAML."""
    if tlslib._pyyaml is not None:  # noqa: SLF001
        return list(tlslib._pyyaml.safe_load_all(text))  # noqa: SLF001
    return [tlslib.parse_yaml_subset(part) for part in DOC_SEPARATOR.split(text) if part.strip()]


def flatten_config(path: Path) -> list[tuple[Any, dict[str, str]]]:
    """A Spring application.yml / .properties as documents: (profile guard or
    None, dotted keys with their raw values). Placeholders are kept as written."""
    if path.suffix == ".properties":
        return parse_properties(scan_rules.read_text(path) or "")
    text = path.read_text(encoding="utf-8-sig", errors="replace")

    def walk(prefix: str, value: Any, into: dict[str, str]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                walk(f"{prefix}.{key}" if prefix else str(key), child, into)
        elif isinstance(value, list):
            into[prefix] = ",".join(str(v) for v in value)
            for index, child in enumerate(value):
                walk(f"{prefix}[{index}]", child, into)
        else:
            into[prefix] = "" if value is None else (str(value).lower() if isinstance(value, bool) else str(value))

    documents = []
    for parsed in yaml_documents_of(text):
        if parsed is None:
            continue
        layer: dict[str, str] = {}
        walk("", parsed or {}, layer)
        canon = {tlslib.canonical(k): v for k, v in layer.items()}
        guard = canon.get(tlslib.canonical("spring.config.activate.on-profile")) or canon.get(tlslib.canonical("spring.profiles"))
        documents.append((guard, layer))
    return documents


def _split_locations(value: Any) -> list[str]:
    return [part.strip() for item in _list(value) for part in re.split(r"[,;]", str(item)) if part.strip()]


def _import_targets(repo: Path, location: str, importer: Path | None) -> tuple[list[Path], str | None]:
    """Files a spring.config.import / location value points at, inside the
    repository. (files, why it cannot be read) - one of the two is empty."""
    text = location
    optional = text.startswith("optional:")
    text = text[len("optional:"):] if optional else text
    if re.match(r"^(?!file:|classpath:)[a-z][a-z0-9+.-]*:", text):
        return [], f"{location} (a source outside the repository)"
    kind = "file"
    if text.startswith("classpath:"):
        kind, text = "classpath", text[len("classpath:"):]
    elif text.startswith("file:"):
        text = text[len("file:"):]
    text = text.lstrip("/") if kind == "classpath" else text
    if "$" in text or "{{" in text:
        return [], f"{location} (a path filled in at run time)"
    bases: list[Path] = []
    if kind == "classpath":
        bases = [p for p in repo.rglob("src/main/resources") if p.is_dir() and "target" not in p.parts][:20]
    else:
        if os.path.isabs(text):
            return [], f"{location} (an absolute path: a file mounted where the service runs, not in the repository)"
        bases = [repo] + ([importer.parent] if importer else []) + [p.parent.parent.parent for p in repo.rglob("src/main/resources")
                                                                   if p.is_dir() and "target" not in p.parts][:20]
    found: list[Path] = []
    for base in bases:
        candidate = base / text
        if candidate.is_dir():
            # A folder: Spring reads its application.* files, profile files for the active profiles.
            found += [p for p in sorted(candidate.iterdir()) if tlslib.CONFIG_NAME.match(p.name)]
        elif candidate.is_file():
            found.append(candidate)
    if not found:
        # An optional classpath file that is not in the sources is not in the jar either.
        return [], None if optional and kind == "classpath" else f"{location} (not found in the repository)"
    return list(dict.fromkeys(found)), None


def _folder_import(location: str) -> bool:
    """A location that names a folder (ends in /): its profile files follow the profiles."""
    return location.rstrip().endswith("/")


PAIR = re.compile(r"(?<![\w.\-${])(?:-D|--)?([A-Za-z][A-Za-z0-9_.\-]{2,80})[\"']?[ \t]*[:=][ \t]*[\"']?([^\"'\s,;}\]#]*)")
K8S_ENV = re.compile(r"name:\s*[\"']?([A-Za-z_][A-Za-z0-9_.\-]*)[\"']?\s*\n\s*value:\s*[\"']?([^\"'\n#]*)"
                     r"|value:\s*[\"']?([^\"'\n#]*?)[\"']?\s*\n\s*(?:-\s*)?name:\s*[\"']?([A-Za-z_][A-Za-z0-9_.\-]*)")
FLOW_ENV = re.compile(r"\{\s*name:\s*[\"']?([A-Za-z_][A-Za-z0-9_.\-]*)[\"']?\s*,\s*value:\s*[\"']?([^\"',}\n]*)")
# The value runs to its last character that is not white space (one blank
# when there is none): no run of blanks can be read two ways (S-04).
DOCKER_ENV = re.compile(r"(?im)^[ \t]*ENV[ \t]+([A-Za-z_][A-Za-z0-9_]*)[ \t]+([^\n=]*[^\n= \t]|[ \t])[ \t]*$")
JSON_ENV = re.compile(r"SPRING_APPLICATION_JSON[\"']?[ \t]*(?:[:=]|\n[ \t]*value:)[ \t]*['\"]?(?P<json>\{[^\n]*\})")


APP_JSON_ARG = re.compile(r"(?i)(?<![\w.])(?:-D|--)?(spring[._-]?application[._-]?json)[\"']?[ \t]*[=:][ \t]*")


def json_after(text: str, position: int) -> str | None:
    """The JSON object that starts at `position` (after an optional quote or an
    escaped one), normalised; None when there is none or it does not parse. It
    is read in every form it is written in: plain, inside single quotes, or with
    escaped quotes inside a JSON string (a Dockerfile's exec form)."""
    index = position
    while index < len(text) and index - position < 4 and text[index] in "'\"\\ ":
        index += 1
    if index >= len(text) or text[index] != "{":
        return None
    depth, end = 0, None
    for cursor in range(index, min(len(text), index + 20000)):
        if text[cursor] == "{":
            depth += 1
        elif text[cursor] == "}":
            depth -= 1
            if depth == 0:
                end = cursor
                break
    if end is None:
        return None
    candidate = text[index:end + 1]
    for form in (candidate, candidate.replace('\\"', '"').replace("\\\\", "\\")):
        try:
            return json.dumps(json.loads(form), sort_keys=True)
        except ValueError:
            continue
    return None


# A config-format file in a module's resources. Spring Boot loads one only when
# something names it: an import, spring.config.* given to the service, a
# @PropertySource, a mount or copy in a deployment. Named nowhere, it is in the
# jar and never read (checked on the reference pair: custom.yml with want is
# ignored; imported, it is in force).
RESOURCE_CONFIG = re.compile(r"(^|/)src/main/resources/(?:.+/)?[^/]+\.(?:ya?ml|properties)$")
# Loaded by name, with nothing naming them: Spring Cloud's bootstrap context reads these.
LOADED_BY_NAME = re.compile(r"^bootstrap(?:-[A-Za-z0-9_.]+)?\.(?:ya?ml|properties)$")
# Code that loads property files in a way the gate cannot tie to a file name.
DYNAMIC_LOADER = re.compile(r"\b(?:EnvironmentPostProcessor|PropertySourceLoader|YamlPropertiesFactoryBean|YamlMapFactoryBean"
                            r"|PropertiesFactoryBean|ResourcePropertySource|PropertiesLoaderUtils|ConfigDataLocationResolver"
                            r"|ConfigDataLoader|PropertySourcesPlaceholderConfigurer|PropertyPlaceholderConfigurer"
                            r"|getPropertySources|property-placeholder)\b")
PROPERTY_SOURCE = re.compile(r"@(?:[\w.]+\.)?PropertySources?\s*\(")
LOADER_FILES = re.compile(r"(^|/)src/main/.+\.(?:java|kt|kts|groovy|scala|xml|factories|imports)$")
JAVA_STRING = re.compile(r'"(?:\\.|[^"\\\n])*"')


def _property_source_unclear(text: str) -> str | None:
    """Why a @PropertySource's locations cannot be read from the code (a constant,
    a placeholder, a pattern), or None when every location is a plain literal."""
    for match in PROPERTY_SOURCE.finditer(text):
        depth, end = 0, None
        for cursor in range(match.end() - 1, min(len(text), match.end() + 4000)):
            if text[cursor] == "(":
                depth += 1
            elif text[cursor] == ")":
                depth -= 1
                if depth == 0:
                    end = cursor
                    break
        # Never more than the 4000 characters searched for the closing parenthesis: the
        # patterns below are tried from every position, so their work stays bounded (S-04).
        arguments = text[match.end():end] if end is not None else text[match.end():match.end() + 4000]
        # The string literals, read in one pass (S-04: an unclosed one is not re-read from every later quote).
        spans = scan_rules.lex_tokens(arguments, "dq")
        literals = [arguments[start:end] for start, end in spans]
        if any("${" in literal or "*" in literal for literal in literals):
            return "a @PropertySource location with a placeholder or a pattern"
        rest = "".join(arguments[end:start] for end, start in zip([0] + [e for _, e in spans], [s for s, _ in spans] + [len(arguments)]))
        rest = re.sub(r"[\w.]+\.class|::class(?:\.java)?|\b(?:value|name|encoding|ignoreResourceNotFound|factory|true|false)\b"
                      r"|@(?:[\w.]+\.)?PropertySource\b|[=,{}\[\]()\s]", "", rest)
        if rest or not literals:
            return "a @PropertySource whose location is not written as a literal"
    return None


def unloaded_resource_configs(repo: Path, taken: set[str]) -> tuple[set[str], list[str]]:
    """Config-format files under src/main/resources that nothing loads, so Spring
    never reads them: not named application* (the reader's own), not a source
    the reader took (an import), and named by no other file in the repository
    (code, build files, deployment files, scripts, other config; documentation,
    test sources and the run's evidence records do not load anything). A file
    that is named anywhere is read as before. Where the code loads property
    files in a way the gate cannot follow, none is left out.
    Returns (files to leave out, evidence notes)."""
    files = list(scan_rules.iter_files(repo))
    candidates = [rel for rel in (_rel(repo, path) for path in files)
                  if RESOURCE_CONFIG.search(rel) and not tlslib.CONFIG_NAME.match(Path(rel).name)
                  and not LOADED_BY_NAME.match(Path(rel).name)
                  and rel not in taken and not SOURCE_TEST.search(rel)]
    if not candidates:
        return set(), []
    named: dict[str, re.Pattern[str]] = {rel: re.compile(r"(?<![\w.\-])" + re.escape(Path(rel).name) + r"(?![\w\-])")
                                         for rel in candidates}
    referenced: set[str] = set()
    for path in files:
        relative = _rel(repo, path)
        if SOURCE_TEST.search(relative) or scan_rules.DOC_FILE.search(relative) or relative.startswith(WORKING_PREFIX + "evidence/"):
            continue
        text = scan_rules.read_text(path)
        if not text:
            continue
        if LOADER_FILES.search(relative):
            loader = DYNAMIC_LOADER.search(text)
            unclear = f"{loader.group(0)}" if loader else _property_source_unclear(text)
            if unclear:
                return set(), [f"{relative}: {unclear} loads property files the gate cannot name, so every config-format "
                               "file under src/main/resources is read as an override"]
        for rel, pattern in named.items():
            if rel != relative and rel not in referenced and Path(rel).name in text and pattern.search(text):
                referenced.add(rel)
    left_out = set(candidates) - referenced
    notes = [f"not read: {rel} (nothing loads it: no import, spring.config.*, @PropertySource, mount or copy names it; "
             "Spring does not read it)" for rel in sorted(left_out)]
    notes += [f"read as an override: {rel} (another file names it, so something may load it)" for rel in sorted(referenced)]
    return left_out, notes


def deployment_pairs(repo: Path, manifest: dict[str, Any], names: set[str], skip: set[str],
                     prefixes: tuple[str, ...] = (), problems: list[str] | None = None) -> list[tuple[str, str, str]]:
    """(name, value, file:line) for every assignment in the tree to a name the
    caller asks about: Kubernetes env entries (parsed as YAML, any layout),
    maps and nested config in YAML and JSON, NAME=value, -Dname= and --name=
    arguments, both forms of Dockerfile ENV, spring.application.json given as an
    argument (-D or --, any quoting). `names` holds canonical forms (see
    tlslib.canonical) and exact names. Documentation, comments, test sources
    and the config files themselves (`skip`) are left out; deployment
    descriptors and start scripts never are, wherever they are kept.
    A YAML or JSON file that holds a name asked about but does not parse is
    recorded in `problems` (and listed as blocking in E15): never read as
    text alone, with or without PyYAML."""
    local = manifest.get("environment") == "local"
    wanted_canon = {n for n in names if n == tlslib.canonical(n)}

    def wanted(name: str) -> str | None:
        """The name to record when it is one the caller asked about: itself, or the
        tail of a dotted path (data.SERVER_SSL_ENABLED, config.server.ssl.enabled).
        management.server.ssl.* is another setting, not server.ssl.*."""
        name = str(name)

        def asked(text: str) -> bool:
            canon = tlslib.canonical(text)
            return text in names or canon in wanted_canon or canon.startswith(prefixes) if prefixes else (
                text in names or canon in wanted_canon)

        if asked(name):
            return name
        segments = name.split(".")
        for index in range(1, len(segments)):
            tail = ".".join(segments[index:])
            if asked(tail) and segments[index - 1].lower() != "management":
                return tail
        return None

    found: list[tuple[str, str, str]] = []
    for path in scan_rules.iter_files(repo):
        relative = _rel(repo, path)
        if relative in skip or SOURCE_TEST.search(relative) or scan_rules.DOC_FILE.search(relative):
            continue
        if tlslib.CONFIG_NAME.match(path.name) and "src/main/resources" in relative:
            continue      # another service's own Spring config: its settings are its own, not an override of this one
        if not local and any(p.search(relative) for p in scan_rules.LOCAL_ALLOWED):
            continue
        text = scan_rules.read_text(path)
        if not text:
            continue
        squashed = scan_rules.squashed_text(path)
        if not any(n in squashed for n in wanted_canon | set(prefixes)) and not any(n in text for n in names):
            continue
        if path.suffix.lower() == ".properties":
            text = scan_rules.join_continuations(text)
        spans = scan_rules.comment_spans(text, path.name)

        def add(name: str, value: Any, position: int) -> None:
            if position >= 0 and scan_rules.in_comment(spans, position):
                return
            line = text.count("\n", 0, max(position, 0)) + 1
            if isinstance(value, bool):
                value = str(value).lower()
            found.append((str(name), UNREADABLE if value is None else str(value).strip(), f"{relative}:{line}"))

        parsed = None
        if path.suffix.lower() in (".yml", ".yaml", ".json"):
            parsed = _yaml_documents(text)
            if parsed is None:
                reason = ("holds a setting the gate reads but does not parse as YAML"
                          + ("" if tlslib._pyyaml is not None else " without PyYAML") + ": what it sets is not known")  # noqa: SLF001
                scan_rules.note_skip(relative, reason, blocking=True)
                if problems is not None:
                    problems.append(f"{relative} {reason}")
            for document in parsed or []:
                for node_path, node in _walk(document):
                    if isinstance(node, dict) and isinstance(node.get("name"), str) and ("value" in node or "valueFrom" in node) \
                            and wanted(node["name"]):
                        add(node["name"], node.get("value") if "value" in node else None, text.find(node["name"]))
                    elif node_path and not isinstance(node, (dict, list)) and wanted(node_path):
                        add(wanted(node_path), "" if node is None else node, text.find(node_path.rsplit(".", 1)[-1]))
                    elif node_path and isinstance(node, list) and node and all(not isinstance(v, (dict, list)) for v in node) \
                            and wanted(node_path):
                        add(wanted(node_path), ",".join(str(v) for v in node), text.find(node_path.rsplit(".", 1)[-1]))
        # The text forms. Where the file parsed as YAML, its env entries and maps are
        # already read above; an empty or JSON value is left to that reading.
        for match in PAIR.finditer(text):
            name = wanted(match.group(1))
            if not name or name == "SPRING_APPLICATION_JSON" or tlslib.canonical(name) == JSON_CANON:
                continue
            if parsed is not None and not match.group(2):
                continue
            add(name, match.group(2), match.start())
        if parsed is None:
            for match in K8S_ENV.finditer(text):
                name, value = (match.group(1), match.group(2)) if match.group(1) else (match.group(4), match.group(3))
                if wanted(name) and name != "SPRING_APPLICATION_JSON":
                    add(name, value, match.start())
            for match in FLOW_ENV.finditer(text):
                if wanted(match.group(1)) and match.group(1) != "SPRING_APPLICATION_JSON":
                    add(match.group(1), match.group(2), match.start())
        for match in DOCKER_ENV.finditer(text):
            if wanted(match.group(1)):
                add(match.group(1), match.group(2), match.start())
        if "SPRING_APPLICATION_JSON" in names and parsed is None:
            for match in JSON_ENV.finditer(text):
                add("SPRING_APPLICATION_JSON", json_after(match.group("json"), 0) or match.group("json"), match.start())
        if JSON_CANON in names:
            # -Dspring.application.json=... and --spring.application.json=... in a start
            # script, a Dockerfile ENTRYPOINT or CMD, an args list or JAVA_OPTS.
            for match in APP_JSON_ARG.finditer(text):
                value = json_after(text, match.end())
                add("spring.application.json", value if value is not None else None, match.start())
    # The same assignment is often seen twice (parsed and as text): keep one.
    unique: dict[tuple[str, str, str], tuple[str, str, str]] = {}
    for name, value, where in found:
        if tlslib.canonical(name) in (JSON_CANON, tlslib.canonical("SPRING_APPLICATION_JSON")) and value != UNREADABLE:
            value = json_after(value.strip("\"' "), 0) or value
        unique.setdefault((tlslib.canonical(name), value.strip("\"' "), where.rsplit(":", 1)[0]), (name, value.strip("\"' "), where))
    return list(unique.values())


def _unresolved(value: str) -> bool:
    return value == UNREADABLE or bool(re.search(r"\$\{|\$\(|\{\{|\$[A-Za-z_]", value))


GROUP_KEY = re.compile(r"(?i)^spring\.profiles\.group\.([^\[\]]+?)(?:\[\d+\])?$")


def _resources_module(repo: Path, item: Any) -> Path | None:
    """The module folder of a file under src/main/resources, or None."""
    parts = Path(str(item)).parts
    for index in range(len(parts) - 2):
        if parts[index:index + 3] == ("src", "main", "resources"):
            return _p(repo, Path(*parts[:index]) if index else ".").resolve()
    return None


class ProducerConfig:
    """Everything that can set one of the producer's stage keys, read once.

    Each source carries what Spring orders it by: its group (0 inside the jar,
    1 outside it, 2 a file a deployment imports or adds with
    spring.config.import / additional-location), whether it is a profile file,
    its place in the group, .properties over .yml, and for an import the source
    that imports it (an import ranks right above its importer). The order of
    profile files follows the order the profiles were activated in (the last
    wins); where that order is not known, every value an active profile file
    sets is judged (resolve_all)."""

    def __init__(self, repo: Path, manifest: dict[str, Any], listed: list[str] | None = None):
        """listed: another service's config files (a consumer module); by default
        the producer's, from the manifest."""
        self.repo, self.manifest = repo, manifest
        producer = _producer(manifest) if listed is None else {}
        self.listed = [str(item) for item in (_list(producer.get("config_files")) if listed is None else listed)]
        for item in self.listed:
            if not _p(repo, item).is_file():
                raise ValueError(f"config file {item} listed but missing, or not a regular file")
        self.unreadable: list[str] = []
        self.notes: list[str] = []          # what was read differently than it looks, for the evidence
        self.sources: list[dict[str, Any]] = []
        for entry in tlslib.spring_config_files(repo, self.listed):
            self._add_source(entry["path"], entry["name"], entry["profile"], entry["group"], entry["rank"], entry["props"])
        self._add_library_sources()
        # Files pulled in by spring.config.import inside the config files, and inside those.
        self._follow_imports(list(self.sources))
        # Names of placeholders on stage keys: their assignments are looked for too,
        # under the name as written and in the canonical form Spring also resolves
        # (${inventory.client-auth} from INVENTORY_CLIENT_AUTH or INVENTORY_CLIENTAUTH).
        self.placeholder_names = set()
        for source in self.sources:
            for _, layer in source["documents"]:
                for key, value in layer.items():
                    if tlslib.canonical(key) in STAGE_CANON:
                        for match in placeholders(str(value)):
                            self.placeholder_names |= {match.group(1).strip(), tlslib.canonical(match.group(1))}
        names = set(STAGE_CANON) | IMPORT_CANON | PROFILE_CANON | {NAME_CANON, JSON_CANON, "SPRING_APPLICATION_JSON"} \
            | self.placeholder_names
        skip = {source["name"] for source in self.sources}
        unloaded, unloaded_notes = unloaded_resource_configs(repo, skip)
        self.notes += unloaded_notes
        self.pairs = deployment_pairs(repo, manifest, names, skip | unloaded, TLS_PREFIXES, problems=self.unreadable)
        deployment_settings = []
        for name, value, where in self.pairs:
            if tlslib.canonical(name) in (JSON_CANON, tlslib.canonical("SPRING_APPLICATION_JSON")):
                deployment_settings += [(key, inner, where) for key, inner in (_flatten_json(value) or {}).items()]
            else:
                deployment_settings.append((name, value, where))
        before = len(self.sources)
        for name, value, where in deployment_settings:
            canon = tlslib.canonical(name)
            if canon == NAME_CANON and [n for n in _split_locations(value) if n != "application"]:
                self.unreadable.append(f"{where}: spring.config.name={value} replaces the names Spring reads (application.*); "
                                       "the files then in force are not resolved by this gate")
            if canon not in IMPORT_CANON:
                continue
            if _unresolved(value):
                self.unreadable.append(f"{where}: {name} is filled in at run time")
                continue
            if canon == LOCATION_CANON:
                self.unreadable.append(f"{where}: spring.config.location={value} replaces the files Spring reads by default; "
                                       "the files then in force are not resolved by this gate")
            self._import(value, None, None, where)
        self._follow_imports(self.sources[before:])
        # spring.config.name or location inside a config file: Spring reads them from the environment only.
        for source in self.sources:
            for _, layer in source["documents"]:
                for key, value in layer.items():
                    if tlslib.canonical(key) == NAME_CANON and binds_in_file(key):
                        self.unreadable.append(f"{source['name']}: sets spring.config.name={value}; which files are then read "
                                               "is not resolved by this gate")
        self._activation(producer)

    def _activation(self, producer: dict[str, Any]) -> None:
        """The profiles the service runs with and their order, by Spring Boot 3.4's
        rule (checked on the reference pair): spring.profiles.active is one
        setting, so the source that ranks highest gives the whole list (the
        manifest's profiles, which a deployment gives as SPRING_PROFILES_ACTIVE
        or --spring.profiles.active, replace the config files' list; between
        files, application.properties over application.yml); the profiles of
        spring.profiles.include come before the active ones; each group's members
        right after the group. Where the order cannot be told (an include set in
        two places, or by a deployment; an activation in a profile file or an
        import), every value an active profile file sets is judged."""
        manifest_order = list(dict.fromkeys(str(p) for p in _list(producer.get("profiles"))))
        # spring.profiles.group.<name>: activating the name activates its members, recursively.
        self.groups: dict[str, list[str]] = {}
        includes: list[str] = []
        include_lists = 0
        actives: list[tuple[str, list[str]]] = []      # (where, list), lowest precedence first
        unclear: list[str] = []
        for source in sorted(self.sources, key=lambda s: self._rank_key(s, [])):
            for guard, layer in source["documents"]:
                for key, value in layer.items():
                    group = GROUP_KEY.match(key)
                    if group and not _unresolved(str(value)):
                        members = self.groups.setdefault(group.group(1), [])
                        members += [m for m in _split_locations(value) if m not in members]
                if guard is not None:
                    continue
                for key, value in layer.items():
                    canon = tlslib.canonical(key)
                    if canon not in PROFILE_CANON or _unresolved(str(value)) or not binds_in_file(key):
                        continue
                    listed = _split_locations(value)
                    if source["profile"] or source.get("parent") is not None or source["group"] == 2:
                        unclear.append(f"{source['name']} sets {key}")
                    if canon == INCLUDE_CANON:
                        include_lists += 1
                        includes += [p for p in listed if p not in includes]
                    else:
                        actives.append((source["name"], listed))
        # Included profiles always come before the active ones (checked: SPRING_PROFILES_INCLUDE=zeta with include: beta
        # and active: alpha runs zeta, beta, alpha). Set in more than one place, their order among themselves is not known:
        # each order is judged.
        include_places = include_lists
        for name, value, where in self.pairs:
            if tlslib.canonical(name) == INCLUDE_CANON and not _unresolved(value):
                include_places += 1
                includes += [p for p in _split_locations(value) if p not in includes]
        if manifest_order:
            active = manifest_order
            replaced = [where for where, listed in actives if set(listed) - set(manifest_order)]
            if replaced:
                self.notes.append(f"spring.profiles.active in {', '.join(dict.fromkeys(replaced))} is replaced by the manifest's "
                                  f"profiles {manifest_order} (a deployment's spring.profiles.active wins over the files'); a "
                                  "profile only that list names is judged as one a deployment may activate")
        else:
            active = actives[-1][1] if actives else []
        self.include_orders: list[list[str]] | None = None
        if not unclear:
            if include_places <= 1:
                self.include_orders = [includes]
            elif len(includes) <= 5:
                self.include_orders = [list(order) for order in itertools.permutations(includes)]
            else:
                self.include_orders = [[p for p in includes if p != last] + [last] for last in includes]
            if include_places > 1:
                self.notes.append(f"spring.profiles.include is set in {include_places} places: the included profiles {includes} "
                                  "come before the active ones, in an order not known, so every order of them is judged")
        self.base_orders: list[list[str]] | None = None if unclear else [
            list(dict.fromkeys(order + active)) for order in self.include_orders or []]
        if self.base_orders:
            self.base_order: list[str] = self.base_orders[0]
        else:
            self.base_order = list(dict.fromkeys(manifest_order + [p for _, listed in actives for p in listed] + includes))
            self.notes.append("the profile activation order is not known (" + "; ".join(unclear[:2]) + "): every value an "
                              "active profile file sets is judged")
        self.base_profiles = set(self.base_order)

    def expand(self, profiles: Any) -> set[str]:
        """A profile set with every profile group it names expanded, recursively."""
        return set(self.expand_order(list(profiles)))

    def expand_order(self, order: list[str]) -> list[str]:
        """An activation list with each group's members right after the group, recursively
        (Spring Boot 3.4: "prod" with group prod: [eu] runs as prod, eu)."""
        found: list[str] = []

        def visit(name: str) -> None:
            if name in found:
                return
            found.append(name)
            for member in self.groups.get(name, []):
                visit(member)
        for name in order:
            visit(name)
        return found

    def _add_library_sources(self) -> None:
        """Spring config files of the modules the service's build file depends on
        (a shared library module in the same repository). Spring reads
        classpath:/application.yml and classpath:/config/application.yml from
        whichever jar on the classpath has them, so a library's file is in force
        unless the service's own module has a file at the same place (that one
        comes first on the classpath; the library's is then read below it, so
        a setting only the library makes is still seen)."""
        modules = []
        for item in self.listed:
            module = _resources_module(self.repo, item)
            if module is not None and module not in modules:
                modules.append(module)
        for module in modules:
            libraries, unknown = module_dependencies(module, self.repo)
            self.unreadable += [f"{note}: its configuration cannot be read" for note in unknown]
            own = module / "src" / "main" / "resources"
            for library in libraries:
                resources = library / "src" / "main" / "resources"
                for sub, rank in (("", 0), ("config", 1)):
                    folder = resources / sub if sub else resources
                    if not folder.is_dir():
                        continue
                    for path in sorted(folder.iterdir()):
                        match = tlslib.CONFIG_NAME.match(path.name)
                        if not match or not path.is_file():
                            continue
                        shadowed = ((own / sub / path.name) if sub else (own / path.name)).is_file()
                        self._add_source(path, _rel(self.repo, path), match.group("profile"), 0,
                                         rank - 0.5 if shadowed else rank + 0.25, 1 if path.suffix == ".properties" else 0)

    def _add_source(self, path: Path, name: str, profile: str | None, group: int, rank: float, props: int,
                    parent: dict[str, Any] | None = None, index: tuple = (), guard: Any = None) -> dict[str, Any] | None:
        if any(source["path"].resolve() == path.resolve() for source in self.sources):
            return None
        try:
            documents = flatten_config(path)
        except Exception as problem:  # noqa: BLE001 - YAML errors differ by parser
            if name in self.listed:
                raise ValueError(f"{name}: {type(problem).__name__}: {str(problem).splitlines()[0][:120]}") from problem
            self.unreadable.append(f"{name} could not be read as Spring config ({type(problem).__name__})")
            return None
        source = {"path": path, "name": name, "profile": profile, "group": group, "rank": rank, "props": props,
                  "parent": parent, "index": index, "guard": guard, "documents": documents}
        self.sources.append(source)
        return source

    def _follow_imports(self, pending: list[dict[str, Any]]) -> None:
        """spring.config.import inside config files, followed into the files they
        import, however deep. spring.config.location and additional-location
        written in a file have no effect in Spring: not a source, and said so."""
        while pending:
            source = pending.pop(0)
            before = len(self.sources)
            for guard, layer in source["documents"]:
                for key, value in layer.items():
                    canon = tlslib.canonical(key)
                    if canon not in IMPORT_CANON or not binds_in_file(key):
                        continue
                    if canon == FILE_IMPORT_CANON:
                        self._import(value, source, guard)
                    else:
                        written = "spring.config.location" if canon == LOCATION_CANON else "spring.config.additional-location"
                        self.notes.append(f"{source['name']}: {key}={value} is ignored, not a source: Spring takes "
                                          f"{written} from the environment, system properties and the command line "
                                          "only, never from a config file")
            pending += self.sources[before:]

    def _import(self, value: Any, importer: dict[str, Any] | None, guard: Any, where: str = "") -> None:
        for number, location in enumerate(_split_locations(value)):
            files, problem = _import_targets(self.repo, location, importer["path"] if importer else None)
            if problem:
                label = where or (importer["name"] if importer else "config")
                self.unreadable.append(f"{label}: imports {problem}")
            folder = _folder_import(location)
            for path in files:
                match = tlslib.CONFIG_NAME.match(path.name)
                profile = match.group("profile") if match and folder else None
                props = 1 if path.suffix == ".properties" else 0
                # The import ranks right above its importer; later imports above earlier ones;
                # in a folder, profile files above plain ones, .properties above .yml.
                index = (number, 1 if profile else 0, profile or "", props, path.name)
                if importer is None:
                    self._add_source(path, _rel(self.repo, path), profile, 2, number, props, index=index)
                else:
                    self._add_source(path, _rel(self.repo, path), profile, importer["group"], importer["rank"], props,
                                     parent=importer, index=index, guard=guard)

    def _rank_key(self, source: dict[str, Any], order: list[str]) -> tuple:
        """Where a source stands in Spring's order for this activation list (lowest first)."""
        parent = source.get("parent")
        if parent is not None:
            profile = source["profile"]
            number, flag, _, props, name = source["index"]
            position = (order.index(profile) if profile in order else len(order)) if profile else 0
            return self._rank_key(parent, order) + (number, flag, position, props, name)
        profile = source["profile"]
        position = (order.index(profile) if profile in order else len(order)) if profile else 0
        return (source["group"], 1 if profile else 0, position, source["rank"], source["props"], source["name"]) \
            + ((source["index"][0],) if source["index"] else ())

    def _active(self, source: dict[str, Any], profiles: set[str]) -> bool:
        if source["profile"] and source["profile"] not in profiles:
            return False
        if source.get("guard") and not profile_active(source["guard"], profiles):
            return False
        return source.get("parent") is None or self._active(source["parent"], profiles)

    def names(self) -> list[str]:
        """Every file whose content can change the producer's behaviour."""
        return list(dict.fromkeys([source["name"] for source in self.sources]
                                  + [where.rsplit(":", 1)[0] for name, _, where in self.pairs
                                     if not tlslib.canonical(name).startswith(TLS_PREFIXES)]))

    def scenarios(self) -> list[tuple[str, set[str], list[str] | None]]:
        """The profile sets the service may run with: the manifest's, each one a
        deployment file activates, and each profile that guards a stage key.
        Each with its activation order, or None where the order is not known."""
        local = self.manifest.get("environment") == "local"
        base = self.base_order
        label = "the profiles the manifest and the config activate "
        found: list[tuple[str, set[str], list[str] | None]] = [
            (label + (str(order) if order else "(none)") + (" (one order of the included profiles)" if len(self.base_orders) > 1 else ""),
             set(order), order) for order in self.base_orders] if self.base_orders else [
            (label + (str(base) if base else "(none)"), set(base), None)]
        for name, value, where in self.pairs:
            if tlslib.canonical(name) in PROFILE_CANON and not _unresolved(value):
                listed = _split_locations(value)
                if self.include_orders is not None and tlslib.canonical(name) == INCLUDE_CANON:
                    continue      # a deployment's include is among the included profiles above, in every order
                if self.include_orders is not None:
                    # A deployment's spring.profiles.active replaces the files' list; the included profiles come first.
                    for includes in self.include_orders:
                        order = list(dict.fromkeys(includes + listed))
                        found.append((f"profiles {value} set at {where} (in Spring's order {order})", set(order), order))
                else:
                    found.append((f"profiles {value} set at {where}", self.base_profiles | set(listed), None if base else listed))
        guarding: set[str] = set()
        for source in self.sources:
            for guard, layer in source["documents"]:
                if any(tlslib.canonical(key) in STAGE_CANON for key in layer):
                    guarding |= _expression_profiles(guard) if guard else set()
                    # An imported file is in force under its importer's profile and document guard.
                    current: dict[str, Any] | None = source
                    while current is not None:
                        if current["profile"]:
                            guarding.add(current["profile"])
                        if current.get("guard"):
                            guarding |= _expression_profiles(current["guard"])
                        current = current.get("parent")
        if not local:
            guarding.discard("local")         # application-local.* is a laptop-only file by this toolkit's convention
        # A group's members are as active as the group, and in a known place: not a profile to try on its own.
        known = self.expand(self.base_profiles)
        for profile in sorted(guarding - known):
            found.append((f"profile {profile} (it guards a stage setting; nothing says it is never active)",
                          self.base_profiles | {profile}, None if base else [profile]))
        # A document guarded "a & b" is in force when both are active (a profile group, two
        # deployments' settings together): every guarding profile is also tried at once.
        if len(guarding - known) > 1:
            found.append((f"profiles {sorted(guarding - known)} together (each guards a stage setting)",
                          self.base_profiles | guarding, None))
        # One scenario per profile set, the first found; several only for the orders of the included profiles.
        unique: dict[frozenset, list[tuple[str, set[str], list[str] | None]]] = {}
        for text, profiles, order in found:
            entries = unique.setdefault(frozenset(profiles), [])
            if not entries or (order is not None and all(seen is not None and seen != order for _, _, seen in entries)):
                entries.append((text, set(profiles), order))
        return [entry for entries in unique.values() for entry in entries]

    def _descends(self, source: dict[str, Any], ancestor: dict[str, Any] | None) -> bool:
        while source is not None:
            if source is ancestor:
                return True
            source = source.get("parent")
        return False

    def resolve(self, profiles: Any, order: list[str] | None = None, last: dict[str, Any] | None = None,
                expanded: bool = False) -> Settings:
        """The settings in force for a profile set, Spring's precedence applied:
        inside the jar, then outside it, plain files before profile files, each
        import right above its importer, profile files in activation order (the
        last wins); later documents win; inactive documents are left out. A key
        Spring does not bind in a file (SERVER_SSL_CLIENTAUTH written in
        application.properties) is left out and listed in settings.ignored."""
        # expanded: the order is final, groups already expanded (a group's member may then come after other profiles).
        order_list = list(dict.fromkeys(order)) if expanded and order is not None else \
            self.expand_order(list(order) if order is not None else sorted(profiles))
        active_profiles = set(order_list) | self.expand(set(profiles))
        order_list += sorted(active_profiles - set(order_list))
        settings = Settings()
        active = [source for source in self.sources if self._active(source, active_profiles)]
        for source in sorted(active, key=lambda s: ((1,) if self._descends(s, last) else (0,)) + self._rank_key(s, order_list)):
            for guard, layer in source["documents"]:
                if guard and not profile_active(guard, active_profiles):
                    continue
                for key, value in layer.items():
                    if not binds_in_file(key):
                        if tlslib.canonical(key) in STAGE_CANON or tlslib.canonical(key).startswith(TLS_PREFIXES):
                            settings.ignored.append(f"{source['name']}: {key} is an environment-variable spelling inside a file; "
                                                    "Spring does not bind it there, so it is not counted")
                        continue
                    settings.put(key, value, source["name"])
        return settings

    def resolve_all(self, profiles: Any, order: list[str] | None = None) -> list[tuple[Settings, str]]:
        """Every configuration Spring may run with for this profile set: one when the
        activation order is known; otherwise one per profile that has a profile
        file, with that profile applied last, so the value each profile file
        sets is judged (never only the one that happens to sort last)."""
        primary = self.resolve(profiles, order)
        found, seen = [(primary, "")], {tuple(sorted(primary.canon.items()))}

        def keep(variant: Settings, why: str) -> None:
            signature = tuple(sorted(variant.canon.items()))
            if signature not in seen:
                seen.add(signature)
                found.append((variant, why))
        expanded = self.expand(set(profiles))
        # Files deployments import (group 2) come from different deployment files: any one may be the one in force.
        for source in self.sources:
            if source["group"] == 2 and source.get("parent") is None and self._active(source, expanded):
                keep(self.resolve(profiles, order, last=source), f"with {source['name']} as the import in force")
        if order is not None and set(self.expand_order(list(order))) >= expanded:
            return found
        with_files = sorted({source["profile"] for source in self.sources if source["profile"] in expanded})
        if len(with_files) < 2:
            return found
        default = sorted(expanded) if order is None else self.expand_order(list(order))
        for profile in with_files:
            # Last after expansion too: a group's member is not kept right behind its group here.
            keep(self.resolve(profiles, [p for p in self.expand_order(default) if p != profile] + [profile], expanded=True),
                 f"if profile {profile} is applied last (the activation order is not known)")
        return found


_CONFIG_CACHE: dict[str, ProducerConfig] = {}


def reset_caches() -> None:
    """Forget everything read so far: the next scan sees the tree as it is now."""
    scan_rules.reset_skipped()
    _CONFIG_CACHE.clear()
    _CONSUMER_CACHE.clear()
    _MODULE_INDEX.clear()


def producer_config(repo: Path, manifest: dict[str, Any]) -> ProducerConfig:
    """Read once per run: several checks need it."""
    key = str(repo) + json.dumps(manifest, sort_keys=True, default=str)
    if key not in _CONFIG_CACHE:
        _CONFIG_CACHE[key] = ProducerConfig(repo, manifest)
    return _CONFIG_CACHE[key]


def config_source_names(repo: Path, manifest: dict[str, Any]) -> list[str]:
    """For probe_tls.bound_inputs: the files recorded probes are bound to."""
    if manifest.get("role") == "consumer" or not _list(_producer(manifest).get("config_files")):
        return []
    return ProducerConfig(repo, manifest).names()


def producer_code_names(repo: Path, manifest: dict[str, Any]) -> list[str]:
    """For probe_tls.bound_inputs: the producer module's code (every file under
    src/main) and build files, and those of the modules it depends on in this
    repository. A probe describes the build it ran against."""
    if manifest.get("role") == "consumer":
        return []
    names: list[str] = []
    for item in _list(_producer(manifest).get("config_files")):
        module = _resources_module(repo, item)
        if module is None:
            continue
        for folder in [module] + module_dependencies(module, repo)[0]:
            names += [_rel(repo, path) for path in _build_files(folder, repo)]
            main = folder / "src" / "main"
            if main.is_dir():
                names += sorted(_rel(repo, path) for path in main.rglob("*")
                                if path.is_file() and not any(part.startswith(".") for part in path.relative_to(main).parts))
    return list(dict.fromkeys(names))


def producer_settings(repo: Path, manifest: dict[str, Any]) -> tuple[Settings, list[str]]:
    """The producer's settings under the manifest's profiles, and the files read."""
    config = producer_config(repo, manifest)
    settings = config.resolve(config.base_profiles, config.base_order if config.base_orders else None)
    for key in list(settings):
        match = PLACEHOLDER.fullmatch(str(settings[key]).strip())
        if match and match.group(2) is not None:
            settings.put(key, match.group(2), settings.origin.get(tlslib.canonical(key), ""))
    return settings, [source["name"] for source in config.sources]


# ---------------------------------------------------------------- where each service takes its key and its trust from

def _location(value: Any) -> str:
    """A configured file location as a plain path: ${VAR:default} reads as its
    default, and the file:, classpath: and optional: prefixes are dropped."""
    text = replace_placeholders(str(value or "").strip(), lambda m: m.group(2) if m.group(2) is not None else m.group(0))
    return re.sub(r"^(?:optional:)?(?:file:|classpath:)?", "", text)


def tls_bundles(settings: Settings) -> dict[str, dict[str, Any]]:
    """The SSL bundles a configuration defines, by canonical name: the trust-store
    location, and whether the bundle has a key store (PEM: certificate and
    private key; JKS/PKCS12: a location)."""
    bundles: dict[str, dict[str, Any]] = {}
    for key, value in settings.items():
        match = BUNDLE_KEY.match(tlslib.canonical(key))
        if not match or not str(value).strip():
            continue
        kind, name, store, attribute = match.groups()
        bundle = bundles.setdefault(name, {"kind": kind, "truststore": "", "key_parts": set(), "written": key.split(".")[-3] if key.count(".") >= 3 else name})
        if store == "truststore" and attribute in ("certificate", "location"):
            bundle["truststore"] = _location(value)
        elif store == "keystore":
            bundle["key_parts"].add(attribute)
    for bundle in bundles.values():
        parts = bundle["key_parts"]
        bundle["has_key_store"] = {"certificate", "privatekey"} <= parts if bundle["kind"] == "pem" else "location" in parts
    return bundles


def tls_scenarios(config: ProducerConfig) -> list[tuple[str, set[str], list[str] | None]]:
    """The profile sets a service's key and trust settings are read under: the
    stage scenarios, and every profile the module's config names. The local
    profile is a laptop-only file, so it is read in a local run only."""
    local = config.manifest.get("environment") == "local"
    found = list(config.scenarios())
    seen = {frozenset(profiles) for _, profiles, _ in found}
    named: set[str] = set()
    for source in config.sources:
        if source["profile"]:
            named.add(source["profile"])
        for guard, _ in source["documents"]:
            named |= _expression_profiles(guard) if guard else set()
    for profile in sorted(named):
        profiles = config.base_profiles | {profile}
        if (profile == "local" and not local) or frozenset(profiles) in seen:
            continue
        seen.add(frozenset(profiles))
        found.append((f"profile {profile}", profiles, None if config.base_profiles else [profile]))
    return found


def _tls_overrides(config: ProducerConfig) -> list[tuple[str, str, str]]:
    """Deployment-time settings of a bundle's key or trust (environment variables,
    arguments), outside the run's own records and the kits."""
    return [(name, value, where) for name, value, where in config.pairs
            if tlslib.canonical(name).startswith(TLS_PREFIXES) and not where.startswith(WORKING_PREFIX) and not _unresolved(value)]


WORKING_PREFIX = "tls-migration/"
_CONSUMER_CACHE: dict[str, list[tuple[str, ProducerConfig]]] = {}


def _producer_modules(manifest: dict[str, Any]) -> set[str]:
    """The repository-relative module folders of the producer's config files."""
    marker = ("src", "main", "resources")
    modules = set()
    for item in _list(_producer(manifest).get("config_files")):
        parts = Path(str(item)).parts
        for index in range(len(parts) - 2):
            if parts[index:index + 3] == marker:
                modules.add("/".join(parts[:index]))
    return modules


def client_scope(repo: Path, manifest: dict[str, Any], module: str) -> Scope:  # noqa: ARG001 - same shape as the other scope helpers
    """The hosts a module's client calls count for. For the producer's own module
    (a service that is both), the producer's own names are not a call to a
    producer: every other in-scope host is (W5, Q-13)."""
    scope = Scope(manifest)
    if (module if module != "." else "") not in _producer_modules(manifest):
        return scope
    own = _own_names(manifest)
    return Scope({"in_scope_hosts": sorted(h for h in scope.hosts if not own.covers(h))})


def consumer_configs(repo: Path, manifest: dict[str, Any]) -> list[tuple[str, ProducerConfig]]:
    """(module, its configuration) for every Spring module in the repository that
    calls an in-scope host: the services that call a producer. The producer's own
    module is one of them when it calls another in-scope host (role both): its
    outbound client is checked like any consumer's."""
    key = str(repo) + json.dumps(manifest, sort_keys=True, default=str)
    if key in _CONSUMER_CACHE:
        return _CONSUMER_CACHE[key]
    if manifest.get("role") not in ("consumer", "both"):
        return []
    marker = ("src", "main", "resources")
    modules: dict[str, list[str]] = {}
    for path in scan_rules.iter_files(repo):
        if not tlslib.CONFIG_NAME.match(path.name):
            continue
        parts = Path(_rel(repo, path)).parts
        for index in range(len(parts) - 2):
            if parts[index:index + 3] == marker:
                module = "/".join(parts[:index])
                modules.setdefault(module, []).append("/".join(parts))
                break
    found = []
    for module, files in sorted(modules.items()):
        plain = sorted(f for f in files if "-" not in Path(f).name) or sorted(files)
        scope = client_scope(repo, manifest, module or ".")
        if not scope.hosts or not _may_call_in_scope(repo, module, files, scope):
            continue          # read only what can matter: a module that names no in-scope host is not a consumer
        try:
            found.append((module or ".", ProducerConfig(repo, manifest, listed=plain[:1])))
        except ValueError:
            continue
    _CONSUMER_CACHE[key] = found
    return found


def _may_call_in_scope(repo: Path, module: str, files: list[str], scope: Scope) -> bool:
    """Whether a module's own config files, or those of the modules it depends
    on, name an in-scope host over https or import other config: a quick look
    before its configuration is read in full."""
    paths = [repo / f for f in files]
    try:
        libraries, _ = module_dependencies(_p(repo, module or "."), repo)
    except Exception:  # noqa: BLE001 - when in doubt, read the module in full
        return True
    for library in libraries:
        for folder in (library / "src/main/resources", library / "src/main/resources/config"):
            if folder.is_dir():
                paths += [p for p in folder.iterdir() if tlslib.CONFIG_NAME.match(p.name)]
    for path in paths:
        text = scan_rules.read_text(path) or ""
        squashed = scan_rules.squashed_text(path)
        if any(name in squashed for name in IMPORT_CANON):
            return True
        if any(scope.covers(match.group("host").lower().rstrip(".")) for match in scan_rules.HTTPS_URL.finditer(text)):
            return True
    return False


def _calls_in_scope(config: ProducerConfig, scope: Scope) -> bool:
    for source in config.sources:
        for _, layer in source["documents"]:
            for value in layer.values():
                for match in scan_rules.HTTPS_URL.finditer(str(value)):
                    if scope.covers(match.group("host").lower().rstrip(".")):
                        return True
    return False


def consumer_client_problems(repo: Path, manifest: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    """The consumer counterpart of the producer's stage check: every service that
    calls an in-scope host must build its client from an SSL bundle with a key
    store under every profile set a deployment may run with, or it cannot
    present its client certificate. (problems, not provable, evidence)."""
    problems, unproven, evidence = [], [], []
    for module, config in consumer_configs(repo, manifest):
        if not _calls_in_scope(config, client_scope(repo, manifest, module)):
            continue
        unproven += [f"{module}: {note}" for note in config.unreadable]
        checked = 0
        cases = [(label + (f"; {why}" if why else ""), settings) for label, profiles, order in tls_scenarios(config)
                 for settings, why in config.resolve_all(profiles, order)]
        for label, settings in cases:
            server_bundle = tlslib.canonical(settings.find("server.ssl.bundle"))
            clients = {name: bundle for name, bundle in tls_bundles(settings).items() if name != server_bundle}
            checked += 1
            if not clients:
                unproven.append(f"{module}: no client SSL bundle in its configuration ({label}); how its client presents a certificate cannot be read")
            elif not any(bundle["has_key_store"] for bundle in clients.values()):
                problems.append(f"{module}: the client SSL bundle {sorted(b['written'] for b in clients.values())} has no key store "
                                f"({label}): the service cannot present its client certificate to the producer")
        evidence.append(f"{module}: client key store checked under {checked} profile set(s); read: "
                        + ", ".join(source["name"] for source in config.sources))
    # W5: a caller in another stack is read by no rule here: never a pass, never a fail.
    for folder, stack in sorted(other_stack_callers(repo, manifest).items()):
        unproven.append(f"{_rel(repo, folder)}: stack not read ({stack}): it calls an in-scope host and E12 reads Spring Boot "
                        f"only; check its client certificate and trust by hand (references/{STACK_PAGES.get(stack, 'java-spring.md')})")
    return list(dict.fromkeys(problems)), list(dict.fromkeys(unproven)), evidence


def _store_problem(repo: Path, location: str, mine: dict[str, set[str]], other: dict[str, set[str]]) -> str | None:
    """Why a configured trust store is not the planned one for its side, or None."""
    if not location:
        return "names no trust store, so the JVM's default store would be trusted where a private CA is planned"
    if SYSTEM_STORE.search(location):
        return f"trusts {location}, a system trust store, not the planned CA"
    base = location.rstrip("/").rsplit("/", 1)[-1]
    if base in other["names"] and base not in mine["names"]:
        return f"trusts {base}, which the certificate plan gives to the other side, not the planned store for this side"
    if "$" not in location and not os.path.isabs(location):
        for candidate in [repo / location] + [p / location for p in repo.glob("*/src/main/resources")]:
            if candidate.is_file():
                try:
                    prints = {tlslib.cert_info_from_pem(pem)["fingerprint_sha256"] for pem in tlslib.split_bundle(candidate)}
                except (OSError, ValueError):
                    return f"trusts {location}, which cannot be read as certificates"
                if mine["fingerprints"] and not prints <= mine["fingerprints"]:
                    return f"trusts {location}, which holds certificates other than the planned CA for this side"
                break
    return None


def configured_trust_problems(repo: Path, manifest: dict[str, Any], rerun: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Holds the trust store each service's configuration names, under every
    profile set and deployment override, against the certificate plan:
    the producer trusts its consumer CA, a consumer trusts the server CA."""
    plan = _cert_plan(repo, manifest)
    sides: dict[str, dict[str, set[str]]] = {"producer": {"names": set(), "fingerprints": set()},
                                             "consumer": {"names": {"ca-bundle.pem"}, "fingerprints": set()}}
    for entry in _list(plan.get("certificates")):
        if not isinstance(entry, dict) or not entry.get("issuer_ca"):
            continue
        side = "consumer" if entry.get("role") == "server" else "producer" if entry.get("role") == "client" else None
        if side:
            sides[side]["names"].add(str(entry["issuer_ca"]).rsplit("/", 1)[-1])
            try:
                sides[side]["fingerprints"] |= {tlslib.cert_info_from_pem(pem)["fingerprint_sha256"]
                                                for pem in tlslib.split_bundle(_p(repo, entry["issuer_ca"]))}
            except (OSError, ValueError):
                pass
    issuing = rerun.get("issuing_cas")
    if isinstance(issuing, dict):
        # The CAs that really issue the planned certificates (signature checked), never
        # every certificate an issuer file happens to hold.
        sides["producer"]["fingerprints"] = set(issuing.get("client") or [])
        sides["consumer"]["fingerprints"] = set(issuing.get("server") or [])
    for store in rerun.get("trust_stores", []):
        prints = set(store.get("fingerprints") or [])
        core = prints - set(store.get("previous_fingerprints") or [])
        for side, other in (("producer", "consumer"), ("consumer", "producer")):
            if core and (core <= sides[side]["fingerprints"] or (not sides[side]["fingerprints"] and not core & sides[other]["fingerprints"])):
                sides[side]["names"].add(str(store.get("path")).rsplit("/", 1)[-1])
                sides[side]["fingerprints"] |= prints
                break
    problems, evidence = [], []

    def look(config: ProducerConfig, who: str, side: str, pick) -> None:  # noqa: ANN001
        other = "consumer" if side == "producer" else "producer"
        cases = [(label + (f"; {why}" if why else ""), settings) for label, profiles, order in tls_scenarios(config)
                 for settings, why in config.resolve_all(profiles, order)]
        base = config.resolve(config.base_profiles, config.base_order if config.base_orders else None)
        cases += [(f"an override at {where} sets {name}", base.copy_with(name, value, where)) for name, value, where in _tls_overrides(config)]
        for label, settings in cases:
            for bundle_name, location in pick(settings):
                problem = _store_problem(repo, location, sides[side], sides[other])
                if problem:
                    problems.append(f"{who}{' bundle ' + bundle_name if bundle_name else ''} {problem}  [{label}]")
                else:
                    evidence.append(f"{who}{' bundle ' + bundle_name if bundle_name else ''} trusts {location}  [{label}]")

    def producer_trust(settings: Settings) -> list[tuple[str, str]]:
        if settings.find("server.ssl.client-auth").strip().lower() not in ("want", "need"):
            return []                                  # no client certificates asked for yet: nothing is trusted
        name = tlslib.canonical(settings.find("server.ssl.bundle"))
        bundle = tls_bundles(settings).get(name)
        if bundle:
            return [(bundle["written"], bundle["truststore"])]
        return [("", _location(settings.find("server.ssl.trust-store") or settings.find("server.ssl.trust-certificate")))]

    def consumer_trust(settings: Settings) -> list[tuple[str, str]]:
        server_bundle = tlslib.canonical(settings.find("server.ssl.bundle"))
        clients = {n: b for n, b in tls_bundles(settings).items() if n != server_bundle}
        with_key = {n: b for n, b in clients.items() if b["has_key_store"]}
        return [(b["written"], b["truststore"]) for b in (with_key or clients).values()]

    if manifest.get("role") in ("producer", "both") and _list(_producer(manifest).get("config_files")):
        try:
            look(producer_config(repo, manifest), "the producer's server", "producer", producer_trust)
        except ValueError:
            pass                                       # an unreadable producer config is E12's finding
    own_modules = _producer_modules(manifest)
    for module, config in consumer_configs(repo, manifest):
        # The producer's own outbound client trusts another producer's CA, which this
        # plan does not hold: E12 checks its key store; its trust is that producer's kit.
        if (module if module != "." else "") in own_modules:
            continue
        if _calls_in_scope(config, client_scope(repo, manifest, module)):
            look(config, f"{module}: the client", "consumer", consumer_trust)
    return list(dict.fromkeys(problems)), list(dict.fromkeys(evidence))


def _stage_problems(settings: Settings, stage: int) -> list[str]:
    problems = []
    client_auth = settings.find("server.ssl.client-auth").strip().lower()
    legacy = tlslib.spring_bool(settings.find("tls.migration.legacy-http.enabled"))
    enforce = tlslib.spring_bool(settings.find("tls.migration.allowlist.enforce"))
    has_tls = any(tlslib.canonical(k).startswith(("serversslbundle", "serversslkeystore", "serversslcertificate")) for k in settings)
    if tlslib.spring_bool(settings.find("server.ssl.enabled")) == "false":
        problems.append("server.ssl.enabled is false: the service would not speak TLS at all")
    if stage >= 2 and not has_tls:
        problems.append("no server TLS settings (server.ssl.bundle, key-store or certificate)")
    if stage >= 2 and client_auth in ("", "none"):
        problems.append(f"stage {stage} needs server.ssl.client-auth want (stages 2-4) or need (5-6); found '{client_auth or 'not set'}'")
    elif stage >= 5 and client_auth != "need":
        problems.append(f"stage {stage} needs server.ssl.client-auth: need; found '{client_auth}'")
    if 2 <= stage <= 4 and client_auth == "need":
        problems.append(f"stage {stage} but client-auth is already need; consumers without certificates break")
    if stage >= 6 and legacy != "false":
        # Whether a missing key keeps the connector off depends on code the gate does not
        # read (matchIfMissing): stage 6 needs it written as false.
        problems.append(f"stage 6 but tls.migration.legacy-http.enabled is '{legacy or 'not set'}'; stage 6 needs it set to false")
    if 2 <= stage <= 5 and legacy != "true":
        problems.append(f"stage {stage} but the plain-HTTP connector is not enabled (tls.migration.legacy-http.enabled); consumers on HTTP would break")
    if stage >= 4 and enforce != "true":
        problems.append(f"stage {stage} needs tls.migration.allowlist.enforce: true; found '{enforce or 'not set'}'")
    where, protocols, ciphers = protocols_in_force(settings)
    if re.search(r"(?i)TLSv1(\.[01])?(?![.\d])|SSLv3", protocols):
        problems.append(f"{where} allows an old protocol: {protocols}")
    weak = [c for c in re.split(r"[,\s]+", ciphers) if WEAK_CIPHER.search(c)]
    if weak:
        problems.append(f"the server's cipher list allows weak ciphers: {weak[:4]}")
    return problems


WEAK_CIPHER = re.compile(r"(?i)NULL|EXPORT|RC4|(?<![A-Z0-9])(?:3?DES)(?![A-Z0-9])|_DES_|MD5|anon|SSLv3")


def _server_bundle(settings: Settings) -> tuple[str, str] | None:
    """(kind, name) of the SSL bundle server.ssl.bundle names, as written in the config."""
    wanted = tlslib.canonical(settings.find("server.ssl.bundle"))
    if not wanted:
        return None
    for key in settings:
        match = re.match(r"^springsslbundle(pem|jks)(.+?)(keystore|truststore|options|reloadonupdate|key)", tlslib.canonical(key))
        if match and match.group(2) == wanted:
            return match.group(1), wanted
    return "pem", wanted


def protocols_in_force(settings: Settings) -> tuple[str, str, str]:
    """(where they come from, the server's enabled protocols, its ciphers). With
    server.ssl.bundle set, Spring uses the bundle's options and ignores
    server.ssl.enabled-protocols and server.ssl.ciphers, so only the bundle's
    count; "" when nothing sets them (the JVM's defaults, which P5 and P6 test)."""
    bundle = _server_bundle(settings)
    if bundle is None:
        return ("server.ssl.enabled-protocols", settings.find("server.ssl.enabled-protocols"), settings.find("server.ssl.ciphers"))
    kind, name = bundle
    values = {"protocols": "", "ciphers": ""}
    for key, value in settings.items():
        canon = tlslib.canonical(key)
        if canon == f"springsslbundle{kind}{name}optionsenabledprotocols":
            values["protocols"] = str(value)
        elif canon == f"springsslbundle{kind}{name}optionsciphers":
            values["ciphers"] = str(value)
    written = next((k.rsplit(".options.", 1)[0] for k in settings if ".options." in k
                    and tlslib.canonical(k).startswith(f"springsslbundle{kind}{name}options")), f"spring.ssl.bundle.{kind}.{name}")
    return (f"{written}.options.enabled-protocols (server.ssl.bundle is set, so Spring ignores server.ssl.enabled-protocols)",
            values["protocols"], values["ciphers"])


def _flatten_json(text: str) -> dict[str, str] | None:
    try:
        data = json.loads(text)
    except ValueError:
        return None
    flat: dict[str, str] = {}

    def walk(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                walk(f"{prefix}.{key}" if prefix else str(key), child)
        else:
            flat[prefix] = str(value).lower() if isinstance(value, bool) else "" if value is None else str(value)

    walk("", data)
    return flat if isinstance(data, dict) else None


E12_TITLE = ("The services' configuration, with profiles and deployment overrides: the producer matches its stage, "
             "each consumer's client has a key store")


def check_producer_config(repo: Path, manifest: dict[str, Any]) -> Check:
    """E12: the producer's stage settings, and the consumer counterpart."""
    first = _check_producer_stage(repo, manifest)
    first.title = E12_TITLE
    problems, unproven, evidence = consumer_client_problems(repo, manifest)
    if not (problems or unproven or evidence):
        return first                                   # no consumer service in this repository
    applicable = first.result != "not applicable"
    if first.result == "fail" or problems:
        result = "fail"
    elif first.result == "not run" or unproven:
        result = "not run"
    else:
        result = "pass"
    consumer_part = ("; ".join(problems[:2]) if problems else
                     "consumers: " + "; ".join(unproven[:2]) if unproven else
                     f"consumers: every in-scope client is built from a bundle with a key store ({len(evidence)} service(s))")
    detail = (first.detail + "; " if applicable and not (problems and first.result != "fail") else "") + consumer_part
    return Check("E12", E12_TITLE).set(result, detail, problems + unproven + (first.evidence if applicable else []) + evidence)


def _check_producer_stage(repo: Path, manifest: dict[str, Any]) -> Check:
    check = Check("E12", "The producer's configuration, with profiles and deployment overrides, matches its stage")
    if manifest.get("role") == "consumer":
        return check.set("not applicable", "consumer run")
    stage = _stage(manifest)
    local = manifest.get("environment") == "local"
    if not _list(_producer(manifest).get("config_files")):
        return check.set("not run", "the manifest lists no producer config_files")
    stack, folder = producer_stack(repo, manifest)
    if folder is not None and stack not in SPRING_STACKS and stack != "unknown":
        # W5: E12 reads Spring Boot. Another stack is never a pass and never a fail here.
        return check.set("not run", f"stack not read ({stack}): {_rel(repo, folder)} is not a Spring Boot service; E12 reads "
                         "Spring Boot configuration only. Check its TLS settings by hand with the stack page "
                         f"(references/{STACK_PAGES.get(stack, 'java-spring.md')})")
    try:
        config = producer_config(repo, manifest)
    except ValueError as problem:
        return check.set("fail", f"producer config unreadable: {problem}")
    problems: list[str] = []
    unproven: list[str] = list(config.unreadable)
    # Assignments by canonical name: Spring resolves ${inventory.client-auth} from
    # INVENTORY_CLIENT_AUTH and INVENTORY_CLIENTAUTH too, and ${clientAuth} from CLIENTAUTH.
    assignments: dict[str, list[tuple[str, str]]] = {}
    for name, value, where in config.pairs:
        assignments.setdefault(tlslib.canonical(name), []).append((value, where))

    def judge(settings: Settings, label: str) -> None:
        """One way the service may be configured: placeholders resolved to their
        default and to every value found for them, then held against the stage."""
        variants: list[tuple[Settings, str]] = [(settings, label)]
        for canon, key in STAGE_CANON.items():
            raw = str(settings.canon.get(canon, ""))
            if "${" not in raw:
                continue
            match = PLACEHOLDER.fullmatch(raw.strip())
            if not match:
                unproven.append(f"{key} is '{raw}' ({label}): not a value this reader can resolve")
                variants = [(s.copy_with(key, "", "unresolved"), w) for s, w in variants]
                continue
            name, default = match.group(1).strip(), match.group(2)
            found = list(assignments.get(tlslib.canonical(name), []))
            # A placeholder is also resolved from the config files themselves (application-prod.yml
            # setting inventory.client-auth), never only from the deployment.
            in_files = settings.find(name) if tlslib.canonical(name) != canon else ""
            if in_files and in_files != raw:
                found.append((in_files, settings.origin.get(tlslib.canonical(name), "a config file")))
            if default is None and not found:
                unproven.append(f"{key} is ${{{name}}} with no default, and nothing in the repository sets {name}")
            if not found and not local and default is not None:
                unproven.append(f"{key} is ${{{name}:{default}}}: nothing in the repository sets {name}, so what the deployment "
                                "gives it cannot be read")
            values = ([(default, f"{label}, default of ${{{name}}}")] if default is not None else []) + [
                (value, f"{label}, {name} set at {where}") for value, where in found]
            next_variants = []
            for base, base_label in variants:
                for value, why in values or [("", base_label)]:
                    if _unresolved(str(value)):
                        unproven.append(f"{key}: {name} is set to a value filled in at run time ({why})")
                        continue
                    next_variants.append((base.copy_with(key, str(value), why), why))
            variants = next_variants or variants
        for variant, why in variants[:40]:
            for problem in _stage_problems(variant, stage):
                text = f"{problem}  [{why}]"
                if not any(existing.startswith(problem) for existing in problems):
                    problems.append(text)

    scenarios = config.scenarios()
    base = config.resolve(config.base_profiles, config.base_order if config.base_orders else None)
    ignored: list[str] = []
    for label, profiles, order in scenarios:
        for settings, why in config.resolve_all(profiles, order):
            ignored += settings.ignored
            judge(settings, label + (f"; {why}" if why else ""))
    # Deployment-time overrides: environment variables, SPRING_APPLICATION_JSON,
    # -D and -- arguments, in any spelling Spring binds.
    overrides = []
    for name, value, where in config.pairs:
        canon = tlslib.canonical(name)
        key = STAGE_CANON.get(canon)
        if canon == JSON_CANON or name == "SPRING_APPLICATION_JSON":
            flat = _flatten_json(value)
            if flat is None:
                unproven.append(f"{where}: SPRING_APPLICATION_JSON could not be read as JSON")
                continue
            changed = base
            for inner_key, inner_value in flat.items():
                if tlslib.canonical(inner_key) in STAGE_CANON:
                    changed = changed.copy_with(inner_key, inner_value, where)
                    overrides.append((inner_key, inner_value, where))
            if changed is not base:
                judge(changed, f"SPRING_APPLICATION_JSON at {where}")
            continue
        if key is None:
            continue
        overrides.append((key, value, where))
        if _unresolved(value):
            unproven.append(f"{where} sets {key} to a value the gate cannot read ("
                            + ("a reference to a Secret or ConfigMap" if value == UNREADABLE else quoted(value, 60)) + ")")
            continue
        judge(base.copy_with(key, value, where), f"an override at {where} sets {key}={value}")
    evidence = [f"read: {source['name']}" for source in config.sources] + list(dict.fromkeys(config.notes))
    # Values of password, secret and token settings never reach the evidence (D5).
    evidence += [tlslib.mask_secrets(f"{k}={v}") for k, v in sorted(base.items()) if "ssl" in k or "tls.migration" in k]
    evidence += [f"override {where}: {key}={'(not readable)' if value == UNREADABLE else value}" for key, value, where in overrides]
    evidence += [f"checked as it would run with {label}" for label, _, _ in scenarios[1:]]
    evidence += list(dict.fromkeys(ignored))
    where, protocols, ciphers = protocols_in_force(base)
    evidence.append(f"protocols in force: {protocols or 'not set (the JVM default; P5 and P6 test it)'}, from {where}"
                    + (f"; ciphers: {ciphers}" if ciphers else ""))
    if problems:
        return check.set("fail", "; ".join(problems[:4]), problems + unproven + evidence)
    if unproven:
        return check.set("not run", "the configuration in force cannot be read in full: " + "; ".join(unproven[:3]), unproven + evidence)
    return check.set("pass", f"stage {stage}: client-auth {base.find('server.ssl.client-auth')}, legacy HTTP "
                     f"{tlslib.spring_bool(base.find('tls.migration.legacy-http.enabled')) or 'absent'}, allowlist enforced "
                     f"{tlslib.spring_bool(base.find('tls.migration.allowlist.enforce')) or 'not set'}; {len(config.sources)} config "
                     f"source(s), {len(scenarios)} profile set(s), {len(overrides)} override(s) checked", evidence)


# ---------------------------------------------------------------- E13, E14, E15

def check_exceptions(repo: Path, manifest: dict[str, Any]) -> Check:
    check = Check("E13", "Every endpoint left on HTTP has a host, an owner, a reason and a future review date")
    exceptions, problems = load_exceptions(repo, manifest)
    for entry in _list(manifest.get("out_of_scope")):
        if not isinstance(entry, dict) or not entry.get("reason") or not (entry.get("host") or entry.get("file")):
            problems.append(f"out_of_scope entry {entry!r} needs a host (or a file) and a reason")
    if problems:
        return check.set("fail", f"{len(problems)} exception(s) incomplete or expired", problems)
    return check.set("pass", f"{len(exceptions)} exception(s), all complete")


def check_cutover_complete(manifest: dict[str, Any]) -> Check:
    check = Check("E14", "The producer cutover is finished (stage 6)")
    if manifest.get("role") == "consumer":
        return check.set("not applicable", "consumer run")
    stage = _stage(manifest)
    if stage >= 6:
        return check.set("pass", "stage 6: client certificates required and plain HTTP closed")
    return check.set("not run", f"cutover in progress at stage {stage}; the end state is not proven yet")


def skipped_files(repo: Path) -> dict[str, list[dict[str, str]]]:
    report = scan_rules.skipped_report()
    for rows in report.values():
        for row in rows:
            if os.path.isabs(row["path"].split("!")[0]):
                head, _, tail = row["path"].partition("!")
                row["path"] = _rel(repo, Path(head)) + (f"!{tail}" if tail else "")
    return report


def check_everything_read(repo: Path) -> Check:
    check = Check("E15", "Every file that could change a verdict was read")
    report = skipped_files(repo)
    blocking = [f"{row['path']}: {row['reason']}" for row in report["blocking"]]
    noted = [f"{row['path']}: {row['reason']}" for row in report["noted"]]
    if blocking:
        return check.set("not run", f"{len(blocking)} file(s) could not be scanned and could hide a finding: " + "; ".join(blocking[:3]),
                         blocking + noted)
    return check.set("pass", f"nothing unreadable; {len(noted)} folder(s) or file(s) left out on purpose, each listed", noted)


# ---------------------------------------------------------------- main

def overall(checks: list[Check], exceptions: int) -> str:
    results = [c.result for c in checks]
    if "fail" in results:
        return "fail"
    if "not run" in results:
        return "not proven"
    return "pass with exceptions" if exceptions or any(c.signed_off for c in checks) else "pass"


def manifest_path_problems(repo: Path, manifest: dict[str, Any]) -> list[str]:
    """Every path the manifest names that leads out of the repository (D3): ~, an
    absolute path elsewhere, .. out of it, or a symbolic link out of it. Keys and
    a consumer's certificate may be under the exported TLS_PRIVATE_DIR."""
    producer = _producer(manifest)
    named: list[tuple[str, Any, bool]] = []
    for key in ("cert_plan", "probe_plan", "kits", "report", "exceptions"):
        if manifest.get(key):
            named.append((key, manifest[key], False))
    if manifest.get("environment") == "local" and manifest.get("policy"):
        named.append(("policy", manifest["policy"], False))
    for key, value in _evidence(manifest).items():
        named += [(f"evidence.{key}", item, False) for item in _list(value) if item]
    for key in ("config_files", "allowlist", "access_log", "deployed_allowlist", "signoff"):
        named += [(f"producer.{key}", item, False) for item in _list(producer.get(key)) if item]
    consumer = manifest.get("consumer") if isinstance(manifest.get("consumer"), dict) else {}
    for index, entry in enumerate(_list(consumer.get("live_verify"))):
        if isinstance(entry, dict):
            named += [(f"consumer.live_verify[{index}].{key}", entry[key], key != "kit")
                      for key in ("kit", "key", "cert") if entry.get(key)]
    problems = []
    for key, value, private in named:
        if isinstance(value, (dict, list)):
            continue
        try:
            _p(repo, value, private)
        except ValueError as problem:
            problems.append(f"{key}: {problem}")
    return problems


def check_manifest(manifest_path: Path, label: str, repo: Path | None = None) -> tuple[Check, dict[str, Any]]:
    m0 = Check("E0", "The run's manifest (tls-services.yaml) exists and names role, environment, stage and migrating model")
    if not manifest_path.exists():
        return m0.set("fail", f"no manifest at {label}: the migration has not recorded what it did"), {}
    try:
        manifest = tlslib.load_yaml(manifest_path) or {}
    except ValueError as problem:
        return m0.set("fail", f"manifest unreadable: {problem}"), {}
    if not isinstance(manifest, dict):
        return m0.set("fail", "the manifest is not a mapping"), {}
    gaps = []
    if manifest.get("role") not in ("producer", "consumer", "both"):
        gaps.append("role must be producer, consumer or both")
    if manifest.get("environment") not in ("local", "test", "staging", "production"):
        gaps.append("environment must be local, test, staging or production")
    if manifest.get("role") in ("producer", "both"):
        stage = _producer(manifest).get("stage")
        if not isinstance(stage, int) or isinstance(stage, bool) or not 1 <= stage <= 6:
            gaps.append("producer.stage must be a number from 1 to 6")
    # The judge must be a different model line from the one that migrated (opus,
    # sonnet, haiku and fable are different lines; the same line in another
    # version is not independent); that can only be checked when the run says,
    # from its first stage, who it was.
    if not str(manifest.get("migrator_model") or "").strip():
        gaps.append("migrator_model must name the model that did the migration")
    if repo is not None:
        gaps += manifest_path_problems(repo, manifest)
    m0.set("fail" if gaps else "pass", "; ".join(gaps) or f"role {manifest['role']}, environment {manifest['environment']}")
    return m0, manifest


def run_checks(repo: Path, manifest: dict[str, Any], live: bool, operator_policy: str | None = None,
               tags_file: str | None = None, live_target: str | list[str] | None = None) -> tuple[list[Check], int]:
    exceptions, _ = load_exceptions(repo, manifest)
    try:
        rerun = rerun_cert_check(repo, manifest, operator_policy)
    except Exception as problem:  # noqa: BLE001
        rerun = {"error": f"{type(problem).__name__}: {problem}"}
    plan: list[tuple[str, str, Callable[[], Check]]] = [
        ("E1", "Tests", lambda: check_tests(repo, manifest)),
        ("E2", "No plain HTTP left", lambda: check_http_left(repo, manifest, exceptions)),
        ("E3", "Checking not switched off", lambda: check_verify_off(repo)),
        ("E4", "No keys in the repository", lambda: check_keys(repo)),
        ("E5", "Certificates", lambda: check_certificates(repo, manifest, rerun)),
        ("E6", "Probes", lambda: check_probes(repo, manifest, live, rerun, tags_file, live_target)),
        ("E7", "Trust scope", lambda: check_trust_scope(repo, manifest, rerun)),
        ("E8", "Readiness", lambda: check_readiness(repo, manifest, operator_policy, tags_file)),
        ("E9", "Kits", lambda: check_kits(repo, manifest, rerun)),
        ("E10", "Local-dev CAs", lambda: check_local_dev(repo, manifest)),
        ("E12", "Producer config", lambda: check_producer_config(repo, manifest)),
        ("E13", "Exceptions", lambda: check_exceptions(repo, manifest)),
        ("E14", "Cutover complete", lambda: check_cutover_complete(manifest)),
        ("E15", "Everything read", lambda: check_everything_read(repo)),
    ]
    checks = [guarded(cid, title, run) for cid, title, run in plan]
    provisional = overall(checks, len(exceptions))
    probes_path = _p(repo, _evidence(manifest).get("probes", "tls-migration/evidence/probes.json"))
    e6 = next((c for c in checks if c.id == "E6"), None)
    derived = getattr(e6, "derived_probes", None)
    target = getattr(e6, "probe_target", None)
    try:
        settings = warning_settings(repo, manifest, operator_policy)
    except Exception:  # noqa: BLE001 - an unreadable policy adds no warning; E5 and E8 report the policy itself
        settings = {}
    checks.insert(10, guarded("E11", "Report", lambda: check_report(repo, manifest, probes_path, provisional, derived,
                                                                    probe_target=target, live=live, e6=e6, settings=settings)))
    return checks, len(exceptions)


class BadInput(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # argparse would exit 2, which here means "not proven"
        raise BadInput(message)


def _out_problem(out: Path) -> str | None:
    """Why the result cannot be written at `out`, or None."""
    if out.is_dir():
        return f"--out {out} is a folder; name the result file"
    for parent in out.parents:
        if parent.exists():
            return None if parent.is_dir() else f"--out {out}: {parent} is not a folder"
    return None


def _placeholder(out: Path, reason: str, repo: Path | None = None) -> None:
    """A result that says fail until the real one replaces it."""
    tlslib.write_json(out, {"tool": "check.sh", "version": GATE_VERSION, "result": "fail",
                            "generated_at": tlslib.iso(tlslib.now_utc()), "checks": [], "error": reason}, repo)


def policy_refusal(repo: Path, manifest: dict[str, Any], operator_policy: str | None,
                   source: str = "--policy") -> str | None:
    """Outside local the policy is the operator's, from outside the repository (D10):
    a tls-policy.yaml inside --repo is the run's own draft, never an authority.
    source names where the path came from (--policy or TLS_POLICY), for the message."""
    if not operator_policy or manifest.get("environment") == "local":
        return None
    path = Path(os.path.realpath(os.path.expanduser(operator_policy)))
    real_repo = Path(os.path.realpath(repo))
    if path == real_repo or real_repo in path.parents:
        given = f"TLS_POLICY={operator_policy}" if source == "TLS_POLICY" else f"--policy {operator_policy}"
        return (f"{given} is inside the repository under review; outside local the policy must be "
                "the operator's own file, kept outside the repository (a policy in the repository is a draft to report)")
    return None


DEPRECATED_MODES = {"agent-runs-tooling": "platform-issues"}


def note_deprecated_modes(repo: Path, operator_policy: str | None, manifest: dict[str, Any]) -> None:
    """D9: the certificate mode agent-runs-tooling is now platform-issues. An operator's
    policy that still says the old name is read as the new one, with a note. A policy
    inside the repository is never an authority for either."""
    if not operator_policy:
        return
    real_repo = Path(os.path.realpath(repo))
    real_policy = Path(os.path.realpath(os.path.expanduser(operator_policy)))
    if real_repo == real_policy or real_repo in real_policy.parents:
        return                                # a policy in the repository is a draft, never read for modes
    try:
        policy = tlslib.load_yaml(os.path.expanduser(operator_policy)) or {}
    except (OSError, ValueError):
        return
    environments = policy.get("environments") if isinstance(policy, dict) else None
    for name, block in (environments or {}).items() if isinstance(environments, dict) else ():
        modes = block.get("certificate_modes") if isinstance(block, dict) else None
        for old, new in DEPRECATED_MODES.items():
            if isinstance(modes, list) and old in [str(m) for m in modes]:
                print(f"note: the policy's {name} environment lists certificate mode '{old}', the former name of "
                      f"'{new}'; it is read as '{new}' (a person or the pipeline applies what the assistant writes). "
                      "Rename it in the policy.", file=sys.stderr)


def _result_target(argv: list[str]) -> Path | None:
    """Where the result goes, read leniently from any command line, mistyped or
    not (--repo dir, --repo=dir, --out file, --out=file), so that a bad command
    still replaces an older result with a fail."""
    lenient = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    lenient.add_argument("--repo")
    lenient.add_argument("--out")
    try:
        known, _ = lenient.parse_known_args(argv)
    except SystemExit:
        known = argparse.Namespace(repo=None, out=None)
        for index, arg in enumerate(argv):
            for name in ("repo", "out"):
                if arg.startswith(f"--{name}="):
                    setattr(known, name, arg.split("=", 1)[1])
                elif arg == f"--{name}" and index + 1 < len(argv):
                    setattr(known, name, argv[index + 1])
    if known.out:
        return Path(known.out)
    if known.repo and Path(known.repo).is_dir():
        return Path(known.repo) / "tls-migration" / "evidence" / "check-result.json"
    return None


def main() -> int:
    parser = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--manifest", default="tls-migration/tls-services.yaml")
    parser.add_argument("--out")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--policy", default=None,
                        help="the operator's tls-policy.yaml; required outside local (or set TLS_POLICY)")
    parser.add_argument("--live-target", action="append", default=[],
                        help="with --live: host:port the operator confirmed; required outside local, and it must equal the "
                        "target the probe plan (or the kit, or a server-only row) names; once per endpoint")
    parser.add_argument("--tags-file", help="with --live: the file the live probes' request tags are appended to "
                        "(default: probe-tags.log beside probes.json); readiness also leaves those tags out")
    try:
        args = parser.parse_args()
    except BadInput as problem:
        # Bad input is exit 3, and never leaves an older result standing.
        print(f"check.sh: bad input: {problem}", file=sys.stderr)
        print(parser.format_usage(), file=sys.stderr)
        target = _result_target(sys.argv[1:])
        if target is not None and _out_problem(target) is None:
            _placeholder(target, f"bad input: {problem}")
            print(f"written: {target} (fail)", file=sys.stderr)
        return 3
    policy_source = "--policy"
    if args.policy is None and os.environ.get("TLS_POLICY"):
        args.policy, policy_source = os.environ["TLS_POLICY"], "TLS_POLICY"
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"not a folder: {repo}", file=sys.stderr)
        return 3
    manifest_path = _op(repo, args.manifest)
    out = Path(args.out) if args.out else repo / "tls-migration" / "evidence" / "check-result.json"
    problem = _out_problem(out)
    if problem:
        print(f"check.sh: bad input: {problem}", file=sys.stderr)
        return 3
    _placeholder(out, "the gate started and did not finish (it was stopped, or is still running)")
    reset_caches()

    m0, manifest = check_manifest(manifest_path, args.manifest, repo)
    refused = policy_refusal(repo, manifest, args.policy, policy_source)
    if refused:
        print(f"check.sh: bad input: {refused}", file=sys.stderr)
        _placeholder(out, f"bad input: {refused}", repo)
        return 3
    note_deprecated_modes(repo, args.policy, manifest)
    exceptions = 0
    if m0.result == "pass":
        checks, exceptions = run_checks(repo, manifest, args.live, args.policy, args.tags_file, args.live_target)
        checks.insert(0, m0)
        result = overall(checks, exceptions)
    else:
        # Keys and disabled checks are worth reporting even without a manifest.
        checks = [m0, guarded("E3", "Checking not switched off", lambda: check_verify_off(repo)),
                  guarded("E4", "No keys in the repository", lambda: check_keys(repo))]
        result = "fail"

    inputs = {}
    try:
        for name in ("cert_plan", "probe_plan", "report", "exceptions"):
            value = manifest.get(name)
            if value and _p(repo, value).is_file():
                inputs[str(value)] = tlslib.sha256_file(_p(repo, value))
        for value in _evidence(manifest).values():
            for item in _list(value):
                if _p(repo, item).is_file():
                    inputs[str(item)] = tlslib.sha256_file(_p(repo, item))
        inputs.update(probe_tls.bound_inputs(repo, manifest) if manifest else {})
        if manifest_path.is_file():
            inputs[str(args.manifest)] = tlslib.sha256_file(manifest_path)
        if args.policy and Path(os.path.expanduser(args.policy)).is_file():
            inputs[f"policy:{_rel(repo, Path(os.path.expanduser(args.policy)))}"] = tlslib.sha256_file(os.path.expanduser(args.policy))
    except Exception as problem:  # noqa: BLE001 - the hashes are a record, never a reason to skip writing
        inputs["_error"] = f"{type(problem).__name__}: {problem}"

    counts = {k: sum(1 for c in checks if c.result == k) for k in ("pass", "fail", "not run", "not applicable")}
    skipped = skipped_files(repo)
    data = {
        "tool": "check.sh",
        "version": GATE_VERSION,
        "generated_at": tlslib.iso(tlslib.now_utc()),
        "repo": ".",
        "role": manifest.get("role"),
        "environment": manifest.get("environment"),
        "stage": _producer(manifest).get("stage"),
        "mode": "live" if args.live else "recorded",
        "result": result,
        "counts": counts,
        "exceptions": exceptions,
        "signed_off": sum(c.signed_off for c in checks),
        "checks": [c.as_dict() for c in checks],
        "skipped": skipped,
        "inputs_sha256": inputs,
    }
    if manifest.get("environment") == "local" and result.startswith("pass"):
        data["note"] = "proven locally with local-dev certificates; this never stands in for staging or production"
    tlslib.write_json(out, data, repo)
    width = max(len(c.title) for c in checks)
    for c in checks:
        print(tlslib.mask_secrets(f"{c.id:<4} {c.result:<15} {c.title:<{width}}  {c.detail}"))
    print(f"\nresult: {result}  ({counts})")
    if data.get("note"):
        print(data["note"])
    total_skipped = len(skipped["blocking"]) + len(skipped["noted"])
    if total_skipped:
        print(f"not scanned: {total_skipped} file(s) or folder(s), each with its reason under \"skipped\" in the result"
              + (f"; {len(skipped['blocking'])} of them could hide a finding" if skipped["blocking"] else ""))
        for row in (skipped["blocking"] + skipped["noted"])[:12]:
            print(tlslib.mask_secrets(f"  - {row['path']}: {row['reason']}"))
        if total_skipped > 12:
            print(f"  - and {total_skipped - 12} more")
    print(f"written: {out}")
    return {"pass": 0, "pass with exceptions": 0, "fail": 1, "not proven": 2}[result]


def stop_on_signals() -> None:
    """SIGTERM and SIGHUP end the gate the way Ctrl-C does: by an exception, so every
    temporary folder is removed on the way out (and a running verify.sh or openssl
    is killed by subprocess). The result file keeps its "did not finish" placeholder."""
    def stop(number: int, _frame: Any) -> None:
        raise SystemExit(128 + number)
    for name in ("SIGTERM", "SIGHUP"):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), stop)


if __name__ == "__main__":
    stop_on_signals()
    try:
        sys.exit(main())
    except Exception as crash:  # noqa: BLE001 - never leave an older passing result behind
        target = _result_target(sys.argv[1:]) or Path(".") / "tls-migration" / "evidence" / "check-result.json"
        try:
            tlslib.write_json(target, {"tool": "check.sh", "version": GATE_VERSION, "result": "fail",
                                       "generated_at": tlslib.iso(tlslib.now_utc()),
                                       "checks": [], "error": f"{type(crash).__name__}: {crash}"})
            print(f"check.sh crashed: {crash}; {target} now says fail", file=sys.stderr)
        except OSError as problem:
            print(f"check.sh crashed: {crash}; and no result could be written at {target}: {problem}", file=sys.stderr)
        sys.exit(1)
