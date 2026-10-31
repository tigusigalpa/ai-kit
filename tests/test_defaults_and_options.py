"""Cover new-project defaults, portable identifiers, human Git identity and Devin migration."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adapters
import doctor
import install


class DefaultsAndOptionsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ai-kit-defaults-")
        self.addCleanup(temporary.cleanup)
        self.target = Path(temporary.name).resolve() / "application with spaces"

    def write(self, relative, value):
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def read(self, relative):
        return (self.target / relative).read_text(encoding="utf-8")

    def settings(self):
        return json.loads(self.read("ai-kit/settings.json"))

    def apply(self, **options):
        plan = install.build_plan(self.target, **options)
        self.assertFalse(plan["conflicts"], sorted(plan["conflicts"]))
        self.assertTrue(install.apply_plan(plan))
        return plan

    def test_fresh_english_and_saved_russian_upgrade(self):
        self.apply()
        self.assertEqual(self.settings()["chat_language"], "English")
        self.apply(language="Russian")
        self.apply(extras=["uuid"])
        self.assertEqual(self.settings()["chat_language"], "Russian")
        self.apply(language="English")
        self.assertEqual(self.settings()["chat_language"], "English")
        self.assertFalse(install.build_plan(self.target)["actions"])

    def test_blank_interactive_language_is_english(self):
        answers = iter(["", "", "", "", "", "", "y"])
        with redirect_stdout(io.StringIO()):
            selected = install.interactive_selections(lambda _: next(answers),
                                                      agents_available={"codex"}, facts={"modules": []})
        self.assertEqual(selected["language"], "English")

    def test_uuid_absent_from_every_preset_and_convention_by_default(self):
        for preset in install.PRESETS:
            for conventions in ("owner", "standard"):
                with self.subTest(preset=preset, conventions=conventions):
                    plan = install.build_plan(self.target, preset=preset, conventions=conventions)
                    settings = json.loads(plan["actions"]["ai-kit/settings.json"]["data"])
                    self.assertFalse(settings["uuid"])
                    self.assertNotIn("ai-kit/UUID.md", plan["actions"])
                    self.assertNotIn(b"ai-kit/UUID.md", plan["actions"]["AGENTS.md"]["data"])

    def test_uuid_is_cross_stack_persistent_and_does_not_change_application_code(self):
        manifests = {"package.json": '{"dependencies":{"express":"^5.0.0"}}',
                     "go/go.mod": "module example.test/api\n\ngo 1.23\n",
                     "python/pyproject.toml": '[project]\nname = "worker"\n',
                     "php/composer.json": '{"require":{"php":"^8.3"}}'}
        for relative, value in manifests.items():
            self.write(relative, value)
        self.apply(conventions="standard", extras=["uuid"])
        self.assertTrue(self.settings()["uuid"])
        self.assertTrue((self.target / "ai-kit/UUID.md").is_file())
        self.assertIn("ai-kit/UUID.md", self.read("AGENTS.md"))
        for relative, value in manifests.items():
            self.assertEqual(self.read(relative), value)
        self.apply(preset="minimal")
        self.assertTrue(self.settings()["uuid"])
        self.assertFalse(install.build_plan(self.target)["actions"])

    def test_deselection_preserves_uuid_files_and_project_owned_documents(self):
        self.apply(extras=["uuid"])
        self.write("PROJECT_CONTEXT.md", "# Application\n\nExisting UUID API contract.\n")
        settings = self.settings()
        settings["uuid"] = False
        self.write("ai-kit/settings.json", json.dumps(settings))
        self.apply()
        self.assertNotIn("ai-kit/UUID.md", self.read("AGENTS.md"))
        self.assertTrue((self.target / "ai-kit/UUID.md").is_file())
        self.assertIn("Existing UUID API contract.", self.read("PROJECT_CONTEXT.md"))

    def test_adapted_uuid_entry_is_a_conflict_when_deselecting(self):
        self.apply(extras=["uuid"])
        self.write("AGENTS.md", self.read("AGENTS.md") + "\nProject-specific rule.\n")
        settings = self.settings()
        settings["uuid"] = False
        self.write("ai-kit/settings.json", json.dumps(settings))
        plan = install.build_plan(self.target)
        self.assertIn("AGENTS.md", plan["conflicts"])
        self.assertIn("Project-specific rule.", self.read("AGENTS.md"))

    def test_node_server_and_browser_profiles_are_distinct(self):
        self.write("server/package.json", json.dumps({"engines": {"node": ">=22"},
                   "dependencies": {"express": "^5.0.0"}, "scripts": {"test": "node --test"}}))
        self.write("web/package.json", '{"devDependencies":{"vite":"^7.0.0"}}')
        facts = {module["path"]: module for module in install.detect_facts(self.target)["modules"]}
        self.assertEqual(facts["/server/"]["profiles"], ["JAVASCRIPT"])
        self.assertEqual(facts["/server/"]["version"], ">=22")
        self.assertEqual(facts["/server/"]["commands"]["test"], "npm test")
        self.assertEqual(facts["/web/"]["profiles"], ["FRONTEND", "JAVASCRIPT"])
        self.apply(agents=["claude", "devin"], extras=["scoped-rules"])
        for relative in (".claude/skills/javascript-work/SKILL.md", "ai-kit/stacks/JAVASCRIPT.md",
                         ".devin/rules/ai-kit-server.md"):
            self.assertTrue((self.target / relative).is_file(), relative)

    def test_devin_rules_and_explicit_legacy_retirement(self):
        self.write("package.json", "{}")
        self.apply(agents=["codex", "windsurf"], extras=["scoped-rules"])
        legacy = self.read(".windsurf/rules/ai-kit.md")
        plan = self.apply(agents=["codex", "devin", "windsurf"])
        self.assertIn("trigger: always_on", self.read(".devin/rules/ai-kit.md"))
        self.assertEqual(self.read(".windsurf/rules/ai-kit.md"), legacy)
        self.assertTrue(any("legacy .windsurf" in warning for warning in plan["warnings"]))
        retirement = adapters.retirement_plan(self.target, "windsurf")
        self.assertFalse(retirement["conflicts"])
        self.assertTrue(adapters.apply_retirement(retirement))
        self.assertFalse((self.target / ".windsurf/rules/ai-kit.md").exists())
        self.assertTrue((self.target / ".devin/rules/ai-kit.md").is_file())
        self.assertFalse(install.build_plan(self.target)["actions"])

    def test_modified_legacy_rule_is_preserved_on_devin_migration(self):
        self.apply(agents=["codex", "windsurf"])
        self.write(".windsurf/rules/ai-kit.md", "# Custom legacy rule\n")
        self.apply(agents=["codex", "devin", "windsurf"])
        plan = adapters.retirement_plan(self.target, "windsurf")
        self.assertIn(".windsurf/rules/ai-kit.md", plan["conflicts"])
        self.assertFalse(adapters.apply_retirement(plan))
        self.assertEqual(self.read(".windsurf/rules/ai-kit.md"), "# Custom legacy rule\n")

    def test_claude_default_suppresses_credit_and_preserves_other_settings(self):
        original = {"model": "human-choice", "attribution": {"pr": "Human team"},
                    "permissions": {"ask": ["Bash(custom)"]}}
        self.write(".claude/settings.local.json", json.dumps(original))
        self.apply(agents=["claude"])
        settings = json.loads(self.read(".claude/settings.local.json"))
        self.assertEqual(settings, {**original, "attribution": {"pr": "Human team", "commit": ""}})
        self.assertFalse((self.target / "ai-kit/CLAUDE-GITHUB.md").exists())
        self.assertFalse(install.build_plan(self.target)["actions"])

    def test_custom_attribution_is_a_reviewable_conflict(self):
        original = '{"attribution":{"commit":"Human credit"},"model":"human-choice"}\n'
        self.write(".claude/settings.local.json", original)
        plan = install.build_plan(self.target, agents=["claude"], extras=["claude-github"])
        self.assertIn(".claude/settings.local.json", plan["conflicts"])
        self.assertEqual(self.read(".claude/settings.local.json"), original)
        self.assertIn(b'"commit": ""', plan["conflicts"][".claude/settings.local.json"])

    def test_github_option_persists_without_changing_git_configuration(self):
        original = '[user]\n\tname = Existing Human\n\temail = human@example.test\n'
        self.write(".git/config", original)
        self.apply(agents=["claude"], extras=["claude-github"])
        self.assertTrue(self.settings()["claude_github"])
        self.assertIn("ai-kit/CLAUDE-GITHUB.md", self.read("CLAUDE.md"))
        self.assertEqual(self.read(".git/config"), original)
        self.apply(preset="minimal", mode="team")
        self.assertEqual(json.loads(self.read(".claude/settings.json"))["attribution"]["commit"], "")
        self.assertNotIn("attribution", json.loads(self.read(".claude/settings.local.json")))
        self.assertTrue(self.settings()["claude_github"])
        self.assertEqual(self.read(".git/config"), original)
        self.assertFalse(install.build_plan(self.target)["actions"])

    def test_github_option_without_claude_reports_missing_wiring(self):
        plan = self.apply(extras=["claude-github"])
        self.assertTrue(any("requires --agent claude" in warning for warning in plan["warnings"]))
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertFalse((self.target / ".claude/settings.local.json").exists())

    def test_doctor_reports_and_repairs_missing_native_attribution(self):
        self.apply(agents=["claude"])
        self.write(".claude/settings.local.json", "{}")
        result = doctor.examine(self.target)
        self.assertTrue(any("attribution.commit" in warning for warning in result["warnings"]))
        self.apply()
        self.assertEqual(json.loads(self.read(".claude/settings.local.json"))["attribution"]["commit"], "")

    def test_new_option_settings_require_booleans(self):
        settings = json.loads((install.ROOT / "template/ai-kit/settings.json").read_text(encoding="utf-8"))
        for field in ("uuid", "claude_github"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                install.validate_settings({**settings, field: "true"})


if __name__ == "__main__":
    unittest.main()
