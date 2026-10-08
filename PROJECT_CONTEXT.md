# PROJECT_CONTEXT

> Template. Bootstrap replaces "not established" only with sourced facts. Last verification: not performed.

## Project overview

- Name and purpose: not established.
- Users and key scenarios: not established.
- Current stage and next goal: not established.

## Verified stack

- Languages, frameworks, versions: not established.
- Data storage and external integrations: not established.
- Evidence: provide paths to manifests, lockfiles, configuration, or code.

## Code map

- Entry points and main modules: not established.
- Test locations: not established.
- Migration locations: not established.

## Working with the project

- Installation and startup: not established.
- Docker dependency for local development/tests: not established; provide supporting files and commands if applicable.
- Verified test, lint, and build commands: not established.
- CI and deployment environment: not established.
- Container images, Kubernetes manifests, and target Kubernetes version: not established; provide actual paths and requirements if applicable.
- Docker test project identity, disposable volume inventory, builder/cache ownership, and supported cleanup commands: not established; verify during adaptation. Do not store temporary disk-usage measurements as lasting project facts.

## Model runtime and routing

- AI-KIT baseline policy: [adaptive router](ai-kit/MODELS.md); Luna for bounded work, Sol 6.1 for engineering, Astra for justified escalation. This is a policy agreement, not evidence of runtime availability.
- Environment/provider, available model IDs, and authorized switching mechanism: not established.
- Supported reasoning efforts/modes, service tiers, tool/endpoint support, and provider/region restrictions: not established.
- Current pricing sources, input/output limits, large-input threshold, and cache support: not established.
- User model/budget/latency constraints and required independent-review access: not established.
- Capability snapshot source and last verification date: not established. During bootstrap, record compact sourced findings; refresh when the runtime changes. Keep credentials out of this file.

## Constraints and agreements

- Business invariants and contracts: not established.
- Security and data requirements: not established.
- AI-KIT container agreement: new Dockerfiles, containers, and microservices are Kubernetes-ready according to [ai-kit/CONTAINERS.md](ai-kit/CONTAINERS.md). Verify Kubernetes availability in the actual project separately.
- Docker cleanup agreement: after testing, measure the combined size of the project's test volumes and build caches; above 10 GB, remove only verified disposable/reclaimable test resources and remeasure. Preserve persistent, active, shared, and unrelated data. See [post-test cleanup](ai-kit/CONTAINERS.md#post-test-docker-cleanup). Confirmed by the user's 2026-10-06 request; actual resource identities and sizes remain unverified.
- Project and AI-KIT language: English for all authored files and artifacts, including instructions, context, wiki, changelog, README, skills, code, prompts, and saved reports, according to the [language policy](AGENTS.md#language).
- Chat language: Russian for communication with the user, including questions, plans, progress, explanations, review summaries, and final reports. Project artifacts shown in chat retain English, with Russian explanations. Agreement confirmed by the user's 2026-10-05 request.
- Architectural decisions: see `docs/DECISIONS.md` and `docs/adr/`.
- Git agreement: do not create/amend commits or push changes without the user's explicit request for that particular operation. Leave work as reviewable local changes; do not routinely request commit/push approval at completion. See [Git operations](AGENTS.md#git-operations). Confirmed by the user's 2026-10-07 request.

## Open questions

- Not established. Add only questions that affect the next work.

## Update rule

After significant facts change, update this file and the brief profile in `.agents/skills/project-continuity/SKILL.md`; record the verification date and source. Do not turn this file into a task diary or a copy of source code.
