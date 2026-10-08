# Skill registry

Codex repository skills live in `.agents/skills/<name>/SKILL.md`. The environment sees the name and description and may select a relevant skill; automatic activation is not guaranteed. `AGENTS.md` provides an explicit route when selection has not occurred.

| Skill | When to use | Profile |
| --- | --- | --- |
| [project-continuity](../.agents/skills/project-continuity/SKILL.md) | Bootstrap and changes to long-term context/procedures | `PROJECT_CONTEXT.md` |
| [laravel-work](../.agents/skills/laravel-work/SKILL.md) | Changes to a confirmed Laravel project | `stacks/LARAVEL.md` |
| [go-work](../.agents/skills/go-work/SKILL.md) | Changes to a confirmed Go project | `stacks/GO.md` |
| [python-work](../.agents/skills/python-work/SKILL.md) | Changes to confirmed Python scripts, packages, and tests | `stacks/PYTHON.md` |
| [moodle-work](../.agents/skills/moodle-work/SKILL.md) | Changes to a confirmed Moodle installation/plugin | `stacks/MOODLE.md` |

## Lifecycle

- A new `SKILL.md` creates a skill; editing `SKILL.md` updates its contract. Check scripts, references, assets, and metadata if present.
- When a skill resource changes, check whether its instructions and description have become outdated. Update only affected content; create resources for an actual purpose.
- Check frontmatter, paths, discovery, and behavior in a representative scenario. Run changed helper scripts with safe input. If a validator is unavailable, state that in the result.
- Repository sources may be changed within the task scope. Global installation or replacement of a personal skill requires a separate request.
