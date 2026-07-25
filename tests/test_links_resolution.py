from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files
from mira_okf.okf.semantic import semantic_text

class LinksResolutionRegressionTest(unittest.TestCase):
    """Regression tests for portable bundle-root link resolution (CHANGE-031).

    Covers root-relative, nested root-relative, source-relative parent,
    /bundles/ non-alias, invocation context equivalence, isolated bundle,
    missing non-fatal, external, no-mutation, and determinism.
    """

    # --------------------------------------------------------------------------
    # root-relative: /concept.md resolves from bundle root
    # --------------------------------------------------------------------------
    def test_links_root_relative_resolves_from_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                    "nested/source.md": (
                        "---\ntype: Note\n---\n"
                        "[Root](/target.md)\n"
                    ),
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0]["target_path"], "target.md")
            self.assertTrue(links[0]["resolved"])
            self.assertFalse(links[0]["broken"])

    def test_links_nested_root_relative_resolves_from_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "nested/target.md": "---\ntype: Note\n---\n",
                    "nested/source.md": (
                        "---\ntype: Note\n---\n"
                        "[Nested](/nested/target.md)\n"
                    ),
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0]["target_path"], "nested/target.md")
            self.assertTrue(links[0]["resolved"])

    # --------------------------------------------------------------------------
    # source-relative: ../concept.md resolves from source directory
    # --------------------------------------------------------------------------
    def test_links_source_relative_parent_resolves_from_source_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "nested/target.md": "---\ntype: Note\n---\n",
                    "nested/deeper/source.md": (
                        "---\ntype: Note\n---\n"
                        "[Parent](../target.md)\n"
                    ),
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertEqual(len(links), 1)
            # ../target.md from nested/deeper/ resolves to nested/target.md
            self.assertEqual(links[0]["target_path"], "nested/target.md")
            self.assertTrue(links[0]["resolved"])

    # --------------------------------------------------------------------------
    # /bundles/concept.md is NOT repo-root alias when bundles/ is root
    # --------------------------------------------------------------------------
    def test_links_bundles_prefix_is_not_repo_root_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundles"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "concept.md": "---\ntype: Note\n---\n",
                    "bundles/deep.md": "---\ntype: Note\n---\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n"
                        "[Deep](/bundles/deep.md) [Self](/concept.md)\n"
                    ),
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            target_paths = {link["target_path"] for link in links}
            # /bundles/deep.md should resolve as bundles/deep.md, not nodeep.md
            self.assertIn("bundles/deep.md", target_paths)
            self.assertIn("concept.md", target_paths)

    # --------------------------------------------------------------------------
    # absolute vs relative invocation produce same data
    # --------------------------------------------------------------------------
    def test_links_invocation_contexts_agree_on_root_relative(self) -> None:
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
            exit_code, abs_stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            exit_code, rel_stdout, stderr = run_main(["links", ".", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            abs_data = json.loads(abs_stdout)["data"]
            rel_data = json.loads(rel_stdout)["data"]
            self.assertEqual(abs_data, rel_data)

    # --------------------------------------------------------------------------
    # isolated vs nested invocation produce same result (seeds for T003)
    # --------------------------------------------------------------------------
    def test_links_nested_repo_path_resolves_root_relative(self) -> None:
        """A bundle nested in a repo subdirectory resolves root-relative links."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repo" / "bundles"
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
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0]["target_path"], "target.md")
            self.assertTrue(links[0]["resolved"])

    # --------------------------------------------------------------------------
    # Missing root-relative target remains non-fatal broken link
    # --------------------------------------------------------------------------
    def test_links_missing_root_relative_is_non_fatal_broken(self) -> None:
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
            exit_code, stdout, stderr = run_main(["links", str(root), "--broken", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([issue["code"] for issue in payload["issues"]], ["OKF_LINK_BROKEN"])
            self.assertFalse(payload["issues"][0]["fatal"])
            links = payload["data"]["links"]
            missing = [l for l in links if l["broken"]]
            self.assertEqual(len(missing), 1)

    # --------------------------------------------------------------------------
    # External URLs are not resolved locally
    # --------------------------------------------------------------------------
    def test_links_external_url_remains_external(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n"
                        "[External](https://example.com/path)\n"
                    ),
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--external", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertTrue(links[0]["external"])
            self.assertFalse(links[0]["resolved"])
            self.assertFalse(links[0]["broken"])

    # --------------------------------------------------------------------------
    # No mutation of fixture data
    # --------------------------------------------------------------------------
    def test_links_does_not_mutate_fixture_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n"
                        "[Root](/target.md) [Local](target.md)\n"
                    ),
                },
            )
            original_content = (root / "index.md").read_text(encoding="utf-8")
            run_main(["links", str(root), "--json"])
            self.assertEqual((root / "index.md").read_text(encoding="utf-8"), original_content)

    # --------------------------------------------------------------------------
    # Deterministic output
    # --------------------------------------------------------------------------
    def test_links_deterministic_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "zeta.md": "---\ntype: Note\n---\n[Alpha](alpha.md)\n",
                    "alpha.md": "---\ntype: Note\n---\n[Zeta](zeta.md) [Root](/zeta.md)\n",
                },
            )
            results = []
            for _ in range(3):
                exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
                self.assertEqual(exit_code, 0)
                results.append(json.loads(stdout))
            self.assertEqual(results[0]["data"], results[1]["data"])
            self.assertEqual(results[0]["data"], results[2]["data"])

