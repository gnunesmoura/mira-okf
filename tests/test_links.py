from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files
from tooling.okf.semantic import semantic_text


class LinksCommandTest(unittest.TestCase):
    def test_links_and_backlinks_use_shared_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nSee [Beta](./beta.md), [[gamma]], [Broken](./missing.md), [External](https://example.com), and [Angle](<https://example.org/path>).\n",
                    "beta.md": "---\ntype: Note\ntitle: Beta\n---\nBack to [Alpha](alpha.md).\n",
                    "gamma.md": "---\ntype: Note\ntitle: Gamma\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.links")
            self.assertEqual([link["target_path"] for link in payload["data"]["links"]], ["beta.md", "gamma.md", "alpha.md"])
            self.assertEqual(payload["data"]["total"], 6)
            self.assertEqual(payload["data"]["returned"], 3)
            self.assertEqual([issue["code"] for issue in payload["issues"]], ["OKF_LINK_BROKEN"])

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--broken", "--external", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([link["target"] for link in payload["data"]["links"]], ["./beta.md", "gamma", "./missing.md", "https://example.com", "https://example.org/path", "alpha.md"])

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--external"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("[external] https://example.com", stdout)
            self.assertIn("[external] https://example.org/path", stdout)

    def test_links_resolve_encoded_and_parent_relative_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "Alpha Note.md": "---\ntype: Note\n---\n",
                    "nested/beta.md": "---\ntype: Note\n---\n[Alpha](../Alpha%20Note.md)\n",
                },
            )
            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["links"][0]["target_path"], "Alpha Note.md")
            self.assertEqual(payload["issues"], [])

    def test_links_and_backlinks_ignore_code_spans_and_fences(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\n"
                        "type: Note\n"
                        "---\n"
                        "[Beta](beta.md)\n"
                        "`[Beta](beta.md)`\n"
                        "`[[beta]]`\n"
                        "```md\n"
                        "[Beta](beta.md)\n"
                        "[Missing](missing.md)\n"
                        "```\n"
                    ),
                    "beta.md": "---\ntype: Note\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--broken", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([link["target"] for link in payload["data"]["links"]], ["beta.md"])
            self.assertEqual(payload["data"]["total"], 1)
            self.assertEqual([issue["code"] for issue in payload["issues"]], [])

            exit_code, stdout, stderr = run_main(["okf", "backlinks", str(root), "beta", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["total"], 1)
            self.assertEqual(payload["data"]["links"][0]["source_path"], "alpha.md")

    def test_semantic_text_is_stable(self) -> None:
        body = "Text `[Ignored](missing.md)`\n```md\n[[ignored]]\n```\n[Kept](kept.md)\n"
        self.assertEqual(semantic_text(body), semantic_text(body))


if __name__ == "__main__":
    unittest.main()
