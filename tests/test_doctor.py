"""Exercise the installed-project health check."""
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


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-doctor-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project with spaces"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        self.initial_version = (self.source / "VERSION").read_text(encoding="utf-8").strip()

    def apply(self, **options):
        plan = install.build_plan(self.target, root=self.source, **options)
        self.assertTrue(install.apply_plan(plan))
        return plan

    def write(self, path, data):
        destination = self.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    def examine(self):
        return doctor.examine(self.target, root=self.source)

    def test_healthy_installation_reports_no_errors_or_warnings(self):
        self.apply()
        # Runtime experiment notes are private data, not managed instruction/link sources.
        self.write("ai-kit/.metrics/private-notes.md", b"[Runtime reference](missing.md)\n\xff")
        report = self.examine()
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["installed_version"], self.initial_version)

    def test_module_map_drift_is_reported(self):
        self.write("go.mod", b"module example.test/app\n\ngo 1.21\n")
        self.apply()
        report = self.examine()
        self.assertFalse(any("module maps differ" in warning for warning in report["warnings"]))
        project = json.loads((self.target / "ai-kit/project.json").read_text(encoding="utf-8"))
        project["modules"][0]["path"] = "/api/"
        (self.target / "ai-kit/project.json").write_text(json.dumps(project) + "\n", encoding="utf-8")
        report = self.examine()
        self.assertTrue(any("module maps differ" in warning for warning in report["warnings"]))

    def test_user_edits_to_client_settings_are_not_reported(self):
        self.apply(agents=["claude"], extras=["guards", "session-start"])
        path = self.target / ".claude/settings.local.json"
        settings = json.loads(path.read_text(encoding="utf-8"))
        settings["model"] = "user-choice"
        path.write_text(json.dumps(settings) + "\n", encoding="utf-8")
        self.assertEqual(self.examine()["warnings"], [])

    def test_removed_managed_client_entry_is_reported(self):
        self.apply(agents=["claude"], extras=["guards"])
        path = self.target / ".claude/settings.local.json"
        settings = json.loads(path.read_text(encoding="utf-8"))
        settings["permissions"]["ask"].remove("Bash(git push *)")
        path.write_text(json.dumps(settings) + "\n", encoding="utf-8")
        self.assertIn("AI-KIT entry missing from .claude/settings.local.json: permissions.ask Bash(git push *)",
                      self.examine()["warnings"])
        path.write_text("[]\n", encoding="utf-8")
        self.assertTrue(any(w.startswith("Cannot read AI-KIT entries") for w in self.examine()["warnings"]))

    def test_missing_installation_is_reported(self):
        self.target.mkdir(parents=True)
        report = self.examine()
        self.assertTrue(any("No installer state" in error for error in report["errors"]))

    def test_modified_managed_file_is_reported(self):
        self.apply()
        self.write("ai-kit/CORE.md", b"Locally edited core\n")
        report = self.examine()
        self.assertTrue(any("Modified after installation" in warning and "ai-kit/CORE.md" in warning
                            for warning in report["warnings"]))

    def test_accepted_local_adaptation_is_not_a_modification_warning(self):
        self.apply()
        self.write("ai-kit/CORE.md", b"Reviewed semantic merge\n")
        self.apply(accept_local=["ai-kit/CORE.md"])
        report = self.examine()
        self.assertEqual(report["errors"], [])
        self.assertFalse(any("Modified after installation" in warning for warning in report["warnings"]))

    def test_missing_owned_document_is_reported(self):
        self.apply()
        (self.target / "WIKI.md").unlink()
        report = self.examine()
        self.assertTrue(any("Owned project document missing: WIKI.md" in warning
                            for warning in report["warnings"]))

    def test_broken_kit_link_is_reported(self):
        self.apply()
        self.write("WIKI.md", b"[Missing](no-such-file.md)\n")
        report = self.examine()
        self.assertTrue(any("missing link" in warning and "WIKI.md" in warning
                            for warning in report["warnings"]))

    def test_stale_provider_verification_is_reported(self):
        self.apply()
        provider = self.target / "ai-kit" / "router" / "providers" / "openai.json"
        config = json.loads(provider.read_text(encoding="utf-8"))
        config["verified_documentation_date"] = "2025-01-01"
        provider.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        report = self.examine()
        self.assertTrue(any("older than" in warning for warning in report["warnings"]))

    def test_main_returns_one_when_errors_exist(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(doctor.main([str(self.target), "--root", str(self.source)]), 1)

    def test_main_returns_zero_for_healthy_installation(self):
        self.apply()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(doctor.main([str(self.target), "--root", str(self.source)]), 0)

    def test_fix_restores_missing_managed_file(self):
        self.apply()
        (self.target / "ai-kit/CORE.md").unlink()
        self.assertTrue(any("Missing managed file: ai-kit/CORE.md" in error
                            for error in self.examine()["errors"]))
        with contextlib.redirect_stdout(io.StringIO()):
            code = doctor.main([str(self.target), "--root", str(self.source), "--fix"])
        self.assertEqual(code, 0)
        self.assertTrue((self.target / "ai-kit/CORE.md").is_file())
        self.assertEqual(self.examine()["errors"], [])

    def test_fix_is_a_noop_for_a_healthy_installation(self):
        self.apply()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(doctor.main([str(self.target), "--root", str(self.source), "--fix"]), 0)


if __name__ == "__main__":
    unittest.main()
