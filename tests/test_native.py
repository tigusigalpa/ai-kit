"""Exercise generated client settings, scoped module rules, presets, and workflow skills."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor
import install

ALL_SCOPED = ["codex", "claude", "cursor", "copilot", "windsurf", "cline"]


class NativeConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-native-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project with spaces"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def plan(self, **options):
        return install.build_plan(self.target, root=self.source, **options)

    def apply(self, **options):
        plan = self.plan(**options)
        self.assertFalse(plan["conflicts"], plan["conflicts"])
        self.assertTrue(install.apply_plan(plan))
        return plan

    def write(self, path, data):
        destination = self.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(data, encoding="utf-8")

    def read_json(self, path):
        return json.loads((self.target / path).read_text(encoding="utf-8"))

    def laravel_and_go(self):
        self.write("web/composer.json", json.dumps({"require": {"php": "^8.3", "laravel/framework": "^12.0"}}))
        self.write("web/artisan", "#!/usr/bin/env php\n")
        self.write("api/go.mod", "module example.test/api\n\ngo 1.23\n")

    # Native settings (item 6)

    def test_private_native_settings_use_the_local_claude_file(self):
        self.laravel_and_go()
        self.apply(agents=["claude"], extras=["native-settings"])
        self.assertFalse((self.target / ".claude/settings.json").exists())
        settings = self.read_json(".claude/settings.local.json")
        self.assertIn("Bash(php artisan test *)", settings["permissions"]["allow"])
        self.assertIn("Bash(go test ./... *)", settings["permissions"]["allow"])
        deny = settings["permissions"]["deny"]
        for rule in ("Read(.env)", "Read(.env.*)", "Read(auth.json)", "Read(/web/storage/*.key)", "Read(/secrets/**)"):
            self.assertIn(rule, deny)
        # Gitignore negations stay after the rules they carve out of.
        self.assertGreater(deny.index("Read(!.env.example)"), deny.index("Read(.env.*)"))
        self.assertNotIn("Read(.pypirc)", deny)
        state = self.read_json("ai-kit/.install-state.json")
        self.assertEqual(sorted(state["managed_json"]), [".claude/settings.local.json"])
        self.assertFalse(self.plan()["actions"])

    def test_moodle_and_python_secrets_are_module_scoped(self):
        self.write("lms/config-dist.php", "<?php\n")
        self.write("lms/lib/moodlelib.php", "<?php\n")
        self.write("tools/pyproject.toml", '[project]\nname = "tools"\n')
        self.apply(agents=["claude"], extras=["native-settings"])
        deny = self.read_json(".claude/settings.local.json")["permissions"]["deny"]
        self.assertIn("Read(/lms/config.php)", deny)
        self.assertIn("Read(.pypirc)", deny)
        self.assertNotIn("Read(config.php)", deny)

    def test_team_mode_uses_shared_file_and_switching_moves_only_owned_entries(self):
        self.laravel_and_go()
        self.write(".claude/settings.local.json", json.dumps({"permissions": {"allow": ["Bash(make dev)"]}}))
        self.apply(agents=["claude"], extras=["native-settings", "guards"])
        self.assertIn("Bash(git push *)", self.read_json(".claude/settings.local.json")["permissions"]["ask"])
        self.apply(mode="team")
        local = self.read_json(".claude/settings.local.json")
        self.assertEqual(local, {"permissions": {"allow": ["Bash(make dev)"]}})
        shared = self.read_json(".claude/settings.json")
        self.assertIn("Bash(git push *)", shared["permissions"]["ask"])
        self.assertIn("Read(.env)", shared["permissions"]["deny"])
        state = self.read_json("ai-kit/.install-state.json")
        self.assertEqual(sorted(state["managed_json"]), [".claude/settings.json"])
        self.assertFalse(self.plan()["actions"])

    def test_previous_private_entries_in_shared_file_move_to_local_file(self):
        self.apply(agents=["claude"])
        hook = install.SESSION_START_COMMAND
        user_and_old = {"model": "user", "permissions": {"ask": ["Bash(git push *)"]},
                        "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": hook}]}]}}
        self.write(".claude/settings.json", json.dumps(user_and_old))
        state_path = self.target / "ai-kit/.install-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["managed_json"] = {".claude/settings.json": {"permissions.ask": ["Bash(git push *)"],
                                                           "hooks.SessionStart": [hook]}}
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.apply(extras=["guards", "session-start"])
        self.assertEqual(self.read_json(".claude/settings.json"), {"model": "user"})
        local = self.read_json(".claude/settings.local.json")
        self.assertIn("Bash(git push *)", local["permissions"]["ask"])
        self.assertEqual(local["hooks"]["SessionStart"][0]["hooks"][0]["command"], hook)

    def test_unsafe_recorded_commands_are_not_allowed(self):
        self.write("pkg/package.json", json.dumps({"scripts": {"test": "jest"}}))
        self.apply(agents=["claude"])
        project = self.read_json("ai-kit/project.json")
        project["modules"][0]["commands"] = {"test": "npm test && rm -rf /", "lint": "npm run lint",
                                             "build": "echo $HOME"}
        self.write("ai-kit/project.json", json.dumps(project))
        self.apply(extras=["native-settings"])
        allow = self.read_json(".claude/settings.local.json")["permissions"]["allow"]
        self.assertEqual(allow, ["Bash(npm run lint *)"])

    def test_project_json_facts_drive_generated_settings(self):
        self.laravel_and_go()
        self.apply(agents=["claude"], extras=["native-settings"])
        project = self.read_json("ai-kit/project.json")
        for module in project["modules"]:
            if module["path"] == "/web/":
                module["commands"]["test"] = "composer test"
        self.write("ai-kit/project.json", json.dumps(project))
        self.apply()
        allow = self.read_json(".claude/settings.local.json")["permissions"]["allow"]
        self.assertIn("Bash(composer test *)", allow)
        self.assertNotIn("Bash(php artisan test *)", allow)

    def test_client_ignore_files_get_a_marked_secret_block(self):
        self.laravel_and_go()
        self.write(".cursorignore", "docs/drafts/\n")
        self.apply(agents=["codex", "cursor", "aider", "gemini"], extras=["native-settings"])
        cursor = (self.target / ".cursorignore").read_text(encoding="utf-8")
        self.assertTrue(cursor.startswith("docs/drafts/\n"))
        self.assertIn(install.START, cursor)
        self.assertIn("\n.env\n", cursor)
        self.assertIn("\n/web/storage/*.key\n", cursor)
        for name in (".aiderignore", ".geminiignore"):
            self.assertIn("!.env.example", (self.target / name).read_text(encoding="utf-8"))
        self.assertFalse(self.plan()["actions"])
        settings_path = self.target / "ai-kit/settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["native_settings"] = False
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        self.apply()
        self.assertEqual((self.target / ".cursorignore").read_text(encoding="utf-8"), "docs/drafts/\n")

    def test_ignore_files_are_skipped_for_unselected_clients(self):
        self.apply(agents=["codex", "claude"], extras=["native-settings"])
        for name in (".cursorignore", ".aiderignore", ".geminiignore"):
            self.assertFalse((self.target / name).exists(), name)

    def test_data_guards_add_universal_and_detected_stack_asks(self):
        self.laravel_and_go()
        self.apply(agents=["claude"], extras=["data-guards"])
        ask = self.read_json(".claude/settings.local.json")["permissions"]["ask"]
        self.assertIn("Bash(rm -rf *)", ask)
        self.assertIn("Bash(php artisan migrate*)", ask)
        self.assertNotIn("Bash(php admin/cli/upgrade.php*)", ask)
        self.assertNotIn("Bash(git push *)", ask)

    def test_doctor_accepts_generated_configuration(self):
        self.laravel_and_go()
        self.apply(agents=ALL_SCOPED + ["aider", "gemini"], preset="strict")
        report = doctor.examine(self.target, root=self.source)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])

    def test_generated_claude_settings_match_golden_snapshot(self):
        self.laravel_and_go()
        self.apply(agents=["claude"], preset="strict")
        golden = install.ROOT / "tests/fixtures/golden/claude-settings-local.json"
        actual = (self.target / ".claude/settings.local.json").read_bytes()
        # Git autocrlf can check the fixture out with CRLF on Windows; compare content, not endings.
        self.assertEqual(actual.replace(b"\r\n", b"\n"), golden.read_bytes().replace(b"\r\n", b"\n"),
                         "Generated .claude/settings.local.json drifted from the golden snapshot; "
                         "update the golden file if the change is intentional.")

    # Scoped rules (item 7)

    def test_scoped_rules_use_each_client_native_format(self):
        self.laravel_and_go()
        self.apply(agents=ALL_SCOPED, extras=["scoped-rules"])
        claude = (self.target / ".claude/rules/ai-kit-web.md").read_text(encoding="utf-8")
        self.assertTrue(claude.startswith('---\npaths:\n  - "web/**"\n---\n'))
        self.assertIn("[LARAVEL](../../ai-kit/stacks/LARAVEL.md)", claude)
        self.assertIn("test `php artisan test`", claude)
        cursor = (self.target / ".cursor/rules/ai-kit-api.mdc").read_text(encoding="utf-8")
        self.assertTrue(cursor.startswith("---\nglobs: api/**\nalwaysApply: false\n---\n"))
        copilot = (self.target / ".github/instructions/ai-kit-api.instructions.md").read_text(encoding="utf-8")
        self.assertTrue(copilot.startswith('---\napplyTo: "api/**"\n---\n'))
        windsurf = (self.target / ".windsurf/rules/ai-kit-web.md").read_text(encoding="utf-8")
        self.assertTrue(windsurf.startswith("---\ntrigger: glob\nglobs: web/**\n---\n"))
        cline = (self.target / ".clinerules/ai-kit-web.md").read_text(encoding="utf-8")
        self.assertIn("[PHP](../ai-kit/stacks/PHP.md)", cline)
        # Codex reads AGENTS.md from the root down to the working directory only; no nested files.
        self.assertFalse((self.target / "web/AGENTS.md").exists())
        self.assertEqual(doctor.link_warnings(self.target), [])
        self.assertFalse(self.plan()["actions"])

    def test_root_module_uses_always_on_forms(self):
        self.write("go.mod", "module example.test/app\n")
        self.apply(agents=ALL_SCOPED, extras=["scoped-rules"])
        self.assertTrue((self.target / ".claude/rules/ai-kit-root.md").read_text(encoding="utf-8")
                        .startswith("# AI-KIT module rules: /\n"))
        self.assertTrue((self.target / ".cursor/rules/ai-kit-root.mdc").read_text(encoding="utf-8")
                        .startswith("---\nalwaysApply: true\n---\n"))
        self.assertTrue((self.target / ".github/instructions/ai-kit-root.instructions.md")
                        .read_text(encoding="utf-8").startswith('---\napplyTo: "**"\n---\n'))
        self.assertTrue((self.target / ".windsurf/rules/ai-kit-root.md").read_text(encoding="utf-8")
                        .startswith("---\ntrigger: always_on\n---\n"))

    def test_scoped_rules_follow_project_json_and_edited_rules_conflict(self):
        self.laravel_and_go()
        self.apply(agents=["claude"], extras=["scoped-rules"])
        project = self.read_json("ai-kit/project.json")
        for module in project["modules"]:
            if module["path"] == "/web/":
                module["profiles"] = ["FILAMENT", "LARAVEL", "PHP"]
        self.write("ai-kit/project.json", json.dumps(project))
        self.apply()
        self.assertIn("[FILAMENT]", (self.target / ".claude/rules/ai-kit-web.md").read_text(encoding="utf-8"))
        rule = self.target / ".claude/rules/ai-kit-api.md"
        rule.write_text(rule.read_text(encoding="utf-8") + "Local note.\n", encoding="utf-8")
        for module in project["modules"]:
            module["commands"] = {}
        self.write("ai-kit/project.json", json.dumps(project))
        plan = self.plan()
        self.assertIn(".claude/rules/ai-kit-api.md", plan["conflicts"])

    def test_unsupported_module_paths_are_skipped_with_a_warning(self):
        self.apply(agents=["claude"])
        self.write("ai-kit/project.json", json.dumps({"schema": 1, "operations": {}, "modules": [
            {"path": "/odd dir/", "profiles": ["GO"], "commands": {}},
            {"path": "/../escape/", "profiles": ["GO"], "commands": {}},
            {"path": "/svc", "profiles": ["GO"], "commands": {}}]}))
        plan = self.apply(extras=["scoped-rules"])
        self.assertEqual(sum("Skipping module path" in w for w in plan["warnings"]), 2)
        self.assertTrue((self.target / ".claude/rules/ai-kit-svc.md").is_file())
        self.assertEqual(len(list((self.target / ".claude/rules").iterdir())), 1)

    def test_colliding_module_slugs_stay_unique(self):
        self.write("a-b/go.mod", "module example.test/one\n")
        self.write("a/b/go.mod", "module example.test/two\n")
        self.apply(agents=["claude"], extras=["scoped-rules"])
        self.assertEqual(len(list((self.target / ".claude/rules").glob("ai-kit-a-b*.md"))), 2)

    def test_deselecting_a_client_with_scoped_rules_requires_retirement_review(self):
        self.laravel_and_go()
        self.apply(agents=["codex", "cursor"], extras=["scoped-rules"])
        plan = self.plan(agents=["codex"])
        self.assertIn(".cursor/rules/ai-kit-web.mdc", plan["adapter_conflicts"])

    # Presets (item 8)

    def test_presets_set_mode_and_managed_extras(self):
        plan = self.plan(preset="solo")
        self.assertEqual(plan["mode"], "private")
        self.assertEqual(plan["extras"], ["native-settings", "scoped-rules", "session-start"])
        plan = self.plan(preset="team")
        self.assertEqual(plan["mode"], "team")
        self.assertIn("guards", plan["extras"])
        plan = self.plan(preset="team", mode="private", extras=["ci"])
        self.assertEqual(plan["mode"], "private")
        self.assertIn("ci", plan["extras"])

    def test_minimal_preset_turns_managed_extras_off_and_keeps_mode(self):
        self.laravel_and_go()
        self.apply(agents=["claude"], preset="team")
        self.assertTrue((self.target / ".claude/settings.json").is_file())
        plan = self.apply(preset="minimal")
        self.assertEqual(plan["mode"], "team")
        self.assertEqual(plan["extras"], [])
        self.assertTrue(any("Preset minimal turns off previously enabled extras: session-start, guards, "
                            "native-settings, scoped-rules" in w for w in plan["warnings"]))
        settings = self.read_json("ai-kit/settings.json")
        self.assertIs(settings["guards"], False)
        self.assertIs(settings["scoped_rules"], False)
        self.assertNotIn("managed_json", self.read_json("ai-kit/.install-state.json"))
        self.assertNotIn("permissions", self.read_json(".claude/settings.json"))
        # Generated rules are never deleted; the preview names them for review.
        self.assertTrue(any("retained without a current source: .claude/rules/ai-kit-web.md" in w
                            for w in plan["warnings"]))

    def test_explicit_flag_keeps_an_extra_the_preset_would_turn_off(self):
        self.apply(agents=["claude"], extras=["guards"])
        plan = self.apply(preset="solo", extras=["guards"])
        self.assertIn("guards", plan["extras"])
        self.assertFalse(any("turns off" in w for w in plan["warnings"]))
        self.assertIn("Bash(git push *)", self.read_json(".claude/settings.local.json")["permissions"]["ask"])

    def test_unknown_preset_is_refused(self):
        with self.assertRaises(ValueError):
            self.plan(preset="everything")

    def test_cli_preset_and_new_flags(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = install.main([str(self.target), "--preset", "strict", "--with-ci"])
        self.assertEqual(code, 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["preset"], "strict")
        self.assertEqual(report["extras"], sorted(install.PRESET_EXTRAS + ("ci",)))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            install.main([str(self.target), "--with-native-settings", "--with-scoped-rules", "--with-data-guards"])
        self.assertEqual(json.loads(output.getvalue())["extras"], ["data-guards", "native-settings", "scoped-rules"])

    # Workflow skills (item 9)

    def test_workflow_skills_install_with_native_copies(self):
        self.apply(agents=["codex", "claude"])
        for name in ("ai-kit-bootstrap", "ai-kit-review", "ai-kit-sync-context"):
            source = self.target / ".agents/skills" / name / "SKILL.md"
            self.assertTrue(source.is_file(), name)
            self.assertEqual(source.read_bytes(), (self.target / ".claude/skills" / name / "SKILL.md").read_bytes())
            self.assertIn("Run only when the user explicitly asks", source.read_text(encoding="utf-8"))
        self.assertEqual(doctor.link_warnings(self.target), [])

    def test_registry_refuses_invalid_scoped_rules_and_ignore_files(self):
        registry_path = self.source / install.AGENT_REGISTRY_PATH
        original = json.loads(registry_path.read_text(encoding="utf-8"))
        for field, value in (("scoped_rules", {"directory": "../rules/", "format": "claude-paths"}),
                             ("scoped_rules", {"directory": ".claude/rules/", "format": "unknown"}),
                             ("scoped_rules", ".claude/rules/"),
                             ("ignore_file", "../.cursorignore"),
                             ("ignore_file", "sub/.ignore")):
            with self.subTest(field=field, value=value):
                registry = json.loads(json.dumps(original))
                registry["agents"]["cursor"][field] = value
                registry_path.write_text(json.dumps(registry), encoding="utf-8")
                with self.assertRaises(ValueError):
                    install.load_agent_registry(self.source)


if __name__ == "__main__":
    unittest.main()
