# Gemini provider controls

Load only with a routing/runtime task. [gemini.json](gemini.json) owns the active role-to-model mapping; model IDs were read from the current [Gemini API models](https://ai.google.dev/gemini-api/docs/models) documentation on 2026-10-10.

- Roles follow the current lineup: the Flash-Lite class owns the cheap role for high-throughput classification and extraction, the Flash class owns the work role for agentic coding and software engineering, and the Pro class (preview) owns escalation.
- Reasoning runs through Gemini's thinking control, not OpenAI effort levels. Confirm the exact thinking field names and supported levels (low/high) against the [thinking](https://ai.google.dev/gemini-api/docs/thinking) documentation before passing an effort value; without that confirmation the router treats effort as unknown and recommends the model default.
- The Pro class is a preview model: confirm its rate limits and availability in your region/plan before relying on it for escalation.
- OpenAI and Anthropic request fields are not portable; pass Gemini controls through the provider's own request schema and report unsupported controls instead of forwarding them.

Sources: [models overview](https://ai.google.dev/gemini-api/docs/models), [thinking](https://ai.google.dev/gemini-api/docs/thinking). No model-switching runtime or API credentials are installed by this distribution.
