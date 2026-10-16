# Contributing

Read [Core](template/ai-kit/CORE.md) and [policy ownership](docs/IMPLEMENTATION.md#policy-ownership).
Make a coherent local change, add behavioral checks for installer or validator risks, and run the documented checks.
Keep project templates free of maintainer facts/history. Preserve local-file ownership and authorization boundaries.
Update the root changelog; record significant design decisions in docs/adr/.
Discuss version/provider changes using current primary documentation and actual runtime evidence. Commit/push authorization follows Core.

## Local maintainer files

Root `AGENTS.md`, `PROJECT_CONTEXT.md` and `WIKI.md` are optional local maintainer files. Keep them on disk, ignored and untracked; do not copy their contents into public documents or build artifacts. Read them when present and preserve local agreements. Otherwise establish current facts from VERSION, pyproject, source and the public guides. Their `template/` counterparts are distribution sources and remain tracked for application installation.

Ignore rules do not untrack existing files. Use `git rm --cached -- AGENTS.md PROJECT_CONTEXT.md WIKI.md` to stop tracking only the root copies while keeping them on disk. This stages removal for a later authorized commit; it does not erase earlier history. Do not force-add local copies. Public documents and checks must work without them; wheel and Docker builds exclude them even when present.

## Maintainer workflow

Follow plan -> implement -> test -> review -> document. Run `python scripts/check_kit.py` and `python -m unittest discover -s tests -v` for affected installer/checker behavior. When packaging changes, build from an isolated source copy and smoke-install the wheel. Review preservation, conflicts, links, visibility and upgrades; report unavailable checks.

Assess [Docker impact](docs/DOCKER.md#change-impact-and-image-refresh) on every task and rebuild/test affected final sources locally. Publication needs authorization. Update the root changelog, any local context/map and the continuity skill when procedures change. Keep templates free of kit history; do not bootstrap this distribution as an application.

## Docker Hub releases

Update [DOCKER_HUB_OVERVIEW.md](docs/DOCKER_HUB_OVERVIEW.md) for every AI-KIT Docker image release, including patch releases and authorized replacements of an existing tag. Keep the complete publication copy in that file; README and the [Docker guide](docs/DOCKER.md) link to it.

Before building, synchronize its version/tag, feature summary, release changes, optional modules, CLI examples and runtime/platform contract with VERSION, README and actual sources. Record only checks that ran. After an authorized push, read back the remote digest and configuration, then update publication status and the immutable pull example from that evidence. Never invent a digest or claim local preparation is publication. Keep descriptive publication receipts separate from the prepared image snapshot; do not rebuild/replace an image just to include its own digest.

The root README and Docker Hub Overview are user documentation without a size quota. Other document and instruction budgets remain scoped. Preparing this file does not itself publish a Docker Hub description, image or Git release; the relevant authorization still applies.

## Python package releases

Follow [PyPI preparation and release](docs/PYPI.md) for every package release. Synchronize VERSION, pyproject metadata, [description](docs/PYPI_DESCRIPTION.md) and README; verify license/resource inclusion and local-file exclusions in both sdist and wheel, build the wheel from sdist, run strict Twine checks and offline fresh-venv smoke. Preserve existing CI matrix/job names. Refresh the image when packaging changes affect it.

Trusted Publishing remains manual and build-only by default. Registry uploads require the matching version/tag, canonical repository and the separately configured registry environment/publisher. Build tests have no OIDC permission; upload jobs consume only validated same-run artifacts. Record local, hosted and registry results separately. No upload, publisher/account setup or Git operation is authorized by preparation alone.

## Repository maintenance

Before changing remote protection or required CI checks, verify live configuration and emitted names. Local jobs establish neither hosted success nor updated protection. Remote changes, commits, pushes and publication need the relevant user authorization. Private context snapshots require verification before use.

## Updating a reference repository

Archive overlays leave old files behind. Compatibility pointers retain known v0.1 rule paths.
Overlay the bundle at the reference root, preserve customizations, and run the checker.

The obsolete .gitignore_real is historical material: its useful rules live in the templates/ policies, scoped by the installer where a global rule would hide project source (Composer vendor, Moodle config.php, Node and Python output). Use templates/ policies for applications.
Keep the root [SKILL.md](SKILL.md) current when commands, options, or features change.
Retire old pointers after reviewing inbound links and local changes.
