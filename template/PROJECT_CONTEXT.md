# Project context

Template: fill only from verified evidence. Project initialization and last verification are not established.

## Purpose and contracts

- Name, purpose, users, current stage: not established.
- Business invariants, public API, security/data boundaries: not established.

## Module map

| Path | Manifest/evidence | Language/framework/version | Active profile(s) | Test/lint/build commands |
| --- | --- | --- | --- | --- |
| Not established | Not established | Not established | None confirmed | Not established |

For a monorepo add one row per verified module; account for cross-module contracts and instructions closer to changed paths.

## Operations

- Startup, CI, deployment, migrations: not established.
- Docker dependency, context/daemon, test project identity, disposable resource inventory, dedicated builder, Kubernetes target: not established.
- Stable commands and paths: not established. Running state and disk measurements belong in task reports.

## AI-KIT installation and runtime

- Installation settings: [settings](ai-kit/settings.json). Accepted bundle/baseline and pending candidates are in local installer state under ai-kit/; verify them before claiming completion.
- Upstream check/applied SHA, source layout, last verification, pending updates: not established. Use [refresh procedure](ai-kit/UPSTREAM.md).
- Provider, available model IDs/controls, pricing/capability source/date, actual switching mechanism: not established. Verify only when needed.
- MCP servers, owners, approved capabilities/data scopes, credential-location classes, and review triggers: not established. Use [MCP posture](ai-kit/MCP.md) before enabling one.
- Explicit local overrides and their evidence: not established; use [Core](ai-kit/CORE.md) and the applicable conventions profile as defaults.
- Decisions and history: [decision log](docs/DECISIONS.md), docs/adr/, and [CHANGELOG](CHANGELOG.md).

## Open questions

Add only unresolved questions that affect the next task. Unknown information is not an invented blocker.
