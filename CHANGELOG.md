# AI-KIT changelog

## v0.4.5 (2026-10-10)

- Added a data-driven agent registry ([integrations/agents.json](integrations/agents.json)) replacing the installer's hardcoded client/entry constants; the installer, checker, and doctor now share one source for agent names, gated template entries, optional integration files, and Claude skill copies. Adding a client is a data change rather than installer code.
- Added [scripts/router.py](scripts/router.py), an offline helper: `route "task"` returns a deterministic capability recommendation (level/role/effort plus a resolved provider/model), and `configure PROJECT --apply` writes `ai-kit/router/resolved.json` and, for a selected Aider agent, a native `.aider.conf.yml` model routing file. Classification is a transparent keyword rule, not a confidence score; no credentials or switching runtime are installed.
- Added [selection.json](template/ai-kit/router/selection.json) to record which providers a project actually uses, with per-role provider/model/effort overrides and self-hosted model IDs.
- Added provider tiers: a [local provider](template/ai-kit/router/providers/local.json) for Ollama/self-hosted models (user-supplied IDs) and a [pending Gemini scaffold](template/ai-kit/router/providers/gemini.json) that links the existing Gemini adapter to the router without fabricating model IDs. The provider schema now supports `tier`, `user_supplied_models`, and `verification_status`.
- Extended the checker and doctor for the registry, the new provider schema, and selection/resolved validation; pending and user-supplied providers surface as info rather than stale-date warnings.
- Reran the full local suite: 92 tests, 91 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors. Gemini router IDs remain pending verification; no live API calls, client activations, or hosted CI ran.

## v0.3.8 (2026-10-10)

