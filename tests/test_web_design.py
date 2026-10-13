"""Web Design is an offline optional workflow with preserved project design memory."""
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
import adapters
import context
import doctor
import install

SKILLS = install.OPTIONAL_ENTRY_POINTS["web-design"]
DOCUMENTS = install.OPTIONAL_DOCUMENTS["web-design"]
RESOURCES = install.OPTIONAL_RESOURCES["web-design"]


class WebDesignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-design-")
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

    def test_default_and_all_presets_omit_the_whole_module(self):
        for preset in (None, *install.PRESETS):
            with self.subTest(preset=preset):
                plan = self.plan(preset=preset, agents=["codex", "claude"])
                self.assertNotIn("web-design", plan["extras"])
                for name in SKILLS:
                    self.assertNotIn(f".agents/skills/{name}/SKILL.md", plan["actions"])
                    self.assertNotIn(f".claude/skills/{name}/SKILL.md", plan["actions"])
                    self.assertNotIn(f"{name}/SKILL.md".encode(), plan["actions"]["ai-kit/SKILLS.md"]["data"])
                self.assertTrue(set(RESOURCES + DOCUMENTS).isdisjoint(plan["actions"]))
        self.apply()
        self.assertEqual(doctor.link_warnings(self.target), [])
        self.assertFalse(any("design" in warning for warning in doctor.examine(self.target, root=self.source)["warnings"]))

    def test_apply_is_offline_and_copies_only_selected_native_skills(self):
        client_files = (".codex/config.toml", ".mcp.json", ".cursor/mcp.json")
        for name in client_files:
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Client-owned configuration stays unchanged.\n")
        with patch("subprocess.Popen", side_effect=AssertionError("No package/browser/client process")), \
                patch("socket.socket", side_effect=AssertionError("No external network")):
            self.apply(extras=["web-design"], agents=["codex", "claude", "cursor"])
        for name in SKILLS:
            source = self.target / f".agents/skills/{name}/SKILL.md"
            native = self.target / f".claude/skills/{name}/SKILL.md"
            self.assertEqual(source.read_bytes(), native.read_bytes())
            self.assertNotIn(b"disable-model-invocation", native.read_bytes())
        self.assertTrue(all((self.target / name).is_file() for name in RESOURCES + DOCUMENTS))
        self.assertFalse((self.target / "ai-kit/.design").exists())
        for name in client_files:
            self.assertEqual((self.target / name).read_bytes(), b"Client-owned configuration stays unchanged.\n")
        self.assertEqual(doctor.link_warnings(self.target), [])
        self.assertEqual(doctor.examine(self.target, root=self.source)["errors"], [])

    def test_choices_persist_independently_and_reruns_are_stable(self):
        self.apply(extras=["web-design"], agents=["codex", "claude"])
        self.assertEqual(self.plan(preset="minimal")["extras"], ["web-design"])
        self.apply(extras=["context7", "security-audit", "strix"])
        stable = self.plan()
        self.assertEqual(stable["extras"], ["context7", "security-audit", "strix", "web-design"])
        self.assertEqual(stable["actions"], {})
        settings = json.loads((self.target / "ai-kit/settings.json").read_text(encoding="utf-8"))
        self.assertIs(settings["web_design"], True)

    def test_existing_design_documents_and_local_edits_survive_source_updates(self):
        original = {}
        for name in DOCUMENTS:
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            original[name] = ("Existing project design: " + name + "\r\n").encode()
            path.write_bytes(original[name])
        self.apply(extras=["web-design"])
        entry = ".agents/skills/web-design/SKILL.md"
        local = self.target / entry
        local.write_bytes(local.read_bytes() + b"\nLocal project adjustment.\n")
        local_bytes = local.read_bytes()
        self.apply()
        self.assertEqual(local.read_bytes(), local_bytes)
        for name in DOCUMENTS:
            source = self.source / "template" / name
            source.write_bytes(source.read_bytes() + b"\nNew distribution scaffold.\n")
        source_entry = self.source / "template" / entry
        source_entry.write_bytes(source_entry.read_bytes() + b"\nNew distribution guidance.\n")
        plan = self.plan()
        self.assertIn(entry, plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(local.read_bytes(), local_bytes)
        for name, data in original.items():
            self.assertEqual((self.target / name).read_bytes(), data)
            self.assertNotIn(name, plan["conflicts"])
        self.assertTrue(any((self.target / "ai-kit/.upstream-cache/candidates").rglob("SKILL.md")))

    def test_project_documents_are_not_accept_local_managed_instructions(self):
        self.apply(extras=["web-design"])
        with self.assertRaisesRegex(ValueError, "managed instructions"):
            self.plan(accept_local=[DOCUMENTS[0]])
        (self.target / DOCUMENTS[-1]).unlink()
        report = doctor.examine(self.target, root=self.source)
        self.assertIn("Owned project document missing: " + DOCUMENTS[-1], report["warnings"])
        self.apply()
        self.assertTrue((self.target / DOCUMENTS[-1]).is_file())
        original = install.is_link
        with patch.object(install, "is_link", side_effect=lambda p: p == self.target / DOCUMENTS[0] or original(p)):
            self.assertTrue(any("Unsafe project document" in error
                                for error in doctor.examine(self.target, root=self.source)["errors"]))
            with self.assertRaisesRegex(ValueError, "[Ll]ink"):
                context.select_context(self.target, workflow="web-design")

    def test_disabled_module_retains_files_but_cannot_select_workflow(self):
        self.apply(extras=["web-design"], agents=["codex", "claude"])
        paths = list(RESOURCES + DOCUMENTS) + [f".agents/skills/{name}/SKILL.md" for name in SKILLS]
        before = {name: (self.target / name).read_bytes() for name in paths}
        settings_path = self.target / "ai-kit/settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["web_design"] = False
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        plan = self.apply()
        self.assertNotIn("web-design", plan["extras"])
        self.assertEqual(before, {name: (self.target / name).read_bytes() for name in paths})
        with self.assertRaisesRegex(ValueError, "disabled"):
            context.select_context(self.target, workflow="web-design")
        self.assertEqual(doctor.link_warnings(self.target), [])
        retire = adapters.retirement_plan(self.target, "claude", root=self.source)
        self.assertTrue(any(item["path"].endswith("web-design/SKILL.md") for item in retire["removals"]))
        self.assertTrue(adapters.apply_retirement(retire))
        self.assertTrue((self.target / ".agents/skills/web-design/SKILL.md").is_file())

    def test_invalid_selection_and_blocked_or_linked_parents_refuse_before_writes(self):
        defaults_path = self.source / "template/ai-kit/settings.json"
        defaults = json.loads(defaults_path.read_text(encoding="utf-8"))
        defaults["web_design"] = "true"
        defaults_path.write_text(json.dumps(defaults), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "web_design"):
            self.plan(extras=["web-design"])
        defaults.pop("web_design")
        defaults_path.write_text(json.dumps(defaults), encoding="utf-8")
        (self.target / "docs").mkdir(parents=True)
        (self.target / "docs/design").write_bytes(b"Existing file marker.\n")
        with self.assertRaisesRegex(NotADirectoryError, "directory"):
            self.plan(extras=["web-design"])
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertEqual((self.target / "docs/design").read_bytes(), b"Existing file marker.\n")
        (self.target / "docs/design").unlink()
        original = install.is_link
        with patch.object(install, "is_link", side_effect=lambda p: p == self.target / "docs/design" or original(p)):
            with self.assertRaisesRegex(ValueError, "[Ll]ink"):
                self.plan(extras=["web-design"])

    def test_plain_html_workflow_is_explicit_scoped_and_read_only(self):
        self.target.mkdir(parents=True)
        (self.target / "index.html").write_text("<!doctype html><title>Website</title>", encoding="utf-8")
        self.apply(extras=["web-design"])
        before = {p.relative_to(self.target): p.read_bytes() for p in self.target.rglob("*") if p.is_file()}
        ordinary = context.select_context(self.target)
        self.assertNotIn("ai-kit/WEB-DESIGN.md", {item["path"] for item in ordinary["selected"]})
        report = context.select_context(self.target, workflow="web-design", budget=1)
        selected = {item["path"] for item in report["selected"]}
        self.assertTrue(set(DOCUMENTS).issubset(selected))
        self.assertIn("ai-kit/WEB-DESIGN.md", selected)
        self.assertNotIn("ai-kit/web-design/LARAVEL.md", selected)
        self.assertNotIn("ai-kit/web-design/TOOLS.md", selected)
        self.assertTrue(report["over_budget"])
        self.assertEqual(report["profiles"], [])
        review = context.select_context(self.target, workflow="ui-review")
        self.assertIn("ai-kit/web-design/REVIEW.md", {item["path"] for item in review["selected"]})
        self.assertEqual(before, {p.relative_to(self.target): p.read_bytes() for p in self.target.rglob("*") if p.is_file()})

    def test_declared_laravel_scope_selects_blade_guidance_without_sibling_leakage(self):
        self.apply(extras=["web-design"])
        facts = self.target / "ai-kit/project.json"
        facts.write_text(json.dumps({"schema": 1, "modules": [
            {"path": "/web/", "profiles": ["LARAVEL", "FRONTEND"]},
            {"path": "/worker/", "profiles": ["GO"]}]}), encoding="utf-8")
        report = context.select_context(self.target, path="web", workflow="web-design")
        selected = {item["path"] for item in report["selected"]}
        self.assertIn("ai-kit/web-design/LARAVEL.md", selected)
        self.assertIn(".agents/skills/laravel-blade-ui/SKILL.md", selected)
        self.assertIn("ai-kit/profiles/OWNER.md", selected)
        worker = context.select_context(self.target, path="worker", workflow="web-design")
        self.assertNotIn("ai-kit/web-design/LARAVEL.md", {item["path"] for item in worker["selected"]})
        with self.assertRaisesRegex(ValueError, "Unknown context workflow"):
            context.select_context(self.target, workflow="unknown")
        (self.target / "ai-kit/web-design/TOOLS.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing required context"):
            context.select_context(self.target, workflow="design-extract")

    def test_cli_preview_is_available_without_applying_or_creating_a_target(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(install, "ROOT", self.source):
            self.assertEqual(install.main([str(self.target), "--with-web-design"]), 0)
        self.assertIn("web-design", json.loads(output.getvalue())["extras"])
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
