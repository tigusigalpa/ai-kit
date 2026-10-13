# Web Design

This optional workflow applies when [settings](settings.json) has `web_design=true` and the task concerns website design or UI implementation. It works with plain HTML/CSS, Blade, existing frontend frameworks and confirmed component systems. Installation supplies instructions and project documents; it starts no website generator, package installer, browser, MCP connection or deployment.

## Project design memory

Use [BRIEF](../docs/design/BRIEF.md) for the audience, content, scope and annotated references; [SYSTEM](../docs/design/SYSTEM.md) for the chosen visual rules and implementation contract; [ACCEPTANCE](../docs/design/ACCEPTANCE.md) for required states and actual evidence. Existing documents remain authoritative: link them instead of duplicating them. Scope decisions to the affected pages/modules, and add pointers to the project's existing WIKI/context when facts change.

Unknown fields remain unknown. Keep private reference material, extraction output and working screenshots in ignored `ai-kit/.design/` or another agreed private location; publishable site assets belong in the project's normal asset structure. Sanitized design documents are ordinary project documentation, visible in both sharing modes. Do not record credentials or sensitive session data.

## From references to a working interface

1. Establish the outcome: audience, primary action, pages/sections, real content/assets, required behavior and existing stack. Inspect manifests, locks, routes, components and current styling. Ask only about missing choices that materially affect the result; proceed with reasonable, stated assumptions where possible.
2. Analyze supplied references for what the user values: hierarchy, composition, typography, density, imagery, spacing and behavior. Record the relevant page/state and separate observations from inference. An inaccessible reference is missing evidence, not a license to invent its contents. Extract design principles without copying unrelated branding or assets.
3. Choose one coherent visual direction. Define semantic color roles, type scale, layout/container rules, spacing, component states, motion and asset treatment. Preserve an existing approved design system. For a substantial new direction, a representative screen or compact plan can expose choices early; a separate approval round is required only when the user or actual action requires it.
4. Implement in the confirmed project stack. Reuse components with stable semantics; introduce abstractions for repeated behavior rather than every small fragment. Build useful vertical slices and add the behavior needed by the task. A static prototype is an option, not an obligatory prerequisite to server-backed work.
5. Review against the brief and [UI acceptance](web-design/REVIEW.md): relevant viewports, actual content, interactions, keyboard/focus, errors/loading/empty states and assets. Refine visible problems; a build alone cannot establish browser behavior.
6. Deliver code/preview, actual checks and remaining gaps. Update project design memory and normal context/history where facts changed. Account setup, external publication and deployment follow the user's existing authorization and [Core](CORE.md); implementation does not grant them automatically.

For a small change, reuse the existing brief/system and check only affected screens and states. Do not rebuild the whole design process or impose a new aesthetic on routine maintenance.

## Conditional routes

| Task | Read when applicable |
| --- | --- |
| Blade, Tailwind or Bootstrap implementation | [Laravel UI](web-design/LARAVEL.md), plus confirmed [Laravel](stacks/LARAVEL.md)/[Frontend](stacks/FRONTEND.md) profiles |
| daisyUI, Flowbite or Livewire/Flux | [Selected libraries](web-design/LIBRARIES.md); no automatic dependency choice |
| TypeUI, an external design skill or SkillUI | [Tools and reference analysis](web-design/TOOLS.md), [MCP](MCP.md) for server setup |
| Browser/visual acceptance | [Review protocol](web-design/REVIEW.md) |

Visual guidance, stack rules and review guidance have different responsibilities. Use the brief and chosen design system for visual decisions, stack profiles for implementation and the review protocol for evidence. Do not stack conflicting aesthetic systems, replace the framework to fit a prompt, or claim a skill's presence establishes a connected tool.

## Scoped context

`aikit context select TARGET --path MODULE --workflow web-design` adds this workflow and project design documents to a read-only context manifest. Confirmed Laravel/Filament module profiles also select the Blade guidance; the agent must still confirm actual Blade usage. `--workflow ui-review` adds review guidance; `--workflow design-extract` adds tool guidance. The helper reports paths, hashes and measured bytes, not a finished model prompt. Required context survives a small byte budget; unrelated workflows/libraries are not loaded automatically.

Skills use normal relevant discovery in supported clients. Setting `web_design=false` makes the workflow inactive and stops its selection; preserved skill files can still appear in the client catalog. Removal of retained files/client connections is separate from changing this setting.
