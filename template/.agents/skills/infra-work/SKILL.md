---
name: infra-work
description: "Apply infrastructure rules to confirmed Terraform/Helm paths: state safety, plan review, pinned versions, and lint/validate."
---

# infra-work

Read current ../../../PROJECT_CONTEXT.md and its module map; apply [profile](../../../ai-kit/stacks/INFRA.md) only to confirmed affected paths.
Verify tool versions, state backend, and the environment/workspace before planning or changing providers, modules, or charts.
