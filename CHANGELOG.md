# AI-KIT changelog

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

## v0.3.8 (2026-10-10)

- Added Gemini CLI, Windsurf, Cline, and Roo adapters: a GEMINI.md project entry plus optional .windsurf/rules/, .clinerules/, and .roo/rules/ pointer rules; private-mode ignores cover the new entries. Client rule formats were checked against current documentation on 2026-10-10 and still require activation verification in the actual clients.
- Filled in the Anthropic and Kimi router mappings as machine-readable provider configurations with roles, defaults, supported efforts, verified documentation dates, and sources. Anthropic IDs, effort levels, and request-field boundaries were verified against primary documentation (models overview and the Haiku 5.5 migration guide); Kimi facts were cross-checked against current online documentation.
- Generalized checker provider validation to every providers/*.json (required verified date, effort/support consistency) and extended the model-ID duplication guard to all configured IDs; the project doctor now handles roles without an effort control.
- Reran the full local suite: 73 tests, 72 passed, 1 unavailable Windows symlink check; kit validation returned no errors or warnings; Python 3.10 grammar verified. Live API calls, native client activation, and hosted CI remain unverified.

## v0.3.6 (2026-10-10)

- Added opt-in install extras selected with --with-session-start, --with-guards, and --with-ci; accepted choices persist in ai-kit/settings.json. Session start installs .agents/hooks/session-start.md and, for claude, .claude/settings.json SessionStart wiring; guards merges the reference deny-Git permissions into the same client settings file; the ci extra installs a self-contained .github/workflows/ai-kit.yml health check intended for team mode.
- Documented extras in ADAPTERS/BOOTSTRAP/README with activation boundaries: hook output, deny enforcement, and workflow behavior require verification in the actual client and hosted runner; MCP servers are declared manually per project and none is installed by default.
- Reran the full local suite: 69 tests, 68 passed, 1 unavailable Windows symlink check; kit validation returned no errors or warnings; Python 3.10 grammar was verified for all scripts. Hosted CI and real application trials remain unverified.

## v0.3.3 (2026-10-10)

- Added installer-suggested stack profiles: the plan detects GO, PYTHON, FRONTEND, PHP, LARAVEL, and MOODLE evidence from module manifests, reports it in the preview, and drafts module-map rows in a fresh PROJECT_CONTEXT.md marked unverified until bootstrap confirms them. Existing context documents remain preserved untouched.
- Added scripts/doctor.py, an offline health check for installed projects: state/settings validation, missing or modified managed files, missing owned documents, pending conflict candidates, always-loaded budget overflows, broken Markdown links/anchors, and stale provider verifications. Exit code 0 means no errors.
- Scoped Node and Python generated-path exclusions to modules with verified manifests (package.json, pyproject.toml, requirements.txt, setup.py, setup.cfg), matching the existing Composer/Moodle scoping; both ignore policies keep only generic output directories statically.
- Extended the checker visibility fixture to compose each policy with installer-detected module rules, as apply does.
- Moved maintainer-only reference-update guidance to CONTRIBUTING.md and the original-bundle verification record to docs/history to keep conditional documents within byte budgets; removed the external hero-image hotlink from the README.
- Reran the full local suite for these changes: 62 tests, 61 passed, 1 unavailable Windows symlink check; kit validation returned no errors or warnings; Python 3.10 grammar was verified for install, checker, and doctor sources. Hosted CI and real application trials remain unverified.

## Earlier kit

The [archived v0.2 changelog](docs/history/v0.2-changelog.md) preserves the v0.2-v0.2.2 and Windows fixture entries verbatim. The [archived v0.1 changelog](docs/history/v0.1-changelog.txt) preserves the detailed pre-refactor record verbatim. Its old relative paths and past language/router agreements are historical data.
[Prior routing decision](docs/adr/0001-adaptive-model-routing.md) records the accepted routing baseline; this changelog is not copied into projects.
