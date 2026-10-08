---
name: project-continuity
description: Maintain verified project context and AI-KIT instructions while making meaningful project changes.
---

# Project continuity

Apply during project bootstrap and when a task changes project structure, working commands, agreements, or long-term context.

## Brief project profile

- Status: not initialized; see `../../../PROJECT_CONTEXT.md`.
- Verified stack: not established.
- Last context synchronization: not performed.
- Routing baseline: [adaptive router](../../../ai-kit/MODELS.md); runtime capabilities remain unverified until project bootstrap.
- Language agreement: project files and artifacts in English; chat with the user in Russian. Confirmed by the user's 2026-10-05 request; see the [language policy](../../../AGENTS.md#language).
- Docker cleanup agreement: measure project test volumes plus build cache after testing; above 10 GB, clean up verified disposable/reclaimable test resources and remeasure. See [cleanup scope](../../../ai-kit/CONTAINERS.md#post-test-docker-cleanup); resource identities remain unverified until adaptation. Confirmed by the user's 2026-10-06 request.

## Procedure

Follow the [Git operations policy](../../../AGENTS.md#git-operations): do not create/amend commits or push changes unless the user explicitly requests that operation. Complete work as reviewable local changes without routinely asking to commit or push. Agreement confirmed by the user's 2026-10-07 request.

1. Read `../../../PROJECT_CONTEXT.md` and relevant links from `../../../WIKI.md`.
2. Verify new facts against project files, tests, or an accessible system. If the task's Docker dependency is confirmed, record it in the context; treat daemon running state as temporary and check it during work. At bootstrap or a runtime change, verify model capabilities and authorized controls using the [adaptive router](../../../ai-kit/MODELS.md), then update the compact context snapshot with sources and a verification date. Keep unknowns explicit.
3. Perform the task using `../../../AGENTS.md`; open only the relevant stack and risk rules from `../../../ai-kit/`. When creating a Dockerfile, container, or microservice, apply the [Kubernetes-ready standard](../../../ai-kit/CONTAINERS.md); record verified manifest paths and startup requirements in the context.
   After Docker-based testing, apply [post-test cleanup](../../../ai-kit/CONTAINERS.md#post-test-docker-cleanup). Record lasting resource ownership and supported cleanup commands in the context; report actual before/after sizes in the task report. Keep protected data and unverified ownership explicit.
4. If a lasting fact changes, update `PROJECT_CONTEXT.md` and this brief profile together. For a new agreement, update `AGENTS.md` or the relevant rules document; for a decision, update the log/ADR. After any task with file changes, add a brief "what changed and why" entry to `../../../CHANGELOG.md`, including changes to the kit itself. Keep all authored project files and artifacts in English and communicate with the user in Russian according to the language policy in `../../../AGENTS.md`. Project artifacts shown in chat retain English, with Russian explanations.
5. Check that links open and the brief profile agrees with the context.
6. If a new AI-KIT file or adapter is added, check that the root `.gitignore` excludes it according to the agreed policy. Do not automatically remove already tracked files from the index.

Keep the full context in its dedicated file. This skill stores the procedure and a few pointers for quick entry.
