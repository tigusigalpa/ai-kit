# Bootstrap procedure

1. Read current target instructions, manifests/locks, module paths, CI, and startup/test configuration. Preserve work and explicit agreements.
2. Preview the installer from a reviewed local distribution. Select sharing mode, chat language, conventions, and agents; defaults come from settings. The preview also lists installer-suggested stack profiles detected from module manifests and clients detected from existing native files; confirm which clients are actually used. Optional extras (session-start hooks, guards, project CI) are selected with --with-session-start/--with-guards/--with-ci and persist in settings.
3. Apply only a compatible plan. Resolve conflicts semantically from candidates; never overwrite project context/history or discard locally adapted rules.
4. Read installed AGENTS/Core/settings. Fill PROJECT_CONTEXT and [project.json](project.json) with verified purpose, supported versions, module -> profile -> command mapping, evidence, and unresolved requirements. Confirm or replace the installer-suggested module/profile/version/command drafts with verified evidence. Update continuity pointers and WIKI without copying policy text.
5. Load profiles only for confirmed modules. PHP/Laravel/Moodle rules can combine; frontend/library apply only when present. Verify ignored files and preserve intentional Go vendoring, package artifacts, fixtures, and executable source.
6. Establish Docker dependency and runtime discovery only when needed. Record stable resource identities, not current daemon state or transient usage. Use the router only for actual model/runtime setup: fill [selection.json](router/selection.json) with the providers the project actually uses, then optionally run the reference `scripts/router.py configure` to write `ai-kit/router/resolved.json` and a native Aider model file.
7. Run meaningful existing checks, review differences, document adopted changes in the project's CHANGELOG, and report pending conflicts/unverified checks.

## Ignore adaptation

The installer owns one marked ignore block. It adds universal cache/secret exclusions plus the selected private/team policy and scoped PHP/Moodle/Node/Python generated paths discovered from module manifests.
It does not delete existing ignore lines, remove Git index entries, or force-add files. Legacy exclusions outside its block can still hide shared team files; reconcile explicitly and verify with Git when available.
Root or mixed Go/PHP vendoring needs project evidence. Store selected module rules in the context; the kit repository's root ignore is never the application template.
