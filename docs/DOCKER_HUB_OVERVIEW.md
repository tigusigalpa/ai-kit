# AI-KIT

**Give your AI coding agents persistent project context, reusable skills and a consistent engineering workflow.**

AI-KIT installs portable project instructions, stack profiles, client configuration and optional skills into your repository. It helps coding agents understand your project, preserve decisions, follow your conventions and verify their work.

The Docker image packages the installer and CLI helpers with Python, Git, templates and integration resources. You can use AI-KIT without installing Python on your host.

**Current image:** `tigusigalpa/ai-kit:1.5.0`

**New in v1.5.0:** `aikit mcp report` reviews project MCP servers without printing secret values, the installer refuses accidental downgrades, and `doctor` names the upgrade commands. The image also brings 1.4.6 and 1.4.7 to Docker Hub: identical LF bytes across distributions, a selectable Docker cleanup policy, SIGTERM handling as PID 1 and the machine-readable `aikit flags` schema. PyPI [1.4.6](https://pypi.org/project/ai-kit-python/1.4.6/) and [1.4.7](https://pypi.org/project/ai-kit-python/1.4.7/) are published; PyPI 1.5.0 follows the owner's approval.

**Published platform:** `linux/amd64`

**Source:** [github.com/tigusigalpa/ai-kit](https://github.com/tigusigalpa/ai-kit)

## What AI-KIT provides

| Capability | Description |
| --- | --- |
| **Persistent project context** | Project facts, module maps, commands, decisions and continuity instructions that agents can reuse across chats. |
| **Configuration for 11 AI clients** | Native entry files and configuration for Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, Windsurf, Cline, Roo, Aider, Kimi and Manus. Documentation for Kimi and Manus is unverified, and activation in actual clients is unverified. |
| **Stack-specific guidance** | Profiles for Go, PHP, Laravel, Filament, Moodle, Python, frontend, libraries, Rust, .NET, Java and Terraform/Helm. |
| **Preview-first installation** | Review proposed changes before writing. Existing project documents and local modifications follow preservation and conflict rules; an older CLI refuses to downgrade a newer installation unless explicitly allowed. |
| **Engineering workflows** | Plan, implement, test, review and document, supported by bootstrap, review and context synchronization skills. |
| **Optional Web Design** | Reference analysis, project briefs, visual systems, stack-aware implementation guidance and UI acceptance criteria, including a Laravel Blade route. |
| **Optional security workflows** | Pinned Cloudflare security-audit references and Strix workflow skills, installed explicitly and invoked on request. |
| **Optional Context7 guidance** | Version-aware documentation lookup workflows, with client connection setup handled separately. |
| **MCP server review** | `aikit mcp report` lists MCP servers from seven clients' project files with transport, URL origin, variable names and approval settings. It hides secret values, warns about literal credentials, plain remote HTTP and auto-approval, and starts or contacts no server. |
| **Shared dialogue context** | Local conversation imports, source references, contradiction review and exports for ChatGPT and OpenRouter. |
| **Routing and evaluation helpers** | Model role and reasoning-effort recommendations (no savings are claimed), context selection, local metrics and benchmark scaffolding. |
| **Optional orchestration** | Native Codex helper configurations and an explicitly invoked OpenRouter text executor with bounded requests, private accounting and review. Native client activation and API credentials are configured separately. |
| **Docker and Kubernetes guidance** | Instructions that tell agents to make new Dockerfiles and services Kubernetes-ready (security, lifecycle, image freshness, deployment), plus a Kubernetes installation-preview Job example. Cleanup after Docker tasks is `maximum` by default or `keep-cache` to keep the dedicated builder cache. |

AI-KIT installs instructions and supporting tools. Your coding client performs the development work.

## What changed since v1.4.5

This image combines releases 1.4.6, 1.4.7 and 1.5.0; 1.4.5 was the previous Docker Hub image.

**v1.5.0**

- **MCP review:** `aikit mcp report /workspace` lists servers from Claude Code, Cursor, VS Code/Copilot, Gemini CLI, Codex, Roo and Kimi Code project files: transport, command, URL origin, variable names, approval and tool settings, Git tracking. Environment and header values appear only as variable references; URL queries and secret-like arguments are hidden. Literal credentials, inline OAuth client secrets, credentials in URLs, plain remote HTTP and auto-approval produce warnings. No server is started or contacted.
- **Downgrade guard:** when a project records a newer AI-KIT than the image, preview warns and `--apply` (also `doctor --fix --apply`) refuses unless `--allow-downgrade` is passed.
- **Upgrade hints:** `doctor` names the preview and apply commands when a newer AI-KIT is available for the project.

**v1.4.7**

- **Flag schema:** `aikit flags` prints every installer option as JSON (value type, choices, exclusions, saved setting, fresh default, help, presets). Kit validation fails when the schema, flag guide or SKILL.md drifts from the installer.
- **Gemini routing:** documented per-model `thinking_level` values replace the "effort unknown" fallback.

**v1.4.6**

- **Identical bytes:** kit text is LF in Git, the wheel and the image; upgrades treat line-ending-only differences as unchanged.
- **Docker cleanup choice:** `--docker-cleanup maximum|keep-cache`, saved as `docker_cleanup`. `maximum` (default) keeps the v1.4.5 policy; `keep-cache` keeps the dedicated project builder cache and reclaims host RAM/disk only on request or pressure.
- **Safer runs:** the CLI handles SIGTERM as PID 1, so `--init` is optional; doctor previews repairs with `--fix` and writes them with `--fix --apply`; the `--with-ci` workflow validates committed files with pinned actions and installs nothing.
- **Robust installs:** linked manifests and unusual module names no longer block fresh installs; secondary stacks fill missing commands instead of replacing them; `--with-security-audit` no longer installs upstream test files.

Optional orchestration, dialogue memory, Web Design, Context7, both pinned security integrations and preservation-aware installation remain available. Existing image versions remain usable.

The image contains no private dialogue memory, journals, design output, credentials or personal client configuration.

## Image verification

Verified on 2026-10-30 from a clean source export: **443 packaged Linux tests passed with three expected skips** (non-root, offline, read-only root) and 443 native Windows tests; zero kit errors/warnings; wheel/sdist metadata, resource, privacy and license checks, strict Twine and an offline fresh-venv wheel installation. Docker smoke passed offline/read-only operation, preview/apply/refusal, all optional modules, preserved files, stable reruns, `aikit mcp report` on a read-only root and SIGTERM with and without `--init`. All 312 packaged files in the wheel and the image are byte-identical.

The dedicated builder and its 341.9 MB cache were removed after verification. No host-wide prune, WSL shutdown or physical disk compaction was performed. The image contains instructions for those host operations and does not execute them itself.

## Pull and check the image

Docker must be running with Linux-container support.

```sh
docker pull tigusigalpa/ai-kit:1.5.0
```

Check the CLI version and help:

```sh
docker run --rm --init --network none --read-only tigusigalpa/ai-kit:1.5.0 --version

docker run --rm --init --network none --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  tigusigalpa/ai-kit:1.5.0 --help
```

Arguments after the image name go directly to `aikit`. Running the image without arguments displays CLI help.

The commands below disable runtime networking. Pulling the image still requires registry access.

## Install into a project: Linux or Bash

Choose an existing application directory. Run as an ordinary host user so the forwarded UID/GID is non-root.

```bash
app_path="$(cd /absolute/path/to/my-app && pwd)"
image="tigusigalpa/ai-kit:1.5.0"

runtime=(
  --rm --init
  --network none
  --read-only
  --cap-drop ALL
  --security-opt no-new-privileges
  --tmpfs /tmp:rw,nosuid,nodev,size=256m
  --user "$(id -u):$(id -g)"
)
```

**Defaults you should know:** chat replies default to Russian, and conventions default to the owner's opinionated Laravel conventions, including no database foreign key constraints. Authored project files are always English. For English replies and your project's own conventions, add `--chat-language English --conventions standard` after `install /workspace` in both the preview and the apply command. Docker cleanup defaults to `maximum`; `--docker-cleanup keep-cache` keeps the dedicated project builder cache. For example:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" install /workspace --agent codex --chat-language English --conventions standard
```

Choices are saved in `ai-kit/settings.json` and reused on upgrades. [Defaults and presets](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/INSTALL.md#choose-your-defaults).

Preview the installation with a read-only project mount:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" install /workspace --agent codex
```

After reviewing the preview, apply using a writable project mount:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace" \
  "$image" install /workspace --agent codex --apply --check
```

Check the installed project later:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" doctor /workspace
```

`doctor /workspace --fix` previews repairs; with a writable mount, `--fix --apply` writes them.

Files written into `/workspace` persist in the mounted host directory after the container exits.

## Install into a project: Windows PowerShell

Use an existing application folder accessible to Docker Desktop.

```powershell
$appPath = (Resolve-Path -LiteralPath 'C:\Projects\my-app').Path
$image = 'tigusigalpa/ai-kit:1.5.0'

$runtime = @(
    '--rm', '--init',
    '--network', 'none',
    '--read-only',
    '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges',
    '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m'
)
```

Preview:

```powershell
docker run @runtime `
  --mount "type=bind,source=$appPath,target=/workspace,readonly" `
  $image install /workspace --agent codex
```

Apply after reviewing the preview:

```powershell
docker run @runtime `
  --mount "type=bind,source=$appPath,target=/workspace" `
  $image install /workspace --agent codex --apply --check
```

Check the installed project:

```powershell
docker run @runtime `
  --mount "type=bind,source=$appPath,target=/workspace,readonly" `
  $image doctor /workspace
```

The image uses UID/GID `10001:10001` by default. Docker Desktop file sharing must permit access to the mounted folder. To change the defaults (Russian chat replies, the owner's opinionated Laravel conventions), add `--chat-language English --conventions standard` to both commands.

## Enable optional modules

Optional modules are selected explicitly and remain independent of installation presets.

| Installer option | Installs |
| --- | --- |
| `--with-web-design` | Design skills, conditional guides and project design documents. |
| `--with-context7` | Context7 documentation lookup guidance and skill entry points. |
| `--with-security-audit` | Pinned Cloudflare security-audit resources and an explicit entry point. |
| `--with-strix` | Pinned Strix workflow references and an explicit entry point. |
| `--with-orchestration` | Codex helper configurations, an orchestration guide and preserved configuration for bounded OpenRouter text tasks. |

For example, in the Bash session above, preview a Codex and Claude Code installation with all five modules:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" install /workspace \
  --agent codex --agent claude \
  --with-web-design \
  --with-context7 \
  --with-security-audit \
  --with-strix \
  --with-orchestration
```

To apply that selection, use a writable project mount and append `--apply --check`, keeping the same agent and module options.

Installing these modules does not start a security scan, connect an MCP server or invoke a model. External tools and client activation are configured separately.

## Optional orchestration

The module adds `aikit orchestrate run`, `status`, `review` and `reconcile`. Its configuration starts disabled; explicitly choose the model, input files and limits before use.

Explore the commands offline using the Bash runtime options above:

```bash
docker run "${runtime[@]}" "$image" orchestrate --help
```

Preview sends no request and writes nothing. An explicitly applied OpenRouter task requires outbound HTTPS, an intentionally supplied `OPENROUTER_API_KEY`, a dedicated capped key and a writable project mount for reservations and outputs. The offline examples in this Overview intentionally retain `--network none`; follow the [orchestration guide](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/ORCHESTRATION.md) when configuring an authorized live run.

There are no automatic inference retries, model fallbacks or executable tool responses. Billing uncertainty or reserve overruns stop further requests until resolved. API costs are recorded separately from native Codex usage; end-to-end savings require real measurements. Installing helper configurations does not launch a Codex client or delegate work automatically.

## Shared context from conversations

AI-KIT can import two local dialogues and prepare a shared reference state.

Supported inputs include:

- ChatGPT-style conversation JSON with explicit conversation or branch selection when needed.
- OpenRouter-style `messages` JSON.
- UTF-8 text or Markdown transcripts from other clients.

The workflow is:

1. Import each conversation into a private workspace.
2. Merge the imports and generate a review worksheet.
3. Review claims and resolve explicit contradictions.
4. Export ChatGPT Markdown and/or an OpenRouter JSON request fragment.

Explore the commands without mounting any project:

```bash
docker run "${runtime[@]}" "$image" memory --help
docker run "${runtime[@]}" "$image" memory import --help
docker run "${runtime[@]}" "$image" memory merge --help
docker run "${runtime[@]}" "$image" memory export --help
```

Imports, merges and exports preview by default; `--apply` writes local artifacts. Use a writable mount for the workspace and readable mounts for source transcripts.

Normal exports require review. Explicit draft exports can retain pending claims and unresolved alternatives. Free-form semantic disagreements require human review.

ChatGPT output is reference Markdown for manual use. OpenRouter output contains a reference message for your own client to include in a request. This workflow does not synchronize accounts, upload conversations or execute API calls.

See the [shared dialogue context guide](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/DIALOGUE_MEMORY.md).

## Other useful commands

Using the Bash runtime options defined above:

```bash
# Show CLI help.
docker run "${runtime[@]}" "$image" --help

# Validate the bundled AI-KIT distribution.
docker run "${runtime[@]}" "$image" check

# Inspect a routing recommendation.
docker run "${runtime[@]}" "$image" route "review an interface"

# Show provider records.
docker run "${runtime[@]}" "$image" providers

# Print every installer option as JSON.
docker run "${runtime[@]}" "$image" flags
```

`check` validates the bundled distribution. `doctor /workspace` examines an installed application project.

For a project with Web Design enabled:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" context select /workspace --workflow web-design
```

Context selection reports the relevant files and their scope. It does not send them to a model.

Review the project's MCP servers without starting them:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" mcp report /workspace
```

The JSON report hides secret values and lists warnings. User-level client files outside the project are not read.

## Runtime contract

| Setting | Value |
| --- | --- |
| Entrypoint | `aikit` |
| Default command | `--help` |
| Published platform | `linux/amd64` |
| Default user | UID/GID `10001:10001` |
| Working directory | `/workspace` |
| Temporary writable storage | `/tmp`, supplied by the caller |
| Exposed ports | None |
| Shutdown signal | SIGTERM, handled as PID 1 (`--init` optional) |

The image is a CLI workload. Each invocation runs a command and exits.

Python, Git and AI-KIT resources are bundled. Application toolchains, browsers, Node.js, Composer, model runtimes, MCP connections and the Strix executable are separate.

The examples use a read-only container root and explicit project mounts. Preview commands can use read-only mounts; installation and other explicit writes require writable mounts.

## Updates and reproducible references

To update a project, pull the selected image version, preview installation against the same project folder and review any conflicts before applying. `doctor /workspace` names the commands when the image is newer than the installation. An older image refuses to apply over a newer installation unless you pass `--allow-downgrade` deliberately.

Existing project documents, settings, private dialogue memory and local edits retain the normal preservation rules.

The registry digest of `1.5.0` is recorded here after publication and read-back. The previous verified image remains available by its immutable reference:

```sh
docker pull tigusigalpa/ai-kit@sha256:01c5ccae6d6b310e4230b6d7482c070c2b7a5b3bbc6c8af5d43180d852874979
```

Registry manifest digest of `1.4.5`: `sha256:01c5ccae6d6b310e4230b6d7482c070c2b7a5b3bbc6c8af5d43180d852874979`. Existing version tags are retained; this release does not assign `latest`.

## Documentation and license

- [Source repository and README](https://github.com/tigusigalpa/ai-kit)
- [Documentation site with a command configurator](https://tigusigalpa.github.io/ai-kit-docs/)
- [All guides](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/README.md)
- [Docker usage](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/DOCKER.md)
- [Installer flags and options](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/INSTALLER_FLAGS.md)
- [MCP server review](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/INSTALL.md#review-mcp-servers)
- [Web Design](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/WEB_DESIGN.md)
- [Shared dialogue context](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/DIALOGUE_MEMORY.md)
- [OpenRouter guidance](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/OPENROUTER.md)
- [Optional orchestration](https://github.com/tigusigalpa/ai-kit/blob/main/docs/guide/ORCHESTRATION.md)

AI-KIT is licensed under MIT. Bundled Cloudflare references retain MIT licensing; bundled Strix references retain Apache-2.0 licensing.
