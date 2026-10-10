# Contributing

Read [maintainer instructions](AGENTS.md) and [policy ownership](docs/IMPLEMENTATION.md#policy-ownership).
Make a coherent local change, add behavioral checks for installer or validator risks, and run the documented checks.
Keep project templates free of maintainer facts/history. Preserve local-file ownership and authorization boundaries.
Update the root changelog; record significant design decisions in docs/adr/.
Discuss version/provider changes using current primary documentation and actual runtime evidence. Commit/push authorization follows Core.

## Updating a reference repository

Archive overlays leave old files behind. Compatibility pointers retain known v0.1 rule paths.
Overlay the bundle at the reference root, preserve customizations, and run the checker.

The obsolete .gitignore_real is historical material: its useful rules live in the templates/ policies, scoped by the installer where a global rule would hide project source (Composer vendor, Moodle config.php, Node and Python output). Use templates/ policies for applications.
Keep the root [SKILL.md](SKILL.md) current when commands, options, or features change.
Retire old pointers after reviewing inbound links and local changes.
