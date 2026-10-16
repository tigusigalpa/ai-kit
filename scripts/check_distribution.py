"""Validate local release archives and manual publication identity without uploading."""
from __future__ import annotations

import argparse
import configparser
from email import policy
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "ai-kit-python"
LICENSES = ("LICENSE", "template/ai-kit/vendor/security-audit/LICENSE",
            "template/ai-kit/vendor/strix/LICENSE")
LOCAL_FILES = {"AGENTS.md", "PROJECT_CONTEXT.md", "WIKI.md"}
PRIVATE_PARTS = {".git", ".aws", ".codex", ".claude", ".secrets", ".metrics", ".memory",
                 ".upstream-cache", ".design", ".private", "__pycache__"}
REQUIRED = {"VERSION", "LICENSE", "aikit_cli.py", "scripts/install.py", "scripts/check_distribution.py",
            "template/AGENTS.md", "template/PROJECT_CONTEXT.md", "template/WIKI.md",
            "template/ai-kit/settings.json", "docs/PYPI_DESCRIPTION.md", "docs/PYPI.md",
            "docker/pypi-requirements.txt", ".github/workflows/publish-pypi.yml", "tests/build_distribution.py", *LICENSES}


def release_identity(version: str, expected: str, destination: str, ref: str, repository: str) -> dict:
    """Require an explicit matching version/tag before either registry upload."""
    if destination not in {"validate", "testpypi", "pypi"}:
        raise ValueError("Unknown publication destination")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:(?:a|b|rc)[0-9]+)?", version):
        raise ValueError("VERSION must be a three-part release or pre-release")
    if expected and expected != version:
        raise ValueError("Requested version does not match VERSION")
    if destination != "validate":
        if expected != version or ref != "refs/tags/v" + version:
            raise ValueError("Publication requires an explicit matching version and vVERSION tag")
        if repository != "tigusigalpa/ai-kit":
            raise ValueError("Publication is restricted to the canonical repository")
    return {"name": PROJECT_NAME, "version": version, "destination": destination,
            "upload_performed": False}


