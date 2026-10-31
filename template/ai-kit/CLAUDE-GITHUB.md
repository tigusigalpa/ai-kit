# Optional Claude GitHub identity

Apply when settings.claude_github is true (`--with-claude-github`) and Claude is selected. Core still requires explicit authorization for each commit and push; this option grants neither. Installation performs no GitHub request, login, Git configuration change, commit, or push.

Before an authorized GitHub commit:

1. Establish the repository and the GitHub host from its reviewed remote. With GitHub CLI available, check the active account for that host (`gh auth status --hostname HOST`, then `gh api --hostname HOST user`). The authenticated API identity, not a repository owner or a Claude account, selects the human user. Never display authentication tokens.
2. Inspect the effective Git author and committer (including environment overrides) and repository configuration. Keep the user's established human name, verified account email, signing configuration, and existing human credits when they match the active account. Read account email metadata only when needed and authorized by the current credentials; never persist it in project context or shared instructions.
3. If identity is absent or differs, resolve it with the user before committing. An API-confirmed name/email or the user's explicit account noreply address may be used for that authorized commit. Never guess email from a login, select another signed-in account, change global Git configuration, or impersonate someone. If authentication/email verification is unavailable, report the specific missing information and stop the commit.
4. Use the verified human identity for author and committer. Omit Claude/Anthropic/agent co-author trailers and generated-by credits unless the user explicitly requests them. Keep requested human co-authors, signatures, and sign-offs. Inspect the resulting commit's author, committer and message; report a mismatch without rewriting existing history automatically.

Claude installations also request an empty native `attribution.commit` value. This controls Claude's added commit trailer, not Git's author/committer fields or permissions. Conflicting custom settings require review; organization-managed settings and native activation must be checked in the actual client. PR attribution is left under the user's existing settings.
