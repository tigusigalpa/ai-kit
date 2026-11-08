"""Guard the security properties of the release and project-check workflows (text-level, stdlib only)."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = [ROOT / ".github/workflows/publish-pypi.yml", ROOT / ".github/workflows/check-kit.yml",
             ROOT / "integrations/ai-kit-check.yml"]
PYTHON_SETUP = ROOT / ".github/actions/setup-python-retry/action.yml"
LOCAL_PYTHON_SETUP = "./.github/actions/setup-python-retry"


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
        for path in [*WORKFLOWS, PYTHON_SETUP]:
            for action in re.findall(r"uses:\s*([^\s#]+)", self.read(path)):
                with self.subTest(path=path.name, action=action):
                    if action == LOCAL_PYTHON_SETUP and path in WORKFLOWS[:2]:
                        self.assertTrue(PYTHON_SETUP.is_file())
                        self.assertFalse(PYTHON_SETUP.is_symlink())
                        continue
                    self.assertRegex(action, r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")

    def test_python_setup_retries_are_bounded_and_fail_closed(self):
        text = self.read(PYTHON_SETUP)
        blocks = re.split(r"(?m)^    - name: ", text.split("  steps:\n", 1)[1])[1:]
        self.assertEqual(len(blocks), 5)
        attempts = [block for block in blocks if "\n      uses:" in block]
        self.assertEqual(len(attempts), 3)
        for number, block in enumerate(attempts, 1):
            with self.subTest(attempt=number):
                self.assertIn(f"\n      id: attempt_{number}\n", block)
                self.assertIn("python-version: ${{ inputs.python-version }}", block)
                self.assertIn("actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97", block)
                self.assertEqual("continue-on-error: true" in block, number < 3)
                if number == 1:
                    self.assertNotIn("\n      if:", block)
                else:
                    self.assertIn("if: ${{ !cancelled() && steps.attempt_" + str(number - 1)
                                  + ".outcome == 'failure' }}", block)
        self.assertEqual(text.count("continue-on-error:"), 2)
        self.assertNotIn("always()", text)
        self.assertNotIn("github.token", text)
        self.assertNotIn("secrets.", text)
        self.assertNotIn("pip install", text)
        self.assertNotIn("unittest", text)

    def test_retry_delays_run_only_after_the_matching_failed_attempt(self):
        text = self.read(PYTHON_SETUP)
        blocks = re.split(r"(?m)^    - name: ", text.split("  steps:\n", 1)[1])[1:]
        waits = [block for block in blocks if "\n      run:" in block]
        self.assertEqual(len(waits), 2)
        for number, delay in ((1, 20), (2, 40)):
            block = waits[number - 1]
            self.assertIn("if: ${{ !cancelled() && steps.attempt_" + str(number)
                          + ".outcome == 'failure' }}", block)
            self.assertIn("shell: pwsh", block)
            self.assertIn(f"Start-Sleep -Seconds {delay}\n", block)
            self.assertNotIn("${{", block.split("run:", 1)[1])

    def test_retry_outputs_prefer_the_latest_successful_setup(self):
        outputs = self.read(PYTHON_SETUP).split("outputs:\n", 1)[1].split("\nruns:", 1)[0]
        for output in ("python-version", "python-path"):
            self.assertIn("value: ${{ steps.attempt_3.outputs." + output + " || steps.attempt_2.outputs."
                          + output + " || steps.attempt_1.outputs." + output + " }}", outputs)

    def test_repository_python_setup_uses_the_checked_out_retry_action(self):
        for path, expected in zip(WORKFLOWS[:2], (2, 3)):
            text = self.read(path)
            self.assertEqual(text.count("uses: " + LOCAL_PYTHON_SETUP), expected)
            self.assertEqual(text.count("timeout-minutes: 15"), expected)
            self.assertNotIn("uses: actions/setup-python@", text)
            for block in jobs(text).values():
                if "uses: " + LOCAL_PYTHON_SETUP in block:
                    self.assertNotIn("continue-on-error:", block)
                    self.assertIn("persist-credentials: false", block)
                    self.assertLess(block.index("uses: actions/checkout@"), block.index("uses: " + LOCAL_PYTHON_SETUP))
        # The installer-owned project workflow cannot depend on a maintainer-only local action.
        self.assertNotIn(LOCAL_PYTHON_SETUP, self.read(WORKFLOWS[2]))

    def test_required_check_matrix_and_names_remain_compatible(self):
        blocks = jobs(self.read(WORKFLOWS[1]))
        self.assertEqual(set(blocks), {"validate", "wheel", "docker"})
        for name in ("validate", "wheel"):
            self.assertIn("os: [ubuntu-latest, windows-latest, macos-latest]", blocks[name])
            self.assertIn("fail-fast: false", blocks[name])
            self.assertNotIn("\n    name:", blocks[name])
        self.assertIn("python: ['3.10', '3.13', '3.14']", blocks["validate"])
        self.assertIn("python: ['3.10', '3.14']", blocks["wheel"])
        self.assertIn("name: Docker CLI", blocks["docker"])

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
