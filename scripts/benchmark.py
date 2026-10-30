"""Preview-first isolated A/B/C trials using an explicitly configured worker protocol."""
from __future__ import annotations

import argparse
import copy
import fnmatch
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adaptive
import context
import install
import learning
import metrics
import router

ARMS = ("baseline", "kit-fixed", "kit-adaptive")
ROOT = Path(__file__).resolve().parents[1]


def argv(value: object) -> list[str]:
    if (not isinstance(value, list) or not value or
            any(not isinstance(item, str) or not item or "\x00" in item for item in value)):
        raise ValueError("Commands must be nonempty argv lists; shell strings are unsupported")
    if not Path(value[0]).is_absolute() or not Path(value[0]).is_file():
        raise ValueError("Command executable must be an existing absolute file path")
    return value


def validate_pack(value: object, project: Path) -> dict:
    pack = metrics._fields(value, {"schema", "experiment", "revision", "repeats", "fixed", "worker",
                                  "tasks", "checks", "timeout_seconds", "kit_agents", "kit_preset"},
                           "benchmark pack")
    if type(pack.get("schema")) is not int or pack["schema"] != 1:
        raise ValueError("Expected benchmark schema 1")
    metrics._identifier(pack.get("experiment"), "experiment")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", pack["experiment"]):
        raise ValueError("Experiment must be a portable directory name")
    revision = pack.get("revision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision):
        raise ValueError("Pin a full Git commit ID")
    if type(pack.get("repeats")) is not int or not 1 <= pack["repeats"] <= 100:
        raise ValueError("Repeats must be 1-100")
    adaptive.validate_pin(pack.get("fixed"))
    pack["kit_agents"] = install.agent_selection(pack.get("kit_agents", ["codex"]),
                                                 install.load_agent_registry()["names"], unique=True)
    pack["kit_preset"] = pack.get("kit_preset", "minimal")
    if pack["kit_preset"] not in install.PRESETS:
        raise ValueError(f"Unknown kit preset: {pack['kit_preset']}")
    worker = metrics._fields(pack.get("worker"), {"protocol", "argv"}, "worker")
    if worker.get("protocol") != "aikit-worker-v1":
        raise ValueError("Worker must explicitly implement aikit-worker-v1")
    argv(worker.get("argv"))
    if type(pack.get("timeout_seconds")) is not int or not 1 <= pack["timeout_seconds"] <= 86400:
        raise ValueError("Timeout must be 1-86400 seconds per process")
    if not isinstance(pack.get("checks"), list):
        raise ValueError("Checks must be an explicit list (empty means not-run)")
    for command in pack["checks"]:
        argv(command)
    tasks = pack.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Include at least one task")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) != {"task_id", "prompt_file", "rubric_file", "path", "stack", "operation", "risks", "capabilities"}:
            raise ValueError("Invalid benchmark task fields")
        identifier = metrics._identifier(task["task_id"], "task_id")
        if len(identifier) > 110 or identifier in seen:
            raise ValueError("Task IDs must be unique and at most 110 characters")
        seen.add(identifier)
        for field in ("prompt_file", "rubric_file", "path"):
            if not isinstance(task[field], str) or not task[field]:
                raise ValueError("Task paths must be nonempty relative paths")
        if task["path"] != ".":
            install.safe_path(project, task["path"] + "/__path_probe__")
        if task["stack"] not in metrics.STACKS or task["operation"] not in router.OPERATIONS:
            raise ValueError("Unknown stack/operation")
        if not isinstance(task["risks"], list) or any(r not in router.RISKS for r in task["risks"]):
            raise ValueError("Unknown risks")
        if not isinstance(task["capabilities"], list):
            raise ValueError("Capabilities must be a list")
        for capability in task["capabilities"]:
            metrics._identifier(capability, "capability")
    return copy.deepcopy(pack)


def git_command(project: Path, args: list[str], *, git: str | None = None, input_bytes: bytes | None = None) -> bytes:
    executable = git or shutil.which("git")
    if not executable:
        raise ValueError("Git is unavailable")
    try:
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        return subprocess.run([executable, "--no-replace-objects", "-C", str(project), *args], check=True,
                              capture_output=True, env=environment, input=input_bytes, timeout=120).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Git snapshot command failed") from exc


def secret_path(name: str, patterns: list[str]) -> bool:
    blocked = False
    for pattern in patterns:
        negative = pattern.startswith("!")
        pattern = pattern.lstrip("!")
        directory = pattern.endswith("/")
        pattern = pattern.strip("/")
        if (fnmatch.fnmatch(name, pattern) or ("/" not in pattern and any(fnmatch.fnmatch(p, pattern) for p in name.split("/"))) or
                (directory and name.startswith(pattern + "/"))):
            blocked = not negative
    return blocked


def snapshot_files(project: Path, revision: str, *, git: str | None = None) -> list[tuple[str, bytes, int]]:
    toplevel = Path(git_command(project, ["rev-parse", "--show-toplevel"], git=git).decode().strip()).resolve()
    if toplevel != project.resolve():
        raise ValueError("Benchmark project must be the Git working-tree root")
    resolved = git_command(project, ["rev-parse", "--verify", revision + "^{commit}"], git=git).decode().strip()
    if resolved != revision:
        raise ValueError("Starting revision is not the specified commit")
    listing = git_command(project, ["ls-tree", "-r", "-z", revision], git=git)
    names, portable_names = [], set()
    detected = install.detect_facts(project)
    patterns = install.secret_patterns(ROOT, detected["modules"])
    patterns.extend(["auth.json", ".pypirc"])
    for entry in listing.split(b"\x00"):
        if not entry:
            continue
        header, name_bytes = entry.split(b"\t", 1)
        mode, _, blob_id = header.split()
        name = name_bytes.decode("utf-8")
        portable = name.casefold()
        if portable in portable_names:
            raise ValueError("Case-colliding Git paths are not a portable benchmark snapshot")
        portable_names.add(portable)
        if mode not in {b"100644", b"100755"}:
            raise ValueError("Snapshots refuse symlinks, submodules and non-regular Git entries")
        # Refuse a compromised fixture instead of silently changing its starting state.
        parts = name.split("/")
        if (any(p in {".git", ".metrics", ".aws", ".ssh"} for p in parts) or
                secret_path(name, patterns) or
                parts[-1] == ".env" or parts[-1].endswith((".pem", ".key"))):
            raise ValueError("Tracked secret/runtime path in benchmark revision; use a sanitized test repository")
        install.safe_path(project, name)
        if name.startswith("ai-kit/"):
            raise ValueError("Starting revision already contains AI-KIT; baseline requires a pre-kit fixture")
        names.append((name, mode, blob_id.decode()))
    # Read immutable blobs directly: archive/checkout filters can apply CRLF, export-ignore or substitutions.
    blobs = git_command(project, ["cat-file", "--batch"], git=git,
                        input_bytes="".join(blob_id + "\n" for _, _, blob_id in names).encode())
    files = []
    with io.BytesIO(blobs) as source:
        for name, mode, blob_id in names:
            header = source.readline().split()
            if len(header) != 3 or header[0].decode() != blob_id or header[1] != b"blob":
                raise ValueError("Unexpected Git blob response")
            data = source.read(int(header[2]))
            if source.read(1) != b"\n":
                raise ValueError("Incomplete Git blob response")
            blob = b"blob " + str(len(data)).encode() + b"\x00" + data
            digest = hashlib.sha256(blob) if len(blob_id) == 64 else hashlib.sha1(blob)
            if digest.hexdigest() != blob_id:
                raise ValueError("Git blob integrity check failed")
            files.append((name, data, 0o755 if mode == b"100755" else 0o644))
    return files


def prepare(project: Path, pack_file: Path, *, git: str | None = None) -> dict:
    project = metrics._target(project)
    pack_file = pack_file.absolute()
    pack_file = install.safe_path(metrics._target(pack_file.parent), pack_file.name)
    pack = validate_pack(json.loads(pack_file.read_text(encoding="utf-8")), project)
    task_fingerprints = set()
    for task in pack["tasks"]:
        for field in ("prompt_file", "rubric_file"):
            path = install.safe_path(pack_file.parent, task[field])
            if path.stat().st_size > 1_000_000:
                raise ValueError("Task material exceeds 1 MB")
            task[field.replace("_file", "")] = path.read_text(encoding="utf-8")
        material = {k: task[k] for k in ("prompt", "rubric", "path", "stack", "operation", "risks", "capabilities")}
        material.update(risks=sorted(task["risks"]), capabilities=sorted(task["capabilities"]), path=task["path"].rstrip("/"))
        fingerprint = install.digest(json.dumps(material, sort_keys=True).encode())
        if fingerprint in task_fingerprints:
            raise ValueError("Duplicate task material cannot count as a distinct case; use repeats")
        task_fingerprints.add(fingerprint)
    files = snapshot_files(project, pack["revision"], git=git)
    selection, providers = router._selection_and_providers(project, ROOT)
    config = adaptive.load_config(project)
    records = metrics.read_records(project)
    units = []
    for repetition in range(1, pack["repeats"] + 1):
        for task in pack["tasks"]:
            # Rotate all arms together to reduce systematic order/cache effects.
            order = ARMS[(repetition - 1) % 3:] + ARMS[:(repetition - 1) % 3]
            for arm in order:
                route = dict(pack["fixed"])
                if arm == "kit-adaptive":
                    recommendation = adaptive.recommend_route(task["prompt"], selection, providers, config=config,
                        records=records, mode="adaptive", task_id=task["task_id"], stack=task["stack"],
                        operation=task["operation"], risks=tuple(task["risks"]), capabilities=task["capabilities"])
                    if recommendation["resolved"]:
                        route = {key: recommendation[key] for key in ("provider", "model", "effort")}
                unit_id = f"unit-{len(units) + 1:06d}"
                units.append({"unit_id": unit_id, "task_id": task["task_id"] + f":r{repetition}",
                              "case_id": task["task_id"], "arm": arm, "repetition": repetition,
                              "route": route})
    relative = "ai-kit/.metrics/benchmarks/" + pack["experiment"]
    install.safe_path(project, relative + "/plan.json")
    return {"project": project, "relative": relative, "pack": pack, "files": files, "units": units,
            "context_budget": config["context_bytes"][config["profile"]]}


def clean_environment(workspace: Path) -> dict[str, str]:
    # Do not inherit credentials, DB URLs, production service configuration or user home files.
    environment = {key: os.environ[key] for key in ("PATH", "SystemRoot", "WINDIR", "PATHEXT") if key in os.environ}
    temporary = install.safe_path(workspace, ".benchmark-tmp/probe").parent
    temporary.mkdir(exist_ok=True)
    # Git applies ceilings above cwd; naming cwd itself does not stop parent discovery.
    environment.update({"HOME": str(temporary), "USERPROFILE": str(temporary), "TMP": str(temporary),
                        "TEMP": str(temporary), "TMPDIR": str(temporary), "AIKIT_BENCHMARK": "1",
                        "GIT_CEILING_DIRECTORIES": str(workspace.parent)})
    return environment


def invoke(command: list[str], workspace: Path, seconds: int, *, request: dict | None = None) -> tuple[int | None, str]:
    try:
        completed = subprocess.run(command, cwd=workspace, env=clean_environment(workspace),
            input=json.dumps(request) if request is not None else None, capture_output=True, text=True,
            encoding="utf-8", timeout=seconds, shell=False)
        return completed.returncode, completed.stdout if request is not None else ""
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return None, ""


def run_unit(plan: dict, manifest: dict, run: Path, unit: dict, tasks: dict) -> dict:
    """Execute one unit or raise; callers record infrastructure failures per unit."""
    workspace = install.safe_path(run, unit["unit_id"] + "/workspace/probe").parent
    workspace.mkdir(parents=True)
    for name, data, file_mode in plan["files"]:
        destination = install.safe_path(workspace, name)
        install.atomic_write(destination, data)
        destination.chmod(file_mode)
    task = tasks[unit["case_id"]]
    pack = plan["pack"]
    context_report = {"selected": [], "total_bytes": 0}
    if unit["arm"] != "baseline":
        install_plan = install.build_plan(workspace, root=ROOT, agents=pack["kit_agents"],
                                          preset=pack["kit_preset"])
        if install_plan["conflicts"] or not install.apply_plan(install_plan):
            raise ValueError("Kit installation conflict inside benchmark workspace")
        context_report = context.select_context(workspace, path=task["path"],
                                                budget=plan["context_budget"])
        if task["stack"] != "unknown" and task["stack"] not in context_report["profiles"]:
            raise ValueError("Task stack is not evidenced by its module; confirm the test fixture")
    request = {"schema": 1, "protocol": "aikit-worker-v1", "task_id": unit["task_id"],
               "arm": unit["arm"], "revision": pack["revision"], "workspace": str(workspace),
               "prompt": task["prompt"], "rubric": task["rubric"], "requested": unit["route"],
               "context": context_report,
               "constraints": {"disposable_services_only": True, "no_commit_push": True,
                               "credentials_external": True}}
    start = time.monotonic()
    status, output = invoke(pack["worker"]["argv"], workspace, pack["timeout_seconds"], request=request)
    wall = time.monotonic() - start
    attempts, rework, escalations = [{"disposition": "inconclusive"}], None, None
    telemetry_valid = False
    if status == 0:
        try:
            response = json.loads(output)
            if (not isinstance(response, dict) or set(response) != {"schema", "attempts", "rework", "escalations"} or
                    type(response["schema"]) is not int or response["schema"] != 1):
                raise ValueError("Invalid worker response")
            attempts, rework, escalations = response["attempts"], response["rework"], response["escalations"]
            if isinstance(attempts, list) and len(attempts) == 1 and attempts[0].get("duration_seconds") is None:
                attempts[0]["duration_seconds"] = wall
            telemetry_valid = True
        except (ValueError, TypeError, AttributeError):
            attempts, rework, escalations = [{"disposition": "inconclusive"}], None, None
    checks = "not-run"
    if pack["checks"]:
        check_results = [invoke(cmd, workspace, pack["timeout_seconds"])[0] for cmd in pack["checks"]]
        checks = "passed" if all(code == 0 for code in check_results) else "failed"
    record = {"schema": 3, "task_id": unit["task_id"], "experiment": pack["experiment"],
              "arm": unit["arm"], "kit_version": manifest["kit_version"], "outcome": "incomplete",
              "checks": checks, "attempts": attempts, "rework": rework, "escalations": escalations,
              "metadata": {"case_id": unit["case_id"], "stack": task["stack"], "task_class": task["operation"],
                           "level": router.classify_task(task["prompt"], operation=task["operation"],
                                                        risks=tuple(task["risks"]))["level"],
                           "revision": pack["revision"], "repetition": unit["repetition"],
                           "review": "pending", "capabilities": task["capabilities"]}}
    try:
        record = metrics.validate_record(record)
    except (ValueError, TypeError):
        record.update(attempts=[{"disposition": "inconclusive"}], rework=None, escalations=None)
        record = metrics.validate_record(record)
        telemetry_valid = False
    matches = telemetry_valid and all(all(a.get(k) == unit["route"][k] for k in ("provider", "model", "effort"))
                                      for a in record["attempts"])
    return {"unit_id": unit["unit_id"], "record": record, "worker_exit_code": status,
            "worker_wall_seconds": wall, "telemetry_valid": telemetry_valid,
            "requested": unit["route"], "observed_matches_request": matches,
            "context_bytes": context_report["total_bytes"]}


def failure_result(manifest: dict, unit: dict, task: dict, message: str) -> dict:
    """Record an infrastructure failure without hiding it as an executed attempt."""
    return {"unit_id": unit["unit_id"],
            "record": {"schema": 3, "task_id": unit["task_id"], "experiment": manifest["experiment"],
                       "arm": unit["arm"], "kit_version": manifest["kit_version"], "outcome": "incomplete",
                       "checks": "not-run", "attempts": [{"disposition": "inconclusive"}],
                       "rework": None, "escalations": None,
                       "metadata": {"case_id": unit["case_id"], "stack": task["stack"],
                                    "task_class": task["operation"],
                                    "level": router.classify_task(task["prompt"], operation=task["operation"],
                                                                  risks=tuple(task["risks"]))["level"],
                                    "revision": manifest["revision"], "repetition": unit["repetition"],
                                    "review": "pending", "capabilities": task["capabilities"]}},
            "worker_exit_code": None, "worker_wall_seconds": None, "telemetry_valid": False,
            "requested": unit["route"], "observed_matches_request": False,
            "context_bytes": 0, "error": message}


def execute(plan: dict) -> Path:
    project, pack = plan["project"], plan["pack"]
    run = install.safe_path(project, plan["relative"] + "/plan.json").parent
    identity = install.digest(json.dumps({"experiment": pack["experiment"], "revision": pack["revision"],
                                          "pack": pack, "units": plan["units"]}, sort_keys=True).encode())
    manifest_path = install.safe_path(run, "plan.json")
    if run.exists():
        if not manifest_path.is_file():
            raise ValueError("Interrupted run directory without a manifest; preserve it and use a new experiment ID")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("identity_sha256") != identity:
            raise ValueError("Existing run has a different plan; preserve it and use a new experiment ID")
    else:
        run.parent.mkdir(parents=True, exist_ok=True)
        run.mkdir()  # Exclusive ownership: never remove a workspace.
        manifest = {"schema": 1, "experiment": pack["experiment"], "revision": pack["revision"],
                    "kit_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
                    "pack_sha256": install.digest(json.dumps(pack, sort_keys=True).encode()),
                    "identity_sha256": identity,
                    "units": plan["units"], "complete": False}
        install.atomic_write(manifest_path, json_bytes(manifest))
    tasks = {task["task_id"]: task for task in pack["tasks"]}
    finished = {path.parent.name for path in run.glob("unit-*/result.json")}
    for unit in plan["units"]:
        if unit["unit_id"] in finished:
            continue  # Resume: never re-run paid work or rebuild an existing workspace.
        try:
            result = run_unit(plan, manifest, run, unit, tasks)
        except (OSError, ValueError) as exc:
            result = failure_result(manifest, unit, tasks[unit["case_id"]], str(exc))
        install.atomic_write(install.safe_path(run, unit["unit_id"] + "/result.json"), json_bytes(result))
    manifest["complete"] = True
    install.atomic_write(manifest_path, json_bytes(manifest))
    write_report(run)
    return run


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")


def report(run: Path) -> dict:
    run = metrics._target(run)
    manifest = json.loads(install.safe_path(run, "plan.json").read_text(encoding="utf-8"))
    results = []
    for unit in manifest["units"]:
        if not re.fullmatch(r"unit-\d{6}", unit["unit_id"]):
            raise ValueError("Invalid run unit ID")
        path = install.safe_path(run, unit["unit_id"] + "/result.json")
        if path.exists():
            value = json.loads(path.read_text(encoding="utf-8"))
            record = metrics.validate_record(value["record"])
            if (value["unit_id"] != unit["unit_id"] or record["experiment"] != manifest["experiment"] or
                    record["task_id"] != unit["task_id"] or record["arm"] != unit["arm"] or
                    record.get("metadata", {}).get("revision") != manifest["revision"] or
                    record["metadata"]["case_id"] != unit["case_id"] or
                    record["metadata"]["repetition"] != unit["repetition"]):
                raise ValueError("Result does not match its planned identity/starting state")
            adaptive.validate_pin(unit["route"])
            value["observed_matches_request"] = all(all(a.get(k) == unit["route"][k] for k in ("provider", "model", "effort"))
                                                    for a in record["attempts"])
            results.append(value)
    records = [r["record"] for r in results]
    comparisons = [learning.compare(records, manifest["experiment"], candidate=arm) for arm in ARMS[1:]]
    invalid = not manifest["complete"] or len(results) != len(manifest["units"]) or any(
        not r["telemetry_valid"] or r["worker_exit_code"] != 0 or not r["observed_matches_request"] for r in results)
    if invalid:
        for comparison in comparisons:
            comparison["savings_percent"] = None
            comparison["unknown_reasons"].append("Incomplete run or unconfirmed actual execution")
    return {"schema": 1, "experiment": manifest["experiment"], "revision": manifest["revision"],
            "complete": manifest["complete"] and len(results) == len(manifest["units"]),
            "expected_units": len(manifest["units"]), "observed_units": len(results),
            "results": results, "summary": metrics.summarize(records), "stacks": learning.by_stack(records),
            "comparisons": comparisons,
            "note": "Worker-reported usage is evidence, not proof of client control. Semantic review is separate from checks."}


def write_report(run: Path) -> dict:
    value = report(run)
    lines = ["# Benchmark report", "", "Experiment: " + value["experiment"], "", "Revision: " + value["revision"], ""]
    for item in value["comparisons"]:
        lines.extend(["| Comparison | Paired tasks | Correct baseline/candidate | Savings (%) |", "| --- | --- | --- | --- |"])
        lines.append(f'| {item["candidate"]} | {item["paired_tasks"]} | {item["baseline_correct"]}/{item["candidate_correct"]} | {item["savings_percent"] or "unknown"} |')
        lines.extend(["", "Unknown reasons: " + ("; ".join(item["unknown_reasons"]) or "none"), ""])
    lines.extend([value["note"], "", "All attempt costs, including failures, review and recovery, must be included.", ""])
    install.atomic_write(install.safe_path(run, "results.json"), json_bytes(value))
    install.atomic_write(install.safe_path(run, "report.md"), "\n".join(lines).encode("utf-8"))
    return value


def review(run: Path, review_file: Path, *, apply: bool = False) -> dict:
    run = metrics._target(run)
    value = metrics._fields(json.loads(review_file.read_text(encoding="utf-8")), {"schema", "reviews"}, "reviews")
    if type(value.get("schema")) is not int or value["schema"] != 1 or not isinstance(value.get("reviews"), list) or not value["reviews"]:
        raise ValueError("Expected schema 1 with reviews")
    current_report = report(run)
    observed = {(r["record"]["arm"], r["record"]["task_id"]): r for r in current_report["results"]}
    changes, seen = [], set()
    for item in value["reviews"]:
        if not isinstance(item, dict) or set(item) != {"task_id", "arm", "review", "outcome"}:
            raise ValueError("Invalid review item")
        identity = (item["arm"], item["task_id"])
        if identity not in observed or identity in seen or item["review"] not in {"manual", "independent"}:
            raise ValueError("Unknown/duplicate review identity or reviewer type")
        seen.add(identity)
        result = copy.deepcopy(observed[identity])
        if item["outcome"] == "correct" and (result["worker_exit_code"] != 0 or not result["telemetry_valid"]):
            raise ValueError("Cannot accept a failed or malformed worker execution")
        record = result["record"]
        record["outcome"], record["metadata"]["review"] = item["outcome"], item["review"]
        metrics.validate_record(record)
        path = install.safe_path(run, result["unit_id"] + "/result.json")
        changes.append((path, path.read_bytes(), json_bytes(result)))
    if apply:
        lock = install.safe_path(run, "review.lock")
        descriptor = install.exclusive_lock(lock)
        try:
            os.close(descriptor)
            if any(path.read_bytes() != old for path, old, _ in changes):
                raise ValueError("Results changed during review")
            for path, old, new in changes:
                backup = install.safe_path(run, "reviews/" + install.digest(old) + ".json")
                if backup.exists() and backup.read_bytes() != old:
                    raise ValueError("Review backup conflict")
                if not backup.exists():
                    install.atomic_write(backup, old)
                install.atomic_write(path, new)
            write_report(run)
        finally:
            lock.unlink()
    return {"preview": not apply, "reviewed_units": len(changes)}


def export_records(run: Path, project: Path, *, apply: bool = False) -> dict:
    value = report(run)
    if not value["complete"] or any(r["record"]["metadata"]["review"] == "pending" for r in value["results"]):
        raise ValueError("Finish execution and semantic review before exporting")
    project = metrics._target(project)
    records = [r["record"] for r in value["results"]]

    def merged() -> tuple[list[dict], int]:
        current = metrics.read_records(project)
        existing = {(r["experiment"], r["arm"], r["task_id"]): r for r in current}
        new = []
        for record in records:
            key = (record["experiment"], record["arm"], record["task_id"])
            if key in existing and existing[key] != record:
                raise ValueError("Export conflicts with reviewed journal data; preserve it")
            if key not in existing:
                new.append(record)
        return [*current, *new], len(new)

    rows, count = merged()
    if apply and count:
        lock = install.safe_path(project, metrics.LOCK)
        lock.parent.mkdir(parents=True, exist_ok=True)
        descriptor = install.exclusive_lock(lock)
        try:
            os.close(descriptor)
            rows, count = merged()
            install.atomic_write(install.safe_path(project, metrics.JOURNAL),
                                 "".join(json.dumps(r, allow_nan=False) + "\n" for r in rows).encode())
        finally:
            lock.unlink()
    return {"preview": not apply, "new_records": count}


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="Preview or execute a reviewed worker in isolated snapshots")
    run_parser.add_argument("project", type=Path)
    run_parser.add_argument("--pack", type=Path, required=True)
    run_parser.add_argument("--apply", action="store_true")
    report_parser = sub.add_parser("report", help="Read run coverage, metrics and savings without writing")
    report_parser.add_argument("run", type=Path)
    review_parser = sub.add_parser("review", help="Preview/apply explicit semantic acceptance and refresh reports")
    review_parser.add_argument("run", type=Path)
    review_parser.add_argument("--from-json", type=Path, required=True)
    review_parser.add_argument("--apply", action="store_true")
    export_parser = sub.add_parser("export", help="Preview/export reviewed records to the private journal")
    export_parser.add_argument("run", type=Path)
    export_parser.add_argument("project", type=Path)
    export_parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(arguments)
    try:
        if args.command == "run":
            plan = prepare(args.project, args.pack)
            run_dir = plan["project"] / plan["relative"]
            finished = ({path.parent.name for path in run_dir.glob("unit-*/result.json")}
                        if run_dir.is_dir() else set())
            value = {"preview": not args.apply, "experiment": plan["pack"]["experiment"],
                     "revision": plan["pack"]["revision"], "units": plan["units"],
                     "tracked_files": len(plan["files"]), "run": str(run_dir),
                     "existing_run": run_dir.is_dir(),
                     "remaining_units": sum(1 for unit in plan["units"]
                                              if unit["unit_id"] not in finished)}
            if args.apply:
                execute(plan)
        elif args.command == "review":
            value = review(args.run, args.from_json, apply=args.apply)
        elif args.command == "export":
            value = export_records(args.run, args.project, apply=args.apply)
        else:
            value = report(args.run)
        print(json.dumps(value, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        print(f"Benchmark refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
