# Decision log

Record brief decisions that affect future work. For choices with several options and long-term consequences, create a separate ADR using the [template](adr/0000-template.md) and link it here.

## AI-KIT baseline decisions

These describe the supplied kit's policy, not verified architecture or runtime state of a future project. Preserve or adapt them explicitly during bootstrap.

| Date | Decision | Rationale / link | Status |
| --- | --- | --- | --- |
| 2026-10-05 | Adopt adaptive Luna / Sol 6.1 / Astra routing. | Optimize total cost to a correct result; verify executable controls. [Kit ADR](../ai-kit/adr/0001-adaptive-model-routing.md). | Accepted kit policy |
| 2026-10-05 | Use English for project files/artifacts and Russian for chat with the user. | User's explicit language separation; project artifacts shown in chat retain English. [Language policy](../AGENTS.md#language). | Accepted kit policy |
| 2026-10-06 | Clean up disposable Docker test volumes/cache when combined test usage exceeds 10 GB. | User's cleanup request; verify project ownership, preserve protected data, and remeasure. [Cleanup rule](../ai-kit/CONTAINERS.md#post-test-docker-cleanup). | Accepted kit policy |
| 2026-10-07 | Do not create/amend commits or push without an explicit user request for the particular operation. | User's Git policy; work finishes as reviewable local changes. [Git operations](../AGENTS.md#git-operations). | Accepted kit policy |

## Project decisions

| Date | Decision | Rationale / link | Status |
| --- | --- | --- | --- |
| — | No project decisions yet. | — | — |
