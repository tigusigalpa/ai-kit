# AGENTS.md

Primary instructions for agents working on this project. Explicit user requests and instructions closer to the code being changed take precedence.

## Language

### Project content: English

- Use English for all authored project files and artifacts, including `AGENTS.md`, `WIKI.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md`, `README.md`, every `SKILL.md`, and all other working files.
- This includes code identifiers and new file names, comments and docstrings, documentation, context, skills, tests and synthetic fixtures, UI text, errors, logs, reusable prompts, structured router decisions, internal agent instructions/handoffs, branch names, commit messages, PR descriptions, and release notes. Plans, reviews, and reports saved as project artifacts also use English.
- Preserve exact external identifiers, protocol values, quoted evidence, and user data. Additional project languages require an explicit user request. Translate existing content within the task scope; preserve public contracts when changing identifiers.

### Chat with the user: Russian

- Communicate with the user in Russian: questions, plans, progress updates, explanations, review summaries, and final reports in the chat. Use another chat language only when the user explicitly requests it.
- Keep code, commands, reusable project text, and structured data in English when presenting them in chat; explain them in Russian. A project artifact shown in chat retains the project language. Chat language does not change file contents or project conventions.

## Before making changes

1. Read the current `PROJECT_CONTEXT.md`; use `WIKI.md` to find only the documents and code relevant to the task.
2. Verify important claims against the repository, configuration, tests, or an accessible system. Do not invent the stack, commands, requirements, decisions, or environment state. Mark unknowns as unknown.
3. If the context file is missing or outdated, first restore the minimum verified information. Do not replace verification with assumptions.

## Git operations

- Do not create or amend commits, and do not push changes, unless the user explicitly requests the particular operation. This applies to direct Git commands and to helpers, hooks, integrations, automations, or delegated agents that perform it on your behalf.
- Requests to implement, fix, test, review, document, bootstrap, or finish a task do not authorize committing or pushing. Permission to commit does not also authorize a push, and vice versa.
- Complete the work as reviewable local changes, preserve the user's existing work, and report changed files and verification results. Do not routinely ask to commit or push at task completion.

## Working rules

- Follow **plan → implement → test → review → document**, with depth proportional to the task. A simple change needs a short plan and an appropriate check; a risky change needs explicit steps and acceptance criteria.
- Change the smallest coherent scope. Preserve existing project conventions. Read [ai-kit/ENGINEERING.md](ai-kit/ENGINEERING.md) for the relevant checks.
- Before programming, determine whether the task needs project containers. If Docker is required, check daemon availability on the user's machine. If it is stopped, ask the user to start Docker Desktop or Docker Engine and repeat the dependent checks after startup; do not claim container checks passed before running them.
- After Docker-based testing, measure the combined test-volume and build-cache size for the current project. If it exceeds 10 GB, clean up verified disposable test volumes and reclaimable test cache under the [post-test cleanup rule](ai-kit/CONTAINERS.md#post-test-docker-cleanup). Preserve persistent/active/shared resources, then verify and report before/after usage.
- Make all new Dockerfiles, containers, and microservices Kubernetes-ready from the start, following [ai-kit/CONTAINERS.md](ai-kit/CONTAINERS.md): portable images, external configuration, secure startup, graceful shutdown, health checks, and minimal manifests suited to the workload. This requirement also applies to local development with Docker Compose.
- Apply stack rules only after confirming the stack: [Laravel](ai-kit/stacks/LARAVEL.md), [Go](ai-kit/stacks/GO.md), [Python](ai-kit/stacks/PYTHON.md), [Moodle](ai-kit/stacks/MOODLE.md). Open the corresponding skill from the [registry](ai-kit/SKILLS.md) if the environment has not activated it. Project rules and actual package versions take precedence over general guidance.
- Apply the [adaptive model router](ai-kit/MODELS.md): optimize total cost to a correct result. Use Luna for bounded work, Sol 6.1 as the engineering default, and Astra only for justified capability escalation. Verify runtime controls; select reasoning effort, service tier, and relevant context separately. Diagnose failures before escalating and never claim an unsupported switch.
- Match review depth to risk. Use separate reviewers or multiple agents only when they materially improve the outcome and governing instructions authorize them; avoid default delegation and duplicated context.
- Keep context small: open relevant files and ranges, avoid loading the entire repository without a reason, and do not repeat large tool outputs.
- Follow [`.gitignore`](.gitignore): AI-KIT and adapters remain local. When adding an AI file, check its ignore rule; do not force it into Git without an explicit request.

## Completion

- Report what changed, how it was checked, and what remains unverified.
- When verified facts, agreements, or work procedures change, update `PROJECT_CONTEXT.md` and `.agents/skills/project-continuity/SKILL.md` in the same task; refresh links in `WIKI.md`.
- Record significant architectural decisions in `docs/DECISIONS.md`; add an ADR in `docs/adr/` for decisions with alternatives and consequences.
- After every task that changes project files, update `CHANGELOG.md`: briefly record what changed and why. Include fixes, internal changes, dependencies, documentation, and AI-KIT changes; cover more than user-facing features. Use `Unreleased` until a release date or version is confirmed. Tasks without file changes need no entry.
- Update AI-KIT as actual project needs emerge. Do not add speculative rules.
- When creating or changing `SKILL.md` or its resources, follow the [skill lifecycle](ai-kit/SKILLS.md): keep the contract, resources, and checks synchronized.

## Code review rules

Look for behavioral errors, contract violations, regressions, weak or missing tests, data leaks, authorization issues, and migration risks. Identify the specific file, scenario, and severity. Formatting already checked by a linter should not be the main review finding.
