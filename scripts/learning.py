"""Measured comparisons and conservative routing proposals; never apply recommendations automatically."""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
import json
import math
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install
import metrics


def actual_cost(records: list[dict]) -> tuple[Decimal | None, str | None]:
    attempts = [attempt for record in records for attempt in record["attempts"]]
    if not attempts or any(a.get("cost") is None or a["cost"]["source"] == "estimate" for a in attempts):
        return None, None
    currencies = {a["cost"]["currency"] for a in attempts}
    if len(currencies) != 1:
        return None, None
    return sum((Decimal(a["cost"]["amount"]) for a in attempts), Decimal()), currencies.pop()


def model_key(record: dict) -> tuple | None:
    """Only homogeneous strategies can inform a single-model recommendation."""
    keys = {(a.get("provider"), a.get("model"), a.get("effort")) for a in record["attempts"]}
    if len(keys) != 1:
        return None
    key = keys.pop()
    return key if key[0] and key[1] else None


def compare(records: list[dict], experiment: str, baseline: str = "baseline",
            candidate: str = "kit-fixed") -> dict:
    """Compare complete matched schema-3 trials with reviewed correctness and real costs."""
    metrics._identifier(experiment, "experiment")
    metrics._identifier(baseline, "baseline arm")
    metrics._identifier(candidate, "candidate arm")
    if baseline == candidate:
        raise ValueError("Comparison arms must differ")
    arms: dict[str, dict[str, dict]] = {baseline: {}, candidate: {}}
    for value in records:
        record = metrics.validate_record(value)
        if record["experiment"] != experiment or record["arm"] not in arms:
            continue
        if record["task_id"] in arms[record["arm"]]:
            raise ValueError("Duplicate task identity in comparison")
        arms[record["arm"]][record["task_id"]] = record
    ids = set(arms[baseline]) | set(arms[candidate])
    paired = sorted(set(arms[baseline]) & set(arms[candidate]))
    reasons = []
    if not ids or len(paired) != len(ids):
        reasons.append("Missing matched tasks")
    base = [arms[baseline][task] for task in paired]
    kit = [arms[candidate][task] for task in paired]
    for left, right in zip(base, kit):
        lm, rm = left.get("metadata", {}), right.get("metadata", {})
        if (not lm.get("revision") or any(lm.get(k) != rm.get(k) for k in
                                         ("revision", "case_id", "stack", "task_class", "level", "repetition", "capabilities"))):
            reasons.append("Starting state or task stratum is unknown/different")
        if any(r.get("metadata", {}).get("review") not in {"manual", "independent"} or
               r["outcome"] == "incomplete" for r in (left, right)):
            reasons.append("Semantic review is incomplete")
        if left["outcome"] == "correct" and right["outcome"] != "correct":
            reasons.append("Candidate regresses a previously correct paired task")
        if candidate in {"kit", "kit-fixed"} and (model_key(left) is None or model_key(left) != model_key(right)):
            reasons.append("Fixed model/effort is unknown/different")
    left_cost, left_currency = actual_cost(base)
    right_cost, right_currency = actual_cost(kit)
    if left_cost is None or right_cost is None or left_currency != right_currency:
        reasons.append("Actual single-currency cost coverage is incomplete")
    if left_cost == 0:
        reasons.append("Baseline cost is zero")
    correct_left = sum(r["outcome"] == "correct" for r in base)
    correct_right = sum(r["outcome"] == "correct" for r in kit)
    if not correct_left or correct_right < correct_left:
        reasons.append("Candidate correctness does not meet the baseline")
    savings = (str((left_cost - right_cost) / left_cost * 100)
               if not reasons and left_cost is not None and right_cost is not None else None)
    return {"experiment": experiment, "baseline": baseline, "candidate": candidate,
            "paired_tasks": len(paired), "expected_tasks": len(ids),
            "baseline_correct": correct_left, "candidate_correct": correct_right,
            "baseline_cost": str(left_cost) if left_cost is not None else None,
            "candidate_cost": str(right_cost) if right_cost is not None else None,
            "currency": left_currency if left_currency == right_currency else None,
            "baseline_cost_per_correct": str(left_cost / correct_left) if left_cost is not None and correct_left else None,
            "candidate_cost_per_correct": str(right_cost / correct_right) if right_cost is not None and correct_right else None,
            "savings_percent": savings, "unknown_reasons": sorted(set(reasons)),
            "note": "Observed matched spend difference, not a causal or predictive guarantee. All retries count."}


