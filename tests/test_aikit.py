"""Exercise the unified aikit CLI dispatcher."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest import mock

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
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as context:
            aikit_cli.main(["install", "--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("--preset", output.getvalue())

    def test_benchmark_help_reaches_worker_commands(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as context:
            aikit_cli.main(["benchmark", "--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("{run,report,review,export}", output.getvalue())

    def test_version_reads_from_version_file(self):
        self.assertEqual(aikit_cli.__version__, (Path(__file__).resolve().parents[1] / "VERSION")
                         .read_text(encoding="utf-8").strip())

    def test_version_flag_reports_bundle_without_loading_or_running_a_command(self):
        output = io.StringIO()
        with mock.patch.object(aikit_cli, "_load") as load, contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as context:
            aikit_cli.main(["--version"])
        self.assertEqual(context.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), "aikit " + aikit_cli.__version__)
        load.assert_not_called()

    def test_memory_help_reaches_offline_commands(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as context:
            aikit_cli.main(["memory", "--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("{import,merge,export}", output.getvalue())

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

    def test_loader_prefers_installed_package_module(self):
        import types
        package_module = types.ModuleType("aikit.scripts.install")
        package_module.main = lambda argv=None: 0
        with mock.patch.dict(sys.modules, {"aikit.scripts.install": package_module}):
            self.assertIs(aikit_cli._load("install"), package_module)
        self.assertTrue(callable(aikit_cli._load("install").main))


if __name__ == "__main__":
    unittest.main()
