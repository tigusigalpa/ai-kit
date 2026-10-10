# ADR-0007: Generated client configuration, scoped module rules, presets, and workflow skills

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

After installation, agents still had to remember to open the right stack profile, asked permission for every routine check, could read secret files, and depended on a pasted bootstrap prompt. The installer already knew module paths, profiles, and commands (project.json) and owned entries in client settings (ADR 0005), but turned none of it into native client configuration. Optional machinery needed several flags to assemble.

## Options

- Keep instructions only and document manual client setup.
- Generate one always-on rule per client listing all modules.
- Generate per-module native configuration from project.json through each client's documented mechanism, opt-in, with presets for common combinations.

## Decision

Generate opt-in configuration from project.json (falling back to detection):

- native-settings: Claude Code allow rules for recorded single-command checks, Read deny rules for secrets from one gitignore-style list plus detected stacks, and a marked secret block in Cursor, Aider, and Gemini ignore files. Private mode writes the personal .claude/settings.local.json; team mode writes the shared .claude/settings.json; owned entries move with the mode.
- scoped-rules: one managed rule per module with stack profiles for Claude Code (paths), Cursor (globs), Copilot (applyTo), Windsurf (trigger glob), and Cline (paths); the root module uses each client's always-on form.
- data-guards: ask rules before destructive file, Git, Docker, and detected migration commands.
- Presets minimal, solo, team, and strict set the managed extras and optionally the mode; explicit flags win and the preview names extras a preset turns off.
- Portable user-invoked workflow skills: ai-kit-bootstrap, ai-kit-review, and ai-kit-sync-context.

Codex receives no nested AGENTS.md, because it reads AGENTS.md only from the repository root to its working directory, and no config.toml, because approval and sandbox choices belong to the user. Skills use only name and description so Codex and Gemini read the same files; Claude-only invocation fields are not added.

## Consequences

Routine checks stop prompting in Claude Code, secret reads are refused by supporting clients, and module profiles attach where those files are touched. Generated files and entries follow project.json on the next installer run; edited generated rules become conflicts. Prefix permission rules and ignore files are not security boundaries: shell commands can still read files. Disabling an extra removes owned settings entries and ignore blocks but leaves generated rule files for review.

## Verification

Regressions cover private/team settings files, mode switches, migration from shared to local entries, unsafe commands, project.json precedence, ignore blocks, data guards, every rule format, root modules, path skipping, slug collisions, retirement, presets, the CLI, and workflow skills. [Results](../V0_6_4.md).
