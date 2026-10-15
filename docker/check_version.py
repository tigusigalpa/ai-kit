"""Refuse an image version label that differs from its bundled AI-KIT source."""
from __future__ import annotations

import os
from pathlib import Path
import sys


def check_version(path: Path, expected: str | None) -> str:
    actual = path.read_text(encoding="utf-8").strip()
    if not expected:
        raise ValueError("Pass --build-arg AIKIT_VERSION with the value from VERSION")
    if expected != actual:
        raise ValueError(f"Image version {expected!r} does not match bundled VERSION {actual!r}")
    return actual


def main() -> int:
    try:
        version = check_version(Path("VERSION"), os.environ.get("AIKIT_VERSION"))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Building AI-KIT " + version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
