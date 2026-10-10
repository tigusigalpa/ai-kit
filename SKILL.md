---
name: ai-kit
description: "Use when installing, configuring, upgrading, explaining, or maintaining AI-KIT, the portable kit that gives AI coding agents verified project memory, stack rules, guardrails, model routing, and native client configuration."
---

# AI-KIT

AI-KIT is a reference distribution of instructions and an offline Python installer. It adds an AI-agent working environment to an application repository: verified project memory, stack profiles (Go, PHP, Laravel, Filament 5, Moodle, Python, frontend, libraries), a Kubernetes-ready container contract, guardrails, adaptive model routing, and native configuration for 11 AI clients.
Source: https://github.com/tigusigalpa/ai-kit. Commands below run from the repository root; read [VERSION](VERSION) instead of assuming a version.

## Two places, never mixed

- **Reference distribution** (the AI-KIT repository): `template/` holds installable project files, `templates/` the private/team ignore policies and the secret list, `scripts/` the installer and helpers, `integrations/` client entries, the agent registry (`agents.json`), and guard rules, `docs/` kit decisions and evidence.
- **Application project**: receives `AGENTS.md`, `PROJECT_CONTEXT.md`, `WIKI.md`, `CHANGELOG.md`, `docs/DECISIONS.md` and `docs/adr/`, `.agents/skills/`, and `ai-kit/` (CORE, settings.json, project.json, ENGINEERING, SECURITY, CONTAINERS, stacks, profiles, router). Never run the installer inside the distribution, and never copy kit history into a project.

## Install into a project

Requires Python 3.10+ and nothing else. Use a reviewed revision and a target path outside the distribution.

1. **Preview** (writes nothing): `python scripts/install.py TARGET --preset solo --agent codex --agent claude`. Show the user `writes`, `conflicts`, `candidates`, `adapter_conflicts`, `detected_profiles`, `detected_agents`, `suggested_agents`, and `warnings`.
2. **Apply** only after the user approves: the same command plus `--apply`; add `--check` to run the doctor. Exit codes: 0 success, 1 refusal, 2 unresolved conflicts.
3. **Bootstrap**: run `/ai-kit-bootstrap` in Claude Code or `$ai-kit-bootstrap` in Codex; other clients use `BOOTSTRAP_PROMPT.md`. Bootstrap confirms installer drafts against manifests, CI, and runnable checks, then fills `PROJECT_CONTEXT.md` and `ai-kit/project.json`.

Existing project documents and context are preserved; customized instructions become conflict candidates; adapters are never deleted.

## Options

| Option | Meaning |
| --- | --- |
| `--mode private\|team` | private ignores AI-KIT files and AI client configuration in Git; team versions shared instructions |
| `--chat-language NAME` | Chat language; project files always stay English |
| `--conventions owner\|standard` | owner applies the owner's Laravel conventions; standard follows the project |
| `--agent NAME` (repeat) | Full client list: codex, claude, cursor, copilot, gemini, windsurf, cline, roo, aider, kimi, manus |
| `--preset NAME` | minimal, solo, team, or strict (below) |
| `--with-session-start` | Claude Code SessionStart hook injecting PROJECT_CONTEXT and Git status |
| `--with-guards` | Claude Code asks before git commit/push |
| `--with-data-guards` | Asks before rm -rf, git reset --hard, git clean, Docker prune, detected migrations |
| `--with-native-settings` | Allows recorded test/lint/build commands, denies secret reads, writes client ignore blocks |
| `--with-scoped-rules` | Per-module path-scoped rules for Claude Code, Cursor, Copilot, Windsurf, Cline |
| `--with-ci` | Project health workflow (needs installer state in Git, which both modes ignore by default) |
| `--interactive`, `--check`, `--dry-run` | Guided prompts, doctor after apply, explicit preview |
| `--accept-local PATH` | Record a reviewed semantic merge of a managed file |

| Preset | Mode | Extras |
| --- | --- | --- |
| minimal | unchanged | none |
| solo | private | session-start, native-settings, scoped-rules |
| team | team | session-start, guards, native-settings, scoped-rules |
| strict | unchanged | session-start, guards, data-guards, native-settings, scoped-rules |

Presets set every extra they manage on or off; explicit flags win, and the preview names extras a preset turns off. Defaults in `ai-kit/settings.json`: English project files, Russian chat, private mode, owner conventions, codex.

## Upgrades, conflicts, and health

