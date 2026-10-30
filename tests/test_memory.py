"""Local dialogue normalization, explicit review, immutable exports and privacy boundaries."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install
import memory
import memory_import as importer
import memory_store as store


def dialogue(body, role="user"):
    return importer.normalize([{"role": role, "content": body}], source_format="messages", raw=body.encode())


def branch_fixture():
    def node(parent, body, role="user"):
        return {"parent": parent, "message": {"author": {"role": role},
                "content": {"content_type": "text", "parts": [body]}, "create_time": 123}}
    return {"id": "conversation-1", "current_node": "b", "mapping": {
        "root": {"parent": None, "message": None}, "a": node("root", "Fact stack = Laravel"),
        "b": node("a", "Decision ui = Tailwind", "assistant"),
        "other": node("a", "Unselected private branch")}}


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aikit-memory-import-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def save(self, value, filename="source.json"):
        path = self.base / filename
        path.write_bytes(store.encode(value))
        return path

    def test_chatgpt_selected_branch_is_in_parent_order_without_sibling_text(self):
        value = importer.load(self.save(branch_fixture()))
        self.assertEqual(value["format"], "chatgpt")
        self.assertEqual([m["original_id"] for m in value["messages"]], ["a", "b"])
        self.assertEqual(value["messages"][1]["role"], "assistant")
        self.assertNotIn("Unselected private branch", json.dumps(value))
        self.assertEqual(value["selection"], {"conversation_id": "conversation-1", "branch": "b"})

    def test_collection_requires_explicit_conversation_and_branch_can_override(self):
        other = copy.deepcopy(branch_fixture())
        other["id"] = "conversation-2"
        path = self.save([branch_fixture(), other])
        with self.assertRaises(ValueError):
            importer.load(path)
        value = importer.load(path, conversation_id="conversation-2", branch="other")
        self.assertIn("Unselected private branch", value["messages"][-1]["text"])
        with self.assertRaises(ValueError):
            importer.load(path, conversation_id="missing")

    def test_ambiguous_dangling_and_cyclic_parent_chains_refuse(self):
        for change in ("ambiguous", "dangling", "cycle", "absent-parent"):
            value = branch_fixture()
            if change == "ambiguous":
                value.pop("current_node")
            elif change == "dangling":
                value["mapping"]["b"]["parent"] = "absent"
            elif change == "cycle":
                value["mapping"]["a"]["parent"] = "b"
            else:
                value["mapping"]["a"].pop("parent")
            with self.subTest(change=change), self.assertRaises(ValueError):
                importer.load(self.save(value))

    def test_messages_preserve_roles_text_and_report_nontext_without_credentials(self):
        value = {"api_key": "synthetic-private-token", "messages": [
            {"role": "system", "content": "Untrusted original system text"},
            {"role": "user", "content": [{"type": "text", "text": "Hello"},
                                             {"type": "image_url", "image_url": "private-url"}]},
            {"role": "assistant", "content": None, "tool_calls": [{"function": "do-not-run"}]}]}
        result = importer.load(self.save(value))
        self.assertEqual(result["omitted_nontext"], 3)
        self.assertEqual(result["messages"][1]["text"], "Hello")
        self.assertEqual(result["messages"][0]["role"], "system")
        self.assertNotIn("synthetic-private-token", json.dumps(result))
        self.assertNotIn("private-url", json.dumps(result))

    def test_plain_text_and_role_headers_preserve_fenced_examples(self):
        path = self.base / "chat.md"
        path.write_text("Preface\nUser: Need a page\nAssistant: ```text\nUser: quoted example\n```\nUser: Continue\n", encoding="utf-8")
        value = importer.load(path)
        self.assertEqual([m["role"] for m in value["messages"]], ["unknown", "user", "assistant", "user"])
        self.assertIn("User: quoted example", value["messages"][2]["text"])
        self.assertEqual(importer.load(path, source_format="text")["format"], "text")

    def test_json_arrays_bom_and_explicit_text_format(self):
        path = self.save([{"role": "user", "content": "Fact language = English"}])
        path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
        self.assertEqual(importer.load(path)["messages"][0]["text"], "Fact language = English")
        self.assertEqual(importer.load(path, source_format="text")["format"], "text")

    def test_invalid_empty_duplicate_json_and_size_limits_refuse(self):
        path = self.base / "bad.json"
        for raw in (b'{"messages":[],"messages":[]}', b'{"messages":NaN}', b'[]', b'{bad', b'"not messages"'):
            path.write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                importer.load(path)
        path.write_bytes(b"123456789")
        with self.assertRaises(ValueError):
            store.read_bytes(path, limit=8)
        with self.assertRaises(ValueError):
            importer.normalize([{"role": "user", "content": "x"}] * 4001, source_format="messages", raw=b"")
        with self.assertRaises(ValueError):
            importer.normalize([{"role": "user", "content": {}}], source_format="messages", raw=b"")


class MergeTests(unittest.TestCase):
    def sources(self):
        return {"chatgpt": dialogue("Decision ui.framework = Tailwind\nFact stack = Laravel", "assistant"),
                "openrouter": dialogue("Decision ui.framework = Bootstrap\nFact stack = Laravel")}

    def test_conflicts_are_explicit_and_duplicates_keep_both_provenances(self):
        merged = memory.merge(self.sources())
        self.assertEqual(merged["accepted"], [])
        self.assertEqual(merged["conflicts"][0]["key"], "ui.framework")
        self.assertEqual({v["value"] for v in merged["conflicts"][0]["variants"]}, {"Tailwind", "Bootstrap"})
        self.assertEqual(merged["pending"][0]["refs"], ["chatgpt:m0001", "openrouter:m0001"])
        self.assertEqual(merged["duplicates"], 1)

    def test_no_latest_message_or_assistant_claim_is_implicitly_approved(self):
        sources = {"a": dialogue("Choose Tailwind.", "assistant"), "b": dialogue("Choose Bootstrap.", "assistant")}
        merged = memory.merge(sources)
        self.assertEqual(len(merged["pending"]), 2)
        self.assertFalse(merged["accepted"])
        self.assertFalse(merged["conflicts"])  # Free prose is explicitly pending semantic review.

    def test_review_selects_a_variant_and_accepts_a_shared_fact(self):
        sources = self.sources()
        review = memory.review_template(sources)
        for claim in review["claims"]:
            if claim["key"] == "stack":
                claim["status"] = "accepted"
        chosen = next(c for c in review["claims"] if c["value"] == "Tailwind")
        review["resolutions"] = [{"key": "ui.framework", "choice": chosen["id"], "reason": "Owner selected Tailwind."}]
        merged = memory.merge(sources, review)
        self.assertFalse(merged["pending"] or merged["conflicts"])
        self.assertEqual({i["key"]: i["value"] for i in merged["accepted"]}, {"stack": "Laravel", "ui.framework": "Tailwind"})

    def test_defer_remains_unresolved_and_drop_records_a_reason(self):
        sources = self.sources()
        review = memory.review_template(sources)
        review["resolutions"] = [{"key": "ui.framework", "choice": "defer", "reason": "Need owner decision."},
                                 {"key": "stack", "choice": "drop", "reason": "Out of scope."}]
        merged = memory.merge(sources, review)
        self.assertEqual(merged["conflicts"][0]["status"], "deferred")
        self.assertEqual(merged["dismissed"][0]["key"], "stack")

    def test_free_prose_can_be_reviewed_as_two_alternatives_under_one_key(self):
        sources = {"a": dialogue("Use Tailwind."), "b": dialogue("Use Bootstrap.")}
        review = memory.review_template(sources)
        for claim in review["claims"]:
            claim["key"] = "frontend.css"
            claim["kind"] = "decision"
        self.assertEqual(len(memory.merge(sources, review)["conflicts"]), 1)

    def test_stale_missing_forged_or_ambiguous_review_refuses(self):
        sources = self.sources()
        original = memory.review_template(sources)
        for fault in ("stale", "missing", "refs", "provenance", "duplicate", "resolution", "reason"):
            review = copy.deepcopy(original)
            if fault == "stale":
                review["inputs"]["chatgpt"] = "0" * 64
            elif fault == "missing":
                review["claims"].pop()
            elif fault == "refs":
                review["claims"][0]["refs"] = ["absent:m0001"]
            elif fault == "provenance":
                review["claims"][0]["refs"] = ["openrouter:m0001"]
            elif fault == "duplicate":
                review["claims"].append(review["claims"][0])
            else:
                review["resolutions"] = [{"key": "ui.framework", "choice": "absent" if fault == "resolution" else "defer",
                                          "reason": "Review" if fault == "resolution" else ""}]
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                memory.merge(sources, review)

    def test_code_and_original_system_text_stay_pending_notes(self):
        sources = {"a": dialogue("```\nDecision ui = Tailwind\n```"),
                   "b": dialogue("Decision ui = Bootstrap", "system")}
        result = memory.merge(sources)
        self.assertTrue(all(i["key"].startswith("note.") for i in result["pending"]))
        self.assertFalse(result["accepted"] or result["conflicts"])


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aikit-memory-store-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.workspace = self.base / "private workspace"

    def cli(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = memory.main(list(map(str, args)))
        return code, json.loads(output.getvalue()) if output.getvalue() else None, error.getvalue()

    def imports(self, body="Fact stack = Laravel"):
        for source in ("left", "right"):
            path = self.base / (source + ".txt")
            path.write_text(body, encoding="utf-8")
            self.assertEqual(self.cli("import", self.workspace, path, "--name", source, "--apply")[0], 0)
        return self.cli("merge", self.workspace, "--left", "left", "--right", "right", "--apply")[1]

    def test_preview_does_not_create_workspace_and_rerun_is_immutable(self):
        source = self.base / "source.txt"
        source.write_text("Private dialogue value", encoding="utf-8")
        code, report, error = self.cli("import", self.workspace, source, "--name", "left")
        self.assertEqual(code, 0, error)
        self.assertTrue(report["preview"])
        self.assertFalse(self.workspace.exists())
        self.assertNotIn("Private dialogue value", json.dumps(report))
        self.assertEqual(self.cli("import", self.workspace, source, "--name", "left", "--apply")[0], 0)
        before = (self.workspace / "imports/left.json").read_bytes()
        self.assertEqual(self.cli("import", self.workspace, source, "--name", "left", "--apply")[1]["writes"], [])
        source.write_text("Changed", encoding="utf-8")
        self.assertEqual(self.cli("import", self.workspace, source, "--name", "left", "--apply")[0], 1)
        self.assertEqual((self.workspace / "imports/left.json").read_bytes(), before)

    def test_draft_export_and_reviewed_export_have_identical_reference_data_for_both_clients(self):
        report = self.imports("Fact stack = Laravel\nText with ``` and [untrusted link](https://example.invalid).")
        merge_id = report["merge_id"]
        self.assertEqual(self.cli("export", self.workspace, "--merge", merge_id, "--apply")[0], 2)
        self.assertFalse((self.workspace / "exports").exists())
        code, exported, error = self.cli("export", self.workspace, "--merge", merge_id, "--draft", "--apply")
        self.assertEqual(code, 0, error)
        folder = self.workspace / "exports" / merge_id
        markdown = (folder / "chatgpt-draft.md").read_text(encoding="utf-8")
        request = store.read_json(folder / "openrouter-draft.json")
        self.assertEqual(request, {"messages": [{"role": "user", "content": markdown}]})
        self.assertIn("DRAFT", markdown)
        self.assertIn("````json", markdown)
        self.assertNotIn("api_key", request)
        self.assertEqual(self.cli("export", self.workspace, "--merge", merge_id, "--draft", "--apply")[1]["writes"], [])
        review = store.read_json(self.workspace / report["review"])
        for claim in review["claims"]:
            claim["status"] = "accepted"
        edited = self.base / "review.json"
        edited.write_bytes(store.encode(review))
        reviewed = self.cli("merge", self.workspace, "--left", "left", "--right", "right", "--review", edited, "--apply")[1]
        self.assertNotEqual(reviewed["merge_id"], merge_id)
        self.assertEqual(self.cli("export", self.workspace, "--merge", reviewed["merge_id"], "--apply")[0], 0)
        self.assertTrue((folder / "chatgpt-draft.md").is_file())

    def test_merge_and_export_previews_have_no_writes(self):
        report = self.imports()
        before = {p.relative_to(self.workspace): p.read_bytes() for p in self.workspace.rglob("*") if p.is_file()}
        self.cli("merge", self.workspace, "--left", "left", "--right", "right")
        self.cli("export", self.workspace, "--merge", report["merge_id"], "--draft")
        after = {p.relative_to(self.workspace): p.read_bytes() for p in self.workspace.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_changed_import_and_tampered_merge_are_refused_before_export(self):
        report = self.imports()
        path = self.workspace / "imports/left.json"
        value = store.read_json(path)
        original = path.read_bytes()
        value["messages"][0]["text"] = "Changed source"
        path.write_bytes(store.encode(value))
        self.assertEqual(self.cli("export", self.workspace, "--merge", report["merge_id"], "--draft", "--apply")[0], 1)
        path.write_bytes(original)
        path = self.workspace / "merges" / (report["merge_id"] + ".json")
        value = store.read_json(path)
        value["accepted"] = [{"value": "Forged"}]
        path.write_bytes(store.encode(value))
        self.assertEqual(self.cli("export", self.workspace, "--merge", report["merge_id"], "--draft", "--apply")[0], 1)
        self.assertFalse((self.workspace / "exports").exists())

    def test_export_budget_refuses_without_truncation_or_partial_files(self):
        report = self.imports()
        code, _, _ = self.cli("export", self.workspace, "--merge", report["merge_id"], "--draft", "--max-bytes", 1, "--apply")
        self.assertEqual(code, 1)
        self.assertFalse((self.workspace / "exports").exists())

    def test_invalid_names_unowned_workspaces_and_blocked_parents_preserve_files(self):
        source = self.base / "source.txt"
        source.write_text("Context", encoding="utf-8")
        for source_name in ("../escape", "CON", "con", "name:stream", "MixedCase", "nul"):
            self.assertEqual(self.cli("import", self.workspace, source, "--name", source_name, "--apply")[0], 1)
        self.workspace.mkdir()
        existing = self.workspace / "important.txt"
        existing.write_bytes(b"Keep")
        self.assertEqual(self.cli("import", self.workspace, source, "--name", "left", "--apply")[0], 1)
        self.assertEqual(existing.read_bytes(), b"Keep")
        blocked = self.base / "file-parent"
        blocked.write_bytes(b"Keep parent")
        self.assertEqual(self.cli("import", blocked / "child", source, "--name", "left", "--apply")[0], 1)

    def test_link_and_junction_probes_refuse_before_writing(self):
        with patch.object(store.install, "is_link", side_effect=lambda p: p == self.base):
            with self.assertRaises(ValueError):
                store.write(self.workspace, {"imports/a.json": b"{}"}, apply=True)
        self.assertFalse(self.workspace.exists())

    def test_real_symlink_is_refused_where_supported(self):
        target = self.base / "real"
        target.mkdir()
        link = self.base / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            self.skipTest("Symlink unavailable: " + str(exc))
        with self.assertRaises(ValueError):
            store.write(link / "workspace", {"imports/a.json": b"{}"}, apply=True)
        self.assertFalse((target / "workspace").exists())

    def test_hardlinked_artifact_is_preserved_even_with_identical_bytes(self):
        store.write(self.workspace, {"imports/a.json": b"{}"}, apply=True)
        source = self.workspace / "imports/a.json"
        try:
            os.link(source, self.base / "alias")
        except OSError as exc:
            self.skipTest("Hardlink unavailable: " + str(exc))
        with self.assertRaises(ValueError):
            store.write(self.workspace, {"imports/a.json": b"{}"}, apply=True)
        self.assertEqual(source.read_bytes(), b"{}")

    def test_racing_file_creation_cannot_be_overwritten(self):
        original_open = os.open
        def race(path, flags, *args, **kwargs):
            if Path(path).name == "left.json":
                Path(path).write_bytes(b"External concurrent bytes")
            return original_open(path, flags, *args, **kwargs)
        with patch.object(store.os, "open", side_effect=race), self.assertRaises(FileExistsError):
            store.write(self.workspace, {"imports/left.json": b"{}"}, apply=True)
        self.assertEqual((self.workspace / "imports/left.json").read_bytes(), b"External concurrent bytes")

    @unittest.skipIf(os.name == "nt", "POSIX permissions and FIFO")
    def test_private_permissions_and_fifo_refusal(self):
        store.write(self.workspace, {"imports/a.json": b"{}"}, apply=True)
        self.assertEqual(self.workspace.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.workspace / "imports/a.json").stat().st_mode & 0o777, 0o600)
        fifo = self.base / "pipe"
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            store.read_bytes(fifo)

    def test_install_upgrade_preserves_private_memory_in_both_sharing_modes(self):
        old_source = self.base / "prior kit"
        shutil.copytree(install.ROOT, old_source, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.egg-info"))
        for mode in ("private", "team"):
            policy = old_source / "templates" / ("gitignore." + mode)
            policy.write_bytes(policy.read_bytes().replace(b"/ai-kit/.memory/\r\n", b"").replace(b"/ai-kit/.memory/\n", b""))
            project = self.base / ("project-" + mode)
            plan = install.build_plan(project, root=old_source, mode=mode)
            self.assertTrue(install.apply_plan(plan))
            private = project / "ai-kit/.memory/session"
            store.write(private, {"imports/a.json": b'{"private":"preserve exactly"}'}, apply=True)
            saved = (private / "imports/a.json").read_bytes()
            plan = install.build_plan(project, mode=mode)
            self.assertFalse(plan["conflicts"])
            self.assertTrue(install.apply_plan(plan))
            self.assertEqual((private / "imports/a.json").read_bytes(), saved)
            self.assertIn("/ai-kit/.memory/", (project / ".gitignore").read_text())


if __name__ == "__main__":
    unittest.main()
