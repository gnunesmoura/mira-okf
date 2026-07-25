from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import NoPyMarkdown, run_main, write_files

try:
    from pymarkdown.api import PyMarkdownApi  # noqa: F401

    HAS_PYMARKDOWN = True
except ImportError:
    HAS_PYMARKDOWN = False

class HealthResolutionRegressionTest(unittest.TestCase):
    """Regression tests for portable bundle-root link resolution via health (CHANGE-031)."""

    # --------------------------------------------------------------------------
    # links/health consistency on root-relative resolution
    # --------------------------------------------------------------------------
    def test_health_and_links_agree_on_root_relative_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                    "alpha.md": (
                        "---\ntype: Note\ntitle: Alpha\n---\n"
                        "[Target](/target.md)\n"
                    ),
                },
            )
            exit_code, links_stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            exit_code, health_stdout, stderr = run_main(["health", str(root), "--json"])
            self.assertEqual(exit_code, 0)

            links_payload = json.loads(links_stdout)
            health_payload = json.loads(health_stdout)

            # Both should have one link, resolved, no broken
            self.assertEqual(
                links_payload["data"]["links"][0]["target_path"],
                "target.md",
            )
            self.assertTrue(links_payload["data"]["links"][0]["resolved"])
            self.assertEqual(health_payload["data"]["links"]["broken_internal_link_count"], 0)
            self.assertEqual(health_payload["data"]["links"]["resolved_internal_link_count"], 1)
            self.assertEqual(health_payload["data"]["links"]["internal_link_count"], 1)

    def test_health_and_links_agree_on_broken_root_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\ntype: Note\ntitle: Alpha\n---\n"
                        "[Missing](/missing.md)\n"
                    ),
                },
            )
            exit_code, links_stdout, stderr = run_main(["links", str(root), "--broken", "--json"])
            self.assertEqual(exit_code, 0)
            exit_code, health_stdout, stderr = run_main(["health", str(root), "--json"])
            self.assertEqual(exit_code, 0)

            links_payload = json.loads(links_stdout)
            health_payload = json.loads(health_stdout)

            self.assertTrue(links_payload["data"]["links"][0]["broken"])
            self.assertEqual(health_payload["data"]["links"]["broken_internal_link_count"], 1)

    # --------------------------------------------------------------------------
    # health invocation context equivalence
    # --------------------------------------------------------------------------
    def test_health_invocation_contexts_agree(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n"
                        "[Root](/target.md)\n"
                    ),
                },
            )
            exit_code, abs_stdout, stderr = run_main(["health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            exit_code, rel_stdout, stderr = run_main(["health", ".", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            abs_data = json.loads(abs_stdout)["data"]
            rel_data = json.loads(rel_stdout)["data"]
            self.assertEqual(abs_data, rel_data)

    # --------------------------------------------------------------------------
    # No mutation of fixture data
    # --------------------------------------------------------------------------
    def test_health_does_not_mutate_fixture_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n"
                        "[Target](/target.md)\n"
                    ),
                },
            )
            original_content = (root / "index.md").read_text(encoding="utf-8")
            run_main(["health", str(root), "--json"])
            self.assertEqual((root / "index.md").read_text(encoding="utf-8"), original_content)

    def test_health_deterministic_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n"
                        "[Target](/target.md)\n"
                    ),
                },
            )
            results = []
            for _ in range(3):
                exit_code, stdout, stderr = run_main(["health", str(root), "--json"])
                self.assertEqual(exit_code, 0)
                results.append(json.loads(stdout))
            self.assertEqual(results[0]["data"], results[1]["data"])
            self.assertEqual(results[0]["data"], results[2]["data"])

    # --------------------------------------------------------------------------
    # Missing root-relative target is non-fatal in health
    # --------------------------------------------------------------------------
    def test_health_missing_root_relative_is_non_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n"
                        "[Missing](/missing.md)\n"
                    ),
                },
            )
            exit_code, stdout, stderr = run_main(["health", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            codes = [issue["code"] for issue in payload["issues"]]
            self.assertIn("OKF_LINK_BROKEN", codes)
            self.assertEqual(payload["data"]["links"]["broken_internal_link_count"], 1)

