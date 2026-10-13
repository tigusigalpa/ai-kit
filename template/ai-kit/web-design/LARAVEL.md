# Laravel UI implementation

Apply to confirmed Blade interfaces with Web Design enabled. Read the [Laravel](../stacks/LARAVEL.md), [PHP](../stacks/PHP.md) and relevant [Frontend](../stacks/FRONTEND.md) baselines. Preserve the application's chosen stack and version: Laravel does not establish Vite, Tailwind, Alpine, Livewire, Inertia or Filament usage. Owner conventions remain in their existing profile.

## Select a route from evidence

- New Blade website: Blade plus a selected CSS approach is sufficient to start. Tailwind is a useful option for design tokens and utilities, not a required installation. Add local JavaScript/Alpine only for the needed behavior.
- Existing Bootstrap or custom CSS: reuse the existing component vocabulary and asset pipeline. Avoid a CSS migration merely to follow a design prompt.
- Livewire interface: confirm the installed major version, Alpine ownership, lifecycle and server actions. Ordinary server-rendered forms can use Laravel validation without Livewire.
- Existing Inertia/React/Vue: keep that boundary and apply the actual frontend implementation rules. Do not silently rewrite it to Blade.
- Filament panel: follow [Filament](../stacks/FILAMENT.md) and existing Resources/Pages/theme conventions. Do not replace panel widgets with an unrelated component library; marketing pages may have a separately documented stack.

## Blade component contracts

Reuse layouts and components in `resources/views/` according to the project. Anonymous components in `resources/views/components/ui/` can expose a stable `<x-ui.button>` or `<x-ui.input>` interface independent of their CSS implementation. Declare props, slots, attribute merging and variants; escape user content with Blade's normal output, and use raw output only for explicitly trusted/sanitized markup.

Distinguish links from actions. Choose an explicit button type where accidental form submission is possible. Preserve names, IDs, label association, validation messages, old input, disabled/loading states and assistive relationships. Component styling must not silently drop `aria-*`, `data-*`, `wire:*` or Alpine attributes. Avoid duplicate IDs in repeated controls.

Wire actual routes/forms with the application's methods, CSRF protection, server validation and policies. A hidden/disabled control is not authorization. Keep business logic in the existing application boundary, not repeated in templates. Acceptance should include persistence and denied/direct requests when affected, not just a toast or a visible button.

## Tailwind

Confirm the installed Tailwind major version before adopting configuration syntax. Tailwind v4 uses CSS configuration and can use `@tailwindcss/vite`; existing v3 projects keep their actual config until an upgrade is requested. Preserve the manifest/lock and asset entry points.

For v4, source discovery must cover real Blade files, JavaScript and used external component sources. The official Laravel guide includes `@source` entries for `resources` views/scripts, pagination views and compiled views; paths are relative to the stylesheet. Verify actual output instead of assuming every project needs identical globs.

Use complete classes in variant maps, for example `'primary' => 'bg-brand text-white hover:bg-brand-strong'`. Do not interpolate class fragments such as `bg-{{ $color }}-600`; the scanner reads text rather than executing PHP. An explicit `@source inline()` can cover a bounded, intentional set when needed. For arbitrary runtime values, validated CSS custom properties may fit better than unlimited generated class names.

Translate the design system into semantic tokens such as brand, surface, ink, border and control radius. In v4 use the appropriate `@theme` namespaces for utilities. Support needed focus, disabled/error states, responsive layout and reduced motion. Token overrides must retain contrast in all supported themes; a small palette is a design aid, not a rule that removes functional colors.

Use [selected library guidance](LIBRARIES.md) for daisyUI, Flowbite or Flux source/plugin requirements. Adding more than one library requires a concrete boundary and collision plan, not a default bundle of all suggested tools.

## Bootstrap

Confirm the installed version and existing Sass/CSS/JavaScript setup. Reuse Vite or the actual bundler, with one intentional asset entry contract. If Sass is imported by JavaScript, do not add a second unrelated stylesheet entry without checking the emitted manifest and layout.

Set Sass variable overrides before the Bootstrap import that consumes them; custom selectors/CSS variable adjustments can follow it. Partial imports need Bootstrap's documented dependency order. Import only the required JavaScript plugins when practical and account for Popper dependencies. Styling classes alone do not provide modal/dropdown behavior or accessible markup.

Do not mix Bootstrap and Tailwind resets/component vocabularies across the same interface without a deliberately scoped migration or boundary. Existing separate surfaces may use different systems with independent layouts/assets and documented ownership.

## Alpine and Livewire

Use one owner for Alpine on a page. Modern Livewire bundles/initializes Alpine; adding a separate import/CDN copy can cause initialization errors. If manual bundling/plugins are needed, use the installed Livewire version's supported integration. Resource directives and automatic injection depend on the real layout/configuration; do not prescribe duplicate script tags.

Respect component roots, stable keys, navigation and DOM update behavior for the installed version. Third-party interactive widgets must initialize and dispose correctly after relevant Livewire updates, without accumulating listeners or stale state. Validate and authorize server actions; inspect exposed public state and scope tenant queries.

## Evidence

Run the configured asset build and affected PHPUnit/Pest/Livewire checks. Exercise changed forms/navigation in a browser when available; confirm production asset URLs/manifests and intended fonts/images. Use [review evidence](REVIEW.md) for states/viewports and report unavailable runtime checks.

Version-match official [Blade](https://laravel.com/docs/blade), [Vite](https://laravel.com/docs/vite), [Tailwind Laravel installation](https://tailwindcss.com/docs/guides/laravel), [class detection](https://tailwindcss.com/docs/detecting-classes-in-source-files), [Bootstrap Sass](https://getbootstrap.com/docs/5.3/customize/sass/) and [Livewire installation](https://livewire.laravel.com/docs/installation) to the project. Connected Context7 can retrieve focused version-aware guidance; its availability is separate from this module.
