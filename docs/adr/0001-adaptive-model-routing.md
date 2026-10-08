# ADR-0001: Adaptive routing by total cost to a correct result

- Date: 2026-10-05
- Status: accepted AI-KIT baseline policy
- Source: the user's supplied "AI-KIT Adaptive Model Router" request.
- Scope: kit instructions; no project stack, account access, or executable router is assumed.

## Context

The earlier kit preferred Terra for routine implementation and Sol for complex work. The new user policy specifies Luna, Sol 6.1, and exceptional Astra escalation. Cheap failed attempts, unnecessary reviewers, and duplicated context can increase total cost even when each call is inexpensive.

## Options

- Retain the previous fixed role mapping.
- Route every task through the cheapest model or use the most capable configuration universally.
- Choose model, reasoning, service tier, context, and review by task needs and verified runtime capabilities.

## Decision

Adopt the [adaptive router](../../template/ai-kit/router/POLICY.md) as the canonical policy: Luna for bounded work, Sol 6.1 medium for normal engineering, higher effort for demonstrated complexity, and Astra when a plausible capability improvement justifies cost. Diagnose failures before escalation. Use independent service-tier choices, targeted context, supported caching, suitable output budgets, and conditional review/delegation.

## Consequences

The kit can evolve as runtime capabilities and representative outcomes change. It requires truthful capability snapshots and actual verification. Markdown rules provide decisions; automatic switching needs a separate supported integration. New production-critical model choices require evaluation. Explicit user model/budget choices remain authoritative.

If routing underperforms, adjust defaults using observed quality, retries, total cost, and latency; record the reason and synchronize the context, skill, and changelog. Avoid reverting solely on per-call prices.

## Verification

Check linked instructions, JSON decision examples, skill/context consistency, and absence of outdated active routing defaults. During project use, verify executed controls and outcomes separately; no live routing benchmark or API execution is claimed by this kit update.
