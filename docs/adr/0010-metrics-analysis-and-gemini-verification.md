# ADR-0010: Measurement analysis for routing and Gemini verification

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

Local measurements aggregated only by experiment/arm, so the per-provider evidence needed to tune `ai-kit/router/selection.json` had to be assembled by hand. The Gemini provider remained a pending scaffold, so route/configure could not resolve a Gemini model.

## Decision

Add `metrics.py analyze` to aggregate reviewed tasks per provider (attempts, success rate, cost coverage, cost per correct result, models/efforts). It is descriptive and read-only: it informs `selection.json` but never rewrites it. Verify the Gemini cheap/work/escalation model IDs against current primary documentation and record them in `gemini.json`; keep effort unknown until Gemini's thinking levels are confirmed.

## Consequences

Routing feedback stays evidence-based and conservative, with no auto-mutation or price lookup. Gemini now resolves real model IDs, but its reasoning effort remains an unknown rather than a fabricated control.

## Verification

Covered by metrics, router, and checker regressions. [Results](../IMPLEMENTATION.md#verification).
