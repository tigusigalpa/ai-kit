"""Install a built wheel into a clean venv and exercise its bundled resources."""
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import venv
import zipfile


def venv_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def venv_aikit(root: Path) -> Path:
    return root / ("Scripts/aikit.exe" if sys.platform == "win32" else "bin/aikit")


def main(argv: list[str] | None = None) -> int:
    arguments = argv if argv is not None else sys.argv[1:]
    if len(arguments) != 1:
        raise SystemExit("Usage: wheel_smoke.py WHEEL")
    wheel = Path(arguments[0]).resolve()
    if wheel.is_dir():
        candidates = sorted(wheel.glob("*.whl"))
        if len(candidates) != 1:
            raise SystemExit("Expected exactly one wheel in: " + str(wheel))
        wheel = candidates[0]
    if not wheel.is_file():
        raise SystemExit("Wheel not found: " + str(wheel))
    with zipfile.ZipFile(wheel) as package:
        for name in ("AGENTS.md", "PROJECT_CONTEXT.md", "WIKI.md"):
            if "aikit/" + name in package.namelist() or "aikit/template/" + name not in package.namelist():
                raise RuntimeError("Wheel must exclude local maintainer files and retain project templates: " + name)
    with tempfile.TemporaryDirectory(prefix="ai-kit-wheel-") as folder:
        root = Path(folder).resolve()
        env = root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(env)
        python = venv_python(env)
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        def run(command):
            subprocess.run([str(item) for item in command], cwd=root, env=environment, check=True)
        run([python, "-m", "pip", "install", "--no-index", "--no-deps", wheel])
        aikit = venv_aikit(env)
        run([aikit, "route", "implement a feature"])
        for module in ("learning", "adaptive", "benchmark", "memory"):
            run([python, "-c", "from aikit.scripts import " + module])
        run([aikit, "benchmark", "--help"])
        run([aikit, "check"])
        # Exercise the packaged offline dialogue pipeline, not only dispatcher help.
        workspace = root / "private memory"
        for name in ("chatgpt", "openrouter"):
            source = root / (name + ".json")
            source.write_text('{"messages":[{"role":"user","content":"Fact stack = Laravel"}]}', encoding="utf-8")
            run([aikit, "memory", "import", workspace, source, "--name", name, "--apply"])
        merged = subprocess.run([str(aikit), "memory", "merge", str(workspace), "--left", "chatgpt",
                                 "--right", "openrouter", "--apply"], cwd=root, env=environment,
                                capture_output=True, text=True, check=True)
        import json
        merge_id = json.loads(merged.stdout)["merge_id"]
        run([aikit, "memory", "export", workspace, "--merge", merge_id, "--draft", "--apply"])
        if not (workspace / "exports" / merge_id / "chatgpt-draft.md").is_file():
            raise RuntimeError("Wheel dialogue export is missing")
        project = root / "project"
        run([aikit, "install", project, "--preset", "minimal", "--agent", "codex", "--apply", "--check"])
        run([aikit, "adapters", "report", "--project", project])
        run([aikit, "context", "select", project])
        audit_project = root / "audit project"
        run([aikit, "install", audit_project, "--with-security-audit", "--with-strix", "--with-context7", "--with-web-design", "--agent", "codex",
             "--agent", "claude", "--apply", "--check"])
        from_manifest = audit_project / "ai-kit/vendor/security-audit/UPSTREAM.json"
        if not from_manifest.is_file() or not (audit_project / ".agents/skills/security-audit/agents/openai.yaml").is_file():
            raise RuntimeError("Wheel did not install the optional audit package and invocation policy")
        strix_manifest = audit_project / "ai-kit/vendor/strix/UPSTREAM.json"
        strix_reference = audit_project / "ai-kit/vendor/strix/penetration-testing-with-strix/SKILL.md"
        if not strix_manifest.is_file() or not strix_reference.is_file() \
                or not (audit_project / ".claude/skills/strix/SKILL.md").is_file():
            raise RuntimeError("Wheel did not install the optional Strix references and native entry point")
        if not (audit_project / "ai-kit/CONTEXT7.md").is_file() \
                or not (audit_project / ".claude/skills/context7-docs/SKILL.md").is_file():
            raise RuntimeError("Wheel did not install the Context7 guide and native documentation skill")
        for name in ("web-design", "laravel-blade-ui", "ui-review", "design-extract"):
            if not (audit_project / f".claude/skills/{name}/SKILL.md").is_file():
                raise RuntimeError("Wheel did not install the Web Design native skill: " + name)
        if not (audit_project / "docs/design/BRIEF.md").is_file():
            raise RuntimeError("Wheel did not initialize the Web Design project documents")
        run([aikit, "context", "select", audit_project, "--workflow", "web-design"])
        run([aikit, "install", audit_project, "--apply", "--check"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
