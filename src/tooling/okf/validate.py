from __future__ import annotations

import json
import re
import sys
from datetime import date
from argparse import Namespace
from pathlib import Path

from .models import Issue
from .read_model import _read_markdown_document, _read_markdown_text, bundle_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, resolve_bundle


def run_validate(args: Namespace) -> int:
    try:
        bundle = resolve_bundle(args.bundle, "validate")
        bundle, _ = scan_bundle(bundle, None)
    except BundleResolutionError as error:
        payload = {
            "ok": False,
            "command": "okf.validate",
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

    issues = sorted(
        [*bundle.issues, *_reserved_issues(bundle.root_path)],
        key=lambda issue: (
            issue.path or "",
            issue.line if issue.line is not None else 10**9,
            issue.field or "",
            issue.code,
        ),
    )
    error_count = sum(1 for issue in issues if issue.severity == "error")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")
    info_count = sum(1 for issue in issues if issue.severity == "info")
    passed = error_count == 0 and warning_count == 0
    payload = {
        "ok": True,
        "command": "okf.validate",
        "bundle": bundle_payload(bundle),
        "data": {
            "passed": passed,
            "status": "pass" if passed else "fail",
            "issue_count": len(issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "concept_count": len(bundle.concepts),
            "checked_file_count": sum(1 for _ in bundle.root_path.rglob("*.md")),
        },
        "issues": [issue_payload(issue) for issue in issues],
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    lines = [payload["bundle"]["relative_path"]]
    data = payload["data"]
    lines.append(
        "validation: "
        f"{data['status']}  "
        f"issues: {data['issue_count']} "
        f"(errors {data['error_count']}, warnings {data['warning_count']}, info {data['info_count']})  "
        f"concepts: {data['concept_count']}  checked: {data['checked_file_count']}"
    )
    for issue in payload["issues"]:
        line = issue["path"] or ""
        if line:
            line += "  "
        line += f"[{issue['severity']}] {issue['code']}: {issue['message']}"
        if issue["suggestion"]:
            line += f"  {issue['suggestion']}"
        lines.append(line)
    print("\n".join(lines))
    return 0


def _reserved_issues(root_path: Path) -> list[Issue]:
    issues: list[Issue] = []
    for path in sorted(root_path.rglob("*.md"), key=lambda item: item.relative_to(root_path).as_posix()):
        if path.name == "index.md":
            issues.extend(_validate_index(path, root_path))
        elif path.name == "log.md":
            issues.extend(_validate_log(path, root_path))
    return issues


def _validate_index(path: Path, root_path: Path) -> list[Issue]:
    relative_path = path.relative_to(root_path).as_posix()
    frontmatter, _, has_frontmatter, issues = _read_markdown_document(path, relative_path)
    if not has_frontmatter:
        return issues
    if path.parent != root_path:
        issues.append(
            Issue(
                code="OKF_INDEX_FRONTMATTER_NOT_ALLOWED",
                message="Non-root index.md files must not have frontmatter.",
                path=relative_path,
                line=1,
                suggestion="Remove the frontmatter block from this index.md file.",
            )
        )
        return issues
    extra_fields = sorted(key for key in frontmatter if key != "okf_version")
    if extra_fields:
        issues.append(
            Issue(
                code="OKF_ROOT_INDEX_FRONTMATTER_INVALID",
                message="Bundle-root index.md frontmatter may only contain okf_version.",
                path=relative_path,
                line=1,
                field=extra_fields[0],
                suggestion="Remove the extra frontmatter fields from bundle-root index.md.",
            )
        )
    return issues


def _validate_log(path: Path, root_path: Path) -> list[Issue]:
    relative_path = path.relative_to(root_path).as_posix()
    text, issues = _read_markdown_text(path, relative_path)
    if text is None:
        return issues
    previous_date: date | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.fullmatch(r"##\s+(.+?)\s*", line)
        if match is None:
            continue
        heading = match.group(1)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", heading):
            issues.append(
                Issue(
                    code="OKF_LOG_INVALID_DATE_HEADING",
                    message="Log date headings must use YYYY-MM-DD.",
                    path=relative_path,
                    line=line_number,
                    suggestion="Change the heading to YYYY-MM-DD.",
                )
            )
            continue
        try:
            current_date = date.fromisoformat(heading)
        except ValueError:
            issues.append(
                Issue(
                    code="OKF_LOG_INVALID_DATE_HEADING",
                    message="Log date headings must use YYYY-MM-DD.",
                    path=relative_path,
                    line=line_number,
                    suggestion="Change the heading to a valid calendar date in YYYY-MM-DD format.",
                )
            )
            continue
        if previous_date is not None and current_date > previous_date:
            issues.append(
                Issue(
                    code="OKF_LOG_DATE_GROUP_ORDER",
                    message="Log date groups must be newest first.",
                    path=relative_path,
                    line=line_number,
                    suggestion="Move this date group above newer entries.",
                )
            )
        previous_date = current_date
    return issues
