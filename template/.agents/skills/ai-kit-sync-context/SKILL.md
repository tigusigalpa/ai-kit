---
name: ai-kit-sync-context
description: "Run only when the user explicitly asks to synchronize AI-KIT project context, WIKI, decisions, and changelog after work in this session."
---

# AI-KIT context sync

1. List what changed in this session (files, commands, agreements, decisions) from the conversation and Git status.
2. Follow steps 1, 3, 4, and 6 of the [continuity skill](../project-continuity/SKILL.md) for those changes only; keep task logs out of ../../../PROJECT_CONTEXT.md.
3. Record significant decisions in docs/DECISIONS.md or a new ADR and add a concise CHANGELOG entry.
4. When module paths, profiles, or commands changed, update ../../../ai-kit/project.json and ask the user to rerun the installer preview so generated client permissions and module rules follow.
5. Report updated files and the facts that remain unverified.
