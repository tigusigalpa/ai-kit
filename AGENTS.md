# AI-KIT maintainer instructions

Read [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) before changes. This repository builds instructions and installation tools; it is not a Laravel/Go/Moodle application.
Use the [Core](template/ai-kit/CORE.md) for language, Git authorization, and fact verification. Preserve the user's defaults in [settings](template/ai-kit/settings.json).

Follow plan -> implement -> test -> review -> document. Keep template rules in their canonical owner; [policy ownership](docs/IMPLEMENTATION.md#policy-ownership) lists those owners.
Project templates must contain no kit history, source-check snapshots, or assumed stack facts.
After file changes update the root [CHANGELOG](CHANGELOG.md); update maintainer context and the [continuity skill](.agents/skills/project-continuity/SKILL.md) when facts/procedures change.

Run python scripts/check_kit.py and python -m unittest discover -s tests -v for affected installer/checker behavior.
Review file preservation, conflicts, symlinks/path boundaries, private/team visibility, links, registry, and upgrade behavior. Report unavailable runtime checks.
Use [WIKI](WIKI.md) to find relevant resources; do not load every profile or provider for ordinary maintenance.
