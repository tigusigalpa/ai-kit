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
LEVEL_MAP = {0: ("cheap", "none"), 1: ("cheap", "low"), 2: ("work", "medium"),
             3: ("work", "high"), 4: ("work", "xhigh"), 5: ("work", "max"),
             6: ("escalation", None)}
OPERATIONS = {"extract": 0, "mechanical": 1, "implement": 2, "debug": 3,
              "architecture": 3, "research": 5}
RISKS = {"security": 4, "payments": 4, "distributed": 4, "conflicting-evidence": 4}
# Word boundaries prevent "trace" from matching "race"; stems cover Russian inflections.
_OPERATIONS = {
    "research": r"formal proof|prove (?:a |the )?(?:theorem|novel algorithm)|novel algorithm|"
                r"(?:\u0434\u043e\u043a\u0430\u0437|\u0434\u043e\u043a\u0430\u0436)\w* \u0442\u0435\u043e\u0440\u0435\u043c\w*|\u0444\u043e\u0440\u043c\u0430\u043b\u044c\u043d\w* \u0434\u043e\u043a\u0430\u0437\u0430\u0442\u0435\u043b\u044c\u0441\u0442\u0432\w*|\u043d\u043e\u0432\w* \u0430\u043b\u0433\u043e\u0440\u0438\u0442\u043c\w*",
    "debug": r"debug\w*|concurrency|race(?: condition)?|deadlock\w*|memory leak|performance|optimiz\w*|"
             r"\u043e\u0442\u043b\u0430\u0434\w*|\u0434\u0435\u0434\u043b\u043e\u043a\w*|\u0432\u0437\u0430\u0438\u043c\u043d\w* \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\w*|\u0433\u043e\u043d\u043a\w*|\u043a\u043e\u043d\u043a\u0443\u0440\u0435\u043d\u0442\u043d\w*|\u0443\u0442\u0435\u0447\u043a\w* \u043f\u0430\u043c\u044f\u0442\u0438|\u043e\u043f\u0442\u0438\u043c\u0438\u0437\w*",
    "architecture": r"architectur\w*|\u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\w*",
    "mechanical": r"rename\w*|bump|boilerplate|lint|typo\w*|format code|mechanical|"
                  r"\u043f\u0435\u0440\u0435\u0438\u043c\u0435\u043d\w*|\u043e\u043f\u0435\u0447\u0430\u0442\u043a\w*|\u043f\u043e\u0434\u043d\u0438\u043c\w* \u0432\u0435\u0440\u0441\u0438\w*|\u0444\u043e\u0440\u043c\u0430\u0442\u0438\u0440\u043e\u0432\u0430\u043d\w* \u043a\u043e\u0434\w*",
    "implement": r"implement\w*|build|add|create|fix|process|\u0440\u0435\u0430\u043b\u0438\u0437\w*|\u0434\u043e\u0431\u0430\u0432\w*|\u0441\u043e\u0437\u0434\u0430\w*|\u0438\u0441\u043f\u0440\u0430\u0432\w*|\u043e\u0431\u0440\u0430\u0431\u043e\u0442\w*",
    "extract": r"classify|categorize|extract|label|tag|parse|\u043a\u043b\u0430\u0441\u0441\u0438\u0444\u0438\u0446\w*|\u0438\u0437\u0432\u043b\u0435\w*|\u0440\u0430\u0437\u043c\u0435\u0442\w*|\u0440\u0430\u0441\u043f\u0430\u0440\u0441\w*",
}
_RISKS = {
    "security": r"security|sensitive data|authentication|authorization|compliance|"
                r"\u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\w*|\u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\w* \u0434\u0430\u043d\u043d\w*|\u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\w*|\u0430\u0443\u0442\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0446\w*",
    "payments": r"payment\w*|billing|money transfer|\u043f\u043b\u0430\u0442\u0435\u0436\w*|\u043f\u043b\u0430\u0442\u0451\u0436\w*|\u043e\u043f\u043b\u0430\u0442\w*|\u043f\u0435\u0440\u0435\u0432\u043e\u0434\w* \u0434\u0435\u043d\u0435\u0433",
    "distributed": r"distributed|consensus|replication|\u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b[\u0435\u0451]\u043d\w*|\u043a\u043e\u043d\u0441\u0435\u043d\u0441\u0443\u0441\w*|\u0440\u0435\u043f\u043b\u0438\u043a\u0430\u0446\w*",
    "conflicting-evidence": r"conflicting (?:evidence|requirements)|\u043f\u0440\u043e\u0442\u0438\u0432\u043e\u0440\u0435\u0447\u0438\u0432\w* (?:\u0434\u0430\u043d\u043d\w*|\u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\w*)",
}
NOTE = ("Offline recommendation, not execution. Rules can miss context; verify risk, "
        "model availability, and client support. Level 6 requires a diagnosed capability shortfall.")


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


