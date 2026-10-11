# ADR 0012: Measurement-led routing and isolated benchmarks

Status: accepted for local tooling; live client adapters and orchestration remain deferred.

## Context

The local distribution already has an offline router, conservative installer, optional telemetry journal, manifest snapshots and opaque A/B coverage. Neither keywords nor generated configuration establish actual execution or savings. The owner requested code/tests now and real application trials separately.

## Decision

Build on the existing contracts. Add backward-readable metric schema 3 with explicit case/repetition/revision/stack/class/level/capabilities and semantic-review metadata. Preserve schemas 1/2. Estimated prices remain labeled subtotals and cannot become actual cost per correct result or savings.

The benchmark reads Git blobs at an exact commit, without checkout filters, hooks, history, hardlinks or source mutations. Each task/arm/repetition gets a new directory. A uses no installed kit; B uses the kit with A's exact provider/model/effort pin; C requests an adaptive recommendation. Reject tracked secret/runtime paths, links, submodules and preinstalled kit trees. Rotate arm order between repetitions. Preserve interrupted runs for inspection; do not automatically delete them or retry paid work.

Execution requires an owner-reviewed `aikit-worker-v1` subprocess that accepts a JSON request on stdin and returns actual attempt telemetry on stdout. The harness controls working directory, timeout and a minimal environment; this is process separation, not a security sandbox. It does not ship an unverified vendor API/client switch. Requested controls and reported execution stay separate. An actual client adapter needs primary documentation verification, credential handling outside reports, and integration tests before being recommended for live use.

Automated checks do not set semantic correctness. Explicit manual/independent review changes outcomes with backups. Reviewed records export idempotently into the existing private journal. Comparisons require matched starting states/tasks and real single-currency costs, include failed/recovery work, and block savings when correctness falls below baseline. Fixed-model comparisons additionally require identical observed model/effort. Report observed differences, never predictive guarantees or causation.

Optional routing modes/profiles/pins live in a separate configuration. Existing selection files/defaults remain valid. Adaptive recommendations require sufficient distinct immutable cases, comparable trial sets, complete actual costs, a conservative quality lower bound and quality no worse than the incumbent. Balanced also requires measured speed no worse. Mixed-model strategies remain in cost summaries but cannot be attributed to a single model for learning. Pins and explicit controls override recommendations. Proposal history stores evidence fingerprints and prior selection; restore is explicit, preview-first, guarded and backed up. No proposal changes active configuration.

Context selection is read-only, by declared module scope and profiles. Keep Core, settings, engineering/security, project facts, relevant profiles, applicable nested instructions and architectural decisions even when they exceed the measured byte budget. Detect byte-identical duplicates and flag unknown module scope. Do not infer loaded tokens from selected bytes or treat manifest drafts as verified stack use.

## Orchestration research

Configurable planner/executor/reviewer/escalation roles map to existing selection roles rather than model names. Recommended starting mappings use work/work/work/escalation; a project can select cheap planning or review only after evidence. These mappings are configuration for a future adapter, not executed calls.

A live orchestrator must: verify supported switching; isolate credentials and disposable services; account for every planning/review/delegation/recovery call; bind outcomes to task identity; preserve useful outputs across escalation; and stop when the measured coordination cost exceeds the benefit. Compare it against the fixed kit arm on matched tasks, require no quality regression, and include coordination spend in cost per correct result. No automatic Git operations or routing-policy writes. This phase follows real benchmark evidence rather than preceding it.

## Consequences

The kit is useful without switching: context selection, explicit pins, manual telemetry and conservative analysis all work offline. Synthetic workers establish harness behavior only. Historical samples and Wilson bounds are decision aids with correlated-task and distribution-shift limits; representative held-out application trials remain necessary. No savings or native client activation has been established by this implementation.
