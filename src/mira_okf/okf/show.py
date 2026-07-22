from __future__ import annotations

import json
import sys
from argparse import Namespace
from typing import Any

from .models import Bundle, MarkdownDocument
from .read_model import bundle_payload, concept_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, ConceptResolutionError, resolve_bundle, resolve_show_target


def run_show(args: Namespace) -> int:
    if args.concept is None and args.bundle is not None:
        args.concept = args.bundle
        args.bundle = None
    try:
        bundle = resolve_bundle(args.bundle, "show")
        bundle, _ = scan_bundle(bundle, None)
        result = resolve_show_target(bundle, args.concept)
    except BundleResolutionError as error:
        return _emit_error(args, "okf.show", error.code, error.message, error.details)
    except ConceptResolutionError as error:
        return _emit_error(args, "okf.show", error.code, error.message, error.details)

    profile = getattr(args, "profile", "brief" if getattr(args, "summary", False) else "normal")

    if isinstance(result, MarkdownDocument):
        return _emit_generic(args, bundle, result, profile)

    concept_data = concept_payload(result)
    payload = {
        "ok": True,
        "command": "okf.show",
        "bundle": bundle_payload(bundle),
        "data": {"profile": profile, **_filter_show_concept(concept_data, profile)},
        "issues": [issue_payload(issue) for issue in bundle.issues],
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    print(_render_show_output(concept_data, profile))
    return 0


def _filter_show_concept(c: dict[str, Any], profile: str) -> dict[str, Any]:
    if profile == "brief":
        fields = ("concept_id", "title", "description", "type", "tags", "relative_path")
    else:
        return dict(c)
    return {field: c[field] for field in fields}


def _render_show_output(data: dict[str, Any], profile: str) -> str:
    lines = [_render_concept_header(data)]
    if data["description"]:
        lines.append(f"description: {data['description']}")
    if data["tags"]:
        lines.append(f"tags: {', '.join(data['tags'])}")
    if profile == "full":
        frontmatter = data.get("frontmatter", {})
        if frontmatter:
            lines.extend(["", "Frontmatter"])
            lines.extend(f"{key}: {frontmatter[key]}" for key in sorted(frontmatter))
    if profile != "brief" and data["body"]:
        lines.extend(["", data["body"]])
    if data["issues"]:
        lines.extend(["", "Issues"])
        lines.extend(_render_issue_line(issue) for issue in data["issues"])
    return "\n".join(lines)


def _render_concept_header(data: dict[str, Any]) -> str:
    line = data["relative_path"]
    if data["type"]:
        line += f"  [{data['type']}]"
    if data["title"]:
        line += f"  {data['title']}"
    return line


def _render_issue_line(issue: dict[str, Any]) -> str:
    line = "- "
    if issue["path"]:
        line += f"{issue['path']}  "
    line += f"[{issue['code']}] {issue['message']}"
    return line


def _filter_generic(doc: MarkdownDocument, profile: str) -> dict[str, Any]:
    data: dict[str, Any] = {"document_kind": "markdown", "relative_path": doc.relative_path}
    if profile != "brief":
        data["content"] = doc.content
    return data


def _render_generic_output(doc: MarkdownDocument, profile: str) -> str:
    header = f"{doc.relative_path}  [Markdown]"
    if profile == "brief":
        return header
    lines = [header, "", doc.content]
    return "\n".join(lines)


def _emit_generic(args: Namespace, bundle: Bundle, doc: MarkdownDocument, profile: str) -> int:
    data = _filter_generic(doc, profile)
    issues = [
        issue_payload(issue) for issue in bundle.issues
        if not (issue.code == "OKF_FRONTMATTER_MISSING" and issue.path == doc.relative_path)
    ]
    payload = {
        "ok": True,
        "command": "okf.show",
        "bundle": bundle_payload(bundle),
        "data": {"profile": profile, **data},
        "issues": issues,
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    print(_render_generic_output(doc, profile))
    return 0


def _emit_error(args: Namespace, command: str, code: str, message: str, details: dict[str, Any]) -> int:
    payload = {
        "ok": False,
        "command": command,
        "bundle": None,
        "data": None,
        "issues": [],
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(message, file=sys.stderr)
        for candidate in details.get("candidates", []):
            print(f"- {candidate['path']} -> {candidate['command']}", file=sys.stderr)
    return 1
