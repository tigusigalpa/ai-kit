# Original bundle checks

Historical verification record for the first consolidated bundle, recorded 2026-10-08 on Windows with bundled Python 3.12.14.

- Behavioral suite: 33 tests executed; 32 passed and 1 skipped. The skipped symlink test requires a Windows privilege unavailable in that session; no claim is made that it ran.
- Installer scenarios cover absent-target preview, project-owned files, idempotency, unchanged upgrades, local conflicts/semantic merges/future conflicts, backups, private/team transitions, mixed Composer/Go vendoring, Moodle scoping, optional entries, settings preservation, unsafe paths, changed previews, and rollback after an injected write failure.
- Checker scenarios cover missing anchors, escaping links, invalid JSON, skill/folder and registry mismatch, clean history boundaries, and Git checkout metadata exclusion.
- Real Git checks passed for reference-source visibility, private/team shared files, secrets/caches, manifests/checksums/locks, intentional vendoring, and executable source.
- All 8 installable skills plus the maintainer continuity skill passed the skill-creator metadata validator. Relative file/heading links, registry, JSON, English content hygiene, and always-loaded byte budgets passed the kit checker.
- Docker evidence tests use a fake command adapter: inspection remains read-only, stopped-container references remain protected, exact bytes stay unknown, and a stopped daemon fails rather than producing a success report. No real Docker environment was exercised.
- Instruction review checked conditional profile loading, unknown project facts, English artifacts/configured chat language, no publication authorization, Docker preflight, and preserved owner conventions. This is source review, not a live client behavior trial.
