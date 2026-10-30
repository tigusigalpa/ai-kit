# ADR 0017: Installer flag schema as the documentation source, and declared Gemini thinking levels

Status: accepted for code, local tests and Docker smoke; hosted release runs are separate.

## Context

Installer options were documented by hand in the flag guide, SKILL.md and the separate documentation site. Each release risked drift: after v1.4.6 the site still lacked `--docker-cleanup` and generated a `doctor --fix` command whose meaning had changed. Several options had no help text, so `aikit install --help` and any generated reference had nothing to show for them.

Gemini routing resolved real model IDs since v0.9 but treated reasoning effort as unknown, because thinking controls had not been confirmed against primary documentation. The current thinking documentation lists `thinking_level` with levels that differ per model.

## Decision

- `scripts/install.py` builds its parser in `build_parser(root)`; `flag_schema(root)` derives a JSON description from it: value type, choices, repeatability, mutual exclusions, the saved `ai-kit/settings.json` key, the fresh default, help text and presets.
- `aikit flags` prints the schema; `integrations/installer-flags.json` is the committed copy for documentation tools. Kit validation fails when that copy differs from the parser, when the flag guide misses or invents an option or misses a choice value, or when SKILL.md does not mention every option and value.
- Every installer option carries help text.
- The Gemini provider declares per-role thinking levels from the documentation (Flash-Lite: minimal/low/medium/high; Flash and Pro: low/medium/high) with each model's documented default as the role default. Unsupported routed levels fall back to the role default, as for other providers.

## Consequences

Changing an installer option now requires regenerating the schema and updating the guide and SKILL.md in the same change; the checker names what is missing. External tools can read one file per release tag instead of re-deriving options. The schema has no version field, so it changes only when options do. Gemini route output now includes an effort; requests must translate it to the target API's own thinking field, and other Gemini request schemas still need their field names confirmed.
