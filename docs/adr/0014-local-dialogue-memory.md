# ADR 0014: Local dialogue import, review and export

- Date: 2026-10-15
- Status: accepted for offline stage one; automatic synchronization remains separate.

## Context and decision

The owner requested combining two ChatGPT/OpenRouter dialogues with conflict review and client exports, without automatic synchronization. AI-KIT has project facts and instruction selection but no conversation importer or live API adapter. Preserve that offline boundary and existing project documents.

Add `aikit memory import|merge|export` with text/Markdown, messages JSON and bounded ChatGPT mapping/branch support. Archive normalized selected messages with roles, timestamps and source hashes. Do not flatten alternative branches, fetch attachments, replay tools or promote imported roles into instructions.

Use deterministic keyed candidate extraction plus a human worksheet. All candidates start pending. Keep free prose as notes and explicitly acknowledge semantic limitations; do not simulate an LLM summarizer or independent fact verification. Review assigns keys, accepts/rejects claims and resolves alternatives with a reason. Preserve message references and reject stale worksheets. No provider, author or timestamp automatically settles a conflict.

Store immutable imports, content-addressed merges and exports under a marked private workspace. Preview changes, exclusively create files, allow identical reruns and refuse overwrites/linked paths. Scope normal Git/build/package exclusions to ai-kit/.memory; storing elsewhere requires explicit privacy configuration. Keep raw dialogue out of metrics and default instruction selection.

Export a quoted Markdown reference for ChatGPT and a user-message fragment for OpenRouter. Block unreviewed normal exports; explicit draft exports retain pending alternatives. Read source hashes and reconstruct the reviewed result before exporting. No API key, network dependency, paid call, model selection, live synchronization or action authorization is introduced.

## Consequences and verification

The workflow is reproducible without an account connection, and both clients can receive the same reference state. It requires human semantic review; arbitrary prose conflicts cannot be reliably inferred by a deterministic parser. Large or unsupported exports refuse explicitly. Files are not a hardened concurrent sandbox or a transactional multi-file database.

[Contract and tests](../DIALOGUE_MEMORY.md) define supported schemas, omissions, privacy, byte limits and recovery. [README](../guide/DIALOGUE_MEMORY.md) gives the import/review/export steps. Native upload/API execution and synchronization need their own implementation and authorization.
