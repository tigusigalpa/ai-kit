"""Conservative, offline AI-KIT installation and unchanged-baseline upgrades."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
START = "# BEGIN AI-KIT MANAGED"
END = "# END AI-KIT MANAGED"
OWNED = {"README.md", "PROJECT_CONTEXT.md", "WIKI.md", "CHANGELOG.md", "docs/DECISIONS.md",
         "docs/adr/0000-template.md"}
ENTRIES = {"CLAUDE.md": "claude", "KIMI.md": "kimi", "MANUS.md": "manus"}
AGENTS = {"codex", "claude", "kimi", "manus", "copilot", "cursor", "aider"}
OPTIONAL = {"copilot": ("copilot-instructions.md", ".github/copilot-instructions.md"),
            "cursor": ("ai-kit.mdc", ".cursor/rules/ai-kit.mdc"),
            "aider": ("CONVENTIONS.md", "CONVENTIONS.md")}
PROFILE_MANIFESTS = {
    "GO": ("go.mod",),
    "PYTHON": ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"),
    "FRONTEND": ("package.json",),
}
EXTRAS = {"session-start", "guards", "ci"}
EXTRA_TEMPLATE = {"session-start": ".agents/hooks/session-start.md"}
EXTRA_INTEGRATIONS = {"ci": ("ai-kit-check.yml", ".github/workflows/ai-kit.yml")}
EXTRA_SETTINGS_KEYS = {"session-start": "session_start", "guards": "guards", "ci": "ci"}
NODE_IGNORES = ("node_modules/", ".npm/", ".pnpm-store/", ".yarn/cache/", ".yarn/unplugged/",
                ".yarn/install-state.gz", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*",
                "pnpm-debug.log*")
PYTHON_IGNORES = (".venv/", "venv/", "__pypackages__/", "__pycache__/", "*.py[cod]", "*$py.class",
                  ".pytest_cache/", ".mypy_cache/", ".ruff_cache/", ".pyre/", ".pytype/",
                  ".hypothesis/", ".tox/", ".nox/", ".ipynb_checkpoints/", ".coverage", ".coverage.*",
                  "htmlcov/", "coverage.xml", "*.egg-info/", ".eggs/", "*.egg", "*.whl",
                  "pip-wheel-metadata/", "pip-log.txt", "pip-delete-this-directory.txt", ".pypirc")
PYTHON_ROOT_IGNORES = (".cache/pip/", ".cache/uv/", ".cache/pypoetry/")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_link(path: Path) -> bool:
    """Recognize symlinks and Windows junctions on Python 3.10 and later."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", None) in {
        getattr(stat, "IO_REPARSE_TAG_SYMLINK", -1),
        getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", -2),
    }


def safe_path(target: Path, relative: str) -> Path:
    parts = relative.replace("\\", "/").split("/")
    if not parts or any(p in {"", ".", ".."} or ":" in p for p in parts):
        raise ValueError(f"Unsafe relative path: {relative}")
    path = target.joinpath(*parts)
    path.resolve().relative_to(target.resolve())
    for candidate in [path, *path.parents]:
        if candidate == target.parent:
            break
        if is_link(candidate):
            raise ValueError(f"Refusing linked installation path: {candidate}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Destination is not a regular file: {relative}")
    return path


def read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def agent_selection(value: object, *, unique: bool = False) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise ValueError("Agents must be a nonempty list of supported strings")
    if set(value) - AGENTS:
        raise ValueError("Unknown agent selection")
    if unique and len(value) != len(set(value)):
        raise ValueError("State agents must be unique")
    return sorted(set(value))


