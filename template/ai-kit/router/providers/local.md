# Self-hosted (local) provider controls

Load only with a routing/runtime task. [local.json](local.json) declares the local role ladder, but no model IDs: self-hosted models are supplied by the project owner in [selection.json](../selection.json) under `local_models`, because a shared kit cannot know which local models are actually installed.

- The local tier maps to any self-hosted/Ollama-compatible runtime. `local_models.cheap/work/escalation` hold the installed model IDs; a role left `null` falls back to the default provider or is reported unresolved.
- Reasoning and effort controls depend on the runtime and model. Treat `supported_efforts` as the offered range, not a promise: confirm that the selected model actually accepts the requested effort and reasoning mode.
- Local models never need a `verified_documentation_date`; their freshness and licensing are the project owner's responsibility, verified against the installed runtime.
- No local runtime or model files are installed by this distribution. Credentials and endpoints stay out of files and logs.

Sources: [Ollama library](https://ollama.com/library). Configuration guidance, not a claim about any installed runtime.
