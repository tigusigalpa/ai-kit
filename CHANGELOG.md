# AI-KIT changelog

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
