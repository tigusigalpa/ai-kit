"""Local lifecycle and source evidence; no model calls, delegation or external services."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor
import install
import task_snapshot as sources
import task_workflow as tasks


@unittest.skipUnless(shutil.which("git"), "Git is required for task source fingerprints")
class WorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aikit-task-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = self.base / "application with spaces"
        self.project.mkdir()
        self.write("ai-kit/settings.json", {"task_workflow": True})
        self.write("app.py", "value = 1\n")
        self.write(".gitignore", "/ai-kit/\n/ignored/\n__pycache__/\n.env\n")
        self.git("init", "-q")
        self.git("add", "app.py", ".gitignore")
        self.git("-c", "user.name=Task Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture")
        self.spec = {"schema": 1, "id": "case-1", "title": "A bounded change", "description": "Preserve the interface.",
                     "acceptance": [{"id": "behavior", "description": "The intended result is correct."},
                                    {"id": "compatibility", "description": "Existing behavior remains valid."}],
                     "checks": [{"id": "tests", "argv": [sys.executable, "-c", "assert 2 + 2 == 4"],
                                 "cwd": ".", "timeout_seconds": 10}]}
        self.spec_path = self.base / "spec.json"
        self.approval_path = self.base / "review.json"
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def write(self, relative, value):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, dict) else value, encoding="utf-8")

    def git(self, *args):
        return sources.git(self.project, *args)

    def save_spec(self):
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def start(self):
        self.save_spec()
        tasks.create(self.project, self.spec_path, apply=True)
        tasks.transition(self.project, "case-1", "implementing", apply=True)

    def ready(self):
        self.start()
        result = tasks.check(self.project, "case-1", "tests", apply=True)
        self.assertEqual(result["receipt"]["outcome"], "passed")
        tasks.transition(self.project, "case-1", "reviewing", apply=True)
        tasks.transition(self.project, "case-1", "awaiting_approval", apply=True)

    def approval(self):
        version = tasks.status(self.project, "case-1")["fingerprint"]
        value = {"schema": 1, "task_id": "case-1", "fingerprint": version, "reviewer": "Fixture reviewer",
                 "criteria": [{"id": c["id"], "passed": True, "evidence": "Reviewed the declared scenario."}
                              for c in self.spec["acceptance"]]}
        self.approval_path.write_text(json.dumps(value), encoding="utf-8")
        return value

    def test_opt_in_is_required_even_for_create_preview(self):
        for settings in ({}, {"task_workflow": False}):
            self.write("ai-kit/settings.json", settings)
            with self.assertRaisesRegex(ValueError, "with-task-workflow"):
                tasks.create(self.project, self.spec_path)

    def test_create_preview_and_repeated_create_preserve_state(self):
        self.assertTrue(tasks.create(self.project, self.spec_path)["preview"])
        self.assertFalse((self.project / tasks.DIRECTORY).exists())
        tasks.create(self.project, self.spec_path, apply=True)
        path = tasks.state_path(self.project, "case-1")
        before = path.read_bytes()
        self.assertTrue(tasks.create(self.project, self.spec_path, apply=True)["unchanged"])
        self.assertEqual(path.read_bytes(), before)
        self.spec["description"] = "Different requirements"
        self.save_spec()
        with self.assertRaisesRegex(ValueError, "revise"):
            tasks.create(self.project, self.spec_path, apply=True)
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_definitions_and_duplicate_json_do_not_create_state(self):
        variants = []
        for key, value in (("id", "../other"), ("id", "con"), ("acceptance", []), ("checks", [])):
            candidate = copy.deepcopy(self.spec)
            candidate[key] = value
            variants.append(candidate)
        for key, value in (("argv", "echo ok"), ("cwd", "../outside"), ("timeout_seconds", True)):
            candidate = copy.deepcopy(self.spec)
            candidate["checks"][0][key] = value
            variants.append(candidate)
        candidate = copy.deepcopy(self.spec)
        candidate["acceptance"].append(candidate["acceptance"][0])
        variants.append(candidate)
        for candidate in variants:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                tasks.definition(candidate)
        self.spec_path.write_text('{"schema":1,"schema":1}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            tasks.create(self.project, self.spec_path, apply=True)
        self.assertFalse((self.project / tasks.DIRECTORY).exists())

    def test_previews_run_no_check_and_write_no_state(self):
        self.start()
        path = tasks.state_path(self.project, "case-1")
        before = path.read_bytes()
        with patch.object(tasks, "execute", side_effect=AssertionError("Preview executed a command")):
            self.assertTrue(tasks.check(self.project, "case-1", "tests")["preview"])
        tasks.transition(self.project, "case-1", "checking")
        tasks.status(self.project, "case-1")
        self.assertEqual(path.read_bytes(), before)

    def test_complete_lifecycle_requires_review_of_every_criterion(self):
        self.ready()
        self.approval()
        before = tasks.state_path(self.project, "case-1").read_bytes()
        self.assertTrue(tasks.accept(self.project, "case-1", self.approval_path)["preview"])
        self.assertEqual(tasks.state_path(self.project, "case-1").read_bytes(), before)
        tasks.accept(self.project, "case-1", self.approval_path, apply=True)
        result = tasks.status(self.project, "case-1")
        self.assertTrue(result["accepted_current"])
        self.assertEqual(result["effective_state"], "accepted")
        self.assertEqual(result["receipts"][0]["returncode"], 0)
        self.assertEqual(len(result["receipts"][0]["output_sha256"]), 64)

    def test_missing_checks_and_skipped_states_cannot_be_accepted(self):
        self.start()
        tasks.transition(self.project, "case-1", "checking", apply=True)
        for target in ("reviewing", "awaiting_approval", "accepted"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                tasks.transition(self.project, "case-1", target, apply=True)

    def test_all_declared_checks_must_pass(self):
        second = copy.deepcopy(self.spec["checks"][0])
        second["id"] = "second"
        self.spec["checks"].append(second)
        self.start()
        tasks.check(self.project, "case-1", "tests", apply=True)
        with self.assertRaises(ValueError):
            tasks.transition(self.project, "case-1", "reviewing", apply=True)
        tasks.check(self.project, "case-1", "second", apply=True)
        tasks.transition(self.project, "case-1", "reviewing", apply=True)

    def test_dirty_untracked_deleted_index_and_head_changes_invalidate_checks(self):
        self.start()
        tasks.check(self.project, "case-1", "tests", apply=True)
        original = tasks.status(self.project, "case-1")["fingerprint"]
        self.write("app.py", "value = 2\n")
        self.assertFalse(tasks.status(self.project, "case-1")["checks"]["tests"])
        self.write("app.py", "value = 1\n")
        self.assertEqual(tasks.status(self.project, "case-1")["fingerprint"], original)
        self.write("new.py", "value = 3\n")
        self.assertFalse(tasks.status(self.project, "case-1")["checks"]["tests"])
        (self.project / "new.py").unlink()
        (self.project / "app.py").unlink()
        self.assertFalse(tasks.status(self.project, "case-1")["checks"]["tests"])
        self.write("app.py", "value = 1\n")
        self.git("-c", "user.name=Task Fixture", "-c", "user.email=fixture@example.invalid", "-c",
                 "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "New revision")
        self.assertFalse(tasks.status(self.project, "case-1")["checks"]["tests"])
        with self.assertRaises(ValueError):
            tasks.transition(self.project, "case-1", "reviewing", apply=True)

    def test_ignored_outputs_and_task_state_do_not_change_fingerprint(self):
        self.start()
        before = tasks.status(self.project, "case-1")["fingerprint"]
        self.write("ignored/result.txt", "Generated output")
        self.write("ai-kit/.tasks/reviews/draft.json", "{}")
        self.assertEqual(tasks.status(self.project, "case-1")["fingerprint"], before)

    def test_stale_approval_and_accepted_status_after_code_changes(self):
        self.ready()
        self.approval()
        self.write("app.py", "value = 2\n")
        with self.assertRaises(ValueError):
            tasks.accept(self.project, "case-1", self.approval_path, apply=True)
        self.write("app.py", "value = 1\n")
        tasks.accept(self.project, "case-1", self.approval_path, apply=True)
        self.write("app.py", "value = 3\n")
        result = tasks.status(self.project, "case-1")
        self.assertEqual(result["state"], "accepted")
        self.assertEqual(result["effective_state"], "stale")
        self.assertFalse(result["accepted_current"])

    def test_false_incomplete_and_other_task_approvals_refuse(self):
        self.ready()
        valid = self.approval()
        variants = []
        for field, value in (("fingerprint", "0" * 64), ("task_id", "other"), ("criteria", valid["criteria"][:1])):
            candidate = copy.deepcopy(valid)
            candidate[field] = value
            variants.append(candidate)
        candidate = copy.deepcopy(valid)
        candidate["criteria"][0]["passed"] = False
        variants.append(candidate)
        for candidate in variants:
            self.approval_path.write_text(json.dumps(candidate), encoding="utf-8")
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                tasks.accept(self.project, "case-1", self.approval_path, apply=True)

    def test_reopening_starts_new_cycle_and_revise_keeps_historical_receipts(self):
        self.ready()
        tasks.transition(self.project, "case-1", "implementing", apply=True)
        self.assertFalse(tasks.status(self.project, "case-1")["checks"]["tests"])
        self.spec["description"] = "Reviewed new requirements"
        self.save_spec()
        tasks.create(self.project, self.spec_path, apply=True, revise=True)
        result = tasks.status(self.project, "case-1")
        self.assertEqual((result["state"], result["revision"]), ("planned", 2))
        self.assertEqual(len(result["receipts"]), 1)

    def test_cancelled_task_is_terminal_and_cannot_run_checks(self):
        self.start()
        tasks.transition(self.project, "case-1", "cancelled", apply=True)
        with self.assertRaises(ValueError):
            tasks.transition(self.project, "case-1", "implementing", apply=True)
        with self.assertRaises(ValueError):
            tasks.check(self.project, "case-1", "tests", apply=True)
        self.spec["description"] = "Try to revive a cancelled task"
        self.save_spec()
        with self.assertRaisesRegex(ValueError, "terminal"):
            tasks.create(self.project, self.spec_path, apply=True, revise=True)

    def test_failed_atomic_save_preserves_the_previous_task(self):
        self.start()
        path = tasks.state_path(self.project, "case-1")
        before = path.read_bytes()
        with patch.object(tasks.os, "replace", side_effect=OSError("Synthetic replace failure")), self.assertRaises(OSError):
            tasks.transition(self.project, "case-1", "checking", apply=True)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_failed_command_is_not_a_pass_and_output_is_not_persisted(self):
        self.spec["checks"][0]["argv"] = [sys.executable, "-c", "print('PRIVATE-OUTPUT'); raise SystemExit(7)"]
        self.start()
        result = tasks.check(self.project, "case-1", "tests", apply=True)
        self.assertEqual((result["state"], result["receipt"]["returncode"]), ("failed", 7))
        self.assertGreater(result["receipt"]["output_bytes"], 0)
        # The argv is declared by the operator; process output itself is not part of a receipt.
        self.assertNotIn("output", result["receipt"])
        self.assertFalse(tasks.status(self.project, "case-1")["checks"]["tests"])

    def test_check_that_changes_source_cannot_pass(self):
        self.spec["checks"][0]["argv"] = [sys.executable, "-c", "open('generated.py','w').write('changed')"]
        self.start()
        result = tasks.check(self.project, "case-1", "tests", apply=True)
        self.assertEqual(result["receipt"]["outcome"], "source_changed")
        self.assertEqual(result["state"], "failed")

    def test_failed_rerun_supersedes_a_prior_pass(self):
        self.start()
        tasks.check(self.project, "case-1", "tests", apply=True)
        result = {"outcome": "failed", "returncode": 9, "duration_seconds": 0.1,
                  "output_sha256": "0" * 64, "output_bytes": 0}
        with patch.object(tasks, "execute", return_value=result):
            tasks.check(self.project, "case-1", "tests", apply=True)
        report = tasks.status(self.project, "case-1")
        self.assertEqual(len(report["receipts"]), 2)
        self.assertFalse(report["checks"]["tests"])

    def test_timeout_and_interruption_leave_nonpassing_receipts(self):
        self.spec["checks"][0].update(argv=[sys.executable, "-c", "import time; time.sleep(20)"], timeout_seconds=1)
        self.start()
        result = tasks.check(self.project, "case-1", "tests", apply=True)
        self.assertEqual(result["receipt"]["outcome"], "timeout")
        tasks.transition(self.project, "case-1", "implementing", apply=True)
        with patch.object(tasks, "execute", side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            tasks.check(self.project, "case-1", "tests", apply=True)
        result = tasks.load_state(self.project, "case-1")
        self.assertEqual(result["state"], "failed")
        self.assertEqual(result["receipts"][-1]["outcome"], "interrupted")

    def test_exclusive_lock_and_invalid_state_are_preserved(self):
        self.start()
        self.write(tasks.LOCK, "Another process owns this lock")
        with self.assertRaises(FileExistsError):
            tasks.transition(self.project, "case-1", "checking", apply=True)
        self.assertEqual((self.project / tasks.LOCK).read_text(), "Another process owns this lock")
        path = tasks.state_path(self.project, "case-1")
        path.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            tasks.status(self.project, "case-1")
        self.assertEqual(path.read_text(), "{}")

    def test_check_cannot_overwrite_an_altered_task_ledger(self):
        self.start()
        def changed(*args):
            tasks.state_path(self.project, "case-1").write_text("{}", encoding="utf-8")
            return {"outcome": "passed"}
        with patch.object(tasks, "execute", side_effect=changed), self.assertRaisesRegex(ValueError, "changed its task state"):
            tasks.check(self.project, "case-1", "tests", apply=True)
        self.assertEqual(tasks.state_path(self.project, "case-1").read_text(), "{}")

    def test_submodules_credentials_and_oversized_files_refuse_fingerprints(self):
        self.git("update-index", "--add", "--cacheinfo", "160000," + self.git("rev-parse", "HEAD").decode().strip() + ",module")
        with self.assertRaisesRegex(ValueError, "submodules"):
            sources.snapshot(self.project)
        self.git("update-index", "--force-remove", "module")
        self.write(".env", "SECRET=private")
        self.git("add", "-f", ".env")
        with self.assertRaisesRegex(ValueError, "credential"):
            sources.snapshot(self.project)
        self.git("rm", "--cached", "-f", ".env")
        with patch.object(sources, "MAX_FILE_BYTES", 1), self.assertRaises(ValueError):
            sources.snapshot(self.project)

    def test_symlink_source_and_linked_task_state_refuse(self):
        outside = self.base / "outside.txt"
        outside.write_text("Do not read or change", encoding="utf-8")
        link = self.project / "linked.txt"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("Symlink creation privilege is unavailable")
        with self.assertRaises(ValueError):
            sources.snapshot(self.project)
        link.unlink()
        self.start()
        path = tasks.state_path(self.project, "case-1")
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises(ValueError):
            tasks.status(self.project, "case-1")
        self.assertEqual(outside.read_text(), "Do not read or change")


class InstallerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aikit-task-install-")
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve() / "project"

    def apply(self, **options):
        plan = install.build_plan(self.project, **options)
        self.assertFalse(plan["conflicts"], plan["conflicts"])
        self.assertTrue(install.apply_plan(plan))
        return plan

    def test_default_absence_opt_in_persistence_and_private_history_preservation(self):
        self.apply()
        self.assertFalse((self.project / "ai-kit/TASK-WORKFLOW.md").exists())
        self.assertFalse((self.project / "ai-kit/task.example.json").exists())
        self.apply(extras=["task-workflow"], agents=["codex", "claude"])
        example = self.project / "ai-kit/task.example.json"
        example.write_text("Custom example remains project-owned.\n", encoding="utf-8")
        state = self.project / tasks.DIRECTORY / "case.json"
        state.parent.mkdir()
        state.write_text("Private state must survive upgrades.\n", encoding="utf-8")
        self.apply(preset="minimal", mode="team")
        self.assertTrue(json.loads((self.project / "ai-kit/settings.json").read_text())["task_workflow"])
        self.assertEqual(example.read_text(), "Custom example remains project-owned.\n")
        self.assertEqual(state.read_text(), "Private state must survive upgrades.\n")
        self.assertFalse(doctor.examine(self.project)["errors"])
        if shutil.which("git"):
            sources.git(self.project, "init", "-q")
            self.assertTrue(sources.git(self.project, "check-ignore", tasks.DIRECTORY + "/case.json"))

    def test_modified_contract_conflicts_without_overwriting_private_state(self):
        self.apply(extras=["task-workflow"])
        contract = self.project / "ai-kit/TASK-WORKFLOW.md"
        contract.write_text("Reviewed local task policy.\n", encoding="utf-8")
        bundle = self.project.parent / "next-bundle"
        bundle.mkdir()
        for name in ("template", "templates", "integrations"):
            shutil.copytree(install.ROOT / name, bundle / name)
        for name in ("VERSION", "LICENSE"):
            shutil.copy2(install.ROOT / name, bundle / name)
        incoming = bundle / "template/ai-kit/TASK-WORKFLOW.md"
        incoming.write_text(incoming.read_text(encoding="utf-8") + "\nNew upstream requirement.\n", encoding="utf-8")
        plan = install.build_plan(self.project, root=bundle, mode="team")
        self.assertIn("ai-kit/TASK-WORKFLOW.md", plan["conflicts"])
        self.assertEqual(contract.read_text(), "Reviewed local task policy.\n")


if __name__ == "__main__":
    unittest.main()
