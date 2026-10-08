# Engineering cycle

## Plan and implement

Establish behavior, affected contracts, and acceptance checks. Use a short plan for ordinary work and explicit steps for risky changes.
Before programming, determine whether code/services/tests require Docker and follow the [runtime preflight](CONTAINERS.md#runtime-preflight) when they do.
Preserve interfaces and conventions; add dependencies or infrastructure only for a demonstrated need.
Read the relevant stack profiles and [security baseline](SECURITY.md); apply [owner conventions](profiles/OWNER.md) when settings select owner and the affected stack is Laravel.

## Test

Use verified project commands; targeted checks first, broader checks when risks or gates require them.
Add meaningful tests for behavioral changes, regressions, authorization, transactions, cancellation, and recovery; simple documentation needs link/content checks.
Unavailable tools/services are unverified, not passed. Container checks follow [CONTAINERS](CONTAINERS.md).
For owner conventions, when Codecov is configured target at least 90% of changed lines and at most 0.5 percentage-point overall decrease; assertions and critical branches matter beyond percentages. Preserve other projects' agreed gates; do not claim an unconfigured gate is active.

## Review

Review diff behavior, edge cases, compatibility, errors, resource use, authorization, sensitive data, and migrations.
Name the concrete scenario, file, and severity. Avoid repeating linter-only findings.
Normal work uses tests and self-review; independent review is required for critical contracts when available and authorized. Report missing required review; self-review is not independent.
Delegation is conditional on host/user authorization and a concrete benefit; do not spawn reviewers by default.

## Migrations

Check actual schema/version, locks, data volume, old/new application compatibility, backfills, and deployment order.
Use staged introduce/backfill/remove changes where appropriate; provide tested recovery or rollback and rerun behavior.
Do not run production migrations without explicit authorization. Verify both fresh and upgrade paths in a disposable test environment.

## Document

Update project docs for behavior/commands/contracts. Synchronize context, continuity skill, and WIKI through [Core](CORE.md#verified-facts-and-context); record significant decisions in docs/DECISIONS and docs/adr/.
Update project CHANGELOG after every task with file changes, including adopted kit changes; keep root kit maintenance history out of project templates.
Show only actual checks/badges/licenses. Report changed files, verification, and concrete remaining limitations.
