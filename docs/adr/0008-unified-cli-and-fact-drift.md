# ADR-0008: Unified CLI, fact-drift detection, and non-Latin chat languages

- Date: 2026-10-10
- Status: accepted for the local working distribution

## Context

The distribution ships several standalone scripts (`install.py`, `doctor.py`, `router.py`, `metrics.py`, `adr.py`, `changelog.py`, `check_kit.py`, `docker_test_usage.py`), so the entry surface is a Makefile plus individual `python scripts/...` calls. `PROJECT_CONTEXT.md` and `ai-kit/project.json` hold the same facts in prose and machine-readable form, and nothing checked that they stayed in agreement. `chat_language` accepted only Latin names despite the promise of chat in any language.

## Decision

Add a thin `aikit` dispatcher (`aikit_cli.py`) plus a `pyproject.toml` console script, deriving its version from VERSION; each subcommand forwards to the existing script. Add a doctor check that the module paths in `project.json` and `PROJECT_CONTEXT.md` agree. Relax `chat_language` to any nonempty, control-character-free name up to 60 characters.

## Consequences

The scripts keep their own entry points; the dispatcher is a convenience, not a replacement. A portable wheel install still needs package-data packaging, which stays deferred. Fact drift becomes a doctor warning rather than silent divergence.

## Verification

Covered by the installer/doctor/aikit regressions. [Results](../IMPLEMENTATION.md#verification).
