"""Regressions for the v1.4.6 review fixes: line endings, read-only facts, doctor robustness and more."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aikit_cli
import check_kit
import context
import doctor
import install
import memory


def copy_reference(destination: Path) -> Path:
    shutil.copytree(install.ROOT, destination, ignore=shutil.ignore_patterns("__pycache__", ".git"))
    return destination


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-review-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project with spaces"
        self.target.mkdir()
        self.source = copy_reference(self.base / "reference")

    def plan(self, root=None, **options):
        return install.build_plan(self.target, root=root or self.source, **options)

    def apply(self, root=None, **options):
        plan = self.plan(root, **options)
        self.assertTrue(install.apply_plan(plan))
        return plan


class LineEndingTests(ProjectTestCase):
    def crlf_reference(self) -> Path:
        crlf = copy_reference(self.base / "crlf reference")
        for path in (crlf / "template").rglob("*"):
            if path.is_file() and "vendor" not in path.parts and path.suffix in {".md", ".json", ".sh", ".toml"}:
                path.write_bytes(install.as_lf(path.read_bytes()).replace(b"\n", b"\r\n"))
        return crlf

    def test_upgrade_from_crlf_bundle_rewrites_and_conflicts_nothing(self):
        crlf = self.crlf_reference()
        self.apply(root=crlf, agents=["codex", "claude"])
        core = self.target / "ai-kit/CORE.md"
        self.assertIn(b"\r\n", core.read_bytes())
        core.write_bytes(core.read_bytes() + b"Local note.\r\n")
        self.apply(root=crlf, accept_local=["ai-kit/CORE.md"])
        plan = self.plan()
        self.assertEqual(plan["conflicts"], {})
        self.assertEqual(sorted(plan["actions"]), ["ai-kit/.install-state.json"])
        self.assertIn("ai-kit/CORE.md", plan["preserved"])

    def test_untracked_identical_text_with_other_line_endings_is_accepted(self):
        source = (self.source / "template/ai-kit/CORE.md").read_bytes()
        (self.target / "ai-kit").mkdir()
        (self.target / "ai-kit/CORE.md").write_bytes(install.as_lf(source).replace(b"\n", b"\r\n"))
        plan = self.plan()
        self.assertNotIn("ai-kit/CORE.md", plan["conflicts"])
        self.assertNotIn("ai-kit/CORE.md", plan["actions"])


class ProjectFactTests(ProjectTestCase):
    def test_linked_manifest_inside_project_does_not_refuse_installation(self):
        write(self.target / "requirements/base.txt", "pytest\n")
        try:
            (self.target / "requirements.txt").symlink_to(Path("requirements/base.txt"))
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {exc}")
        facts = install.detect_facts(self.target)
        evidence = install.project_fact_evidence(self.target, facts)
        self.assertIn("requirements.txt", evidence["modules"][0]["manifests"])
        self.apply()

    def test_manifest_link_escaping_the_project_is_skipped(self):
        write(self.base / "outside/go.mod", "module example.test/outside\n")
        write(self.target / "go.mod", "module example.test/app\n")
        try:
            (self.target / "link.mod").symlink_to(self.base / "outside/go.mod")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {exc}")
        self.assertIsNone(install.readable_project_file(self.target, "link.mod"))
        self.assertIsNotNone(install.readable_project_file(self.target, "go.mod"))
        self.assertIsNone(install.readable_project_file(self.target, "../outside/go.mod"))

    @unittest.skipIf(os.name == "nt", "Colons are not valid in Windows file names")
    def test_module_directory_with_colon_does_not_refuse_installation(self):
        write(self.target / "svc:api/package.json", json.dumps({"scripts": {"test": "jest"}}))
        self.apply()

    def test_secondary_stacks_fill_gaps_without_overwriting_commands(self):
        write(self.target / "pyproject.toml", '[project]\nname = "svc"\n\n[tool.pytest.ini_options]\n\n[tool.ruff]\n')
        write(self.target / "main.tf", 'terraform {}\n')
        module = install.detect_facts(self.target)["modules"][0]
        self.assertEqual(module["commands"]["test"], "pytest")
        self.assertEqual(module["commands"]["lint"], "ruff check .")
        self.assertIn("INFRA", module["profiles"])

    def test_repository_wrapper_scripts_are_not_auto_allowed(self):
        rules = install.claude_allow_rules([{"commands": {"test": "./mvnw test", "build": "./gradlew build",
                                                           "lint": "go vet ./..."}}])
        self.assertEqual(rules, ["Bash(go vet ./... *)"])


class SecurityAuditPayloadTests(ProjectTestCase):
    def test_upstream_tests_are_verified_but_not_installed(self):
        payload = install.upstream_skill_files("security-audit", self.source)
        self.assertFalse(any(name.endswith(".test.cjs") for name in payload))
        self.assertTrue(any(name.endswith("validate-findings.cjs") for name in payload))
        test_file = next((self.source / "template/ai-kit/vendor/security-audit").glob("*.test.cjs"))
        test_file.write_bytes(test_file.read_bytes() + b"// tampered\n")
        with self.assertRaises(ValueError):
            install.upstream_skill_files("security-audit", self.source)


class DoctorRobustnessTests(ProjectTestCase):
    def test_non_utf8_markdown_and_private_memory_do_not_break_or_leak(self):
        self.apply()
        # A Cyrillic legacy document in a single-byte code page (escaped: project sources stay English).
        legacy = "".join(map(chr, (0x0414, 0x043E, 0x043A, 0x0443, 0x043C, 0x0435, 0x043D, 0x0442)))
        (self.target / "docs/legacy.md").write_bytes(legacy.encode("cp1251"))
        write(self.target / "ai-kit/.memory/s/exports/x/draft.md", "````\n```\n[x](secret-plan.md)\n````\n[y](leak.md)\n")
        write(self.target / "venv/lib/package/README.md", "[missing](nowhere.md)\n")
        warnings = doctor.examine(self.target, root=self.source)["warnings"]
        self.assertTrue(any("docs/legacy.md: not readable as UTF-8" in w for w in warnings))
        self.assertFalse(any("secret-plan" in w or "leak.md" in w or "nowhere.md" in w for w in warnings))

    def test_wrong_project_json_shape_is_a_warning(self):
        self.apply()
        for value in ([1], {"schema": 1, "modules": [1]}):
            with self.subTest(value=value):
                write(self.target / "ai-kit/project.json", json.dumps(value))
                report = doctor.examine(self.target, root=self.source)
                self.assertTrue(any(w.startswith("Invalid project.json") for w in report["warnings"]))

    def test_check_failure_after_apply_is_not_reported_as_refusal(self):
        error = io.StringIO()
        with mock.patch.object(doctor, "examine", side_effect=UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad")), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(error):
            code = install.main([str(self.target), "--apply", "--check"])
        self.assertEqual(code, 1)
        self.assertIn("Installation applied; doctor check failed", error.getvalue())
        self.assertNotIn("Installation refused", error.getvalue())
        self.assertTrue((self.target / "AGENTS.md").is_file())


class SettingsTests(ProjectTestCase):
    def test_docker_cleanup_mode_is_validated_and_persisted(self):
        self.apply(docker_cleanup="keep-cache")
        settings = json.loads((self.target / "ai-kit/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["docker_cleanup"], "keep-cache")
        # The recorded mode persists: a rerun without the flag changes nothing.
        self.assertFalse(self.plan()["actions"])
        with self.assertRaises(ValueError):
            self.plan(docker_cleanup="none")
        settings["docker_cleanup"] = "aggressive"
        write(self.target / "ai-kit/settings.json", json.dumps(settings))
        with self.assertRaises(ValueError):
            self.plan()

    def test_cli_flag_sets_the_mode(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main([str(self.target), "--docker-cleanup", "keep-cache", "--apply"]), 0)
        settings = json.loads((self.target / "ai-kit/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["docker_cleanup"], "keep-cache")


class HelperTests(unittest.TestCase):
    def test_turkish_dotted_capital_label_becomes_a_note(self):
        sources = {"a": {"messages": [{"id": "m1", "role": "user",
                                       "text": "İstanbul: office location\nregion: emea"}]}}
        claims = memory.candidates(sources)
        keys = {claim["key"] for claim in claims}
        self.assertIn("region", keys)
        self.assertTrue(any(claim["kind"] == "note" and "İstanbul" in claim["value"] for claim in claims))

    def test_lock_conflict_message_explains_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            lock = Path(folder) / "write.lock"
            os.close(install.exclusive_lock(lock))
            with self.assertRaises(ValueError) as caught:
                install.exclusive_lock(lock)
            self.assertIn("if no aikit process is running", str(caught.exception))

    def test_longer_fences_hide_nested_links_and_headings(self):
        text = "````md\n```\n[x](secret.md)\n## Hidden\n```\n````\n[ok](real.md)\n## Shown\n"
        self.assertEqual(check_kit.links(text), ["real.md"])
        self.assertEqual(check_kit.headings(text), {"shown"})

    def test_cli_handles_sigterm_as_pid_one(self):
        previous = signal.getsignal(signal.SIGTERM)
        self.addCleanup(signal.signal, signal.SIGTERM, previous)
        with contextlib.redirect_stdout(io.StringIO()):
            aikit_cli.main([])
        handler = signal.getsignal(signal.SIGTERM)
        self.assertIs(handler, aikit_cli._terminate)
        with self.assertRaises(SystemExit) as caught:
            handler(signal.SIGTERM, None)
        self.assertEqual(caught.exception.code, 128 + signal.SIGTERM)


class ContextSnapshotTests(ProjectTestCase):
    def test_snapshot_backs_up_project_facts_and_keeps_unicode(self):
        write(self.target / "go.mod", "module example.test/app\n")
        self.apply()
        facts = self.target / "ai-kit/project.json"
        value = json.loads(facts.read_text(encoding="utf-8"))
        # Non-ASCII text must stay readable, not escaped.
        start = "".join(map(chr, (0x0417, 0x0430, 0x043F, 0x0443, 0x0441, 0x043A)))
        value["operations"]["startup"] = start + ": make run"
        facts.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        original = facts.read_bytes()
        plan = context.snapshot_plan(self.target)
        self.assertTrue(context.apply_snapshot(plan))
        self.assertIn(start, facts.read_text(encoding="utf-8"))
        backups = list((self.target / "ai-kit/.upstream-cache/backups").glob("*/ai-kit/project.json"))
        self.assertEqual([backup.read_bytes() for backup in backups], [original])


class EntryFileTests(unittest.TestCase):
    def test_tracked_root_entries_do_not_import_local_maintainer_files(self):
        entries = [install.ROOT / name for name in ("CLAUDE.md", "KIMI.md", "MANUS.md")]
        if not any(entry.is_file() for entry in entries):
            self.skipTest("Root maintainer entries are not part of this packaged distribution")
        for entry in entries:
            text = entry.read_text(encoding="utf-8")
            self.assertIn("CONTRIBUTING.md", text)
            self.assertNotRegex(text, r"(?m)^\s*@(AGENTS|PROJECT_CONTEXT|WIKI)\.md\s*$")


if __name__ == "__main__":
    unittest.main()
