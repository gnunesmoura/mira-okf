from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main


class TreeCommandTest(unittest.TestCase):
    def test_tree_summary_controls_human_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            (root / "index.md").parent.mkdir(parents=True)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "alpha.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")

            plain_exit, plain_stdout, plain_stderr = run_main(["tree", str(root), "--depth", "0"])
            summary_exit, summary_stdout, summary_stderr = run_main(["tree", str(root), "--depth", "0", "--summary"])

            self.assertEqual((plain_exit, plain_stderr), (0, ""))
            self.assertEqual((summary_exit, summary_stderr), (0, ""))
            self.assertTrue(plain_stdout.strip().endswith("/bundle/"))
            self.assertNotIn("concepts:", plain_stdout)
            self.assertNotIn("reserved:", plain_stdout)
            self.assertIn("index.md", summary_stdout)
            self.assertIn("concepts: 1", summary_stdout)
            self.assertIn("reserved: 1", summary_stdout)

    def test_tree_summary_metadata_uses_directory_payload_and_json_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            (root / "area").mkdir(parents=True)
            write = {
                "index.md": "index\n",
                "log.md": "log\n",
                "root.md": "---\ntype: Note\n---\n",
                "area/index.md": "index\n",
                "area/concept.md": "---\ntype: Note\n---\n",
            }
            for relative_path, content in write.items():
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            arguments = ["tree", str(root), "--depth", "1"]
            exit_code, plain_stdout, plain_stderr = run_main(arguments)
            self.assertEqual((exit_code, plain_stderr), (0, ""))
            exit_code, summary_stdout, summary_stderr = run_main([*arguments, "--summary"])
            self.assertEqual((exit_code, summary_stderr), (0, ""))
            self.assertEqual(summary_stdout, run_main([*arguments, "--summary"])[1])
            self.assertIn("bundle/  index.md  log.md  concepts: 1  reserved: 2", summary_stdout)
            self.assertIn("  area/  index.md  concepts: 1  reserved: 1", summary_stdout)
            self.assertNotIn("area/concept.md", plain_stdout)

            exit_code, plain_json, plain_stderr = run_main([*arguments, "--json"])
            self.assertEqual((exit_code, plain_stderr), (0, ""))
            exit_code, summary_json, summary_stderr = run_main([*arguments, "--summary", "--json"])
            self.assertEqual((exit_code, summary_stderr), (0, ""))
            self.assertEqual(json.loads(plain_json), json.loads(summary_json))

    def test_tree_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "alpha.md").write_text("---\ntype: Note\ntitle: Alpha\n---\nbody\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["tree", "--summary"], cwd=root)
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
            exit_code, stdout, stderr = run_main(["tree", "--summary"], cwd=root)
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
            exit_code, stdout, stderr = run_main(["tree", "--depth", "2", "--summary"], cwd=root)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("More than one OKF bundle found", stderr)
            self.assertIn("artifacts -> mira-okf tree artifacts --depth 2 --summary", stderr)
            self.assertIn("tooling/bundles -> mira-okf tree tooling/bundles --depth 2 --summary", stderr)

    def test_tree_respects_depth_and_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            (root / "area" / "deep").mkdir(parents=True)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "root.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "index.md").write_text("index\n", encoding="utf-8")
            (root / "area" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "deep" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["tree", str(root), "--depth", "1", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            output = stdout
            self.assertIn("bundle/", output)
            self.assertIn("area/", output)
            self.assertNotIn("deep/", output)

            exit_code, stdout, stderr = run_main(["tree", str(root.resolve()), "--depth", "2", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("deep/", stdout)

    def test_tree_emits_stable_json_with_tolerated_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            root.mkdir()
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "broken.md").write_text("---\ntitle: Broken\n---\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["tree", str(root), "--depth", "2", "--summary", "--json"])
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
