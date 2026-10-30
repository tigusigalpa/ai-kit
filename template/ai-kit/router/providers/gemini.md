# Gemini provider controls

Load only with a routing/runtime task. [gemini.json](gemini.json) owns the active role-to-model mapping and thinking levels; model IDs and levels were read from the current [Gemini API models](https://ai.google.dev/gemini-api/docs/models) and [thinking](https://ai.google.dev/gemini-api/docs/thinking) documentation on 2026-10-30.

- Roles follow the current lineup: the Flash-Lite class owns the cheap role for high-throughput classification and extraction, the Flash class owns the work role for agentic coding and software engineering, and the Pro class (preview) owns escalation.
- Reasoning runs through Gemini's `thinking_level` (in the Interactions API `generation_config`), not OpenAI effort levels. Supported levels differ per model, so the provider record declares them per role: the cheap model accepts minimal, low, medium and high; the work and escalation models accept low, medium and high. Each role's default equals its model's documented default (minimal, medium, high).
- A routed effort outside the model's list (none, xhigh, max) falls back to the role default; for work beyond high, escalate the role instead of forwarding an unsupported level. Other request schemas such as generateContent name the control differently; confirm the field in that API's reference before translating a level.
- The Pro class is a preview model: confirm its rate limits and availability in your region/plan before relying on it for escalation.
- OpenAI and Anthropic request fields are not portable; pass Gemini controls through the provider's own request schema and report unsupported controls instead of forwarding them.

Sources: [models overview](https://ai.google.dev/gemini-api/docs/models), [thinking](https://ai.google.dev/gemini-api/docs/thinking). No model-switching runtime or API credentials are installed by this distribution.
