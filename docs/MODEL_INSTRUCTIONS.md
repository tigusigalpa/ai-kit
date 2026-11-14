# Model and instruction controls

## Architecture audit

The audit preceding implementation found these existing owners:

| Surface | Existing mechanism | Actual control |
| --- | --- | --- |
| Project instructions | `template/AGENTS.md`, Core, Engineering, settings, scoped stack rules and client adapters in `integrations/agents.json` | Files read by the host; Claude imports AGENTS, other adapters point to the same rules. Host discovery, instruction precedence and previously loaded context remain external. |
| Model recommendations | `scripts/router.py`, `adaptive.py`, router POLICY, provider catalogues, selection/routing JSON | Offline advice, role resolution, effort recommendations and measured optimization. No parent-chat model switch. Existing fixed/manual pins configure recommendations, not a session lock. |
| Native helpers | Installer, `integrations/codex-agents/*.toml`, optional orchestration contract | Explicit model/effort assignments in project helper files; no root Codex configuration change. |
| Aider | `router.configure_plan` | Explicitly applied native `model`/`weak_model` configuration; existing differing bytes become conflicts. |
| External execution | Optional `scripts/orchestrate.py`, `orchestration.json` | One explicitly configured OpenRouter model per request, budget checks and execution receipts; no automatic fallback. This is a separate task, not a switch of the parent chat. |
| Evaluation | Benchmark adaptive arm, metrics proposals and measurement journal | Offline recommendations or explicitly authorized worker execution. Requested settings and worker/provider observations are distinct. |
| Existing configuration | Project settings, installer previews/state/conflicts, doctor, context selector | Reuse these mechanisms; no second router or model-lock service is needed. |

Additional advisory entry points are ADAPTERS, METRICS and the optional orchestration instructions. Ordinary execution already loads routing policy conditionally. Provider catalogues describe capabilities and defaults, not the current session. Client adapters and path-scoped rules preserve nested project requirements.

Pinned security-audit/Strix references were also searched for model/effort guidance. Strix contains explicit external `STRIX_LLM` examples; its wrapper requires an authorized scope and selected data/model destination. These references do not select the parent model or authorize an automatic handoff. Keep their pinned bytes intact and apply the common instruction controls before optional reference guidance.

The implementation adds two independent project settings with legacy defaults (`true`, `full`), gates offline recommendations/native generated assignments, renders a smaller minimal entry point from the same canonical template, and exposes effective settings through existing reports. Mandatory project instructions, security, architectural decisions, applicable stack rules and acceptance checks survive either profile. Explicitly configured external execution remains separate and opt-in. The shared behavior contract lives in Engineering, not in a second router or a copied policy tree.

## Operation and upgrade behavior

The [README instructions](../README.md#keep-your-chosen-model-and-select-instruction-depth) cover the four combinations and command examples. Settings validation rejects non-boolean switching values and unknown instruction profiles. Installer flags are optional, saved values persist, and omitted keys resolve to legacy defaults. Existing presets and economic routing profiles are independent. Changing a profile does not delete optional resources or a project's own rules.

Minimal omits only marked optional entry-point sections; required policy owners are unchanged. The host must read settings before optional instructions. Relevant explicitly requested workflows keep their security/authorization boundaries. Files present on disk are not evidence that a host loaded them. A client may still preload descriptors or global instructions; those are outside this installer.

Disabled routing returns no model, effort or capability-ladder recommendation. CLI routing honors an explicit project or the current installed folder. Configure emits an empty disabled resolution and writes no Aider model configuration; it preserves existing native settings. Metrics observations/reports remain available, while model-selection proposals are refused. Benchmark adaptive trials retain the pack's explicit fixed route when recommendations are disabled; they must not be described as evidence of active adaptive routing.

Managed Codex helpers omit AI-KIT model/effort assignments when switching is disabled. Unchanged helper files update through normal installer baselines; custom edits conflict and block accepting the new installation. User root configuration, reasoning effort and unrelated settings are untouched. Doctor warns about remaining native overrides. Explicitly accepted local adaptations remain the project owner's responsibility.

The OpenRouter executor continues to require its own enablement, exact model, task scope, apply authorization and budget checks in all combinations. Its system message propagates the controls without inserting effort parameters or an alternate model. Disabled fallback and the private requested/served-model accounting remain intact.

Doctor reports effective controls and a null/unavailable parent runtime with provenance rather than guessing. Existing external-call receipts and metrics can provide scoped execution observations. Configuration values, reasoning-token counts and recommendation output cannot establish the actual parent model or reasoning effort.

## Platform boundary

AI-KIT cannot enforce a model lock, set a chat's reasoning effort, inspect hidden reasoning, or prove that a host loaded every file. It must not infer a running model from routing pins, helper configuration, environment hints or the user's preferred model. Existing OpenRouter receipts and benchmark/metrics observations can report the execution they describe; they do not identify the parent chat.

Codex documents separate model/effort controls and native helper overrides; omitted helper controls leave resolution to the host, including its own defaults. See the official [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), [subagent inheritance documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents), and [Astra model/effort selection](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex). Sources checked on 2026-11-14. This establishes a configuration boundary, not live activation evidence.

## Verification

Local checks on 2026-11-14:

- Full Windows/Python 3.12.14 discovery: **501 tests in 1390.916 seconds, successful with 12 environment/platform skips** (unavailable real-symlink privileges, POSIX modes/FIFO/sh, and Windows-invalid colon filenames). This includes 12 new behavioral tests: 11 instruction-control tests and one isolated-benchmark regression.
- All four combinations cover independent settings, legacy missing-key defaults, saved upgrades, presets/team visibility, mandatory security/architecture retention above byte budgets, native configuration preservation/conflicts, disabled recommendations/proposals, unknown parent telemetry and explicitly configured external execution. The benchmark test verifies propagated settings, fixed routes with switching disabled, and refusal to resume with another instruction profile.
- The full suite preceded a final wording-only entry-point compaction. The final 11 control tests passed again in 19.840 seconds, including the new 2500-byte assertion with UUID/orchestration enabled. The final checker and installed-wheel smoke were rerun after that compaction. Applicable project rules and safety requirements were retained.
- `python scripts/check_kit.py`: zero errors and warnings, including Git visibility. Python 3.10 grammar parsed 64 Python files successfully; this is not native Python 3.10 execution.
- Isolated sdist-to-wheel build, distribution resource/privacy checks, strict Twine and a fresh offline wheel installation passed. CLI smoke includes the new flags, upgrade to false/minimal, helpers without model/effort assignments, disabled routing and existing optional modules. All **333 packaged source files** match the final reviewed LF build snapshot; local maintainer files and bytecode are absent. VERSION remains 1.7.0 for this unpublished worktree candidate; no registry or release was changed. This verification section and the changelog result note were appended afterward and are a later documentation snapshot.
- Docker impact is confirmed: code, defaults and installed instructions require an image refresh. The selected context is `desktop-linux`, but repeated daemon version/readiness queries timed out, including a bounded 25-second preflight. **No image build or container smoke was run**, and no image, builder, container or volume was created or changed. Docker Desktop and unrelated workloads were left running. Rebuild/test a development image when that API is available; existing images do not contain these changes.

Hosted CI, Linux/macOS runtime tests, live Codex/Claude activation, actual model/effort telemetry and paid provider executions were not performed. Synthetic local tests establish behavior and preservation, not a performance improvement or a platform-enforced model lock.

Release labeling, Docker availability and publication after these implementation checks are tracked separately in [v1.8.0](V1_8_0.md).
