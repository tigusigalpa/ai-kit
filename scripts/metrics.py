"""Opt-in local task measurements. No prompts, credentials, API calls, or automatic pricing."""
from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import json
import math
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install

JOURNAL = "ai-kit/.metrics/tasks.jsonl"
LOCK = "ai-kit/.metrics/write.lock"
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,127}\Z")
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens")
ATTEMPT_DISPOSITIONS = ("succeeded", "failed", "inconclusive")
STACKS = ("LARAVEL", "FILAMENT", "GO", "MOODLE", "PYTHON", "unknown")


def _fields(value: object, allowed: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError(f"Invalid {label} object or unknown fields")
    return value


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError(f"Invalid {label}; use an opaque identifier, not task text")
    return value


def validate_record(value: object) -> dict:
    record = _fields(value, {"schema", "task_id", "experiment", "arm", "kit_version", "outcome",
                             "checks", "rework", "escalations", "attempts", "metadata"}, "task record")
    if type(record.get("schema")) is not int or record["schema"] not in {1, 2, 3}:
        raise ValueError("Expected measurement schema 1, 2 or 3")
    if record["schema"] < 3 and "metadata" in record:
        raise ValueError("Metadata requires schema 3")
    if record["schema"] == 3:
        metadata = _fields(record.get("metadata"), {"stack", "task_class", "level", "revision",
                                                   "repetition", "review", "capabilities", "case_id"}, "metadata")
        if set(metadata) != {"stack", "task_class", "level", "revision", "repetition", "review", "capabilities", "case_id"}:
            raise ValueError("Schema 3 requires complete metadata, with null for unknown revision/level")
        if not isinstance(metadata["stack"], str) or metadata["stack"] not in STACKS:
            raise ValueError("Unknown measurement stack")
        _identifier(metadata["task_class"], "task_class")
        _identifier(metadata["case_id"], "case_id")
        if metadata["level"] is not None and (type(metadata["level"]) is not int or not 0 <= metadata["level"] <= 6):
            raise ValueError("Metadata level must be 0-6 or null")
        if metadata["revision"] is not None and (not isinstance(metadata["revision"], str) or
                                                not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", metadata["revision"])):
            raise ValueError("Revision must be a full Git object ID or null")
        if type(metadata["repetition"]) is not int or metadata["repetition"] < 1:
            raise ValueError("Repetition must be a positive integer")
        if not isinstance(metadata["review"], str) or metadata["review"] not in {"manual", "independent", "pending"}:
            raise ValueError("Review must be manual, independent or pending")
        if metadata["review"] == "pending" and record.get("outcome") != "incomplete":
            raise ValueError("Pending semantic review requires an incomplete outcome")
        if not isinstance(metadata["capabilities"], list):
            raise ValueError("Capabilities must be a list")
        for capability in metadata["capabilities"]:
            _identifier(capability, "capability")
    for field in ("task_id", "experiment", "arm", "kit_version"):
        _identifier(record.get(field), field)
    if not isinstance(record.get("outcome"), str) or record["outcome"] not in {"correct", "incorrect", "incomplete"}:
        raise ValueError("Outcome must be correct, incorrect, or incomplete after review")
    if not isinstance(record.get("checks"), str) or record["checks"] not in {"passed", "failed", "not-run"}:
        raise ValueError("Checks must be passed, failed, or not-run")
    if record["outcome"] == "correct" and record["checks"] == "failed":
        raise ValueError("A correct result cannot have failed required checks")
    for field in ("rework", "escalations"):
        if record["schema"] == 3 and field in record and record[field] is None:
            continue
        if type(record.get(field)) is not int or record[field] < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    attempts = record.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        raise ValueError("Include all attempts, including failures and recovery")
    for attempt in attempts:
        allowed = {"provider", "model", "effort", "duration_seconds", "cost", *TOKEN_FIELDS}
        if record["schema"] >= 2:
            allowed.add("disposition")
        _fields(attempt, allowed,
                "attempt")
        for field in ("provider", "model", "effort"):
            if attempt.get(field) is not None:
                _identifier(attempt[field], field)
        duration = attempt.get("duration_seconds")
        if duration is not None and (type(duration) not in {int, float} or
                                     duration < 0 or duration > sys.float_info.max or
                                     not math.isfinite(duration)):
            raise ValueError("duration_seconds must be finite and nonnegative, or null")
        for field in TOKEN_FIELDS:
            number = attempt.get(field)
            if number is not None and (type(number) is not int or number < 0):
                raise ValueError(f"{field} must be a nonnegative integer or null")
        for subset, total in (("cached_input_tokens", "input_tokens"),
                              ("reasoning_tokens", "output_tokens")):
            if (attempt.get(subset) is not None and attempt.get(total) is not None and
                    attempt[subset] > attempt[total]):
                raise ValueError(f"{subset} cannot exceed {total}")
        cost = attempt.get("cost")
        if cost is not None:
            _fields(cost, {"amount", "currency", "source"}, "cost")
            amount = cost.get("amount")
            if not isinstance(amount, str) or not re.fullmatch(r"\d{1,16}(?:\.\d{1,12})?", amount):
                raise ValueError("Cost amount must be a nonnegative decimal string")
            try:
                Decimal(amount)
            except InvalidOperation as exc:
                raise ValueError("Invalid decimal amount") from exc
            if not isinstance(cost.get("currency"), str) or not re.fullmatch(r"[A-Z]{3}", cost["currency"]):
                raise ValueError("Cost currency must be a three-letter uppercase code")
            if not isinstance(cost.get("source"), str) or cost["source"] not in {"billing", "provider-usage", "estimate"}:
                raise ValueError("Cost source must be billing, provider-usage, or estimate")
        if record["schema"] >= 2 and attempt.get("disposition") not in ATTEMPT_DISPOSITIONS:
            raise ValueError("Schema 2 attempts need disposition: succeeded, failed, or inconclusive")
    # Normalize JSON values without carrying caller-owned mutable objects into a write plan.
    return json.loads(json.dumps(record, allow_nan=False))


def _target(project: Path) -> Path:
    project = project.absolute()
    if install.is_link(project):
        raise ValueError("Refusing a linked project root")
    project = project.resolve()
    if not project.is_dir():
        raise ValueError("Project must be an existing directory")
    return project


def read_records(project: Path) -> list[dict]:
    path = install.safe_path(_target(project), JOURNAL)
    if not path.exists():
        return []
    records, identities = [], set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = validate_record(json.loads(line))
            identity = (record["experiment"], record["arm"], record["task_id"])
            if identity in identities:
                raise ValueError("Duplicate task identity")
            identities.add(identity)
            records.append(record)
        except ValueError as exc:
            raise ValueError(f"Invalid journal line {number}: {exc}") from exc
    return records


def record_task(project: Path, record: dict, *, apply: bool = False) -> dict:
    project = _target(project)
    record = validate_record(record)
    path = install.safe_path(project, JOURNAL)
    lock = install.safe_path(project, LOCK)

    def check_duplicate(records: list[dict]) -> None:
        if any(all(existing[key] == record[key] for key in ("experiment", "arm", "task_id"))
               for existing in records):
            raise ValueError("Task already recorded for this experiment/arm; journal left unchanged")

    check_duplicate(read_records(project))
    if apply:
        lock.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive lock protects cooperating writers. Never remove another writer's lock.
        descriptor = os.open(install.safe_path(project, LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.close(descriptor)
            records = read_records(project)
            check_duplicate(records)
            data = "".join(json.dumps(item, ensure_ascii=True, allow_nan=False) + "\n"
                           for item in [*records, record]).encode("utf-8")
            install.atomic_write(install.safe_path(project, JOURNAL), data)
        finally:
            install.safe_path(project, LOCK).unlink()
    return {"preview": not apply, "journal": str(path), "task_id": record["task_id"],
            "attempts": len(record["attempts"])}


def summarize(records: list[dict]) -> dict:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        record = validate_record(record)
        groups[(record["experiment"], record["arm"])].append(record)
    results = []
    for (experiment, arm), tasks in sorted(groups.items()):
        attempts = [attempt for task in tasks for attempt in task["attempts"]]
        correct = sum(task["outcome"] == "correct" for task in tasks)
        costs: dict[str, Decimal] = defaultdict(Decimal)
        known_costs = 0
        estimated = 0
        for attempt in attempts:
            cost = attempt.get("cost")
            if cost is not None:
                costs[cost["currency"]] += Decimal(cost["amount"])
                known_costs += 1
                estimated += cost["source"] == "estimate"
        complete = known_costs == len(attempts) and len(costs) == 1 and not estimated
        total = next(iter(costs.values())) if complete else None
        durations = [attempt["duration_seconds"] for attempt in attempts
                     if attempt.get("duration_seconds") is not None]
        results.append({"experiment": experiment, "arm": arm, "tasks": len(tasks), "correct": correct,
                        "success_rate": correct / len(tasks), "attempts": len(attempts),
                        "rework": sum(task["rework"] for task in tasks) if all(task["rework"] is not None for task in tasks) else None,
                        "escalations": sum(task["escalations"] for task in tasks) if all(task["escalations"] is not None for task in tasks) else None,
                        "intervention_coverage": {field: {"known": sum(task[field] is not None for task in tasks),
                                                          "total": len(tasks)} for field in ("rework", "escalations")},
                        "checks_not_run": sum(task["checks"] == "not-run" for task in tasks),
                        "known_cost_by_currency": {key: str(value) for key, value in sorted(costs.items())},
                        "cost_coverage": {"known": known_costs, "total": len(attempts), "estimated": estimated},
                        "cost_per_correct_result": str(total / correct) if complete and correct else None,
                        "duration_seconds": sum(durations) if len(durations) == len(attempts) else None,
                        "duration_coverage": {"known": len(durations), "total": len(attempts)},
                        "tokens": {field: {"known_total": sum(a.get(field) or 0 for a in attempts),
                                           "known_attempts": sum(a.get(field) is not None for a in attempts),
                                           "total_attempts": len(attempts)} for field in TOKEN_FIELDS}})
    return {"groups": results,
            "note": "Descriptive totals only; include all failed/recovery attempts. Unknown values remain "
                    "unknown. Compare matched tasks and reviewed correctness before claiming savings."}


def analyze(records: list[dict]) -> dict:
    """Aggregate reviewed tasks per provider to inform routing without writing anything."""
    providers: dict[str, dict] = {}
    for record in records:
        record = validate_record(record)
        correct = record["outcome"] == "correct"
        for attempt in record["attempts"]:
            provider = attempt.get("provider")
            if provider is None:
                continue
            entry = providers.setdefault(provider, {"tasks": set(), "correct_tasks": set(),
                                                    "attempts": 0, "cost": defaultdict(Decimal),
                                                    "cost_attempts": 0, "models": set(), "efforts": set(),
                                                    "dispositions": defaultdict(int), "known_dispositions": 0,
                                                    "estimated": 0})
            entry["attempts"] += 1
            identity = (record["experiment"], record["arm"], record["task_id"])
            entry["tasks"].add(identity)
            if correct:
                entry["correct_tasks"].add(identity)
            if attempt.get("model") is not None:
                entry["models"].add(attempt["model"])
            if attempt.get("effort") is not None:
                entry["efforts"].add(attempt["effort"])
            cost = attempt.get("cost")
            if cost is not None:
                entry["cost"][cost["currency"]] += Decimal(cost["amount"])
                entry["cost_attempts"] += 1
                entry["estimated"] += cost["source"] == "estimate"
            disposition = attempt.get("disposition")
            if disposition is not None:
                entry["dispositions"][disposition] += 1
                entry["known_dispositions"] += 1
    results = []
    for name in sorted(providers):
        entry = providers[name]
        tasks = len(entry["tasks"])
        correct = len(entry["correct_tasks"])
        complete = (entry["cost_attempts"] == entry["attempts"] and len(entry["cost"]) == 1
                    and not entry["estimated"])
        total = next(iter(entry["cost"].values())) if complete else None
        decisive = entry["dispositions"]["succeeded"] + entry["dispositions"]["failed"]
        results.append({"provider": name, "attempts": entry["attempts"], "tasks": tasks,
                        "correct_tasks": correct, "success_rate": correct / tasks if tasks else None,
                        "known_cost_by_currency": {key: str(value) for key, value in sorted(entry["cost"].items())},
                        "cost_coverage": {"known": entry["cost_attempts"], "total": entry["attempts"],
                                          "estimated": entry["estimated"]},
                        "cost_per_correct": str(total / correct) if complete and correct else None,
                        "attempt_dispositions": {key: entry["dispositions"][key] for key in ATTEMPT_DISPOSITIONS},
                        "attempt_disposition_coverage": {"known": entry["known_dispositions"],
                                                         "total": entry["attempts"]},
                        "attempt_success_rate": (entry["dispositions"]["succeeded"] / decisive
                                                 if decisive else None),
                        "models": sorted(entry["models"]), "efforts": sorted(entry["efforts"])})
    return {"providers": results,
            "note": "Descriptive per-provider totals from reviewed records; a task identity is experiment, arm, "
                    "and task_id, and each provider used in its attempts receives that attribution. Schema 2 "
                    "attempt dispositions describe execution, not causation. Compare matched tasks and reviewed "
                    "correctness before changing selection.json."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    record_parser = sub.add_parser("record", help="Preview or record one reviewed task and all its attempts")
    record_parser.add_argument("project", type=Path)
    record_parser.add_argument("--from-json", type=Path, required=True)
    record_parser.add_argument("--apply", action="store_true")
    summary_parser = sub.add_parser("summary", help="Summarize the local journal without writing")
    summary_parser.add_argument("project", type=Path)
    analyze_parser = sub.add_parser("analyze", help="Aggregate per provider to inform routing, without writing")
    analyze_parser.add_argument("project", type=Path)
    compare_parser = sub.add_parser("compare", help="Compare matched reviewed trials with actual costs")
    compare_parser.add_argument("project", type=Path)
    compare_parser.add_argument("--experiment", required=True)
    compare_parser.add_argument("--baseline", default="baseline")
    compare_parser.add_argument("--candidate", default="kit-fixed")
    stacks_parser = sub.add_parser("stacks", help="Summarize by declared technology stack")
    stacks_parser.add_argument("project", type=Path)
    propose_parser = sub.add_parser("propose", help="Preview or save evidence; never apply routing changes")
    propose_parser.add_argument("project", type=Path)
    propose_parser.add_argument("--stack", choices=STACKS, required=True)
    propose_parser.add_argument("--task-class", required=True)
    propose_parser.add_argument("--level", type=int, required=True)
    propose_parser.add_argument("--capability", action="append", default=[])
    propose_parser.add_argument("--minimum", type=int, default=20)
    propose_parser.add_argument("--quality-floor", type=float, default=0.8)
    propose_parser.add_argument("--apply", action="store_true")
    restore_parser = sub.add_parser("restore", help="Explicitly restore a proposal's prior selection with backup")
    restore_parser.add_argument("project", type=Path)
    restore_parser.add_argument("--proposal", required=True)
    restore_parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            record = json.loads(args.from_json.read_text(encoding="utf-8"))
            result = record_task(args.project, record, apply=args.apply)
        elif args.command == "analyze":
            result = analyze(read_records(args.project))
        elif args.command in {"compare", "stacks", "propose", "restore"}:
            import learning
            if args.command == "compare":
                result = learning.compare(read_records(args.project), args.experiment, args.baseline, args.candidate)
            elif args.command == "stacks":
                result = learning.by_stack(read_records(args.project))
            elif args.command == "restore":
                result = learning.restore_selection(args.project, args.proposal, apply=args.apply)
            else:
                proposal = {"stack": args.stack, "task_class": args.task_class, "level": args.level,
                            "capabilities": args.capability, "minimum": args.minimum,
                            "quality_floor": args.quality_floor,
                            "candidates": learning.candidates(read_records(args.project), stack=args.stack,
                                task_class=args.task_class, level=args.level, capabilities=args.capability,
                                minimum=args.minimum, quality_floor=args.quality_floor)}
                result = learning.save_proposal(args.project, proposal, apply=args.apply)
        else:
            result = summarize(read_records(args.project))
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError) as exc:
        print(f"Measurement refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
