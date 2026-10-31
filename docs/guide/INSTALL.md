# Install AI-KIT and set up a project

![Install](https://i.postimg.cc/pr5W6N9m/04-install.jpg)

This guide covers getting the `aikit` CLI, installing AI-KIT into an application project, the defaults you start with, what lands in your project, sharing modes and later updates. The complete option reference is [Installer flags and options](INSTALLER_FLAGS.md). Windows setup and PATH problems are covered in the [Windows guide](WINDOWS.md); container use is covered in [Run AI-KIT with Docker](DOCKER.md).

## Get the CLI

You need Python 3.10 or later. AI-KIT has no mandatory third-party runtime dependencies; the installer uses only the standard library.

The PyPI package is **`ai-kit-python`**. The command it installs is **`aikit`**, and its module entry point is `python -m aikit.aikit_cli`. Never run `pip install aikit`: `aikit` is not this project's package name.

### pipx: isolated CLI (recommended)

~~~sh
pipx install ai-kit-python
aikit --version
~~~

Update the CLI with `pipx upgrade ai-kit-python`.

### Python virtual environment

Install into a virtual environment. On Windows PowerShell:

~~~powershell
$cliEnv = Join-Path $env:LOCALAPPDATA 'AI-KIT\venv'
python -m venv "$cliEnv"
& "$cliEnv\Scripts\python.exe" -m pip install ai-kit-python
& "$cliEnv\Scripts\aikit.exe" --version
~~~

These explicit executable paths work without activating the environment or changing PATH. The [Windows guide](WINDOWS.md) covers both short commands and interpreter-bound launches. Update with `python -m pip install --upgrade ai-kit-python`, run by the same environment's Python.

~~~powershell
& "$cliEnv\Scripts\aikit.exe" install "C:\Projects\my-app" --agent codex --mode private
& "$cliEnv\Scripts\aikit.exe" install "C:\Projects\my-app" --agent codex --mode private --apply --check
& "$cliEnv\Scripts\aikit.exe" doctor "C:\Projects\my-app"
~~~

Then open that application in your client and run its bootstrap workflow. The CLI bundles templates and optional integration resources, uses no runtime third-party dependencies and preserves local documents/conflicts.

### Source checkout

~~~sh
git clone https://github.com/tigusigalpa/ai-kit.git
cd ai-kit
~~~

Use a reviewed revision and an application path outside this directory. Without installing anything, run `python scripts/install.py ...`, or reach every command through one dispatcher: `python aikit_cli.py install|doctor|route|metrics|benchmark|check|…`. To get the `aikit` command from the reviewed checkout instead, run `python -m pip install .` there.

### Docker image

The published image `tigusigalpa/ai-kit` runs the same CLI with Python, Git, the packaged kit and optional integration resources, without a host Python installation. See [Run AI-KIT with Docker](DOCKER.md).

The package is published on [PyPI](https://pypi.org/project/ai-kit-python/). Updating the CLI, by any route, does not rewrite installed application instructions; update projects separately through [preview and apply](#update-an-application-project).

## Install into a project

**On Windows:** start with the [PowerShell guide](WINDOWS.md), including an empty-project walkthrough, PATH repair and common errors.

**1. Preview.** Nothing is written:

~~~sh
aikit install /path/to/my-app --preset solo --agent codex --agent claude
~~~

From a source checkout, `python scripts/install.py` accepts the same arguments. On Windows use a path like `"C:\Projects\my-app"`. The preview lists writes, preserved files, conflicts, and detected stacks/clients. Add `--interactive` for a guided prompt.

**2. Apply** the same command with `--apply`; add `--check` to run the doctor right away:

~~~sh
aikit install /path/to/my-app --preset solo --agent codex --agent claude --apply --check
~~~

**3. Bootstrap.** Open your AI client in the project and run `/ai-kit-bootstrap` (Claude Code) or `$ai-kit-bootstrap` (Codex). For other clients, give it [BOOTSTRAP_PROMPT.md](../../BOOTSTRAP_PROMPT.md).

Existing project documents and context are never overwritten; customized instructions become reviewable conflicts.

## Choose your defaults

![Choose your defaults](https://i.postimg.cc/FzkrBtfs/05-choose-your-defaults.jpg)

Project choices live in `ai-kit/settings.json`; defaults are in [the settings template](../../template/ai-kit/settings.json).

| Setting | Default | Meaning |
| --- | --- | --- |
| Project language | English | Authored project files use English |
| Chat language | English | Plans, explanations, and replies use English; upgrades preserve the saved language |
| Sharing mode | private | Local AI-KIT files are excluded from Git |
| Conventions | owner | The owner's opinionated Laravel conventions apply when that stack is confirmed, including no database foreign key constraints |
| Agent selection | codex | Default entry points and source skills |
| Public UUID guidance | off | Enable for any stack with `--with-uuid`; owner conventions do not enable it |
| Claude GitHub identity | off | `--with-claude-github` verifies the active human account before authorized commits; all Claude installs suppress its added commit-credit trailer |
| Docker cleanup | maximum | After every Docker task, agents remove all eligible disposable resources, including the dedicated builder and its cache, and reclaim host resources (setting `docker_cleanup`, added after 1.4.5) |

To select Russian chat replies and your project's own conventions, add these flags to both preview and apply. To change an existing project's saved Russian language to English, use `--chat-language English` explicitly:

~~~sh
aikit install /path/to/project --chat-language Russian --conventions standard
~~~

A fuller example that also selects team sharing and two clients:

~~~sh
aikit install /path/to/project --mode team --chat-language English --conventions standard --agent codex --agent claude
~~~

To keep the dedicated project builder cache between Docker tasks, add `--docker-cleanup keep-cache`; see [Docker cleanup and host reclamation](DOCKER.md#docker-cleanup-and-host-reclamation).

**Read [OWNER.md](../../template/ai-kit/profiles/OWNER.md) before adopting owner conventions for Laravel**; standard follows established project conventions.

### Presets

| Preset | Mode | What it adds |
| --- | --- | --- |
| minimal | Keep saved mode; fresh default is private | Disable the five preset-managed extras; independently selected optional modules remain selected |
| solo | private | Session-start context, native client settings and scoped module rules |
| team | team | The solo extras plus Git commit/push confirmation |
| strict | Keep saved mode; fresh default is private | Session-start, Git guards, data guards, native settings and scoped rules |

Explicit `--mode` and `--with-*` flags override presets; previews report disabled extras. CI, security-audit, Strix, Context7, Web Design, orchestration, UUID and Claude GitHub stay outside presets. Claude hook/permission wiring requires Claude selection; a preset does not select clients for you. [Flag reference and combinations](INSTALLER_FLAGS.md) · [All extras and client formats](../../template/ai-kit/ADAPTERS.md#optional-install-extras).

## What lands in your project

![What lands in your project](https://i.postimg.cc/vZKjvVYs/06-what-lands-in-your-project.jpg)

| File or directory | Purpose |
| --- | --- |
| AGENTS.md | Starting instructions and links to relevant rules |
| PROJECT_CONTEXT.md | Verified purpose, contracts, stack, module map, commands, and open questions |
| WIKI.md | A short map of useful documentation |
| .agents/skills/ | Stack skills, the continuity procedure, and the ai-kit workflows |
| ai-kit/ | Core rules, settings, project facts, engineering, security, containers, profiles, and routing |
| docs/DECISIONS.md and docs/adr/ | Decisions, reasons, and tradeoffs |
| CHANGELOG.md | What changed and why |

Selected clients add their own entry files and configuration; see [the client table](../../README.md#works-with-your-ai-clients). [Core](../../template/ai-kit/CORE.md) owns language, Git authorization, and fact verification; the [engineering guide](../../template/ai-kit/ENGINEERING.md) owns the work cycle.

## Sharing

| Mode | Shared AI-KIT files in Git | Suitable for |
| --- | --- | --- |
| private | Ignored | Local instructions installed separately |
| team | Visible | Teammates and agents working from fresh clones |

Both modes exclude secrets, personal overrides, installer state, caches, IDE folders, AI client history, and extracted AI-KIT bundles; private mode also keeps AI client configuration folders (`.cursor`, `.codex`, `.gemini`, `.devin`, legacy `.windsurf`, `.roo`, Copilot prompts and agents) out of Git. The installer owns one marked `.gitignore` block; your other rules survive, and lockfiles and manifests stay visible. Composer, Moodle, Node, and Python exclusions are scoped to detected modules, preserving deliberate Go vendoring. See [ignore adaptation](../../template/ai-kit/BOOTSTRAP.md#ignore-adaptation).

The optional `--with-ci` workflow validates the AI-KIT files committed to the repository, so it is meaningful in team mode. In private mode those files stay out of Git and the workflow has nothing to validate.

## Update an application project

![Update an application project](https://i.postimg.cc/qvFYG3Jr/08-update-an-application-project.jpg)

Updating the CLI package and updating a project are separate steps. First update the CLI (`pipx upgrade ai-kit-python`, or `python -m pip install --upgrade ai-kit-python` in its environment), then preview the newer bundle against the same project path:

~~~sh
aikit install /path/to/project
~~~

After reviewing the preview, apply and check that same project:

~~~sh
aikit install /path/to/project --apply --check
~~~

The [README update commands](../../README.md#update-ai-kit) also show the complete pip/pipx and Windows module-based sequence for the current directory.

Unchanged managed files update, while your context and history are preserved. Saved agent, module and sharing selections are reused when omitted; pass selection flags only when intentionally changing them. Locally adapted files become candidates under `ai-kit/.upstream-cache/candidates/` for review, and changed files are backed up first. After merging a candidate, accept it:

~~~sh
aikit install /path/to/project --accept-local AGENTS.md --apply
~~~

Version direction matters. When the CLI is newer than the project, `aikit doctor` names these upgrade commands. When the project records a newer AI-KIT than the CLI (for example a teammate upgraded first), preview warns and `--apply` refuses, so an older CLI cannot replace newer managed files; upgrade the CLI, or pass `--allow-downgrade` only for a deliberate downgrade.

Kit text files use LF line endings in every distribution (Git, PyPI and Docker). Upgrades treat line-ending-only differences, such as CRLF copies produced by a Windows checkout, as unchanged rather than as local edits.

Exit codes: 0 success, 1 refusal, 2 unresolved conflicts. The installer works offline; agents check the configured upstream through [UPSTREAM](../../template/ai-kit/UPSTREAM.md).

### Check project health

Run `aikit doctor /path/to/project` (or `python scripts/doctor.py /path/to/project` from a checkout) anytime for a health report covering managed-file, link, provider and context drift.

`aikit doctor /path/to/project --fix` previews a repair plan that restores missing/baseline files through the installer; nothing is written. `aikit doctor /path/to/project --fix --apply` writes that plan. Local edits are preserved and conflicts still need review. Earlier releases applied `--fix` directly.

### Review MCP servers

`aikit mcp report /path/to/project` lists MCP servers configured in the project's client files: `.mcp.json` (Claude Code), `.cursor/mcp.json`, `.vscode/mcp.json` (VS Code/Copilot), `.gemini/settings.json`, `.codex/config.toml`, `.roo/mcp.json` and `.kimi-code/mcp.json`. For each server it shows the transport, command, URL origin, environment/header variable names, auto-approval and tool settings, and whether the file is tracked in Git. It never prints secret values; it warns about literal credentials, inline OAuth client secrets, plain HTTP to remote hosts and auto-approval. It only reads files: no server is started, contacted or authorized. Windsurf and Cline keep MCP servers in user-level files, which the report does not read. On Python 3.10, Codex TOML lists server names only; review that file manually. Use the report with the installed [MCP posture](../../template/ai-kit/MCP.md).
