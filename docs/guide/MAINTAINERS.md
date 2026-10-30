# For maintainers

![For maintainers](https://i.postimg.cc/jjJ13S2b/15-for-maintainers.jpg)

Applications install from `template/`; the root maintains AI-KIT itself (`scripts/`, `integrations/`, `templates/`, `docs/`). Root `AGENTS.md`, `PROJECT_CONTEXT.md` and `WIKI.md` are local maintainer files: ignored, untracked and excluded from wheel/Docker builds. Their template counterparts remain public. A clean clone works without local copies; public maintenance starts at [CONTRIBUTING](../../CONTRIBUTING.md). Before contributing, run:

~~~sh
python scripts/check_kit.py
python -m unittest discover -s tests -v
~~~

See [CONTRIBUTING.md](../../CONTRIBUTING.md), [updating a reference repository](../../CONTRIBUTING.md#updating-a-reference-repository), [verification records](../IMPLEMENTATION.md#verification), and [SECURITY.md](../../SECURITY.md). Bundle version: [VERSION](../../VERSION).

## Publication copy

- [PyPI description](../PYPI_DESCRIPTION.md) contains portable publication copy; the [release guide](../PYPI.md) covers local builds, archive/privacy checks, TestPyPI, OIDC publisher fields and later publication.
- The [Docker Hub Overview](../DOCKER_HUB_OVERVIEW.md) covers capabilities, release changes and launch examples; maintain it for every image release using the [release checklist](../../CONTRIBUTING.md#docker-hub-releases).
- Image build checks and the Docker smoke test are described in [Verify or update the image](DOCKER.md#verify-or-update-the-image); the [maintainer contract and results](../DOCKER.md) records pins, packaging, checks and unavailable environments.

## Publish future releases to PyPI

[publish-pypi.yml](../../.github/workflows/publish-pypi.yml) supports **GitHub Release → checks → your approval → PyPI**. Publishing a stable GitHub Release starts production preparation; the upload waits for your review of environment `pypi`. Manual dispatch remains available and defaults to build-only `validate`. No permanent registry token is needed.

1. Prepare the new version through the normal reviewed Git workflow. For example, put `1.5.0` in `VERSION`, update release documentation and complete the kit/package checks. Assess Docker impact through the existing image-refresh procedure. The tag's source must contain the updated release workflow and event guard.
2. Create a new tag such as `v1.5.0` at that prepared commit. **The tag and its committed `VERSION` must match exactly.** Preserve previous tags and published versions.
3. On GitHub, create and publish a normal Release for that tag. `release: published` starts the workflow automatically. Saving a draft, pushing a tag alone, editing an existing Release or marking it as a prerelease does not request automatic production publication.
4. Open **Actions → Prepare or publish Python package**. Its `build` job checks the release identity, runs kit validation and behavioral tests, builds a source archive and wheel, validates metadata/resources/privacy and the description, then smoke-installs the wheel. A failed check prevents the upload job from proceeding.
5. After checks pass, the `pypi` job waits at **Review deployments**. Inspect the tag, commit and successful checks, select environment **pypi**, and click **Approve and deploy**. Required reviewer: repository owner `tigusigalpa`. **This confirmation is a human step; agents must not approve or bypass it on your behalf.** For solo maintenance the owner may approve a run they initiated.
6. GitHub exchanges its OIDC identity for a short-lived PyPI credential and uploads only the same-run validated artifacts. The upload job builds no code. Verify the new version on [PyPI](https://pypi.org/project/ai-kit-python/), compare its file hashes with the run artifacts, and check installation in a fresh environment. The README PyPI badge then follows the published version automatically.

The live `pypi` deployment policy accepts **tags `v*`**, so future versions do not need a new allowlist entry. Branches are excluded. The event guard separately requires a canonical stable tag of the form `vMAJOR.MINOR.PATCH`, the canonical repository, a published non-draft/non-prerelease Release and matching `VERSION`. Tests and your approval remain required for each production run.

For a manual run, choose **Run workflow**, select the versioned tag, set `destination=pypi`, and type the exact version in `version`. Uploads use the same approval gate. `destination=validate` only builds and tests; `testpypi` is an explicit separate registry with its own environment/publisher setup. Prerelease trials can use that manual route. Republishing the same PyPI version fails rather than replacing or silently skipping files.

The Release path is included in **v1.4.3 and later tagged source**. Existing `v1.4.2` stays unchanged. The complete [release procedure](../PYPI.md#release-to-pypi-with-owner-approval) includes activation, recovery and configuration verification. Each stable release still needs your human approval before PyPI upload.

## Release verification records

The complete evidence is in the [1.4.5 release record](../V1_4_5.md).

- **Published versions:** Docker image 1.4.5 and PyPI package 1.4.5. Earlier published versions remain intact.
- **PyPI publication, verified on 2026-10-30:** GitHub Release → checks → owner approval → PyPI completed successfully. [Workflow 41076353098](https://github.com/tigusigalpa/ai-kit/actions/runs/41076353098) completed build and production upload through Trusted Publishing after the human owner's approval. Both PyPI file hashes match the validated workflow artifacts; TestPyPI was not used. [PyPI receipt](../V1_4_5.md#pypi-publication-status).
- **Installation, verified on 2026-10-30:** a clean Windows/Python 3.12.14 environment installed `ai-kit-python==1.4.5` from PyPI with the verified wheel hash, dependencies and cache disabled. `aikit --version` returned `aikit 1.4.5`; CLI/orchestration help, memory/orchestration imports and the installed kit check passed without errors or warnings. [Published hashes and installation record](../V1_4_5.md#pypi-publication-status).
- **Docker Hub, verified on 2026-10-30:** `tigusigalpa/ai-kit:1.4.5`, `linux/amd64`. Docker manifest/configuration/layers and immutable pull are verified and match the tested build. Existing tags are retained; no `latest` tag was assigned. [Docker receipt](../V1_4_5.md#docker-hub-publication).
