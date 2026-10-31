# ADR 0018: Read-only MCP report and a downgrade guard

Status: accepted for code, local tests and Docker smoke; hosted release runs are separate.

## Context

The installed MCP posture asks agents and owners to review every configured server, but nothing listed what a project actually configures. Project MCP files differ per client (`mcpServers`, `servers`, `[mcp_servers.<name>]`, transport inferred from `command`, `url`, `httpUrl` or an explicit type) and often hold credentials, so a naive dump would copy secrets into terminals, logs and chats.

Upgrades were safe in one direction only. Doctor stated that versions differed without saying what to run, and an older CLI applied over a newer installation silently replaced newer managed files with older ones, for example after a teammate upgraded first.

## Decision

- `aikit mcp report TARGET` reads only the documented project files of Claude Code, Cursor, VS Code/Copilot, Gemini CLI, Codex, Roo and Kimi Code (formats checked against vendor documentation on 2026-10-30). It reports transport, command, sanitized arguments, URL origin, variable names, references, helper commands, approval and tool settings, and Git tracking. Literal values are shown as hidden; only values built from variable references are printed. Warnings cover literal credentials, inline client secrets, credentials in URLs, plain HTTP to remote hosts, password inputs with defaults and auto-approval. It starts, contacts and authorizes nothing and reads no user-level files.
- JSON files are read as JSONC. Codex TOML uses `tomllib`; on Python 3.10 the report lists server names and asks for manual review instead of shipping a TOML parser.
- The installer compares the recorded `accepted_version` with its own VERSION. A downgrade is previewed with a warning and refused on apply, including `doctor --fix --apply`, unless `--allow-downgrade` is passed. Doctor names the upgrade commands when the CLI is newer and warns when it is older.

## Consequences

MCP review starts from an inventory instead of manual file reading, without copying secrets; argument redaction is heuristic, so the report states what it hides and keeps values out rather than in. Clients without project files (Windsurf, Cline) stay outside its scope. A team member with an older CLI must upgrade before applying; deliberate downgrades remain possible with an explicit, unsaved flag. Non-release version strings are not compared and behave as before.
