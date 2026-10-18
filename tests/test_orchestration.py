"""Opt-in installation and mocked billing/transport; no live model calls."""
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
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor
import install
import orchestrate as orch


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aikit-orchestration-")
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve()
        (self.project / "ai-kit").mkdir()
        self.write("ai-kit/settings.json", {"orchestration": True})
        self.config = copy.deepcopy(orch.DEFAULTS)
        self.config.update(enabled=True, model="example/text-model")
        self.write(orch.CONFIG, self.config)
        self.write("task.json", {"schema": 1, "id": "case-1", "instruction": "Classify the supplied rows.",
                                  "input_files": ["comments.txt"]})
        (self.project / "comments.txt").write_text("Synthetic input, not a credential.", encoding="utf-8")
        self.calls = []
        self.response = {"id": "gen-example", "model": "example/text-model",
                         "choices": [{"finish_reason": "stop", "message": {"content": "Reviewed output"}}],
                         "usage": {"cost": 0.02, "prompt_tokens": 50, "completion_tokens": 10,
                                   "prompt_tokens_details": {"cached_tokens": 20},
                                   "completion_tokens_details": {"reasoning_tokens": 2}}}
        self.limits = {"data": {"limit": 1, "limit_remaining": 1, "limit_reset": None,
                                "include_byok_in_limit": True}}
        self.environment = patch.dict(os.environ, {"OPENROUTER_API_KEY": "synthetic-secret"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def write(self, relative, value):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def client(self, method, route, payload, key, timeout):
        self.calls.append((method, route, payload))
        self.assertEqual(key, "synthetic-secret")
        if route == "key":
            return copy.deepcopy(self.limits)
        if route.startswith("generation?"):
            return {"data": {"id": "gen-example", "total_cost": 0.03}}
        reservation = orch.state(self.project)["attempts"][-1]
        self.assertEqual(reservation["status"], "pending")
        self.assertIsNone(reservation["cost_usd"])
        self.assertTrue((self.project / orch.LOCK).is_file())
        return copy.deepcopy(self.response)

    def execute(self):
        return orch.run(self.project, "task.json", apply=True, client=self.client)

    def next_task(self, task_id="case-2"):
        task = json.loads((self.project / "task.json").read_text())
        task["id"] = task_id
        self.write("task.json", task)

    def test_preview_needs_no_key_network_or_workspace_writes(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(orch, "transport", side_effect=AssertionError):
            preview = orch.run(self.project, "task.json")
        self.assertTrue(preview["preview"])
        self.assertEqual(preview["network_requests"], 0)
        self.assertFalse((self.project / "ai-kit/.orchestration").exists())

    def test_success_is_durable_private_idempotent_and_source_bound(self):
        result = self.execute()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["cost_usd"], "0.02")
        self.assertEqual(len(self.calls), 2)
        again = self.execute()
        self.assertTrue(again["already_completed"])
        self.assertEqual(len(self.calls), 2)
        record = orch.state(self.project)["attempts"][0]
        self.assertEqual(record["usage"]["cached_input_tokens"], 20)
        self.assertEqual(record["usage"]["reasoning_tokens"], 2)
        text = (self.project / orch.STATE).read_text()
        self.assertNotIn("synthetic-secret", text)
        self.assertNotIn("Synthetic input", text)
        self.assertFalse((self.project / orch.LOCK).exists())
        (self.project / "comments.txt").write_text("Changed task input", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.execute()
        self.assertEqual(len(self.calls), 2)

    def test_request_has_explicit_model_caps_and_no_tools_fallback_or_stream(self):
        self.execute()
        body = self.calls[1][2]
        self.assertEqual(body["model"], "example/text-model")
        self.assertEqual(body["max_tokens"], 1024)
        self.assertFalse(body["stream"])
        self.assertFalse(body["provider"]["allow_fallbacks"])
        self.assertEqual(body["provider"]["max_price"], {"prompt": 1, "completion": 3, "request": 0})
        self.assertNotIn("tools", body)

    def test_disabled_uninstalled_or_unresolved_execution_refuses(self):
        for field, value in (("enabled", False), ("model", None)):
            config = copy.deepcopy(self.config)
            config[field] = value
            self.write(orch.CONFIG, config)
            with self.assertRaises(ValueError):
                self.execute()
        self.write("ai-kit/settings.json", {})
        with self.assertRaises(ValueError):
            orch.run(self.project, "task.json")
        self.assertEqual(self.calls, [])

    def test_key_requires_dedicated_non_resetting_cap_including_byok(self):
        for change in ({"limit": None}, {"limit": 2}, {"limit_reset": "daily"},
                       {"limit_remaining": 0}, {"include_byok_in_limit": False}, {"limit": "NaN"}):
            original = copy.deepcopy(self.limits)
            self.limits["data"].update(change)
            with self.assertRaises(ValueError):
                self.execute()
            self.limits = original
            self.assertFalse((self.project / orch.STATE).exists())
        self.assertTrue(all(route == "key" for _, route, _ in self.calls))

    def test_local_budget_and_request_count_stop_before_network(self):
        for field, value in (("budget_usd", "0.10"), ("max_requests", 1)):
            with self.subTest(field=field):
                self.calls.clear()
                if (self.project / orch.STATE).exists():
                    (self.project / orch.STATE).unlink()
                for output in (self.project / "ai-kit/.orchestration/outputs").glob("*.json"):
                    output.unlink()
                config = copy.deepcopy(self.config)
                config[field] = value
                self.write(orch.CONFIG, config)
                self.limits["data"]["limit"] = float(config["budget_usd"])
                self.execute()
                self.next_task("next-" + field)
                with self.assertRaises(ValueError):
                    self.execute()
                self.assertEqual(len(self.calls), 2)

    def test_unknown_usage_cost_and_expensive_request_freeze_followups(self):
        for cost in (None, "NaN", True, 0.2):
            with self.subTest(cost=cost):
                self.calls.clear()
                if (self.project / orch.STATE).exists():
                    (self.project / orch.STATE).unlink()
                for output in (self.project / "ai-kit/.orchestration/outputs").glob("*.json"):
                    output.unlink()
                self.response["usage"]["cost"] = cost
                self.assertEqual(self.execute()["status"], "uncertain")
                self.next_task("another-case")
                with self.assertRaises(ValueError):
                    self.execute()
                self.assertEqual(len(self.calls), 2)

    def test_timeout_and_process_interruption_never_retry_paid_work(self):
        def timeout(method, route, payload, key, seconds):
            if method == "GET":
                return self.limits
            raise TimeoutError("Sensitive raw provider message must not be stored")
        result = orch.run(self.project, "task.json", apply=True, client=timeout)
        self.assertEqual(result["status"], "uncertain")
        self.assertNotIn("Sensitive raw", (self.project / orch.STATE).read_text())
        with self.assertRaises(ValueError):
            self.execute()
        current = orch.state(self.project)
        current["attempts"][0]["status"] = "pending"
        orch.save(self.project, current)
        self.next_task()
        with self.assertRaises(ValueError):
            self.execute()

    def test_malformed_wrong_model_tool_calls_and_truncation_keep_billed_cost(self):
        for change in ({"choices": []}, {"model": "example/other"},
                       {"choices": [{"finish_reason": "length", "message": {"content": "partial"}}]},
                       {"choices": [{"finish_reason": "stop", "message": {"content": "x", "tool_calls": [{}]}}]}):
            original = copy.deepcopy(self.response)
            self.response.update(change)
            if (self.project / orch.STATE).exists():
                (self.project / orch.STATE).unlink()
            self.assertEqual(self.execute()["status"], "failed")
            self.assertEqual(orch.summary(orch.state(self.project))["known_cost_usd"], "0.02")
            self.response = original

    def test_ledger_lock_and_existing_outputs_refuse_without_network(self):
        lock = self.project / orch.LOCK
        lock.parent.mkdir(parents=True)
        lock.write_text("Existing owner", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.execute()
        self.assertTrue(lock.exists())
        lock.unlink()
        self.write("ai-kit/.orchestration/outputs/case-1.json", {"keep": "existing output"})
        with self.assertRaises(ValueError):
            self.execute()
        self.assertFalse(self.calls)

    def test_paths_private_files_input_bounds_and_schema_are_checked_before_network(self):
        for name in ("../outside.txt", ".env", "nested/auth.json", "private.pem"):
            self.write("task.json", {"schema": 1, "id": "case-1", "instruction": "Inspect", "input_files": [name]})
            with self.assertRaises((ValueError, OSError)):
                self.execute()
        self.write("task.json", {"schema": 1, "id": "case-1", "instruction": "x" * 20000, "input_files": []})
        with self.assertRaises(ValueError):
            self.execute()
        self.assertFalse(self.calls)
        for field, invalid in (("budget_usd", "Infinity"), ("max_requests", True), ("unknown", 1),
                               ("model", "openrouter/auto"), ("request_reserve_usd", "0")):
            config = copy.deepcopy(self.config)
            config[field] = invalid
            with self.assertRaises(ValueError):
                orch.validate_config(config)
        with self.assertRaises(ValueError):
            orch.load_json('{"schema":1,"schema":2}')

    def test_symlinked_input_and_runtime_parent_are_refused(self):
        linked = self.project / "linked.txt"
        try:
            linked.symlink_to(self.project / "comments.txt")
        except OSError:
            self.skipTest("Symlink creation unavailable")
        self.write("task.json", {"schema": 1, "id": "case-1", "instruction": "Inspect", "input_files": ["linked.txt"]})
        with self.assertRaises(ValueError):
            self.execute()
        self.assertFalse(self.calls)

    def test_review_is_explicit_source_bound_and_costs_include_rejected_work(self):
        self.execute()
        self.assertEqual(orch.summary(orch.state(self.project))["accepted"], 0)
        orch.review(self.project, "case-1", "accepted")
        self.assertEqual(orch.summary(orch.state(self.project))["accepted"], 0)
        orch.review(self.project, "case-1", "accepted", apply=True)
        self.next_task()
        self.execute()
        orch.review(self.project, "case-2", "rejected", apply=True)
        report = orch.summary(orch.state(self.project))
        self.assertEqual(report["cost_per_accepted_usd"], "0.04")
        output = self.project / "ai-kit/.orchestration/outputs/case-1.json"
        output.write_text("Changed result", encoding="utf-8")
        with self.assertRaises(ValueError):
            orch.review(self.project, "case-1", "accepted", apply=True)

    def test_reconcile_known_generation_reads_billing_without_repeating_inference(self):
        self.response["usage"].pop("cost")
        self.execute()
        with self.assertRaises(ValueError):
            orch.review(self.project, "case-1", "accepted", apply=True)
        result = orch.reconcile(self.project, "case-1", apply=True, client=self.client)
        self.assertEqual(result["cost_usd"], "0.03")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(sum(method == "POST" for method, _, _ in self.calls), 1)

    def test_reconciliation_never_accepts_an_unrelated_generation(self):
        self.response["usage"].pop("cost")
        self.execute()
        with self.assertRaises(ValueError):
            orch.reconcile(self.project, "case-1", apply=True,
                           client=lambda *args: {"data": {"id": "different", "total_cost": 0}})
        self.assertEqual(orch.state(self.project)["attempts"][0]["status"], "uncertain")

    def test_process_interrupt_keeps_a_durable_pending_charge(self):
        def interrupt(method, *args):
            if method == "GET":
                return self.limits
            raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            orch.run(self.project, "task.json", apply=True, client=interrupt)
        self.assertEqual(orch.state(self.project)["attempts"][0]["status"], "pending")
        self.assertFalse((self.project / orch.LOCK).exists())
        with self.assertRaises(ValueError):
            self.execute()

    def test_output_created_during_request_is_preserved_and_charge_retained(self):
        def competing_output(method, route, payload, key, timeout):
            result = self.client(method, route, payload, key, timeout)
            if method == "POST":
                self.write("ai-kit/.orchestration/outputs/case-1.json", {"keep": "other writer"})
            return result
        result = orch.run(self.project, "task.json", apply=True, client=competing_output)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["cost_usd"], "0.02")
        self.assertEqual(json.loads((self.project / result["output"]).read_text())["keep"], "other writer")

    def test_posix_runtime_permissions_fifo_and_linked_runtime_are_checked(self):
        if os.name == "nt":
            self.skipTest("POSIX modes/FIFO checks")
        fifo = self.project / "pipe.txt"
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            orch.read_file(self.project, "pipe.txt")
        self.execute()
        self.assertEqual((self.project / orch.STATE).stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.project / "ai-kit/.orchestration").stat().st_mode & 0o777, 0o700)
        shutil.rmtree(self.project / "ai-kit/.orchestration")
        outside = self.project / "outside"
        outside.mkdir()
        (self.project / "ai-kit/.orchestration").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.execute()
        self.assertFalse(list(outside.iterdir()))

    def test_transport_rejects_redirects_and_bounds_responses(self):
        self.assertIsNone(orch.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.invalid"))
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"x" * 2000001
        opener = unittest.mock.Mock()
        opener.open.return_value = response
        with patch.object(orch.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(ValueError):
                orch.transport("GET", "key", None, "synthetic-secret", 3)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://openrouter.ai/api/v1/key")
        self.assertEqual(request.get_header("Authorization"), "Bearer synthetic-secret")

    def test_private_write_collision_preserves_unowned_temporary_file(self):
        path = self.project / (orch.STATE + ".fixed.tmp")
        path.parent.mkdir(parents=True)
        path.write_text("Keep another writer's file", encoding="utf-8")
        fake_id = unittest.mock.Mock(hex="fixed")
        with patch.object(orch.uuid, "uuid4", return_value=fake_id):
            with self.assertRaises(FileExistsError):
                orch.private_write(self.project, orch.STATE, b"replacement")
        self.assertEqual(path.read_text(), "Keep another writer's file")


class OrchestrationInstallationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aikit-optional-orchestration-")
        self.addCleanup(temporary.cleanup)
        self.target = Path(temporary.name).resolve() / "project with spaces"

    def apply(self, **options):
        plan = install.build_plan(self.target, **options)
        self.assertTrue(install.apply_plan(plan), plan["conflicts"])
        return plan

    def test_module_default_absence_and_explicit_install_preservation(self):
        self.apply(preset="minimal", agents=["codex"])
        self.assertFalse((self.target / orch.CONFIG).exists())
        self.assertFalse((self.target / ".codex/agents").exists())
        self.apply(extras=["orchestration"])
        self.assertFalse(orch.configuration(self.target)["enabled"])
        for name in ("explorer", "worker", "reviewer"):
            path = self.target / f".codex/agents/aikit_{name}.toml"
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("__CHEAP", text)
            if sys.version_info >= (3, 11):
                import tomllib
                data = tomllib.loads(text)
                self.assertEqual(data["name"], "aikit_" + name)
                self.assertTrue(data["model"])
        private = self.target / "ai-kit/.orchestration/custom-result.json"
        private.parent.mkdir()
        private.write_text("Existing private result", encoding="utf-8")
        config = orch.configuration(self.target)
        config["budget_usd"] = "2"
        (self.target / orch.CONFIG).write_text(json.dumps(config), encoding="utf-8")
        plan = self.apply(preset="minimal")
        self.assertIn("orchestration", plan["extras"])
        self.assertEqual(orch.configuration(self.target)["budget_usd"], "2")
        self.assertEqual(private.read_text(), "Existing private result")
        self.assertEqual(install.build_plan(self.target)["actions"], {})
        self.assertEqual(doctor.examine(self.target)["errors"], [])

    def test_non_codex_selection_and_helper_retirement_are_explicit(self):
        self.apply(extras=["orchestration"], agents=["claude"])
        self.assertFalse((self.target / ".codex/agents").exists())
        self.apply(agents=["codex", "claude"])
        plan = install.build_plan(self.target, agents=["claude"])
        self.assertTrue(any(name.startswith(".codex/agents/") for name in plan["adapter_conflicts"]))
        self.assertFalse(install.apply_plan(plan))

    def test_existing_codex_config_and_helper_edits_survive_and_upgrades_conflict(self):
        self.target.mkdir()
        (self.target / ".codex").mkdir()
        (self.target / ".codex/config.toml").write_text('model = "existing-model"\n', encoding="utf-8")
        self.apply(extras=["orchestration"], agents=["codex"])
        self.assertIn("existing-model", (self.target / ".codex/config.toml").read_text())
        path = self.target / ".codex/agents/aikit_worker.toml"
        original = path.read_text(encoding="utf-8")
        path.write_text(original + "\n# Local customization\n", encoding="utf-8")
        self.assertEqual(install.build_plan(self.target)["actions"], {})
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder).resolve() / "reference"
            shutil.copytree(install.ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            incoming = source / "integrations/codex-agents/aikit_worker.toml"
            incoming.write_text(incoming.read_text() + "\n# Changed upstream\n", encoding="utf-8")
            plan = install.build_plan(self.target, root=source)
            self.assertIn(".codex/agents/aikit_worker.toml", plan["conflicts"])
            self.assertFalse(install.apply_plan(plan))
            self.assertIn("Local customization", path.read_text())

    def test_private_team_visibility_keeps_runtime_private_and_helpers_shareable(self):
        git = shutil.which("git")
        if not git:
            self.skipTest("Git unavailable")
        for mode in ("private", "team"):
            if self.target.exists():
                shutil.rmtree(self.target)
            self.apply(extras=["orchestration"], agents=["codex"], mode=mode)
            subprocess.run([git, "init", str(self.target)], capture_output=True, check=True)
            for relative in ("ai-kit/.orchestration/state.json", ".codex/agents/aikit_worker.toml"):
                result = subprocess.run([git, "-C", str(self.target), "check-ignore", "--no-index", relative], capture_output=True)
                self.assertEqual(result.returncode == 0, relative.startswith("ai-kit/") or mode == "private")


if __name__ == "__main__":
    unittest.main()
