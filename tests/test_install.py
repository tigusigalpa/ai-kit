"""Exercise preservation, upgrade boundaries, ignore merging, and write failures."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-project-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.target = self.base / "project with spaces"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def plan(self, **options):
        return install.build_plan(self.target, root=self.source, **options)

    def apply(self, **options):
        plan = self.plan(**options)
        self.assertTrue(install.apply_plan(plan))
        return plan

    def write(self, path, data):
        destination = self.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    def change_source(self):
        core = self.source / "template/ai-kit/CORE.md"
        core.write_bytes(core.read_bytes() + b"\nUpstream clarification.\n")
        (self.source / "VERSION").write_text("0.2.1\n", encoding="utf-8")

    def test_preview_creates_nothing(self):
        plan = self.plan()
        self.assertTrue(plan["actions"])
        self.assertFalse(self.target.exists())

    def test_fresh_install_and_second_run_are_stable(self):
        self.apply()
        state = (self.target / "ai-kit/.install-state.json").read_bytes()
        plan = self.plan()
        self.assertFalse(plan["actions"])
        self.assertFalse(plan["conflicts"])
        self.assertTrue(install.apply_plan(plan))
        self.assertEqual(state, (self.target / "ai-kit/.install-state.json").read_bytes())

    def test_all_project_owned_documents_are_preserved(self):
        for path in install.OWNED:
            self.write(path, ("Existing " + path + "\n").encode())
        self.apply()
        for path in install.OWNED:
            self.assertEqual((self.target / path).read_bytes(), ("Existing " + path + "\n").encode())

    def test_unmanaged_instruction_conflict_applies_only_candidates(self):
        self.write("AGENTS.md", b"Existing instructions\n")
        plan = self.plan()
        self.assertIn("AGENTS.md", plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual((self.target / "AGENTS.md").read_bytes(), b"Existing instructions\n")
        self.assertFalse((self.target / "ai-kit/CORE.md").exists())
        self.assertFalse((self.target / "ai-kit/.install-state.json").exists())
        self.assertTrue((self.target / "ai-kit/.upstream-cache/candidates/AGENTS.md").exists())

    def test_unchanged_baseline_upgrade_and_backup(self):
        self.apply()
        old = (self.target / "ai-kit/CORE.md").read_bytes()
        self.change_source()
        self.apply()
        self.assertNotEqual(old, (self.target / "ai-kit/CORE.md").read_bytes())
        backups = list((self.target / "ai-kit/.upstream-cache/backups").glob("*/ai-kit/CORE.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), old)

    def test_local_edit_survives_repeat_and_blocks_new_upstream(self):
        self.apply()
        self.write("ai-kit/CORE.md", b"Local adapted core\n")
        self.assertFalse(self.plan()["conflicts"])
        old_state = (self.target / "ai-kit/.install-state.json").read_bytes()
        self.change_source()
        plan = self.plan()
        self.assertIn("ai-kit/CORE.md", plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(old_state, (self.target / "ai-kit/.install-state.json").read_bytes())
        self.assertEqual((self.target / "ai-kit/CORE.md").read_bytes(), b"Local adapted core\n")
        self.assertEqual((self.target / "ai-kit/VERSION").read_text().strip(), "0.2.0")

    def test_explicit_semantic_acceptance_preserves_future_adaptations(self):
        self.apply()
        self.change_source()
        self.write("ai-kit/CORE.md", b"Reviewed semantic merge\n")
        self.apply(accept_local=["ai-kit/CORE.md"])
        self.assertFalse(self.plan()["actions"])
        state = json.loads((self.target / "ai-kit/.install-state.json").read_text())
        self.assertTrue(state["files"]["ai-kit/CORE.md"]["local_adaptation"])
        self.change_source()
        self.assertIn("ai-kit/CORE.md", self.plan()["conflicts"])
        self.assertEqual((self.target / "ai-kit/CORE.md").read_bytes(), b"Reviewed semantic merge\n")

    def test_cannot_accept_unknown_or_project_owned_path(self):
        for path in ["../escape", "README.md", "ai-kit/settings.json"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.plan(accept_local=[path])

    def test_ignore_block_preserves_other_lines_without_duplicates(self):
        self.write(".gitignore", b"custom.log\n")
        self.apply()
        first = (self.target / ".gitignore").read_bytes()
        self.apply()
        self.assertEqual((self.target / ".gitignore").read_bytes(), first)
        self.assertTrue(first.startswith(b"custom.log\n"))
        self.assertEqual(first.count(install.START.encode()), 1)

    def test_team_change_replaces_only_managed_policy(self):
        self.write(".gitignore", b"custom.log\n")
        self.apply()
        self.apply(mode="team", language="English", conventions="standard")
        text = (self.target / ".gitignore").read_text()
        self.assertIn("custom.log", text)
        self.assertNotIn("\n/AGENTS.md\n", text)
        settings = json.loads((self.target / "ai-kit/settings.json").read_text())
        self.assertEqual(settings["sharing_mode"], "team")
        self.assertEqual(settings["chat_language"], "English")
        self.assertEqual(settings["conventions"], "standard")
        self.assertFalse(self.plan()["actions"])

    def test_legacy_team_exclusions_are_reported_not_removed(self):
        self.write(".gitignore", b"/AGENTS.md\ncustom.log\n")
        plan = self.plan(mode="team")
        self.assertIn(".gitignore", plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual((self.target / ".gitignore").read_bytes(), b"/AGENTS.md\ncustom.log\n")

    def test_php_vendor_rule_is_scoped_and_go_vendor_is_preserved(self):
        self.write("web/composer.json", b"{}\n")
        self.write("mixed/composer.json", b"{}\n")
        self.write("mixed/go.mod", b"module example.test/mixed\n")
        self.write("vendored/composer.json", b"{}\n")
        self.write("vendored/vendor/modules.txt", b"# module v1\n")
        self.write("go/go.mod", b"module example.test/go\n")
        self.assertEqual(install.module_ignores(self.target), ["/web/vendor/"])

    def test_moodle_config_rules_require_verified_module(self):
        self.write("moodle/config-dist.php", b"<?php\n")
        self.write("moodle/lib/moodlelib.php", b"<?php\n")
        self.write("other/config-dist.php", b"<?php\n")
        self.assertEqual(install.module_ignores(self.target), ["/moodle/behat.yml", "/moodle/config.php"])

    def test_claude_and_optional_entries_have_native_paths(self):
        self.apply(agents=["codex", "claude", "copilot", "cursor", "aider"])
        self.assertIn("@AGENTS.md", (self.target / "CLAUDE.md").read_text())
        for original in (self.target / ".agents/skills").glob("*/SKILL.md"):
            copied = self.target / ".claude/skills" / original.parent.name / "SKILL.md"
            self.assertEqual(original.read_bytes(), copied.read_bytes())
        self.assertTrue((self.target / ".github/copilot-instructions.md").exists())
        self.assertTrue((self.target / ".cursor/rules/ai-kit.mdc").exists())
        self.assertTrue((self.target / "CONVENTIONS.md").exists())
        self.assertFalse((self.target / ".claude/settings.json").exists())

    def test_settings_preserve_unrecognized_local_fields(self):
        self.apply()
        path = self.target / "ai-kit/settings.json"
        settings = json.loads(path.read_text())
        settings["local_option"] = "keep"
        self.write("ai-kit/settings.json", (json.dumps(settings) + "\n").encode())
        self.apply()
        self.assertEqual(json.loads(path.read_text())["local_option"], "keep")

    def test_refuse_reference_target(self):
        for target in [self.source, self.source / "nested"]:
            with self.subTest(target=target), self.assertRaises(ValueError):
                install.build_plan(target, root=self.source)

    def test_refuse_path_traversal_and_directory_destinations(self):
        for path in ["../outside", "/absolute", "C:/absolute", "a/../outside"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                install.safe_path(self.target, path)
        (self.target / "AGENTS.md").mkdir(parents=True)
        with self.assertRaises(ValueError):
            self.plan()

    def test_refuse_linked_destination(self):
        self.target.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.target / "ai-kit").symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest("Symlinks unavailable: " + str(exc))
        with self.assertRaises(ValueError):
            self.plan()
        self.assertFalse(list(outside.iterdir()))

    def test_refuse_malformed_ignore_markers(self):
        for text in [install.START + "\n", install.END + "\n" + install.START,
                     (install.START + "\n" + install.END + "\n") * 2]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                install.merge_ignore(text, "foo\n", [])

    def test_file_changed_after_preview_refuses_all_instruction_writes(self):
        self.write(".gitignore", b"initial\n")
        plan = self.plan()
        self.write(".gitignore", b"concurrent edit\n")
        with self.assertRaises(ValueError):
            install.apply_plan(plan)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertEqual((self.target / ".gitignore").read_bytes(), b"concurrent edit\n")

    def test_write_failure_rolls_back_completed_instruction_writes(self):
        plan = self.plan()
        real_write = install.atomic_write

        def failing_write(path, data):
            if path == self.target / "ai-kit/CORE.md":
                raise OSError("Injected failure")
            real_write(path, data)

        with patch.object(install, "atomic_write", side_effect=failing_write), self.assertRaises(OSError):
            install.apply_plan(plan)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / "ai-kit/.install-state.json").exists())

    def test_cli_preview_and_conflict_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()), patch.object(install, "ROOT", self.source):
            # Default argument binds the distribution root; CLI is exercised against real sources.
            self.assertEqual(install.main([str(self.target), "--dry-run"]), 0)
            self.assertFalse(self.target.exists())
            self.write("AGENTS.md", b"Existing\n")
            self.assertEqual(install.main([str(self.target), "--apply"]), 2)


if __name__ == "__main__":
    unittest.main()
