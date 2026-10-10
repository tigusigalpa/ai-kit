"""Local measurement accounting, preservation, validation, and path guards."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import metrics


def task(task_id="pair-01", **overrides):
    value = {"schema": 1, "task_id": task_id, "experiment": "trial", "arm": "kit",
             "kit_version": "test-fixture", "outcome": "correct", "checks": "passed",
             "rework": 0, "escalations": 0,
             "attempts": [{"provider": "test-provider", "model": "test-model", "effort": "low",
                           "duration_seconds": 10, "input_tokens": 100, "cached_input_tokens": 20,
                           "output_tokens": 40, "reasoning_tokens": 10,
                           "cost": {"amount": "0.10", "currency": "USD", "source": "provider-usage"}}]}
    value.update(overrides)
    return value


class AccountingTests(unittest.TestCase):
    def test_failed_and_recovery_costs_are_included(self):
        successful = task(rework=1, escalations=1)
        successful["attempts"].append(copy.deepcopy(successful["attempts"][0]))
        failed = task("pair-02", outcome="incorrect", checks="failed")
        group = metrics.summarize([successful, failed])["groups"][0]
        self.assertEqual(group["correct"], 1)
        self.assertEqual(group["attempts"], 3)
        self.assertEqual(group["cost_per_correct_result"], "0.30")
        self.assertEqual(group["duration_seconds"], 30)
        self.assertEqual(group["tokens"]["input_tokens"]["known_total"], 300)
        self.assertEqual((group["rework"], group["escalations"]), (1, 1))

    def test_unknown_cost_time_and_tokens_are_not_zero(self):
        value = task()
        value["attempts"].append({})
        group = metrics.summarize([value])["groups"][0]
        self.assertIsNone(group["cost_per_correct_result"])
        self.assertIsNone(group["duration_seconds"])
        self.assertEqual(group["cost_coverage"], {"known": 1, "total": 2, "estimated": 0})
        self.assertEqual(group["tokens"]["input_tokens"]["known_attempts"], 1)

    def test_currencies_and_estimates_are_explicit(self):
        value = task()
        other = copy.deepcopy(value["attempts"][0])
        other["cost"] = {"amount": "0.20", "currency": "EUR", "source": "estimate"}
        value["attempts"].append(other)
        group = metrics.summarize([value])["groups"][0]
        self.assertIsNone(group["cost_per_correct_result"])
        self.assertEqual(group["known_cost_by_currency"], {"EUR": "0.20", "USD": "0.10"})
        self.assertEqual(group["cost_coverage"]["estimated"], 1)

    def test_no_correct_result_has_no_cost_per_correct_result(self):
        group = metrics.summarize([task(outcome="incomplete", checks="not-run")])["groups"][0]
        self.assertIsNone(group["cost_per_correct_result"])
        self.assertEqual(group["checks_not_run"], 1)

    def test_experiment_arms_are_separate(self):
        results = metrics.summarize([task(), task(arm="baseline"), task(experiment="other")])["groups"]
        self.assertEqual(len(results), 3)

    def test_analyze_aggregates_per_provider(self):
        openai = task()
        openai["attempts"][0].update({"provider": "openai", "model": "gpt-6.1-sol"})
        anthropic = task("pair-02", outcome="incorrect", checks="failed")
        anthropic["attempts"][0].update({"provider": "anthropic", "model": "claude-opus-5-5"})
        report = metrics.analyze([openai, anthropic])
        by_name = {item["provider"]: item for item in report["providers"]}
        self.assertEqual(set(by_name), {"openai", "anthropic"})
        self.assertEqual(by_name["openai"]["correct_tasks"], 1)
        self.assertEqual(by_name["openai"]["success_rate"], 1.0)
        self.assertEqual(by_name["openai"]["cost_per_correct"], "0.10")
        self.assertEqual(by_name["anthropic"]["correct_tasks"], 0)
        self.assertEqual(by_name["anthropic"]["success_rate"], 0.0)
        self.assertIsNone(by_name["anthropic"]["cost_per_correct"])

    def test_record_validation_refuses_bad_data_and_task_text(self):
        invalid = [task(schema=True), task(task_id="please fix this bug"), task(prompt="secret"),
                   task(outcome=[]), task(checks=[]), task(rework=True), task(escalations=-1),
                   task(outcome="correct", checks="failed"), task(attempts=[]), task(attempts=[3])]
        for field, value in (("duration_seconds", float("nan")), ("duration_seconds", True),
                             ("duration_seconds", 10 ** 400),
                             ("input_tokens", -1), ("input_tokens", True),
                             ("cached_input_tokens", 101), ("reasoning_tokens", 41),
                             ("model", "model with task text"), ("prompt", "secret")):
            record = task()
            record["attempts"][0][field] = value
            invalid.append(record)
        for cost in ({"amount": "-1", "currency": "USD", "source": "billing"},
                     {"amount": "NaN", "currency": "USD", "source": "billing"},
                     {"amount": 0.1, "currency": "USD", "source": "billing"},
                     {"amount": "1", "currency": "usd", "source": "billing"},
                     {"amount": "1", "currency": "USD", "source": []}):
            record = task()
            record["attempts"][0]["cost"] = cost
            invalid.append(record)
        for record in invalid:
            with self.subTest(record=record), self.assertRaises(ValueError):
                metrics.validate_record(record)


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-metrics-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve()
        self.journal = self.project / metrics.JOURNAL

    def test_preview_and_empty_summary_write_nothing(self):
        result = metrics.record_task(self.project, task())
        self.assertTrue(result["preview"])
        self.assertEqual(metrics.summarize(metrics.read_records(self.project))["groups"], [])
        self.assertEqual(list(self.project.iterdir()), [])

    def test_apply_and_duplicate_preserve_data(self):
        metrics.record_task(self.project, task(), apply=True)
        original = self.journal.read_bytes()
        with self.assertRaises(ValueError):
            metrics.record_task(self.project, task(), apply=True)
        self.assertEqual(self.journal.read_bytes(), original)
        metrics.record_task(self.project, task("pair-02"), apply=True)
        self.assertEqual(len(metrics.read_records(self.project)), 2)
        self.assertFalse((self.project / metrics.LOCK).exists())

    def test_malformed_journal_refuses_without_overwrite(self):
        self.journal.parent.mkdir(parents=True)
        self.journal.write_bytes(b"not-json\n")
        with self.assertRaises(ValueError):
            metrics.record_task(self.project, task(), apply=True)
        self.assertEqual(self.journal.read_bytes(), b"not-json\n")

    def test_duplicate_existing_journal_is_refused(self):
        self.journal.parent.mkdir(parents=True)
        line = json.dumps(task()) + "\n"
        self.journal.write_text(line * 2, encoding="utf-8")
        with self.assertRaises(ValueError):
            metrics.read_records(self.project)

    def test_busy_writer_lock_is_preserved(self):
        lock = self.project / metrics.LOCK
        lock.parent.mkdir(parents=True)
        lock.write_bytes(b"other writer\n")
        with self.assertRaises(FileExistsError):
            metrics.record_task(self.project, task(), apply=True)
        self.assertEqual(lock.read_bytes(), b"other writer\n")
        self.assertFalse(self.journal.exists())

    def test_write_failure_keeps_journal_and_cleans_owned_lock(self):
        metrics.record_task(self.project, task(), apply=True)
        original = self.journal.read_bytes()
        with mock.patch.object(metrics.install, "atomic_write", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                metrics.record_task(self.project, task("pair-02"), apply=True)
        self.assertEqual(self.journal.read_bytes(), original)
        self.assertFalse((self.project / metrics.LOCK).exists())

    def test_file_parent_refused_before_writes(self):
        (self.project / "ai-kit").write_bytes(b"native data")
        with self.assertRaises(NotADirectoryError):
            metrics.record_task(self.project, task(), apply=True)
        self.assertEqual((self.project / "ai-kit").read_bytes(), b"native data")

    def test_linked_root_parent_and_destination_refused(self):
        for candidate in (self.project, self.journal.parent, self.journal, self.project / metrics.LOCK):
            with self.subTest(candidate=candidate), mock.patch.object(
                    metrics.install, "is_link", side_effect=lambda path: path == candidate):
                with self.assertRaises(ValueError):
                    metrics.record_task(self.project, task(), apply=True)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_cli_preview_apply_summary_and_invalid_input(self):
        source = self.project / "record.json"
        source.write_text(json.dumps(task()), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(metrics.main(["record", str(self.project), "--from-json", str(source)]), 0)
        self.assertFalse(self.journal.exists())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(metrics.main(["record", str(self.project), "--from-json", str(source), "--apply"]), 0)
            self.assertEqual(metrics.main(["summary", str(self.project)]), 0)
        source.write_text("{}\n", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(metrics.main(["record", str(self.project), "--from-json", str(source)]), 1)
