# Optional orchestration

**Introduced in v1.4.4.** Native Codex helpers and the bounded OpenRouter text executor are optional. Installation performs no API calls, creates no credentials, changes no global Codex configuration and launches no agents. Use a Python package or image release from v1.4.4 on, or a reviewed source checkout; [1.4.5 publication status](../V1_4_5.md).

## Enable the module in an existing project

Use a CLI from v1.4.4 or later. Preview against the same application path and retain the existing client selection:

```powershell
aikit install "C:\Projects\my-app" --with-orchestration
aikit install "C:\Projects\my-app" --with-orchestration --apply --check
```

For a first Codex installation, add `--agent codex` to both commands. Existing selected agents, settings and other enabled modules persist. Orchestration is outside all presets, including strict. Its configuration starts with `enabled: false` and `model: null`; API execution needs separate configuration and `--apply`.

The installer adds:

| File | Ownership and purpose |
| --- | --- |
| `ai-kit/ORCHESTRATION.md` | Managed execution, authorization, accounting and recovery rules. |
| `ai-kit/orchestration.json` | Created once, then preserved as project configuration. |
| `.codex/agents/aikit_explorer.toml` | Read-only evidence gathering, only when Codex is selected. |
| `.codex/agents/aikit_worker.toml` | Narrow implementation/mechanical work, only for Codex. |
| `.codex/agents/aikit_reviewer.toml` | Independent read-only review, only for Codex. |
| `ai-kit/.orchestration/` | Private runtime state, outputs and exclusive lock; created only when executing. |

Private mode ignores helpers and configuration; team mode can share those instructions while runtime state remains ignored. Ignore rules do not remove previously tracked files. Orchestration runtime state is excluded from the published packages and Docker image. Existing helper edits become normal upgrade conflicts; existing `.codex/config.toml` and unrelated helper files are preserved. Deselecting Codex requires normal adapter review/retirement.

## Delegate bounded work to Codex helpers

