# AI-KIT changelog

## v0.6.5 (2026-10-10)

- Added a root [SKILL.md](SKILL.md) that makes the repository itself a skill: cloned into a skills directory it carries the installer and teaches any assistant to install, configure, upgrade, explain, and maintain the kit; the checker requires it and validates its frontmatter.
- Revised ignore rules. The reference repository now ignores IDE, editor, and OS files; `.idea/` was removed from the Git index (local files kept). Application policies gain the useful `.gitignore_real` rules: private mode keeps AI client configuration folders out of Git, and both modes ignore extracted AI-KIT bundles, `.netrc`, `.pypirc`, Aider history, PHP-CS-Fixer and Homestead files, Zed/Nova folders, and Delve binaries. Node modules also ignore Next, Nuxt, SvelteKit, Turbo, and Parcel output. Rules that would hide project source (global `vendor/`, `SKILL.md`, `/bin/`, `/config.php`) stay scoped or excluded. The bundle pattern uses a hyphen because `/AI-KIT*/` matched `ai-kit/` itself on case-insensitive systems and would hide AI-KIT files in team mode.
- Rewrote the root README as a feature showcase: a features-at-a-glance table, a feature tour (project memory, stack profiles for Go/PHP/Laravel/Filament 5/Moodle/Python, the Kubernetes-ready container contract, adaptive model routing, 11 AI clients, native configuration, guardrails, workflows), a three-step quick start, and an honest-boundaries section. Claims were checked against the canonical template documents. The root README budget rises to 20000 bytes; other documents keep 12000.
- Verification: 185 tests ran, 184 passed, one Windows symlink skip; kit validation returned zero errors and one pending-Gemini warning, including the new private/team visibility checks. Client activation and hosted CI remain unverified.

## v0.6.4 (2026-10-10)

- Added `--with-native-settings`: Claude Code allow rules for recorded single-command checks, Read deny rules for secrets from [one list](templates/agent-secrets.ignore) plus detected Laravel/Moodle/Composer/Python secrets, and a marked secret block in `.cursorignore`, `.aiderignore`, and `.geminiignore` for selected clients. Private mode now keeps all AI-KIT Claude entries in `.claude/settings.local.json`, team mode in `.claude/settings.json`; owned entries move with the mode and user entries stay.
- Added `--with-scoped-rules`: one managed rule per module with stack profiles for Claude Code (`paths`), Cursor (`globs`), Copilot (`applyTo`), Windsurf (`trigger: glob`), and Cline (`paths`), generated from `ai-kit/project.json`. Codex gets no nested AGENTS.md (it reads only root-to-working-directory files) and no config.toml.
- Added `--with-data-guards`: ask rules before `rm -rf`, `git reset --hard`, `git clean`, Docker prune/volume removal, and detected Laravel/Moodle migrations.
- Added `--preset minimal|solo|team|strict` (also in `--interactive`); explicit flags win and the preview names extras a preset turns off.
- Added user-invoked workflow skills `ai-kit-bootstrap`, `ai-kit-review`, and `ai-kit-sync-context`, so the first session starts with `/ai-kit-bootstrap` instead of a pasted prompt.
- Gave the root README its own 16000-byte budget; other documents keep 12000. Moved v0.3.x entries to [docs/history](docs/history/v0.3-changelog.md).
- Verification: 185 tests ran, 184 passed, one Windows symlink skip; kit validation returned zero errors and one pending-Gemini warning; a real v0.5.0 installation upgraded without conflicts. Client activation remains unverified. [Results](docs/V0_6_4.md), [ADR 0007](docs/adr/0007-generated-client-configuration-and-presets.md).

## v0.5.0 (2026-10-10)

- Aligned the offline router with the canonical capability ladder (level 0 cheap/none when supported, level 5 work/max, level 6 diagnosed escalation with a separate effort choice). Added English/Russian operation/risk rules, word boundaries, structured evidence flags, explanation signals, and per-call provider/model overrides. Explicit selection/CLI effort wins; unknown or unsupported model controls are not fabricated.
- Added a conditional [Filament profile](template/ai-kit/stacks/FILAMENT.md) and source/native Claude skill copies. Composer requirements/locks suggest FILAMENT per module; bootstrap still verifies actual use, versions, and application commands. Existing personal conventions remain in OWNER.
- Added opt-in [local measurements](template/ai-kit/METRICS.md) with validated task/attempt records, coverage-aware totals, failure/recovery accounting, duplicate/lock/path guards, and private journals in both sharing modes. No automatic telemetry, API execution, or inferred prices.
- Prepared a [real-project evaluation protocol](docs/EVALUATION.md): fixed-model instruction comparisons first, context selection/fresh-session continuation checks, routing as a separate experiment. The owner deferred application trials; no savings or application activation is claimed.

- Fixed the Linux client-detection regression when `.clinerules` is a regular file: unselected directory adapters are probed without treating a file parent as a fatal error. Existing rules and agent selections remain intact.
- Selected installation paths now reject non-directory parents during planning on every platform, before any write. Permission failures and linked-path refusal remain enforced; regressions cover POSIX errors, preservation, CLI refusal, and rerun stability.
- Earlier adapter-only verification: Windows/Python 3.12.14 ran 133 tests, 129 passed, four environment-dependent skips; Python 3.10 grammar passed. [Verification](docs/ADAPTER_PATH_FIX.md) distinguishes portable POSIX regression coverage from unverified native Linux and corrected hosted CI.
- v0.5.0 verification: 161 tests ran, 157 passed, four environment-dependent skips; post-review targeted checks passed. Kit validation returned zero errors and one expected pending-Gemini warning; all scripts/tests passed Python 3.10 grammar. Synthetic upgrade preserves project facts, model selection, and measurement bytes while adding Filament source/native skills. [Results and runtime limits](docs/V0_5_0.md).

