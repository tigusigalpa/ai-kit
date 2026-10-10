# ADR-0009: Provider review listing, doctor --fix, and CI self-install

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

Provider verification state lived only inside per-provider JSON, so a pending or stale mapping was easy to miss. The doctor reported missing managed files but offered no way to restore them. The CI extra required installer state in Git, which private mode deliberately excludes.

## Decision

Add `router.py providers` to surface tier, verification status, date, and primary-doc sources for every provider. Add `doctor.py --fix` to re-run the installer and restore missing managed files and owned documents while preserving local edits and reporting conflicts. Make the CI extra install AI-KIT itself from a reviewed revision when state is absent. Add a golden snapshot test pinning the generated Claude settings merge.

## Consequences

Provider verification becomes a visible review task rather than hidden JSON; Gemini remains pending until verified. `--fix` is conservative: it never overwrites local edits. The CI extra now needs network access to clone the kit and must pin a reviewed revision.

## Verification

Covered by router, doctor, native-settings, and aikit regressions. [Results](../IMPLEMENTATION.md#verification).
