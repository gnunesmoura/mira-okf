from __future__ import annotations

import json
import sys
from argparse import Namespace
from typing import Any

from .read_model import bundle_payload, concept_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, ConceptResolutionError, resolve_bundle, resolve_concept


def run_show(args: Namespace) -> int:
    if args.concept is None and args.bundle is not None:
        args.concept = args.bundle
        args.bundle = None
    try:
        bundle = resolve_bundle(args.bundle, "show")
        bundle, _ = scan_bundle(bundle, None)
        concept = resolve_concept(bundle, args.concept)
    except BundleResolutionError as error:
        return _emit_error(args, "okf.show", error.code, error.message, error.details)
    except ConceptResolutionError as error:
        return _emit_error(args, "okf.show", error.code, error.message, error.details)

    payload = {
        "ok": True,
        "command": "okf.show",
        "bundle": bundle_payload(bundle),
        "data": concept_payload(concept),
        "issues": [issue_payload(issue) for issue in bundle.issues],
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    print(_render_show_output(payload["data"], getattr(args, "summary", False)))
    return 0


def _render_show_output(data: dict[str, Any], summary: bool) -> str:
    lines = [_render_concept_header(data)]
    if data["description"]:
        lines.append(f"description: {data['description']}")
    if data["tags"]:
        lines.append(f"tags: {', '.join(data['tags'])}")
    if not summary and data["body"]:
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
