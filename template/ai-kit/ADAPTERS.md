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
Reference integrations/ guards are the reviewed source for the optional ask rules below; they are supplementary confirmation, not a universal command ban.

## Changing the agent selection

Repeating --agent selects the full desired list. Omitting it reuses the accepted list, or codex for a fresh installation. It is not an additive command.
Preview reports detected_agents (existing native files such as .claude/, .cursor/, or GEMINI.md) and suggested_agents; without an explicit --agent it warns with the command that wires them. Detection is evidence of files, not of client use, and never changes the selection by itself; --interactive offers it as the default answer.
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
| Session start | --with-session-start | .agents/hooks/session-start.md and session-start.sh; with claude also a SessionStart hook in .claude/settings.json that adds the instructions, current PROJECT_CONTEXT (first 8000 bytes), and Git status to the session | Needs POSIX sh, tr, and head (Git Bash on Windows); verify hook output reaches the session in the actual client |
| Guards | --with-guards | Ask rules for Git commit/push in .claude/settings.json from integrations/claude-settings.git-ask.json | Confirmation, not a universal ban: Core allows an explicitly requested commit; test in the client. Requires the claude selection |
| Project CI | --with-ci | .github/workflows/ai-kit.yml self-contained health check (state validity, managed files, budgets, owned documents) | Team mode is the intended companion: private mode excludes installer state from Git. Pin referenced actions to reviewed SHAs |

guards/session-start client wiring requires the claude agent selection; without it only the shared hook files are installed. MCP servers stay project-specific: choose read-only servers and declare them in .mcp.json manually; no server is installed by default.

### Client settings ownership

AI-KIT owns only its own entries in .claude/settings.json: listed permission rules and hook groups identified by their command. Other keys, rules, and hooks survive; the file is rewritten as two-space JSON only when an entry changes, after a backup. Installer state records the owned entries under managed_json, so disabling an extra (for example "guards": false in settings) removes only its entries. A file that is not a JSON object becomes a reviewed conflict whose candidate holds the AI-KIT fragment. Earlier installations that managed the whole file migrate on the next run: their Git deny rules and cat hook become the ask rules and the current hook.
The hook pipes the script through tr before sh, so a CRLF checkout (Git autocrlf on Windows) still runs.
