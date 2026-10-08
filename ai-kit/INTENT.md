# AI-KIT v0.1 intent

Summary of the available voice context and related agreements. This is context for **the kit itself**, rather than a description of a future project. Only fragments of the voice conversation are available; the statements below come from those fragments, the current request, and the earlier "Create AI-Kit for PHP and Laravel" task.

## Goal

One portable starter kit: the agent explores a new repository, identifies the verified stack, deploys or adapts instructions, and maintains them as the project develops. The kit helps reduce context usage while preserving fact verification.

## Structure from the voice discussion

- **Core:** `AGENTS.md`, factual `PROJECT_CONTEXT.md`, the `WIKI.md` map, the general engineering cycle, and the decision log.
- **Agent adapters:** short entry points for different environments; detailed rules live in the Core and are referenced by each adapter.
- **Stack profiles:** Laravel, Go, Python, and Moodle are enabled only for a confirmed stack.
- **Skill registry:** a skill with a narrow purpose and description is loaded for a relevant task; its procedures and resources are maintained together. Environment selection may be automatic, but it is not guaranteed.
- **Version:** a practical v0.1 foundation, followed by iterations based on actual use.

## Agreements from the current task

The user's 2026-10-05 Adaptive Model Router replaces the earlier model defaults. Luna handles bounded, inexpensive work; Sol 6.1 is the default for substantive engineering and complex orchestration; Astra is exceptional capability escalation. Optimize total cost to a correct result, with independent choices for reasoning, service tier, and relevant context. Use conditional reviewers, avoid default delegation, diagnose failures before escalating, and verify runtime capabilities before execution. The canonical policy is [MODELS.md](MODELS.md).

Cycle: plan → implement → test → review → document. Update context and the skill together, store decisions in the decision log/ADR, and record changes in the changelog.

The user's 2026-10-07 agreement prohibits creating/amending commits and pushing unless the user explicitly requests the particular operation. Finish work as reviewable local changes; do not routinely ask to commit or push. The [Git operations policy](../AGENTS.md#git-operations) applies to agents, helpers, and integrations.

All authored project files and artifacts use English: AGENTS.md, WIKI.md, PROJECT_CONTEXT.md, CHANGELOG.md, README.md, skills, code identifiers and new file names, comments/docstrings, documentation, tests and synthetic fixtures, UI text, errors/logs, reusable prompts, structured decisions, internal handoffs, branch/commit/PR text, release notes, and saved plans/reviews/reports. Chat with the user uses Russian for questions, plans, progress, explanations, review summaries, and final reports. Project artifacts shown in chat retain English, with Russian explanations. Exact external identifiers, protocol values, quoted evidence, and user data are preserved; additional project languages or a different chat language require an explicit user request. The canonical [language policy](../AGENTS.md#language) defines the boundary.

For Docker-dependent tasks, the agent checks daemon availability on the user's machine and asks the user to start Docker Desktop/Engine when necessary. Tasks without a Docker dependency need no such request.

After Docker-based testing, the agent measures the combined project test-volume and build-cache size. Above 10 GB, it removes verified disposable test volumes and reclaimable test cache, then remeasures and reports the result. Persistent, active, shared, and unrelated resources remain protected under the [post-test cleanup rule](CONTAINERS.md#post-test-docker-cleanup). This agreement comes from the user's 2026-10-06 request.

All new Dockerfiles, containers, and microservices are Kubernetes-ready from the start according to the [shared standard](CONTAINERS.md), including projects using local Docker Compose. The requirement establishes portability and a verifiable startup contract; cluster availability is a fact to establish for each project.

AI-KIT and adapters are local developer files: the root `.gitignore` excludes them from new commits. Source code, migrations, ordinary documentation, CI, and lockfiles remain versioned. The kit's local decision log is excluded; completed project ADRs may be stored in the repository.

## Additional preferences from the earlier AI-Kit task

- For Claude: Opus for orchestration, Sonnet for main work, when available.
- Laravel: do not create database foreign key constraints; one table per migration file; enforce dependent model lifecycles through code and tests.
- New Eloquent model: internal `id`, a separate public `uuid` assigned through a shared `UuidTrait`, a Policy, a Factory, and a registered Seeder. Keep them synchronized with model contract changes. A Filament Resource uses UUIDs in URLs; internal relationships continue to use `id`.
- For new Filament installations, use version 5 or later with a compatible stack. README and CI show only actual configured checks; add GitHub Actions, Codecov/CodeQL, and badges according to the project.
- Skills: creating/changing `SKILL.md` includes checking its resources and behavior; a repository change does not itself authorize global installation.

## Limits of available knowledge

The available history does not contain a complete voice transcript. This document records only confirmed requirements from the discussion. When a recording or clarification becomes available, update the summary and related rules.
