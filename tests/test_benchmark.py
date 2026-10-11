"""Synthetic workers exercise isolation, execution evidence, semantic review and private export."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import benchmark
import install
import metrics

WORKER = '''import json, os, pathlib, shutil, subprocess, sys
r = json.load(sys.stdin)
w = pathlib.Path.cwd()
assert (w / "value.txt").read_text() == "initial\\n"
assert "DATABASE_URL" not in os.environ
assert not (w / ".git").exists()
git = shutil.which("git")
if git:
    assert subprocess.run([git, "rev-parse", "--show-toplevel"], capture_output=True).returncode != 0
assert (w / "ai-kit/CORE.md").exists() == (r["arm"] != "baseline")
(w / "value.txt").write_text("changed\\n")
a = dict(r["requested"], disposition="succeeded", input_tokens=100, output_tokens=10,
         cached_input_tokens=0, reasoning_tokens=0,
         cost={"amount": "1.00" if r["arm"] == "baseline" else "0.50", "currency": "USD", "source": "provider-usage"})
print(json.dumps({"schema": 1, "attempts": [a], "rework": 0, "escalations": 0}))
'''


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "project"
        self.root.mkdir()
        self.git = shutil.which("git")
        if not self.git:
            self.skipTest("Git unavailable for immutable fixture snapshots")
        self.git_run("init", "-q")
        (self.root / "value.txt").write_text("initial\n", encoding="utf-8")
        (self.root / "pyproject.toml").write_text('[project]\nname = "fixture"\nrequires-python = ">=3.10"\n', encoding="utf-8")
        self.commit()
        self.revision = self.git_run("rev-parse", "HEAD").strip()
        # Current installed config is outside the fixture's pre-kit Git revision.
        shutil.copytree(install.ROOT / "template/ai-kit", self.root / "ai-kit")
        self.worker = self.base / "worker.py"
        self.worker.write_text(WORKER, encoding="utf-8")
        (self.base / "prompt.txt").write_text("Implement the requested fixture change.", encoding="utf-8")
        (self.base / "rubric.txt").write_text("Manually verify the intended change and absence of unrelated edits.", encoding="utf-8")
        self.pack = {"schema": 1, "experiment": "fixture-only", "revision": self.revision, "repeats": 2,
                     "fixed": {"provider": "fixture", "model": "fixture-model", "effort": None},
                     "worker": {"protocol": "aikit-worker-v1", "argv": [sys.executable, str(self.worker)]},
                     "checks": [[sys.executable, "-c", "from pathlib import Path; assert Path('value.txt').read_text() == 'changed\\n'"]],
                     "timeout_seconds": 15, "tasks": [{"task_id": "change", "prompt_file": "prompt.txt",
                         "rubric_file": "rubric.txt", "path": ".", "stack": "PYTHON", "operation": "implement",
                         "risks": [], "capabilities": []}]}
        self.pack_file = self.base / "pack.json"

    def git_run(self, *args):
        return subprocess.run([self.git, "-C", str(self.root), *args], capture_output=True, text=True, check=True).stdout

    def commit(self):
        self.git_run("add", "--", "value.txt", "pyproject.toml")
        self.git_run("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "commit", "-qm", "Fixture")

    def prepare(self):
        self.pack_file.write_text(json.dumps(self.pack), encoding="utf-8")
        return benchmark.prepare(self.root, self.pack_file, git=self.git)

    def reviews(self, run, *, outcome="correct"):
        value = benchmark.report(run)
        path = self.base / "reviews.json"
        path.write_text(json.dumps({"schema": 1, "reviews": [
            {"task_id": r["record"]["task_id"], "arm": r["record"]["arm"], "review": "manual", "outcome": outcome}
            for r in value["results"]]}), encoding="utf-8")
        return path

    def test_isolated_repeats_fixed_models_semantic_gate_reports_and_export(self):
        plan = self.prepare()
        self.assertFalse((self.root / plan["relative"]).exists())
        self.assertEqual(len(plan["units"]), 6)
        self.assertEqual(plan["units"][0]["route"], plan["units"][1]["route"])
        (self.root / "value.txt").write_text("uncommitted owner change\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"DATABASE_URL": "fixture-sensitive-value"}):
            run = benchmark.execute(plan)
        value = benchmark.report(run)
        self.assertTrue(value["complete"])
        self.assertEqual(value["observed_units"], 6)
        self.assertTrue(all(r["record"]["checks"] == "passed" for r in value["results"]))
        self.assertTrue(all(r["record"]["outcome"] == "incomplete" for r in value["results"]))
        self.assertTrue(all(c["savings_percent"] is None for c in value["comparisons"]))
        self.assertEqual((self.root / "value.txt").read_text(), "uncommitted owner change\n")
        with self.assertRaises(ValueError):
            benchmark.export_records(run, self.root)
        reviews = self.reviews(run)
        benchmark.review(run, reviews)
        self.assertEqual(benchmark.report(run)["results"][0]["record"]["outcome"], "incomplete")
        benchmark.review(run, reviews, apply=True)
        report = benchmark.report(run)
        self.assertEqual(report["comparisons"][0]["savings_percent"], "50.0")
        self.assertTrue((run / "results.json").is_file())
        self.assertIn("50.0", (run / "report.md").read_text())
        self.assertEqual(benchmark.export_records(run, self.root, apply=True)["new_records"], 6)
        self.assertEqual(benchmark.export_records(run, self.root, apply=True)["new_records"], 0)
        self.assertEqual(len(metrics.read_records(self.root)), 6)
        again = self.prepare()
        self.assertEqual(benchmark.execute(again), run)
        self.assertEqual(benchmark.report(run)["observed_units"], 6)
        self.pack["repeats"] = 3
        self.pack_file.write_text(json.dumps(self.pack), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "different plan"):
            benchmark.execute(benchmark.prepare(self.root, self.pack_file, git=self.git))

    def test_failed_checks_cannot_be_reviewed_as_correct(self):
        self.pack["repeats"] = 1
        self.pack["checks"] = [[sys.executable, "-c", "raise SystemExit(1)"]]
        run = benchmark.execute(self.prepare())
        with self.assertRaises(ValueError):
            benchmark.review(run, self.reviews(run), apply=True)
        benchmark.review(run, self.reviews(run, outcome="incorrect"), apply=True)
        self.assertTrue(all(c["savings_percent"] is None for c in benchmark.report(run)["comparisons"]))

    def test_unknown_telemetry_and_unconfirmed_execution_block_savings(self):
        self.worker.write_text('import json; print(json.dumps({"schema": 1, "attempts": [{"disposition": "inconclusive"}], "rework": 0, "escalations": 0}))', encoding="utf-8")
        self.pack["repeats"] = 1
        self.pack["checks"] = []
        run = benchmark.execute(self.prepare())
        benchmark.review(run, self.reviews(run), apply=True)
        value = benchmark.report(run)
        self.assertFalse(value["results"][0]["observed_matches_request"])
        self.assertIsNone(value["summary"]["groups"][0]["cost_per_correct_result"])
        self.assertTrue(all(c["savings_percent"] is None for c in value["comparisons"]))

    def test_invalid_packs_prompt_traversal_secret_revision_and_links_refused(self):
        self.pack["tasks"][0]["prompt_file"] = "../outside.txt"
        with self.assertRaises(ValueError):
            self.prepare()
        self.pack["tasks"][0]["prompt_file"] = "prompt.txt"
        original = install.is_link
        with mock.patch.object(install, "is_link", side_effect=lambda p: p.name == "benchmarks" or original(p)):
            with self.assertRaises(ValueError):
                self.prepare()
        (self.root / ".env").write_text("FIXTURE_SECRET=not-real\n", encoding="utf-8")
        self.git_run("add", "-f", ".env")
        self.git_run("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "commit", "-qm", "Secret fixture")
        self.pack["revision"] = self.git_run("rev-parse", "HEAD").strip()
        with self.assertRaisesRegex(ValueError, "secret/runtime"):
            self.prepare()

    def test_worker_timeout_produces_unknown_attempt_not_a_free_success(self):
        self.pack["repeats"] = 1
        self.pack["checks"] = []
        plan = self.prepare()
        with mock.patch.object(benchmark, "invoke", return_value=(None, "")):
            run = benchmark.execute(plan)
        value = benchmark.report(run)
        self.assertTrue(all(r["worker_exit_code"] is None for r in value["results"]))
        self.assertTrue(all(r["record"]["rework"] is None and r["record"]["escalations"] is None for r in value["results"]))
        self.assertTrue(all(g["rework"] is None and g["escalations"] is None for g in value["summary"]["groups"]))
        with self.assertRaises(ValueError):
            benchmark.review(run, self.reviews(run), apply=True)

    def test_command_validation_secret_exceptions_and_shell_refusal(self):
        bad = copy.deepcopy(self.pack)
        bad["worker"]["argv"] = "python worker.py"
        with self.assertRaises(ValueError):
            benchmark.validate_pack(bad, self.root)
        self.assertFalse(benchmark.secret_path(".env.example", [".env.*", "!.env.example"]))
        self.assertTrue(benchmark.secret_path("secrets/test.txt", ["/secrets/"]))
        routing = self.root / "ai-kit/router/routing.json"
        config = json.loads(routing.read_text())
        config["project_pin"] = {"provider": "local", "model": "fixture-local", "effort": None}
        routing.write_text(json.dumps(config), encoding="utf-8")
        plan = self.prepare()
        adaptive_unit = next(unit for unit in plan["units"] if unit["arm"] == "kit-adaptive")
        self.assertEqual(adaptive_unit["route"], config["project_pin"])
        duplicate = copy.deepcopy(self.pack["tasks"][0])
        duplicate["task_id"] = "renamed-same-case"
        self.pack["tasks"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "Duplicate task material"):
            self.prepare()
        listing = b"100644 blob " + b"a" * 40 + b"\tCase.txt\x00" + b"100644 blob " + b"b" * 40 + b"\tcase.txt\x00"
        with mock.patch.object(benchmark, "git_command", side_effect=[str(self.root).encode() + b"\n", self.revision.encode() + b"\n", listing]):
            with self.assertRaisesRegex(ValueError, "Case-colliding"):
                benchmark.snapshot_files(self.root, self.revision)

    def test_task_path_is_probed_against_the_project(self):
        bad = copy.deepcopy(self.pack)
        bad["tasks"][0]["path"] = "../outside"
        with self.assertRaises(ValueError):
            benchmark.validate_pack(bad, self.root)
        benchmark.validate_pack(copy.deepcopy(self.pack), self.root)

    def test_kit_arm_agents_and_preset_are_configurable_and_validated(self):
        self.pack["repeats"] = 1
        self.pack["kit_agents"] = ["not-a-client"]
        with self.assertRaises(ValueError):
            self.prepare()
        self.pack["kit_agents"] = ["claude"]
        self.pack["kit_preset"] = "unknown-preset"
        with self.assertRaises(ValueError):
            self.prepare()
        self.pack["kit_preset"] = "strict"
        run = benchmark.execute(self.prepare())
        workspaces = sorted(run.glob("unit-*/workspace"))
        kit_workspaces = [w for w in workspaces if (w / "ai-kit/CORE.md").exists()]
        baseline_workspaces = [w for w in workspaces if not (w / "ai-kit/CORE.md").exists()]
        self.assertEqual(len(kit_workspaces), 2)
        self.assertEqual(len(baseline_workspaces), 1)
        self.assertTrue(all((w / "CLAUDE.md").is_file() for w in kit_workspaces))
        self.assertFalse((baseline_workspaces[0] / "CLAUDE.md").exists())

    def test_unit_failures_are_recorded_and_runs_resume_without_retry(self):
        self.pack["repeats"] = 1
        # The fixture evidences PYTHON only, so both kit arms fail before any paid worker call.
        self.pack["tasks"][0]["stack"] = "GO"
        plan = self.prepare()
        run = benchmark.execute(plan)
        value = benchmark.report(run)
        self.assertTrue(value["complete"])
        self.assertEqual(value["observed_units"], 3)
        failed = [r for r in value["results"] if not r["telemetry_valid"]]
        self.assertEqual(len(failed), 2)
        self.assertTrue(all(r["record"]["arm"] in {"kit-fixed", "kit-adaptive"} for r in failed))
        self.assertTrue(all("error" in r for r in failed))
        baseline = next(r for r in value["results"] if r["record"]["arm"] == "baseline")
        self.assertTrue(baseline["telemetry_valid"])
        self.assertTrue(all(c["savings_percent"] is None for c in value["comparisons"]))
        self.assertEqual(benchmark.execute(plan), run)
        self.assertEqual(benchmark.report(run)["observed_units"], 3)
        self.pack["repeats"] = 2
        self.pack_file.write_text(json.dumps(self.pack), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "different plan"):
            benchmark.execute(benchmark.prepare(self.root, self.pack_file, git=self.git))
