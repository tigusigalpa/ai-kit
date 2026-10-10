"""Offline health check for an AI-KIT-installed application project."""
from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_kit
import install
import router

BUDGETS = {"AGENTS.md": 2500, "ai-kit/CORE.md": 3000}
PROVIDER_FRESHNESS_DAYS = 90


def examine(target: Path, *, root: Path = install.ROOT) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    try:
        target = target.absolute()
        if install.is_link(target):
            raise ValueError("Refusing a linked target root")
        target = target.resolve()
    except ValueError as exc:
        return {"target": str(target), "installed_version": None, "bundle_version": None,
                "errors": [str(exc)], "warnings": warnings, "info": info}
    report = {"target": str(target),
              "installed_version": None,
              "bundle_version": (root / "VERSION").read_text(encoding="utf-8").strip(),
              "errors": errors, "warnings": warnings, "info": info}
    if not target.is_dir():
        errors.append("Target is not a directory")
        return report
    try:
        settings = install.read_json(target / "ai-kit" / "settings.json", {})
        install.validate_settings(settings)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid installation settings: {exc}")
    state_path = target / "ai-kit" / ".install-state.json"
    if not state_path.is_file():
        errors.append("No installer state found; is AI-KIT installed in this project?")
        return report
    try:
        state = install.read_json(state_path, {})
        install.validate_state(state, target)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid installer state: {exc}")
        return report
    report["installed_version"] = state.get("accepted_version")
    if report["installed_version"] != report["bundle_version"]:
        info.append("Installed baseline differs from this bundle's VERSION.")
    records = state.get("files", {})
    modified, adapted = [], []
    for relative in sorted(records):
        try:
            path = install.safe_path(target, relative)
        except ValueError as exc:
            errors.append(f"Unsafe recorded path {relative}: {exc}")
            continue
        if not path.is_file():
            errors.append("Missing managed file: " + relative)
        elif install.digest(path.read_bytes()) != records[relative]["installed_hash"]:
            (adapted if records[relative].get("local_adaptation") else modified).append(relative)
    warnings.extend(f"Modified after installation; rerun the installer to review: {r}" for r in modified)
    info.extend(f"Locally adapted (accepted): {r}" for r in adapted)
    for relative in sorted(install.OWNED):
        if not (target / relative).is_file():
            warnings.append("Owned project document missing: " + relative)
    for relative, limit in BUDGETS.items():
        path = target / relative
        if path.is_file() and path.stat().st_size > limit:
            warnings.append(f"Always-loaded entry exceeds budget: {relative}")
    candidates_dir = target / "ai-kit" / ".upstream-cache" / "candidates"
    if candidates_dir.is_dir():
        pending = list(candidates_dir.glob("*/*.metadata.json"))
        if pending:
            warnings.append(f"Pending conflict candidates need review: {len(pending)}")
    providers_dir = target / "ai-kit" / "router" / "providers"
    provider_configs = sorted(providers_dir.glob("*.json")) if providers_dir.is_dir() else []
    for provider in provider_configs:
        try:
            config = json.loads(provider.read_text(encoding="utf-8"))
        except ValueError as exc:
            warnings.append(f"Invalid provider configuration {provider.name}: {exc}")
            continue
        user_supplied = config.get("user_supplied_models") is True
        pending = config.get("verification_status") == "pending"
        for role, spec in config.get("roles", {}).items():
            if "effort" in spec and spec["effort"] not in config.get("supported_efforts", {}).get(role, []):
                warnings.append(f"Unsupported configured effort: {provider.name} role {role}")
        verified = config.get("verified_documentation_date")
        try:
            verified_date = date.fromisoformat(verified) if isinstance(verified, str) else None
        except ValueError:
            verified_date = None
        if user_supplied:
            info.append(f"Provider {provider.name} uses project-supplied local models")
        elif pending:
            info.append(f"Provider {provider.name} verification is pending")
        elif verified_date is None:
            warnings.append(f"Provider {provider.name} lacks a valid verified_documentation_date")
        elif (date.today() - verified_date).days > PROVIDER_FRESHNESS_DAYS:
            warnings.append(f"Provider {provider.name} verification is older than "
                            f"{PROVIDER_FRESHNESS_DAYS} days")
    selection_path = target / "ai-kit" / "router" / "selection.json"
    if selection_path.is_file():
        try:
            router.validate_selection(json.loads(selection_path.read_text(encoding="utf-8")))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            warnings.append(f"Invalid router selection: {exc}")
    resolved_path = target / "ai-kit" / "router" / "resolved.json"
    if resolved_path.is_file():
        try:
            resolved = json.loads(resolved_path.read_text(encoding="utf-8"))
            if type(resolved.get("schema")) is not int or resolved["schema"] != 1:
                raise ValueError("Unsupported resolved schema; expected schema 1")
            if not isinstance(resolved.get("roles"), dict):
                raise ValueError("Resolved roles must be an object")
        except (ValueError, json.JSONDecodeError) as exc:
            warnings.append(f"Invalid generated router config: {exc}")
    warnings.extend(link_warnings(target))
    return report


def link_warnings(target: Path) -> list[str]:
    """Report broken relative links/anchors in the installed project's Markdown."""
    problems = []
    excluded = {".git", ".upstream-cache", "node_modules", "vendor", ".venv", "__pycache__"}
    for directory, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if d not in excluded and not install.is_link(Path(directory) / d)]
        for name in files:
            path = Path(directory) / name
            if path.suffix != ".md":
                continue
            relative = path.relative_to(target).as_posix()
            text = path.read_text(encoding="utf-8")
            for link in check_kit.links(text):
                if re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I):
                    continue
                filename, _, anchor = unquote(link).partition("#")
                destination = (path.parent / filename).resolve() if filename else path.resolve()
                try:
                    destination.relative_to(target.resolve())
                except ValueError:
                    problems.append(f"{relative}: link escapes project: {link}")
                    continue
                if not destination.exists():
                    problems.append(f"{relative}: missing link: {link}")
                elif anchor and destination.is_file() and destination.suffix == ".md":
                    if anchor not in check_kit.headings(destination.read_text(encoding="utf-8")):
                        problems.append(f"{relative}: missing heading: {link}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--root", type=Path, default=install.ROOT,
                        help="Reference distribution used for the bundle version comparison")
    args = parser.parse_args(argv)
    try:
        report = examine(args.target, root=args.root)
    except OSError as exc:
        print(f"Examination failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
