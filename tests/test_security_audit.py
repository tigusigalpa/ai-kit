"""Pinned optional skill installation, client policy, and conservative upgrades."""
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


class SecurityAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-security-audit-")
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

    def package_path(self, name, *, source=False):
        root = self.source / "template" if source else self.target
        return root / install.SECURITY_AUDIT_PACKAGE / name

    def update_fixture_pin(self, name, data):
        """Model a reviewed upstream update inside a disposable distribution."""
        self.package_path(name, source=True).write_bytes(data)
        manifest_path = self.source / install.SECURITY_AUDIT_MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["revision"] = "f" * 40
        record = manifest["files"][name]
        record.update(size=len(data), sha256=install.digest(data),
                      git_blob=hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data,
                                            usedforsecurity=False).hexdigest())
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    def test_every_preset_leaves_the_skill_absent_until_opted_in(self):
        for preset in (None, *install.PRESETS):
            with self.subTest(preset=preset):
                plan = self.plan(preset=preset, agents=["codex", "claude"])
                self.assertNotIn("security-audit", plan["extras"])
                self.assertFalse(any("/security-audit/" in path for path in plan["actions"]))
                self.assertNotIn(b"../.agents/skills/security-audit/SKILL.md",
                                 plan["actions"]["ai-kit/SKILLS.md"]["data"])
        self.apply()
        self.assertFalse((self.target / install.SECURITY_AUDIT_SKILL).exists())
        self.assertFalse((self.target / install.SECURITY_AUDIT_PACKAGE).exists())
        self.assertEqual(doctor.link_warnings(self.target), [])

    def test_preview_and_apply_need_no_network_node_or_audit_execution(self):
        with patch("subprocess.Popen", side_effect=AssertionError("No processes during installation")), \
                patch("socket.socket", side_effect=AssertionError("Offline installation")):
            plan = self.plan(extras=["security-audit"])
            self.assertFalse(self.target.exists())
            self.assertIn("security-audit", plan["extras"])
            self.assertTrue(install.apply_plan(plan))
        manifest = json.loads(self.package_path("UPSTREAM.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["revision"], "c1c8a8c1471069fb0e188eeaff69b8e8db6564a8")
        self.assertIn(b"Cloudflare", self.package_path("LICENSE").read_bytes())
        for name, record in manifest["files"].items():
            if install.UPSTREAM_TEST_FILE.search(name):
                # Upstream tests are verified at source but never installed into projects.
                self.assertFalse(self.package_path(name).exists())
                continue
            self.assertEqual(install.digest(self.package_path(name).read_bytes()), record["sha256"])
        self.assertFalse(any(self.target.rglob("findings.json")))
        self.assertFalse(any(self.target.rglob("coverage-ledger.json")))

    def test_client_entry_points_are_manual_and_links_survive_installation(self):
        self.apply(extras=["security-audit"], agents=["codex", "claude"])
        source_entry = self.target / install.SECURITY_AUDIT_SKILL / "SKILL.md"
        native_entry = self.target / ".claude/skills/security-audit/SKILL.md"
        source_text = source_entry.read_text(encoding="utf-8")
        native_text = native_entry.read_text(encoding="utf-8")
        self.assertLess(source_entry.stat().st_size, 2500)
        self.assertEqual(native_text.replace("disable-model-invocation: true\n", "", 1), source_text)
        policy = (self.target / install.SECURITY_AUDIT_SKILL / "agents/openai.yaml").read_text()
        self.assertEqual([line.strip() for line in policy.splitlines()],
                         ["policy:", "allow_implicit_invocation: false"])
        self.assertEqual((self.target / ".claude/skills/security-audit/agents/openai.yaml").read_text(), policy)
        self.assertEqual(doctor.link_warnings(self.target), [])
        self.assertEqual(doctor.examine(self.target, root=self.source)["errors"], [])

    def test_selection_persists_and_presets_keep_the_explicit_choice(self):
        self.apply(extras=["security-audit"], agents=["codex", "claude"])
        self.assertEqual(self.plan()["actions"], {})
        plan = self.apply(preset="minimal")
        self.assertEqual(plan["extras"], ["security-audit"])
        settings = json.loads((self.target / "ai-kit/settings.json").read_text())
        self.assertIs(settings["security_audit"], True)
        self.assertEqual(self.plan()["actions"], {})

    def test_local_changes_survive_reruns_and_updated_pins_become_conflicts(self):
        self.apply(extras=["security-audit"])
        entry = self.target / install.SECURITY_AUDIT_SKILL / "SKILL.md"
        entry.write_bytes(entry.read_bytes() + b"\nLocal project guidance.\n")
        local = self.package_path("ATTACK-CLASSES.md")
        local.write_bytes(local.read_bytes() + b"\nLocal reviewed adaptation.\n")
        self.assertEqual(self.plan()["conflicts"], {})
        self.assertEqual(self.plan()["actions"], {})
        previous_state = (self.target / "ai-kit/.install-state.json").read_bytes()
        previous_pin = self.package_path("UPSTREAM.json").read_bytes()
        previous_local = local.read_bytes()
        updated = self.package_path("ATTACK-CLASSES.md", source=True).read_bytes() + b"\nUpstream change.\n"
        self.update_fixture_pin("ATTACK-CLASSES.md", updated)
        plan = self.plan()
        relative = install.SECURITY_AUDIT_PACKAGE + "ATTACK-CLASSES.md"
        self.assertIn(relative, plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(local.read_bytes(), previous_local)
        self.assertEqual(self.package_path("UPSTREAM.json").read_bytes(), previous_pin)
        self.assertEqual((self.target / "ai-kit/.install-state.json").read_bytes(), previous_state)
        self.assertEqual((self.target / plan["candidates"][relative]["path"]).read_bytes(), updated)

    def test_unchanged_package_follows_a_reviewed_pin_update(self):
        self.apply(extras=["security-audit"])
        old = self.package_path("ATTACK-CLASSES.md").read_bytes()
        updated = old + b"\nReviewed upstream change.\n"
        self.update_fixture_pin("ATTACK-CLASSES.md", updated)
        self.apply()
        self.assertEqual(self.package_path("ATTACK-CLASSES.md").read_bytes(), updated)
        self.assertEqual(json.loads(self.package_path("UPSTREAM.json").read_text())["revision"], "f" * 40)
        self.assertTrue(any(path.read_bytes() == old
                            for path in (self.target / "ai-kit/.upstream-cache/backups").rglob("ATTACK-CLASSES.md")))
        self.assertEqual(self.plan()["actions"], {})

    def test_existing_untracked_entry_is_a_conflict_and_is_not_overwritten(self):
        entry = self.target / install.SECURITY_AUDIT_SKILL / "SKILL.md"
        entry.parent.mkdir(parents=True)
        entry.write_bytes(b"Existing project skill.\n")
        plan = self.plan(extras=["security-audit"])
        self.assertIn(install.SECURITY_AUDIT_SKILL + "SKILL.md", plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual(entry.read_bytes(), b"Existing project skill.\n")
        self.assertFalse(self.package_path("UPSTREAM.json").exists())

    def test_deselecting_stops_management_and_preserves_existing_files(self):
        self.apply(extras=["security-audit"])
        settings_path = self.target / "ai-kit/settings.json"
        settings = json.loads(settings_path.read_text())
        settings["security_audit"] = False
        settings_path.write_text(json.dumps(settings) + "\n", encoding="utf-8")
        previous = self.package_path("SKILL.md").read_bytes()
        plan = self.apply()
        self.assertNotIn("security-audit", plan["extras"])
        self.assertEqual(self.package_path("SKILL.md").read_bytes(), previous)
        self.assertTrue(any("Previously managed path retained" in warning
                            and "security-audit" in warning for warning in plan["warnings"]))
        self.assertEqual(doctor.link_warnings(self.target), [])

    def test_native_retirement_requires_review_and_keeps_baseline(self):
        self.apply(extras=["security-audit"], agents=["codex", "claude"])
        state = (self.target / "ai-kit/.install-state.json").read_bytes()
        plan = self.plan(agents=["codex"])
        self.assertIn(".claude/skills/security-audit/SKILL.md", plan["adapter_conflicts"])
        self.assertIn(".claude/skills/security-audit/agents/openai.yaml", plan["adapter_conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual((self.target / "ai-kit/.install-state.json").read_bytes(), state)

    def test_corrupted_upstream_is_refused_before_any_target_write(self):
        self.package_path("SKILL.md", source=True).write_bytes(b"Changed upstream instructions.\n")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            self.plan(extras=["security-audit"])
        self.assertFalse(self.target.exists())
        self.assertNotIn("security-audit", self.plan()["extras"])

    def test_unlisted_upstream_files_and_unsafe_manifest_names_are_refused(self):
        extra = self.package_path("extra.cjs", source=True)
        extra.write_bytes(b"Unreviewed extra file.\n")
        with self.assertRaisesRegex(ValueError, "differ from the manifest"):
            self.plan(extras=["security-audit"])
        extra.unlink()
        manifest_path = self.source / install.SECURITY_AUDIT_MANIFEST
        manifest = json.loads(manifest_path.read_text())
        for name in ("../../escape", "UPSTREAM.json", "license"):
            with self.subTest(name=name):
                changed = dict(manifest, files=dict(manifest["files"], **{name: manifest["files"]["LICENSE"]}))
                manifest_path.write_text(json.dumps(changed) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Unsafe.*filename"):
                    self.plan(extras=["security-audit"])
        self.assertFalse(self.target.exists())

    def test_linked_source_and_target_package_paths_are_refused(self):
        original = install.is_link
        source = self.package_path("SKILL.md", source=True)
        with patch.object(install, "is_link", side_effect=lambda path: path == source or original(path)):
            with self.assertRaisesRegex(ValueError, "[Ll]ink"):
                self.plan(extras=["security-audit"])
        target = self.target / install.SECURITY_AUDIT_PACKAGE.rstrip("/")
        with patch.object(install, "is_link", side_effect=lambda path: path == target or original(path)):
            with self.assertRaisesRegex(ValueError, "[Ll]ink"):
                self.plan(extras=["security-audit"])
        self.assertFalse(self.target.exists())

    def test_invalid_settings_and_manifest_metadata_are_refused(self):
        defaults = json.loads((self.source / "template/ai-kit/settings.json").read_text())
        defaults["security_audit"] = "true"
        with self.assertRaisesRegex(ValueError, "must be a boolean"):
            install.validate_settings(defaults)
        manifest_path = self.source / install.SECURITY_AUDIT_MANIFEST
        original = json.loads(manifest_path.read_text())
        for field, value in (("revision", "main"), ("schema", True), ("license", "unknown")):
            with self.subTest(field=field):
                changed = dict(original, **{field: value})
                manifest_path.write_text(json.dumps(changed) + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.plan(extras=["security-audit"])
        manifest_path.write_text(json.dumps(original) + "\n", encoding="utf-8")
        original["files"]["LICENSE"]["git_mode"] = []
        manifest_path.write_text(json.dumps(original) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid.*record"):
            self.plan(extras=["security-audit"])
        self.assertFalse(self.target.exists())

    def test_cli_flag_previews_the_opt_in_package(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(install.main([str(self.target), "--with-security-audit"]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["extras"], ["security-audit"])
        self.assertIn(install.SECURITY_AUDIT_PACKAGE + "LICENSE", report["writes"])
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
