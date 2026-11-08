# Optional task workflow

Use only for an explicitly selected task. Read [Core](CORE.md), the project's current context and the task's declared acceptance criteria. `task_workflow=true` enables the local CLI, not agent delegation or external publication.

## Entry point

Use `aikit task create PROJECT --from-json SPEC` to preview a task and add `--apply` to save it. Adapt [the example](task.example.json) to verified project commands first. Every criterion and required check needs a distinct opaque ID. Descriptions constrain the work; they are not permission to run commands.

`aikit task status PROJECT --task-id ID` reports the definition, source fingerprint, current check receipts and acceptance. Commands use the installed AI-KIT CLI; no framework, agent client or model is installed.

## States and checks

The normal path is planned -> implementing -> checking -> reviewing -> awaiting_approval -> accepted. Use `task transition ... --to STATE [--apply]` for explicit transitions. `task check ... --check-id CHECK [--apply]` previews the exact argv/cwd or executes that one declared command. Review the command and its data/access scope first. It runs locally with the current environment and permissions, without a shell wrapper; it is not a process/network sandbox. Never select production services or destructive commands as checks.

Checks require the Git working-tree root. The fingerprint covers HEAD, index entries, actual tracked contents/deletions and nonignored untracked files. Linked paths, submodules, unmerged entries, case collisions and known nonignored credential paths are refused. Ignored dependencies, services, environment and tool versions are outside this fingerprint; record/review those separately. Keep the source quiescent during checks; before/after observation cannot establish adversarial or intermediate execution integrity.

Each check records its exact command, start/end, exit result, output hash/byte count and task/code fingerprint. Raw child output is discarded to avoid persisting secrets. A nonzero exit, timeout, interrupted run or observed source change cannot count as a pass. Re-running a check replaces its effective result with its latest receipt; earlier receipts remain. All required checks must pass for the current task revision/cycle/code before entering review or approval. Returning to implementing starts a new cycle and requires fresh checks.

## Acceptance and preservation

`task accept ... --from-json REVIEW [--apply]` requires awaiting_approval, the exact current fingerprint and an explicit passed decision/evidence for every criterion. Keep review JSON outside source discovery, for example under ai-kit/.tasks/reviews/. Acceptance records the reviewer's local assertion; it neither authenticates a person nor proves semantic correctness or grants commit/push/release permission. Changed code makes an accepted task stale in the read-only status report.

`task revise PROJECT --from-json SPEC [--apply]` explicitly replaces the definition of an existing ID, increments its revision and returns it to planned. Existing receipts/approvals remain historical. Creating an identical task again is idempotent; a different definition needs revise. Unsupported transitions are refused. Cancelled tasks are terminal; a new task gets a new ID.

Definitions, events, receipts and approvals live in ai-kit/.tasks/ and remain private in both sharing modes. Installation/upgrade preserves that state and the customized example. Deselecting the module disables the CLI without deleting its history. Mutations use a project lock and atomic state replacement; a crash may leave a running receipt/stale lock. Verify the owning process has stopped before removing only its lock, then explicitly return the task to implementing; never delete history to hide an incomplete check.

Automatic scheduling, agent coordination, review loops and hosted-CI ingestion are separate. The controller has no model, Git-publication or deployment action and starts no automatic retry. Declared check commands can have side effects, including network access; they require their own reviewed scope and authorization. Keep credentials out of definitions, argv and review evidence.
