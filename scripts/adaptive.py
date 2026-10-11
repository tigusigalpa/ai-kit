"""Optional routing modes, pins and measured recommendations, without a switching runtime."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install
import learning
import metrics
import router

MODES = ("manual", "fixed", "recommended", "adaptive")
PROFILES = ("economy", "balanced", "quality")


def defaults() -> dict:
    return {"schema": 1, "mode": "recommended", "profile": "balanced", "project_pin": None,
            "task_pins": {}, "minimum_cases": 20, "quality_floor": 0.8,
            "context_bytes": {"economy": 16000, "balanced": 32000, "quality": 64000},
            "orchestration": {"planner": "work", "executor": "work", "reviewer": "work", "escalation": "escalation"}}


def validate_pin(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {"provider", "model", "effort"}:
        raise ValueError("A pin needs provider, model and effort (null when unknown/not controlled)")
    for key in ("provider", "model"):
        metrics._identifier(value[key], key)
    if value["effort"] is not None:
        metrics._identifier(value["effort"], "effort")
    return value


def validate_config(value: object) -> dict:
    base = defaults()
    if not isinstance(value, dict) or set(value) - set(base):
        raise ValueError("Invalid routing configuration or unknown fields")
    base.update(copy.deepcopy(value))
    if type(base["schema"]) is not int or base["schema"] != 1:
        raise ValueError("Expected routing schema 1")
    if not isinstance(base["mode"], str) or not isinstance(base["profile"], str) or base["mode"] not in MODES or base["profile"] not in PROFILES:
        raise ValueError("Unknown routing mode/profile")
    if base["project_pin"] is not None:
        validate_pin(base["project_pin"])
    if not isinstance(base["task_pins"], dict):
        raise ValueError("task_pins must be an object")
    for key, pin in base["task_pins"].items():
        metrics._identifier(key, "task pin ID")
        validate_pin(pin)
    if type(base["minimum_cases"]) is not int or base["minimum_cases"] < 5:
        raise ValueError("Minimum sample must be at least five distinct cases")
    if type(base["quality_floor"]) not in {int, float} or not 0.5 <= base["quality_floor"] <= 1:
        raise ValueError("Quality floor must be 0.5-1")
    if (not isinstance(base["context_bytes"], dict) or set(base["context_bytes"]) != set(PROFILES) or
            any(type(v) is not int or v < 1 for v in base["context_bytes"].values())):
        raise ValueError("Every profile needs a positive context byte budget")
    roles = base["orchestration"]
    if (not isinstance(roles, dict) or set(roles) != {"planner", "executor", "reviewer", "escalation"} or
            any(v not in router.ROLES for v in roles.values())):
        raise ValueError("Orchestration roles must map to configured routing roles")
    return base


def load_config(project: Path | None = None, root: Path = router.ROOT) -> dict:
    path = (install.safe_path(metrics._target(project), "ai-kit/router/routing.json") if project else
            root / "template/ai-kit/router/routing.json")
    return validate_config(json.loads(path.read_text(encoding="utf-8")) if path.exists() else {})


def recommend_route(text: str, selection: dict, providers: dict, *, config: dict | None = None,
                    records: list[dict] | None = None, mode: str | None = None, profile: str | None = None,
                    task_id: str | None = None, stack: str = "unknown", capabilities: list[str] | None = None,
                    **overrides) -> dict:
    config = validate_config(config or {})
    mode, profile = mode or config["mode"], profile or config["profile"]
    if mode not in MODES or profile not in PROFILES:
        raise ValueError("Unknown routing mode/profile")
    if stack not in metrics.STACKS:
        raise ValueError("Unknown stack")
    if task_id is not None:
        metrics._identifier(task_id, "task_id")
    capabilities = capabilities or []
    for capability in capabilities:
        metrics._identifier(capability, "capability")
    pin = config["task_pins"].get(task_id, config["project_pin"])
    source = "task pin" if task_id in config["task_pins"] else "project pin"
    explicit = any(overrides.get(k) is not None for k in ("provider", "model", "effort"))
    call = dict(overrides)
    effective_pin = copy.deepcopy(pin)
    if pin:
        if overrides.get("provider") is not None and overrides["provider"] != pin["provider"]:
            effective_pin.pop("model", None)
            effective_pin.pop("effort", None)
        elif overrides.get("model") is not None and overrides["model"] != pin["model"]:
            effective_pin.pop("effort", None)
        call = {**effective_pin, **{k: v for k, v in overrides.items() if v is not None}}
        selection = copy.deepcopy(selection)
        for name in router.ROLES:
            spec = selection["roles"].get(name)
            if isinstance(spec, dict):
                spec.pop("effort", None)
    result = router.route_result(text, selection, providers, **call)
    if mode in {"manual", "fixed"} and not pin and overrides.get("model") is None:
        raise ValueError("Manual/fixed mode requires a project/task pin or explicit model")
    if mode in {"manual", "fixed"} and not result["resolved"]:
        raise ValueError("Pinned model is unresolved")
    if pin and "effort" in effective_pin and overrides.get("effort") is None:
        # Null pin effort explicitly means no effort control; the ladder cannot override it.
        result["effort"] = effective_pin["effort"]
        result["effort_source"] = source
    configured_effort = router._role_selection(result["role"], selection).get("effort") is not None
    if not pin and not explicit and not configured_effort:
        supported = router._supported_efforts(providers.get(result["provider"], {}), result["model"])
        ladder = ("none", "minimal", "low", "medium", "high", "xhigh", "max")
        if profile == "quality" and result["effort"] in ladder and "high" in supported and ladder.index(result["effort"]) < ladder.index("high"):
            result["effort"], result["effort_source"] = "high", "quality profile"
        elif profile == "economy" and result["level"] < 3 and result["effort"] == "medium" and "low" in supported:
            result["effort"], result["effort_source"] = "low", "economy profile"
    learned = None
    if mode == "adaptive" and not pin and not explicit and not configured_effort:
        classified = router.classify_task(text, operation=overrides.get("operation"),
                                         risks=overrides.get("risks", ()), components=overrides.get("components"))
        task_class = overrides.get("operation") or classified["signals"][0].split(": ")[-1]
        available = {selection.get("default_provider")}
        available.update(router._role_selection(name, selection).get("provider") for name in router.ROLES)
        if any(selection["local_models"].values()):
            available.update(name for name, catalogue in providers.items() if catalogue.get("user_supplied_models"))
        available.discard(None)
        learned = learning.recommend(records or [], result, stack=stack, task_class=task_class,
                                     level=result["level"], capabilities=capabilities,
                                     minimum=config["minimum_cases"],
                                     quality_floor=max(config["quality_floor"], 0.95 if profile == "quality" else 0.5),
                                     profile=profile, allowed_providers=available)
        if learned:
            catalogue = providers.get(learned["provider"], {})
            declared = list(catalogue.get("roles", {}).values())
            supported = set(next((s.get("capabilities", []) for s in declared if s.get("model") == learned["model"]), []))
            known_models = {s.get("model") for s in declared} | (set(selection["local_models"].values()) if catalogue.get("user_supplied_models") else set())
            efforts = router._supported_efforts(catalogue, learned["model"])
            if (catalogue and catalogue.get("verification_status") != "pending" and learned["model"] in known_models and
                    (learned["effort"] is None or learned["effort"] in efforts) and set(capabilities) <= supported):
                proposed = router.route_result(text, selection, providers, **{
                    **overrides, **{k: learned[k] for k in ("provider", "model", "effort")}})
                result = proposed
                result["effort"] = learned["effort"]
                result["effort_source"] = "matched measurements"
            else:
                learned = None
    result.update({"routing_mode": mode, "optimization_profile": profile,
                   "context_budget_bytes": config["context_bytes"][profile],
                   "independent_review": profile == "quality" or result["level"] >= 4,
                   "escalation_policy": "diagnosed failure; independent review before acceptance" if profile == "quality" else
                                        "bounded rework before diagnosed escalation; preserve quality floor" if profile == "economy" else
                                        "diagnosed capability shortfall; include recovery cost",
                   "recommendation_source": "explicit" if explicit else source if pin else
                                            "matched measurements" if learned else "capability ladder",
                   "measurement_evidence": learned, "execution_confirmed": False})
    declared = providers.get(result["provider"], {}).get("roles", {}).values()
    known = set(next((s.get("capabilities", []) for s in declared if s.get("model") == result["model"]), []))
    result["capabilities_verified"] = set(capabilities) <= known
    if not result["capabilities_verified"]:
        result["adjustments"].append("Required capabilities are not declared for this model; verify before execution.")
    if mode == "adaptive" and not learned and not pin and not explicit:
        result["adjustments"].append("Insufficient comparable measured evidence; retain the capability recommendation.")
    return result
