"""Exercise manifest-evidence snapshots and doctor freshness warnings."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import context
import doctor
import install


class ContextFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-context-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def write(self, relative, data):
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")

    def apply(self):
        plan = install.build_plan(self.target, root=self.source)
        self.assertTrue(install.apply_plan(plan))

    def test_fresh_install_captures_manifest_evidence(self):
        self.write("go.mod", "module example.test/project\n\ngo 1.23\n")
        self.apply()
        project = json.loads((self.target / "ai-kit/project.json").read_text(encoding="utf-8"))
        self.assertEqual(project["evidence"]["schema"], 1)
        self.assertIn("go.mod", project["evidence"]["modules"][0]["manifests"])
        report = doctor.examine(self.target, root=self.source)
        self.assertFalse(any("evidence" in warning for warning in report["warnings"]))

    def test_changed_manifest_and_new_module_are_reported(self):
        self.write("go.mod", "module example.test/project\n\ngo 1.23\n")
        self.apply()
        self.write("go.mod", "module example.test/project\n\ngo 1.24\n")
        self.write("api/pyproject.toml", '[project]\nname = "api"\nrequires-python = ">=3.10"\n')
        warnings = doctor.examine(self.target, root=self.source)["warnings"]
        self.assertTrue(any("Manifest evidence changed at /" in warning for warning in warnings))
        self.assertTrue(any("Detected module missing from project facts: /api/" in warning for warning in warnings))

    def test_changed_detected_command_is_reported(self):
        self.write("package.json", '{"scripts": {"test": "vitest"}}\n')
        self.apply()
        self.write("package.json", '{"scripts": {"lint": "eslint ."}}\n')
        warnings = doctor.examine(self.target, root=self.source)["warnings"]
        self.assertTrue(any("Detected commands changed at /" in warning for warning in warnings))

    def test_snapshot_preserves_project_facts_and_refreshes_evidence_only_on_apply(self):
        self.write("go.mod", "module example.test/project\n\ngo 1.23\n")
        self.apply()
        self.write("go.mod", "module example.test/project\n\ngo 1.24\n")
        before = json.loads((self.target / "ai-kit/project.json").read_text(encoding="utf-8"))
        plan = context.snapshot_plan(self.target)
        self.assertTrue(plan["changed"])
        self.assertEqual(json.loads(plan["data"])["modules"], before["modules"])
        self.assertTrue(context.apply_snapshot(plan))
        report = doctor.examine(self.target, root=self.source)
        self.assertFalse(any("Manifest evidence changed" in warning for warning in report["warnings"]))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(context.main(["snapshot", str(self.target)]), 0)


if __name__ == "__main__":
    unittest.main()
