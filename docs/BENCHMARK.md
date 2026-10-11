# Benchmark and adaptive recommendation contract

Use a sanitized disposable application fixture at an exact Git commit. Real application runs are separately configured; shipped tests use synthetic workers and establish no model-quality or savings result. The [development stages](DEVELOPMENT_PLAN.md) and [ADR](adr/0012-measurement-led-routing.md) describe acceptance and boundaries.

## Prepare a private pack

Store prompts, rubric and pack in a private directory. The prompt/rubric paths are relative to the pack directory; linked paths and traversal are refused. Replace the example commit, executable and model identifiers with reviewed values. Commands use argv arrays, never a shell string. A worker executable must implement the protocol below; a normal CLI does not implement it just because it prints JSON.

~~~json
{
  "schema": 1,
  "experiment": "python-parser-trial-01",
  "revision": "REPLACE_WITH_FULL_COMMIT_ID",
  "repeats": 3,
  "fixed": {"provider": "configured-provider", "model": "configured-model", "effort": null},
  "worker": {"protocol": "aikit-worker-v1", "argv": ["/absolute/path/to/reviewed-worker"]},
  "timeout_seconds": 900,
  "kit_agents": ["codex"],
  "kit_preset": "minimal",
  "checks": [["/absolute/path/to/python", "-m", "unittest", "discover", "-s", "tests", "-v"]],
  "tasks": [{
    "task_id": "parser-01",
    "prompt_file": "parser.txt",
    "rubric_file": "parser-rubric.txt",
    "path": "api",
    "stack": "PYTHON",
    "operation": "implement",
    "risks": [],
    "capabilities": []
  }]
}
~~~

`stack` is one of LARAVEL/FILAMENT/GO/MOODLE/PYTHON/unknown. It must match the kit arm's detected module profiles or remain unknown. `path` selects a directory/module, with `.` for the root; it is validated against the benchmark project. `operation` and `risks` use the router's existing names. `kit_agents`/`kit_preset` are optional (default codex/minimal) and select which client adapters and preset the kit arms install, so the measured kit matches the client's real setup. Full Git object IDs, opaque unique task IDs and 1-100 repeats are required. Identical prompt/rubric/scope material under another ID is refused; use repeats. Baseline must start before AI-KIT is tracked. Tracked secret paths, symlinks, submodules and case-colliding paths are refused; untracked source/dependencies/services are not copied. Review the fixture contents as well: filename guards cannot detect every embedded secret.

~~~sh
aikit benchmark run /path/to/test-project --pack /private/trial/pack.json
aikit benchmark run /path/to/test-project --pack /private/trial/pack.json --apply
~~~

Preview does not write or execute the worker. Apply creates `ai-kit/.metrics/benchmarks/<experiment>/` under the test project, ignored in both sharing modes. Existing experiments conflict; choose a new ID for a new run. Every arm/task/repetition starts from immutable Git blob bytes and preserves executable modes. Workspaces contain source snapshots rather than a Git checkout/history. The source checkout and its uncommitted changes remain untouched.

A is baseline, B is `kit-fixed` on the exact A provider/model/effort pin, C is `kit-adaptive`. C retains the fixed pin if no provider resolves and otherwise falls back to the current capability recommendation when evidence is insufficient. Rotate arm order across repetitions; a later real trial should also address worker/provider caching and external concurrency.

## Worker protocol

The stdin request includes schema/protocol, task ID, arm, starting revision, workspace, prompt, rubric, requested provider/model/effort, selected context paths/byte counts and execution constraints. The worker must honor baseline isolation, explicitly load selected instructions in kit arms, use only disposable services, perform no commit/push, verify client controls and return the actual executed provider/model/effort. A context manifest does not prove the client loaded those files. Credentials must come from a reviewed external mechanism, never the task pack or stdout.

Only PATH and Windows process essentials are inherited. HOME/USERPROFILE/TEMP point inside the disposable workspace; provider credentials, DB URLs and other service environment are not inherited. A Git discovery ceiling prevents ordinary commands from finding the parent test repository; snapshots have no Git history, so a client requiring a Git checkout needs a separately reviewed adapter. The source must be its Git working-tree root. The harness is not a network/process security sandbox. A worker or check that explicitly overrides this boundary or internally reaches production is unsuitable for this protocol. Review commands and service provisioning before a real run.

Stdout must contain exactly this JSON shape:

