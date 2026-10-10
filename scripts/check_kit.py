"""Offline validation of reference/template boundaries, metadata, links, and visibility."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install

ROOT = Path(__file__).resolve().parents[1]


def source_files(root: Path):
    # IDE and tool state is local to a checkout, never a kit source.
    excluded = {".git", "__pycache__", ".upstream-cache", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                ".idea", ".vscode", ".fleet", ".zed", ".nova", ".history", ".claude"}
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in excluded]
        if Path(directory) == root / "ai-kit":
            dirs[:] = [d for d in dirs if d != ".metrics"]
        for name in files:
            path = Path(directory) / name
            if path.suffix != ".pyc":
                yield path


def headings(text: str) -> set[str]:
    result, counts = set(), {}
    fenced = False
    marker = ""
    for line in text.splitlines():
        if re.match(r"^\s*([~]{3,}|[\x60]{3,})", line):
            token = line.strip()[0]
            if not fenced:
                fenced, marker = True, token
            elif token == marker:
                fenced = False
            continue
        if fenced or not re.match(r"^#{1,6}\s", line):
            continue
        label = re.sub(r"^#{1,6}\s+", "", line).strip().lower()
        label = re.sub(r"<[^>]+>", "", label)
        label = re.sub(r"[^\w -]", "", label).replace(" ", "-")
        count = counts.get(label, 0)
        counts[label] = count + 1
        result.add(label + (f"-{count}" if count else ""))
    return result


def metadata(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text.replace("\r\n", "\n"), re.S)
    if not match:
        raise ValueError("Missing frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise ValueError("Unsupported frontmatter line")
        key, value = line.split(":", 1)
        if key in fields:
            raise ValueError("Duplicate frontmatter field")
        value = value.strip()
        fields[key] = json.loads(value) if value.startswith('"') else value
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields.get("name", "")):
        raise ValueError("Invalid skill name")
    if not isinstance(fields.get("description"), str) or len(fields["description"]) < 20:
        raise ValueError("Missing useful description")
    return fields


def links(text: str):
    # Fenced examples are data, not Markdown links.
    text = re.sub(r"(?ms)^\s*(?:~~~|[\x60]{3}).*?^\s*(?:~~~|[\x60]{3})\s*$", "", text)
    return re.findall(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text)


def visibility(root: Path, git: str) -> list[str]:
    errors = []
    with tempfile.TemporaryDirectory(prefix="ai-kit-ignore-") as folder:
        scratch = Path(folder)
        subprocess.run([git, "init", "-q", str(scratch)], check=True, capture_output=True)

        def ignored(path: str) -> bool:
            result = subprocess.run([git, "-c", "core.excludesFile=" + os.devnull,
                                     "-C", str(scratch), "check-ignore", "--no-index", "--", path],
                                    capture_output=True)
            if result.returncode not in {0, 1}:
                raise ValueError(result.stderr.decode(errors="replace"))
            return result.returncode == 0

        (scratch / ".gitignore").write_bytes((root / ".gitignore").read_bytes())
        for p in source_files(root):
            relative = p.relative_to(root).as_posix()
            if ignored(relative):
                errors.append("Reference source ignored: " + relative)
        # Compose the policy with installer-detected module rules, as apply does.
        (scratch / "package.json").write_text("{}\n", encoding="utf-8")
        (scratch / "pyproject.toml").write_text("[project]\nname = \"scratch\"\n", encoding="utf-8")
        for mode in ("private", "team"):
            policy = (root / "templates" / ("gitignore." + mode)).read_text(encoding="utf-8")
            merged, _ = install.merge_ignore("", policy, install.module_ignores(scratch))
            (scratch / ".gitignore").write_bytes(merged.encode("utf-8"))
            for path in ("AGENTS.md", "PROJECT_CONTEXT.md", "ai-kit/CORE.md", "GEMINI.md",
                         ".agents/skills/go-work/SKILL.md", ".claude/skills/go-work/SKILL.md",
                         ".agents/hooks/session-start.md", ".agents/hooks/session-start.sh",
                         ".agents/skills/ai-kit-bootstrap/SKILL.md", ".claude/rules/ai-kit-web.md",
                         ".cursor/rules/ai-kit-web.mdc", ".github/instructions/ai-kit-web.instructions.md",
                         ".windsurf/rules/ai-kit-web.md", ".clinerules/ai-kit-web.md",
                         ".windsurf/rules/ai-kit.md", "docs/DECISIONS.md",
                         ".codex/config.toml", ".cursor/mcp.json", ".gemini/settings.json", ".clinerules",
                         ".github/prompts/review.prompt.md", ".aider.conf.yml"):
                if ignored(path) != (mode == "private"):
                    errors.append(f"{mode}: wrong shared visibility: {path}")
            for path in (".env", ".claude/settings.local.json", "ai-kit/.upstream-cache/a",
                         "ai-kit/.metrics/tasks.jsonl", "ai-kit/.metrics/write.lock",
                         "go-cache/a", "test.out", "__pycache__/a.pyc", ".idea/workspace.xml",
                         ".netrc", ".pypirc", ".aider.chat.history.md", ".aider.tags.cache.v4/a",
                         "AI-KIT-0.6.5/README.md", "web/.next/cache/a", "__debug_bin1234"):
                if not ignored(path):
                    errors.append(f"{mode}: private/generated data visible: {path}")
            for path in ("composer.lock", "go.mod", "go.sum", "uv.lock", ".env.example",
                         "vendor/modules.txt", "src/SKILL.md", "bin/worker.py", ".cursorignore",
                         ".github/workflows/ci.yml", ".aiderignore"):
                if ignored(path):
                    errors.append(f"{mode}: intended project source ignored: {path}")
    return errors


def agent_registry_links(root: Path) -> list[str]:
    """Cross-check registry entries and optional sources against the distribution."""
    errors = []
    registry = install.load_agent_registry(root)
    for entry in registry["entries"]:
        if not (root / "template" / entry).is_file():
            errors.append("Agent registry entry missing from template: " + entry)
    destinations: set[str] = set()
    for agent, items in registry["optional"].items():
        for source, destination in items:
            if not (root / "integrations" / source).is_file():
                errors.append("Agent registry optional source missing: " + source)
            if destination in destinations:
                errors.append("Agent registry destination owned by multiple agents: " + destination)
            destinations.add(destination)
    return errors


def check(root: Path, *, git: str | None = None) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    required = ["VERSION", "LICENSE", "AGENTS.md", "PROJECT_CONTEXT.md", "README.md",
                "template/AGENTS.md", "template/ai-kit/CORE.md", "template/ai-kit/settings.json",
                "template/ai-kit/project.json", "template/ai-kit/MCP.md",
                "scripts/install.py", "scripts/router.py", "scripts/adr.py", "scripts/changelog.py",
                "scripts/metrics.py", "scripts/context.py", "scripts/adapters.py", "scripts/evaluate.py",
                "scripts/__init__.py", "template/ai-kit/METRICS.md",
                "template/ai-kit/stacks/FILAMENT.md", "template/.agents/skills/filament-work/SKILL.md",
                "integrations/agents.json", "integrations/claude-settings.git-ask.json",
                "integrations/claude-settings.data-ask.json", "templates/agent-secrets.ignore",
                "SKILL.md",
                "template/.agents/hooks/session-start.md", "template/.agents/hooks/session-start.sh",
                "template/ai-kit/router/selection.json",
                "template/ai-kit/router/providers/local.json",
                "template/ai-kit/router/providers/gemini.json",
                "templates/gitignore.private", "templates/gitignore.team",
                "aikit_cli.py", "__init__.py", "MANIFEST.in", "pyproject.toml", "tests/wheel_smoke.py",
                ".github/workflows/check-kit.yml", "docs/IMPLEMENTATION.md"]
    for relative in required:
        if not (root / relative).is_file():
            errors.append("Missing: " + relative)
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8")
        if 'aikit = "aikit.aikit_cli:main"' not in text:
            errors.append("pyproject.toml must declare the aikit console script")
        if "version = {file = [\"VERSION\"]}" not in text:
            errors.append("pyproject.toml must derive its version from VERSION")
    elif not (root / "aikit_cli.py").is_file():
        errors.append("Missing unified CLI entry point")
    for p in source_files(root):
        if p.is_symlink():
            errors.append("Linked source: " + str(p))
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append("Not UTF-8 text: " + str(p))
            continue
        if re.search(r"[\u0400-\u04ff]", text):
            errors.append("Unexpected Cyrillic project content: " + str(p))
        if p.suffix == ".json":
            try:
                json.loads(text)
            except ValueError as exc:
                errors.append(f"{p}: invalid JSON: {exc}")
        if p.name == "SKILL.md":
            try:
                fields = metadata(text)
                # The repository root is itself a skill; its folder name depends on the checkout.
                expected = "ai-kit" if p.parent == root else p.parent.name
                if fields["name"] != expected:
                    errors.append("Skill name/folder mismatch: " + str(p))
            except (ValueError, TypeError) as exc:
                errors.append(f"{p}: {exc}")
        if p.suffix != ".md":
            continue
        if any(line.rstrip() != line for line in text.splitlines()):
            errors.append("Trailing whitespace: " + str(p))
        if not text.endswith("\n"):
            errors.append("Missing final newline: " + str(p))
        # The root README is human onboarding that never enters project context, so it gets more room.
        if len(text.encode()) > (20000 if p == root / "README.md" else 12000):
            warnings.append("Large conditional document: " + str(p))
        for target in links(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            filename, _, anchor = unquote(target).partition("#")
            destination = (p.parent / filename).resolve() if filename else p.resolve()
            try:
                destination.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{p}: link escapes reference: {target}")
                continue
            if not destination.exists():
                errors.append(f"{p}: missing link: {target}")
            elif anchor and destination.is_file() and destination.suffix == ".md":
                if anchor not in headings(destination.read_text(encoding="utf-8")):
                    errors.append(f"{p}: missing heading: {target}")
    budgets = {"template/AGENTS.md": 2500, "template/ai-kit/CORE.md": 3000,
               "BOOTSTRAP_PROMPT.md": 2000}
    for relative, limit in budgets.items():
        if (root / relative).is_file() and (root / relative).stat().st_size > limit:
            errors.append(f"Always-loaded entry exceeds budget: {relative}")
    registry = root / "template/ai-kit/SKILLS.md"
    if registry.exists():
        expected = {p.parent.name for p in (root / "template/.agents/skills").glob("*/SKILL.md")}
        entries = re.findall(r"\.\./\.agents/skills/([^/]+)/SKILL.md", registry.read_text())
        if expected != set(entries) or len(entries) != len(set(entries)):
            errors.append("Skill registry differs from actual source skills")
    for relative in ("template/PROJECT_CONTEXT.md", "template/docs/DECISIONS.md", "template/CHANGELOG.md"):
        if (root / relative).exists() and re.search(r"2026-\d\d-\d\d|5dd530b9|voice conversation",
                                                   (root / relative).read_text()):
            errors.append("Kit-maintenance history leaked into project template: " + relative)
    project_json = root / "template/ai-kit/project.json"
    if project_json.is_file():
        try:
            value = json.loads(project_json.read_text(encoding="utf-8"))
            if type(value.get("schema")) is not int or value["schema"] != 1:
                raise ValueError("schema must be 1")
            evidence = value.get("evidence")
            if (value.get("modules") != [] or not isinstance(value.get("operations"), dict) or
                    not isinstance(evidence, dict) or evidence.get("schema") != 1 or
                    evidence.get("modules") != []):
                errors.append("Project template project.json must start empty of module facts")
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append("Invalid project template project.json: " + str(exc))
    providers_dir = root / "template" / "ai-kit" / "router" / "providers"
    model_ids: list[str] = []
    if providers_dir.is_dir():
        for provider_path in sorted(providers_dir.glob("*.json")):
            try:
                config = json.loads(provider_path.read_text(encoding="utf-8"))
                if not isinstance(config, dict):
                    raise ValueError("provider must be an object")
                tier = config.get("tier", "cloud")
                if tier not in {"cloud", "local", "free"}:
                    errors.append(f"Unknown provider tier: {provider_path.name}")
                user_supplied = config.get("user_supplied_models") is True
                if "user_supplied_models" in config and not isinstance(config["user_supplied_models"], bool):
                    raise ValueError("user_supplied_models must be a boolean")
                status = config.get("verification_status", "verified")
                if status not in {"verified", "pending"}:
                    errors.append(f"Unknown verification_status: {provider_path.name}")
                verified = config.get("verified_documentation_date")
                if isinstance(verified, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified):
                    pass
                elif user_supplied:
                    pass
                elif status == "pending":
                    warnings.append(f"Provider {provider_path.name} verification is pending")
                else:
                    errors.append("Provider lacks a verified_documentation_date: " + provider_path.name)
                supported = config.get("supported_efforts", {})
                if not isinstance(supported, dict):
                    raise ValueError("supported_efforts must be an object")
                roles = config.get("roles")
                if not isinstance(roles, dict) or not roles:
                    raise ValueError("roles must be a nonempty object")
                for role, spec in roles.items():
                    if not isinstance(spec, dict):
                        raise ValueError(f"Invalid role spec: {role}")
                    model = spec.get("model")
                    if model is not None and not isinstance(model, str):
                        raise ValueError(f"Invalid model for role {role}")
                    if model is not None:
                        model_ids.append(model)
                    elif not (user_supplied or status == "pending"):
                        errors.append(f"Provider role lacks a model: {provider_path.name} role {role}")
                    if "effort" in spec:
                        if spec["effort"] not in supported.get(role, []):
                            errors.append(f"Unsupported configured effort: {provider_path.name} role {role}")
                    elif role in supported and not user_supplied:
                        errors.append(f"Role declares supported efforts but uses none: "
                                      f"{provider_path.name} role {role}")
            except (ValueError, KeyError, TypeError) as exc:
                errors.append("Invalid provider configuration: " + str(exc))
    try:
        errors.extend(agent_registry_links(root))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append("Invalid agent registry: " + str(exc))
    for p in (root / "template").rglob("*.md"):
        text = p.read_text()
        if re.search(r"gpt-[0-9]", text) or any(model_id in text for model_id in model_ids):
            errors.append("Active model IDs duplicated outside provider configuration: " + str(p))
    for mode in ("private", "team"):
        p = root / "templates" / ("gitignore." + mode)
        if p.exists() and any(line in {"SKILL.md", "vendor/"} for line in p.read_text().splitlines()):
            errors.append("Overbroad skill/vendor ignore: " + mode)
    git = git or os.environ.get("AI_KIT_GIT") or shutil.which("git")
    if git:
        try:
            errors.extend(visibility(root, git))
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            errors.append("Git visibility verification failed: " + str(exc))
    else:
        warnings.append("Git unavailable: visibility checks were not run")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--git")
    args = parser.parse_args(argv)
    errors, warnings = check(args.root, git=args.git)
    print(json.dumps({"errors": errors, "warnings": warnings}, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
