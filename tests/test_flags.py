"""Keep the installer flag schema, its guide and SKILL.md in step with the argparse definition."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_kit
import flags
import install

# The minimal tree that installer_flag_errors reads.
FILES = ("integrations/agents.json", "template/ai-kit/settings.json", check_kit.FLAG_SCHEMA,
         check_kit.FLAG_GUIDE, "SKILL.md")


class FlagSchemaTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="ai-kit-flags-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for relative in FILES:
            (self.root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, self.root / relative)

    def edit(self, relative: str, old: str, new: str, count: int = 1) -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new) if count < 0 else text.replace(old, new, count),
                        encoding="utf-8", newline="\n")

    def errors(self) -> list[str]:
        return check_kit.installer_flag_errors(self.root)

    def test_committed_schema_matches_parser_and_documentation(self):
        self.assertEqual(self.errors(), [])
        committed = json.loads((ROOT / check_kit.FLAG_SCHEMA).read_text(encoding="utf-8"))
        self.assertEqual(committed, install.flag_schema())

    def test_schema_describes_values_defaults_and_presets(self):
        options = {entry["option"]: entry for entry in install.flag_schema()["options"]}
        self.assertEqual(options["TARGET"], {"option": "TARGET", "value": "path", "required": True,
                                             "help": "Application directory to set up or update"})
        self.assertEqual(options["--apply"]["excludes"], ["--dry-run"])
        self.assertEqual(options["--mode"]["setting"], "sharing_mode")
        self.assertEqual(options["--mode"]["fresh_default"], "private")
        self.assertEqual(options["--docker-cleanup"]["choices"], list(install.DOCKER_CLEANUP_MODES))
        self.assertTrue(options["--agent"]["repeatable"])
        self.assertEqual(options["--agent"]["fresh_default"], list(install.DEFAULT_AGENTS))
        self.assertTrue(options["--accept-local"]["repeatable"])
        self.assertEqual(options["--with-web-design"]["setting"], "web_design")
        self.assertNotIn("--help", options)
        self.assertTrue(all(entry.get("help") for entry in options.values()))
        presets = install.flag_schema()["presets"]
        self.assertEqual(presets["solo"], {"mode": "private", "extras": list(install.PRESETS["solo"]["extras"])})

    def test_stale_committed_schema_is_reported(self):
        self.edit(check_kit.FLAG_SCHEMA, '"keep-cache"', '"keep-everything"')
        self.assertTrue(any(error.startswith("Stale " + check_kit.FLAG_SCHEMA) for error in self.errors()))

    def test_undocumented_flag_is_reported(self):
        self.edit(check_kit.FLAG_GUIDE, "| `--docker-cleanup` |", "| Docker cleanup |")
        self.assertIn("Installer flag undocumented in " + check_kit.FLAG_GUIDE + ": --docker-cleanup", self.errors())

    def test_documented_flag_without_parser_option_is_reported(self):
        self.edit(check_kit.FLAG_GUIDE, "| `--check` |", "| `--with-nothing` | Switch | Retired. | None. |\n| `--check` |")
        self.assertIn(check_kit.FLAG_GUIDE + " documents a missing installer flag: --with-nothing", self.errors())

    def test_undocumented_choice_value_is_reported(self):
        self.edit(check_kit.FLAG_GUIDE, "`keep-cache`", "keep cache", count=-1)
        self.assertIn("Installer flag value undocumented in " + check_kit.FLAG_GUIDE + ": --docker-cleanup keep-cache",
                      self.errors())

    def test_skill_must_mention_every_flag_and_value(self):
        self.edit("SKILL.md", "--with-context7", "--with-docs", count=-1)
        self.assertIn("Installer flag or value missing from SKILL.md: --with-context7", self.errors())

    def test_cli_prints_and_writes_the_same_schema(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(flags.main([]), 0)
        self.assertEqual(json.loads(output.getvalue()), install.flag_schema())
        target = self.root / "out" / "flags.json"
        self.assertEqual(flags.main(["--output", str(target)]), 0)
        data = target.read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertEqual(json.loads(data), install.flag_schema())


if __name__ == "__main__":
    unittest.main()
