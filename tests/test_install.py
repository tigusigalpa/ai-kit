"""Exercise preservation, upgrade boundaries, ignore merging, and write failures."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-project-")
        self.addCleanup(self.temp.cleanup)
        # Windows TEMP can use an 8.3 alias; match the installer's resolved paths.
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project with spaces"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        self.initial_version = (self.source / "VERSION").read_text(encoding="utf-8").strip()

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
        version_path = self.source / "VERSION"
        major, minor, patch_version = version_path.read_text(encoding="utf-8").strip().split(".")
        version_path.write_text(f"{major}.{minor}.{int(patch_version) + 1}\n", encoding="utf-8")

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
        candidate = self.target / plan["candidates"]["AGENTS.md"]["path"]
        self.assertTrue(candidate.exists())
        manifest = json.loads((self.target / plan["candidates"]["AGENTS.md"]["manifest"]).read_text())
        self.assertEqual(manifest["relative_path"], "AGENTS.md")
        self.assertEqual(manifest["source_hash"], install.digest(candidate.read_bytes()))
        self.assertEqual(manifest["local_hash"], install.digest(b"Existing instructions\n"))

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
        self.assertEqual((self.target / "ai-kit/VERSION").read_text().strip(), self.initial_version)

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

    def test_node_and_python_rules_are_scoped_to_verified_modules(self):
        self.write("app/package.json", b"{}\n")
        self.write("svc/pyproject.toml", b'[project]\nname = "svc"\n')
        self.write("plain/notes.txt", b"nothing detected\n")
        rules = install.module_ignores(self.target)
        self.assertIn("app/**/node_modules/", rules)
        self.assertIn("app/**/.yarn/cache/", rules)
        self.assertIn("svc/**/__pycache__/", rules)
        self.assertIn("svc/**/.venv/", rules)
        self.assertIn("/svc/.cache/pip/", rules)
        self.assertFalse(any(rule.startswith("plain/") for rule in rules))

    def test_no_manifests_produce_no_generated_path_rules(self):
        self.write("src/app.go", b"package main\n")
        self.assertEqual(install.module_ignores(self.target), [])

    def test_detected_profiles_feed_fresh_project_context_draft(self):
        self.write("go.mod", b"module example.test/app\n")
        self.write("package.json", b"{}\n")
        plan = self.plan()
        self.assertEqual(plan["detected_profiles"], {"FRONTEND": [""], "GO": [""]})
        self.apply()
        context = (self.target / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("| / | installer-detected manifests | not established | "
                      "FRONTEND, GO (suggested, confirm at bootstrap) | not established |", context)

    def test_detected_profiles_are_scoped_to_module_prefixes(self):
        self.write("api/go.mod", b"module example.test/api\n")
        self.write("web/composer.json", b"{}\n")
        self.write("web/artisan", b"#!/usr/bin/env php\n")
        self.assertEqual(self.plan()["detected_profiles"],
                         {"GO": ["api/"], "LARAVEL": ["web/"], "PHP": ["web/"]})

    def test_detection_and_placeholder_persist_without_manifests(self):
        self.assertEqual(self.plan()["detected_profiles"], {})
        self.apply()
        context = (self.target / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("| Not established | Not established | Not established | None confirmed | Not established |",
                      context)

    def test_existing_project_context_is_preserved_against_detection(self):
        self.write("PROJECT_CONTEXT.md", b"Existing verified context\n")
        self.write("go.mod", b"module example.test/app\n")
        self.apply()
        self.assertEqual((self.target / "PROJECT_CONTEXT.md").read_bytes(), b"Existing verified context\n")

    def test_session_start_extra_installs_hook_and_claude_wiring(self):
        plan = self.plan(agents=["codex", "claude"], extras=["session-start"])
        self.assertEqual(plan["extras"], ["session-start"])
        self.assertIn(".agents/hooks/session-start.md", plan["actions"])
        self.assertIn(".claude/settings.json", plan["actions"])
        self.apply(agents=["codex", "claude"], extras=["session-start"])
        self.assertIn("SessionStart", (self.target / ".claude/settings.json").read_text())
        settings = json.loads((self.target / "ai-kit/settings.json").read_text())
        self.assertIs(settings["session_start"], True)

    def test_guards_extra_merges_deny_rules_and_persists(self):
        self.apply(agents=["claude"], extras=["guards"])
        claude_settings = json.loads((self.target / ".claude/settings.json").read_text())
        self.assertIn("Bash(git push *)", claude_settings["permissions"]["deny"])
        plan = self.plan()
        self.assertEqual(plan["extras"], ["guards"])
        self.assertFalse(plan["actions"])

    def test_session_start_and_guards_merge_into_one_settings_file(self):
        self.apply(agents=["claude"], extras=["session-start", "guards"])
        claude_settings = json.loads((self.target / ".claude/settings.json").read_text())
        self.assertIn("hooks", claude_settings)
        self.assertIn("permissions", claude_settings)

    def test_guards_without_claude_warns_and_skips_wiring(self):
        plan = self.plan(extras=["guards"])
        self.assertNotIn(".claude/settings.json", plan["actions"])
        self.assertTrue(any("requires the claude agent selection" in warning for warning in plan["warnings"]))

    def test_ci_extra_installs_workflow_and_warns_in_private_mode(self):
        plan = self.plan(extras=["ci"])
        self.assertIn(".github/workflows/ai-kit.yml", plan["actions"])
        self.assertTrue(any("team mode is the intended companion" in warning for warning in plan["warnings"]))
        self.apply(extras=["ci"])
        self.assertIn("AI-KIT project check", (self.target / ".github/workflows/ai-kit.yml").read_text())

    def test_unknown_extra_is_refused(self):
        with self.assertRaises(ValueError):
            self.plan(extras=["unknown"])

    def test_non_boolean_settings_extra_is_refused(self):
        settings = {"project_language": "English", "chat_language": "Russian",
                    "sharing_mode": "private", "conventions": "owner", "ci": "yes"}
        self.write("ai-kit/settings.json", (json.dumps(settings) + "\n").encode())
        with self.assertRaises(ValueError):
            self.plan()

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

    def test_repeated_candidate_conflict_preserves_draft_and_manifest(self):
        self.write("AGENTS.md", b"Project instructions\n")
        plan = self.plan()
        info = plan["candidates"]["AGENTS.md"]
        self.assertFalse(self.target.joinpath(info["path"]).exists())
        self.assertFalse(install.apply_plan(plan))
        self.write(info["path"], b"Human reviewed draft\n")
        old_manifest = self.target.joinpath(info["manifest"]).read_bytes()
        self.write("AGENTS.md", b"Another local edit\n")
        again = self.plan()
        self.assertFalse(again["candidates"]["AGENTS.md"]["matches_source"])
        self.assertFalse(install.apply_plan(again))
        self.assertEqual(self.target.joinpath(info["path"]).read_bytes(), b"Human reviewed draft\n")
        self.assertEqual(self.target.joinpath(info["manifest"]).read_bytes(), old_manifest)
        self.assertFalse((self.target / "ai-kit/.install-state.json").exists())

    def test_new_source_candidate_preserves_previous_and_legacy_drafts(self):
        self.write("AGENTS.md", b"Project instructions\n")
        legacy = "ai-kit/.upstream-cache/candidates/AGENTS.md"
        self.write(legacy, b"Legacy review draft\n")
        first = self.plan()
        install.apply_plan(first)
        old_path = first["candidates"]["AGENTS.md"]["path"]
        self.write(old_path, b"Current review draft\n")
        source = self.source / "template/AGENTS.md"
        source.write_bytes(source.read_bytes() + b"\nNew upstream instructions.\n")
        next_plan = self.plan()
        new_path = next_plan["candidates"]["AGENTS.md"]["path"]
        self.assertNotEqual(old_path, new_path)
        self.assertFalse(self.target.joinpath(new_path).exists())
        install.apply_plan(next_plan)
        self.assertEqual(self.target.joinpath(new_path).read_bytes(), source.read_bytes())
        self.assertEqual(self.target.joinpath(old_path).read_bytes(), b"Current review draft\n")
        self.assertEqual(self.target.joinpath(legacy).read_bytes(), b"Legacy review draft\n")

    def test_candidate_created_after_preview_is_never_overwritten(self):
        self.write("AGENTS.md", b"Project instructions\n")
        plan = self.plan()
        path = plan["candidates"]["AGENTS.md"]["path"]
        self.write(path, b"Draft created after preview\n")
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(self.target.joinpath(path).read_bytes(), b"Draft created after preview\n")

    def test_agent_retirement_conflict_preserves_active_files_and_state(self):
        self.apply(agents=["codex", "claude"])
        state_path = self.target / "ai-kit/.install-state.json"
        original_state = state_path.read_bytes()
        self.write("CLAUDE.md", b"Locally adapted Claude instructions\n")
        plan = self.plan(agents=["codex", "copilot"])
        self.assertIn("CLAUDE.md", plan["adapter_conflicts"])
        self.assertEqual(len(plan["adapter_conflicts"]), 9)
        self.assertTrue(install.needs_review(plan))
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(state_path.read_bytes(), original_state)
        self.assertFalse((self.target / ".github/copilot-instructions.md").exists())
        self.assertEqual((self.target / "CLAUDE.md").read_bytes(), b"Locally adapted Claude instructions\n")
        self.assertIn("CLAUDE.md", json.loads(original_state)["files"])
        self.assertFalse(self.plan(agents=["codex", "claude"])["adapter_conflicts"])

    def test_reviewed_manual_retirement_allows_new_selection(self):
        self.apply(agents=["codex", "claude"])
        plan = self.plan(agents=["codex", "copilot"])
        for relative in plan["adapter_conflicts"]:
            path = install.safe_path(self.target, relative)
            path.resolve().relative_to(self.target.resolve())
            path.unlink()
        self.apply(agents=["codex", "copilot"])
        state = json.loads((self.target / "ai-kit/.install-state.json").read_text())
        self.assertEqual(state["agents"], ["codex", "copilot"])
        self.assertNotIn("CLAUDE.md", state["files"])
        self.assertTrue((self.target / ".github/copilot-instructions.md").exists())

    def test_untracked_unselected_adapter_and_skills_are_reported(self):
        self.write("CLAUDE.md", b"Custom Claude instructions\n")
        self.write(".claude/skills/custom/SKILL.md", b"Custom native skill\n")
        plan = self.apply()
        self.assertTrue(any("Untracked unselected claude" in warning for warning in plan["warnings"]))
        self.assertTrue(any("Unselected .claude/skills" in warning for warning in plan["warnings"]))
        self.assertEqual((self.target / "CLAUDE.md").read_bytes(), b"Custom Claude instructions\n")
        self.assertEqual((self.target / ".claude/skills/custom/SKILL.md").read_bytes(), b"Custom native skill\n")

    def test_state_validation_refuses_shapes_before_planning(self):
        valid = {"schema": 1, "accepted_version": "0.2.1", "agents": ["codex"], "files": {}}
        cases = [{}, {**valid, "schema": 99}, {**valid, "schema": True},
                 {**valid, "accepted_version": []}, {**valid, "agents": "codex"},
                 {**valid, "agents": ["codex", 1]}, {**valid, "agents": ["codex", "codex"]},
                 {**valid, "agents": ["unknown"]}, {**valid, "files": []},
                 {**valid, "files": {"AGENTS.md": "bad"}},
                 {**valid, "files": {"AGENTS.md": {"source_hash": "bad", "installed_hash": "a" * 64}}},
                 {**valid, "files": {"AGENTS.md": {"source_hash": "a" * 64, "installed_hash": None}}},
                 {**valid, "files": {"AGENTS.md": {"source_hash": "a" * 64, "installed_hash": "b" * 64,
                                                  "local_adaptation": 1}}},
                 {**valid, "files": {"../outside": {"source_hash": "a" * 64, "installed_hash": "b" * 64}}}]
        for state in cases:
            with self.subTest(state=state):
                self.write("ai-kit/.install-state.json", json.dumps(state).encode())
                with self.assertRaises(ValueError):
                    self.plan()
                self.assertFalse((self.target / "AGENTS.md").exists())

    def test_cli_corrupt_state_reports_refusal_without_traceback(self):
        self.write("ai-kit/.install-state.json",
                   json.dumps({"schema": 99, "agents": ["codex", 1], "files": {}}).encode())
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main([str(self.target), "--apply"]), 1)
        self.assertIn("Installation refused: Unsupported installer state schema", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_settings_type_validation_is_controlled(self):
        valid = json.loads((self.source / "template/ai-kit/settings.json").read_text())
        for field, value in [("project_language", 1), ("chat_language", []), ("sharing_mode", {}),
                             ("conventions", False), ("upstream", "not-an-object"),
                             ("upstream", {"ref": 1})]:
            with self.subTest(field=field, value=value):
                self.write("ai-kit/settings.json", json.dumps({**valid, field: value}).encode())
                with self.assertRaises(ValueError):
                    self.plan()
                self.assertFalse((self.target / "AGENTS.md").exists())

    def test_previous_bundle_state_and_project_data_survive_upgrade(self):
        (self.source / "VERSION").write_text("0.2.1\n", encoding="utf-8")
        self.write("README.md", b"Existing application documentation\n")
        self.write(".gitignore", b"custom.cache\n")
        self.apply()
        self.write("ai-kit/.upstream-cache/candidates/AGENTS.md", b"Old review work\n")
        (self.source / "VERSION").write_text(self.initial_version + "\n", encoding="utf-8")
        self.apply()
        state = json.loads((self.target / "ai-kit/.install-state.json").read_text())
        self.assertEqual(state["schema"], 1)
        self.assertEqual(state["accepted_version"], self.initial_version)
        self.assertEqual((self.target / "README.md").read_bytes(), b"Existing application documentation\n")
        self.assertTrue((self.target / ".gitignore").read_bytes().startswith(b"custom.cache\n"))
        self.assertEqual((self.target / "ai-kit/.upstream-cache/candidates/AGENTS.md").read_bytes(),
                         b"Old review work\n")

    def test_existing_mixed_project_and_installed_git_visibility(self):
        git = os.environ.get("AI_KIT_GIT") or shutil.which("git")
        if not git:
            self.skipTest("Git unavailable for installed-project visibility check")
        files = {"AGENTS.md": b"Reviewed application instructions\n",
                 "README.md": b"Existing application documentation\n",
                 ".gitignore": b"custom.cache\n",
                 "web/composer.json": b'{"require": {}}\n', "web/composer.lock": b"{}\n",
                 "web/vendor/autoload.php": b"<?php\n",
                 "api/go.mod": b"module example.test/api\n", "api/go.sum": b"fixture checksum\n",
                 "api/vendor/modules.txt": b"# intentional vendor fixture\n",
                 "tools/pyproject.toml": b'[project]\nname = "fixture-tools"\n',
                 "tools/uv.lock": b"version = 1\n", "tools/requirements.txt": b"# fixture\n",
                 "tools/__pycache__/task.pyc": b"cache", ".env": b"FIXTURE=local\n",
                 ".env.example": b"FIXTURE=example\n", "api/go-cache/item": b"cache",
                 "api/result.out": b"output", "custom.cache": b"local"}
        for path, data in files.items():
            self.write(path, data)
        pending = self.plan(agents=["codex", "claude"])
        self.assertFalse(install.apply_plan(pending))
        self.assertFalse((self.target / "ai-kit/.install-state.json").exists())
        subprocess.run([git, "-C", str(self.target), "init", "--quiet"], check=True,
                       capture_output=True, timeout=20)

        def ignored(path):
            result = subprocess.run([git, "-C", str(self.target), "-c", "core.excludesFile=",
                                     "check-ignore", "--no-index", "-q", path],
                                    capture_output=True, timeout=20)
            self.assertIn(result.returncode, (0, 1), result.stderr.decode(errors="replace"))
            return result.returncode == 0

        shared = ["AGENTS.md", "ai-kit/CORE.md", ".agents/skills/go-work/SKILL.md",
                  "CLAUDE.md", ".claude/skills/go-work/SKILL.md"]
        visible = ["README.md", "CHANGELOG.md", ".env.example", "web/composer.json",
                   "web/composer.lock", "api/go.mod", "api/go.sum", "api/vendor/modules.txt",
                   "tools/pyproject.toml", "tools/uv.lock", "tools/requirements.txt"]
        hidden = [".env", "custom.cache", "web/vendor/autoload.php", "api/go-cache/item",
                  "api/result.out", "tools/__pycache__/task.pyc", "ai-kit/.install-state.json",
                  pending["candidates"]["AGENTS.md"]["path"]]
        for mode in ("private", "team"):
            with self.subTest(mode=mode):
                self.apply(mode=mode, agents=["codex", "claude"], accept_local=["AGENTS.md"])
                for path in visible:
                    self.assertFalse(ignored(path), path)
                for path in hidden:
                    self.assertTrue(ignored(path), path)
                for path in shared:
                    self.assertEqual(ignored(path), mode == "private", path)
                self.assertEqual((self.target / "AGENTS.md").read_bytes(), files["AGENTS.md"])
                self.assertEqual((self.target / "README.md").read_bytes(), files["README.md"])
                self.assertTrue((self.target / ".gitignore").read_bytes().startswith(files[".gitignore"]))
                for path in ["web/composer.lock", "api/go.mod", "api/go.sum", "tools/uv.lock"]:
                    self.assertEqual((self.target / path).read_bytes(), files[path])
                self.assertFalse(self.plan()["actions"])

    @unittest.skipUnless(os.name == "nt", "Windows junction fixture")
    def test_windows_junctions_refused_and_excluded_from_module_scan(self):
        shell = shutil.which("powershell") or shutil.which("pwsh")
        if not shell:
            self.skipTest("PowerShell unavailable for junction fixture")
        self.target.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "composer.json").write_bytes(b"{}\n")
        sentinel = outside / "preserved.txt"
        sentinel.write_bytes(b"Keep outside data\n")
        helper = install.ROOT / "tests/fixtures/create-junction.ps1"

        def junction(link):
            # Both paths are confined to this disposable test fixture.
            link.absolute().relative_to(self.base.resolve())
            outside.resolve().relative_to(self.base.resolve())
            result = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                     "-File", str(helper),
                                     "-LinkPath", str(link), "-TargetPath", str(outside)],
                                    capture_output=True, timeout=30)
            if result.returncode == 77:
                self.skipTest("Junction creation unavailable: " + result.stderr.decode(errors="replace"))
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertTrue(install.is_link(link))
            self.addCleanup(link.rmdir)

        nested = self.target / "ai-kit"
        junction(nested)
        with self.assertRaises(ValueError):
            self.plan()
        root_link = self.base / "linked root"
        junction(root_link)
        with self.assertRaisesRegex(ValueError, "linked target root"):
            install.build_plan(root_link, root=self.source)
        module_link = self.target / "linked module"
        junction(module_link)
        self.assertEqual(install.module_ignores(self.target), [])
        self.assertEqual(sentinel.read_bytes(), b"Keep outside data\n")
        self.assertFalse((outside / "settings.json").exists())


class NoncanonicalTempPathTests(unittest.TestCase):
    """Run the two affected scenarios with another spelling of the temp root."""

    plan = InstallerTests.plan
    test_write_failure_rolls_back_completed_instruction_writes = (
        InstallerTests.test_write_failure_rolls_back_completed_instruction_writes)
    test_windows_junctions_refused_and_excluded_from_module_scan = (
        InstallerTests.test_windows_junctions_refused_and_excluded_from_module_scan)

    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory

        def noncanonical_directory(*args, **kwargs):
            directory = temporary_directory(*args, **kwargs)
            self.addCleanup(directory.cleanup)
            actual = Path(directory.name).resolve()
            route = temporary_directory(dir=actual.parent, prefix="ai-kit-alias-route-")
            self.addCleanup(route.cleanup)
            # This real '..' route has a different prefix, like an 8.3 alias.
            # Cleanup stays bound to each original directory, never the alias.
            return SimpleNamespace(name=str(Path(route.name) / ".." / actual.name),
                                   cleanup=directory.cleanup)

        replacement = patch.object(tempfile, "TemporaryDirectory", side_effect=noncanonical_directory)
        replacement.start()
        self.addCleanup(replacement.stop)
        InstallerTests.setUp(self)


if __name__ == "__main__":
    unittest.main()
