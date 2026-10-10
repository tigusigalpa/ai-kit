"""Exercise adapter documentation reporting and conservative retirement."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adapters
import install


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-adapters-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def apply(self, **options):
        plan = install.build_plan(self.target, root=self.source, **options)
        self.assertTrue(install.apply_plan(plan))
        return plan

    def test_report_exposes_documentation_and_runtime_boundaries(self):
        self.apply(agents=["codex", "cursor"])
        report = adapters.report(root=self.source, project=self.target)
        by_name = {item["client"]: item for item in report["clients"]}
        self.assertEqual(by_name["cursor"]["documentation_status"], "verified")
        self.assertEqual(by_name["cursor"]["activation"], "unverified")
        self.assertTrue(by_name["cursor"]["selected"])
        self.assertIn(".cursor/rules/ai-kit.mdc", by_name["cursor"]["managed_paths"])
        self.assertEqual(by_name["kimi"]["documentation_status"], "unverified")

    def test_retire_removes_only_unchanged_owned_files_and_updates_state(self):
        self.apply(agents=["codex", "cursor"])
        plan = adapters.retirement_plan(self.target, "cursor", root=self.source)
        paths = {item["path"] for item in plan["removals"]}
        self.assertIn(".cursor/rules/ai-kit.mdc", paths)
        self.assertTrue(any("deselected" in warning for warning in plan["warnings"]))
        self.assertTrue(adapters.apply_retirement(plan))
        self.assertFalse((self.target / ".cursor/rules/ai-kit.mdc").exists())
        backup = self.target / next(item["backup"] for item in plan["removals"]
                                    if item["path"] == ".cursor/rules/ai-kit.mdc")
        self.assertTrue(backup.is_file())
        state = json.loads((self.target / "ai-kit/.install-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["agents"], ["codex"])
        rerun = install.build_plan(self.target, root=self.source, agents=["codex"])
        self.assertFalse(rerun["adapter_conflicts"])

    def test_retire_refuses_modified_adapter_and_preserves_state(self):
        self.apply(agents=["codex", "cursor"])
        path = self.target / ".cursor/rules/ai-kit.mdc"
        path.write_text(path.read_text(encoding="utf-8") + "Local note.\n", encoding="utf-8")
        plan = adapters.retirement_plan(self.target, "cursor", root=self.source)
        self.assertIn(".cursor/rules/ai-kit.mdc", plan["conflicts"])
        self.assertFalse(adapters.apply_retirement(plan))
        self.assertTrue(path.is_file())
        state = json.loads((self.target / "ai-kit/.install-state.json").read_text(encoding="utf-8"))
        self.assertIn("cursor", state["agents"])

    def test_report_and_retire_preserve_a_file_blocking_adapter_directory(self):
        self.apply(agents=["codex", "cline"])
        directory = self.target / ".clinerules"
        (directory / "ai-kit.md").unlink()
        directory.rmdir()
        directory.write_text("native data\n", encoding="utf-8")
        report = adapters.report(root=self.source, project=self.target)
        cline = next(item for item in report["clients"] if item["client"] == "cline")
        self.assertEqual(cline["blocked_paths"], [".clinerules/ai-kit.md"])
        plan = adapters.retirement_plan(self.target, "cline", root=self.source)
        self.assertEqual(plan["conflicts"], [".clinerules/ai-kit.md"])
        self.assertEqual(directory.read_text(encoding="utf-8"), "native data\n")

    def test_cli_report_and_retire_preview(self):
        self.apply(agents=["codex", "cursor"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(adapters.main(["report", "--project", str(self.target)]), 0)
        self.assertIn('"client": "cursor"', output.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(adapters.main(["retire", str(self.target), "--agent", "cursor"]), 0)
        self.assertTrue((self.target / ".cursor/rules/ai-kit.mdc").is_file())


if __name__ == "__main__":
    unittest.main()
