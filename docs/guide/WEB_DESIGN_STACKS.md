# Web Design: implementation routes

Part 2 of the [Web Design guide](WEB_DESIGN.md). Choose a route from the actual project, then follow the stack-specific notes for Blade, Tailwind, Bootstrap, component libraries, Alpine and Livewire.

## Choose the implementation route from the actual project

| Project situation | Recommended approach |
| --- | --- |
| New content/marketing website with a chosen Laravel backend | Blade with a selected CSS system; add only the interaction needed |
| Existing Blade + Tailwind project | Reuse its version, tokens, layouts and component contracts |
| Existing Bootstrap site | Keep Bootstrap and improve its tokens/layout/components unless a migration is requested |
| Existing React/Vue/Inertia interface | Keep the actual frontend boundary and apply the design system there |
| Livewire application | Reuse its state/lifecycle conventions and choose compatible controls |
| Existing Filament panel | Follow the confirmed Filament profile, Resources/Pages and theme conventions |
| Plain HTML/CSS website | Work directly with its files and available checks; no package manifest is required merely for this module |

For a new Blade project, Tailwind is a useful starting choice when you want direct token and layout control. Alpine can handle local menus/tabs/disclosures; Livewire can handle server-reactive scenarios. Neither is mandatory for every page. Existing CSS and component systems take precedence over a default recommendation.

One primary visual system per surface is a good default. Different surfaces can have different documented stacks: a marketing site and a Filament admin panel do not need identical component internals. A deliberate migration can cross boundaries, but adding Bootstrap, Tailwind, daisyUI, Flowbite and Flux to the same page by default creates unnecessary collisions.

## Laravel: implement the design directly in Blade

The `laravel-blade-ui` skill complements the existing Laravel/PHP/Frontend profiles. It does not replace their security, data or owner conventions. Inspect Composer/frontend manifests and locks, routes, layouts, components and the real asset pipeline before generating files.

A possible project layout is:

```text
resources/
  css/app.css
  js/app.js
  views/
    layouts/app.blade.php
    components/
      ui/button.blade.php
      ui/input.blade.php
      ui/alert.blade.php
      ui/empty-state.blade.php
      marketing/feature-card.blade.php
    pages/marketing/home.blade.php
docs/design/
  BRIEF.md
  SYSTEM.md
  ACCEPTANCE.md
```

