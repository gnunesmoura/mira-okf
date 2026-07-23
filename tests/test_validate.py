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


class ValidatePortableResolutionRegressionTest(unittest.TestCase):
    """Regression tests for portable bundle-root link resolution via validate (CHANGE-031).

    Validate does not produce link output; this test asserts that a missing
    root-relative target remains a non-fatal finding (does not fail the bundle).
    """

    def test_validate_missing_root_relative_is_non_fatal(self) -> None:
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
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            # Missing link is not a validate issue — validate doesn't check links
            # But the command must complete successfully (non-fatal)
            self.assertIsInstance(payload["data"]["passed"], bool)


class ValidateCommandTest(unittest.TestCase):
    def test_validate_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.validate")
            self.assertEqual(payload["bundle"]["source_kind"], "discovered")

    def test_validate_reports_reserved_files_and_validation_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "---\nokf_version: 0.1\n---\n",
                    "log.md": "# Log\n\n## 2026-07-04\n\n## not-a-date\n\n## 2026-07-05\n",
                    "alpha.md": "alpha\n",
                    "beta.md": "---\ntype:\n---\n",
                    "gamma.md": "---\ntype: Mystery\ncustom: value\n---\n",
                    "nested/index.md": "---\ntitle: Nested\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.validate")
            self.assertFalse(payload["data"]["passed"])
            self.assertEqual(payload["data"]["status"], "fail")
            self.assertEqual(payload["data"]["issue_count"], len(payload["issues"]))
            self.assertEqual(payload["data"]["error_count"], 2)
            self.assertEqual(payload["data"]["warning_count"], 3)
            self.assertEqual(payload["data"]["info_count"], 0)
            self.assertEqual(payload["data"]["concept_count"], 3)
            self.assertEqual(payload["data"]["checked_file_count"], 6)
            self.assertEqual(
                [issue["code"] for issue in payload["issues"]],
                [
                    "OKF_FRONTMATTER_MISSING",
                    "OKF_CONCEPT_MISSING_TYPE",
                    "OKF_LOG_INVALID_DATE_HEADING",
                    "OKF_LOG_DATE_GROUP_ORDER",
                    "OKF_INDEX_FRONTMATTER_NOT_ALLOWED",
                ],
            )

    def test_validate_allows_root_index_without_frontmatter_and_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "bundle index\n",
                    "alpha.md": "---\ntype: Mystery\ncustom_field: value\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["data"]["passed"])
            self.assertEqual(payload["data"]["status"], "pass")
            self.assertEqual(payload["data"]["issue_count"], 0)
            self.assertEqual(payload["data"]["concept_count"], 1)
            self.assertEqual(payload["data"]["checked_file_count"], 2)

    def test_validate_allows_missing_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["data"]["passed"])
            self.assertEqual(payload["data"]["checked_file_count"], 1)

    def test_validate_reports_root_index_frontmatter_with_extra_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "---\nokf_version: 0.1\ntitle: Nope\n---\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertFalse(payload["data"]["passed"])
            self.assertEqual(payload["issues"][0]["code"], "OKF_ROOT_INDEX_FRONTMATTER_INVALID")

    def test_validate_uses_shared_failure_envelope_for_ambiguous_and_missing_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for bundle_root in (root / "artifacts", root / "tooling" / "bundles"):
                write_files(
                    bundle_root,
                    {
                        "index.md": "index\n",
                        "alpha.md": "---\ntype: Note\n---\n",
                    },
                )
            exit_code, stdout, stderr = run_main(["validate", "--json"], cwd=root)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "OKF_DISCOVERY_AMBIGUOUS")

        exit_code, stdout, stderr = run_main(["validate", "/no/such/bundle", "--json"])
        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "OKF_BUNDLE_NOT_FOUND")

    def test_validate_human_output_is_path_first_and_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "broken body\n",
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], str(root))
            self.assertIn("validation: fail", lines[1])
            self.assertIn("[error] OKF_FRONTMATTER_MISSING", lines[2])


class ValidateLintIntegrationTest(unittest.TestCase):
    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_validate_includes_lint_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n# Heading\ntext\n"
                    ),
                },
            )
            exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertIn("lint", payload["data"])
            lint = payload["data"]["lint"]
            self.assertIn("findings", lint)
            self.assertIn("count", lint)
            self.assertIn("by_file", lint)
            self.assertIn("config", lint)
            self.assertGreater(lint["count"], 0)

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt to confirm it can be blocked")
    def test_validate_lint_omitted_when_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\ntype: Note\n---\n# Heading\ntext\n"
                    ),
                },
            )
            with NoPyMarkdown():
                exit_code, stdout, stderr = run_main(["validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertNotIn("lint", payload["data"])
            codes = [issue["code"] for issue in payload["issues"]]
            self.assertIn("OKF_LINT_UNAVAILABLE", codes)


if __name__ == "__main__":
    unittest.main()

