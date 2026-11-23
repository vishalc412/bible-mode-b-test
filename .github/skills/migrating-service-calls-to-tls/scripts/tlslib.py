"""Shared helpers for the TLS migration scripts.

Python 3.9+ standard library only, plus the openssl 3 command line. Nothing
here ever reads a private key: certificate facts come from public files, and
key-holding commands are left to the shell scripts that create the keys. The
one exception, key_matches_cert, has openssl derive the public half of a key;
the key's content never enters Python and nothing of it is printed.
"""
from __future__ import annotations

import base64
import binascii
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------- YAML subset

try:  # PyYAML when present; otherwise the small parser below.
    import yaml as _pyyaml  # type: ignore
except ImportError:  # pragma: no cover - depends on the machine
    _pyyaml = None


UNSUPPORTED = ("this YAML needs PyYAML, which is not available to this run (a person decides whether to install it; "
               "an assistant never installs software), or a plainer form")


def _scalar(text: str) -> Any:
    text = text.strip()
    if text == "" or text in ("~", "null", "Null", "NULL"):
        return None
    # The subset reader refuses what it cannot read exactly, rather than guess:
    # results with and without PyYAML must never differ silently.
    if text[0] == "{":
        raise ValueError(f"flow mapping {text[:40]!r}: {UNSUPPORTED}: write the map as indented lines")
    if re.fullmatch(r"[|>][+-]?\d*", text):
        # A literal block (| |- |+) is read before this; a folded one (>) or one
        # with an indentation indicator is not.
        raise ValueError(f"block scalar '{text}': {UNSUPPORTED}: put the value on one line")
    if text[0] in "&*!" or text.startswith("<<"):
        raise ValueError(f"anchor, alias, tag or merge key {text[:40]!r}: {UNSUPPORTED}")
    if (text[0] == text[-1]) and text[0] in "\"'" and len(text) >= 2:
        inner = text[1:-1]
        # YAML escapes a single quote inside single quotes by doubling it.
        return inner.replace("''", "'") if text[0] == "'" else inner.replace('\\"', '"')
    if text[0] in "\"'" and (len(text) < 2 or text[-1] != text[0]):
        raise ValueError(f"unclosed quote {text[:40]!r}: {UNSUPPORTED}")
    if text[0] == "[" and not text.endswith("]"):
        # An unclosed flow sequence: PyYAML refuses it, so the subset reader does too
        # (the gate runs isolated and may not see a PyYAML installed for one user only).
        raise ValueError(f"unclosed flow sequence {text[:40]!r}: {UNSUPPORTED}")
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        if "[" in inner or "{" in inner:
            raise ValueError(f"nested inline collection {text[:40]!r}: {UNSUPPORTED}")
        return [_scalar(part) for part in _split_inline(inner)]
    # The same spellings PyYAML (YAML 1.1) reads as booleans, so a sign-off that
    # says "No" is never a truthy string on a machine without PyYAML.
    if text in _YAML_TRUE:
        return True
    if text in _YAML_FALSE:
        return False
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


_YAML_TRUE = {"true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"}
_YAML_FALSE = {"false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"}


def _split_inline(text: str) -> list[str]:
    parts, current, quote = [], "", None
    for char in text:
        if quote:
            current += char
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
            current += char
        elif char == ",":
            parts.append(current)
            current = ""
        else:
            current += char
    parts.append(current)
    return [p.strip() for p in parts if p.strip()]


def _strip_comment(line: str) -> str:
    quote = None
    for index, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or line[index - 1] in " \t"):
            return line[:index].rstrip()
    return line.rstrip()


def _parse_block(lines: list[tuple[int, str]], start: int, indent: int) -> tuple[Any, int]:
    """Parses the block whose lines are indented exactly `indent`."""
    if start >= len(lines):
        return None, start
    is_list = lines[start][1].startswith("- ") or lines[start][1] == "-"
    result: Any = [] if is_list else {}
    index = start
    while index < len(lines):
        line_indent, text = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise ValueError(f"unexpected indentation: {text!r}")
        if is_list:
            if not (text.startswith("- ") or text == "-"):
                break
            item_text = text[2:].strip() if text != "-" else ""
            if item_text == "":
                value, index = _parse_block(lines, index + 1, _child_indent(lines, index + 1, indent))
                result.append(value)
                continue
            if re.match(r"^[A-Za-z0-9_.\-\"']+\s*:(\s|$)", item_text):
                # A map item: its first key is on the dash line, the rest are indented.
                item_indent = indent + 2
                synthetic = [(item_indent, item_text)]
                cursor = index + 1
                while cursor < len(lines) and lines[cursor][0] >= item_indent:
                    synthetic.append(lines[cursor])
                    cursor += 1
                value, _ = _parse_block(synthetic, 0, item_indent)
                result.append(value)
                index = cursor
                continue
            result.append(_scalar(item_text))
            index += 1
        else:
            # The key runs to its last character that is not white space before the
            # colon (one blank when there is none): no blank is read two ways (S-04).
            match = re.match(r"^(\"[^\"]*\"|'[^']*'|[^:]*[^:\s]|\s)\s*:(?:\s+(.*))?$", text)
            if not match:
                raise ValueError(f"cannot parse line: {text!r}")
            key = _scalar(match.group(1))
            rest = (match.group(2) or "").strip()
            if rest:
                result[key] = _scalar(rest)
                index += 1
            else:
                child = _child_indent(lines, index + 1, indent)
                if child is None:
                    result[key] = None
                    index += 1
                else:
                    result[key], index = _parse_block(lines, index + 1, child)
    return result, index


