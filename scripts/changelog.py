"""Append a changelog entry to a project's CHANGELOG.md."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

HEADING = "## Unreleased"


def add_entry(root: Path, message: str) -> Path:
    path = root / "CHANGELOG.md"
    if not path.is_file():
        raise ValueError(f"Missing changelog: {path}")
    text = path.read_text(encoding="utf-8")
    bullet = f"- {message.strip()}\n"
    index = text.find(HEADING)
    if index == -1:
        lines = text.splitlines(keepends=True)
        insert_at = 0
        for position, line in enumerate(lines):
            if line.startswith("# "):
                insert_at = position + 1
                break
        lines[insert_at:insert_at] = ["\n", HEADING, "\n", bullet]
        path.write_text("".join(lines), encoding="utf-8")
        return path
    after = index + len(HEADING)
    if text[after:after + 2] == "\r\n":
        after += 2
    elif text[after:after + 1] == "\n":
        after += 1
    path.write_text(text[:after] + bullet + text[after:], encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    add_parser = sub.add_parser("add", help="Append a bullet under the top changelog section")
    add_parser.add_argument("message")
    add_parser.add_argument("--root", type=Path, default=Path.cwd(),
                            help="Project root (default: current directory)")
    args = parser.parse_args(argv)
    try:
        path = add_entry(args.root.absolute(), args.message)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Changelog update refused: {exc}", file=sys.stderr)
        return 1
    print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
