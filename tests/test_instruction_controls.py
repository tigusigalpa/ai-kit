"""Independent model advice/instruction profiles, compatibility and native-setting boundaries."""
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
import context
import doctor
import install
import metrics
import orchestrate
import router


class InstructionControlsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aikit-controls-")
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve()

    def apply(self, **options):
        plan = install.build_plan(self.project, agents=["codex", "claude"], **options)
        self.assertFalse(plan["conflicts"])
        self.assertTrue(install.apply_plan(plan))
        return plan

    def test_four_combinations_keep_security_and_model_controls_independent(self):
        sizes = {}
        for switching in (True, False):
            for profile in ("full", "minimal"):
                with self.subTest(switching=switching, profile=profile):
                    plan = self.apply(model_switching_enabled=switching, instruction_profile=profile,
                                      extras=["orchestration", "uuid", "claude-github", "guards"])
                    controls = {"model_switching_enabled": switching, "instruction_profile": profile, "model_switching_exceptions": []}
                    self.assertEqual(plan["instruction_settings"], controls)
                    entry = (self.project / "AGENTS.md").read_text(encoding="utf-8")
                    sizes[profile] = len(entry)
                    self.assertLessEqual(len(entry.encode("utf-8")), 2500)
                    self.assertEqual("UPSTREAM.md" in entry, profile == "full")
                    for required in ("CORE.md", "settings.json", "ENGINEERING.md", "SECURITY.md",
                                     "CONTAINERS.md", "MCP.md", "docs/adr/", "UUID.md"):
                        self.assertIn(required, entry)
                    self.assertIn("CLAUDE-GITHUB.md", (self.project / "CLAUDE.md").read_text())
                    native = (self.project / ".codex/agents/aikit_worker.toml").read_text()
                    self.assertEqual("model = " in native, switching)
                    self.assertEqual("model_reasoning_effort = " in native, switching)
                    self.assertIn("Do not create/amend commits", (self.project / "ai-kit/CORE.md").read_text())
                    report = doctor.examine(self.project)
                    self.assertFalse(report["errors"], report["errors"])
                    self.assertEqual(report["instruction_settings"], controls)
                    self.assertIsNone(report["runtime"]["model"])
                    self.assertIsNone(report["runtime"]["reasoning_effort"])
                    self.assertEqual(report["runtime"]["status"], "unavailable")
                    selected = context.select_context(self.project, budget=1)
                    self.assertEqual(selected["instruction_settings"], controls)
                    self.assertTrue(selected["over_budget"])
                    self.assertIn("ai-kit/SECURITY.md", [f["path"] for f in selected["selected"]])
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(router.main(["route", "implement feature", "--project", str(self.project)]), 0)
                    recommendation = json.loads(output.getvalue())
                    self.assertEqual(recommendation["recommendations_enabled"], switching)
                    self.assertFalse(recommendation["execution_confirmed"])
                    if not switching:
                        self.assertIsNone(recommendation["model"])
                        self.assertIsNone(recommendation["effort"])
        self.assertLess(sizes["minimal"], sizes["full"])

    def test_missing_keys_retain_legacy_defaults_and_explicit_choices_persist(self):
        self.apply()
        path = self.project / "ai-kit/settings.json"
        settings = json.loads(path.read_text())
        for key in install.INSTRUCTION_DEFAULTS:
            settings.pop(key)
        path.write_text(json.dumps(settings), encoding="utf-8")
        self.assertEqual(install.load_instruction_settings(self.project), install.INSTRUCTION_DEFAULTS)
        self.apply()
        self.apply(model_switching_enabled=False, instruction_profile="minimal")
        self.assertEqual(self.apply()["instruction_settings"],
                         {"model_switching_enabled": False, "instruction_profile": "minimal", "model_switching_exceptions": []})

    def test_invalid_controls_are_refused_before_writes(self):
        for bad in ("false", 0, 1, None, [], {}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                install.instruction_settings({"model_switching_enabled": bad})
        for bad in (True, None, "economy", "Minimal", [], {}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                install.instruction_settings({"instruction_profile": bad})
        with self.assertRaises(ValueError):
            install.build_plan(self.project, instruction_profile="economy")
        self.assertEqual(list(self.project.iterdir()), [])

    def test_presets_and_team_visibility_do_not_reset_controls(self):
        self.apply(model_switching_enabled=False, instruction_profile="minimal")
        plan = self.apply(preset="strict", mode="team")
        self.assertEqual(plan["instruction_settings"],
                         {"model_switching_enabled": False, "instruction_profile": "minimal", "model_switching_exceptions": []})
        self.assertEqual(plan["mode"], "team")
        self.assertTrue((self.project / ".claude/settings.json").is_file())
        self.assertEqual(self.apply(preset="minimal")["instruction_settings"], plan["instruction_settings"])

    def test_custom_native_model_effort_and_project_constraints_are_preserved(self):
        self.apply(extras=["orchestration"])
        helper = self.project / ".codex/agents/aikit_worker.toml"
        native = self.project / ".codex/config.toml"
        native.write_bytes(b'model = "user-selected-astra"\nmodel_reasoning_effort = "xhigh"\n')
        helper.write_bytes(helper.read_bytes() + b"# Owner customization\n")
        owned = self.project / "PROJECT_CONTEXT.md"
        owned.write_bytes(owned.read_bytes() + b"\nMandatory architecture: keep the public contract.\n")
        expected = {p: p.read_bytes() for p in (helper, native, owned)}
        plan = install.build_plan(self.project, model_switching_enabled=False, instruction_profile="minimal")
        self.assertIn(".codex/agents/aikit_worker.toml", plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        for path, data in expected.items():
            self.assertEqual(path.read_bytes(), data)

    def test_disabled_route_skips_catalogues_effort_overrides_and_cwd_bypass(self):
        self.apply(model_switching_enabled=False)
        with patch("pathlib.Path.cwd", return_value=self.project), patch.object(
                router, "_selection_and_providers", side_effect=AssertionError("must not route")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(router.main(["route", "save tokens", "--model", "cheap", "--effort", "low"]), 0)
        report = json.loads(output.getvalue())
        self.assertIsNone(report["model"])
        self.assertIsNone(report["effort"])
        with patch.object(router, "route_result", side_effect=AssertionError("must not classify")):
            self.assertFalse(adaptive.recommend_route("task", {}, {},
                instruction_settings={"model_switching_enabled": False})["resolved"])

    def test_disabled_configure_preserves_existing_aider_model(self):
        plan = install.build_plan(self.project, agents=["aider"], model_switching_enabled=False)
        self.assertTrue(install.apply_plan(plan))
        path = self.project / ".aider.conf.yml"
        path.write_bytes(b'model: user-selected\n')
        plan = router.configure_plan(self.project)
        self.assertNotIn(".aider.conf.yml", plan["actions"])
        self.assertTrue(router.apply_configure(plan))
        self.assertEqual(path.read_bytes(), b'model: user-selected\n')
        resolved = json.loads((self.project / "ai-kit/router/resolved.json").read_text())
        self.assertEqual(resolved["roles"], {})
        self.assertTrue(any(".aider.conf.yml" in item for item in doctor.examine(self.project)["warnings"]))

    def test_minimal_keeps_nested_architecture_and_checks_above_budget(self):
        self.apply(instruction_profile="minimal")
        nested = self.project / "src"
        nested.mkdir()
        (nested / "AGENTS.md").write_text("Mandatory: preserve API compatibility.\n", encoding="utf-8")
        adr = self.project / "docs/adr/0001-boundary.md"
        adr.write_text("# Boundary\nNo production data in tests.\n", encoding="utf-8")
        report = context.select_context(self.project, path="src", budget=1)
        selected = {item["path"] for item in report["selected"]}
        self.assertTrue({"src/AGENTS.md", "docs/adr/0001-boundary.md", "ai-kit/ENGINEERING.md",
                         "ai-kit/SECURITY.md", "ai-kit/CORE.md"} <= selected)

    def test_external_executor_uses_only_explicit_model_and_propagates_controls(self):
        config = dict(orchestrate.DEFAULTS, model="provider/explicit-model")
        path = self.project / "task.json"
        path.write_text(json.dumps({"schema": 1, "id": "example", "instruction": "Analyze text", "input_files": []}))
        self.apply(model_switching_enabled=False, instruction_profile="minimal")
        _, payload, _ = orchestrate.prepare(self.project, "task.json", config)
        self.assertEqual(payload["model"], "provider/explicit-model")
        self.assertNotIn("reasoning_effort", payload)
        self.assertFalse(payload["provider"]["allow_fallbacks"])
        system = payload["messages"][0]["content"]
        self.assertIn("Do not recommend changing models", system)
        self.assertIn("mandatory project/architecture", system)
        self.assertIn("untrusted data", system)

    def test_disabled_metrics_proposal_has_no_candidates_or_writes(self):
        self.apply(model_switching_enabled=False)
        with patch("learning.candidates", side_effect=AssertionError("must not recommend")):
            with contextlib.redirect_stderr(io.StringIO()) as output:
                code = metrics.main(["propose", str(self.project), "--stack", "PYTHON",
                                     "--task-class", "implement", "--level", "2", "--apply"])
        self.assertEqual(code, 1)
        self.assertIn("recommendations are disabled", output.getvalue())
        self.assertFalse((self.project / "ai-kit/.metrics/proposals").exists())

    def test_controls_loader_refuses_linked_settings(self):
        self.apply()
        original = install.is_link
        with patch.object(install, "is_link", side_effect=lambda p:
                          Path(p) == self.project / "ai-kit/settings.json" or original(p)):
            with self.assertRaises(ValueError):
                install.load_instruction_settings(self.project)


if __name__ == "__main__":
    unittest.main()
