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
         "docs/adr/0000-template.md", "ai-kit/project.json"}
AGENT_REGISTRY_PATH = "integrations/agents.json"
PROFILE_MANIFESTS = {
    "GO": ("go.mod",),
    "PYTHON": ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"),
    "JAVASCRIPT": ("package.json",),
}
FILAMENT_PACKAGES = {"filament/filament", "filament/forms", "filament/tables", "filament/schemas",
                     "filament/actions", "filament/widgets", "filament/infolists", "filament/notifications"}
EXTRAS = {"session-start", "guards", "data-guards", "native-settings", "scoped-rules", "ci", "security-audit", "strix",
          "context7", "web-design", "orchestration", "uuid", "claude-github"}
EXTRA_TEMPLATE = {"session-start": (".agents/hooks/session-start.md", ".agents/hooks/session-start.sh")}
EXTRA_INTEGRATIONS = {"ci": ("ai-kit-check.yml", ".github/workflows/ai-kit.yml")}
EXTRA_SETTINGS_KEYS = {"session-start": "session_start", "guards": "guards", "data-guards": "data_guards",
                       "native-settings": "native_settings", "scoped-rules": "scoped_rules", "ci": "ci",
                       "security-audit": "security_audit", "strix": "strix", "context7": "context7",
                       "web-design": "web_design", "orchestration": "orchestration",
                       "uuid": "uuid", "claude-github": "claude_github"}
SECURITY_AUDIT_SKILL = ".agents/skills/security-audit/"
SECURITY_AUDIT_PACKAGE = "ai-kit/vendor/security-audit/"
SECURITY_AUDIT_MANIFEST = "integrations/security-audit.json"
STRIX_SKILLS = ("api-security-testing", "application-security-testing", "ci-security-scanning-with-strix",
                "find-security-vulnerabilities-in-code", "fix-security-vulnerabilities-with-strix",
                "managed-pentesting-with-strix", "owasp-top-10-testing", "penetration-testing-with-strix",
                "web-app-penetration-testing")
OPTIONAL_SKILLS = {
    "security-audit": {"repository": "https://github.com/cloudflare/security-audit-skill",
                       "source_directory": "skills/security-audit", "license": "MIT", "depth": 1,
                       "required": {"SKILL.md", "LICENSE", "RECONNAISSANCE.md", "HUNTING.md", "ATTACK-CLASSES.md",
                                    "VALIDATION-AND-REPORTING.md", "report-schema.json", "validate-findings.cjs",
                                    "validate-coverage-ledger.cjs"}},
    "strix": {"repository": "https://github.com/usestrix/strix", "source_directory": "skills",
              "license": "Apache-2.0", "depth": 2,
              "required": {"LICENSE", *(name + "/SKILL.md" for name in STRIX_SKILLS)}},
}
# Local documentation workflows share selection/preservation behavior, without an upstream payload.
OPTIONAL_ENTRY_POINTS = {**{name: (name,) for name in OPTIONAL_SKILLS}, "context7": ("context7-docs",),
                         "web-design": ("web-design", "laravel-blade-ui", "ui-review", "design-extract")}
OPTIONAL_DOCUMENTS = {"orchestration": ("ai-kit/orchestration.json",), "web-design": ("docs/design/BRIEF.md", "docs/design/SYSTEM.md", "docs/design/ACCEPTANCE.md")}
OPTIONAL_RESOURCES = {"uuid": ("ai-kit/UUID.md",), "claude-github": ("ai-kit/CLAUDE-GITHUB.md",),
                     "orchestration": ("ai-kit/ORCHESTRATION.md",), "web-design": ("ai-kit/WEB-DESIGN.md", "ai-kit/web-design/LARAVEL.md",
                                    "ai-kit/web-design/LIBRARIES.md", "ai-kit/web-design/TOOLS.md",
                                    "ai-kit/web-design/REVIEW.md")}
# Presets set every extra they manage on or off; explicit --with-* flags add on top. CI is left
# to an explicit choice, as are optional integrations. A preset mode of None keeps the sharing mode.
PRESET_EXTRAS = ("session-start", "guards", "data-guards", "native-settings", "scoped-rules")
PRESETS = {
    "minimal": {"mode": None, "extras": ()},
    "solo": {"mode": "private", "extras": ("session-start", "native-settings", "scoped-rules")},
    "team": {"mode": "team", "extras": ("session-start", "guards", "native-settings", "scoped-rules")},
    "strict": {"mode": None, "extras": PRESET_EXTRAS},
}
DEFAULT_AGENTS = ("codex",)
# Installer options that persist a choice: argparse destination -> ai-kit/settings.json key.
OPTION_SETTINGS = {"mode": "sharing_mode", "chat_language": "chat_language", "conventions": "conventions",
                   "docker_cleanup": "docker_cleanup"}
CLAUDE_SETTINGS = ".claude/settings.json"
CLAUDE_LOCAL_SETTINGS = ".claude/settings.local.json"
GUARDS_SOURCE = "claude-settings.git-ask.json"
DATA_GUARDS_SOURCE = "claude-settings.data-ask.json"
SECRETS_SOURCE = "agent-secrets.ignore"
SCOPED_FORMATS = {"claude-paths": ".md", "cline-paths": ".md", "cursor-globs": ".mdc",
                  "copilot-applyto": ".instructions.md", "windsurf-trigger": ".md", "devin-trigger": ".md"}
CLAUDE_SCALAR_ENTRIES = {"attribution.commit"}
MODULE_PATH = re.compile(r"/(?:[A-Za-z0-9_-][A-Za-z0-9._-]*/)*")
# Recorded commands become allow rules only when they are one plain command.
UNSAFE_COMMAND = re.compile(r"[;&|<>`$()*\\\"'\r\n]")
UPSTREAM_TEST_FILE = re.compile(r"\.test\.[cm]?[jt]s$")
DOCKER_CLEANUP_MODES = ("maximum", "keep-cache")
# tr strips CR so a CRLF checkout of the hook script still runs under sh.
SESSION_START_COMMAND = "tr -d '\\r' < \"$CLAUDE_PROJECT_DIR/.agents/hooks/session-start.sh\" | sh"
# Entries written by v0.3.6-v0.4.6, which managed the whole client settings file.
LEGACY_CLAUDE_ENTRIES = {"permissions.deny": ["Bash(git commit *)", "Bash(git push *)"],
                         "hooks.SessionStart": ["cat .agents/hooks/session-start.md"]}
NODE_MANAGERS = ("npm", "pnpm", "yarn", "bun")
NODE_LOCKFILES = (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lock", "bun"),
                  ("bun.lockb", "bun"), ("package-lock.json", "npm"), ("npm-shrinkwrap.json", "npm"))
PYTHON_RUNNERS = (("uv.lock", "uv run "), ("poetry.lock", "poetry run "))
PYTHON_TOOL_FILES = ("pyproject.toml", "setup.cfg", "tox.ini", "requirements.txt", "requirements-dev.txt",
                     "requirements_dev.txt", "dev-requirements.txt", "requirements-test.txt",
                     "test-requirements.txt")
NODE_IGNORES = ("node_modules/", ".npm/", ".pnpm-store/", ".yarn/cache/", ".yarn/unplugged/",
                ".yarn/install-state.gz", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*",
                "pnpm-debug.log*", ".next/", ".nuxt/", ".svelte-kit/", ".turbo/", ".parcel-cache/")
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
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", None) in {
        getattr(stat, "IO_REPARSE_TAG_SYMLINK", -1),
        getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", -2),
    }


def safe_path(target: Path, relative: str, *, allow_obstructions: bool = False) -> Path:
    """Guard lexical/link boundaries; only read-only audits may allow file/directory obstructions."""
    parts = relative.replace("\\", "/").split("/")
    if not parts or any(p in {"", ".", ".."} or ":" in p for p in parts):
        raise ValueError(f"Unsafe relative path: {relative}")
    path = target.joinpath(*parts)
    path.resolve().relative_to(target.resolve())
    obstruction = None
    for candidate in [path, *path.parents]:
        if candidate == target.parent:
            break
        if is_link(candidate):
            raise ValueError(f"Refusing linked installation path: {candidate}")
        if candidate != path and candidate.exists() and not candidate.is_dir():
            obstruction = candidate
    if obstruction is not None and not allow_obstructions:
        raise NotADirectoryError(f"Installation parent is not a directory: {obstruction}")
    if path.exists() and not path.is_file() and not allow_obstructions:
        raise ValueError(f"Destination is not a regular file: {relative}")
    return path


