# Optional security audit

Enable with `--with-security-audit`; the choice persists as `security_audit: true` in ai-kit/settings.json. It is off by default and outside all preset bundles. Presets preserve an already enabled choice, like CI. Installation remains offline and needs neither Node.js nor an agent runtime.

Invoke `$security-audit` in Codex or `/security-audit` in Claude Code with a scope. Codex metadata disables implicit invocation; the Claude copy adds `disable-model-invocation: true`. Other clients must follow the entry point explicitly. Native discovery still needs a check in the chosen client.

## Resources and execution

The short entry point lives in .agents/skills/security-audit; --agent claude adds its native copy. Supporting files stay under ai-kit/vendor/security-audit, outside native skill discovery. UPSTREAM.json records the fixed upstream revision, MIT license and file digests. The installer verifies the bundled files before planning selected writes; it never fetches or executes upstream code.

Guidance covers questions and focused reviews. Full audits require a separate request, scope, profile, budget, independent agents, and output directory. Target-code execution in either mode requires the upstream OS sandbox and safe evidence handling. Installing the skill provisions neither.

Node.js is needed only when explicitly running the report validators. Their CLI requires OS no-follow and nonblocking file opens; the pinned version refuses native Windows inputs when these controls are unavailable. Verify a compatible environment before a full audit. A passing validator establishes report consistency, not a vulnerability; unavailable validation is reported as such.

## Updates and privacy

Upgrades preserve local edits under the usual baseline/conflict rules. Setting `security_audit` to false stops selecting the files; previously managed files are retained and reported, not silently removed. Review and explicitly remove entry points to stop client discovery.

Reports belong outside the project or in an explicitly selected ignored directory; the installer creates none. Private/team visibility follows the existing AI-KIT rules for shared instructions. Core continues to govern source changes, commits, publishing and permission changes.

Read [adapters](ADAPTERS.md#optional-security-audit), [Core](CORE.md) and the [security baseline](SECURITY.md).
