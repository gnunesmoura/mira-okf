from __future__ import annotations

import json
import sys
from argparse import Namespace
from copy import deepcopy
from typing import Any, Iterable

from .models import Bundle, Concept
from .read_model import bundle_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, resolve_bundle

DEFAULT_FIELDS = ("type", "title", "description", "tags")
_NORMALIZED_FIELDS = frozenset(DEFAULT_FIELDS)


def project_concept(concept: Concept, fields: Iterable[str] | None = None) -> dict[str, Any]:
    selected = tuple(fields) if fields is not None else DEFAULT_FIELDS
    row: dict[str, Any] = {"concept_id": concept.concept_id}
    for field in selected:
        value = getattr(concept, field) if field in _NORMALIZED_FIELDS else concept.frontmatter.get(field)
        row[field] = deepcopy(value)
    return row


def project_bundle(bundle: Bundle, fields: Iterable[str] | None = None) -> dict[str, Any]:
    selected = tuple(fields) if fields is not None else DEFAULT_FIELDS
    return {
        "fields": list(selected),
        "rows": [project_concept(concept, selected) for concept in sorted(bundle.concepts, key=lambda item: item.concept_id)],
        "issues": list(bundle.issues),
    }


def run_props(args: Namespace) -> int:
    try:
        bundle = resolve_bundle(getattr(args, "bundle", None), "props")
        bundle, _ = scan_bundle(bundle, None)
    except BundleResolutionError as error:
        return _emit_error(args, error)

    data = project_bundle(bundle, getattr(args, "field", None))
    payload = {
        "ok": True,
        "command": "okf.props",
        "bundle": bundle_payload(bundle),
        "data": {"fields": data["fields"], "rows": data["rows"]},
        "issues": [issue_payload(issue) for issue in bundle.issues],
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(_render_table(payload["data"]))
    return 0


def _emit_error(args: Namespace, error: BundleResolutionError) -> int:
    payload = {
        "ok": False,
        "command": "okf.props",
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


def _render_table(data: dict[str, Any]) -> str:
    fields = ["concept_id", *data["fields"]]
    lines = ["\t".join(fields)]
    for row in data["rows"]:
        lines.append("\t".join(_render_value(row[field]) for field in fields))
    return "\n".join(lines)


def _render_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)