def read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def load_agent_registry(root: Path = ROOT) -> dict:
    """Load and validate the data-driven agent registry (integrations/agents.json)."""
    data = json.loads((root / AGENT_REGISTRY_PATH).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or type(data.get("schema")) is not int or data["schema"] != 1:
        raise ValueError("Unsupported agent registry schema; expected schema 1")
    agents = data.get("agents")
    if not isinstance(agents, dict) or not agents:
        raise ValueError("Agent registry must declare a nonempty agents object")
    names: set[str] = set()
    entries: dict[str, str] = {}
    optional: dict[str, list[tuple[str, str]]] = {}
    skills_copies: dict[str, str] = {}
    detect: dict[str, list[str]] = {}
    scoped_rules: dict[str, dict[str, str]] = {}
    ignore_files: dict[str, str] = {}
    metadata: dict[str, dict] = {}
    for name, spec in agents.items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            raise ValueError(f"Invalid agent name: {name}")
        if not isinstance(spec, dict):
            raise ValueError(f"Invalid agent spec for {name}")
        names.add(name)
        for entry in spec.get("entries", []):
            if not isinstance(entry, str) or not entry:
                raise ValueError(f"Invalid entry for {name}")
            if entry in entries:
                raise ValueError(f"Entry owned by multiple agents: {entry}")
            entries[entry] = name
        for item in spec.get("optional", []):
            if not isinstance(item, dict):
                raise ValueError(f"Invalid optional entry for {name}")
            source, destination = item.get("source"), item.get("destination")
            if not isinstance(source, str) or not source or not isinstance(destination, str) or not destination:
                raise ValueError(f"Invalid optional source/destination for {name}")
            optional.setdefault(name, []).append((source, destination))
        prefix = spec.get("skills_copy")
        if prefix is not None:
            if not isinstance(prefix, str) or not prefix.startswith(".") or not prefix.endswith("/"):
                raise ValueError(f"Invalid skills_copy prefix for {name}")
            skills_copies[name] = prefix
        markers = spec.get("detect", [])
        if not isinstance(markers, list) or any(
                not isinstance(marker, str) or
                not re.fullmatch(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*/?", marker) or
                any(part in {".", ".."} for part in marker.rstrip("/").split("/")) for marker in markers):
            raise ValueError(f"Invalid detect markers for {name}")
        if markers:
            detect[name] = markers
        scoped = spec.get("scoped_rules")
        if scoped is not None:
            directory = scoped.get("directory") if isinstance(scoped, dict) else None
            if (not isinstance(directory, str) or not re.fullmatch(r"\.[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*/",
                                                                   directory)
                    or ".." in directory.split("/") or scoped.get("format") not in SCOPED_FORMATS):
                raise ValueError(f"Invalid scoped_rules for {name}")
            scoped_rules[name] = {"directory": directory, "format": scoped["format"]}
        ignore_file = spec.get("ignore_file")
        if ignore_file is not None:
            if not isinstance(ignore_file, str) or not re.fullmatch(r"\.[A-Za-z0-9._-]+", ignore_file):
                raise ValueError(f"Invalid ignore_file for {name}")
            ignore_files[name] = ignore_file
        documentation = spec.get("documentation")
        if not isinstance(documentation, dict) or set(documentation) != {
                "status", "verified_documentation_date", "sources", "activation"}:
            raise ValueError(f"Invalid documentation metadata for {name}")
        status = documentation["status"]
        verified = documentation["verified_documentation_date"]
        sources = documentation["sources"]
        activation = documentation["activation"]
        if status not in {"verified", "unverified"}:
            raise ValueError(f"Invalid documentation status for {name}")
        if verified is not None and (not isinstance(verified, str) or
                                     not re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified)):
            raise ValueError(f"Invalid documentation date for {name}")
        if not isinstance(sources, list) or any(not isinstance(source, str) or not source.startswith("https://")
                                                for source in sources):
            raise ValueError(f"Invalid documentation sources for {name}")
        if activation not in {"verified", "unverified", "not-applicable"}:
            raise ValueError(f"Invalid activation status for {name}")
        if status == "verified" and (verified is None or not sources):
            raise ValueError(f"Verified documentation needs date and sources for {name}")
        metadata[name] = {"status": status, "verified_documentation_date": verified,
                          "sources": sources, "activation": activation}
    return {"names": names, "entries": entries, "optional": optional,
            "skills_copies": skills_copies, "detect": detect, "scoped_rules": scoped_rules,
            "ignore_files": ignore_files, "metadata": metadata}


def detect_agents(target: Path, registry: dict) -> dict[str, list[str]]:
    """Map clients to existing native files/directories suggesting they are in use (unverified)."""
    found: dict[str, list[str]] = {}
    for agent, markers in sorted(registry["detect"].items()):
        evidence = []
        for marker in markers:
            path = target.joinpath(*marker.rstrip("/").split("/"))
            if is_link(path):
                continue
            # A trailing slash marks a directory; other markers may be files or directories.
            if path.is_dir() if marker.endswith("/") else path.exists():
                evidence.append(marker)
        if evidence:
            found[agent] = evidence
    return found


def agent_selection(value: object, agents: set[str], *, unique: bool = False) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise ValueError("Agents must be a nonempty list of supported strings")
    if set(value) - agents:
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
    chat_language = settings["chat_language"]
    if not chat_language.strip() or len(chat_language) > 60 or any(ord(ch) < 32 for ch in chat_language):
        raise ValueError("Chat language must be a nonempty name up to 60 characters without control characters")
    if settings["sharing_mode"] not in {"private", "team"} or settings["conventions"] not in {"owner", "standard"}:
        raise ValueError("Invalid sharing mode or conventions")
    for field in EXTRA_SETTINGS_KEYS.values():
        if field in settings and not isinstance(settings[field], bool):
            raise ValueError(f"Settings {field} must be a boolean")
    if "docker_cleanup" in settings and settings["docker_cleanup"] not in DOCKER_CLEANUP_MODES:
        raise ValueError("Settings docker_cleanup must be one of: " + ", ".join(DOCKER_CLEANUP_MODES))
    upstream = settings.get("upstream")
    if upstream is not None:
        if not isinstance(upstream, dict):
            raise ValueError("Settings upstream must be an object or null")
        for field in ("url", "ref", "source_directory"):
            if field in upstream and not isinstance(upstream[field], str):
                raise ValueError(f"Settings upstream.{field} must be a string")


def upstream_skill_files(name: str, root: Path = ROOT) -> dict[str, bytes]:
    """Verify a bounded upstream reference tree and return its offline install payload."""
    spec = OPTIONAL_SKILLS[name]
    package_prefix = "ai-kit/vendor/" + name + "/"
    with safe_path(root, "integrations/" + name + ".json").open("rb") as stream:
        manifest_bytes = stream.read(1024 * 1024 + 1)
    if len(manifest_bytes) > 1024 * 1024:
        raise ValueError(f"Oversized {name} upstream manifest")
    manifest = json.loads(manifest_bytes)
    if (not isinstance(manifest, dict) or type(manifest.get("schema")) is not int
            or manifest["schema"] != 1
            or manifest.get("repository") != spec["repository"]
            or not isinstance(manifest.get("revision"), str)
            or not re.fullmatch(r"[0-9a-f]{40}", manifest["revision"])
            or manifest.get("source_directory") != spec["source_directory"]
            or manifest.get("license") != spec["license"]):
        raise ValueError(f"Invalid {name} upstream identity")
    files = manifest.get("files")
    if not isinstance(files, dict) or not spec["required"] <= files.keys() or len(files) > 100:
        raise ValueError(f"Incomplete {name} upstream manifest")
    prefixes: dict[str, str] = {}
    reserved = {"con", "prn", "aux", "nul", *("com" + str(i) for i in range(1, 10)),
                *("lpt" + str(i) for i in range(1, 10))}
    for filename in files:
        parts = filename.split("/") if isinstance(filename, str) else []
        if (not parts or len(parts) > spec["depth"] or filename.casefold() == "upstream.json"
                or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", part)
                       or part.endswith(".") or part.split(".")[0].casefold() in reserved for part in parts)):
            raise ValueError(f"Unsafe {name} upstream filename")
        for i in range(1, len(parts) + 1):
            prefix = "/".join(parts[:i])
            folded = prefix.casefold()
            if folded in prefixes and prefixes[folded] != prefix:
                raise ValueError(f"Unsafe {name} upstream filename alias")
            prefixes[folded] = prefix
    package = safe_path(root, "template/" + package_prefix + "LICENSE").parent
    actual = set()
    pending = [package]
    while pending:
        directory = pending.pop()
        for path in directory.iterdir():
            relative = path.relative_to(package).as_posix()
            if is_link(path):
                raise ValueError(f"Linked {name} upstream entry: {relative}")
            if path.is_dir() and len(path.relative_to(package).parts) < spec["depth"]:
                if not any(filename.startswith(relative + "/") for filename in files):
                    raise ValueError(f"{name} upstream directories differ from the manifest")
                pending.append(path)
            elif path.is_file():
                actual.add(relative)
            else:
                raise ValueError(f"Non-regular {name} upstream entry: {relative}")
    if actual != set(files):
        raise ValueError(f"{name} upstream files differ from the manifest")
    incoming: dict[str, bytes] = {}
    total = 0
    for filename, record in sorted(files.items()):
        if (not isinstance(record, dict) or type(record.get("size")) is not int
                or not 0 <= record["size"] <= 1024 * 1024
                or record.get("git_mode") not in ("100644", "100755")
                or any(not isinstance(record.get(field), str)
                       or not re.fullmatch(r"[0-9a-f]{" + str(length) + "}", record[field])
                       for field, length in (("sha256", 64), ("git_blob", 40)))):
            raise ValueError(f"Invalid {name} upstream record: {filename}")
        source = safe_path(root, "template/" + package_prefix + filename)
        with source.open("rb") as stream:
            data = stream.read(1024 * 1024 + 1)
        total += len(data)
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data,
                            usedforsecurity=False).hexdigest()
        if (total > 5 * 1024 * 1024 or len(data) != record["size"]
                or digest(data) != record["sha256"] or blob != record["git_blob"]):
            raise ValueError(f"{name} upstream integrity mismatch: {filename}")
        if UPSTREAM_TEST_FILE.search(filename):
            # Verified with the payload, but never installed: host test runners would collect it.
            continue
        incoming[package_prefix + filename] = data
    incoming[package_prefix + "UPSTREAM.json"] = manifest_bytes
    return incoming


