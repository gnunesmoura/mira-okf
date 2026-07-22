from __future__ import annotations

import posixpath
from pathlib import Path, PurePosixPath
from typing import Any

from .models import Bundle, Concept
from .read_model import _is_hidden

RESERVED_FILENAMES = {"index.md", "log.md"}


class BundleResolutionError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class ConceptResolutionError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def resolve_bundle(bundle_argument: str | None, command: str, reference_suffix: str = "") -> Bundle:
    cwd = Path.cwd().resolve()
    if bundle_argument:
        candidate_input = Path(bundle_argument).expanduser()
        bundle_path = (cwd / candidate_input).resolve() if not candidate_input.is_absolute() else candidate_input.resolve()
        if not bundle_path.exists() or not bundle_path.is_dir():
            raise BundleResolutionError("OKF_BUNDLE_NOT_FOUND", f"OKF bundle not found: {bundle_argument}")
        relative_path = _display_path(bundle_argument, bundle_path, cwd)
        return Bundle(root_path=bundle_path, relative_path=relative_path, source_kind="explicit", source_path=bundle_path)

    candidates = _discover_bundles(cwd)
    if not candidates:
        raise BundleResolutionError("OKF_BUNDLE_NOT_FOUND", "No OKF bundle found in the current directory.")
    if len(candidates) > 1:
        raise BundleResolutionError(
            "OKF_DISCOVERY_AMBIGUOUS",
            "More than one OKF bundle found. Provide the path explicitly:",
            {
                "candidates": [
                    {
                        "path": _display_path(str(path.relative_to(cwd)) if path != cwd else ".", path, cwd),
                        "command": _reference_command(command, path, cwd, reference_suffix),
                    }
                    for path in candidates
                ],
            },
        )
    path = candidates[0]
    return Bundle(
        root_path=path,
        relative_path=_display_path(str(path.relative_to(cwd)) if path != cwd else ".", path, cwd),
        source_kind="discovered",
        source_path=path,
    )


def resolve_concept(bundle: Bundle, target: str) -> Concept:
    concepts_by_id = {concept.concept_id: concept for concept in bundle.concepts}
    concepts_by_relative = {concept.relative_path: concept for concept in bundle.concepts}

    normalized_target = target.strip().lstrip("/").replace("\\", "/")
    candidates = [normalized_target]
    if normalized_target.endswith(".md"):
        candidates.append(normalized_target.removesuffix(".md"))
    else:
        candidates.append(f"{normalized_target}.md")

    for candidate in candidates:
        if concept := concepts_by_id.get(candidate) or concepts_by_relative.get(candidate):
            if _is_hidden(concept.relative_path):
                break
            return concept

    raise ConceptResolutionError(
        "OKF_CONCEPT_NOT_FOUND",
        f"Concept not found: {target}",
        {"target": target},
    )


def _reference_command(command: str, path: Path, cwd: Path, reference_suffix: str) -> str:
    bundle_path = _display_path(str(path.relative_to(cwd)) if path != cwd else ".", path, cwd)
    suffix = f" {reference_suffix}" if reference_suffix else ""
    return f"mira-okf {command} {bundle_path}{suffix}"


def _discover_bundles(cwd: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in _walk_directories(cwd):
        if _is_bundle_root(path):
            candidates.append(path)
    return candidates


def _walk_directories(root: Path) -> list[Path]:
    directories = [root.resolve()]
    for child in sorted((candidate for candidate in root.iterdir() if candidate.is_dir()), key=lambda candidate: candidate.name):
        if _is_hidden(str(child.relative_to(root))):
            continue
        directories.extend(_walk_directories(child))
    return directories


def _is_bundle_root(path: Path) -> bool:
    if (path / "index.md").is_file():
        return True
    return any(_is_candidate_concept(file_path) for file_path in path.iterdir() if file_path.is_file())


def _is_candidate_concept(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    return path.suffix == ".md" and path.name not in RESERVED_FILENAMES and _has_frontmatter(path)


def _has_frontmatter(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            if handle.readline().strip() != "---":
                return False
            for line in handle:
                if line.strip() == "---":
                    return True
    except OSError:
        return False
    return False


def link_candidates(source_path: str, target: str) -> list[str]:
    root_relative = target.startswith("/")
    target = clean_internal_path(target)
    if not root_relative and source_path:
        parent = PurePosixPath(source_path).parent
        target = clean_internal_path((parent / target).as_posix())

    candidates = [target]
    if target.endswith(".md"):
        candidates.append(target.removesuffix(".md"))
    else:
        candidates.append(f"{target}.md")
    normalized = []
    for candidate in candidates:
        if candidate and candidate not in normalized:
            normalized.append(candidate)
    return normalized


def clean_internal_path(path: str) -> str:
    cleaned = posixpath.normpath(path.replace("\\", "/"))
    return "" if cleaned == "." else cleaned.lstrip("/")


def _display_path(input_path: str, resolved_path: Path, cwd: Path) -> str:
    if input_path == ".":
        return "."
    if resolved_path.is_absolute() and Path(input_path).is_absolute():
        return str(Path(input_path))
    try:
        return resolved_path.relative_to(cwd).as_posix()
    except ValueError:
        return input_path
