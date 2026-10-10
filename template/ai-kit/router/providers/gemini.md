# Gemini provider controls (pending verification)

Load only with a routing/runtime task. [gemini.json](gemini.json) is a pending scaffold: it links the existing Gemini CLI adapter to the router but declares no active model IDs, because current Gemini model IDs, reasoning controls, and tiers were not verified against primary documentation at the time of this release.

- Fill the cheap/work/escalation `model` values, set `verification_status` to `verified`, and add a `verified_documentation_date` after reading the current [Gemini API models](https://ai.google.dev/gemini-api/docs/models) documentation.
- Verify reasoning/effort controls and any free versus paid tier boundary before routing. Do not copy OpenAI or Anthropic request fields; Gemini controls are provider-specific.
- Until verified, `route` and `configure` skip this provider rather than emit an unverified model ID.

No model-switching runtime or API credentials are installed by this distribution.
