"""Guard the security properties of the release and project-check workflows (text-level, stdlib only)."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = [ROOT / ".github/workflows/publish-pypi.yml", ROOT / ".github/workflows/check-kit.yml",
             ROOT / "integrations/ai-kit-check.yml"]


def jobs(text: str) -> dict[str, str]:
    """Split the top-level jobs mapping into job-name -> block text."""
    body = text.split("\njobs:\n", 1)[1]
    blocks: dict[str, str] = {}
    name = None
    for line in body.splitlines():
        if line.lstrip().startswith("#"):
            continue
        match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if match:
            name = match.group(1)
            blocks[name] = ""
        elif name is not None:
            blocks[name] += line + "\n"
    return blocks


class WorkflowSecurityTests(unittest.TestCase):
    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_actions_are_pinned_to_full_commit_shas(self):
        for path in WORKFLOWS:
            for action in re.findall(r"uses:\s*([^\s#]+)", self.read(path)):
                with self.subTest(path=path.name, action=action):
                    self.assertRegex(action, r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")

    def test_no_privileged_pull_request_trigger(self):
        for path in WORKFLOWS:
            self.assertNotIn("pull_request_target", self.read(path))

    def test_publish_tokens_are_scoped_to_upload_jobs(self):
        text = self.read(WORKFLOWS[0])
        self.assertIn("\npermissions:\n  contents: read\n", text)
        blocks = jobs(text)
        for name, block in blocks.items():
            with self.subTest(job=name):
                self.assertEqual("id-token: write" in block, name in {"pypi", "testpypi"})

    def test_build_job_runs_only_hash_pinned_tools(self):
        build = jobs(self.read(WORKFLOWS[0]))["build"]
        self.assertIn("--require-hashes -r docker/build-requirements.txt", build)
        self.assertNotIn("pypi-requirements", build)
        self.assertNotIn("twine", build)
        for line in (ROOT / "docker/build-requirements.txt").read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                self.assertRegex(line, r"==\S+.*--hash=sha256:[0-9a-f]{64}$")

    def test_build_tools_pin_conditional_dependencies_for_python_310(self):
        # build requires tomli below Python 3.11; hash mode refuses any unpinned transitive requirement.
        requirements = (ROOT / "docker/build-requirements.txt").read_text(encoding="utf-8")
        self.assertRegex(requirements, r'(?m)^tomli==\S+ ; python_version < "3\.11" --hash=sha256:[0-9a-f]{64}$')
        self.assertIn("'3.10'", self.read(WORKFLOWS[1]))

    def test_uploads_need_twine_check_and_verify_build_digests(self):
        blocks = jobs(self.read(WORKFLOWS[0]))
        self.assertIn("twine check --strict", blocks["twine-check"])
        self.assertNotIn("id-token", blocks["twine-check"])
        for name in ("pypi", "testpypi"):
            with self.subTest(job=name):
                block = blocks[name]
                self.assertIn("needs: [build, twine-check]", block)
                self.assertIn("needs.build.outputs.sha256", block)
                self.assertIn("sha256sum --check --strict", block)
                self.assertNotIn("actions/checkout", block)
                self.assertLess(block.index("sha256sum --check"), block.index("gh-action-pypi-publish"))

    def test_project_check_installs_nothing(self):
        text = self.read(WORKFLOWS[2])
        self.assertNotIn("git clone", text)
        self.assertNotIn("install.py", text)
        self.assertIn("persist-credentials: false", text)


if __name__ == "__main__":
    unittest.main()
