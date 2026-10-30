# ADR 0016: Consistent distributions, safer project checks and selectable Docker cleanup

Status: accepted for code, local tests and Docker smoke; hosted release runs and live client activation are separate.

## Context

A review of v1.4.3-v1.4.5 found that the same version shipped different bytes: a Windows working tree with `core.autocrlf=true` produced CRLF text in the Docker image while the Linux-built wheel carried LF, so installers compared different hashes and proposed rewrites or conflicts. The optional project CI cloned an unpinned AI-KIT revision and reinstalled it on every push. The CLI ignored SIGTERM as PID 1 without `--init`. The release build job installed unpinned twine dependencies next to the files it published. Read-only fact detection refused projects with linked manifests, and v1.4.5 made host reclamation and builder-cache removal a completion requirement for every Docker task in every installed project.

## Decision

- Pin every text checkout to LF through `.gitattributes`; pinned vendor bytes stay `-text`. Installers treat line-ending-only differences as unchanged, so earlier CRLF installations upgrade without churn or false conflicts. Docker smoke rejects CR in packaged text.
- The project CI template validates committed files only, with pinned actions; it never clones or installs AI-KIT.
- The CLI handles SIGTERM itself; smoke tests run with and without `--init`.
- The release build job installs only hash-pinned tools and publishes artifact digests; twine runs in a separate job; upload jobs verify digests before publishing. A text-level test guards these properties.
- Read-only project facts resolve files for reading inside the project and skip escapes instead of applying write guards.
- `docker_cleanup` selects `maximum` (default, the owner's v1.4.5 policy) or `keep-cache` (task-owned resources removed, dedicated builder cache kept, host reclamation on request or pressure).
- Tracked root entry files import CONTRIBUTING.md instead of local maintainer files; a local ignored CLAUDE.local.md can import them.
- The conditional document budget rises from 12000 to 24000 bytes so canonical rules stay readable; always-loaded budgets are unchanged.

## Consequences

Git, PyPI and Docker distributions of one version carry the same text bytes. Existing projects keep their files; only installer state records the new source hashes. The default cleanup behavior is unchanged. Upstream security-audit test files are verified but no longer installed; old copies remain until removed manually. Hosted workflow execution, owner-approved PyPI publication and Docker Hub publication remain separate, authorized steps.
