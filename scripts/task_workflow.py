"""Opt-in local task definitions, explicit states and source-bound check receipts."""
from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
if __package__:
    from . import install, task_snapshot as sources
else:
    import install
    import task_snapshot as sources

DIRECTORY = "ai-kit/.tasks"
LOCK = DIRECTORY + "/write.lock"
ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
STATES = ("planned", "implementing", "checking", "reviewing", "awaiting_approval", "accepted", "failed", "cancelled")
TRANSITIONS = {"planned": {"implementing", "cancelled"},
               "implementing": {"checking", "failed", "cancelled"},
               "checking": {"implementing", "reviewing", "failed", "cancelled"},
               "reviewing": {"implementing", "awaiting_approval", "failed", "cancelled"},
               "awaiting_approval": {"implementing", "failed", "cancelled"},
               "accepted": {"implementing"}, "failed": {"implementing", "cancelled"}, "cancelled": set()}
MAX_STATE = 4 * 1024 * 1024
MAX_EVENTS = 1000


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def identifier(value: object) -> str:
    if (not isinstance(value, str) or not ID.fullmatch(value) or
            re.fullmatch(r"con|prn|aux|nul|com[0-9]|lpt[0-9]", value)):
        raise ValueError("Use an opaque lowercase task/check/criterion ID of at most 64 characters")
    return value


def load_json(data: bytes) -> object:
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("Duplicate JSON key")
            value[key] = item
        return value
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))


def read(path: Path, limit: int = MAX_STATE) -> bytes:
    if any(install.is_link(p) for p in (path, *path.parents)):
        raise ValueError("Linked paths are unsupported")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("Expected a regular file")
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("File exceeds the byte limit")
    return data


def project_root(project: Path) -> Path:
    project = project.absolute()
    if not project.is_dir() or any(install.is_link(p) for p in (project, *project.parents)):
        raise ValueError("Project must be an existing, unlinked directory")
    project = project.resolve()
    settings = load_json(read(install.safe_path(project, "ai-kit/settings.json")))
    if not isinstance(settings, dict) or settings.get("task_workflow") is not True:
        raise ValueError("Install explicitly with --with-task-workflow first")
    return project


def definition(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {"schema", "id", "title", "description", "acceptance", "checks"}:
        raise ValueError("Task requires schema, id, title, description, acceptance and checks")
    if type(value["schema"]) is not int or value["schema"] != 1:
        raise ValueError("Unsupported task schema")
    identifier(value["id"])
    for field, limit in (("title", 200), ("description", 16000)):
        if not isinstance(value[field], str) or not value[field].strip() or len(value[field]) > limit:
            raise ValueError("Invalid task " + field)
    criteria = value["acceptance"]
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= 50:
        raise ValueError("Declare 1-50 acceptance criteria before execution")
    seen = set()
    for item in criteria:
        if (not isinstance(item, dict) or set(item) != {"id", "description"} or
                identifier(item["id"]) in seen or not isinstance(item["description"], str) or
                not item["description"].strip() or len(item["description"]) > 2000):
            raise ValueError("Invalid or duplicate acceptance criterion")
        seen.add(item["id"])
    checks = value["checks"]
    if not isinstance(checks, list) or not 1 <= len(checks) <= 20:
        raise ValueError("Declare 1-20 required checks")
    seen = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"id", "argv", "cwd", "timeout_seconds"}:
            raise ValueError("Each check requires id, argv, cwd and timeout_seconds")
        if identifier(check["id"]) in seen:
            raise ValueError("Duplicate check ID")
        seen.add(check["id"])
        argv = check["argv"]
        if (not isinstance(argv, list) or not 1 <= len(argv) <= 64 or
                any(not isinstance(arg, str) or not arg or len(arg) > 8000 or
                    any(ord(c) < 32 for c in arg) for arg in argv)):
            raise ValueError("Check argv must be a bounded array of nonempty strings; no shell string")
        if not isinstance(check["cwd"], str):
            raise ValueError("Check cwd must be a project-relative directory")
        if check["cwd"] != ".":
            sources.source_path(check["cwd"])
        if type(check["timeout_seconds"]) is not int or not 1 <= check["timeout_seconds"] <= 3600:
            raise ValueError("Check timeout must be 1-3600 seconds")
    return value


def state_path(project: Path, task_id: str) -> Path:
    return install.safe_path(project, DIRECTORY + "/" + identifier(task_id) + ".json")


