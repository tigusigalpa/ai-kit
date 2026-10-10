# AI-KIT changelog

## v0.7.0 (2026-10-10)

- Added a unified `aikit` command line ([aikit_cli.py](aikit_cli.py)) that dispatches `install`, `doctor`, `route`, `configure`, `metrics`, `adr`, `changelog`, `check`, and `docker` to their scripts, plus a [pyproject.toml](pyproject.toml) console script (`pip install -e .` exposes `aikit`). The version is derived from VERSION; a portable wheel still needs the package-data packaging step, which stays deferred.
- Expanded the CI matrix to macOS and Python 3.14 and added a `route` smoke step through the unified CLI.
- The doctor now reports when `ai-kit/project.json` and `PROJECT_CONTEXT.md` module maps disagree, so machine and human project facts cannot silently drift apart.
- Relaxed `chat_language` to accept non-Latin language names (for example Ukrainian or Chinese); it remains a nonempty, control-character-free name up to 60 characters.
- Verification: 191 tests ran, 189 passed, two skipped (Windows symlink privilege and POSIX sh unavailable); kit validation returned zero errors and one pending-Gemini warning. Hosted CI on the expanded matrix remains unverified until the next push; a portable wheel is deferred.

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

## Earlier kit

The [archived v0.4 changelog](docs/history/v0.4-changelog.md) preserves the v0.4.5-v0.4.7 entries verbatim. The [archived v0.3 changelog](docs/history/v0.3-changelog.md) preserves the v0.3.3-v0.3.8 entries verbatim. The [archived v0.2 changelog](docs/history/v0.2-changelog.md) preserves the v0.2-v0.2.2 and Windows fixture entries verbatim. The [archived v0.1 changelog](docs/history/v0.1-changelog.txt) preserves the detailed pre-refactor record verbatim. Its old relative paths and past language/router agreements are historical data.
[Prior routing decision](docs/adr/0001-adaptive-model-routing.md) records the accepted routing baseline; this changelog is not copied into projects.
