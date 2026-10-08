# OpenAI provider controls

Load only with a routing/runtime task. [openai.json](openai.json) is the single owner of active model IDs and default role/effort mappings.
Its documentation date is not proof of account access. Verify current runtime registry, endpoint, region, tool support, efforts, modes, context/output limits, prices, and actual served tier.

- Prefer Responses for reasoning-enabled function/tool workflows. Some Chat Completions model combinations lack tool calling or require none effort.
- reasoning.effort and reasoning.mode are separate controls. Default standard; pro adds billed work and needs a supported endpoint/model and justified expected benefit.
- Policy standard tier maps to service_tier default; auto follows project settings. Flex/fast/priority/ultrafast availability varies by model/region/account. Observe the actual served tier.
- For applicable models, check the large-input pricing boundary against current model documentation before a large call; do not put a fixed pricing threshold into universal policy.
- max_output_tokens includes reasoning; a short visible reply can require a larger reasoning allowance.
- Verify prompt caching eligibility and cached-token observations; a stable prefix alone is not a cache hit.

Sources: [model catalog](https://developers.openai.com/api/docs/models), [reasoning](https://developers.openai.com/api/docs/guides/reasoning), [Responses create](https://developers.openai.com/api/reference/java/resources/responses/methods/create), [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
No model-switching runtime or API credentials are installed by this distribution.
