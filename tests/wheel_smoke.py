"""Install a built wheel into a clean venv and exercise its bundled resources."""
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import venv


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
        for module in ("learning", "adaptive", "benchmark"):
            run([python, "-c", "from aikit.scripts import " + module])
        run([aikit, "benchmark", "--help"])
        run([aikit, "check"])
        project = root / "project"
        run([aikit, "install", project, "--preset", "minimal", "--agent", "codex", "--apply", "--check"])
        run([aikit, "adapters", "report", "--project", project])
        run([aikit, "context", "select", project])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
