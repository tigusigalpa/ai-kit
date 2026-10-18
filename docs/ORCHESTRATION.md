# Optional orchestration implementation

The [user guide](../README.md#optional-orchestration) owns launch examples; [installed contract](../template/ai-kit/ORCHESTRATION.md) owns execution policy. VERSION 1.4.4 is release preparation, not a publication claim.

## Boundaries

The installer adds an independent persistent orchestration extra, outside presets. Configuration is created once; managed instructions and rendered Codex helpers retain normal backup/conflict handling. Helpers are rendered from canonical OpenAI catalogue roles, inherit the parent provider/permissions and require actual client discovery. No global Codex configuration, new credential, tool server or runtime is installed.

The standard-library executor has a fixed HTTPS destination, non-streaming text requests, explicit model and provider price filters, bounded input/output/response/timeout, no redirects, no fallback and no automatic retries. Task files explicitly select project-relative inputs. Responses never become executable tools or instructions. Credentials are read only from OPENROUTER_API_KEY, never journaled or printed. Provider errors are suppressed to avoid echoing secrets or prompts.

A dedicated capped, non-resetting key including BYOK must pass the current-key preflight. Local project-wide accounting serializes apply operations with an exclusive lock, reserves before POST, persists pending attempts across crashes and freezes uncertain billing or reserve overruns. Cost is observed usage.cost, not a quote. The server key cap and local reservation have different semantics: an already-sent request can overrun its reserve. No claim of precise pre-billing cost or cancellation is made.

Known generation IDs support explicit billing reconciliation without inference replay. Idempotency binds task/config/input hashes; output acceptance binds original output bytes. Review remains explicit; failed/rejected attempts still contribute to total cost. Native planner/helper/reviewer costs are outside this ledger and must be measured separately for end-to-end claims. Mixed-model results do not silently enter single-model adaptive learning or the benchmark protocol.

Private runtime state is ignored in both modes and excluded from source archives, wheel and Docker context. Application code, unrelated native configuration, private memory and project documents stay under existing ownership rules. Runtime filesystem access is not an adversarial process sandbox; do not concurrently mutate project ancestors during execution.

## Verification

Verified locally on 2026-10-18, using synthetic data and substituted provider responses:

- Full packaged Linux/Python 3.13.16 discovery on the final non-root, offline/read-only image: **392 tests in 30.770 seconds; 390 passed, two Windows-junction skips**.
- Native Windows/Python 3.12.14 orchestration tests: **24 tests in 17.480 seconds; 22 passed**, with symlink privilege and POSIX-only checks skipped. The full native Windows suite was not repeated; full-suite evidence here is Linux.
- Regression coverage includes disabled/default absence, independent persistent opt-in, settings/private-file preservation, local helper conflicts and retirement, valid TOML, no writes/network in preview, fixed endpoint/no redirects, request/token/byte/time bounds, key caps, budget/count exhaustion, durable pending reservations, lock refusal, uncertain billing, interrupted work, model/tool/truncation failures, idempotency, stale result review, generation reconciliation and temporary-file collision preservation.
- The wheel and sdist built in an isolated source copy with synthetic privacy probes. Archive metadata/licenses/resources/privacy checks and strict Twine passed; the wheel code matches the reviewed source. Fresh offline Windows wheel installation passed version/CLI/kit checks, native-helper installation, orchestration preview/status and existing optional modules/dialogue commands.
- Docker smoke on the final image passed offline/read-only reports, installed helpers/all optional modules, orchestration preview/status, preserved files, refusal and stable reruns, SIGTERM, and the actual ignore engine including private orchestration state. Changed packaged resource hashes match source; root local maintainer files are absent and template counterparts present.
- Upgrades from the actual v1.4.3 Git archive passed in private/team modes: README, project facts, MCP configuration, design brief, private dialogue memory and custom settings survived; orchestration starts disabled; doctor reports 1.4.4 without errors and reruns are stable.

Real OpenRouter requests, account/model availability, native Codex activation, measured savings, hosted CI, macOS and Kubernetes deployment remain unverified. Tests created no Docker volumes; disposable containers were removed. Shared cache ownership is unknown, so no shared pruning was performed. Build binaries, raw logs, image identities and upgrade fixtures remain outside the checkout. These descriptive receipts follow the tested package/image snapshot; runtime sources are unchanged.

## Primary references

- [Codex standalone agent files](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [OpenRouter completion API](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion)
- [Provider max_price filters](https://openrouter.ai/docs/guides/routing/provider-selection#max-price)
- [Key and credit limits](https://openrouter.ai/docs/api/reference/limits)
- [Observed usage/cost](https://openrouter.ai/docs/cookbook/administration/usage-accounting)
- [Generation billing lookup](https://openrouter.ai/docs/api/api-reference/generations/get-generation)
