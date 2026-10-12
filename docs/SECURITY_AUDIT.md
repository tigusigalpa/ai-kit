# Optional security-audit integration

The owner requested an optional, pinned skill with a short entry point and explicit invocation. Current scope is integration and tests; full audits remain separately requested.

## Ownership and installation

- [Upstream manifest](../integrations/security-audit.json) is the canonical revision/file identity: Cloudflare commit c1c8a8c1471069fb0e188eeaff69b8e8db6564a8, 20 skill files plus the upstream MIT license. Each imported blob was verified against the Git tree; the installer also validates byte size, Git blob SHA-1 and SHA-256 before selecting writes.
- Original bytes live in template/ai-kit/vendor/security-audit. [.gitattributes](../.gitattributes) disables newline conversion there. The checker exempts only manifest-verified conditional references from document-size warnings and authored-language checks (upstream tests contain exact Unicode fixtures); authored entry points retain their normal rules. UTF-8, metadata and links still receive checks.
- [Installer](../scripts/install.py) adds --with-security-audit and the persisted security_audit setting, outside every preset. Defaults remain unchanged. Optional source/native entry points and vendor files are omitted when unselected; the installed skill registry omits their link too.
- [Source entry point](../template/.agents/skills/security-audit/SKILL.md) defers to Core and the pinned method. Codex gets agents/openai.yaml with allow_implicit_invocation=false. Claude gets the same body with disable-model-invocation=true. Supporting files are not copied into native skill directories.
- The selected payload uses existing backup/baseline/conflict handling. Deselecting retains and reports managed files; removing a native client with tracked files still blocks until retirement is reviewed. Reports and audit execution are not installer outputs.

Installed-project usage and limitations: [security-audit contract](../template/ai-kit/SECURITY-AUDIT.md).
Invocation metadata follows [official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude skills](https://code.claude.com/docs/en/skills), checked 2026-10-12. File installation does not establish native discovery or runtime isolation.

## Verification

- Targeted Windows/Python 3.12.14 integration tests: 14 passed, covering absent defaults/presets, process/network-free preview/apply, explicit client metadata, links/doctor, persistence, reviewed synthetic pin upgrades, adaptations/conflicts/candidates/backups, retained deselection, native retirement, invalid metadata, digest failures and linked source/target refusal.
- Native Windows/Node.js 24.17.0 upstream tests exposed unsupported OS no-follow/nonblocking input opens. Keep the upstream rejection intact; native Windows CLI findings-validation tests cannot pass on this runtime. This is not evidence of a ready full-audit environment.
- Upstream full Windows run: 65 tests, 46 passed, seven CLI assertions failed because file opening is refused, 12 skipped. A separate run excluding CLI-named tests passed 44 in-memory checks with four runtime skips; 17 CLI-named tests were excluded, not counted as passed. POSIX Node was unavailable in the installed Ubuntu distribution and no cached Node Docker image was present; no runtime was installed.
- Kit validation passed with zero errors/warnings, including private/team visibility. All 21 upstream Git blobs also matched with core.autocrlf=true. Changed Python files passed Python 3.10 grammar; the short skill passed skill-creator's quick validator using installed Ubuntu Python/PyYAML 6.0.3.
- A wheel built offline without build isolation or new dependencies passed external Windows fresh-venv installation: CLI/imports, packaged kit validation, default install/doctor, optional Codex/Claude audit-file install/doctor and stable rerun. This does not establish Linux/macOS wheel execution or native client activation for these changes.
- Full Windows/Python 3.12.14 discovery: 271 tests in 991.952 seconds, 267 passed and four runtime skips (POSIX hook execution, symlink creation, two junction scenarios). Post-review package-name checks passed after rejecting traversal, case-fold aliases and collision with generated UPSTREAM.json; Python 3.10 grammar passed again. The earlier wheel smoke preceded that narrow manifest-name hardening.
- Self-review covered default/preset omission, persisted choices, source/native policy and paths, independent-review wording, license/provenance, backups/conflicts/candidates, symlinks/path boundaries, registry links, private/team visibility and packaged resources. The v0.10.0 changelog entry moved to the history archive to keep the root document within its budget.
- No full audit, live target, model run, external publication or native client activation is established.
- Included alongside Strix in [v1.1.0](../CHANGELOG.md#v110-2026-10-12). Release checks verified CLI/wheel identity, offline fresh-environment installation with both extras, stable rerun and a preserved synthetic upgrade; [shared release verification](STRIX.md#verification). Earlier behavioral/upstream results above were not rerun for documentation/version labeling.
