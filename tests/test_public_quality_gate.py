from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import configparser
import tarfile
import tempfile
import unittest
import zipfile
from csv import reader
from email.parser import Parser
from pathlib import Path
import tomllib

from tests.support import run_main, write_files


PROJECT = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
PROJECT_METADATA = PROJECT["project"]
PUBLIC_DISTRIBUTION = PROJECT["tool"]["mira_okf"]["public_distribution"]
README = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
LICENSE_TEXT = (Path(__file__).resolve().parents[1] / "LICENSE").read_text(encoding="utf-8")
COMMANDS = {
    "tree": ["tree", "--summary"],
    "list": ["list"],
    "show": ["show", "alpha"],
    "links": ["links", "--broken", "--external"],
    "backlinks": ["backlinks", "alpha"],
    "props": ["props"],
    "validate": ["validate"],
    "health": ["health"],
}
FIXTURE_FILES = {
    "valid": {
        "index.md": "- [Alpha](alpha.md)\n- [Beta](nested/beta.md)\n",
        "log.md": "## 2026-07-05\n\n## 2026-07-04\n",
        "alpha.md": "---\ntype: Note\ntitle: Alpha\ndescription: First concept\ntags:\n  - shared\n---\nAlpha body. See [Beta](nested/beta.md) and [Gamma](nested/gamma.md).\n",
        "nested/beta.md": "---\ntype: Task\ntitle: Beta\ntags:\n  - shared\n---\nBeta body. See [Alpha](../alpha.md).\n",
        "nested/gamma.md": "---\ntype: Note\ntitle: Gamma\n---\nGamma body.\n",
    },
    "malformed-readable": {
        "index.md": "index\n",
        "alpha.md": "---\ntype: Note\ntitle: Alpha\n---\nReadable content.\n",
        "unterminated.md": "---\ntype: Note\ntitle: Incomplete\nReadable content remains available.\n",
    },
    "invalid": {"index.md": "index\n", "broken.md": "This is not a concept document.\n"},
    "ambiguous": {
        "one/index.md": "index\n",
        "one/alpha.md": "---\ntype: Note\n---\n",
        "two/index.md": "index\n",
        "two/beta.md": "---\ntype: Note\n---\n",
    },
    "empty": {},
}