The native helper model/effort defaults are rendered from AI-KIT's canonical OpenAI catalogue: explorer and worker use the cheap role, reviewer the work role. Verify availability in your actual Codex session and edit/accept local adaptations when needed. These files inherit the parent provider, permissions and tools; they do not connect OpenRouter or change the parent's active model. Start a fresh session if required for discovery. [Official custom-agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Example task for the main agent:

> Inspect the parser change. Delegate read-only path discovery to aikit_explorer. Give aikit_worker only the identified parser and its regression tests, with exact acceptance criteria. Ask aikit_reviewer to review the resulting diff independently. Do not delegate recursively. Return the actual checks and unresolved risks.

Use the helpers only with explicit task/host authorization. Define file scope and expected evidence before delegation; keep large logs out of the parent thread. A simple task can stay with one agent. Native helpers consume their host's subscription/API limits: the OpenRouter budget below does not govern their spend. End-to-end savings require all planning, helper and review costs, including failed work.

## Configure the OpenRouter executor

Edit `ai-kit/orchestration.json` deliberately. Example configuration, using a placeholder that you must replace with a verified available text-model ID:

```json
{
  "schema": 1,
  "enabled": true,
  "model": "provider/model-id",
  "budget_usd": "1.00",
  "request_reserve_usd": "0.10",
  "max_requests": 10,
  "max_input_bytes": 16000,
  "max_output_tokens": 1024,
  "timeout_seconds": 60,
  "max_price": {"prompt": "1", "completion": "3", "request": "0"}
}
```

Select an exact model, not an automatic/free router alias. Confirm that the model supports text completions and the requested output limit. Price ceilings are USD per **million** prompt/completion tokens and USD per request. They filter providers; they are not a pre-billing quote. Set the request ceiling to zero to exclude per-request-priced routes. The runner disables model/provider fallbacks and streaming, sends no tools/plugins, and has no recursive agent or automatic retry loop. [Provider price filters](https://openrouter.ai/docs/guides/routing/provider-selection#max-price).

Create a **dedicated OpenRouter key** in the provider dashboard. Give it a positive, non-resetting spending limit no greater than `budget_usd`, include BYOK usage in that limit, and reserve it exclusively for this workflow. The runner verifies these settings using `GET /api/v1/key` before inference. It does not create keys or raise their limits. The key must have at least one request reserve remaining. Configure OPENROUTER_API_KEY through your approved secret manager or process environment; never put its value in a prompt, tracked file, task JSON or command-line argument. The CLI never prints it. [Key and budget limits](https://openrouter.ai/docs/api/reference/limits).

The dollar budget is lifetime accounting for this project's retained ledger, not an automatically resetting daily allowance. Local reservations prevent admitting more work than the remaining recorded budget. An already-sent request can exceed its reserve; server-side key caps provide an additional boundary with the provider's billing semantics. A local timeout does not prove cancellation or zero spend. Keep reserves conservative and input/output limits small.

## Prepare a task and review the outgoing scope

Create a UTF-8 task file inside the application, for example `tasks/classify.json`:

```json
{
  "schema": 1,
  "id": "comments-001",
  "instruction": "Classify each supplied comment using bug, feature or other. Preserve each original id. Mark uncertain rows needs_review. Return JSON text and do not omit rows.",
  "input_files": ["data/comments-sample.txt"]
}
```

The input list is explicit and project-relative. There is no implicit repository traversal or upload of project rules/history. Review the instruction and every selected file before permitting data to leave the machine. Hidden/credential paths, linked paths, traversal, nonregular files and oversized serialized messages are refused. Filename checks cannot recognize secrets embedded in ordinary text. Only selected text reaches `https://openrouter.ai/api/v1/chat/completions`; model output is treated as untrusted data.

```powershell
# Preview: no key needed, no writes and no network.
aikit orchestrate run "C:\Projects\my-app" --task tasks/classify.json

# Execute only after reviewing the selected content and configured budget.
aikit orchestrate run "C:\Projects\my-app" --task tasks/classify.json --apply

# Read local accounting without network.
aikit orchestrate status "C:\Projects\my-app"
```

Preview reports the model, selected paths, serialized message bytes, request/config fingerprint, reserve and output path. An exact completed rerun uses its retained result; changing inputs/configuration while reusing the task ID refuses. Use a new opaque ID for a deliberately new task. A changed/deleted prior output refuses instead of silently rebilling.

## Review results and account for costs

Each completed response is stored under `ai-kit/.orchestration/outputs/<id>.json`; it is never executed or applied to application code. A main agent or human must check coverage, invariants and uncertain cases. Passing transport validation is not semantic correctness.

```powershell
# Preview an explicit acceptance decision after inspecting the result.
aikit orchestrate review "C:\Projects\my-app" --task-id comments-001 --outcome accepted

aikit orchestrate review "C:\Projects\my-app" --task-id comments-001 --outcome accepted --apply
```

Use `rejected` for a reviewed incorrect result. Acceptance binds to the original output hash and requires completed accounting. Status reports requested/served model, generation ID, input/output/cached/reasoning tokens when available, duration, billed USD, review state, incomplete accounting and cost per accepted result. All attempts contribute to spend, including failed and rejected results. Prompt text, input files, raw provider errors and credentials are absent from the accounting ledger; private output files still contain the model's text and need normal access controls. On Windows, filesystem ACLs control access; private modes are not a sandbox.

Observed `usage.cost` is recorded directly; no price-based token estimate is substituted. Missing token/cost fields remain unknown. Native Codex planning/review costs and manual review time remain separate; this ledger alone cannot establish end-to-end savings. The existing benchmark protocol still needs a reviewed worker for a controlled experiment; this text executor does not silently implement `aikit-worker-v1` or feed mixed-model evidence into adaptive learning. [Usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting).

## Failures, concurrency and recovery

- An exclusive project lock serializes applies. A reservation is saved **before** each completion POST; a crash cannot make a potentially billed attempt disappear.
- Unknown cost, a pending reservation, a timeout or a cost above the reserve blocks further inference. No automatic retry occurs, including after 429/5xx errors. Known charges for malformed/truncated/wrong-model/tool-call responses are retained.
- If a generation ID is known, preview then apply a billing read-back. This never reruns inference:

```powershell
aikit orchestrate reconcile "C:\Projects\my-app" --task-id comments-001
aikit orchestrate reconcile "C:\Projects\my-app" --task-id comments-001 --apply
```

- Reconciliation uses `GET /api/v1/generation?id=...`, requires the same generation ID and actual `total_cost`, then settles a valid retained result or a failed attempt. Unavailable billing stays unresolved.
- A timeout without a generation ID needs operator investigation in OpenRouter billing. Preserve the state; do not delete it or replace unknown spend with zero. Automatic recovery for that ambiguous case is intentionally unavailable.
- A process crash can leave `run.lock`. Confirm its owner stopped before removing that lock only; pending accounting must still be resolved. Never prune a shared Docker builder or delete the project ledger to bypass a budget.

Exit codes: **0** for preview, completed work or a status report; **1** for refusal/configuration/path/network preflight failure; **2** for a failed or uncertain inference result. Status itself remains read-only even when it reports unresolved accounting.

## Python package, Docker and verification boundaries

The published distributions since v1.4.4, including v1.4.5, include the executor, templates, helper sources and tests without new runtime dependencies; [registry status](../V1_4_5.md). Earlier artifacts remain intact. Offline preview/status need no network; real `run --apply` needs outbound HTTPS, an intentionally supplied key and a writable project mount for reservations/results. No Docker socket or privileged mode is needed.

Code and tests use synthetic inputs and substituted provider responses. Real API calls, native client activation, account availability and measured savings remain separate. [Maintainer verification and limitations](../ORCHESTRATION.md).
