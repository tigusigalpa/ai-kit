"""Report MCP servers configured in a project's client files for review; reads only and prints no secret values."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 has no TOML parser in the standard library.
    tomllib = None

# Project-scoped MCP files and the key holding servers, from each client's documentation (checked 2026-10-30).
PROJECT_FILES = (
    ("claude", ".mcp.json", "mcpServers"),
    ("cursor", ".cursor/mcp.json", "mcpServers"),
    ("copilot", ".vscode/mcp.json", "servers"),
    ("gemini", ".gemini/settings.json", "mcpServers"),
    ("codex", ".codex/config.toml", "mcp_servers"),
    ("roo", ".roo/mcp.json", "mcpServers"),
    ("kimi", ".kimi-code/mcp.json", "mcpServers"),
)
USER_LEVEL_NOTE = ("Legacy Windsurf and Cline user-level MCP files and Devin (Windsurf) configuration "
                   "are not inventoried here; Aider has no MCP configuration. This report reads only "
                   "the listed project client files.")
SENSITIVE = re.compile(r"key|token|secret|passw|auth|credential|bearer|cookie|session", re.I)
REFERENCE = re.compile(r"\$\{[^}]+\}|\$[A-Za-z_][A-Za-z0-9_]*|%[A-Za-z_][A-Za-z0-9_]*%")
OPAQUE = re.compile(r"(?=[A-Za-z0-9_+=-]*\d)(?=[A-Za-z0-9_+=-]*[A-Za-z])[A-Za-z0-9_+=-]{20,}")
SECRET_FIELDS = ("clientSecret", "CLIENT_SECRET", "client_secret")
HELPER_FIELDS = ("headersHelper", "http_headers_helper")
APPROVAL_FIELDS = ("trust", "alwaysAllow", "autoApprove", "default_tools_approval_mode")
TOOL_FIELDS = ("includeTools", "excludeTools", "disabledTools", "enabled_tools", "disabled_tools",
               "enabledTools")
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
CODEX_SERVER = re.compile(r'^\s*\[\s*mcp_servers\s*\.\s*("(?:[^"\\]|\\.)*"|[A-Za-z0-9_-]+)\s*\]\s*(?:#.*)?$', re.M)


def strip_jsonc(text: str) -> str:
    """Remove comments and trailing commas outside strings (VS Code reads mcp.json as JSONC)."""
    out, index, quoted = [], 0, False
    while index < len(text):
        char = text[index]
        if quoted:
            out.append(char)
            if char == "\\" and index + 1 < len(text):
                out.append(text[index + 1])
                index += 1
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
            out.append(char)
        elif text.startswith("//", index):
            index = text.find("\n", index)
            if index < 0:
                break
            continue
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)
            index = len(text) if end < 0 else end + 2
            continue
        else:
            out.append(char)
        index += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def shown(value) -> str:
    """Show a value only when it is made of references; otherwise say a literal is hidden."""
    if not isinstance(value, str):
        return "<non-string>"
    rest = REFERENCE.sub("", value)
    if REFERENCE.search(value) and not re.search(r"[A-Za-z0-9_+/=-]{12,}", rest):
        return value
    return "<literal hidden>" if value else ""


def safe_args(args) -> list[str]:
    result, hide_next = [], False
    for arg in args if isinstance(args, list) else []:
        text = str(arg)
        if hide_next and not text.startswith("-"):
            result.append(shown(text) if REFERENCE.search(text) else "<hidden>")
            hide_next = False
            continue
        hide_next = False
        if text.startswith("-") and "=" in text:
            name, _, value = text.partition("=")
            result.append(name + "=" + (shown(value) if SENSITIVE.search(name) else value))
        elif text.startswith("-"):
            result.append(text)
            hide_next = bool(SENSITIVE.search(text))
        elif OPAQUE.fullmatch(text) or (SENSITIVE.search(text) and "=" in text):
            result.append("<hidden>")
        else:
            result.append(text)
    return result


def safe_url(value) -> tuple[str | None, list[str]]:
    if not isinstance(value, str) or not value:
        return None, []
    notes = []
    if REFERENCE.search(value):
        return shown(value), notes
    parts = urlsplit(value)
    host = parts.hostname or ""
    if parts.username or parts.password:
        notes.append("credentials in URL")
    if parts.scheme == "http" and host not in LOCAL_HOSTS:
        notes.append("plain HTTP to a remote host")
    netloc = host + (f":{parts.port}" if parts.port else "")
    return f"{parts.scheme}://{netloc}{parts.path}" + ("?<hidden>" if parts.query else ""), notes


def transport(client: str, entry: dict) -> str:
    explicit = entry.get("type") or entry.get("transport")
    if isinstance(explicit, str):
        return explicit
    if entry.get("httpUrl"):
        return "http"
    if entry.get("url") or entry.get("serverUrl"):
        return "sse" if client == "gemini" else "http"
    return "stdio" if entry.get("command") else "unknown"


def mapping(entry: dict, name: str) -> dict:
    value = entry.get(name)
    return value if isinstance(value, dict) else {}


def describe(client: str, relative: str, name: str, entry: dict, tracked: bool | None) -> tuple[dict, list[str]]:
    where = f"{relative}: server {name}"
    warnings: list[str] = []
    url, url_notes = safe_url(entry.get("httpUrl") or entry.get("url") or entry.get("serverUrl"))
    warnings.extend(f"{where}: {note}" for note in url_notes)
    record = {"client": client, "file": relative, "name": name, "transport": transport(client, entry),
              "tracked": tracked}
    if isinstance(entry.get("command"), str):
        record["command"] = entry["command"]
        record["args"] = safe_args(entry.get("args"))
    if url:
        record["url"] = url
    for field in ("env", "headers", "http_headers"):
        values = mapping(entry, field)
        if values:
            record[field] = {key: shown(value) for key, value in values.items()}
            for key, value in values.items():
                if record[field][key] == "<literal hidden>" and SENSITIVE.search(str(key)):
                    warnings.append(f"{where}: {field} {key} holds a literal value"
                                    + (" in a Git-tracked file" if tracked else "")
                                    + "; reference an environment variable instead")
    references = {}
    for field in ("env_vars", "bearer_token_env_var", "bearerTokenEnvVar", "env_http_headers", "envFile"):
        if entry.get(field) not in (None, "", [], {}):
            references[field] = entry[field]
    if references:
        record["references"] = references
    secrets = [field for field in SECRET_FIELDS
               if entry.get(field) or mapping(entry, "oauth").get(field) or mapping(entry, "auth").get(field)]
    for field in secrets:
        warnings.append(f"{where}: OAuth {field} is stored inline; keep client secrets out of project files")
    helpers = {field: entry[field] for field in HELPER_FIELDS if entry.get(field)}
    if helpers:
        record["helpers"] = helpers
    approval = {field: entry[field] for field in APPROVAL_FIELDS if field in entry}
    if approval:
        record["approval"] = approval
        if approval.get("trust") is True or approval.get("alwaysAllow") or approval.get("autoApprove"):
            warnings.append(f"{where}: tools may run without confirmation ({', '.join(approval)}); review them")
    tools = {field: entry[field] for field in TOOL_FIELDS if field in entry}
    if tools:
        record["tools"] = tools
    for field in ("disabled", "enabled"):
        if isinstance(entry.get(field), bool):
            record[field] = entry[field]
    return record, warnings


def tracked_files(target: Path, relatives: list[str]) -> set[str] | None:
    git = shutil.which("git")
    if not git or not relatives:
        return None
    try:
        result = subprocess.run([git, "-C", str(target), "ls-files", "-z", "--", *relatives],
                                capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return {name for name in result.stdout.decode("utf-8", "replace").split("\0") if name}


def load_servers(client: str, path: Path, key: str) -> tuple[dict, list[str]]:
    text = path.read_text(encoding="utf-8")
    if client != "codex":
        data = json.loads(strip_jsonc(text))
        servers = data.get(key) if isinstance(data, dict) else None
        return (servers if isinstance(servers, dict) else {}), []
    if tomllib is None:
        names = [json.loads(name) if name.startswith('"') else name for name in CODEX_SERVER.findall(text)]
        note = ("Python 3.10 cannot parse TOML: server names only; review the file manually"
                if names else "")
        return {name: {} for name in names}, [note] if note else []
    servers = tomllib.loads(text).get(key)
    return (servers if isinstance(servers, dict) else {}), []


def report(target: Path) -> dict:
    target = target.absolute()
    if install.is_link(target):
        raise ValueError("Refusing a linked target root")
    target = target.resolve()
    if not target.is_dir():
        raise ValueError("Target must be a directory")
    found = [(client, relative, key, install.readable_project_file(target, relative))
             for client, relative, key in PROJECT_FILES]
    present = [(client, relative, key, path) for client, relative, key, path in found if path is not None]
    tracked = tracked_files(target, [relative for _, relative, _, _ in present])
    servers, warnings, files = [], [], []
    for client, relative, key, path in present:
        is_tracked = None if tracked is None else relative in tracked
        try:
            entries, notes = load_servers(client, path, key)
        except (OSError, UnicodeError, ValueError) as exc:
            warnings.append(f"{relative}: cannot be read as {client} MCP configuration ({exc}); review it manually")
            files.append({"client": client, "file": relative, "servers": None, "tracked": is_tracked})
            continue
        warnings.extend(f"{relative}: {note}" for note in notes)
        files.append({"client": client, "file": relative, "servers": len(entries), "tracked": is_tracked})
        for name, entry in sorted(entries.items()):
            record, issues = describe(client, relative, str(name), entry if isinstance(entry, dict) else {},
                                      is_tracked)
            servers.append(record)
            warnings.extend(issues)
        if client == "copilot":
            data = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
            for item in data.get("inputs", []) if isinstance(data, dict) else []:
                if isinstance(item, dict) and item.get("password") and item.get("default"):
                    warnings.append(f"{relative}: password input {item.get('id')} has a default value; remove it")
    return {"target": str(target), "files": files, "servers": servers, "warnings": warnings,
            "notes": [USER_LEVEL_NOTE, "The report lists configuration only; it starts, contacts and "
                      "authorizes no server. Review it against ai-kit/MCP.md."]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    report_parser = commands.add_parser("report", help="List project MCP servers without secret values")
    report_parser.add_argument("target", type=Path)
    args = parser.parse_args(argv)
    try:
        result = report(args.target)
    except (OSError, ValueError) as exc:
        print(json.dumps({"errors": [str(exc)]}, indent=2))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
