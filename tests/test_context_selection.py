"""Module-scoped instruction selection, immutable critical rules and byte-budget transparency."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import context
import install


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for name in ("AGENTS.md", "ai-kit/CORE.md", "ai-kit/settings.json", "PROJECT_CONTEXT.md",
                     "ai-kit/ENGINEERING.md", "ai-kit/SECURITY.md", "docs/DECISIONS.md",
                     "docs/adr/0001-module-boundary.md", "ai-kit/stacks/PYTHON.md", "ai-kit/stacks/GO.md"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"conventions": "owner"}) if name.endswith(".json") else "Rules: " + name, encoding="utf-8")
        (self.root / "ai-kit/project.json").write_text(json.dumps({"schema": 1, "modules": [
            {"path": "/api/", "profiles": ["PYTHON"]}, {"path": "/worker/", "profiles": ["GO"]}]}), encoding="utf-8")

    def test_only_matching_profiles_are_selected_and_no_file_is_changed(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        report = context.select_context(self.root, path="api/services")
        names = {item["path"] for item in report["selected"]}
        self.assertIn("ai-kit/stacks/PYTHON.md", names)
        self.assertNotIn("ai-kit/stacks/GO.md", names)
        self.assertIn("docs/adr/0001-module-boundary.md", names)
        self.assertEqual(report["modules"], ["/api/"])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_critical_context_survives_budget_and_duplicates_are_reported(self):
        (self.root / "ai-kit/ENGINEERING.md").write_bytes((self.root / "ai-kit/SECURITY.md").read_bytes())
        report = context.select_context(self.root, path="worker", budget=1)
        self.assertTrue(report["over_budget"])
        self.assertTrue(any(r["path"] == "ai-kit/CORE.md" for r in report["selected"]))
        self.assertEqual(len(report["duplicates"]), 1)
        self.assertEqual(report["total_bytes"], sum(r["bytes"] for r in report["selected"]))

    def test_unknown_scope_is_not_given_sibling_stack_facts(self):
        report = context.select_context(self.root, path="unknown")
        self.assertFalse(report["selection_complete"])
        self.assertEqual(report["profiles"], [])

    def test_nested_module_overrides_parent_stack_but_preserves_shared_requirements(self):
        path = self.root / "ai-kit/project.json"
        data = json.loads(path.read_text())
        data["modules"].append({"path": "/", "profiles": ["LARAVEL"]})
        path.write_text(json.dumps(data), encoding="utf-8")
        report = context.select_context(self.root, path="worker")
        self.assertEqual(report["profiles"], ["GO"])
        self.assertTrue(any(r["path"] == "ai-kit/SECURITY.md" for r in report["selected"]))

    def test_traversal_link_and_missing_profile_are_refused(self):
        for scope in ("../outside", "/api", "C:/outside"):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                context.select_context(self.root, path=scope)
        original = install.is_link
        with mock.patch.object(install, "is_link", side_effect=lambda p: p.name == "CORE.md" or original(p)):
            with self.assertRaises(ValueError):
                context.select_context(self.root, path="api")
        (self.root / "ai-kit/stacks/PYTHON.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing required"):
            context.select_context(self.root, path="api")
