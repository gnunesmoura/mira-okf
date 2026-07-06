from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest
from unittest import mock
from pathlib import Path
import argparse
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tooling.cli import build_parser, main
from tooling.okf.commands import command_stub


def _write_files(root: Path, files: dict[str, str]) -> None:
    for relative_path, contents in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")


def _run_main(argv: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    previous_cwd = Path.cwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(argv)
    finally:
        if cwd is not None:
            os.chdir(previous_cwd)
    return exit_code, stdout.getvalue(), stderr.getvalue()


class CliBootstrapTest(unittest.TestCase):
    def test_okf_subcommands_exist(self) -> None:
        parser = build_parser()
        root_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
        okf_parser = root_actions[0].choices["okf"]
        okf_actions = [action for action in okf_parser._actions if isinstance(action, argparse._SubParsersAction)]
        self.assertEqual(sorted(okf_actions[0].choices), ["backlinks", "links", "list", "show", "tree", "validate"])

    def test_okf_command_stub_dispatches_list(self) -> None:
        args = argparse.Namespace(okf_command="list")
        with mock.patch("tooling.okf.commands.run_list", return_value=7) as run_list:
            self.assertEqual(command_stub(args), 7)
        run_list.assert_called_once_with(args)

    def test_okf_command_stub_dispatches_show(self) -> None:
        args = argparse.Namespace(okf_command="show")
        with mock.patch("tooling.okf.commands.run_show", return_value=9) as run_show:
            self.assertEqual(command_stub(args), 9)
        run_show.assert_called_once_with(args)

    def test_okf_command_stub_dispatches_validate(self) -> None:
        args = argparse.Namespace(okf_command="validate")
        with mock.patch("tooling.okf.commands.run_validate", return_value=11) as run_validate:
            self.assertEqual(command_stub(args), 11)
        run_validate.assert_called_once_with(args)

    def test_tree_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "alpha.md").write_text("---\ntype: Note\ntitle: Alpha\n---\nbody\n", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = main(["okf", "tree", "--summary"])
            finally:
                os.chdir(cwd)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            output = stdout.getvalue().strip().splitlines()
            self.assertIn("index.md", output[0])
            self.assertIn("concepts: 1", output[0])

    def test_tree_discovers_nested_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            nested = root / "workspace" / "bundle"
            nested.mkdir(parents=True)
            (nested / "index.md").write_text("index\n", encoding="utf-8")
            (nested / "alpha.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = main(["okf", "tree", "--summary"])
            finally:
                os.chdir(cwd)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("workspace/bundle/", stdout.getvalue())

    def test_tree_reports_ambiguous_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "artifacts").mkdir()
            (root / "tooling" / "bundles").mkdir(parents=True)
            for bundle_root in (root / "artifacts", root / "tooling" / "bundles"):
                (bundle_root / "index.md").write_text("index\n", encoding="utf-8")
                (bundle_root / "alpha.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = main(["okf", "tree", "--depth", "2", "--summary"])
            finally:
                os.chdir(cwd)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("More than one OKF bundle found", stderr.getvalue())
            self.assertIn("artifacts -> tooling okf tree artifacts --depth 2 --summary", stderr.getvalue())
            self.assertIn("tooling/bundles -> tooling okf tree tooling/bundles --depth 2 --summary", stderr.getvalue())

    def test_tree_respects_depth_and_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            (root / "area" / "deep").mkdir(parents=True)
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "root.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "index.md").write_text("index\n", encoding="utf-8")
            (root / "area" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            (root / "area" / "deep" / "leaf.md").write_text("---\ntype: Note\n---\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["okf", "tree", str(root), "--depth", "1", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            output = stdout.getvalue()
            self.assertIn("bundle/", output)
            self.assertIn("area/", output)
            self.assertNotIn("deep/", output)

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["okf", "tree", str(root.resolve()), "--depth", "2", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("deep/", stdout.getvalue())

    def test_tree_emits_stable_json_with_tolerated_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            root.mkdir()
            (root / "index.md").write_text("index\n", encoding="utf-8")
            (root / "broken.md").write_text("---\ntitle: Broken\n---\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["okf", "tree", str(root), "--depth", "2", "--summary", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue(), "")
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.tree")
            self.assertEqual(payload["bundle"]["source_kind"], "explicit")
            self.assertEqual(payload["data"]["concept_count"], 1)
            self.assertEqual(payload["data"]["concepts"][0]["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")

    def test_list_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nbody\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "list", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.list")
            self.assertEqual(payload["bundle"]["source_kind"], "discovered")
            self.assertEqual(payload["data"]["total"], 1)
            self.assertEqual(payload["data"]["returned"], 1)
            self.assertFalse(payload["data"]["truncated"])
            self.assertEqual(payload["data"]["concepts"][0]["concept_id"], "alpha")

    def test_list_returns_sorted_inventory_and_tolerated_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "log.md": "log\n",
                    "gamma.md": "---\ntype: Note\ntitle: Gamma\ntags:\n  - shared\n---\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\ntags:\n  - shared\n---\n",
                    "beta.md": "---\ntype: Task\ntitle: Beta\ntags:\n  - blue\n---\n",
                    "broken.md": "---\ntitle: Broken\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "list", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha", "beta", "broken", "gamma"])
            self.assertEqual(payload["data"]["total"], 4)
            self.assertEqual(payload["data"]["returned"], 4)
            self.assertEqual(payload["data"]["offset"], 0)
            self.assertIsNone(payload["data"]["limit"])
            self.assertFalse(payload["data"]["truncated"])
            self.assertEqual([issue["code"] for issue in payload["issues"]], ["OKF_CONCEPT_MISSING_TYPE"])

    def test_list_applies_exact_filters_with_and_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntags:\n  - shared\n---\n",
                    "beta.md": "---\ntype: Task\ntags:\n  - shared\n---\n",
                    "gamma.md": "---\ntype: Note\ntags:\n  - other\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "list", str(root), "--type", "Note", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha", "gamma"])

            exit_code, stdout, stderr = _run_main(["okf", "list", str(root), "--tag", "shared", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha", "beta"])

            exit_code, stdout, stderr = _run_main(["okf", "list", str(root), "--type", "Note", "--tag", "shared", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["alpha"])

    def test_list_windows_and_reports_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                    "beta.md": "---\ntype: Note\n---\n",
                    "gamma.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "list", str(root), "--offset", "1", "--limit", "1", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["total"], 3)
            self.assertEqual(payload["data"]["returned"], 1)
            self.assertEqual(payload["data"]["offset"], 1)
            self.assertEqual(payload["data"]["limit"], 1)
            self.assertTrue(payload["data"]["truncated"])
            self.assertEqual([concept["concept_id"] for concept in payload["data"]["concepts"]], ["beta"])

    def test_list_human_output_is_path_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "list", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], "concepts: 2 of 2")
            self.assertEqual(lines[1], "alpha.md  [Note]  Alpha")
            self.assertEqual(lines[2], "nested/beta.md  [Task]  Beta")

    def test_show_resolves_exact_concept_id_and_summary_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nAlpha body\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\ndescription: Beta description\ntags:\n  - shared\n---\nBeta body\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", str(root), "alpha", "--summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], "alpha.md  [Note]  Alpha")
            self.assertNotIn("Alpha body", stdout)

    def test_show_appends_issues_section_after_concept_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", str(root), "broken"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertIn("Broken body", lines)
            self.assertEqual(lines[-2], "Issues")
            self.assertEqual(lines[-1], "- broken.md  [OKF_CONCEPT_MISSING_TYPE] Concept frontmatter is missing required type.")

    def test_show_omits_issues_section_when_none_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nAlpha body\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", str(root), "alpha"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertNotIn("Issues", stdout)

    def test_show_summary_keeps_issues_section_at_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", str(root), "broken", "--summary"])
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
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nAlpha body\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", "alpha", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["bundle"]["source_kind"], "discovered")
            self.assertEqual(payload["data"]["concept_id"], "alpha")

    def test_show_resolves_bundle_relative_path_and_normalizes_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\ndescription: Beta description\ntags:\n  - shared\n---\nBeta body\n",
                },
            )
            for target in ("nested/beta", "nested/beta.md"):
                exit_code, stdout, stderr = _run_main(["okf", "show", str(root), target, "--json"])
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
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "---\ntitle: Broken\n---\nBroken body\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", str(root), "broken", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.show")
            self.assertEqual(payload["data"]["concept_id"], "broken")
            self.assertEqual(payload["data"]["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")
            self.assertEqual(payload["issues"][0]["code"], "OKF_CONCEPT_MISSING_TYPE")

    def test_show_reports_not_found_and_ambiguous_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", str(root), "missing"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("Concept not found: missing", stderr)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for bundle_root in (root / "artifacts", root / "tooling" / "bundles"):
                _write_files(
                    bundle_root,
                    {
                        "index.md": "index\n",
                        "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "show", "alpha", "--json"], cwd=root)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "OKF_DISCOVERY_AMBIGUOUS")

    def test_show_produces_stable_output_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "nested/beta.md": "---\ntype: Task\ntitle: Beta\ndescription: Beta description\ntags:\n  - shared\n---\nBeta body\n",
                },
            )
            exit_code, stdout_one, stderr_one = _run_main(["okf", "show", str(root), "nested/beta.md", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr_one, "")
            exit_code, stdout_two, stderr_two = _run_main(["okf", "show", str(root), "nested/beta.md", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr_two, "")
            self.assertEqual(stdout_one, stdout_two)

    def test_list_rejects_negative_window_values(self) -> None:
        parser = build_parser()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                parser.parse_args(["okf", "list", "--limit", "-1"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("must be non-negative", stderr.getvalue())

    def test_links_and_backlinks_use_shared_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nSee [Beta](./beta.md), [[gamma]], [Broken](./missing.md), [External](https://example.com), and [Angle](<https://example.org/path>).\n",
                    "beta.md": "---\ntype: Note\ntitle: Beta\n---\nBack to [Alpha](alpha.md).\n",
                    "gamma.md": "---\ntype: Note\ntitle: Gamma\n---\n",
                },
            )

            exit_code, stdout, stderr = _run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.links")
            self.assertEqual([link["target_path"] for link in payload["data"]["links"]], ["beta.md", "gamma.md", "alpha.md"])
            self.assertEqual(payload["data"]["total"], 6)
            self.assertEqual(payload["data"]["returned"], 3)
            self.assertEqual([issue["code"] for issue in payload["issues"]], ["OKF_LINK_BROKEN"])

            exit_code, stdout, stderr = _run_main(["okf", "links", str(root), "--broken", "--external", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([link["target"] for link in payload["data"]["links"]], ["./beta.md", "gamma", "./missing.md", "https://example.com", "https://example.org/path", "alpha.md"])

            exit_code, stdout, stderr = _run_main(["okf", "links", str(root), "--external"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("[external] https://example.com", stdout)
            self.assertIn("[external] https://example.org/path", stdout)

            exit_code, stdout, stderr = _run_main(["okf", "backlinks", str(root), "beta.md", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.backlinks")
            self.assertEqual(payload["data"]["concept"]["concept_id"], "beta")
            self.assertEqual([link["source_path"] for link in payload["data"]["links"]], ["alpha.md"])


class ValidateCommandTest(unittest.TestCase):
    def test_validate_discovers_bundle_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "validate", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.validate")
            self.assertEqual(payload["bundle"]["source_kind"], "discovered")

    def test_validate_reports_reserved_files_and_validation_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
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
            exit_code, stdout, stderr = _run_main(["okf", "validate", str(root), "--json"])
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
            _write_files(
                root,
                {
                    "index.md": "bundle index\n",
                    "alpha.md": "---\ntype: Mystery\ncustom_field: value\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "validate", str(root), "--json"])
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
            _write_files(
                root,
                {
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["data"]["passed"])
            self.assertEqual(payload["data"]["checked_file_count"], 1)

    def test_validate_reports_root_index_frontmatter_with_extra_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "---\nokf_version: 0.1\ntitle: Nope\n---\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "validate", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertFalse(payload["data"]["passed"])
            self.assertEqual(payload["issues"][0]["code"], "OKF_ROOT_INDEX_FRONTMATTER_INVALID")

    def test_validate_uses_shared_failure_envelope_for_ambiguous_and_missing_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for bundle_root in (root / "artifacts", root / "tooling" / "bundles"):
                _write_files(
                    bundle_root,
                    {
                        "index.md": "index\n",
                        "alpha.md": "---\ntype: Note\n---\n",
                    },
                )
            exit_code, stdout, stderr = _run_main(["okf", "validate", "--json"], cwd=root)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "OKF_DISCOVERY_AMBIGUOUS")

        exit_code, stdout, stderr = _run_main(["okf", "validate", "/no/such/bundle", "--json"])
        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "OKF_BUNDLE_NOT_FOUND")

    def test_validate_human_output_is_path_first_and_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _write_files(
                root,
                {
                    "index.md": "index\n",
                    "broken.md": "broken body\n",
                },
            )
            exit_code, stdout, stderr = _run_main(["okf", "validate", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            lines = stdout.strip().splitlines()
            self.assertEqual(lines[0], str(root))
            self.assertIn("validation: fail", lines[1])
            self.assertIn("[error] OKF_FRONTMATTER_MISSING", lines[2])


if __name__ == "__main__":
    unittest.main()
