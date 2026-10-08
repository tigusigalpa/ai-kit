# Owner conventions

Apply when settings.conventions is owner. These are the owner's chosen Laravel conventions, not framework requirements; standard installations use actual project conventions.
Existing incompatible schema/contracts require an explicit adaptation plan rather than a destructive retrofit.

## Laravel schema and lifecycle

- Do not create database foreign key constraints. Indexed relationship columns and internal *_id joins are allowed; enforce integrity in code, transactions, orphan checks, and a documented repair plan.
- One table per migration, including changes/deletion. Add migrations rather than rewriting applied ones.
- Define dependent deletion/restoration behavior through observers/events or a synchronous domain service; test soft/force delete, restore, bulk paths, and reruns. Mass deletes bypass model events.

## Models and Filament

- Every new Eloquent model gets a Policy, Factory, and registered Seeder; keep them synchronized with its contract and test allowed/denied actions.
- Keep an auto-incrementing internal id and a separate unique public uuid assigned on creation by shared App\Traits\UuidTrait. Preserve uuid on updates; internal relations use id.
- New Filament Resources use UUID record URLs with verified route binding and Policy checks.
- New Filament installations use version 5 or later after verifying PHP/Laravel/Tailwind compatibility. Surface upgrades of existing projects explicitly.

The built-in UUID trait can be evaluated as an explicit implementation choice; do not silently replace this agreed UuidTrait contract.
