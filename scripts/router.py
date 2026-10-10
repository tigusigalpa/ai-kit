"""Offline model routing: deterministic recommendation and native configuration generation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install

ROOT = Path(__file__).resolve().parents[1]
ROLES = ("cheap", "work", "escalation")
LEVEL_MAP = {0: ("cheap", "low"), 1: ("cheap", "low"), 2: ("work", "medium"),
             3: ("work", "high"), 4: ("work", "xhigh"), 5: ("escalation", "high"),
             6: ("escalation", "max")}
_KEYWORDS = {
    5: ("prove theorem", "formal proof", "novel algorithm", "research", "frontier", "invent"),
    4: ("distributed", "consensus", "consistency", "replication", "sensitive data", "security audit",
        "compliance", "conflicting"),
    3: ("debug", "concurrency", "race", "deadlock", "architecture", "memory leak", "performance", "optimize"),
    0: ("classify", "categorize", "extract", "label", "tag", "trivial", "parse"),
    1: ("rename", "bump", "boilerplate", "lint", "typo", "format code", "simple", "mechanical"),
}
NOTE = ("Rule-based keyword recommendation; verify current model availability and your account "
        "tier before relying.")


def load_providers(providers_dir: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    if not providers_dir.is_dir():
        return result
    for path in sorted(providers_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Expected provider object: {path.name}")
        result[path.stem] = data
    return result


def validate_selection(selection: dict) -> None:
    if type(selection.get("schema")) is not int or selection["schema"] != 1:
        raise ValueError("Unsupported selection schema; expected schema 1")
    default = selection.get("default_provider")
    if default is not None and not isinstance(default, str):
        raise ValueError("Selection default_provider must be a string or null")
    roles = selection.get("roles")
    if not isinstance(roles, dict):
        raise ValueError("Selection roles must be an object")
    local = selection.get("local_models")
    if not isinstance(local, dict):
        raise ValueError("Selection local_models must be an object")
    for role in ROLES:
        spec = roles.get(role)
        if spec is not None and not isinstance(spec, (str, dict)):
            raise ValueError(f"Selection role {role} must be a string, object, or null")
        if isinstance(spec, dict):
            for field, value in spec.items():
                if field not in {"provider", "model", "effort"}:
                    raise ValueError(f"Unknown selection field {field} for role {role}")
                if value is not None and not isinstance(value, str):
                    raise ValueError(f"Selection {role}.{field} must be a string or null")
        model = local.get(role)
        if model is not None and not isinstance(model, str):
            raise ValueError(f"Selection local_models.{role} must be a string or null")


def load_selection(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"Missing selection file: {path}")
    selection = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(selection, dict):
        raise ValueError(f"Expected selection object: {path}")
    validate_selection(selection)
    return selection


def classify_level(text: str) -> int:
    lowered = text.lower()
    for level in (5, 4, 3, 0, 1):
        if any(keyword in lowered for keyword in _KEYWORDS[level]):
            return level
    return 2


def resolve_role(role: str, selection: dict, providers: dict[str, dict]) -> dict:
    spec = selection.get("roles", {}).get(role)
    if spec is None:
        spec = {}
    elif isinstance(spec, str):
        spec = {"provider": spec}
    provider_id = spec.get("provider") or selection.get("default_provider")
    if provider_id is None:
        return {"role": role, "provider": None, "model": None, "effort": None,
                "reasoning_mode": "standard", "service_tier": "standard", "tier": None,
                "resolved": False}
    if provider_id not in providers:
        raise ValueError(f"Unknown provider in selection: {provider_id}")
    config = providers[provider_id]
    if config.get("verification_status") == "pending":
        return {"role": role, "provider": provider_id, "model": None, "effort": None,
                "reasoning_mode": None, "service_tier": None, "tier": config.get("tier"),
                "resolved": False}
    role_spec = config.get("roles", {}).get(role, {})
    if not isinstance(role_spec, dict):
        role_spec = {}
    model = spec.get("model")
    if model is None and config.get("user_supplied_models"):
        model = selection.get("local_models", {}).get(role)
    if model is None:
        model = role_spec.get("model")
    effort = spec.get("effort") or role_spec.get("effort")
    return {"role": role, "provider": provider_id, "model": model, "effort": effort,
            "reasoning_mode": config.get("reasoning_mode", "standard"),
            "service_tier": config.get("service_tier_policy", "standard"),
            "tier": config.get("tier", "cloud"), "resolved": model is not None}


def classify(text: str) -> dict:
    level = classify_level(text)
    role, effort = LEVEL_MAP[level]
    return {"level": level, "role": role, "effort": effort}


def route_result(text: str, selection: dict, providers: dict[str, dict], *,
                 level: int | None = None, role: str | None = None, effort: str | None = None) -> dict:
    if level is None:
        level = classify_level(text)
    elif type(level) is not int or not 0 <= level <= 6:
        raise ValueError("Level must be an integer 0-6")
    default_role, default_effort = LEVEL_MAP.get(level, ("work", "medium"))
    role = role or default_role
    effort = effort or default_effort
    if role not in ROLES:
        raise ValueError("Role must be one of: " + ", ".join(ROLES))
    resolved = resolve_role(role, selection, providers)
    return {"level": level, "role": role, "effort": effort,
            "provider": resolved["provider"], "model": resolved["model"],
            "reasoning_mode": resolved["reasoning_mode"], "service_tier": resolved["service_tier"],
            "tier": resolved["tier"], "note": NOTE}


def _selection_and_providers(project: Path | None, root: Path) -> tuple[dict, dict[str, dict]]:
    if project is not None:
        base = project / "ai-kit" / "router"
    else:
        base = root / "template" / "ai-kit" / "router"
    selection = load_selection(base / "selection.json")
    providers = load_providers(base / "providers")
    return selection, providers


def resolved_document(selection: dict, providers: dict[str, dict]) -> dict:
    roles = {}
    for role in ROLES:
        resolved = resolve_role(role, selection, providers)
        roles[role] = {"provider": resolved["provider"], "model": resolved["model"],
                       "effort": resolved["effort"], "reasoning_mode": resolved["reasoning_mode"],
                       "service_tier": resolved["service_tier"], "tier": resolved["tier"]}
    return {"schema": 1, "roles": roles}


def aider_config(selection: dict, providers: dict[str, dict]) -> str | None:
    cheap = resolve_role("cheap", selection, providers)
    work = resolve_role("work", selection, providers)
    if not cheap["resolved"] or not work["resolved"]:
        return None
    lines = ["# Generated by AI-KIT router (scripts/router.py). Review before committing.",
             f'model: "{work["model"]}"', f'weak_model: "{cheap["model"]}"']
    return "\n".join(lines) + "\n"


def configure_plan(project: Path) -> dict:
    project = project.absolute()
    if install.is_link(project):
        raise ValueError("Refusing a linked target root")
    project = project.resolve()
    if not project.is_dir():
        raise ValueError("Target must be a directory")
    base = project / "ai-kit" / "router"
    selection = load_selection(base / "selection.json")
    providers = load_providers(base / "providers")
    state = install.read_json(project / "ai-kit" / ".install-state.json", {})
    agents = state.get("agents", []) if isinstance(state.get("agents"), list) else []
    actions: dict[str, bytes] = {
        "ai-kit/router/resolved.json": (json.dumps(resolved_document(selection, providers),
                                                   indent=2) + "\n").encode(),
    }
    conflicts: dict[str, bytes] = {}
    info: list[str] = []
    if "aider" in agents:
        config = aider_config(selection, providers)
        if config is None:
            info.append("Aider selected but cheap/work models are unresolved; skipped .aider.conf.yml.")
        else:
            data = config.encode("utf-8")
            destination = install.safe_path(project, ".aider.conf.yml")
            current = destination.read_bytes() if destination.exists() else None
            if current is not None and current != data:
                conflicts[".aider.conf.yml"] = data
            else:
                actions[".aider.conf.yml"] = data
    for name in sorted(providers):
        if providers[name].get("verification_status") == "pending":
            info.append(f"Provider {name} verification is pending; its roles are unresolved.")
    return {"target": str(project), "actions": actions, "conflicts": conflicts, "info": info}


def apply_configure(plan: dict) -> bool:
    if plan["conflicts"]:
        return False
    target = Path(plan["target"])
    for relative, data in plan["actions"].items():
        install.atomic_write(install.safe_path(target, relative), data)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    route_parser = sub.add_parser("route", help="Recommend a capability level, role, and model for a task")
    route_parser.add_argument("task")
    route_parser.add_argument("--level", type=int)
    route_parser.add_argument("--role", choices=list(ROLES))
    route_parser.add_argument("--effort")
    route_parser.add_argument("--project", type=Path)
    route_parser.add_argument("--root", type=Path, default=ROOT)
    configure_parser = sub.add_parser("configure", help="Generate resolved routing config for an installed project")
    configure_parser.add_argument("project", type=Path)
    configure_parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "route":
            selection, providers = _selection_and_providers(args.project, args.root)
            print(json.dumps(route_result(args.task, selection, providers, level=args.level,
                                          role=args.role, effort=args.effort), indent=2))
            return 0
        plan = configure_plan(args.project)
        print(json.dumps({"target": plan["target"], "preview": not args.apply,
                          "writes": sorted(plan["actions"]), "conflicts": sorted(plan["conflicts"]),
                          "info": plan["info"]}, indent=2))
        if args.apply:
            apply_configure(plan)
        return 2 if plan["conflicts"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Routing refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
