# ADR 0015: Optional bounded orchestration

Status: accepted for code and synthetic verification; live trials are separate.

## Decision

Extend the installer with an independent persistent opt-in module. Render narrow Codex helper files from canonical provider roles without modifying global/native parent configuration. Native execution depends on explicit host/user authorization, account controls and actual client discovery.

Provide a standard-library, explicit-apply OpenRouter text executor with fixed endpoint, selected project-relative inputs, validated configuration, capped non-resetting dedicated-key preflight, bounded requests, no redirects/fallback/retries, and no execution of model output. This is a text worker for a caller/coordinator, not an autonomous coding-agent loop or a replacement for the benchmark protocol.

Maintain one project-wide private journal and exclusive apply lock. Reserve before billable POST; retain ambiguous/pending attempts and known charges on failed responses. Stop admitting inference on unknown cost or a reserve overrun. A known generation ID can be reconciled against actual billing without replay. Server billing limits and local admission accounting have different guarantees; no precise price estimate or cancellation promise is made.

Bind repeated task IDs to complete request/config/input hashes and acceptance to the original output hash. Manual review is explicit. Report unknowns and count failed/rejected attempts in cost per accepted result; native planner/helper/reviewer spend must be recorded separately for an end-to-end comparison. No live API/client savings or automatic learning is claimed.

## Consequences

Default installation and existing presets remain offline and unchanged. Opt-in configuration starts disabled; upgrades preserve it and private state. Local helper edits use normal reconciliation. Runtime files are excluded in private/team Git policies, source archives, wheels and Docker context. Unit tests substitute transports; package/image smoke remains offline. Real provider/account integration and comparative trials are separate.
