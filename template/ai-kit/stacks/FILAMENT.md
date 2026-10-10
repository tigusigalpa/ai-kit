# Filament

Apply only to confirmed Filament work. Inspect composer.json and composer.lock for Filament, Laravel, PHP, Livewire, and plugins; inspect frontend locks when assets change. A detected dependency suggests this profile but does not establish panel usage or a supported runtime. Combine the [Laravel baseline](LARAVEL.md) with this profile for Laravel modules; apply [owner conventions](../profiles/OWNER.md) only when selected.

## Version and structure

- Match APIs and generators to the installed major version. Confirm compatibility before a new installation or upgrade; preserve an existing application's version and layout. The official [installation guide](https://filamentphp.com/docs/5.x/introduction/installation) covers panel and component installations; do not run a fresh-app scaffold over an existing project.
- Follow the project's Resource, Page, RelationManager, Widget, and schema conventions. Keep forms, tables, filters, and actions focused on presentation; put reusable business operations in the existing application service layer. Avoid creating duplicate domain logic in UI callbacks.
- Bound queries and loading: eager-load displayed relations, paginate large tables, and check reactive fields/widgets for repeated queries. Validate submitted data and uploads on the server. Review what public Livewire state exposes to the browser.

## Authorization and verification

- Enforce panel access, model policies, action authorization, and tenant scope on the server. Hidden navigation or controls do not protect a callable operation. Check related-owner access and additional model properties explicitly; never assume an extra property receives the resource record's checks.
- Review the [resource authorization contract](https://filamentphp.com/docs/5.x/resources/overview#authorization) for single-record and bulk operations. Test mixed selections, denied records, and cross-tenant access. Do not remove query scopes or skip authorization to make a screen work.
- Keep effects, retries, transactions, and money handling under the Laravel baseline. When owner conventions apply, verify public UUID URLs and bindings through Resources and relation pages.
- Use the project's PHPUnit/Pest and Livewire setup. Test affected list/filter behavior, create/edit validation and persistence, direct denied requests, actions/bulk actions, and tenant isolation. A visible button or a successful page load alone is insufficient verification.

Version-match the official [security guide](https://filamentphp.com/docs/5.x/advanced/security) and [resource tests](https://filamentphp.com/docs/5.x/testing/testing-resources). Report application checks that could not run; kit validation does not execute a Filament application.
