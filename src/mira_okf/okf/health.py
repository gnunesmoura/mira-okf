from __future__ import annotations

import json
import re
import sys
from argparse import Namespace
from collections import Counter
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

from .links import _broken_link_issue, _extract_links, _is_external_target, _normalize_target, _resolve_internal_target
from .models import Bundle, Directory, Issue
from .read_model import _is_hidden, _read_markdown_text, bundle_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, link_candidates, resolve_bundle
from .semantic import semantic_text
from .validate import _reserved_issues

METADATA_FIELDS = ("title", "description", "resource", "tags", "timestamp")
PROFILE_GROUPS = {
    "quick": ("inventory", "reserved_files", "links", "connectivity"),
    "full": ("inventory", "reserved_files", "links", "indexes", "logs", "metadata", "citations", "connectivity"),
}
GROUP_LABELS = {
    "inventory": "inventory",
    "reserved_files": "reserved files",
    "links": "links",
    "indexes": "indexes",
    "logs": "logs",
    "metadata": "metadata",
    "citations": "citations",
    "connectivity": "connectivity",
}


def run_health(args: Namespace) -> int:
    try:
        bundle = resolve_bundle(args.bundle, "health")
        bundle, _ = scan_bundle(bundle, None)
    except BundleResolutionError as error:
        return _emit_error(args, error)

    links, link_issues = _collect_health_links(bundle)
    reserved_issues = _reserved_issues(bundle.root_path)
    validation = _validation_data(bundle, reserved_issues)
    data = _health_data(bundle, validation, reserved_issues, links, getattr(args, "profile", "quick"))
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


