"""Exercise private task packs and measurement-pair coverage reports."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import evaluate
import metrics


def record(task_id, arm, outcome="correct"):
    return {"schema": 2, "task_id": task_id, "experiment": "trial", "arm": arm,
            "kit_version": "test", "outcome": outcome, "checks": "passed" if outcome == "correct" else "failed",
            "rework": 0, "escalations": 0,
            "attempts": [{"provider": "provider", "model": "model", "effort": None,
                          "disposition": "succeeded" if outcome == "correct" else "failed",
                          "duration_seconds": None, "input_tokens": None, "cached_input_tokens": None,
                          "output_tokens": None, "reasoning_tokens": None, "cost": None}]}


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-evaluate-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / "project"
        self.project.mkdir()
        self.pack_path = self.root / "tasks.json"

    def test_scaffold_is_preview_first_and_refuses_overwrite(self):
        plan = evaluate.scaffold_plan(self.pack_path, "trial", ["task-01", "task-02"])
        self.assertTrue(plan["changed"])
        self.assertFalse(self.pack_path.exists())
        self.assertTrue(evaluate.apply_scaffold(plan))
        self.assertTrue(self.pack_path.is_file())
        with self.assertRaises(ValueError):
            evaluate.scaffold_plan(self.pack_path, "other", ["task-01"])

    def test_coverage_reports_missing_baseline_kit_pairs_and_unexpected_records(self):
        plan = evaluate.scaffold_plan(self.pack_path, "trial", ["task-01", "task-02"])
        evaluate.apply_scaffold(plan)
        metrics.record_task(self.project, record("task-01", "baseline"), apply=True)
        metrics.record_task(self.project, record("task-01", "kit"), apply=True)
        metrics.record_task(self.project, record("task-02", "baseline", "incorrect"), apply=True)
        metrics.record_task(self.project, record("other", "kit"), apply=True)
        report = evaluate.coverage(self.project, self.pack_path)
        self.assertEqual(report["complete_pairs"], 1)
        self.assertEqual(report["missing"], [{"task_id": "task-02", "arms": ["kit"]}])
        self.assertEqual(report["unexpected_records"], [{"task_id": "other", "arm": "kit"}])
        self.assertEqual(report["reviewed_outcomes"], {"correct": 2, "incorrect": 1, "incomplete": 0})

    def test_validation_and_cli_reject_nonopaque_task_content(self):
        with self.assertRaises(ValueError):
            evaluate.validate_pack({"schema": 1, "experiment": "trial", "arms": ["baseline", "kit"],
                                    "tasks": [{"task_id": "please fix payment bug"}]})
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(evaluate.main(["scaffold", "--output", str(self.pack_path), "--experiment", "trial",
                                             "--task", "task one"]), 1)


if __name__ == "__main__":
    unittest.main()