class PublicQualityGateTest(unittest.TestCase):
    def test_approved_public_distribution_inputs_are_authoritative(self) -> None:
        self.assertEqual(
            PUBLIC_DISTRIBUTION,
            {
                "distribution": "mira-okf",
                "import_package": "mira_okf",
                "cli": "mira-okf",
                "repository": "gnunesmoura/mira-okf",
                "version_source": "pyproject.toml",
                "version": "0.0.1a2",
                "repository_url": "https://github.com/gnunesmoura/mira-okf",
                "documentation_url": "https://github.com/gnunesmoura/mira-okf/tree/main/docs",
                "issues_url": "https://github.com/gnunesmoura/mira-okf/issues",
                "python": ">=3.12",
                "license": "MIT",
                "maintainer": "gnunesmoura",
                "support_stage": "alpha",
                "okf_specification": "0.1",
                "platform_support": [
                    "Linux (validated)",
                    "Windows (best effort)",
                    "macOS (out of scope)",
                ],
                "compatibility": "Breaking changes may omit a major version before 1.0 but require one after 1.0.",
            },
        )

    def copy_fixture(self, name: str, temporary_root: Path) -> Path:
        destination = temporary_root / name
        destination.mkdir(parents=True)
        write_files(destination, FIXTURE_FILES[name])
        return destination

    def write_independent_bundle(self, root: Path, *, malformed: bool = False) -> Path:
        bundle = root / ("malformed" if malformed else "valid")
        write_files(
            bundle,
            {
                "index.md": "- [Alpha](alpha.md)\n",
                "alpha.md": (
                    "---\ntype: Note\ntitle: Alpha\n---\nReadable content.\n"
                    if not malformed
                    else "---\ntype: Note\ntitle: Alpha\n---\nReadable content.\n"
                ),
            },
        )
        if malformed:
            (bundle / "index.md").write_text("index\n", encoding="utf-8")
            (bundle / "unterminated.md").write_text(
                "---\ntype: Note\ntitle: Incomplete\nReadable content remains available.\n",
                encoding="utf-8",
            )
        return bundle

    def invoke(self, command: str, bundle: Path) -> tuple[int, dict, str]:
        arguments = [*COMMANDS[command]]
        arguments.insert(1, str(bundle))
        exit_code, stdout, stderr = run_main([*arguments, "--json"])
        return exit_code, json.loads(stdout), stderr

    def installed_command(self, command: str, bundle: Path) -> list[str]:
        arguments = [*COMMANDS[command]]
        arguments.insert(1, str(bundle))
        return arguments + ["--json"]

    def build_wheel(self, artifact_dir: Path) -> Path:
        self.build_artifacts(artifact_dir, formats=("--wheel",))
        wheels = sorted(artifact_dir.glob("mira_okf-*.whl"))
        self.assertEqual(len(wheels), 1)
        return wheels[0]

    def build_artifacts(
        self, artifact_dir: Path, *, formats: tuple[str, ...] = ("--sdist", "--wheel"), epoch: str | None = None
    ) -> tuple[Path, ...]:
        repository = Path(__file__).resolve().parents[1]
        command = [sys.executable, "-m", "build", *formats, "--no-isolation", "--outdir", str(artifact_dir)]
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment["PIP_NO_INDEX"] = "1"
        if epoch is not None:
            environment["SOURCE_DATE_EPOCH"] = epoch
        with tempfile.TemporaryDirectory() as source_dir:
            source = Path(source_dir) / repository.name
            shutil.copytree(
                repository,
                source,
                ignore=shutil.ignore_patterns(".git", ".venv", "build", "dist", "*.egg-info", "__pycache__"),
            )
            result = subprocess.run(command, cwd=source, env=environment, capture_output=True, text=True)
        if result.returncode != 0 and "No module named build.__main__" in result.stderr:
            self.skipTest("PEP 517 prerequisite unavailable: python -m build is not installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        return tuple(sorted(artifact_dir.iterdir()))

    def assert_metadata(self, metadata: Parser) -> None:
        self.assertEqual(metadata["Name"], PUBLIC_DISTRIBUTION["distribution"])
        self.assertEqual(metadata["Version"], PUBLIC_DISTRIBUTION["version"])
        self.assertEqual(metadata["Requires-Python"], PUBLIC_DISTRIBUTION["python"])
        self.assertEqual(metadata["Maintainer"], PUBLIC_DISTRIBUTION["maintainer"])
        self.assertEqual(metadata["License-Expression"], "MIT")
        self.assertEqual(metadata["License-File"], "LICENSE")
        self.assertEqual(metadata["Description-Content-Type"], "text/markdown")
        self.assertEqual(metadata.get_payload().strip(), README.strip())
        self.assertIn("Project-URL: Repository, " + PUBLIC_DISTRIBUTION["repository_url"], metadata.as_string())
        self.assertIn("Project-URL: Documentation, " + PUBLIC_DISTRIBUTION["documentation_url"], metadata.as_string())
        self.assertIn("Project-URL: Issues, " + PUBLIC_DISTRIBUTION["issues_url"], metadata.as_string())

    def assert_forbidden_content_absent(self, names: list[str], contents: list[bytes]) -> None:
        forbidden = (
            "bundles/", ".git", ".agents", ".codex", "fixtures", "private prompt",
            "agents.md", ".github/", "tests/", "spec-driven-development/", "mulher de luxo",
        )
        for name, content in zip(names, contents):
            lowered = name.lower()
            self.assertFalse(lowered.startswith("/"), name)
            self.assertNotIn("../", name)
            self.assertNotIn("\\..\\", name)
            self.assertFalse(any(token in lowered for token in forbidden), name)
            text = content.decode("utf-8", errors="ignore").lower()
            self.assertNotIn("mulher de luxo", text, name)
            self.assertNotRegex(text, r"(?:/home/|/documentos/|/repositorios/|/bases de conhecimento/)", name)

    def inspect_sdist(self, artifact: Path) -> tuple[list[str], list[bytes]]:
        with tarfile.open(artifact) as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            contents = [archive.extractfile(member).read() if member.isfile() else b"" for member in members]
            root = f"mira_okf-{PUBLIC_DISTRIBUTION['version']}"
            self.assertIn(f"{root}/README.md", names)
            self.assertIn(f"{root}/LICENSE", names)
            self.assertIn(f"{root}/pyproject.toml", names)
            self.assertIn(f"{root}/src/mira_okf/__init__.py", names)
            self.assertIn(f"{root}/src/mira_okf/cli.py", names)
            self.assertIn(f"{root}/src/mira_okf/__main__.py", names)
            metadata = Parser().parsestr(archive.extractfile(f"{root}/PKG-INFO").read().decode())
            self.assert_metadata(metadata)
            project = tomllib.loads(archive.extractfile(f"{root}/pyproject.toml").read().decode())["project"]
            self.assertEqual(project["scripts"][PUBLIC_DISTRIBUTION["cli"]], "mira_okf.cli:main")
            self.assertEqual(archive.extractfile(f"{root}/README.md").read().decode(), README)
        self.assert_forbidden_content_absent(names, contents)
        return names, contents

    def inspect_wheel(self, artifact: Path) -> tuple[list[str], list[bytes]]:
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
            contents = [archive.read(name) for name in names]
            self.assertIn("mira_okf/__init__.py", names)
            self.assertIn("mira_okf/cli.py", names)
            self.assertIn("mira_okf/__main__.py", names)
            license_names = [name for name in names if name.endswith("/LICENSE") or name == "LICENSE"]
            self.assertTrue(license_names)
            metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
            record_name = next(name for name in names if name.endswith(".dist-info/RECORD"))
            entry_points_name = next(name for name in names if name.endswith(".dist-info/entry_points.txt"))
            self.assert_metadata(Parser().parsestr(archive.read(metadata_name).decode()))
            entry_points = configparser.ConfigParser()
            entry_points.read_string(archive.read(entry_points_name).decode())
            self.assertEqual(entry_points["console_scripts"][PUBLIC_DISTRIBUTION["cli"]], "mira_okf.cli:main")
            recorded = {row[0] for row in reader(archive.read(record_name).decode().splitlines())}
            self.assertEqual(recorded, set(names))
        self.assert_forbidden_content_absent(names, contents)
        return names, contents

    def test_built_source_and_wheel_contain_only_public_distribution_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts = self.build_artifacts(Path(tmpdir))
            sdists = [path for path in artifacts if path.name.endswith(".tar.gz")]
            wheels = [path for path in artifacts if path.name.endswith(".whl")]
            self.assertEqual([path.name for path in sdists], ["mira_okf-0.0.1a2.tar.gz"])
            self.assertEqual([path.name for path in wheels], ["mira_okf-0.0.1a2-py3-none-any.whl"])
            self.inspect_sdist(sdists[0])
            self.inspect_wheel(wheels[0])

    def test_project_metadata_uses_readme_and_approved_public_inputs(self) -> None:
        self.assertEqual(PROJECT_METADATA["name"], PUBLIC_DISTRIBUTION["distribution"])
        self.assertEqual(PROJECT_METADATA["version"], PUBLIC_DISTRIBUTION["version"])
        self.assertEqual(PROJECT_METADATA["readme"], "README.md")
        self.assertEqual(PROJECT_METADATA["license"], "MIT")
        self.assertEqual(PROJECT_METADATA["maintainers"], [{"name": PUBLIC_DISTRIBUTION["maintainer"]}])
        self.assertEqual(PROJECT_METADATA["requires-python"], PUBLIC_DISTRIBUTION["python"])
        self.assertEqual(PROJECT["project"]["urls"], {
            "Repository": PUBLIC_DISTRIBUTION["repository_url"],
            "Documentation": PUBLIC_DISTRIBUTION["documentation_url"],
            "Issues": PUBLIC_DISTRIBUTION["issues_url"],
        })
        self.assertEqual(PROJECT["project"]["scripts"], {"mira-okf": "mira_okf.cli:main"})
        self.assertEqual(PROJECT_METADATA["description"], "Local, read-only Python library and CLI for inspecting Open Knowledge Format bundles.")
        self.assertNotRegex(README, r"(?i)(?:/home/|/documentos/|private prompt|hosted operation|package index)")

    def test_pep517_artifacts_are_reproducible_with_fixed_epoch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = root / "first"
            second = root / "second"
            first.mkdir()
            second.mkdir()
            self.build_artifacts(first, epoch="1700000000")
            self.build_artifacts(second, epoch="1700000000")

            left_wheel = next(first.glob("*.whl"))
            right_wheel = next(second.glob("*.whl"))
            self.assertEqual(left_wheel.name, right_wheel.name)
            self.assertEqual(left_wheel.read_bytes(), right_wheel.read_bytes())
            self.assertEqual(hashlib.sha256(left_wheel.read_bytes()).digest(), hashlib.sha256(right_wheel.read_bytes()).digest())

            left_sdist = next(first.glob("*.tar.gz"))
            right_sdist = next(second.glob("*.tar.gz"))
            self.assertEqual(left_sdist.name, right_sdist.name)
            with tarfile.open(left_sdist) as left_archive, tarfile.open(right_sdist) as right_archive:
                left_members = {member.name: member for member in left_archive.getmembers()}
                right_members = {member.name: member for member in right_archive.getmembers()}
                self.assertEqual(set(left_members), set(right_members))
                timestamp_differences = []
                for name in sorted(left_members):
                    left_member = left_members[name]
                    right_member = right_members[name]
                    self.assertEqual(
                        left_archive.extractfile(left_member).read() if left_member.isfile() else None,
                        right_archive.extractfile(right_member).read() if right_member.isfile() else None,
                        name,
                    )
                    for field in ("mtime", "mode", "uid", "gid", "uname", "gname"):
                        if getattr(left_member, field) != getattr(right_member, field):
                            timestamp_differences.append((name, field))
                self.assertTrue(timestamp_differences)
                self.assertTrue(all(field == "mtime" for _, field in timestamp_differences), timestamp_differences)
                self.assertEqual(self.inspect_sdist(left_sdist)[0], self.inspect_sdist(right_sdist)[0])

    def test_installed_console_smoke_uses_built_wheel_outside_checkout(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact_dir = root / "artifacts"
            artifact_dir.mkdir()
            wheel = self.build_wheel(artifact_dir)
            environment = root / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(environment)], check=True)
            python = environment / "bin" / "python"
            bin_dir = environment / "bin"
            install_result = subprocess.run(
                [str(python), "-m", "pip", "install", "--force-reinstall", "--no-index", "--no-deps", str(wheel)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(install_result.returncode, 0, install_result.stderr)
            run_environment = os.environ.copy()
            run_environment.pop("PYTHONPATH", None)
            run_environment.update(
                PATH=f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
                PYTHONNOUSERSITE="1",
            )
            origin_result = subprocess.run(
                [str(python), "-c", "import mira_okf; print(mira_okf.__file__)"],
                cwd=root,
                env=run_environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(origin_result.returncode, 0, origin_result.stderr)
            origin = origin_result.stdout.strip()
            self.assertNotIn(str(repository), origin)
            self.assertTrue(Path(origin).is_relative_to(environment), origin)
            installed_entry_point = shutil.which("mira-okf", path=str(bin_dir))
            self.assertEqual(installed_entry_point, str(bin_dir / "mira-okf"))

            grouped_result = subprocess.run(
                ["mira-okf", "okf", "tree", ".", "--json"],
                cwd=root,
                env=run_environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(grouped_result.returncode, 0)
            self.assertEqual(grouped_result.stdout, "")

            valid = self.write_independent_bundle(root)
            malformed = self.write_independent_bundle(root, malformed=True)
            workdir = root / "unrelated-workdir"
            workdir.mkdir()

            for command in COMMANDS:
                result = subprocess.run(
                    ["mira-okf", *self.installed_command(command, valid)],
                    cwd=workdir,
                    env=run_environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, command)
                self.assertEqual(result.stderr, "", command)
                payload = json.loads(result.stdout)
                self.assertTrue(payload["ok"], command)
                self.assertEqual(payload["command"], f"okf.{command}", command)

                result = subprocess.run(
                    ["mira-okf", *self.installed_command(command, malformed)],
                    cwd=workdir,
                    env=run_environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, command)
                issue_payload = json.loads(result.stdout)
                self.assertTrue(issue_payload["ok"], command)
                self.assertTrue(issue_payload["issues"], command)

                result = subprocess.run(
                    ["mira-okf", *self.installed_command(command, root / "missing")],
                    cwd=workdir,
                    env=run_environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 1, command)
                fatal_payload = json.loads(result.stdout)
                self.assertFalse(fatal_payload["ok"], command)
                self.assertEqual(fatal_payload["error"]["code"], "OKF_BUNDLE_NOT_FOUND", command)

    def test_all_supported_commands_have_human_and_json_success_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle = self.copy_fixture("valid", Path(tmpdir))
            for command in COMMANDS:
                exit_code, payload, stderr = self.invoke(command, bundle)
                self.assertEqual(exit_code, 0, command)
                self.assertEqual(stderr, "", command)
                self.assertEqual(
                    set(payload), {"ok", "command", "bundle", "data", "issues"}, command
                )
                self.assertTrue(payload["ok"], command)
                self.assertEqual(payload["command"], f"okf.{command}")

                human_args = [*COMMANDS[command]]
                human_args.insert(1, str(bundle))
                human_exit, human_stdout, human_stderr = run_main(human_args)
                self.assertEqual(human_exit, 0, command)
                self.assertEqual(human_stderr, "", command)
                self.assertTrue(human_stdout.strip(), command)

    def test_empty_and_deterministic_success_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            empty = self.copy_fixture("empty", Path(tmpdir))
            for command in ("tree", "list", "links", "props", "validate", "health"):
                exit_code, payload, stderr = self.invoke(command, empty)
                self.assertEqual(exit_code, 0, command)
                self.assertEqual(stderr, "", command)
                self.assertTrue(payload["ok"], command)

            valid = self.copy_fixture("valid", Path(tmpdir))
            for command in COMMANDS:
                first = self.invoke(command, valid)
                second = self.invoke(command, valid)
                self.assertEqual(first, second, command)

            _, listing, _ = self.invoke("list", valid)
            self.assertEqual(
                [concept["concept_id"] for concept in listing["data"]["concepts"]],
                ["alpha", "nested/beta", "nested/gamma"],
            )
            _, links, _ = self.invoke("links", valid)
            self.assertEqual(
                [link["source_path"] for link in links["data"]["links"]],
                ["alpha.md", "alpha.md", "nested/beta.md"],
            )

    def test_content_issues_are_non_fatal_and_readable_data_remains_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            malformed = self.copy_fixture("malformed-readable", Path(tmpdir))
            for command in COMMANDS:
                exit_code, payload, stderr = self.invoke(command, malformed)
                self.assertEqual(exit_code, 0, command)
                self.assertEqual(stderr, "", command)
                self.assertTrue(payload["ok"], command)
                self.assertTrue(payload["issues"], command)

            _, listing, _ = self.invoke("list", malformed)
            self.assertEqual(
                [concept["concept_id"] for concept in listing["data"]["concepts"]],
                ["alpha", "unterminated"],
            )
            _, shown, _ = self.invoke("show", malformed)
            self.assertEqual(shown["data"]["concept_id"], "alpha")

    def test_invalid_and_ambiguous_inputs_are_fatal_with_shared_failure_envelopes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            invalid = self.copy_fixture("invalid", root)
            _, invalid_validation, _ = self.invoke("validate", invalid)
            self.assertTrue(invalid_validation["ok"])
            self.assertFalse(invalid_validation["data"]["passed"])

            ambiguous = self.copy_fixture("ambiguous", root)
            for command in COMMANDS:
                arguments = [*COMMANDS[command]]
                exit_code, stdout, stderr = run_main([*arguments, "--json"], cwd=ambiguous)
                self.assertEqual(exit_code, 1, command)
                self.assertEqual(stderr, "", command)
                payload = json.loads(stdout)
                self.assertEqual(
                    set(payload),
                    {"ok", "command", "bundle", "data", "issues", "error"},
                    command,
                )
                self.assertFalse(payload["ok"], command)
                self.assertEqual(payload["error"]["code"], "OKF_DISCOVERY_AMBIGUOUS", command)

            for command in COMMANDS:
                arguments = [*COMMANDS[command], "/no/such/bundle"]
                if command in {"show", "backlinks"}:
                    arguments = [command, "/no/such/bundle", "alpha"]
                exit_code, stdout, stderr = run_main([*arguments, "--json"])
                self.assertEqual(exit_code, 1, command)
                self.assertEqual(stderr, "", command)
                self.assertEqual(json.loads(stdout)["error"]["code"], "OKF_BUNDLE_NOT_FOUND", command)


if __name__ == "__main__":
    unittest.main()
