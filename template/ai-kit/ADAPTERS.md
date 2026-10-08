# Agent adapters

| Client | Entry / installation |
| --- | --- |
| Codex | Root AGENTS and source skills in .agents/skills |
| Claude Code | CLAUDE imports @AGENTS; --agent claude copies selected skills into .claude/skills |
| Kimi / Manus | Optional short entry; supply explicitly when automatic discovery is unavailable |
| Copilot | Optional .github/copilot-instructions.md pointing to Core/current context |
| Cursor | Optional .cursor/rules/ai-kit.mdc; verify native activation in the installed client |
| Aider | Optional CONVENTIONS.md; load with --read CONVENTIONS.md rather than assuming discovery |

Existing adapters/settings are preserved or reported as conflicts. Copied Claude skills retain their three-level relative root paths; discovery must be checked in the actual client.
Private mode excludes local adapters; team mode keeps shared instruction sources visible. Personal client settings remain excluded.
Optional guards in the reference integrations/ are supplemental, not a universal command ban. They are not installed automatically.

## Changing the agent selection

Repeating --agent selects the full desired list. Omitting it reuses the accepted list, or codex for a fresh installation. It is not an additive command.
If previously tracked adapters for an unselected agent still exist, preview lists exact adapter_conflicts. Apply returns 2 and preserves the accepted files, agent list, and baseline; no adapter is deleted automatically.
For codex + claude to codex + copilot, review CLAUDE.md and each listed .claude/skills file. Keep claude selected while it is in use, or preserve needed local work and manually retire the specific listed files after review. Rerun preview before applying the new selection.
Untracked unselected entry files and remaining .claude/skills produce warnings because they may still load. Review custom skills/settings separately; do not delete an entire native directory to resolve a managed-file conflict.
This version uses an explicit review conflict instead of implementing add/remove/replace commands. Client activation and unloading still require checks in the actual client.

Sources: [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), [Claude imports](https://code.claude.com/docs/en/memory), [Claude skills](https://code.claude.com/docs/en/skills), [Copilot instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions), [Cursor documentation](https://cursor.com/docs), [Aider conventions](https://aider.chat/docs/usage/conventions.html).
