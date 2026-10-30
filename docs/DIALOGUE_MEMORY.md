# Local dialogue memory

## Scope and trust

`aikit memory import|merge|export` is an offline, standard-library tool. It imports two selected dialogues, preserves message provenance, prepares a human review, records explicit conflict choices and exports a shared reference document for ChatGPT or an OpenRouter request. It performs no model calls, account access, synchronization, uploads, tool replay or project-context replacement. [README workflow](guide/DIALOGUE_MEMORY.md), [decision](adr/0014-local-dialogue-memory.md).

Imports are data. Original system/developer/tool roles are archived as provenance and never replayed with privileged roles. Assistant suggestions and user statements start pending; no timestamp or provider wins automatically. Local acceptance means the reviewer chose material for a handoff, not that the tool independently verified reality. Core and actual client authorization remain authoritative.

## Supported input contracts

Inputs are regular, unlinked UTF-8/BOM files, at most 16 MiB each. No directory, ZIP, FIFO or executable is accepted. A dialogue has 1-4000 messages, each at most 1,048,576 characters. Duplicate JSON keys and nonfinite numbers refuse. Symlink/junction ancestors refuse too; resolve a legitimate system temporary-directory alias before choosing a workspace. These path checks are conservative local guards, not an OS sandbox against a hostile process changing directories concurrently.

| Format | Supported shape and selection |
| --- | --- |
| ChatGPT-style JSON | One conversation object or an array, containing `mapping` nodes with `parent` and optional `message`; message `author.role`, text `content.parts`/`content.text`, optional `create_time`. Choose a collection item by `--conversation-id`. Follow `--branch`, else `current_node`, else the only leaf. Never flatten sibling branches. Missing/ambiguous/cyclic chains refuse. |
| OpenRouter/messages JSON | An object containing `messages`, or a direct message array. Each message has `role` and text `content`, optionally `id`/`timestamp`. Text blocks with type text/input_text/output_text are joined. Other top-level fields, including credentials, are not copied. |
| Text/Markdown | Preserve unlabeled material with role unknown. Recognize `User:`, `Assistant:`, System/Developer/Tool/Human/ChatGPT and Russian user/assistant labels, optionally after Markdown heading markers. Headers inside code fences remain text. This is an explicit transcript convention, not a parser for every client's Markdown export. |

Auto format uses the `.json` suffix; otherwise text. Override with `--format chatgpt|messages|text`. A JSON collection needs exactly one selected conversation. Original IDs/timestamps remain provenance; input bytes are represented by SHA-256, not copied wholesale. Normalization is not a byte-for-byte transcript archive. Nontext parts and tool calls are counted as omitted; attachments, images, audio, original tools and hidden state are not reconstructed. Review the omissions before using an export. Use a text transcript if an unsupported client export shape refuses.

