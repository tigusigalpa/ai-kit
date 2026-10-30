# AI-KIT

Portable project instructions, verified context and reusable skills for AI coding agents.

AI-KIT installs a shared instruction layer into an application repository. It gives agents a project module map, stack guidance, engineering workflows and explicit authorization rules. The installer previews changes, preserves existing project documents and reports conflicts before applying an upgrade.

The `ai-kit-python` distribution exposes the `aikit` command. Python 3.10 or later is required; the runtime uses only the standard library. Git supports repository evidence and visibility checks. Application toolchains and AI clients are installed separately.

## Install the CLI

For an isolated command-line installation with pipx:

```sh
pipx install ai-kit-python
aikit --version
```

Or install into a Python virtual environment:

```sh
python -m venv .venv
# Activate the environment using your operating system's activation command.
python -m pip install ai-kit-python
aikit --help
```

The package name is `ai-kit-python`; the executable is `aikit`. Never run `pip install aikit`: that is not this project's package name. Installing the CLI does not modify an application project until you run the installer with `--apply`.

## Preview, install and initialize

**Defaults you should know:** chat replies default to Russian, and conventions default to the owner's opinionated Laravel conventions, including no database foreign key constraints. Authored project files are always English. For English replies and your project's own conventions, add both flags to the preview and the apply command:

```sh
aikit install /path/to/my-app --agent codex --mode private --chat-language English --conventions standard
```

Choices are saved in `ai-kit/settings.json` and reused on upgrades. See [defaults and presets](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/INSTALL.md#choose-your-defaults).

Choose an existing application folder, then preview:

```sh
aikit install /path/to/my-app --agent codex --mode private
```

Review the proposed files and any conflicts. Apply the same selection:

```sh
aikit install /path/to/my-app --agent codex --mode private --apply --check
aikit doctor /path/to/my-app
```

On Windows, use a quoted path such as `"C:\Projects\my-app"`. Add `--agent claude` for Claude Code or choose another supported adapter. Private mode keeps new kit configuration local through ignore policies; team mode shares project instructions. Existing tracked files remain tracked until explicitly untracked.

Open the application in your AI client and invoke `$ai-kit-bootstrap` in Codex or `/ai-kit-bootstrap` in Claude Code. Bootstrap verifies installer drafts against the repository and fills project context from evidence. Other clients can use the [bootstrap prompt](https://github.com/tigusigalpa/ai-kit/blob/main/BOOTSTRAP_PROMPT.md).

## Capabilities

- **Project context:** verified facts, module maps, commands, decisions and continuity instructions.
- **Client adapters:** native entry files and configuration for Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, Windsurf, Cline, Roo, Aider, Kimi and Manus. Documentation for Kimi and Manus is unverified, and activation in actual clients is unverified.
- **Stack guidance:** Go, PHP, Laravel, Filament, Moodle, Python, frontend, libraries, Rust, .NET, Java and Terraform/Helm, selected from project evidence.
- **Conservative upgrades:** existing documents, settings and local adaptations are preserved; conflicts remain reviewable.
- **Engineering workflows:** plan, implement, test, review and document, with explicit Git authorization.
- **Routing and measurement:** offline model role/effort recommendations (no savings are claimed), context selection, metrics and benchmark scaffolding. Live execution needs a separately configured worker.
- **Container guidance:** the kit instructs agents to make new Dockerfiles and services Kubernetes-ready, keep images fresh and clean up after every Docker task. The default `maximum` mode removes all eligible disposable resources, including the dedicated builder cache, without a size threshold, and reclaims host RAM/disk; `--docker-cleanup keep-cache` keeps the dedicated project builder cache and reclaims host resources only on request or observed pressure. Persistent data and unrelated workloads remain protected; installation starts no cleanup or compaction process.

## Optional integrations

Enable these modules explicitly in both preview and apply:

| Option | Included guidance |
| --- | --- |
| `--with-web-design` | References and briefs, visual systems, UI implementation and acceptance, including a Blade route. |
| `--with-context7` | Version-aware documentation lookup; MCP setup is separate. |
| `--with-security-audit` | Pinned Cloudflare security-audit resources with an explicit entry point. |
| `--with-strix` | Pinned Strix workflow skills with an explicit entry point. |

```sh
aikit install /path/to/my-app --agent codex --agent claude --with-web-design --with-context7
```

Installation runs no audit, security scan, external tool setup or model call. These modules are independent of installation presets.

## Shared dialogue context

`aikit memory import`, `merge` and `export` work locally with two conversations. Supported inputs include selected ChatGPT JSON branches, messages JSON and UTF-8 text/Markdown transcripts. The workflow preserves source references, prepares human review and records explicit keyed contradictions.

Reviewed exports provide ChatGPT Markdown and an OpenRouter JSON request fragment. Pending claims block normal exports; explicit draft exports retain unresolved material. Free-form semantic disagreements require human review. The CLI does not connect accounts, synchronize chat histories or send API requests.

```sh
aikit memory --help
aikit context --help
aikit route "review an interface"
```

## Updates and distribution privacy

Update the CLI with `pipx upgrade ai-kit-python`, or `python -m pip install --upgrade ai-kit-python` inside its virtual environment. Preview the installer against an existing project before applying an upgrade. Updating the CLI alone does not rewrite installed application instructions.

The distribution excludes root maintainer AGENTS.md, PROJECT_CONTEXT.md and WIKI.md, plus private dialogue/metrics/cache paths. Application template counterparts remain included. Secrets and raw project conversations belong outside distribution sources; review exported data before sharing.

A separate [Docker image](https://hub.docker.com/r/tigusigalpa/ai-kit) packages the CLI for container use.

Package releases follow GitHub Release, automated checks and owner approval before PyPI upload through Trusted Publishing. Future stable tags must match VERSION; manual runs default to validation. See the [release procedure](https://github.com/tigusigalpa/ai-kit/blob/main/docs/PYPI.md#release-to-pypi-with-owner-approval).

## Documentation and license

- [Repository and README](https://github.com/tigusigalpa/ai-kit)
- [Documentation site with a command configurator](https://tigusigalpa.github.io/ai-kit-docs/)
- [All guides](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/README.md)
- [Installation and upgrades](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/INSTALL.md)
- [Installer flags and options](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/INSTALLER_FLAGS.md)
- [Windows guide](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/WINDOWS.md)
- [Web Design](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/WEB_DESIGN.md)
- [Dialogue context](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/DIALOGUE_MEMORY.md)
- [Issues](https://github.com/tigusigalpa/ai-kit/issues)

AI-KIT's own code and instructions are MIT licensed. Bundled Cloudflare references retain MIT; bundled Strix references retain Apache-2.0. The complete distribution declares `MIT AND Apache-2.0` and includes the corresponding license texts. External runtimes and application dependencies keep their own licenses.

## Optional orchestration (v1.4.4)

Install with `--with-orchestration` to add scoped Codex helpers and disabled-by-default OpenRouter configuration. `aikit orchestrate` previews selected text tasks, executes only on explicit apply, enforces local admission and capped-key preflight, and retains private observed usage/cost, review and billing reconciliation. It never executes model output. Native helper billing is separate; real trials and savings are unverified. See the [complete guide](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/ORCHESTRATION.md).
