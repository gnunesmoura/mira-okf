from __future__ import annotations

import json
import posixpath
import re
import sys
from argparse import Namespace
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import unquote

from .read_model import _is_hidden, bundle_payload, concept_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, ConceptResolutionError, resolve_bundle, resolve_concept
from .semantic import semantic_text

LINK_PATTERN = re.compile(
    r"(?<!\!)\[[^\]]+\]\((?P<markdown>[^)\s]+)(?:\s+\"[^\"]*\")?\)|\[\[(?P<wikilink>[^\]]+)\]\]"
)


def run_links(args: Namespace) -> int:
    try:
        bundle = resolve_bundle(args.bundle, "links")
        bundle, _ = scan_bundle(bundle, None)
        records, link_issues = _collect_links(bundle)
    except BundleResolutionError as error:
        return _emit_bundle_error("okf.links", args, error)

    visible = _visible_links(records, getattr(args, "broken", False), getattr(args, "external", False))
    payload = {
        "ok": True,
        "command": "okf.links",
        "bundle": bundle_payload(bundle),
        "data": {
            "links": visible,
            "total": len(records),
            "returned": len(visible),
        },
        "issues": [issue_payload(issue) for issue in bundle.issues + link_issues],
    }
    _emit_payload(args, payload, _render_links_summary)
    return 0


def run_backlinks(args: Namespace) -> int:
    try:
        bundle = resolve_bundle(args.bundle, "backlinks")
        bundle, _ = scan_bundle(bundle, None)
        target = resolve_concept(bundle, args.concept)
        records, link_issues = _collect_links(bundle)
    except BundleResolutionError as error:
        return _emit_bundle_error("okf.backlinks", args, error)
    except ConceptResolutionError as error:
        return _emit_concept_error(args, error)

    visible = [record for record in records if record["resolved"] and record["target_concept_id"] == target.concept_id]
    payload = {
        "ok": True,
        "command": "okf.backlinks",
        "bundle": bundle_payload(bundle),
        "data": {
            "concept": concept_payload(target),
            "links": visible,
            "total": len(visible),
            "returned": len(visible),
        },
        "issues": [issue_payload(issue) for issue in bundle.issues + link_issues],
    }
    _emit_payload(args, payload, lambda data: _render_backlinks_summary(target.relative_path, data))
    return 0


def _collect_links(bundle):
    records: list[dict[str, Any]] = []
    issues = []
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
                    candidates = _link_candidates(concept.relative_path, target)
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


def _extract_links(body: str):
    for match in LINK_PATTERN.finditer(body):
        if match.group("markdown") is not None:
            yield "markdown", match.group("markdown")
        else:
            yield "wikilink", match.group("wikilink")


def _normalize_target(raw_target: str) -> str:
    target = raw_target.strip()
    if "|" in target:
        target = target.split("|", 1)[0]
    if "#" in target:
        target = target.split("#", 1)[0]
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    target = target.strip()
    if _is_external_target(target):
        return target
    return unquote(target)


def _is_external_target(target: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("//"))


def _resolve_internal_target(concept, target, concepts_by_id, concepts_by_relative):
    candidates = _link_candidates(concept.relative_path, target)
    for candidate in candidates:
        resolved = concepts_by_id.get(candidate) or concepts_by_relative.get(candidate)
        if resolved is not None:
            return resolved
    return None


def _link_candidates(source_path: str, target: str) -> list[str]:
    root_relative = target.startswith("/")
    target = _clean_internal_path(target)
    if not root_relative and source_path:
        parent = PurePosixPath(source_path).parent
        target = _clean_internal_path((parent / target).as_posix())

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


def _clean_internal_path(path: str) -> str:
    cleaned = posixpath.normpath(path.replace("\\", "/"))
    return "" if cleaned == "." else cleaned.lstrip("/")


def _broken_link_issue(path: str, raw_target: str):
    from .models import Issue

    return Issue(
        code="OKF_LINK_BROKEN",
        message="Link target does not resolve inside the bundle.",
        severity="warning",
        path=path,
        field="link",
        suggestion=f"Check the target: {raw_target}",
    )


def _visible_links(records: list[dict[str, Any]], broken: bool, external: bool) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if record["resolved"] or (broken and record["broken"]) or (external and record["external"])
    ]


def _render_links_summary(data: dict[str, Any]) -> str:
    lines = [f"links: {data['returned']} of {data['total']}"]
    for link in data["links"]:
        lines.append(_render_link_line(link))
    return "\n".join(lines)


def _render_backlinks_summary(target_path: str, data: dict[str, Any]) -> str:
    lines = [f"backlinks: {data['returned']} of {data['total']} for {target_path}"]
    for link in data["links"]:
        lines.append(_render_link_line(link))
    return "\n".join(lines)


def _render_link_line(link: dict[str, Any]) -> str:
    if link["external"]:
        return f"{link['source_path']}  ->  [external] {link['target']}"
    if link["broken"]:
        return f"{link['source_path']}  ->  [broken] {link['target']}"
    return f"{link['source_path']}  ->  {link['target_path']}"


def _emit_bundle_error(command: str, args: Namespace, error: BundleResolutionError) -> int:
    payload = {
        "ok": False,
        "command": command,
        "bundle": None,
        "data": None,
        "issues": [],
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    }
    return _emit_error(args, payload)


def _emit_concept_error(args: Namespace, error: ConceptResolutionError) -> int:
    payload = {
        "ok": False,
        "command": "okf.backlinks",
        "bundle": None,
        "data": None,
        "issues": [],
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    }
    return _emit_error(args, payload)


def _emit_error(args: Namespace, payload: dict[str, Any]) -> int:
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(payload["error"]["message"], file=sys.stderr)
        for candidate in payload["error"].get("details", {}).get("candidates", []):
            print(f"- {candidate['path']} -> {candidate['command']}", file=sys.stderr)
    return 1


def _emit_payload(args: Namespace, payload: dict[str, Any], renderer) -> None:
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return
    print(renderer(payload["data"]))