This is an example, not a forced directory migration. Laravel supports anonymous components in `resources/views/components`, including dot notation such as `<x-ui.button>`. Define props, slots, variants and attribute forwarding so styling changes do not break consumers. Extract repeated semantics/behavior; a one-off fragment does not automatically deserve a component. [Official Blade components](https://laravel.com/docs/blade).

The interface must use real routes and form methods, CSRF protection, escaped output, server validation and appropriate policies. Preserve input values and show actionable validation errors. Hidden buttons do not authorize server actions; a success toast does not prove persistence. Use the project's PHPUnit/Pest/Livewire checks for affected server behavior and a browser for interaction.

For a design that starts in TypeUI or an HTML prototype, carry over the chosen tokens, hierarchy and component intent into the real Laravel implementation. A separate React generation-and-conversion stage is not required. If a supplied prototype already uses another framework, assess what can be reused and the cost of adaptation instead of claiming an automatic lossless export.

## Tailwind with Laravel: source discovery and stable classes

Confirm the installed Tailwind major version. The following example is for v4; existing v3 projects keep their version-specific configuration until an upgrade is requested. The official Laravel/Vite guide uses `@tailwindcss/vite`, a Tailwind import, source entries and Laravel's `@vite` asset inclusion. Preserve the project's chosen package manager, lock and plugin configuration. [Laravel installation guide](https://tailwindcss.com/docs/guides/laravel).

An illustrative `resources/css/app.css` for a v4 Blade project:

```css
@import "tailwindcss";

@source "../**/*.blade.php";
@source "../**/*.js";
@source "../../vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php";
@source "../../storage/framework/views/*.php";

@theme {
  --color-brand: #155e75;
  --color-brand-strong: #0e7490;
  --color-surface: #f8fafc;
  --color-ink: #0f172a;
  --color-border: #cbd5e1;
  --radius-control: 0.625rem;
}
```

Choose values from the actual approved design, not this example. `@source` paths are relative to the stylesheet; verify source detection for the real directories and selected library. v4 also has automatic discovery, so the absence of one identical glob is not proof of a bug. Confirm that the production build emits the classes actually used.

Tailwind scans text. A fragment such as `bg-{{ $color }}-600` will not reliably produce its eventual class. Use complete class strings or a deliberately bounded `@source inline()` set. For arbitrary runtime values, validated CSS custom properties may be more suitable. [Class detection](https://tailwindcss.com/docs/detecting-classes-in-source-files).

For example, an anonymous `button.blade.php` can keep complete variant classes:

```blade
@props(['variant' => 'primary', 'type' => 'button'])

@php
    $variants = [
        'primary' => 'bg-brand text-white hover:bg-brand-strong focus-visible:outline-brand',
        'secondary' => 'bg-white text-ink ring-1 ring-border hover:bg-surface focus-visible:outline-ink',
    ];
@endphp

<button type="{{ $type }}" {{ $attributes->class([
    'inline-flex items-center rounded-control px-4 py-2 font-medium focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50',
    $variants[$variant] ?? $variants['primary'],
]) }}>
    {{ $slot }}
</button>
```

This shows a variant map and explicit button type; it is not a complete form component library. Add the actual project's loading, error, icon and accessibility contract where needed. Do not strip `aria-*`, `data-*`, Alpine or Livewire attributes when wrapping controls.

## Bootstrap with Laravel: keep overrides and assets deliberate

Bootstrap is a valid route for an existing project or a deliberately chosen component vocabulary. Verify its version and the actual Sass/JavaScript pipeline. For Sass variables, put overrides before the import that consumes them:

```scss
/* resources/scss/app.scss */
$primary: #155e75;
$border-radius: 0.625rem;

@import "bootstrap/scss/bootstrap";

/* Additional project CSS rules can follow the Bootstrap output. */
```

For partial imports, follow Bootstrap's dependency order, including functions before overrides that use them. CSS variable adjustments and ordinary selector overrides can be applied later; changing a Sass variable after compilation does not regenerate already emitted rules. [Bootstrap Sass customization](https://getbootstrap.com/docs/5.3/customize/sass/).

If the confirmed asset entry is JavaScript, it can import the stylesheet and required plugins:

```javascript
// resources/js/app.js
import '../scss/app.scss';
import { Dropdown, Modal } from 'bootstrap';

// Initialize or use the selected plugins according to the page lifecycle.
```

Use the corresponding Laravel Vite entry in the layout, and check the emitted manifest. Avoid adding both an independent stylesheet entry and a JavaScript import without considering the existing output contract. Include the needed Popper dependency for the selected plugins. A `modal` or `dropdown` class alone does not establish working behavior. [Bootstrap/Vite](https://getbootstrap.com/docs/5.3/getting-started/vite/), [Laravel/Vite](https://laravel.com/docs/vite).

## daisyUI, Flowbite and Flux: select a library for a reason

These are component libraries, not interchangeable design skills. Use the one that fits the actual project and required controls; installing Web Design chooses none of them.

| Library | Useful when | What still needs attention |
| --- | --- | --- |
| **daisyUI** | You want concise component classes and semantic themes in Blade | Behavior, accessible markup, application contracts and theme contrast |
| **Flowbite** | You want selected interactive widgets and supported blocks | Theme/plugin/source setup, JavaScript and initialization after navigation/DOM updates |
| **Flux** | You are building a compatible Livewire interface | Supported package versions, resource ownership and free/Pro component availability |

**daisyUI can live inside your own Blade components.** Its `btn`, `input` and other classes can implement a stable `<x-ui.button>` API. This gives the project reusable contracts without requiring every consumer to know library internals. daisyUI styling does not itself supply Laravel validation or every state transition. [Laravel fit](https://daisyui.com/laravel-component-library/).

The official daisyUI agent skill exists, but its reviewed entry broadly tells the agent to use daisyUI for HTML/JSX even without an explicit request. AI-KIT therefore does not auto-install it or adopt that trigger universally. If you separately add a library skill, scope it to projects/surfaces where the library is selected, review its real files and retain the project's brief as the visual authority. [Official skill](https://github.com/saadeghi/daisyui/blob/master/skills/daisyui/SKILL.md).

**Flowbite** requires its selected version's CSS/theme/plugin/source configuration and JavaScript for interactive components. The Laravel guide demonstrates the setup, but a static example does not prove correct behavior after Livewire updates or client navigation. Check repeated opening/closing, focus return, Escape, scrolling and listener cleanup. Use the existing asset pipeline rather than introducing an unrelated unpinned CDN. [Laravel setup](https://flowbite.com/docs/getting-started/laravel/).

**Flux** is built for Livewire. Its current installation page lists Laravel 10+, Livewire 3.7+ and Tailwind 4.2+; verify compatibility against your actual locked versions when adopting it. Flux Pro is separate from the free package, and the available control set matters before choosing it. Keep Composer authentication/license credentials private. [Flux installation](https://fluxui.dev/docs/installation).

Check each selected library's actual license for the components, blocks and assets you adopt. Avoid installing multiple component systems simply because they appeared in a recommendation list. The [conditional library reference](../../template/ai-kit/web-design/LIBRARIES.md) covers these decisions.

## Alpine and Livewire: own the behavior once

Alpine is useful for local disclosures, tabs and similar interactions. Livewire is useful when the interface needs server-reactive state. Ordinary Laravel forms can submit to controllers with server validation without adding Livewire.

When Livewire is present, inspect its installed major version and resource strategy. Modern Livewire includes and initializes Alpine; a second standalone Alpine import or CDN copy can cause initialization errors. Manual bundling/plugins should use the supported integration. Resource directives and automatic injection depend on the actual version/layout/configuration; adding script tags by habit can create duplication. [Livewire installation](https://livewire.laravel.com/docs/installation).

Check component roots, stable keys and DOM ownership. A third-party date picker/modal/dropdown must survive the relevant navigation and updates, initialize once and dispose correctly. On the server, validate inputs, authorize actions and scope queries. UI polish does not replace the existing Laravel/Filament security contract.

Next: [tools, browser review and troubleshooting](WEB_DESIGN_TOOLS.md).
