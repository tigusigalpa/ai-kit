# AI-KIT

**Give your AI coding agents persistent project context, reusable skills and a consistent engineering workflow.**

AI-KIT installs portable project instructions, stack profiles, client configuration and optional skills into your repository. It helps coding agents understand your project, preserve decisions, follow your conventions and verify their work.

The Docker image packages the installer and CLI helpers with Python, Git, templates and integration resources. You can use AI-KIT without installing Python on your host.

**Release image:** `tigusigalpa/ai-kit:1.6.0`

**New in v1.6.0:** English chat defaults with saved-language preservation, current Devin (Windsurf) rules, a JavaScript/Node.js profile, optional public UUIDs and human Claude GitHub identity, plus detailed TypeUI setup for Codex and Claude. [Release and publication status](https://github.com/tigusigalpa/ai-kit/blob/main/docs/V1_6_0.md).

**Published platform:** `linux/amd64`

**Source:** [github.com/tigusigalpa/ai-kit](https://github.com/tigusigalpa/ai-kit)

## What AI-KIT provides

| Capability | Description |
| --- | --- |
| **Persistent project context** | Project facts, module maps, commands, decisions and continuity instructions that agents can reuse across chats. |
| **Configuration for 11 AI clients** | Native entry files and configuration for Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, Devin (Windsurf), Cline, Roo, Aider, Kimi and Manus. Documentation for Kimi and Manus is unverified, and activation in actual clients is unverified. |
| **Stack-specific guidance** | Profiles for Go, PHP, Laravel, Filament, Moodle, Python, JavaScript/TypeScript/Node.js, frontend, libraries, Rust, .NET, Java and Terraform/Helm. |
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

## What changed in v1.6.0

- **English defaults:** new-project and interactive chat defaults to English; saved languages remain on upgrades. Use `--chat-language Russian` or `--chat-language English` explicitly to change an existing choice.
- **Devin (Windsurf):** `--agent devin` installs `.devin/rules/`; the legacy `windsurf` adapter remains available. Preserve custom legacy rules and retire unchanged owned files explicitly.
- **JavaScript / Node.js:** a dedicated profile covers services, CLIs, workers, TypeScript and packages. Browser/frontend suggestions require dependency evidence.
- **Optional public UUIDs:** `--with-uuid` enables guidance across confirmed languages/technologies, independently of owner/standard conventions and presets. Installation changes no application schema or code.
- **Human Claude authorship:** default Claude entries preserve the human Git identity and suppress added Claude commit credit. `--with-claude-github` adds authenticated human GitHub account verification before authorized commits. Conflicting native settings require review; installation performs no login, Git config, commit or push.
- **Clear setup/update instructions:** the README includes TypeUI MCP setup for Codex and Claude Code, troubleshooting, and exact package/project update commands.

AI-KIT still includes the read-only MCP report, downgrade protection, shared dialogue context, security/design modules and bounded optional orchestration from earlier releases. Old image tags remain intact and no `latest` tag is assigned.

## Image verification

The implementation passed 458 native Windows tests (14 environment/platform skips) and 458 packaged Linux tests (three platform/distribution skips) before release labeling. Isolated wheel/sdist metadata/privacy checks, strict Twine, fresh offline wheel installation and Docker smoke passed; 318 packaged files matched the reviewed source, wheel and development image. The versioned release is rebuilt from its committed source; exact final checks and registry identity are recorded in [v1.6.0](https://github.com/tigusigalpa/ai-kit/blob/main/docs/V1_6_0.md).

Publication status is verified separately from local preparation. Live TypeUI/Claude activation and real model/scanner calls are not established by these offline tests. Task builders/cache are removed after verification; unrelated workloads and data stay protected. Host RAM/virtual-disk compaction is not inferred from Docker cache cleanup.

## Pull and check the image

Docker must be running with Linux-container support.

```sh
docker pull tigusigalpa/ai-kit:1.6.0
```

Check the CLI version and help:

```sh
docker run --rm --init --network none --read-only tigusigalpa/ai-kit:1.6.0 --version

docker run --rm --init --network none --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  tigusigalpa/ai-kit:1.6.0 --help
```

Arguments after the image name go directly to `aikit`. Running the image without arguments displays CLI help.

The commands below disable runtime networking. Pulling the image still requires registry access.

## Install into a project: Linux or Bash

Choose an existing application directory. Run as an ordinary host user so the forwarded UID/GID is non-root.

```bash
app_path="$(cd /absolute/path/to/my-app && pwd)"
image="tigusigalpa/ai-kit:1.6.0"

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

**Defaults:** new projects use English chat and files; saved project languages survive upgrades. Owner Laravel conventions remain the default; UUID guidance now requires `--with-uuid` independently. For Russian replies and standard conventions, add `--chat-language Russian --conventions standard` after `install /workspace`. Docker cleanup defaults to `maximum`; `--docker-cleanup keep-cache` preserves the dedicated builder cache. For example:

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
$image = 'tigusigalpa/ai-kit:1.6.0'

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

The image uses UID/GID `10001:10001` by default. Docker Desktop file sharing must permit access to the mounted folder. To select Russian replies and standard conventions, add `--chat-language Russian --conventions standard` to both commands; existing projects retain saved choices.

## Enable optional modules

Optional modules are selected explicitly and remain independent of installation presets.

| Installer option | Installs |
| --- | --- |
| `--with-uuid` | Optional public UUID policy for any confirmed stack; no automatic code/schema changes. |
| `--with-claude-github` | Authenticated human GitHub identity guidance for selected Claude, without installation-time login or Git changes. |
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

Immutable reference to this verified build:

```sh
docker pull tigusigalpa/ai-kit@sha256:a224498c211db3e9e7c416dc91b3a1eacc85d675b71ab0c87c1faead4342a11b
```

Registry manifest digest: `sha256:a224498c211db3e9e7c416dc91b3a1eacc85d675b71ab0c87c1faead4342a11b`. The previous image `1.4.5` keeps `sha256:01c5ccae6d6b310e4230b6d7482c070c2b7a5b3bbc6c8af5d43180d852874979`. Existing version tags are retained; this release does not assign `latest`.

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
