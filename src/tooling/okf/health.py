from __future__ import annotations

import json
import re
import sys
from argparse import Namespace
from collections import Counter
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

from .links import _collect_links, _extract_links, _is_external_target, _link_candidates, _normalize_target
from .models import Bundle, Directory, Issue
from .read_model import _read_markdown_text, bundle_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, resolve_bundle
from .validate import _reserved_issues

METADATA_FIELDS = ("title", "description", "resource", "tags", "timestamp")


def run_health(args: Namespace) -> int:
    try:
        bundle = resolve_bundle(args.bundle, "health")
        bundle, _ = scan_bundle(bundle, None)
    except BundleResolutionError as error:
        return _emit_error(args, error)

    links, link_issues = _collect_links(bundle)
    reserved_issues = _reserved_issues(bundle.root_path)
    validation = _validation_data(bundle, reserved_issues)
    data = _health_data(bundle, validation, reserved_issues, links)
    payload = {
        "ok": True,
        "command": "okf.health",
        "bundle": bundle_payload(bundle),
        "data": data,
        "issues": [issue_payload(issue) for issue in sorted([*bundle.issues, *reserved_issues, *link_issues], key=_issue_key)],
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(_render_human(payload["bundle"]["relative_path"], data))
    return 0


def _validation_data(bundle: Bundle, reserved_issues: list[Issue]) -> dict[str, Any]:
    issues = [*bundle.issues, *reserved_issues]
    error_count = sum(1 for issue in issues if issue.severity == "error")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")
    info_count = sum(1 for issue in issues if issue.severity == "info")
    passed = error_count == 0 and warning_count == 0
    return {
        "passed": passed,
        "status": "pass" if passed else "fail",
        "issue_count": len(issues),
        "error_count": error_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "checked_file_count": sum(1 for _ in bundle.root_path.rglob("*.md")),
    }


def _health_data(bundle: Bundle, validation: dict[str, Any], reserved_issues: list[Issue], links: list[dict[str, Any]]) -> dict[str, Any]:
    reserved = _reserved_files(bundle, reserved_issues)
    indexes = _indexes(bundle)
    logs = _logs(bundle)
    metadata = _metadata(bundle)
    citations = _citations(bundle, links)
    connectivity = _connectivity(bundle, links)
    link_data = _links(links)
    warnings = (
        reserved["malformed_reserved_file_count"]
        + link_data["broken_internal_link_count"]
        + indexes["directories_without_index_count"]
        + indexes["unlisted_content_count"]
        + logs["malformed_date_heading_count"]
        + logs["ordering_issue_count"]
        + sum(field["missing_count"] for field in metadata["fields"])
        + citations["external_linked_without_citations_count"]
        + connectivity["orphan_concept_count"]
    )
    status = "invalid" if not validation["passed"] else "attention" if warnings else "ok"
    return {
        "status": status,
        "summary": {
            "status": status,
            "validation_passed": validation["passed"],
            "concept_count": len(bundle.concepts),
            "directory_count": len(bundle.directories),
            "warning_signal_count": warnings,
            "error_signal_count": 0,
        },
        "validation": validation,
        "inventory": _inventory(bundle),
        "reserved_files": reserved,
        "links": link_data,
        "indexes": indexes,
        "logs": logs,
        "metadata": metadata,
        "citations": citations,
        "connectivity": connectivity,
    }


def _inventory(bundle: Bundle) -> dict[str, Any]:
    counts = Counter(concept.type or "<missing>" for concept in bundle.concepts)
    return {
        "concept_count": len(bundle.concepts),
        "directory_count": len(bundle.directories),
        "reserved_file_count": sum(1 for path in bundle.root_path.rglob("*.md") if path.name in {"index.md", "log.md"}),
        "index_file_count": sum(1 for directory in bundle.directories if directory.has_index),
        "log_file_count": sum(1 for directory in bundle.directories if directory.has_log),
        "concept_types": [{"type": name, "count": counts[name]} for name in sorted(counts, key=str.casefold)],
    }


def _reserved_files(bundle: Bundle, reserved_issues: list[Issue]) -> dict[str, Any]:
    malformed = sorted({issue.path for issue in reserved_issues if issue.path}, key=_path_key)
    return {
        "root_index_present": bundle.has_root_index,
        "root_log_present": bundle.has_root_log,
        "index_issue_count": sum(1 for issue in reserved_issues if issue.path and issue.path.endswith("index.md")),
        "log_issue_count": sum(1 for issue in reserved_issues if issue.path and issue.path.endswith("log.md")),
        "malformed_reserved_file_count": len(malformed),
        "malformed_reserved_file_paths": malformed,
    }


def _links(links: list[dict[str, Any]]) -> dict[str, Any]:
    broken_sources = sorted({link["source_concept_id"] for link in links if link["broken"]}, key=str.casefold)
    return {
        "internal_link_count": sum(1 for link in links if not link["external"]),
        "resolved_internal_link_count": sum(1 for link in links if not link["external"] and link["resolved"]),
        "broken_internal_link_count": sum(1 for link in links if link["broken"]),
        "external_link_count": sum(1 for link in links if link["external"]),
        "concepts_with_broken_internal_links_count": len(broken_sources),
        "concepts_with_broken_internal_links": broken_sources,
    }


def _indexes(bundle: Bundle) -> dict[str, Any]:
    listed: set[str] = set()
    unlisted: set[str] = set()
    concepts_by_relative = {concept.relative_path: concept for concept in bundle.concepts}
    concepts_by_id = {concept.concept_id: concept for concept in bundle.concepts}
    directories = {directory.path: directory for directory in bundle.directories}
    for directory in bundle.directories:
        expected = _directory_contents(directory)
        directory_listed: set[str] = set()
        if directory.has_index:
            directory_listed = expected & _index_links(bundle.root_path, directory, concepts_by_relative, concepts_by_id, directories)
            listed.update(directory_listed)
        unlisted.update(expected - directory_listed)
    without_index = sorted((directory.path for directory in bundle.directories if not directory.has_index), key=_path_key)
    return {
        "directory_count": len(bundle.directories),
        "directories_with_index_count": sum(1 for directory in bundle.directories if directory.has_index),
        "directories_without_index_count": len(without_index),
        "directories_without_index": without_index,
        "listed_content_count": len(listed),
        "unlisted_content_count": len(unlisted),
        "unlisted_content_paths": sorted(unlisted, key=_path_key),
    }


def _directory_contents(directory: Directory) -> set[str]:
    return {concept.relative_path for concept in directory.concepts} | {child.path for child in directory.children}


def _index_links(root_path: Path, directory: Directory, concepts_by_relative: dict[str, Any], concepts_by_id: dict[str, Any], directories: dict[str, Directory]) -> set[str]:
    text, _ = _read_markdown_text(root_path / directory.path / "index.md" if directory.path != "." else root_path / "index.md", "index.md")
    if text is None:
        return set()
    found: set[str] = set()
    source = f"{directory.path}/index.md" if directory.path != "." else "index.md"
    for _, raw in _extract_links(text):
        target = _normalize_target(raw)
        if not target or _is_external_target(target):
            continue
        for candidate in _link_candidates(source, target):
            if concept := concepts_by_relative.get(candidate) or concepts_by_id.get(candidate):
                found.add(concept.relative_path)
            directory_path = candidate.removesuffix("/index.md").removesuffix("/").removesuffix(".md")
            if directory_path in directories:
                found.add(directory_path)
    return found


def _logs(bundle: Bundle) -> dict[str, Any]:
    newest: date | None = None
    malformed = 0
    ordering = 0
    paths: set[str] = set()
    for path in sorted(bundle.root_path.rglob("log.md"), key=lambda item: item.relative_to(bundle.root_path).as_posix()):
        relative = path.relative_to(bundle.root_path).as_posix()
        text, _ = _read_markdown_text(path, relative)
        previous: date | None = None
        for line in (text or "").splitlines():
            match = re.fullmatch(r"##\s+(.+?)\s*", line)
            if match is None:
                continue
            try:
                current = date.fromisoformat(match.group(1))
            except ValueError:
                malformed += 1
                paths.add(relative)
                continue
            newest = current if newest is None or current > newest else newest
            if previous is not None and current > previous:
                ordering += 1
                paths.add(relative)
            previous = current
    return {
        "log_file_count": sum(1 for directory in bundle.directories if directory.has_log),
        "newest_entry_date": newest.isoformat() if newest else None,
        "malformed_date_heading_count": malformed,
        "ordering_issue_count": ordering,
        "log_paths_with_issues": sorted(paths, key=_path_key),
    }


def _metadata(bundle: Bundle) -> dict[str, Any]:
    fields = []
    for field in METADATA_FIELDS:
        missing = sorted((concept.concept_id for concept in bundle.concepts if not _metadata_present(concept, field)), key=str.casefold)
        fields.append(
            {
                "field": field,
                "present_count": len(bundle.concepts) - len(missing),
                "missing_count": len(missing),
                "missing_concepts": missing,
            }
        )
    return {"fields": fields}


def _metadata_present(concept: Any, field: str) -> bool:
    value = concept.frontmatter.get(field)
    return bool(value)


def _citations(bundle: Bundle, links: list[dict[str, Any]]) -> dict[str, Any]:
    cited = {concept.concept_id for concept in bundle.concepts if _has_citations(concept.body)}
    external = {link["source_concept_id"] for link in links if link["external"]}
    missing = sorted(external - cited, key=str.casefold)
    return {
        "concepts_with_citations_count": len(cited),
        "concepts_with_external_links_count": len(external),
        "external_linked_without_citations_count": len(missing),
        "external_linked_without_citations": missing,
    }


def _has_citations(body: str) -> bool:
    return any(re.fullmatch(r"\s{0,3}#{1,6}\s+Citations\s*#*\s*", line, re.IGNORECASE) for line in body.splitlines())


def _connectivity(bundle: Bundle, links: list[dict[str, Any]]) -> dict[str, Any]:
    concepts = {concept.concept_id for concept in bundle.concepts}
    outbound = {link["source_concept_id"] for link in links if link["resolved"] and link["target_concept_id"] in concepts}
    inbound = {link["target_concept_id"] for link in links if link["resolved"] and link["target_concept_id"] in concepts}
    orphans = sorted(concepts - inbound - outbound, key=str.casefold)
    return {
        "concepts_with_internal_links_count": len(outbound),
        "concepts_without_inbound_count": len(concepts - inbound),
        "concepts_without_outbound_count": len(concepts - outbound),
        "orphan_concept_count": len(orphans),
        "orphan_concepts": orphans,
    }


def _render_human(bundle_path: str, data: dict[str, Any]) -> str:
    summary = data["summary"]
    return "\n".join(
        [
            f"{bundle_path}  health: {data['status']}",
            f"validation: {data['validation']['status']}  issues: {data['validation']['issue_count']}",
            f"inventory: concepts {summary['concept_count']}  directories {summary['directory_count']}",
            f"reserved files: malformed {data['reserved_files']['malformed_reserved_file_count']}  root index {data['reserved_files']['root_index_present']}  root log {data['reserved_files']['root_log_present']}",
            f"links: internal {data['links']['internal_link_count']}  resolved {data['links']['resolved_internal_link_count']}  broken {data['links']['broken_internal_link_count']}  external {data['links']['external_link_count']}",
            f"indexes: without index {data['indexes']['directories_without_index_count']}  unlisted {data['indexes']['unlisted_content_count']}",
            f"logs: newest {data['logs']['newest_entry_date'] or '-'}  malformed dates {data['logs']['malformed_date_heading_count']}  ordering {data['logs']['ordering_issue_count']}",
            f"metadata: missing {sum(field['missing_count'] for field in data['metadata']['fields'])}",
            f"citations: external without citations {data['citations']['external_linked_without_citations_count']}",
            f"connectivity: orphans {data['connectivity']['orphan_concept_count']}",
        ]
    )


def _emit_error(args: Namespace, error: BundleResolutionError) -> int:
    payload = {
        "ok": False,
        "command": "okf.health",
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
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(error.message, file=sys.stderr)
        for candidate in error.details.get("candidates", []):
            print(f"- {candidate['path']} -> {candidate['command']}", file=sys.stderr)
    return 1


def _issue_key(issue: Issue) -> tuple[str, int, str, str]:
    return (issue.path or "", issue.line if issue.line is not None else 10**9, issue.field or "", issue.code)


def _path_key(path: str) -> tuple[str, ...]:
    return PurePosixPath(path).parts
