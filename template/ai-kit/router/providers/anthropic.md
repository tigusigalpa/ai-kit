# Anthropic provider controls

Load only with a routing/runtime task. [anthropic.json](anthropic.json) is the single owner of active model IDs and default role/effort mappings.
Its documentation date is not proof of account access. Verify the current model registry, effort levels, context/output limits, prices, and retirement dates before routing.

- Roles follow the provider's guidance: start substantive work on the Opus-class model and move to Fable-class only when Opus at higher effort still falls short. The Sonnet-class model is the faster, cheaper workhorse for well-scoped steps and sub-agents; adapt the work role when speed matters more than judgment. The Haiku-class model owns the cheap role for classification, extraction, and routing.
- Effort levels run low/medium/high/xhigh/max on current models and move cost per task more than the model name. Treat max as a special tool, not a quality default: it can spend the whole output budget on thinking and return no answer. Confirm the levels each model accepts in the current registry.
- Current models use adaptive thinking with effort as the lever, set through the provider's own request field; OpenAI service tiers, reasoning modes, and sampling parameters are not Anthropic request fields and non-default values return errors.
- The newest tokenizer produces roughly 30 percent more tokens for the same text than pre-4.7 models; recount prompts and revisit output limits when switching models.
- Claude Code can select models in native subagent configuration, but these templates install no subagents or executable routing. Delegation still requires authorization and a task benefit.

Sources: [models overview](https://docs.anthropic.com/en/docs/about-claude/models/overview), [Haiku 5.5 migration guide](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide), [pricing](https://docs.anthropic.com/en/docs/about-claude/pricing), [model deprecations](https://docs.anthropic.com/en/docs/deprecations).
Configuration verified against primary documentation on 2026-10-10.
No model-switching runtime or API credentials are installed by this distribution.
