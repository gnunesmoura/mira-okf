from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest
from pathlib import Path
import argparse
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tooling.cli import build_parser, main


class CliBootstrapTest(unittest.TestCase):
    def test_okf_subcommands_exist(self) -> None:
        parser = build_parser()
        root_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
        okf_parser = root_actions[0].choices["okf"]
        okf_actions = [action for action in okf_parser._actions if isinstance(action, argparse._SubParsersAction)]
        self.assertEqual(sorted(okf_actions[0].choices), ["list", "show", "tree"])

    def test_tree_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "alpha.md").write_text("---\ntype: Note\ntitle: Alpha\n---\nbody\n", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = main(["okf", "tree", "--summary"])
            finally:
                os.chdir(cwd)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            output = stdout.getvalue().strip().splitlines()
            self.assertIn("index.md", output[0])
            self.assertIn("concepts: 1", output[0])

    def test_tree_discovers_nested_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            nested = root / "workspace" / "bundle"
            nested.mkdir(parents=True)
            (nested / "index.md").write_text("index\n", encoding="utf-8")
            (nested / "alpha.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = main(["okf", "tree", "--summary"])
            finally:
                os.chdir(cwd)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("workspace/bundle/", stdout.getvalue())

    def test_tree_reports_ambiguous_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "artifacts").mkdir()
            (root / "tooling" / "bundles").mkdir(parents=True)
            for bundle_root in (root / "artifacts", root / "tooling" / "bundles"):
                (bundle_root / "index.md").write_text("index\n", encoding="utf-8")
                (bundle_root / "alpha.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = main(["okf", "tree", "--depth", "2", "--summary"])
            finally:
                os.chdir(cwd)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("More than one OKF bundle found", stderr.getvalue())
            self.assertIn("artifacts -> tooling okf tree artifacts --depth 2 --summary", stderr.getvalue())
            self.assertIn("tooling/bundles -> tooling okf tree tooling/bundles --depth 2 --summary", stderr.getvalue())

    def test_tree_respects_depth_and_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            (root / "area" / "deep").mkdir(parents=True)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "root.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "index.md").write_text("index\n", encoding="utf-8")
            (root / "area" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "deep" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["okf", "tree", str(root), "--depth", "1", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            output = stdout.getvalue()
            self.assertIn("bundle/", output)
            self.assertIn("area/", output)
            self.assertNotIn("deep/", output)

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["okf", "tree", str(root.resolve()), "--depth", "2", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("deep/", stdout.getvalue())

    def test_tree_emits_stable_json_with_tolerated_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            root.mkdir()
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "broken.md").write_text("---\ntitle: Broken\n---\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["okf", "tree", str(root), "--depth", "2", "--summary", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.tree")
            self.assertEqual(payload["bundle"]["source_kind"], "explicit")
            self.assertEqual(payload["data"]["concept_count"], 1)
            self.assertEqual(payload["data"]["concepts"][0]["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")


if __name__ == "__main__":
    unittest.main()
