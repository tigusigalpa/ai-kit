"""Report project MCP servers for review without leaking secret values."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import aikit_cli
import mcp_report

SECRETS = ("ghp_abcdefghij0123456789KLMNOP", "sk-live-0123456789abcdef", "hunter2-password-value",
           "urlpass", "query-secret-123", "client-secret-value", "codex-literal-token-999", "Bearer abc1234567890xyz")


class McpReportTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="ai-kit-mcp-")
        self.addCleanup(temp.cleanup)
        self.project = Path(temp.name) / "app"
        self.project.mkdir()

    def write(self, relative: str, text: str) -> None:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def write_json(self, relative: str, data: dict) -> None:
        self.write(relative, json.dumps(data, indent=2) + "\n")

    def servers(self, result: dict) -> dict:
        return {(item["client"], item["name"]): item for item in result["servers"]}

    def fixture(self) -> None:
        self.write_json(".mcp.json", {"mcpServers": {
            "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github", "--api-key",
                                                  SECRETS[1], "--token=" + SECRETS[2], SECRETS[0]],
                       "env": {"GITHUB_TOKEN": SECRETS[0], "LOG_LEVEL": "debug", "API_KEY": "${API_KEY}"}},
            "remote": {"type": "http", "url": f"https://user:{SECRETS[3]}@api.example.com/mcp?key={SECRETS[4]}",
                       "headers": {"Authorization": "Bearer ${API_TOKEN}", "X-Api-Key": SECRETS[1]},
                       "oauth": {"clientId": "app"}}}})
        self.write(".vscode/mcp.json", """{
  // VS Code reads this file as JSONC.
  "inputs": [{"type": "promptString", "id": "token", "password": true, "default": "%s"},],
  "servers": {
    "files": {"type": "stdio", "command": "node", "args": ["server.js"], "env": {"TOKEN": "${input:token}"}},
  },
}
""" % SECRETS[2])
        self.write_json(".gemini/settings.json", {"mcpServers": {
            "docs": {"httpUrl": "https://docs.example.com/mcp", "trust": True,
                     "oauth": {"enabled": True, "clientSecret": SECRETS[5]}},
            "events": {"url": "http://events.example.com/sse"}}})
        self.write_json(".roo/mcp.json", {"mcpServers": {
            "local": {"type": "sse", "url": "http://localhost:8080/sse", "alwaysAllow": ["read"], "disabled": True}}})
        self.write_json(".kimi-code/mcp.json", {"mcpServers": {
            "search": {"url": "https://search.example.com/mcp", "bearerTokenEnvVar": "SEARCH_TOKEN"}}})
        self.write(".codex/config.toml", """model = "example"

[mcp_servers.context]
command = "npx"
args = ["-y", "@example/context-mcp"]
env = { "CONTEXT_API_KEY" = "%s" }
enabled_tools = ["lookup"]

