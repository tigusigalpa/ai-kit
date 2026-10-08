# Laravel

Confirm installed Laravel/PHP/Filament versions and composer scripts. Apply the [PHP baseline](PHP.md) and, when conventions=owner, [owner rules](../profiles/OWNER.md).
- Read env() only from configuration files; use config() in application code so cached configuration works.
- Validate request boundaries; policies/gates protect APIs, jobs, tenants, and admin UI. Hidden UI controls are not authorization.
- Keep database transactions bounded. Dispatch dependent jobs/events after commit using supported framework configuration/APIs; rolled-back work must not escape.
- Make business effects idempotent. Unique jobs/locks help coordination but do not guarantee exactly-once external effects; handle retry/replay explicitly.
- Set outbound timeouts and retry predicates; do not blindly retry non-idempotent writes. Test remote errors with fakes.
- Check N+1 queries, pagination, indexes, mass assignment, cache invalidation, and transaction/deletion races.
- Use exact money representation. Factories create valid minimal records; seeders are safe to rerun. migrate:fresh is only for an isolated disposable database.
- Use configured PHPUnit/Pest tests. For a new application prefer Pint, an explicitly chosen Larastan level, and a documented test runner; preserve existing tooling.
- Test UUID route binding, policies, lifecycle, fresh/upgrade migrations, and factories/seeders when affected.

Version-match the official [configuration](https://laravel.com/framework/docs/configuration), [queues](https://laravel.com/framework/docs/queues), [HTTP client](https://laravel.com/framework/docs/http-client), and [Eloquent](https://laravel.com/framework/docs/eloquent) docs to the installed major version.
