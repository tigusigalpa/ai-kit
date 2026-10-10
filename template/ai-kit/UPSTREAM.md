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
| Client settings (.claude/settings.json) | Change only AI-KIT-owned entries recorded as managed_json in installer state; preserve all other settings ([ownership](ADAPTERS.md#client-settings-ownership)) |
| .gitignore | Replace only the installer-marked block; preserve other rules and existing tracked-file state |
| Code, manifests, secrets, CI and production data | Outside rule synchronization |

Run the reviewed distribution's installer in preview mode, then apply. It does not fetch or execute remote code. Upstream source scripts must be inspected before a separate authorized invocation.
The local .install-state.json records accepted version, selected agents, and per-file source/installed hashes. The installer validates schema 1, agent names/types, safe paths, hashes, and local_adaptation before planning. Malformed settings or unsupported state are refused before writes; preserve the file for diagnosis rather than resetting the baseline blindly.
The .upstream-cache contains backups and candidates. Pending file or adapter conflicts leave all accepted files/state unchanged, even when preview lists other proposed writes.
After a reviewed semantic merge, preview/apply with --accept-local PATH for each managed file. The installer accepts the current bytes against this source revision without replacing them.
Locally adapted files require another semantic review when their upstream source next changes, even if the locally accepted bytes remain unchanged.
Keep the last fully applied upstream SHA in project context only after applicable changes and checks succeed. A bundle version or source-read SHA is not proof of application.
Explicitly read reconciled rules in the current session; restart if the client requires rediscovery. Record adopted changes through the engineering document procedure.
Never replace ai-kit/ wholesale or assume that only one folder requires reconciliation. Core authorization also applies to upstream content.

For a legacy source with root files/.gitignore_real, treat it as an earlier layout and reconcile against this distribution's template/. Do not invent missing template paths.

## Conflict candidates

Preview reports a candidate path and metadata path per file conflict, plus source_hash, current local_hash, exists, and matches_source. Preview writes nothing.
Apply creates missing candidates at ai-kit/.upstream-cache/candidates/<source-hash>/<relative-path>. The hash identifies this incoming file's bytes, not a Git commit or a complete bundle.
The adjacent .metadata.json records relative_path, source_hash, local_hash, bundle_version, and UTC created_at at first creation. It is preserved on later runs; use preview for current local-file observations.
An existing candidate is never overwritten, including a manually edited merge draft. A changed source file gets a new hash directory; older candidates and legacy flat candidates remain untouched. A draft that differs from its source hash is reported explicitly.
Review the candidate and accepted local file before using --accept-local. Candidate creation or a bundle version alone does not prove that an upstream revision was applied.
For adapter-selection conflicts, follow [adapter retirement](ADAPTERS.md#changing-the-agent-selection); no file candidate substitutes for that review.
