# AI-KIT maintainer context

## Verified project

- Purpose: portable instructions, clean project templates, conservative installation and kit validation.
- Stack: Markdown, JSON, and Python standard library; scripts require Python 3.10 or later.
- Source layout: template/ contains installable files; templates/ contains ignore policies; scripts/ and tests/ maintain the distribution. The registry lives in integrations/agents.json. Router/adaptive/learning provide recommendations and analysis; benchmark executes configured protocol workers; context snapshots evidence and selects scoped instructions; adapters audit/retire clients; evaluate reports opaque pair coverage; adr/changelog scaffold records. A Makefile wraps the established commands.
- Version source: [VERSION](VERSION), currently 0.11.0, locally prepared at the owner's request. Publishing/tagging remain separate; the last verified published source was v0.2.2.
- Project ownership: root documentation/history describe AI-KIT; template/ project context and history remain uninitialized.
- Onboarding: root README is the practical entry guide; its command examples match the installer CLI and distinguish application installation from reference-repository overlays.

## Source verification

- Canonical repository: https://github.com/tigusigalpa/ai-kit, tracking main.
- Last checked: 2026-10-08; main resolved to 5b487824e3c6f5ab697981f4f3b19f59f5d16af4. Relevant published test source matched the local pre-fix file; this revision was not rebuilt in full.
- Earlier snapshot: published v0.2 at 73707036c1098d8c1c81ab2c51d723c3d521f6b8 overlaid on v0.1. All 91 tracked blobs were rebuilt with verified Git object hashes, reproducing the five missing-heading errors.
- Compatibility pointers replace known old rule documents; application installation uses template/ exclusively. Current local fixture correction: [Windows CI regression](docs/WINDOWS_CI_FIX.md).
- Independently reproduced three Manus installer findings against v0.2.1: candidate overwrite, lost adapter tracking, and unsupported/mixed-type state failure. Patch 0.2.2 preserves candidates, blocks unresolved adapter retirement, and validates inputs before planning; [audit disposition](docs/MANUS_REVIEW.md).
- Earlier run 37810446904 failed at the v0.2 snapshot. Latest checked run 37819777582 failed on Windows/Python 3.10 and 3.13; its Ubuntu/Python 3.10 and 3.13 jobs succeeded. The supplied Windows traceback exposes unresolved versus canonical fixture-path comparisons; current correction resolves the root before deriving paths.

## Working commands

