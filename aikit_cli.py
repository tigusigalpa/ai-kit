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
    "context": ("context", None),
    "memory": ("memory", None),
    "adapters": ("adapters", None),
    "route": ("router", "route"),
    "configure": ("router", "configure"),
    "providers": ("router", "providers"),
    "metrics": ("metrics", None),
    "evaluate": ("evaluate", None),
    "benchmark": ("benchmark", None),
    "adr": ("adr", None),
    "changelog": ("changelog", None),
    "check": ("check_kit", None),
    "docker": ("docker_test_usage", None),
}


def _load(module_name: str):
    """Prefer the installed package so modules are not duplicated as bare names."""
    try:
        return __import__("aikit.scripts." + module_name, fromlist=["main"])
    except ImportError:
        return __import__(module_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aikit", description=__doc__)
    parser.add_argument("command", nargs="?", choices=sorted(_COMMANDS),
                        help="AI-KIT command to run")
    values = list(argv) if argv is not None else sys.argv[1:]
    # Parse only the dispatcher command; child --help and flags belong to the child parser.
    args = parser.parse_args(values[:1])
    rest = values[1:]
    if args.command is None:
        parser.print_help()
        return 2
    module_name, prefix = _COMMANDS[args.command]
    module = _load(module_name)
    forwarded = ([prefix] + rest) if prefix else rest
    return module.main(forwarded)


if __name__ == "__main__":
    raise SystemExit(main())