[mcp_servers."remote.docs"]
url = "https://remote.example.com/mcp"
bearer_token_env_var = "REMOTE_TOKEN"
""" % SECRETS[6])
        self.write(".cursor/mcp.json", "{ not json")

    def test_report_lists_servers_without_secret_values(self):
        self.fixture()
        result = mcp_report.report(self.project)
        text = json.dumps(result)
        for secret in SECRETS:
            self.assertNotIn(secret, text)
        servers = self.servers(result)
        github = servers[("claude", "github")]
        self.assertEqual(github["transport"], "stdio")
        self.assertEqual(github["args"], ["-y", "@modelcontextprotocol/server-github", "--api-key", "<hidden>",
                                          "--token=<literal hidden>", "<hidden>"])
        self.assertEqual(github["env"], {"GITHUB_TOKEN": "<literal hidden>", "LOG_LEVEL": "<literal hidden>",
                                         "API_KEY": "${API_KEY}"})
        remote = servers[("claude", "remote")]
        self.assertEqual((remote["transport"], remote["url"]), ("http", "https://api.example.com/mcp?<hidden>"))
        self.assertEqual(remote["headers"]["Authorization"], "Bearer ${API_TOKEN}")
        self.assertEqual(servers[("copilot", "files")]["env"], {"TOKEN": "${input:token}"})
        self.assertEqual(servers[("gemini", "docs")]["transport"], "http")
        self.assertEqual(servers[("gemini", "events")]["transport"], "sse")
        self.assertEqual(servers[("roo", "local")]["disabled"], True)
        self.assertEqual(servers[("kimi", "search")]["references"], {"bearerTokenEnvVar": "SEARCH_TOKEN"})
        warnings = "\n".join(result["warnings"])
        for expected in ("env GITHUB_TOKEN holds a literal value", "headers X-Api-Key holds a literal value",
                         "credentials in URL", "password input token has a default value",
                         "OAuth clientSecret is stored inline", "tools may run without confirmation (trust)",
                         "server events: plain HTTP to a remote host", "tools may run without confirmation (alwaysAllow)",
                         ".cursor/mcp.json: cannot be read"):
            self.assertIn(expected, warnings)
        self.assertNotIn("LOG_LEVEL holds", warnings)
        self.assertNotIn("server local: plain HTTP", warnings)
        files = {item["file"]: item for item in result["files"]}
        self.assertIsNone(files[".cursor/mcp.json"]["servers"])
        self.assertTrue(any("user-level" in note for note in result["notes"]))

    @unittest.skipIf(mcp_report.tomllib is None, "tomllib requires Python 3.11 or later")
    def test_codex_tables_are_parsed_with_tomllib(self):
        self.fixture()
        servers = self.servers(mcp_report.report(self.project))
        context = servers[("codex", "context")]
        self.assertEqual(context["args"], ["-y", "@example/context-mcp"])
        self.assertEqual(context["env"], {"CONTEXT_API_KEY": "<literal hidden>"})
        self.assertEqual(context["tools"], {"enabled_tools": ["lookup"]})
        docs = servers[("codex", "remote.docs")]
        self.assertEqual((docs["transport"], docs["references"]), ("http", {"bearer_token_env_var": "REMOTE_TOKEN"}))

    def test_codex_names_are_listed_without_a_toml_parser(self):
        self.fixture()
        with mock.patch.object(mcp_report, "tomllib", None):
            result = mcp_report.report(self.project)
        servers = self.servers(result)
        self.assertEqual(servers[("codex", "context")]["transport"], "unknown")
        self.assertIn(("codex", "remote.docs"), servers)
        self.assertTrue(any("cannot parse TOML" in warning for warning in result["warnings"]))
        self.assertNotIn(SECRETS[6], json.dumps(result))

    def test_empty_project_reports_no_servers(self):
        result = mcp_report.report(self.project)
        self.assertEqual((result["files"], result["servers"], result["warnings"]), ([], [], []))

    @unittest.skipUnless(shutil.which("git"), "Git is required")
    def test_reports_git_tracking(self):
        self.write_json(".mcp.json", {"mcpServers": {"a": {"command": "a"}}})
        self.write_json(".roo/mcp.json", {"mcpServers": {"b": {"command": "b"}}})
        git = shutil.which("git")
        for args in (["init", "-q"], ["add", ".mcp.json"]):
            subprocess.run([git, "-C", str(self.project), *args], check=True, capture_output=True)
        files = {item["file"]: item["tracked"] for item in mcp_report.report(self.project)["files"]}
        self.assertEqual(files, {".mcp.json": True, ".roo/mcp.json": False})

    def test_linked_config_outside_project_is_skipped(self):
        outside = self.project.parent / "outside.json"
        outside.write_text(json.dumps({"mcpServers": {"x": {"command": "x"}}}), encoding="utf-8")
        try:
            (self.project / ".mcp.json").symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable")
        self.assertEqual(mcp_report.report(self.project)["files"], [])

    def test_cli_reports_and_refuses_missing_target(self):
        self.write_json(".mcp.json", {"mcpServers": {"a": {"command": "a"}}})
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(aikit_cli.main(["mcp", "report", str(self.project)]), 0)
        self.assertEqual(json.loads(output.getvalue())["servers"][0]["name"], "a")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(aikit_cli.main(["mcp", "report", str(self.project / "missing")]), 1)


if __name__ == "__main__":
    unittest.main()
