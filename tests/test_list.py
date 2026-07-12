from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tooling.cli import build_parser
from tests.support import run_main, write_files


class ListCommandTest(unittest.TestCase):
    def test_list_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nbody\n",
                },
            )
            exit_code, stdout, stderr = run_main(["okf", "list", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.list")
            self.assertEqual(payload["bundle"]["source_kind"], "discovered")
            self.assertEqual(payload["data"]["total"], 1)
            self.assertEqual(payload["data"]["returned"], 1)
            self.assertFalse(payload["data"]["truncated"])
            self.assertEqual(payload["data"]["concepts"][0]["concept_id"], "alpha")

    def test_list_returns_sorted_inventory_and_tolerated_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "log.md": "log\n",
                    "gamma.md": "---\ntype: Note\ntitle: Gamma\ntags:\n  - shared\n---\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\ntags:\n  - shared\n---\n",
                    "beta.md": "---\ntype: Task\ntitle: Beta\ntags:\n  - blue\n---\n",
                    "broken.md": "---\ntitle: Broken\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["okf", "list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha", "beta", "broken", "gamma"])
            self.assertEqual(payload["data"]["total"], 4)
            self.assertEqual(payload["data"]["returned"], 4)
            self.assertEqual(payload["data"]["offset"], 0)
            self.assertIsNone(payload["data"]["limit"])
            self.assertFalse(payload["data"]["truncated"])
            self.assertEqual([issue["code"] for issue in payload["issues"]], ["OKF_CONCEPT_MISSING_TYPE"])

    def test_list_applies_exact_filters_with_and_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntags:\n  - shared\n---\n",
                    "beta.md": "---\ntype: Task\ntags:\n  - shared\n---\n",
                    "gamma.md": "---\ntype: Note\ntags:\n  - other\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["okf", "list", str(root), "--type", "Note", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha", "gamma"])

            exit_code, stdout, stderr = run_main(["okf", "list", str(root), "--tag", "shared", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha", "beta"])

            exit_code, stdout, stderr = run_main(["okf", "list", str(root), "--type", "Note", "--tag", "shared", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha"])

    def test_list_windows_and_reports_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                    "beta.md": "---\ntype: Note\n---\n",
                    "gamma.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["okf", "list", str(root), "--offset", "1", "--limit", "1", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["total"], 3)
            self.assertEqual(payload["data"]["returned"], 1)
            self.assertEqual(payload["data"]["offset"], 1)
            self.assertEqual(payload["data"]["limit"], 1)
            self.assertTrue(payload["data"]["truncated"])
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["beta"])

    def test_list_human_output_is_path_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["okf", "list", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], "concepts: 2 of 2")
            self.assertEqual(lines[1], "alpha.md  [Note]  Alpha")
            self.assertEqual(lines[2], "nested/beta.md  [Task]  Beta")

    def test_list_rejects_negative_window_values(self) -> None:
        parser = build_parser()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                parser.parse_args(["okf", "list", "--limit", "-1"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("must be non-negative", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
