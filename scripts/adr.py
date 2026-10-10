"""Scaffold a decision record (ADR) from the project's ADR template."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "decision"


def next_number(adr_dir: Path) -> int:
    numbers = [0]
    for path in adr_dir.glob("*.md"):
        match = re.match(r"(\d+)-", path.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers) + 1


def scaffold(title: str, root: Path) -> Path:
    adr_dir = root / "docs" / "adr"
    template_path = adr_dir / "0000-template.md"
    if not template_path.is_file():
        raise ValueError(f"Missing ADR template: {template_path}")
    number = next_number(adr_dir)
    text = template_path.read_text(encoding="utf-8")
    content = (text
               .replace("# ADR-NNNN: Title", f"# ADR-{number:04d}: {title}", 1)
               .replace("use the verified decision date", date.today().isoformat(), 1)
               .replace("proposed / accepted / superseded", "proposed", 1))
    destination = adr_dir / f"{number:04d}-{slugify(title)}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(content)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    new_parser = sub.add_parser("new", help="Create a new ADR from the template")
    new_parser.add_argument("title")
    new_parser.add_argument("--root", type=Path, default=Path.cwd(),
                            help="Project root (default: current directory)")
    args = parser.parse_args(argv)
    try:
        path = scaffold(args.title, args.root.absolute())
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"ADR creation refused: {exc}", file=sys.stderr)
        return 1
    print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
