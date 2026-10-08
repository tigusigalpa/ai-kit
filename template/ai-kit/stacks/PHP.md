# PHP

Confirm PHP versions/extensions, composer manifests/lock, autoload boundaries, and framework before edits. Laravel and Moodle add their own profiles.
- Use Composer autoload/PSR conventions and the project's formatter/static analyzer. Do not impose a new directory layout or analyzer on an existing package.
- Validate inputs, escape output by its context, parameterize SQL, and enforce authorization; use the shared security baseline.
- Keep money/quantities exact (integer minor units or decimal/string contracts), not binary floats. Preserve protocol formats.
- Bound HTTP/connect timeouts, response sizes, retries, and stream ownership. Retry writes only with proven idempotency.
- Use narrow exceptions, preserve causes, and avoid logging secrets. Test failure paths and public contracts.
- Run composer validate, configured unit/static/format checks, and dependency audit when applicable. Track application locks; honor deliberate library lock policy.

Sources: [Composer](https://getcomposer.org/doc/03-cli.md), [PSR standards](https://www.php-fig.org/psr/).
