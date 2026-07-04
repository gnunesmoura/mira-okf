from __future__ import annotations

import json
import re
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

from .models import Bundle, Concept, Directory, Issue

RESERVED_FILENAMES = {"index.md", "log.md"}


class OkfError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def run_tree(args: Namespace) -> int:
    try:
        bundle = _resolve_bundle(args.bundle, getattr(args, "depth", 2))
        bundle, root_directory = _scan_bundle(bundle, args.depth)
    except OkfError as error:
        return _emit_error(args, error)

    payload = {
        "ok": True,
        "command": "okf.tree",
        "bundle": _bundle_payload(bundle),
        "data": _directory_payload(root_directory),
        "issues": [_issue_payload(issue) for issue in bundle.issues],
    }
    _emit_payload(args, payload)
    return 0


def _emit_error(args: Namespace, error: OkfError) -> int:
    payload = {
        "ok": False,
        "command": "okf.tree",
        "bundle": None,
        "data": None,
        "issues": [],
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    }
    if getattr(args, "json", False):
        _emit_payload(args, payload)
    else:
        print(error.message, file=sys.stderr)
        details = error.details.get("candidates", [])
        for candidate in details:
            print(f"- {candidate['path']} -> {candidate['command']}", file=sys.stderr)
    return 1


def _emit_payload(args: Namespace, payload: dict[str, Any]) -> None:
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return
    if not payload["ok"]:
        return
    print(_render_directory_summary(payload["data"], 0))


