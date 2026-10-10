# AI-KIT

A new chat should be able to pick up your project without making you explain every decision again. AI-KIT keeps the instructions, verified project facts, and working practices that make that possible alongside your code.

Adapt it to your stack and keep it current.

Bundle version: [VERSION](VERSION). License: [MIT](LICENSE).

[Get started](#install) · [Choose defaults](#choose-your-defaults) · [Share with a team](#sharing) · [Update a project](#update-an-application-project)

## What you get

- Project memory: verified context, a documentation map, and decisions.
- A repeatable plan -> implement -> test -> review -> document workflow.
- Relevant stack, security, container, and routing guidance.
- Installation previews, preserved project documents, and conflict handling.
- Private or shared instructions that grow with your project.

## Install

You need Python 3.10 or later (the installer uses the standard library). Get the repository or extract a prepared bundle, then review its files:

~~~sh
git clone https://github.com/tigusigalpa/ai-kit.git
cd ai-kit
~~~

Use a verified revision; main can change and no release tag is assumed. Choose your application's absolute path outside this reference directory.

### 1. Preview

Linux or macOS:

~~~sh
python scripts/install.py /home/you/projects/my-app
~~~

Windows:

~~~powershell
python scripts/install.py "C:\Projects\my-app"
~~~

Replace the path with your own. Preview creates no files; --dry-run is equivalent.
Review writes, preserved files, candidate paths, conflicts, and the stack profiles suggested from detected module manifests.

### 2. Apply

Add --apply to the same command:

~~~sh
python scripts/install.py /home/you/projects/my-app --apply
~~~

Missing files are created; existing project README, context, WIKI, changelog, and decision documents survive.
Customized instructions can conflict; use [the update procedure](#update-an-application-project) to merge them.

### 3. Start the first session

Give the agent [BOOTSTRAP_PROMPT.md](BOOTSTRAP_PROMPT.md) and access to the bundle and repository. It fills the templates with actual purpose, versions, module paths, commands, and open questions, so the next session knows how to run the project and check a change. Without file access, attach templates and repository evidence, then apply the proposed files yourself.

## Choose your defaults

Select alternatives during installation. Project choices live in ai-kit/settings.json; defaults are in [the settings template](template/ai-kit/settings.json).

| Setting | Default | Meaning |
| --- | --- | --- |
| Project language | English | Authored project files use English |
| Chat language | Russian | Plans, explanations, and replies use Russian |
| Sharing mode | private | Local AI-KIT files are excluded from Git |
| Conventions | owner | Personal Laravel conventions apply when that stack is confirmed |
| Agent selection | codex | Default entry points and source skills |

For shared rules, English chat, and your project's own conventions, preview:

~~~sh
python scripts/install.py /path/to/project --mode team --chat-language English --conventions standard --agent codex --agent claude
~~~

Add --apply after reviewing the plan.

**Read [OWNER.md](template/ai-kit/profiles/OWNER.md) before adopting owner for Laravel** (no database foreign key constraints, separate public UUID, model policies/factories/seeders); standard follows your project's established conventions.

## The files you will use

Installed project files:

| File or directory | Purpose |
| --- | --- |
| AGENTS.md | Starting instructions and links to relevant rules |
| PROJECT_CONTEXT.md | Verified purpose, contracts, stack, module map, commands, and open questions |
| WIKI.md | A short map of useful documentation |
| .agents/skills/project-continuity/SKILL.md | The procedure for keeping context and pointers current |
| ai-kit/ | Core rules, settings, engineering guidance, profiles, and routing |
| docs/DECISIONS.md and docs/adr/ | Decisions, reasons, and tradeoffs |
| CHANGELOG.md | What changed and why |

Keep current facts in context and the reasoning behind choices in decisions/ADRs. When facts, agreements, or procedures change, synchronize context, the continuity skill, and WIKI in the same task. After a task with file changes, add a concise changelog entry.

A fresh session reads context before editing.

## A normal working session

Follow **plan -> implement -> test -> review -> document**: establish behavior and acceptance checks, make a focused change, run relevant tests, review, and record what changed. Load relevant rules, review risky changes, and report actual checks and unavailable verification; the [engineering guide](template/ai-kit/ENGINEERING.md) owns the detailed rules.

[Core](template/ai-kit/CORE.md) owns Git authorization: commits and pushes require an explicit request for that operation. Normal task completion leaves reviewable local changes.

## Stack profiles

Bootstrap confirms which profiles apply and records a path-to-profile map for each module.
The install preview suggests profiles from module manifests (go.mod, package.json, composer.json, pyproject.toml); verify suggestions at bootstrap.

| Profile | Main concerns |
| --- | --- |
| [PHP](template/ai-kit/stacks/PHP.md) | Composer, application boundaries, errors, and checks |
| [Laravel](template/ai-kit/stacks/LARAVEL.md) | Authorization, transactions, queues, and migrations |
| [Go](template/ai-kit/stacks/GO.md) | Context, HTTP, errors, concurrency, and modules |
| [Python](template/ai-kit/stacks/PYTHON.md) | Scripts, CLI, paths, dependencies, and tests |
| [Moodle](template/ai-kit/stacks/MOODLE.md) | Plugins, capabilities, upgrades, and privacy |
| [Frontend](template/ai-kit/stacks/FRONTEND.md) | Toolchain, UI states, accessibility, and browser checks |
| [Library](template/ai-kit/stacks/LIBRARY.md) | Public APIs, consumer examples, and compatibility |

Profiles can combine: a Laravel application may also need PHP and frontend guidance.
Adapt them to existing versions and local instructions; available profiles do not establish the project's stack.

## Agents

Repeat --agent to select the clients you use:

~~~sh
python scripts/install.py /path/to/project --agent codex --agent claude --agent cursor
~~~

Explicit selections replace recorded choices; tracked adapters left on disk block the change. The installer never deletes adapters.

| Client | Entry provided |
| --- | --- |
| Codex | AGENTS.md and .agents/skills/ |
| Claude Code | CLAUDE.md importing AGENTS; skill copies in .claude/skills/ |
| Kimi / Manus | Short entry files to supply explicitly |
| Copilot | .github/copilot-instructions.md |
| Cursor | .cursor/rules/ai-kit.mdc |
| Aider | CONVENTIONS.md; load with --read CONVENTIONS.md |

Verify instruction and skill loading in the actual client; see [adapter details](template/ai-kit/ADAPTERS.md). Opt-in extras: --with-session-start, --with-guards, --with-ci.

## Sharing

Choose how others will receive the project's rules:

| Mode | Shared AI-KIT files in Git | Suitable for |
| --- | --- | --- |
| private | Ignored | Local instructions installed separately |
| team | Visible | Teammates and agents working from fresh clones |

Both modes exclude secrets, personal overrides, installer state, and caches. A private-mode clone needs kit installation; team files can be versioned.

The installer owns one marked .gitignore block. Other rules survive and may still hide team files; reconcile them explicitly.
Ignore rules do not remove files already tracked by Git.

Manifests/checksums/locks stay visible, including composer.lock for applications, go.mod, go.sum, and Python/frontend locks.
Composer, Moodle, Node, and Python exclusions are scoped to verified module manifests, preserving deliberate Go vendoring and executable source.
See [ignore adaptation](template/ai-kit/BOOTSTRAP.md#ignore-adaptation).

## Update an application project

Preview a reviewed newer bundle against the same application path. Context/history survives; unchanged managed instructions update from their baseline, local adaptations need review.

Conflicts leave the accepted installation unchanged. Apply creates candidates under ai-kit/.upstream-cache/candidates/<source-hash>/ with metadata; existing drafts survive. Compare and merge using the reported paths.

After reviewing a merge to AGENTS.md:

~~~sh
python scripts/install.py /path/to/project --accept-local AGENTS.md
python scripts/install.py /path/to/project --accept-local AGENTS.md --apply
~~~

Repeat --accept-local for each reviewed managed path; local adaptations require review again when that upstream file changes. Changed existing files are backed up in ai-kit/.upstream-cache/backups/.

Exit codes: 0 success; 1 refusal/failure; 2 unresolved file/adapter conflicts. Invalid state/settings are refused before writes; preview creates nothing.

The installer works offline. The agent follows [UPSTREAM](template/ai-kit/UPSTREAM.md) to check the configured source; unavailable access means verified local fallback with freshness marked unverified.

## Check an installed project

Run the offline health check against an installed application:

~~~sh
python scripts/doctor.py /path/to/project
~~~

It validates installer state/settings and reports missing or modified managed files, missing owned documents, pending candidates, budget overflows, broken Markdown links/anchors, and stale provider verifications. Exit code 0 means no errors; warnings mark work worth reviewing.

## Docker and model routing

For container-dependent work, check the Docker client and daemon. A stopped daemon prompts a startup request while independent work continues.
New services follow the [Kubernetes-ready contract](template/ai-kit/CONTAINERS.md) (configuration, health, shutdown, storage, manifests).

Collect read-only resource evidence with:

~~~sh
python scripts/docker_test_usage.py --project my-app-tests
~~~

The container guide owns size, ownership, and cleanup protections.

[Routing policy](template/ai-kit/router/POLICY.md) guides capability/effort choices; defaults live in [the provider configuration](template/ai-kit/router/providers/openai.json).
Model switching depends on supported runtime controls.

## Repository layout

The reference repository maintains the kit. Application installation uses template/.

| Path | Purpose |
| --- | --- |
| template/ | Clean project instructions, context, skills, and docs |
| templates/ | Private/team application ignore policies |
| scripts/ | Installer, project doctor, checker, and Docker helper |
| integrations/ | Optional client entries and guard examples |
| docs/ | Kit decisions, evidence, and archived history |
| ai-kit/ | Pointers for old reference paths |
| Root README/context/changelog | AI-KIT's own docs and history |

The root .gitignore keeps reference sources visible.

Maintainers: see [updating a reference repository](CONTRIBUTING.md#updating-a-reference-repository).

## Check and contribute

Run from the reference repository root:

~~~sh
python scripts/check_kit.py
python -m unittest discover -s tests -v
~~~

The checker covers internal links/anchors, skills, registry, template boundaries, JSON, content hygiene, and Git visibility when available.
External links and native client behavior need separate verification.

CI defines Windows/Linux jobs for Python 3.10/3.13. See [GitHub Actions](https://github.com/tigusigalpa/ai-kit/actions) for hosted results and [verification](docs/IMPLEMENTATION.md#verification) for local evidence/limits.

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for improvements and [SECURITY.md](SECURITY.md) for vulnerability reporting.
Useful additions come from actual project work: a missing check, an unclear instruction, or a convention worth preserving.

## License

AI-KIT is released under [MIT](LICENSE). The kit's license covers the kit; choose and verify your application's license separately.
