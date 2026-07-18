from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files
from mira_okf.cli import build_parser


class PropsCommandTest(unittest.TestCase):
    def test_default_table_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "zeta.md": "---\ntype: Task\ntitle: Zeta\ndescription: Last\ntags: [later, shared]\n---\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: First\ntags:\n  - shared\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["props", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertEqual(
                stdout,
                "concept_id\ttype\ttitle\tdescription\ttags\n"
                "alpha\tNote\tAlpha\tFirst\t[\"shared\"]\n"
                "zeta\tTask\tZeta\tLast\t[\"later\",\"shared\"]\n",
            )

    def test_json_preserves_requested_extension_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\nowner: [team, ops]\n---\n",
                    "beta.md": "---\ntype: Task\ntitle: Beta\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(
                ["props", str(root), "--field", "title", "--field", "owner", "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(
                {key: payload[key] for key in ("ok", "command", "data", "issues")},
                {
                    "ok": True,
                    "command": "okf.props",
                    "data": {
                        "fields": ["title", "owner"],
                        "rows": [
                            {"concept_id": "alpha", "title": "Alpha", "owner": ["team", "ops"]},
                            {"concept_id": "beta", "title": "Beta", "owner": None},
                        ],
                    },
                    "issues": [],
                },
            )
            self.assertIn("bundle", payload)

    def test_invalid_field_arguments_fail_without_success_output(self) -> None:
        for fields in (("",), ("title", "title")):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with self.subTest(fields=fields), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    build_parser().parse_args(["props", *(arg for field in fields for arg in ("--field", field))])
            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertNotIn("concept_id", stderr.getvalue())

    def test_missing_values_and_empty_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n", "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\n"})

            exit_code, stdout, stderr = run_main(["props", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            row = json.loads(stdout)["data"]["rows"][0]
            self.assertIsNone(row["description"])
            self.assertEqual(row["tags"], [])

            exit_code, stdout, stderr = run_main(["props", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertEqual(stdout.splitlines()[1], "alpha\tNote\tAlpha\t\t[]")

            empty = Path(tmpdir) / "empty"
            empty.mkdir()
            exit_code, stdout, stderr = run_main(["props", str(empty), "--field", "owner", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertEqual(json.loads(stdout)["data"], {"fields": ["owner"], "rows": []})

    def test_mixed_frontmatter_keeps_rows_and_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "valid.md": "---\ntype: Note\ntitle: Valid\nowner: team\n---\n",
                    "unknown.md": "---\ntype: Task\ntitle: Unknown\nowner: ops\ncustom: value\n---\n",
                    "issue.md": "---\ntitle: Issue\nowner: review\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(
                ["props", str(root), "--field", "title", "--field", "custom", "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([row["concept_id"] for row in payload["data"]["rows"]], ["issue", "unknown", "valid"])
            self.assertEqual(payload["data"]["rows"][1]["custom"], "value")
            self.assertIsNone(payload["data"]["rows"][0]["custom"])
            self.assertEqual(payload["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")

    def test_concept_order_is_independent_of_filesystem_creation_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            files = {
                "index.md": "index\n",
                "nested/zeta.md": "---\ntype: Note\ntitle: Zeta\n---\n",
                "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\n",
                "nested/beta.md": "---\ntype: Note\ntitle: Beta\n---\n",
            }
            first = root / "first"
            second = root / "second"
            write_files(first, files)
            write_files(second, dict(reversed(list(files.items()))))

            outputs = []
            for bundle in (first, second):
                exit_code, stdout, stderr = run_main(["props", str(bundle), "--json"])
                self.assertEqual(exit_code, 0)
                self.assertEqual(stderr, "")
                outputs.append(json.loads(stdout)["data"])
            self.assertEqual(outputs[0], outputs[1])

    def test_props_does_not_change_bundle_bytes_or_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n", "alpha.md": "---\ntype: Note\n---\n"})
            paths = [root, *root.rglob("*")]
            before = {
                path: (path.read_bytes() if path.is_file() else None, path.stat().st_mode, path.stat().st_mtime_ns)
                for path in paths
            }

            for arguments in ([], ["--json"]):
                exit_code, _, stderr = run_main(["props", str(root), *arguments])
                self.assertEqual(exit_code, 0)
                self.assertEqual(stderr, "")

            after = {
                path: (path.read_bytes() if path.is_file() else None, path.stat().st_mode, path.stat().st_mtime_ns)
                for path in paths
            }
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
