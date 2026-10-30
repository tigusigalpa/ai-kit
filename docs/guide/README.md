# AI-KIT user guides

Start with the [root README](../../README.md) for the overview, defaults and a three-step quick start. These guides hold the detailed instructions.

## Guides

| Guide | What it covers |
| --- | --- |
| [Install AI-KIT and set up a project](INSTALL.md) | Getting the `aikit` CLI (pipx, virtual environment, source checkout, Docker), installing into a project, defaults and presets, what lands in your project, sharing modes, updates and health checks |
| [Installer flags and options](INSTALLER_FLAGS.md) | Every `aikit install` option with accepted values, defaults and persistence, optional module flags, common combinations and similarly named options in other commands |
| [Windows: installation and troubleshooting](WINDOWS.md) | PowerShell quick start for an empty project, isolated CLI without activation, PATH repair, multiple Python installations and an error guide |
| [Run AI-KIT with Docker](DOCKER.md) | The published image, local builds, preview/apply mounts on Windows and Linux/macOS, the runtime contract, the Kubernetes preview Job, Docker cleanup modes and host RAM/disk reclamation |
| [Security workflows](SECURITY_WORKFLOWS.md) | Pinned Cloudflare security-audit and Strix skills: installation, invocation, prerequisites and limits |
| [Web Design](WEB_DESIGN.md) | Part 1: installation, what the module installs, the brief, design memory, context selection and one visual direction |
| [Web Design: implementation routes](WEB_DESIGN_STACKS.md) | Part 2: choosing a route; Blade, Tailwind, Bootstrap, daisyUI/Flowbite/Flux, Alpine and Livewire |
| [Web Design: tools, review and troubleshooting](WEB_DESIGN_TOOLS.md) | Part 3: TypeUI, SkillUI, browser acceptance, starter requests, updates and troubleshooting |
| [Library documentation with Context7](CONTEXT7.md) | The optional `context7-docs` workflow and its separate connection setup |
| [Shared context from two dialogues](DIALOGUE_MEMORY.md) | Importing two conversations, reviewing facts and contradictions, exporting for ChatGPT and OpenRouter |
| [Optional orchestration](ORCHESTRATION.md) | Codex helper agents and the bounded OpenRouter text executor: configuration, budgets, review, accounting and recovery |
| [Working with OpenRouter](OPENROUTER.md) | Reusing AI-KIT rules and context in API requests, caching and measurement; a proposed adapter design |
| [Measure, recommend and select context](MEASUREMENT.md) | Benchmark trials, adaptive routing recommendations, local metrics, context selection and client documentation evidence |
| [For maintainers](MAINTAINERS.md) | Maintainer checks, publication copy, the PyPI release procedure and release verification records |

## Contracts and maintainer records

The guides explain usage. These documents are the maintained contracts and verification records:

- [Docker image contract and results](../DOCKER.md)
- [Web Design integration record](../WEB_DESIGN.md)
- [Dialogue memory contract](../DIALOGUE_MEMORY.md)
- [Orchestration implementation record](../ORCHESTRATION.md)
- [Context7 integration record](../CONTEXT7.md)
- [Strix integration record](../STRIX.md)
- [Benchmark contract](../BENCHMARK.md)
- [PyPI release guide](../PYPI.md)

Installed agent rules live under [template/ai-kit](../../template/ai-kit/CORE.md); the [Core](../../template/ai-kit/CORE.md) owns language, Git authorization and fact verification.

## Changes after 1.4.5

These behaviors are in the current source and are not part of the published 1.4.5 packages and image. Check `aikit --version` and `aikit COMMAND --help` for what your installed version supports.

- `aikit doctor TARGET --fix` previews the repair plan; `--fix --apply` writes it. [Health checks](INSTALL.md#check-project-health).
- The `--with-ci` workflow validates the committed AI-KIT files without cloning or installing AI-KIT; it is meaningful in team mode. [Module flags](INSTALLER_FLAGS.md#optional-module-flags).
- The `docker_cleanup` setting and `--docker-cleanup maximum|keep-cache` flag. [Cleanup modes](DOCKER.md#docker-cleanup-and-host-reclamation).
- `--with-security-audit` no longer installs the upstream `*.test.cjs` files. [Security workflows](SECURITY_WORKFLOWS.md).
- Kit text files are LF in every distribution; upgrades treat line-ending-only differences as unchanged. [Updates](INSTALL.md#update-an-application-project).
- The Docker image handles SIGTERM as PID 1, so `--init` is optional. [Runtime contract](DOCKER.md#other-commands-and-writable-paths).

## Where former README sections live

| Former README section | Now |
| --- | --- |
| Install, Packaged CLI and PyPI status | [Install AI-KIT and set up a project](INSTALL.md) |
| Installer flags and options | [Installer flags and options](INSTALLER_FLAGS.md) |
| Choose your defaults, Presets, What lands in your project, Sharing, Update an application project | [Install AI-KIT and set up a project](INSTALL.md) |
| Publish future releases to PyPI, release verification notes, For maintainers | [For maintainers](MAINTAINERS.md) |
| Windows: installation and troubleshooting | [Windows guide](WINDOWS.md) |
| Run AI-KIT with Docker, Maximum Docker cleanup and host reclamation | [Run AI-KIT with Docker](DOCKER.md) |
| Security workflows | [Security workflows](SECURITY_WORKFLOWS.md) |
| Web Design | [Part 1](WEB_DESIGN.md), [part 2](WEB_DESIGN_STACKS.md), [part 3](WEB_DESIGN_TOOLS.md) |
| Library documentation with Context7 | [Context7](CONTEXT7.md) |
| Shared context from two dialogues | [Dialogue context](DIALOGUE_MEMORY.md) |
| Optional orchestration | [Optional orchestration](ORCHESTRATION.md) |
| Working with OpenRouter | [Working with OpenRouter](OPENROUTER.md) |
| Measure, recommend and select context; routing details | [Measurement](MEASUREMENT.md) |
