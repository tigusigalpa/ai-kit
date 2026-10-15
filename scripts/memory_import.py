"""Normalize selected text dialogue branches without network access or tool replay."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import re

import memory_store as store

ROLES = {"user", "assistant", "system", "developer", "tool", "function", "unknown"}
MAX_MESSAGES = 4000


def text(value: object, label: str, *, maximum: int = 1024 * 1024) -> str:
    if not isinstance(value, str) or len(value) > maximum or "\x00" in value:
        raise ValueError("Invalid " + label)
    return value


def content(value: object) -> tuple[str, int]:
    if isinstance(value, str):
        return text(value, "message text"), 0
    if value is None:
        return "", 1
    if not isinstance(value, list):
        raise ValueError("Expected text or a list of content blocks")
    parts, omitted = [], 0
    for part in value:
        if isinstance(part, str):
            parts.append(text(part, "text part"))
        elif isinstance(part, dict):
            if part.get("type") in {"text", "input_text", "output_text"}:
                parts.append(text(part.get("text"), "text block"))
            else:
                omitted += 1
        else:
            raise ValueError("Invalid content part")
    return text("\n".join(parts), "combined message"), omitted


def normalize(rows: list[dict], *, source_format: str, raw: bytes,
              selection: dict | None = None, omitted: int = 0) -> dict:
    if not rows or len(rows) > MAX_MESSAGES:
        raise ValueError("Dialogue must contain 1-4000 messages")
    messages = []
    for number, row in enumerate(rows, 1):
        role = row.get("role")
        if not isinstance(role, str) or role not in ROLES:
            raise ValueError("Unknown message role")
        body, dropped = content(row.get("content"))
        omitted += dropped + int(bool(row.get("tool_calls")))
        timestamp = row.get("timestamp")
        if timestamp is not None and (type(timestamp) not in {str, int, float} or
                                      (type(timestamp) in {int, float} and not math.isfinite(timestamp))):
            raise ValueError("Invalid message timestamp")
        original_id = row.get("id")
        if original_id is not None:
            text(original_id, "original message identifier", maximum=256)
        messages.append({"id": f"m{number:04d}", "role": role, "text": body,
                         "original_id": original_id, "timestamp": timestamp})
    if not any(m["text"].strip() for m in messages):
        raise ValueError("Dialogue has no usable text")
    return {"schema": 1, "kind": "aikit-dialogue", "format": source_format,
            "source_sha256": hashlib.sha256(raw).hexdigest(), "selection": selection or {},
            "omitted_nontext": omitted, "messages": messages}


def chatgpt(value: object, conversation_id: str | None, branch: str | None) -> tuple[list[dict], dict]:
    conversations = value if isinstance(value, list) else [value]
    if not conversations or any(not isinstance(c, dict) for c in conversations):
        raise ValueError("Expected ChatGPT conversation object(s)")
    if conversation_id is not None:
        conversations = [c for c in conversations if c.get("id", c.get("conversation_id")) == conversation_id]
    if len(conversations) != 1:
        raise ValueError("Select exactly one conversation with --conversation-id")
    conversation = conversations[0]
    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict) or not mapping or len(mapping) > 20000:
        raise ValueError("Expected a bounded ChatGPT mapping")
    if any(not isinstance(key, str) or not isinstance(node, dict) for key, node in mapping.items()):
        raise ValueError("Invalid ChatGPT mapping nodes")
    leaf = branch if branch is not None else conversation.get("current_node")
    if leaf is None:
        parents = {n.get("parent") for n in mapping.values() if isinstance(n.get("parent"), str)}
        leaves = set(mapping) - parents
        if len(leaves) != 1:
            raise ValueError("Ambiguous ChatGPT branch; pass --branch")
        leaf = next(iter(leaves))
    if not isinstance(leaf, str) or leaf not in mapping:
        raise ValueError("Selected ChatGPT branch is missing")
    visited, nodes = set(), []
    node_id = leaf
    while node_id is not None:
        if not isinstance(node_id, str) or node_id not in mapping or node_id in visited:
            raise ValueError("Broken or cyclic ChatGPT parent chain")
        visited.add(node_id)
        node = mapping[node_id]
        if "parent" not in node:
            raise ValueError("Missing ChatGPT parent field")
        nodes.append((node_id, node))
        node_id = node.get("parent")
    rows = []
    for node_id, node in reversed(nodes):
        message = node.get("message")
        if message is None:
            continue
        if not isinstance(message, dict) or not isinstance(message.get("author"), dict):
            raise ValueError("Invalid ChatGPT message")
        payload = message.get("content")
        if not isinstance(payload, dict):
            raise ValueError("Invalid ChatGPT content object")
        if "parts" in payload:
            body = payload["parts"]
        elif isinstance(payload.get("text"), str):
            body = payload["text"]
        else:
            body = None  # Nontext-only messages stay visible as an omission.
        rows.append({"id": node_id, "role": message["author"].get("role"), "content": body,
                     "timestamp": message.get("create_time")})
    selected_id = conversation.get("id", conversation.get("conversation_id"))
    if selected_id is not None:
        text(selected_id, "conversation identifier", maximum=256)
    return rows, {"conversation_id": selected_id, "branch": leaf}


def transcript(value: str) -> list[dict]:
    """Recognize explicit role headers outside code fences; preserve unlabeled text."""
    rows, lines, role, fence = [], [], "unknown", None
    header = re.compile(r"^(?:#{1,6}\s+)?(user|assistant|system|developer|tool|human|chatgpt|\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c|\u0430\u0441\u0441\u0438\u0441\u0442\u0435\u043d\u0442):\s*(.*)$", re.I)
    for line in value.splitlines(keepends=True):
        match = header.fullmatch(line.rstrip("\r\n")) if fence is None else None
        if match:
            if lines:
                rows.append({"role": role, "content": "".join(lines)})
            label = match[1].casefold()
            role = {"human": "user", "chatgpt": "assistant", "\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c": "user",
                    "\u0430\u0441\u0441\u0438\u0441\u0442\u0435\u043d\u0442": "assistant"}.get(label, label)
            lines = [match[2] + ("\n" if line.endswith("\n") else "")] if match[2] else []
            marker = re.match(r"^\s*(`{3,}|~{3,})", match[2])
            if marker:
                fence = marker[1]
        else:
            lines.append(line)
            marker = re.match(r"^\s*(`{3,}|~{3,})", line)
            if marker:
                token = marker[1]
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
    if lines:
        rows.append({"role": role, "content": "".join(lines)})
    return rows


def load(path: Path, *, source_format: str = "auto", conversation_id: str | None = None,
         branch: str | None = None) -> dict:
    raw = store.read_bytes(path)
    if source_format == "auto":
        source_format = "json" if path.suffix.casefold() == ".json" else "text"
    if source_format == "text":
        if conversation_id is not None or branch is not None:
            raise ValueError("Conversation/branch selection requires ChatGPT JSON")
        return normalize(transcript(raw.decode("utf-8-sig")), source_format="text", raw=raw)
    value = store.decode(raw)
    is_mapping = isinstance(value, dict) and "mapping" in value
    is_collection = isinstance(value, list) and any(isinstance(c, dict) and "mapping" in c for c in value)
    if source_format == "chatgpt" or (source_format == "json" and (is_mapping or is_collection)):
        rows, selection = chatgpt(value, conversation_id, branch)
        return normalize(rows, source_format="chatgpt", raw=raw, selection=selection)
    if conversation_id is not None or branch is not None:
        raise ValueError("Conversation/branch selection requires ChatGPT JSON")
    rows = value.get("messages") if isinstance(value, dict) else value
    if not isinstance(rows, list) or any(not isinstance(m, dict) for m in rows):
        raise ValueError("Expected a messages array or an object containing messages")
    return normalize(rows, source_format="messages", raw=raw)
