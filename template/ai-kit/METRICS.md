# Optional local measurements

Load only for an agreed evaluation or cost review. Measurement is opt-in: no automatic task logging, prompt capture, credentials, API calls, or price lookup. The reference distribution's `scripts/metrics.py` accepts user-supplied evidence of executed work. Routing recommendations do not establish which model actually ran.

## Record a reviewed task

Put a JSON record in a private location, preferably under `ai-kit/.metrics/` (ignored in both sharing modes). Use opaque task/experiment identifiers; do not include task text, file contents, personal data, or secrets. The helper rejects unknown fields. A minimal schema is:

~~~json
{
  "schema": 2,
  "task_id": "pair-01-run-01",
  "experiment": "context-trial",
  "arm": "kit",
  "kit_version": "installed-version",
  "outcome": "incomplete",
  "checks": "not-run",
  "rework": 0,
  "escalations": 0,
  "attempts": [{
    "provider": null,
    "model": null,
    "effort": null,
    "disposition": "inconclusive",
    "duration_seconds": null,
    "input_tokens": null,
    "cached_input_tokens": null,
    "output_tokens": null,
    "reasoning_tokens": null,
    "cost": null
  }]
}
~~~

Replace placeholders with observed facts. Include every attempt, failed call, tool/review loop, and recovery in the task's final accounting. An attempt may represent an aggregated phase only when its model/settings and measurements are consistent. In schema 2, each attempt has a `disposition` of `succeeded`, `failed`, or `inconclusive`; it distinguishes an unsuccessful cheap pass from a successful escalation without claiming causation. Existing schema 1 journals remain readable and simply have unknown attempt dispositions. Provider/model/effort, duration, token counts, and cost can be unknown (`null` or omitted); never turn missing telemetry into zero. Durations are elapsed seconds per attempt, not total experiment wall time when attempts overlap.

`outcome` is `correct`, `incorrect`, or `incomplete` after applying the experiment's acceptance rubric. `checks` is `passed`, `failed`, or `not-run` for the required automated checks; a human-reviewed correct result may have no applicable automated checks. Skipped or unavailable checks are not a pass. `rework` and `escalations` count observed interventions, independently of the number of attempts.

Cost is either `null` or an object with `amount` (nonnegative decimal string), `currency` (uppercase three-letter code), and `source` (`billing`, `provider-usage`, or `estimate`). Keep pricing provenance in the private experiment notes; estimates must remain labeled. Token fields are nonnegative integers. Cached input is a subset of input; reasoning tokens are a subset of output under this schema. If the provider's accounting differs, normalize with documented evidence or leave the field unknown. Do not add subset counts twice when calculating costs.

From the reference checkout:

~~~sh
python scripts/metrics.py record /path/to/project --from-json /private/path/task.json
python scripts/metrics.py record /path/to/project --from-json /private/path/task.json --apply
python scripts/metrics.py summary /path/to/project
python scripts/metrics.py analyze /path/to/project
python scripts/evaluate.py scaffold --output /private/path/tasks.json --experiment context-trial --task pair-01 --task pair-02
python scripts/evaluate.py coverage /path/to/project --tasks /private/path/tasks.json
~~~

Preview writes nothing. Apply writes the local `ai-kit/.metrics/tasks.jsonl` journal, refuses duplicate experiment/arm/task IDs and malformed existing data, and guards path boundaries and links. A cooperating-writer lock refuses concurrent writes; investigate an interrupted writer before manually removing its stale lock. The journal is local runtime data, not an installer-owned template. An upgrade must preserve it.

## Interpret totals

Summary groups records by experiment and arm. It reports reviewed success, attempts, rework/escalations, elapsed attempt time, token coverage, known costs by currency, and estimated-cost coverage. Cost per correct result divides **all** task costs, including unsuccessful work, by correct results. It remains unknown unless every attempt has an actual (billing/provider-usage) cost in one currency and at least one result is correct. Estimated costs remain labeled subtotals and cannot establish actual cost per correct result or savings. Known subtotals with incomplete coverage are not total spend.