def _health_data(bundle: Bundle, validation: dict[str, Any], reserved_issues: list[Issue], links: list[dict[str, Any]], profile: str) -> dict[str, Any]:
    selected_groups = PROFILE_GROUPS.get(profile, PROFILE_GROUPS["quick"])
    ignored_groups = tuple(group for group in PROFILE_GROUPS["full"] if group not in selected_groups)
    reserved = _reserved_files(bundle, reserved_issues)
    indexes = _indexes(bundle)
    logs = _logs(bundle)
    metadata = _metadata(bundle)
    citations = _citations(bundle, links)
    connectivity = _connectivity(bundle, links)
    link_data = _links(links)
    group_data = {
        "inventory": _inventory(bundle),
        "reserved_files": reserved,
        "links": link_data,
        "indexes": indexes,
        "logs": logs,
        "metadata": metadata,
        "citations": citations,
        "connectivity": connectivity,
    }
    warnings = sum(_warning_signal_count(group, group_data[group]) for group in selected_groups)
    status = "invalid" if not validation["passed"] else "attention" if warnings else "ok"
    return {
        "rules": {
            "profile": profile if profile in PROFILE_GROUPS else "quick",
            "evaluated_groups": list(selected_groups),
            "ignored_groups": list(ignored_groups),
        },
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
        **group_data,
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
    text, _ = _read_markdown_text(directory.absolute_path / "index.md", "index.md")
    if text is None:
        return set()
    found: set[str] = set()
    directory_relative = directory.absolute_path.relative_to(root_path).as_posix()
    source = f"{directory_relative}/index.md" if directory_relative != "." else "index.md"
    for _, raw in _extract_links(semantic_text(text)):
        target = _normalize_target(raw)
        if not target or _is_external_target(target):
            continue
        for candidate in link_candidates(source, target):
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
        for line in semantic_text(text or "").splitlines():
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
    return any(re.fullmatch(r"\s{0,3}#{1,6}\s+Citations\s*#*\s*", line, re.IGNORECASE) for line in semantic_text(body).splitlines())


def _connectivity(bundle: Bundle, links: list[dict[str, Any]]) -> dict[str, Any]:
    concepts_by_id = {concept.concept_id: concept for concept in bundle.concepts}
    concepts_by_relative = {concept.relative_path: concept for concept in bundle.concepts}
    semantic = {
        concept_id
        for link in links
        if link["resolved"]
        and link["target_concept_id"] in concepts_by_id
        and link["source_concept_id"] != link["target_concept_id"]
        for concept_id in (link["source_concept_id"], link["target_concept_id"])
    }
    navigable: set[str] = set()
    indexes = {
        (directory.absolute_path.relative_to(bundle.root_path).as_posix() + "/" if directory.absolute_path != bundle.root_path else "") + "index.md"
        for directory in bundle.directories
        if directory.has_index
    }
    index_directories = {
        index.removesuffix("/index.md").removesuffix("index.md"): index
        for index in indexes
    }
    pending = sorted(indexes, key=_path_key)
    visited: set[str] = set()
    while pending:
        source = pending.pop(0)
        if source in visited:
            continue
        visited.add(source)
        text, _ = _read_markdown_text(bundle.root_path / source, source)
        for _, raw_target in _extract_links(semantic_text(text or "")):
            target = _normalize_target(raw_target)
            if not target or _is_external_target(target):
                continue
            for candidate in link_candidates(source, target):
                concept = concepts_by_id.get(candidate) or concepts_by_relative.get(candidate)
                if concept is not None:
                    navigable.add(concept.concept_id)
                    break
                index = index_directories.get(candidate)
                index = index or (candidate if candidate in indexes else None)
                if index is None and candidate.endswith(".md"):
                    index = candidate.removesuffix(".md") + "/index.md"
                if index in indexes and index not in visited:
                    pending.append(index)
                    break
    semantic_only = semantic & set(concepts_by_id)
    navigation_only = navigable - semantic_only
    unreachable = set(concepts_by_id) - semantic_only - navigation_only
    unreachable_concepts = sorted(unreachable, key=str.casefold)
    return {
        "concepts_with_internal_links_count": len({link["source_concept_id"] for link in links if link["resolved"] and link["target_concept_id"] in concepts_by_id and link["source_concept_id"] != link["target_concept_id"]}),
        "concepts_without_inbound_count": len(set(concepts_by_id) - {link["target_concept_id"] for link in links if link["resolved"] and link["target_concept_id"] in concepts_by_id and link["source_concept_id"] != link["target_concept_id"]}),
        "concepts_without_outbound_count": len(set(concepts_by_id) - {link["source_concept_id"] for link in links if link["resolved"] and link["target_concept_id"] in concepts_by_id and link["source_concept_id"] != link["target_concept_id"]}),
        "semantic_concept_count": len(semantic_only),
        "navigation_only_concept_count": len(navigation_only),
        "navigation_only_concepts": sorted(navigation_only, key=str.casefold),
        "unreachable_concept_count": len(unreachable),
        "unreachable_concepts": unreachable_concepts,
    }


def _collect_health_links(bundle: Bundle) -> tuple[list[dict[str, Any]], list[Issue]]:
    records: list[dict[str, Any]] = []
    issues: list[Issue] = []
    concepts_by_id = {concept.concept_id: concept for concept in bundle.concepts}
    concepts_by_relative = {concept.relative_path: concept for concept in bundle.concepts}

    for concept in sorted(bundle.concepts, key=lambda item: item.relative_path):
        for index, (kind, raw_target) in enumerate(_extract_links(semantic_text(concept.body))):
            target = _normalize_target(raw_target)
            if not target:
                continue
            external = _is_external_target(target)
            resolved_concept = None
            resolved = False
            broken = False
            target_concept_id = None
            target_path = None
            if not external:
                resolved_concept = _resolve_internal_target(concept, target, concepts_by_id, concepts_by_relative)
                resolved = resolved_concept is not None
                broken = not resolved
                if resolved_concept is not None:
                    target_concept_id = resolved_concept.concept_id
                    target_path = resolved_concept.relative_path
                if broken:
                    candidates = link_candidates(concept.relative_path, target)
                    if not any(_is_hidden(c) for c in candidates):
                        issues.append(
                            _broken_link_issue(concept.relative_path, raw_target)
                        )
            records.append(
                {
                    "source_concept_id": concept.concept_id,
                    "source_path": concept.relative_path,
                    "raw": raw_target,
                    "kind": kind,
                    "target": target,
                    "resolved": resolved,
                    "broken": broken,
                    "external": external,
                    "target_concept_id": target_concept_id,
                    "target_path": target_path,
                    "_order": index,
                }
            )

    records.sort(key=lambda record: (record["source_path"], record["_order"], record["target"]))
    for record in records:
        record.pop("_order", None)
    return records, issues


def _render_human(bundle_path: str, data: dict[str, Any]) -> str:
    summary = data["summary"]
    lines = [f"{bundle_path}  profile: {data['rules']['profile']}  health: {data['status']}"]
    for group in data["rules"]["evaluated_groups"]:
        lines.append(_render_group(group, data, summary))
    return "\n".join(lines)


def _render_group(group: str, data: dict[str, Any], summary: dict[str, Any]) -> str:
    if group == "inventory":
        return f"{GROUP_LABELS[group]}: concepts {summary['concept_count']}  directories {summary['directory_count']}"
    if group == "reserved_files":
        reserved = data[group]
        return (
            f"{GROUP_LABELS[group]}: malformed {reserved['malformed_reserved_file_count']}  "
            f"root index {reserved['root_index_present']}  root log {reserved['root_log_present']}"
        )
    if group == "links":
        links = data[group]
        return (
            f"{GROUP_LABELS[group]}: internal {links['internal_link_count']}  resolved {links['resolved_internal_link_count']}  "
            f"broken {links['broken_internal_link_count']}  external {links['external_link_count']}"
        )
    if group == "indexes":
        indexes = data[group]
        return f"{GROUP_LABELS[group]}: without index {indexes['directories_without_index_count']}  unlisted {indexes['unlisted_content_count']}"
    if group == "logs":
        logs = data[group]
        return (
            f"{GROUP_LABELS[group]}: newest {logs['newest_entry_date'] or '-'}  malformed dates {logs['malformed_date_heading_count']}  "
            f"ordering {logs['ordering_issue_count']}"
        )
    if group == "metadata":
        metadata = data[group]
        return f"{GROUP_LABELS[group]}: missing {sum(field['missing_count'] for field in metadata['fields'])}"
    if group == "citations":
        citations = data[group]
        return f"{GROUP_LABELS[group]}: external without citations {citations['external_linked_without_citations_count']}"
    if group == "connectivity":
        connectivity = data[group]
        return (
            f"{GROUP_LABELS[group]}: semantic {connectivity['semantic_concept_count']}  "
            f"navigation-only {connectivity['navigation_only_concept_count']}  "
            f"unreachable {connectivity['unreachable_concept_count']}"
        )
    return group


def _warning_signal_count(group: str, data: dict[str, Any]) -> int:
    if group == "reserved_files":
        return data["malformed_reserved_file_count"]
    if group == "links":
        return data["broken_internal_link_count"]
    if group == "indexes":
        return data["directories_without_index_count"] + data["unlisted_content_count"]
    if group == "logs":
        return data["malformed_date_heading_count"] + data["ordering_issue_count"]
    if group == "metadata":
        return sum(field["missing_count"] for field in data["fields"])
    if group == "citations":
        return data["external_linked_without_citations_count"]
    if group == "connectivity":
        return data["unreachable_concept_count"]
    return 0


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
