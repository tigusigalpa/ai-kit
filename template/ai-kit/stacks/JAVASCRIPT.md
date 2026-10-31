# JavaScript / TypeScript / Node.js

Apply to confirmed JavaScript/TypeScript modules, Node.js services, CLIs, workers, and libraries. Inspect package.json, workspaces, lockfiles, engines, module type, tsconfig and recorded commands. A package manifest alone does not establish browser UI or a particular server framework.

- Preserve the supported runtime, package manager and ESM/CommonJS boundary. Use the existing lock-based install and scripts; do not introduce a framework, TypeScript conversion or toolchain migration without a requirement.
- Keep async work bounded: await errors, propagate cancellation, limit concurrency/timeouts, and close servers, connections and workers during shutdown. Avoid blocking the event loop with large synchronous CPU or filesystem work on request paths.
- Validate external input at HTTP/CLI/message boundaries. Keep secrets on the server; use argument arrays for child processes and parameterized persistence APIs. Apply the project's authentication, authorization, tenant isolation and request-size limits.
- Use exact money representation and idempotent retry/queue effects where relevant. Preserve serialization and public API contracts. Public UUID guidance applies only when settings.uuid is enabled or the user explicitly asks for it.
- Run configured lint, type, unit/integration and build checks. Test rejected inputs, asynchronous failures, cancellation and affected lifecycle paths using the actual project runner. Review dependency/lock changes; installation scripts execute code and require the normal dependency review.
- Load [frontend guidance](FRONTEND.md) additionally for confirmed browser work and [library guidance](LIBRARY.md) for published package contracts. Keep browser and Node runtime APIs distinct.
