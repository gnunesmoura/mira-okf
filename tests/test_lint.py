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


def _minimal_bundle(root: Path) -> None:
    write_files(root, {
        "index.md": "index\n",
        "alpha.md": "---\ntype: Note\n---\n# Heading\ntext\n",
    })


_LINT_TRIGGER = "---\ntype: Note\n---\n# No blank\nshould trigger MD022\n"


class LintConfigDiscoveryTest(unittest.TestCase):
    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_no_config_uses_okf_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _minimal_bundle(root)
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            config = payload["data"]["config"]
            self.assertEqual(config["source"], "okf-default")
            self.assertEqual(config["profile"], "okf-default")
            self.assertEqual(config["ignores"], [])

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_json_config_honored(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                ".markdownlint.json": json.dumps({"MD022": False}),
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            config = payload["data"]["config"]
            self.assertEqual(config["source"], ".markdownlint.json")
            self.assertEqual(config["profile"], "user")
            for finding in payload["data"]["findings"]:
                self.assertNotEqual(finding["rule"], "MD022")

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_yaml_config_honored(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                ".markdownlint.yaml": "MD022: false\n",
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            config = payload["data"]["config"]
            self.assertEqual(config["source"], ".markdownlint.yaml")
            self.assertEqual(config["profile"], "user")
            for finding in payload["data"]["findings"]:
                self.assertNotEqual(finding["rule"], "MD022")

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_config_conflict_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                ".markdownlint.json": json.dumps({"MD022": False}),
                ".markdownlint.yaml": "MD022: false\n",
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            config = payload["data"]["config"]
            self.assertEqual(config["source"], ".markdownlint.json")
            codes = [issue["code"] for issue in payload["issues"]]
            self.assertIn("OKF_LINT_CONFIG_CONFLICT", codes)

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_malformed_json_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                ".markdownlint.json": "{not json}",
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            codes = [issue["code"] for issue in payload["issues"]]
            self.assertIn("OKF_LINT_CONFIG_MALFORMED", codes)

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_unknown_rule_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                ".markdownlint.json": json.dumps({"FAKE_RULE": False}),
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            codes = [issue["code"] for issue in payload["issues"]]
            self.assertIn("OKF_LINT_CONFIG_UNKNOWN_RULE", codes)


class LintIgnoresTest(unittest.TestCase):
    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_ignores_excludes_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                ".markdownlint.json": json.dumps({"ignores": ["generated/**"]}),
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
                "generated/foo.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            for finding in payload["data"]["findings"]:
                self.assertNotIn("generated", finding["file"])


class LintCommandTest(unittest.TestCase):
    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_lint_only_formatting_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "alpha.md": "# No frontmatter\ntext\n",
                "beta.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["command"], "okf.lint")
            self.assertGreater(payload["data"]["count"], 0)
            for finding in payload["data"]["findings"]:
                self.assertIn(finding["rule"], {"MD003", "MD022", "MD041", "CRITICAL"})

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_lint_envelope_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            _minimal_bundle(root)
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            self.assertEqual(sorted(payload), ["bundle", "command", "data", "issues", "ok"])
            self.assertEqual(payload["command"], "okf.lint")
            self.assertTrue(payload["ok"])
            self.assertEqual(
                sorted(payload["data"]),
                ["by_file", "config", "count", "findings"],
            )

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_findings_sorted_by_file_line_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "alpha.md": "---\ntype: Note\n---\n# One\ntext\n\n# Two\ntext\n",
                "beta.md": "---\ntype: Note\n---\n# One\ntext\n",
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            findings = payload["data"]["findings"]
            for i in range(len(findings) - 1):
                a = findings[i]
                b = findings[i + 1]
                key_a = (a["file"], a["line"], a["rule"])
                key_b = (b["file"], b["line"], b["rule"])
                self.assertLessEqual(key_a, key_b)

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_findings_use_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
            })
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout)
            for finding in payload["data"]["findings"]:
                self.assertFalse(
                    finding["file"].startswith("/"),
                    f"finding file should be relative, got: {finding['file']}",
                )
                self.assertNotIn(
                    str(root), finding["file"],
                    f"finding file should not contain the bundle root, got: {finding['file']}",
                )
            for file_key in payload["data"]["by_file"]:
                self.assertFalse(
                    file_key.startswith("/"),
                    f"by_file key should be relative, got: {file_key}",
                )

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt")
    def test_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "alpha.md": _LINT_TRIGGER,
            })
            original = (root / "alpha.md").read_text(encoding="utf-8")
            exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                (root / "alpha.md").read_text(encoding="utf-8"), original
            )

    @unittest.skipUnless(HAS_PYMARKDOWN, "requires pymarkdownlnt to confirm it can be blocked")
    def test_lint_unavailable_without_extra(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(root, {
                "index.md": "index\n",
                "alpha.md": "---\ntype: Note\n---\n# Heading\ntext\n",
            })
            with NoPyMarkdown():
                exit_code, stdout, stderr = run_main(["lint", str(root), "--json"])
            self.assertEqual(exit_code, 1)
            payload = json.loads(stdout)
            self.assertFalse(payload["ok"])
            codes = [issue["code"] for issue in payload["issues"]]
            self.assertIn("OKF_LINT_UNAVAILABLE", codes)


if __name__ == "__main__":
    unittest.main()
