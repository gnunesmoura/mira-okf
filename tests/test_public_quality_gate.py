from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import configparser
import contextlib
import io
import tarfile
import tempfile
import unittest
import zipfile
from email.parser import Parser
from pathlib import Path
import tomllib

from tests.support import run_main


FIXTURES = Path(__file__).parent / "fixtures"
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


class PublicQualityGateTest(unittest.TestCase):
    def copy_fixture(self, name: str, temporary_root: Path) -> Path:
        destination = temporary_root / name
        shutil.copytree(FIXTURES / name, destination)
        return destination

    def invoke(self, command: str, bundle: Path) -> tuple[int, dict, str]:
        arguments = ["okf", *COMMANDS[command]]
        arguments.insert(2, str(bundle))
        exit_code, stdout, stderr = run_main([*arguments, "--json"])
        return exit_code, json.loads(stdout), stderr

    def installed_command(self, command: str, bundle: Path) -> list[str]:
        arguments = ["okf", *COMMANDS[command]]
        arguments.insert(2, str(bundle))
        return arguments + ["--json"]

    def build_wheel(self, artifact_dir: Path) -> Path:
        repository = Path(__file__).resolve().parents[1]
        build = [sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(artifact_dir)]
        if subprocess.run(build, cwd=repository, capture_output=True, text=True).returncode != 0:
            build = [sys.executable, "-m", "pip", "wheel", "--no-build-isolation", "--no-deps", "--wheel-dir", str(artifact_dir), "."]
            result = subprocess.run(build, cwd=repository, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        wheels = sorted(artifact_dir.glob("tooling-*.whl"))
        self.assertEqual(len(wheels), 1)
        return wheels[0]

    def build_artifacts(self, artifact_dir: Path) -> tuple[Path, Path]:
        from setuptools.build_meta import build_sdist, build_wheel

        with contextlib.redirect_stdout(io.StringIO()):
            sdist_name = build_sdist(str(artifact_dir))
            wheel_name = build_wheel(str(artifact_dir))
        return artifact_dir / sdist_name, artifact_dir / wheel_name

    def assert_public_artifact_paths(self, paths: list[str], *, source: bool) -> None:
        self.assertTrue(paths, "artifact is empty")
        forbidden = (".git/", ".agents/", ".codex/", "/fixtures/", "\\fixtures\\")
        for path in paths:
            self.assertFalse(path.startswith("/"), path)
            self.assertNotIn("../", path)
            self.assertNotIn("\\..\\", path)
            self.assertNotIn("Mulher de Luxo", path)
            self.assertFalse(any(token in path for token in forbidden), path)
        if source:
            self.assertIn("tooling-0.1.0/README.md", paths)
            self.assertIn("tooling-0.1.0/pyproject.toml", paths)
            self.assertIn("tooling-0.1.0/src/tooling/__init__.py", paths)
            self.assertIn("tooling-0.1.0/src/tooling/cli.py", paths)
            self.assertIn("tooling-0.1.0/src/tooling/__main__.py", paths)
            self.assertIn("tooling-0.1.0/setup.cfg", paths)
        else:
            self.assertIn("tooling/__init__.py", paths)
            self.assertIn("tooling/cli.py", paths)
            self.assertIn("tooling/__main__.py", paths)

    def test_built_source_and_wheel_contain_only_public_distribution_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdist, wheel = self.build_artifacts(Path(tmpdir))
            with tarfile.open(sdist) as archive:
                sdist_paths = archive.getnames()
                self.assert_public_artifact_paths(sdist_paths, source=True)
                metadata = Parser().parsestr(
                    archive.extractfile("tooling-0.1.0/PKG-INFO").read().decode("utf-8")
                )
                project = tomllib.loads(
                    archive.extractfile("tooling-0.1.0/pyproject.toml").read().decode("utf-8")
                )["project"]
                self.assertEqual(metadata["Name"], "tooling")
                self.assertEqual(metadata["Version"], "0.1.0")
                self.assertIn("# Tooling", metadata.get_payload())
                self.assertEqual(project["scripts"]["tooling"], "tooling.cli:main")

            with zipfile.ZipFile(wheel) as archive:
                wheel_paths = archive.namelist()
                self.assert_public_artifact_paths(wheel_paths, source=False)
                metadata_path = next(path for path in wheel_paths if path.endswith(".dist-info/METADATA"))
                entry_points_path = next(
                    path for path in wheel_paths if path.endswith(".dist-info/entry_points.txt")
                )
                metadata = Parser().parsestr(archive.read(metadata_path).decode("utf-8"))
                entry_points = configparser.ConfigParser()
                entry_points.read_string(archive.read(entry_points_path).decode("utf-8"))
                self.assertEqual(metadata["Name"], "tooling")
                self.assertEqual(metadata["Version"], "0.1.0")
                self.assertEqual(metadata["Requires-Python"], ">=3.12")
                self.assertIn("# Tooling", metadata.get_payload())
                self.assertEqual(entry_points["console_scripts"]["tooling"], "tooling.cli:main")

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
                [str(python), "-c", "import tooling; print(tooling.__file__)"],
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
            installed_entry_point = shutil.which("tooling", path=str(bin_dir))
            self.assertEqual(installed_entry_point, str(bin_dir / "tooling"))

            valid = self.copy_fixture("valid", root)
            malformed = self.copy_fixture("malformed-readable", root)
            workdir = root / "unrelated-workdir"
            workdir.mkdir()

            for command in COMMANDS:
                result = subprocess.run(
                    ["tooling", *self.installed_command(command, valid)],
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
                    ["tooling", *self.installed_command(command, malformed)],
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
                    ["tooling", *self.installed_command(command, root / "missing")],
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

                human_args = ["okf", *COMMANDS[command]]
                human_args.insert(2, str(bundle))
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
                arguments = ["okf", *COMMANDS[command]]
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
                arguments = ["okf", *COMMANDS[command], "/no/such/bundle"]
                if command in {"show", "backlinks"}:
                    arguments = ["okf", command, "/no/such/bundle", "alpha"]
                exit_code, stdout, stderr = run_main([*arguments, "--json"])
                self.assertEqual(exit_code, 1, command)
                self.assertEqual(stderr, "", command)
                self.assertEqual(json.loads(stdout)["error"]["code"], "OKF_BUNDLE_NOT_FOUND", command)


if __name__ == "__main__":
    unittest.main()
