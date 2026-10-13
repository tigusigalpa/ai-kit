# UI acceptance and evidence

Review the affected routes/states against the project brief and design system, with the actual available runtime/tools. Use existing component/browser tests and an available browser or Playwright when appropriate. No single tool is mandatory and no screenshot baseline is created automatically.

## Visual and responsive checks

- Inspect a representative narrow viewport, a content-driven intermediate width and a wide layout; choose widths from the actual product rather than treating one screenshot size as universal coverage.
- Use actual or representative long content, supported languages, empty data and dense/repeated items. Check clipping, horizontal overflow, wrapping, reading order and main actions.
- Check hierarchy, type scale, spacing, contrast, imagery and consistent component states against the chosen direction. Preserve intended variation; do not force every section into identical cards.
- Confirm fonts, images, icons and production asset URLs load. Consider image sizing/layout shift and performance on the relevant environment; record measurements before claiming a performance result.
- Respect reduced motion and supported themes. Test meaningful transition/feedback behavior; visual polish must not hide a state or delay an action unnecessarily.

## Interaction and accessibility

Exercise changed links, navigation, menus, tabs, drawers, dialogs and forms. Check keyboard access, visible focus, focus entry/return, Escape and scroll behavior where applicable. Use appropriate native semantics, names, labels and error associations; automated accessibility checks supplement manual interaction.

Check initial, loading, success, empty, invalid, server-error, disabled and denied states that actually apply. Verify that submissions perform the intended server action/persistence, including validation, CSRF and authorization tests when affected. Do not mark authentication/payment/storage integration complete based on a mocked screen alone.

For Livewire/client navigation, repeat the interaction after DOM updates/navigation and check event/listener ownership, stale state and duplicate initialization. Capture relevant browser console/network errors without leaking credentials.

## Record what was established

Use per-check statuses in the project's acceptance document:

| Status | Evidence |
| --- | --- |
| `source-reviewed` | Inspected code/markup; no runtime behavior established |
| `build-verified` | The named build/static check passed in the recorded environment |
| `browser-verified` | The specific route, viewport and state were exercised and observed |
| `unverified` | A required check could not run or its result is unknown |
| `failed` | A reproducible requirement is not met |

Record the environment, route, viewport/state, command/action, outcome and screenshot/report pointer when useful. A screenshot is visual evidence for that captured state; it does not establish all behavior, accessibility or backend persistence. Sanitized summaries can be shared; raw screenshots/reports stay private unless the task calls for a shareable artifact.

When visual regression snapshots are useful, control browser version, OS/fonts, viewport, data and animation to make comparisons meaningful; inspect proposed baselines before accepting them. Use official [Playwright screenshot assertions](https://playwright.dev/docs/test-snapshots) for the actual toolchain, not as a claim this kit runs them.

Report concrete issues with reproduction, location, expected/observed behavior and impact. Fix within the authorized task, rerun the affected check, and keep unresolved failures explicit. If the browser/runtime is unavailable, finish available source/build work and state which acceptance remains unverified.
