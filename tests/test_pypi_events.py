"""Exercise release-triggered publication guards without publishing or approving jobs."""
from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_distribution as release

REPOSITORY = "tigusigalpa/ai-kit"
VERSION = "1.5.0"


class PyPIEventTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aikit-release-event-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / "VERSION").write_text(VERSION + "\n", encoding="utf-8")
        self.event_path = self.root / "event.json"

    def published(self, version=VERSION):
        return {"action": "published", "repository": {"full_name": REPOSITORY},
                "release": {"tag_name": "v" + version, "draft": False, "prerelease": False}}

    def dispatch(self, **inputs):
        return {"repository": {"full_name": REPOSITORY}, "inputs": inputs}

    def resolve(self, payload, *, event="release", version=VERSION,
                ref="refs/tags/v" + VERSION, repository=REPOSITORY):
        return release.workflow_identity(version, event, payload, ref, repository)

    def cli(self, payload, *extra, event="release", ref="refs/tags/v" + VERSION):
        self.event_path.write_text(json.dumps(payload), encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(release, "ROOT", self.root), redirect_stdout(output):
            code = release.main(["identity", "--event-name", event, "--event-path", str(self.event_path),
                                 "--ref", ref, "--repository", REPOSITORY, *extra])
        return code, json.loads(output.getvalue()), output.getvalue()

    def test_future_stable_releases_select_production_without_uploading(self):
        for version in ("1.4.3", "1.5.0", "2.0.0", "10.42.300"):
            with self.subTest(version=version):
                result = self.resolve(self.published(version), version=version, ref="refs/tags/v" + version)
                self.assertEqual((result["version"], result["destination"], result["event"]),
                                 (version, "pypi", "release"))
                self.assertFalse(result["upload_performed"])

    def test_draft_prerelease_and_missing_boolean_flags_refuse(self):
        for field in ("draft", "prerelease"):
            for value in (True, None, "false", 0):
                with self.subTest(field=field, value=value):
                    payload = self.published()
                    payload["release"][field] = value
                    with self.assertRaisesRegex(ValueError, "stable, non-draft"):
                        self.resolve(payload)
            payload = self.published()
            del payload["release"][field]
            with self.assertRaises(ValueError):
                self.resolve(payload)

    def test_other_release_actions_and_missing_release_refuse(self):
        for action in ("created", "edited", "deleted", "released", "prereleased", ""):
            with self.subTest(action=action):
                payload = self.published()
                payload["action"] = action
                with self.assertRaises(ValueError):
                    self.resolve(payload)
        for value in (None, [], "release"):
            payload = self.published()
            payload["release"] = value
            with self.assertRaises(ValueError):
                self.resolve(payload)

    def test_automatic_tags_must_be_canonical_stable_versions(self):
        for tag in ("1.5.0", "v1.5", "v1.5.0rc1", "v01.5.0", "v1.05.0", "v1.5.00",
                    "v1.5.0\n", "v1.5.0$(echo synthetic)", "v1/5/0"):
            with self.subTest(tag=tag):
                payload = self.published()
                payload["release"]["tag_name"] = tag
                with self.assertRaises(ValueError):
                    self.resolve(payload, ref="refs/tags/" + tag)

    def test_release_tag_runner_ref_and_version_must_agree(self):
        for ref in ("refs/heads/main", "refs/tags/v1.4.2", ""):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                self.resolve(self.published(), ref=ref)
        with self.assertRaisesRegex(ValueError, "VERSION"):
            self.resolve(self.published(), version="1.4.2")

    def test_repository_mismatch_and_fork_publication_refuse(self):
        for event_repository, repository in (("example/fork", REPOSITORY),
                                             (REPOSITORY, "example/fork"),
                                             ("example/fork", "example/fork")):
            payload = self.published()
            payload["repository"]["full_name"] = event_repository
            with self.subTest(repository=repository), self.assertRaises(ValueError):
                self.resolve(payload, repository=repository)
        for value in (None, [], {}):
            payload = self.published()
            payload["repository"] = value
            with self.assertRaises(ValueError):
                self.resolve(payload)

    def test_dispatch_defaults_to_build_only_on_branches_and_forks(self):
        payload = {"repository": {"full_name": "example/fork"}}
        result = self.resolve(payload, event="workflow_dispatch", ref="refs/heads/review", repository="example/fork")
        self.assertEqual(result["destination"], "validate")
        self.assertFalse(result["upload_performed"])

    def test_manual_upload_still_requires_explicit_matching_version(self):
        for destination in ("pypi", "testpypi"):
            for version in ("", "1.4.2"):
                with self.subTest(destination=destination, version=version), self.assertRaises(ValueError):
                    self.resolve(self.dispatch(destination=destination, version=version), event="workflow_dispatch")
            result = self.resolve(self.dispatch(destination=destination, version=VERSION), event="workflow_dispatch")
            self.assertEqual(result["destination"], destination)
            self.assertFalse(result["upload_performed"])

    def test_invalid_inputs_and_unsupported_events_refuse(self):
        for payload in ([], None, "event"):
            with self.assertRaises(ValueError):
                self.resolve(payload)
        for inputs in (None, [], {"version": True}, {"destination": False}, {"destination": "other"}):
            payload = self.dispatch()
            payload["inputs"] = inputs
            with self.assertRaises(ValueError):
                self.resolve(payload, event="workflow_dispatch")
        for event in ("push", "pull_request", "repository_dispatch", ""):
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.resolve(self.published(), event=event)

    def test_cli_ignores_release_body_and_conflicting_manual_inputs(self):
        payload = self.published()
        marker = "SYNTHETIC_PRIVATE_RELEASE_BODY"
        payload["release"]["body"] = marker + "\ndestination=validate\nversion=9.9.9"
        payload["inputs"] = {"destination": "validate", "version": "9.9.9"}
        code, result, output = self.cli(payload)
        self.assertEqual(code, 0)
        self.assertEqual(result["destination"], "pypi")
        self.assertNotIn(marker, output)
        self.assertFalse(result["upload_performed"])

    def test_cli_validation_upload_and_refusal_remain_distinct(self):
        code, result, _ = self.cli(self.dispatch(), event="workflow_dispatch", ref="refs/heads/main")
        self.assertEqual((code, result["destination"]), (0, "validate"))
        code, result, _ = self.cli(self.dispatch(destination="pypi", version=VERSION), event="workflow_dispatch")
        self.assertEqual((code, result["destination"]), (0, "pypi"))
        bad = copy.deepcopy(self.published())
        bad["release"]["tag_name"] = "v9.9.9"
        code, result, _ = self.cli(bad)
        self.assertEqual(code, 1)
        self.assertIn("error", result)
        self.assertFalse(result["upload_performed"])

    def test_cli_rejects_mixed_argument_sources(self):
        for extra in (("--expected-version", VERSION), ("--destination", "pypi")):
            code, result, _ = self.cli(self.published(), *extra)
            self.assertEqual(code, 1)
            self.assertIn("event inputs", result["error"])

    def test_cli_requires_both_event_arguments(self):
        for arguments in (("--event-name", "release"), ("--event-path", str(self.event_path))):
            output = io.StringIO()
            with mock.patch.object(release, "ROOT", self.root), redirect_stdout(output):
                code = release.main(["identity", *arguments])
            self.assertEqual(code, 1)
            self.assertIn("Both event", json.loads(output.getvalue())["error"])

    def test_event_reader_bounds_and_invalid_json_do_not_echo_content(self):
        self.event_path.write_bytes(b"x" * 1_000_001)
        with self.assertRaisesRegex(ValueError, "inspection limit"):
            release.read_workflow_event(self.event_path)
        self.event_path.write_text("{SYNTHETIC_PRIVATE_RELEASE_BODY}", encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(release, "ROOT", self.root), redirect_stdout(output):
            code = release.main(["identity", "--event-name", "release", "--event-path", str(self.event_path)])
        self.assertEqual(code, 1)
        self.assertNotIn("SYNTHETIC_PRIVATE_RELEASE_BODY", output.getvalue())

    def test_event_reader_refuses_missing_directory_and_linked_files(self):
        for path in (self.root / "missing.json", self.root):
            with self.assertRaisesRegex(ValueError, "regular unlinked"):
                release.read_workflow_event(path)
        self.event_path.write_text("{}", encoding="utf-8")
        linked = self.root / "linked.json"
        try:
            linked.symlink_to(self.event_path)
        except OSError as exc:
            self.skipTest("Native symlink creation unavailable: " + str(exc))
        with self.assertRaisesRegex(ValueError, "regular unlinked"):
            release.read_workflow_event(linked)


if __name__ == "__main__":
    unittest.main()