def _child_indent(lines: list[tuple[int, str]], index: int, parent: int) -> Any:
    if index >= len(lines):
        return None
    line_indent, text = lines[index]
    if line_indent > parent:
        return line_indent
    # YAML allows a list at the same indentation as its parent key.
    if line_indent == parent and text.startswith("- "):
        return line_indent
    return None


# A key line ending in a literal block indicator. The key runs up to the first
# colon in one piece (S-04: a lazy key followed by optional white space matched
# the same spaces two ways).
BLOCK_HEAD = re.compile(r"(?P<head>(?:- )?(?:\"[^\"]*\"\s*|'[^']*'\s*|[^:#]+):|-)\s+\|(?P<chomp>[+-]?)")
_BLOCK_TOKEN = re.compile(r"\x00block(\d+)\x00")


def _literal_block(raw_lines: list[str], start: int, parent_indent: int, chomp: str,
                   final_break: bool = True) -> tuple[str, int]:
    """A literal block scalar (| |- |+) from the raw lines after its key line:
    (the text, the index of the first line after it). Lines are kept as written,
    comments and blank lines included, less the block's own indentation."""
    content: list[str] = []
    block_indent = None
    index = start
    while index < len(raw_lines):
        raw = raw_lines[index].rstrip("\r")
        if not raw.strip():
            content.append("")
            index += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent <= parent_indent:
            break
        if block_indent is None:
            block_indent = indent
        elif indent < block_indent:
            raise ValueError(f"a block scalar line is indented less than the block: {raw.strip()[:40]!r}")
        content.append(raw[block_indent:])
        index += 1
    while index > start and not raw_lines[index - 1].strip() and content and content[-1] == "" and chomp != "+":
        # Trailing blank lines are not part of the value (unless kept with |+); they stay with the document.
        content.pop()
        index -= 1
    body = "\n".join(content)
    if index >= len(raw_lines) and not final_break:
        return body.rstrip("\n") if chomp != "+" else body, index     # the text ends without a line break
    if chomp == "-":
        return body.rstrip("\n"), index
    if chomp == "+":
        return body + "\n", index
    return (body.rstrip("\n") + "\n") if body else "", index


def parse_yaml_subset(text: str) -> Any:
    raw_lines = text.splitlines()
    lines = []
    blocks: list[str] = []
    index = 0
    while index < len(raw_lines):
        raw = raw_lines[index]
        index += 1
        if raw.strip() in ("---", "..."):
            continue
        cleaned = _strip_comment(raw)
        if not cleaned.strip():
            continue
        if "\t" in cleaned[: len(cleaned) - len(cleaned.lstrip())]:
            raise ValueError("tabs are not allowed for indentation")
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        block = BLOCK_HEAD.fullmatch(cleaned.strip())
        if block:
            # A literal block (a file kept in a ConfigMap): read exactly, never guessed.
            head = block.group("head")
            parent = indent + 2 if head.startswith("- ") else indent     # "- key: |": the map is two further in
            value, index = _literal_block(raw_lines, index, parent, block.group("chomp"), text.endswith(("\n", "\r")))
            blocks.append(value)
            cleaned = " " * indent + head + f" \x00block{len(blocks) - 1}\x00"
        lines.append((indent, cleaned.strip()))
    if not lines:
        return None
    value, index = _parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise ValueError(f"could not parse from line: {lines[index][1]!r}")
    return _fill_blocks(value, blocks) if blocks else value


def _fill_blocks(value: Any, blocks: list[str]) -> Any:
    if isinstance(value, dict):
        return {key: _fill_blocks(child, blocks) for key, child in value.items()}
    if isinstance(value, list):
        return [_fill_blocks(child, blocks) for child in value]
    if isinstance(value, str):
        match = _BLOCK_TOKEN.fullmatch(value)
        if match:
            return blocks[int(match.group(1))]
    return value


