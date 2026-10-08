# AI-KIT maintainer context

## Verified project

- Purpose: portable instructions, clean project templates, conservative installation and kit validation.
- Stack: Markdown, JSON, and Python standard library; scripts require Python 3.10 or later.
- Source layout: template/ contains installable files; templates/ contains ignore policies; scripts/ and tests/ maintain the distribution.
- Version source: [VERSION](VERSION). The working distribution is prepared locally; no tag or GitHub release has been created.
- Project ownership: root documentation/history describe AI-KIT; template/ project context and history remain uninitialized.
- Onboarding: root README is the practical entry guide; its command examples match the installer CLI and distinguish application installation from reference-repository overlays.

## Source verification

- Canonical repository: https://github.com/tigusigalpa/ai-kit, tracking main.
- Last checked: 2026-10-08; main resolved to 73707036c1098d8c1c81ab2c51d723c3d521f6b8.
- Remote snapshot: published v0.2 template layout overlaid on v0.1; old ai-kit/ paths and .gitignore_real remain.
- Rebuilt all 91 tracked blobs from this revision with verified Git object hashes and reproduced the supplied five missing-heading errors.
- Current patch 0.2.2 is local and unpublished by the agent. Compatibility pointers replace known old rule documents; application installation still uses template/ exclusively.
- Independently reproduced three Manus installer findings against v0.2.1: candidate overwrite, lost adapter tracking, and unsupported/mixed-type state failure. Patch 0.2.2 preserves candidates, blocks unresolved adapter retirement, and validates inputs before planning; [audit disposition](docs/MANUS_REVIEW.md).
- Published run 37810446904 was confirmed failed at the checked SHA. Repository metadata confirmed a description, MIT, empty topics/homepage, no releases, and no tag refs. Community Profile details remain unverified.

## Working commands

- Validation: python scripts/check_kit.py
- Behavioral tests: python -m unittest discover -s tests -v
- Install preview: python scripts/install.py TARGET
- Apply installation: python scripts/install.py TARGET --apply
- Verification results and limitations: [implementation record](docs/IMPLEMENTATION.md#verification).
- Local verified environment: Windows, bundled Python 3.12.14. The user supplied a Linux/Python 3.13.16 hosted-check failure; successful hosted matrix execution remains unverified.
- Earlier patch verification: v0.2.1 clean/mixed-layout checks returned no errors or warnings; its patched public snapshot passed 32 tests with 1 unavailable Windows symlink test.
- Current local evidence: clean and patched-public-tree v0.2.2 suites each executed 45 tests, 43 passed and 2 linked-path tests were unavailable. Kit validation returned no errors/warnings; 85 archive source files and Python 3.10 syntax were verified. An actual v0.2.1 installation upgraded successfully to v0.2.2 and remained stable on rerun. Details: [Manus patch verification](docs/IMPLEMENTATION.md#manus-patch-verification).

## Agreements

- Policy defaults and authorization: [Core](template/ai-kit/CORE.md) and [settings](template/ai-kit/settings.json).
- User selected MIT on 2026-10-08; [LICENSE](LICENSE) applies to the kit.
- Actual client activation, live model switching, Docker cleanup, and successful hosted CI are not established by local file checks.
- Last context synchronization: 2026-10-08.
