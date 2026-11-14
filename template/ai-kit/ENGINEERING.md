# Engineering cycle

## Instruction controls

Read settings before applying optional guidance. Absent `model_switching_enabled` means true; absent `instruction_profile` means full. These settings are independent of routing optimization profiles and installer presets.

When `model_switching_enabled` is false, use the user's selected model. Do not recommend another model (including cheaper/weaker models), change reasoning effort, or override other model settings. Skip the role/effort ladder, adaptive recommendations and economic model selection even if another AI-KIT document suggests them. Do not pass model/effort overrides to helpers. Explicitly configured external text tasks are separate executions, never an implicit handoff or fallback.

Optional `model_switching_exceptions` selects protected families: astra, fable, k3.1. Absent/empty preserves previous behavior. With switching enabled and a selected protected family, keep that model and its chosen effort, skip model/effort advice and economic substitution, and do not automatically hand work to cheaper helpers. A change needs the user's explicit request. Never raise effort automatically either. Use trusted platform model metadata when supplied, or the user's declared choice as intent; never label that declaration observed execution. Do not infer the current model from router pins, helper files, quota consumption or self-identification. If exceptions are enabled and the model is unknown, avoid model/effort advice until the user declares it. Full/minimal does not reset exceptions.

The exception list also accepts exact model names/IDs. A direct user request to preserve any selected model/effort takes precedence for that task even without a saved exception. CLI --preserve-model declares an invocation-only exception without writing files; installer --protect-model appends a persistent exception and prepares managed helpers. Do not invoke a helper with conflicting fixed model/effort settings for a protected task; use a compatible inherited helper or report unavailable/unverified inheritance. A one-call advice flag does not rewrite existing native configuration or remove loaded context.

When any exceptions are enabled, managed Codex helpers omit static model/effort assignments so changing the parent model between sessions cannot silently bypass the exception. Preserve host inheritance; do not supply model/effort overrides for protected/unknown parents. Other-model delegation requires a separate explicit user request, not an inferred savings benefit. Existing custom helper/Aider/native configuration needs review; instructions do not enforce host behavior. Explicitly configured external tasks remain separate and budgeted.

`full` retains the existing conditional guidance. `minimal` loads only mandatory project/nested instructions, architecture decisions, task-relevant stack rules, authorization, security and critical quality/check requirements. Skip unsolicited upstream maintenance, optional workflows, extra roles and economic optimization. Use an optional workflow only when directly needed by the user's task; retain its safety boundaries. Do not omit owner conventions, enabled UUID/identity requirements or required checks. A direct routing request may use recommendations when switching is enabled, independently of this profile.

Neither setting enforces host behavior, removes already loaded context or overrides explicit project constraints. Never infer the running model/effort from a catalogue, pin, config or preferred name. Report runtime values only with platform execution evidence and its scope; otherwise report unknown. Preserve the user's chosen reasoning effort in both profiles.

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