def validate_state(value: object, task_id: str) -> dict:
    fields = {"schema", "definition", "revision", "cycle", "state", "events", "receipts", "approvals"}
    if (not isinstance(value, dict) or set(value) != fields or type(value["schema"]) is not int or
            value["schema"] != 1 or definition(value["definition"])["id"] != task_id or
            not isinstance(value["state"], str) or value["state"] not in STATES or
            type(value["revision"]) is not int or value["revision"] < 1 or
            type(value["cycle"]) is not int or value["cycle"] < 0):
        raise ValueError("Invalid task state; preserve it for inspection")
    for key in ("events", "receipts", "approvals"):
        if not isinstance(value[key], list) or len(value[key]) > MAX_EVENTS:
            raise ValueError("Invalid or exhausted task history")
    for receipt in value["receipts"]:
        fields = {"id", "check_id", "revision", "cycle", "fingerprint", "started", "finished", "outcome",
                  "returncode", "duration_seconds", "output_sha256", "output_bytes", "argv", "cwd"}
        if (not isinstance(receipt, dict) or set(receipt) != fields or
                not isinstance(receipt["fingerprint"], str) or not HASH.fullmatch(receipt["fingerprint"]) or
                not isinstance(receipt["outcome"], str) or
                receipt["outcome"] not in {"running", "passed", "failed", "timeout", "interrupted", "source_changed"} or
                type(receipt["revision"]) is not int or not 1 <= receipt["revision"] <= value["revision"] or
                type(receipt["cycle"]) is not int or receipt["cycle"] < 1 or
                not isinstance(receipt["check_id"], str) or not ID.fullmatch(receipt["check_id"]) or
                (receipt["returncode"] is not None and type(receipt["returncode"]) is not int) or
                (receipt["outcome"] == "passed" and receipt["returncode"] != 0)):
            raise ValueError("Invalid check receipt")
    for event in value["events"]:
        if not isinstance(event, dict) or set(event) != {"at", "kind", "state", "revision", "cycle"}:
            raise ValueError("Invalid task event")
    for approval in value["approvals"]:
        validate_approval(approval)
        if approval["task_id"] != task_id:
            raise ValueError("Approval belongs to another task")
    return value


def load_state(project: Path, task_id: str) -> dict:
    return validate_state(load_json(read(state_path(project, task_id))), task_id)


def write(project: Path, value: dict, *, exclusive: bool = False) -> None:
    validate_state(value, value["definition"]["id"])
    data = sources.canonical(value) + b"\n"
    if len(data) > MAX_STATE:
        raise ValueError("Task history is full; preserve it and create a new task")
    destination = state_path(project, value["definition"]["id"])
    destination.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    state_path(project, value["definition"]["id"])
    temporary = destination.with_name(destination.name + "." + uuid.uuid4().hex + ".tmp")
    created = False
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            if os.name == "nt":
                # Windows rename is atomic and refuses an existing destination; it needs no hard-link privilege.
                os.rename(temporary, destination)
            else:
                os.link(temporary, destination)
        else:
            os.replace(temporary, destination)
    finally:
        if created and temporary.exists():
            temporary.unlink()


@contextmanager
def locked(project: Path):
    path = install.safe_path(project, LOCK)
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    install.safe_path(project, LOCK)
    token = sources.canonical({"pid": os.getpid(), "token": uuid.uuid4().hex})
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(token)
        yield
    finally:
        if path.exists() and read(path) == token:
            path.unlink()


def event(value: dict, kind: str) -> None:
    if len(value["events"]) >= MAX_EVENTS:
        raise ValueError("Task history is full; create another task")
    value["events"].append({"at": now(), "kind": kind, "state": value["state"],
                            "revision": value["revision"], "cycle": value["cycle"]})


def fingerprint(value: dict, source: dict) -> str:
    return hashlib.sha256(sources.canonical({"definition": value["definition"], "revision": value["revision"],
                                            "cycle": value["cycle"], "source": source["digest"]})).hexdigest()


def current_checks(value: dict, version: str) -> dict:
    latest = {}
    for receipt in value["receipts"]:
        if receipt["revision"] == value["revision"] and receipt["cycle"] == value["cycle"]:
            latest[receipt["check_id"]] = receipt
    return {check["id"]: bool(latest.get(check["id"], {}).get("outcome") == "passed" and
                             latest[check["id"]]["fingerprint"] == version)
            for check in value["definition"]["checks"]}


def report(value: dict, source: dict) -> dict:
    version = fingerprint(value, source)
    checks = current_checks(value, version)
    accepted = bool(value["state"] == "accepted" and value["approvals"] and
                    value["approvals"][-1]["fingerprint"] == version and all(checks.values()))
    return {"task_id": value["definition"]["id"], "state": value["state"],
            "effective_state": "stale" if value["state"] == "accepted" and not accepted else value["state"],
            "revision": value["revision"], "cycle": value["cycle"], "fingerprint": version,
            "source": source, "checks": checks, "accepted_current": accepted,
            "definition": value["definition"], "receipts": value["receipts"], "approvals": value["approvals"]}


