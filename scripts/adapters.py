"""Review client adapters and retire only unchanged AI-KIT-owned adapter files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install


STATE_PATH = "ai-kit/.install-state.json"


def target_root(target: Path) -> Path:
    target = target.absolute()
    if install.is_link(target):
        raise ValueError("Refusing a linked project root")
    target = target.resolve()
    if not target.is_dir():
        raise ValueError("Project must be an existing directory")
    return target


def installed_state(target: Path, registry: dict) -> dict:
    path = install.safe_path(target, STATE_PATH)
    if not path.is_file():
        raise ValueError("No installer state found; is AI-KIT installed in this project?")
    state = install.read_json(path, {})
    install.validate_state(state, target, registry["names"])
    return state


def report(*, root: Path = install.ROOT, project: Path | None = None) -> dict:
    registry = install.load_agent_registry(root)
    state = None
    detected: dict[str, list[str]] = {}
    target = None
    if project is not None:
        target = target_root(project)
        state = installed_state(target, registry)
        detected = install.detect_agents(target, registry)
    clients = []
    for name in sorted(registry["names"]):
        metadata = registry["metadata"][name]
        managed = []
        blocked = []
        selected = None
        if state is not None:
            selected = name in state["agents"]
            for relative in sorted(state["files"]):
                if install.adapter_owner(relative, registry) != name:
                    continue
                try:
                    exists = install.safe_path(target, relative).is_file()
                except (ValueError, NotADirectoryError):
                    blocked.append(relative)
                    continue
                if exists:
                    managed.append(relative)
        clients.append({"client": name, "documentation_status": metadata["status"],
                        "verified_documentation_date": metadata["verified_documentation_date"],
                        "sources": metadata["sources"], "activation": metadata["activation"],
                        "selected": selected, "detected": detected.get(name, []), "managed_paths": managed,
                        "blocked_paths": blocked})
    return {"project": str(target) if target is not None else None, "clients": clients,
            "note": "Documentation status does not prove native client activation."}


def retirement_plan(project: Path, agent: str, *, root: Path = install.ROOT) -> dict:
    target = target_root(project)
    registry = install.load_agent_registry(root)
    if agent not in registry["names"]:
        raise ValueError("Unknown client: " + agent)
    state = installed_state(target, registry)
    if agent in state["agents"] and len(state["agents"]) == 1:
        raise ValueError("Cannot retire the last selected client; install a replacement selection first")
    records = state["files"]
    removals, conflicts, absent = [], [], []
    for relative in sorted(records):
        if install.adapter_owner(relative, registry) != agent:
            continue
        try:
            path = install.safe_path(target, relative)
        except (ValueError, NotADirectoryError):
            conflicts.append(relative)
            continue
        if not path.exists():
            absent.append(relative)
            continue
        if not path.is_file():
            conflicts.append(relative)
            continue
        data = path.read_bytes()
        record = records[relative]
        if record.get("local_adaptation") or install.digest(data) != record.get("installed_hash"):
            conflicts.append(relative)
            continue
        removals.append({"path": relative, "old": data,
                         "backup": "ai-kit/.upstream-cache/retirements/" + install.digest(data) + "/" + relative})
    next_state = dict(state)
    next_files = dict(records)
    for item in removals:
        next_files.pop(item["path"], None)
    for relative in absent:
        next_files.pop(relative, None)
    next_state["files"] = next_files
    next_state["agents"] = [name for name in state["agents"] if name != agent]
    state_path = install.safe_path(target, STATE_PATH)
    old_state = state_path.read_bytes()
    state_data = (json.dumps(next_state, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return {"target": str(target), "agent": agent, "removals": removals, "conflicts": conflicts,
            "absent": absent, "state_path": STATE_PATH, "state_old": old_state, "state_data": state_data,
            "warnings": ((["Selected client will be deselected only after this explicit retirement."]
                          if agent in state["agents"] else []) +
                         (["Modified or non-file adapter paths require manual retirement."] if conflicts else []))}


def apply_retirement(plan: dict) -> bool:
    if plan["conflicts"]:
        return False
    target = Path(plan["target"])
    state_path = install.safe_path(target, plan["state_path"])
    if state_path.read_bytes() != plan["state_old"]:
        raise ValueError("Installer state changed after preview")
    for item in plan["removals"]:
        path = install.safe_path(target, item["path"])
        actual = path.read_bytes() if path.exists() and path.is_file() else None
        if actual != item["old"]:
            raise ValueError("Adapter changed after preview: " + item["path"])
    completed = []
    try:
        for item in plan["removals"]:
            path = install.safe_path(target, item["path"])
            backup = install.safe_path(target, item["backup"])
            if backup.exists():
                if backup.read_bytes() != item["old"]:
                    raise ValueError("Existing retirement backup differs: " + item["backup"])
            else:
                install.atomic_write(backup, item["old"])
            path.unlink()
            completed.append(item)
        install.atomic_write(state_path, plan["state_data"])
    except (OSError, ValueError):
        for item in reversed(completed):
            path = install.safe_path(target, item["path"])
            if not path.exists():
                install.atomic_write(path, item["old"])
        raise
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    report_parser = sub.add_parser("report", help="List client documentation status and installed adapter evidence")
    report_parser.add_argument("--project", type=Path)
    retire = sub.add_parser("retire", help="Preview or remove unchanged tracked files and explicitly deselect one client")
    retire.add_argument("project", type=Path)
    retire.add_argument("--agent", required=True)
    retire.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "report":
            print(json.dumps(report(project=args.project), indent=2))
            return 0
        plan = retirement_plan(args.project, args.agent)
        print(json.dumps({"target": plan["target"], "agent": plan["agent"], "preview": not args.apply,
                          "removals": [item["path"] for item in plan["removals"]],
                          "backups": [item["backup"] for item in plan["removals"]],
                          "conflicts": plan["conflicts"], "absent": plan["absent"],
                          "warnings": plan["warnings"]}, indent=2))
        if args.apply:
            apply_retirement(plan)
        return 2 if plan["conflicts"] else 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Adapter operation refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
