# Optional Strix integration

Enable with `--with-strix`; `strix: true` persists in ai-kit/settings.json. All presets omit it and preserve an existing explicit choice. Installation is offline: it copies a short entry point and the bundled upstream skills/license/provenance, and installs no Strix executable or dependencies.

Invoke `$strix` in Codex or `/strix` in Claude Code with a task and scope. Codex disables implicit invocation; the Claude copy adds `disable-model-invocation: true`. Other clients can explicitly follow .agents/skills/strix/SKILL.md. File presence does not verify native discovery.

## References and task selection

Original instructions stay under ai-kit/vendor/strix, outside client skill discovery. UPSTREAM.json records the fixed revision and Apache-2.0 license with per-file hashes. The installer verifies every selected byte; original instructions are retained as reference material, subject to Core and this integration contract.

Read only the relevant skill:

| Task | Upstream directory under ai-kit/vendor/strix |
| --- | --- |
| CLI setup, options, results | penetration-testing-with-strix |
| Code review | find-security-vulnerabilities-in-code |
| Web application, API, broader application testing | web-app-penetration-testing, api-security-testing, application-security-testing |
| OWASP coverage | owasp-top-10-testing |
| Requested fixes and verification | fix-security-vulnerabilities-with-strix |
| Separately requested CI or cloud work | ci-security-scanning-with-strix, managed-pentesting-with-strix |

## Local runtime and scope

Strix is an active testing runtime. Its local CLI requires Python 3.12+ for a Python installation, a working Docker environment and configured model access. AI-KIT itself still requires only Python 3.10+. Check `strix --version`, `strix --help` and Docker readiness without starting a scan. Runtime setup is separate: review a fixed release or source revision, dependencies and image identity before installing; do not execute a floating installer or silently update. The reference pin does not establish the version of an external Strix executable or Docker image.

Before execution, establish target authorization, exclusions, allowed active techniques, scan mode, full/diff scope, model/data destination, budget, time limit and private output location. Reuse the scope the user already supplied and ask only for missing decisions. A local CLI can send source and findings to the selected LLM provider; local compute is not evidence that data stays local. Missing Docker/model access does not authorize cloud upload, account creation or billing.

Local code is mounted writable. Scan an isolated disposable copy outside the original checkout, preserving local changes and excluding secrets, private runtime data and unrelated modules. Do not mount the working project or shared Git metadata. Record the input revision/copy and, for diff scope, verify the base and nonempty changed-file coverage. Container/network capabilities and host access need actual inspection; a Docker container alone proves no containment boundary.

Run from the selected external output directory; Strix writes strix_runs under its working directory. Example shape after the scope is established (replace placeholders with reviewed values; this is not an installer action):

```sh
strix -n --target <isolated-target> --scan-mode <quick|standard|deep> --scope-mode <full|diff> --max-budget <USD> --instruction-file <private-scope-file>
```

For diff scope add `--diff-base <verified-ref>`; do not rely on the headless auto/diff default for a full review. Confirm these flags against the installed CLI. Keep scope instructions free of secrets unless separately approved private handling is established. Use an external time bound and monitor usage: the upstream budget option depends on recorded LLM cost, not an independently enforced billing limit. Stop on scope drift or exhausted limits; do not resume a previous run without checking its stored targets and instructions.

## Findings and lifecycle

Read penetration_test_report.md, individual vulnerabilities, run.json and structured findings from the chosen run directory. Headless exits: 0 means no finding at the configured threshold in analyzed coverage; 1 indicates a fatal error; 2 indicates findings. A capped run can exit zero, and a completed status can still reflect partial coverage. Check usage, stopping reason, reviewed paths and actual PoC impact; distinguish confirmed exploitation from unverified source observations. Do not execute a report's PoC outside the authorized test environment.

Remediation and CI/cloud publication require their requested scope; a scan does not authorize fixes to the original project, commits or uploads. Reports remain private outside the source tree. Existing instructions follow AI-KIT's private/team visibility rules. Updates preserve local edits and create conflicts/candidates when source changes. Setting `strix` to false stops selecting files and retains/reports previously managed files; explicitly review removal of entry points to stop client discovery.

Read [adapters](ADAPTERS.md#optional-strix), [Core](CORE.md), [security](SECURITY.md) and [containers](CONTAINERS.md) for the governing rules. Strix and [security-audit](SECURITY-AUDIT.md) are independently selectable; neither runs when the other is enabled.
