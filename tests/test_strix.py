"""Optional Strix references install offline without starting the active runtime."""
from __future__ import annotations

import contextlib
import hashlib
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

PACKAGE = "ai-kit/vendor/strix/"
ENTRY = ".agents/skills/strix/"
REFERENCE = "penetration-testing-with-strix/SKILL.md"


class StrixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-strix-")
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

    def package(self, filename, *, source=False):
        root = self.source / "template" if source else self.target
        return root / PACKAGE / filename

    def manifest(self):
        return json.loads((self.source / "integrations/strix.json").read_text(encoding="utf-8"))

    def write_manifest(self, value):
        (self.source / "integrations/strix.json").write_text(json.dumps(value) + "\n", encoding="utf-8")

    def update_pin(self, data):
        self.package(REFERENCE, source=True).write_bytes(data)
        manifest = self.manifest()
        manifest["revision"] = "f" * 40
        manifest["files"][REFERENCE].update(
            size=len(data), sha256=install.digest(data),
            git_blob=hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data,
                                  usedforsecurity=False).hexdigest())
        self.write_manifest(manifest)

    def test_default_and_every_preset_omit_runtime_skill_and_payload(self):
        for preset in (None, *install.PRESETS):
            with self.subTest(preset=preset):
                plan = self.plan(preset=preset, agents=["codex", "claude"])
                self.assertNotIn("strix", plan["extras"])
                self.assertFalse(any("/strix/" in path for path in plan["actions"]))
                self.assertNotIn(b"../.agents/skills/strix/SKILL.md", plan["actions"]["ai-kit/SKILLS.md"]["data"])
        self.apply()
        self.assertFalse((self.target / ENTRY).exists())
        self.assertFalse((self.target / PACKAGE).exists())
        self.assertEqual(doctor.link_warnings(self.target), [])

    def test_install_is_offline_process_free_and_preserves_the_complete_pin(self):
        with patch("subprocess.Popen", side_effect=AssertionError("Installation must start no runtime")), \
                patch("socket.socket", side_effect=AssertionError("Installation must stay offline")):
            plan = self.plan(extras=["strix"], agents=["codex", "claude"])
            self.assertFalse(self.target.exists())
            self.assertTrue(install.apply_plan(plan))
        pin = json.loads(self.package("UPSTREAM.json").read_text())
        self.assertEqual(pin, self.manifest())
        self.assertEqual(pin["revision"], "f7a32ae62d94872631bc8415073868d02a6ffdaf")
        self.assertEqual(len(pin["files"]), 10)
        self.assertEqual(pin["license"], "Apache-2.0")
        for filename, record in pin["files"].items():
            self.assertEqual(install.digest(self.package(filename).read_bytes()), record["sha256"])
        source_entry = self.target / ENTRY / "SKILL.md"
        native_entry = self.target / ".claude/skills/strix/SKILL.md"
        self.assertLess(source_entry.stat().st_size, 2500)
        self.assertEqual(native_entry.read_text().replace("disable-model-invocation: true\n", "", 1),
                         source_entry.read_text())
        policy = (self.target / ENTRY / "agents/openai.yaml").read_text()
        self.assertEqual([line.strip() for line in policy.splitlines()],
                         ["policy:", "allow_implicit_invocation: false"])
        self.assertEqual((native_entry.parent / "agents/openai.yaml").read_text(), policy)
        self.assertFalse(any((self.target / ".agents/skills").glob("*-with-strix")))
        self.assertFalse(any((self.target / ".claude/skills").glob("*-with-strix")))
        self.assertFalse((self.target / "strix_runs").exists())
        self.assertEqual(doctor.link_warnings(self.target), [])
        self.assertEqual(doctor.examine(self.target, root=self.source)["errors"], [])

    def test_choices_are_independent_and_persist_outside_presets(self):
        for name, other in (("strix", "security-audit"), ("security-audit", "strix")):
            with self.subTest(name=name):
                plan = self.plan(extras=[name])
                self.assertFalse(any("/" + other + "/" in path for path in plan["actions"]))
        self.apply(extras=["strix", "security-audit"])
        self.assertEqual(self.plan()["actions"], {})
        self.apply(preset="minimal")
        self.assertEqual(self.plan()["extras"], ["security-audit", "strix"])
        settings = json.loads((self.target / "ai-kit/settings.json").read_text())
        self.assertIs(settings["strix"], True)
        self.assertIs(settings["security_audit"], True)
        self.assertEqual(self.plan()["actions"], {})

    def test_nested_local_edits_survive_and_new_pins_preserve_conflicts(self):
        self.apply(extras=["strix"])
        entry = self.target / ENTRY / "SKILL.md"
        entry.write_bytes(entry.read_bytes() + b"\nLocal guidance.\n")
        local = self.package(REFERENCE)
        local.write_bytes(local.read_bytes() + b"\nReviewed project adaptation.\n")
        self.assertEqual(self.plan()["actions"], {})
        self.assertEqual(self.plan()["conflicts"], {})
        old_state = (self.target / "ai-kit/.install-state.json").read_bytes()
        old_pin, old_local = self.package("UPSTREAM.json").read_bytes(), local.read_bytes()
        new = self.package(REFERENCE, source=True).read_bytes() + b"\nReviewed upstream change.\n"
        self.update_pin(new)
        plan = self.plan()
        relative = PACKAGE + REFERENCE
        self.assertIn(relative, plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(local.read_bytes(), old_local)
        self.assertEqual(self.package("UPSTREAM.json").read_bytes(), old_pin)
        self.assertEqual((self.target / "ai-kit/.install-state.json").read_bytes(), old_state)
        self.assertEqual((self.target / plan["candidates"][relative]["path"]).read_bytes(), new)

    def test_unchanged_nested_reference_updates_with_backup(self):
        self.apply(extras=["strix"])
        old = self.package(REFERENCE).read_bytes()
        new = old + b"\nReviewed upstream change.\n"
        self.update_pin(new)
        self.apply()
        self.assertEqual(self.package(REFERENCE).read_bytes(), new)
        self.assertEqual(json.loads(self.package("UPSTREAM.json").read_text())["revision"], "f" * 40)
        self.assertTrue(any(p.read_bytes() == old for p in
                            (self.target / "ai-kit/.upstream-cache/backups").rglob("SKILL.md")))
        self.assertEqual(self.plan()["actions"], {})

    def test_existing_entry_conflicts_before_any_payload_is_written(self):
        entry = self.target / ENTRY / "SKILL.md"
        entry.parent.mkdir(parents=True)
        entry.write_bytes(b"Existing project skill.\n")
        plan = self.plan(extras=["strix"])
        self.assertIn(ENTRY + "SKILL.md", plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(entry.read_bytes(), b"Existing project skill.\n")
        self.assertFalse(self.package("UPSTREAM.json").exists())

    def test_deselection_retains_files_and_native_retirement_still_requires_review(self):
        self.apply(extras=["strix"], agents=["codex", "claude"])
        plan = self.plan(agents=["codex"])
        self.assertIn(".claude/skills/strix/SKILL.md", plan["adapter_conflicts"])
        self.assertFalse(install.apply_plan(plan))
        settings_path = self.target / "ai-kit/settings.json"
        settings = json.loads(settings_path.read_text())
        settings["strix"] = False
        settings_path.write_text(json.dumps(settings) + "\n", encoding="utf-8")
        old = self.package(REFERENCE).read_bytes()
        plan = self.apply()
        self.assertNotIn("strix", plan["extras"])
        self.assertEqual(self.package(REFERENCE).read_bytes(), old)
        self.assertTrue(any("Previously managed path retained" in warning and "/strix/" in warning
                            for warning in plan["warnings"]))
        self.assertEqual(doctor.link_warnings(self.target), [])

    def test_invalid_metadata_and_corrupt_bytes_are_refused_without_writes(self):
        original = self.manifest()
        for field, value in (("schema", True), ("revision", "main"), ("repository", "https://example.com"),
                             ("license", "MIT"), ("source_directory", "strix")):
            with self.subTest(field=field):
                self.write_manifest(dict(original, **{field: value}))
                with self.assertRaisesRegex(ValueError, "upstream identity"):
                    self.plan(extras=["strix"])
        self.write_manifest(original)
        self.package(REFERENCE, source=True).write_bytes(b"Corrupt reference.\n")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            self.plan(extras=["strix"])
        self.assertNotIn("strix", self.plan()["extras"])
        defaults = json.loads((self.source / "template/ai-kit/settings.json").read_text())
        defaults["strix"] = "true"
        with self.assertRaisesRegex(ValueError, "must be a boolean"):
            install.validate_settings(defaults)
        self.assertFalse(self.target.exists())

    def test_nested_traversal_reserved_names_and_directory_aliases_are_refused(self):
        original = self.manifest()
        for filename in ("../escape", "extra/../../escape", "extra\\SKILL.md", "C:/escape", "UPSTREAM.json",
                         "CON.md", "folder./file.md", "Penetration-testing-with-strix/extra.md"):
            with self.subTest(filename=filename):
                changed = dict(original, files=dict(original["files"], **{filename: original["files"]["LICENSE"]}))
                self.write_manifest(changed)
                with self.assertRaisesRegex(ValueError, "Unsafe.*filename"):
                    self.plan(extras=["strix"])
        self.assertFalse(self.target.exists())

    def test_unlisted_nested_files_and_missing_skills_are_refused(self):
        directory = self.package("unlisted", source=True)
        directory.mkdir()
        with self.assertRaisesRegex(ValueError, "differ from the manifest"):
            self.plan(extras=["strix"])
        directory.rmdir()
        extra = self.package("penetration-testing-with-strix/extra.md", source=True)
        extra.write_bytes(b"Unlisted reference.\n")
        with self.assertRaisesRegex(ValueError, "differ from the manifest"):
            self.plan(extras=["strix"])
        extra.unlink()
        self.package("api-security-testing/SKILL.md", source=True).unlink()
        with self.assertRaisesRegex(ValueError, "differ from the manifest"):
            self.plan(extras=["strix"])
        self.assertFalse(self.target.exists())

    def test_linked_source_directory_and_target_ancestor_are_refused(self):
        original = install.is_link
        paths = (self.package(REFERENCE, source=True).parent, self.package(REFERENCE).parent,
                 self.source / "integrations/strix.json")
        for linked in paths:
            with self.subTest(linked=linked), patch.object(
                    install, "is_link", side_effect=lambda path: path == linked or original(path)):
                with self.assertRaisesRegex(ValueError, "[Ll]ink"):
                    self.plan(extras=["strix"])
        self.assertFalse(self.target.exists())

    def test_cli_flag_selects_strix_without_selecting_cloudflare_or_scanning(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(install.main([str(self.target), "--with-strix"]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["extras"], ["strix"])
        self.assertIn(PACKAGE + "LICENSE", report["writes"])
        self.assertFalse(any("/security-audit/" in path for path in report["writes"]))
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
