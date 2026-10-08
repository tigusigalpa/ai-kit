# ADR-0002: Clean templates and conservative upgrades

- Date: 2026-10-08
- Status: accepted for the local working distribution

## Context

Three external reviews corroborated duplicated operative policy, mixed kit/project history, ambiguous ignore installation, and missing shipped checks.

## Decision

Keep canonical installable instructions in template/, maintain kit facts/history at the root, and route conditional rules through short entries.
Use private/team ignore templates and a cross-platform standard-library installer. Preview by default; preserve project-owned files and local managed-file adaptations.
Update managed files only from a known unchanged baseline. Conflicts require review; no blind folder replacement or force flag.
Keep owner conventions as this user's default; expose explicit settings for other installations.

## Consequences

The installer handles mechanics; bootstrap still verifies and reconciles project semantics. Baselines/candidates are local private state.
Plain instructions do not guarantee client activation, model switching, or command enforcement. Test those controls in the actual runtime.

## Verification

Behavioral tests cover dry-run, repeat installation, upgrade conflicts, scoped ignores, and path boundaries. [Results](../IMPLEMENTATION.md#verification).