def create(project: Path, spec: Path, *, apply: bool = False, revise: bool = False) -> dict:
    project = project_root(project)
    proposed = definition(load_json(read(spec.absolute(), 100000)))
    with locked(project) if apply else nullcontext():
        path = state_path(project, proposed["id"])
        if path.exists():
            value = load_state(project, proposed["id"])
            if value["definition"] == proposed:
                return {"preview": not apply, "unchanged": True, "task_id": proposed["id"], "state": value["state"]}
            if not revise:
                raise ValueError("Task ID already exists; use revise explicitly")
            if value["state"] == "cancelled":
                raise ValueError("Cancelled tasks are terminal; create a new task ID")
            value.update(definition=proposed, revision=value["revision"] + 1, cycle=0, state="planned")
            event(value, "revised")
        else:
            if revise:
                raise ValueError("Cannot revise a task that does not exist")
            value = {"schema": 1, "definition": proposed, "revision": 1, "cycle": 0, "state": "planned",
                     "events": [], "receipts": [], "approvals": []}
            event(value, "created")
        if apply:
            write(project, value, exclusive=not path.exists())
    return {"preview": not apply, "task_id": proposed["id"], "state": value["state"], "revision": value["revision"]}


def status(project: Path, task_id: str) -> dict:
    project = project_root(project)
    value = load_state(project, task_id)
    return report(value, sources.snapshot(project))


def transition(project: Path, task_id: str, target: str, *, apply: bool = False) -> dict:
    project = project_root(project)
    with locked(project) if apply else nullcontext():
        value = load_state(project, task_id)
        if target not in TRANSITIONS[value["state"]]:
            raise ValueError("Unsupported task transition; acceptance uses the accept command")
        if target in {"reviewing", "awaiting_approval"}:
            version = fingerprint(value, sources.snapshot(project))
            if not all(current_checks(value, version).values()):
                raise ValueError("All required checks must pass against the current code and task revision")
        value["state"] = target
        if target == "implementing":
            value["cycle"] += 1
            for receipt in value["receipts"]:
                if receipt["outcome"] == "running":
                    receipt.update(outcome="interrupted", finished=now())
        event(value, "transition")
        if apply:
            write(project, value)
    return {"preview": not apply, "task_id": task_id, "state": target, "cycle": value["cycle"]}


def stop(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            pass
        if process.poll() is None:
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=10)


def execute(argv: list[str], cwd: Path, timeout: int) -> dict:
    """Bound duration; discard child output rather than persist arbitrary secrets in task state."""
    started = time.monotonic()
    # A pipe is drained continuously and hashed without retaining child output in memory/on disk.
    import threading
    digest = hashlib.sha256()
    count = [0]
    errors = []
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    process = subprocess.Popen(argv, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, **options)
    def drain():
        try:
            with process.stdout:
                while data := process.stdout.read(65536):
                    digest.update(data)
                    count[0] += len(data)
        except OSError:
            errors.append("Output could not be fully read")
    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    outcome = "failed"
    try:
        process.wait(timeout=timeout)
        outcome = "passed" if process.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        outcome = "timeout"
        stop(process)
    except BaseException:
        stop(process)
        raise
    finally:
        reader.join(timeout=10)
    if reader.is_alive():
        raise ValueError("Check output remains open; inspect child processes before continuing")
    if errors:
        raise ValueError(errors[0])
    return {"outcome": outcome, "returncode": process.returncode,
            "duration_seconds": round(time.monotonic() - started, 6),
            "output_sha256": digest.hexdigest(), "output_bytes": count[0]}


def check(project: Path, task_id: str, check_id: str, *, apply: bool = False) -> dict:
    project = project_root(project)
    with locked(project) if apply else nullcontext():
        value = load_state(project, task_id)
        if value["state"] not in {"implementing", "checking"}:
            raise ValueError("Enter implementing/checking before running a check")
        spec = next((c for c in value["definition"]["checks"] if c["id"] == check_id), None)
        if spec is None:
            raise ValueError("Unknown check ID")
        cwd = project if spec["cwd"] == "." else install.safe_path(project, spec["cwd"])
        if not cwd.is_dir():
            raise ValueError("Check working directory must exist inside the project")
        source = sources.snapshot(project)
        version = fingerprint(value, source)
        if not apply:
            return {"preview": True, "task_id": task_id, "check": spec, "fingerprint": version}
        if (len(value["receipts"]) >= MAX_EVENTS or len(value["events"]) > MAX_EVENTS - 2 or
                len(sources.canonical(value)) > MAX_STATE - 8192):
            raise ValueError("Task history has insufficient room for another check receipt")
        receipt = {"id": uuid.uuid4().hex, "check_id": check_id, "revision": value["revision"],
                   "cycle": value["cycle"], "fingerprint": version, "started": now(), "finished": None,
                   "outcome": "running", "returncode": None, "duration_seconds": None,
                   "output_sha256": None, "output_bytes": None, "argv": spec["argv"], "cwd": spec["cwd"]}
        value["state"] = "checking"
        value["receipts"].append(receipt)
        event(value, "check_started")
        write(project, value)
        pending_bytes = read(state_path(project, task_id))
        try:
            result = execute(spec["argv"], cwd, spec["timeout_seconds"])
            if read(state_path(project, task_id)) != pending_bytes:
                raise ValueError("Check changed its task state; preserve the altered file for inspection")
            receipt.update(result)
            if fingerprint(value, sources.snapshot(project)) != version:
                receipt["outcome"] = "source_changed"
        except BaseException:
            if read(state_path(project, task_id)) == pending_bytes:
                receipt["outcome"] = "interrupted"
                value["state"] = "failed"
                receipt["finished"] = now()
                event(value, "check_interrupted")
                write(project, value)
            raise
        receipt["finished"] = now()
        if receipt["outcome"] != "passed":
            value["state"] = "failed"
        event(value, "check_finished")
        write(project, value)
        return {"preview": False, "task_id": task_id, "state": value["state"], "receipt": receipt}


