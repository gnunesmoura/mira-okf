from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files

class ShowInvalidTargetTest(unittest.TestCase):

    def test_show_malformed_concept_preserved_when_generic_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                "readme.md": "# Readme\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "broken"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("Broken body", stdout)
            self.assertIn("Issues", stdout)
            self.assertIn("OKF_CONCEPT_MISSING_TYPE", stdout)

    def test_show_rejects_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n"})
            exit_code, stdout, stderr = run_main(["show", str(root), "nonexistent"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("not found", stderr.lower())

    def test_show_rejects_directory_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "subdir/index.md": "nested\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "subdir"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)

    def test_show_rejects_non_markdown_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "data.json": '{"key": "value"}\n',
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "data.json"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)

    def test_show_rejects_hidden_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                ".hidden.md": "secret\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), ".hidden.md"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)

    def test_show_rejects_outside_bundle_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n"})
            outside = Path(tmpdir) / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["show", str(root), "../outside.md"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)

