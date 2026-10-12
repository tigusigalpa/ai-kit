"""Context7 workflows remain optional, offline and separate from native MCP activation."""
from __future__ import annotations

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
import doctor
import install

ENTRY = ".agents/skills/context7-docs/SKILL.md"
NATIVE = ".claude/skills/context7-docs/SKILL.md"


class Context7Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-context7-")
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name).resolve()
        self.source = base / "reference"
        self.target = base / "project with spaces"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def plan(self, **options):
        return install.build_plan(self.target, root=self.source, **options)

    def apply(self, **options):
        plan = self.plan(**options)
        self.assertFalse(install.needs_review(plan), plan)
        self.assertTrue(install.apply_plan(plan))
        return plan

    def test_default_and_presets_omit_skill_and_registry_entry(self):
        for preset in (None, *install.PRESETS):
            with self.subTest(preset=preset):
                plan = self.plan(preset=preset, agents=["codex", "claude"])
                self.assertNotIn("context7", plan["extras"])
                self.assertNotIn(ENTRY, plan["actions"])
                self.assertNotIn(NATIVE, plan["actions"])
                self.assertNotIn(b"context7-docs/SKILL.md", plan["actions"]["ai-kit/SKILLS.md"]["data"])
        self.apply()
        self.assertEqual(doctor.link_warnings(self.target), [])

    def test_apply_is_offline_and_preserves_native_mcp_configuration(self):
        paths = (".codex/config.toml", ".mcp.json", ".cursor/mcp.json", ".gemini/settings.json")
        for path in paths:
            existing = self.target / path
            existing.parent.mkdir(parents=True, exist_ok=True)
            existing.write_bytes(b"Existing client-owned configuration.\n")
        with patch("subprocess.Popen", side_effect=AssertionError("No client or package process")), \
                patch("socket.socket", side_effect=AssertionError("No network connection")):
            plan = self.apply(extras=["context7"], agents=["codex", "claude", "cursor"])
        for path in paths:
            self.assertNotIn(path, plan["actions"])
            self.assertEqual((self.target / path).read_bytes(), b"Existing client-owned configuration.\n")
        original = (self.source / "template" / ENTRY).read_bytes()
        self.assertEqual((self.target / ENTRY).read_bytes(), original)
        self.assertEqual((self.target / NATIVE).read_bytes(), original)
        self.assertNotIn(b"disable-model-invocation", original)
        self.assertEqual(doctor.examine(self.target, root=self.source)["errors"], [])
        self.assertEqual(doctor.link_warnings(self.target), [])
        self.assertEqual(self.plan()["actions"], {})

    def test_selection_persists_independently_of_other_integrations_and_presets(self):
        self.apply(extras=["context7"])
        self.assertFalse((self.target / "ai-kit/vendor/security-audit").exists())
        self.assertFalse((self.target / "ai-kit/vendor/strix").exists())
        self.apply(preset="minimal")
        self.assertEqual(self.plan()["extras"], ["context7"])
        self.apply(extras=["security-audit", "strix"], agents=["codex", "claude"])
        self.assertEqual(self.plan()["extras"], ["context7", "security-audit", "strix"])
        settings = json.loads((self.target / "ai-kit/settings.json").read_text(encoding="utf-8"))
        self.assertIs(settings["context7"], True)
        self.assertEqual(self.plan()["actions"], {})

    def test_local_edits_and_source_upgrade_preserve_conflicting_files(self):
        self.apply(extras=["context7"])
        path = self.target / ENTRY
        local = path.read_bytes() + b"\nProject-specific documentation scope.\n"
        path.write_bytes(local)
        self.assertEqual(self.plan()["actions"], {})
        source = self.source / "template" / ENTRY
        incoming = source.read_bytes() + b"\nUpdated documentation workflow.\n"
        source.write_bytes(incoming)
        old_state = (self.target / "ai-kit/.install-state.json").read_bytes()
        plan = self.plan()
        self.assertIn(ENTRY, plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(path.read_bytes(), local)
        self.assertEqual((self.target / "ai-kit/.install-state.json").read_bytes(), old_state)
        self.assertEqual((self.target / plan["candidates"][ENTRY]["path"]).read_bytes(), incoming)

    def test_untracked_skill_conflict_blocks_install_before_managed_writes(self):
        path = self.target / ENTRY
        path.parent.mkdir(parents=True)
        path.write_bytes(b"Existing skill.\n")
        plan = self.plan(extras=["context7"])
        self.assertIn(ENTRY, plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(path.read_bytes(), b"Existing skill.\n")
        self.assertFalse((self.target / "ai-kit/settings.json").exists())

    def test_deselection_retains_files_and_native_retirement_requires_review(self):
        self.apply(extras=["context7"], agents=["codex", "claude"])
        plan = self.plan(agents=["codex"])
        self.assertIn(NATIVE, plan["adapter_conflicts"])
        self.assertFalse(install.apply_plan(plan))
        settings_path = self.target / "ai-kit/settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["context7"] = False
        settings_path.write_text(json.dumps(settings) + "\n", encoding="utf-8")
        old = (self.target / ENTRY).read_bytes()
        plan = self.apply()
        self.assertNotIn("context7", plan["extras"])
        self.assertEqual((self.target / ENTRY).read_bytes(), old)
        self.assertTrue(any("Previously managed path retained" in warning and "context7-docs" in warning
                            for warning in plan["warnings"]))
        self.assertEqual(doctor.link_warnings(self.target), [])

    def test_invalid_choice_and_blocked_skill_parent_are_refused(self):
        defaults_path = self.source / "template/ai-kit/settings.json"
        defaults = json.loads(defaults_path.read_text(encoding="utf-8"))
        defaults["context7"] = "true"
        defaults_path.write_text(json.dumps(defaults) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "context7"):
            self.plan(extras=["context7"])
        defaults.pop("context7")
        defaults_path.write_text(json.dumps(defaults) + "\n", encoding="utf-8")
        parent = (self.target / ENTRY).parent
        parent.parent.mkdir(parents=True)
        parent.write_bytes(b"Blocked directory.\n")
        with self.assertRaises(NotADirectoryError):
            self.plan(extras=["context7"])
        self.assertFalse((self.target / "ai-kit/settings.json").exists())
        self.assertEqual(parent.read_bytes(), b"Blocked directory.\n")

    def test_cli_flag_only_previews_until_apply_is_requested(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(install.main([str(self.target), "--with-context7"]), 0)
        self.assertFalse(self.target.exists())
        self.assertIn("context7", json.loads(output.getvalue())["extras"])


if __name__ == "__main__":
    unittest.main()
