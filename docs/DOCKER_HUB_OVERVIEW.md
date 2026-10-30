# AI-KIT

**Give your AI coding agents persistent project context, reusable skills and a consistent engineering workflow.**

AI-KIT installs portable project instructions, stack profiles, client configuration and optional skills into your repository. It helps coding agents understand your project, preserve decisions, follow your conventions and verify their work.

The Docker image packages the installer and CLI helpers with Python, Git, templates and integration resources. You can use AI-KIT without installing Python on your host.

**Current image:** `tigusigalpa/ai-kit:1.4.5`

**New in v1.4.5:** mandatory maximum disposable Docker cleanup without a size threshold, dedicated-builder lifecycle and separate Windows/WSL2 RAM and virtual-disk reclamation guidance. Docker publication is verified. PyPI 1.4.5 follows GitHub validation and separate human approval; the previous verified package is 1.4.4.

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
| **Routing and evaluation helpers** | Model-routing recommendations, context selection, local metrics and benchmark scaffolding. |
| **Optional orchestration** | Native Codex helper configurations and an explicitly invoked OpenRouter text executor with bounded requests, private accounting and review. Native client activation and API credentials are configured separately. |
| **Docker and Kubernetes guidance** | Container security, lifecycle, image freshness and deployment instructions, plus a Kubernetes installation-preview Job example. |

AI-KIT installs instructions and supporting tools. Your coding client performs the development work.

## What changed in v1.4.5

This release strengthens installed Docker housekeeping and includes the Windows installation/troubleshooting guide.

- **No cleanup threshold:** every Docker build, test and debugging task ends with zero eligible disposable resources, including interrupted runs after reports are saved.
- **Complete resource coverage:** temporary containers, disposable anonymous/named volumes, networks, unnecessary test images and all reclaimable dedicated-builder cache.
- **Host reclamation:** separate RAM return, logical Docker usage and physical disk allocation; WSL2 memory-reclaim settings and supported offline disk compaction require the actual backend and a safe maintenance window.
- **Preserved data:** persistent databases, unrelated/active workloads and retained final/recovery images remain protected. Host-wide pruning requires an established owner scope and reviewed inventory.
- **Clear execution boundary:** AI-KIT installs agent instructions. The CLI image does not mount the Docker socket, run a cleanup daemon or compact its host disk.
- **Upgrade preservation:** unchanged managed rules update normally; locally adapted rules and entry points produce reviewable conflicts rather than being overwritten.

Optional orchestration, dialogue memory, Web Design, Context7 and both pinned security integrations remain available.

### Project privacy and existing features

Root AI-KIT maintainer `AGENTS.md`, `PROJECT_CONTEXT.md` and `WIKI.md` are excluded from the build context and Python distributions. Their application template counterparts remain included. Private dialogue memory, journals, design output, credentials and personal client configuration also stay outside the image.

Shared dialogue memory, Web Design, Context7, both security integrations and preservation-aware installation remain available. Existing image versions remain usable.

### Image verification

Verified on 2026-10-30: **395 packaged Linux tests, 393 passed and two Windows-only skips**; three native Windows upgrade regressions; zero kit errors/warnings; source/archive privacy, strict Twine validation and fresh offline Windows wheel installation. Docker smoke passed offline/read-only operation, preview/apply/refusal, all optional modules, preserved files, stable reruns, SIGTERM and actual build-context exclusions. All 205 inspected packaged resources matched source. Anonymous registry manifest/configuration/layer read-back, immutable pull and published CLI/kit checks passed.

The dedicated release builder reclaimed 340 MB, then its container and state volume were removed. Existing unrelated workloads remained running; no host-wide prune, WSL shutdown or physical disk compaction was performed. The image contains instructions for those host operations and does not execute them itself.

## Pull and check the image

Docker must be running with Linux-container support.

```sh
docker pull tigusigalpa/ai-kit:1.4.5
```

Check the CLI version and help:

```sh
docker run --rm --init --network none --read-only tigusigalpa/ai-kit:1.4.5 --version

docker run --rm --init --network none --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  tigusigalpa/ai-kit:1.4.5 --help
```

Arguments after the image name go directly to `aikit`. Running the image without arguments displays CLI help.

The commands below disable runtime networking. Pulling the image still requires registry access.

## Install into a project: Linux or Bash

Choose an existing application directory. Run as an ordinary host user so the forwarded UID/GID is non-root.

```bash
app_path="$(cd /absolute/path/to/my-app && pwd)"
image="tigusigalpa/ai-kit:1.4.5"

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
$image = 'tigusigalpa/ai-kit:1.4.5'

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

Preview sends no request and writes nothing. An explicitly applied OpenRouter task requires outbound HTTPS, an intentionally supplied `OPENROUTER_API_KEY`, a dedicated capped key and a writable project mount for reservations and outputs. The offline examples in this Overview intentionally retain `--network none`; follow the [orchestration guide](https://github.com/tigusigalpa/ai-kit#optional-orchestration) when configuring an authorized live run.

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

Immutable reference to this verified build:

```sh
docker pull tigusigalpa/ai-kit@sha256:01c5ccae6d6b310e4230b6d7482c070c2b7a5b3bbc6c8af5d43180d852874979
```

Registry manifest digest: `sha256:01c5ccae6d6b310e4230b6d7482c070c2b7a5b3bbc6c8af5d43180d852874979`. Existing version tags are retained; this release does not assign `latest`. Descriptive publication receipts can follow the tested image documentation snapshot without replacing its runtime or installed guidance.

## Documentation and license

- [Source repository and README](https://github.com/tigusigalpa/ai-kit)
- [Docker usage](https://github.com/tigusigalpa/ai-kit#run-ai-kit-with-docker)
- [Web Design](https://github.com/tigusigalpa/ai-kit#web-design)
- [Shared dialogue context](https://github.com/tigusigalpa/ai-kit#shared-context-from-two-dialogues)
- [OpenRouter guidance](https://github.com/tigusigalpa/ai-kit#working-with-openrouter)
- [Optional orchestration](https://github.com/tigusigalpa/ai-kit#optional-orchestration)

AI-KIT is licensed under MIT. Bundled Cloudflare references retain MIT licensing; bundled Strix references retain Apache-2.0 licensing.
