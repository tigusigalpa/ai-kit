"""Bounded local Git working-tree fingerprints for explicit task checks."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile

if __package__:
    from . import install
else:
    import install

MAX_FILES = 20000
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
RUNTIME = {".tasks", ".metrics", ".memory", ".orchestration", ".design", ".upstream-cache"}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def git(project: Path, *args: str, optional: bool = False) -> bytes:
    # Local discovery must not use an inherited alternate repository/index or a configured fsmonitor.
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                       GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    command = ["git", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
               "-C", str(project), *args]
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(command, env=environment, stdin=subprocess.DEVNULL,
                                stdout=output, stderr=subprocess.DEVNULL, timeout=30)
        if result.returncode:
            if optional:
                return b""
            raise ValueError("Git source discovery failed; use a readable Git working-tree root")
        output.seek(0)
        data = output.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise ValueError("Git source listing exceeds the inspection limit")
    return data


def source_path(value: str) -> str:
    parts = PurePosixPath(value).parts
    if (not parts or value.startswith("/") or "\\" in value or ":" in value or
            any(p in {".", "..", ".git"} for p in parts) or
            any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError("Unsupported source path")
    return value


def excluded(value: str) -> bool:
    parts = PurePosixPath(value).parts
    return len(parts) >= 2 and parts[0] == "ai-kit" and parts[1] in RUNTIME


def secret(value: str) -> bool:
    parts = PurePosixPath(value).parts
    return any(p in {".env", ".envrc", "auth.json", ".netrc", ".pypirc", ".secrets", ".aws"} or
               (p.startswith(".env.") and not p.endswith((".example", ".dist"))) or
               p.lower().endswith((".pem", ".p12", ".pfx", ".private.key")) or
               p.startswith(("id_rsa", "id_ed25519")) for p in parts)


def snapshot(project: Path) -> dict:
    """Hash HEAD, index entries and actual files, including deletions and nonignored untracked files."""
    if install.is_link(project / ".git"):
        raise ValueError("Linked Git metadata is unsupported")
    top = git(project, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    if Path(top).resolve() != project:
        raise ValueError("Task checks require the Git working-tree root, not a nested module")
    head = git(project, "rev-parse", "--verify", "HEAD", optional=True).decode("ascii").strip() or None
    if head is not None and not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", head):
        raise ValueError("Invalid Git revision")
    tracked: dict[str, tuple[str, str]] = {}
    for item in git(project, "ls-files", "--stage", "-z").split(b"\0"):
        if not item:
            continue
        header, name = item.split(b"\t", 1)
        mode, oid, stage = header.decode("ascii").split()
        path = source_path(name.decode("utf-8"))
        if excluded(path):
            continue
        if stage != "0" or mode not in {"100644", "100755"}:
            raise ValueError("Resolve unmerged entries; linked files and submodules are unsupported")
        tracked[path] = (mode, oid)
    others = {source_path(p.decode("utf-8")) for p in
              git(project, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if p}
    paths = sorted(set(tracked) | {p for p in others if not excluded(p)})
    if len(paths) > MAX_FILES:
        raise ValueError("Too many source files for a task fingerprint")
    records = []
    total = 0
    folded = set()
    for name in paths:
        if name.casefold() in folded:
            raise ValueError("Case-colliding source paths are unsupported")
        folded.add(name.casefold())
        if secret(name):
            raise ValueError("Source contains a nonignored credential path; review Git visibility first")
        path = install.safe_path(project, name)
        index = tracked.get(name)
        if not path.exists():
            if index is None:
                raise ValueError("Source changed during fingerprinting")
            records.append([name, index, "missing"])
            continue
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError("Source must contain only regular, unlinked files")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        digest = hashlib.sha256()
        size = 0
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
                raise ValueError("Source file is nonregular or exceeds the byte limit")
            while data := stream.read(65536):
                size += len(data)
                total += len(data)
                if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                    raise ValueError("Source exceeds fingerprint byte limits")
                digest.update(data)
            after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError("Source changed while a file was being fingerprinted")
        executable = bool(after.st_mode & 0o111) if os.name != "nt" else bool(index and index[0] == "100755")
        records.append([name, index, executable, size, digest.hexdigest()])
    return {"schema": 1, "head": head, "files": len(records), "bytes": total,
            "digest": hashlib.sha256(canonical({"head": head, "files": records})).hexdigest()}
