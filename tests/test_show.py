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

    def test_show_summary_is_brief_json_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: A description\ntags:\n  - shared\n---\nAlpha body\n",
                },
            )
            arguments = ["show", str(root), "alpha", "--json"]
            exit_code, brief_json, brief_stderr = run_main([*arguments, "--profile", "brief"])
            self.assertEqual((exit_code, brief_stderr), (0, ""))
            exit_code, summary_json, summary_stderr = run_main([*arguments, "--summary"])
            self.assertEqual((exit_code, summary_stderr), (0, ""))
            self.assertEqual(json.loads(brief_json), json.loads(summary_json))
            self.assertNotIn("body", json.loads(summary_json)["data"])

    def test_show_profiles_filter_json_and_render_human(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: A description\ntags:\n  - shared\nstatus: draft\n---\nAlpha body\n",
                "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
            })

            for profile in ("brief", "normal", "full"):
                exit_code, stdout, stderr = run_main(["show", str(root), "alpha", "--profile", profile, "--json"])
                self.assertEqual((exit_code, stderr), (0, ""))
                data = json.loads(stdout)["data"]
                self.assertEqual(data["profile"], profile)
                if profile == "brief":
                    self.assertEqual(set(data) - {"profile"}, {"concept_id", "title", "description", "type", "tags", "relative_path"})
                    self.assertNotIn("body", data)
                elif profile == "normal":
                    self.assertIn("body", data)
                    self.assertEqual(data["frontmatter"]["status"], "draft")
                else:
                    self.assertIn("body", data)
                    self.assertEqual(data["frontmatter"]["status"], "draft")

                exit_code, human, stderr = run_main(["show", str(root), "alpha", "--profile", profile])
                self.assertEqual((exit_code, stderr), (0, ""))
                self.assertIn("alpha.md  [Note]  Alpha", human)
                self.assertIn("description: A description", human)
                self.assertIn("tags: shared", human)
                if profile == "brief":
                    self.assertNotIn("Alpha body", human)
                else:
                    self.assertIn("Alpha body", human)
                if profile == "full":
                    self.assertIn("Frontmatter", human)
                    self.assertLess(human.index("status: draft"), human.index("Alpha body"))

            exit_code, stdout, stderr = run_main(["show", str(root), "broken", "--profile", "brief"])
            self.assertEqual((exit_code, stderr), (0, ""))
            self.assertIn("Issues", stdout)
            self.assertNotIn("Broken body", stdout)

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


    # --- Generic Markdown file reads (reserved files) ---

    def test_show_reads_root_index_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "# Root Index\n\nWelcome.\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "index.md"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("index.md  [Markdown]", stdout)
            self.assertIn("# Root Index", stdout)

    def test_show_reads_root_log_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "log.md": "# Changelog\n\n## v0.2\n\n- Fixed bug\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "log.md"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("log.md  [Markdown]", stdout)
            self.assertIn("# Changelog", stdout)

    def test_show_reads_nested_index_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "nested/index.md": "# Nested Index\n\nNested content.\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "nested/index.md"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("nested/index.md  [Markdown]", stdout)
            self.assertIn("# Nested Index", stdout)

    # --- Visible Markdown without concept frontmatter ---

    def test_show_reads_visible_md_without_concept_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "readme.md": "# Readme\n\nThis file has no concept frontmatter.\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "readme"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("readme.md  [Markdown]", stdout)
            self.assertIn("# Readme", stdout)

    # --- JSON generic output ---

    def test_show_generic_json_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            content = "# Readme\n\nContent.\n"
            write_files(root, {
                "index.md": "index\n",
                "readme.md": content,
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "readme.md", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.show")
            self.assertIsNotNone(payload["bundle"])
            data = payload["data"]
            self.assertEqual(data["document_kind"], "markdown")
            self.assertEqual(data["relative_path"], "readme.md")
            self.assertEqual(data["content"], content)
            self.assertNotIn("concept_id", data)
            self.assertEqual(payload["issues"], [])

    # --- Profile filtering for generic output ---

    def test_show_generic_brief_omits_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "readme.md": "# Readme\n\nLong content here.\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "readme", "--profile", "brief"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("readme.md  [Markdown]", stdout)
            self.assertNotIn("Long content here", stdout)

    def test_show_generic_summary_is_brief_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "readme.md": "# Readme\n\nLong content here.\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "readme", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("readme.md  [Markdown]", stdout)
            self.assertNotIn("Long content here", stdout)

    def test_show_generic_normal_includes_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            content = "# Readme\n\nFull content.\n"
            write_files(root, {
                "index.md": "index\n",
                "readme.md": content,
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "readme", "--profile", "normal"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("readme.md  [Markdown]", stdout)
            self.assertIn(content.strip(), stdout)

    def test_show_generic_json_profile_brief_omits_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "readme.md": "# Readme\n\nContent.\n",
            })
            exit_code, brief, stderr = run_main(
                ["show", str(root), "readme", "--json", "--profile", "brief"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            brief_data = json.loads(brief)["data"]
            self.assertEqual(brief_data["document_kind"], "markdown")
            self.assertEqual(brief_data["relative_path"], "readme.md")
            self.assertNotIn("content", brief_data)

    def test_show_generic_json_normal_includes_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            content = "# Readme\n\nContent.\n"
            write_files(root, {
                "index.md": "index\n",
                "readme.md": content,
            })
            exit_code, normal, stderr = run_main(
                ["show", str(root), "readme", "--json", "--profile", "normal"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            normal_data = json.loads(normal)["data"]
            self.assertEqual(normal_data["document_kind"], "markdown")
            self.assertEqual(normal_data["relative_path"], "readme.md")
            self.assertEqual(normal_data["content"], content)

    # --- Concept precedence ---

    def test_show_concept_precedence_over_generic_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nAlpha body\n",
                "readme.md": "# Plain readme\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "alpha", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            data = json.loads(stdout)["data"]
            self.assertEqual(data["concept_id"], "alpha")
            self.assertNotIn("document_kind", data)

    def test_show_concept_path_precedence_over_generic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "nested/beta.md": "---\ntype: Task\ntitle: Beta\n---\nBeta body\n",
                "readme.md": "# Readme\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "nested/beta"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("nested/beta.md  [Task]", stdout)
            self.assertIn("Beta body", stdout)
            self.assertNotIn("[Markdown]", stdout)

    # --- Malformed concept preserved alongside generic files ---

    def test_show_malformed_concept_preserved_when_generic_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                "readme.md": "# Readme\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "broken"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("Broken body", stdout)
            self.assertIn("Issues", stdout)
            self.assertIn("OKF_CONCEPT_MISSING_TYPE", stdout)

    # --- Rejection of invalid targets ---

    def test_show_rejects_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n"})
            exit_code, stdout, stderr = run_main(["show", str(root), "nonexistent"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("not found", stderr.lower())

    def test_show_rejects_directory_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "subdir/index.md": "nested\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "subdir"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)

    def test_show_rejects_non_markdown_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "data.json": '{"key": "value"}\n',
            })
            exit_code, stdout, stderr = run_main(["show", str(root), "data.json"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)

    def test_show_rejects_hidden_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                ".hidden.md": "secret\n",
            })
            exit_code, stdout, stderr = run_main(["show", str(root), ".hidden.md"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)

    def test_show_rejects_outside_bundle_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {"index.md": "index\n"})
            outside = Path(tmpdir) / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            exit_code, stdout, stderr = run_main(["show", str(root), "../outside.md"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)


if __name__ == "__main__":
    unittest.main()
