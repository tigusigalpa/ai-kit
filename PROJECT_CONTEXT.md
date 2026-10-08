# AI-KIT maintainer context

## Verified project

- Purpose: portable instructions, clean project templates, conservative installation and kit validation.
- Stack: Markdown, JSON, and Python standard library; scripts require Python 3.10 or later.
- Source layout: template/ contains installable files; templates/ contains ignore policies; scripts/ and tests/ maintain the distribution.
- Version source: [VERSION](VERSION). The working distribution is prepared locally; no tag or GitHub release has been created.
- Project ownership: root documentation/history describe AI-KIT; template/ project context and history remain uninitialized.

## Source verification

- Canonical repository: https://github.com/tigusigalpa/ai-kit, tracking main.
- Last checked: 2026-10-08; main resolved to 5dd530b9046fa09742f2ac13e22fabcbde70d749.
- Remote snapshot: older root distribution with .gitignore_real. This new template layout is not published by the agent.
- Local work is based on the previously reviewed distribution; no remote revision is claimed as a fully applied installation baseline.

## Working commands

- Validation: python scripts/check_kit.py
- Behavioral tests: python -m unittest discover -s tests -v
- Install preview: python scripts/install.py TARGET
- Apply installation: python scripts/install.py TARGET --apply
- Verification results and limitations: [implementation record](docs/IMPLEMENTATION.md#verification).
- Local verified environment: Windows, bundled Python 3.12.14; structural checks and behavioral suite completed on 2026-10-08. Hosted Linux/Python 3.10/3.13 execution remains unverified.

## Agreements

- Policy defaults and authorization: [Core](template/ai-kit/CORE.md) and [settings](template/ai-kit/settings.json).
- User selected MIT on 2026-10-08; [LICENSE](LICENSE) applies to the kit.
- Actual client activation, live model switching, Docker cleanup, and hosted CI execution are not established by local file checks.
- Last context synchronization: 2026-10-08.
