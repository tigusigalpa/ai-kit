# Consolidated implementation

## Scope and decisions

The [changelog](../CHANGELOG.md) records kit evolution. v0.11.0 extends local v0.10.0 with isolated benchmarks, conservative measured routing and scoped context; [current verification](#measurement-led-development-verification) records limits. Earlier results remain in [v0.6.4 verification](V0_6_4.md), [v0.5.0 verification](V0_5_0.md), and the [audit disposition](MANUS_REVIEW.md).
The original review checked 5dd530b9046fa09742f2ac13e22fabcbde70d749. The first overlay check read 73707036c1098d8c1c81ab2c51d723c3d521f6b8; current source evidence is in [the Windows CI record](WINDOWS_CI_FIX.md).
Assessments were reconciled against actual files and official documentation; reviewer claims about their own executions are not test evidence.

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
| Docker cleanup helper | Read-only evidence collector; actual deletion governed by the existing ownership/disposability/size rule, with no unscoped prune |
| Dogfooding and source accuracy | Root context describes AI-KIT itself; checker validates reference boundaries, anchors, skills, and Git visibility |
| ADR/change history | Kit ADRs stay under root docs/; clean project ADR/decision templates; CHANGELOG updates remain required after tasks changing files |

The owner's English project/Russian chat split, Laravel conventions, no-commit/no-push agreement, Docker availability checks, Kubernetes-ready contract, and cleanup threshold remain applicable.
Installation can explicitly select another chat language or standard conventions for another project. No automatic conversion of existing conventions occurs.

## Policy ownership

| Policy | Canonical owner |
| --- | --- |
| Language, Git authorization, verified facts | [Core](../template/ai-kit/CORE.md) |
| User/project selections | [Settings](../template/ai-kit/settings.json) |
| Work cycle, tests/review/docs/migrations | [Engineering](../template/ai-kit/ENGINEERING.md) |
| Security implementation checks | [Security baseline](../template/ai-kit/SECURITY.md) |
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
| MCP trust boundary | [MCP posture](../template/ai-kit/MCP.md) and [Security baseline](../template/ai-kit/SECURITY.md) |
| Installation/upstream reconciliation | [Bootstrap](../template/ai-kit/BOOTSTRAP.md), [upstream](../template/ai-kit/UPSTREAM.md), installer state |
| Current project facts and navigation | Installed PROJECT_CONTEXT, WIKI, and ai-kit/project.json |
| Context maintenance procedure | [Continuity skill](../template/.agents/skills/project-continuity/SKILL.md) |

Entry points and skills link to policy owners. Historical ADRs explain prior decisions and do not activate superseded rules.

## Deferred with reasons

- Exchange/trading-specific profile: no confirmed domain requirement; the library profile covers reusable code without introducing trading assumptions.
- Executable Docker cleanup: an inspection report cannot establish exact project bytes, exclusive builder ownership, and disposability by itself. Keep the existing actionable policy; add automation after representative resource fixtures and live trials.
- Runtime guards and automatic model switching: clients expose different controls. The opt-in Claude Code ask rules are supplementary confirmation, not a proven universal Git ban; other clients receive no guard.
- Context/token cost claims: byte budgets are measured, but no tokenizer, runtime-loaded-context benchmark, or performance comparison has been run.
- Additional model/client mappings: unsupported provider IDs and runtime settings remain unknown; no speculative model names or fake activation.
- Codex nested AGENTS.md and config.toml: Codex reads AGENTS.md only from the root to its working directory, and approval/sandbox settings are user decisions; Roo has no documented path-scoped rules.
- Topics, homepage, hosted publication, tags/releases: these require remote changes; local work does not authorize them. The current repository description and MIT were independently confirmed; a homepage is unnecessary for the first usable bundle.
- Portable wheel/PyPI packaging: local Windows wheel checks are recorded below; hosted matrix results remain unverified. PyPI publication stays deferred (remote changes are not authorized locally).
- Real-project trials and Linux execution: temporary project fixtures exercise preservation and mixed manifests. These do not replace trials on actual applications or hosted CI.

## Verification

Historical links apply only to their recorded revisions.

### Measurement-led development verification

The [plan](DEVELOPMENT_PLAN.md), [benchmark contract](BENCHMARK.md) and [ADR 0012](adr/0012-measurement-led-routing.md) cover v0.11.0. Behavioral checks ran before release labeling, on Windows/Python 3.12.14 with external fixtures because sandbox TEMP was unavailable.

- Full discovery: 248 tests in 1700.396 seconds; 244 passed, four skipped (POSIX shell, symlink creation, two junction fixtures).
- Post-review: 70 learning/metrics/router/CLI checks passed. Benchmark exposed an ineffective Git ceiling at cwd; using its parent fixed discovery. All six benchmark checks then passed, including source preservation, review/export and unknown/timeout telemetry.
- Kit: zero errors/warnings. Python 3.10 grammar: all 32 CLI/script/test files passed; execution on 3.10 remains unverified.
- Upgrade from actual tracked v0.10.0 preserved PROJECT_CONTEXT, project.json, selection and schema-2 journal bytes; modified routing survived a stable rerun.
- Offline wheel: 178 files, no private journals/caches. External fresh-venv installation without dependencies/network passed imports, route/help, validation, install/doctor, adapter report and context selection; installed validation had zero errors/warnings.
- Release labeling: seven CLI checks passed; VERSION and wheel metadata agree at 0.11.0. The rebuilt wheel passed external install smoke; kit had zero errors/warnings.
- Self-review covered boundaries/links, read-only obstructions, visibility, conflicts/locks, paired quality/cost, pins/provider availability and critical context. Synthetic workers establish no model result.

Owner deferred real application/model calls. Hosted CI, other runtimes, native client/MCP activation, live switching and orchestration remain unverified. VERSION is 0.11.0, locally prepared without publication or a tag.

### v0.10.0 release preparation

v0.10.0 adds schema-2 metric dispositions and corrected A/B identity, manifest-evidence snapshots and doctor drift reporting, client registry evidence plus conservative retirement, opaque evaluation pair coverage, MCP posture, and portable-wheel CI jobs. During its initial preparation the shell did not expose Python, so that preparation established no checker, unit, build or wheel-smoke result. Later bundled-runtime checks cover v0.11.0 preparation, not a reconstruction of pristine v0.10.0. Hosted CI and native client/MCP activation remain unverified.

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