def validate_state(state: dict, target: Path, agents: set[str] | None = None, *, allow_obstructions: bool = False) -> None:
    if type(state.get("schema")) is not int or state["schema"] != 1:
        raise ValueError("Unsupported installer state schema; expected schema 1")
    if not isinstance(state.get("accepted_version"), str) or not state["accepted_version"].strip():
        raise ValueError("State accepted_version must be a nonempty string")
    agent_selection(state.get("agents"), agents if agents is not None else load_agent_registry()["names"],
                    unique=True)
    records = state.get("files")
    if not isinstance(records, dict):
        raise ValueError("State files must be an object")
    for relative, record in records.items():
        if not isinstance(relative, str) or not isinstance(record, dict):
            raise ValueError("State files must map relative paths to objects")
        if allow_obstructions:
            safe_path(target, relative, allow_obstructions=True)
        else:
            safe_path(target, relative)
        for field in ("installed_hash", "source_hash"):
            value = record.get(field)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError(f"Invalid state {field} for {relative}")
        if "local_adaptation" in record and type(record["local_adaptation"]) is not bool:
            raise ValueError(f"State local_adaptation must be boolean for {relative}")
    managed = state.get("managed_json", {})
    if not isinstance(managed, dict):
        raise ValueError("State managed_json must be an object")
    for relative, entries in managed.items():
        if not isinstance(relative, str) or not isinstance(entries, dict):
            raise ValueError("State managed_json must map relative paths to objects")
        if allow_obstructions:
            safe_path(target, relative, allow_obstructions=True)
        else:
            safe_path(target, relative)
        for key, values in entries.items():
            if (not isinstance(key, str) or not (re.fullmatch(r"(?:permissions|hooks)\.[A-Za-z]+", key)
                                                or key in CLAUDE_SCALAR_ENTRIES) or
                    not isinstance(values, list) or any(not isinstance(value, str) for value in values)):
                raise ValueError(f"Invalid state managed_json entry for {relative}")
            if key in CLAUDE_SCALAR_ENTRIES and values != [""]:
                raise ValueError(f"Invalid scalar ownership for {relative}: {key}")


def merge_managed_json(current: dict, remove: dict[str, list[str]], add: dict[str, list[str]]) -> dict:
    """Drop stale AI-KIT-owned entries and add missing ones; all other content is preserved.

    Keys name a settings list: permissions.<list> holds rule strings, hooks.<event> holds
    command hook groups identified by their command. Known scalar keys use a singleton list
    in ownership state; conflicting user values are preserved and reported for review.
    """
    result = json.loads(json.dumps(current))
    for key, values in remove.items():
        section, name = key.split(".", 1)
        if key in CLAUDE_SCALAR_ENTRIES:
            container = result.get(section)
            if key not in add and isinstance(container, dict) and container.get(name) in values:
                del container[name]
                if not container:
                    del result[section]
            continue
        stale = [value for value in values if value not in add.get(key, [])]
        container = result.get(section)
        if not stale or not isinstance(container, dict) or not isinstance(container.get(name), list):
            continue
        items = container[name]
        kept = []
        for item in items:
            if section != "hooks":
                if item not in stale:
                    kept.append(item)
                continue
            handlers = item.get("hooks") if isinstance(item, dict) else None
            if isinstance(handlers, list):
                remaining = [h for h in handlers if not (isinstance(h, dict) and h.get("command") in stale)]
                if len(remaining) != len(handlers):
                    if not remaining:
                        continue
                    item = {**item, "hooks": remaining}
            kept.append(item)
        if kept == items:
            continue
        container[name] = kept
        if not kept:
            del container[name]
            if not container:
                del result[section]
    for key, values in add.items():
        section, name = key.split(".", 1)
        container = result.setdefault(section, {})
        if not isinstance(container, dict):
            raise ValueError(f"{section} must be an object")
        if key in CLAUDE_SCALAR_ENTRIES:
            if values != [""]:
                raise ValueError(f"Unsupported scalar value: {key}")
            if name in container and container[name] != values[0]:
                raise ValueError(f"User setting conflicts with {key}; review the candidate")
            container[name] = values[0]
            continue
        items = container.setdefault(name, [])
        if not isinstance(items, list):
            raise ValueError(f"{key} must be a list")
        if section == "hooks":
            present = set()
            for group in items:
                handlers = group.get("hooks") if isinstance(group, dict) else None
                for handler in handlers if isinstance(handlers, list) else []:
                    if isinstance(handler, dict):
                        present.add(handler.get("command"))
            for value in values:
                if value not in present:
                    items.append({"hooks": [{"type": "command", "command": value}]})
        else:
            for value in values:
                if value not in items:
                    items.append(value)
    return result


def project_modules(target: Path, facts: dict) -> tuple[list[dict], list[str]]:
    """Module facts for generated client configuration: project.json when filled, else detection."""
    warnings: list[str] = []
    source = facts["modules"]
    path = target / "ai-kit" / "project.json"
    if path.is_file() and not is_link(path):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict) and isinstance(value.get("modules"), list) and value["modules"]:
                source = value["modules"]
        except (OSError, ValueError, UnicodeError):
            warnings.append("ai-kit/project.json is unreadable; generated client configuration uses detection.")
    modules = []
    for item in source:
        module_path = item.get("path") if isinstance(item, dict) else None
        if isinstance(module_path, str) and not module_path.endswith("/"):
            module_path += "/"
        if not isinstance(module_path, str) or not MODULE_PATH.fullmatch(module_path):
            warnings.append(f"Skipping module path unsupported by generated client configuration: {module_path!r}")
            continue
        profiles = item.get("profiles") if isinstance(item.get("profiles"), list) else []
        commands = item.get("commands") if isinstance(item.get("commands"), dict) else {}
        modules.append({"path": module_path,
                        "profiles": sorted({p for p in profiles if isinstance(p, str) and re.fullmatch(r"[A-Z]+", p)}),
                        "commands": {k: v for k, v in commands.items() if isinstance(k, str) and isinstance(v, str)}})
    return modules, warnings


def secret_patterns(root: Path, modules: list[dict]) -> list[str]:
    """Gitignore-style secret patterns: the shared list plus secrets of detected stacks."""
    text = (root / "templates" / SECRETS_SOURCE).read_text(encoding="utf-8")
    patterns = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    for module in modules:
        prefix = module["path"][1:]
        profiles = set(module["profiles"])
        extra = []
        if profiles & {"PHP", "LARAVEL", "MOODLE"}:
            extra.append("auth.json")
        if "LARAVEL" in profiles:
            extra.append("/" + prefix + "storage/*.key")
        if "MOODLE" in profiles:
            extra.append("/" + prefix + "config.php")
        if "PYTHON" in profiles:
            extra.append(".pypirc")
        patterns.extend(pattern for pattern in extra if pattern not in patterns)
    return patterns


def claude_read_rules(patterns: list[str]) -> list[str]:
    """Convert gitignore patterns to Claude Code Read rules; negations keep their order."""
    rules = []
    for pattern in patterns:
        negated = pattern.startswith("!")
        body = pattern[1:] if negated else pattern
        if body.endswith("/"):
            body += "**"
        rules.append("Read(" + ("!" if negated else "") + body + ")")
    return rules


def claude_allow_rules(modules: list[dict]) -> list[str]:
    rules = []
    for module in modules:
        for key in ("test", "lint", "build"):
            command = module["commands"].get(key)
            # Repository wrapper scripts such as ./mvnw or ./gradlew download toolchains; keep them prompted.
            if (command and command == command.strip() and not UNSAFE_COMMAND.search(command)
                    and not command.startswith("./")):
                # A trailing " *" also matches the bare command.
                rule = f"Bash({command} *)"
                if rule not in rules:
                    rules.append(rule)
    return rules


def claude_managed_entries(root: Path, extras: set[str], modules: list[dict] | None = None) -> dict[str, list[str]]:
    """Client settings entries AI-KIT owns for the enabled extras."""
    entries: dict[str, list[str]] = {"attribution.commit": [""]}

    def add(key: str, values: list[str]) -> None:
        bucket = entries.setdefault(key, [])
        bucket.extend(value for value in values if value not in bucket)

    modules = modules or []
    if "guards" in extras:
        guards = read_json(root / "integrations" / GUARDS_SOURCE, {})
        for kind, rules in guards.get("permissions", {}).items():
            add("permissions." + kind, list(rules))
    if "data-guards" in extras:
        data_guards = read_json(root / "integrations" / DATA_GUARDS_SOURCE, {})
        for kind, rules in data_guards.get("permissions", {}).items():
            add("permissions." + kind, list(rules))
        stacks = data_guards.get("stacks", {})
        for profile in sorted({p for module in modules for p in module["profiles"]}):
            add("permissions.ask", list(stacks.get(profile, [])))
    if "native-settings" in extras:
        add("permissions.allow", claude_allow_rules(modules))
        add("permissions.deny", claude_read_rules(secret_patterns(root, modules)))
    if "session-start" in extras:
        entries["hooks.SessionStart"] = [SESSION_START_COMMAND]
    return {key: values for key, values in entries.items() if values}


