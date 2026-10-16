"""Exercise publication guards and built-artifact privacy/resource contracts offline."""
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_distribution as release
import build_distribution

VERSION = "1.4.1"
DESCRIPTION = b"# AI-KIT\n\nPortable project instructions.\n"


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="aikit-package-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def metadata(self, *, version=VERSION, extra="", description=DESCRIPTION):
        headers = ("Metadata-Version: 2.4\nName: ai-kit-python\nVersion: " + version + "\n"
                   "Requires-Python: >=3.10\nLicense-Expression: MIT AND Apache-2.0\n"
                   "Author: Igor Sazonov\nDescription-Content-Type: text/markdown\n")
        headers += "".join("License-File: " + name + "\n" for name in release.LICENSES)
        headers += "".join("Project-URL: " + name + ", https://example.invalid/\n"
                           for name in ("Homepage", "Documentation", "Source", "Issues", "Changelog"))
        return (headers + extra + "\n").encode() + description

    def payload(self, *, description=DESCRIPTION):
        result = {name: b"Public resource.\n" for name in release.REQUIRED}
        result["VERSION"] = (VERSION + "\n").encode()
        result["docs/PYPI_DESCRIPTION.md"] = description
        return result

    def wheel(self, *, payload=None, metadata=None, mutate=None):
        payload = self.payload() if payload is None else payload
        files = {"aikit/" + name: data for name, data in payload.items()}
        prefix = "ai_kit_python-" + VERSION + ".dist-info/"
        files[prefix + "METADATA"] = self.metadata() if metadata is None else metadata
        files[prefix + "entry_points.txt"] = b"[console_scripts]\naikit = aikit.aikit_cli:main\n"
        files[prefix + "WHEEL"] = b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        for name in release.LICENSES:
            files[prefix + "licenses/" + name] = payload.get(name, b"")
        if mutate:
            mutate(files, prefix)
        path = self.directory / ("ai_kit_python-" + VERSION + "-py3-none-any.whl")
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        return path

    def sdist(self, *, metadata=None):
        path = self.directory / ("ai_kit_python-" + VERSION + ".tar.gz")
        files = {**self.payload(), "PKG-INFO": self.metadata() if metadata is None else metadata}
        with tarfile.open(path, "w:gz") as archive:
            for name, data in files.items():
                item = tarfile.TarInfo("ai_kit_python-" + VERSION + "/" + name)
                item.size = len(data)
                archive.addfile(item, io.BytesIO(data))
        return path

    def test_valid_wheel_and_sdist_keep_templates_licenses_and_same_version(self):
        self.wheel()
        self.sdist()
        reports = release.check_archives(self.directory, VERSION)
        self.assertEqual(len(reports), 2)
        self.assertTrue(all(report["version"] == VERSION and len(report["sha256"]) == 64 for report in reports))

    def test_archive_version_mismatch_refuses(self):
        path = self.wheel(metadata=self.metadata(version="1.3.0"))
        with self.assertRaisesRegex(ValueError, "name/version"):
            release.inspect_distribution(path, VERSION)

    def test_legacy_distribution_name_refuses(self):
        metadata = self.metadata().replace(b"Name: ai-kit-python\n", b"Name: ai-kit\n")
        for path in (self.wheel(metadata=metadata), self.sdist(metadata=metadata)):
            with self.assertRaisesRegex(ValueError, "name/version"):
                release.inspect_distribution(path, VERSION)

    def test_unexpected_runtime_dependency_refuses(self):
        path = self.wheel(metadata=self.metadata(extra="Requires-Dist: unexpected-package\n"))
        with self.assertRaisesRegex(ValueError, "dependency contract"):
            release.inspect_distribution(path, VERSION)

    def test_private_root_documents_and_memory_refuse_but_templates_remain_required(self):
        for name in ("AGENTS.md", "PROJECT_CONTEXT.md", "WIKI.md", "ai-kit/.memory/raw.json",
                     "ai-kit/.design/raw.md", "docs/.private/raw.md", ".env", "auth.json", "docs/private.pem"):
            with self.subTest(name=name):
                path = self.wheel(payload={**self.payload(), name: b"Synthetic private content."})
                with self.assertRaisesRegex(ValueError, "Private local|Credential"):
                    release.inspect_distribution(path, VERSION)
        payload = self.payload()
        del payload["template/AGENTS.md"]
        with self.assertRaisesRegex(ValueError, "required distribution resources"):
            release.inspect_distribution(self.wheel(payload=payload), VERSION)

    def test_missing_cli_and_changed_license_payload_refuse(self):
        for suffix in ("entry_points.txt", "licenses/LICENSE"):
            with self.subTest(suffix=suffix):
                path = self.wheel(mutate=lambda files, prefix: files.__setitem__(prefix + suffix, b"changed\n"))
                with self.assertRaises((ValueError, release.configparser.Error)):
                    release.inspect_distribution(path, VERSION)

    def test_source_description_and_portable_links_are_checked(self):
        with self.assertRaisesRegex(ValueError, "differs from"):
            release.inspect_distribution(self.wheel(metadata=self.metadata(description=b"Other description.\n")), VERSION)
        for text in (b"[Guide](../README.md)\n", b"```mermaid\ngraph LR\n```\n"):
            with self.subTest(text=text):
                path = self.wheel(payload=self.payload(description=text), metadata=self.metadata(description=text))
                with self.assertRaisesRegex(ValueError, "nonportable"):
                    release.inspect_distribution(path, VERSION)

    def test_missing_or_multiple_archives_refuse(self):
        self.wheel()
        with self.assertRaisesRegex(ValueError, "exactly one"):
            release.check_archives(self.directory, VERSION)
        self.sdist()
        (self.directory / "extra.whl").write_bytes(b"not a wheel")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            release.check_archives(self.directory, VERSION)

    def test_traversal_and_linked_members_refuse_without_extraction(self):
        path = self.wheel()
        with zipfile.ZipFile(path, "a") as archive:
            archive.writestr("../outside", b"synthetic")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            release.inspect_distribution(path, VERSION)
        self.assertFalse((self.directory.parent / "outside").exists())
        path = self.wheel()
        with zipfile.ZipFile(path, "a") as archive:
            item = zipfile.ZipInfo("aikit/linked")
            item.create_system = 3
            item.external_attr = 0o120777 << 16
            archive.writestr(item, "outside")
        with self.assertRaisesRegex(ValueError, "Linked"):
            release.inspect_distribution(path, VERSION)
        path = self.sdist()
        with tarfile.open(path, "w:gz") as archive:
            item = tarfile.TarInfo("source/linked")
            item.type = tarfile.SYMTYPE
            item.linkname = "outside"
            archive.addfile(item)
        with self.assertRaisesRegex(ValueError, "Linked"):
            release.inspect_distribution(path, VERSION)

    def test_default_validation_is_local_and_allows_review_branches(self):
        result = release.release_identity(VERSION, "", "validate", "refs/heads/review", "example/fork")
        self.assertFalse(result["upload_performed"])

    def test_build_output_inside_source_refuses_before_writing(self):
        with self.assertRaisesRegex(ValueError, "outside the source"):
            build_distribution.prepare(build_distribution.ROOT / "dist")

    def test_registry_upload_requires_exact_version_tag_and_canonical_repository(self):
        for destination in ("testpypi", "pypi"):
            for expected, ref, repository in (
                ("", "refs/tags/v" + VERSION, "tigusigalpa/ai-kit"),
                ("1.3.0", "refs/tags/v" + VERSION, "tigusigalpa/ai-kit"),
                (VERSION, "refs/heads/main", "tigusigalpa/ai-kit"),
                (VERSION, "refs/tags/v1.3.0", "tigusigalpa/ai-kit"),
                (VERSION, "refs/tags/v" + VERSION, "example/fork"),
            ):
                with self.subTest(destination=destination, expected=expected, ref=ref, repository=repository):
                    with self.assertRaises(ValueError):
                        release.release_identity(VERSION, expected, destination, ref, repository)
            result = release.release_identity(VERSION, VERSION, destination, "refs/tags/v" + VERSION, "tigusigalpa/ai-kit")
            self.assertFalse(result["upload_performed"])

    def test_invalid_versions_destinations_and_mismatched_validation_refuse(self):
        for version, expected, destination in (("1.4", "", "validate"), (VERSION, "1.3.0", "validate"), (VERSION, "", "other")):
            with self.subTest(version=version, destination=destination), self.assertRaises(ValueError):
                release.release_identity(version, expected, destination, "", "")
        self.assertEqual(release.release_identity("1.5.0rc1", "", "validate", "", "")["version"], "1.5.0rc1")


if __name__ == "__main__":
    unittest.main()
