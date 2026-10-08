# Changelog

After every task with file changes, briefly record what changed and why: features, fixes, internal work, dependencies, documentation, and AI-KIT. Keep new entries under `Unreleased` until a release is confirmed; use verified dates and versions. Tasks without file changes need no entry.

## Unreleased

### AI-KIT

- 2026-10-07: prohibited creating/amending commits and pushing without an explicit user request for the particular operation, including actions through helpers/integrations/other agents. Tasks finish as reviewable local changes without routine commit/push approval prompts. Synchronized instructions, bootstrap, context, continuity skill, engineering rules, README, intent, wiki, and decision log.
- 2026-10-06: added post-test Docker volume/cache cleanup when combined project test usage exceeds 10 GB. Requires measured usage, verified disposable/reclaimable resources, preserved diagnostics and protected data, scoped removal, and a before/after check. Synchronized agent/engineering rules, bootstrap, context, continuity skill, navigation, README, intent, and decision log to control test storage growth without deleting persistent or unrelated data.
- 2026-10-05: separated the language policy: all authored project files and artifacts remain English, while chat with the user uses Russian for questions, plans, progress, explanations, review summaries, and final reports. Project artifacts shown in chat retain English. Synchronized instructions, bootstrap, context, continuity skill, engineering/router rules, README, wiki, and decision log to preserve this distinction.
- 2026-10-05: replaced the former Terra-based defaults with the user's Adaptive Model Router: Luna for bounded tasks, Sol 6.1 for engineering, and justified Astra escalation. Optimizes total cost to a correct result rather than the price of one call.
- 2026-10-05: added runtime capability verification, independent reasoning/service-tier/context decisions, standard/pro criteria, the large-input pricing boundary, cache/output budgets, conditional reviewers/delegation, diagnosed retries, and compact JSON router decisions. Distinguished policy fields from supported execution controls.
- 2026-10-05: synchronized bootstrap, agent/review rules, context and continuity skill, intent, navigation, and README; recorded the routing decision and consequences in a kit ADR. Runtime availability and switching remain explicitly unverified until project adaptation.
- v0.1: added agent instructions, context, a skill, stack and engineering rules, model routing, and the bootstrap prompt.
- Summarized the available voice context; added thin adapters, the skill registry, and stack skills; recovered the user's Laravel agreements from the earlier AI-Kit task.
- Added a Docker daemon check and a request for the user to start it for container-dependent tasks.
- Added a universal `.gitignore` for PHP/Laravel/Moodle/Go, development artifacts, secrets, and local AI-KIT files.
- Added local Go cache directories and `*.out` files to `.gitignore`.
- Clarified the `composer.lock` policy: versioned by default for applications, with an optional exclusion for libraries.
- Clarified that `go.mod` and `go.sum` remain versioned for Go modules.
- Added Python script rules and a skill; `.gitignore` excludes virtual environments, caches, coverage output, and build artifacts while keeping configuration and lockfiles versioned.
- Made `CHANGELOG.md` updates mandatory after every task with file changes to preserve the history of reasons and results, including internal changes and the kit itself.
- Added a mandatory Kubernetes-ready standard for new Dockerfiles, containers, and microservices: portable images, configuration, security, shutdown, health checks, storage, and minimal manifests. Integrated the rule into instructions, context, the skill, and bootstrap so services are ready for Kubernetes from the start.
- 2026-10-04: translated all AI-KIT documents, adapters, rules, templates, and the bootstrap prompt into English; established English as the language for future kit updates.
- 2026-10-04: extended the English language requirement to all authored project content and agent communication, including code, UI text, logs, Git messages, reviews, and reports, so future project work follows one language policy.

### Project

- No verified project changes yet.