def validate_settings(settings: dict) -> None:
    for field in ("project_language", "chat_language", "sharing_mode", "conventions"):
        if not isinstance(settings.get(field), str):
            raise ValueError(f"Settings {field} must be a string")
    if settings["project_language"] != "English":
        raise ValueError("This distribution requires English project content")
    if not re.fullmatch(r"[A-Za-z][A-Za-z -]{0,40}", settings["chat_language"]):
        raise ValueError("Use an English chat language name")
    if settings["sharing_mode"] not in {"private", "team"} or settings["conventions"] not in {"owner", "standard"}:
        raise ValueError("Invalid sharing mode or conventions")
    for field in EXTRA_SETTINGS_KEYS.values():
        if field in settings and not isinstance(settings[field], bool):
            raise ValueError(f"Settings {field} must be a boolean")
    upstream = settings.get("upstream")
    if upstream is not None:
        if not isinstance(upstream, dict):
            raise ValueError("Settings upstream must be an object or null")
        for field in ("url", "ref", "source_directory"):
            if field in upstream and not isinstance(upstream[field], str):
                raise ValueError(f"Settings upstream.{field} must be a string")


def validate_state(state: dict, target: Path) -> None:
    if type(state.get("schema")) is not int or state["schema"] != 1:
        raise ValueError("Unsupported installer state schema; expected schema 1")
    if not isinstance(state.get("accepted_version"), str) or not state["accepted_version"].strip():
        raise ValueError("State accepted_version must be a nonempty string")
    agent_selection(state.get("agents"), unique=True)
    records = state.get("files")
    if not isinstance(records, dict):
        raise ValueError("State files must be an object")
    for relative, record in records.items():
        if not isinstance(relative, str) or not isinstance(record, dict):
            raise ValueError("State files must map relative paths to objects")
        safe_path(target, relative)
        for field in ("installed_hash", "source_hash"):
            value = record.get(field)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError(f"Invalid state {field} for {relative}")
        if "local_adaptation" in record and type(record["local_adaptation"]) is not bool:
            raise ValueError(f"State local_adaptation must be boolean for {relative}")


def adapter_owner(relative: str) -> str | None:
    if relative in ENTRIES:
        return ENTRIES[relative]
    if relative.startswith(".claude/skills/"):
        return "claude"
    return next((agent for agent, (_, path) in OPTIONAL.items() if relative == path), None)


def split_ignore(current: str) -> tuple[str, str]:
    if current.count(START) != current.count(END) or current.count(START) > 1:
        raise ValueError("Malformed or repeated AI-KIT ignore markers")
    if START not in current:
        return current, ""
    a, b = current.index(START), current.index(END)
    if b < a:
        raise ValueError("Reversed AI-KIT ignore markers")
    # Markers must occupy complete lines, avoiding matches inside unrelated comments.
    lines = current.splitlines(keepends=True)
    if sum(line.strip() == START for line in lines) != 1 or sum(line.strip() == END for line in lines) != 1:
        raise ValueError("Ignore markers must occupy complete lines")
    end = b + len(END)
    if current[end:end + 2] == "\r\n":
        end += 2
    elif current[end:end + 1] == "\n":
        end += 1
    return current[:a], current[end:]


def module_ignores(target: Path) -> list[str]:
    rules = []
    excluded = {".git", "node_modules", "vendor", "ai-kit", ".agents", ".claude", ".venv"}
    for directory, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if d not in excluded and not is_link(Path(directory) / d)]
        module = Path(directory)
        prefix = module.relative_to(target).as_posix()
        prefix = "" if prefix == "." else prefix + "/"
        # Deliberate Go vendoring wins over a generic Composer exclusion.
        if "composer.json" in files and "go.mod" not in files and not (module / "vendor/modules.txt").exists():
            rules.append("/" + prefix + "vendor/")
        if "config-dist.php" in files and (module / "lib/moodlelib.php").is_file():
            rules.extend(["/" + prefix + "config.php", "/" + prefix + "behat.yml"])
        # Node/Python generated paths are scoped to modules with verified manifests.
        if "package.json" in files:
            rules.extend(prefix + "**/" + name for name in NODE_IGNORES)
        if any(name in files for name in PROFILE_MANIFESTS["PYTHON"]):
            rules.extend(prefix + "**/" + name for name in PYTHON_IGNORES)
            rules.extend("/" + prefix + name for name in PYTHON_ROOT_IGNORES)
    return sorted(set(rules))


