# AI-KIT maintainer context

## Verified project

- Purpose: portable instructions, clean project templates, conservative installation and kit validation.
- Stack: Markdown, JSON, and Python standard library; scripts require Python 3.10 or later.
- Source layout: template/ contains installable files; templates/ contains ignore policies; scripts/ and tests/ maintain the distribution. The agent registry lives in integrations/agents.json; scripts/router.py is the routing helper; scripts/adr.py and scripts/changelog.py scaffold records; a Makefile wraps the commands.
- Version source: [VERSION](VERSION). The local tree is prepared as v0.6.5. Publishing/tagging this version has not been requested; the last verified published source was v0.2.2.
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
- Install preview: python scripts/install.py TARGET
- Apply installation: python scripts/install.py TARGET --apply (add --check to run the doctor afterward, --interactive for a guided prompt)
- Installed-project health check: python scripts/doctor.py TARGET
- Routing recommendation: python scripts/router.py route "task"
- Routing configuration: python scripts/router.py configure TARGET --apply
- Routing evidence/overrides: route accepts --operation, repeatable --risk, --components, --level, --role, --effort, --provider, and --model. English/Russian rules explain recommendations; only declared model capabilities produce an effort control. The helper does not execute tasks or switch live models.
- Optional measurement preview/apply: python scripts/metrics.py record TARGET --from-json PRIVATE_RECORD [--apply]; summary: python scripts/metrics.py summary TARGET. ai-kit/.metrics/ journals are ignored in private/team modes, validated, and preserved by upgrades.
- Filament: known Composer dependencies/locks suggest the conditional FILAMENT profile per module. Bootstrap verifies use and installed versions; source and Claude-native skills point to the same profile.
- Application evaluation: [protocol](docs/EVALUATION.md) separates fixed-model instruction trials, context/continuation checks, and routing. The owner chose to run real-project trials separately; no productivity/cost result is established.
- Decision record scaffold: python scripts/adr.py new "title" --root TARGET
- Changelog entry: python scripts/changelog.py add "message" --root TARGET
- Optional install extras: --with-session-start, --with-guards, --with-data-guards, --with-native-settings, --with-scoped-rules, --with-ci (persist in ai-kit/settings.json), or --preset minimal|solo|team|strict for the managed set (CI stays explicit). Claude wiring merges owned entries (managed_json in installer state) into .claude/settings.local.json in private mode and .claude/settings.json in team mode; guards are ask rules.
- Generated client configuration derives from ai-kit/project.json (detection fallback): secrets from templates/agent-secrets.ignore plus stack additions, client ignore files and scoped rule formats declared per agent in integrations/agents.json. Workflow skills ai-kit-bootstrap/review/sync-context install with source and Claude copies.
- Client detection: detect markers per agent in integrations/agents.json; preview reports detected_agents/suggested_agents without changing the selection.
- Adapter file parents: an existing `.clinerules` file is detected and preserved when Cline is unselected. Selecting its directory adapter refuses the blocked parent during planning; see [file-parent compatibility](docs/ADAPTER_PATH_FIX.md).
- Optional adapters: gemini, windsurf, cline, roo; machine-readable router providers live in template/ai-kit/router/providers/, with provider choice in template/ai-kit/router/selection.json.
- Verification results and limitations: [implementation record](docs/IMPLEMENTATION.md#verification).
- Local verified environment: Windows, bundled Python 3.12.14. The user supplied a Linux/Python 3.13.16 hosted-check failure; successful hosted matrix execution remains unverified.
- Earlier patch verification: v0.2.1 clean/mixed-layout checks returned no errors or warnings; its patched public snapshot passed 32 tests with 1 unavailable Windows symlink test.
- Earlier v0.2.2 evidence: clean and patched-public-tree suites each executed 45 tests, 43 passed and 2 linked-path checks were unavailable. An actual v0.2.1 installation upgraded successfully and remained stable on rerun; [Manus patch verification](docs/IMPLEMENTATION.md#manus-patch-verification).
- Current fixture correction: 47 local tests executed, 44 passed, 3 linked-path variants unavailable. Kit validation and repackaged archive inventory/bytes/Python 3.10 syntax passed; [Windows CI fixture verification](docs/IMPLEMENTATION.md#windows-ci-fixture-verification). Hosted corrected Windows results remain unverified.
- v0.4.5 (2026-10-10): 92 tests ran, 91 passed, 1 Windows symlink skip; kit validation returned no errors (one pending-Gemini warning). Covers the agent registry, router route/configure, and local/pending provider tiers; [router verification](docs/IMPLEMENTATION.md#router-and-agent-registry-verification). Gemini router IDs and hosted CI remain unverified.
- v0.4.6 (2026-10-10): 109 tests ran, 108 passed, 1 Windows symlink skip; kit validation returned no errors (one pending-Gemini warning). Covers interactive/check onboarding, project-fact detection and project.json drafting, and the adr/changelog helpers; [onboarding verification](docs/IMPLEMENTATION.md#onboarding-and-project-facts-verification). Hosted CI and PyPI publication remain unverified.
- v0.4.7 (2026-10-10): 128 tests ran, 127 passed, 1 Windows symlink skip; kit validation returned no errors (one pending-Gemini warning). Covers key-level client settings merging/migration, ask guards, the session-start script (executed through Git Bash with CRLF and a spaced Windows path), client detection, and evidence-based Node/Python commands; a real v0.4.6 installation upgraded cleanly; [client settings verification](docs/IMPLEMENTATION.md#client-settings-and-detection-verification). Native Claude Code hook delivery/ask enforcement and hosted CI remain unverified.
- Earlier adapter-only verification (2026-10-10, Windows/Python 3.12.14): 133 tests ran, 129 passed, four skipped (symlink, two junction variants, POSIX sh hook). Portable POSIX-error regressions and Python 3.10 grammar checks passed; [verification record](docs/ADAPTER_PATH_FIX.md). Native Linux and corrected hosted CI remain unverified.
- v0.5.0 (2026-10-10, Windows/Python 3.12.14): 161 tests ran, 157 passed, four environment-dependent skips; 48 post-review router/manifest/metrics checks and a separate doctor check passed. Kit validation returned zero errors and one pending-Gemini warning; all scripts/tests passed Python 3.10 grammar. Synthetic profile upgrade preserves facts/selection/private journals and source/native skills, with stable rerun; [release verification](docs/V0_5_0.md). Real application trials, native Linux/hosted CI, Filament application execution, and live model/client controls remain unverified.
- v0.6.4 (2026-10-10, Windows/Python 3.14.6): 185 tests ran, 184 passed, one Windows symlink skip; kit validation returned zero errors and one pending-Gemini warning; Python 3.10 grammar passed. Covers native settings, scoped rules, data guards, presets, and workflow skills; a real v0.5.0 installation upgraded with --preset solo without conflicts and moved private entries to settings.local.json; [release verification](docs/V0_6_4.md). Client formats come from primary docs read 2026-10-10; activation in the actual clients, native Linux, and hosted CI remain unverified.
- v0.6.5 (2026-10-10, Windows/Python 3.14.6): 185 tests ran, 184 passed, one Windows symlink skip; kit validation returned zero errors and one pending-Gemini warning. Adds the root SKILL.md (repository as a skill), the README feature showcase, and the ignore-rule revision with private/team visibility checks; .idea is ignored and untracked in the reference repository.

## Agreements

- Policy defaults and authorization: [Core](template/ai-kit/CORE.md) and [settings](template/ai-kit/settings.json).
- User selected MIT on 2026-10-08; [LICENSE](LICENSE) applies to the kit.
- Actual client activation, live model switching, Docker cleanup, and successful hosted CI are not established by local file checks.
- Last context synchronization: 2026-10-10.
