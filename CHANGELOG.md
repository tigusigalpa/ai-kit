# AI-KIT changelog

## Unreleased

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

- Prepared v1.1.0 for security-audit and Strix. Expanded README capabilities/examples, pins, lifecycle and execution prerequisites; behavioral results below preceded release labeling.
- Release labeling verified on Windows/Python 3.12.14: eight CLI tests, 1.1.0 wheel metadata/install/rerun, preserved 0.13.0 upgrade and clean kit checks.
- Added --with-strix: one explicit-only entry point and nine original Strix skills plus Apache-2.0 license pinned at f7a32ae62d94872631bc8415073868d02a6ffdaf. Offline installation verifies bounded nested trees, Git blobs/SHA-256 and newline bytes; choices persist independently outside presets. Documented external runtime setup, writable target copies, explicit scope/budget, findings and separate cloud/CI/fix authorization. Added preservation/conflict/path/client/checker/wheel tests; [contract and results](docs/STRIX.md).
- Strix verification on Windows/Python 3.12.14: 285 tests (281 passed, four runtime skips), clean kit validation, original-byte/skill checks, installed private/team visibility and offline fresh-environment wheel smoke with both optional skills and stable rerun. External Strix runtime and real scans remain unverified.
- Added opt-in --with-security-audit: a short explicit-only Codex/Claude entry point and the complete Cloudflare skill pinned at c1c8a8c1471069fb0e188eeaff69b8e8db6564a8, with MIT license, Git blob/SHA-256 integrity checks and preserved newline bytes. Offline installation persists the choice outside presets, preserves local adaptations/conflicts, and runs no audit or upstream code. Added installation/checker/wheel coverage and documented native Windows validator limitations; [contract and results](docs/SECURITY_AUDIT.md).
- Prior security-audit verification: 271 Windows/Python tests (267 passed/four skips), clean kit/skill/wheel checks. Cloudflare's native Windows suite had seven CLI platform failures; 44 in-memory checks passed separately. [Details](docs/SECURITY_AUDIT.md); full audits/native activation remain deferred.
- Enabled main protection through gh: pull requests, 15 GitHub Actions checks, current branches and resolved conversations; blocked force pushes/deletion, including for admins. Zero mandatory approvals permit solo maintenance. Verified by API read-back; updated maintainer guidance.

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