def detect_profiles(target: Path) -> dict[str, list[str]]:
    """Map stack profiles to module prefixes evidenced by manifests (unverified draft)."""
    found: dict[str, set[str]] = {}
    excluded = {".git", "node_modules", "vendor", "ai-kit", ".agents", ".claude", ".venv"}
    for directory, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if d not in excluded and not is_link(Path(directory) / d)]
        module = Path(directory)
        prefix = module.relative_to(target).as_posix()
        prefix = "" if prefix == "." else prefix + "/"
        for profile, manifests in PROFILE_MANIFESTS.items():
            if any(name in files for name in manifests):
                found.setdefault(profile, set()).add(prefix)
        if "composer.json" in files:
            found.setdefault("PHP", set()).add(prefix)
            if (module / "artisan").is_file():
                found.setdefault("LARAVEL", set()).add(prefix)
        if "config-dist.php" in files and (module / "lib/moodlelib.php").is_file():
            found.setdefault("MOODLE", set()).add(prefix)
    return {profile: sorted(prefixes) for profile, prefixes in sorted(found.items())}


def project_context_draft(data: bytes, detected: dict[str, list[str]]) -> bytes:
    """Turn installer-detected manifests into draft module-map rows for a fresh context."""
    by_prefix: dict[str, set[str]] = {}
    for profile, prefixes in detected.items():
        for prefix in prefixes:
            by_prefix.setdefault(prefix, set()).add(profile)
    if not by_prefix:
        return data
    text = data.decode("utf-8")
    placeholder = "| Not established | Not established | Not established | None confirmed | Not established |"
    if placeholder not in text:
        return data
    rows = []
    for prefix in sorted(by_prefix):
        label = "/" + prefix.rstrip("/") if prefix else "/"
        profiles = ", ".join(sorted(by_prefix[prefix]))
        rows.append(f"| {label} | installer-detected manifests | not established | "
                    f"{profiles} (suggested, confirm at bootstrap) | not established |")
    return text.replace(placeholder, "\n".join(rows), 1).encode("utf-8")


def merge_ignore(current: str, policy: str, extra: list[str]) -> tuple[str, str]:
    before, after = split_ignore(current)
    outside = before + after
    block = START + "\n" + policy.rstrip() + "\n"
    if extra:
        block += "\n# Verified module-specific generated paths\n" + "\n".join(extra) + "\n"
    block += END + "\n"
    if before and not before.endswith(("\n", "\r")):
        before += "\n"
    return before + block + after, outside


