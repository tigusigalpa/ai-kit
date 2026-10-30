# Security workflows

**Available since v1.1.0: established security methods in your coding workflow.** Give your agent a structured audit method for understanding risk, and a separate workflow for testing exploitability with Strix. Choose the capability your task needs; enable either or both.

| Integration | What it adds | Install flag | Codex / Claude Code |
| --- | --- | --- | --- |
| **Cloudflare security-audit** | Security guidance and focused review; a full audit method with reconnaissance, hunting, evidence validation, coverage and reporting | `--with-security-audit` | `$security-audit` / `/security-audit` |
| **Strix** | Workflows for code, web application, API and OWASP testing, findings review and requested remediation; separate CI/cloud references | `--with-strix` | `$strix` / `/strix` |

**Cloudflare: a method for evidence-based review.** The complete upstream skill includes attack-class references, report schemas and Node.js validators. The short entry point loads only relevant material and distinguishes focused guidance from a separately requested full audit. Independent verification, execution isolation and safe evidence handling remain part of that full-audit contract. The installer copies the pinned skill except the upstream `*.test.cjs` test files: they remain recorded and verified in the pinned manifest but are not installed into projects (after 1.4.5). Installations made before that change keep their old copies until you remove them manually. [Usage and prerequisites](../../template/ai-kit/SECURITY-AUDIT.md).

**Strix: a path from source review to active testing.** Nine original skills cover local code and deployed targets, API/web testing, OWASP coverage, fixing findings and verification. The AI-KIT entry point prepares scoped local CLI work, checks prerequisites and reviews proof-of-concept evidence, usage and actual coverage. CI and managed-cloud guidance is available when specifically requested. [Runtime and scan contract](../../template/ai-kit/STRIX.md).

Preview both integrations in an application project:

~~~sh
aikit install /path/to/my-app --agent codex --agent claude --with-security-audit --with-strix
~~~

Review the preview, then repeat with `--apply --check`. Use either flag alone to select one integration; from a source checkout, `python scripts/install.py` accepts the same flags. Invoke the installed skill with a concrete scope, for example in Codex:

~~~text
$security-audit Review authentication and tenant isolation in api/. Use guidance mode and report evidence and validation gaps.
$strix Prepare a local scan of a disposable copy of api/. Agree the model, scope, budget and time limit before execution.
~~~

In Claude Code use `/security-audit` and `/strix`. Other clients can explicitly follow the installed source entry points.

- **Controlled discovery:** both are off by default and outside presets. Explicit selections persist; Codex/Claude metadata prevents implicit invocation. Supporting references stay outside native skill discovery.
- **Traceable inputs:** Cloudflare is pinned at `c1c8a8c…` ([manifest](../../integrations/security-audit.json), MIT); Strix at `f7a32ae…` ([manifest](../../integrations/strix.json), Apache-2.0). The installer checks file coverage, sizes, Git blobs and SHA-256 and preserves original bytes/licenses.
- **Preserved customization:** existing backup/conflict rules protect local adaptations; private/team visibility follows the kit's instruction policy.

Installation stays offline and copies files only. A Strix scan requires a separately configured CLI, Docker and model access, plus authorized targets and limits; local code mounts are writable, so use an isolated copy. Cloudflare's pinned validator CLI needs OS no-follow/nonblocking input protection and refuses unsupported native Windows inputs. Installation establishes neither a running audit nor complete vulnerability coverage; [integration verification](../STRIX.md#verification) records what was tested.

See [Installer flags and options](INSTALLER_FLAGS.md#optional-module-flags) for persistence and deselection.