def validate_approval(value: object) -> dict:
    if (not isinstance(value, dict) or set(value) != {"schema", "task_id", "fingerprint", "reviewer", "criteria"} or
            type(value["schema"]) is not int or value["schema"] != 1):
        raise ValueError("Approval requires schema, task_id, fingerprint, reviewer and criteria")
    identifier(value["task_id"])
    if not isinstance(value["fingerprint"], str) or not HASH.fullmatch(value["fingerprint"]):
        raise ValueError("Approval must name the exact fingerprint from task status")
    if not isinstance(value["reviewer"], str) or not value["reviewer"].strip() or len(value["reviewer"]) > 200:
        raise ValueError("Name the reviewer; this is a local assertion, not authenticated identity")
    if not isinstance(value["criteria"], list) or not 1 <= len(value["criteria"]) <= 50:
        raise ValueError("Review each acceptance criterion")
    seen = set()
    for criterion in value["criteria"]:
        if (not isinstance(criterion, dict) or set(criterion) != {"id", "passed", "evidence"} or
                identifier(criterion["id"]) in seen or criterion["passed"] is not True or
                not isinstance(criterion["evidence"], str) or not criterion["evidence"].strip() or
                len(criterion["evidence"]) > 4000):
            raise ValueError("Acceptance requires distinct passed criteria and explicit evidence")
        seen.add(criterion["id"])
    return value


def accept(project: Path, task_id: str, approval_path: Path, *, apply: bool = False) -> dict:
    project = project_root(project)
    approval = validate_approval(load_json(read(approval_path.absolute(), 256000)))
    with locked(project) if apply else nullcontext():
        value = load_state(project, task_id)
        version = fingerprint(value, sources.snapshot(project))
        if (value["state"] != "awaiting_approval" or approval["task_id"] != task_id or
                approval["fingerprint"] != version or not all(current_checks(value, version).values()) or
                {c["id"] for c in approval["criteria"]} != {c["id"] for c in value["definition"]["acceptance"]}):
            raise ValueError("Acceptance needs current checks, exact task/fingerprint and all declared criteria")
        value["state"] = "accepted"
        value["approvals"].append(approval)
        event(value, "accepted")
        if apply:
            write(project, value)
    return {"preview": not apply, "task_id": task_id, "state": "accepted", "fingerprint": version}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("create", "revise", "status", "transition", "check", "accept"):
        child = commands.add_parser(name)
        child.add_argument("project", type=Path)
        if name in {"create", "revise", "accept"}:
            child.add_argument("--from-json", type=Path, required=True)
        if name not in {"create", "revise"}:
            child.add_argument("--task-id", required=True)
        if name == "transition":
            child.add_argument("--to", choices=STATES, required=True)
        if name == "check":
            child.add_argument("--check-id", required=True)
        if name != "status":
            child.add_argument("--apply", action="store_true", help="Write state; check also runs the declared command")
    args = parser.parse_args(argv)
    try:
        if args.command in {"create", "revise"}:
            result = create(args.project, args.from_json, apply=args.apply, revise=args.command == "revise")
        elif args.command == "status":
            result = status(args.project, args.task_id)
        elif args.command == "transition":
            result = transition(args.project, args.task_id, args.to, apply=args.apply)
        elif args.command == "check":
            result = check(args.project, args.task_id, args.check_id, apply=args.apply)
        else:
            result = accept(args.project, args.task_id, args.from_json, apply=args.apply)
        print(json.dumps(result, indent=2))
        return 1 if result.get("receipt", {}).get("outcome") not in {None, "passed"} else 0
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError) as error:
        print("Task workflow refused: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