def _members(path: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    total = 0

    def add(name: str, size: int, read) -> None:
        nonlocal total
        parts = PurePosixPath(name).parts
        if not parts or "\\" in name or name.startswith("/") or ".." in parts or ":" in parts[0]:
            raise ValueError("Unsafe archive member path")
        if name in result:
            raise ValueError("Duplicate archive member")
        total += size
        if size > 32_000_000 or total > 128_000_000 or len(result) >= 5000:
            raise ValueError("Archive exceeds inspection limits")
        result[name] = read()

    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            for item in archive.infolist():
                if stat.S_ISLNK(item.external_attr >> 16):
                    raise ValueError("Linked archive member")
                if not item.is_dir():
                    add(item.filename, item.file_size, lambda item=item: archive.read(item))
    else:
        with tarfile.open(path, "r:gz") as archive:
            for item in archive.getmembers():
                if item.isdir():
                    continue
                if not item.isfile():
                    raise ValueError("Linked or special archive member")
                def read(item=item):
                    with archive.extractfile(item) as stream:
                        return stream.read()
                add(item.name, item.size, read)
    return result


def inspect_distribution(path: Path, version: str) -> dict:
    """Check metadata, CLI/resources, licenses and private-file boundaries in one archive."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("Distribution must be a regular unlinked file")
    files = _members(path)
    wheel = path.suffix == ".whl"
    if wheel:
        metadata_paths = [name for name in files if re.fullmatch(r"[^/]+\.dist-info/METADATA", name)]
        if len(metadata_paths) != 1:
            raise ValueError("Wheel must contain exactly one metadata record")
        info = metadata_paths[0].rsplit("/", 1)[0]
        payload = {name[6:]: data for name, data in files.items() if name.startswith("aikit/")}
        metadata_bytes = files[metadata_paths[0]]
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string(files.get(info + "/entry_points.txt", b"").decode("utf-8"))
        if parser.get("console_scripts", "aikit", fallback="") != "aikit.aikit_cli:main":
            raise ValueError("Missing aikit console entry point")
        wheel_metadata = files.get(info + "/WHEEL", b"")
        if b"Root-Is-Purelib: true" not in wheel_metadata or b"Tag: py3-none-any" not in wheel_metadata:
            raise ValueError("Expected a portable pure-Python wheel")
    else:
        roots = {name.split("/", 1)[0] for name in files}
        if len(roots) != 1:
            raise ValueError("Source archive must have one root")
        prefix = next(iter(roots)) + "/"
        payload = {name[len(prefix):]: data for name, data in files.items()}
        metadata_bytes = payload.get("PKG-INFO", b"")
    metadata = BytesParser(policy=policy.default).parsebytes(metadata_bytes)
    if metadata.get("Name") != PROJECT_NAME or metadata.get("Version") != version:
        raise ValueError("Archive name/version metadata does not match the release")
    if metadata.get("Requires-Python") != ">=3.10" or metadata.get_all("Requires-Dist"):
        raise ValueError("Unexpected runtime Python/dependency contract")
    if metadata.get("License-Expression") != "MIT AND Apache-2.0":
        raise ValueError("Missing complete distribution license expression")
    if set(metadata.get_all("License-File", [])) != set(LICENSES):
        raise ValueError("Missing bundled license declarations")
    if metadata.get("Description-Content-Type") != "text/markdown":
        raise ValueError("Missing Markdown description content type")
    if not metadata.get("Author") or len(metadata.get_all("Project-URL", [])) < 5:
        raise ValueError("Missing author or project URLs")
    if not REQUIRED.issubset(payload) or payload["VERSION"].decode().strip() != version:
        raise ValueError("Missing required distribution resources or bundled VERSION")
    for name in payload:
        parts = PurePosixPath(name).parts
        if name in LOCAL_FILES or PRIVATE_PARTS.intersection(parts) or any(p.startswith(".env") for p in parts):
            raise ValueError("Private local content included in distribution")
        if (parts[-1] in {"auth.json", ".netrc", ".pypirc"}
                or parts[-1].endswith((".pem", ".p12", ".pfx"))
                or parts[-1].startswith(("id_rsa", "id_ed25519"))):
            raise ValueError("Credential file included in distribution")
    description = metadata.get_payload().replace("\r\n", "\n").strip()
    if description != payload["docs/PYPI_DESCRIPTION.md"].decode("utf-8").replace("\r\n", "\n").strip():
        raise ValueError("Package description differs from its canonical source")
    if re.search(r"\]\((?!https://|mailto:|#)[^)]+\)", description) or "```mermaid" in description:
        raise ValueError("PyPI description contains nonportable links or diagrams")
    if wheel:
        for name in LICENSES:
            if files.get(info + "/licenses/" + name) != payload[name]:
                raise ValueError("Wheel license payload is missing or changed")
    return {"file": path.name, "version": version, "payload_files": len(payload),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def check_archives(directory: Path, version: str) -> list[dict]:
    paths = sorted(directory.glob("*.whl")) + sorted(directory.glob("*.tar.gz"))
    if len(paths) != 2 or sum(path.suffix == ".whl" for path in paths) != 1:
        raise ValueError("Expected exactly one wheel and one source archive")
    return [inspect_distribution(path, version) for path in paths]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    identity = sub.add_parser("identity", help="Validate a manual build/publication request; never uploads")
    identity.add_argument("--expected-version", default="")
    identity.add_argument("--destination", choices=("validate", "testpypi", "pypi"), default="validate")
    identity.add_argument("--ref", default="")
    identity.add_argument("--repository", default="")
    archives = sub.add_parser("archives", help="Inspect a prepared wheel and sdist; never uploads")
    archives.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    try:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        if args.command == "identity":
            result = release_identity(version, args.expected_version, args.destination, args.ref, args.repository)
        else:
            result = {"archives": check_archives(args.directory, version), "upload_performed": False}
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError, configparser.Error, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc), "upload_performed": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
