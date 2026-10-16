# PyPI package preparation and release

## Status and package identity

Release 1.4.2 is prepared for authorized PyPI publication on 2026-10-16; [release status](V1_4_2.md) records verification. PyPI registered a pending Trusted Publisher for `ai-kit-python`, repository `tigusigalpa/ai-kit`, workflow `publish-pypi.yml`, environment `pypi`. The GitHub environment allows only tag `v1.4.2` with owner review. No upload or hosted workflow run is established yet. VERSION is the version source; import package and executable are `aikit`. Python 3.10+ is required with no runtime dependencies.

PyPI rejected `ai-kit` and `ai-kit-cli` as too similar to existing projects; the owner selected `ai-kit-python`, whose pending-publisher registration succeeded. A public JSON 404 alone does not establish eligibility, and a pending publisher does not reserve a name. For a rename synchronize pyproject, archive checks, metadata smoke tests, workflow URLs, publisher configuration and install examples before rebuilding.

[pyproject.toml](../pyproject.toml) owns metadata. [PYPI_DESCRIPTION.md](PYPI_DESCRIPTION.md) is the complete Markdown description, with absolute public links and no GitHub-only diagrams. AI-KIT's own code remains MIT; the distribution also bundles Apache-2.0 Strix resources, so its SPDX expression is `MIT AND Apache-2.0`. All three declared license files are included under wheel dist-info/licenses and retained beside their payload resources.

## Install before and after publication

Before the first authorized upload, use a reviewed checkout and a virtual environment:

~~~powershell
$cliEnv = Join-Path $env:LOCALAPPDATA 'AI-KIT\venv'
python -m venv "$cliEnv"
& "$cliEnv\Scripts\Activate.ps1"
python -m pip install .
aikit --version
~~~

Keep that environment local; it is not an application dependency. After publication, users can run `pipx install ai-kit-python`, or `python -m pip install ai-kit-python` in a virtual environment. Update via `pipx upgrade ai-kit-python` or `python -m pip install --upgrade ai-kit-python`. Upgrading the CLI does not rewrite installed project instructions: preview `aikit install TARGET` and apply after review. [Usage](../README.md#packaged-cli-and-pypi-status).

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

[publish-pypi.yml](../.github/workflows/publish-pypi.yml) has only a manual workflow_dispatch trigger. Its default destination is `validate`, which builds/tests/retains artifacts and skips both upload jobs. Pushes, pull requests and GitHub releases do not trigger publishing. The existing required validation/wheel job names remain unchanged.

Configure these account settings separately when publication is authorized. PyPI and TestPyPI are separate services/accounts; use a pending publisher for a new project or add a publisher to an owned project.

| Field | Production | Test registry |
| --- | --- | --- |
| Registry | pypi.org | test.pypi.org |
| Project name | ai-kit-python | ai-kit-python, subject to availability |
| GitHub owner | tigusigalpa | tigusigalpa |
| Repository | ai-kit | ai-kit |
| Workflow filename | publish-pypi.yml | publish-pypi.yml |
| Environment | pypi | testpypi |

Create the exact GitHub environments in repository settings, restrict deployment refs to approved release tags and enable required reviewers where supported. Keep publisher environment names identical. Do not store a PyPI API token: the pinned PyPA action exchanges GitHub OIDC identity for a short-lived token. Only the upload jobs receive `id-token: write`; the build/test job has read-only repository access. Upload jobs retrieve the validated same-run artifact, check out no repository code and perform no build.

## Later authorized publication

1. Review VERSION, metadata, description, README examples, license files, tool/action pins and changes since the prior release. Complete local checks, including image-impact handling. Any Git commit/tag/push still requires its own authorization. Preserve existing tags: if a release tag predates publication support, prepare a new patch version instead of moving it.
2. After the reviewed workflow exists on the default branch, a `validate` dispatch can exercise hosted build-only preparation. Hosted results remain unknown until that run finishes.
3. For an upload, select the reviewed `vVERSION` tag, explicitly choose `testpypi` or `pypi`, and type the exact VERSION as confirmation. The guard rejects branches, other versions, missing confirmation and noncanonical repositories before artifact building. Each registry uses its own environment/publisher; production does not automatically upload to TestPyPI.
4. TestPyPI is the recommended first external trial. After an explicitly authorized trial, install the exact version in a fresh environment using `--index-url https://test.pypi.org/simple/ --no-deps`, inspect the CLI/resources and compare downloaded hashes. Do not mix TestPyPI and PyPI using an extra index.
5. After production upload, verify the public version, metadata, files, SHA-256 hashes and fresh isolated installation from PyPI. Record registry evidence separately from prepared local hashes; update publication status/examples only after read-back. Duplicate uploads fail rather than silently skipping a file.

No workflow is dispatched and no account/environment is configured by merely committing these files. Keep local preparation, hosted checks, registry activation and actual publication distinct. The candidate version must not be described as available on PyPI until verified.

## Docker and documentation continuity

Packaging metadata, description selection and bundled resource changes affect the CLI image: rebuild/test `ai-kit:dev`, verify new resources/version and preserve published release identities. Docker publication is separate. Follow [image refresh](DOCKER.md#change-impact-and-image-refresh) and the [Docker Hub checklist](../CONTRIBUTING.md#docker-hub-releases) when preparing an image release. Publication receipts alone may retain the tested image snapshot; record that boundary.

For every Python package release, refresh metadata/description/README, run archive checks, strict Twine validation and offline installation, and record unavailable OS/runtime checks. [Contribution rules](../CONTRIBUTING.md#python-package-releases) own the release-maintenance trigger.

Primary sources checked on 2026-10-16: [project metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [license expressions](https://packaging.python.org/en/latest/specifications/license-expression/), [PyPI descriptions](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/), [pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/), [OIDC publication](https://docs.pypi.org/trusted-publishers/using-a-publisher/), [PyPA action](https://github.com/pypa/gh-action-pypi-publish).
