from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files


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


if __name__ == "__main__":
    unittest.main()