def _module_slugs(modules: list[dict]) -> dict[str, str]:
    slugs: dict[str, str] = {}
    for module in modules:
        path = module["path"]
        slug = re.sub(r"[^a-z0-9]+", "-", path.strip("/").lower()).strip("-") or "root"
        if slug in slugs.values():
            slug += "-" + digest(path.encode())[:6]
        slugs[path] = slug
    return slugs


def render_scoped_rule(fmt: str, relative: str, module: dict) -> bytes:
    """One module rule pointing to canonical profiles; the root module uses each client's always-on form."""
    path = module["path"]
    root_module = path == "/"
    glob = "**" if root_module else path[1:] + "**"
    up = "../" * relative.count("/")
    links = ", ".join(f"[{profile}]({up}ai-kit/stacks/{profile}.md)" for profile in module["profiles"])
    scope = "this repository" if root_module else f"files under `{path[1:]}`"
    if fmt in {"claude-paths", "cline-paths"}:
        header = "" if root_module else f"---\npaths:\n  - {json.dumps(glob)}\n---\n\n"
    elif fmt == "cursor-globs":
        header = "---\nalwaysApply: true\n---\n\n" if root_module else f"---\nglobs: {glob}\nalwaysApply: false\n---\n\n"
    elif fmt == "copilot-applyto":
        header = f"---\napplyTo: {json.dumps(glob)}\n---\n\n"
    else:
        header = "---\ntrigger: always_on\n---\n\n" if root_module else f"---\ntrigger: glob\nglobs: {glob}\n---\n\n"
    body = (f"# AI-KIT module rules: {path}\n\n"
            "Generated by the AI-KIT installer from ai-kit/project.json; update the module facts there and rerun "
            "the installer instead of editing this file.\n"
            f"For {scope} apply {links} with the project's actual versions and conventions.\n")
    if module["commands"]:
        body += "Recorded module commands: " + "; ".join(
            f"{key} `{value}`" for key, value in sorted(module["commands"].items())) + ".\n"
    return (header + body).encode("utf-8")


def scoped_rule_files(root: Path, registry: dict, agents: list[str], modules: list[dict]) -> dict[str, bytes]:
    """Generate path-scoped rules per module for selected clients that support them."""
    usable = []
    for module in modules:
        profiles = [p for p in module["profiles"] if (root / "template/ai-kit/stacks" / (p + ".md")).is_file()]
        if profiles:
            usable.append({**module, "profiles": profiles})
    slugs = _module_slugs(usable)
    files: dict[str, bytes] = {}
    for agent in agents:
        spec = registry["scoped_rules"].get(agent)
        if spec is None:
            continue
        for module in usable:
            relative = spec["directory"] + "ai-kit-" + slugs[module["path"]] + SCOPED_FORMATS[spec["format"]]
            files[relative] = render_scoped_rule(spec["format"], relative, module)
    return files


def adapter_owner(relative: str, registry: dict) -> str | None:
    if relative.startswith(".codex/agents/aikit_") and relative.endswith(".toml"):
        return "codex"
    entries = registry["entries"]
    skills_copies = registry["skills_copies"]
    optional = registry["optional"]
    if relative in entries:
        return entries[relative]
    for agent, prefix in skills_copies.items():
        if relative.startswith(prefix):
            return agent
    for agent, items in optional.items():
        if any(destination == relative for _, destination in items):
            return agent
    for agent, spec in registry.get("scoped_rules", {}).items():
        if relative.startswith(spec["directory"] + "ai-kit-"):
            return agent
    return None


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