## v0.4.7 (2026-10-10)

- Guards now use Claude Code `permissions.ask` for Git commit/push (source renamed to [claude-settings.git-ask.json](integrations/claude-settings.git-ask.json)). Core allows an explicitly requested commit, which the previous deny rules blocked; bare `git commit`/`git push` forms are now covered too.
- The installer owns only its own entries in `.claude/settings.json` instead of the whole file: other keys, rules, and hooks survive, owned entries are recorded under `managed_json` in installer state, and disabling an extra removes only its entries. A file that is not a JSON object becomes a reviewed conflict whose candidate holds the AI-KIT fragment. Whole-file installations from earlier versions migrate on the next run. The doctor reports missing owned entries instead of flagging user edits.
- The session-start hook runs a managed `.agents/hooks/session-start.sh` via `$CLAUDE_PROJECT_DIR` and adds the instructions, current PROJECT_CONTEXT (first 8000 bytes, with a truncation notice), and Git status to the session, saving a file read per session. The script is piped through `tr` so CRLF checkouts (Git autocrlf on Windows, team clones) still run. Private mode now hides the hook files.
- The preview reports `detected_agents` from existing native files (detect markers in [agents.json](integrations/agents.json)) and `suggested_agents`, with a ready `--agent` command when no explicit selection is given; `--interactive` uses the detected clients as its default. Detection never changes the selection by itself.
- Command suggestions follow evidence: Node uses `packageManager` or a lockfile, searched up to the workspace root, and runs Bun scripts with `bun run test`; Python suggests pytest/ruff only when manifests or config files reference them, prefixed with `uv run`/`poetry run` when their lockfile exists.
- Moved the v0.2.x changelog entries verbatim to [docs/history](docs/history/v0.2-changelog.md) to keep this changelog within its byte budget.
- Upgraded a real v0.4.6 installation (claude, guards, session-start, user-edited settings): no conflicts, user settings kept, legacy entries migrated, rerun stable, doctor clean. A v0.4.6 preview against the upgraded project reports `.claude/settings.json` as a conflict without writing.
- Recorded the decision in [ADR 0005](docs/adr/0005-client-settings-ownership.md). Reran the full local suite: 128 tests, 127 passed, 1 skipped (Windows symlink privilege); kit validation returned no errors; the hook script was executed through Git Bash. Native Claude Code hook delivery, ask enforcement, and hosted CI remain unverified.

## v0.4.6 (2026-10-10)

- Added one-step onboarding: `--interactive` prompts for mode, language, conventions, agents, and extras; `--check` runs the doctor after `--apply`.
- Added [ai-kit/project.json](template/ai-kit/project.json): the installer detects per-module manifests, language, version, and suggested test/lint/build commands and drafts `PROJECT_CONTEXT.md` and `project.json`, marked suggested until bootstrap confirms them.
- Added `scripts/adr.py new` and `scripts/changelog.py add` helpers plus a [Makefile](Makefile) front-door (`make install`, `make doctor`, `make check`, `make test`, `make router`, `make adr`, `make changelog`).
- Extended the checker and doctor for `project.json` and the helper scripts.
- Reran the full local suite: 109 tests, 108 passed, 1 skipped; kit validation returned no errors. PyPI publication stays deferred (remote changes are not authorized).

## v0.4.5 (2026-10-10)

- Added a data-driven agent registry ([integrations/agents.json](integrations/agents.json)) replacing hardcoded client/entry constants; installer, checker, and doctor now share one source for agent wiring.
- Added [scripts/router.py](scripts/router.py): `route "task"` returns a deterministic capability recommendation, and `configure PROJECT --apply` writes `ai-kit/router/resolved.json` plus a native Aider model file. Classification is a transparent rule; no credentials or switching runtime.
- Added [selection.json](template/ai-kit/router/selection.json) for provider choice with per-role overrides and self-hosted model IDs.
- Added provider tiers: a [local provider](template/ai-kit/router/providers/local.json) (user-supplied Ollama IDs) and a [pending Gemini scaffold](template/ai-kit/router/providers/gemini.json) (no fabricated IDs). Schema adds `tier`, `user_supplied_models`, `verification_status`.
- Extended the checker and doctor for the registry, provider schema, and selection/resolved validation.
- Reran the full local suite: 92 tests, 91 passed, 1 skipped; kit validation returned no errors. Gemini IDs remain pending; no live API or hosted CI.

## Earlier kit

The [archived v0.3 changelog](docs/history/v0.3-changelog.md) preserves the v0.3.3-v0.3.8 entries verbatim. The [archived v0.2 changelog](docs/history/v0.2-changelog.md) preserves the v0.2-v0.2.2 and Windows fixture entries verbatim. The [archived v0.1 changelog](docs/history/v0.1-changelog.txt) preserves the detailed pre-refactor record verbatim. Its old relative paths and past language/router agreements are historical data.
[Prior routing decision](docs/adr/0001-adaptive-model-routing.md) records the accepted routing baseline; this changelog is not copied into projects.
