"""Exercise the installed task CLI with disposable source and synthetic acceptance."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def smoke() -> None:
    with tempfile.TemporaryDirectory(prefix="aikit-task-smoke-") as temporary:
        base = Path(temporary).resolve()
        project = base / "application with spaces"
        project.mkdir()

        def cli(*args):
            result = subprocess.run([sys.executable, "-m", "aikit.aikit_cli", *map(str, args)],
                                    cwd=project, capture_output=True, text=True, timeout=60)
            if result.returncode:
                raise RuntimeError("Synthetic task CLI failed: " + result.stderr + result.stdout)
            return result.stdout

        cli("install", project, "--with-task-workflow", "--apply", "--check")
        (project / "app.py").write_text("value = 1\n", encoding="utf-8")
        git_env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        git_env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(project)], check=True, env=git_env)
        subprocess.run(["git", "-C", str(project), "add", "app.py", ".gitignore"], check=True, env=git_env)
        subprocess.run(["git", "-C", str(project), "-c", "user.name=Smoke Fixture",
                        "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                        "commit", "-qm", "Synthetic task source"], check=True, env=git_env)
        definition = {"schema": 1, "id": "smoke", "title": "Synthetic CLI fixture", "description": "Keep value equal to one.",
                      "acceptance": [{"id": "value", "description": "The source retains value one."}],
                      "checks": [{"id": "tests", "argv": [sys.executable, "-c", "assert 'value = 1' in open('app.py').read()"],
                                  "cwd": ".", "timeout_seconds": 10}]}
        spec = base / "spec.json"
        spec.write_text(json.dumps(definition), encoding="utf-8")
        cli("task", "create", project, "--from-json", spec)
        if (project / "ai-kit/.tasks").exists():
            raise AssertionError("Create preview wrote task state")
        cli("task", "create", project, "--from-json", spec, "--apply")
        cli("task", "transition", project, "--task-id", "smoke", "--to", "implementing", "--apply")
        cli("task", "check", project, "--task-id", "smoke", "--check-id", "tests")
        checked = json.loads(cli("task", "check", project, "--task-id", "smoke", "--check-id", "tests", "--apply"))
        assert checked["receipt"]["outcome"] == "passed", checked
        for state in ("reviewing", "awaiting_approval"):
            cli("task", "transition", project, "--task-id", "smoke", "--to", state, "--apply")
        report = json.loads(cli("task", "status", project, "--task-id", "smoke"))
        approval = {"schema": 1, "task_id": "smoke", "fingerprint": report["fingerprint"],
                    "reviewer": "Synthetic smoke assertion", "criteria": [
                        {"id": "value", "passed": True, "evidence": "Synthetic fixture source and check were inspected."}]}
        review = base / "review.json"
        review.write_text(json.dumps(approval), encoding="utf-8")
        cli("task", "accept", project, "--task-id", "smoke", "--from-json", review, "--apply")
        report = json.loads(cli("task", "status", project, "--task-id", "smoke"))
        assert report["accepted_current"], report
        (project / "app.py").write_text("value = 2\n", encoding="utf-8")
        report = json.loads(cli("task", "status", project, "--task-id", "smoke"))
        assert report["effective_state"] == "stale" and not report["accepted_current"], report
    print("Task workflow CLI smoke passed: preview, states, source-bound checks, synthetic acceptance and staleness.")


if __name__ == "__main__":
    smoke()
