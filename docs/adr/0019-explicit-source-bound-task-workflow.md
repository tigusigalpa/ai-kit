# ADR 0019: Explicit source-bound task workflow

Date: 2026-11-08
Status: Accepted; introduced in v1.7.0

## Context

Passing tests do not alone establish that a task met its requirements. A check against an older source tree cannot establish the current tree's correctness. AI-KIT has a manual engineering cycle, a measurement harness and bounded text accounting, but none is a general task-state controller.

## Decision

Add an independent task-workflow installer extra and a standard-library local task CLI. Persist each task atomically under ignored ai-kit/.tasks/: definition/revision, execution cycle, state/events, check receipts and explicit criterion approvals. Preserve prior receipts and decisions when revising/reopening work. Installation adds a short optional contract and a create-once example, without changing Core, launching checks or installing new skills.

Use Git HEAD/index plus actual tracked/deleted/nonignored untracked file content as a bounded source fingerprint. Include task revision/cycle/definition in the check fingerprint. Compare before and after a selected local command; current passing receipts for all declared checks gate review and acceptance. A new cycle, revised requirements or changed source invalidates effective evidence. A read-only report marks historical acceptance stale rather than rewriting history.

Mutations preview by default and use exclusive locking and atomic file replacement. Check execution needs its own explicit apply. Commands use argv arrays without a shell and run in a validated project directory; duration is bounded and raw child output is hashed/discarded. Acceptance requires exact fingerprint and criterion evidence, but remains the operator's assertion, not an authenticated human identity or independent semantic judge.

## Consequences and limits

No external model, automatic agent coordination, hosted CI ingestion, retry loop, commit, push or deployment is introduced. Task checks use current local credentials/permissions: this is not an adversarial process/network sandbox. Ignored dependencies, services, tool versions and transient intermediate changes are outside the source evidence. Submodules, linked sources, unresolved merges and known nonignored credential paths are refused. The first stage requires a Git working-tree root for source checks and has explicit file/byte/history limits.

Private state stays out of Git in both modes and out of sdist/wheel/image inputs. A normal installer upgrade preserves state and customized examples. Runtime/template changes require a locally rebuilt/tested development image; publication is separate.
