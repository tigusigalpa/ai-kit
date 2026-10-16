# AI-KIT changelog

## v1.4.3 (2026-10-16)

- Added a live PyPI version badge to README.
- Added stable GitHub Release preparation with event/version/repository guards and owner-approved PyPI uploads; manual validation stays the default. Future v* tags retain reviewer protections. [Procedure](docs/PYPI.md#release-to-pypi-with-owner-approval). Archived v0.13.0 text intact for the changelog budget.
- Added fifteen event regression tests. Before release labeling, 32 hosted CI checks and build-only workflow verification passed; kit checks, 368 packaged Linux tests (two platform skips), archive/privacy/Twine/offline wheel checks and Docker smoke also passed. [Release verification](docs/V1_4_3.md).
- Verified 1.4.3 CLI/archive/image identity, offline packaging, Docker smoke, 368 Linux tests and preserved private/team upgrades from v1.4.2.
- Verified PyPI 1.4.3 publication, matching hosted hashes and fresh registry installation; [receipt](docs/V1_4_3.md#pypi-publication-and-read-back).

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
- Added offline `aikit memory import|merge|export`: three dialogue formats, selected ChatGPT branches, source-bound human review, explicit contradictions and ChatGPT/OpenRouter reference exports. Preserves immutable artifacts, refuses unreviewed normal exports and protects private memory across upgrades/builds. Added tests and detailed [workflow](README.md#shared-context-from-two-dialogues)/[contract](docs/DIALOGUE_MEMORY.md). Automatic sync and API execution remain separate. Archived v1.1.0 history without dropping its text.
- Before release labeling, dialogue-memory verification passed: 336 Windows tests (329 passed/seven environment skips), 336 packaged Linux tests (334 passed/two skips), clean kit validation, offline wheel and private-package exclusion, README conflict-resolution flow and Docker smoke. [Coverage and limits](docs/DIALOGUE_MEMORY.md#verification).
- Added standalone non-root Docker CLI, pinned build inputs, offline wheel resources, application mounts, Kubernetes preview Job, smoke tests, CI and [usage/results](docs/DOCKER.md). Earlier Docker-only Windows and packaged Linux runs passed 309 tests (307 passed/two skips each); actual image, preservation, signals, context exclusions, wheel and schema checks passed.
- After labeling: nine CLI tests, 336 packaged Linux tests (334 passed/two Windows-only skips), clean kit validation, isolated Windows wheel/fresh-venv smoke and private-memory exclusion passed. The actual linux/amd64 image passed Docker smoke. Tracked 1.3.0 upgrades in private/team modes preserved data and pin identities, with explicit review of a local skill conflict; reruns stayed stable. [Release evidence](docs/V1_4_0.md#verification).

## v1.3.0 (2026-10-13)

- Prepared v1.3.0 for optional Web Design and the expanded README guide. The 304-test behavioral discovery below preceded release labeling; publication/tagging remain separate. [Release checks](docs/WEB_DESIGN.md#release-labeling).
- After labeling: eight CLI tests, version/wheel metadata 1.3.0, clean kit checks and offline fresh-venv wheel smoke passed. The pre-label 1.2.0 upgrade preserved facts, settings, local design/skill edits, MCP configuration and both security pins; rerun stayed stable.
- Added optional Web Design: --with-web-design installs four short skills, conditional Blade/library/tool/review guides and created-once project design documents. Added scoped context workflows, source/Claude lifecycle and preservation tests; installation remains offline. [Guide](README.md#web-design), [integration record](docs/WEB_DESIGN.md).
- Removed the root README size quota and added extensive reference-to-site instructions for Laravel, Tailwind, Bootstrap, Alpine/Livewire, daisyUI, Flowbite, Flux, TypeUI and SkillUI. Existing instruction budgets remain scoped; external setup and real application checks stay separate.
- Verified on Windows/Python 3.12.14: 304 tests (300 passed/four runtime skips), clean kit/skill checks, all-client private/team visibility, preserved tracked 1.2.0 upgrade and fresh-venv wheel smoke. Live tools/sites remain unverified. Archived v0.6.4 history without losing its text; [details](docs/WEB_DESIGN.md#verification).

## v1.2.0 (2026-10-12)

[Archived release entry](docs/history/v1.2.0-changelog.md#v120-2026-10-12).

## v1.1.0 (2026-10-12)

[Archived release entry](docs/history/v1.1.0-changelog.md#v110-2026-10-12).

## v0.13.0 (2026-10-11)

[Archived release entry](docs/history/v0.13.0-changelog.md#v0130-2026-10-11).

## v0.12.0 (2026-10-11)

- Benchmark packs accept optional `kit_agents`/`kit_preset` (default codex/minimal), so kit arms install the client's real adapter set and preset instead of a hard-coded arm; both are validated against the installer registry.
- Benchmark task paths are now probed against the benchmark project instead of the process working directory.
- Interrupted benchmark runs are resumable: re-running `benchmark run` with the identical pack skips completed units and continues missing ones, and a changed pack is refused against the existing run. Per-unit infrastructure failures are recorded as explicit failed units, so one bad unit neither aborts the run nor hides as an executed attempt; failed units still block savings and cannot be reviewed as correct.
- The unified `aikit` dispatcher now prefers installed `aikit.scripts.*` package modules over bare script-path imports, avoiding duplicate module objects inside the wheel.
- The checker document budgets are named constants; the root README budget rises to 22000 bytes (human onboarding that never enters project context), other documents keep 12000.
- Verified locally (Windows/Python 3.14.6): 252 tests ran, all passed, 1 runtime skip; kit validation returned zero errors and zero warnings; Python 3.10 grammar was verified for the changed sources. Live workers, native client activation and hosted CI remain unverified.

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