def classify_task(text: str, *, operation: str | None = None, risks: tuple[str, ...] = (),
                  components: int | None = None) -> dict:
    if operation is not None and operation not in OPERATIONS:
        raise ValueError("Unknown operation: " + operation)
    if any(risk not in RISKS for risk in risks):
        raise ValueError("Unknown risk")
    if components is not None and (type(components) is not int or components < 1):
        raise ValueError("Components must be a positive integer")
    # File names and code identifiers are weak evidence of the requested operation.
    prose = re.sub(r"`[^`]*`|\S+\.[a-z][a-z0-9]{0,9}\b", " ", text.lower())
    signals = []
    if operation is None:
        operation = next((name for name, pattern in _OPERATIONS.items()
                          if re.search(r"\b(?:" + pattern + r")\b", prose)), "implement")
        signals.append("text operation: " + operation)
    else:
        signals.append("explicit operation: " + operation)
    level = OPERATIONS[operation]
    detected = {name for name, pattern in _RISKS.items()
                if re.search(r"\b(?:" + pattern + r")\b", prose)}
    for risk in sorted(detected | set(risks)):
        level = max(level, RISKS[risk])
        signals.append(("explicit risk: " if risk in risks else "text risk: ") + risk)
    if components is not None and components >= 3:
        level = max(level, 3)
        signals.append("three or more affected components")
    return {"level": level, "signals": signals}


def classify_level(text: str) -> int:
    return classify_task(text)["level"]


def _role_selection(role: str, selection: dict) -> dict:
    spec = selection.get("roles", {}).get(role)
    return {"provider": spec} if isinstance(spec, str) else (spec or {})


def _supported_efforts(config: dict, model: str | None) -> list[str]:
    # Capability declarations belong to known model IDs, not arbitrary overrides or local models.
    if model is not None:
        for name, spec in config.get("roles", {}).items():
            if spec.get("model") == model:
                return config.get("supported_efforts", {}).get(name, [])
    return []


def resolve_role(role: str, selection: dict, providers: dict[str, dict]) -> dict:
    spec = _role_selection(role, selection)
    provider_id = spec.get("provider") or selection.get("default_provider")
    if provider_id is None:
        return {"role": role, "provider": None, "model": None, "effort": None,
                "reasoning_mode": "standard", "service_tier": "standard", "tier": None,
                "supported_efforts": [], "resolved": False}
    if provider_id not in providers:
        raise ValueError(f"Unknown provider in selection: {provider_id}")
    config = providers[provider_id]
    if config.get("verification_status") == "pending":
        return {"role": role, "provider": provider_id, "model": None, "effort": None,
                "reasoning_mode": None, "service_tier": None, "tier": config.get("tier"),
                "supported_efforts": [], "resolved": False}
    role_spec = config.get("roles", {}).get(role, {})
    if not isinstance(role_spec, dict):
        role_spec = {}
    model = spec.get("model")
    if model is None and config.get("user_supplied_models"):
        model = selection.get("local_models", {}).get(role)
    if model is None:
        model = role_spec.get("model")
    supported = _supported_efforts(config, model)
    effort = spec.get("effort")
    if effort is not None and effort not in supported:
        raise ValueError(f"Effort {effort} is not declared for provider/model {provider_id}/{model}")
    if effort is None and role_spec.get("effort") in supported:
        effort = role_spec["effort"]
    return {"role": role, "provider": provider_id, "model": model, "effort": effort,
            "reasoning_mode": config.get("reasoning_mode", "standard"),
            "service_tier": config.get("service_tier_policy", "standard"),
            "tier": config.get("tier", "cloud"), "supported_efforts": supported,
            "resolved": model is not None}


def classify(text: str) -> dict:
    level = classify_level(text)
    role, effort = LEVEL_MAP[level]
    return {"level": level, "role": role, "effort": effort}


