# AI-KIT changelog

## v0.11.0 (2026-10-11)

- Fixed provider/model overrides carrying inherited effort; synchronized Gemini routing policy with the reviewed registry. Existing selection/settings defaults stay readable and unchanged.
- Fixed the untested v0.10 adapter audit failing before it could report file-blocked native paths. Read-only state validation now allows obstructions after strict link/boundary checks; installation writes retain their refusal guards.
- Forwarded subcommand help to the actual command parser, so `aikit benchmark --help` and install flags are discoverable.
- Added preview-first `aikit benchmark run|review|report|export`: immutable Git blobs, separate A/B/C workspaces/repeats, equal fixed A/B controls, a configured worker protocol, actual-telemetry coverage, checks plus explicit semantic review, private JSON/Markdown reports and idempotent journal export. No live vendor adapter or application savings is claimed.
- Added metric schema 3 for revision/case/repetition/stack/class/level/capability/review strata, keeping schemas 1/2 readable. Comparisons require matched reviewed tasks and actual single-currency costs, include all failures/retries and refuse lower-quality/unknown/estimated spend claims. Added per-stack analysis.
- Added optional manual/fixed/recommended/adaptive modes, task/project pins and economy/balanced/quality profiles. Learned recommendations require comparable distinct-case samples and quality floors; unsupported controls or insufficient evidence retain the capability recommendation. Immutable proposals preserve prior selection and support explicit backed-up restore without automatic policy writes.
- Added read-only module context selection, duplicate detection and byte-budget reporting while preserving critical requirements and architectural decisions. Added staged acceptance plan and orchestration research in ADR 0012.
- Expanded wheel resources and smoke checks outside the source checkout, including installed validation, new command imports and context selection. Windows/Python 3.12.14 full discovery ran 248 tests (244 passed, four runtime skips); post-review checks and offline wheel installation passed; kit validation returned zero errors/warnings. [Results and limits](docs/IMPLEMENTATION.md#measurement-led-development-verification).

## v0.10.0 (2026-10-10)

- Fixed `metrics.py analyze` task attribution: the identity is now `(experiment, arm, task_id)`, so baseline and kit rows with the same task ID no longer collapse. Added backward-readable measurement schema 2 with required per-attempt `succeeded`/`failed`/`inconclusive` disposition, coverage, and decisive-attempt rate; schema 1 journals remain valid with unknown disposition.
- Added manifest evidence snapshots in `ai-kit/project.json`, `aikit context snapshot TARGET [--apply]`, and doctor warnings for new/removed modules, profile drift, and changed manifest evidence. The snapshot is preview-first and changes only evidence after explicit apply.
- Added client documentation metadata in `integrations/agents.json`, `aikit adapters report`, and conservative `aikit adapters retire TARGET --agent NAME [--apply]`. Retirement backs up and removes only unchanged tracked adapter files, then deselects that client; local edits, untracked files, native directories, settings fragments, and ignore blocks remain untouched.
- Added the private `aikit evaluate scaffold|coverage` harness for opaque baseline/kit task packs and measurement-pair coverage. It reports missing pairs and unexpected records but does not inspect prompts or infer semantic correctness.
- Added MCP posture and an indirect-instruction boundary: untrusted repository/remote content cannot authorize commands, integrations, credentials, or permission changes; MCP servers remain opt-in, least-privilege, and project-recorded.
- Packaged the `aikit` console command with bundled templates/resources for a portable wheel and added a six-cell Windows/macOS/Linux, Python 3.10/3.14 CI smoke-install job. The hosted job has not run on this revision.
- Initial release preparation established no checker, unit, build or wheel-smoke result because the shell did not expose Python. Later bundled-runtime checks cover v0.11.0 preparation; see [current verification](docs/IMPLEMENTATION.md#measurement-led-development-verification). The hosted job and pristine v0.10.0 reconstruction remain unverified.

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

The [archived v0.6.5-v0.9 entries](docs/history/v0.6.5-v0.9-changelog.md) preserve later local releases. The [archived v0.4 changelog](docs/history/v0.4-changelog.md) preserves the v0.4.5-v0.4.7 entries verbatim. The [archived v0.3 changelog](docs/history/v0.3-changelog.md) preserves the v0.3.3-v0.3.8 entries verbatim. The [archived v0.2 changelog](docs/history/v0.2-changelog.md) preserves the v0.2-v0.2.2 and Windows fixture entries verbatim. The [archived v0.1 changelog](docs/history/v0.1-changelog.txt) preserves the detailed pre-refactor record verbatim. Its old relative paths and past language/router agreements are historical data.
[Prior routing decision](docs/adr/0001-adaptive-model-routing.md) records the accepted routing baseline; this changelog is not copied into projects.
