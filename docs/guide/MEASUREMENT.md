# Measure, recommend and select context

![Measure, recommend and select context](https://i.postimg.cc/RZY8THS9/10-measure-recommend-select-context.jpg)

These helpers are offline and opt-in. They recommend and measure; they do not switch models for you, send prompts or claim savings that were not measured.

- `aikit benchmark run TARGET --pack PRIVATE_PACK`: isolated, resumable A/B/C trials through a reviewed worker, configurable kit arms and private reports. Fixed models, actual telemetry and semantic review underpin comparisons. [Contract](../BENCHMARK.md).
- `aikit route "task" --project TARGET --mode adaptive`: recommendations from sufficient comparable cost/quality history; explicit pins win. `metrics compare|stacks|propose|restore` analyzes without automatic selection changes. [Policy](../../template/ai-kit/router/POLICY.md#modes-pins-and-optimization-profiles).
- `aikit context select TARGET --path api --budget 32000`: module rules, duplicate detection and byte accounting; critical requirements survive budgets. [Development stages](../DEVELOPMENT_PLAN.md).

From a source checkout, prefix the same commands with `python aikit_cli.py` instead of `aikit`.

## Adaptive model routing

The [routing policy](../../template/ai-kit/router/POLICY.md) maps every task to a capability level and recommends a model role and reasoning effort for it. It is a recommendation; no cost savings are claimed.

| Level | Task | Role / effort |
| --- | --- | --- |
| 0-1 | Classification, narrow mechanical edits | cheap / none or low |
| 2 | Substantive engineering | work / medium |
| 3-5 | Hard debugging, concurrency, distributed or sensitive correctness | work / high to max |
| 6 | Diagnosed capability shortfall | escalation |

Provider configurations map roles to OpenAI, Anthropic, Kimi, and Gemini models, or your own local/Ollama models. The offline helper understands English and Russian task descriptions and explains its choice:

~~~sh
python scripts/router.py route "debug a race condition in the queue worker"
~~~

The installed CLI exposes the same helper as `aikit route "TASK"`. `router.py configure` writes the resolved role mapping and a native Aider model file; `router.py providers` lists each provider's tier, status, and sources. The kit never fakes a model switch: when a client offers no switching control, you get a recommendation.

## Local measurements

`scripts/metrics.py` (`aikit metrics`) records supplied attempt/token/cost evidence and analyzes provider results. There is no automatic telemetry, and the journal stores no prompts, credentials or API calls. Evaluation checks opaque pair coverage. [Metrics contract](../../template/ai-kit/METRICS.md).

## Select context for a task

`aikit context select` reports selected paths, hashes and measured bytes, not an assembled model prompt or an API call. The budget is bytes, not model tokens; critical rules and ADRs can exceed it. Design workflows add their own documents when Web Design is enabled; see [Select design context](WEB_DESIGN.md#select-design-context-without-loading-every-tool). Sending selected context to an API is covered in [Working with OpenRouter](OPENROUTER.md).

## Client documentation evidence

`aikit adapters report --project TARGET` (or `python scripts/adapters.py report --project TARGET`) lists each client's documentation status/date/sources, selected/detected evidence, and tracked adapter paths. Documentation verification is not a native activation result; Kimi and Manus remain explicitly unverified. [Adapter details](../../template/ai-kit/ADAPTERS.md#client-evidence-and-safe-retirement).
