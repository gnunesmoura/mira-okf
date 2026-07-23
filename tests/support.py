from __future__ import annotations

import contextlib
import io
import os
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mira_okf.cli import main


def write_files(root: Path, files: dict[str, str]) -> None:
    for relative_path, contents in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")


def run_main(argv: Sequence[str], cwd: Path | None = None) -> tuple[int, str, str]:
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


class NoPyMarkdown:
    """Context manager that makes `pymarkdown` unimportable for its duration."""

    def __init__(self) -> None:
        self._saved: dict[str, object] = {}

    def __enter__(self) -> "NoPyMarkdown":
        self._saved = {key: sys.modules.get(key) for key in list(sys.modules) if key == "pymarkdown" or key.startswith("pymarkdown.")}
        for key in list(sys.modules):
            if key == "pymarkdown" or key.startswith("pymarkdown."):
                del sys.modules[key]

        from importlib.machinery import ModuleSpec

        class _Blocker:
            def find_spec(self, fullname: str, path=None, target=None):
                if fullname == "pymarkdown" or fullname.startswith("pymarkdown."):
                    return ModuleSpec(fullname, None)
                return None

        self._blocker = _Blocker()
        sys.meta_path.insert(0, self._blocker)
        return self

    def __exit__(self, *exc) -> None:
        sys.meta_path.remove(self._blocker)
        for key in list(sys.modules):
            if key == "pymarkdown" or key.startswith("pymarkdown."):
                del sys.modules[key]
        for key, value in self._saved.items():
            if value is not None:
                sys.modules[key] = value
