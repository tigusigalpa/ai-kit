"""Catch concrete metadata, link, template, and checkout regressions."""
from pathlib import Path
import json
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

    def test_provider_effort_outside_supported_list_is_reported(self):
        path = self.root / "template/ai-kit/router/providers/openai.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["roles"]["work"]["effort"] = "ultra"
        path.write_text(json.dumps(config), encoding="utf-8")
        self.assertTrue(any("Unsupported configured effort" in error for error in self.check()))

    def test_active_model_id_in_markdown_is_reported(self):
        with (self.root / "template/ai-kit/ENGINEERING.md").open("a", encoding="utf-8") as stream:
            stream.write("\nRoute this step to claude-opus-5-5.\n")
        self.assertTrue(any("duplicated outside provider configuration" in error
                            for error in self.check()))

    def test_provider_without_verified_date_is_reported(self):
        path = self.root / "template/ai-kit/router/providers/anthropic.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        del config["verified_documentation_date"]
        path.write_text(json.dumps(config), encoding="utf-8")
        self.assertTrue(any("verified_documentation_date" in error for error in self.check()))

    def test_source_enumeration_skips_git_but_keeps_hidden_instructions(self):
        measurement = self.root / "ai-kit/.metrics/private-notes.md"
        measurement.parent.mkdir(parents=True)
        measurement.write_bytes(b"Private runtime data\n")
        sources = {p.relative_to(self.root).as_posix() for p in check_kit.source_files(self.root)}
        self.assertIn(".agents/skills/project-continuity/SKILL.md", sources)
        self.assertIn("template/.agents/skills/go-work/SKILL.md", sources)
        self.assertFalse(any(p.startswith(".git/") for p in sources))
        self.assertFalse(any(p.startswith("ai-kit/.metrics/") for p in sources))
        self.assertIn("template/ai-kit/METRICS.md", sources)

    def test_agent_registry_missing_optional_source_is_reported(self):
        path = self.root / "integrations/agents.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["agents"]["aider"]["optional"] = [{"source": "missing.md", "destination": "CONVENTIONS.md"}]
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        self.assertTrue(any("optional source missing" in error for error in self.check()))

    def test_agent_registry_entry_missing_from_template_is_reported(self):
        path = self.root / "integrations/agents.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["agents"]["gemini"]["entries"] = ["NOPE.md"]
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        self.assertTrue(any("entry missing from template" in error for error in self.check()))

    def test_pending_provider_is_warning_not_error(self):
        path = self.root / "template/ai-kit/router/providers/gemini.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config.pop("verified_documentation_date", None)
        config["verification_status"] = "pending"
        path.write_text(json.dumps(config) + "\n", encoding="utf-8")
        with patch.object(check_kit, "visibility", return_value=[]):
            errors, warnings = check_kit.check(self.root, git="not-invoked")
        self.assertEqual(errors, [])
        self.assertTrue(any("pending" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
