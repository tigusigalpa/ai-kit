# ADR-0003: Data-driven agent registry and offline router helper

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

Agent wiring was hardcoded in the installer as three parallel constants (entry files, valid names, optional integration files), so adding a client meant editing installer code. The router was pure policy: provider JSON declared model roles, but nothing turned that into a concrete recommendation or a generated configuration, and there was no place to record which providers a project actually had.

## Decision

Move the client list and each adapter's entry files into [integrations/agents.json](../../integrations/agents.json), a single registry shared by the installer and the checker. Derive agent names, gated template entries, optional integration files, and Claude skill copies from that registry.

Add [scripts/router.py](../../scripts/router.py), an offline, standard-library helper with two commands: `route` returns a deterministic capability recommendation (level/role/effort plus a resolved provider/model), and `configure` writes a resolved role mapping and a native Aider model file. Record provider availability and role overrides in [selection.json](../../template/ai-kit/router/selection.json).

Keep the distribution offline and credential-free; classify with transparent keyword rules and skip unverified or self-hosted-supplied models rather than inventing model IDs.

## Consequences

Adding a client is a data change, not installer code; the checker validates the registry against template entries and integration sources. `route`/`configure` respect the existing "no switching runtime" boundary: they advise and generate, never switch or store credentials.

## Verification

Router, registry, and provider-schema regressions run alongside the installer/checker/doctor suites. [Results](../IMPLEMENTATION.md#verification).
