from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files


class ShowCommandTest(unittest.TestCase):
    def test_show_resolves_exact_concept_id_and_summary_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nAlpha body\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\ndescription: Beta description\ntags:\n  - shared\n---\nBeta body\n",
                },
            )
            exit_code, stdout, stderr = run_main(["show", str(root), "alpha", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], "alpha.md  [Note]  Alpha")
            self.assertNotIn("Alpha body", stdout)

    def test_show_appends_issues_section_after_concept_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                },
            )
            exit_code, stdout, stderr = run_main(["show", str(root), "broken"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertIn("Broken body", lines)
            self.assertEqual(lines[-2], "Issues")
            self.assertEqual(lines[-1], "- broken.md  [OKF_CONCEPT_MISSING_TYPE] Concept frontmatter is missing required type.")

    def test_show_omits_issues_section_when_none_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nAlpha body\n",
                },
            )
            exit_code, stdout, stderr = run_main(["show", str(root), "alpha"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertNotIn("Issues", stdout)

    def test_show_summary_keeps_issues_section_at_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                },
            )
            exit_code, stdout, stderr = run_main(["show", str(root), "broken", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], "broken.md  Broken")
            self.assertNotIn("Broken body", stdout)
            self.assertEqual(lines[-2], "Issues")
            self.assertEqual(lines[-1], "- broken.md  [OKF_CONCEPT_MISSING_TYPE] Concept frontmatter is missing required type.")

    def test_show_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nAlpha body\n",
                },
            )
            exit_code, stdout, stderr = run_main(["show", "alpha", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["bundle"]["source_kind"], "discovered")
            self.assertEqual(payload["data"]["concept_id"], "alpha")

    def test_show_resolves_bundle_relative_path_and_normalizes_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\ndescription: Beta description\ntags:\n  - shared\n---\nBeta body\n",
                },
            )
            for target in ("nested/beta", "nested/beta.md"):
                exit_code, stdout, stderr = run_main(["show", str(root), target, "--json"])
                self.assertEqual(exit_code, 0)
                self.assertEqual(stderr, "")
                payload = json.loads(stdout)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["command"], "okf.show")
                self.assertEqual(payload["data"]["concept_id"], "nested/beta")
                self.assertEqual(payload["data"]["relative_path"], "nested/beta.md")

    def test_show_emits_json_payload_and_visible_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                },
            )
            exit_code, stdout, stderr = run_main(["show", str(root), "broken", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.show")
            self.assertEqual(payload["data"]["concept_id"], "broken")
            self.assertEqual(payload["data"]["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")
            self.assertEqual(payload["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")

    def test_show_summary_preserves_complete_json_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: A description\ntags:\n  - shared\n---\nAlpha body\n",
                },
            )
            arguments = ["show", str(root), "alpha"]
            exit_code, plain_json, plain_stderr = run_main([*arguments, "--json"])
            self.assertEqual((exit_code, plain_stderr), (0, ""))
            exit_code, summary_json, summary_stderr = run_main([*arguments, "--summary", "--json"])
            self.assertEqual((exit_code, summary_stderr), (0, ""))
            self.assertEqual(json.loads(plain_json), json.loads(summary_json))

    def test_show_reports_not_found_and_ambiguous_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = run_main(["show", str(root), "missing"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("Concept not found: missing", stderr)

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
            exit_code, stdout, stderr = run_main(["show", "alpha", "--json"], cwd=root)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "OKF_DISCOVERY_AMBIGUOUS")

    def test_show_produces_stable_output_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\ndescription: Beta description\ntags:\n  - shared\n---\nBeta body\n",
                },
            )
            exit_code, stdout_one, stderr_one = run_main(["show", str(root), "nested/beta.md", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr_one, "")
            exit_code, stdout_two, stderr_two = run_main(["show", str(root), "nested/beta.md", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr_two, "")
            self.assertEqual(stdout_one, stdout_two)

    def test_show_renders_code_spans_and_fences_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            body = "Inline `[Beta](beta.md)` remains.\n\n```md\n[Beta](beta.md)\n[[beta]]\n```"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": f"---\ntype: Note\ntitle: Alpha\n---\n{body}\n",
                    "beta.md": "---\ntype: Note\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["show", str(root), "alpha"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn(body, stdout)

            exit_code, stdout, stderr = run_main(["show", str(root), "alpha", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertEqual(json.loads(stdout)["data"]["body"], body)


if __name__ == "__main__":
    unittest.main()
