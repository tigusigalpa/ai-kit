"""Conservative, offline AI-KIT installation and unchanged-baseline upgrades."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
START = "# BEGIN AI-KIT MANAGED"
END = "# END AI-KIT MANAGED"
OWNED = {"README.md", "PROJECT_CONTEXT.md", "WIKI.md", "CHANGELOG.md", "docs/DECISIONS.md",
         "docs/adr/0000-template.md"}
ENTRIES = {"CLAUDE.md": "claude", "KIMI.md": "kimi", "MANUS.md": "manus"}
AGENTS = {"codex", "claude", "kimi", "manus", "copilot", "cursor", "aider"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(target: Path, relative: str) -> Path:
    parts = relative.replace("\\", "/").split("/")
    if not parts or any(p in {"", ".", ".."} or ":" in p for p in parts):
        raise ValueError(f"Unsafe relative path: {relative}")
    path = target.joinpath(*parts)
    path.resolve().relative_to(target.resolve())
    for candidate in [path, *path.parents]:
        if candidate == target.parent:
            break
        if candidate.is_symlink() or (hasattr(candidate, "is_junction") and candidate.is_junction()):
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
        dirs[:] = [d for d in dirs if d not in excluded and not (Path(directory) / d).is_symlink()]
        module = Path(directory)
        prefix = module.relative_to(target).as_posix()
        prefix = "" if prefix == "." else prefix + "/"
        # Deliberate Go vendoring wins over a generic Composer exclusion.
        if "composer.json" in files and "go.mod" not in files and not (module / "vendor/modules.txt").exists():
            rules.append("/" + prefix + "vendor/")
        if "config-dist.php" in files and (module / "lib/moodlelib.php").is_file():
            rules.extend(["/" + prefix + "config.php", "/" + prefix + "behat.yml"])
    return sorted(set(rules))


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
               agents: list[str] | None = None, accept_local: list[str] | None = None) -> dict:
    target = target.absolute()
    if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
        raise ValueError("Refusing a linked target root")
    target = target.resolve()
    if target == root.resolve() or root.resolve() in target.parents:
        raise ValueError("Cannot install an application kit inside the reference distribution")
    if target.exists() and not target.is_dir():
        raise ValueError("Target must be a directory")
    settings_path = safe_path(target, "ai-kit/settings.json")
    settings = read_json(settings_path, read_json(root / "template/ai-kit/settings.json", {}))
    state_path = safe_path(target, "ai-kit/.install-state.json")
    state = read_json(state_path, {})
    mode = mode or settings.get("sharing_mode", "private")
    language = language or settings.get("chat_language", "Russian")
    conventions = conventions or settings.get("conventions", "owner")
    agents = sorted(set(agents or state.get("agents", ["codex"])))
    accept = set(accept_local or [])
    if mode not in {"private", "team"} or conventions not in {"owner", "standard"}:
        raise ValueError("Invalid sharing mode or conventions")
    if not re.fullmatch(r"[A-Za-z][A-Za-z -]{0,40}", language):
        raise ValueError("Use an English language name")
    if set(agents) - AGENTS:
        raise ValueError("Unknown agent selection")
    settings.update(sharing_mode=mode, chat_language=language, conventions=conventions)
    if settings.get("project_language") != "English":
        raise ValueError("Project language requires explicit rule adaptation; this distribution uses English")
    incoming: dict[str, bytes] = {}
    for src in sorted((root / "template").rglob("*")):
        if not src.is_file():
            continue
        if src.is_symlink():
            raise ValueError(f"Linked source file: {src}")
        relative = src.relative_to(root / "template").as_posix()
        if relative in ENTRIES and ENTRIES[relative] not in agents:
            continue
        incoming[relative] = src.read_bytes()
    incoming["ai-kit/settings.json"] = (json.dumps(settings, indent=2) + "\n").encode()
    incoming["ai-kit/VERSION"] = (root / "VERSION").read_bytes()
    incoming["ai-kit/LICENSE"] = (root / "LICENSE").read_bytes()
    if "claude" in agents:
        for relative, data in list(incoming.items()):
            if relative.startswith(".agents/skills/"):
                incoming[relative.replace(".agents/skills/", ".claude/skills/", 1)] = data
    optional = {"copilot": ("copilot-instructions.md", ".github/copilot-instructions.md"),
                "cursor": ("ai-kit.mdc", ".cursor/rules/ai-kit.mdc"),
                "aider": ("CONVENTIONS.md", "CONVENTIONS.md")}
    for agent, (src, dst) in optional.items():
        if agent in agents:
            incoming[dst] = (root / "integrations" / src).read_bytes()
    if accept - incoming.keys() or accept & (OWNED | {"ai-kit/settings.json"}):
        raise ValueError("Accept-local paths must name selected managed instructions")
    records = state.get("files", {})
    if not isinstance(records, dict):
        raise ValueError("Invalid installer state")
    actions, conflicts, preserved, accepted = {}, {}, [], {}
    for relative, data in incoming.items():
        path = safe_path(target, relative)
        current = path.read_bytes() if path.exists() else None
        source_hash = digest(data)
        previous = records.get(relative, {})
        if not isinstance(previous, dict):
            raise ValueError("Invalid baseline record")
        if relative in OWNED:
            if current is None:
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
    ignore_path = safe_path(target, ".gitignore")
    old_ignore = ignore_path.read_bytes() if ignore_path.exists() else None
    merged, outside = merge_ignore((old_ignore or b"").decode("utf-8-sig"),
                                  (root / "templates" / ("gitignore." + mode)).read_text(encoding="utf-8"),
                                  module_ignores(target))
    # Recognized legacy private exclusions cannot be silently removed for team mode.
    legacy = {"AGENTS.md", "/AGENTS.md", "/ai-kit/", "ai-kit/", "/.agents/", "/.agents/skills/",
              "PROJECT_CONTEXT.md", "/PROJECT_CONTEXT.md", "/.claude/", "SKILL.md"}
    warnings = ["Existing ignore rules outside the managed block need project-specific visibility review."]
    if mode == "team" and legacy.intersection(line.strip() for line in outside.splitlines()):
        conflicts[".gitignore"] = merged.encode()
        warnings.append("Remove or reconcile legacy private exclusions explicitly before applying team mode.")
    elif old_ignore != merged.encode():
        actions[".gitignore"] = {"data": merged.encode(), "old": old_ignore}
    new_state = {"schema": 1, "accepted_version": (root / "VERSION").read_text().strip(),
                 "agents": agents, "files": accepted}
    state_data = (json.dumps(new_state, indent=2, sort_keys=True) + "\n").encode()
    old_state = state_path.read_bytes() if state_path.exists() else None
    if old_state != state_data:
        actions["ai-kit/.install-state.json"] = {"data": state_data, "old": old_state}
    return {"target": target, "mode": mode, "version": new_state["accepted_version"],
            "actions": actions, "conflicts": conflicts, "preserved": preserved, "warnings": warnings}


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


def apply_plan(plan: dict) -> bool:
    target: Path = plan["target"]
    if plan["conflicts"]:
        for relative, data in plan["conflicts"].items():
            atomic_write(safe_path(target, "ai-kit/.upstream-cache/candidates/" + relative), data)
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
    args = parser.parse_args(argv)
    try:
        plan = build_plan(args.target, mode=args.mode, language=args.chat_language,
                          conventions=args.conventions, agents=args.agent, accept_local=args.accept_local)
        print(json.dumps({"target": str(plan["target"]), "version": plan["version"], "mode": plan["mode"],
                          "preview": not args.apply, "writes": sorted(plan["actions"]),
                          "conflicts": sorted(plan["conflicts"]), "preserved": sorted(plan["preserved"]),
                          "warnings": plan["warnings"]}, indent=2))
        if args.apply:
            apply_plan(plan)
        return 2 if plan["conflicts"] else 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Installation refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
