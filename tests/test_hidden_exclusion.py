from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files


# ======================================================================
# Unit tests for _is_hidden() — a function that does not exist yet
# ======================================================================


class IsHiddenUnitTest(unittest.TestCase):
    """_is_hidden() doesn't exist yet — importing it will raise ImportError."""

    def test_is_hidden_can_be_imported(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

    def test_is_hidden_empty_path(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertFalse(_is_hidden(""))

    def test_is_hidden_single_dot(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertTrue(_is_hidden("."))

    def test_is_hidden_double_dot(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertTrue(_is_hidden(".."))

    def test_is_hidden_single_component(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertTrue(_is_hidden(".git"))

    def test_is_hidden_visible_path(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertFalse(_is_hidden("visible/file.md"))

    def test_is_hidden_hidden_dir_visible_file(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertTrue(_is_hidden(".hidden/visible.md"))

    def test_is_hidden_visible_dir_hidden_file(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertTrue(_is_hidden("visible/.hidden/file.md"))

    def test_is_hidden_trailing_slash(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertTrue(_is_hidden(".direnv/"))

    def test_is_hidden_visible_trailing_slash(self) -> None:
        from mira_okf.okf.read_model import _is_hidden

        self.assertFalse(_is_hidden("visible/"))


# ======================================================================
# Integration: list — hidden items excluded from inventory
# ======================================================================


class ListHiddenExclusionTest(unittest.TestCase):
    BUNDLE_FILES: dict[str, str] = {
        "index.md": "index\n",
        "visible.md": "---\ntype: Note\ntitle: Visible\n---\n",
        ".hidden.md": "---\ntype: Note\ntitle: Hidden\n---\n",
        ".secret/index.md": "index\n",
        ".secret/hidden.md": "---\ntype: Note\ntitle: Secret\n---\n",
    }

    def test_list_excludes_hidden_concepts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            concept_ids = {c["concept_id"] for c in payload["data"]["concepts"]}
            self.assertNotIn(".hidden", concept_ids)
            self.assertNotIn(".secret/hidden", concept_ids)
            self.assertIn("visible", concept_ids)

    def test_list_count_excludes_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, self.BUNDLE_FILES)
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["total"], 1)


# ======================================================================
# Integration: tree — hidden directories not descended into
# ======================================================================


class TreeHiddenExclusionTest(unittest.TestCase):
    def test_tree_hidden_directory_not_shown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "visible.md": "---\ntype: Note\n---\n",
                    ".hidden/index.md": "index\n",
                    ".hidden/secret.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(
                ["tree", str(root), "--depth", "2", "--summary"]
            )
            self.assertEqual(exit_code, 0)
            self.assertNotIn(".hidden", stdout)
            self.assertIn("concepts: 1", stdout)
            self.assertIn("index.md", stdout)

    def test_tree_hidden_file_not_shown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    ".hidden.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(
                ["tree", str(root), "--depth", "1", "--summary"]
            )
            self.assertEqual(exit_code, 0)
            self.assertNotIn(".hidden", stdout)

    def test_tree_concept_count_excludes_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "visible.md": "---\ntype: Note\n---\n",
                    ".hidden.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(
                ["tree", str(root), "--depth", "1", "--summary", "--json"]
            )
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["concept_count"], 1)


# ======================================================================
# Integration: validate — hidden files produce no diagnostics
# ======================================================================


class ValidateHiddenExclusionTest(unittest.TestCase):
    def test_validate_hidden_index_produces_no_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    ".hidden/index.md": "---\ntitle: Nope\n---\n",
                    "visible.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            hidden_issues = [
                i for i in payload["issues"] if ".hidden" in i.get("path", "")
            ]
            self.assertEqual(len(hidden_issues), 0)

    def test_validate_hidden_concept_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    ".hidden/secret.md": "body without frontmatter\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            hidden_issues = [
                i for i in payload["issues"] if ".hidden" in i.get("path", "")
            ]
            self.assertEqual(len(hidden_issues), 0)

    def test_validate_concept_count_excludes_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "visible.md": "---\ntype: Note\n---\n",
                    ".hidden.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["concept_count"], 1)


# ======================================================================
# Integration: links — hidden sources skipped, hidden targets broken
# ======================================================================


class LinksHiddenExclusionTest(unittest.TestCase):
    def test_links_from_hidden_source_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    ".hidden.md": "---\ntype: Note\n---\n[Target](visible.md)\n",
                    "visible.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            hidden_links = [
                l
                for l in payload["data"]["links"]
                if ".hidden" in l.get("source_path", "")
            ]
            self.assertEqual(len(hidden_links), 0)

    def test_links_to_hidden_target_reported_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "visible.md": "---\ntype: Note\n---\n[Hidden](.hidden.md)\n",
                    ".hidden.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--broken", "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            link_to_hidden = [
                l for l in payload["data"]["links"] if l["target"] == ".hidden.md"
            ]
            self.assertEqual(len(link_to_hidden), 1)
            self.assertTrue(link_to_hidden[0]["broken"])
            self.assertFalse(link_to_hidden[0]["resolved"])
            hidden_issues = [
                i for i in payload["issues"] if i["code"] == "OKF_LINK_BROKEN" and ".hidden" in i.get("path", "")
            ]
            self.assertEqual(len(hidden_issues), 0)

    def test_links_total_excludes_hidden_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    ".hidden.md": "---\ntype: Note\n---\n[Alpha](alpha.md)\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["total"], 0)


# ======================================================================
# Integration: health — hidden items excluded from counts
# ======================================================================


class HealthHiddenExclusionTest(unittest.TestCase):
    def test_health_concept_count_excludes_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "visible.md": "---\ntype: Note\n---\n",
                    ".hidden.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(
                ["health", str(root), "--json", "--profile", "full"]
            )
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["inventory"]["concept_count"], 1)

    def test_health_directory_count_excludes_hidden_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    ".hidden/index.md": "index\n",
                    ".hidden/secret.md": "---\ntype: Note\n---\n",
                    "visible.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(
                ["health", str(root), "--json", "--profile", "full"]
            )
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["inventory"]["directory_count"], 1)


# ======================================================================
# Symlink tests
# ======================================================================


class SymlinkHiddenExclusionTest(unittest.TestCase):
    def test_symlink_hidden_name_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "visible.md": "---\ntype: Note\n---\n",
                },
            )
            (root / ".link_to_visible.md").symlink_to("visible.md")
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            concept_ids = {c["concept_id"] for c in payload["data"]["concepts"]}
            self.assertNotIn(".link_to_visible", concept_ids)

    def test_symlink_visible_name_to_hidden_target_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n"})
            write_files(root, {".secret.md": "---\ntype: Note\n---\n"})
            (root / "link_to_secret.md").symlink_to(".secret.md")
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            concept_ids = {c["concept_id"] for c in payload["data"]["concepts"]}
            self.assertNotIn("link_to_secret", concept_ids)

    def test_symlink_visible_name_to_visible_target_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                },
            )
            (root / "link_to_target.md").symlink_to("target.md")
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            concept_ids = {c["concept_id"] for c in payload["data"]["concepts"]}
            self.assertIn("link_to_target", concept_ids)


# ======================================================================
# Explicit-path tests: single-item command with hidden path excluded
# ======================================================================


class ExplicitPathHiddenExclusionTest(unittest.TestCase):
    def test_list_explicit_hidden_path_excluded(self) -> None:
        path = ".hidden.md"
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    ".hidden.md": "---\ntype: Note\ntitle: Hidden\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            concept_ids = {c["concept_id"] for c in payload["data"]["concepts"]}
            self.assertNotIn(".hidden", concept_ids)
