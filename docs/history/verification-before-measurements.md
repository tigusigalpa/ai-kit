# Verification before measurement-led development

Historical results; current checks are in [implementation](../IMPLEMENTATION.md#measurement-led-development-verification).

### Early distribution verification

Pre-v0.4.7 detection, adapter/provider, and extras verification (62/73/69-test runs) is preserved in the [v0.3 changelog](../history/v0.3-changelog.md).

### Router and agent-registry verification

2026-10-10, Windows/Python 3.14.6: 92 tests ran, 91 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors. Covers registry, route classification/resolution, local and pending providers, and configure preview/apply/conflict. Gemini IDs remain pending; no live API or hosted CI ran.

### Client settings and detection verification

2026-10-10, Windows/Python 3.14.6: 128 tests ran, 127 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors; Python 3.10 grammar was verified. Regressions cover key-level settings merges with backups, user-edit survival, disabled-extra removal, legacy whole-file migration, the invalid-JSON conflict, managed_json validation, doctor reports, client detection, and lockfile/evidence-based commands. The hook ran through Git Bash sh with a CRLF script and a spaced Windows path; an end-to-end CLI run was stable on rerun. A real v0.4.6 installation upgraded cleanly; a v0.4.6 downgrade preview reports a settings conflict. Native Claude Code hook delivery, ask enforcement, and hosted CI remain unverified.

### Onboarding and project-facts verification

2026-10-10, Windows/Python 3.14.6: 109 tests ran, 108 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors; Python 3.10 grammar was verified. Regressions cover interactive selections, the post-apply doctor check, per-manifest language/version/command detection, project.json drafting and preservation, and the adr/changelog scaffolding helpers. The Makefile targets were exercised locally; hosted CI and PyPI publication remain unverified.

### Unified CLI and fact-drift verification

2026-10-10, Windows/Python 3.14.6: 191 tests ran, 189 passed, two skipped; kit validation returned zero errors. Covers the `aikit` dispatcher, the module-map drift warning, and non-Latin chat language names. Hosted CI and a portable wheel remain unverified.

### Provider review and doctor-fix verification

2026-10-10, Windows/Python 3.14.6: 197 tests ran, 195 passed, two skipped; kit validation returned zero errors. Covers `router.py providers` status/sources, `doctor.py --fix` restore/no-op behavior, CI self-install wiring, and the golden `.claude/settings.local.json` snapshot. Hosted CI, Gemini verification, and a portable wheel remain unverified.

### Measurement analysis and Gemini verification

2026-10-10, Windows/Python 3.14.6: 199 tests ran, 197 passed, two skipped; kit validation returned zero errors and zero warnings. Covers `metrics.py analyze` and verified Gemini IDs; thinking/effort levels remain to be confirmed. Hosted CI and a portable wheel remain unverified.

### Windows CI fixture verification

2026-10-08, Windows/Python 3.12.14: 47 tests executed, 44 passed, 3 skipped (symlink privilege and two junction variants). Equivalent-path reproductions exposed both failures before the fix; the corrected fixture restores rollback injection and reaches the junction permission check. See [source/job evidence and limits](../WINDOWS_CI_FIX.md). Corrected hosted Windows results remain unverified.

### Manus patch verification

The detailed v0.2.2 record lives in [MANUS_REVIEW.md](../MANUS_REVIEW.md): candidate preservation, adapter-retirement review, junction detection, and the synthetic/upgrade smoke checks. Local result: 45 tests, 43 passed, 2 skipped. These are synthetic project/file tests, not application runtime trials; hosted CI remains unverified.

### Overlay regression

The supplied Linux/Python 3.13.16 CI failure exposed old v0.1 documents remaining beside the new v0.2 layout.
All 91 tracked source blobs at the published revision were reconstructed with matching Git object hashes. The original checker reproduced all five missing-heading errors and the large MODELS warning.
Patch 0.2.1 replaces known old rule documents with small canonical-resource pointers. It preserves the checker's full validation scope and does not reintroduce language/Git policy into maintainer AGENTS.
The clean bundle and patched public snapshot both passed the unchanged checker with zero errors/warnings and real Git visibility checks on Windows/Python 3.12.14.
The behavioral suite was rerun on the patched public snapshot: 33 tests, 32 passed, 1 Windows symlink-privilege skip. Upgrade fixtures now derive their versions from VERSION rather than pinning an old bundle number.
Archive inventory/exact bytes and Python 3.10 syntax were verified. Successful hosted CI after publication remains unverified.

### Original bundle checks

The original-bundle verification record is archived in [docs/history](../history/original-bundle-checks.md).

