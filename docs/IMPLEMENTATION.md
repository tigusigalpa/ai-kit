# Consolidated implementation

## Scope and decisions

The [changelog](../CHANGELOG.md) records evolution; [measurement verification](#measurement-led-development-verification) records v0.11 tooling limits. Earlier results: [v0.6.4](V0_6_4.md), [v0.5.0](V0_5_0.md), [audit disposition](MANUS_REVIEW.md). [Dialogue memory](DIALOGUE_MEMORY.md) records the offline import/review/export contract.
Historical source evidence: [Windows CI](WINDOWS_CI_FIX.md). Current facts: PROJECT_CONTEXT.
Execution claims require evidence.

| Recommendation | Implemented treatment |
| --- | --- |
| Repeated policies and excessive startup context | Short AGENTS/Core/bootstrap; conditional profiles, container rules, and provider material; canonical owners below |
| Template contains kit history | Separate reference root and clean template/; project context and history start unknown; existing documents survive installation |
| Deterministic installation and upgrades | Offline Python installer: preview, explicit apply, hashes, conflicts, backups, rerun stability, semantic acceptance |
| Private versus shared use | Private remains default; explicit team mode preserves shared instructions in Git; local state, secrets, overrides, and caches remain private |
| Universal ignore safety | Separate repository and application policies; Composer exclusions scoped to verified modules; intentional Go vendoring/source and dependency locks stay visible |
| Monorepos and stack depth | Empty path-to-profile map plus PHP, Laravel, Go, Python, Moodle, frontend, and library profiles; verified versions and commands required |
| Security, tests, review, migrations | Task-relevant application/dependency checks, realistic unavailable outcomes, safe migration review, project toolchain preservation |
| Native entry points and skills | Claude import and optional native skill copies; Codex source skills; optional Copilot/Cursor/Aider/Kimi/Manus entries with runtime verification boundary |
| Provider-specific router details | Shared capability/risk policy; model IDs and supported efforts in reviewed provider JSON; controls and unknown mappings explicit |
| Model escalation | Latest owner policy retained: inexpensive bounded work, substantive engineering, justified higher-capability escalation; no switching is simulated |
| License and public maintenance | Owner-selected MIT; CONTRIBUTING, separate reporting SECURITY, version source, checks and CI workflow |
| Docker CLI and cleanup | [Standalone image](DOCKER.md); read-only cleanup evidence helper, deletion governed by ownership/disposability/size rules |
| Dogfooding and source accuracy | Root context describes AI-KIT itself; checker validates reference boundaries, anchors, skills, and Git visibility |
| ADR/change history | Kit ADRs stay under root docs/; clean project ADR/decision templates; CHANGELOG updates remain required after tasks changing files |

Owner defaults remain: English files/Russian chat, Laravel conventions, explicit commits/pushes, Docker preflight, Kubernetes readiness and cleanup threshold. Installation can select another chat language or standard conventions without converting existing code.

## Policy ownership

| Policy | Canonical owner |
| --- | --- |
| Language, Git authorization, verified facts | [Core](../template/ai-kit/CORE.md) |
| User/project selections | [Settings](../template/ai-kit/settings.json) |
| Work cycle, tests/review/docs/migrations | [Engineering](../template/ai-kit/ENGINEERING.md) |
| Security implementation checks | [Security baseline](../template/ai-kit/SECURITY.md) |
| Optional security workflows | [Cloudflare](../template/ai-kit/SECURITY-AUDIT.md), [Strix](../template/ai-kit/STRIX.md) |
| Container design and cleanup threshold | [Containers](../template/ai-kit/CONTAINERS.md) |
| Owner Laravel conventions | [Owner profile](../template/ai-kit/profiles/OWNER.md) |
| Stack practices | [Stack directory](../template/ai-kit/stacks), including Filament |
| Routing and provider controls | [Router](../template/ai-kit/router/POLICY.md) and relevant provider |
| Optional local measurement contract | [Metrics](../template/ai-kit/METRICS.md) |
| Generated client settings, scoped module rules, presets | [Adapters](../template/ai-kit/ADAPTERS.md#optional-install-extras), [secret list](../templates/agent-secrets.ignore), installer |
| Provider selection, optional modes/profiles/pins and measured routing | [selection.json](../template/ai-kit/router/selection.json), [routing.json](../template/ai-kit/router/routing.json), [router.py](../scripts/router.py), [adaptive.py](../scripts/adaptive.py), [learning.py](../scripts/learning.py) |
| Benchmark execution, telemetry and semantic acceptance | [benchmark contract](BENCHMARK.md), [benchmark helper](../scripts/benchmark.py), [Metrics](../template/ai-kit/METRICS.md) |
| Client evidence and conservative adapter retirement | [agent registry](../integrations/agents.json), [adapters helper](../scripts/adapters.py), [Adapters](../template/ai-kit/ADAPTERS.md) |
| Project-fact evidence and pair-coverage evaluation | [context helper](../scripts/context.py), [evaluation helper](../scripts/evaluate.py), [Metrics](../template/ai-kit/METRICS.md) |
| Local dialogue import, conflict review and reference exports | [Contract](DIALOGUE_MEMORY.md), [memory CLI](../scripts/memory.py) |
| MCP trust boundary and documentation workflow | [MCP](../template/ai-kit/MCP.md), [Security](../template/ai-kit/SECURITY.md), [Context7](../template/ai-kit/CONTEXT7.md) |
| Optional visual workflow and UI implementation | [Web Design](../template/ai-kit/WEB-DESIGN.md), conditional [guides](../template/ai-kit/web-design); project-owned docs/design records actual choices/evidence |
| Installation/upstream reconciliation | [Bootstrap](../template/ai-kit/BOOTSTRAP.md), [upstream](../template/ai-kit/UPSTREAM.md), installer state |
| Current project facts and navigation | Installed PROJECT_CONTEXT, WIKI, and ai-kit/project.json |
| Context maintenance procedure | [Continuity skill](../template/.agents/skills/project-continuity/SKILL.md) |

Entry points link to policy owners; historical ADRs do not activate superseded rules.

## Deferred with reasons

- Exchange/trading-specific profile: no confirmed domain requirement; the library profile covers reusable code without introducing trading assumptions.
- Executable Docker cleanup: an inspection report cannot establish exact project bytes, exclusive builder ownership, and disposability by itself. Keep the existing actionable policy; add automation after representative resource fixtures and live trials.
- Runtime guards and automatic model switching: clients expose different controls. The opt-in Claude Code ask rules are supplementary confirmation, not a proven universal Git ban; other clients receive no guard.
- Context/token cost claims: byte budgets are measured, but no tokenizer, runtime-loaded-context benchmark, or performance comparison has been run.
- Additional model/client mappings: unsupported provider IDs and runtime settings remain unknown; no speculative model names or fake activation.
- Codex nested AGENTS.md and config.toml: Codex reads AGENTS.md only from the root to its working directory, and approval/sandbox settings are user decisions; Roo has no documented path-scoped rules.
- Topics, homepage, hosted publication, tags/releases: these require remote changes; local work does not authorize them. The current repository description and MIT were independently confirmed; a homepage is unnecessary for the first usable bundle.
- PyPI publication needs explicit authorization. [Repository administration](../CONTRIBUTING.md#repository-maintenance).
- Real-project trials: synthetic fixtures do not replace actual applications or hosted CI; [Docker results](DOCKER.md#verification-results) record local Linux checks.

## Verification

Historical links are revision-specific.
Optional integration checks: [security-audit](SECURITY_AUDIT.md), [Strix](STRIX.md).

### Measurement-led development verification

The [plan](DEVELOPMENT_PLAN.md), [benchmark contract](BENCHMARK.md) and [ADR 0012](adr/0012-measurement-led-routing.md) cover v0.11.0. Behavioral checks ran before release labeling, on Windows/Python 3.12.14 with external fixtures because sandbox TEMP was unavailable.

- Full discovery: 248 tests in 1700.396 seconds; 244 passed, four skipped (POSIX shell, symlink creation, two junction fixtures).
- Post-review: 70 learning/metrics/router/CLI checks passed. Benchmark exposed an ineffective Git ceiling at cwd; using its parent fixed discovery. All six benchmark checks then passed, including source preservation, review/export and unknown/timeout telemetry.
- Kit: zero errors/warnings. Python 3.10 grammar: all 32 CLI/script/test files passed; execution on 3.10 remains unverified.
- Upgrade from actual tracked v0.10.0 preserved PROJECT_CONTEXT, project.json, selection and schema-2 journal bytes; modified routing survived a stable rerun.
- Offline wheel: 178 files, no private journals/caches. External fresh-venv installation without dependencies/network passed imports, route/help, validation, install/doctor, adapter report and context selection; installed validation had zero errors/warnings.
- Release labeling: seven CLI checks passed; VERSION and wheel metadata agree at 0.11.0. The rebuilt wheel passed external install smoke; kit had zero errors/warnings.
- Self-review covered boundaries/links, read-only obstructions, visibility, conflicts/locks, paired quality/cost, pins/provider availability and critical context. Synthetic workers establish no model result.

Owner deferred application/model calls; native/MCP activation, live switching and orchestration remain unverified. This section records historical checks; current version/facts are in PROJECT_CONTEXT.

### v0.10.0 release preparation

v0.10.0 adds schema-2 metric dispositions and corrected A/B identity, manifest-evidence snapshots and doctor drift reporting, client registry evidence plus conservative retirement, opaque evaluation pair coverage, MCP posture, and portable-wheel CI jobs. Its initial preparation established no checker/unit/build/wheel-smoke result (no shell Python); later bundled-runtime checks cover v0.11.0-v0.12.0 preparation, not pristine v0.10.0. Hosted CI and native client/MCP activation remain unverified.

### Early distribution verification

[Historical results](history/verification-before-measurements.md#early-distribution-verification).

### Router and agent-registry verification

[Historical results](history/verification-before-measurements.md#router-and-agent-registry-verification).

### Client settings and detection verification

[Historical results](history/verification-before-measurements.md#client-settings-and-detection-verification).

### Onboarding and project-facts verification

[Historical results](history/verification-before-measurements.md#onboarding-and-project-facts-verification).

### Unified CLI and fact-drift verification

[Historical results](history/verification-before-measurements.md#unified-cli-and-fact-drift-verification).

### Provider review and doctor-fix verification

[Historical results](history/verification-before-measurements.md#provider-review-and-doctor-fix-verification).

### Measurement analysis and Gemini verification

[Historical results](history/verification-before-measurements.md#measurement-analysis-and-gemini-verification).

### Windows CI fixture verification

[Historical results](history/verification-before-measurements.md#windows-ci-fixture-verification).

### Manus patch verification

[Historical results](history/verification-before-measurements.md#manus-patch-verification).

### Overlay regression

[Historical results](history/verification-before-measurements.md#overlay-regression).

### Original bundle checks

[Historical results](history/verification-before-measurements.md#original-bundle-checks).

