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
    def test_ladder_matches_canonical_policy(self):
        policy = (router.ROOT / "template/ai-kit/router/POLICY.md").read_text(encoding="utf-8")
        rows = [line.split("|")[3].strip() for line in policy.splitlines()
                if line.startswith("| ") and line.split("|")[1].strip().isdigit()]
        expected = ["cheap / none if supported", "cheap / low", "work / medium", "work / high",
                    "work / xhigh", "work / max", "escalation / effort selected separately"]
        self.assertEqual(rows, expected)
        self.assertEqual(list(router.LEVEL_MAP.values()),
                         [("cheap", "none"), ("cheap", "low"), ("work", "medium"),
                          ("work", "high"), ("work", "xhigh"), ("work", "max"), ("escalation", None)])

    def test_operation_risk_and_word_boundaries(self):
        cases = {"fix typo in research.md": 1, "add stack trace logs": 2,
                 "implement a parser": 2, "parse payments": 4,
                 "classify the authentication logs": 4,
                 "simple distributed consensus fix": 4, "rename `deadlock` to `lock`": 1,
                 "fix typo in architecture.yaml": 1, "add logging to debug.rs": 2,
                 "\u043f\u0435\u0440\u0435\u0438\u043c\u0435\u043d\u0443\u0439 \u043f\u0435\u0440\u0435\u043c\u0435\u043d\u043d\u0443\u044e": 1, "\u0438\u0441\u043f\u0440\u0430\u0432\u044c \u043e\u043f\u0435\u0447\u0430\u0442\u043a\u0443 \u0432 research.md": 1,
                 "\u0434\u043e\u0431\u0430\u0432\u044c \u043d\u043e\u0432\u044b\u0439 \u0444\u0438\u043b\u044c\u0442\u0440": 2, "\u043e\u0442\u043b\u0430\u0434\u044c \u0432\u0437\u0430\u0438\u043c\u043d\u0443\u044e \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0443": 3,
                 "\u0441\u043f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u0443\u0439 \u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u0451\u043d\u043d\u0443\u044e \u0440\u0435\u043f\u043b\u0438\u043a\u0430\u0446\u0438\u044e": 4, "\u0440\u0430\u0437\u0431\u0435\u0440\u0438 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044e": 4,
                 "\u0434\u043e\u043a\u0430\u0436\u0438 \u0442\u0435\u043e\u0440\u0435\u043c\u0443": 5, "\u0438\u0437\u0432\u043b\u0435\u043a\u0438 \u043c\u0435\u0442\u043a\u0438 \u0438\u0437 \u0441\u043f\u0438\u0441\u043a\u0430": 0,
                 "\u0434\u043e\u0431\u0430\u0432\u044c \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0443 \u043f\u043b\u0430\u0442\u0435\u0436\u0435\u0439": 4}
        for task, expected in cases.items():
            with self.subTest(task=task):
                self.assertEqual(router.classify_level(task), expected)

    def test_structured_evidence_and_manual_level(self):
        result = router.route_result("unknown", selection(), providers(), operation="extract",
                                     risks=("payments",), components=3)
        self.assertEqual(result["level"], 4)
        self.assertIn("explicit risk: payments", result["signals"])
        self.assertEqual(router.classify_task("unknown", components=3)["level"], 3)
        result = router.route_result("payment fix", selection(), providers(), level=1)
        self.assertEqual(result["level"], 1)
        self.assertEqual(result["level_source"], "explicit")
        for kwargs in ({"operation": "missing"}, {"risks": ("missing",)},
                       {"components": 0}, {"components": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                router.classify_task("unknown", **kwargs)

    def test_automatic_routing_never_claims_escalation(self):
        for task in ("formal proof", "debug deadlock", "security audit"):
            result = router.route_result(task, selection(default_provider="openai"), providers())
            self.assertNotEqual(result["level"], 6)
            self.assertNotEqual(result["role"], "escalation")
        research = router.route_result("formal proof", selection(default_provider="openai"), providers())
        self.assertEqual((research["role"], research["effort"]), ("work", "max"))
        escalation = router.route_result("diagnosed shortfall", selection(default_provider="openai"),
                                         providers(), level=6)
        self.assertEqual(escalation["effort"], "high")
        self.assertIsNone(escalation["recommended_effort"])

    def test_selection_effort_is_respected_and_cli_wins(self):
        settings = selection(default_provider="openai", roles={"work": {"effort": "low"}})
        chosen = router.route_result("implement feature", settings, providers())
        self.assertEqual(chosen["effort"], "low")
        self.assertEqual(chosen["effort_source"], "selection")
        chosen = router.route_result("implement feature", settings, providers(), effort="high")
        self.assertEqual(chosen["effort"], "high")
        self.assertEqual(settings["roles"]["work"]["effort"], "low")

    def test_effort_controls_require_model_capability(self):
        openai = router.route_result("classify tickets", selection(default_provider="openai"), providers())
        self.assertEqual(openai["effort"], "none")
        fallback = router.route_result("classify tickets", selection(default_provider="anthropic"), providers())
        self.assertEqual(fallback["recommended_effort"], "none")
        self.assertEqual(fallback["effort"], "low")
        self.assertTrue(fallback["adjustments"])
        for provider_id in ("kimi", "local", None, "gemini"):
            result = router.route_result("implement feature", selection(default_provider=provider_id,
                                         local_models={"work": "user-model"}), providers())
            self.assertIsNone(result["effort"])
        for kwargs in ({"provider": "anthropic", "effort": "none"},
                       {"provider": "openai", "model": "unknown-model", "effort": "high"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                router.route_result("classify tickets", selection(), providers(), **kwargs)

    def test_provider_and_model_overrides_do_not_mutate_selection(self):
        settings = selection(default_provider="openai")
        result = router.route_result("feature", settings, providers(), provider="kimi", model="custom-id")
        self.assertEqual((result["provider"], result["model"]), ("kimi", "custom-id"))
        self.assertIsNone(result["effort"])
        self.assertEqual(settings["default_provider"], "openai")
        self.assertIsNone(settings["roles"]["work"])
        settings["roles"]["work"] = {"provider": "openai", "model": "owner-openai-model"}
        result = router.route_result("feature", settings, providers(), provider="kimi")
        self.assertEqual(result["model"], providers()["kimi"]["roles"]["work"]["model"])
        self.assertEqual(settings["roles"]["work"]["model"], "owner-openai-model")

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

    def test_route_resolves_verified_gemini_model(self):
        result = router.route_result("implement the feature", selection(default_provider="gemini"),
                                     providers())
        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(result["model"], "gemini-3.8-flash")
        self.assertIsNone(result["effort"])

    def test_route_resolves_local_model(self):
        selection_data = selection(roles={"work": "local"},
                                   local_models={"work": "llama3.3:70b"})
        result = router.route_result("implement the feature", selection_data, providers())
        self.assertEqual(result["provider"], "local")
        self.assertEqual(result["model"], "llama3.3:70b")

    def test_route_skips_pending_provider(self):
        provs = providers()
        provs["experimental"] = {"tier": "cloud", "verification_status": "pending",
                                 "roles": {"cheap": {}, "work": {}, "escalation": {}}}
        result = router.route_result("implement the feature", selection(default_provider="experimental"),
                                     provs)
        self.assertIsNone(result["model"])
        self.assertEqual(result["provider"], "experimental")

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

    def test_providers_lists_status_and_sources(self):
        report = router.providers_report(providers())
        by_name = {item["provider"]: item for item in report["providers"]}
        self.assertEqual(set(by_name), {"openai", "anthropic", "kimi", "local", "gemini"})
        self.assertEqual(by_name["openai"]["status"], "verified")
        self.assertEqual(by_name["local"]["status"], "local")
        self.assertEqual(by_name["gemini"]["status"], "verified")
        self.assertTrue(by_name["openai"]["sources"])

    def test_providers_cli_prints_report(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(router.main(["providers"]), 0)
        self.assertIn('"provider": "gemini"', output.getvalue())

    def test_cli_structured_flags_and_invalid_effort(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = router.main(["route", "extract tickets", "--operation", "implement",
                                  "--risk", "payments", "--components", "2", "--provider", "openai"])
        self.assertEqual(status, 0)
        result = json.loads(output.getvalue())
        self.assertEqual((result["level"], result["effort"]), (4, "xhigh"))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(router.main(["route", "feature", "--provider", "openai", "--effort", "invalid"]), 1)


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
