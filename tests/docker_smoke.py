"""Exercise a local CLI image with isolated fixtures and no runtime network access."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid


def docker(arguments: list[str], *, expected: int = 0, timeout: int = 180) -> str:
    result = subprocess.run(["docker", *arguments], capture_output=True, text=True,
                            encoding="utf-8", timeout=timeout)
    if result.returncode != expected:
        raise RuntimeError(f"Docker exited {result.returncode}, expected {expected}: "
                           + result.stdout + result.stderr)
    return result.stdout


def runtime_arguments(image: str, project: Path | None = None, *, readonly: bool = False,
                      entrypoint: str | None = None, create: bool = False,
                      name: str | None = None, init: bool = True) -> list[str]:
    arguments = ["create" if create else "run"]
    if not create:
        arguments.append("--rm")
    if init:
        arguments.append("--init")
    arguments.extend(["--network", "none", "--read-only", "--cap-drop", "ALL",
                      "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m",
                      "--label", "ai-kit.disposable=true"])
    if hasattr(os, "getuid") and os.getuid() != 0:
        arguments.extend(["--user", f"{os.getuid()}:{os.getgid()}"])
    if project is not None:
        source = project.resolve()
        if not source.is_dir():
            raise ValueError("Smoke project must be an existing directory")
        mount = f"type=bind,source={source},target=/workspace" + (",readonly" if readonly else "")
        arguments.extend(["--mount", mount])
    if entrypoint:
        arguments.extend(["--entrypoint", entrypoint])
    if name:
        arguments.extend(["--name", name, "--label", "ai-kit.test-run=" + name])
    if create:
        arguments.append("--interactive")
    return [*arguments, image]


def context_smoke(source: Path, base: Path, builder: str | None) -> None:
    """Use Docker's actual ignore engine on synthetic sensitive files, not user secrets."""
    context = base / "build context"
    output = base / "context export"
    context.mkdir()
    for name in ("Dockerfile", ".dockerignore"):
        (context / name).write_bytes((source / name).read_bytes())
    included = ("VERSION", "scripts/install.py", "template/AGENTS.md", "template/PROJECT_CONTEXT.md",
                "template/WIKI.md", "template/.agents/skills/web-design/SKILL.md",
                "template/ai-kit/vendor/security-audit/LICENSE", "docker/check_version.py")
    excluded = ("AGENTS.md", "PROJECT_CONTEXT.md", "WIKI.md", ".env", ".git/config",
                ".codex/auth.json", ".aws/credentials", "private-helper.py",
                "docs/.private/brief.txt", "docs/auth.json", "template/.env", "ai-kit/.metrics/tasks.jsonl",
                "ai-kit/.orchestration/state.json", "ai-kit/.design/screenshots/private.png", "ai-kit/.memory/session/imports/private.json",
                "scripts/__pycache__/private.pyc")
    for name in included + excluded:
        path = context / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"Synthetic build-context probe.\n")
    arguments = ["buildx", "build"]
    if builder:
        arguments.extend(["--builder", builder])
    arguments.extend(["--target", "context-audit", "--output", "type=local,dest=" + str(output), str(context)])
    docker(arguments, timeout=300)
    if not all((output / name).is_file() for name in included):
        raise RuntimeError("Docker ignored required kit sources")
    if any((output / name).exists() for name in excluded):
        raise RuntimeError("Docker exposed a synthetic secret or private state in the build context")
    print("Build context: required sources included; synthetic secrets/private state excluded.", flush=True)


def signal_smoke(image: str, project: Path, *, init: bool) -> None:
    """Without --init the CLI is PID 1, as in a Kubernetes Job, and must handle SIGTERM itself."""
    name = "aikit-cli-signal-" + uuid.uuid4().hex[:12]
    created = False
    try:
        docker([*runtime_arguments(image, project, readonly=True, create=True, name=name, init=init),
                "install", "/workspace", "--interactive"])
        created = True
        docker(["start", name])
        deadline = time.monotonic() + 15
        while "AI-KIT interactive installer" not in docker(["logs", name]):
            if time.monotonic() >= deadline:
                raise RuntimeError("Interactive CLI did not reach its input prompt")
            time.sleep(0.2)
        docker(["stop", "--time", "5", name])
        state = json.loads(docker(["inspect", name]))[0]
        if state["State"]["Running"] or state["State"]["ExitCode"] != 143:
            raise RuntimeError("SIGTERM did not terminate the CLI without a forced kill")
        mode = "with --init" if init else "as PID 1 without --init"
        print(f"SIGTERM reached the foreground CLI {mode}; preview terminated with exit 143.", flush=True)
    finally:
        if created:
            record = json.loads(docker(["inspect", name]))[0]
            if record["Config"]["Labels"].get("ai-kit.test-run") != name:
                raise RuntimeError("Refusing cleanup of an unrelated container")
            docker(["rm", "--force", name])


