# Frontend / JavaScript / TypeScript

Confirm package.json, lockfile/package manager, Node version, bundler, and framework/module boundaries. Do not assume Vite/Inertia/Livewire solely from Laravel.
- Honor the pinned package manager/Node version and use reproducible lock-based installation. Keep generated assets separate from source.
- Run actual type/lint/unit/build commands; new TypeScript code should have a documented strictness baseline. Avoid unrelated tool migrations.
- Check accessibility, keyboard/focus behavior, loading/error states, escaping, and server-side authorization boundaries.
- Treat browser-exposed configuration as public; secrets belong on the server. Audit dependencies after relevant changes.
- Test affected interactions with the project's tooling; distinguish a successful asset build from a verified browser interaction.
- Preserve asset URL/cache behavior and generated manifest contracts with the backend. Bound fetch requests and cancel obsolete work.
