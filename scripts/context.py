"""Capture manifest evidence for an installed project's verified context."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install


PROJECT_FACTS = "ai-kit/project.json"
DESIGN_WORKFLOWS = {"web-design": "web-design", "ui-review": "ui-review", "design-extract": "design-extract"}


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
    data = (json.dumps(updated, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
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
    # project.json is project-owned: keep the previous bytes, as installer upgrades do.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    install.atomic_write(install.safe_path(target, "ai-kit/.upstream-cache/backups/" + stamp + "/" + plan["path"]),
                         plan["old"])
    install.atomic_write(path, plan["data"])
    return True


def select_context(target: Path, *, path: str = ".", budget: int = 32000,
                   workflow: str | None = None) -> dict:
    """Select instructions by declared module scope; budgets cannot remove critical rules."""
    target = target_root(target)
    if type(budget) is not int or budget < 1:
        raise ValueError("Context budget must be a positive byte count")
    if workflow is not None and workflow not in DESIGN_WORKFLOWS:
        raise ValueError("Unknown context workflow: " + str(workflow))
    if path == ".":
        relative = ""
    else:
        # Probe a file rather than accepting directory links through resolve().
        install.safe_path(target, path.rstrip("/") + "/__context_probe__")
        relative = path.strip("/")
        if path.startswith(("/", "\\")):
            raise ValueError("Module path must be relative")
    facts = install.read_json(install.safe_path(target, PROJECT_FACTS), {})
    if facts.get("schema") != 1 or not isinstance(facts.get("modules"), list):
        raise ValueError("Missing/invalid project module map")
    profiles, matching, scoped = set(), [], []
    for module in facts["modules"]:
        if not isinstance(module, dict) or not isinstance(module.get("path"), str) or not install.MODULE_PATH.fullmatch(module["path"]):
            raise ValueError("Invalid declared module path")
        scope = module["path"].strip("/")
        if not scope or relative == scope or relative.startswith(scope + "/"):
            if not isinstance(module.get("profiles"), list) or any(not isinstance(p, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", p) for p in module["profiles"]):
                raise ValueError("Invalid module profiles")
            scoped.append(module)
    # A nested declared module supersedes its parent's stack, while shared instructions still apply.
    deepest = max((len(m["path"]) for m in scoped), default=0)
    for module in scoped:
        if len(module["path"]) == deepest:
            matching.append(module["path"])
            profiles.update(module["profiles"])
    critical = ["AGENTS.md", "ai-kit/CORE.md", "ai-kit/settings.json", "PROJECT_CONTEXT.md",
                "ai-kit/ENGINEERING.md", "ai-kit/SECURITY.md", "docs/DECISIONS.md"]
    settings = install.read_json(install.safe_path(target, "ai-kit/settings.json"), {})
    workflow_files = []
    if workflow is not None:
        if settings.get("web_design") is not True:
            raise ValueError("Web Design workflow is disabled; install with --with-web-design first")
        workflow_files = ["ai-kit/WEB-DESIGN.md", ".agents/skills/" + DESIGN_WORKFLOWS[workflow] + "/SKILL.md",
                          *install.OPTIONAL_DOCUMENTS["web-design"]]
        if workflow == "ui-review":
            workflow_files.append("ai-kit/web-design/REVIEW.md")
        elif workflow == "design-extract":
            workflow_files.append("ai-kit/web-design/TOOLS.md")
        elif profiles & {"LARAVEL", "FILAMENT"}:
            workflow_files.extend(["ai-kit/web-design/LARAVEL.md", ".agents/skills/laravel-blade-ui/SKILL.md"])
        critical.extend(workflow_files)
    if settings.get("conventions") == "owner" and profiles & {"LARAVEL", "FILAMENT"}:
        critical.append("ai-kit/profiles/OWNER.md")
    # ADRs preserve architectural constraints between sessions; do not truncate them for a budget.
    adr_dir = target / "docs/adr"
    if install.is_link(adr_dir):
        raise ValueError("Refusing linked ADR directory")
    if adr_dir.is_dir():
        critical.extend(p.relative_to(target).as_posix() for p in sorted(adr_dir.glob("*.md")) if p.name != "0000-template.md")
    if relative:
        parts = relative.split("/")
        critical.extend("/".join(parts[:i]) + "/AGENTS.md" for i in range(1, len(parts) + 1))
    required_profiles = ["ai-kit/stacks/" + p + ".md" for p in sorted(profiles)]
    critical.extend(required_profiles)
    selected, missing, duplicates = [], [], []
    hashes: dict[str, str] = {}
    for name in dict.fromkeys(critical):
        candidate = install.safe_path(target, name)
        if not candidate.is_file():
            # Nested instructions and project decision records are optional; Core/settings are required.
            if name in {"AGENTS.md", "ai-kit/CORE.md", "ai-kit/settings.json", "PROJECT_CONTEXT.md",
                        "ai-kit/ENGINEERING.md", "ai-kit/SECURITY.md"} or name in required_profiles or name in workflow_files:
                missing.append(name)
            continue
        data = candidate.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest in hashes:
            duplicates.append({"path": name, "same_as": hashes[digest]})
        else:
            hashes[digest] = name
        selected.append({"path": name, "bytes": len(data), "sha256": digest, "critical": True})
    if missing:
        raise ValueError("Missing required context: " + ", ".join(missing))
    total = sum(item["bytes"] for item in selected)
    return {"selected": selected, "duplicates": duplicates, "modules": matching, "profiles": sorted(profiles),
            "workflow": workflow,
            "total_bytes": total, "budget_bytes": budget, "over_budget": total > budget,
            "selection_complete": bool(matching),
            "note": "Declared modules may still need bootstrap verification. Byte counts are not token counts. "
                    "Critical rules, matching profiles and architecture decisions are retained even above budget. "
                    "Duplicate critical files retain their scope/relative-link meaning. "
                    "Unrelated profiles and instruction history are excluded; no files are changed."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    snapshot = sub.add_parser("snapshot", help="Preview or record current manifest evidence in project.json")
    snapshot.add_argument("project", type=Path)
    snapshot.add_argument("--apply", action="store_true")
    select = sub.add_parser("select", help="Select module instructions and measure a byte budget without writing")
    select.add_argument("project", type=Path)
    select.add_argument("--path", default=".", help="Relative module/directory scope")
    select.add_argument("--budget", type=int, default=32000, help="Byte budget; critical context is never dropped")
    select.add_argument("--workflow", choices=sorted(DESIGN_WORKFLOWS),
                        help="Include the enabled design workflow and project design documents")
    args = parser.parse_args(argv)
    try:
        if args.command == "select":
            print(json.dumps(select_context(args.project, path=args.path, budget=args.budget,
                                            workflow=args.workflow), indent=2))
            return 0
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
