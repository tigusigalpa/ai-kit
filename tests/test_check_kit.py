"""Catch concrete metadata, link, template, and checkout regressions."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_kit


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-kit-check-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "reference"
        shutil.copytree(check_kit.ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def check(self):
        # Real Git visibility is exercised by the top-level checker/CI invocation.
        with patch.object(check_kit, "visibility", return_value=[]):
            return check_kit.check(self.root, git="not-invoked")[0]

    def test_clean_distribution(self):
        self.assertEqual(self.check(), [])

    def test_git_checkout_binary_metadata_is_excluded(self):
        path = self.root / ".git/objects/binary"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\xff\x00")
        self.assertEqual(self.check(), [])

    def test_missing_heading_is_reported(self):
        with (self.root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n[Broken](PROJECT_CONTEXT.md#nonexistent-heading)\n")
        self.assertTrue(any("missing heading" in error for error in self.check()))

    def test_link_cannot_escape_reference(self):
        with (self.root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n[Escape](../../outside.md)\n")
        self.assertTrue(any("escapes reference" in error for error in self.check()))

    def test_skill_folder_name_mismatch(self):
        path = self.root / "template/.agents/skills/go-work/SKILL.md"
        path.write_text(path.read_text().replace("name: go-work", "name: wrong-name"), encoding="utf-8")
        self.assertTrue(any("name/folder mismatch" in error for error in self.check()))

    def test_registry_duplicate_is_reported(self):
        path = self.root / "template/ai-kit/SKILLS.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\n[Repeated](../.agents/skills/go-work/SKILL.md)\n")
        self.assertTrue(any("registry differs" in error for error in self.check()))

    def test_history_is_not_installable_project_fact(self):
        path = self.root / "template/PROJECT_CONTEXT.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\nKit review date: 2026-10-08.\n")
        self.assertTrue(any("history leaked" in error for error in self.check()))

    def test_invalid_provider_json_is_failure_not_crash(self):
        path = self.root / "template/ai-kit/router/providers/openai.json"
        path.write_text("{", encoding="utf-8")
        self.assertTrue(any("invalid JSON" in error for error in self.check()))

    def test_source_enumeration_skips_git_but_keeps_hidden_instructions(self):
        sources = {p.relative_to(self.root).as_posix() for p in check_kit.source_files(self.root)}
        self.assertIn(".agents/skills/project-continuity/SKILL.md", sources)
        self.assertIn("template/.agents/skills/go-work/SKILL.md", sources)
        self.assertFalse(any(p.startswith(".git/") for p in sources))


if __name__ == "__main__":
    unittest.main()
