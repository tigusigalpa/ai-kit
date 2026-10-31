"""Refuse accidental downgrades and point doctor users to the upgrade commands."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor
import install

VERSION = (install.ROOT / "VERSION").read_text(encoding="utf-8").strip()


class UpgradeGuardTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="ai-kit-upgrade-")
        self.addCleanup(temp.cleanup)
        self.target = Path(temp.name).resolve() / "app"
        self.assertTrue(install.apply_plan(install.build_plan(self.target)))
        self.state_path = self.target / "ai-kit/.install-state.json"

    def record_version(self, version: str) -> None:
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        state["accepted_version"] = version
        self.state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def recorded_version(self) -> str:
        return json.loads(self.state_path.read_text(encoding="utf-8"))["accepted_version"]

    def test_versions_compare_numerically(self):
        self.assertTrue(install.is_downgrade("1.10.0", "1.9.9"))
        self.assertTrue(install.is_downgrade("2.0.0", "1.4.7"))
        self.assertFalse(install.is_downgrade("1.4.7", "1.4.7"))
        self.assertFalse(install.is_downgrade("1.4.6", "1.4.7"))
        for value in ("1.4", "v1.4.7", "1.4.7rc1", None, ""):
            self.assertIsNone(install.version_key(value))
            self.assertFalse(install.is_downgrade(value, "1.0.0"))

    def test_newer_installation_is_previewed_and_refused(self):
        self.record_version("99.0.0")
        plan = install.build_plan(self.target)
        self.assertEqual(plan["downgrade_from"], "99.0.0")
        self.assertTrue(any("newer than this installer" in warning and "--allow-downgrade" in warning
                            for warning in plan["warnings"]))
        with self.assertRaisesRegex(ValueError, "Refusing to downgrade AI-KIT 99.0.0"):
            install.apply_plan(plan)
        self.assertEqual(self.recorded_version(), "99.0.0")
        allowed = install.build_plan(self.target, allow_downgrade=True)
        self.assertTrue(install.apply_plan(allowed))
        self.assertEqual(self.recorded_version(), VERSION)

    def test_cli_refuses_downgrade_unless_allowed(self):
        self.record_version("99.0.0")
        errors = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
            self.assertEqual(install.main([str(self.target), "--apply"]), 1)
        self.assertIn("Refusing to downgrade", errors.getvalue())
        self.assertEqual(self.recorded_version(), "99.0.0")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main([str(self.target), "--apply", "--allow-downgrade"]), 0)
        self.assertEqual(self.recorded_version(), VERSION)

    def test_doctor_warns_about_newer_installation_and_refuses_fix(self):
        self.record_version("99.0.0")
        report = doctor.examine(self.target)
        self.assertTrue(any("newer than this CLI" in warning for warning in report["warnings"]))
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(doctor.main([str(self.target), "--fix"]), 0)
        self.assertTrue(any("newer than this installer" in warning
                            for warning in json.loads(output.getvalue())["fix"]["warnings"]))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
            self.assertEqual(doctor.main([str(self.target), "--fix", "--apply"]), 1)
        self.assertIn("Refusing to downgrade", errors.getvalue())

    def test_doctor_suggests_upgrade_commands_for_older_installation(self):
        self.record_version("0.0.1")
        report = doctor.examine(self.target)
        hint = [line for line in report["info"] if "is available for this project" in line]
        self.assertEqual(len(hint), 1)
        self.assertIn("`aikit install .`", hint[0])
        self.assertIn("`aikit install . --apply --check`", hint[0])
        self.assertEqual(report["warnings"], [])
        plan = install.build_plan(self.target)
        self.assertIsNone(plan["downgrade_from"])


if __name__ == "__main__":
    unittest.main()
