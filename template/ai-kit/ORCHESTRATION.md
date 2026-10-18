# Optional orchestration

Load only for an explicitly requested delegation or external text task. Installation alone authorizes no execution.

## Native Codex helpers

The installer can add project-scoped aikit_explorer, aikit_worker and aikit_reviewer TOML files under .codex/agents/. Read/reconcile their model and effort against the actual Codex session's supported controls and account access before use. Model defaults derive from the canonical OpenAI provider catalogue; they are independent of offline router advice. Native helpers inherit their parent's provider, permissions and tool access. No root Codex configuration, credentials or MCP servers are changed.

The main agent owns decomposition and final acceptance. Delegate only bounded, independent work when the user/host permits it and the expected benefit exceeds coordination cost. Pass paths, exact invariants, expected output and acceptance checks; return concise evidence and uncertain cases. Helpers do not delegate further or call paid APIs. Keep independent review distinct from self-review. Native helpers use the host's billing/limits: the OpenRouter ledger does not cap subscription or Codex usage.

## OpenRouter text executor

Use the installed `aikit orchestrate` CLI. `run PROJECT --task RELATIVE_JSON` previews without network or writes. `--apply` separately authorizes sending the selected text/instructions to OpenRouter. Enable orchestration.json, select a verified exact provider/model ID and set a dedicated API key in OPENROUTER_API_KEY. Never put credentials in chats, task files, configuration, reports or logs.

The task JSON contains schema 1, opaque id, instruction and an explicit input_files list relative to PROJECT. No implicit tree scan or context upload occurs. Review every selected file for sensitive data before applying. Hidden/credential paths, linked paths, oversized input and nonregular files are refused. Model output is untrusted text; it is saved privately and never interpreted as commands, Git authorization or tool calls.

The project-wide private ledger is ai-kit/.orchestration/state.json; outputs and lock files live beside it. Both sharing modes ignore this runtime directory. Keep configuration and accepted installer state intact across upgrades.

## Budget and recovery

- Configure total USD budget, per-request USD reserve, billable request count, serialized input bytes, maximum output tokens, timeout and provider price ceilings. Provider prompt/completion prices are USD per million tokens; request is USD per request. Price ceilings filter providers; they are not a total-dollar guarantee.
- A dedicated, non-resetting OpenRouter key must have a positive limit no greater than the configured budget, include BYOK usage and enough remaining credit. Configure it yourself in the provider dashboard; AI-KIT neither creates keys nor changes limits. Do not share this key with other workloads. Provider billing enforcement is an additional boundary, not local proof of a precise invoice maximum.
- One exclusive project lock serializes apply operations. A durable reservation is recorded before each completion POST. Known billed costs include failed/malformed results. Unknown cost, timeout, interrupted reservation or cost above the reserve freezes further inference. No automatic retry, model fallback or recursive tool loop runs.
- A per-request reserve is a conservative local admission limit, not an exact pre-billing quote. An already-sent request can exceed it. Local stops cannot refund that request; use the server key cap and small input/output limits. Missing cost remains unknown, never zero. GET key probes are separate from billable inference count.
- Preserve uncertain records and stale locks. Confirm that the owning process stopped before removing only its lock. Inspect provider billing/generation evidence before reconciling accounting; never erase state or change unknown costs to zero to resume. For an uncertain attempt with a known generation ID, `reconcile PROJECT --task-id ID` previews; --apply reads that generation's billing without repeating inference. A timeout without a generation ID needs separate operator investigation; it cannot be automatically settled.

`status PROJECT` is offline and reports all attempts, known cost, incomplete coverage and cost per explicitly accepted result. `review PROJECT --task-id ID --outcome accepted|rejected` previews; --apply records the operator's decision. Only fully accounted completed results can be accepted. Review is an assertion by the reviewer, not automatic correctness verification. Native planner/reviewer costs must be accounted separately before claiming end-to-end savings. Real trials, automatic policy learning and cross-client orchestration are separate.
