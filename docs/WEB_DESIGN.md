# Web Design integration record

## Scope and ownership

The optional module turns a brief and annotated references into project design memory, stack-aware implementation and recorded UI acceptance. The [README guide](../README.md#web-design) is human onboarding; [WEB-DESIGN](../template/ai-kit/WEB-DESIGN.md) owns the installed workflow. Conditional references own [Blade implementation](../template/ai-kit/web-design/LARAVEL.md), [libraries](../template/ai-kit/web-design/LIBRARIES.md), [tools](../template/ai-kit/web-design/TOOLS.md) and [UI evidence](../template/ai-kit/web-design/REVIEW.md). Existing Core/engineering/security/stack policies remain canonical.

No external skill/runtime bytes are bundled. Local skills use normal relevant discovery and check `web_design=true`; extraction describes requested reference work without automatically starting a CLI. TypeUI/MCP authentication, external skill/package setup and website publication remain separate actions.

## Installer and context behavior

- `--with-web-design` persists an independent boolean outside presets. Fresh default/preset installations omit all module resources, skills and project documents. Selection supports multiple short entry points for one extra without changing the pinned security packages.
- Four source skills have matching Claude copies when that client is selected. The installer preserves native MCP configuration and invokes no process/network/runtime during module installation.
- `docs/design/BRIEF.md`, `SYSTEM.md` and `ACCEPTANCE.md` are created only when missing and preserved byte-for-byte thereafter. Existing project WIKI/context are preserved; bootstrap adds relevant pointers. Doctor checks/restores the enabled module's missing project documents through the normal installer path.
- Managed module guides/skills use normal local-adaptation/conflict behavior. Disabling selection retains previous files; the setting prevents workflow use/selection, while catalog discovery may still list retained skills. Explicit adapter retirement removes only that client's unchanged tracked files.
- Design documents stay ordinary project source in both sharing modes. Working output under `ai-kit/.design/` is ignored in private/team modes; already tracked data needs separate review.
- `context select --workflow web-design|ui-review|design-extract` requires the enabled setting and selects the relevant workflow plus project design documents. Main Web Design selection adds Blade guidance only for the declared Laravel/Filament module. Ordinary selection is unchanged; required files survive byte overruns, and the result is a manifest rather than a prompt.
- The root README has no byte quota. Existing entry-point and conditional instruction budgets remain scoped to their actual files; link/language/metadata checks still apply to README.

## Recommendation disposition and source review

Reviewed on 2026-10-13 against the supplied Manus design/Laravel report and primary documentation. No real website or external runtime was executed in this research.

| Recommendation | Treatment |
| --- | --- |
| Brief, tokens, components and browser acceptance | Implemented as distinct project documents and workflow responsibilities |
| Blade + Tailwind + Alpine | Supported route; actual stack is verified and existing versions/components are preserved |
| Bootstrap alternative | Supported route with Sass overrides before consuming imports and deliberate asset ownership |
| A single UI skill | Separate visual, stack and review responsibilities; avoid conflicting visual systems |
| daisyUI or own Blade components | Compatible layers: project Blade wrappers may use daisyUI |
| Flowbite and Livewire/Flux | Conditional library guidance; no implicit installation or purchase |
| Livewire assets and Alpine | Version/layout-aware; avoid a second Alpine copy and duplicate scripts |
| Mandatory approval before every implementation | Material choices may need clarification; routine authorized work proceeds |
| Ready custom skills/prompts linked by Manus | Their contents were not attached; supplied local wrappers and English examples are independently authored |
| TypeUI reference-to-site workflow | References become a local design system, optionally imported/selected through TypeUI; code is built by the connected agent in the project |
| SkillUI | Optional reviewed extraction, with executable-config/global-copy/data-destination boundaries; no default runtime integration |

Primary sources:

- [Tailwind Laravel guide](https://tailwindcss.com/docs/guides/laravel), [class detection](https://tailwindcss.com/docs/detecting-classes-in-source-files), [Blade](https://laravel.com/docs/blade), [Laravel Vite](https://laravel.com/docs/vite).
- [Bootstrap Sass](https://getbootstrap.com/docs/5.3/customize/sass/), [Bootstrap Vite](https://getbootstrap.com/docs/5.3/getting-started/vite/), [Livewire installation](https://livewire.laravel.com/docs/installation), [Flux installation](https://fluxui.dev/docs/installation). Current Flux prerequisites are Laravel 10+, Livewire 3.7+ and Tailwind 4.2+; installed contracts direct agents to recheck actual versions.
- [daisyUI Laravel fit](https://daisyui.com/laravel-component-library/), [official skill](https://github.com/saadeghi/daisyui/blob/master/skills/daisyui/SKILL.md): broad HTML/JSX invocation instructions are not adopted. [Flowbite Laravel setup](https://flowbite.com/docs/getting-started/laravel/): direct fetch was blocked, but the official indexed page exposed theme/plugin/source and JS setup; dynamic DOM behavior is not established by that example.
- [Anthropic frontend-design](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md): useful visual method, below the brief. [Vercel web-design-guidelines](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines): a wrapper can fetch mutable guidelines separately, so pinning the wrapper is insufficient.
- [TypeUI overview](https://www.typeui.sh/docs), [MCP](https://www.typeui.sh/docs/overview/mcp-server), [design systems](https://www.typeui.sh/docs/creative/design-systems): themes, Markdown ZIP and Figma imports; authenticated HTTP MCP at `https://mcp.typeui.sh/mcp`. Workspace publishing/selection and saved package identity are distinct from code generation and hosting. No arbitrary URL-list import or Laravel code export was established.
- [SkillUI](https://github.com/amaancoderx/npxskillui) inspected at `bc913a8d3503d6b2a683e4a3ac04ffe7304ac510`: [component scanner](https://github.com/amaancoderx/npxskillui/blob/bc913a8d3503d6b2a683e4a3ac04ffe7304ac510/src/extractors/components.ts) omits Blade/PHP; [Tailwind loader](https://github.com/amaancoderx/npxskillui/blob/bc913a8d3503d6b2a683e4a3ac04ffe7304ac510/src/extractors/tokens/tailwind.ts) invokes `jiti(configPath)`; [screenshot helper](https://github.com/amaancoderx/npxskillui/blob/bc913a8d3503d6b2a683e4a3ac04ffe7304ac510/src/screenshot.ts) uses Microlink; [CLI](https://github.com/amaancoderx/npxskillui/blob/bc913a8d3503d6b2a683e4a3ac04ffe7304ac510/src/cli.ts) can copy generated skills globally. The README's fixed npm 1.3.4 example is not a verified npm-to-Git integrity mapping and is not executed by AI-KIT.
- [Playwright screenshot comparisons](https://playwright.dev/docs/test-snapshots): relevant browser/OS/font/data/animation controls for actual project regression tests.

## Verification

Verified on 2026-10-13, Windows/Python 3.12.14, using disposable fixtures outside the checkout:

- Full discovery: 304 tests in 976.969 seconds; 300 passed, four skipped. Skips were POSIX hook execution, symlink creation privilege and two junction fixtures. Simulated linked/blocked path checks passed separately; unavailable native cases are not counted as passed.
- Focused checks: ten Web Design tests and 24 checker tests passed. Covered whole-module default/preset absence, offline apply without process/network calls, independent persistence, source/native copies, preserved existing design documents, local/source conflicts, explicit retirement, disabled selection, blocked/linked paths and read-only scoped context for plain HTML and declared Laravel modules.
- Kit validation: zero errors and zero warnings, including actual Git visibility. Before release labeling, the root README was 69664 UTF-8 bytes with no size quota; other instruction budgets remain scoped. The checker regression enlarges README without a size warning while retaining conditional-guide warnings and normal validation.
- All 11 client selections in private/team fixtures: installed links, actual Git ignore visibility and unchanged reruns passed. Raw design output stayed ignored; ordinary design documents stayed visible.
- Upgrade from tracked pre-change HEAD at version 1.2.0: project context/facts, preexisting design documents and native MCP configuration retained their bytes. Settings values/unknown preferences and both security package identities were preserved; reapplying stayed stable. This is a local reference-upgrade fixture, not a reconstruction of a published release. Manifest newline representations can differ between archive and checkout; identity comparison used parsed data.
- Actual `doctor --fix` restored a missing design acceptance document without replacing the other design documents. Existing Context7/OpenRouter and following README sections stayed unchanged; archived v0.6.4 release text was preserved exactly apart from relative link relocation.
- Four new skills passed the bundled skill-creator validator in Ubuntu/WSL with PyYAML. Python 3.10 grammar checks passed for CLI/scripts/tests; this does not establish execution under Python 3.10.
- Offline wheel built in an isolated source copy and installed in a fresh venv. Smoke checks passed default installation, all four optional integrations, native entries, health checks, Web Design context selection and stable rerun. Final documentation is included in the rebuilt package; no packaging output was created in the source checkout.
- Self-review covered ownership, defaults, module selection, file preservation/conflicts, path guards, visibility, registry/links, client copies, upgrade behavior and tool execution boundaries. This was not an independent agent review.

Live TypeUI retrieval/publishing, SkillUI execution, actual client discovery, generated website acceptance and Laravel/browser application trials are unverified. Integration checks establish file/workflow contracts only; they establish no design quality, speed, cost or token savings.

## Release labeling

v1.3.0 is locally prepared on 2026-10-13. The full 304-test discovery above preceded labeling; labeling changes VERSION and maintainer release metadata without changing module behavior. Publication/tagging remain separate.

Post-label verification on Windows/Python 3.12.14:

- Eight CLI tests passed; the CLI module version, VERSION and parsed wheel metadata agree at 1.3.0. Kit validation returned zero errors/warnings.
- The v1.3.0 wheel passed offline fresh-venv smoke: default installation, all four optional integrations, source/native skills, doctor, Web Design context and a stable rerun.
- Upgrade from the pre-label 1.2.0 reference copy preserved project facts, settings values/unknown preferences, modified design documents, a locally edited Web Design skill, native MCP configuration and both security manifests byte-for-byte. Installed VERSION/state advanced to 1.3.0 without conflicts; doctor/links and repeat installation passed. This baseline already contained Web Design and is separate from the earlier tracked pre-change upgrade.
- Final release documentation is included in the rebuilt wheel. These checks establish labeling/package preservation, not a new application or hosted CI result.
