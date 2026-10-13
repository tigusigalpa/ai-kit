# UI library choices

Read only for a library selected by the user or confirmed in the affected project. A skill describes use; a CSS/JavaScript/Composer package supplies runtime components. Installing this module installs neither. Confirm versions/locks, required components, licenses and asset ownership before adding a dependency. Keep the chosen project design system authoritative.

| Route | Useful fit | Contract |
| --- | --- | --- |
| Tailwind with custom Blade components | A distinctive website with direct control over markup/style | Own component APIs and behavior; complete utility classes |
| Tailwind with daisyUI | Shared themes and a concise component vocabulary | daisyUI styling can live inside custom Blade components; behavior still needs an implementation |
| Tailwind with Flowbite | A selected collection of interactive UI components | CSS/theme/plugin/source setup plus JavaScript lifecycle |
| Livewire with Flux | A Livewire application's forms/navigation and controls | Supported Laravel/Livewire/Tailwind combination; check free/Pro component availability |
| Existing Bootstrap/custom CSS | An established project | Existing conventions, overrides and plugin behavior |

## daisyUI

Keep daisyUI's semantic theme roles and the project tokens consistent; test content colors, selected/disabled/error states and supported themes. Add its plugin according to the installed Tailwind/daisyUI major versions. A component class does not implement backend validation, authorization or every interaction. Use native HTML behavior, local JavaScript or the actual Alpine/Livewire integration as needed.

Own Blade wrappers remain useful: a project's `<x-ui.button>` may internally use daisyUI classes. There is no need to choose between wrappers and the library. Do not add daisyUI automatically to all HTML/Tailwind projects because an external skill has a broad trigger. Load its guides only for actual selected use and preserve the user's design decisions. Read component behavior and structure before adopting unfamiliar classes.

Official [Laravel fit](https://daisyui.com/laravel-component-library/), [installation](https://daisyui.com/docs/install/), [themes](https://daisyui.com/docs/themes/) and [agent guidance](https://daisyui.com/docs/skill/). External skill installation/update requires reviewed content and a bounded trigger; it is not part of this installer.

## Flowbite

Check the selected version's theme import, plugin and source scanning paths. Prefer the existing reproducible asset pipeline over adding an independent unpinned CDN. Load the JavaScript needed for the components in use; test drawers, dropdowns, modals and other widgets rather than accepting markup alone.

When combined with Livewire or client navigation, follow supported initialization/cleanup and ownership of the affected DOM. Check repeated navigation, opening/closing, focus restoration, Escape handling, scrolling and listener duplication. Do not assume a static Laravel example proves integration across dynamic DOM updates.

Free core components, Pro blocks and third-party templates can have different licenses and capabilities; verify the actual chosen assets. Use official [Laravel setup](https://flowbite.com/docs/getting-started/laravel/) and [JavaScript API](https://flowbite.com/docs/getting-started/javascript/).

## Flux

Flux is designed for Livewire. Confirm compatibility against the current [installation guide](https://fluxui.dev/docs/installation) and actual locked packages rather than encoding one compatibility tuple forever. Distinguish free Flux from Flux Pro and confirm that the proposed controls are available under the project's license.

Follow its styles/directives and appearance behavior without duplicating Livewire/Alpine resources. Adapt tokens/themes to the brief. Publish only the components that actually need customization, and account for maintenance when upstream components change. Composer authentication/license credentials are private; do not write them into design docs, model prompts or Git.

## Adoption and review

Pick one primary component system for a surface. Extra systems need a concrete benefit and defined asset/style/behavior boundaries. Avoid default installations of daisyUI, Flowbite and Flux together. A library can accelerate implementation, but speed, cost and quality claims require actual project evidence.

Use [Laravel UI](LARAVEL.md) for the application contract and [UI acceptance](REVIEW.md) to check the rendered result. If an optional tool or library is unavailable, continue within the chosen stack with available components rather than silently migrating to another framework/service.
