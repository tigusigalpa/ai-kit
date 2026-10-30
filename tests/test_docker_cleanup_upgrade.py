"""New Docker guidance upgrades without replacing project data or local policy."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install


class DockerCleanupUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="aikit-cleanup-upgrade-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.source = self.base / "source"
        shutil.copytree(install.ROOT, self.source,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.paths = ("AGENTS.md", "ai-kit/CONTAINERS.md")
        self.current = {name: (self.source / "template" / name).read_bytes()
                        for name in self.paths}
        # Simulate an older managed baseline without depending on a Git checkout.
        for name in self.paths:
            path = self.source / "template" / name
            path.write_bytes(self.current[name] + b"\nEarlier local test baseline.\n")

    def plan(self, project, **options):
        return install.build_plan(project, root=self.source, **options)

    def restore_current_source(self):
        for name, content in self.current.items():
            (self.source / "template" / name).write_bytes(content)

    def test_upgrade_replaces_managed_guidance_in_private_and_team_modes(self):
        for mode in ("private", "team"):
            with self.subTest(mode=mode):
                project = self.base / mode
                for name in self.paths:
                    (self.source / "template" / name).write_bytes(
                        self.current[name] + b"\nEarlier local test baseline.\n")
                self.assertTrue(install.apply_plan(self.plan(project, mode=mode, agents=["codex"])))
                owned = {name: (project / name).read_bytes()
                         for name in ("PROJECT_CONTEXT.md", "WIKI.md", "ai-kit/settings.json")}
                old = {name: (project / name).read_bytes() for name in self.paths}
                self.restore_current_source()
                plan = self.plan(project)
                self.assertFalse(plan["conflicts"])
                self.assertTrue(install.apply_plan(plan))
                for name in self.paths:
                    self.assertEqual((project / name).read_bytes(), self.current[name])
                    backups = list((project / "ai-kit/.upstream-cache/backups").glob("*/" + name))
                    self.assertEqual(len(backups), 1)
                    self.assertEqual(backups[0].read_bytes(), old[name])
                self.assertEqual(owned, {name: (project / name).read_bytes() for name in owned})
                self.assertFalse(self.plan(project)["actions"])

    def assert_local_policy_conflict(self, relative):
        project = self.base / "adapted project"
        self.assertTrue(install.apply_plan(self.plan(project, agents=["codex"])))
        adapted = (project / relative).read_bytes() + b"\nKeep the owner's recovery volume.\n"
        (project / relative).write_bytes(adapted)
        state = (project / "ai-kit/.install-state.json").read_bytes()
        self.restore_current_source()
        plan = self.plan(project)
        self.assertIn(relative, plan["conflicts"])
        self.assertFalse(install.apply_plan(plan))
        self.assertEqual((project / relative).read_bytes(), adapted)
        self.assertEqual((project / "ai-kit/.install-state.json").read_bytes(), state)
        candidate = project / plan["candidates"][relative]["path"]
        self.assertEqual(candidate.read_bytes(), self.current[relative])
        manifest = json.loads((project / plan["candidates"][relative]["manifest"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["local_hash"], install.digest(adapted))
        self.assertEqual(manifest["source_hash"], install.digest(self.current[relative]))

    def test_locally_adapted_container_policy_requires_reconciliation(self):
        self.assert_local_policy_conflict("ai-kit/CONTAINERS.md")

    def test_locally_adapted_entry_point_requires_reconciliation(self):
        self.assert_local_policy_conflict("AGENTS.md")


if __name__ == "__main__":
    unittest.main()