def _resolve_bundle(bundle_argument: str | None, depth: int) -> Bundle:
    cwd = Path.cwd().resolve()
    if bundle_argument:
        candidate_input = Path(bundle_argument).expanduser()
        bundle_path = (cwd / candidate_input).resolve() if not candidate_input.is_absolute() else candidate_input.resolve()
        if not bundle_path.exists() or not bundle_path.is_dir():
            raise OkfError("OKF_BUNDLE_NOT_FOUND", f"OKF bundle not found: {bundle_argument}")
        relative_path = _display_path(bundle_argument, bundle_path, cwd)
        return Bundle(root_path=bundle_path, relative_path=relative_path, source_kind="explicit", source_path=bundle_path)

    candidates = _discover_bundles(cwd)
    if not candidates:
        raise OkfError("OKF_BUNDLE_NOT_FOUND", "No OKF bundle found in the current directory.")
    if len(candidates) > 1:
        raise OkfError(
            "OKF_DISCOVERY_AMBIGUOUS",
            "More than one OKF bundle found. Provide the path explicitly:",
            {
                "candidates": [
                    {
                        "path": _display_path(str(path.relative_to(cwd)) if path != cwd else ".", path, cwd),
                        "command": f"tooling okf tree {_display_path(str(path.relative_to(cwd)) if path != cwd else '.', path, cwd)} --depth {depth} --summary",
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


def _discover_bundles(cwd: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in _walk_directories(cwd):
        if _is_bundle_root(path):
            candidates.append(path)
    return candidates


def _walk_directories(root: Path) -> list[Path]:
    directories = [root.resolve()]
    for child in sorted((candidate for candidate in root.iterdir() if candidate.is_dir()), key=lambda candidate: candidate.name):
        directories.extend(_walk_directories(child))
    return directories


def _is_bundle_root(path: Path) -> bool:
    if (path / "index.md").is_file():
        return True
    return any(_is_candidate_concept(file_path) for file_path in path.iterdir() if file_path.is_file())


def _is_candidate_concept(path: Path) -> bool:
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


def _scan_bundle(bundle: Bundle, max_depth: int) -> tuple[Bundle, Directory]:
    root_directory, concepts, issues = _scan_directory(bundle.root_path, bundle.relative_path, 0, max(0, max_depth), bundle.root_path)
    return (
        Bundle(
            root_path=bundle.root_path,
            relative_path=bundle.relative_path,
            source_kind=bundle.source_kind,
            source_path=bundle.source_path,
            concepts=concepts,
            directories=_collect_directories(root_directory),
            issues=issues,
            has_root_index=root_directory.has_index,
            has_root_log=root_directory.has_log,
            root_index_issues=[issue for issue in root_directory.issues if issue.code.startswith("OKF_ROOT_INDEX")],
            root_log_issues=[issue for issue in root_directory.issues if issue.code.startswith("OKF_ROOT_LOG")],
        ),
        root_directory,
    )


def _scan_directory(path: Path, display_path: str, depth: int, max_depth: int, root_path: Path) -> tuple[Directory, list[Concept], list[Issue]]:
    issues: list[Issue] = []
    directory_concepts: list[Concept] = []
    concepts: list[Concept] = []
    children: list[Directory] = []

    has_index = (path / "index.md").is_file()
    has_log = (path / "log.md").is_file()

    if depth < max_depth:
        for child_path in sorted((candidate for candidate in path.iterdir() if candidate.is_dir()), key=lambda candidate: candidate.name):
            child_relative = _relative_display_path(child_path, root_path)
            child_directory, child_concepts, child_issues = _scan_directory(child_path, child_relative, depth + 1, max_depth, root_path)
            children.append(child_directory)
            concepts.extend(child_concepts)
            issues.extend(child_issues)

    for file_path in sorted((candidate for candidate in path.iterdir() if _is_concept_file(candidate)), key=lambda candidate: candidate.name):
        concept = _read_concept(file_path, root_path, display_path)
        directory_concepts.append(concept)
        concepts.append(concept)
        issues.extend(concept.issues)

    directory_concepts.sort(key=lambda concept: concept.concept_id)
    concepts.sort(key=lambda concept: concept.concept_id)
    children.sort(key=lambda directory: directory.path)

    directory = Directory(
        path=display_path,
        absolute_path=path,
        name=path.name or path.resolve().name,
        depth=depth,
        has_index=has_index,
        has_log=has_log,
        concept_count=len(directory_concepts),
        directory_count=len(children) if depth < max_depth else 0,
        children=children,
        concepts=directory_concepts,
        issues=issues,
    )
    return directory, concepts, issues


def _is_concept_file(path: Path) -> bool:
    return path.is_file() and path.suffix == ".md" and path.name not in RESERVED_FILENAMES


def _read_concept(path: Path, root_path: Path, directory_label: str) -> Concept:
    relative_path = _relative_display_path(path, root_path)
    directory = relative_path.rsplit("/", 1)[0] if "/" in relative_path else directory_label
    frontmatter, issues = _read_frontmatter(path, relative_path)
    title = _scalar_text(frontmatter.get("title")) or _title_from_filename(path.stem)
    concept_type = _scalar_text(frontmatter.get("type"))
    if not concept_type:
        issues.append(
            Issue(
                code="OKF_CONCEPT_MISSING_TYPE",
                message="Concept frontmatter is missing required type.",
                path=relative_path,
                field="type",
                suggestion="Add a non-empty type in frontmatter.",
            )
        )
    return Concept(
        concept_id=relative_path.removesuffix(".md"),
        path=path,
        relative_path=relative_path,
        directory=directory,
        filename=path.name,
        type=concept_type,
        title=title,
        description=_scalar_text(frontmatter.get("description")),
        resource=_scalar_text(frontmatter.get("resource")),
        tags=_normalize_tags(frontmatter.get("tags")),
        timestamp=_scalar_text(frontmatter.get("timestamp")),
        body="",
        frontmatter=frontmatter,
        issues=issues,
    )


def _read_frontmatter(path: Path, relative_path: str) -> tuple[dict[str, Any], list[Issue]]:
    issues: list[Issue] = []
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            if handle.readline().strip() != "---":
                issues.append(
                    Issue(
                        code="OKF_FRONTMATTER_MISSING",
                        message="Concept is missing frontmatter.",
                        path=relative_path,
                    )
                )
                return {}, issues
            raw_lines: list[str] = []
            for line in handle:
                if line.strip() == "---":
                    return _parse_frontmatter(raw_lines), issues
                raw_lines.append(line.rstrip("\n"))
    except OSError as error:
        issues.append(
            Issue(
                code="OKF_CONCEPT_READ_ERROR",
                message=str(error),
                severity="error",
                path=relative_path,
                fatal=False,
            )
        )
        return {}, issues
    issues.append(
        Issue(
            code="OKF_FRONTMATTER_UNTERMINATED",
            message="Concept frontmatter is missing a closing delimiter.",
            path=relative_path,
        )
    )
    return _parse_frontmatter(raw_lines), issues


def _parse_frontmatter(lines: list[str]) -> dict[str, Any]:
    frontmatter: dict[str, Any] = {}
    current_key: str | None = None
    list_items: list[str] | None = None
    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if list_items is not None and raw_line.startswith("  - "):
            list_items.append(_parse_scalar(raw_line[4:]))
            continue
        if list_items is not None and raw_line.startswith("- "):
            list_items.append(_parse_scalar(raw_line[2:]))
            continue
        if list_items is not None:
            frontmatter[current_key or ""] = list_items
            list_items = None
            current_key = None
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not value:
            current_key = key
            list_items = []
            continue
        frontmatter[key] = _parse_scalar(value)
    if list_items is not None and current_key is not None:
        frontmatter[current_key] = list_items
    return frontmatter


def _parse_scalar(value: str) -> str | list[str]:
    if value.startswith("[") and value.endswith("]"):
        return [item for item in (_parse_scalar(part.strip()) for part in value[1:-1].split(",")) if item]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def _scalar_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or None
    text = str(value).strip()
    return text or None


def _title_from_filename(stem: str) -> str:
    return re.sub(r"[_-]+", " ", stem).strip().title() or stem


def _relative_display_path(path: Path, root_path: Path) -> str:
    relative = path.relative_to(root_path).as_posix()
    return relative


def _display_path(input_path: str, resolved_path: Path, cwd: Path) -> str:
    if input_path == ".":
        return "."
    if resolved_path.is_absolute() and Path(input_path).is_absolute():
        return str(Path(input_path))
    try:
        return resolved_path.relative_to(cwd).as_posix()
    except ValueError:
        return input_path


def _bundle_payload(bundle: Bundle) -> dict[str, Any]:
    return {
        "root_path": str(bundle.root_path),
        "relative_path": bundle.relative_path,
        "source_kind": bundle.source_kind,
        "source_path": str(bundle.source_path),
        "has_root_index": bundle.has_root_index,
        "has_root_log": bundle.has_root_log,
        "okf_version": bundle.okf_version,
    }


def _directory_payload(directory: Directory) -> dict[str, Any]:
    return {
        "path": directory.path,
        "absolute_path": str(directory.absolute_path),
        "name": directory.name,
        "depth": directory.depth,
        "has_index": directory.has_index,
        "has_log": directory.has_log,
        "concept_count": directory.concept_count,
        "directory_count": directory.directory_count,
        "children": [_directory_payload(child) for child in directory.children],
        "concepts": [_concept_payload(concept) for concept in directory.concepts],
        "issues": [_issue_payload(issue) for issue in directory.issues],
    }


def _concept_payload(concept: Concept) -> dict[str, Any]:
    return {
        "concept_id": concept.concept_id,
        "path": str(concept.path),
        "relative_path": concept.relative_path,
        "directory": concept.directory,
        "filename": concept.filename,
        "type": concept.type,
        "title": concept.title,
        "description": concept.description,
        "resource": concept.resource,
        "tags": concept.tags,
        "timestamp": concept.timestamp,
        "body": concept.body,
        "frontmatter": concept.frontmatter,
        "issues": [_issue_payload(issue) for issue in concept.issues],
    }


def _issue_payload(issue: Issue) -> dict[str, Any]:
    return {
        "code": issue.code,
        "message": issue.message,
        "severity": issue.severity,
        "path": issue.path,
        "line": issue.line,
        "field": issue.field,
        "suggestion": issue.suggestion,
        "fatal": issue.fatal,
    }


def _render_directory_summary(directory: dict[str, Any], indent: int) -> str:
    label = directory["path"] if indent == 0 else directory["name"]
    line = f"{'  ' * indent}{label or directory['name']}/"
    if directory["has_index"]:
        line += "  index.md"
    if directory["has_log"]:
        line += "  log.md"
    line += f"  concepts: {directory['concept_count']}"
    lines = [line]
    for child in directory["children"]:
        lines.append(_render_directory_summary(child, indent + 1))
    return "\n".join(lines)


def _collect_directories(directory: Directory) -> list[Directory]:
    collected = [directory]
    for child in directory.children:
        collected.extend(_collect_directories(child))
    return collected
