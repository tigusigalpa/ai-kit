# Measurement-led development

The supplied brief refers to v0.9.0; the audit started from local v0.10.0. The owner requested packaging the completed changes as v0.11.0 on 2026-10-11. Existing metrics use experiment/arm/task identity, schema-2 dispositions, private journals and a read-only provider analysis. Existing evaluation checks opaque pair coverage; context snapshots detect manifest drift. Reuse these contracts.

| Stage | Deliverable and acceptance | Automated verification |
| --- | --- | --- |
| Stability | Provider changes discard inherited model/effort; Gemini policy matches its reviewed registry; wheel runs outside the checkout | Cross-provider precedence and composite-experiment regression; offline wheel installation, resource inventory and CLI/install smoke |
| Measurements | Preview-first `benchmark run` uses one immutable Git revision, fresh workspaces per task/arm/repeat, a declared worker protocol, complete attempt telemetry, checks and separate semantic review; JSON/Markdown reports | A/B share a model pin; no checkout mutation or shared workspace; unknown usage, failed checks, review gate, interrupted execution, paths/conflicts and repeated runs |
| Adaptive routing | Optional modes, task/project pins, economy/balanced/quality profiles and conservative evidence-based recommendations; existing selection remains readable | Pin precedence, unsupported controls, sufficient matched samples, quality floor, retry cost, missing/estimated cost refusal and no selection writes |
| Context | Read-only selection by declared module/profiles, duplicate detection and a measured byte budget; critical rules/decisions cannot be dropped | Monorepo scope, unknown modules, shared requirements, duplicates, over-budget critical context and linked paths |
| Orchestration research | Configurable planner/executor/reviewer/escalation design; live execution depends on a separately verified client contract | Document protocol boundaries and coordination-cost acceptance before a live adapter is added |
| Optimization | Immutable proposal history with a prior configuration snapshot and explicit restore; no automatic application | Proposal preservation, concurrent-write/conflict refusal, rollback preview and selection preservation |

Real application trials are deferred by the owner. Synthetic workers verify the harness, not savings, model quality, native client activation or production isolation of a future worker. A trusted worker must use disposable services and collect actual execution/usage; credentials stay outside packs/workspaces/reports. A task is not correct merely because checks pass. Missing telemetry, unmatched tasks, estimates, unequal fixed models and incomplete review block savings claims.

See [ADR 0012](adr/0012-measurement-led-routing.md), the [benchmark contract](BENCHMARK.md), and the [evaluation protocol](EVALUATION.md).
