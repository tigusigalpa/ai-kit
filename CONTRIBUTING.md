# Contributing

Read [maintainer instructions](AGENTS.md) and [policy ownership](docs/IMPLEMENTATION.md#policy-ownership).
Make a coherent local change, add behavioral checks for installer or validator risks, and run the documented checks.
Keep project templates free of maintainer facts/history. Preserve local-file ownership and authorization boundaries.
Update the root changelog; record significant design decisions in docs/adr/.
Discuss version/provider changes using current primary documentation and actual runtime evidence. Commit/push authorization follows Core.

## Updating a reference repository

Archive overlays leave old files behind. Compatibility pointers retain known v0.1 rule paths.
Overlay the bundle at the reference root, preserve customizations, and run the checker.

The obsolete .gitignore_real is historical material. Use templates/ policies for applications.
Retire old pointers after reviewing inbound links and local changes.
