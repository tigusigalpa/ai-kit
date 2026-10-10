# ADR-0011: Evidence freshness, adapter lifecycle, and evaluation coverage

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

Provider-level analysis could collapse matching task IDs from different experiment arms, adapter retirement required manual deletion, and project context had no durable evidence that its manifest facts were still current. Client adapter documentation status was scattered across prose. The evaluation protocol needed a minimal private pairing tool, while indirect prompt injection and tool-server scope required a concrete policy boundary. Finally, the console script was editable-install-only rather than verified as a portable wheel.

## Decision

Release v0.10.0 with backward-readable measurement schema 2, adding per-attempt disposition and experiment/arm/task identity to provider analysis. Capture manifest digests in optional project-fact evidence and have doctor report module, profile, and evidence drift; `aikit context snapshot` is preview-first and updates evidence only on explicit apply. Add `aikit adapters report` and a conservative explicit `retire` flow that backs up and removes only unchanged tracked adapter files. Add client documentation metadata to the registry, a private opaque A/B task-pack scaffold/coverage harness, and an MCP posture policy. Package repository resources with the `aikit` console script and add cross-platform wheel smoke jobs.

## Consequences

Existing schema 1 metric journals remain valid but have unknown attempt disposition. Context snapshots are evidence of reviewed manifests, not automatic truth or command execution. Retirement never deletes local edits, untracked files, directories, client settings fragments, or ignore blocks. Client documentation verification remains distinct from native client activation. The evaluator reports record completeness, not semantic correctness or causal performance. Wheel and hosted CI behavior remain unverified until the workflow runs on a published revision.

## Verification

Covered by new metrics, context, adapter, evaluator, package, checker, and CLI regressions; final local and hosted execution results must be recorded separately.
