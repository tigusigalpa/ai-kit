# Kimi provider controls

Load only with a routing/runtime task. [kimi.json](kimi.json) is the single owner of active model IDs and default role/effort mappings.
Its documentation date is not proof of account access. Verify the current model list, reasoning controls, context limits, prices, and retirement status before routing.

- Roles map to the provider's current lineup: the K2.6-class model for cheap high-volume steps, the K2.7 Code model for agentic coding work, and the K3-class model for escalation.
- K3 thinking cannot be disabled; its reasoning effort accepts low/high/max and defaults to max, so set it deliberately or trivial calls pay maximum reasoning. The cheaper K2 models do not reason by default; enable thinking explicitly where the client supports it.
- The flagship has no batch tier; bulk K2 work can use the batch API at a discount. The coding assistant uses a bracketed context alias that differs from the plain API model name, and sending the alias to the chat-completions endpoint fails.
- OpenAI request fields are not portable: pass provider extensions through the SDK's extra body and report unsupported controls instead of forwarding them. Do not claim automatic routing from a KIMI.md adapter.

Sources: [Kimi platform documentation](https://platform.kimi.ai/docs), [model inference pricing](https://platform.kimi.ai/docs/pricing).
Configuration cross-checked against current online documentation on 2026-10-10.
No model-switching runtime or API credentials are installed by this distribution.
