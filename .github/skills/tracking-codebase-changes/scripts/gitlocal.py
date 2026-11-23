#!/usr/bin/env python3
"""Read a local Git repository's history from its `.git` folder, without running `git`.

Read-only and offline: opens files under the Git directory and nothing else. Supports
loose objects, pack files (version 2 index, offset and reference deltas), packed refs,
linked worktrees (`.git` file with `gitdir:`), and object alternates. Refuses SHA-256
repositories and does not follow submodules. Standard library only.

Used by track.py; can also be run to check that a repository is readable:

  python3 -I gitlocal.py --repo . [--rev HEAD] [--log 10]
"""

from __future__ import annotations

import argparse
import bisect
import os
import re
import struct
import sys
import zlib

TYPES = {1: b"commit", 2: b"tree", 3: b"blob", 4: b"tag"}
OFS_DELTA, REF_DELTA = 6, 7
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class GitError(Exception):
    pass


def _read(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def _text(path: str) -> str:
    return _read(path).decode("utf-8", "replace").strip()


class Pack:
    """One pack file and its version 2 index."""

    def __init__(self, idx_path: str):
        self.idx_path = idx_path
        self.pack_path = idx_path[:-4] + ".pack"
        data = _read(idx_path)
        if data[:4] != b"\xfftOc" or struct.unpack(">I", data[4:8])[0] != 2:
            raise GitError("unsupported pack index (only version 2): " + idx_path)
        fanout = struct.unpack(">256I", data[8:8 + 1024])
        self.count = fanout[255]
        start = 8 + 1024
        self.names = [data[start + 20 * i:start + 20 * (i + 1)] for i in range(self.count)]
        offsets_at = start + 20 * self.count + 4 * self.count
        self.small = struct.unpack(">%dI" % self.count, data[offsets_at:offsets_at + 4 * self.count])
        self.large_at = offsets_at + 4 * self.count
        self.idx = data
        self._pack = None

    def offset_of(self, raw: bytes):
        i = bisect.bisect_left(self.names, raw)
        if i == self.count or self.names[i] != raw:
            return None
        off = self.small[i]
        if off & 0x80000000:
            j = off & 0x7FFFFFFF
            off = struct.unpack(">Q", self.idx[self.large_at + 8 * j:self.large_at + 8 * j + 8])[0]
        return off

    def with_prefix(self, prefix: bytes):
        i = bisect.bisect_left(self.names, prefix)
        found = []
        while i < self.count and self.names[i].startswith(prefix):
            found.append(self.names[i])
            i += 1
        return found

    @property
    def pack(self) -> bytes:
        if self._pack is None:
            self._pack = _read(self.pack_path)
            if self._pack[:4] != b"PACK":
                raise GitError("not a pack file: " + self.pack_path)
        return self._pack


def _inflate(data: bytes, at: int, size: int) -> bytes:
    out = zlib.decompressobj().decompress(data[at:at + max(size * 2 + 1024, 4096)], size)
    if len(out) < size:  # rare: compressed data longer than the guess
        out = zlib.decompressobj().decompress(data[at:], size)
    return out


def _varint(data: bytes, pos: int):
    value, shift = 0, 0
    while True:
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            return value, pos


def apply_delta(base: bytes, delta: bytes) -> bytes:
    src_size, pos = _varint(delta, 0)
    dst_size, pos = _varint(delta, pos)
    if src_size != len(base):
        raise GitError("delta base size mismatch")
    out = bytearray()
    while pos < len(delta):
        op = delta[pos]
        pos += 1
        if op & 0x80:
            offset = size = 0
            for bit in range(4):
                if op & (1 << bit):
                    offset |= delta[pos] << (8 * bit)
                    pos += 1
            for bit in range(3):
                if op & (0x10 << bit):
                    size |= delta[pos] << (8 * bit)
                    pos += 1
            out += base[offset:offset + (size or 0x10000)]
        elif op:
            out += delta[pos:pos + op]
            pos += op
        else:
            raise GitError("invalid delta opcode 0")
    if len(out) != dst_size:
        raise GitError("delta result size mismatch")
    return bytes(out)


class Repo:
    def __init__(self, work_tree: str):
        self.work_tree = os.path.abspath(work_tree)
        dotgit = os.path.join(self.work_tree, ".git")
        if os.path.isfile(dotgit):
            line = _text(dotgit)
            if not line.startswith("gitdir:"):
                raise GitError(".git file without gitdir: " + dotgit)
            gitdir = line[len("gitdir:"):].strip()
            self.git_dir = os.path.normpath(os.path.join(self.work_tree, gitdir))
        elif os.path.isdir(dotgit):
            self.git_dir = dotgit
        else:
            raise GitError("no .git folder or file in " + self.work_tree)
        common = os.path.join(self.git_dir, "commondir")
        self.common_dir = os.path.normpath(os.path.join(self.git_dir, _text(common))) if os.path.isfile(common) else self.git_dir
        config = os.path.join(self.common_dir, "config")
        if os.path.isfile(config) and re.search(r"objectformat\s*=\s*sha256", _text(config), re.I):
            raise GitError("SHA-256 repositories are not supported")
        self.object_dirs = [os.path.join(self.common_dir, "objects")]
        alternates = os.path.join(self.object_dirs[0], "info", "alternates")
        if os.path.isfile(alternates):
            for line in _text(alternates).splitlines():
                if line.strip() and not line.startswith("#"):
                    self.object_dirs.append(os.path.normpath(os.path.join(self.object_dirs[0], line.strip())))
        self.packs = []
        for objects in self.object_dirs:
            pack_dir = os.path.join(objects, "pack")
            if os.path.isdir(pack_dir):
                self.packs += [Pack(os.path.join(pack_dir, n)) for n in sorted(os.listdir(pack_dir))
                               if n.endswith(".idx") and os.path.isfile(os.path.join(pack_dir, n[:-4] + ".pack"))]
        shallow = os.path.join(self.common_dir, "shallow")
        self.shallow = set(_text(shallow).split()) if os.path.isfile(shallow) else set()
        self._cache = {}

    # ---------- objects ----------

    def read(self, sha: str):
        """(type, content) of an object."""
        if sha in self._cache:
            return self._cache[sha]
        for objects in self.object_dirs:
            path = os.path.join(objects, sha[:2], sha[2:])
            if os.path.isfile(path):
                raw = zlib.decompress(_read(path))
                head, _, body = raw.partition(b"\x00")
                kind = head.split(b" ")[0]
                return self._remember(sha, (kind, body))
        raw = bytes.fromhex(sha)
        for pack in self.packs:
            off = pack.offset_of(raw)
            if off is not None:
                return self._remember(sha, self._from_pack(pack, off))
        raise GitError("object not found: %s" % sha)

    def _remember(self, sha, value):
        if len(self._cache) > 2048:
            self._cache.clear()
        self._cache[sha] = value
        return value

    def _from_pack(self, pack: Pack, off: int, depth: int = 0):
        if depth > 64:
            raise GitError("delta chain too long")
        data = pack.pack
        byte = data[off]
        kind = (byte >> 4) & 7
        size = byte & 0x0F
        pos, shift = off + 1, 4
        while byte & 0x80:
            byte = data[pos]
            pos += 1
            size |= (byte & 0x7F) << shift
            shift += 7
        if kind in TYPES:
            return TYPES[kind], _inflate(data, pos, size)
        if kind == OFS_DELTA:
            byte = data[pos]
            pos += 1
            back = byte & 0x7F
            while byte & 0x80:
                byte = data[pos]
                pos += 1
                back = ((back + 1) << 7) | (byte & 0x7F)
            base_kind, base = self._from_pack(pack, off - back, depth + 1)
        elif kind == REF_DELTA:
            base_kind, base = self.read(data[pos:pos + 20].hex())
            pos += 20
        else:
            raise GitError("unknown pack object type %d" % kind)
        return base_kind, apply_delta(base, _inflate(data, pos, size))

    # ---------- refs and revisions ----------

    def _ref(self, name: str, depth: int = 0):
        if depth > 8:
            raise GitError("symbolic ref loop: " + name)
        for base in (self.git_dir, self.common_dir):
            path = os.path.join(base, *name.split("/"))
            if os.path.isfile(path):
                value = _text(path)
                if value.startswith("ref:"):
                    return self._ref(value[4:].strip(), depth + 1)
                return value if HEX40.match(value) else None
        packed = os.path.join(self.common_dir, "packed-refs")
        if os.path.isfile(packed):
            for line in _text(packed).splitlines():
                parts = line.split()
                if len(parts) == 2 and parts[1] == name and HEX40.match(parts[0]):
                    return parts[0]
        return None

    def branch(self):
        """Name of the checked-out branch, or None when HEAD is detached."""
        value = _text(os.path.join(self.git_dir, "HEAD"))
        return value[len("ref: refs/heads/"):] if value.startswith("ref: refs/heads/") else None

    def _peel(self, sha: str) -> str:
        for _ in range(8):
            kind, body = self.read(sha)
            if kind != b"tag":
                return sha
            sha = body.split(b"\n", 1)[0].split()[1].decode()
        raise GitError("tag chain too long")

    def resolve(self, rev: str) -> str:
        """A commit id from HEAD, a full or short id, a branch, tag or remote name, with ~N or ^ suffixes."""
        match = re.match(r"^(.*?)((?:~\d*|\^1?)*)$", rev.strip())
        name, suffix = match.group(1), match.group(2)
        sha = None
        if name == "HEAD" or name == "":
            sha = self._ref("HEAD")
        elif HEX40.match(name.lower()):
            sha = name.lower()
        else:
            for candidate in (name, "refs/" + name, "refs/heads/" + name, "refs/tags/" + name, "refs/remotes/" + name):
                sha = self._ref(candidate)
                if sha:
                    break
            if sha is None and re.match(r"^[0-9a-fA-F]{4,39}$", name):
                sha = self._short(name.lower())
        if sha is None:
            raise GitError("unknown revision: " + rev)
        sha = self._peel(sha)
        for step in re.findall(r"~\d*|\^1?", suffix):
            count = int(step[1:] or 1) if step.startswith("~") else 1
            for _ in range(count):
                parents = self.commit(sha)["parents"]
                if not parents:
                    raise GitError("%s has no parent" % sha[:12])
                sha = parents[0]
        return sha

    def _short(self, prefix: str):
        found = set()
        for objects in self.object_dirs:
            folder = os.path.join(objects, prefix[:2])
            if os.path.isdir(folder):
                found |= {prefix[:2] + n for n in os.listdir(folder) if (prefix[:2] + n).startswith(prefix)}
        raw = bytes.fromhex(prefix[: len(prefix) // 2 * 2])
        for pack in self.packs:
            found |= {n.hex() for n in pack.with_prefix(raw) if n.hex().startswith(prefix)}
        if len(found) > 1:
            raise GitError("ambiguous short id: " + prefix)
        return found.pop() if found else None

    # ---------- commits and trees ----------

    def commit(self, sha: str) -> dict:
        kind, body = self.read(sha)
        if kind != b"commit":
            raise GitError("%s is a %s, not a commit" % (sha[:12], kind.decode()))
        head, _, message = body.partition(b"\n\n")
        info = {"sha": sha, "tree": None, "parents": [], "time": 0, "message": message.decode("utf-8", "replace")}
        for line in head.split(b"\n"):
            if line.startswith(b"tree "):
                info["tree"] = line[5:].decode()
            elif line.startswith(b"parent "):
                info["parents"].append(line[7:].decode())
            elif line.startswith(b"committer "):
                match = re.search(rb"> (\d+) [+-]\d{4}$", line)
                info["time"] = int(match.group(1)) if match else 0
        if sha in self.shallow:
            info["parents"] = []
        info["subject"] = info["message"].strip().split("\n", 1)[0] if info["message"].strip() else ""
        return info

    def tree_files(self, tree_sha: str, prefix: str = "") -> dict:
        """path -> blob id for every regular file under the tree (no symbolic links, no submodules)."""
        out = {}
        _kind, body = self.read(tree_sha)
        pos = 0
        while pos < len(body):
            space = body.index(b" ", pos)
            nul = body.index(b"\x00", space)
            mode = body[pos:space]
            name = body[space + 1:nul].decode("utf-8", "replace")
            sha = body[nul + 1:nul + 21].hex()
            pos = nul + 21
            path = prefix + name
            if mode in (b"40000", b"040000"):
                out.update(self.tree_files(sha, path + "/"))
            elif mode.startswith(b"100"):
                out[path] = sha
        return out

    def _entries(self, tree_sha):
        if tree_sha is None:
            return {}
        _kind, body = self.read(tree_sha)
        out, pos = {}, 0
        while pos < len(body):
            space = body.index(b" ", pos)
            nul = body.index(b"\x00", space)
            out[body[space + 1:nul].decode("utf-8", "replace")] = (body[pos:space], body[nul + 1:nul + 21].hex())
            pos = nul + 21
        return out

    def diff_trees(self, old_tree, new_tree, prefix: str = "") -> dict:
        """path -> (old blob or None, new blob or None) for regular files that differ; equal subtrees are skipped."""
        if old_tree == new_tree:
            return {}
        out = {}
        old, new = self._entries(old_tree), self._entries(new_tree)
        for name in sorted(set(old) | set(new)):
            a, b = old.get(name), new.get(name)
            if a == b:
                continue
            a_dir = a is not None and a[0] in (b"40000", b"040000")
            b_dir = b is not None and b[0] in (b"40000", b"040000")
            if a_dir or b_dir:
                out.update(self.diff_trees(a[1] if a_dir else None, b[1] if b_dir else None, prefix + name + "/"))
            a_file = a[1] if a is not None and a[0].startswith(b"100") else None
            b_file = b[1] if b is not None and b[0].startswith(b"100") else None
            if a_file != b_file:
                out[prefix + name] = (a_file, b_file)
        return out

    def blob(self, sha: str) -> bytes:
        kind, body = self.read(sha)
        if kind != b"blob":
            raise GitError("%s is not a blob" % sha[:12])
        return body

    def first_parent_chain(self, head: str, stop: str, limit: int = 5000, not_before: int = 0):
        """Commits from head back along first parents until stop (excluded). None when stop is not reached,
        or when the walk passes commits older than not_before (seconds since the epoch)."""
        chain, sha = [], head
        while sha and sha != stop:
            if len(chain) >= limit:
                return None
            info = self.commit(sha)
            if not_before and info["time"] < not_before:
                return None
            chain.append(info)
            sha = info["parents"][0] if info["parents"] else None
        return chain if sha == stop else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", default="HEAD")
    parser.add_argument("--log", type=int, default=5)
    args = parser.parse_args()
    try:
        repo = Repo(args.repo)
        sha = repo.resolve(args.rev)
        print("branch: %s" % (repo.branch() or "(detached)"))
        info = repo.commit(sha)
        for _ in range(args.log):
            print("%s %s" % (info["sha"][:12], info["subject"][:100]))
            if not info["parents"]:
                break
            info = repo.commit(info["parents"][0])
        print("files at %s: %d" % (sha[:12], len(repo.tree_files(repo.commit(sha)["tree"]))))
    except (GitError, OSError, zlib.error, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