def smoke(image: str, *, source: Path | None = None, builder: str | None = None) -> None:
    inspection = json.loads(docker(["image", "inspect", image]))[0]
    config = inspection["Config"]
    if config["User"] != "10001:10001" or config["Entrypoint"] != ["aikit"]:
        raise RuntimeError("Image must have a non-root user and direct aikit entry point")
    if config.get("ExposedPorts") or config.get("Healthcheck") or config.get("Volumes"):
        raise RuntimeError("A one-shot CLI must not introduce ports, a service probe or anonymous volumes")
    identity_code = ("import json,os,aikit.aikit_cli; "
                     "print(json.dumps({'uid':os.getuid(),'version':aikit.aikit_cli.__version__}))")
    identity = json.loads(docker([*runtime_arguments(image, entrypoint="python"), "-c", identity_code]))
    if identity["uid"] == 0 or identity["version"] != config["Labels"]["org.opencontainers.image.version"]:
        raise RuntimeError("Runtime UID/version does not match the image contract")
    # Every distribution must carry LF text; vendored upstream bytes are pinned separately.
    newline_code = ("import pathlib,aikit.aikit_cli as c; root=c.ROOT; "
                    "bad=[p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() "
                    "and 'vendor' not in p.relative_to(root).parts and b'\\r' in p.read_bytes()[:1048576] "
                    "and p.suffix in {'.md','.py','.json','.toml','.yml','.yaml','.txt','.sh','.mdc','.cfg','.in'}]; "
                    "print(len(bad), *bad[:5])")
    crlf = docker([*runtime_arguments(image, entrypoint="python"), "-c", newline_code]).split()
    if crlf[0] != "0":
        raise RuntimeError("Packaged text files contain CR line endings: " + " ".join(crlf[1:]))
    docker([*runtime_arguments(image), "--help"])
    docker([*runtime_arguments(image), "route", "implement a feature"])
    docker([*runtime_arguments(image), "check"])

    with tempfile.TemporaryDirectory(prefix="aikit-container-") as folder:
        base = Path(folder).resolve()
        project = base / "project with spaces"
        project.mkdir(mode=0o777)
        project.chmod(0o777)
        preserved = {"README.md": b"Existing project README.\r\n", ".mcp.json": b'{"mcpServers":{}}\r\n'}
        for name, data in preserved.items():
            (project / name).write_bytes(data)
        preview = json.loads(docker([*runtime_arguments(image, project, readonly=True), "install", "/workspace",
                                    "--with-web-design"]))
        if not preview["preview"] or (project / "ai-kit").exists():
            raise RuntimeError("Preview changed the mounted project")
        docker([*runtime_arguments(image, project, readonly=True), "install", "/workspace", "--apply"], expected=1)
        if (project / "ai-kit").exists():
            raise RuntimeError("Read-only mount refusal left project writes")
        docker([*runtime_arguments(image, project), "install", "/workspace", "--agent", "codex", "--agent", "claude",
                "--agent", "devin", "--with-uuid", "--with-claude-github", "--with-web-design", "--with-context7",
                "--with-security-audit", "--with-strix", "--with-orchestration", "--apply", "--check"])
        for relative in ("ai-kit/UUID.md", "ai-kit/CLAUDE-GITHUB.md", ".devin/rules/ai-kit.md",
                         "ai-kit/stacks/JAVASCRIPT.md", ".claude/skills/javascript-work/SKILL.md"):
            if not (project / relative).is_file():
                raise RuntimeError("Image did not deliver a selected development resource: " + relative)
        if json.loads((project / "ai-kit/settings.json").read_text(encoding="utf-8"))["chat_language"] != "English":
            raise RuntimeError("Image does not use the English fresh-install default")
        if not (project / ".codex/agents/aikit_worker.toml").is_file():
            raise RuntimeError("Orchestration helper was not installed")
        (project / "task.json").write_text('{"schema":1,"id":"image-smoke","instruction":"Summarize","input_files":[]}', encoding="utf-8")
        docker([*runtime_arguments(image, project, readonly=True), "orchestrate", "run", "/workspace", "--task", "task.json"])
        docker([*runtime_arguments(image, project, readonly=True), "orchestrate", "status", "/workspace"])
        if preserved != {name: (project / name).read_bytes() for name in preserved}:
            raise RuntimeError("Installation replaced existing project/client documents")
        report = json.loads(docker([*runtime_arguments(image, project, readonly=True), "doctor", "/workspace"]))
        if report["errors"]:
            raise RuntimeError("Installed project failed doctor: " + str(report["errors"]))
        selection = json.loads(docker([*runtime_arguments(image, project, readonly=True), "context", "select",
                                       "/workspace", "--workflow", "web-design"]))
        if selection["workflow"] != "web-design":
            raise RuntimeError("Installed design context was not selected")
        repeated = json.loads(docker([*runtime_arguments(image, project), "install", "/workspace", "--apply"]))
        if repeated["writes"]:
            raise RuntimeError("Repeated installation was not stable")
        signal_smoke(image, project, init=True)
        signal_smoke(image, project, init=False)
        if source:
            context_smoke(source, base, builder)
    print("CLI image smoke passed: offline/read-only runtime, preview, refusal, all extras, preservation and rerun.", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Already built local image; this command does not publish images")
    parser.add_argument("--context", type=Path, help="Reference checkout for an actual Docker ignore-engine check")
    parser.add_argument("--builder", help="Optional dedicated builder for the context-export check")
    args = parser.parse_args(argv)
    try:
        smoke(args.image, source=args.context, builder=args.builder)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print("Container verification failed: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