def _manifest_json(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return None
    return value if isinstance(value, dict) else None


def _go_version(path: Path) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*go\s+(\d+\.\d+(?:\.\d+)?)\s*$", line)
            if match:
                return match.group(1)
    except (OSError, UnicodeError):
        pass
    return None


def _python_requires(path: Path) -> str | None:
    try:
        match = re.search(r'requires-python\s*=\s*"([^"]+)"', path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return None
    return match.group(1) if match else None


def _upward(module: Path, target: Path):
    """Yield the module directory and its ancestors up to the project root (workspace roots)."""
    current = module
    while True:
        yield current
        if current == target or target not in current.parents:
            return
        current = current.parent


def _node_manager(module: Path, target: Path) -> str:
    """Prefer a declared packageManager, then a lockfile, searching up to the workspace root."""
    for directory in _upward(module, target):
        declared = (_manifest_json(directory / "package.json") or {}).get("packageManager")
        if isinstance(declared, str) and declared.split("@", 1)[0] in NODE_MANAGERS:
            return declared.split("@", 1)[0]
        for lockfile, manager in NODE_LOCKFILES:
            if (directory / lockfile).is_file():
                return manager
    return "npm"


def _package_facts(pkg: dict, manager: str = "npm") -> dict:
    version = None
    engines = pkg.get("engines")
    if isinstance(engines, dict) and isinstance(engines.get("node"), str):
        version = engines["node"]
    scripts = pkg.get("scripts") if isinstance(pkg.get("scripts"), dict) else {}
    commands = {}
    if "test" in scripts:
        # "bun test" starts Bun's own runner rather than the package script.
        commands["test"] = f"{manager} run test" if manager == "bun" else f"{manager} test"
    if "build" in scripts:
        commands["build"] = f"{manager} run build"
    if "lint" in scripts:
        commands["lint"] = f"{manager} run lint"
    return {"language": "Node", "version": version, "commands": commands}


def _browser_package(pkg: dict) -> bool:
    """Only suggest browser guidance when dependencies establish a frontend toolchain."""
    names = {name for section in ("dependencies", "devDependencies", "peerDependencies")
             for name in (pkg.get(section) if isinstance(pkg.get(section), dict) else {})}
    return bool(names & {"react", "react-dom", "vue", "svelte", "next", "nuxt", "astro", "vite",
                         "webpack", "parcel", "tailwindcss", "@angular/core", "@sveltejs/kit"})


def _python_commands(module: Path, target: Path, files: list[str]) -> dict:
    """Suggest pytest/ruff only when manifests or config files reference them."""
    texts = []
    for name in PYTHON_TOOL_FILES:
        if name in files:
            try:
                texts.append((module / name).read_text(encoding="utf-8"))
            except (OSError, UnicodeError):
                pass
    evidence = "\n".join(texts)
    runner = next((prefix for directory in _upward(module, target)
                   for lockfile, prefix in PYTHON_RUNNERS if (directory / lockfile).is_file()), "")
    commands = {}
    if re.search(r"\bpytest\b", evidence) or "pytest.ini" in files or "conftest.py" in files:
        commands["test"] = runner + "pytest"
    if re.search(r"\bruff\b", evidence) or "ruff.toml" in files or ".ruff.toml" in files:
        commands["lint"] = runner + "ruff check ."
    return commands


def _composer_facts(composer: dict, *, laravel: bool) -> dict:
    require = composer.get("require") if isinstance(composer.get("require"), dict) else {}
    version = require.get("php") if isinstance(require.get("php"), str) else None
    if laravel and isinstance(require.get("laravel/framework"), str):
        version = require["laravel/framework"]
    scripts = composer.get("scripts") if isinstance(composer.get("scripts"), dict) else {}
    commands = {}
    if "test" in scripts:
        commands["test"] = "composer test"
    if laravel:
        commands["test"] = "php artisan test"
    return {"language": "PHP", "version": version, "commands": commands}


def _filament_manifests(module: Path, composer: dict) -> list[str]:
    """Suggest a profile from known first-party dependencies, never from a wrapper or directory name."""
    evidence = []
    for section in ("require", "require-dev"):
        dependencies = composer.get(section, {})
        if isinstance(dependencies, dict) and FILAMENT_PACKAGES.intersection(dependencies):
            evidence.append("composer.json")
            break
    lock_path = module / "composer.lock"
    lock = (_manifest_json(lock_path) if not is_link(lock_path) else None) or {}
    for section in ("packages", "packages-dev"):
        packages = lock.get(section, [])
        if isinstance(packages, list) and any(isinstance(package, dict) and
                                             isinstance(package.get("name"), str) and
                                             package["name"] in FILAMENT_PACKAGES for package in packages):
            evidence.append("composer.lock")
            break
    return evidence


def _cargo_facts(module: Path) -> dict:
    version = None
    try:
        match = re.search(r'^\s*rust-version\s*=\s*"([^"]+)"',
                          (module / "Cargo.toml").read_text(encoding="utf-8"), re.M)
        if match:
            version = match.group(1)
    except (OSError, UnicodeError):
        pass
    return {"language": "Rust", "version": version,
            "commands": {"test": "cargo test", "build": "cargo build", "lint": "cargo clippy"}}


def _dotnet_facts(module: Path, files: list[str]) -> dict:
    project_file = next((name for name in sorted(files)
                         if name.endswith((".csproj", ".fsproj", ".vbproj"))), None)
    version = None
    if project_file:
        try:
            match = re.search(r"<TargetFrameworks?>([^<]+)</TargetFrameworks?>",
                              (module / project_file).read_text(encoding="utf-8"))
            if match:
                version = match.group(1).split(";")[0].strip()
        except (OSError, UnicodeError):
            pass
    return {"language": ".NET", "version": version,
            "commands": {"test": "dotnet test", "build": "dotnet build"}}


def _java_facts(module: Path, files: list[str]) -> dict:
    if "pom.xml" in files or "mvnw" in files:
        version = None
        if "pom.xml" in files:
            try:
                match = re.search(r"<(maven.compiler.release|java.version|maven.compiler.source)>([^<]+)</",
                                  (module / "pom.xml").read_text(encoding="utf-8"))
                if match:
                    version = match.group(2).strip()
            except (OSError, UnicodeError):
                pass
        runner = "./mvnw" if "mvnw" in files else "mvn"
        return {"language": "Java", "version": version,
                "commands": {"test": runner + " test", "build": runner + " compile"}}
    runner = "./gradlew" if "gradlew" in files else "gradle"
    return {"language": "Java", "version": None,
            "commands": {"test": runner + " test", "build": runner + " build"}}


def _infra_facts(module: Path, files: list[str]) -> tuple[list[str], dict]:
    if "Chart.yaml" in files:
        return ["Chart.yaml"], {"language": "Helm", "version": None,
                                "commands": {"lint": "helm lint ."}}
    terraform = sorted(name for name in files if name.endswith(".tf"))
    if terraform:
        return terraform, {"language": "Terraform", "version": None,
                           "commands": {"lint": "terraform fmt -check", "test": "terraform validate"}}
    return [], {"language": None, "version": None, "commands": {}}


def detect_facts(target: Path) -> dict:
    """Detect per-module manifests, language, version, and suggested commands (unverified draft)."""
    modules: dict[str, dict] = {}
    excluded = {".git", "node_modules", "vendor", "ai-kit", ".agents", ".claude", ".venv"}
    for directory, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if d not in excluded and not is_link(Path(directory) / d)]
        module = Path(directory)
        prefix = module.relative_to(target).as_posix()
        prefix = "" if prefix == "." else prefix + "/"
        facts: dict = {"path": "/" + prefix if prefix else "/", "manifests": [],
                       "language": None, "version": None, "profiles": [], "commands": {}}
        if "go.mod" in files:
            facts["manifests"].append("go.mod")
            facts["profiles"].append("GO")
            facts["language"] = "Go"
            facts["version"] = _go_version(module / "go.mod")
            facts["commands"].update({"test": "go test ./...", "build": "go build ./...",
                                      "lint": "go vet ./..."})
        py_manifest = next((name for name in PROFILE_MANIFESTS["PYTHON"] if name in files), None)
        if py_manifest:
            facts["manifests"].append(py_manifest)
            facts["profiles"].append("PYTHON")
            if facts["language"] is None:
                facts["language"] = "Python"
            if facts["version"] is None:
                facts["version"] = _python_requires(module / py_manifest)
            facts["commands"].update(_python_commands(module, target, files))
        if "package.json" in files:
            facts["manifests"].append("package.json")
            manifest = _manifest_json(module / "package.json") or {}
            facts["profiles"].append("JAVASCRIPT")
            if _browser_package(manifest):
                facts["profiles"].append("FRONTEND")
            package = _package_facts(manifest, _node_manager(module, target))
            if facts["language"] is None:
                facts["language"] = package["language"]
            if facts["version"] is None:
                facts["version"] = package["version"]
            facts["commands"].update(package["commands"])
        if "composer.json" in files:
            facts["manifests"].append("composer.json")
            facts["profiles"].append("PHP")
            laravel = (module / "artisan").is_file()
            if laravel:
                facts["profiles"].append("LARAVEL")
            manifest = _manifest_json(module / "composer.json") or {}
            filament = _filament_manifests(module, manifest)
            if filament:
                facts["profiles"].append("FILAMENT")
                if "composer.lock" in filament:
                    facts["manifests"].append("composer.lock")
            composer = _composer_facts(manifest, laravel=laravel)
            if facts["language"] is None:
                facts["language"] = composer["language"]
            if facts["version"] is None:
                facts["version"] = composer["version"]
            facts["commands"].update(composer["commands"])
        if "config-dist.php" in files and (module / "lib/moodlelib.php").is_file():
            facts["manifests"].append("config-dist.php")
            facts["profiles"].append("MOODLE")
            if facts["language"] is None:
                facts["language"] = "PHP"
            facts["commands"].setdefault("test", "vendor/bin/phpunit")
        if "Cargo.toml" in files:
            facts["manifests"].append("Cargo.toml")
            facts["profiles"].append("RUST")
            cargo = _cargo_facts(module)
            if facts["language"] is None:
                facts["language"] = cargo["language"]
            if facts["version"] is None:
                facts["version"] = cargo["version"]
            # Secondary stacks fill gaps only; a primary language keeps its test/lint/build commands.
            for key, value in cargo["commands"].items():
                facts["commands"].setdefault(key, value)
        if any(name.endswith((".csproj", ".fsproj", ".vbproj")) for name in files) or "global.json" in files:
            project_files = [name for name in sorted(files)
                           if name.endswith((".csproj", ".fsproj", ".vbproj"))]
            facts["manifests"].extend(project_files or ["global.json"])
            facts["profiles"].append("DOTNET")
            dotnet = _dotnet_facts(module, files)
            if facts["language"] is None:
                facts["language"] = dotnet["language"]
            if facts["version"] is None:
                facts["version"] = dotnet["version"]
            for key, value in dotnet["commands"].items():
                facts["commands"].setdefault(key, value)
        if any(name in files for name in ("pom.xml", "mvnw", "build.gradle", "build.gradle.kts", "gradlew")):
            java_manifest = next(name for name in ("pom.xml", "mvnw", "build.gradle", "build.gradle.kts", "gradlew")
                                 if name in files)
            facts["manifests"].append(java_manifest)
            facts["profiles"].append("JAVA")
            java = _java_facts(module, files)
            if facts["language"] is None:
                facts["language"] = java["language"]
            if facts["version"] is None:
                facts["version"] = java["version"]
            for key, value in java["commands"].items():
                facts["commands"].setdefault(key, value)
        infra_manifests, infra = _infra_facts(module, files)
        if infra_manifests:
            facts["manifests"].extend(infra_manifests)
            facts["profiles"].append("INFRA")
            if facts["language"] is None:
                facts["language"] = infra["language"]
            for key, value in infra["commands"].items():
                facts["commands"].setdefault(key, value)
        if facts["manifests"]:
            facts["profiles"] = sorted(set(facts["profiles"]))
            modules[prefix] = facts
    return {"modules": [modules[key] for key in sorted(modules)]}


def as_lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def eol_variant_hashes(data: bytes) -> set[str]:
    """Hashes of the same text with LF and CRLF endings; earlier bundles shipped either form."""
    lf = as_lf(data)
    return {digest(data), digest(lf), digest(lf.replace(b"\n", b"\r\n"))}


def readable_project_file(target: Path, relative: str) -> Path | None:
    """Resolve a project file for reading only; links inside the project are fine, escapes are skipped."""
    parts = relative.replace("\\", "/").split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None
    path = target.joinpath(*parts)
    try:
        resolved = path.resolve()
        resolved.relative_to(target.resolve())
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def project_fact_evidence(target: Path, facts: dict) -> dict:
    """Return stable manifest digests for doctor freshness checks without write-time path guards."""
    modules = []
    for module in facts["modules"]:
        prefix = "" if module["path"] == "/" else module["path"].strip("/") + "/"
        manifests = {}
        for name in sorted(module["manifests"]):
            path = readable_project_file(target, prefix + name)
            if path is not None:
                try:
                    manifests[name] = digest(path.read_bytes())
                except OSError:
                    continue
        modules.append({"path": module["path"], "manifests": manifests,
                        "profiles": list(module["profiles"]), "commands": dict(module["commands"])})
    return {"schema": 1, "modules": modules}


def profiles_from_facts(facts: dict) -> dict[str, list[str]]:
    found: dict[str, set[str]] = {}
    for module in facts["modules"]:
        prefix = "" if module["path"] == "/" else module["path"][1:]
        for profile in module["profiles"]:
            found.setdefault(profile, set()).add(prefix)
    return {profile: sorted(prefixes) for profile, prefixes in sorted(found.items())}


def detect_profiles(target: Path) -> dict[str, list[str]]:
    """Map stack profiles to module prefixes evidenced by manifests (unverified draft)."""
    return profiles_from_facts(detect_facts(target))


def project_context_draft(data: bytes, facts: dict) -> bytes:
    """Turn installer-detected manifests into draft module-map rows for a fresh context."""
    modules = facts["modules"]
    if not modules:
        return data
    text = data.decode("utf-8")
    placeholder = "| Not established | Not established | Not established | None confirmed | Not established |"
    if placeholder not in text:
        return data
    rows = []
    for module in modules:
        manifests = ", ".join(module["manifests"]) + " (installer-detected)"
        language = module["language"] or "not established"
        if module["version"]:
            language += " " + module["version"]
        language += " (suggested)"
        profiles = ", ".join(module["profiles"]) + " (suggested, confirm at bootstrap)"
        commands = module["commands"]
        if commands:
            command_text = "; ".join(f"{key}: {value}" for key, value in sorted(commands.items()))
        else:
            command_text = "not established"
        rows.append(f"| {module['path']} | {manifests} | {language} | {profiles} | {command_text} |")
    return text.replace(placeholder, "\n".join(rows), 1).encode("utf-8")


def project_json_draft(data: bytes, facts: dict, target: Path) -> bytes:
    """Fill the machine-readable project.json modules from detected manifests (unverified draft)."""
    if not facts["modules"]:
        return data
    value = json.loads(data.decode("utf-8"))
    value["modules"] = [{"path": m["path"], "manifests": m["manifests"], "language": m["language"],
                         "version": m["version"], "profiles": m["profiles"], "commands": m["commands"]}
                        for m in facts["modules"]]
    value["evidence"] = project_fact_evidence(target, facts)
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


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


def project_documents(settings: dict) -> set[str]:
    """Project-owned documents are created once, including those of enabled modules."""
    return OWNED | {path for extra, paths in OPTIONAL_DOCUMENTS.items()
                    if settings.get(EXTRA_SETTINGS_KEYS[extra]) is True for path in paths}


def version_key(value) -> tuple[int, ...] | None:
    """Parse a released X.Y.Z version; anything else is not comparable."""
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value.strip()) if isinstance(value, str) else None
    return tuple(int(part) for part in match.groups()) if match else None


