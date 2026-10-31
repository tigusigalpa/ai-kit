# Owner conventions

Apply when settings.conventions is owner. These are the owner's chosen Laravel conventions, not framework requirements; standard installations use actual project conventions.
Existing incompatible schema/contracts require an explicit adaptation plan rather than a destructive retrofit.

## Laravel schema and lifecycle

- Do not create database foreign key constraints. Indexed relationship columns and internal *_id joins are allowed; enforce integrity in code, transactions, orphan checks, and a documented repair plan.
- One table per migration, including changes/deletion. Add migrations rather than rewriting applied ones.
- Define dependent deletion/restoration behavior through observers/events or a synchronous domain service; test soft/force delete, restore, bulk paths, and reruns. Mass deletes bypass model events.

## Models and Filament

- Every new Eloquent model gets a Policy, Factory, and registered Seeder; keep them synchronized with its contract and test allowed/denied actions.
- Preserve existing identifier contracts. Public UUIDs and UUID-based Filament routes are enabled only through settings.uuid (`--with-uuid`); owner conventions alone do not require them.
- New Filament installations use version 5 or later after verifying PHP/Laravel/Tailwind compatibility. Surface upgrades of existing projects explicitly.

When UUID guidance is enabled, follow the optional UUID policy through AGENTS; choose an existing project mechanism before introducing a trait or library.
