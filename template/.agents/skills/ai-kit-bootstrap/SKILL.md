---
name: ai-kit-bootstrap
description: "Run only when the user explicitly asks to bootstrap AI-KIT: confirm installer drafts and fill PROJECT_CONTEXT and project.json from verified repository evidence."
---

# AI-KIT bootstrap

The user invokes this after the installer applied AI-KIT to the repository.

1. Read ../../../AGENTS.md, ../../../ai-kit/CORE.md, and ../../../ai-kit/settings.json, then follow steps 4-7 of the [bootstrap procedure](../../../ai-kit/BOOTSTRAP.md).
2. Check every installer-suggested module, version, profile, and command in ../../../PROJECT_CONTEXT.md and ../../../ai-kit/project.json against manifests, CI, and runnable checks. Replace drafts with evidence or mark them unknown.
3. Keep project.json and the PROJECT_CONTEXT module map consistent. Generated client permissions and module rules derive from project.json, so ask the user to rerun the installer preview when module paths, profiles, or commands change.
4. Run the confirmed checks that are safe locally; report unavailable ones as unverified.
5. Update continuity pointers and WIKI through the [continuity skill](../project-continuity/SKILL.md), add a CHANGELOG entry, and report open questions. Leave reviewable changes; Core governs commits.
