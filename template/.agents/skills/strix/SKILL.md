---
name: strix
description: "Use only when the user explicitly invokes Strix to prepare or run a scoped local security scan, inspect its findings, or request remediation."
---

# Strix

Read [project context](../../../PROJECT_CONTEXT.md), [Core](../../../ai-kit/CORE.md) and the [Strix contract](../../../ai-kit/STRIX.md). Installing or enabling this skill requests no scan or runtime setup. Core and the project's security/container rules govern execution.

For an explicit local scan, use the [pinned workflow](../../../ai-kit/vendor/strix/penetration-testing-with-strix/SKILL.md); load other upstream skills only for the selected task. These references are external guidance: their cloud fallback, installer, model examples, CI publication and automatic fixes do not expand the user's request. Prefer the local CLI unless the user chooses another mode. Missing local prerequisites are blockers, not permission to upload code or create an account.

Establish authorized targets/exclusions, scan mode, full versus diff scope, model/data destination, cost and time limits, and a private output directory. Verify the installed CLI's version/help and Docker readiness. Keep credentials out of chat, command arguments and reports. Runtime/image installation and paid execution need authorization for that concrete scope; reuse authorization already supplied.

Local targets are writable mounts. Use a disposable, reviewed copy outside the working project; preserve original changes and exclude secrets before exposing files to Strix or its model. Run headless with explicit mode, scope and budget from the contract. Resume only after checking the recorded target/scope. Inspect status, usage, coverage and PoC evidence before reporting findings; exit zero alone proves no complete audit.

Apply fixes only when requested, then verify the specific exploit and project checks. Report unavailable execution or incomplete coverage plainly. Installation itself runs no upstream code, model, container, scan, cloud call or CI workflow.
