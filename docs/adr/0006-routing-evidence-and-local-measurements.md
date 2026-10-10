# ADR-0006: Evidence-based recommendations and optional local measurements

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

The offline classifier diverged from the canonical capability ladder, matched fragments inside unrelated words/file names, and ignored explicit selection effort. Russian task descriptions fell through to the engineering default. There was no local accounting contract to test whether instruction/context or routing changes improved cost to a correct result. Filament work depended on a broad Laravel wrapper despite distinct UI/version/authorization concerns.

## Decision

Keep the capability ladder in [POLICY](../../template/ai-kit/router/POLICY.md); regression tests compare its table with the implementation mapping. Classify English/Russian operations with bounded patterns and explicit risk/component evidence, retaining manual overrides. Expose signals, requested effort, declared controls, and unresolved models separately. Level 6 requires explicit diagnosis; recommendations do not execute tasks or switch clients. Arbitrary model IDs do not inherit another model's effort capabilities.

Add a conditional Filament profile/skill and suggest it from known Composer dependencies, including component-only installs and lock evidence. Actual versions and use remain bootstrap facts. Keep personal conventions in OWNER and retain the existing minimum-context/module-map procedure.

Measure only on request through a local schema and journal. Store opaque IDs and actual executed settings, nullable telemetry, reviewed outcomes, all attempts, rework, and escalation. Ignore runtime journals in both sharing modes; never install a populated journal or overwrite it on upgrades. Costs include unsuccessful work; incomplete coverage or mixed currency leaves cost per correct result unknown.

Use a [fixed-model real-project protocol](../EVALUATION.md) to evaluate instructions first and routing separately. Real-project trials are deferred by the owner's choice. Multi-agent orchestration remains deferred until measured benefit and explicit authorization justify it.

## Consequences

Rules remain conservative heuristics and can over/under-route; explicit evidence and review are necessary. Unknown custom/local capability controls stay null until configured. Journaling is manual and opt-in, so coverage depends on runtime evidence supplied by the evaluator. The helper protects cooperating writers with an exclusive lock; interrupted locks require manual investigation. These choices add no network dependencies or always-loaded provider/profile context.

## Verification

Tests cover policy consistency, multilingual/risk regressions, effort support/precedence, scoped dependency suggestions, preservation/skill upgrades, measurement accounting/validation, and boundary guards. The kit checker verifies links, registries, template isolation, and private/team visibility. [Release verification](../V0_5_0.md) records actual results and unavailable checks.
