from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files


class RegressionVisibleBundleTest(unittest.TestCase):
    """Characterization tests capturing current visible-only bundle behavior.

    These tests provide a measurable baseline for all five commands (list, tree,
    validate, links, health) over a visible-only bundle. They assert structural
    fields (counts, shapes, keys) without fragile exact-value assertions beyond
    what is stable. Run before any hidden-exclusion changes to validate that
    production code is unchanged.
    """

    BUNDLE_FILES: dict[str, str] = {
        "index.md": "index\n",
        "log.md": "# Log\n\n## 2026-07-05\n\n## 2026-07-04\n",
        "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: A note\nresource: R\ntags: [one]\ntimestamp: 2026-07-05\n---\n[Target](target.md) [Missing](missing.md) [External](https://example.com)\n## Citations\n",
        "beta.md": "---\ntype: Task\ntitle: Beta\n---\n[Alpha](alpha.md)\n",
        "target.md": "---\ntype: Note\ntitle: Target\n---\n",
        "broken.md": "---\ntitle: Broken\n---\n",
        "nested/index.md": "---\ntitle: Nested Index\n---\n",
        "nested/concept.md": "---\ntype: Note\ntitle: Nested Concept\n---\n",
    }

    # ------------------------------------------------------------------
    # list
    # ------------------------------------------------------------------
    def test_list_json_envelope_and_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.list")
            self.assertIn("bundle", payload)
            self.assertIn("data", payload)
            self.assertIn("issues", payload)
            data = payload["data"]
            self.assertEqual(sorted(data), ["concepts", "limit", "offset", "returned", "total", "truncated"])
            self.assertFalse(data["truncated"])
            self.assertIsInstance(data["concepts"], list)
            self.assertGreater(len(data["concepts"]), 0)
            for c in data["concepts"]:
                self.assertIn("concept_id", c)
                self.assertIn("path", c)
                self.assertIn("type", c)
                self.assertIn("title", c)

    def test_list_includes_all_visible_concepts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            concept_ids = {c["concept_id"] for c in payload["data"]["concepts"]}
            self.assertIn("alpha", concept_ids)
            self.assertIn("beta", concept_ids)
            self.assertIn("target", concept_ids)
            self.assertIn("nested/concept", concept_ids)
            self.assertEqual(payload["data"]["total"], len(payload["data"]["concepts"]))

    def test_list_handles_empty_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            root.mkdir()
            (root / "index.md").write_text("index\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["total"], 0)
            self.assertEqual(payload["data"]["concepts"], [])

    # ------------------------------------------------------------------
    # tree
    # ------------------------------------------------------------------
    def test_tree_json_envelope_and_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["tree", str(root), "--depth", "2", "--summary", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.tree")
            self.assertIn("bundle", payload)
            self.assertIn("data", payload)
            self.assertIn("issues", payload)
            data = payload["data"]
            self.assertIn("concept_count", data)
            self.assertIn("concepts", data)
            self.assertGreater(data["concept_count"], 0)
            self.assertIsInstance(data["concepts"], list)

    def test_tree_shows_nested_visible_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["tree", str(root), "--depth", "2", "--summary", "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            children_names = [c["name"] for c in payload["data"]["children"]]
            self.assertIn("nested", children_names)
            nested = next(c for c in payload["data"]["children"] if c["name"] == "nested")
            self.assertGreater(nested["concept_count"], 0)
            self.assertTrue(nested["has_index"])

    def test_tree_reserved_file_count_in_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["tree", str(root), "--depth", "2", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertIn("reserved:", stdout)

    # ------------------------------------------------------------------
    # validate
    # ------------------------------------------------------------------
    def test_validate_json_envelope_and_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.validate")
            self.assertIn("bundle", payload)
            self.assertIn("data", payload)
            self.assertIn("issues", payload)
            data = payload["data"]
            self.assertIn("passed", data)
            self.assertIn("status", data)
            self.assertIn("issue_count", data)
            self.assertIn("error_count", data)
            self.assertIn("warning_count", data)
            self.assertIn("info_count", data)
            self.assertIn("concept_count", data)
            self.assertIn("checked_file_count", data)
            self.assertIsInstance(payload["issues"], list)

    def test_validate_counts_are_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["issue_count"], len(payload["issues"]))
            self.assertEqual(
                payload["data"]["error_count"] + payload["data"]["warning_count"] + payload["data"]["info_count"],
                payload["data"]["issue_count"],
            )

    # ------------------------------------------------------------------
    # links
    # ------------------------------------------------------------------
    def test_links_json_envelope_and_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.links")
            self.assertIn("bundle", payload)
            self.assertIn("data", payload)
            self.assertIn("issues", payload)
            data = payload["data"]
            self.assertIn("links", data)
            self.assertIn("total", data)
            self.assertIn("returned", data)
            self.assertIsInstance(data["links"], list)
            if data["links"]:
                link = data["links"][0]
                self.assertIn("source_path", link)
                self.assertIn("target", link)
                self.assertIn("target_path", link)
                self.assertIn("target_concept_id", link)
                self.assertIn("broken", link)
                self.assertIn("external", link)
                self.assertIn("kind", link)
                self.assertIn("raw", link)
                self.assertIn("resolved", link)

    def test_links_broken_and_external_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["links", str(root), "--broken", "--external", "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            links = payload["data"]["links"]
            broken = [l for l in links if l["broken"]]
            external = [l for l in links if l["external"]]
            self.assertGreater(len(broken), 0)
            self.assertGreater(len(external), 0)

    # ------------------------------------------------------------------
    # health
    # ------------------------------------------------------------------
    def test_health_json_envelope_and_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.health")
            self.assertIn("bundle", payload)
            self.assertIn("data", payload)
            self.assertIn("issues", payload)
            data = payload["data"]
            expected_keys = {
                "citations", "connectivity", "indexes", "inventory", "links",
                "logs", "metadata", "reserved_files", "rules", "status", "summary", "validation",
            }
            self.assertEqual(set(data), expected_keys)
            self.assertIn("inventory", data)
            self.assertIn("concept_count", data["inventory"])
            self.assertIn("directory_count", data["inventory"])
            self.assertIn("reserved_file_count", data["inventory"])
            self.assertIn("concept_types", data["inventory"])
            self.assertIn("validation", data)
            self.assertIn("passed", data["validation"])
            self.assertIn("issue_count", data["validation"])
            self.assertIn("summary", data)
            self.assertIn("status", data)

    def test_health_inventory_counts_are_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            data = payload["data"]
            self.assertGreater(data["inventory"]["concept_count"], 0)
            self.assertGreater(data["inventory"]["directory_count"], 0)
            self.assertGreater(data["inventory"]["reserved_file_count"], 0)
            self.assertIsInstance(data["inventory"]["concept_types"], list)
            total_from_types = sum(ct["count"] for ct in data["inventory"]["concept_types"])
            self.assertEqual(total_from_types, data["inventory"]["concept_count"])

    def test_health_summary_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            data = payload["data"]
            self.assertGreaterEqual(data["summary"]["warning_signal_count"], 0)
            self.assertGreaterEqual(data["summary"]["error_signal_count"], 0)
