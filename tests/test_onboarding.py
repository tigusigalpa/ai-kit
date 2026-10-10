"""Exercise onboarding (interactive/check), project facts, and the adr/changelog helpers."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adr
import changelog
import install


class DetectFactsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-facts-")
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name).resolve() / "project"
        self.target.mkdir()

    def write(self, path, data):
        destination = self.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(data, encoding="utf-8")

    def test_go_version_and_commands(self):
        self.write("go.mod", "module example.test/app\n\ngo 1.22\n")
        module = install.detect_facts(self.target)["modules"][0]
        self.assertEqual(module["path"], "/")
        self.assertEqual(module["language"], "Go")
        self.assertEqual(module["version"], "1.22")
        self.assertEqual(module["profiles"], ["GO"])
        self.assertEqual(module["commands"]["test"], "go test ./...")

    def test_python_requires_and_commands(self):
        self.write("pyproject.toml", '[project]\nname = "svc"\nrequires-python = ">=3.10"\n')
        module = install.detect_facts(self.target)["modules"][0]
        self.assertEqual(module["language"], "Python")
        self.assertEqual(module["version"], ">=3.10")
        self.assertEqual(module["commands"]["test"], "pytest")

    def test_frontend_commands_from_scripts(self):
        self.write("package.json", json.dumps({"scripts": {"test": "jest", "build": "tsc"}}))
        module = install.detect_facts(self.target)["modules"][0]
        self.assertEqual(module["commands"]["test"], "npm test")
        self.assertEqual(module["commands"]["build"], "npm run build")

    def test_composer_and_laravel(self):
        self.write("composer.json", json.dumps({"require": {"php": "^8.2"}}))
        self.write("artisan", "#!/usr/bin/env php\n")
        module = install.detect_facts(self.target)["modules"][0]
        self.assertEqual(module["profiles"], ["LARAVEL", "PHP"])
        self.assertEqual(module["version"], "^8.2")
        self.assertEqual(module["commands"]["test"], "php artisan test")

    def test_subdirectory_prefix(self):
        self.write("api/go.mod", "module example.test/api\n")
        module = install.detect_facts(self.target)["modules"][0]
        self.assertEqual(module["path"], "/api/")
        self.assertEqual(install.detect_profiles(self.target), {"GO": ["api/"]})

    def test_no_manifests_yield_no_modules(self):
        self.write("notes.txt", "nothing\n")
        self.assertEqual(install.detect_facts(self.target)["modules"], [])


class ProjectJsonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-pjson-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / "project"
        self.source = self.base / "reference"
        shutil.copytree(install.ROOT, self.source, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def write(self, path, data):
        destination = self.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(data, encoding="utf-8")

    def apply(self, **options):
        plan = install.build_plan(self.target, root=self.source, **options)
        self.assertTrue(install.apply_plan(plan))
        return plan

    def test_project_json_drafted_on_fresh_install(self):
        self.write("go.mod", "module example.test/app\n\ngo 1.21\n")
        self.apply()
        value = json.loads((self.target / "ai-kit/project.json").read_text(encoding="utf-8"))
        self.assertEqual(value["schema"], 1)
        self.assertEqual(len(value["modules"]), 1)
        self.assertEqual(value["modules"][0]["language"], "Go")
        self.assertEqual(value["modules"][0]["version"], "1.21")

    def test_project_json_preserved_when_existing(self):
        existing = json.dumps({"schema": 1, "modules": [], "operations": {}}) + "\n"
        self.write("ai-kit/project.json", existing)
        self.write("go.mod", "module example.test/app\n")
        self.apply()
        self.assertEqual((self.target / "ai-kit/project.json").read_text(encoding="utf-8"), existing)


class InteractiveTests(unittest.TestCase):
    def test_selections_are_collected(self):
        responses = iter(["team", "English", "standard", "codex,claude", "ci", "y"])
        read = lambda prompt: next(responses)
        selections = install.interactive_selections(read, agents_available={"codex", "claude"},
                                                    facts={"modules": []})
        self.assertEqual(selections, {"mode": "team", "language": "English", "conventions": "standard",
                                      "agents": ["codex", "claude"], "extras": ["ci"]})

    def test_defaults_apply_when_answers_are_blank(self):
        responses = iter(["", "", "", "", "", "y"])
        read = lambda prompt: next(responses)
        selections = install.interactive_selections(read, agents_available={"codex"}, facts={"modules": []})
        self.assertEqual(selections["mode"], "private")
        self.assertEqual(selections["agents"], ["codex"])
        self.assertEqual(selections["extras"], [])

    def test_decline_returns_none(self):
        responses = iter(["private", "Russian", "owner", "codex", "", "n"])
        read = lambda prompt: next(responses)
        self.assertIsNone(install.interactive_selections(read, agents_available={"codex"},
                                                         facts={"modules": []}))


class CheckAfterApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-check-")
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name).resolve() / "project"

    def test_check_runs_doctor_after_apply(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(install.main([str(self.target), "--apply", "--check"]), 0)
        self.assertIn('"doctor"', output.getvalue())


class AdrTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-adr-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "project"
        adr_dir = self.root / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "0000-template.md").write_text(
            "# ADR-NNNN: Title\n\n- Date: use the verified decision date\n"
            "- Status: proposed / accepted / superseded\n", encoding="utf-8")

    def test_scaffold_creates_numbered_adr(self):
        path = adr.scaffold("Use Postgres", self.root)
        self.assertEqual(path.name, "0001-use-postgres.md")
        content = path.read_text(encoding="utf-8")
        self.assertIn("# ADR-0001: Use Postgres", content)
        self.assertIn("- Status: proposed", content)
        self.assertNotIn("use the verified decision date", content)

    def test_second_adr_increments(self):
        adr.scaffold("First", self.root)
        self.assertEqual(adr.scaffold("Second", self.root).name, "0002-second.md")

    def test_title_slug_is_normalized(self):
        path = adr.scaffold("Use Postgres + Redis!", self.root)
        self.assertEqual(path.name, "0001-use-postgres-redis.md")


class ChangelogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-clog-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "project"
        self.root.mkdir()

    def test_add_under_unreleased(self):
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n\nNote text\n", encoding="utf-8")
        changelog.add_entry(self.root, "Fix auth bug")
        text = (self.root / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("- Fix auth bug\n", text)
        self.assertLess(text.index("- Fix auth bug"), text.index("Note text"))

    def test_add_creates_unreleased_section(self):
        (self.root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        changelog.add_entry(self.root, "Add feature")
        text = (self.root / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## Unreleased\n- Add feature\n", text)


if __name__ == "__main__":
    unittest.main()
