# Agent adapters

| Client | Entry / installation |
| --- | --- |
| Codex | Root AGENTS and source skills in .agents/skills |
| Claude Code | CLAUDE imports @AGENTS; --agent claude copies selected skills into .claude/skills |
| Kimi / Manus | Optional short entry; supply explicitly when automatic discovery is unavailable |
| Copilot | Optional .github/copilot-instructions.md pointing to Core/current context |
| Cursor | Optional .cursor/rules/ai-kit.mdc; verify native activation in the installed client |
| Aider | Optional CONVENTIONS.md; load with --read CONVENTIONS.md rather than assuming discovery |
| Gemini CLI | GEMINI.md project entry discovered at the project root |
| Windsurf | Optional .windsurf/rules/ai-kit.md; verify during the Windsurf/Devin rules transition |
| Cline | Optional .clinerules/ai-kit.md |
| Roo | Optional .roo/rules/ai-kit.md |

Existing adapters/settings are preserved or reported as conflicts. Copied Claude skills retain their three-level relative root paths; discovery must be checked in the actual client.
Private mode excludes local adapters; team mode keeps shared instruction sources visible. Personal client settings remain excluded.
Reference integrations/ guards are the reviewed source for the optional deny rules below; they are supplementary policy, not a universal command ban.

## Changing the agent selection

Repeating --agent selects the full desired list. Omitting it reuses the accepted list, or codex for a fresh installation. It is not an additive command.
If previously tracked adapters for an unselected agent still exist, preview lists exact adapter_conflicts. Apply returns 2 and preserves the accepted files, agent list, and baseline; no adapter is deleted automatically.
For codex + claude to codex + copilot, review CLAUDE.md and each listed .claude/skills file. Keep claude selected while it is in use, or preserve needed local work and manually retire the specific listed files after review. Rerun preview before applying the new selection.
Untracked unselected entry files and remaining .claude/skills produce warnings because they may still load. Review custom skills/settings separately; do not delete an entire native directory to resolve a managed-file conflict.
This version uses an explicit review conflict instead of implementing add/remove/replace commands. Client activation and unloading still require checks in the actual client.

Sources: [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), [Claude imports](https://code.claude.com/docs/en/memory), [Claude skills](https://code.claude.com/docs/en/skills), [Claude hooks](https://code.claude.com/docs/en/hooks), [Copilot instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions), [Cursor documentation](https://cursor.com/docs), [Aider conventions](https://aider.chat/docs/usage/conventions.html), [Gemini CLI configuration](https://geminicli.com/docs/get-started/configuration/), [Windsurf documentation](https://docs.windsurf.com/), [Cline rules](https://docs.cline.bot/customization/cline-rules), [Roo Code custom instructions](https://docs.roocode.com/features/custom-instructions).

## Model routing

The reference distribution ships `scripts/router.py` (offline, no credentials). `route "<task>"` prints a capability recommendation and the resolved provider/model; `configure PROJECT --apply` writes `ai-kit/router/resolved.json` and, for a selected Aider agent, a native `.aider.conf.yml` mapping the cheap/work/escalation roles to `weak_model`/`model`.
Provider availability and role overrides live in [selection.json](router/selection.json). Most clients select models in their own UI or environment rather than a shared config file; apply `resolved.json` through the client's native mechanism (for example, Claude Code environment model variables) and verify activation in the actual client.

## Optional install extras

Opt-in flags add machinery beyond the standard entries; accepted choices persist in ai-kit/settings.json and apply to later runs.

| Extra | Flag | Installed | Boundary |
| --- | --- | --- | --- |
| Session start | --with-session-start | .agents/hooks/session-start.md; with claude also .claude/settings.json wiring a SessionStart hook that feeds the file to the session | Verify hook output reaches the session in the actual client |
| Guards | --with-guards | .claude/settings.json deny rules for Git commit/push from integrations/claude-settings.deny-git.json | Supplementary enforcement, not a universal ban; test in the client. Requires the claude selection |
| Project CI | --with-ci | .github/workflows/ai-kit.yml self-contained health check (state validity, managed files, budgets, owned documents) | Team mode is the intended companion: private mode excludes installer state from Git. Pin referenced actions to reviewed SHAs |

guards/session-start client wiring requires the claude agent selection; without it only the shared hook file is installed. MCP servers stay project-specific: choose read-only servers and declare them in .mcp.json manually; no server is installed by default.
