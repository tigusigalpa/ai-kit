# Web Design: tools, review and troubleshooting

Part 3 of the [Web Design guide](WEB_DESIGN.md). It covers optional TypeUI and SkillUI routes, browser acceptance, reusable requests, updates and troubleshooting.

## TypeUI: use its design context in the coding project

TypeUI can be a useful source of the visual system in this workflow. Its documented role is to give a connected coding agent design context while that agent builds the interface. The site code belongs in your project; hosting/deployment is a separate capability. [TypeUI overview](https://www.typeui.sh/docs).

For your own references and brief, the route is:

1. Analyze the annotated references into concrete design observations.
2. Choose one coherent direction and record it in the local design system.
3. Select/adapt a TypeUI theme or prepare a custom Markdown ZIP in its supported format. Figma import is another documented route; check its current availability.
4. Review the workspace draft and publish the intended system for MCP when that external action is authorized.
5. Connect the account through your client's supported authentication flow, verify actual available resources, and select the intended system.
6. Ask the coding agent to implement the brief in the confirmed project stack using that selected system.
7. Verify the rendered pages and real behavior, then update local design memory with the system/package used.

The documented MCP endpoint is:

```text
https://mcp.typeui.sh/mcp
```

Follow the service's current [MCP setup](https://www.typeui.sh/docs/overview/mcp-server) for the client you use. AI-KIT does not write this server configuration or authenticate an account. Reuse a working connection when present, and make a small retrieval before claiming activation. Keep account tokens outside repository docs/config examples.

Custom design systems are editable Markdown files describing brand, colors, typography, layout and component rules. Use the current import format rather than assuming any ZIP will work. Arbitrary reference URL lists are not a documented automatic import; the coding agent must analyze them first. [Design systems](https://www.typeui.sh/docs/creative/design-systems).

Use one selected visual system per surface. Keep AI-KIT's general engineering, Laravel and review rules active, while avoiding conflicting aesthetic prompts. Record the workspace system/version and a local export or identity of the exact retrieved package where available: remote saved content may change, and a source repository revision does not pin a hosted system. If TypeUI is unavailable, local tokens/components remain a workable route; report retrieval as unverified.

An example request after a verified connection:

```text
$web-design Use the selected TypeUI design system for the public website described in docs/design/BRIEF.md. Implement it in this project's confirmed Blade/Tailwind stack, preserve Laravel form and route contracts, and record the retrieved design-system identity and actual UI checks.
```

## SkillUI: optional reference extraction with reviewed side effects

[SkillUI](https://github.com/amaancoderx/npxskillui) can analyze URLs, directories and public repositories and produce design observations. It can help with colors, typography and layout, but it is not a Laravel UI generator. The reviewed component extractor recognizes TSX/JSX/Vue/Svelte, not Blade/PHP; use URL/CSS evidence and design the Blade component API in the application.

An important implementation detail: Tailwind configuration loading can execute JavaScript via `jiti`. A branch or a copied directory is not a sandbox. Before processing untrusted directories/repositories, inspect executable configs and use a disposable environment without credentials, mounted personal home or unrelated writable paths, with an appropriate network boundary. The reviewed screenshot helper also uses Microlink; confirm the actual chosen path before submitting private or staging URLs. [Reviewed Tailwind loader](https://github.com/amaancoderx/npxskillui/blob/bc913a8d3503d6b2a683e4a3ac04ffe7304ac510/src/extractors/tokens/tailwind.ts), [screenshot helper](https://github.com/amaancoderx/npxskillui/blob/bc913a8d3503d6b2a683e4a3ac04ffe7304ac510/src/screenshot.ts).

Default skill generation can copy a skill to the user's global Claude directory. For a separately authorized, reviewed run in an appropriate disposable environment, prefer design-data output. This illustrative command fixes the npm version and writes to a dedicated directory inside that environment:

```bash
npx --yes --package=skillui@1.3.4 skillui --url https://example.com --format design-md --no-skill --out ./reference-output
```

The flags suppress skill generation/global copying; they do not disable all executable configuration or network behavior. A fixed package version is not proof that its npm bytes match the reviewed source commit; review integrity/source correspondence before relying on it. AI-KIT does not execute this command or install the package. Check runtime/browser requirements and report partial/default extraction if a requested mode is unavailable.

Use the result as observations to reconcile with the brief. Do not install generated `SKILL.md` or `CLAUDE.md` as authoritative project rules without review. Keep raw output private and promote only relevant sanitized rules into `docs/design/SYSTEM.md`. Manual browser analysis is a valid fallback when it is enough for the task.

## Review the interface in the browser

Use the project's actual browser/test tools or an available browser session. Playwright can support interactions, screenshots and regression checks; this module installs no browser/runtime and does not prescribe one tool for every environment.

A useful acceptance pass checks:

- The main route/action at a representative narrow, intermediate and wide viewport.
- Real content, long headings, dense lists/tables and supported user-facing languages.
- Layout overflow, reading order, typography, contrast and consistency with the chosen system.
- Images, icons, fonts and production asset URLs; layout shift/performance where relevant and measurable.
- Navigation, menus, tabs, drawers, dialogs, keyboard/focus and reduced motion.
- Applicable initial, loading, empty, invalid, server-error, success, disabled and denied states.
- Actual server validation, authorization and persistence for affected application scenarios.
- Repeated navigation/DOM updates for Livewire or client-managed widgets, including duplicate initialization and stale state.

Choose viewports from the real content/product. A 360-pixel screenshot is useful evidence, but not universal responsive coverage. Automated accessibility tools supplement keyboard/semantic checks. Screenshots show the captured state; they do not establish every interaction or backend effect.

Record each check honestly:

| Status | What it establishes |
| --- | --- |
| `source-reviewed` | Markup/code was inspected; behavior has not been exercised |
| `build-verified` | The named build/static check passed in the recorded environment |
| `browser-verified` | The specific route, viewport and state were exercised and observed |
| `unverified` | A required check could not run or its result is unknown |
| `failed` | A reproducible requirement is not met |

Add route, environment, viewport/state, action/command, outcome and a useful evidence pointer to `ACCEPTANCE.md`. If visual regression tests are appropriate, stabilize browser/OS/fonts, viewport, data and animation, then review the baseline. [Playwright screenshot comparisons](https://playwright.dev/docs/test-snapshots).

When no browser or Laravel runtime is available, complete the source/build work that can run and state the remaining acceptance explicitly. Do not mark a form working merely because it is visible. Full security-audit or Strix testing remains a separately requested workflow when needed.

## Reusable starter requests

**Design plan from references:**

```text
$web-design Analyze the annotated references in docs/design/BRIEF.md. Propose a coherent direction for the actual subject and audience, with semantic colors, typography, layout, responsive behavior and component states. Preserve established project constraints and record material assumptions before implementation.
```

**First Blade page:**

```text
$laravel-blade-ui Implement the first marketing page from the approved brief and system. Reuse the confirmed Laravel/CSS setup, create only useful reusable components, use complete Tailwind classes where applicable, and wire real routes and forms. Verify the available build, server and browser checks.
```

**Existing Bootstrap interface:**

```text
$laravel-blade-ui Improve this Bootstrap page using the existing visual system. Preserve the project's version and asset pipeline, place Sass overrides correctly, and verify navigation, form errors and narrow-screen layout. Keep the chosen Bootstrap route.
```

**Server-reactive form:**

```text
$laravel-blade-ui Implement the specified form in the existing Livewire application. Confirm the installed versions and Alpine ownership, preserve validation and policy checks, use the selected component system, and test loading, invalid, denied and successful persistence states.
```

**Reference analysis without installing a CLI:**

```text
$design-extract Analyze the supplied reference pages with available browser/source tools. Record observed typography, layout, component states and missing evidence. Reconcile useful principles with our brief; do not assume an external extractor or a global skill installation is required.
```

**UI acceptance:**

```text
$ui-review Review the changed routes against docs/design/BRIEF.md and SYSTEM.md. Exercise the relevant viewports and real interactions with available tools, fix issues within this task's scope, and record per-check evidence and unavailable coverage in ACCEPTANCE.md.
```

For a small change, specify the affected page/state and reuse the established system. The agent should not rerun reference extraction or redesign the product on every edit.

## Updates, deactivation and troubleshooting

Preview normal AI-KIT updates against the same target. Unchanged module instructions update; edited instructions stay local or produce conflict candidates when source rules change. Review/merge candidates and use the existing `--accept-local` flow for managed instructions. Project design documents remain project-owned and are preserved even when their template changes.

To stop selecting Web Design, set `web_design=false` in the installed settings and preview/apply the installer. This makes workflow selection inactive and stops future module selection, but the installer preserves previously installed files. Their skills may remain visible in the client's catalog and their entry points check the setting. It does not disconnect a TypeUI account or uninstall a CLI/library. Remove retained files only as an explicit, reviewed maintenance action; retiring a client removes that client's unchanged tracked copies, not the project's design memory.

| Symptom | Check |
| --- | --- |
| A fresh installation has no design skill | Was `--with-web-design` selected, and does the current client discover the installed skill path? |
| Context selection says the workflow is disabled | Check `web_design=true`; changing a catalog entry does not enable the setting |
| The project WIKI has no design links | Existing WIKI content is preserved; add pointers during bootstrap/context synchronization |
| Tailwind styles are missing | Confirm the version, source paths, complete class strings and actual production output |
| Alpine initializes twice | Check Livewire's bundled Alpine and the page's separate imports/CDN scripts |
| A widget fails after navigation | Check supported initialization/disposal and DOM ownership after updates |
| A TypeUI system changes unexpectedly | Check the selected system and exact saved/retrieved package; retain a local identity/export |
| Extraction lacks Blade components | SkillUI's reviewed component scanner does not parse them; use CSS/URL evidence and project contracts |
| A generated form looks complete but does nothing | Verify routes, methods, CSRF, server validation, authorization and persistence |
| Browser checks cannot run | Record source/build evidence and the specific unverified acceptance; do not invent a passing result |

Useful pilot tasks are a content landing page, a redesign of an existing page, and a form with real validation/error states. Compare the actual code, observed UI and maintenance effort before claiming any speed or quality improvement. The kit's integration tests establish installation/preservation behavior; they do not establish the quality of a generated website or a live TypeUI/SkillUI run.

Maintainer source notes and actual integration results are recorded separately in [Web Design verification](../WEB_DESIGN.md). Canonical references: [workflow](../../template/ai-kit/WEB-DESIGN.md), [Laravel UI](../../template/ai-kit/web-design/LARAVEL.md), [libraries](../../template/ai-kit/web-design/LIBRARIES.md), [tools](../../template/ai-kit/web-design/TOOLS.md) and [review](../../template/ai-kit/web-design/REVIEW.md).