- Added Gemini CLI, Windsurf, Cline, and Roo adapters: a GEMINI.md project entry plus optional .windsurf/rules/, .clinerules/, and .roo/rules/ pointer rules; private-mode ignores cover the new entries. Client rule formats were checked against current documentation on 2026-10-10 and still require activation verification in the actual clients.
- Filled in the Anthropic and Kimi router mappings as machine-readable provider configurations with roles, defaults, supported efforts, verified documentation dates, and sources. Anthropic IDs, effort levels, and request-field boundaries were verified against primary documentation (models overview and the Haiku 5.5 migration guide); Kimi facts were cross-checked against current online documentation.
- Generalized checker provider validation to every providers/*.json (required verified date, effort/support consistency) and extended the model-ID duplication guard to all configured IDs; the project doctor now handles roles without an effort control.
- Reran the full local suite: 73 tests, 72 passed, 1 unavailable Windows symlink check; kit validation returned no errors or warnings; Python 3.10 grammar verified. Live API calls, native client activation, and hosted CI remain unverified.

## v0.3.6 (2026-10-10)

- Added opt-in install extras selected with --with-session-start, --with-guards, and --with-ci; accepted choices persist in ai-kit/settings.json. Session start installs .agents/hooks/session-start.md and, for claude, .claude/settings.json SessionStart wiring; guards merges the reference deny-Git permissions into the same client settings file; the ci extra installs a self-contained .github/workflows/ai-kit.yml health check intended for team mode.
- Documented extras in ADAPTERS/BOOTSTRAP/README with activation boundaries: hook output, deny enforcement, and workflow behavior require verification in the actual client and hosted runner; MCP servers are declared manually per project and none is installed by default.
- Reran the full local suite: 69 tests, 68 passed, 1 unavailable Windows symlink check; kit validation returned no errors or warnings; Python 3.10 grammar was verified for all scripts. Hosted CI and real application trials remain unverified.

## v0.3.3 (2026-10-10)

- Added installer-suggested stack profiles: the plan detects GO, PYTHON, FRONTEND, PHP, LARAVEL, and MOODLE evidence from module manifests, reports it in the preview, and drafts module-map rows in a fresh PROJECT_CONTEXT.md marked unverified until bootstrap confirms them. Existing context documents remain preserved untouched.
- Added scripts/doctor.py, an offline health check for installed projects: state/settings validation, missing or modified managed files, missing owned documents, pending conflict candidates, always-loaded budget overflows, broken Markdown links/anchors, and stale provider verifications. Exit code 0 means no errors.
- Scoped Node and Python generated-path exclusions to modules with verified manifests (package.json, pyproject.toml, requirements.txt, setup.py, setup.cfg), matching the existing Composer/Moodle scoping; both ignore policies keep only generic output directories statically.
- Extended the checker visibility fixture to compose each policy with installer-detected module rules, as apply does.
- Moved maintainer-only reference-update guidance to CONTRIBUTING.md and the original-bundle verification record to docs/history to keep conditional documents within byte budgets; removed the external hero-image hotlink from the README.
- Reran the full local suite for these changes: 62 tests, 61 passed, 1 unavailable Windows symlink check; kit validation returned no errors or warnings; Python 3.10 grammar was verified for install, checker, and doctor sources. Hosted CI and real application trials remain unverified.

- Corrected v0.2.2 installer test fixtures after the Windows/Python 3.13.15 CI log exposed short-versus-long temporary path comparisons. Fixture roots now resolve before child paths are derived; junction guards and rollback fault injection use the same path spelling as the installer.
- Added permanent regression variants for rollback and junction scenarios using a real equivalent temporary path with a different prefix. Cleanup remains bound to the original owned directories; installer behavior and CI gates were preserved.
- Recorded source verification and Windows/Linux job outcomes in docs/WINDOWS_CI_FIX.md. This fixture correction is local; no commit, push, tag, or release was made by the agent.
- Reran the complete local suite for the fixture correction: 44 passed, 3 linked-path checks unavailable. Kit checks returned no errors/warnings; the repackaged source inventory/bytes and Python 3.10 syntax were verified. Corrected hosted Windows jobs remain unverified.

- Prepared local patch 0.2.2 after independently reproducing three installer findings from the Manus audit of published v0.2.
- Addressed conflict candidates by incoming-file SHA-256; preview reports paths/hashes and adjacent first-creation metadata. Exclusive creation preserves edited, concurrent, and legacy candidates.
- Blocked agent-list replacement while tracked unselected adapters remain; preserved accepted files/state, reported exact retirement paths, and warned about untracked native instructions/skills. No automatic deletion was added.
- Validated supported state schema, agent/file/hash types, settings, and safe paths before planning; malformed input receives a controlled refusal.
- Added regression scenarios for candidate preservation, agent retirement, corrupt inputs, previous-version state, installed mixed-project Git visibility, and Windows junctions. Junction detection uses APIs available on Python 3.10.
- Updated installation/adapter procedures and recorded audit evidence and deferred publication work in docs/MANUS_REVIEW.md.
- Verified the local v0.2.2 clean and patched-public-tree suites: 43 passed, 2 linked-path checks unavailable; kit checks returned no errors/warnings. Verified a genuine v0.2.1 installation upgrade and the 85-file archive's inventory/bytes and Python 3.10 syntax. Successful hosted CI remains unverified.

- Rewrote the English README as a practical onboarding guide with Windows/Linux examples, defaults, project memory, workflow, profiles, clients, sharing, upgrades, and reference-layout guidance.

- Prepared local patch bundle 0.2.1 after reproducing the published v0.2 overlay's five missing-heading failures.
- Replaced known v0.1 rule paths with compact compatibility pointers to canonical template resources, preserving old inbound links without restoring duplicated policies.
- Documented reference-repository overlays and obsolete .gitignore_real; validated the real mixed-layout snapshot as well as the clean bundle. No checker exclusions or synthetic headings were added.
- Made upgrade-test fixtures derive versions from VERSION; reran the patched public snapshot's suite with 32 passed tests and 1 unavailable Windows symlink test.

- Prepared the working distribution identified by VERSION with clean project templates and separate maintainer context/history.
- Consolidated language/Git/fact rules in Core, project-specific Laravel choices in the owner profile, container policy in CONTAINERS, and active model IDs in the OpenAI provider configuration.
- Added a conservative Python installer with preview, private/team modes, managed ignore blocks, backups, conflict candidates, and unchanged-file upgrades.
- Added explicit semantic acceptance that preserves local adaptations across future upstream revisions.
- Added internal-link/anchor, frontmatter, registry, ownership, JSON, and source-visibility validation plus behavioral tests and a CI workflow.
- Expanded PHP, Laravel, Go, Python, Moodle, frontend, and library profiles; added a compact security baseline and monorepo context routing.
- Added selective Claude skills copying and optional adapters; supplied a read-only Docker resource report, with deletion governed by the existing container policy.
- Retained Docker client/daemon preflight, a startup request for a stopped daemon, and honest unavailable check outcomes.
- Added MIT after the owner's explicit selection. No commit, push, tag, release, metadata update, or runtime model switch was performed.
- Verified 32 passing behavioral tests, 1 unavailable Windows symlink test, internal checks, 9 skill metadata checks, and real Git ignore visibility; recorded runtime/hosted-CI limits.
- Preserved same-task context/continuity synchronization and the owner's configured Codecov gate during the policy consolidation.

## Earlier kit

The [archived v0.1 changelog](docs/history/v0.1-changelog.txt) preserves the detailed pre-refactor record verbatim. Its old relative paths and past language/router agreements are historical data.
[Prior routing decision](docs/adr/0001-adaptive-model-routing.md) records the accepted routing baseline; this changelog is not copied into projects.
