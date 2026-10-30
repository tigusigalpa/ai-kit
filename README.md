# AI-KIT

![AI KIT](https://i.postimg.cc/BvrB6sKt/ai-kit-hero-banner.jpg)

**Stop re-explaining your project to every new AI chat.**

AI-KIT gives your coding agents persistent project memory, expert stack rules, **Kubernetes-ready** container guidance, an **adaptive model routing** policy, and native entry files and configuration for **11 AI clients**. Add **Cloudflare security-audit** for structured security review and **Strix** for scoped pentesting workflows. One offline installer, zero installer dependencies, changes previewed before you apply them.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](#get-ai-kit)
[![PyPI version](https://img.shields.io/pypi/v/ai-kit-python?logo=pypi&logoColor=white)](https://pypi.org/project/ai-kit-python/)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-2ea44f)](scripts/install.py)
[![AI clients: 11](https://img.shields.io/badge/AI%20clients-11-7c3aed)](#works-with-your-ai-clients)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-ai--kit-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/tigusigalpa/ai-kit)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Docs site](https://img.shields.io/badge/docs-ai--kit--docs-7c3aed?logo=githubpages&logoColor=white)](https://tigusigalpa.github.io/ai-kit-docs/)

What changed in each release: [CHANGELOG](CHANGELOG.md).

[Get AI-KIT](#get-ai-kit) · [Defaults](#defaults-you-should-know) · [Features](#features-at-a-glance) · [Honest boundaries](#honest-boundaries) · [Quick start](#install) · [Docs site](https://tigusigalpa.github.io/ai-kit-docs/) · [Guides](docs/guide/README.md) · [Install guide](docs/guide/INSTALL.md) · [CLI flags](docs/guide/INSTALLER_FLAGS.md) · [Windows](docs/guide/WINDOWS.md) · [Docker](docs/guide/DOCKER.md)

<div align="center">
<table>
<tr>
<td align="center">

### 📘 Interactive documentation site

**Build your install command in the browser instead of reading flag tables.**

Pick your AI clients, preset, sharing mode, chat language and optional modules: the configurator writes the exact preview and apply commands for PowerShell or Bash and shows the resulting `settings.json` and file list. Every option is a real installer flag, and the commands are generated locally in your browser.

[![Open the documentation site](https://img.shields.io/badge/Open%20the%20docs-ai--kit--docs-7c3aed?style=for-the-badge&logo=githubpages&logoColor=white)](https://tigusigalpa.github.io/ai-kit-docs/)

[⚙️ Command configurator](https://tigusigalpa.github.io/ai-kit-docs/#configure) · [💻 Install the CLI](https://tigusigalpa.github.io/ai-kit-docs/#install) · [🩺 After install](https://tigusigalpa.github.io/ai-kit-docs/#commands) · [📖 Flag reference](https://tigusigalpa.github.io/ai-kit-docs/#reference) · [❓ FAQ](https://tigusigalpa.github.io/ai-kit-docs/#faq)

<sub>English and Russian · light and dark themes · Windows PowerShell and Linux/macOS Bash</sub>

</td>
</tr>
</table>
</div>

## Get AI-KIT

**Python package (recommended).** Requires Python 3.10+; no mandatory third-party runtime dependencies.

~~~sh
pipx install ai-kit-python
aikit --version
~~~

The PyPI package is **`ai-kit-python`**; the command it installs is **`aikit`**. Never run `pip install aikit`: that is not this project's package name. Without pipx, run `python -m pip install ai-kit-python` inside a virtual environment. On Windows, the [Windows guide](docs/guide/WINDOWS.md) covers PATH and interpreter problems.

**Docker image.** [`tigusigalpa/ai-kit`](https://hub.docker.com/r/tigusigalpa/ai-kit) runs the same CLI without host Python (`linux/amd64`). Image tags follow the repository [VERSION](VERSION) of each release and there is no `latest` tag, so pick a version from the [tags page](https://hub.docker.com/r/tigusigalpa/ai-kit/tags), for example the published `1.4.5`:

~~~sh
docker pull tigusigalpa/ai-kit:1.4.5
docker run --rm tigusigalpa/ai-kit:1.4.5 --version
~~~

Project mounts, preview/apply examples and the runtime contract are in [Run AI-KIT with Docker](docs/guide/DOCKER.md).

**Source checkout (alternative).**

~~~sh
git clone https://github.com/tigusigalpa/ai-kit.git
cd ai-kit
python scripts/install.py --help
~~~

From a checkout, run `python scripts/install.py` or `python aikit_cli.py COMMAND` directly, or run `python -m pip install .` there to get the `aikit` command. Details: [Get the CLI](docs/guide/INSTALL.md#get-the-cli).

## Defaults you should know

> [!IMPORTANT]
> **Chat replies default to Russian, and conventions default to the owner's opinionated Laravel conventions**, including **no database foreign key constraints**, a public UUID beside the internal ID, Policy/Factory/Seeder per model and one table per migration. Authored project files are always English.
>
> For English replies and your project's own conventions, add both flags to the preview and the apply command:
>
> ~~~sh
> aikit install /path/to/my-app --chat-language English --conventions standard
> ~~~
>
> Other fresh defaults: private sharing mode, the `codex` client and maximum Docker cleanup. Choices are saved in `ai-kit/settings.json` and reused on upgrades. [All defaults](docs/guide/INSTALL.md#choose-your-defaults) · [Owner profile](template/ai-kit/profiles/OWNER.md)

## Features at a glance

![Features at a glance](https://i.postimg.cc/BbPSVW8b/01-features-at-a-glance.jpg)

| | Feature | What it does for you |
| --- | --- | --- |
| 🧠 | **Project memory** | Verified facts, module map, commands, and decisions that every new chat reads first |
| 🧩 | **Stack profiles** | Expert rules for Go, PHP, Laravel, Filament 5, Moodle, Python, Rust, .NET, Java, Terraform/Helm, frontend, and libraries, auto-detected per module |
| 🐳 | **Kubernetes-ready container guidance** | The kit instructs agents to make new Dockerfiles and services Kubernetes-ready: probes, graceful shutdown, non-root execution and manifests |
| 🧭 | **Adaptive model routing** | A 0-6 capability ladder; the routing policy recommends a model role and reasoning effort per task. No savings are claimed |
| 🤖 | **11 AI clients** | Native entry files and configuration for Codex, Claude Code, Cursor, Copilot, Gemini CLI, Windsurf, Cline, Roo, Aider, Kimi and Manus. Documentation for Kimi and Manus is unverified, and activation in actual clients is unverified |
| 🎯 | **Native client configuration** | Claude Code allow rules for the recorded test/lint/build commands (with `--with-native-settings`); module rules scoped to the paths where they apply (with `--with-scoped-rules`) |
| 🛡️ | **Guardrails that reduce risk** | No commits without your request, optional ask rules before destructive commands, deny rules and ignore files for secret files. Not a security boundary |
| 🔐 | **Optional security workflows** | Cloudflare's audit method and nine Strix skills, pinned and invoked explicitly in Codex or Claude Code |
| 🎨 | **Optional Web Design** | Annotated references and a brief become a coherent visual system, stack-aware implementation and recorded UI acceptance; includes a dedicated Blade route |
| 🔁 | **Engineering loop** | Plan → implement → test → review → document, with honest reporting of what was really checked |
| ⚡ | **One-command workflows** | `/ai-kit-bootstrap`, `/ai-kit-review`, `/ai-kit-sync-context` |
| 📦 | **Safe installer and upgrades** | Preview first, offline, backups, conflict candidates, explicit unchanged-adapter retirement, your local edits preserved |
| 🐋 | **Docker CLI image** | Run the bundled installer and helpers without host Python; mount your project, preview changes and apply explicitly |
| 🗂️ | **Shared dialogue context** | Import two conversations locally, review conflicting claims and export the same reference state for ChatGPT and OpenRouter |

## Why AI-KIT

![Why AI-KIT](https://i.postimg.cc/qq6J5ftv/02-why-ai-kit.jpg)

AI-KIT preserves facts and decisions, points agents at real checks and records authorization boundaries:

- **Project knowledge:** manifests draft module facts and commands; bootstrap verifies them.
- **Stack depth:** relevant profiles cover framework authorization, transactions, cancellation, privacy and infrastructure review.
- **Your authority:** explicit commits/pushes, optional risky-command guards and secret exclusions.
- **Visible evidence:** unavailable checks remain unverified.

```mermaid
flowchart LR
    A[aikit install preview] --> B[apply]
    B --> C["/ai-kit-bootstrap"]
    C --> D[plan → implement → test → review → document]
    D --> E["/ai-kit-sync-context"]
    E --> D
```

## Feature tour

### Project memory that survives every chat

- **Verified context:** PROJECT_CONTEXT and project.json hold contracts, module facts, commands and unknowns.
- **Manifest drafts:** Go, Composer, Node, Python and Moodle evidence suggests versions and module commands until bootstrap confirms them.
- **Session start:** an optional Claude hook reads context and Git status.
- **Continuity:** decisions, ADRs and changelog preserve reasons; the continuity skill keeps context and pointers synchronized.

[What lands in your project](docs/guide/INSTALL.md#what-lands-in-your-project)

### Built for your stack

| Profile | What the agent gets right |
| --- | --- |
| [Go](template/ai-kit/stacks/GO.md) | Context propagation, timeouts, error wrapping, goroutine ownership, `-race`, govulncheck, deliberate vendoring |
| [PHP](template/ai-kit/stacks/PHP.md) | Composer and PSR boundaries, exact money, bounded HTTP, narrow exceptions, `composer audit` |
| [Laravel](template/ai-kit/stacks/LARAVEL.md) | Policies, bounded transactions, after-commit jobs, idempotent effects, N+1 checks, safe migrations |
| [Filament 5](template/ai-kit/stacks/FILAMENT.md) | Resources, schemas, tables, and actions with server-side authorization, tenant scope, and bounded queries |
| [Moodle](template/ai-kit/stacks/MOODLE.md) | Plugin APIs, capabilities and `sesskey`, upgrade savepoints, Privacy API, cache invalidation |
| [Python](template/ai-kit/stacks/PYTHON.md) | Safe CLIs, pathlib, subprocess without a shell, isolated environments, uv/ruff for new packages |
| [Frontend](template/ai-kit/stacks/FRONTEND.md) | Pinned package manager, type/lint/build checks, accessibility, public-config hygiene |
| [Library/SDK](template/ai-kit/stacks/LIBRARY.md) | Public API stability, semantic versioning, consumer examples, compatibility matrices |
| [Rust](template/ai-kit/stacks/RUST.md) | Ownership and borrowing, unsafe discipline, Result errors, cargo fmt/clippy/test, lockfile hygiene |
| [.NET](template/ai-kit/stacks/DOTNET.md) | Nullable types, async with CancellationToken, deterministic disposal, dotnet build/test |
| [Java](template/ai-kit/stacks/JAVA.md) | Maven/Gradle wrappers, exception boundaries, try-with-resources, wrapper test/verify |
| [Terraform/Helm](template/ai-kit/stacks/INFRA.md) | Remote state, plan review, pinned providers and charts, fmt/validate and lint/template gates |

Profiles combine per module, so a monorepo with a Laravel app in `web/` and a Go service in `api/` gets the right rules in each place. Opinionated **owner conventions** for Laravel (no database foreign keys, public UUID beside the internal id, Policy + Factory + Seeder per model, one table per migration, Filament 5+ for new panels) are the default; use `--conventions standard` to follow your project's own conventions instead.

### Docker-aware, Kubernetes-ready guidance

The kit instructs agents to make new Dockerfiles and services Kubernetes-ready, following the [Kubernetes-ready contract](template/ai-kit/CONTAINERS.md), including local Docker Compose projects:

- **Images/runtime:** pinned multi-stage images, build secrets outside layers, non-root execution, read-only root, exec entrypoints; no privileged mode or Docker socket.
- **Lifecycle:** startup/readiness/liveness probes, SIGTERM drain, migrations in separate Jobs.
- **Deployment:** ConfigMap/Secret, stdout logs, stateless replicas, PVCs where needed, dropped capabilities, seccomp and resource requests.
- **Preflight/cleanup:** verify Docker client/daemon; after every Docker task remove eligible disposable containers, volumes, networks and superseded test images. The default `maximum` mode also removes the dedicated builder and its cache, without a size threshold, and reclaims host RAM/disk; `--docker-cleanup keep-cache` keeps the builder cache. [Cleanup modes and host reclamation](docs/guide/DOCKER.md#docker-cleanup-and-host-reclamation).

### Adaptive model routing

The [routing policy](template/ai-kit/router/POLICY.md) recommends a model role and reasoning effort for each task on a 0-6 capability ladder: the cheap role for classification and narrow mechanical edits, the work role for engineering and hard debugging, escalation after a diagnosed capability shortfall. Provider configurations map roles to OpenAI, Anthropic, Kimi, and Gemini models, or your own local/Ollama models. The offline helper understands English and Russian task descriptions and explains its choice:

~~~sh
aikit route "debug a race condition in the queue worker"
~~~

It is a recommendation, and no cost savings are claimed. The kit never fakes a model switch: when a client offers no switching control, you get a recommendation. [Levels, providers and configuration](docs/guide/MEASUREMENT.md#adaptive-model-routing).

### Works with your AI clients

| Client | What gets installed |
| --- | --- |
| Codex | `AGENTS.md` and `.agents/skills/` |
| Claude Code | `CLAUDE.md` importing AGENTS, skills, settings, path-scoped `.claude/rules/` |
| Cursor | `.cursor/rules/` with module globs, `.cursorignore` secrets |
| GitHub Copilot | `copilot-instructions.md` and per-module `.instructions.md` |
| Gemini CLI | `GEMINI.md` and `.geminiignore`; reads the shared skills |
| Windsurf, Cline, Roo | Native rule folders, with glob- or path-scoped module rules for Windsurf and Cline |
| Aider | `CONVENTIONS.md` and `.aiderignore`, plus model routing config |
| Kimi, Manus | Short entry files |

Scoped rules, ignore files, and settings come with the native-settings and scoped-rules extras. The preview spots the clients you already use from existing files and suggests the matching `--agent` list. Copying files does not prove that a client discovers or activates them, and documentation for Kimi and Manus is unverified; `aikit adapters report --project TARGET` lists each client's documentation status.

### Native configuration from your project facts

- **Recorded checks:** Claude Code allow rules for the recorded test/lint/build commands (with `--with-native-settings`).
- **Secret exclusions:** shared lists cover env files, keys, Composer auth, Laravel/Moodle credentials and .pypirc through selected client deny/ignore controls.
- **Module scope:** native rules select relevant guidance by file path (with `--with-scoped-rules`).
- **Owned entries:** Claude settings merge by key, using local settings in private mode and moving only kit entries on mode switches.

### Guardrails that reduce risk

These guardrails reduce risk through instructions, client ask/deny rules and ignore files. They are not a security boundary or a sandbox.

- **No surprise commits.** Commits and pushes require your explicit request, and optional Claude Code ask rules back that up.
- **Confirmation before damage.** With data guards, Claude Code asks before `rm -rf`, `git reset --hard`, `git clean`, a Docker prune, or a Laravel/Moodle migration.
- **Secret files.** Deny rules and ignore files discourage reads of common secret files in clients that honor them; they do not encrypt or lock those files.
- **Security baseline:** input validation, server-side authorization, and no secrets in code, logs, or prompts. Dependency audits run per stack with `composer audit`, `govulncheck`, `pip-audit`, and your package manager's audit.
- **Honest verification:** unavailable tools, services, or CI are reported as unverified, never as passed.

### Engineering loop and one-command workflows

Every task follows **plan → implement → test → review → document**, with staged migrations and rollback plans, review by concrete scenario and severity, and a changelog entry for every change. Owner conventions add a Codecov gate of at least 90% of changed lines when Codecov is configured. Three user-invoked skills make the routine instant:

- `/ai-kit-bootstrap` confirms installer drafts and fills context from real evidence.
- `/ai-kit-review` reviews current changes against the engineering and security rules.
- `/ai-kit-sync-context` updates context, decisions, and the changelog after work.

In Codex, use `$ai-kit-bootstrap` and the other skills the same way.

### Security workflows

| Integration | What it adds | Install flag | Codex / Claude Code |
| --- | --- | --- | --- |
| **Cloudflare security-audit** | Security guidance and focused review; a full audit method with reconnaissance, hunting, evidence validation, coverage and reporting | `--with-security-audit` | `$security-audit` / `/security-audit` |
| **Strix** | Workflows for code, web application, API and OWASP testing, findings review and requested remediation; separate CI/cloud references | `--with-strix` | `$strix` / `/strix` |

Both are off by default, pinned to reviewed upstream revisions and invoked explicitly. Installation copies files only: it runs no audit or scan, and a Strix scan needs its own CLI, Docker, model access and authorized targets. [Security workflows guide](docs/guide/SECURITY_WORKFLOWS.md).

### Web Design

Give your agent the sites you like, a short brief and the target project. The optional module (`--with-web-design`) organizes that material into one visual direction, reusable components and a working interface with recorded checks, with a detailed Laravel/Blade route and conditional guidance for Tailwind, Bootstrap, Alpine, Livewire, daisyUI, Flowbite and Flux. It installs no external tools and generates or deploys nothing by itself. [Web Design guide](docs/guide/WEB_DESIGN.md): [implementation routes](docs/guide/WEB_DESIGN_STACKS.md) · [tools, review and troubleshooting](docs/guide/WEB_DESIGN_TOOLS.md).

### Library documentation with Context7

The optional `context7-docs` workflow (`--with-context7`) checks the dependency version, resolves the library, retrieves focused examples and records source/coverage gaps. MCP connection and authentication stay separate. [Context7 guide](docs/guide/CONTEXT7.md).

### Shared context from two dialogues

The offline `aikit memory` command imports two conversations, preserves their sources, shows contradictions for your review and exports the same reviewed reference state as ChatGPT Markdown and an OpenRouter request fragment. It uploads nothing and needs no API key. [Dialogue context guide](docs/guide/DIALOGUE_MEMORY.md).

### Optional orchestration

`--with-orchestration` adds scoped Codex helper agents and a disabled-by-default, bounded OpenRouter text executor with explicit apply, capped-key preflight, private accounting and review. Installation launches no agents and makes no paid calls. [Orchestration guide](docs/guide/ORCHESTRATION.md).

### Working with OpenRouter

AI-KIT rules, project facts and selected context can travel with your API requests; the guide covers request layout, prompt and response caching, and measuring actual usage. [OpenRouter guide](docs/guide/OPENROUTER.md).

### Run AI-KIT with Docker

The `tigusigalpa/ai-kit` image runs the installer and helpers with a read-only root, no network and an explicit project mount: preview with a read-only mount, then apply with a writable one. [Docker guide](docs/guide/DOCKER.md).

### Measure, recommend and select context

`aikit benchmark` runs isolated A/B/C trials through a reviewed worker, `aikit route --mode adaptive` recommends from comparable history, and `aikit context select` selects module rules within a byte budget. [Measurement guide](docs/guide/MEASUREMENT.md).

### More built in

- **Language/sharing:** English files, Russian chat by default; private or team instructions. [Sharing](docs/guide/INSTALL.md#sharing).
- **Health:** `aikit doctor TARGET` reports managed-file, link, provider and context drift; `--fix` previews a repair plan and `--fix --apply` writes it, preserving local edits.
- **CI:** `--with-ci` adds a workflow that validates the committed AI-KIT files; it does not clone or install AI-KIT and is meaningful in team mode.
- **Measurements:** `aikit metrics` records supplied attempt/token/cost evidence and analyzes provider results. No automatic telemetry; evaluation checks opaque pair coverage.

## Honest boundaries

![Honest boundaries](https://i.postimg.cc/kgHZybJq/09-honest-boundaries.jpg)

- **Installation copies files.** It runs no audit, scan, model call, cleanup or external tool setup; optional modules need their own tools, credentials and authorization.
- **Client activation is unverified.** AI-KIT writes native entry files and configuration; whether a client discovers and applies them must be checked in that client. Documentation for Kimi and Manus is unverified.
- **Routing recommends.** Confirm actual client controls; no cost savings are claimed.
- **Guardrails reduce risk.** Permission rules and ignores are not a security boundary.
- **Measurement needs evidence.** The benchmark requires its own reviewed protocol worker. Optional OpenRouter text execution is separately enabled and explicitly applied; native client activation and end-to-end savings require independent verification.
- **CI checks files, not behavior.** The `--with-ci` workflow validates committed AI-KIT files only; it does not run your application's tests.

## Install

Quick start in three steps.

![Install](https://i.postimg.cc/pr5W6N9m/04-install.jpg)

Use an application folder outside any AI-KIT checkout.

**1. Preview.** Nothing is written:

~~~sh
aikit install /path/to/my-app --preset solo --agent codex --agent claude
~~~

On Windows use a path like `"C:\Projects\my-app"`. The preview lists writes, preserved files, conflicts, and detected stacks/clients. Add `--chat-language English --conventions standard` here and in step 2 to change the [defaults](#defaults-you-should-know).

**2. Apply** the same command with `--apply`; add `--check` to run the doctor right away:

~~~sh
aikit install /path/to/my-app --preset solo --agent codex --agent claude --apply --check
~~~

**3. Bootstrap.** Open your AI client in the project and run `/ai-kit-bootstrap` (Claude Code) or `$ai-kit-bootstrap` (Codex). For other clients, give it [BOOTSTRAP_PROMPT.md](BOOTSTRAP_PROMPT.md).

Existing project documents and context are never overwritten; customized instructions become reviewable conflicts. From a source checkout, `python scripts/install.py` takes the same arguments; in Docker, see [preview and apply](docs/guide/DOCKER.md).

## Documentation

- **[Documentation site](https://tigusigalpa.github.io/ai-kit-docs/)**: an interactive command configurator, CLI installation for Windows and Linux/macOS, post-install commands and a searchable flag reference, in English and Russian
- [All guides](docs/guide/README.md)
- [Install AI-KIT and set up a project](docs/guide/INSTALL.md): CLI, defaults, presets, what lands in your project, sharing, updates
- [Installer flags and options](docs/guide/INSTALLER_FLAGS.md)
- [Windows: installation and troubleshooting](docs/guide/WINDOWS.md)
- [Run AI-KIT with Docker](docs/guide/DOCKER.md), including Docker cleanup and host reclamation
- [Security workflows](docs/guide/SECURITY_WORKFLOWS.md), [Web Design](docs/guide/WEB_DESIGN.md), [Context7](docs/guide/CONTEXT7.md), [shared dialogue context](docs/guide/DIALOGUE_MEMORY.md)
- [Optional orchestration](docs/guide/ORCHESTRATION.md), [working with OpenRouter](docs/guide/OPENROUTER.md), [measurement and context selection](docs/guide/MEASUREMENT.md)
- [CHANGELOG](CHANGELOG.md) · [SKILL.md](SKILL.md) · [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [License](LICENSE)

## Teach any AI about AI-KIT

![Teach any AI about AI-KIT](https://i.postimg.cc/nLQWShrf/14-teach-any-ai.jpg)

The repository is a skill: [SKILL.md](SKILL.md) covers installation, configuration, upgrades and maintenance. For Claude Code, clone into your skills directory:

~~~sh
git clone https://github.com/tigusigalpa/ai-kit.git ~/.claude/skills/ai-kit
~~~

For other assistants, share the repository or SKILL.md.

## For maintainers

Applications install from `template/`; the root maintains AI-KIT itself. Before contributing, run:

~~~sh
python scripts/check_kit.py
python -m unittest discover -s tests -v
~~~

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [maintainer guide](docs/guide/MAINTAINERS.md) for local maintainer files, publication copy and the PyPI release procedure.

## License

AI-KIT is released under [MIT](LICENSE); bundled Cloudflare references retain MIT and Strix references retain Apache-2.0. Choose and verify your application's license separately.
