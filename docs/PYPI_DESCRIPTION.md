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

The package name is `ai-kit-python`; the executable is `aikit`. Installing the CLI does not modify an application project until you run the installer with `--apply`.

## Preview, install and initialize

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
- **Client adapters:** Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, Windsurf, Cline, Roo, Aider, Kimi and Manus. Actual discovery and activation depend on the client.
- **Stack guidance:** Go, PHP, Laravel, Filament, Moodle, Python, frontend, libraries, Rust, .NET, Java and Terraform/Helm, selected from project evidence.
- **Conservative upgrades:** existing documents, settings and local adaptations are preserved; conflicts remain reviewable.
- **Engineering workflows:** plan, implement, test, review and document, with explicit Git authorization.
- **Routing and measurement:** offline recommendations, context selection, metrics and benchmark scaffolding. Live execution needs a separately configured worker.
- **Container guidance:** non-root execution, lifecycle, image freshness, mounts and Kubernetes readiness appropriate to the workload.

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

- [Repository and full README](https://github.com/tigusigalpa/ai-kit)
- [Installation and upgrades](https://github.com/tigusigalpa/ai-kit#install)
- [Web Design](https://github.com/tigusigalpa/ai-kit#web-design)
- [Dialogue context](https://github.com/tigusigalpa/ai-kit#shared-context-from-two-dialogues)
- [Issues](https://github.com/tigusigalpa/ai-kit/issues)

AI-KIT's own code and instructions are MIT licensed. Bundled Cloudflare references retain MIT; bundled Strix references retain Apache-2.0. The complete distribution declares `MIT AND Apache-2.0` and includes the corresponding license texts. External runtimes and application dependencies keep their own licenses.
