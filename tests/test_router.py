"""Exercise the offline model router (route and configure) and the agent registry."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install
import router


def providers():
    return router.load_providers(router.ROOT / "template" / "ai-kit" / "router" / "providers")


def selection(**overrides):
    base = {"schema": 1, "default_provider": None,
            "roles": {"cheap": None, "work": None, "escalation": None},
            "local_models": {"cheap": None, "work": None, "escalation": None}}
    base.update(overrides)
    return base


class RouteTests(unittest.TestCase):
    def test_classify_levels(self):
        self.assertEqual(router.classify("classify these tickets")["level"], 0)
        self.assertEqual(router.classify("rename the variable")["level"], 1)
        self.assertEqual(router.classify("implement the feature")["level"], 2)
        self.assertEqual(router.classify("debug the concurrency race")["level"], 3)
        self.assertEqual(router.classify("design a distributed consensus layer")["level"], 4)
        self.assertEqual(router.classify("prove a novel algorithm")["level"], 5)

    def test_route_resolves_model_from_default_provider(self):
        result = router.route_result("implement the feature", selection(default_provider="openai"),
                                     providers())
        self.assertEqual(result["level"], 2)
        self.assertEqual(result["role"], "work")
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["model"], "gpt-6.1-sol")

    def test_route_resolves_local_model(self):
        selection_data = selection(roles={"work": "local"},
                                   local_models={"work": "llama3.3:70b"})
        result = router.route_result("implement the feature", selection_data, providers())
        self.assertEqual(result["provider"], "local")
        self.assertEqual(result["model"], "llama3.3:70b")

    def test_route_skips_pending_provider(self):
        result = router.route_result("implement the feature", selection(default_provider="gemini"),
                                     providers())
        self.assertIsNone(result["model"])
        self.assertEqual(result["provider"], "gemini")

    def test_route_explicit_overrides(self):
        result = router.route_result("anything", selection(default_provider="openai"), providers(),
                                     level=5, role="escalation", effort="max")
        self.assertEqual(result["level"], 5)
        self.assertEqual(result["role"], "escalation")
        self.assertEqual(result["effort"], "max")
        self.assertEqual(result["model"], "gpt-6-astra")

    def test_route_unknown_provider_is_refused(self):
        with self.assertRaises(ValueError):
            router.route_result("anything", selection(default_provider="missing"), providers())

    def test_selection_validation_rejects_bad_shapes(self):
        for bad in [{"schema": 99, "roles": {}, "local_models": {}},
                    {"schema": 1, "roles": {"work": 7}, "local_models": {}},
                    {"schema": 1, "roles": {}, "local_models": {"work": 7}},
                    {"schema": 1, "roles": {"work": {"unknown": "x"}}, "local_models": {}}]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                router.validate_selection(bad)

    def test_route_cli_prints_recommendation(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(router.main(["route", "implement the feature"]), 0)
        self.assertIn('"level": 2', output.getvalue())


class ConfigureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-router-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def apply(self, **options):
        plan = install.build_plan(self.target, root=self.source, **options)
        self.assertTrue(install.apply_plan(plan))
        return plan

    def write(self, path, data):
        destination = self.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    def test_configure_preview_writes_nothing(self):
        self.apply(agents=["codex", "aider"])
        self.write("ai-kit/router/selection.json",
                   (json.dumps(selection(default_provider="openai")) + "\n").encode())
        plan = router.configure_plan(self.target)
        self.assertTrue(plan["actions"])
        self.assertFalse((self.target / "ai-kit/router/resolved.json").exists())

    def test_configure_apply_writes_resolved_and_aider(self):
        self.apply(agents=["codex", "aider"])
        self.write("ai-kit/router/selection.json",
                   (json.dumps(selection(default_provider="openai")) + "\n").encode())
        plan = router.configure_plan(self.target)
        self.assertTrue(router.apply_configure(plan))
        resolved = json.loads((self.target / "ai-kit/router/resolved.json").read_text())
        self.assertEqual(resolved["schema"], 1)
        self.assertEqual(resolved["roles"]["work"]["model"], "gpt-6.1-sol")
        aider = (self.target / ".aider.conf.yml").read_text(encoding="utf-8")
        self.assertIn('model: "gpt-6.1-sol"', aider)
        self.assertIn('weak_model: "gpt-6-luna"', aider)

    def test_configure_skips_aider_without_resolution(self):
        self.apply(agents=["codex", "aider"])
        # default selection has no provider, so no model resolves
        plan = router.configure_plan(self.target)
        self.assertTrue(plan["actions"])
        self.assertNotIn(".aider.conf.yml", plan["actions"])

    def test_configure_conflict_preserves_existing_aider_config(self):
        self.apply(agents=["codex", "aider"])
        self.write("ai-kit/router/selection.json",
                   (json.dumps(selection(default_provider="openai")) + "\n").encode())
        self.write(".aider.conf.yml", b"model: my-custom-model\n")
        plan = router.configure_plan(self.target)
        self.assertIn(".aider.conf.yml", plan["conflicts"])
        self.assertFalse(router.apply_configure(plan))
        self.assertEqual((self.target / ".aider.conf.yml").read_text(encoding="utf-8"),
                         "model: my-custom-model\n")

    def test_configure_unknown_provider_is_refused(self):
        self.apply()
        self.write("ai-kit/router/selection.json",
                   (json.dumps(selection(default_provider="missing")) + "\n").encode())
        with self.assertRaises(ValueError):
            router.configure_plan(self.target)

    def test_route_project_uses_installed_selection(self):
        self.apply()
        self.write("ai-kit/router/selection.json",
                   (json.dumps(selection(default_provider="openai")) + "\n").encode())
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(router.main(["route", "implement the feature",
                                          "--project", str(self.target)]), 0)
        self.assertIn('"model": "gpt-6.1-sol"', output.getvalue())


class RegistryTests(unittest.TestCase):
    def test_registry_names_match_expected(self):
        registry = install.load_agent_registry()
        self.assertEqual(registry["names"],
                         {"codex", "claude", "kimi", "manus", "copilot", "cursor", "aider",
                          "gemini", "windsurf", "cline", "roo"})
        self.assertEqual(registry["entries"]["CLAUDE.md"], "claude")
        self.assertEqual(registry["skills_copies"]["claude"], ".claude/skills/")
        self.assertEqual(registry["optional"]["aider"], [("CONVENTIONS.md", "CONVENTIONS.md")])

    def test_registry_rejects_duplicate_entry_ownership(self):
        temp = tempfile.TemporaryDirectory(prefix="ai-kit-registry-")
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "reference"
        shutil.copytree(install.ROOT, root, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        path = root / "integrations/agents.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["agents"]["gemini"]["entries"] = ["CLAUDE.md"]
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            install.load_agent_registry(root)


if __name__ == "__main__":
    unittest.main()
