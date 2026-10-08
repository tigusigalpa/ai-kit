"""Evidence collection never authorizes deletion or infers exact storage ownership."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import docker_test_usage


class DockerEvidenceTests(unittest.TestCase):
    def test_inspection_only_and_referenced_volume_is_protected(self):
        calls = []

        def run(argv):
            calls.append(argv)
            args = argv[1:]
            if args == ["context", "show"]:
                return "desktop-linux\n"
            if args[:1] == ["info"]:
                return "test-version\n"
            if args[:2] == ["volume", "ls"]:
                return "exact test volume\n"
            if args[:2] == ["volume", "inspect"]:
                self.assertEqual(args[2], "exact test volume")
                return json.dumps([{"Labels": {"com.docker.compose.project": "demo",
                                               "ai-kit.disposable": "true"}}])
            if args[:1] == ["ps"]:
                return "stopped-container\n"
            if args == ["system", "df", "-v"]:
                return "Human-readable storage report\n"
            if args[:2] == ["buildx", "du"]:
                return "{}\n"
            self.fail("Unexpected command: " + repr(argv))

        report = docker_test_usage.collect("demo", run=run, builder="dedicated-test")
        self.assertIsNone(report["measured_project_bytes"])
        self.assertEqual(report["builder_project_ownership"], "unverified")
        self.assertTrue(report["volumes"][0]["declared_disposable"])
        self.assertEqual(report["volumes"][0]["container_references"], ["stopped-container"])
        self.assertFalse(report["volumes"][0]["eligible_without_more_evidence"])
        self.assertFalse(any(token in {"rm", "prune", "remove", "stop"} for argv in calls for token in argv))

    def test_stopped_daemon_is_not_a_successful_evidence_report(self):
        def unavailable(argv):
            raise subprocess.CalledProcessError(1, argv, stderr="Daemon unavailable")

        with self.assertRaises(subprocess.CalledProcessError):
            docker_test_usage.collect("demo", run=unavailable)


if __name__ == "__main__":
    unittest.main()
