"""Version binding and safe CLI image smoke argument construction."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ROOT = Path(__file__).resolve().parents[1]
version_check = module(ROOT / "docker/check_version.py", "aikit_image_version_check")
smoke = module(ROOT / "tests/docker_smoke.py", "aikit_image_smoke")


class DockerImageTests(unittest.TestCase):
    def test_matching_version_returns_the_bundled_value(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "VERSION"
            path.write_bytes(b"1.3.0\r\n")
            self.assertEqual(version_check.check_version(path, "1.3.0"), "1.3.0")

    def test_missing_or_wrong_image_label_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "VERSION"
            path.write_text("1.3.0\n", encoding="utf-8")
            for expected in (None, "", "1.2.0"):
                with self.subTest(expected=expected), self.assertRaises(ValueError):
                    version_check.check_version(path, expected)

    def test_mount_paths_with_spaces_are_one_argument_and_runtime_is_restricted(self):
        with tempfile.TemporaryDirectory(prefix="aikit image ") as folder:
            path = Path(folder).resolve()
            arguments = smoke.runtime_arguments("aikit:test", path, readonly=True)
            self.assertIn(f"type=bind,source={path},target=/workspace,readonly", arguments)
            self.assertIn("--read-only", arguments)
            self.assertEqual(arguments[arguments.index("--network") + 1], "none")
            self.assertEqual(arguments[arguments.index("--cap-drop") + 1], "ALL")
            self.assertEqual(arguments[-1], "aikit:test")
            self.assertNotIn("--privileged", arguments)

    def test_nonexistent_mount_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                smoke.runtime_arguments("aikit:test", Path(folder) / "missing")

    def test_linux_host_identity_is_used_without_switching_to_root(self):
        with patch.object(os, "getuid", return_value=1002, create=True), \
                patch.object(os, "getgid", return_value=1003, create=True):
            arguments = smoke.runtime_arguments("aikit:test")
        self.assertEqual(arguments[arguments.index("--user") + 1], "1002:1003")
        with patch.object(os, "getuid", return_value=0, create=True):
            self.assertNotIn("--user", smoke.runtime_arguments("aikit:test"))


if __name__ == "__main__":
    unittest.main()
