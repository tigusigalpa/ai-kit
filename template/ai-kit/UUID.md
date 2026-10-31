# Optional public UUID identifiers

Apply only when settings.uuid is true (`--with-uuid`), regardless of language, framework, or owner/standard conventions. This is engineering guidance for affected identifier work; installing it runs no generator or migration.

- For new persisted domain entities exposed through URLs, APIs, or external integrations, use a unique, immutable public UUID assigned at creation. Reuse an existing UUID identifier instead of adding another one. Internal numeric keys may remain where appropriate; do not require an SQL model for a document store or a frontend-only component.
- Match the UUID version, generator, validation, storage, indexes, serialization and route bindings to the project's supported runtime and current contracts. Prefer native facilities or an existing dependency; verify APIs before introducing code in PHP, JavaScript/Node.js, Python, Go, or another stack.
- Keep authorization and tenant isolation explicit: an unpredictable identifier is not an access control. Reject invalid identifiers and test collisions/uniqueness, create/update stability, lookup, denied access, and serialization.
- Preserve existing public IDs, database keys and API contracts. For an existing system, propose a compatible rollout and backfill before changing schema or routes; use the project's migration and recovery process. Do not rewrite primary keys or silently retrofit every table.
- In Laravel/Filament an internal id plus public uuid is one supported layout. Reuse an existing UuidTrait or the project's framework mechanism, keep factories/seeders consistent, and verify Resource route binding and policies. This layout is not required when the option is disabled.

Disabling the setting does not remove UUID columns, data, dependencies, or previously installed files. Explicit project agreements still govern existing UUID implementations.
