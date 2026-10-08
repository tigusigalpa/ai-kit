# AI-KIT

A practical starter for development with ChatGPT/Codex and other coding agents. It keeps verified project facts, routes relevant rules, and provides conservative installation.
Current bundle version is in [VERSION](VERSION); license is [MIT](LICENSE). Default conventions are the owner's explicit choices.

## Layout

| Path | Purpose |
| --- | --- |
| template/ | Clean files installed into an application project |
| templates/gitignore.private | Universal exclusions plus local AI-KIT files |
| templates/gitignore.team | Universal exclusions; shared instructions and context stay visible |
| scripts/ | Installer, checker, and read-only Docker resource report |
| docs/ | Kit decisions and implementation record |
| Root context/changelog | Facts and history of AI-KIT itself |

The root .gitignore governs this reference repository. The two templates are not active ignore files here.
Keep the reference layout when placing this distribution in the canonical repository; copying the reference root wholesale into an application is not installation.

## Install

Requires Python 3.10+; the installer has no third-party dependencies and does not call Git writes or execute downloaded code.
Run from this distribution, using the target repository's absolute path:

~~~sh
python scripts/install.py /path/to/project
python scripts/install.py /path/to/project --apply
python scripts/install.py /path/to/project --mode team --agent claude --apply
~~~

Preview is the default; --dry-run is an explicit equivalent. Default mode is private, chat language Russian, project content English, and conventions owner.
The installer creates missing files, preserves project-owned context/history/README/wiki, and updates managed instructions only if unchanged since the accepted baseline.
Conflicts yield exit code 2. Apply stores proposed files under ai-kit/.upstream-cache/candidates/ for review and leaves the accepted installation unchanged.
Merge those candidates semantically, then preview/apply with --accept-local PATH for each reviewed managed path. This records the incoming source and retained local content without overwriting the merge.
An accepted adaptation requires reconciliation again when that upstream file next changes. Backups precede changed-file writes.
Do not delete an existing ai-kit/ to upgrade it. [Upgrade rules](template/ai-kit/UPSTREAM.md).

For another user's project, --chat-language English or --conventions standard can be selected explicitly. The owner's projects retain owner conventions.
--agent claude copies selected source skills to .claude/skills/ without symlinks or overwriting unmanaged files; default codex uses .agents/skills/.
Optional --agent kimi, manus, copilot, cursor, or aider installs the matching entry. Native activation is client-dependent; see [adapters](template/ai-kit/ADAPTERS.md).

## Ignore modes

Private excludes installed AI-KIT instructions/context and .claude/; a new clone needs a separate installation.
Team keeps shared AGENTS, CLAUDE, skills, context, decisions, and ADRs visible, while excluding personal settings, secrets, installer state/cache, and overrides.
Installer-owned ignore rules form one replaceable marked block; existing rules remain intact. Legacy unmanaged exclusions may still hide team files and require explicit reconciliation.
Track composer.lock by default for applications, Go manifests/checksums, and Python/frontend locks. The installer detects PHP/Moodle module roots for scoped generated-file rules and preserves Go vendoring. See [installation procedure](template/ai-kit/BOOTSTRAP.md).

## Adapt and work

Send [the start prompt](BOOTSTRAP_PROMPT.md). Bootstrap verifies stack/version/commands and fills the target's context and module map.
Root instructions and Core are short; load profiles, container detail, and provider routing only when relevant.
Settings are in template/ai-kit/settings.json; active OpenAI model defaults have one owner in the provider JSON. These files do not implement model switching.
After each task with project file changes, update that project's CHANGELOG; kit maintenance belongs in this root changelog.

## Check and develop

~~~sh
python scripts/check_kit.py
python -m unittest discover -s tests -v
~~~

The checker validates internal files/anchors and lightweight Markdown hygiene without a network dependency; external URLs need targeted verification.
The CI workflow runs the same validation and tests on Windows and Linux. Its hosted status is unverified until uploaded and run.
[Implementation and measured checks](docs/IMPLEMENTATION.md). [Contributing](CONTRIBUTING.md). [Security reporting](SECURITY.md).
