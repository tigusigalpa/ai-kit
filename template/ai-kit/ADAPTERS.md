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
| Devin (Windsurf) | --agent devin installs .devin/rules/ai-kit.md and optional scoped rules; --agent windsurf retains legacy .windsurf/rules/ paths |
| Cline | Optional .clinerules/ai-kit.md |
| Roo | Optional .roo/rules/ai-kit.md |

Existing adapters/settings are preserved or reported as conflicts. Copied Claude skills retain their three-level relative root paths; discovery must be checked in the actual client.
Devin loads both .devin/rules/ and legacy .windsurf/rules/. Add devin alongside the accepted legacy client list before explicitly retiring unchanged windsurf adapter files; preserve edited rules and review duplicates. [Current formats](https://docs.devin.ai/desktop/devin-local/customizations).
All Claude installations preserve human authorship and request an empty native attribution.commit value. Custom values conflict for review; PR attribution remains unchanged. Optional --with-claude-github adds authenticated GitHub identity checks before authorized commits, without changing installation permissions or global Git configuration.
Private mode excludes local adapters and AI client configuration folders (.agents, .claude, .codex, .cursor, .gemini, .windsurf, .devin, .roo, .clinerules, Copilot instructions, prompts, and agents); team mode keeps shared instruction sources visible. Personal client settings and AI client history remain excluded in both modes.
Reference integrations/ guards are the reviewed source for the optional ask rules below; they are supplementary confirmation, not a universal command ban.

## Changing the agent selection

Repeating --agent selects the full desired list. Omitting it reuses the accepted list, or codex for a fresh installation. It is not an additive command.
Preview reports detected_agents (existing native files such as .claude/, .cursor/, or GEMINI.md) and suggested_agents; without an explicit --agent it warns with the command that wires them. Detection is evidence of files, not of client use, and never changes the selection by itself; --interactive offers it as the default answer.
If previously tracked adapters for an unselected agent still exist, preview lists exact adapter_conflicts. Apply returns 2 and preserves the accepted files, agent list, and baseline; no adapter is deleted automatically.
For codex + claude to codex + copilot, review CLAUDE.md and each listed .claude/skills file. Keep claude selected while it is in use, or retire its unchanged owned files explicitly after review. Rerun preview before applying the new selection.
Untracked unselected entry files and remaining .claude/skills produce warnings because they may still load. Review custom skills/settings separately; do not delete an entire native directory to resolve a managed-file conflict.
Client activation and unloading still require checks in the actual client.

### Client evidence and safe retirement

`python scripts/adapters.py report --project TARGET` (or `aikit adapters report --project TARGET`) lists each client's documentation status/date/sources, selected/detected evidence, and tracked adapter paths. Documentation verification is not a native activation result; Kimi and Manus remain explicitly unverified until primary references are recorded.

To retire one client, first preview `aikit adapters retire TARGET --agent claude`, then repeat with `--apply`. The explicit command deselects that client only after it has removed its unchanged tracked adapter files. Every removed file is copied to `ai-kit/.upstream-cache/retirements/`; modified, locally accepted, or non-file paths remain conflicts and are never removed. Missing tracked paths are cleared from installer state without deleting anything. The last selected client cannot be retired, and the command does not delete untracked files, whole native directories, settings fragments, or secret-ignore blocks.

Sources: [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), [Claude imports](https://code.claude.com/docs/en/memory), [Claude skills](https://code.claude.com/docs/en/skills), [Claude hooks](https://code.claude.com/docs/en/hooks), [Copilot instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions), [Cursor documentation](https://cursor.com/docs), [Aider conventions](https://aider.chat/docs/usage/conventions.html), [Gemini CLI configuration](https://geminicli.com/docs/get-started/configuration/), [Windsurf documentation](https://docs.windsurf.com/), [Cline rules](https://docs.cline.bot/customization/cline-rules), [Roo Code custom instructions](https://docs.roocode.com/features/custom-instructions).

## Model routing

The reference distribution ships `scripts/router.py` (offline, no credentials). `route "<task>"` prints a capability recommendation and the resolved provider/model; `configure PROJECT --apply` writes `ai-kit/router/resolved.json` and, for a selected Aider agent, a native `.aider.conf.yml` mapping the cheap/work/escalation roles to `weak_model`/`model`.
Provider availability and role overrides live in [selection.json](router/selection.json). Most clients select models in their own UI or environment rather than a shared config file; apply `resolved.json` through the client's native mechanism (for example, Claude Code environment model variables) and verify activation in the actual client.

## Optional install extras

Opt-in flags add machinery beyond the standard entries; accepted choices persist in ai-kit/settings.json and apply to later runs.

| Extra | Flag | Installed | Boundary |
| --- | --- | --- | --- |
| UUID identifiers | --with-uuid | Optional public identifier policy and a short AGENTS entry | Cross-stack; no automatic code/schema changes; independent of owner/standard conventions and presets |
| Claude GitHub identity | --with-claude-github | Optional human account verification policy linked from the selected Claude entry | No login, Git config, commit or push at installation; account mismatch requires resolution before an authorized commit |
| Session start | --with-session-start | .agents/hooks/session-start.md and session-start.sh; selected Claude gets a hook with instructions, first 8000 context bytes and Git status | Needs POSIX sh/tr/head; verify actual session output; settings ownership below |
| Guards | --with-guards | Ask rules for Git commit/push in .claude/settings.json from integrations/claude-settings.git-ask.json | Confirmation, not a universal ban: Core allows an explicitly requested commit; test in the client. Requires the claude selection |
| Project CI | --with-ci | .github/workflows/ai-kit.yml self-contained health check (state validity, managed files, budgets, owned documents) | Team mode is the intended companion: private mode excludes installer state from Git. Pin referenced actions to reviewed SHAs |
| Data guards | --with-data-guards | Claude Code ask rules for rm -rf, git reset --hard, git clean, Docker prune/volume removal, and migrations of detected Laravel/Moodle modules (integrations/claude-settings.data-ask.json) | Command-prefix confirmation, not a security boundary; requires the claude selection |
| Native settings | --with-native-settings | Claude allow/secret rules and managed secret blocks in selected client ignores | Secret list plus detected stack additions; shell operators are not allowed; settings ownership below |
| Scoped rules | --with-scoped-rules | One path-scoped rule per module with stack profiles, pointing to its profiles and recorded commands | Generated managed files: rerun the installer after project.json changes; edited files become conflicts |
| Security audit | --with-security-audit | Explicit-only skill, pinned Cloudflare method and validators | [Contract](SECURITY-AUDIT.md); files only |
| Strix | --with-strix | Explicit-only skill, nine pinned upstream skills and license/provenance | [Contract](STRIX.md); no runtime installation or scan |
| Context7 | --with-context7 | Optional context7-docs skill, source/Claude copies | [Contract](CONTEXT7.md); MCP setup/authentication separate |
| Web Design | --with-web-design | Four source/Claude skills, conditional guides and missing project design documents | [Contract](WEB-DESIGN.md); no runtime, account, package or deployment setup |

Client wiring for guards, data guards, session start, and native settings requires the claude agent selection; without it only shared files are installed. MCP servers stay project-specific: choose read-only servers and declare them in .mcp.json manually; no server is installed by default.

### Optional security audit

Read the [contract](SECURITY-AUDIT.md).

### Optional Strix

Read the [contract](STRIX.md).

### Presets

--preset sets its extras on or off and may set the sharing mode; explicit --mode and --with-* flags win. The preview reports disabled extras. CI, upstream skills, Context7 and Web Design stay outside presets.

| Preset | Mode | Extras |
| --- | --- | --- |
| minimal | unchanged | none |
| solo | private | session-start, native-settings, scoped-rules |
| team | team | session-start, guards, native-settings, scoped-rules |
| strict | unchanged | session-start, guards, data-guards, native-settings, scoped-rules |

### Client settings ownership

AI-KIT owns only its own entries in the Claude Code settings file: listed permission rules and hook groups identified by their command. Private mode uses the personal .claude/settings.local.json; team mode uses the shared .claude/settings.json. Changing the mode moves only the owned entries. Other keys, rules, and hooks survive; a file is rewritten as two-space JSON only when an entry changes, after a backup. Installer state records the owned entries under managed_json, so disabling an extra removes only its entries. A file that is not a JSON object becomes a reviewed conflict whose candidate holds the AI-KIT fragment. Earlier installations that managed the whole settings.json migrate on the next run.
Allow rules in a shared settings.json apply after the workspace trust prompt. Read deny rules also block edits of the same paths, but not shell commands that open files. The hook pipes the script through tr before sh, so a CRLF checkout (Git autocrlf on Windows) still runs.

### Scoped module rules

Module facts come from ai-kit/project.json when it lists modules, otherwise from installer detection. Modules whose paths need glob escaping are skipped with a warning. The root module uses each client's always-on form.

| Client | Generated file | Scope field |
| --- | --- | --- |
| Claude Code | .claude/rules/ai-kit-MODULE.md | paths YAML list |
| Cursor | .cursor/rules/ai-kit-MODULE.mdc | globs with alwaysApply false |
| Copilot | .github/instructions/ai-kit-MODULE.instructions.md | applyTo |
| Devin (Windsurf) | .devin/rules/ai-kit-MODULE.md; legacy .windsurf/rules/ with --agent windsurf | trigger glob with globs |
| Cline | .clinerules/ai-kit-MODULE.md | paths YAML list |

Codex reads AGENTS.md only from the repository root down to its working directory, so no nested AGENTS.md is generated; start Codex in a module directory for module-local instructions. Roo, Aider, Gemini, Kimi, and Manus have no generated scoped rules. AI-KIT writes no Codex config.toml: approval and sandbox choices stay with the user.
Client ignore files remain visible in private mode, like .gitignore. Disabling native settings removes only the marked block.

Sources: [Claude memory and rules](https://code.claude.com/docs/en/memory), [Claude permissions](https://code.claude.com/docs/en/permissions), [Claude settings](https://code.claude.com/docs/en/settings), [Cursor rules](https://cursor.com/docs/context/rules), [Cursor ignore file](https://cursor.com/docs/reference/ignore-file), [Copilot support matrix](https://docs.github.com/en/copilot/reference/custom-instructions-support), [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Gemini ignore](https://geminicli.com/docs/cli/gemini-ignore/), [Aider options](https://aider.chat/docs/config/options.html), [Windsurf rules](https://docs.devin.ai/desktop/cascade/memories). Checked 2026-10-10; activation still needs a check in the actual client.
