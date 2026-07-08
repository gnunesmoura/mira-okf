from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files


class HealthCommandTest(unittest.TestCase):
    def test_health_reports_contract_groups_and_soft_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "- [Alpha](alpha.md)\n",
                    "log.md": "## 2026-07-04\n\n## no\n\n## 2026-07-05\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: One\nresource: R\ntags: [x]\ntimestamp: 2026-07-04\n---\n[Beta](nested/beta.md) [Missing](missing.md) [External](https://example.com)\n## citations\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\n---\n[Alpha](alpha.md)\n",
                    "nested/gamma.md": "---\ntype: Note\ntitle: Gamma\n---\n",
                    "nested/index.md": "---\ntitle: nope\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            data = payload["data"]
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.health")
            self.assertEqual(data["status"], "invalid")
            self.assertEqual(
                sorted(data),
                ["citations", "connectivity", "indexes", "inventory", "links", "logs", "metadata", "reserved_files", "status", "summary", "validation"],
            )
            self.assertNotIn("issues", data["validation"])
            self.assertFalse(data["validation"]["passed"])
            self.assertEqual(data["validation"]["issue_count"], len([issue for issue in payload["issues"] if issue["code"] != "OKF_LINK_BROKEN"]))
            self.assertEqual(data["inventory"]["concept_count"], 3)
            self.assertEqual(data["inventory"]["directory_count"], 2)
            self.assertEqual(data["inventory"]["reserved_file_count"], 3)
            self.assertEqual(data["inventory"]["concept_types"], [{"type": "Note", "count": 2}, {"type": "Task", "count": 1}])
            self.assertEqual(data["reserved_files"]["malformed_reserved_file_paths"], ["log.md", "nested/index.md"])
            self.assertEqual(data["links"]["broken_internal_link_count"], 1)
            self.assertEqual(data["links"]["external_link_count"], 1)
            self.assertEqual(data["links"]["concepts_with_broken_internal_links"], ["alpha"])
            self.assertEqual(data["indexes"]["directories_without_index"], [])
            self.assertIn("nested/gamma.md", data["indexes"]["unlisted_content_paths"])
            self.assertEqual(data["logs"]["newest_entry_date"], "2026-07-05")
            self.assertEqual(data["logs"]["malformed_date_heading_count"], 1)
            self.assertEqual(data["logs"]["ordering_issue_count"], 1)
            self.assertEqual(data["metadata"]["fields"][0]["field"], "title")
            self.assertIn("nested/beta", data["metadata"]["fields"][1]["missing_concepts"])
            self.assertEqual(data["citations"]["external_linked_without_citations_count"], 0)
            self.assertEqual(data["connectivity"]["orphan_concepts"], ["nested/gamma"])

    def test_health_status_ok_and_attention(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "- [Alpha](alpha.md)\n",
                    "log.md": "## 2026-07-05\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: One\nresource: R\ntags: [x]\ntimestamp: 2026-07-05\n---\n[Alpha](alpha.md)\n",
                },
            )
            exit_code, stdout, _ = run_main(["okf", "health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(json.loads(stdout)["data"]["status"], "ok")

            write_files(root, {"alpha.md": "---\ntype: Note\ntitle: Alpha\n---\n"})
            exit_code, stdout, _ = run_main(["okf", "health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(json.loads(stdout)["data"]["status"], "attention")

    def test_health_discovers_and_reports_ambiguity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_files(root / "one", {"index.md": "index\n", "a.md": "---\ntype: Note\n---\n"})
            write_files(root / "two", {"index.md": "index\n", "b.md": "---\ntype: Note\n---\n"})
            exit_code, stdout, stderr = run_main(["okf", "health", "--json"], cwd=root)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            self.assertEqual(json.loads(stdout)["error"]["code"], "OKF_DISCOVERY_AMBIGUOUS")

    def test_health_human_output_starts_with_path_and_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n", "alpha.md": "---\ntype: Note\n---\n"})
            exit_code, stdout, stderr = run_main(["okf", "health", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], f"{root}  health: attention")
            self.assertEqual([line.split(":", 1)[0] for line in lines[1:]], ["validation", "inventory", "reserved files", "links", "indexes", "logs", "metadata", "citations", "connectivity"])


if __name__ == "__main__":
    unittest.main()
