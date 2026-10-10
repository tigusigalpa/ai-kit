"""Unified AI-KIT command-line entry point (`aikit`)."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
__version__ = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
sys.path.insert(0, str(ROOT / "scripts"))

# Subcommand -> (module, prefix to prepend to the remaining arguments, or None).
_COMMANDS = {
    "install": ("install", None),
    "doctor": ("doctor", None),
    "route": ("router", "route"),
    "configure": ("router", "configure"),
    "metrics": ("metrics", None),
    "adr": ("adr", None),
    "changelog": ("changelog", None),
    "check": ("check_kit", None),
    "docker": ("docker_test_usage", None),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aikit", description=__doc__)
    parser.add_argument("command", nargs="?", choices=sorted(_COMMANDS),
                        help="AI-KIT command to run")
    args, rest = parser.parse_known_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    module_name, prefix = _COMMANDS[args.command]
    module = __import__(module_name)
    forwarded = ([prefix] + rest) if prefix else rest
    return module.main(forwarded)


if __name__ == "__main__":
    raise SystemExit(main())
