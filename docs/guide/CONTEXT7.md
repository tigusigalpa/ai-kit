# Library documentation with Context7

![Library documentation with Context7](https://i.postimg.cc/bv25Vwrc/12-library-documentation-context7.jpg)

**Bring version-relevant library documentation into coding tasks.** The optional Context7 workflow checks the dependency version, resolves the library, retrieves focused examples and records source/coverage gaps. Retrieved documentation complements AI-KIT's project facts and checks. [Upstream Context7](https://github.com/upstash/context7).

Preview installation:

```text
aikit install /path/to/my-app --agent codex --agent claude --with-context7
```

Review, then repeat with `--apply --check`; from a source checkout, `python scripts/install.py` accepts the same flag. The choice persists independently outside presets. It adds the short `context7-docs` skill with normal discovery; invoke `$context7-docs` in Codex or `/context7-docs` in Claude when needed. Send sanitized public library/version questions and verify returned examples against your project's checks.

**Connection setup is separate.** AI-KIT installs no server/package, provisions no account and writes no MCP credentials/configuration. The [connection and usage guide](../../template/ai-kit/CONTEXT7.md) includes Codex, Claude Code and Cursor HTTP examples with environment-based credentials, an OAuth alternative, activation checks and fallback behavior. Reuse an existing Context7 connection. [Source review and integration verification](../CONTEXT7.md); the hosted service is not revision-pinned.