- Preview a newer distribution against the same target. Unchanged managed files update; locally adapted files become candidates under `ai-kit/.upstream-cache/candidates/<source-hash>/`; changed files are backed up under `ai-kit/.upstream-cache/backups/`.
- After reviewing and merging a candidate: preview, then apply, with `--accept-local PATH`.
- Deselecting a client whose tracked files remain yields `adapter_conflicts`: keep the client or retire its listed files manually.
- AI-KIT owns only its own entries in Claude Code settings (`managed_json` in installer state): `.claude/settings.local.json` in private mode, `.claude/settings.json` in team mode. Generated module rules are managed files that follow `ai-kit/project.json`; client ignore files and `.gitignore` get one marked block each.
- Health report: `python scripts/doctor.py TARGET`; `--fix` restores missing managed files and owned documents (local edits stay untouched).

## Rules an agent follows in an installed project

- **Language:** authored files, code, comments, and docs in English; chat in the configured chat language.
- **Git:** never commit or push unless the user explicitly requests that operation; commit permission does not include push. Finish with reviewable local changes.
- **Facts:** read `PROJECT_CONTEXT.md` first, verify claims against files and commands, keep unknowns explicit, and update context, the continuity skill, and WIKI when facts change. Add a CHANGELOG entry after file changes; record significant decisions as ADRs.
- **Work cycle:** plan, implement, test, review, document. Report unavailable checks as unverified, never as passed.
- **Containers:** new Dockerfiles and services are Kubernetes-ready: multi-stage pinned images, non-root, read-only root filesystem, exec-form entrypoint, SIGTERM drain, real probes, ConfigMap/Secret, PVC for state, minimal manifests. Check the Docker client and daemon before container work; clean only verified disposable test volumes and cache, only above 10 GB, never with an unscoped prune.
- **Security:** validate input, authorize on the server, keep secrets out of code, logs, and prompts; run the stack's dependency audit after dependency changes.
- **Stacks:** load only profiles confirmed for the affected module. Owner Laravel conventions: no database foreign keys, internal id plus public UUID, Policy, Factory, and Seeder per model, one table per migration, Filament 5+ for new panels.
- **Routing:** capability ladder 0-6 maps to cheap, work, and escalation roles with an effort level. A routing result is a recommendation; never claim a model switch the client did not perform.

## Model routing helper

- `python scripts/router.py route "task"` classifies English or Russian task text and explains signals; overrides include `--operation`, `--risk`, `--level`, `--role`, `--effort`, `--provider`, and `--model`.
- `python scripts/router.py configure TARGET --apply` writes `ai-kit/router/resolved.json` and, for Aider, `.aider.conf.yml`.
- Providers available to the project are recorded in `ai-kit/router/selection.json`: OpenAI, Anthropic, Kimi, Gemini, and local or Ollama models. `python scripts/router.py providers` lists status and sources; `python scripts/metrics.py analyze TARGET` aggregates the local journal per provider to inform that selection.

## Unified CLI

A single `aikit` command wraps the scripts: `python aikit_cli.py install|doctor|route|configure|providers|metrics|adr|changelog|check|docker ...`. A `pyproject.toml` console script exposes it after `pip install -e .`; the standalone `python scripts/*.py` commands and the Makefile remain equivalent.

## Maintaining AI-KIT itself

1. Read the repository's `PROJECT_CONTEXT.md` and `AGENTS.md`; keep template rules in their canonical owner (see policy ownership in `docs/IMPLEMENTATION.md`).
2. Run `python scripts/check_kit.py` and `python -m unittest discover -s tests -v` for affected behavior.
3. Keep `template/` free of kit history and assumed stack facts. Byte budgets: template AGENTS 2500, CORE 3000, documents 12000, root README 20000.
4. Verify client formats and model facts against primary vendor documentation before changing them.
5. Update the root CHANGELOG, maintainer context, the continuity skill, and this skill when commands or features change.

## Boundaries

AI-KIT writes instructions and configuration; it does not run agents. Confirm activation in the actual client. Permission rules and ignore files reduce risk but are not a security boundary. Hosted CI and real application trials are recorded as unverified unless evidence exists.

## Use this repository as a skill

This SKILL.md sits at the root of the AI-KIT repository, so the repository itself is the skill and carries its installer, templates, and documents. For Claude Code across all projects, clone it into the skills directory: `git clone https://github.com/tigusigalpa/ai-kit.git ~/.claude/skills/ai-kit`; the commands above then run from that folder. For other assistants, clone the repository next to the project or paste this file as context. Canonical documents: [README](README.md), [Core](template/ai-kit/CORE.md), [adapters and presets](template/ai-kit/ADAPTERS.md), [containers](template/ai-kit/CONTAINERS.md), [routing](template/ai-kit/router/POLICY.md), [maintainer instructions](AGENTS.md).
