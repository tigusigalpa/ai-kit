# AI-KIT maintainer context

## Verified project

- Purpose: portable instructions, clean project templates, conservative installation and kit validation.
- Stack: Markdown, JSON, and Python standard library; scripts require Python 3.10 or later.
- Source layout: template/ contains installable files; templates/ contains ignore policies; scripts/ and tests/ maintain the distribution. The registry lives in integrations/agents.json. Router/adaptive/learning provide recommendations and analysis; benchmark executes configured protocol workers; context snapshots evidence and selects scoped instructions; adapters audit/retire clients; evaluate reports opaque pair coverage; adr/changelog scaffold records. A Makefile wraps the established commands.
- Version source: [VERSION](VERSION), currently 1.3.0, locally prepared for Web Design. Publishing/tagging remain separate.
- Project ownership: root documentation/history describe AI-KIT; template/ project context and history remain uninitialized.
- Onboarding: README covers Web Design, security, Context7 and proposed OpenRouter use; no OpenRouter runtime adapter is shipped. Root README has no size quota; project instruction budgets remain unchanged.

## Source verification

- Canonical repository: https://github.com/tigusigalpa/ai-kit, tracking main.
- Remote administration check: 2026-10-11; main resolved to b62e409cb4f8d9fbb2299ff2eed667f7fe628451. All 15 distinct GitHub Actions checks on that commit reported success; the remote CI workflow matched the local file. This was not a full source reconstruction or a new CI run.
- Earlier source/CI reconstruction and fixture-path corrections: [Windows record](docs/WINDOWS_CI_FIX.md). Compatibility pointers replace known old rules; installation uses template/ exclusively.
- Reproduced older installer findings and preservation fixes: [Manus disposition](docs/MANUS_REVIEW.md). Temporary fixture roots resolve before guard/assertion paths are derived.

## Repository maintenance

- Main protection was enabled through gh at the owner's request and independently read back on 2026-10-11. Changes require a pull request, all 15 current validation/wheel checks from GitHub Actions, an up-to-date branch, and resolved review conversations. Force pushes and branch deletion are disabled; administrators follow the same rules. Required approving reviews: zero, allowing solo maintenance.
- Validation covers Linux/Windows/macOS with Python 3.10/3.13/3.14; wheel checks cover those systems with Python 3.10/3.14. When changing CI job names or matrix cells, synchronize required check names under explicit remote authorization. Existing Core commit/push authorization still applies.

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
- Optional security audit: --with-security-audit persists security_audit=true outside presets; pinned Cloudflare identity is in integrations/security-audit.json. Offline explicit-only entry points create no reports. Native Windows validator CLI lacks required OS input-open protections; [contract/results](docs/SECURITY_AUDIT.md).
- Prior security-audit checks and Windows validator limits: [results](docs/SECURITY_AUDIT.md).
- Optional Strix: --with-strix persists strix=true outside presets, independently of security-audit. integrations/strix.json pins nine skills and Apache-2.0 license at f7a32ae62d94872631bc8415073868d02a6ffdaf. One explicit-only source/Claude entry point; offline installation runs no runtime/scan. External CLI, Docker/image, model, writable target copy, scope and budget are separate; [contract/results](docs/STRIX.md).
- Optional Context7: --with-context7 persists context7=true outside presets; source/Claude context7-docs uses normal discovery. HTTP client examples and sanitized version-aware lookup: [contract](template/ai-kit/CONTEXT7.md). MCP setup/activation stays separate; [source and checks](docs/CONTEXT7.md).
- Optional Web Design: --with-web-design persists web_design=true outside presets; four normal-discovery source/Claude skills and conditional guides. docs/design/BRIEF.md, SYSTEM.md and ACCEPTANCE.md are created only when missing and preserved. Actual stack selection and external tools remain separate; [contract](template/ai-kit/WEB-DESIGN.md), [source/checks](docs/WEB_DESIGN.md).
- Design context: context select --workflow web-design|ui-review|design-extract includes enabled project design memory; main workflow selects Blade guidance only for declared Laravel/Filament modules. Ordinary selection stays unchanged; reports are manifests, not prompts. Raw ai-kit/.design output is ignored in both modes; sanitized project design docs stay visible.
- Strix verification and unavailable scans: [results](docs/STRIX.md#verification).
- Earlier release labeling: [v1.1.0](CHANGELOG.md#v110-2026-10-12), [Context7/v1.2.0](docs/CONTEXT7.md#release-labeling). Current labeling: [Web Design/v1.3.0](docs/WEB_DESIGN.md#release-labeling).
- Generated client configuration derives from ai-kit/project.json (detection fallback): secrets from templates/agent-secrets.ignore plus stack additions, client ignore files and scoped rule formats declared per agent in integrations/agents.json. Workflow skills ai-kit-bootstrap/review/sync-context install with source and Claude copies.
- Client detection: detect markers per agent in integrations/agents.json; preview reports detected_agents/suggested_agents without changing the selection.
- Adapter file parents: an existing `.clinerules` file is detected and preserved when Cline is unselected. Selecting its directory adapter refuses the blocked parent during planning; see [file-parent compatibility](docs/ADAPTER_PATH_FIX.md).
- Optional adapters: gemini, windsurf, cline, roo; machine-readable client documentation/activation metadata lives in integrations/agents.json. Machine-readable router providers live in template/ai-kit/router/providers/, with provider choice in template/ai-kit/router/selection.json. MCP posture is template/ai-kit/MCP.md; no MCP server is installed automatically.
- Verification results and limitations: [implementation record](docs/IMPLEMENTATION.md#verification).
- Pre-label checks: 304 Windows/Python 3.12.14 tests (300 passed/four skips), clean kit/skills, all-client visibility and tracked 1.2.0 upgrade; [results](docs/WEB_DESIGN.md#verification). Post-label: eight CLI tests, v1.3.0 wheel smoke and preserved pre-label upgrade passed; no live application result is implied.
- Earlier release results remain in [the implementation record](docs/IMPLEMENTATION.md#verification) and linked history; they do not establish the current revision.
- Use bundled Windows/Python 3.12.14 and writable external fixtures when sandbox TEMP is unavailable. Earlier checks remain in [implementation](docs/IMPLEMENTATION.md#measurement-led-development-verification); hosted CI/client activation are separate.

## Agreements

- Policy defaults and authorization: [Core](template/ai-kit/CORE.md) and [settings](template/ai-kit/settings.json).
- User selected MIT on 2026-10-08; [LICENSE](LICENSE) applies to the kit.
- Actual client activation, live model switching, Docker cleanup, and successful hosted CI are not established by local file checks.
- Owner deferred real benchmark/application calls; current scope is code and synthetic tests, including orchestration research rather than a live orchestrator.
- Last context synchronization: 2026-10-13.
