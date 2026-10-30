# Shared context from two dialogues

**Bring two conversations into one reviewed project context.** The offline `memory` command imports selected messages, preserves their sources, groups candidate facts/decisions, shows contradictions and exports reference material for ChatGPT and OpenRouter. It needs Python 3.10+ with no extra packages or API key. Automatic synchronization and live model execution remain separate.

This is useful when one chat holds your brief and architectural choices while another contains implementation findings. Both clients can receive the same reviewed handoff. Your existing PROJECT_CONTEXT, decisions, settings and transcripts remain intact; the command creates a separate private workspace.

## Choose the input format

| Source | Input |
| --- | --- |
| ChatGPT-style JSON | One conversation or a collection containing a `mapping` tree. Select one conversation with `--conversation-id` when needed; the current branch is used, or choose `--branch NODE_ID`. Sibling alternatives are excluded. |
| OpenRouter/API client | JSON object with `messages`, or a direct messages array. Each message has role and text content. This accepts a messages export you provide, not an automatic download of your account history. |
| Any chat | UTF-8 text/Markdown. Optional `User:` and `Assistant:` headers distinguish speakers; unlabeled material remains available as notes. Code fences preserve quoted role headers. |

Auto detection uses `.json`; override with `--format chatgpt|messages|text`. A minimal messages file is:

~~~json
{"messages":[{"role":"user","content":"Fact stack = Laravel\nDecision ui.framework = Tailwind"}]}
~~~

