# Installer flags and options

Use this reference for **`aikit install TARGET [OPTIONS]`**. `TARGET` is your application folder: `.` means the current working directory. Run it from your application, or supply an absolute path; installing an application kit inside the AI-KIT reference checkout is refused.

The same options work with `python -m aikit.aikit_cli install` after package installation, or `python scripts/install.py` from a source checkout. In Docker, put installer options **after the image name and `install /workspace`**. These are subcommand options, not global settings for every AI-KIT command.

**How to read the tables:** a **switch** takes no value: write `--apply`, not `--apply true`. An option with a value uses a space, for example `--mode private`. Defaults below describe a fresh non-interactive installation with no preset; on upgrades, saved choices are reused unless explicitly changed.

For a first installation walkthrough, defaults and updates, see [Install AI-KIT and set up a project](INSTALL.md).

**Machine-readable reference.** `aikit flags` prints these options as JSON: value type, choices, repeatability, exclusions, the saved setting, the fresh default, help text and presets. The repository copy is [installer-flags.json](../../integrations/installer-flags.json); kit validation fails when that file, this guide or [SKILL.md](../../SKILL.md) drifts from the installer, so tools such as the [documentation site](https://tigusigalpa.github.io/ai-kit-docs/) can build their option lists from it.

## Main installation options

| Argument or flag | Accepted value | What it does | Default or upgrade behavior |
| --- | --- | --- | --- |
| `TARGET` | Required directory path, e.g. `.` or `"C:\Projects\my-app"` | Chooses the application to initialize or update. An absent target directory can be created during apply. Quote paths containing spaces. | Required on every invocation; never inferred from the last installation. |
| `--apply` | Switch | Writes the installation/update plan: managed instructions, selected adapters, settings and ignore block. Existing project documents and conflict rules still apply. | Omitted: preview only, with no files written. |
| `--dry-run` | Switch | Explicitly requests the same read-only preview used by default. | Optional; cannot be combined with `--apply`. |
| `--check` | Switch | Runs the installed-project doctor **after a successful `--apply`** and reports installation health. | Omitted: no post-install doctor. **Without `--apply`, this flag still produces only a preview.** |
| `--interactive` | Switch | Asks about preset, sharing, chat language, conventions, agents and extras, then asks whether to proceed. | Omitted: use CLI/saved/default choices. The wizard has its own offered defaults: review answers on upgrades. Proceeding still needs `--apply` to write files. |
| `--mode` | `private` or `team` | Sets Git visibility of installed AI-KIT instructions/configuration. See the values below. | Fresh: `private`; upgrade: saved mode. A preset may set it; explicit `--mode` wins. |
| `--agent` | One client name from the list below; repeat the flag for multiple clients | Selects which client adapters to install. Example: `--agent codex --agent claude`. | Fresh: `codex`; upgrade: saved selection. An explicit list is the complete requested selection, not an addition to saved agents; removing a selected adapter may require retirement/reconciliation. |
| `--chat-language` | Non-empty language name, up to 60 characters without control characters, e.g. `Russian` or `English` | Sets the language for the agent's chat replies and explanations. Authored project files remain English. | Fresh: `Russian`; upgrade: saved language. |
| `--conventions` | `owner` or `standard` | Selects stack-specific coding preferences. This does not replace Core authorization/security rules. See the values below. | Fresh: `owner`; upgrade: saved conventions. |
| `--docker-cleanup` | `maximum` or `keep-cache` | Selects how agents clean up after Docker tasks in this project. See the values below. | Fresh: `maximum` (an absent `docker_cleanup` setting means `maximum`). An explicit value is saved as `docker_cleanup` in `ai-kit/settings.json` and reused on upgrades. Added after 1.4.5. |
| `--preset` | `minimal`, `solo`, `team` or `strict` | Applies a bundle of sharing/extra choices. It can turn previously enabled preset-managed extras off. [Exact preset contents](INSTALL.md#presets). | Omitted: no preset is reapplied; saved selections remain. Explicit `--mode` and `--with-*` selections override the preset. |
| `--accept-local` | Existing selected managed path relative to `TARGET`, e.g. `AGENTS.md`; repeat for more paths | Acknowledges the current local file as an **explicitly reviewed semantic merge** for this source revision. On apply, records that acceptance without replacing its contents. | Omitted: normal conflict handling. Review/merge the incoming candidate first; this is not a force-overwrite option. Project-owned files and `ai-kit/settings.json` cannot be accepted through it. |
| `--allow-downgrade` | Switch | Applies even when the project records a newer AI-KIT version than this installer. Without it, preview warns and `--apply` (also `doctor --fix --apply`) refuses, so an older CLI cannot silently replace newer managed files. | Omitted: downgrades are refused; upgrade the CLI instead. Not saved. |
| `-h`, `--help` | Switch | Prints the options for `install` and exits without installing. | Use `aikit install --help`; use `aikit --help` for the command list. |

**Valid `--agent` names:** `aider`, `claude`, `cline`, `codex`, `copilot`, `cursor`, `gemini`, `kimi`, `manus`, `roo`, `windsurf`. CLI names are lowercase. Pass multiple clients as repeated flags, not `--agent codex,claude`. Client discovery/activation and the tools used by optional modules remain separate from copying their configuration.

## Sharing, convention and Docker cleanup values

| Selection | Meaning | Practical consequence |
| --- | --- | --- |
| `--mode private` | Keep installed AI-KIT instructions and client configuration local through the managed `.gitignore` block. | Suitable for personal use in a project. Already tracked files remain tracked; changing ignore rules does not untrack them. |
| `--mode team` | Keep shared instructions/context visible to Git while excluding local state, caches, secrets and personal overrides. | Suitable for teammates receiving shared instructions through the repository. This option creates no commit or push. Existing custom ignore rules can still need review. |
| `--conventions owner` | Apply the owner's opinionated preferences when the relevant stack is confirmed. | For Laravel, these include no database foreign key constraints, a public UUID beside the internal ID, Policy/Factory/Seeder per model and one table per migration. [Full owner profile](../../template/ai-kit/profiles/OWNER.md). |
| `--conventions standard` | Follow established project conventions and the confirmed stack's normal guidance. | Choose this for a project whose conventions differ from the owner profile; the shared engineering and security rules still apply. |
| `--docker-cleanup maximum` | After every Docker task, remove all eligible disposable Docker resources, including the dedicated builder and its cache, and reclaim host resources. | The default and the behavior of earlier releases. Rebuilds start without a warm builder cache. |
| `--docker-cleanup keep-cache` | After every Docker task, still remove task-owned containers, networks, volumes and superseded test images, but keep the dedicated project builder and its cache. | Faster rebuilds. Host RAM/disk reclamation runs only on explicit request or observed resource pressure. [Cleanup details](DOCKER.md#docker-cleanup-and-host-reclamation). |

## Optional module flags

All flags below are **switches**. Without a preset they start off on a fresh installation; enabled selections persist in `ai-kit/settings.json` after apply. They can be combined with the main options above.

| Flag | Saved settings key | What it adds | Requirement or separate step |
| --- | --- | --- | --- |
| `--with-session-start` | `session_start` | Session-start instruction/shell hook and Claude wiring that reads context and Git status. | Claude must be selected for automatic hook wiring; the shell hook needs POSIX tools. Verify it in the actual client. |
| `--with-guards` | `guards` | Claude confirmation rules for Git commit/push. | Claude must be selected for native wiring. Core still requires explicit authorization for those operations. |
| `--with-data-guards` | `data_guards` | Claude confirmation rules for destructive file/Docker commands and detected framework migrations. | Claude must be selected for native wiring; these are client ask rules, not a universal sandbox. |
| `--with-native-settings` | `native_settings` | AI-KIT-owned Claude allow rules for the recorded test/lint/build commands, secret deny rules and managed secret-ignore blocks for supported selected clients. | Claude permission entries require Claude selection. Existing unrelated client settings are preserved; verify actual client behavior. |
| `--with-scoped-rules` | `scoped_rules` | Path-scoped module rules for selected clients with a supported scoped format. | Uses project module/profile evidence; rerun after reviewed module-map changes. Edited generated rules follow conflict handling. |
| `--with-ci` | `ci` | The application workflow `.github/workflows/ai-kit.yml`, which validates the committed AI-KIT files: required documents, settings fields, recorded managed files and local links. | It does not clone or install AI-KIT. It is meaningful in team mode; private mode keeps AI-KIT files out of Git, so there is nothing to validate. Review/pin the generated workflow before relying on remote execution. This does not publish packages/images or run the application's own test suite. |
| `--with-security-audit` | `security_audit` | Pinned Cloudflare audit resources and an explicit skill entry point. | Audit execution and compatible validators are separate; installing the module starts no audit. Upstream `*.test.cjs` files are not installed; they remain recorded and verified in the pinned manifest. Installations made earlier keep their old copies until removed manually. |
| `--with-strix` | `strix` | Pinned Strix reference skills and an explicit entry point. | Strix CLI, Docker, model access, targets and scan authorization are configured separately. |
| `--with-context7` | `context7` | Version-aware documentation lookup guidance and the `context7-docs` skill. | MCP server registration, authentication and a working live connection are separate. |
| `--with-web-design` | `web_design` | Web Design skills/guides and missing project brief, design-system and acceptance documents. | Existing design documents are preserved; external design tools, site generation services and framework dependencies require separate setup. |
| `--with-orchestration` | `orchestration` | Optional Codex helper configurations and disabled-by-default OpenRouter configuration. | Codex must be selected for native helpers; compatible clients, model credentials, budgets and explicit execution are separate. Installation launches no agents or paid calls. |

**Omitting a module flag during an upgrade does not disable it.** There are no `--without-*` flags. Presets manage only `session_start`, `guards`, `data_guards`, `native_settings` and `scoped_rules`; CI, security-audit, Strix, Context7, Web Design and orchestration remain independent and preserve prior explicit selections. To deselect another module, review its contract, set the corresponding existing JSON setting to `false`, then preview the installer. Previously installed files may be retained/reported and can still be discoverable by a client; deselection is not automatic file removal. [Lifecycle and client ownership](../../template/ai-kit/ADAPTERS.md#optional-install-extras).

## Common flag combinations

| Command | Result |
| --- | --- |
| `aikit install .` | Preview using saved choices, or fresh defaults if this project has no installation. |
| `aikit install . --dry-run` | The same explicit read-only preview. |
| `aikit install . --check` | Preview only; the doctor is not run because there was no apply. |
| `aikit install . --apply` | Apply an installation/update without a post-install doctor. |
| `aikit install . --apply --check` | Apply, then check the installed AI-KIT files. A doctor error can make this command fail after writes have already succeeded; it does not undo that installation. |
| `aikit install . --interactive` | Run the wizard and preview its choices. |
| `aikit install . --interactive --apply --check` | Run the wizard, apply after confirmation, then check the installation. |
| `aikit install . --preset team --mode private` | Preview the team's extra bundle with private sharing. Explicit mode takes precedence over the preset's mode. |
| `aikit install . --chat-language English --conventions standard` | Preview with English chat replies and the project's own conventions instead of the defaults. |
| `aikit install . --apply --dry-run` | Invalid: apply and preview switches are mutually exclusive. |

For normal non-interactive runs, settings resolve as follows: explicit CLI values take precedence; a preset sets its mode and five managed extras; other choices come from saved settings/agent state, then template defaults. Repeated `--agent` values form the explicit selection; `--with-*` switches add extras on top of the preset. The interactive wizard can supply its own selections, so review its summary and the final JSON plan. See [presets](INSTALL.md#presets) for exact mode behavior.

Use the same selections in preview and apply:

~~~sh
# Preview a new personal Codex installation.
aikit install . --agent codex --mode private

# Apply that selection and check the installed files.
aikit install . --agent codex --mode private --apply --check

# Update an existing installation while keeping its saved clients and settings.
aikit install . --apply --check

# Add documentation and security workflows to an existing installation.
aikit install . --with-context7 --with-strix --apply --check

# Install shared Codex/Claude instructions with the team extra bundle.
aikit install . --preset team --agent codex --agent claude --apply --check
~~~

When adding or changing options, first run the intended command without `--apply`; inspect `writes`, `conflicts`, `adapter_conflicts`, `warnings` and `extras`. An apply with unresolved conflicts can create missing review candidates while leaving accepted files and installer state unchanged. After reviewing a managed-file merge, use `--accept-local PATH` for that path and preview/apply again. [Conflict review and acceptance](../../template/ai-kit/UPSTREAM.md#conflict-candidates).

## Similar names in other commands

| Invocation | Meaning |
| --- | --- |
| `aikit install . --mode private` | Installation sharing mode: `private` or `team`. |
| `aikit route "task" --mode fixed` | Routing mode: `manual`, `fixed`, `recommended` or `adaptive`. These values are not accepted by `install --mode`. |
| `aikit install . --apply --check` | Check installation health after successfully applying an install/update. It does not run framework tests, a security audit or Docker cleanup. |
| `aikit doctor .` | Check an already installed application independently, without applying an update. |
| `aikit doctor . --fix` | Preview the repair plan that restores missing/baseline files through the installer. Nothing is written. |
| `aikit doctor . --fix --apply` | Write that repair plan. Local edits are preserved and conflicts still need review. `--fix` belongs to `doctor`, not `install`. Earlier releases applied `--fix` directly. |
| `aikit check` | Validate the bundled/reference AI-KIT distribution itself, not the application selected by `install`. |
| `aikit flags` | Print the `install` option schema as JSON (`--output FILE` writes it with LF line endings). It reads no project and installs nothing. |
| `aikit --version` | Show the CLI version; `--version` is a top-level option, not `aikit install --version`. |

Other subcommands have their own option sets and apply semantics. Use `aikit COMMAND --help` (for example, `aikit orchestrate run --help`) before combining flags from different commands; the help output of your installed version is authoritative. The tables above follow the [installer implementation](../../scripts/install.py) and [dispatcher](../../aikit_cli.py).