~~~json
{
  "schema": 1,
  "attempts": [{
    "provider": null, "model": null, "effort": null,
    "disposition": "inconclusive",
    "duration_seconds": null,
    "input_tokens": null, "cached_input_tokens": null,
    "output_tokens": null, "reasoning_tokens": null,
    "cost": null
  }],
    "rework": null,
    "escalations": null
}
~~~

Attempts follow [the metric contract](../template/ai-kit/METRICS.md). Include all unsuccessful/recovery/tool/review phases and measured spend; do not discard expensive attempts. For one attempt without a reported duration, the harness supplies observed worker wall time, including worker overhead. For multiple attempts, per-attempt durations remain unknown if absent; worker wall time is reported separately. Usage and cost come from the worker's actual provider/billing evidence; they cannot be derived from requested model names. Unknown telemetry stays null. Estimates cannot establish savings. Capture known usage even on provider failures by returning a valid inconclusive/failed attempt; process failure/malformed output/timeout becomes unknown telemetry and blocks a savings claim. Worker logs/stderr/prompts are not copied into reports.

Observed controls must match requests for a controlled benchmark. A mismatch blocks savings; it is not silently repaired. Independent reviewers or mixed-model coordination currently need a separate experiment and complete manual accounting, because the harness does not ship an orchestrator and homogeneous fixed-model attribution is conservative.

## Review and export

Checks run in the workspace with the same clean environment. Passing checks leaves `outcome=incomplete`, `review=pending`. A private review file contains explicit acceptance:

~~~json
{"schema":1,"reviews":[{"task_id":"parser-01:r1","arm":"kit-fixed","review":"manual","outcome":"correct"}]}
~~~

Review can be manual or independent. Correctness applies the same rubric across all arms and includes semantic behavior, edge cases and unrelated changes. Required failed checks cannot be overridden as correct. Failed/malformed workers cannot be accepted as correct. Review updates back up prior result bytes. It is not an automatic independent reviewer or a quality score from tests.

~~~sh
aikit benchmark review /path/to/run --from-json /private/trial/reviews.json
aikit benchmark review /path/to/run --from-json /private/trial/reviews.json --apply
aikit benchmark report /path/to/run
aikit benchmark export /path/to/run /path/to/test-project --apply
aikit metrics compare /path/to/test-project --experiment python-parser-trial-01 --candidate kit-fixed
aikit metrics stacks /path/to/test-project
~~~

The run has per-unit results, a completeness manifest, `results.json` and `report.md`. Interrupted runs retain completed units; reporting them shows incomplete coverage, with no savings claim. Re-running `benchmark run` with the identical pack resumes: units with an existing `result.json` are never re-executed or rebuilt, missing units continue, and a changed pack is refused against the existing run. Infrastructure failures inside one unit (kit install conflict, unevidenced stack, workspace errors) are recorded as failed units with an explicit `error`, so one bad unit neither aborts the run nor hides as an executed attempt; such units still block savings and cannot be reviewed as correct. Export waits for complete execution and semantic reviews, preserves existing journal records, refuses differing duplicates and is idempotent. Include incorrect/incomplete reviewed outcomes, not just successes.

Cost per correct result includes **all** actual attempt cost divided by correct results. Savings = (baseline spend - candidate spend) / baseline spend * 100%. Savings stay unknown for unmatched cases, different starting/task strata, unreviewed outcomes, actual execution mismatch, estimated/missing/mixed-currency cost, zero baseline spend or lower candidate correctness. Fixed A/B also requires matching observed provider/model/effort. These are observed paired differences; sample size and representativeness still matter.

## Recommendations and context

~~~sh
aikit route "implement the parser" --project /path/to/project --mode adaptive --profile balanced --stack PYTHON --operation implement
aikit metrics propose /path/to/project --stack PYTHON --task-class implement --level 2
aikit metrics propose /path/to/project --stack PYTHON --task-class implement --level 2 --apply
aikit metrics restore /path/to/project --proposal PROPOSAL_SHA256
aikit context select /path/to/project --path api --budget 32000
~~~

Modes/pins/profiles are owned by [routing policy](../template/ai-kit/router/POLICY.md). Proposals save immutable evidence and a prior selection under `.metrics/proposals/`; saving never applies recommendations. `metrics restore --apply` explicitly restores that prior selection, with a backup of the current one. No automatic learned policy update. The context selector reports declared scope, selected paths, byte-identical duplicates, measured bytes and budget overruns. Required rules/decisions remain selected even above budget; bytes do not establish token savings or client loading.
