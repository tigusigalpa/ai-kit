"""Capture manifest evidence for an installed project's verified context."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install


PROJECT_FACTS = "ai-kit/project.json"


def target_root(target: Path) -> Path:
    target = target.absolute()
    if install.is_link(target):
        raise ValueError("Refusing a linked project root")
    target = target.resolve()
    if not target.is_dir():
        raise ValueError("Project must be an existing directory")
    return target


def snapshot_plan(target: Path) -> dict:
    """Prepare, but do not write, a manifest-evidence snapshot."""
    target = target_root(target)
    path = install.safe_path(target, PROJECT_FACTS)
    if not path.is_file():
        raise ValueError("Missing ai-kit/project.json; install AI-KIT before recording context evidence")
    value = install.read_json(path, {})
    if type(value.get("schema")) is not int or value["schema"] != 1:
        raise ValueError("Unsupported project.json schema; expected schema 1")
    if not isinstance(value.get("modules"), list) or any(not isinstance(module, dict) for module in value["modules"]):
        raise ValueError("project.json modules must be a list of objects")
    facts = install.detect_facts(target)
    updated = dict(value)
    updated["evidence"] = install.project_fact_evidence(target, facts)
    data = (json.dumps(updated, indent=2) + "\n").encode("utf-8")
    old = path.read_bytes()
    return {"target": str(target), "path": PROJECT_FACTS, "old": old, "data": data,
            "changed": old != data, "detected_modules": [module["path"] for module in facts["modules"]]}


def apply_snapshot(plan: dict) -> bool:
    target = Path(plan["target"])
    path = install.safe_path(target, plan["path"])
    actual = path.read_bytes() if path.exists() else None
    if actual != plan["old"]:
        raise ValueError("project.json changed after preview")
    if not plan["changed"]:
        return True
    install.atomic_write(path, plan["data"])
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    snapshot = sub.add_parser("snapshot", help="Preview or record current manifest evidence in project.json")
    snapshot.add_argument("project", type=Path)
    snapshot.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan = snapshot_plan(args.project)
        print(json.dumps({"target": plan["target"], "preview": not args.apply, "changed": plan["changed"],
                          "path": plan["path"], "detected_modules": plan["detected_modules"]}, indent=2))
        if args.apply:
            apply_snapshot(plan)
        return 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Context snapshot refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
