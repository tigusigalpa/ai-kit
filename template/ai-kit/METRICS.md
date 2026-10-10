# Optional local measurements

Load only for an agreed evaluation or cost review. Measurement is opt-in: no automatic task logging, prompt capture, credentials, API calls, or price lookup. The reference distribution's `scripts/metrics.py` accepts user-supplied evidence of executed work. Routing recommendations do not establish which model actually ran.

## Record a reviewed task

Put a JSON record in a private location, preferably under `ai-kit/.metrics/` (ignored in both sharing modes). Use opaque task/experiment identifiers; do not include task text, file contents, personal data, or secrets. The helper rejects unknown fields. A minimal schema is:

~~~json
{
  "schema": 1,
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
    "duration_seconds": null,
    "input_tokens": null,
    "cached_input_tokens": null,
    "output_tokens": null,
    "reasoning_tokens": null,
    "cost": null
  }]
}
~~~

Replace placeholders with observed facts. Include every attempt, failed call, tool/review loop, and recovery in the task's final accounting. An attempt may represent an aggregated phase only when its model/settings and measurements are consistent. Provider/model/effort, duration, token counts, and cost can be unknown (`null` or omitted); never turn missing telemetry into zero. Durations are elapsed seconds per attempt, not total experiment wall time when attempts overlap.

`outcome` is `correct`, `incorrect`, or `incomplete` after applying the experiment's acceptance rubric. `checks` is `passed`, `failed`, or `not-run` for the required automated checks; a human-reviewed correct result may have no applicable automated checks. Skipped or unavailable checks are not a pass. `rework` and `escalations` count observed interventions, independently of the number of attempts.

Cost is either `null` or an object with `amount` (nonnegative decimal string), `currency` (uppercase three-letter code), and `source` (`billing`, `provider-usage`, or `estimate`). Keep pricing provenance in the private experiment notes; estimates must remain labeled. Token fields are nonnegative integers. Cached input is a subset of input; reasoning tokens are a subset of output under this schema. If the provider's accounting differs, normalize with documented evidence or leave the field unknown. Do not add subset counts twice when calculating costs.

From the reference checkout:

~~~sh
python scripts/metrics.py record /path/to/project --from-json /private/path/task.json
python scripts/metrics.py record /path/to/project --from-json /private/path/task.json --apply
python scripts/metrics.py summary /path/to/project
python scripts/metrics.py analyze /path/to/project
~~~

Preview writes nothing. Apply writes the local `ai-kit/.metrics/tasks.jsonl` journal, refuses duplicate experiment/arm/task IDs and malformed existing data, and guards path boundaries and links. A cooperating-writer lock refuses concurrent writes; investigate an interrupted writer before manually removing its stale lock. The journal is local runtime data, not an installer-owned template. An upgrade must preserve it.

## Interpret totals

Summary groups records by experiment and arm. It reports reviewed success, attempts, rework/escalations, elapsed attempt time, token coverage, known costs by currency, and estimated-cost coverage. Cost per correct result divides **all** task costs, including unsuccessful work, by correct results. It remains unknown unless every attempt has a cost in one currency and at least one result is correct. Known subtotals with incomplete coverage are not total spend.

These are descriptive records, not evidence of causation or savings. Compare matched tasks with a fixed model/settings, fresh sessions, the same acceptance checks, and balanced run order. Evaluate routing changes in a separate experiment. Include failed and inconclusive trials; do not infer cache benefit, model switching, or native client activation from a generated configuration.

## Analyze for routing

`analyze` aggregates the journal per provider: attempts, reviewed tasks, correct tasks, success rate, known cost by currency, cost coverage, cost per correct result, and the models/efforts seen. A task is attributed to every provider used in its attempts, so a provider's success rate reflects the tasks it actually worked on.

Use the report to inform `ai-kit/router/selection.json`, never to rewrite it automatically. Prefer the provider with the best cost per correct result for the work role and the cheapest provider that still passes checks for the cheap role, then run a separate matched experiment before trusting the change. `analyze` writes nothing and performs no API calls or price lookup; unknown cost or outcome coverage stays unknown rather than becoming zero.
