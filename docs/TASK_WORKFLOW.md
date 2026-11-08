# Optional task workflow implementation

The [README walkthrough](../README.md#optional-task-workflow-requirements-states-and-checks-tied-to-code) owns user examples. The [installed contract](../template/ai-kit/TASK-WORKFLOW.md) owns behavior and boundaries. [ADR 0019](adr/0019-explicit-source-bound-task-workflow.md) records the design. Introduced in v1.7.0; [the release record](V1_7_0.md) owns final versioned checks and registry status. The implementation receipts below predate release labeling.

## Components and ownership

- `scripts/task_workflow.py` owns explicit task commands, validated definitions, task revision/cycle/state, local check execution, atomic records and acceptance.
- `scripts/task_snapshot.py` owns bounded offline Git source discovery and working-tree fingerprints.
- `--with-task-workflow` persists the independent `task_workflow` setting. Optional TASK-WORKFLOW.md is managed with normal installer conflict handling; task.example.json is project-owned and created once. Presets do not enable or disable this extra.
- Definitions, events, receipts and approvals live in ai-kit/.tasks/. Both sharing modes ignore it; archive/context filters exclude it. The installer does not interpret or rewrite task history.

## Definition and state contract

Schema-1 definitions have exactly schema/id/title/description/acceptance/checks. Acceptance requires 1-50 distinct criteria with descriptions; checks require 1-20 distinct IDs, bounded argv arrays, a project-relative cwd and 1-3600-second timeout. IDs are portable opaque lowercase names; reserved Windows device names are refused. Duplicate JSON keys and nonfinite constants are refused.

Normal state path: planned -> implementing -> checking -> reviewing -> awaiting_approval -> accepted. Entering implementing increments the cycle, so old checks cannot stand in for a new implementation pass. Revision explicitly replaces the definition, increments revision, resets cycle and returns to planned, preserving historical receipts/approvals. Active tasks can fail/cancel; accepted tasks can reopen; cancelled tasks are terminal. All transitions are explicit and guarded. Check execution itself enters checking; a failed/timed-out/interrupted/source-changing check leaves failed.

Records use schema 1 and contain the definition, revision, cycle, state, bounded event/receipt/approval arrays. Per-project exclusive locks serialize writes/checks. State replacement is atomic and synced; interrupted operations retain pending receipts/stale locks for operator investigation. Creating an identical task is idempotent; different content cannot silently reset it.

## Source and check evidence

Inspection requires Git and its working-tree root, including an unborn repository if it has not yet committed. Git discovery strips inherited GIT_* repository/index overrides, disables fsmonitor/untracked cache and contacts no remote. Fingerprints include HEAD, index modes/objects, regular working-file bytes/executable evidence, deleted tracked paths and nonignored untracked files. Runtime journals under ai-kit are excluded even if accidentally tracked. Case collisions, submodules, unmerged entries, known nonignored credential paths and linked/nonregular source files are refused. Bounds: 20000 paths, 16 MiB per file, 256 MiB total content and 8 MiB Git listings.

The effective check fingerprint also binds the definition/revision/cycle. Each receipt identifies the selected argv/cwd, task/code fingerprint, start/end, exit code, duration and combined child-output SHA-256/byte count. Raw output is streamed into a digest and discarded, not retained in memory/history or copied to reports. On apply, a running receipt is persisted before execution. Output from the process is untrusted data and cannot transition/accept the task. A command changing the task ledger is refused without overwriting that altered state.

Every required check needs its latest passing receipt at the current fingerprint before review/approval/acceptance. A failing rerun supersedes a prior pass. Acceptance additionally binds the task ID/current fingerprint and requires exactly every criterion with passed=true and nonempty evidence, plus a reviewer label. That label is not authenticated identity; the decision is an assertion by the operator. No Git/deployment permission follows from acceptance. Status remains read-only, exposes current validity and marks changed accepted work stale without changing the stored historical state.

## Boundaries

The runner is a convenience for local trusted checks, not a command allowlist or process/network sandbox. It inherits the invoking environment and permissions; dependencies, network, databases and production protection must be configured separately. Checks run with no shell wrapper and stdin closed. Timeout/interruption attempts to stop the process tree/group, but is not a guarantee against a process deliberately escaping. Descendants retaining stdout after a command exits cause refusal; inspect their lifecycle separately.

Before/after fingerprints assume quiescent source and do not detect an adversarial change-and-restore between observations or establish a hermetic build. Ignored files/dependencies, services, environment and tool versions are outside the fingerprint. Git staging or a new commit conservatively invalidates evidence even when runtime bytes are otherwise equal. Review files should be outside source discovery, e.g. ai-kit/.tasks/reviews/.

The controller launches no agent/client, contacts no model, runs no automatic retry/review loop and ingests no hosted-CI result. Declared check commands may themselves contact services or perform other effects: review and authorize their scope separately and keep credentials out of argv/evidence. Native orchestration and its monetary ledger remain separate. A deployment controller or isolated executor is not part of this stage.

## Verification

Verified locally on 2026-11-08 using disposable repositories and synthetic criterion decisions; no model/client orchestration or real application feature was run:

- Full Windows/Python 3.12.14 discovery: **483 tests in 804.843 seconds, successful with 12 platform/environment skips**. These include POSIX hooks/modes/FIFO, Windows filename restrictions and unavailable symlink privileges. Restricted Windows creation and refusal to overwrite an existing task were also exercised directly.
- Full packaged Linux/Python 3.13.16 discovery in the final non-root, offline/read-only image: **483 tests in 59.225 seconds, successful with three skips** (two Windows junction fixtures and a deliberately excluded root maintainer-entry check).
- Twenty-four task-module scenarios plus dispatcher coverage exercise default absence/independent selection, create-once examples and private upgrade preservation, invalid/duplicate definitions, preview/state preservation, complete acceptance, missing/stale/failed checks, reopening/revision, cancellation, interrupted runs/timeouts, source mutation, credential/submodule/link/size refusals, exclusive locking, altered-state preservation and atomic-save failure. The Windows publication path uses no hard-link operation.
- Python 3.10 grammar checks passed for **62 Python source/test files**. A native Python 3.10 runtime, macOS and hosted CI were not run in this task.
- Isolated sdist-to-wheel builds, metadata/resources/privacy probes, strict Twine and fresh offline wheel installation passed. The actual installed task CLI completed preview/create/transitions/check/synthetic acceptance/stale-status scenarios. No user-global Python package was changed.
- Upgrade from the previously published `ai-kit-python 1.6.0` preserved saved Russian chat, Codex/Claude selections, Context7, project documents, MCP configuration and private artifacts. Explicit module enabling passed doctor and a stable rerun. This establishes installer preservation, not actual native-client activation.
- Docker CLI smoke passed offline/read-only reports, installation of all extras, source-bound task CLI execution, preservation, stable reruns, actual build-context privacy probes and SIGTERM both with init and as PID 1. The Windows bind-mount all-extras test allows 600 seconds for its file I/O; semantic assertions are unchanged. A separate full task lifecycle also passed with the non-root, network-disabled image writing into a Windows bind-mounted disposable project; its temporary project was removed.
- All **327 packaged files** match between the reviewed LF source export, final local wheel and final Linux image. Private task state and root local maintainer files are absent. Local aliases `ai-kit:dev` and `ai-kit:task-workflow-dev` identify the tested development image: `sha256:49cead3c4fb476b503f9f2b6fd79e212ddff55f8eabc2748a41216a871ddcb7e`. This is a local image identity, not a registry publication/digest.

The tested export is based on commit `ccddc4d91c5c6bdbb33ba0dd0fed554710b93bc8` plus the reviewed uncommitted feature tree, SHA-256 `5d5a1f086886008dd58a3ed1c4382a39b1c7bfd5f00d442b9fe1a35b4c7a5a50`; the image revision label records that distinction. Subsequent verification notes and README/guide clarifications are descriptive only, so the prepared artifacts retain their earlier documentation snapshot. These implementation-only receipts used VERSION 1.6.0 and involved no Git/PyPI/Docker Hub publication. Versioned release verification is recorded separately.

The dedicated builder/cache/container/state volume and two superseded task images were removed. Builder prune reported 624.8 MB; this does not establish physical disk shrinkage or host RAM reclamation. No host compaction or unrelated workload cleanup was performed. Raw logs, prepared artifacts and source/image receipts stay outside the source checkout.
