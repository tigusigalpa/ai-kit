# Project agent instructions

Read [Core](ai-kit/CORE.md), [settings](ai-kit/settings.json), and the current [PROJECT_CONTEXT](PROJECT_CONTEXT.md) before changes.
Use [WIKI](WIKI.md) and the context's module map to load only applicable rules. Verify claims; keep unknowns explicit.
If upstream is configured, check once per task through [UPSTREAM](ai-kit/UPSTREAM.md), preserve local agreements, and read reconciled rules.

Follow plan -> implement -> test -> review -> document using [ENGINEERING](ai-kit/ENGINEERING.md).
For a confirmed stack use the [registry](ai-kit/SKILLS.md); nested instructions and actual supported versions guide the affected paths.
For an explicit bootstrap, review, or context-sync request follow the matching ai-kit workflow skill in the registry.
For container-dependent work read [CONTAINERS](ai-kit/CONTAINERS.md); for auth/data/dependency boundaries read [SECURITY](ai-kit/SECURITY.md).
Ordinary execution uses the available model and relevant checks. Load the [full router](ai-kit/router/POLICY.md) only for orchestration, routing/runtime setup, or routing review; never claim an unsupported switch.

Synchronize verified facts and continuity pointers when they change; record significant decisions in docs/ and update CHANGELOG after tasks with file changes.
Report changed behavior, checks performed, and material unverified work. Host policy and explicit user instructions remain authoritative.
