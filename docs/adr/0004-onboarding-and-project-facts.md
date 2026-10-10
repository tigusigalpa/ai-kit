# ADR-0004: Interactive onboarding and machine-readable project facts

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

Installation required composing a flag list by hand, and the installer only detected that a stack profile was present — not the language version or the project's test/lint/build commands. The `PROJECT_CONTEXT.md` module map therefore stayed mostly `not established` until a human filled it in.

## Decision

Add `--interactive` to prompt for mode, language, conventions, agents, and extras, and `--check` to run the project doctor immediately after a successful `--apply`. Add a `Makefile` front-door wrapping the common commands.

Add a schema-versioned `ai-kit/project.json` and detect, per module, the manifests, language, version, and suggested commands from go.mod, pyproject.toml, package.json, and composer.json. Draft both `PROJECT_CONTEXT.md` and `project.json` from that evidence on a fresh install, marked as suggested until bootstrap confirms them; preserve existing project facts.

Add `scripts/adr.py new` and `scripts/changelog.py add` to lower the cost of the document step.

## Consequences

Detected versions and commands are drafts, never verified facts, and existing context/history stays untouched. A `Makefile` is a convenience over the canonical Python commands, not a replacement for them.

## Verification

Onboarding, detection, project.json, and helper regressions run with the installer/checker/doctor suites. [Results](../IMPLEMENTATION.md#verification).
