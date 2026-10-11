# Adaptive routing policy

Load for orchestration, model/budget/runtime decisions, or routing review. Ordinary execution need not load provider detail.
Optimize total cost to a correct result, including failed calls, tool loops, review, context, reasoning/output tokens, and recovery. Avoid invented confidence scores or savings.

## Capability ladder

| Level | Task | Role / effort |
| --- | --- | --- |
| 0 | Trivial classification/extraction | cheap / none if supported |
| 1 | Narrow mechanical implementation | cheap / low |
| 2 | Substantive engineering | work / medium |
| 3 | Difficult debugging, architecture, concurrency | work / high |
| 4 | Conflicting evidence, distributed or sensitive correctness | work / xhigh |
| 5 | Exceptional reasoning with a plausible benefit | work / max |
| 6 | Diagnosed capability shortfall or demonstrated advantage | escalation / effort selected separately |

Choose a justified starting level directly. Do not pay for every lower rung. Diagnose ambiguity, missing evidence, tool mistakes, environment failure, and capability shortfalls before changing models.
After repeated diagnosed failure change approach; keep useful independent work moving. Escalation must address the cause.

## Runtime and context

Choose model/effort, latency tier, and relevant context separately. Use standard reasoning/mode/tier defaults; paid acceleration/pro requires supported controls and a concrete benefit.
Retrieve -> select -> reason. Preserve exact invariants/evidence, trim duplicated or stale output, use stable cacheable prefixes only where supported, and check actual cache usage.
Match output budget to deliverable and invisible reasoning needs. Costs/thresholds are provider facts, not universal constants.
Normal work uses checks/self-review; critical correctness needs independent review when available and authorized. No default delegation or fabricated reviewer execution.

## Providers

Active role defaults: [openai.json](providers/openai.json), [anthropic.json](providers/anthropic.json), [kimi.json](providers/kimi.json), and [gemini.json](providers/gemini.json), interpreted by their provider references.
[local.json](providers/local.json) maps the same roles to self-hosted models declared in [selection.json](selection.json). Gemini's reviewed model mapping is active; its thinking controls remain unknown until declared against primary documentation.
Registry/configuration plus current primary docs establish capabilities; model names alone do not.
Unavailable switching means a recommendation, not a claim of execution. Respect explicit model, cost, and latency choices.

## Selection

[selection.json](selection.json) records which providers the project owner actually has, so routing advice and generated configuration resolve to reachable models rather than abstract capability.
`default_provider` names the provider used for any role without an override; `roles.<role>` may be `null`, a provider name, or an object overriding `provider`/`model`/`effort`.
`local_models.<role>` supplies self-hosted model IDs for the local provider. Pending providers are skipped until their IDs are verified.

## Offline routing helper

The reference distribution ships `scripts/router.py`, which works offline and never installs credentials or a switching runtime:

- `route "<task>"` uses English/Russian operation and risk rules, word boundaries, and optional `--operation`, repeatable `--risk`, and `--components` evidence. Signals explain the chosen level; rules can miss context. Level 6 requires explicit selection after diagnosis. File names/code spans are not operation evidence.
- `--level`, `--role`, `--effort`, `--provider`, and `--model` override the recommendation without changing selection.json. Effort precedence is explicit CLI, explicit role selection, then the ladder; level 6 uses the declared model default unless explicitly chosen. `recommended_effort` preserves the request while `effort` names a declared supported control or is null. Unsupported automatic effort falls back to the declared default; an unsupported explicit effort is refused for a resolved model. Unknown custom/local model capabilities stay unknown until declared in provider configuration.
- `configure PROJECT --apply` writes `ai-kit/router/resolved.json` (the resolved role mapping) and, when Aider is a selected agent, a native `.aider.conf.yml` model routing file. Preview first; existing differing native files conflict and are never overwritten.

The helper recommends; it does not change the active chat model or run a task. Use [optional local measurements](../METRICS.md) only when evaluation is requested; record the actual executed model separately from routing advice.

Examples from the reference checkout:

~~~sh
python scripts/router.py route "implement payment parsing" --operation implement --risk payments
python scripts/router.py route "review the patch" --level 3 --role work --effort high
~~~

## Modes, pins and optimization profiles

Optional [routing.json](routing.json) selects `manual`, `fixed`, `recommended` (default) or `adaptive`, with `economy`, `balanced` (default) or `quality`. Missing routing.json preserves the default behavior of older installations. Selection.json still owns provider/model role mappings; no command applies learned changes automatically.

`project_pin` and `task_pins.<opaque-id>` contain provider/model/effort (null effort means no control). A task pin overrides a project pin; explicit per-call provider/model/effort overrides pins. Manual/fixed requires a resolved pin or explicit controls. Pins and configured effort are preserved. Switching provider/model discards inherited model-bound effort; an explicit incompatible effort is refused.

`route` accepts --mode, --profile, --task-id, --stack and repeatable --capability. Adaptive mode considers matching schema-3 measurements with the same stack/class/level/capabilities. Default minimum is 20 distinct immutable cases; repeated trials of one case do not inflate that count. Candidates need complete actual single-currency costs, a Wilson 95% lower quality bound above `quality_floor`, identical case/repetition sets and quality no worse than the current model. All retries count. Mixed-model strategies cannot be attributed to one model. Missing/incomparable evidence retains the capability recommendation. Current catalogue/model/effort/capability declarations must permit the proposed controls; unsupported candidates are skipped. Declare required capability labels in the model's provider role configuration; unknown capabilities cannot be asserted from a model name.

Training excludes the instruction baseline and compares kit trials within the same experiments; reused opaque case IDs from different task packs cannot establish comparable history. Pending/incomplete trials and mixed-model recovery are not discarded to inflate quality; pending review, unattributable executed models or mixed strategies block a single-model recommendation.
Historical access does not declare current availability: learned choices are limited to providers selected by default/role mappings, plus configured self-hosted models. Project/task pins also remain authoritative in the adaptive benchmark arm.

Economy prefers lower cost, can use supported low effort for bounded level-2 work and has a smaller context byte target. Balanced also requires comparable measured time no worse than the incumbent. Quality raises automatic low effort to high when supported, requires independent review and a measured quality lower bound of at least 0.95. Explicit controls, risk floors and critical context take precedence. Escalation remains diagnosed rather than a retry of every lower rung.

`context_bytes` sets per-profile targets; the helper returns a recommendation and never drops critical rules for a budget. `orchestration` maps planner/executor/reviewer/escalation to configured cheap/work/escalation roles; these are research mappings, not executed delegation. Every route returns `execution_confirmed=false`; verify a live client separately. Use the [measurement contract](../METRICS.md) for proposal history and explicit restore.

## Optional decision record

~~~json
{"level":2,"role":"work","effort":"medium","mode":"standard","tier":"standard","independent_review":false,"confidence":null,"reason":"Substantive engineering with targeted verification."}
~~~

Map roles through the actual provider configuration. This JSON is not an API request and does not prove execution. Persist only meaningful routing decisions/capability changes.
