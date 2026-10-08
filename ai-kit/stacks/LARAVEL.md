# Laravel: apply only to a confirmed Laravel project

- Check the Laravel/PHP version, `composer.json`, lockfile, module structure, and established startup method. Verify the structure instead of assuming the standard layout.

## Schema and lifecycle

- **Do not create database foreign key constraints.** Relationship columns named `*_id` are allowed and should be indexed for actual queries, but without `foreign()`, `constrained()`, or equivalent SQL. Enforce integrity through code, checks, and a data repair plan.
- **One table per migration file**, including table changes or deletion. Add new migrations instead of rewriting applied migrations. Check old/new code compatibility, locks, and rollback.
- Explicitly define dependent model behavior on deletion/restoration. Implement it through model events/Observers or a synchronous domain service, and check transactions, soft delete, force delete, and repeated calls.
- Avoid mass `delete()`/`MassPrunable` for models whose integrity depends on model events: these operations bypass them. Provide integrity checks and repair for imports and raw SQL. See [Laravel mass delete documentation](https://laravel.com/framework/docs/11.x/eloquent#deleting-models-using-queries).

## Models, access, and data

- For **every new Eloquent model**, create a Policy, a Factory, and a registered Seeder. Check allowed and denied actions. When fields, casts, relationships, tenant rules, or lifecycle change, update the Factory and Seeder together.
- A Factory creates a valid minimal model; a reference Seeder makes reruns safe. `migrate:fresh --seed` is allowed only in an isolated, disposable database.
- The model's internal primary key is a normal auto-incrementing `id`; its public `uuid` is a separate unique field, not a foreign key. A shared `App\Traits\UuidTrait` assigns the UUID on creation; if the trait is missing, create it in `app/Traits/` after checking project conventions. Internal relationships, `*_id`, and joins continue to use `id`; do not overwrite the UUID on update.
- For a new Filament Resource, expose record URLs through UUIDs while keeping internal relationships on `id`. Check route key configuration against the installed Filament version; verify URLs, access restrictions for other users' records, and the Policy.
- Use request validation, policies/gates, and project services for their intended purposes. Check authorization in APIs, background jobs, and Filament; a hidden button does not replace server-side enforcement.

## Filament and checks

- For a new Filament installation, choose version **5 or later** and first verify compatibility with the actual PHP/Laravel/Tailwind versions. Surface existing-project upgrades explicitly.
- Check N+1 queries, result sizes, transactions, and mass assignment. Use the project's configuration and secret mechanisms; keep live keys out of code and logs.
- Prefer the existing test suite; where applicable, run targeted PHPUnit/Pest tests and `php artisan test`. Take formatting and static analysis commands from `composer.json` and CI. For new models, add Policy, Factory/Seeder, UUID, and lifecycle checks; for Filament, check UUID route binding.
