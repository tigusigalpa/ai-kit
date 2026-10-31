# AI-KIT changelog

## v1.5.0 (2026-10-30)

- New `aikit mcp report TARGET`: lists MCP servers from project client files (Claude Code, Cursor, VS Code/Copilot, Gemini CLI, Codex, Roo, Kimi Code) with transport, command, URL origin, variable names, approval and tool settings and Git tracking. It never prints secret values and warns about literal credentials, inline OAuth client secrets, credentials in URLs, plain remote HTTP and auto-approval. Read-only: no server is started or contacted. The installed MCP posture points to it. [Guide](docs/guide/INSTALL.md#review-mcp-servers).
- Downgrade guard: when a project records a newer AI-KIT than the installer, preview warns and `--apply` (also `doctor --fix --apply`) refuses unless the new `--allow-downgrade` flag is passed.
- `aikit doctor` names the upgrade commands when a newer AI-KIT is available and warns when the CLI is older than the installation; `doctor --fix` output includes the plan warnings.
- The [Docker Hub Overview](docs/DOCKER_HUB_OVERVIEW.md) describes image 1.5.0, including the 1.4.6 and 1.4.7 changes it brings to Docker Hub; the registry digest is recorded after publication.
- Published Docker Hub `tigusigalpa/ai-kit:1.5.0` (linux/amd64) from the v1.5.0 tag: anonymous manifest/configuration/layer read-back and an immutable pull matched the tested image, whose packaged files equal the hosted release wheel. README and the Docker guides now name 1.5.0. [Docker receipt](docs/V1_5_0.md#docker-hub-publication).
- Published `ai-kit-python` 1.5.0 after the owner's approval; PyPI hashes match the workflow artifacts and a fresh hashed installation passed. [PyPI receipt](docs/V1_5_0.md#pypi-publication-status).
- [Decision](docs/adr/0018-mcp-report-and-downgrade-guard.md), [release record](docs/V1_5_0.md).

## v1.4.7 (2026-10-30)

- New `aikit flags` command prints every `aikit install` option as JSON (value type, choices, repeatability, exclusions, saved setting, fresh default, help, presets); the committed copy [installer-flags.json](integrations/installer-flags.json) is the source for documentation tools such as the [documentation site](https://tigusigalpa.github.io/ai-kit-docs/).
- Kit validation now fails when that schema, the [flag guide](docs/guide/INSTALLER_FLAGS.md) or SKILL.md drifts from the installer parser: stale schema, undocumented or invented options, undocumented choice values. Every installer option has help text in `aikit install --help`.
- Gemini routing declares the documented `thinking_level` values per model (Flash-Lite: minimal-high; Flash and Pro: low-high) with each model's default as the role default, replacing the "effort unknown" fallback. Installed router guidance explains the mapping.
- Published `ai-kit-python` 1.4.7 after the owner's approval; PyPI hashes match the workflow artifacts and a fresh hashed installation passed. [PyPI receipt](docs/V1_4_7.md#pypi-publication-status).
- Maintenance: release receipts stay in release records rather than maintainer context; build-tool changes are exercised on Python 3.10. [Decision](docs/adr/0017-installer-flag-schema-and-gemini-thinking.md), [release record](docs/V1_4_7.md).

## v1.4.6 (2026-10-30)

For installed projects:

- Kit text is LF in every distribution (`* text=auto eol=lf`), so Git checkouts, the PyPI wheel and the Docker image carry identical bytes. Upgrades treat line-ending-only differences as unchanged: earlier CRLF installations neither rewrite nor conflict.
- The `--with-ci` workflow validates committed AI-KIT files with pinned actions; it no longer clones an unpinned AI-KIT or reinstalls on every push. The private-mode warning now explains that team mode keeps the files to check.
- New `docker_cleanup` setting and `--docker-cleanup maximum|keep-cache` flag. `maximum` (default) keeps the v1.4.5 policy; `keep-cache` still removes task-owned resources but keeps the dedicated project builder cache and reclaims host RAM/disk only on request or pressure. CONTAINERS regains its full Kubernetes wording.
- Fresh installs no longer refuse projects with linked manifests or unusual module directory names; secondary stacks (Rust, .NET, Java, Infra) fill missing commands instead of replacing pytest/npm/Go commands; `./mvnw`/`./gradlew` wrappers are no longer auto-allowed.
- `--with-security-audit` stops installing upstream `*.test.cjs` files that host test runners collected (still verified in the manifest); remove old copies from `ai-kit/vendor/security-audit/` manually. Delegated audit prompts must mark target content as untrusted data.
- Doctor: `--fix` previews and `--fix --apply` writes; non-UTF-8 Markdown, environment/build folders and private dialogue/design/orchestration data no longer crash, flood or leak into reports; a malformed project.json is a warning. `install --apply --check` reports a doctor failure after successful writes accurately.
- Memory imports keep labels such as Turkish "İ" as notes instead of aborting; `context snapshot` backs up project.json and keeps non-ASCII text readable; writer locks explain recovery; atomic writes fsync.

CLI, packaging and image:

- The CLI handles SIGTERM as PID 1 (Kubernetes Jobs, `docker run` without `--init`); smoke tests cover both. The image label declares `MIT AND Apache-2.0` and records the source revision; images are built from a clean LF export.
- The PyPI build job installs only hash-pinned tools (now including `build` and its Python 3.10 `tomli` dependency), records artifact SHA-256 digests, and leaves twine to a separate job; upload jobs verify the digests before publishing. A workflow-security test guards pinned actions, token scope and these steps.
- README is a 23 KB landing page with install paths (PyPI `ai-kit-python`, the image, a checkout), visible defaults (Russian chat, owner conventions) and honest feature wording; the reference material moved to [user guides](docs/guide/README.md). README installer flag tables, defaults, persistence and command examples now live in the [flag reference](docs/guide/INSTALLER_FLAGS.md).
- Tracked CLAUDE.md, KIMI.md and MANUS.md point to CONTRIBUTING.md and work in a clean clone; a local ignored CLAUDE.local.md can import the private AGENTS.md. The conditional document budget rises to 24000 bytes; always-loaded budgets stay 2500/3000.
- README features the [documentation site](https://tigusigalpa.github.io/ai-kit-docs/) (command configurator, CLI installation, flag reference) in a highlighted block, badge and navigation link; the guides index, PyPI description, Docker Hub Overview, SKILL.md and the PyPI `Documentation` project URL point to it.
- [Decision](docs/adr/0016-consistent-distributions-and-safer-defaults.md), [release record](docs/V1_4_6.md).

## v1.4.5 (2026-10-30)

- Require maximum disposable Docker cleanup after every build/test/debug task, without a size/age threshold; include containers, volumes, networks, unnecessary test images and dedicated-builder cache.
- Require separate host RAM/disk reclamation, supported WSL2 settings and offline compaction; preserve persistent data, unrelated workloads and reviewed retention scope.
- Updated installed AGENTS/docs; tested private/team upgrades and conflicts; published/verified Docker Hub and owner-approved PyPI 1.4.5, including a fresh registry installation. [Release record](docs/V1_4_5.md).
- Added a detailed Windows README guide covering setup, inherited/stale PATH, persistent user PATH, isolated CLI, common errors and project updates.

## v1.4.4 (2026-10-18)

- Added opt-in Codex helpers and a bounded OpenRouter executor with capped-key preflight, reservations, private accounting, source-bound review and billing reconciliation; preserved installer defaults/edits and added tests, packaging and instructions.
- Published and verified Docker Hub/PyPI 1.4.4, exact hosted hashes, registry installation and image behavior; refreshed README/Overview. [Complete entry and evidence](docs/V1_4_4.md).

## v1.4.3 (2026-10-16)

- Added a live PyPI version badge to README.
- Added stable GitHub Release checks and owner-approved PyPI uploads, event/version/repository guards, future v* tags and manual validation. [Procedure](docs/PYPI.md#release-to-pypi-with-owner-approval). Archived v0.13.0 text intact.
- Added fifteen event regression tests. Before labeling, 32 hosted checks and build-only verification passed, plus kit, 368 Linux tests (two skips), archive/privacy/Twine/offline wheel and Docker checks. [Verification](docs/V1_4_3.md).
- Verified 1.4.3 CLI/archive/image identity, offline packaging, Docker smoke, 368 Linux tests and preserved private/team upgrades from v1.4.2.
- Verified PyPI 1.4.3 publication, matching hosted hashes and fresh registry installation; [receipt](docs/V1_4_3.md#pypi-publication-and-read-back).
- Published Docker Hub 1.4.3 with verified image/digest and refreshed README/Overview; [receipt](docs/V1_4_3.md#docker-hub-143).

## v1.4.2 (2026-10-16)

- Verified kit/archive/offline installation, 351 Linux tests (two skips), 23 Windows CLI/archive tests and Docker smoke. [Evidence](docs/V1_4_2.md).
- Published `ai-kit-python` 1.4.2 with verified PyPI hashes and installation. Preserved v1.4.1 Git/Docker; [evidence](docs/V1_4_2.md).
- Fixed quoted Twine wildcards for Windows CI.
- Added PyPI metadata, a portable [description](docs/PYPI_DESCRIPTION.md), README guidance and a [release procedure](docs/PYPI.md). Wheel/sdist checks cover metadata, licenses, resources, private files, offline installation and publication identity. Manual Trusted Publishing defaults to validation, requires exact version/tag/repository, and gives OIDC only to upload jobs consuming tested artifacts. Required CI names stay unchanged.
- Isolated builds inject synthetic private probes; archives exclude private drafts and credential filenames. Added tested `aikit --version`; published Docker 1.4.1 examples use its existing `--help`. Added a README Docker Hub badge.

- Saved the complete [Docker Hub Overview](docs/DOCKER_HUB_OVERVIEW.md) for v1.4.1 and linked it from README/Docker docs. The [release checklist](CONTRIBUTING.md#docker-hub-releases) and continuity skill require updating it for every image release, with verified publication identity recorded after push. Exempted only this user-facing document from the size quota alongside README; instruction budgets remain unchanged, with regression coverage.

## v1.4.1 (2026-10-15)

- Added [image freshness](docs/DOCKER.md#change-impact-and-image-refresh): maintainer and installed AGENTS assess Docker impact, rebuild/test affected images and preserve publication authorization.
- Keep root maintainer AGENTS/PROJECT_CONTEXT/WIKI local and untracked; retain template counterparts. Exclude local copies from Git, wheel and Docker; validate distributions without them.

- Prepared matching VERSION, wheel and Docker version 1.4.1; [release checks and publication record](docs/V1_4_1.md). Added package/context regression coverage and retained full v1.2.0 history in its archive.

- Published `tigusigalpa/ai-kit:1.4.1`; push, remote digest/configuration and anonymous tag visibility matched the tested image. Post-label: nine Windows CLI tests, 339 Linux tests (337 passed/two skips), Docker smoke, offline wheel/source privacy checks and private/team 1.4.0 upgrades passed. [Evidence](docs/V1_4_1.md#verification).

## v1.4.0 (2026-10-15)

- Published `tigusigalpa/ai-kit:1.4.0` to Docker Hub at the owner's request. Remote digest, linux/amd64 platform, version label and non-root entrypoint were read back and matched the prepared image; [publication record](docs/V1_4_0.md#docker-hub-publication). No `latest` tag was assigned.
- Prepared v1.4.0 for the Docker CLI and local dialogue memory. VERSION, CLI/wheel metadata, image label and release pointers use the same version; [release checks and Docker Hub handoff](docs/V1_4_0.md). Registry publication and Git tagging remain separate.
- Added offline `aikit memory import|merge|export`: three dialogue formats, selected ChatGPT branches, source-bound human review, explicit contradictions and ChatGPT/OpenRouter reference exports. Preserves immutable artifacts, refuses unreviewed normal exports and protects private memory across upgrades/builds. Added tests and detailed [workflow](docs/guide/DIALOGUE_MEMORY.md)/[contract](docs/DIALOGUE_MEMORY.md). Automatic sync and API execution remain separate. Archived v1.1.0 history without dropping its text.
- Before release labeling, dialogue-memory verification passed: 336 Windows tests (329 passed/seven environment skips), 336 packaged Linux tests (334 passed/two skips), clean kit validation, offline wheel and private-package exclusion, README conflict-resolution flow and Docker smoke. [Coverage and limits](docs/DIALOGUE_MEMORY.md#verification).
- Added standalone non-root Docker CLI, pinned build inputs, offline wheel resources, application mounts, Kubernetes preview Job, smoke tests, CI and [usage/results](docs/DOCKER.md). Earlier Docker-only Windows and packaged Linux runs passed 309 tests (307 passed/two skips each); actual image, preservation, signals, context exclusions, wheel and schema checks passed.
- After labeling: nine CLI tests, 336 packaged Linux tests (334 passed/two Windows-only skips), clean kit validation, isolated Windows wheel/fresh-venv smoke and private-memory exclusion passed. The actual linux/amd64 image passed Docker smoke. Tracked 1.3.0 upgrades in private/team modes preserved data and pin identities, with explicit review of a local skill conflict; reruns stayed stable. [Release evidence](docs/V1_4_0.md#verification).

## v1.3.0 (2026-10-13)

- Prepared v1.3.0 for optional Web Design and the expanded README guide. The 304-test behavioral discovery below preceded release labeling; publication/tagging remain separate. [Release checks](docs/WEB_DESIGN.md#release-labeling).
- After labeling: eight CLI tests, version/wheel metadata 1.3.0, clean kit checks and offline fresh-venv wheel smoke passed. The pre-label 1.2.0 upgrade preserved facts, settings, local design/skill edits, MCP configuration and both security pins; rerun stayed stable.
- Added optional Web Design: --with-web-design installs four short skills, conditional Blade/library/tool/review guides and created-once project design documents. Added scoped context workflows, source/Claude lifecycle and preservation tests; installation remains offline. [Guide](docs/guide/WEB_DESIGN.md), [integration record](docs/WEB_DESIGN.md).
- Removed the root README size quota and added extensive reference-to-site instructions for Laravel, Tailwind, Bootstrap, Alpine/Livewire, daisyUI, Flowbite, Flux, TypeUI and SkillUI. Existing instruction budgets remain scoped; external setup and real application checks stay separate.
- Verified on Windows/Python 3.12.14: 304 tests (300 passed/four runtime skips), clean kit/skill checks, all-client private/team visibility, preserved tracked 1.2.0 upgrade and fresh-venv wheel smoke. Live tools/sites remain unverified. Archived v0.6.4 history without losing its text; [details](docs/WEB_DESIGN.md#verification).

## v1.2.0 (2026-10-12)

[Archived release entry](docs/history/v1.2.0-changelog.md#v120-2026-10-12).

## v1.1.0 (2026-10-12)

[Archived release entry](docs/history/v1.1.0-changelog.md#v110-2026-10-12).

## v0.13.0 (2026-10-11)

[Archived release entry](docs/history/v0.13.0-changelog.md#v0130-2026-10-11).

## v0.12.0 (2026-10-11)

[Full preserved entry](docs/changelog/v0.12.0.md).

## v0.11.0 (2026-10-11)

- Fixed provider/model overrides carrying inherited effort; synchronized Gemini routing policy with the reviewed registry. Existing selection/settings defaults stay readable and unchanged.
- Fixed the untested v0.10 adapter audit failing before it could report file-blocked native paths. Read-only state validation now allows obstructions after strict link/boundary checks; installation writes retain their refusal guards.
- Forwarded subcommand help to the actual command parser, so `aikit benchmark --help` and install flags are discoverable.
- Added preview-first `aikit benchmark run|review|report|export`: immutable Git blobs, separate A/B/C workspaces/repeats, equal fixed A/B controls, a configured worker protocol, actual-telemetry coverage, checks plus explicit semantic review, private JSON/Markdown reports and idempotent journal export. No live vendor adapter or application savings is claimed.
- Added metric schema 3 for revision/case/repetition/stack/class/level/capability/review strata, keeping schemas 1/2 readable. Comparisons require matched reviewed tasks and actual single-currency costs, include all failures/retries and refuse lower-quality/unknown/estimated spend claims. Added per-stack analysis.
- Added optional manual/fixed/recommended/adaptive modes, task/project pins and economy/balanced/quality profiles. Learned recommendations require comparable distinct-case samples and quality floors; unsupported controls or insufficient evidence retain the capability recommendation. Immutable proposals preserve prior selection and support explicit backed-up restore without automatic policy writes.
- Added read-only module context selection, duplicate detection and byte-budget reporting while preserving critical requirements and architectural decisions. Added staged acceptance plan and orchestration research in ADR 0012.
- Expanded wheel resources and smoke checks outside the source checkout, including installed validation, new command imports and context selection. Windows/Python 3.12.14 full discovery ran 248 tests (244 passed, four runtime skips); post-review checks and offline wheel installation passed; kit validation returned zero errors/warnings. [Results and limits](docs/IMPLEMENTATION.md#measurement-led-development-verification).

## v0.6.4 (2026-10-10)

[Archived release entry](docs/history/v0.6.4-changelog.md#v064-2026-10-10).

## v0.5.0 (2026-10-10)

[Archived release entry](docs/history/v0.5-changelog.md#v050-2026-10-10).

## Earlier kit

Release history is preserved: [v0.5.0](docs/history/v0.5-changelog.md), [v0.10.0](docs/history/v0.10-changelog.md), [v0.6.5-v0.9](docs/history/v0.6.5-v0.9-changelog.md), [v0.4.5-v0.4.7](docs/history/v0.4-changelog.md), [v0.3.3-v0.3.8](docs/history/v0.3-changelog.md), [v0.2-v0.2.2 and Windows fixtures](docs/history/v0.2-changelog.md), and [v0.1](docs/history/v0.1-changelog.txt). Old paths and language/router agreements are historical data.
[Prior routing decision](docs/adr/0001-adaptive-model-routing.md) records the accepted routing baseline; this changelog is not copied into projects.