def is_downgrade(installed, bundle) -> bool:
    old, new = version_key(installed), version_key(bundle)
    return old is not None and new is not None and old > new


def build_plan(target: Path, *, root: Path = ROOT, mode: str | None = None,
               language: str | None = None, conventions: str | None = None,
               agents: list[str] | None = None, accept_local: list[str] | None = None,
               extras: list[str] | None = None, preset: str | None = None,
               docker_cleanup: str | None = None, allow_downgrade: bool = False) -> dict:
    if docker_cleanup is not None and docker_cleanup not in DOCKER_CLEANUP_MODES:
        raise ValueError("Docker cleanup must be one of: " + ", ".join(DOCKER_CLEANUP_MODES))
    if preset is not None and preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}; choose one of {', '.join(sorted(PRESETS))}")
    target = target.absolute()
    if is_link(target):
        raise ValueError("Refusing a linked target root")
    target = target.resolve()
    if target == root.resolve() or root.resolve() in target.parents:
        raise ValueError("Cannot install an application kit inside the reference distribution")
    if target.exists() and not target.is_dir():
        raise ValueError("Target must be a directory")
    registry = load_agent_registry(root)
    settings_path = safe_path(target, "ai-kit/settings.json")
    settings = read_json(settings_path, read_json(root / "template/ai-kit/settings.json", {}))
    validate_settings(settings)
    state_path = safe_path(target, "ai-kit/.install-state.json")
    state = read_json(state_path, {})
    if state_path.exists():
        validate_state(state, target, registry["names"])
    preset_disabled = []
    if preset is not None:
        mode = mode or PRESETS[preset]["mode"]
        for name in PRESET_EXTRAS:
            key = EXTRA_SETTINGS_KEYS[name]
            enabled = name in PRESETS[preset]["extras"]
            if settings.get(key) is True and not enabled and name not in (extras or []):
                preset_disabled.append(name)
            settings[key] = enabled
    mode = mode or settings.get("sharing_mode", "private")
    language = language or settings.get("chat_language", "English")
    conventions = conventions or settings.get("conventions", "owner")
    explicit_agents = agents is not None
    agents = agent_selection(agents if agents is not None else state.get("agents", list(DEFAULT_AGENTS)),
                             registry["names"])
    detected_agents = detect_agents(target, registry)
    suggested_agents = sorted(set(agents) | set(detected_agents))
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
    if docker_cleanup is not None:
        settings["docker_cleanup"] = docker_cleanup
    validate_settings(settings)
    owned_documents = project_documents(settings)
    facts = detect_facts(target)
    detected = profiles_from_facts(facts)
    modules, module_warnings = project_modules(target, facts)
    upstream_files = {}
    for name in OPTIONAL_SKILLS:
        if name in enabled_extras:
            upstream_files.update(upstream_skill_files(name, root))
    incoming: dict[str, bytes] = {}
    for src in sorted((root / "template").rglob("*")):
        if is_link(src):
            raise ValueError(f"Linked source path: {src}")
        if not src.is_file():
            continue
        relative = src.relative_to(root / "template").as_posix()
        if any(relative.startswith("ai-kit/vendor/" + name + "/") for name in OPTIONAL_SKILLS):
            # Only the manifest-verified bytes may enter an optional upstream payload.
            continue
        if any(relative.startswith(".agents/skills/" + skill + "/") and name not in enabled_extras
               for name, skills in OPTIONAL_ENTRY_POINTS.items() for skill in skills):
            continue
        if any(relative in paths and name not in enabled_extras
               for mapping in (OPTIONAL_RESOURCES, OPTIONAL_DOCUMENTS) for name, paths in mapping.items()):
            continue
        if relative in registry["entries"] and registry["entries"][relative] not in agents:
            continue
        if any(relative in paths for paths in EXTRA_TEMPLATE.values()):
            continue
        incoming[relative] = src.read_bytes()
    incoming.update(upstream_files)
    if "uuid" in enabled_extras:
        incoming["AGENTS.md"] += b"\nFor identifier changes apply the enabled [UUID policy](ai-kit/UUID.md) across confirmed stacks.\n"
    if "claude-github" in enabled_extras and "claude" in agents:
        incoming["CLAUDE.md"] += b"\nBefore an authorized GitHub commit read [human GitHub identity](ai-kit/CLAUDE-GITHUB.md).\n"
    if "orchestration" in enabled_extras:
        incoming["AGENTS.md"] += b"\nFor explicitly requested orchestration read [the optional contract](ai-kit/ORCHESTRATION.md).\n"
        if "codex" in agents:
            catalogue = read_json(root / "template/ai-kit/router/providers/openai.json", {})
            for source in sorted((root / "integrations/codex-agents").glob("*.toml")):
                if is_link(source):
                    raise ValueError("Linked helper source")
                text = source.read_text(encoding="utf-8")
                for role in ("cheap", "work"):
                    spec = catalogue["roles"][role]
                    for field in ("model", "effort"):
                        value = spec[field]
                        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", value):
                            raise ValueError("Invalid native helper model/effort")
                        text = text.replace("__" + role.upper() + "_" + field.upper() + "__", value)
                incoming[".codex/agents/" + source.name] = text.encode()
    for name, skills in OPTIONAL_ENTRY_POINTS.items():
        if name not in enabled_extras:
            registry_path = "ai-kit/SKILLS.md"
            incoming[registry_path] = b"\n".join(
                line for line in incoming[registry_path].split(b"\n")
                if not any(("(../.agents/skills/" + skill + "/SKILL.md)").encode() in line for skill in skills))
    if "web-design" not in enabled_extras:
        # These navigation lines only exist when their optional destinations are installed.
        for navigation in ("WIKI.md", "ai-kit/ADAPTERS.md"):
            incoming[navigation] = b"\n".join(line for line in incoming[navigation].split(b"\n")
                                             if b"WEB-DESIGN.md)" not in line)
    incoming["ai-kit/settings.json"] = (json.dumps(settings, indent=2) + "\n").encode()
    incoming["ai-kit/VERSION"] = (root / "VERSION").read_bytes()
    incoming["ai-kit/LICENSE"] = (root / "LICENSE").read_bytes()
    for agent, prefix in registry["skills_copies"].items():
        if agent in agents:
            for relative, data in list(incoming.items()):
                if relative.startswith(".agents/skills/"):
                    if agent == "claude" and relative in {
                            ".agents/skills/" + name + "/SKILL.md" for name in OPTIONAL_SKILLS}:
                        newline = b"\r\n" if data.startswith(b"---\r\n") else b"\n"
                        header = b"---" + newline
                        if not data.startswith(header):
                            raise ValueError("Optional upstream entry point lacks frontmatter")
                        data = header + b"disable-model-invocation: true" + newline + data[len(header):]
                    incoming[relative.replace(".agents/skills/", prefix, 1)] = data
    for agent, items in registry["optional"].items():
        if agent in agents:
            for source, destination in items:
                incoming[destination] = (root / "integrations" / source).read_bytes()
    for name in sorted(enabled_extras):
        if name in EXTRA_TEMPLATE:
            for relative in EXTRA_TEMPLATE[name]:
                incoming[relative] = (root / "template" / relative).read_bytes()
        elif name in EXTRA_INTEGRATIONS:
            src, dst = EXTRA_INTEGRATIONS[name]
            incoming[dst] = (root / "integrations" / src).read_bytes()
    if "scoped-rules" in enabled_extras:
        # Generated module rules are managed files: unchanged ones follow project.json, edited ones conflict.
        incoming.update(scoped_rule_files(root, registry, agents, modules))
    if accept - incoming.keys() or accept & (owned_documents | {"ai-kit/settings.json"}):
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
        if relative in owned_documents:
            if current is None:
                if relative == "PROJECT_CONTEXT.md":
                    data = project_context_draft(data, facts)
                elif relative == "ai-kit/project.json":
                    data = project_json_draft(data, facts, target)
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
        elif previous.get("source_hash") in eol_variant_hashes(data):
            # No upstream change (line endings alone do not count): retain local bytes without rewriting.
            accepted[relative] = {**previous, "source_hash": source_hash}
            preserved.append(relative)
        elif not previous and as_lf(current) == as_lf(data):
            # An untracked file that differs only in line endings is the same content.
            accepted[relative] = {"installed_hash": digest(current), "source_hash": source_hash}
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
    bundle_version = (root / "VERSION").read_text(encoding="utf-8").strip()
    downgrade_from = state.get("accepted_version") if is_downgrade(state.get("accepted_version"),
                                                                   bundle_version) else None
    if downgrade_from:
        warnings.append(f"This project has AI-KIT {downgrade_from}, newer than this installer ({bundle_version}); "
                        "applying would replace managed files with older versions. Upgrade the CLI first"
                        + ("; --allow-downgrade permits it deliberately." if allow_downgrade else
                           ", or pass --allow-downgrade to downgrade deliberately."))
    if "ci" in enabled_extras and mode == "private":
        warnings.append("The CI check validates committed AI-KIT files, but private sharing mode keeps them "
                        "out of Git; use team mode for a meaningful check.")
    if "claude" not in agents and ({"guards", "session-start"} & enabled_extras):
        warnings.append("guards/session-start client wiring requires the claude agent selection; "
                        "only the shared files were installed.")
    if "claude-github" in enabled_extras and "claude" not in agents:
        warnings.append("claude-github guidance requires --agent claude; no GitHub identity was queried or changed.")
    if "devin" in agents and "windsurf" in detected_agents:
        warnings.append("Devin (Windsurf) also loads legacy .windsurf rules; review duplicate guidance. "
                        "Previously managed legacy rules require explicit adapter retirement, never deletion here.")
    if mode == "team" and legacy.intersection(line.strip() for line in outside.splitlines()):
        conflicts[".gitignore"] = merged.encode()
        conflict_local_hashes[".gitignore"] = digest(old_ignore) if old_ignore is not None else None
        warnings.append("Remove or reconcile legacy private exclusions explicitly before applying team mode.")
    elif old_ignore != merged.encode():
        actions[".gitignore"] = {"data": merged.encode(), "old": old_ignore}
    missing_agents = sorted(set(detected_agents) - set(agents))
    if missing_agents and not explicit_agents:
        evidence = "; ".join(f"{agent} ({', '.join(detected_agents[agent])})" for agent in missing_agents)
        warnings.append(f"Detected client files for {evidence}; preview with "
                        + " ".join("--agent " + agent for agent in suggested_agents) + " to wire them.")
    warnings.extend(module_warnings)
    if preset_disabled:
        warnings.append(f"Preset {preset} turns off previously enabled extras: {', '.join(preset_disabled)}; "
                        "add their --with-* flags to keep them.")
    # AI-KIT owns only its own entries in the client settings file; other settings survive.
    # Private mode keeps them in the personal local file, team mode in the shared one.
    managed_json = {relative: dict(entries) for relative, entries in state.get("managed_json", {}).items()}
    claude_target = CLAUDE_LOCAL_SETTINGS if mode == "private" else CLAUDE_SETTINGS
    if "claude" in agents:
        wanted_entries = claude_managed_entries(root, enabled_extras, modules)
        for relative in (CLAUDE_SETTINGS, CLAUDE_LOCAL_SETTINGS):
            wanted = wanted_entries if relative == claude_target else {}
            previous = {key: list(values) for key, values in managed_json.get(relative, {}).items()}
            if relative == CLAUDE_SETTINGS and CLAUDE_SETTINGS in records:
                for key, values in LEGACY_CLAUDE_ENTRIES.items():
                    previous.setdefault(key, []).extend(values)
            if not (wanted or previous):
                continue
            settings_file = safe_path(target, relative)
            old_settings = settings_file.read_bytes() if settings_file.exists() else None
            try:
                current = json.loads(old_settings.decode("utf-8-sig")) if old_settings is not None else {}
                if not isinstance(current, dict):
                    raise ValueError("expected a JSON object")
                merged_settings = merge_managed_json(current, previous, wanted)
            except (ValueError, UnicodeError) as exc:
                fragment = merge_managed_json({}, {}, wanted)
                conflicts[relative] = (json.dumps(fragment, indent=2) + "\n").encode()
                conflict_local_hashes[relative] = digest(old_settings)
                warnings.append(f"Cannot merge AI-KIT entries into {relative} ({exc}); fix the file "
                                "or merge the candidate fragment manually, then rerun the preview.")
                continue
            if (old_settings is None and wanted) or (old_settings is not None and merged_settings != current):
                data = (json.dumps(merged_settings, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
                actions[relative] = {"data": data, "old": old_settings}
            if wanted:
                managed_json[relative] = wanted
            else:
                managed_json.pop(relative, None)
    else:
        for relative in (CLAUDE_SETTINGS, CLAUDE_LOCAL_SETTINGS):
            if relative in managed_json:
                warnings.append(f"AI-KIT entries remain in {relative} for the unselected claude client; "
                                "review them before retirement.")
    # Client ignore files get one marked secret block, like .gitignore; other lines survive.
    secret_block = None
    if "native-settings" in enabled_extras:
        secret_block = ("# Secret files AI clients must not read\n"
                        + "\n".join(secret_patterns(root, modules)) + "\n")
    for agent, relative in sorted(registry["ignore_files"].items()):
        ignore_file = safe_path(target, relative)
        old_text_bytes = ignore_file.read_bytes() if ignore_file.exists() else None
        old_text = (old_text_bytes or b"").decode("utf-8-sig")
        if secret_block is not None and agent in agents:
            new_text, _ = merge_ignore(old_text, secret_block, [])
        elif old_text_bytes is not None and START in old_text:
            before, after = split_ignore(old_text)
            new_text = before + after
        else:
            continue
        if new_text.encode("utf-8") != old_text_bytes:
            actions[relative] = {"data": new_text.encode("utf-8"), "old": old_text_bytes}
    retirements = []
    for relative, record in records.items():
        if relative in incoming or relative in owned_documents:
            continue
        if relative == CLAUDE_SETTINGS and "claude" in agents:
            # Earlier versions managed the whole file; its entries now migrate to managed_json.
            continue
        if safe_path(target, relative).exists():
            # Keep old baseline information even when a path leaves the bundle.
            accepted[relative] = record
            owner = adapter_owner(relative, registry)
            if owner is not None and owner not in agents:
                retirements.append(relative)
            else:
                warnings.append(f"Previously managed path retained without a current source: {relative}")
    if retirements:
        warnings.append("Agent selection replaces the recorded list, but tracked unselected adapters "
                        "remain on disk and may still load. Review/retire the listed files or retain "
                        "their agent selection; accepted files/state will not change.")
    unselected = dict(registry["entries"])
    unselected.update({".codex/agents/" + p.name: "codex"
                       for p in (root / "integrations/codex-agents").glob("aikit_*.toml")})
    for agent, items in registry["optional"].items():
        for _, destination in items:
            unselected[destination] = agent
    for relative, owner in unselected.items():
        if owner in agents or relative in records:
            continue
        try:
            exists = safe_path(target, relative).exists()
        except NotADirectoryError:
            # An existing native rule file can occupy a directory adapter's parent.
            continue
        if exists:
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
    if managed_json:
        new_state["managed_json"] = managed_json
    else:
        new_state.pop("managed_json", None)
    state_data = (json.dumps(new_state, indent=2, sort_keys=True) + "\n").encode()
    old_state = state_path.read_bytes() if state_path.exists() else None
    if old_state != state_data:
        actions["ai-kit/.install-state.json"] = {"data": state_data, "old": old_state}
    return {"target": target, "mode": mode, "version": new_state["accepted_version"],
            "actions": actions, "conflicts": conflicts, "candidates": candidates,
            "adapter_conflicts": sorted(retirements), "preserved": preserved,
            "detected_profiles": detected, "detected_agents": detected_agents,
            "suggested_agents": suggested_agents, "extras": sorted(enabled_extras), "preset": preset,
            "warnings": warnings, "downgrade_from": downgrade_from, "allow_downgrade": allow_downgrade}


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".ai-kit-" + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def exclusive_lock(path: Path) -> int:
    """Create a cooperative writer lock; a lock left by a crash needs an informed manual removal."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        return os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError(f"Another AI-KIT writer holds {path}; if no aikit process is running, "
                         "remove that lock file and retry") from None


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
    if plan.get("downgrade_from") and not plan.get("allow_downgrade"):
        # An older CLI would otherwise silently replace newer managed files.
        raise ValueError(f"Refusing to downgrade AI-KIT {plan['downgrade_from']} to {plan['version']}; upgrade the "
                         "CLI (for example `pipx upgrade ai-kit-python`) or pass --allow-downgrade deliberately")
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


def interactive_selections(read=input, *, agents_available: set[str], facts: dict,
                           detected_agents: dict[str, list[str]] | None = None) -> dict | None:
    """Prompt for selections; returns None when the user declines to continue."""
    print("AI-KIT interactive installer")
    for module in facts["modules"]:
        print(f"  Detected: {module['path']} ({', '.join(module['profiles']) or 'no profile'})"
              f" from {', '.join(module['manifests'])}")
    detected_agents = detected_agents or {}
    for agent, evidence in sorted(detected_agents.items()):
        print(f"  Detected client: {agent} ({', '.join(evidence)})")
    default_agents = sorted(set(DEFAULT_AGENTS) | set(detected_agents))
    preset = read(f"Preset [{'/'.join(PRESETS)}] (none): ").strip().lower() or None
    spec = PRESETS.get(preset or "", {"mode": None, "extras": ()})
    default_mode = spec["mode"] or "private"
    mode = (read(f"Sharing mode [private/team] ({default_mode}): ").strip() or default_mode).lower()
    language = read("Chat language (English): ").strip() or "English"
    conventions = (read("Conventions [owner/standard] (owner): ").strip() or "owner").lower()
    agent_text = read(f"Agents, comma-separated ({', '.join(sorted(agents_available))}) "
                      f"[{','.join(default_agents)}]: ").strip()
    agents = [a.strip() for a in agent_text.split(",") if a.strip()] or default_agents
    default_extras = list(spec["extras"])
    extra_text = read(f"Extras, comma-separated [{','.join(sorted(EXTRAS))}] "
                      f"({','.join(default_extras) or 'none'}): ").strip()
    extras = [e.strip() for e in extra_text.split(",") if e.strip()] or default_extras
    print("\nSummary:")
    print(f"  preset={preset or 'none'}, mode={mode}, language={language}, conventions={conventions}")
    print(f"  agents={', '.join(agents)}, extras={', '.join(extras) or 'none'}")
    confirm = read("Proceed? [y/N]: ").strip().lower()
    if confirm not in {"y", "yes"}:
        print("Aborted.")
        return None
    return {"preset": preset, "mode": mode, "language": language, "conventions": conventions,
            "agents": agents, "extras": extras}


def build_parser(root: Path = ROOT) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Application directory to set up or update")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="Write the previewed plan; without it nothing is written")
    group.add_argument("--dry-run", action="store_true", help="Explicitly request the read-only preview (the default)")
    parser.add_argument("--mode", choices=["private", "team"],
                        help="Git visibility of AI-KIT files: private keeps them local, team shares instructions")
    parser.add_argument("--chat-language",
                        help="Language for chat replies and plans; project files stay English")
    parser.add_argument("--conventions", choices=["owner", "standard"],
                        help="Stack preferences: owner applies the owner's conventions, standard follows the project")
    parser.add_argument("--docker-cleanup", choices=list(DOCKER_CLEANUP_MODES),
                        help="Post-Docker cleanup: maximum (default) removes every eligible disposable resource "
                             "and reclaims host resources; keep-cache keeps the dedicated project builder cache")
    parser.add_argument("--agent", choices=sorted(load_agent_registry(root)["names"]), action="append",
                        help="AI client adapter to install; repeat for several clients")
    parser.add_argument("--interactive", action="store_true",
                        help="Prompt for sharing mode, language, conventions, agents, and extras")
    parser.add_argument("--check", action="store_true",
                        help="Run the project doctor after a successful --apply")
    parser.add_argument("--accept-local", action="append", default=[],
                        help="Record an explicitly reviewed semantic merge of a managed path")
    parser.add_argument("--with-session-start", action="store_true",
                        help="Install the session-start hook file and client wiring")
    parser.add_argument("--with-guards", action="store_true",
                        help="Install client confirmation (ask) rules for Git commit/push")
    parser.add_argument("--with-ci", action="store_true",
                        help="Install the self-contained AI-KIT project check workflow")
    parser.add_argument("--with-data-guards", action="store_true",
                        help="Ask before destructive file, Docker, and detected migration commands (Claude Code)")
    parser.add_argument("--with-native-settings", action="store_true",
                        help="Allow recorded checks, deny secret reads, and write client ignore files")
    parser.add_argument("--with-scoped-rules", action="store_true",
                        help="Generate path-scoped rules per module for clients that support them")
    parser.add_argument("--with-security-audit", action="store_true",
                        help="Install the pinned, user-invoked security-audit skill without running an audit")
    parser.add_argument("--with-strix", action="store_true",
                        help="Install pinned Strix skills and a user-invoked entry point without installing or running Strix")
    parser.add_argument("--with-context7", action="store_true",
                        help="Install the Context7 documentation skill; MCP connection/authentication stays separate")
    parser.add_argument("--preset", choices=list(PRESETS),
                        help="Apply a selection bundle; explicit --mode and --with-* flags take precedence")
    parser.add_argument("--with-orchestration", action="store_true",
                        help="Install optional Codex helpers and disabled OpenRouter configuration; no calls")
    parser.add_argument("--with-web-design", action="store_true",
                        help="Install Web Design workflows and project documents; no external tool setup")
    parser.add_argument("--with-uuid", action="store_true",
                        help="Enable public UUID guidance for any confirmed stack; no schema/code changes")
    parser.add_argument("--with-claude-github", action="store_true",
                        help="Require the authenticated human GitHub identity for authorized Claude commits; no login")
    parser.add_argument("--allow-downgrade", action="store_true",
                        help="Apply even when the project has a newer AI-KIT version than this installer")
    return parser


def flag_schema(root: Path = ROOT) -> dict:
    """Describe installer options for documentation and configurators; check_kit compares the committed copy."""
    parser = build_parser(root)
    settings = json.loads((root / "template/ai-kit/settings.json").read_text(encoding="utf-8"))
    excludes: dict[str, list[str]] = {}
    for group in parser._mutually_exclusive_groups:
        names = [action.option_strings[-1] for action in group._group_actions]
        for name in names:
            excludes[name] = [other for other in names if other != name]
    extra_keys = {"--with-" + name: key for name, key in EXTRA_SETTINGS_KEYS.items()}
    options = []
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            continue
        name = action.option_strings[-1] if action.option_strings else action.dest.upper()
        entry: dict = {"option": name}
        if action.nargs == 0:
            entry["value"] = "switch"
        elif action.choices:
            entry["value"], entry["choices"] = "choice", list(action.choices)
        else:
            entry["value"] = "path" if action.type is Path else "text"
        if not action.option_strings:
            entry["required"] = True
        if isinstance(action, argparse._AppendAction):
            entry["repeatable"] = True
        if name in excludes:
            entry["excludes"] = excludes[name]
        setting = OPTION_SETTINGS.get(action.dest) or extra_keys.get(name)
        if setting:
            entry["setting"] = setting
        if setting in settings:
            entry["fresh_default"] = settings[setting]
        elif action.dest == "agent":
            entry["fresh_default"] = list(DEFAULT_AGENTS)
        if action.help:
            entry["help"] = action.help
        options.append(entry)
    presets = {name: {"mode": spec["mode"], "extras": list(spec["extras"])} for name, spec in PRESETS.items()}
    return {"schema": 1, "command": "aikit install", "options": options, "presets": presets}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    extras = [name for name, flag in (("session-start", args.with_session_start),
                                      ("guards", args.with_guards),
                                      ("ci", args.with_ci),
                                      ("data-guards", args.with_data_guards),
                                      ("native-settings", args.with_native_settings),
                                      ("scoped-rules", args.with_scoped_rules),
                                      ("security-audit", args.with_security_audit), ("strix", args.with_strix),
                                      ("context7", args.with_context7),
                                      ("web-design", args.with_web_design),
                                      ("orchestration", args.with_orchestration),
                                      ("uuid", args.with_uuid), ("claude-github", args.with_claude_github)) if flag]
    mode, language, conventions, agents = args.mode, args.chat_language, args.conventions, args.agent
    preset = args.preset
    if args.interactive:
        target = args.target.absolute().resolve()
        registry = load_agent_registry()
        selections = interactive_selections(agents_available=registry["names"], facts=detect_facts(target),
                                            detected_agents=detect_agents(target, registry))
        if selections is None:
            return 0
        mode = mode or selections["mode"]
        language = language or selections["language"]
        conventions = conventions or selections["conventions"]
        agents = agents or selections["agents"]
        extras = sorted(set(extras) | set(selections["extras"]))
        preset = preset or selections["preset"]
    try:
        plan = build_plan(args.target, mode=mode, language=language,
                          conventions=conventions, agents=agents, accept_local=args.accept_local,
                          extras=extras, preset=preset, docker_cleanup=args.docker_cleanup,
                          allow_downgrade=args.allow_downgrade)
        print(json.dumps({"target": str(plan["target"]), "version": plan["version"], "mode": plan["mode"],
                          "preset": plan["preset"],
                          "preview": not args.apply, "writes": sorted(plan["actions"]),
                          "conflicts": sorted(plan["conflicts"]), "preserved": sorted(plan["preserved"]),
                          "candidates": plan["candidates"], "adapter_conflicts": plan["adapter_conflicts"],
                          "detected_profiles": plan["detected_profiles"],
                          "detected_agents": plan["detected_agents"],
                          "suggested_agents": plan["suggested_agents"], "extras": plan["extras"],
                          "warnings": plan["warnings"]}, indent=2))
        if args.apply:
            applied = apply_plan(plan)
            if applied and args.check:
                import doctor
                try:
                    report = doctor.examine(plan["target"], root=ROOT)
                except (OSError, ValueError, UnicodeError) as exc:
                    # The writes above already succeeded; report the check failure as such.
                    print(f"Installation applied; doctor check failed: {exc}", file=sys.stderr)
                    return 1
                print(json.dumps({"doctor": report}, indent=2))
                return 1 if report["errors"] else 0
        return 2 if needs_review(plan) else 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Installation refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
