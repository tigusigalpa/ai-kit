"""Create private A/B task packs and report reviewed measurement-pair coverage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics


ARMS = ("baseline", "kit")


def identifier(value: object, label: str) -> str:
    return metrics._identifier(value, label)


def validate_pack(value: object) -> dict:
    if not isinstance(value, dict) or set(value) - {"schema", "experiment", "arms", "tasks"}:
        raise ValueError("Invalid task pack object or unknown fields")
    if type(value.get("schema")) is not int or value["schema"] != 1:
        raise ValueError("Expected task-pack schema 1")
    identifier(value.get("experiment"), "experiment")
    arms = value.get("arms")
    if not isinstance(arms, list) or tuple(arms) != ARMS:
        raise ValueError("Task pack arms must be exactly baseline, kit")
    tasks = value.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Task pack requires at least one task")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) != {"task_id"}:
            raise ValueError("Each task pack item must contain only task_id")
        task_id = identifier(task.get("task_id"), "task_id")
        if task_id in seen:
            raise ValueError("Task pack task_id values must be unique")
        seen.add(task_id)
    return json.loads(json.dumps(value))


def scaffold_plan(output: Path, experiment: str, tasks: list[str]) -> dict:
    experiment = identifier(experiment, "experiment")
    pack = validate_pack({"schema": 1, "experiment": experiment, "arms": list(ARMS),
                          "tasks": [{"task_id": identifier(task, "task_id")} for task in tasks]})
    output = output.absolute()
    if output.exists() and output.is_symlink():
        raise ValueError("Refusing a linked task-pack path")
    if not output.parent.is_dir():
        raise ValueError("Task-pack parent must already exist")
    old = output.read_bytes() if output.exists() else None
    data = (json.dumps(pack, indent=2) + "\n").encode("utf-8")
    if old is not None and old != data:
        raise ValueError("Task-pack path already has different content; preserve it or choose another path")
    return {"output": str(output), "old": old, "data": data, "changed": old != data, "pack": pack}


def apply_scaffold(plan: dict) -> bool:
    output = Path(plan["output"])
    actual = output.read_bytes() if output.exists() else None
    if actual != plan["old"]:
        raise ValueError("Task-pack path changed after preview")
    if plan["changed"]:
        metrics.install.atomic_write(output, plan["data"])
    return True


def coverage(project: Path, task_pack: Path) -> dict:
    pack = validate_pack(json.loads(task_pack.read_text(encoding="utf-8")))
    records = [record for record in metrics.read_records(project) if record["experiment"] == pack["experiment"]]
    expected = {task["task_id"] for task in pack["tasks"]}
    observed: dict[str, dict[str, dict]] = {task_id: {} for task_id in expected}
    unexpected = []
    for record in records:
        if record["task_id"] not in expected or record["arm"] not in ARMS:
            unexpected.append({"task_id": record["task_id"], "arm": record["arm"]})
            continue
        observed[record["task_id"]][record["arm"]] = record
    missing, completed = [], 0
    for task_id in sorted(expected):
        missing_arms = [arm for arm in ARMS if arm not in observed[task_id]]
        if missing_arms:
            missing.append({"task_id": task_id, "arms": missing_arms})
        else:
            completed += 1
    outcomes = {"correct": 0, "incorrect": 0, "incomplete": 0}
    for arms in observed.values():
        for record in arms.values():
            outcomes[record["outcome"]] += 1
    return {"experiment": pack["experiment"], "tasks": len(expected), "complete_pairs": completed,
            "pair_coverage": {"complete": completed, "total": len(expected)}, "missing": missing,
            "unexpected_records": unexpected, "reviewed_outcomes": outcomes,
            "note": "This checks paired-record coverage only. Compare matched acceptance rubrics before claiming a difference."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scaffold = sub.add_parser("scaffold", help="Preview or create an opaque private baseline/kit task pack")
    scaffold.add_argument("--output", type=Path, required=True)
    scaffold.add_argument("--experiment", required=True)
    scaffold.add_argument("--task", action="append", required=True)
    scaffold.add_argument("--apply", action="store_true")
    coverage_parser = sub.add_parser("coverage", help="Report baseline/kit measurement-pair coverage")
    coverage_parser.add_argument("project", type=Path)
    coverage_parser.add_argument("--tasks", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "coverage":
            print(json.dumps(coverage(args.project, args.tasks), indent=2))
            return 0
        plan = scaffold_plan(args.output, args.experiment, args.task)
        print(json.dumps({"output": plan["output"], "preview": not args.apply, "changed": plan["changed"],
                          "task_pack": plan["pack"]}, indent=2))
        if args.apply:
            apply_scaffold(plan)
        return 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Evaluation operation refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
