# AI-KIT

**Give your AI coding agents persistent project context, reusable skills and a consistent engineering workflow.**

AI-KIT installs portable project instructions, stack profiles, client configuration and optional skills into your repository. It helps coding agents understand your project, preserve decisions, follow your conventions and verify their work.

The Docker image packages the installer and CLI helpers with Python, Git, templates and integration resources. You can use AI-KIT without installing Python on your host.

**Current image:** `tigusigalpa/ai-kit:1.4.1`

**Published platform:** `linux/amd64`

**Source:** [github.com/tigusigalpa/ai-kit](https://github.com/tigusigalpa/ai-kit)

## What AI-KIT provides

| Capability | Description |
| --- | --- |
| **Persistent project context** | Project facts, module maps, commands, decisions and continuity instructions that agents can reuse across chats. |
| **Configuration for 11 AI clients** | Adapters for Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, Windsurf, Cline, Roo, Aider, Kimi and Manus. Discovery and activation depend on the selected client. |
| **Stack-specific guidance** | Profiles for Go, PHP, Laravel, Filament, Moodle, Python, frontend, libraries, Rust, .NET, Java and Terraform/Helm. |
| **Preview-first installation** | Review proposed changes before writing. Existing project documents and local modifications follow preservation and conflict rules. |
| **Engineering workflows** | Plan, implement, test, review and document, supported by bootstrap, review and context synchronization skills. |
| **Optional Web Design** | Reference analysis, project briefs, visual systems, stack-aware implementation guidance and UI acceptance criteria, including a Laravel Blade route. |
| **Optional security workflows** | Pinned Cloudflare security-audit references and Strix workflow skills, installed explicitly and invoked on request. |
| **Optional Context7 guidance** | Version-aware documentation lookup workflows, with client connection setup handled separately. |
| **Shared dialogue context** | Local conversation imports, source references, contradiction review and exports for ChatGPT and OpenRouter. |
| **Routing and evaluation helpers** | Model-routing recommendations, context selection, local metrics and benchmark scaffolding. Actual model execution requires a separately configured runtime. |
| **Docker and Kubernetes guidance** | Container security, lifecycle, image freshness and deployment instructions, plus a Kubernetes installation-preview Job example. |

AI-KIT installs instructions and supporting tools. Your coding client performs the development work.

## What changed in v1.4.1

### Docker image freshness

Installed project instructions now ask agents to assess Docker impact whenever the project has images.

When changes affect an image, the workflow calls for updating build inputs where needed, rebuilding the image and checking its actual behavior. This covers packaged code, instructions, templates, defaults and dependencies.

These are maintenance instructions; rebuilding and publishing still happen through the project's tools and authorization rules.

### Local maintainer files excluded

The following root AI-KIT maintainer documents are excluded from the Docker build context and Python distributions:

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `WIKI.md`

Their **application template counterparts remain included** and can still be installed into your projects.

Public maintenance documentation now starts at `CONTRIBUTING.md`. Validation supports clean distributions without the optional local maintainer documents.

### Packaging and upgrade verification

The release includes regression coverage for package exclusions, template preservation and public links.

Verification included:

- 339 packaged Linux tests: **337 passed, two Windows-specific skips**.
- Nine Windows CLI tests.
- Actual Docker smoke tests, including offline execution, read-only behavior, installation, preservation, stable reruns and SIGTERM.
- Offline wheel installation into a clean environment.
- Upgrade fixtures from 1.4.0 in private and team modes.

## Pull and check the image

Docker must be running with Linux-container support.

```sh
docker pull tigusigalpa/ai-kit:1.4.1
```

Check the CLI help:

```sh
docker run --rm --init --network none --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  tigusigalpa/ai-kit:1.4.1 --help
```

Arguments after the image name go directly to `aikit`. Running the image without arguments displays CLI help.

The commands below disable runtime networking. Pulling the image still requires registry access.

## Install into a project: Linux or Bash

Choose an existing application directory. Run as an ordinary host user so the forwarded UID/GID is non-root.

```bash
app_path="$(cd /absolute/path/to/my-app && pwd)"
image="tigusigalpa/ai-kit:1.4.1"

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

Files written into `/workspace` persist in the mounted host directory after the container exits.

## Install into a project: Windows PowerShell

Use an existing application folder accessible to Docker Desktop.

```powershell
$appPath = (Resolve-Path -LiteralPath 'C:\Projects\my-app').Path
$image = 'tigusigalpa/ai-kit:1.4.1'

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

The image uses UID/GID `10001:10001` by default. Docker Desktop file sharing must permit access to the mounted folder.

## Enable optional modules

Optional modules are selected explicitly and remain independent of installation presets.

| Installer option | Installs |
| --- | --- |
| `--with-web-design` | Design skills, conditional guides and project design documents. |
| `--with-context7` | Context7 documentation lookup guidance and skill entry points. |
| `--with-security-audit` | Pinned Cloudflare security-audit resources and an explicit entry point. |
| `--with-strix` | Pinned Strix workflow references and an explicit entry point. |

For example, in the Bash session above, preview a Codex and Claude Code installation with all four modules:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" install /workspace \
  --agent codex --agent claude \
  --with-web-design \
  --with-context7 \
  --with-security-audit \
  --with-strix
```

To apply that selection, use a writable project mount and append `--apply --check`, keeping the same agent and module options.

Installing these modules does not start a security scan, connect an MCP server or invoke a model. External tools and client activation are configured separately.

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

See the [shared dialogue context guide](https://github.com/tigusigalpa/ai-kit#shared-context-from-two-dialogues).

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
```

`check` validates the bundled distribution. `doctor /workspace` examines an installed application project.

For a project with Web Design enabled:

```bash
docker run "${runtime[@]}" \
  --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" context select /workspace --workflow web-design
```

Context selection reports the relevant files and their scope. It does not send them to a model.

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
| Shutdown signal | SIGTERM |

The image is a CLI workload. Each invocation runs a command and exits.

Python, Git and AI-KIT resources are bundled. Application toolchains, browsers, Node.js, Composer, model runtimes, MCP connections and the Strix executable are separate.

The examples use a read-only container root and explicit project mounts. Preview commands can use read-only mounts; installation and other explicit writes require writable mounts.

## Updates and reproducible references

To update a project, pull the selected image version, preview installation against the same project folder and review any conflicts before applying.

Existing project documents, settings, private dialogue memory and local edits retain the normal preservation rules.

For an immutable reference to this published build:

```sh
docker pull tigusigalpa/ai-kit@sha256:d11fc24026f13ad90d3ef7a39a235fa40db29ff022999cff3585e7e707978370
```

Use the explicit version tag or digest. This release did not assign a `latest` tag.

## Documentation and license

- [Source repository and README](https://github.com/tigusigalpa/ai-kit)
- [Docker usage](https://github.com/tigusigalpa/ai-kit#run-ai-kit-with-docker)
- [Web Design](https://github.com/tigusigalpa/ai-kit#web-design)
- [Shared dialogue context](https://github.com/tigusigalpa/ai-kit#shared-context-from-two-dialogues)
- [OpenRouter guidance](https://github.com/tigusigalpa/ai-kit#working-with-openrouter)

AI-KIT is licensed under MIT. Bundled Cloudflare references retain MIT licensing; bundled Strix references retain Apache-2.0 licensing.