def regular_file(path: str | Path) -> Path:
    """The path, when it is a regular file (or a link to one). A named pipe,
    socket or device would block or never end a read: refused with ValueError,
    as is a folder. A missing file raises FileNotFoundError, as open() would."""
    import stat as _stat

    path = Path(path)
    mode = path.stat().st_mode
    if not _stat.S_ISREG(mode):
        raise ValueError(f"{path} is not a regular file (a pipe, socket, device or folder): not read")
    return path


def read_regular(path: str | Path, encoding: str = "utf-8", errors: str = "strict") -> str:
    return regular_file(path).read_text(encoding=encoding, errors=errors)


def load_yaml(path: str | Path) -> Any:
    """Loads one YAML document. Raises ValueError for anything unparsable."""
    text = read_regular(path, encoding="utf-8-sig")   # a byte-order mark is not part of the first key
    if _pyyaml is not None:
        try:
            return _pyyaml.safe_load(text)
        except _pyyaml.YAMLError as problem:
            raise ValueError(f"{path}: {problem}".splitlines()[0]) from problem
    return parse_yaml_subset(text)


# ---------------------------------------------------------------- Spring names and values

def canonical(name: Any) -> str:
    """One spelling for every form Spring's relaxed binding accepts:
    server.ssl.client-auth, server.ssl.clientAuth, server.ssl.client_auth,
    SERVER_SSL_CLIENTAUTH and SERVER_SSL_CLIENT_AUTH all read "serversslclientauth"."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


_SPRING_TRUE = {"true", "on", "yes", "1"}
_SPRING_FALSE = {"false", "off", "no", "0"}


def spring_bool(value: Any) -> str:
    """A boolean the way Spring converts it: "true", "false", or the text itself
    (lower case) when it is neither, so the caller can see it was not a boolean."""
    text = str(value).strip().strip("\"'").lower()
    if text in _SPRING_TRUE:
        return "true"
    if text in _SPRING_FALSE:
        return "false"
    return text


CONFIG_NAME = re.compile(r"^application(?:-(?P<profile>[A-Za-z0-9_.]+))?\.(?:ya?ml|properties)$")


def spring_config_files(repo: str | Path, listed: list[Any]) -> list[dict[str, Any]]:
    """Every Spring config file of the modules the listed files belong to, lowest
    precedence first, in Spring's order: inside the jar (classpath root, then
    classpath config/), plain files before profile files; then outside the jar
    (the module and repository root, their config/ and config/*/ folders),
    plain files before profile files. .properties after .yml at one place.
    Each entry: path, name (relative), profile (None or its name), group (0
    inside the jar, 1 outside it), rank (the place within the group) and
    order (group, profile file, rank, .properties, name)."""
    repo = Path(repo)
    found: dict[Path, dict[str, Any]] = {}

    def add(path: Path, group: int, rank: float) -> None:
        if not path.is_file():
            return
        match = CONFIG_NAME.match(path.name)
        profile = match.group("profile") if match else None
        key = path.resolve()
        if key in found:
            return
        try:
            relative = path.relative_to(repo).as_posix()
        except ValueError:
            relative = str(path)
        props = 1 if path.suffix == ".properties" else 0
        found[key] = {"path": path, "name": relative, "profile": profile, "group": group, "rank": rank, "props": props,
                      "order": (group, 1 if profile else 0, rank, props, path.name)}

    def folder(directory: Path, group: int, rank: float) -> None:
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                if CONFIG_NAME.match(path.name):
                    add(path, group, rank)

    def outside(base: Path) -> None:
        folder(base, 1, 0)
        folder(base / "config", 1, 1)
        if (base / "config").is_dir():
            for sub in sorted((base / "config").iterdir()):        # file:./config/*/
                if sub.is_dir() and not sub.name.startswith("."):
                    folder(sub, 1, 2)

    paths = []
    for item in listed:
        path = repo_path(repo, item)          # inside the repository only (D3); raises OutsideRepo
        paths.append(path)
        parts = path.parts
        module = None
        for index in range(len(parts) - 2):
            if parts[index:index + 3] == ("src", "main", "resources"):
                module = Path(*parts[:index]) if index else Path(".")
                break
        if module is None:
            folder(path.parent, 0, 0)
            continue
        resources = module / "src" / "main" / "resources"
        folder(resources, 0, 0)
        folder(resources / "config", 0, 1)
        outside(module)
    outside(repo)
    for path in paths:          # a listed file in a place of its own: read as a classpath root file
        add(path, 0, 0)
    return sorted(found.values(), key=lambda entry: entry["order"])


# ---------------------------------------------------------------- shell + json

def run(cmd: list[str], stdin: str | None = None, timeout: int = 60) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            cmd, input=stdin, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s: {' '.join(cmd)}"
    return completed.returncode, completed.stdout, completed.stderr


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(moment: dt.datetime | None) -> str | None:
    return moment.isoformat().replace("+00:00", "Z") if moment else None


class UnsafeWrite(OSError):
    """A write the toolkit refuses: through a symbolic link, or out of the repository."""


def find_repo_root(path: str | Path) -> Path | None:
    """The repository a path lies in, found without following links: the nearest
    folder above it that holds tls-migration/ or a version-control folder."""
    current = Path(os.path.abspath(path)).parent
    while True:
        for marker in ("tls-migration", ".git", ".svn", ".hg"):
            if os.path.lexists(current / marker):
                return current
        if current.parent == current:
            return None
        current = current.parent


def _under(path: Path, base: Path) -> bool:
    return path == base or base in path.parents


def check_write_target(path: str | Path, repo: str | Path | None = None) -> Path:
    """Refuses (UnsafeWrite) a file the toolkit is about to write when the file,
    its .tmp, or any folder between the repository root and the file is a
    symbolic link, or when the folder it lands in is outside the repository.
    Folders above the repository root are not looked at. Without `repo`, the
    repository is found from the path (find_repo_root); outside any repository
    only the file and its .tmp are checked. Returns the path, absolute."""
    target = Path(os.path.abspath(path))
    for item in (target, target.with_name(target.name + ".tmp")):
        if os.path.islink(item):
            raise UnsafeWrite(f"refused to write {item}: it is a symbolic link")
    root = Path(os.path.abspath(repo)) if repo is not None else find_repo_root(target)
    if root is None:
        return target
    real_root = Path(os.path.realpath(root))
    # The repository as this path spells it: the outermost folder on the way that
    # is the repository (a link above the repository, such as /tmp, is fine).
    base = None
    for ancestor in reversed([target.parent, *target.parent.parents]):
        if ancestor in (root, real_root) or Path(os.path.realpath(ancestor)) == real_root:
            base = ancestor
            break
    if base is None:
        if _under(Path(os.path.realpath(target.parent)), real_root):
            raise UnsafeWrite(f"refused to write {target}: it reaches into the repository {root} through a symbolic link")
        return target            # outside the repository: the operator's own place
    current = base
    for part in target.parent.relative_to(base).parts:
        current = current / part
        if os.path.islink(current):
            raise UnsafeWrite(f"refused to write {target}: {current} is a symbolic link "
                              "(a file inside the repository may not lead the toolkit elsewhere)")
    existing = target.parent
    while not existing.exists() and existing != base:
        existing = existing.parent
    if not _under(Path(os.path.realpath(existing)), real_root):
        raise UnsafeWrite(f"refused to write {target}: its folder is outside the repository {root}")
    return target


def safe_mkdir(folder: str | Path, repo: str | Path | None = None, mode: int = 0o777) -> Path:
    """Creates a folder (and its parents) after the same checks as a file write."""
    folder = Path(os.path.abspath(folder))
    check_write_target(folder / ".probe", repo)
    folder.mkdir(parents=True, exist_ok=True, mode=mode)
    check_write_target(folder / ".probe", repo)       # nothing was swapped in while it was made
    return folder


def write_text(path: str | Path, text: str | bytes, repo: str | Path | None = None, mode: int | None = None) -> None:
    """Writes a file through <file>.tmp beside it, then moves it into place, after
    check_write_target. The .tmp is created new (never through a link) and never
    stays behind. A target that is a folder is refused before anything is written."""
    path = Path(path)
    if path.is_dir() and not path.is_symlink():
        raise IsADirectoryError(f"{path} is a folder, not a file to write")
    target = check_write_target(path, repo)
    safe_mkdir(target.parent, repo)
    tmp = target.with_name(target.name + ".tmp")
    data = text.encode("utf-8") if isinstance(text, str) else text
    if os.path.lexists(tmp):
        if os.path.islink(tmp) or not tmp.is_file():
            raise UnsafeWrite(f"refused to write {target}: {tmp} is in the way and is not a plain file")
        tmp.unlink()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        handle = os.open(tmp, flags, 0o666 if mode is None else mode)
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        if mode is not None:
            os.chmod(tmp, mode)
        check_write_target(target, repo)
        os.replace(tmp, target)
    finally:
        if os.path.lexists(tmp) and not os.path.islink(tmp) and tmp.is_file():
            tmp.unlink()


def write_json(path: str | Path, data: Any, repo: str | Path | None = None) -> None:
    """Writes JSON through write_text: secret values masked (mask_data), no write
    through a symbolic link, never out of the repository."""
    write_text(path, json.dumps(mask_data(data), indent=2, sort_keys=False) + "\n", repo)


# ---------------------------------------------------------------- secrets in evidence

# The names whose values are never written or printed (D5).
SECRET_NAME = re.compile(r"(?i)password|passphrase|secret|token|credential|api[-_]?key")
# key = value, key: value, "key": "value", with the key holding one of those names.
# Bounded, non-overlapping pieces only: this runs over repository text.
_SECRET_PAIR = re.compile(
    r"(?i)(?P<head>(?:password|passphrase|secret|token|credential|api[-_]?key)[\w.\-]{0,64}[\"']?[ \t]{0,8}[:=][ \t]{0,8}[\"']?)"
    r"(?P<value>[^\s\"',;}\]]{1,512})")
# scheme://user:password@host and scheme://token@host.
_USERINFO = re.compile(r"(?i)\b(?P<scheme>[a-z][a-z0-9+.\-]{0,30}://)[^\s/?#@\"'<>]{1,256}@")
# A field whose value is masked whole: its name ends in one of the words
# (key-store-password, client_secret, apiKey), never a file name or a list of tags.
_SECRET_FIELD = re.compile(r"(?i)[\w.\-]{0,64}(?:password|passphrase|secret|token|credential|api[-_]?key)")
_OWN_FIELDS = {"tokens"}


def _keep_value(value: str) -> bool:
    """A placeholder (${DB_PASSWORD}, {{ .Values.x }}) or an already masked value says nothing secret."""
    return value == "***" or value.startswith(("${", "{{", "#{", "$(", "%(", "<")) or value.startswith("@")


def mask_secrets(text: str) -> str:
    """The text with every secret value replaced by ***: values of keys named
    password, passphrase, secret, token, credential or api key, and URL user-info."""
    if not isinstance(text, str) or not text:
        return text
    text = _USERINFO.sub(lambda m: m.group("scheme") + "***@", text)
    return _SECRET_PAIR.sub(lambda m: m.group(0) if _keep_value(m.group("value"))
                            else m.group("head") + "***", text)


def mask_data(data: Any) -> Any:
    """mask_secrets over every string of a JSON-like value; a string value whose
    own key is a secret name (password: "...") is masked whole."""
    if isinstance(data, str):
        return mask_secrets(data)
    if isinstance(data, dict):
        out = {}
        for key, value in data.items():
            if isinstance(value, str) and isinstance(key, str) and key not in _OWN_FIELDS \
                    and _SECRET_FIELD.fullmatch(key) and value and not _keep_value(value):
                out[key] = "***"
            else:
                out[key] = mask_data(value)
        return out
    if isinstance(data, (list, tuple)):
        return [mask_data(item) for item in data]
    return data


# ---------------------------------------------------------------- paths a repository file names

class OutsideRepo(ValueError):
    """A path from a repository file (manifest, plan) that leads out of the repository."""


PRIVATE_DIR_TOKENS = ("$TLS_PRIVATE_DIR", "${TLS_PRIVATE_DIR}")


def private_dir() -> Path | None:
    """The operator's exported key folder, or None."""
    value = os.environ.get("TLS_PRIVATE_DIR", "").strip()
    return Path(os.path.abspath(value)) if value else None


def _spelled_under(path: Path, real_base: Path) -> bool:
    """True when a folder on the way to `path` is `real_base` spelled another way
    (through a link above it, such as /var for /private/var)."""
    return any(Path(os.path.realpath(ancestor)) == real_base for ancestor in path.parents)


def repo_path(repo: str | Path, value: Any, private: bool = False) -> Path:
    """A path named by a repository file, resolved inside the repository only (D3):
    no ~, no absolute path outside it, no .. out of it, no symbolic link out of it.
    With private=True a path under the exported TLS_PRIVATE_DIR is allowed too,
    written as $TLS_PRIVATE_DIR/... or as the folder itself. Raises OutsideRepo."""
    repo = Path(os.path.abspath(repo))
    text = str(value).strip()
    if private:
        for token in PRIVATE_DIR_TOKENS:
            if text == token or text.startswith(token + "/"):
                folder = private_dir()
                if folder is None:
                    raise OutsideRepo(f"{text}: TLS_PRIVATE_DIR is not set, so this path cannot be used")
                text = str(folder) + text[len(token):]
                break
    if text.startswith("~"):
        raise OutsideRepo(f"{text}: outside the repository (a path in a repository file may not start with ~)")
    candidate = Path(text) if os.path.isabs(text) else repo / text
    normal = Path(os.path.normpath(candidate))
    folder = private_dir() if private else None
    if folder is not None:
        real_folder = Path(os.path.realpath(folder))
        if _under(normal, folder) or _under(normal, real_folder) or _spelled_under(normal, real_folder):
            return normal
    real_repo = Path(os.path.realpath(repo))
    if not (_under(normal, repo) or _under(normal, real_repo) or _spelled_under(normal, real_repo)):
        raise OutsideRepo(f"{text}: outside the repository; a repository file may only name paths inside it"
                          + (" or under the exported TLS_PRIVATE_DIR" if private else ""))
    if not _under(Path(os.path.realpath(normal)), real_repo):
        raise OutsideRepo(f"{text}: a symbolic link inside the repository leads out of it")
    return normal


def shown_path(path: str | Path, repo: str | Path | None = None) -> str:
    """A path as evidence shows it: relative to the repository, or
    $TLS_PRIVATE_DIR/..., never an absolute path with a user name in it (D5)."""
    path = Path(os.path.abspath(path))
    if repo is not None:
        for base in (Path(os.path.abspath(repo)), Path(os.path.realpath(repo))):
            if _under(path, base):
                return path.relative_to(base).as_posix() or "."
    folder = private_dir()
    if folder is not None:
        for base in (folder, Path(os.path.realpath(folder))):
            if _under(path, base):
                rest = path.relative_to(base).as_posix()
                return "$TLS_PRIVATE_DIR" + ("/" + rest if rest != "." else "")
    home = Path(os.path.expanduser("~"))
    if _under(path, home):
        return "~/" + path.relative_to(home).as_posix()
    return str(path)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------- certificates

PEM_CERT = re.compile(r"-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----", re.S)
PRIVATE_KEY_MARKER = re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")
EKU_NAMES = {
    "TLS Web Server Authentication": "serverAuth",
    "TLS Web Client Authentication": "clientAuth",
    "Code Signing": "codeSigning",
    "E-mail Protection": "emailProtection",
    "Time Stamping": "timeStamping",
    "OCSP Signing": "OCSPSigning",
    "Any Extended Key Usage": "anyExtendedKeyUsage",
}


PEM_BEGIN = re.compile(r"^-----BEGIN ([^-]*)-----$")
PEM_BODY_LINE = re.compile(r"^[A-Za-z0-9+/=]+$")
# Every label OpenSSL, curl, Python's ssl and Spring's PEM reader take for a
# certificate. Scans for certificates in arbitrary text read all of them;
# a file that is trusted holds only the plain one (split_bundle).
ANY_PEM_CERT = re.compile(r"-----BEGIN ((?:X509 |TRUSTED )?CERTIFICATE)-----([A-Za-z0-9+/=\s]+?)-----END \1-----")


def split_bundle(path: str | Path) -> list[str]:
    """The certificates of a file that is trusted or issued (a trust store, a CA,
    a kit's ca-bundle.pem, a leaf): plain CERTIFICATE blocks and nothing else.
    Any other line outside the blocks, or any other -----BEGIN label (X509
    CERTIFICATE, TRUSTED CERTIFICATE, a CRL, a key), raises ValueError, the way
    the kit's verify.sh refuses it: a block this reader skipped would still be
    trusted by OpenSSL, curl, Python's ssl and Spring."""
    text = read_regular(path, errors="replace")
    if PRIVATE_KEY_MARKER.search(text):
        # A certificate file must never carry a key; refuse rather than parse it.
        raise ValueError(f"{path} contains a private key block")
    certs: list[str] = []
    body: list[str] | None = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip().lstrip("\ufeff") if number == 1 else raw.strip()
        if body is None:
            if not line:
                continue
            if line == "-----BEGIN CERTIFICATE-----":
                body = []
                continue
            label = PEM_BEGIN.match(line)
            if label:
                raise ValueError(f"{path}: line {number} starts a '-----BEGIN {label.group(1)}-----' block; "
                                 "a certificate file holds only CERTIFICATE blocks")
            raise ValueError(f"{path}: line {number} is outside any CERTIFICATE block; "
                             "a certificate file holds only CERTIFICATE blocks")
        if line == "-----END CERTIFICATE-----":
            if not body:
                raise ValueError(f"{path}: line {number} ends an empty CERTIFICATE block")
            certs.append("-----BEGIN CERTIFICATE-----\n" + "\n".join(body) + "\n-----END CERTIFICATE-----")
            body = None
            continue
        if not PEM_BODY_LINE.match(line):
            raise ValueError(f"{path}: line {number}, inside a CERTIFICATE block, is not base64")
        body.append(line)
    if body is not None:
        raise ValueError(f"{path}: a CERTIFICATE block is not closed")
    return certs


def _leading_der(data: bytes) -> bytes | None:
    """The DER SEQUENCE at the start of `data` (a TRUSTED CERTIFICATE carries
    trust settings after the certificate), or None when there is none."""
    if data[:1] != b"\x30" or len(data) < 4:
        return None
    first = data[1]
    if first < 0x80:
        total = 2 + first
    elif first in (0x81, 0x82, 0x83):
        count = first - 0x80
        total = 2 + count + int.from_bytes(data[2:2 + count], "big")
    else:
        return None
    return data[:total] if total <= len(data) else None


def certificates_in_text(text: str) -> list[tuple[int, str]]:
    """Every certificate block in a text, under any label a TLS library reads
    (CERTIFICATE, X509 CERTIFICATE, TRUSTED CERTIFICATE), as (offset, plain
    PEM). A TRUSTED CERTIFICATE's leading DER is the certificate."""
    found = []
    for match in ANY_PEM_CERT.finditer(text):
        body = "".join(match.group(2).split())
        if match.group(1) != "CERTIFICATE":
            try:
                der = _leading_der(base64.b64decode(body + "=" * (-len(body) % 4)))
            except (binascii.Error, ValueError):
                continue
            if der is None:
                continue
            body = base64.b64encode(der).decode()
        lines = [body[i:i + 64] for i in range(0, len(body), 64)]
        found.append((match.start(), "-----BEGIN CERTIFICATE-----\n" + "\n".join(lines) + "\n-----END CERTIFICATE-----"))
    return found


def _parse_iso(text: str) -> dt.datetime:
    """Reads an ISO time or openssl's 'Nov 13 23:33:30 2026 GMT' form, as UTC."""
    text = " ".join(text.split())
    if text.endswith(" GMT"):
        moment = dt.datetime.strptime(text, "%b %d %H:%M:%S %Y GMT")
        return moment.replace(tzinfo=dt.timezone.utc)
    moment = dt.datetime.fromisoformat(text.replace("Z", "+00:00").replace(" ", "T"))
    return moment if moment.tzinfo else moment.replace(tzinfo=dt.timezone.utc)


def cert_info_from_pem(pem: str) -> dict[str, Any]:
    code, text, err = run(
        ["openssl", "x509", "-noout", "-text", "-nameopt", "RFC2253", "-dateopt", "iso_8601",
         "-fingerprint", "-sha256"],
        stdin=pem,
    )
    if code != 0:
        raise ValueError(f"openssl could not read certificate: {err.strip()}")
    info: dict[str, Any] = {}

    def grab(pattern: str) -> str | None:
        match = re.search(pattern, text, re.M)
        return match.group(1).strip() if match else None

    info["subject"] = grab(r"^\s*Subject:\s*(.*)$") or ""
    info["issuer"] = grab(r"^\s*Issuer:\s*(.*)$") or ""
    info["subject_cn"] = _cn(info["subject"])
    info["issuer_cn"] = _cn(info["issuer"])
    info["not_before"] = iso(_parse_iso(grab(r"Not Before\s*:\s*(.*)$") or ""))
    info["not_after"] = iso(_parse_iso(grab(r"Not After\s*:\s*(.*)$") or ""))
    fingerprint = grab(r"^sha256 Fingerprint=(.*)$") or grab(r"^SHA256 Fingerprint=(.*)$") or ""
    info["fingerprint_sha256"] = fingerprint.replace(":", "").lower()

    if "id-ecPublicKey" in text:
        curve = grab(r"NIST CURVE:\s*(\S+)") or grab(r"ASN1 OID:\s*(\S+)") or "unknown"
        curve = {"prime256v1": "P-256", "secp384r1": "P-384", "secp521r1": "P-521"}.get(curve, curve)
        info["key_type"] = f"EC {curve}"
    elif "rsaEncryption" in text:
        bits = grab(r"Public-Key:\s*\((\d+) bit\b")
        info["key_type"] = f"RSA {bits}"
    elif "ED25519" in text:
        info["key_type"] = "Ed25519"
    else:
        info["key_type"] = "unknown"

    basic = _extension_body(text, "X509v3 Basic Constraints")
    info["is_ca"] = bool(basic and "CA:TRUE" in basic)
    pathlen = re.search(r"pathlen:(\d+)", basic or "")
    info["pathlen"] = int(pathlen.group(1)) if pathlen else None

    eku = _extension_body(text, "X509v3 Extended Key Usage")
    info["extended_key_usage"] = sorted(
        EKU_NAMES.get(item.strip(), item.strip()) for item in (eku or "").split(",") if item.strip()
    )
    key_usage = _extension_body(text, "X509v3 Key Usage")
    info["key_usage"] = sorted(item.strip() for item in (key_usage or "").split(",") if item.strip())

    sans: dict[str, list[str]] = {"dns": [], "ip": [], "uri": []}
    san_body = _extension_body(text, "X509v3 Subject Alternative Name") or ""
    for item in san_body.split(","):
        item = item.strip()
        if item.startswith("DNS:"):
            sans["dns"].append(item[4:].lower())
        elif item.startswith("IP Address:"):
            sans["ip"].append(item[len("IP Address:"):].strip().lower())
        elif item.startswith("URI:"):
            sans["uri"].append(item[4:])
    info["san"] = sans
    return info


def _cn(name: str) -> str | None:
    # RFC 2253 order: CN=x,O=y. Commas inside values are escaped as \, .
    for part in re.split(r"(?<!\\),", name):
        if part.strip().upper().startswith("CN="):
            return part.strip()[3:].replace("\\,", ",")
    return None


def _extension_body(text: str, header: str) -> str | None:
    match = re.search(re.escape(header) + r":(?: critical)?\s*\n\s*(.+?)\n", text)
    return match.group(1).strip() if match else None


def cert_info(path: str | Path) -> dict[str, Any]:
    pems = split_bundle(path)
    if not pems:
        raise ValueError(f"no certificate in {path}")
    info = cert_info_from_pem(pems[0])
    info["chain_length_in_file"] = len(pems)
    return info


def verify_chain(cert_path: str | Path, ca_path: str | Path, purpose: str | None) -> tuple[bool, str]:
    """True when cert_path chains to ca_path (and only ca_path, no system store)."""
    cmd = ["openssl", "verify", "-no-CApath", "-no-CAstore", "-CAfile", str(ca_path)]
    pems = split_bundle(cert_path)
    untrusted = None
    try:
        if len(pems) > 1:
            # Intermediates shipped with the leaf are passed as untrusted helpers, from
            # a private temporary file: never beside the certificate, whose folder may
            # be read-only (a mounted Secret) or inside the repository.
            handle, untrusted = tempfile.mkstemp(prefix="tls-untrusted-", suffix=".pem")
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                stream.write("\n".join(pems[1:]) + "\n")
            cmd += ["-untrusted", untrusted]
        if purpose:
            cmd += ["-purpose", purpose]
        code, out, err = run(cmd, stdin=pems[0])
    finally:
        if untrusted:
            try:
                os.unlink(untrusted)
            except OSError:
                pass
    message = (out + err).strip().splitlines()
    return code == 0 and "OK" in out, message[-1] if message else ""


def key_matches_cert(key_path: str | Path, cert_path: str | Path) -> bool:
    """True when the key file holds the private half of the certificate's public key.
    openssl derives both public halves; the key's content never enters Python. An
    encrypted or unreadable key is "no match" (it is never prompted for)."""
    code_key, from_key, _ = run(["openssl", "pkey", "-in", str(key_path), "-pubout", "-passin", "pass:"], stdin="")
    code_cert, from_cert, _ = run(["openssl", "x509", "-in", str(cert_path), "-noout", "-pubkey"], stdin="")
    return code_key == 0 and code_cert == 0 and bool(from_key.strip()) and from_key.strip() == from_cert.strip()


def days_left(info: dict[str, Any], moment: dt.datetime | None = None) -> float:
    moment = moment or now_utc()
    end = _parse_iso(info["not_after"])
    return (end - moment).total_seconds() / 86400


# Seconds kept between a leaf's end and its CA's end. Lifetimes are whole days
# counted from the moment of signing, which comes after the moment of measuring.
SIGNING_MARGIN_SECONDS = 300


def leaf_days_within(info: dict[str, Any], moment: dt.datetime | None = None) -> int:
    """Whole days a leaf signed now may live and still end before this CA does."""
    seconds = days_left(info, moment) * 86400 - SIGNING_MARGIN_SECONDS
    return max(0, int(seconds // 86400))


def lifetime_days(info: dict[str, Any]) -> float:
    return (_parse_iso(info["not_after"]) - _parse_iso(info["not_before"])).total_seconds() / 86400


def name_covered(name: str, sans: dict[str, list[str]]) -> bool:
    name = name.lower().strip()
    if re.fullmatch(r"[0-9.]+|[0-9a-f:]+", name) and ("." in name or ":" in name):
        return _normalise_ip(name) in {_normalise_ip(ip) for ip in sans.get("ip", [])}
    for dns in sans.get("dns", []):
        if dns == name:
            return True
        if dns.startswith("*.") and "." in name and name.split(".", 1)[1] == dns[2:]:
            return True
    return False


def _normalise_ip(text: str) -> str:
    import ipaddress

    try:
        return str(ipaddress.ip_address(text.strip()))
    except ValueError:
        return text.strip().lower()


def key_allowed(key_type: str) -> bool:
    if key_type in ("EC P-256", "EC P-384"):
        return True
    match = re.fullmatch(r"RSA (\d+)", key_type or "")
    return bool(match and int(match.group(1)) >= 2048)
