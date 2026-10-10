# ADR-0005: Key-level client settings ownership and confirmation guards

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

The session-start and guards extras generated .claude/settings.json as one installer-managed file. Any existing project settings file became a conflict, and later user edits looked like local adaptations. The guards denied Git commit/push, although Core allows these operations on an explicit user request, so an authorized commit was blocked. The session-start hook printed an instruction to read PROJECT_CONTEXT through a relative cat command, costing an extra read every session.

## Options

- Keep whole-file ownership and ask users to merge candidates by hand.
- Own a marked block, as in .gitignore; JSON has no comments, so a block cannot be delimited.
- Own individual entries: listed permission rules and hook groups identified by their command.

## Decision

Own individual entries and record them in installer state under managed_json. Each run removes stale owned entries, adds missing ones, and preserves all other content; a file that is not a JSON object becomes a reviewed conflict with the AI-KIT fragment as candidate. Earlier whole-file installations migrate on the next run.

Guards use permissions.ask for Git commit/push. The session-start hook runs a managed script via $CLAUDE_PROJECT_DIR, piped through tr so CRLF checkouts still run, and prints the instructions, current PROJECT_CONTEXT (capped), and Git status.

The preview also reports clients detected from existing native files, declared as detect markers in the agent registry, without changing the selection.

## Consequences

Existing client settings survive installation and upgrades; the file is reformatted as two-space JSON only when an owned entry changes, after a backup. Guards now need user confirmation rather than blocking, which matches Core but is weaker against unattended runs. The hook depends on POSIX sh, tr, and head in the client's hook shell.

## Verification

Merge, migration, conflict, disable, doctor, detection, and hook-execution regressions run with the installer suites. [Results](../IMPLEMENTATION.md#client-settings-and-detection-verification).
