"""Exercise the unified aikit CLI dispatcher."""
import contextlib
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aikit_cli


class AikitCliTests(unittest.TestCase):
    def test_no_command_prints_help(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(aikit_cli.main([]), 2)

    def test_route_dispatches_to_router(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(aikit_cli.main(["route", "implement a feature"]), 0)
        self.assertIn('"level"', output.getvalue())

    def test_install_help_forwards_arguments(self):
        with self.assertRaises(SystemExit) as context:
            aikit_cli.main(["install", "--help"])
        self.assertEqual(context.exception.code, 0)

    def test_version_reads_from_version_file(self):
        self.assertEqual(aikit_cli.__version__, (Path(__file__).resolve().parents[1] / "VERSION")
                         .read_text(encoding="utf-8").strip())

    def test_providers_dispatches_to_router(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(aikit_cli.main(["providers"]), 0)
        self.assertIn('"provider": "gemini"', output.getvalue())

    def test_adapters_dispatches_to_client_report(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(aikit_cli.main(["adapters", "report"]), 0)
        self.assertIn('"client": "codex"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
