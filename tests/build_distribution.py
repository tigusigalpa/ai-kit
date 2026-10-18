"""Build release archives in an isolated copy with synthetic private-file probes."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_distribution

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROBES = ("AGENTS.md", "PROJECT_CONTEXT.md", "WIKI.md", "auth.json",
                  "ai-kit/.orchestration/state.json", "ai-kit/.memory/session/private.json", "ai-kit/.metrics/private.json",
                  "ai-kit/.upstream-cache/private.md", "ai-kit/.design/private.md",
                  "docs/.private/private.md", "docs/auth.json", "docs/.env.release",
                  "template/.env", "docs/private.pem", "docs/id_ed25519")
MARKER = b"SYNTHETIC_PRIVATE_" + b"DISTRIBUTION_PROBE_MUST_NOT_SHIP"


def prepare(destination: Path) -> list[dict]:
    destination = destination.resolve()
    if destination.is_relative_to(ROOT):
        raise ValueError("Distribution output must be outside the source checkout")
    if list(destination.glob("*.whl")) or list(destination.glob("*.tar.gz")):
        raise ValueError("Choose an output directory without existing distribution archives")
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="aikit-source-", dir=destination.parent) as temporary:
        source = Path(temporary) / "source"
        source.mkdir()
        names = {p.name for pattern in ("*.md", "*.py") for p in ROOT.glob(pattern)} - check_distribution.LOCAL_FILES
        names.update(("VERSION", "LICENSE", "MANIFEST.in", "pyproject.toml", "Makefile", "Dockerfile",
                      ".dockerignore", ".gitignore", ".gitattributes"))
        for name in sorted(names):
            shutil.copy2(ROOT / name, source / name)
        ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.egg-info", ".memory", ".metrics",
                                       ".upstream-cache", ".design", ".private", ".orchestration", ".env", ".env.*", "auth.json",
                                       ".aws", ".codex", ".claude", ".secrets", ".netrc", ".pypirc",
                                       "*.pem", "*.p12", "*.pfx", "id_rsa*", "id_ed25519*")
        for name in ("scripts", "tests", "docs", "template", "templates", "integrations", "ai-kit", ".agents", ".github", "docker", "deploy"):
            shutil.copytree(ROOT / name, source / name, ignore=ignore)
        for name in PRIVATE_PROBES:
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(MARKER + b"\n")
        subprocess.run([sys.executable, "-m", "build", "--no-isolation", "--outdir", str(destination)],
                       cwd=source, check=True)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        result = check_distribution.check_archives(destination, version)
        for item in result:
            members = check_distribution._members(destination / item["file"])
            if any(MARKER in data for data in members.values()):
                raise ValueError("Synthetic private marker leaked into an archive")
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        for item in prepare(args.destination):
            print(item["file"] + ": metadata/resources/privacy passed; sha256=" + item["sha256"])
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print("Distribution build refused: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
