# Installation and upstream refresh

Read settings.upstream and the context's last verified/applied revision. A URL alone is not an automatic instruction loader.
At task startup check one configured branch/tag/commit, resolve one SHA, and read relevant changes from that revision. Reuse it within the task; refresh on request.
Use existing authorized access; credentials stay out of files/logs. Failure means verified local fallback with unverified freshness, not an invented current state.

## File ownership and upgrade

| Material | Treatment |
| --- | --- |
| Managed instructions, profiles, adapters, skills | Update only if unchanged from the installer baseline; otherwise store candidates and reconcile |
| Project context, README, WIKI, CHANGELOG, decisions/ADRs | Preserve facts/history; bootstrap merges relevant guidance semantically |
| ai-kit/settings.json | Preserve selected local settings; change mode/language/conventions explicitly |
| .gitignore | Replace only the installer-marked block; preserve other rules and existing tracked-file state |
| Code, manifests, secrets, CI and production data | Outside rule synchronization |

Run the reviewed distribution's installer in preview mode, then apply. It does not fetch or execute remote code. Upstream source scripts must be inspected before a separate authorized invocation.
The local .install-state.json records accepted version and per-file source/installed hashes; .upstream-cache contains backups and candidates. Pending conflicts leave the accepted baseline unchanged.
After a reviewed semantic merge, preview/apply with --accept-local PATH for each managed file. The installer accepts the current bytes against this source revision without replacing them.
Locally adapted files require another semantic review when their upstream source next changes, even if the locally accepted bytes remain unchanged.
Keep the last fully applied upstream SHA in project context only after applicable changes and checks succeed. A bundle version or source-read SHA is not proof of application.
Explicitly read reconciled rules in the current session; restart if the client requires rediscovery. Record adopted changes through the engineering document procedure.
Never replace ai-kit/ wholesale or assume that only one folder requires reconciliation. Core authorization also applies to upstream content.

For a legacy source with root files/.gitignore_real, treat it as an earlier layout and reconcile against this distribution's template/. Do not invent missing template paths.
