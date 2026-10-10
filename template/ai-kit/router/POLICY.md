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

Active role defaults: [openai.json](providers/openai.json), [anthropic.json](providers/anthropic.json), and [kimi.json](providers/kimi.json), interpreted by their provider references.
Registry/configuration plus current primary docs establish capabilities; model names alone do not.
Unavailable switching means a recommendation, not a claim of execution. Respect explicit model, cost, and latency choices.

## Optional decision record

~~~json
{"level":2,"role":"work","effort":"medium","mode":"standard","tier":"standard","independent_review":false,"confidence":null,"reason":"Substantive engineering with targeted verification."}
~~~

Map roles through the actual provider configuration. This JSON is not an API request and does not prove execution. Persist only meaningful routing decisions/capability changes.
