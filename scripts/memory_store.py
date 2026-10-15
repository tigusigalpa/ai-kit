"""Bounded local I/O and immutable artifacts for dialogue memory."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat

import install

LIMIT = 16 * 1024 * 1024
MARKER = {"schema": 1, "kind": "aikit-memory-workspace"}


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(encode(value)).hexdigest()


def guarded(path: Path) -> Path:
    path = path.absolute()
    for parent in (path, *path.parents):
        if install.is_link(parent):
            raise ValueError("Linked paths and junctions are not supported")
        if parent != path and parent.exists() and not parent.is_dir():
            raise ValueError("Path parent is not a directory")
    return path.resolve()


def read_bytes(path: Path, *, limit: int = LIMIT) -> bytes:
    path = guarded(path)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError("Expected a bounded regular file")
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Input exceeds the byte limit")
    return data


def decode(data: bytes) -> object:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON keys are not supported")
            result[key] = value
        return result

    def constant(_):
        raise ValueError("Nonfinite JSON numbers are not supported")

    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)


def read_json(path: Path) -> object:
    return decode(read_bytes(path))


def root(path: Path, *, existing: bool = True) -> Path:
    path = guarded(path)
    if path.exists() and not path.is_dir():
        raise ValueError("Workspace must be a directory")
    marker = install.safe_path(path, "workspace.json")
    if marker.exists():
        value = read_json(marker)
        if not isinstance(value, dict) or type(value.get("schema")) is not int or value != MARKER:
            raise ValueError("Unknown workspace marker")
    elif existing or (path.exists() and any(path.iterdir())):
        raise ValueError("Use a new/empty directory or an AI-KIT memory workspace")
    return path


def artifact(workspace: Path, relative: str) -> object:
    return read_json(install.safe_path(root(workspace), relative))


def write(workspace: Path, files: dict[str, bytes], *, apply: bool) -> list[str]:
    """Preview first; exclusively create files, preserve existing bytes, allow identical reruns."""
    workspace = root(workspace, existing=False)
    if "workspace.json" in files:
        raise ValueError("Workspace marker is managed internally")
    files = {"workspace.json": encode(MARKER), **files}
    writes = []
    for relative, data in files.items():
        if len(data) > LIMIT:
            raise ValueError("Artifact exceeds the byte limit")
        target = install.safe_path(workspace, relative)
        if target.exists():
            if target.stat().st_nlink != 1 or read_bytes(target) != data:
                raise ValueError("Existing artifact differs or is hard-linked; use a new name/workspace")
        else:
            writes.append(relative)
    if not apply:
        return writes
    for relative in writes:
        target = install.safe_path(guarded(workspace), relative)
        missing = []
        parent = target.parent
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        for parent in reversed(missing):
            guarded(parent)
            parent.mkdir(mode=0o700, exist_ok=True)
        # O_EXCL refuses a file/link created after planning, rather than replacing it.
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        identity = os.fstat(descriptor)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(files[relative])
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            current = target.lstat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                target.unlink()
            raise
    return writes
