"""Collect read-only Docker evidence; no pruning or volume/container deletion."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess


def command(argv: list[str]) -> str:
    result = subprocess.run(argv, capture_output=True, text=True, timeout=60, check=True)
    return result.stdout


def collect(project: str, *, docker: str = "docker", run=command, builder: str | None = None) -> dict:
    context = run([docker, "context", "show"]).strip()
    run([docker, "info", "--format", "{{.ServerVersion}}"])
    names = run([docker, "volume", "ls", "--filter", "label=com.docker.compose.project=" + project,
                 "--format", "{{.Name}}"]).splitlines()
    volumes = []
    for name in names:
        # Pass exact names as arguments, never as shell fragments.
        data = json.loads(run([docker, "volume", "inspect", name]))[0]
        labels = data.get("Labels") or {}
        refs = run([docker, "ps", "-a", "--filter", "volume=" + name, "--format", "{{.ID}}"]).splitlines()
        volumes.append({"name": name, "project_label": labels.get("com.docker.compose.project"),
                        "declared_disposable": labels.get("ai-kit.disposable") == "true",
                        "container_references": refs, "eligible_without_more_evidence": False})
    report = {"context": context, "project": project, "volumes": volumes,
              "disk_usage_raw": run([docker, "system", "df", "-v"]),
              "measured_project_bytes": None,
              "note": "Human-readable usage is evidence, not exact project ownership or a deletion plan."}
    if builder:
        report["builder"] = builder
        report["build_cache_usage_raw"] = run([docker, "buildx", "du", "--builder", builder, "--format", "json"])
        report["builder_project_ownership"] = "unverified"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--builder")
    args = parser.parse_args(argv)
    if not shutil.which("docker"):
        parser.exit(1, "Docker client unavailable; install/configure the actual project runtime first.\n")
    try:
        print(json.dumps(collect(args.project, builder=args.builder), indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Docker evidence unavailable: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
