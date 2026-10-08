# Consolidated implementation

## Scope and decisions

Version 0.2 consolidates the Claude, Kimi, and DeepSeek reviews and the owner's agreements; v0.2.1 fixes reference overlays; v0.2.2 addresses reproduced Manus installer findings. See [audit disposition](MANUS_REVIEW.md).
The original review checked 5dd530b9046fa09742f2ac13e22fabcbde70d749. The patch source check on 2026-10-08 resolved published main to 73707036c1098d8c1c81ab2c51d723c3d521f6b8; this patch remains local and unpublished by the agent.
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
| Stack practices | [Stack directory](../template/ai-kit/stacks) |
| Routing and provider controls | [Router](../template/ai-kit/router/POLICY.md) and relevant provider |
| Installation/upstream reconciliation | [Bootstrap](../template/ai-kit/BOOTSTRAP.md), [upstream](../template/ai-kit/UPSTREAM.md), installer state |
| Current project facts and navigation | Installed PROJECT_CONTEXT and WIKI |
| Context maintenance procedure | [Continuity skill](../template/.agents/skills/project-continuity/SKILL.md) |

Entry points and skills link to policy owners. Historical ADRs explain prior decisions and do not activate superseded rules.

## Deferred with reasons

- Exchange/trading-specific profile: no confirmed domain requirement; the library profile covers reusable code without introducing trading assumptions.
- Executable Docker cleanup: an inspection report cannot establish exact project bytes, exclusive builder ownership, and disposability by itself. Keep the existing actionable policy; add automation after representative resource fixtures and live trials.
- Runtime guards and automatic model switching: clients expose different controls. Optional deny examples are supplementary, not a proven universal Git ban; installer does not activate them.
- Context/token cost claims: byte budgets are measured, but no tokenizer, runtime-loaded-context benchmark, or performance comparison has been run.
- Additional model/client mappings: unsupported provider IDs and runtime settings remain unknown; no speculative model names or fake activation.
- Topics, homepage, hosted publication, tags/releases: these require remote changes; local work does not authorize them. The current repository description and MIT were independently confirmed; a homepage is unnecessary for the first usable bundle.
- Real-project trials and Linux execution: temporary project fixtures exercise preservation and mixed manifests. These do not replace trials on actual applications or hosted CI.

## Verification

### Manus patch verification

Measured on 2026-10-08 for local bundle 0.2.2, on Windows with Python 3.12.14. Upstream read: 73707036c1098d8c1c81ab2c51d723c3d521f6b8; this is not a commit containing the patch.

- Clean behavioral suite: 45 tests executed, 43 passed, 2 skipped. The symlink test lacks Windows privilege; the junction fixture received Access denied in this sandbox. Neither real linked-path test is claimed to have passed locally.
- After tightening the junction helper to skip only recognized access/privilege denial, its focused check confirmed that unavailable outcome; unexpected helper errors fail the test.
- The same suite passed on a fresh v0.2.2 overlay of the reconstructed published tree: 43 passed, 2 skipped. Old .gitignore_real, native entries, and legacy skills remained in that fixture; compatibility pointers corrected known obsolete policy paths.
- New regressions cover edited/old/concurrently created candidates, first-creation metadata, source changes, adapter-retirement conflicts and reviewed resolution, untracked native warnings, invalid settings/state, and previous-version state.
- An installed synthetic Go/Composer/Python project preserved local AGENTS/README/ignore rules and dependency manifests/locks. Real Git private/team checks verified shared entries/skills, Composer exclusions, deliberate Go vendoring, and hidden secrets/caches/state/candidates.
- A separate smoke check used the actual v0.2.1 installer, then upgraded with v0.2.2. Documents, settings, and selected agents survived; a repeated plan had no writes or conflicts.
- Junction detection uses lstat and Windows reparse tags documented in [Python 3.10 os](https://docs.python.org/3.10/library/os.html#os.stat_result.st_reparse_tag) and [stat](https://docs.python.org/3.10/library/stat.html#stat.IO_REPARSE_TAG_MOUNT_POINT), avoiding reliance on a newer pathlib method. The fixture invokes only its saved helper with a process-scoped execution policy; no persistent host setting changes.

- Clean and mixed-layout kit validation returned no errors or warnings, including real Git source visibility. The changed maintainer continuity skill passed its metadata validator.
- The archive contains exactly 85 source files; file inventory/bytes and ZIP integrity were verified. All Python sources parsed with the Python 3.10 syntax grammar. Always-loaded entries remained 1,327 bytes (template AGENTS), 1,995 (Core), and 1,058 (bootstrap prompt); these are file sizes, not measured runtime token costs.

Python 3.10/3.13 runtime execution and successful hosted CI remain unverified locally; the workflow defines that matrix.
These are synthetic project/file tests, not application runtime trials. Publication and native client behavior remain separate verification.

### Overlay regression

The supplied Linux/Python 3.13.16 CI failure exposed old v0.1 documents remaining beside the new v0.2 layout.
All 91 tracked source blobs at the published revision were reconstructed with matching Git object hashes. The original checker reproduced all five missing-heading errors and the large MODELS warning.
Patch 0.2.1 replaces known old rule documents with small canonical-resource pointers. It preserves the checker's full validation scope and does not reintroduce language/Git policy into maintainer AGENTS.
The clean bundle and patched public snapshot both passed the unchanged checker with zero errors/warnings and real Git visibility checks on Windows/Python 3.12.14.
The behavioral suite was rerun on the patched public snapshot: 33 tests, 32 passed, 1 Windows symlink-privilege skip. Upgrade fixtures now derive their versions from VERSION rather than pinning an old bundle number.
Archive inventory/exact bytes and Python 3.10 syntax were verified. Successful hosted CI after publication remains unverified.

### Original bundle checks

- Local environment: Windows, bundled Python 3.12.14; verification date 2026-10-08.
- Behavioral suite: 33 tests executed; 32 passed and 1 skipped. The skipped symlink test requires a Windows privilege unavailable in this session; no claim is made that it ran.
- Installer scenarios cover absent-target preview, project-owned files, idempotency, unchanged upgrades, local conflicts/semantic merges/future conflicts, backups, private/team transitions, mixed Composer/Go vendoring, Moodle scoping, optional entries, settings preservation, unsafe paths, changed previews, and rollback after an injected write failure.
- Checker scenarios cover missing anchors, escaping links, invalid JSON, skill/folder and registry mismatch, clean history boundaries, and Git checkout metadata exclusion.
- Real Git checks passed for reference-source visibility, private/team shared files, secrets/caches, manifests/checksums/locks, intentional vendoring, and executable source.
- All 8 installable skills plus the maintainer continuity skill passed the skill-creator metadata validator. Relative file/heading links, registry, JSON, English content hygiene, and always-loaded byte budgets passed the kit checker.
- Docker evidence tests use a fake command adapter: inspection remains read-only, stopped-container references remain protected, exact bytes stay unknown, and a stopped daemon fails rather than producing a success report. No real Docker environment was exercised.
- Instruction review checked conditional profile loading, unknown project facts, English artifacts/configured chat language, no publication authorization, Docker preflight, and preserved owner conventions. This is source review, not a live client behavior trial.

The hosted workflow is prepared for Python 3.10/3.13 on Windows/Linux, with read-only repository permissions and immutable action revisions.

No commit, push, remote repository write, real Docker deletion, native client activation, or live model switch is part of this implementation.
