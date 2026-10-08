# Agent adapters

One Core with short entry points. An adapter points to `AGENTS.md`, `PROJECT_CONTEXT.md`, and relevant rules; it does not keep a separate copy of agreements.

| Environment | Entry point | Integration |
| --- | --- | --- |
| Codex | `AGENTS.md` and `.agents/skills/` | Repository instructions and skills are available when the project is open. |
| ChatGPT without file access | `BOOTSTRAP_PROMPT.md` and attached kit files | Provide the files or their contents in the chat; verify the agent has read them. |
| Claude | `CLAUDE.md` | Thin adapter; model selection is described in `MODELS.md`. |
| Kimi / Manus | `KIMI.md` / `MANUS.md` | Supply the corresponding adapter to the environment; automatic reading depends on the product. |

If an environment uses its own instruction format, create a short project adapter with links to the Core. Do not copy the entire Core into every entry point. When instructions conflict, explicit user requests and more specific project instructions take precedence.