These are descriptive records, not evidence of causation or savings. Compare matched tasks with a fixed model/settings, fresh sessions, the same acceptance checks, and balanced run order. Evaluate routing changes in a separate experiment. Include failed and inconclusive trials; do not infer cache benefit, model switching, or native client activation from a generated configuration.

## Analyze for routing

`analyze` aggregates the journal per provider: attempts, reviewed tasks, correct tasks, task success rate, known cost by currency, cost coverage, cost per correct result, and the models/efforts seen. Task identity is `(experiment, arm, task_id)`, so paired baseline/kit rows never collapse. Schema 2 also reports attempt-disposition coverage and decisive attempt success rate. A task is attributed to every provider used in its attempts, so neither measure establishes causation.

Use the report to inform `ai-kit/router/selection.json`, never to rewrite it automatically. Prefer the provider with the best cost per correct result for the work role and the cheapest provider that still passes checks for the cheap role, then run a separate matched experiment before trusting the change. `analyze` writes nothing and performs no API calls or price lookup; unknown cost or outcome coverage stays unknown rather than becoming zero.

## Pair coverage

`evaluate.py scaffold` writes an opaque private task pack only with `--apply`; it contains an experiment ID and task IDs, not task text or private evidence. `evaluate.py coverage` compares that pack with the local journal and reports missing baseline/kit pairs, unexpected records, and reviewed outcomes. It does not score prompts, inspect patches, or infer a winner. Keep prompts, rubrics, and private notes outside the pack; document matched tasks, controls, acceptance and review before the actual trial.

## Controlled execution and schema 3

The distribution's `aikit benchmark run PROJECT --pack PRIVATE_PACK` previews isolated baseline/kit-fixed/kit-adaptive trials; --apply invokes an explicitly configured worker. Fixed baseline/kit use the same provider/model/effort. Every task/repetition starts at the same immutable Git revision; worker-reported actual execution stays separate from requests. No live vendor adapter is implied. Tokens/cost must come from actual worker/provider/billing evidence, with missing values left null. Passing checks leaves semantic review pending. `benchmark review` accepts explicit manual/independent outcomes; `benchmark export` transfers reviewed records into the private journal without overwriting differing duplicates. Never benchmark production services or carry credentials into workspaces/reports.

Schema 3 adds required `metadata`: case_id, stack (LARAVEL/FILAMENT/GO/MOODLE/PYTHON/unknown), task_class, level (0-6 or null), revision (full Git commit ID or null), repetition (positive integer), review (manual/independent/pending), and capabilities (opaque labels). Pending review requires an incomplete outcome. Schemas 1/2 remain readable; old records have unknown strata and cannot establish controlled savings. All schema-3 attempts require disposition as in schema 2.
Schema 3 permits explicit null rework/escalation counts when telemetry cannot establish them. Summary reports intervention coverage rather than inventing zero. A failed/unreported worker becomes one inconclusive local execution phase with unknown model/usage/interventions; that phase count does not establish how many model calls occurred.

`metrics stacks PROJECT` groups declared stack strata; missing stack stays unknown. `metrics compare PROJECT --experiment ID --candidate kit-fixed|kit-adaptive` reports paired costs, correctness, cost per correct result and `(baseline cost - candidate cost) / baseline cost * 100%`. Savings stay null for incomplete pairs/review, unknown/different starting state or strata, unknown/estimated/mixed-currency cost, zero baseline cost or lower candidate correctness. Fixed-model comparisons also require identical observed provider/model/effort. Include all failed and recovery attempts; an observed difference is not a prediction or causal guarantee.

## Proposal history and explicit restore

`metrics propose PROJECT --stack PYTHON --task-class implement --level 2` analyzes matching schema-3 evidence and previews candidate models with sample/quality/cost/time coverage. --apply saves an immutable proposal under `ai-kit/.metrics/proposals/`, including the evidence fingerprint and prior selection. It never changes active selection. Requirements and profile behavior live in [routing policy](router/POLICY.md#modes-pins-and-optimization-profiles).

`metrics restore PROJECT --proposal SHA256` previews restoring that proposal's prior selection; --apply verifies immutable history, backs up the current selection, refuses concurrent writes and performs the explicit restore. It does not roll back project files, journals or live client state. Preserve history and review the proposed selection before applying it.
