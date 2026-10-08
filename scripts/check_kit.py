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

ROOT = Path(__file__).resolve().parents[1]


def source_files(root: Path):
    excluded = {".git", "__pycache__", ".upstream-cache", ".pytest_cache"}
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in excluded]
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
        for mode in ("private", "team"):
            (scratch / ".gitignore").write_bytes((root / "templates" / ("gitignore." + mode)).read_bytes())
            for path in ("AGENTS.md", "PROJECT_CONTEXT.md", "ai-kit/CORE.md",
                         ".agents/skills/go-work/SKILL.md", ".claude/skills/go-work/SKILL.md",
                         "docs/DECISIONS.md"):
                if ignored(path) != (mode == "private"):
                    errors.append(f"{mode}: wrong shared visibility: {path}")
            for path in (".env", ".claude/settings.local.json", "ai-kit/.upstream-cache/a",
                         "go-cache/a", "test.out", "__pycache__/a.pyc"):
                if not ignored(path):
                    errors.append(f"{mode}: private/generated data visible: {path}")
            for path in ("composer.lock", "go.mod", "go.sum", "uv.lock", ".env.example",
                         "vendor/modules.txt", "src/SKILL.md", "bin/worker.py"):
                if ignored(path):
                    errors.append(f"{mode}: intended project source ignored: {path}")
    return errors


def check(root: Path, *, git: str | None = None) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    required = ["VERSION", "LICENSE", "AGENTS.md", "PROJECT_CONTEXT.md", "README.md",
                "template/AGENTS.md", "template/ai-kit/CORE.md", "template/ai-kit/settings.json",
                "scripts/install.py", "templates/gitignore.private", "templates/gitignore.team",
                ".github/workflows/check-kit.yml", "docs/IMPLEMENTATION.md"]
    for relative in required:
        if not (root / relative).is_file():
            errors.append("Missing: " + relative)
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
                if fields["name"] != p.parent.name:
                    errors.append("Skill name/folder mismatch: " + str(p))
            except (ValueError, TypeError) as exc:
                errors.append(f"{p}: {exc}")
        if p.suffix != ".md":
            continue
        if any(line.rstrip() != line for line in text.splitlines()):
            errors.append("Trailing whitespace: " + str(p))
        if not text.endswith("\n"):
            errors.append("Missing final newline: " + str(p))
        if len(text.encode()) > 12000:
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
    provider_path = root / "template/ai-kit/router/providers/openai.json"
    if provider_path.exists():
        try:
            config = json.loads(provider_path.read_text(encoding="utf-8"))
            for role, spec in config["roles"].items():
                if spec["effort"] not in config["supported_efforts"][role]:
                    errors.append("Unsupported configured effort: " + role)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append("Invalid provider configuration: " + str(exc))
        for p in (root / "template").rglob("*.md"):
            if re.search(r"gpt-[0-9]", p.read_text()):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--git")
    args = parser.parse_args()
    errors, warnings = check(args.root, git=args.git)
    print(json.dumps({"errors": errors, "warnings": warnings}, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
