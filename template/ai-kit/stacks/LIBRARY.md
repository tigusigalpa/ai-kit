# Reusable library / SDK

Confirm package type, supported language versions, exported API, versioning policy, and publishing workflow.
- Preserve public API/serialization/error contracts. Use semantic versioning where adopted; breaking changes require the policy's appropriate version and migration notes.
- Document examples and compatibility requirements; test consumer use, including Go example tests or Composer autoload where appropriate.
- Keep protocol numbers/IDs exact, distinguish retryable errors, and expose cancellation/timeouts without leaking provider credentials.
- Review dependency additions for consumer impact. Check go mod tidy/Go compatibility or composer validate and a supported dependency matrix.
- Track Go manifests/checksums; for PHP libraries follow the explicit lockfile policy. Keep source/tests/docs rather than unintentionally ignoring release artifacts.
- Publishing, tags, releases, and external notifications need an explicit task. A passing test suite does not authorize release.