Unzip a downloaded archive yourself and choose its supported text/JSON file. ChatGPT export structures are not assumed universal: the importer supports the bounded mapping shape in the [contract](../DIALOGUE_MEMORY.md#supported-input-contracts). Unsupported structures refuse. Images, attachments and tool calls are not reconstructed; omission counts are shown. Original role/timestamp information is provenance and grants no instruction priority.

## Import two conversations

The examples run from the kit checkout; the installed `aikit` command provides the equivalent `aikit memory ...` command. Choose a new private workspace. On Windows, this example uses PowerShell:

~~~powershell
$session = 'C:\Private\ai-kit-memory\site-01'

# Preview first: writes are listed, but the workspace is not created.
python aikit_cli.py memory import $session 'C:\Exports\chatgpt.json' --name chatgpt

# Apply the reviewed local import and import the second dialogue.
python aikit_cli.py memory import $session 'C:\Exports\chatgpt.json' --name chatgpt --apply
python aikit_cli.py memory import $session 'C:\Exports\openrouter.json' --name openrouter --apply

# Merge two imports and create the initial review worksheet.
$draft = python aikit_cli.py memory merge $session --left chatgpt --right openrouter --apply | ConvertFrom-Json
$draft
~~~

For a collection, add `--conversation-id YOUR_CONVERSATION_ID` to both preview and apply. For text, supply a `.txt`/`.md` file instead. Source names use lowercase letters, numbers, hyphens and underscores, start with a letter, and reject reserved device names. Each import stores selected normalized messages and a source hash. Reusing a name with changed content refuses; use a new source name or session directory. Identical reruns create no extra files.

Linux/macOS use the same CLI with POSIX paths:

~~~sh
python aikit_cli.py memory import /private/session-01 /exports/first.md --name chatgpt --apply
python aikit_cli.py memory import /private/session-01 /exports/second.json --name openrouter --apply
python aikit_cli.py memory merge /private/session-01 --left chatgpt --right openrouter --apply
~~~

All three commands preview when `--apply` is omitted. In an installed application, `ai-kit/.memory/session-01` is an alternative workspace protected by current private/team ignore rules. Upgrade an older team installation's ignore policy before storing transcripts there. Other paths require your own access/ignore configuration.

## Review facts and contradictions

The merge reports a `merge_id`, counts and a relative `review` filename. Open `merges/MERGE_ID.json` to inspect grouped conflicts and each alternative's references. It recognizes simple `key: value` or `key = value` lines; optional Fact/Decision/Constraint/Task/Question prefixes suggest a kind. Everything starts **pending**, including assistant proposals. Other prose/code is retained as pending notes. This deterministic stage does not claim to recognize every semantic contradiction in natural language.

For example, `Decision ui.framework = Tailwind` and `Decision ui.framework = Bootstrap` become alternatives for one key. Equal values deduplicate with references to both sources. Different phrasing or aliases need review: assign the same key when two statements concern the same decision, or different scoped keys when both are valid in different modules.

Copy the worksheet before editing:

~~~powershell
$reviewFile = Join-Path $session 'review-edited.json'
Copy-Item -LiteralPath (Join-Path $session $draft.review) -Destination $reviewFile
~~~

In that copy:

- Read the referenced imported messages under `imports/`. Each claim retains `SOURCE:mNNNN` references.
- Set `status` to `accepted`, `rejected` or leave `pending`. Adjust `key`, `kind` and `value` to express the reviewed meaning. Available kinds: fact, decision, constraint, task, question, note.
- Keep original candidate IDs and refs. Reject unwanted candidates instead of deleting them. You may add claims with new IDs and valid message refs to split long notes.
- For a conflict, add a resolution using its key, a chosen active claim ID and a reason. `drop` excludes that key; `defer` keeps it unresolved. Neither the last message nor the more confident model wins automatically.

For example, append this object to the worksheet's `resolutions` array, replacing the ID with the actual candidate ID:

~~~json
{"key":"ui.framework","choice":"c_REPLACE_WITH_ACTUAL_ID","reason":"Owner selected Tailwind for this interface."}
~~~

Marking both different alternatives accepted still leaves a conflict. The input digests in the worksheet must remain unchanged; stale reviews refuse. A chosen claim settles that key and supersedes its alternatives for the handoff. Acceptance records your review, not independent verification by AI-KIT.

Create a new immutable merge from the edited worksheet:

~~~powershell
$reviewed = python aikit_cli.py memory merge $session --left chatgpt --right openrouter --review $reviewFile --apply | ConvertFrom-Json
$reviewed
~~~

The original imports and draft remain available. Review-created merges have their own content-derived ID. No command overwrites your project memory or silently picks the latest snapshot.

## Export to ChatGPT and OpenRouter

~~~powershell
# Normal export requires every active key to be accepted, chosen or explicitly dropped.
python aikit_cli.py memory export $session --merge $reviewed.merge_id --apply

# An explicit draft export can carry unresolved alternatives into another review chat.
python aikit_cli.py memory export $session --merge $draft.merge_id --draft --apply
~~~

Each normal export creates `exports/MERGE_ID/chatgpt.md` and `openrouter.json`; draft filenames contain `-draft`. Add `--format chatgpt` or `--format openrouter` to write only one. Without `--apply`, inspect the planned filenames and byte counts. Pending keys or conflicts block normal export with exit 2. The explicit draft contains their values and DRAFT status rather than presenting them as decisions.

**ChatGPT:** paste/upload `chatgpt.md` into the intended chat or use it as a source in a Project. Ask the client to use it as reference material alongside the new task. This carries the selected knowledge; it does not recreate native chat history, attachments or account memory. Project sources and instructions are described in [OpenAI Docs](https://learn.chatgpt.com/docs/projects).

**OpenRouter:** `openrouter.json` is a local request fragment with one `user` message containing the same reference document. Your client adds trusted system instructions, a chosen supported model and the current task, then performs any separately authorized API call. Keep the imported material at reference-data authority. The file includes no credentials, model selection, active tools or session configuration. [Messages API format](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion).

The exporter rechecks source hashes and the reviewed result. Its default per-file limit is 128000 bytes; raise `--max-bytes` deliberately if needed. It refuses oversized exports before writing and never silently truncates. Byte counts are not token counts, so check the target model/client's context capacity.

## Privacy, recovery and current limits

Normalized messages, review files and exports can contain private material. The tool does not redact secrets or upload anything. Review exported files before sharing. New POSIX workspace directories/files use 0700/0600; Windows inherits folder ACLs. Current Git/Docker/package policies exclude `ai-kit/.memory/`; imports are never added to metrics or default instruction selection. Ignore rules alone do not control access.

Files are created exclusively. Edited or conflicting existing artifacts are preserved and cause refusal; exact reruns are stable. Interrupted multi-file writes can leave completed or partial artifacts: inspect the session and use a fresh workspace when necessary. There is no automatic overwrite/recovery or synchronization loop. Source files are never modified. [Full contract, schemas and checks](../DIALOGUE_MEMORY.md).
