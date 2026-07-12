from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.support import run_main, write_files
from tooling.okf.semantic import semantic_text


class LinksCommandTest(unittest.TestCase):
    def test_links_preserve_external_and_missing_record_compatibility(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\ntype: Note\ntitle: Alpha\n---\n"
                        "[External](http://127.0.0.1:1/never-fetch) "
                        "[Missing](missing.md)\n"
                    ),
                },
            )

            exit_code, stdout, stderr = run_main(
                ["okf", "links", str(root), "--broken", "--external", "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            links = payload["data"]["links"]
            self.assertEqual([link["target"] for link in links], ["http://127.0.0.1:1/never-fetch", "missing.md"])
            self.assertEqual(
                [(link["external"], link["broken"], link["resolved"]) for link in links],
                [(True, False, False), (False, True, False)],
            )
            self.assertEqual([issue["code"] for issue in payload["issues"]], ["OKF_LINK_BROKEN"])
            self.assertEqual(payload["issues"][0]["fatal"], False)

    def test_links_json_shape_and_order_are_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "zeta.md": "---\ntype: Note\n---\n[Alpha](alpha.md)\n",
                    "alpha.md": "---\ntype: Note\n---\n[Zeta](zeta.md)\n",
                },
            )

            payloads = []
            for _ in range(2):
                exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
                self.assertEqual(exit_code, 0)
                self.assertEqual(stderr, "")
                payloads.append(json.loads(stdout))

            payload = payloads[0]
            self.assertEqual(sorted(payload), ["bundle", "command", "data", "issues", "ok"])
            self.assertEqual(sorted(payload["data"]), ["links", "returned", "total"])
            self.assertEqual(
                sorted(payload["data"]["links"][0]),
                [
                    "broken",
                    "external",
                    "kind",
                    "raw",
                    "resolved",
                    "source_concept_id",
                    "source_path",
                    "target",
                    "target_concept_id",
                    "target_path",
                ],
            )
            self.assertEqual(payloads[0]["data"], payloads[1]["data"])
            self.assertEqual(payloads[0]["issues"], payloads[1]["issues"])
            self.assertEqual(
                [link["source_path"] for link in payload["data"]["links"]],
                ["alpha.md", "zeta.md"],
            )

    def test_links_absolute_and_discovered_bundle_invocation_have_same_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\n---\n",
                },
            )
            exit_code, absolute_stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            exit_code, relative_stdout, stderr = run_main(["okf", "links", ".", "--json"], cwd=root)
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            absolute = json.loads(absolute_stdout)
            relative = json.loads(relative_stdout)
            self.assertEqual(absolute["data"], relative["data"])
            self.assertEqual(absolute["issues"], relative["issues"])

    def test_links_and_backlinks_use_shared_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nSee [Beta](./beta.md), [[gamma]], [Broken](./missing.md), [External](https://example.com), and [Angle](<https://example.org/path>).\n",
                    "beta.md": "---\ntype: Note\ntitle: Beta\n---\nBack to [Alpha](alpha.md).\n",
                    "gamma.md": "---\ntype: Note\ntitle: Gamma\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "okf.links")
            self.assertEqual([link["target_path"] for link in payload["data"]["links"]], ["beta.md", "gamma.md", "alpha.md"])
            self.assertEqual(payload["data"]["total"], 6)
            self.assertEqual(payload["data"]["returned"], 3)
            self.assertEqual([issue["code"] for issue in payload["issues"]], ["OKF_LINK_BROKEN"])

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--broken", "--external", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([link["target"] for link in payload["data"]["links"]], ["./beta.md", "gamma", "./missing.md", "https://example.com", "https://example.org/path", "alpha.md"])

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--external"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("[external] https://example.com", stdout)
            self.assertIn("[external] https://example.org/path", stdout)

    def test_links_resolve_encoded_and_parent_relative_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "Alpha Note.md": "---\ntype: Note\n---\n",
                    "nested/beta.md": "---\ntype: Note\n---\n[Alpha](../Alpha%20Note.md)\n",
                },
            )
            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["links"][0]["target_path"], "Alpha Note.md")
            self.assertEqual(payload["issues"], [])

    def test_links_preserve_root_relative_and_relative_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\ntitle: Root\n---\n",
                    "nested/source.md": (
                        "---\ntype: Note\ntitle: Source\n---\n"
                        "[Relative](target.md) [Root](/target.md) [Nested](/nested/target.md)\n"
                    ),
                    "nested/target.md": "---\ntype: Note\ntitle: Nested\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(
                [link["target_path"] for link in payload["data"]["links"]],
                ["nested/target.md", "target.md", "nested/target.md"],
            )
            self.assertEqual(payload["issues"], [])

    def test_root_relative_links_anchor_at_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "root.md": "---\ntype: Note\n---\n",
                    "nested/root.md": "---\ntype: Note\n---\n",
                    "nested/source.md": (
                        "---\ntype: Note\n---\n"
                        "[Root](/root.md) [Nested](/nested/root.md)\n"
                    ),
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertEqual([link["target_path"] for link in links], ["root.md", "nested/root.md"])

    def test_source_relative_forms_precede_bundle_root_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "target.md": "---\ntype: Note\n---\n",
                    "nested/target.md": "---\ntype: Note\n---\n",
                    "nested/deeper/source.md": (
                        "---\ntype: Note\n---\n"
                        "[Plain](../target.md) [Dot](.././target.md)\n"
                    ),
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertEqual([link["target_path"] for link in links], ["nested/target.md", "nested/target.md"])

    def test_links_decode_and_normalize_bundle_relative_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "Alpha Note.md": "---\ntype: Note\n---\n",
                    "nested/source.md": (
                        "---\ntype: Note\n---\n"
                        "[Encoded](/nested/../Alpha%20Note.md)\n"
                    ),
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            links = json.loads(stdout)["data"]["links"]
            self.assertEqual(links[0]["target"], "/nested/../Alpha Note.md")
            self.assertEqual(links[0]["target_path"], "Alpha Note.md")
            self.assertFalse(links[0]["broken"])

    def test_links_and_backlinks_ignore_code_spans_and_fences(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bundle"
            write_files(
                root,
                {
                    "index.md": "index\n",
                    "alpha.md": (
                        "---\n"
                        "type: Note\n"
                        "---\n"
                        "[Beta](beta.md)\n"
                        "`[Beta](beta.md)`\n"
                        "`[[beta]]`\n"
                        "```md\n"
                        "[Beta](beta.md)\n"
                        "[Missing](missing.md)\n"
                        "```\n"
                    ),
                    "beta.md": "---\ntype: Note\n---\n",
                },
            )

            exit_code, stdout, stderr = run_main(["okf", "links", str(root), "--broken", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual([link["target"] for link in payload["data"]["links"]], ["beta.md"])
            self.assertEqual(payload["data"]["total"], 1)
            self.assertEqual([issue["code"] for issue in payload["issues"]], [])

            exit_code, stdout, stderr = run_main(["okf", "backlinks", str(root), "beta", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["data"]["total"], 1)
            self.assertEqual(payload["data"]["links"][0]["source_path"], "alpha.md")

    def test_semantic_text_is_stable(self) -> None:
        body = "Text `[Ignored](missing.md)`\n```md\n[[ignored]]\n```\n[Kept](kept.md)\n"
        self.assertEqual(semantic_text(body), semantic_text(body))


if __name__ == "__main__":
    unittest.main()
