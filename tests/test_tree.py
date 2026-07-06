from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main


class TreeCommandTest(unittest.TestCase):
    def test_tree_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "alpha.md").write_text("---\ntype: Note\ntitle: Alpha\n---\nbody\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["okf", "tree", "--summary"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            output = stdout.strip().splitlines()
            self.assertIn("index.md", output[0])
            self.assertIn("concepts: 1", output[0])

    def test_tree_discovers_nested_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            nested = root / "workspace" / "bundle"
            nested.mkdir(parents=True)
            (nested / "index.md").write_text("index\n", encoding="utf-8")
            (nested / "alpha.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["okf", "tree", "--summary"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("workspace/bundle/", stdout)

    def test_tree_reports_ambiguous_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "artifacts").mkdir()
            (root / "tooling" / "bundles").mkdir(parents=True)
            for bundle_root in (root / "artifacts", root / "tooling" / "bundles"):
                (bundle_root / "index.md").write_text("index\n", encoding="utf-8")
                (bundle_root / "alpha.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["okf", "tree", "--depth", "2", "--summary"], cwd=root)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("More than one OKF bundle found", stderr)
            self.assertIn("artifacts -> tooling okf tree artifacts --depth 2 --summary", stderr)
            self.assertIn("tooling/bundles -> tooling okf tree tooling/bundles --depth 2 --summary", stderr)

    def test_tree_respects_depth_and_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            (root / "area" / "deep").mkdir(parents=True)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "root.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "index.md").write_text("index\n", encoding="utf-8")
            (root / "area" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "deep" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["okf", "tree", str(root), "--depth", "1", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            output = stdout
            self.assertIn("bundle/", output)
            self.assertIn("area/", output)
            self.assertNotIn("deep/", output)

            exit_code, stdout, stderr = run_main(["okf", "tree", str(root.resolve()), "--depth", "2", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("deep/", stdout)

    def test_tree_emits_stable_json_with_tolerated_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            root.mkdir()
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "broken.md").write_text("---\ntitle: Broken\n---\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["okf", "tree", str(root), "--depth", "2", "--summary", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.tree")
            self.assertEqual(payload["bundle"]["source_kind"], "explicit")
            self.assertEqual(payload["data"]["concept_count"], 1)
            self.assertEqual(payload["data"]["concepts"][0]["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")


if __name__ == "__main__":
    unittest.main()