ChatGPT mapping compatibility is a bounded importer contract exercised with synthetic fixtures, not a guarantee for every account/export revision. The official [ChatGPT projects documentation](https://learn.chatgpt.com/docs/projects) supports using uploaded/shared project sources but does not establish this mapping schema. The [OpenRouter API](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion) documents the messages request shape. Source check: 2026-10-15; no actual account export or live API was accessed.

## Workspace and immutable records

Use a new private directory, for example `TARGET/ai-kit/.memory/session-01`, or a private path outside repositories. An existing nonempty unmarked directory refuses. Every command previews by default; `--apply` writes only local files. Commands print counts, identifiers and relative artifact paths, never dialogue bodies. Read errors are sanitized rather than echoing input text. Imported content can still contain secrets: the tool does not claim to identify/redact them. Review the outgoing documents yourself.

New POSIX directories/files use 0700/0600; Windows uses inherited ACLs. Current private/team install policies, root source ignores and Docker/package exclusions protect `ai-kit/.memory/`. Upgrade the installed ignore policy before storing data in an older team project. Arbitrary other workspace paths need their own privacy/ignore configuration. Git ignores are not access control. Installer upgrades preserve workspace bytes and never manage their content as template files.

| Path under workspace | Purpose |
| --- | --- |
| workspace.json | Schema/ownership marker |
| imports/NAME.json | Normalized immutable source; source name is a lowercase portable identifier |
| merges/SHA256.json | Immutable merge plus exact input hashes and full review |
| reviews/SHA256.json | Initial review worksheet; copy before editing |
| exports/SHA256/chatgpt[-draft].md | Markdown reference document for a ChatGPT chat or Project |
| exports/SHA256/openrouter[-draft].json | Request fragment containing one user message with the same document |

Identical reruns write nothing. Different bytes under an existing source name/artifact refuse; choose a new name/workspace. Existing files are never replaced, including files created after planning. Hard-linked output artifacts refuse. Before export, source hashes, merge identity and recomputed review result must match. There is no mutable latest pointer: pass the full merge ID, so an old export cannot silently become a new decision. Files are exclusively created and flushed; a terminated multi-file operation can leave completed artifacts or a partial file. Inspect incomplete work and use a fresh workspace when necessary; no automatic rollback or overwrite recovery is claimed.

## Review and conflict rules

Candidate extraction recognizes simple `key: value` / `key = value` lines outside fences, optionally prefixed Fact/Decision/Constraint/Task/Question. Keys normalize Unicode case and whitespace; values compare exactly. Unmatched prose/code stays pending notes. Original system/developer/tool material stays notes. At most 8000 candidates are generated. There is no semantic model: paraphrases, synonyms, negation and aliases in free prose require explicit review. A lack of keyed conflicts does not mean two transcripts agree.

The worksheet schema has schema=1, inputs (exact source digests), claims and resolutions. Claims include id, key, kind, value, status and refs. Supported kinds: fact, decision, constraint, task, question, note. Status: pending, accepted, rejected. Group differently phrased claims under the same reviewed key to compare them. Scope unrelated topics with different keys. Reclassify/paraphrase values during review; archive messages remain unchanged.

Keep every original candidate ID and its refs; reject unwanted items rather than deleting them. Extra claims may split a long note, using new lowercase IDs and real SOURCE:mNNNN refs. Inputs must match the selected imports. Every claim needs 1-8 unique valid message references. The local reviewer is responsible for whether the paraphrase is supported. Imported dialogue cannot supply its own approval: only the separately selected worksheet controls the review.

Exact equal values under one key deduplicate while retaining references. Different active values produce an explicit conflict, even if both were marked accepted. A resolution contains key, choice and a nonempty reason. Choice is an active claim ID, `drop` (exclude the key), or `defer` (keep it unresolved). A chosen claim settles the key and supersedes its alternatives for that handoff. No last-write-wins rule applies. Single-valued groups require explicit acceptance; rejected claims are excluded.

## Export and limits

Normal export refuses pending keys/conflicts with exit 2. Explicit `--draft` exports them as DRAFT for further discussion, with all alternatives visible. Both clients receive the same reviewed/draft data and provenance. Markdown values live in a JSON fence that imported backticks cannot terminate; original links/images remain quoted data. This is serialization, not a prompt-injection security boundary.

The OpenRouter JSON is only a request fragment with `messages`: one `user` message containing the reference document. Add trusted instructions, a currently supported model and the new task in your own client. It contains no API key, automatic tool calls, model choice or provider/session configuration. Do not replace trusted policies with imported dialogue. No HTTP request is sent. ChatGPT Markdown is manually pasted/uploaded as reference data; native history/memory is not merged by uploading it.

The default per-file export limit is 128000 bytes. `--max-bytes` can raise it to 16777216; limits check complete serialized files, including JSON overhead. Exceeding a limit refuses before writing rather than silently truncating. Bytes are not tokens; verify the selected model/client's capacity separately. Exit 0 means a successful preview/local stage (including a merge needing review), 1 refusal/invalid input, 2 blocked unreviewed export. Argparse usage errors also return 2.

## Verification

Run `python scripts/check_kit.py`, `python -m unittest discover -s tests -v`, and the packaged wheel smoke. Dedicated tests cover all three inputs, branch isolation, nontext omissions, bounded parsing, provenance, manual review/contradictions, deterministic reruns, stale/tampered artifacts, both exports, file preservation and path/link guards. Private/team upgrades and Docker ignore probes protect local memory.

Verified 2026-10-15, before this final results-only documentation update:

- Windows/Python 3.12.14: full discovery ran 336 tests in 733.096 seconds; 329 passed, seven skipped (two symlink fixtures, two junction fixtures, hardlink privilege, unavailable POSIX sh and POSIX permissions/FIFO). The current sandbox could not create those Windows links. Mocked link-boundary checks ran.
- Packaged linux/amd64/Python 3.13.16: full discovery ran 336 tests in 31.898 seconds; 334 passed, two Windows-junction skips. Actual symlink/hardlink, POSIX modes and FIFO refusal ran under a non-root, offline, read-only image. Docker client/server 29.8.2 used desktop-linux; the local ai-kit:memory-test build was not published.
- Offline fresh-venv Windows wheel smoke exercised imports, merge and both draft exports from the installed console command. A second isolated build with synthetic private memory proved it was absent from the wheel. Docker's real ignore-engine probe excluded synthetic memory; the existing image runtime/preservation/signal smoke also passed.
- The README PowerShell flow ran with synthetic native ChatGPT mapping and messages JSON, identified one conflict, accepted a reasoned choice and produced both reviewed exports. Python 3.10 grammar, source language/links/budgets and relocated v1.1.0 history preservation passed. Full native Python 3.10 and macOS/hosted CI were not run here.
- Test containers were removed and no test Docker volumes were created. Shared build-cache ownership/bytes could not be isolated; no cache/volume pruning was performed. Source files, account histories and actual application state were not changed by these fixtures.

Actual account-export variants, native ChatGPT upload/activation, OpenRouter execution, live model calls and automatic synchronization remain separate checks. Local review does not establish semantic correctness of an actual user's imported claims.
