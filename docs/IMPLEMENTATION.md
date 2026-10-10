# Consolidated implementation

## Scope and decisions

The [changelog](../CHANGELOG.md) records kit evolution; [v0.6.4 verification](V0_6_4.md) covers the current additions and [v0.5.0 verification](V0_5_0.md) the previous ones. v0.7.0 adds the `aikit` CLI and a fact-drift check. Earlier reproduced findings remain in the [audit disposition](MANUS_REVIEW.md).
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
| Provider-specific router details | Shared capability/risk policy; model IDs and supported efforts only in OpenAI JSON; provider-specific controls and unknown mappings explicit |
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
| Provider selection, agent registry, routing helper | [selection.json](../template/ai-kit/router/selection.json), [agents.json](../integrations/agents.json), [router.py](../scripts/router.py) |
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
- Portable wheel/PyPI packaging: the `aikit` console script works from a checkout or editable install; bundling the distribution dirs for a self-contained wheel and publication stay deferred (remote changes are not authorized locally).
- Real-project trials and Linux execution: temporary project fixtures exercise preservation and mixed manifests. These do not replace trials on actual applications or hosted CI.

## Verification

### Early distribution verification

Pre-v0.4.7 detection, adapter/provider, and extras verification (62/73/69-test runs) is preserved in the [v0.3 changelog](history/v0.3-changelog.md).

### Router and agent-registry verification

2026-10-10, Windows/Python 3.14.6: 92 tests ran, 91 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors. Covers registry, route classification/resolution, local and pending providers, and configure preview/apply/conflict. Gemini IDs remain pending; no live API or hosted CI ran.

### Client settings and detection verification

2026-10-10, Windows/Python 3.14.6: 128 tests ran, 127 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors; Python 3.10 grammar was verified. Regressions cover key-level settings merges with backups, user-edit survival, disabled-extra removal, legacy whole-file migration, the invalid-JSON conflict, managed_json validation, doctor reports, client detection, and lockfile/evidence-based commands. The hook ran through Git Bash sh with a CRLF script and a spaced Windows path; an end-to-end CLI run was stable on rerun. A real v0.4.6 installation upgraded cleanly; a v0.4.6 downgrade preview reports a settings conflict. Native Claude Code hook delivery, ask enforcement, and hosted CI remain unverified.

### Onboarding and project-facts verification

2026-10-10, Windows/Python 3.14.6: 109 tests ran, 108 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors; Python 3.10 grammar was verified. Regressions cover interactive selections, the post-apply doctor check, per-manifest language/version/command detection, project.json drafting and preservation, and the adr/changelog scaffolding helpers. The Makefile targets were exercised locally; hosted CI and PyPI publication remain unverified.

### Unified CLI and fact-drift verification

2026-10-10, Windows/Python 3.14.6: 191 tests ran, 189 passed, two skipped; kit validation returned zero errors. Covers the `aikit` dispatcher, the module-map drift warning, and non-Latin chat language names. Hosted CI and a portable wheel remain unverified.

### Windows CI fixture verification

2026-10-08, Windows/Python 3.12.14: 47 tests executed, 44 passed, 3 skipped (symlink privilege and two junction variants). Equivalent-path reproductions exposed both failures before the fix; the corrected fixture restores rollback injection and reaches the junction permission check. See [source/job evidence and limits](WINDOWS_CI_FIX.md). Corrected hosted Windows results remain unverified.

### Manus patch verification

The detailed v0.2.2 record lives in [MANUS_REVIEW.md](MANUS_REVIEW.md): candidate preservation, adapter-retirement review, junction detection, and the synthetic/upgrade smoke checks. Local result: 45 tests, 43 passed, 2 skipped. These are synthetic project/file tests, not application runtime trials; hosted CI remains unverified.

### Overlay regression

The supplied Linux/Python 3.13.16 CI failure exposed old v0.1 documents remaining beside the new v0.2 layout.
All 91 tracked source blobs at the published revision were reconstructed with matching Git object hashes. The original checker reproduced all five missing-heading errors and the large MODELS warning.
Patch 0.2.1 replaces known old rule documents with small canonical-resource pointers. It preserves the checker's full validation scope and does not reintroduce language/Git policy into maintainer AGENTS.
The clean bundle and patched public snapshot both passed the unchanged checker with zero errors/warnings and real Git visibility checks on Windows/Python 3.12.14.
The behavioral suite was rerun on the patched public snapshot: 33 tests, 32 passed, 1 Windows symlink-privilege skip. Upgrade fixtures now derive their versions from VERSION rather than pinning an old bundle number.
Archive inventory/exact bytes and Python 3.10 syntax were verified. Successful hosted CI after publication remains unverified.

### Original bundle checks

The original-bundle verification record is archived in [docs/history](history/original-bundle-checks.md).