- Validation: python scripts/check_kit.py
- Behavioral tests: python -m unittest discover -s tests -v
- Unified CLI: python aikit_cli.py install|doctor|context|adapters|route|configure|providers|metrics|evaluate|benchmark|adr|changelog|check|docker ... (pyproject.toml exposes `aikit` after pip installation); standalone scripts remain equivalent.
- Install preview: python scripts/install.py TARGET
- Apply installation: python scripts/install.py TARGET --apply (add --check to run the doctor afterward, --interactive for a guided prompt)
- Installed-project health check: python scripts/doctor.py TARGET (add --fix to restore missing managed files/owned documents); it reports module/profile/manifest-evidence drift.
- Project-fact snapshot: python scripts/context.py snapshot TARGET [--apply] (preview first; updates only project.json evidence).
- Context selection: aikit context select TARGET --path MODULE --budget BYTES (read-only declared scope, critical rules/decisions, duplicates and measured bytes; budget overruns retain requirements).
- Benchmark: aikit benchmark run TARGET --pack PRIVATE_PACK [--apply], then review/report/export. Uses immutable pre-kit Git blobs, private workspaces, a reviewed worker protocol, separate checks/semantic acceptance, JSON/Markdown reports and the existing journal; [contract](docs/BENCHMARK.md).
- Optional routing modes/profiles/pins: ai-kit/router/routing.json; route --mode manual|fixed|recommended|adaptive --profile economy|balanced|quality. Adaptive recommendations require matched schema-3 measurements, sufficient distinct cases, actual retry costs and quality floors. No live model switching or active policy writes; [plan](docs/DEVELOPMENT_PLAN.md), [ADR 0012](docs/adr/0012-measurement-led-routing.md).
- Analysis: metrics compare --experiment ID, stacks, propose [--apply] and restore --proposal SHA256 [--apply]. Proposal saving is immutable and does not apply suggestions; restore explicitly backs up/replaces prior selection. Schema 3 records strata/review while schemas 1/2 stay readable.
- Client report/retirement: python scripts/adapters.py report [--project TARGET]; python scripts/adapters.py retire TARGET --agent NAME [--apply] (removes only unchanged tracked adapter files after preview and backup).
- Routing recommendation: python scripts/router.py route "task"
- Routing configuration: python scripts/router.py configure TARGET --apply
- Provider review: python scripts/router.py providers (also `aikit providers`; lists tier, status, date, and sources)
- Routing evidence/overrides: route accepts --operation, repeatable --risk, --components, --level, --role, --effort, --provider, and --model. English/Russian rules explain recommendations; only declared model capabilities produce an effort control. The helper does not execute tasks or switch live models.
- Optional measurement preview/apply: python scripts/metrics.py record TARGET --from-json PRIVATE_RECORD [--apply]; summary/analyze: python scripts/metrics.py summary|analyze TARGET (analyze aggregates per provider by experiment/arm/task identity to inform selection.json, read-only). Schema 2 records per-attempt disposition; schema 1 journals remain readable. ai-kit/.metrics/ journals are ignored in private/team modes, validated, and preserved by upgrades.
- Filament: known Composer dependencies/locks suggest the conditional FILAMENT profile per module. Bootstrap verifies use and installed versions; source and Claude-native skills point to the same profile.
- Application evaluation: [protocol](docs/EVALUATION.md) separates fixed-model instruction trials, context/continuation checks, and routing. scripts/evaluate.py scaffolds opaque baseline/kit task IDs and reports journal pair coverage; it does not assess semantic correctness. The owner chose to run real-project trials separately; no productivity/cost result is established.
- Decision record scaffold: python scripts/adr.py new "title" --root TARGET
- Changelog entry: python scripts/changelog.py add "message" --root TARGET
- Optional install extras: --with-session-start, --with-guards, --with-data-guards, --with-native-settings, --with-scoped-rules, --with-ci (persist in ai-kit/settings.json), or --preset minimal|solo|team|strict for the managed set (CI stays explicit). Claude wiring merges owned entries (managed_json in installer state) into .claude/settings.local.json in private mode and .claude/settings.json in team mode; guards are ask rules.
- Generated client configuration derives from ai-kit/project.json (detection fallback): secrets from templates/agent-secrets.ignore plus stack additions, client ignore files and scoped rule formats declared per agent in integrations/agents.json. Workflow skills ai-kit-bootstrap/review/sync-context install with source and Claude copies.
- Client detection: detect markers per agent in integrations/agents.json; preview reports detected_agents/suggested_agents without changing the selection.
- Adapter file parents: an existing `.clinerules` file is detected and preserved when Cline is unselected. Selecting its directory adapter refuses the blocked parent during planning; see [file-parent compatibility](docs/ADAPTER_PATH_FIX.md).
- Optional adapters: gemini, windsurf, cline, roo; machine-readable client documentation/activation metadata lives in integrations/agents.json. Machine-readable router providers live in template/ai-kit/router/providers/, with provider choice in template/ai-kit/router/selection.json. MCP posture is template/ai-kit/MCP.md; no MCP server is installed automatically.
- Verification results and limitations: [implementation record](docs/IMPLEMENTATION.md#verification).
- Local verified environment: Windows, bundled Python 3.12.14. The user supplied a Linux/Python 3.13.16 hosted-check failure; successful hosted matrix execution remains unverified.
- Earlier release results remain in [the implementation record](docs/IMPLEMENTATION.md#verification) and linked history; they do not establish the current revision.
- Current verification uses bundled Windows/Python 3.12.14; it is accessible even when the shell has no `python` command. Point disposable fixtures at a writable external root when sandbox TEMP is unavailable. Before release labeling, full discovery ran 248 tests (244 passed, four runtime skips); post-review checks passed. v0.11.0 CLI/version checks and rebuilt wheel installation passed. Results and limits are recorded in [implementation](docs/IMPLEMENTATION.md#measurement-led-development-verification); hosted CI and native client activation remain separate.

## Agreements

- Policy defaults and authorization: [Core](template/ai-kit/CORE.md) and [settings](template/ai-kit/settings.json).
- User selected MIT on 2026-10-08; [LICENSE](LICENSE) applies to the kit.
- Actual client activation, live model switching, Docker cleanup, and successful hosted CI are not established by local file checks.
- Owner deferred real benchmark/application calls; current scope is code and synthetic tests, including orchestration research rather than a live orchestrator.
- Last context synchronization: 2026-10-11.
