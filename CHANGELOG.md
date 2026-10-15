# AI-KIT changelog

## Unreleased

- Added mandatory [Docker impact/refresh](docs/DOCKER.md#change-impact-and-image-refresh): rebuild/test changed packaged code, rules and dependencies; document exceptions, use development tags and preserve separate registry authorization. Wired maintainer and canonical container rules.

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

- Prepared v1.2.0 for optional Context7 documentation lookup and the OpenRouter integration guide. Version labeling is local; the full behavioral results below preceded labeling. Publication/tagging remain separate.
- After labeling: eight CLI tests, CLI/wheel version 1.2.0, clean kit validation and offline fresh-environment wheel smoke passed. Synthetic pre-label 1.1.0 upgrade preserved facts, settings values/choices, local Context7 edits, MCP configuration and both security pins; rerun stayed stable. [Release checks](docs/CONTEXT7.md#release-labeling).
- Added optional --with-context7: persistent documentation lookup skill with source/Claude copies, version-aware sanitized queries, and separate Codex/Claude/Cursor MCP setup examples. Installation remains offline and preserves native MCP configuration. Recorded upstream documentation revision; no hosted runtime pin or live connection is implied. Added lifecycle/preservation tests and wheel smoke coverage; [contract and verification](docs/CONTEXT7.md).
- Context7 verification on Windows/Python 3.12.14: 293 tests in 1239.036 seconds (289 passed/four runtime skips), clean kit/config/skill checks, all-client private/team visibility and offline fresh-environment wheel smoke. Live client activation and documentation retrieval remain unverified.
- Added a dedicated README OpenRouter section: reusable rules/context, current offline helpers versus a proposed API adapter, request layout, prompt/response caching, provider/session behavior, actual usage accounting and execution boundaries. Raised only the root README budget from 22000 to 32000 bytes at the owner's request; retained all existing feature content. Archived v0.5.0 release history with adjusted relative links to keep the changelog within its budget.
- Verified on Windows/Python 3.12.14: kit validation without errors/warnings, both README JSON examples, Python 3.10 grammar, exact preservation of prior README content and archived release text, and 285 tests in 970.706 seconds (281 passed, four runtime skips). No live OpenRouter call, cache experiment or savings measurement was run.

## v1.1.0 (2026-10-12)

[Archived release entry](docs/history/v1.1.0-changelog.md#v110-2026-10-12).

## v0.13.0 (2026-10-11)

- Added Rust, .NET, Java (Maven/Gradle), and Terraform/Helm stack profiles with evidence-based per-module detection: Cargo.toml (rust-version, cargo test/build/clippy), *.csproj/*.fsproj/*.vbproj and global.json (TargetFramework, dotnet test/build), pom.xml/mvnw/build.gradle(.kts)/gradlew (language level, wrapper-aware commands), and .tf files or Chart.yaml (fmt/validate, helm lint). Drafts remain suggestions until bootstrap confirms them.
- Added rust-work, dotnet-work, java-work, and infra-work skills to the registry; Claude native copies install with the claude agent selection.
- Benchmark packs accept the new stack names; README, SKILL.md, and WIKI profile lists updated.
- Verified locally (Windows/Python 3.14.6): 254 tests ran, all passed, 1 runtime skip; kit validation returned zero errors and zero warnings; Python 3.10 grammar verified; end-to-end smoke detected RUST/INFRA with drafted context and installed source/native skills. Real applications of the new stacks remain untrialed.

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
