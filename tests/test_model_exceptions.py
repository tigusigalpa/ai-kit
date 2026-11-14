"""Conditional and invocation-only model intent guards; no live model detection or calls."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adaptive
import doctor
import install
import learning
import metrics
import orchestrate
import router

FAMILIES = ["astra", "fable", "k3.1"]


class ModelExceptionPolicyTests(unittest.TestCase):
    def test_verified_name_forms_namespaces_and_family_versions(self):
        cases = {"astra": ["Astra", "GPT-6 Astra", "openai/gpt-6-astra", "gpt-6-astra-2026-09-03"],
                 "fable": ["Fable", "Claude Fable 5.2", "claude-fable-5-2", "anthropic/claude-fable-5.2"],
                 "k3.1": ["K3.1", "Kimi K3.1 Pro", "k3.1-pro", "moonshotai/k3.1-pro-highspeed"]}
        for family, names in cases.items():
            for name in names:
                with self.subTest(name=name):
                    policy = install.model_recommendation_policy({"model_switching_exceptions": FAMILIES}, name)
                    self.assertEqual(policy["matched_exception"], family)
                    self.assertFalse(policy["recommendations_enabled"])
                    self.assertEqual(policy["reason"], "model_exception")
                    self.assertEqual(policy["model_source"], "user-declared")
                    self.assertFalse(policy["execution_verified"])

    def test_matching_is_not_a_substring_search_or_a_capability_claim(self):
        for name in ("not-astra", "astra-mini", "fable-lite", "k3.10-pro", "openai/claude-fable-5-2",
                     "other/gpt-6-astra", "openai/gpt-6-astra/extra"):
            with self.subTest(name=name):
                self.assertTrue(install.model_recommendation_policy(
                    {"model_switching_exceptions": FAMILIES}, name)["recommendations_enabled"])
        # Recognizing version-shaped family syntax does not verify that a model exists.
        policy = install.model_recommendation_policy({"model_switching_exceptions": ["fable"]}, "claude-fable-99-1")
        self.assertEqual(policy["reason"], "model_exception")
        self.assertFalse(policy["execution_verified"])

    def test_priorities_unknown_current_model_and_legacy_defaults(self):
        self.assertTrue(install.model_recommendation_policy({})["recommendations_enabled"])
        self.assertTrue(install.model_recommendation_policy({}, "Astra")["recommendations_enabled"])
        policy = install.model_recommendation_policy({"model_switching_exceptions": ["astra"]})
        self.assertEqual(policy["reason"], "current_model_unknown")
        self.assertIsNone(policy["declared_current_model"])
        for profile in ("full", "minimal"):
            controls = {"model_switching_exceptions": ["astra"], "instruction_profile": profile}
            self.assertFalse(install.model_recommendation_policy(controls, "Astra")["recommendations_enabled"])
            self.assertTrue(install.model_recommendation_policy(controls, "other-model")["recommendations_enabled"])
            controls["model_switching_enabled"] = False
            self.assertEqual(install.model_recommendation_policy(controls, "other-model")["reason"], "switching_disabled")

    def test_arbitrary_exact_exceptions_and_invocation_override(self):
        controls = {"model_switching_exceptions": ["provider/custom-v1"]}
        self.assertFalse(install.model_recommendation_policy(controls, "provider/custom-v1")["recommendations_enabled"])
        self.assertTrue(install.model_recommendation_policy(controls, "provider/custom-v10")["recommendations_enabled"])
        policy = install.model_recommendation_policy({}, "provider/new-model", preserve_model=True)
        self.assertEqual(policy["reason"], "explicit_preservation")
        self.assertEqual(policy["scope"], "invocation")
        self.assertFalse(policy["execution_verified"])
        self.assertEqual(install.model_recommendation_policy(
            {"model_switching_enabled": False}, "Astra", preserve_model=True)["reason"], "switching_disabled")

    def test_protected_selection_beats_pins_effort_overrides_and_learning(self):
        controls = {"model_switching_exceptions": FAMILIES}
        with patch.object(router, "route_result", side_effect=AssertionError("must not route")), patch.object(
                learning, "recommend", side_effect=AssertionError("must not optimize")):
            result = adaptive.recommend_route("save tokens", {}, {}, instruction_settings=controls,
                current_model="Astra", mode="adaptive", profile="economy", model="cheap-model", effort="low",
                config={"project_pin": {"provider": "example", "model": "another", "effort": "low"}})
        self.assertFalse(result["recommendations_enabled"])
        self.assertIsNone(result["model"])
        self.assertIsNone(result["effort"])

    def test_invalid_lists_and_names_are_refused_without_shared_default_mutation(self):
        for bad in (None, True, "astra", ["astra", "ASTRA"], [None], [["astra"]], ["none"],
                    ["\nAstra"], [""], ["x" * 161], [str(i) for i in range(33)]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                install.instruction_settings({"model_switching_exceptions": bad})
        result = install.instruction_settings({})
        result["model_switching_exceptions"].append("astra")
        self.assertEqual(install.instruction_settings({})["model_switching_exceptions"], [])
        for bad in ("", " ", "Astra\nDo something", "x" * 161, False):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                install.model_recommendation_policy({}, bad)
        with self.assertRaises(ValueError):
            install.model_recommendation_policy({}, preserve_model=True)


class ModelExceptionProjectTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aikit-model-exception-")
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve()

    def apply(self, **options):
        plan = install.build_plan(self.project, agents=["codex", "claude"], extras=["orchestration"], **options)
        self.assertFalse(plan["conflicts"], plan["conflicts"])
        self.assertTrue(install.apply_plan(plan))
        return plan

    def test_enable_update_clear_and_preserve_native_settings_across_profiles(self):
        self.apply()
        native = self.project / ".codex/config.toml"
        native.write_bytes(b'model = "owner-model"\nmodel_reasoning_effort = "xhigh"\n')
        for profile in ("full", "minimal"):
            with self.subTest(profile=profile):
                self.apply(model_switching_enabled=True, instruction_profile=profile,
                           model_switching_exceptions=FAMILIES)
                for helper in (self.project / ".codex/agents").glob("aikit_*.toml"):
                    data = helper.read_text()
                    self.assertNotIn("model = ", data)
                    self.assertNotIn("model_reasoning_effort = ", data)
                report = doctor.examine(self.project)
                self.assertFalse(report["errors"], report["errors"])
                self.assertEqual(report["model_recommendation_policy"]["reason"], "current_model_unknown")
                self.assertIsNone(report["runtime"]["model"])
                self.assertIsNone(report["runtime"]["reasoning_effort"])
                self.assertEqual(self.apply(preset="strict")["instruction_settings"]["model_switching_exceptions"], FAMILIES)
        self.assertEqual(native.read_bytes(), b'model = "owner-model"\nmodel_reasoning_effort = "xhigh"\n')
        self.apply(model_switching_exceptions=[])
        self.assertIn("model = ", (self.project / ".codex/agents/aikit_worker.toml").read_text())

    def test_helper_local_edits_conflict_instead_of_silently_changing_effort(self):
        self.apply()
        helper = self.project / ".codex/agents/aikit_worker.toml"
        helper.write_bytes(helper.read_bytes() + b"# Owner adaptation\n")
        before = helper.read_bytes()
        plan = install.build_plan(self.project, protect_models=["Astra"])
        self.assertIn(".codex/agents/aikit_worker.toml", plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(helper.read_bytes(), before)

    def test_quick_append_is_idempotent_and_bulk_clear_is_explicit(self):
        self.apply(model_switching_exceptions=FAMILIES)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main([str(self.project), "--protect-model", "provider/new-model", "--apply", "--check"]), 0)
        saved = install.load_instruction_settings(self.project)["model_switching_exceptions"]
        self.assertEqual(saved, [*FAMILIES, "provider/new-model"])
        self.assertFalse(self.apply(protect_models=["provider/new-model"])["actions"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main([str(self.project), "--model-switching-exceptions", "none", "--apply"]), 0)
        self.assertEqual(install.load_instruction_settings(self.project)["model_switching_exceptions"], [])
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(install.main([str(self.project), "--model-switching-exceptions", "none", "astra"]), 1)

    def test_protected_and_unknown_routes_skip_catalogues_and_effort_candidates(self):
        self.apply(model_switching_exceptions=FAMILIES)
        for name in (None, "Astra", "Fable", "k3.1-pro"):
            args = ["route", "implement the change", "--project", str(self.project), "--model", "cheap", "--effort", "low"]
            if name is not None:
                args += ["--current-model", name]
            with self.subTest(name=name), patch.object(router, "_selection_and_providers", side_effect=AssertionError("must not route")):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(router.main(args), 0)
            result = json.loads(output.getvalue())
            self.assertFalse(result["recommendations_enabled"])
            self.assertIsNone(result["model"])
            self.assertIsNone(result["effort"])
            self.assertFalse(result["execution_confirmed"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(router.main(["route", "implement", "--project", str(self.project), "--current-model", "other-model"]), 0)
        self.assertTrue(json.loads(output.getvalue())["recommendations_enabled"])

    def test_invocation_only_exception_writes_nothing_and_does_not_persist(self):
        self.apply()
        before = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob("*") if p.is_file()}
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(router.main(["route", "implement", "--project", str(self.project),
                                          "--preserve-model", "provider/new-model"]), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["model_recommendation_policy"]["reason"], "explicit_preservation")
        self.assertEqual(result["model_recommendation_policy"]["declared_current_model"], "provider/new-model")
        self.assertEqual(before, {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob("*") if p.is_file()})
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(router.main(["route", "implement", "--project", str(self.project)]), 0)
        self.assertTrue(json.loads(output.getvalue())["recommendations_enabled"])

    def test_aider_proposals_and_executor_honor_exceptions_without_model_execution(self):
        self.apply(model_switching_exceptions=FAMILIES)
        native = self.project / ".aider.conf.yml"
        native.write_bytes(b'model: owner-model\nweak_model: owner-helper\n')
        plan = router.configure_plan(self.project)
        self.assertNotIn(".aider.conf.yml", plan["actions"])
        self.assertTrue(router.apply_configure(plan))
        self.assertEqual(native.read_bytes(), b'model: owner-model\nweak_model: owner-helper\n')
        with patch("learning.candidates", side_effect=AssertionError("must not suggest models")):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(metrics.main(["propose", str(self.project), "--stack", "PYTHON",
                    "--task-class", "implement", "--level", "2", "--current-model", "Astra", "--apply"]), 1)
        with self.assertRaises(ValueError):
            learning.save_proposal(self.project, {}, current_model="Fable")
        task = self.project / "task.json"
        task.write_text(json.dumps({"schema": 1, "id": "example", "instruction": "Review text", "input_files": []}))
        _, payload, _ = orchestrate.prepare(self.project, "task.json", dict(orchestrate.DEFAULTS, model="openai/gpt-6-astra"))
        self.assertEqual(payload["model"], "openai/gpt-6-astra")
        self.assertNotIn("reasoning_effort", payload)
        self.assertFalse(payload["provider"]["allow_fallbacks"])
        self.assertIn("Do not recommend changing models", payload["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