def by_stack(records: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for value in records:
        record = metrics.validate_record(value)
        groups[record.get("metadata", {}).get("stack", "unknown")].append(record)
    return {"stacks": {stack: metrics.summarize(rows)["groups"] for stack, rows in sorted(groups.items())}}


def wilson_lower(correct: int, count: int) -> float:
    if not count:
        return 0.0
    z = 1.96
    proportion = correct / count
    return ((proportion + z * z / (2 * count) - z * math.sqrt(
        proportion * (1 - proportion) / count + z * z / (4 * count * count))) / (1 + z * z / count))


def candidates(records: list[dict], *, stack: str, task_class: str, level: int,
               capabilities: list[str], minimum: int = 20, quality_floor: float = 0.8) -> list[dict]:
    if not isinstance(stack, str) or stack not in metrics.STACKS:
        raise ValueError("Unknown measurement stack")
    metrics._identifier(task_class, "task_class")
    if type(level) is not int or not 0 <= level <= 6:
        raise ValueError("Level must be 0-6")
    if not isinstance(capabilities, list):
        raise ValueError("Capabilities must be a list of opaque labels")
    for capability in capabilities:
        metrics._identifier(capability, "capability")
    if type(minimum) is not int or minimum < 5:
        raise ValueError("Minimum sample must be at least five distinct cases")
    if type(quality_floor) not in {int, float} or not 0.5 <= quality_floor <= 1:
        raise ValueError("Quality floor must be 0.5-1")
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    identities = set()
    unattributed = 0
    for value in records:
        record = metrics.validate_record(value)
        identity = (record["experiment"], record["arm"], record["task_id"])
        if identity in identities:
            raise ValueError("Duplicate task identity in learning evidence")
        identities.add(identity)
        meta = record.get("metadata", {})
        # Baseline measures instructions, not an alternative model under the kit's conditions.
        if (record["arm"] == "baseline" or meta.get("stack") != stack or meta.get("task_class") != task_class or meta.get("level") != level or
                sorted(meta.get("capabilities", [])) != sorted(capabilities) or not meta.get("revision") or
                not meta.get("case_id")):
            continue
        key = model_key(record)
        if key is None:
            first = record["attempts"][0]
            if first.get("provider") and first.get("model"):
                key = (first["provider"], first["model"], first.get("effort"))
        if key is not None:
            grouped[key].append(record)
        else:
            # Unknown executed models cannot be dropped as though their failures/spend were free.
            unattributed += 1
    result = []
    for key, rows in sorted(grouped.items(), key=lambda item: repr(item[0])):
        # Repeated trials are correlated: count each immutable case only once for the confidence floor.
        cases: dict[tuple, list[dict]] = defaultdict(list)
        for row in rows:
            meta = row["metadata"]
            cases[(meta["revision"], meta["case_id"])].append(row)
        correct_cases = sum(all(r["outcome"] == "correct" for r in group) for group in cases.values())
        lower = wilson_lower(correct_cases, len(cases))
        total, currency = actual_cost(rows)
        correct = sum(r["outcome"] == "correct" for r in rows)
        duration = metrics.summarize(rows)["groups"]
        seconds = [g["duration_seconds"] for g in duration]
        sample_keys = sorted((r["experiment"], r["metadata"]["revision"], r["metadata"]["case_id"],
                              r["metadata"]["repetition"]) for r in rows)
        correct_samples = sorted((r["experiment"], r["metadata"]["revision"], r["metadata"]["case_id"], r["metadata"]["repetition"])
                                 for r in rows if r["outcome"] == "correct")
        mixed = sum(model_key(row) is None for row in rows)
        pending = sum(row["metadata"]["review"] == "pending" for row in rows)
        eligible = (len(cases) >= minimum and lower >= quality_floor and total is not None and correct > 0
                    and not mixed and not pending and not unattributed)
        result.append({"provider": key[0], "model": key[1], "effort": key[2], "trials": len(rows),
                       "distinct_cases": len(cases), "correct": correct, "success_rate": correct / len(rows),
                       "quality_lower_bound": lower, "eligible": eligible, "currency": currency,
                       "mixed_strategy_trials": mixed, "pending_reviews": pending,
                       "unattributed_trials": unattributed,
                       "cost_per_correct": str(total / correct) if total is not None and correct else None,
                       "seconds_per_trial": sum(seconds) / len(rows) if all(s is not None for s in seconds) else None,
                       "sample_keys": sample_keys, "correct_sample_keys": correct_samples})
    return result


def recommend(records: list[dict], incumbent: dict, *, stack: str, task_class: str, level: int,
              capabilities: list[str], minimum: int = 20, quality_floor: float = 0.8,
              profile: str = "balanced", allowed_providers: set[str] | None = None) -> dict | None:
    rows = candidates(records, stack=stack, task_class=task_class, level=level, capabilities=capabilities,
                      minimum=minimum, quality_floor=quality_floor)
    reference = next((r for r in rows if all(r[k] == incumbent.get(k) for k in ("provider", "model", "effort"))), None)
    if reference is None or not reference["eligible"]:
        return None
    choices = [r for r in rows if r["eligible"] and (allowed_providers is None or r["provider"] in allowed_providers) and
               r["currency"] == reference["currency"] and
               r["sample_keys"] == reference["sample_keys"] and r["success_rate"] >= reference["success_rate"] and
               r["quality_lower_bound"] >= reference["quality_lower_bound"] and
               set(reference["correct_sample_keys"]) <= set(r["correct_sample_keys"]) and
               Decimal(r["cost_per_correct"]) <= Decimal(reference["cost_per_correct"])]
    if profile == "balanced":
        choices = [r for r in choices if r["seconds_per_trial"] is not None and
                   reference["seconds_per_trial"] is not None and r["seconds_per_trial"] <= reference["seconds_per_trial"]]
    if profile == "quality":
        choices.sort(key=lambda r: (-r["quality_lower_bound"], Decimal(r["cost_per_correct"])))
    else:
        choices.sort(key=lambda r: (Decimal(r["cost_per_correct"]), -r["quality_lower_bound"]))
    return choices[0] if choices else None


def save_proposal(project: Path, proposal: dict, *, apply: bool = False) -> dict:
    """Freeze evidence and selection for a reviewed, explicitly restorable proposal."""
    project = metrics._target(project)
    selection_path = install.safe_path(project, "ai-kit/router/selection.json")
    selection = selection_path.read_text(encoding="utf-8")
    payload = {"schema": 1, "selection_before": selection, "proposal": proposal,
               "evidence_sha256": install.digest(json.dumps(metrics.read_records(project), sort_keys=True).encode())}
    data = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    identifier = install.digest(data)
    path = install.safe_path(project, "ai-kit/.metrics/proposals/" + identifier + ".json")
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("xb") as output:
                output.write(data)
        except FileExistsError:
            if path.read_bytes() != data:
                raise ValueError("Proposal history conflict")
    return {"preview": not apply, "proposal_id": identifier, "path": str(path), "proposal": proposal}


def restore_selection(project: Path, identifier: str, *, apply: bool = False) -> dict:
    if not isinstance(identifier, str) or not re.fullmatch(r"[0-9a-f]{64}", identifier):
        raise ValueError("Proposal ID must be a SHA-256 digest")
    project = metrics._target(project)
    data = install.safe_path(project, "ai-kit/.metrics/proposals/" + identifier + ".json").read_bytes()
    if install.digest(data) != identifier:
        raise ValueError("Proposal history was modified")
    payload = json.loads(data)
    import router
    restored = payload["selection_before"].encode("utf-8")
    router.validate_selection(json.loads(restored))
    path = install.safe_path(project, "ai-kit/router/selection.json")
    current = path.read_bytes()
    if apply and current != restored:
        lock = install.safe_path(project, metrics.LOCK)
        lock.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.close(descriptor)
            backup = install.safe_path(project, "ai-kit/.metrics/proposals/selection-" + install.digest(current) + ".json")
            if backup.exists() and backup.read_bytes() != current:
                raise ValueError("Rollback backup conflict")
            if not backup.exists():
                with backup.open("xb") as output:
                    output.write(current)
            if path.read_bytes() != current:
                raise ValueError("Selection changed during rollback")
            install.atomic_write(install.safe_path(project, "ai-kit/router/selection.json"), restored)
        finally:
            install.safe_path(project, metrics.LOCK).unlink()
    return {"preview": not apply, "changed": current != restored, "proposal_id": identifier}
