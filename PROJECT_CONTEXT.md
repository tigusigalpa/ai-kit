# AI-KIT maintainer context

## Verified project

- Purpose: portable instructions, clean project templates, conservative installation and kit validation.
- Stack: Markdown, JSON, and Python standard library; scripts require Python 3.10 or later.
- Source layout: template/ contains installable files; templates/ contains ignore policies; scripts/ and tests/ maintain the distribution.
- Version source: [VERSION](VERSION). The local tree is prepared as v0.3.6; the last published source was v0.2.2. No release or tag refs were returned at the latest read.
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
- Apply installation: python scripts/install.py TARGET --apply
- Installed-project health check: python scripts/doctor.py TARGET
- Optional install extras: --with-session-start, --with-guards, --with-ci (persist in ai-kit/settings.json).
- Verification results and limitations: [implementation record](docs/IMPLEMENTATION.md#verification).
- Local verified environment: Windows, bundled Python 3.12.14. The user supplied a Linux/Python 3.13.16 hosted-check failure; successful hosted matrix execution remains unverified.
- Earlier patch verification: v0.2.1 clean/mixed-layout checks returned no errors or warnings; its patched public snapshot passed 32 tests with 1 unavailable Windows symlink test.
- Earlier v0.2.2 evidence: clean and patched-public-tree suites each executed 45 tests, 43 passed and 2 linked-path checks were unavailable. An actual v0.2.1 installation upgraded successfully and remained stable on rerun; [Manus patch verification](docs/IMPLEMENTATION.md#manus-patch-verification).
- Current fixture correction: 47 local tests executed, 44 passed, 3 linked-path variants unavailable. Kit validation and repackaged archive inventory/bytes/Python 3.10 syntax passed; [Windows CI fixture verification](docs/IMPLEMENTATION.md#windows-ci-fixture-verification). Hosted corrected Windows results remain unverified.

## Agreements

- Policy defaults and authorization: [Core](template/ai-kit/CORE.md) and [settings](template/ai-kit/settings.json).
- User selected MIT on 2026-10-08; [LICENSE](LICENSE) applies to the kit.
- Actual client activation, live model switching, Docker cleanup, and successful hosted CI are not established by local file checks.
- Last context synchronization: 2026-10-10.
