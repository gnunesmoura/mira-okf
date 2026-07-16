from __future__ import annotations

import json
import sys
from argparse import Namespace
from typing import Any

from .read_model import bundle_payload, directory_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, resolve_bundle


def run_tree(args: Namespace) -> int:
    try:
        reference_suffix = f"--depth {getattr(args, 'depth', 2)} --summary"
        bundle = resolve_bundle(args.bundle, "tree", reference_suffix)
        bundle, root_directory = scan_bundle(bundle, args.depth)
    except BundleResolutionError as error:
        return _emit_error(args, error)

    payload = {
        "ok": True,
        "command": "okf.tree",
        "bundle": bundle_payload(bundle),
        "data": directory_payload(root_directory),
        "issues": [issue_payload(issue) for issue in bundle.issues],
    }
    _emit_payload(args, payload)
    return 0


def _emit_error(args: Namespace, error: BundleResolutionError) -> int:
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
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(error.message, file=sys.stderr)
        for candidate in error.details.get("candidates", []):
            print(f"- {candidate['path']} -> {candidate['command']}", file=sys.stderr)
    return 1


def _emit_payload(args: Namespace, payload: dict[str, Any]) -> None:
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return
    print(_render_directory_summary(payload["data"], getattr(args, "summary", False)))


def _render_directory_summary(directory: dict[str, Any], summary: bool) -> str:
    return _render_directory(directory, 0, summary)


def _render_directory(directory: dict[str, Any], indent: int, summary: bool) -> str:
    label = directory["path"] if indent == 0 else directory["name"]
    line = f"{'  ' * indent}{label or directory['name']}/"
    if summary:
        if directory["has_index"]:
            line += "  index.md"
        if directory["has_log"]:
            line += "  log.md"
        reserved_count = int(directory["has_index"]) + int(directory["has_log"])
        line += f"  concepts: {directory['concept_count']}  reserved: {reserved_count}"
    lines = [line]
    for child in directory["children"]:
        lines.append(_render_directory(child, indent + 1, summary))
    return "\n".join(lines)
