# PyPI package preparation and release

## Status and package identity

Release [1.4.2 is published on PyPI](https://pypi.org/project/ai-kit-python/1.4.2/); [evidence](V1_4_2.md) records its workflow, uploaded hashes and clean registry installation. Trusted Publishing uses repository `tigusigalpa/ai-kit`, workflow `publish-pypi.yml`, environment `pypi`. On 2026-10-16 that environment was extended to future `v*` tags with owner review preserved. VERSION is the version source; distribution `ai-kit-python`, import package and executable `aikit`, Python 3.10+, no runtime dependencies. TestPyPI remains unconfigured.

PyPI rejected `ai-kit` and `ai-kit-cli` as too similar to existing projects; the owner selected `ai-kit-python`, whose pending-publisher registration succeeded. A public JSON 404 alone does not establish eligibility, and a pending publisher does not reserve a name. For a rename synchronize pyproject, archive checks, metadata smoke tests, workflow URLs, publisher configuration and install examples before rebuilding.

[pyproject.toml](../pyproject.toml) owns metadata. [PYPI_DESCRIPTION.md](PYPI_DESCRIPTION.md) is the complete Markdown description, with absolute public links and no GitHub-only diagrams. AI-KIT's own code remains MIT; the distribution also bundles Apache-2.0 Strix resources, so its SPDX expression is `MIT AND Apache-2.0`. All three declared license files are included under wheel dist-info/licenses and retained beside their payload resources.

## Install the published package

Use an isolated CLI installation with `pipx install ai-kit-python`, or a Python virtual environment:

~~~powershell
$cliEnv = Join-Path $env:LOCALAPPDATA 'AI-KIT\venv'
python -m venv "$cliEnv"
& "$cliEnv\Scripts\Activate.ps1"
python -m pip install ai-kit-python
aikit --version
~~~

Keep that environment local; it is not an application dependency. For a reviewed checkout, `python -m pip install .` remains available. Update via `pipx upgrade ai-kit-python` or `python -m pip install --upgrade ai-kit-python`. Upgrading the CLI does not rewrite installed project instructions: preview `aikit install TARGET` and apply after review. [Usage](../README.md#packaged-cli-and-pypi-status).

## Build and validate without uploading

Use an isolated checkout/source copy and an output directory outside it. This keeps archive binaries, temporary metadata and private maintainer files away from source validation and test fixture copies. Example from that source copy in PowerShell:

~~~powershell
$releaseEnv = Join-Path ([System.IO.Path]::GetTempPath()) ('ai-kit-build-env-' + [guid]::NewGuid())
python -m venv "$releaseEnv"
& "$releaseEnv\Scripts\Activate.ps1"
python -m pip install --require-hashes -r docker/build-requirements.txt
python -m pip install -r docker/pypi-requirements.txt

python scripts/check_kit.py
python -m unittest discover -s tests -v

$distPath = Join-Path ([System.IO.Path]::GetTempPath()) ('ai-kit-dist-' + [guid]::NewGuid())
python tests/build_distribution.py "$distPath"
python scripts/check_distribution.py archives "$distPath"
python -m twine check --strict "$distPath/*"
python tests/wheel_smoke.py "$distPath"
~~~

Use separate commands or stop on each nonzero exit. The build helper copies public source inputs into a disposable directory, injects synthetic private files, runs `build` to create sdist then wheel from sdist, and rejects leaked markers. Output inside the checkout or mixed with old archives refuses. The archive checker inspects paths without extracting, confirms metadata/version, description, CLI, resources, licenses and private-file exclusions, and reports SHA-256. Fresh-venv smoke exercises the installed CLI, optional resources and dialogue pipeline offline. Also check Python 3.10 compatibility and preserve the cross-platform CI matrix. Synthetic probes never read real credentials or conversations.

The source checker and publication identity helper upload nothing:

~~~sh
python scripts/check_distribution.py identity
~~~

## Trusted Publishing configuration

[publish-pypi.yml](../.github/workflows/publish-pypi.yml) supports `release: published` for stable releases and `workflow_dispatch` for manual runs. The Release path prepares production PyPI artifacts automatically, then waits for the owner's environment approval. Drafts and prereleases skip automatic production preparation. Pushes, tag pushes and Release edits do not request publication. Manual dispatch defaults to `validate`, which builds/tests/retains artifacts and skips both upload jobs. Existing required CI names remain unchanged.

Configure these account settings separately when publication is authorized. PyPI and TestPyPI are separate services/accounts; use a pending publisher for a new project or add a publisher to an owned project.

| Field | Production | Test registry |
| --- | --- | --- |
| Registry | pypi.org | test.pypi.org |
| Project name | ai-kit-python | ai-kit-python, subject to availability |
| GitHub owner | tigusigalpa | tigusigalpa |
| Repository | ai-kit | ai-kit |
| Workflow filename | publish-pypi.yml | publish-pypi.yml |
| Environment | pypi | testpypi |

The verified production environment requires reviewer `tigusigalpa` (GitHub user ID 2721390). Its custom deployment policy is **type `tag`, pattern `v*`**; matching branch names are not admitted. The same reviewer and all other environment protections were preserved when replacing the earlier v1.4.2-only policy. Self-review remains allowed so the sole owner can approve a run they started. The required confirmation must be performed by the human owner: agents must not approve or bypass it. [Contribution policy](../CONTRIBUTING.md#python-package-releases).

Keep publisher/environment names identical. No PyPI API token is stored: the pinned PyPA action exchanges GitHub OIDC identity for a short-lived credential after approval. Only upload jobs receive `id-token: write`; build/tests have read-only repository access. Upload jobs consume the validated same-run artifact without checking out or building source. Manual and Release production runs share a per-tag concurrency group and do not cancel each other during approval.

## Release to PyPI with owner approval

1. Review VERSION, metadata, description, README, licenses and changes since the prior release; complete checks and Docker-impact handling. Any Git commit/tag/push needs its own authorization. The reviewed release commit must contain the updated workflow and event guard. Existing tags, including v1.4.2, stay unchanged.
2. Prepare a new version, for example VERSION `1.5.0`, and a new tag `v1.5.0` at that commit. The automatic path accepts canonical stable `vMAJOR.MINOR.PATCH` tags; release tag, runner ref and the tag's VERSION must agree exactly. The guard also checks the event's repository against the canonical runner repository. Release notes/body are not commands or publication inputs.
3. Publish a stable GitHub Release for that tag. The workflow first verifies event identity, then validates the kit, runs tests, builds sdist followed by wheel, checks metadata/resources/privacy/licenses/description and smoke-installs offline. A failure stops the upload job.
4. In **Actions → Prepare or publish Python package**, wait for `build` to succeed. The `pypi` job then pauses at **Review deployments**. The human owner inspects the tag, commit and checks, selects `pypi`, and clicks **Approve and deploy**. Rejecting or leaving it pending uploads nothing. GitHub's required reviewer is the final gate; the agent does not submit this approval.
5. The approved upload job obtains OIDC credentials and publishes only that run's tested files. Verify the public version, metadata, files, hashes and fresh installation from PyPI; compare downloads against the actual hosted artifacts. Update publication receipts after read-back. The README badge follows PyPI availability, not GitHub Release creation.

### Manual runs and recovery

- **Build only:** use Run workflow with destination `validate`; a branch is allowed. No upload or environment approval occurs.
- **Manual upload:** select a `vVERSION` tag, choose `pypi` or `testpypi` and enter that exact version. Event inputs are checked before building; production uses the same human approval gate. Explicit manual prerelease trials remain possible.
- **TestPyPI:** configure its separate environment/publisher before an authorized trial. Install with `--index-url https://test.pypi.org/simple/ --no-deps`; do not mix it with PyPI using an extra index. Production does not automatically upload there.
- **Failed checks:** fix through the reviewed Git workflow and prepare a new release tag as needed. Do not move a released tag. The release workflow must exist in the tagged source; creating a Release for an older tag does not retrofit this implementation.
- **Duplicate version:** uploads fail instead of replacing files or silently skipping them. Use a new version for changed packages; check public files and hashes before considering a retry of a partial upload.

Committing these files alone neither creates a GitHub Release nor uploads a package. Keep prepared source, hosted checks, environment approval and registry evidence distinct. No future version is available on PyPI until read-back verifies it.

## Release-chain verification

Verified on 2026-10-16: kit checks returned no errors/warnings; 368 packaged Linux/Python 3.13.16 tests ran with two Windows-only skips. Fifteen new event tests cover future tags, invalid release identities, manual defaults and untrusted payloads. Workflow YAML/security assertions and Python 3.10 grammar passed. Isolated sdist-to-wheel, privacy probes, strict Twine and offline Windows wheel smoke passed. Local ai-kit:dev was rebuilt and passed Docker smoke; ten changed packaged resources matched source. These local runs did not cover macOS or a hosted Release event. No package/image was uploaded. The tested image retains the earlier documentation snapshot preceding this verification receipt.

## Docker and documentation continuity

Packaging metadata, description selection and bundled resource changes affect the CLI image: rebuild/test `ai-kit:dev`, verify new resources/version and preserve published release identities. Docker publication is separate. Follow [image refresh](DOCKER.md#change-impact-and-image-refresh) and the [Docker Hub checklist](../CONTRIBUTING.md#docker-hub-releases) when preparing an image release. Publication receipts alone may retain the tested image snapshot; record that boundary.

For every Python package release, refresh metadata/description/README, run archive checks, strict Twine validation and offline installation, and record unavailable OS/runtime checks. [Contribution rules](../CONTRIBUTING.md#python-package-releases) own the release-maintenance trigger.

Primary sources checked on 2026-10-16: [project metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [license expressions](https://packaging.python.org/en/latest/specifications/license-expression/), [PyPI descriptions](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/), [pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/), [OIDC publication](https://docs.pypi.org/trusted-publishers/using-a-publisher/), [PyPA action](https://github.com/pypa/gh-action-pypi-publish).

Release/approval sources checked on 2026-10-16: [release events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#release), [deployment tag policies](https://docs.github.com/en/rest/deployments/branch-policies), [human deployment review](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments).
