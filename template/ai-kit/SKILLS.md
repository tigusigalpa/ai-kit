# Skill registry

Source skills live in .agents/skills; metadata selects relevant work and the body points to one maintained profile.
Read a skill explicitly when needed and automatic selection has not occurred. Stack discovery is evidence-based; wrappers do not prove the stack.
Workflow skills run on an explicit request: /ai-kit-bootstrap in Claude Code, $ai-kit-bootstrap or /skills in Codex; clients without skill support can follow the same file.

| Skill | Profile |
| --- | --- |
| [project-continuity](../.agents/skills/project-continuity/SKILL.md) | Context/procedure |
| [ai-kit-bootstrap](../.agents/skills/ai-kit-bootstrap/SKILL.md) | Workflow: first-session bootstrap (user-invoked) |
| [ai-kit-review](../.agents/skills/ai-kit-review/SKILL.md) | Workflow: change review (user-invoked) |
| [ai-kit-sync-context](../.agents/skills/ai-kit-sync-context/SKILL.md) | Workflow: context sync after work (user-invoked) |
| [php-work](../.agents/skills/php-work/SKILL.md) | PHP |
| [laravel-work](../.agents/skills/laravel-work/SKILL.md) | LARAVEL |
| [filament-work](../.agents/skills/filament-work/SKILL.md) | FILAMENT |
| [go-work](../.agents/skills/go-work/SKILL.md) | GO |
| [python-work](../.agents/skills/python-work/SKILL.md) | PYTHON |
| [moodle-work](../.agents/skills/moodle-work/SKILL.md) | MOODLE |
| [frontend-work](../.agents/skills/frontend-work/SKILL.md) | FRONTEND |
| [library-work](../.agents/skills/library-work/SKILL.md) | LIBRARY |

## Lifecycle

Update the manifest and relevant references/scripts together. Verify frontmatter, paths, discovery, and actual behavior for meaningful changes.
Preserve invocation defaults; no global installation is implied. Claude native copies are managed by the installer and must be updated together with source skills.
Record current facts in project context; do not turn every wrapper into another policy/context copy.