def route_result(text: str, selection: dict, providers: dict[str, dict], *,
                 level: int | None = None, role: str | None = None, effort: str | None = None,
                 operation: str | None = None, risks: tuple[str, ...] = (),
                 components: int | None = None, provider: str | None = None,
                 model: str | None = None) -> dict:
    validate_selection(selection)
    classified = classify_task(text, operation=operation, risks=risks, components=components)
    explicit_level = level is not None
    if level is None:
        level = classified["level"]
    elif type(level) is not int or not 0 <= level <= 6:
        raise ValueError("Level must be an integer 0-6")
    if explicit_level:
        classified["signals"].append(f"explicit level: {level}")
    default_role, default_effort = LEVEL_MAP.get(level, ("work", "medium"))
    role = role or default_role
    if role not in ROLES:
        raise ValueError("Role must be one of: " + ", ".join(ROLES))
    if provider is not None or model is not None or effort is not None:
        override = dict(_role_selection(role, selection))
        previous_provider = override.get("provider") or selection.get("default_provider")
        if provider is not None and provider != previous_provider:
            # A provider switch must not carry the old provider's model ID into the new catalogue.
            override.pop("model", None)
        selection = {**selection, "roles": {**selection["roles"], role: {
            **override,
            **({"provider": provider} if provider is not None else {}),
            **({"model": model} if model is not None else {}),
            **({"effort": effort} if effort is not None else {})}}}
    resolved = resolve_role(role, selection, providers)
    configured = _role_selection(role, selection).get("effort")
    requested = effort if effort is not None else configured
    recommended = requested if requested is not None else default_effort
    supported = resolved["supported_efforts"]
    adjustments = []
    if requested is not None and requested not in supported and resolved["resolved"]:
        raise ValueError(f"Effort {requested} is not declared for the selected model")
    if resolved["resolved"] and recommended in supported:
        chosen_effort = recommended
    else:
        chosen_effort = resolved["effort"]
        if recommended is not None:
            adjustments.append("Recommended effort is unavailable; using the declared model default "
                               "or no effort control when capabilities are unknown.")
    return {"level": level, "role": role, "effort": chosen_effort,
            "recommended_effort": recommended, "resolved": resolved["resolved"],
            "provider": resolved["provider"], "model": resolved["model"],
            "reasoning_mode": resolved["reasoning_mode"], "service_tier": resolved["service_tier"],
            "tier": resolved["tier"], "signals": classified["signals"],
            "level_source": "explicit" if explicit_level else "classified",
            "effort_source": "explicit" if effort is not None else
                             ("selection" if configured is not None else "ladder"),
            "adjustments": adjustments, "note": NOTE}


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


def providers_report(providers: dict[str, dict]) -> dict:
    """Summarize provider status, verification dates, and sources for review."""
    items = []
    for name in sorted(providers):
        config = providers[name]
        if config.get("user_supplied_models"):
            status = "local"
        elif config.get("verification_status") == "pending":
            status = "pending"
        else:
            status = "verified"
        items.append({"provider": name, "tier": config.get("tier", "cloud"), "status": status,
                      "verified_documentation_date": config.get("verified_documentation_date"),
                      "sources": config.get("sources", [])})
    return {"providers": items}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    route_parser = sub.add_parser("route", help="Recommend a capability level, role, and model for a task")
    route_parser.add_argument("task")
    route_parser.add_argument("--level", type=int)
    route_parser.add_argument("--role", choices=list(ROLES))
    route_parser.add_argument("--effort")
    route_parser.add_argument("--provider", help="Provider override for this recommendation only")
    route_parser.add_argument("--model", help="Model ID override; capabilities must be declared")
    route_parser.add_argument("--operation", choices=list(OPERATIONS))
    route_parser.add_argument("--risk", choices=list(RISKS), action="append", default=[])
    route_parser.add_argument("--components", type=int, help="Number of affected interacting components")
    route_parser.add_argument("--project", type=Path)
    route_parser.add_argument("--root", type=Path, default=ROOT)
    configure_parser = sub.add_parser("configure", help="Generate resolved routing config for an installed project")
    configure_parser.add_argument("project", type=Path)
    configure_parser.add_argument("--apply", action="store_true")
    providers_parser = sub.add_parser("providers", help="List providers with status and verification sources")
    providers_parser.add_argument("--project", type=Path)
    providers_parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        if args.command == "route":
            selection, providers = _selection_and_providers(args.project, args.root)
            print(json.dumps(route_result(args.task, selection, providers, level=args.level,
                                          role=args.role, effort=args.effort, provider=args.provider,
                                          model=args.model, operation=args.operation,
                                          risks=tuple(args.risk), components=args.components), indent=2))
            return 0
        if args.command == "providers":
            _, providers = _selection_and_providers(args.project, args.root)
            print(json.dumps(providers_report(providers), indent=2))
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
