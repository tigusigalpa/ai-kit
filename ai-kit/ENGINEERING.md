# Engineering cycle

Use **plan → implement → test → review → document**. The depth of each step depends on task risk and scope.

## Plan

- Establish the desired behavior and acceptance criteria. Find affected contracts, tests, and migrations.
- For a nontrivial task, record a short plan and risks. If information is missing, inspect the repository or ask a precise question.

## Implement

- Make a coherent, reviewable change. Add dependencies and infrastructure only when they benefit the task.
- Respect existing interfaces, style, and supported versions. Protect input and output boundaries.
- Use English for code identifiers, new file names, comments/docstrings, tests and synthetic fixtures, UI text, errors, and logs. Preserve external contracts and real input data when applying the language policy in `../AGENTS.md`.
- Design new Dockerfiles, containers, and microservices to be Kubernetes-ready from the start. When working on them, read the [container standard](CONTAINERS.md) and meet its applicable acceptance criteria.
- If the task's code, local services, or tests depend on Docker, check Docker daemon availability on the user's machine. If it is stopped, ask the user to start Docker Desktop/Engine; after their response, repeat the availability check and continue dependent steps. Proceed with independent work immediately. Tasks without Docker do not require a startup request.

## Test

- Run targeted tests first, then broaden checks as needed. Use commands from the project rather than from the template.
- Add tests for changed behavior and important regressions. For a simple documentation change, checking links and content is sufficient.
- If a check is unavailable, report the command, reason, and remaining risk. Do not claim tests passed if they were not run.
- After Docker-based tests, preserve diagnostics and apply [post-test Docker cleanup](CONTAINERS.md#post-test-docker-cleanup): measure project test volumes plus build cache, clean up verified disposable/reclaimable resources when their combined size exceeds 10 GB, then verify and report remaining usage. Apply the same check after failed/interrupted tests when access is available; preserve persistent, active, and unrelated data.
- When Codecov is configured, use meaningful diff/patch coverage: the earlier kit's target is at least 90% of changed lines, with an overall coverage decrease of no more than 0.5 percentage points. For critical branches, cover all important behavior. Check assertions, negative scenarios, and authorization in addition to percentages. Connect PR comments and required checks to actual CI and the current commit; claim them active only after configuration.

## Review

- Before completion, review the diff for compliance with the request, edge cases, backward compatibility, error handling, logging, and performance where relevant.
- For code handling data, check authorization, injections, secrets, personal data, access rights, and dependent services. Keep secrets out of code, tests, logs, and documents.
- Match reviewers to risk using [MODELS.md](MODELS.md): normal engineering uses tests and lightweight self-review; complex changes use Sol medium/high review; critical architecture/security/trading correctness requires independent Sol high/xhigh review when available. Astra review needs a specific capability justification. Resolve supported findings and report unavailable required review; never call self-review independent.

## Migrations

- Check the current schema and actual tool versions. Describe data changes, deployment order, and compatibility between old and new code.
- For risky changes, use a staged approach: introduce a compatible schema, migrate/backfill data, then remove the old path after verification. Provide recovery or rollback where possible.
- Do not run production migrations without explicit authorization. Verify migrations in an available test environment with representative data.

## Document

- Complete the task as reviewable local changes under the [Git operations policy](../AGENTS.md#git-operations). Do not create/amend commits or push unless the user explicitly requests the particular operation; task completion or passing checks does not authorize either action.
- Write all project files and artifacts in English, including documentation, context, wiki, changelog, README, skills, reusable prompts, internal handoffs, structured decisions, branch/commit/PR text, release notes, and saved reviews/reports. Communicate with the user in Russian in chat, including progress and final reports; keep project artifacts shown there in English with Russian explanations. Follow the [language policy](../AGENTS.md#language).
- Update documentation for changed behavior, commands, and contracts. Keep current operational facts in `PROJECT_CONTEXT.md` without duplicating them elsewhere.
- Record significant decisions in `docs/DECISIONS.md`; use the ADR template when alternatives and long-term consequences matter.
- For every task with file changes, update `CHANGELOG.md` in the same change: briefly describe what changed and why, including fixes, internal work, dependencies, documentation, and the kit. Put kit entries in its section; do not invent dates or versions. Synchronize context and the skill when their facts or procedures are affected.
- When creating or updating a project README, show CI, tests, Codecov, CodeQL, release, and license badges only for actual, working checks or established releases/licenses. Choose GitHub Actions and security checks for the stack; do not add fictitious statuses.
