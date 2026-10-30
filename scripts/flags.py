"""Print the machine-readable `aikit install` option schema for documentation and configurators."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install

SCHEMA_PATH = "integrations/installer-flags.json"


def render(schema: dict) -> str:
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="Write the schema to this file with LF line endings instead of printing it")
    args = parser.parse_args(argv)
    text = render(install.flag_schema())
    if args.output is None:
        sys.stdout.write(text)
        return 0
    if install.is_link(args.output):
        print(f"Refusing a linked output path: {args.output}", file=sys.stderr)
        return 1
    install.atomic_write(args.output, text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
