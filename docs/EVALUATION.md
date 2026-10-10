# Real-project evaluation protocol

This protocol prepares application trials; it contains no measured application results. The owner chose to run the real-project trials separately. Synthetic routing and installer regressions validate implementation behavior, not productivity or savings.

## First experiment: instructions with a fixed model

1. Select a representative repository and record its starting revision, actual stack/versions, runnable checks, and allowed files. Use isolated disposable checkouts and a disposable database for each run; never reuse changes from the other arm.
2. Define a small task set before running anything: mechanical edit, substantive feature, bug diagnosis, authorization/tenant boundary, and fresh-session continuation. Include Filament tasks only if the application actually uses Filament. For each task write an identical prompt, acceptance rubric, scope, required checks, and stopping rule. Include tasks where the kit may add overhead. Use `scripts/evaluate.py scaffold` to create an opaque private baseline/kit task-ID pack, not a prompt or evidence store.
3. Arm A uses the project's existing instructions; arm B adds a reviewed AI-KIT installation. Preserve the same project facts, source starting state, tools, permissions, provider, actual model, effort, context/output limits, and runtime settings. Disable adaptive model changes in this experiment. Record the kit version and installation choices.
4. Start a fresh session for every run. Balance/randomize A/B order, repeat task pairs, and record model/version and pricing dates when runs occur. Do not feed one arm's answer, patch, or corrections into the other. Account for bootstrap/context preparation time separately and for every retry/review/recovery call within the task.
5. Apply the predeclared rubric and checks. Prefer a reviewer unaware of the arm, when available and authorized. Mark failures, unavailable checks, and incomplete work explicitly. Avoid treating compilation or tests alone as full semantic correctness. Record code scope violations or unintended edits in the private trial notes.
6. Collect actual runtime telemetry; store one reviewed task record with all attempts through [metrics.py](../scripts/metrics.py) using the [measurement contract](../template/ai-kit/METRICS.md). A generated route/configuration is not telemetry. Use opaque matched task IDs and private notes. Baseline records may use `kit_version: "not-used"`.

Run `scripts/evaluate.py coverage PROJECT --tasks PRIVATE_PACK` before comparing results. It reports missing baseline/kit pairs and unexpected journal records, but cannot assess semantic equivalence. Compare matched correctness and failure rate before cost/time. Report total cost per correct result, rework, recovery/escalations, duration coverage, input/output/reasoning/cache token coverage, and bootstrap overhead. Include failed tasks in spend. Separate billed/usage-derived costs from estimates, keep currencies separate, and report missing observations. Small samples support provisional conclusions; do not publish a savings percentage when arms or telemetry are not comparable.

## Context and continuation checks

For a mixed repository, pick one affected module. Observe which context/profile files are loaded: the active module's minimum needed rules and relevant shared boundaries should be selected from PROJECT_CONTEXT/WIKI. Unrelated stack/provider profiles should not be loaded by default. Record loaded bytes/tokens only when actually observable; do not substitute file size for token usage.

For continuation, end a session after documenting verified facts, commands, decisions, and unresolved work. Start another session with the same repository state and task handoff but without the previous chat. Check whether the agent recovers module paths, commands, defaults, Git authorization limits, and remaining work correctly. Measure rereads/corrections and accidental unrelated edits. The existing context map and continuity skills guide this process; no automatic context engine is claimed.

## Second experiment: routing

Hold the adopted instruction setup fixed, then compare fixed-model execution with reviewed routing recommendations on matched tasks. Record the recommended level/model/effort separately from what the client actually executed. Manual risk/operation inputs must have the same evidence available across runs. Diagnose missing facts, ambiguous tasks, tool failures, and environment failures before model escalation; level 6 needs a documented capability reason.

The offline helper does not switch live models, invoke delegates, or measure calls. Trials must verify client controls explicitly. Evaluate cost to a correct result including escalation and retained context, rather than initial-call price. Add orchestration only after a measured improvement justifies its operational complexity.

## Trial notes template

Keep this file in the project's ignored `ai-kit/.metrics/` directory. Record experiment ID, starting revisions, kit version/choices, task IDs, acceptance rubrics, run order, timestamps, actual model/settings, tools, check commands/results/skips, reviewer disposition, cost/pricing provenance, missing telemetry, and deviations. Store no secrets or production data. Summaries may be shared after reviewing their contents and receiving the owner's publication authorization.