def build_plan(target: Path, *, root: Path = ROOT, mode: str | None = None,
               language: str | None = None, conventions: str | None = None,
               agents: list[str] | None = None, accept_local: list[str] | None = None,
               extras: list[str] | None = None) -> dict:
    target = target.absolute()
    if is_link(target):
        raise ValueError("Refusing a linked target root")
    target = target.resolve()
    if target == root.resolve() or root.resolve() in target.parents:
        raise ValueError("Cannot install an application kit inside the reference distribution")
    if target.exists() and not target.is_dir():
        raise ValueError("Target must be a directory")
    settings_path = safe_path(target, "ai-kit/settings.json")
    settings = read_json(settings_path, read_json(root / "template/ai-kit/settings.json", {}))
    validate_settings(settings)
    state_path = safe_path(target, "ai-kit/.install-state.json")
    state = read_json(state_path, {})
    if state_path.exists():
        validate_state(state, target)
    mode = mode or settings.get("sharing_mode", "private")
    language = language or settings.get("chat_language", "Russian")
    conventions = conventions or settings.get("conventions", "owner")
    agents = agent_selection(agents if agents is not None else state.get("agents", ["codex"]))
    if accept_local is not None and (not isinstance(accept_local, list) or
                                     any(not isinstance(path, str) for path in accept_local)):
        raise ValueError("Accept-local paths must be a list of strings")
    accept = set(accept_local or [])
    enabled_extras = set(extras or [])
    if enabled_extras - EXTRAS:
        raise ValueError("Unknown install extras: " + ", ".join(sorted(enabled_extras - EXTRAS)))
    for name, key in EXTRA_SETTINGS_KEYS.items():
        if name not in enabled_extras and settings.get(key) is True:
            enabled_extras.add(name)
    for name, key in EXTRA_SETTINGS_KEYS.items():
        if name in enabled_extras:
            settings[key] = True
    settings.update(sharing_mode=mode, chat_language=language, conventions=conventions)
    validate_settings(settings)
    detected = detect_profiles(target)
    incoming: dict[str, bytes] = {}
    for src in sorted((root / "template").rglob("*")):
        if is_link(src):
            raise ValueError(f"Linked source path: {src}")
        if not src.is_file():
            continue
        relative = src.relative_to(root / "template").as_posix()
        if relative in ENTRIES and ENTRIES[relative] not in agents:
            continue
        if relative in EXTRA_TEMPLATE.values():
            continue
        incoming[relative] = src.read_bytes()
    incoming["ai-kit/settings.json"] = (json.dumps(settings, indent=2) + "\n").encode()
    incoming["ai-kit/VERSION"] = (root / "VERSION").read_bytes()
    incoming["ai-kit/LICENSE"] = (root / "LICENSE").read_bytes()
    if "claude" in agents:
        for relative, data in list(incoming.items()):
            if relative.startswith(".agents/skills/"):
                incoming[relative.replace(".agents/skills/", ".claude/skills/", 1)] = data
    for agent, (src, dst) in OPTIONAL.items():
        if agent in agents:
            incoming[dst] = (root / "integrations" / src).read_bytes()
    for name in sorted(enabled_extras):
        if name in EXTRA_TEMPLATE:
            relative = EXTRA_TEMPLATE[name]
            incoming[relative] = (root / "template" / relative).read_bytes()
        elif name in EXTRA_INTEGRATIONS:
            src, dst = EXTRA_INTEGRATIONS[name]
            incoming[dst] = (root / "integrations" / src).read_bytes()
    claude_settings: dict = {}
    if "guards" in enabled_extras:
        deny = read_json(root / "integrations" / "claude-settings.deny-git.json", {})
        claude_settings.setdefault("permissions", {}).update(deny.get("permissions", {}))
    if "session-start" in enabled_extras:
        claude_settings["hooks"] = {"SessionStart": [{"hooks": [{"type": "command",
                                                                  "command": "cat .agents/hooks/session-start.md"}]}]}
    if "claude" in agents and claude_settings:
        incoming[".claude/settings.json"] = (json.dumps(claude_settings, indent=2) + "\n").encode()
    if accept - incoming.keys() or accept & (OWNED | {"ai-kit/settings.json"}):
        raise ValueError("Accept-local paths must name selected managed instructions")
    records = state.get("files", {})
    if not isinstance(records, dict):
        raise ValueError("Invalid installer state")
    actions, conflicts, preserved, accepted = {}, {}, [], {}
    conflict_local_hashes = {}
    for relative, data in incoming.items():
        path = safe_path(target, relative)
        current = path.read_bytes() if path.exists() else None
        source_hash = digest(data)
        previous = records.get(relative, {})
        if not isinstance(previous, dict):
            raise ValueError("Invalid baseline record")
        if relative in OWNED:
            if current is None:
                if relative == "PROJECT_CONTEXT.md":
                    data = project_context_draft(data, detected)
                actions[relative] = {"data": data, "old": None}
            else:
                preserved.append(relative)
            continue
        if relative in accept:
            if current is None:
                raise ValueError(f"Cannot accept a missing file: {relative}")
            accepted[relative] = {"installed_hash": digest(current), "source_hash": source_hash,
                                  "local_adaptation": True}
            continue
        if relative == "ai-kit/settings.json" or current is None or current == data:
            accepted[relative] = {"installed_hash": source_hash, "source_hash": source_hash}
            if current != data:
                actions[relative] = {"data": data, "old": current}
        elif previous.get("source_hash") == source_hash:
            # No upstream change: retain local adaptations without rewriting them.
            accepted[relative] = previous
            preserved.append(relative)
        elif not previous.get("local_adaptation") and previous.get("installed_hash") == digest(current):
            actions[relative] = {"data": data, "old": current}
            accepted[relative] = {"installed_hash": source_hash, "source_hash": source_hash}
        else:
            conflicts[relative] = data
            conflict_local_hashes[relative] = digest(current)
    ignore_path = safe_path(target, ".gitignore")
    old_ignore = ignore_path.read_bytes() if ignore_path.exists() else None
    merged, outside = merge_ignore((old_ignore or b"").decode("utf-8-sig"),
                                  (root / "templates" / ("gitignore." + mode)).read_text(encoding="utf-8"),
                                  module_ignores(target))
    # Recognized legacy private exclusions cannot be silently removed for team mode.
    legacy = {"AGENTS.md", "/AGENTS.md", "/ai-kit/", "ai-kit/", "/.agents/", "/.agents/skills/",
              "PROJECT_CONTEXT.md", "/PROJECT_CONTEXT.md", "/.claude/", "SKILL.md"}
    warnings = ["Existing ignore rules outside the managed block need project-specific visibility review."]
    if "ci" in enabled_extras and mode == "private":
        warnings.append("The CI check reads installer state that private sharing mode excludes from Git; "
                        "team mode is the intended companion.")
    if "claude" not in agents and ({"guards", "session-start"} & enabled_extras):
        warnings.append("guards/session-start client wiring requires the claude agent selection; "
                        "only the shared files were installed.")
    if mode == "team" and legacy.intersection(line.strip() for line in outside.splitlines()):
        conflicts[".gitignore"] = merged.encode()
        conflict_local_hashes[".gitignore"] = digest(old_ignore) if old_ignore is not None else None
        warnings.append("Remove or reconcile legacy private exclusions explicitly before applying team mode.")
    elif old_ignore != merged.encode():
        actions[".gitignore"] = {"data": merged.encode(), "old": old_ignore}
    retirements = []
    for relative, record in records.items():
        if relative in incoming or relative in OWNED:
            continue
        if safe_path(target, relative).exists():
            # Keep old baseline information even when a path leaves the bundle.
            accepted[relative] = record
            owner = adapter_owner(relative)
            if owner is not None and owner not in agents:
                retirements.append(relative)
            else:
                warnings.append(f"Previously managed path retained without a current source: {relative}")
    if retirements:
        warnings.append("Agent selection replaces the recorded list, but tracked unselected adapters "
                        "remain on disk and may still load. Review/retire the listed files or retain "
                        "their agent selection; accepted files/state will not change.")
    unselected = {path: agent for path, agent in ENTRIES.items()}
    unselected.update({path: agent for agent, (_, path) in OPTIONAL.items()})
    for relative, owner in unselected.items():
        if owner not in agents and relative not in records and safe_path(target, relative).exists():
            warnings.append(f"Untracked unselected {owner} entry may still load: {relative}")
    if "claude" not in agents and (target / ".claude/skills").exists():
        warnings.append("Unselected .claude/skills remains on disk; verify actual client loading "
                        "and review custom/untracked skills before retirement.")
    candidates = {}
    for relative, data in conflicts.items():
        source_hash = digest(data)
        path = "ai-kit/.upstream-cache/candidates/" + source_hash + "/" + relative
        candidate = safe_path(target, path)
        manifest = path + ".metadata.json"
        safe_path(target, manifest)
        exists = candidate.exists()
        matches = digest(candidate.read_bytes()) == source_hash if exists else None
        candidates[relative] = {"path": path, "manifest": manifest, "source_hash": source_hash,
                                "local_hash": conflict_local_hashes[relative],
                                "exists": exists, "matches_source": matches}
        if exists and not matches:
            warnings.append(f"Existing candidate has local edits and will be preserved: {path}")
    new_state = dict(state)
    new_state.update(schema=1, accepted_version=(root / "VERSION").read_text().strip(),
                     agents=agents, files=accepted)
    state_data = (json.dumps(new_state, indent=2, sort_keys=True) + "\n").encode()
    old_state = state_path.read_bytes() if state_path.exists() else None
    if old_state != state_data:
        actions["ai-kit/.install-state.json"] = {"data": state_data, "old": old_state}
    return {"target": target, "mode": mode, "version": new_state["accepted_version"],
            "actions": actions, "conflicts": conflicts, "candidates": candidates,
            "adapter_conflicts": sorted(retirements), "preserved": preserved,
            "detected_profiles": detected, "extras": sorted(enabled_extras), "warnings": warnings}


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".ai-kit-" + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("xb") as stream:
            stream.write(data)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def write_once(path: Path, data: bytes) -> bool:
    """Create exclusively; preserve every existing file, including an edited draft."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stream = path.open("xb")
    except FileExistsError:
        return False
    with stream:
        stream.write(data)
    return True


def needs_review(plan: dict) -> bool:
    return bool(plan["conflicts"] or plan["adapter_conflicts"])


def apply_plan(plan: dict) -> bool:
    target: Path = plan["target"]
    if needs_review(plan):
        for relative, data in plan["conflicts"].items():
            info = plan["candidates"][relative]
            write_once(safe_path(target, info["path"]), data)
            manifest = {"relative_path": relative, "source_hash": info["source_hash"],
                        "local_hash": info["local_hash"], "bundle_version": plan["version"],
                        "created_at": datetime.now(timezone.utc).isoformat()}
            write_once(safe_path(target, info["manifest"]),
                       (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
        return False
    # Recheck every planned write before modifying any project file.
    for relative, action in plan["actions"].items():
        path = safe_path(target, relative)
        actual = path.read_bytes() if path.exists() else None
        if actual != action["old"]:
            raise ValueError(f"File changed after preview: {relative}")
    if not plan["actions"]:
        return True
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    # Prepare all existing-file backups before writing any instruction.
    for relative, action in plan["actions"].items():
        if action["old"] is not None:
            backup = safe_path(target, "ai-kit/.upstream-cache/backups/" + stamp + "/" + relative)
            atomic_write(backup, action["old"])
    completed = []
    try:
        for relative, action in plan["actions"].items():
            path = safe_path(target, relative)
            actual = path.read_bytes() if path.exists() else None
            if actual != action["old"]:
                raise ValueError(f"Concurrent modification: {relative}")
            atomic_write(path, action["data"])
            completed.append(relative)
    except (OSError, ValueError):
        # Restore only files that still contain our exact write.
        for relative in reversed(completed):
            path = safe_path(target, relative)
            action = plan["actions"][relative]
            if path.read_bytes() == action["data"]:
                if action["old"] is None:
                    path.unlink()
                else:
                    atomic_write(path, action["old"])
        raise
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mode", choices=["private", "team"])
    parser.add_argument("--chat-language")
    parser.add_argument("--conventions", choices=["owner", "standard"])
    parser.add_argument("--agent", choices=sorted(AGENTS), action="append")
    parser.add_argument("--accept-local", action="append", default=[],
                        help="Record an explicitly reviewed semantic merge of a managed path")
    parser.add_argument("--with-session-start", action="store_true",
                        help="Install the session-start hook file and client wiring")
    parser.add_argument("--with-guards", action="store_true",
                        help="Install client deny rules for Git write operations")
    parser.add_argument("--with-ci", action="store_true",
                        help="Install the self-contained AI-KIT project check workflow")
    args = parser.parse_args(argv)
    extras = [name for name, flag in (("session-start", args.with_session_start),
                                      ("guards", args.with_guards),
                                      ("ci", args.with_ci)) if flag]
    try:
        plan = build_plan(args.target, mode=args.mode, language=args.chat_language,
                          conventions=args.conventions, agents=args.agent, accept_local=args.accept_local,
                          extras=extras)
        print(json.dumps({"target": str(plan["target"]), "version": plan["version"], "mode": plan["mode"],
                          "preview": not args.apply, "writes": sorted(plan["actions"]),
                          "conflicts": sorted(plan["conflicts"]), "preserved": sorted(plan["preserved"]),
                          "candidates": plan["candidates"], "adapter_conflicts": plan["adapter_conflicts"],
                          "detected_profiles": plan["detected_profiles"], "extras": plan["extras"],
                          "warnings": plan["warnings"]}, indent=2))
        if args.apply:
            apply_plan(plan)
        return 2 if needs_review(plan) else 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Installation refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
