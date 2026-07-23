from __future__ import annotations

import json
import os
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

from .models import Bundle, Issue
from .read_model import bundle_payload, issue_payload, scan_bundle
from .resolution import BundleResolutionError, resolve_bundle

OKF_DEFAULT_LINT_CONFIG: dict[str, Any] = {
    "default": True,
    "MD013": False,
    "MD033": False,
    "MD041": False,
    "whitespace": False,
    "no-bare-urls": False,
    "fenced-code-language": False,
    "ul-indent": False,
}

_CONFIG_FILES = [".markdownlint.json", ".markdownlint.yaml", ".markdownlint.yml"]

_ALIAS_TO_RULE: dict[str, str] = {
    "line-length": "MD013",
    "no-inline-html": "MD033",
    "first-line-heading": "MD041",
    "no-bare-urls": "MD034",
    "fenced-code-language": "MD040",
    "ul-indent": "MD007",
}


def _is_known_rule_key(key: str) -> bool:
    if key.startswith("MD"):
        return True
    if key in _ALIAS_TO_RULE:
        return True
    if key in OKF_DEFAULT_LINT_CONFIG and key != "default":
        return True
    return False


def _load_lint_config(bundle_root: Path) -> tuple[dict, str, list[str], list[Issue]]:
    issues: list[Issue] = []

    existing = [name for name in _CONFIG_FILES if (bundle_root / name).is_file()]

    if not existing:
        return dict(OKF_DEFAULT_LINT_CONFIG), "okf-default", [], []

    if len(existing) > 1:
        issues.append(
            Issue(
                code="OKF_LINT_CONFIG_CONFLICT",
                message=f"Multiple markdownlint config files found: {', '.join(existing)}. Using {existing[0]}.",
                severity="warning",
                path=".",
            )
        )

    source = existing[0]
    config_path = bundle_root / source

    raw: dict[str, Any] = {}
    if source.endswith(".json"):
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError) as e:
            issues.append(
                Issue(
                    code="OKF_LINT_CONFIG_MALFORMED",
                    message=f"Failed to parse {source}: {e}",
                    severity="error",
                    path=str(source),
                )
            )
            return {}, source, [], issues
    else:
        try:
            import yaml
        except ImportError:
            issues.append(
                Issue(
                    code="OKF_LINT_UNAVAILABLE",
                    message="PyYAML is required to parse .yaml/.yml lint config files. Install with: pip install mira-okf[lint]",
                    severity="error",
                )
            )
            return {}, source, [], issues
        try:
            raw = yaml.safe_load(config_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError) as e:
            issues.append(
                Issue(
                    code="OKF_LINT_CONFIG_MALFORMED",
                    message=f"Failed to parse {source}: {e}",
                    severity="error",
                    path=str(source),
                )
            )
            return {}, source, [], issues

    if not isinstance(raw, dict):
        issues.append(
            Issue(
                code="OKF_LINT_CONFIG_MALFORMED",
                message=f"Config file {source} must contain a top-level mapping.",
                severity="error",
                path=str(source),
            )
        )
        return {}, source, [], issues

    ignores_value = raw.pop("ignores", None)
    ignores: list[str] = list(ignores_value) if isinstance(ignores_value, list) else []

    for key in raw:
        if key == "default":
            continue
        if not _is_known_rule_key(key):
            issues.append(
                Issue(
                    code="OKF_LINT_CONFIG_UNKNOWN_RULE",
                    message=f"Unknown lint rule: {key}",
                    severity="warning",
                    path=str(source),
                )
            )

    return raw, source, ignores, issues


def _apply_config_to_api(api: Any, config: dict, issues: list[Issue]) -> None:
    from pymarkdown.api import PyMarkdownApiException

    for key, value in config.items():
        if key == "default":
            continue

        rule_id = _ALIAS_TO_RULE.get(key, key)

        try:
            if value is False:
                api.disable_rule_by_identifier(rule_id)
            elif value is True or value in ("error", "warning"):
                api.enable_rule_by_identifier(rule_id)
            elif isinstance(value, dict):
                api.enable_rule_by_identifier(rule_id)
                for prop_name, prop_value in value.items():
                    full_prop = f"plugins.{rule_id}.{prop_name}"
                    if isinstance(prop_value, bool):
                        api.set_boolean_property(full_prop, prop_value)
                    elif isinstance(prop_value, int):
                        api.set_integer_property(full_prop, prop_value)
                    elif isinstance(prop_value, str):
                        api.set_string_property(full_prop, prop_value)
        except PyMarkdownApiException:
            issues.append(
                Issue(
                    code="OKF_LINT_CONFIG_UNKNOWN_RULE",
                    message=f"Failed to configure lint rule: {key}",
                    severity="warning",
                )
            )


def _relative_to(raw_file: str, bundle_root: Path) -> str:
    if not raw_file:
        return ""
    try:
        return str(Path(raw_file).resolve().relative_to(bundle_root)).replace(os.sep, "/")
    except ValueError:
        return raw_file


def _normalize_findings(scan_result, bundle_root: Path) -> list[dict]:
    findings: list[dict] = []
    failures = []
    failures.extend(getattr(scan_result, "scan_failures", []))
    failures.extend(getattr(scan_result, "pragma_errors", []))
    for failure in failures:
        findings.append(
            {
                "file": _relative_to(getattr(failure, "scan_file", ""), bundle_root),
                "line": getattr(failure, "line_number", 0),
                "column": getattr(failure, "column_number", 0),
                "rule": getattr(failure, "rule_id", ""),
                "rule_alias": getattr(failure, "rule_name", ""),
                "description": getattr(failure, "rule_description", ""),
                "severity": "error" if getattr(scan_result, "critical_errors", None) else "warning",
            }
        )
    for failure in getattr(scan_result, "critical_errors", []):
        findings.append(
            {
                "file": _relative_to(getattr(failure, "scan_file", "") if not isinstance(failure, str) else "", bundle_root),
                "line": getattr(failure, "line_number", 0) if not isinstance(failure, str) else 0,
                "column": getattr(failure, "column_number", 0) if not isinstance(failure, str) else 0,
                "rule": "CRITICAL",
                "rule_alias": "",
                "description": str(failure),
                "severity": "error",
            }
        )
    return findings


def _lint_data(bundle: Bundle) -> tuple[dict | None, list[Issue]]:
    try:
        from pymarkdown.api import PyMarkdownApi, PyMarkdownApiException
    except ImportError:
        return None, []

    config_dict, source, ignores, config_issues = _load_lint_config(bundle.root_path)

    api = PyMarkdownApi()
    _apply_config_to_api(api, config_dict, config_issues)

    original_cwd = Path.cwd().resolve()
    bundle_root = bundle.root_path.resolve()
    all_findings: list[dict] = []
    try:
        os.chdir(str(bundle_root))
        for concept in bundle.concepts:
            try:
                results = api.scan_path(concept.relative_path, exclude_patterns=ignores)
                findings = _normalize_findings(results, bundle_root)
                all_findings.extend(findings)
            except PyMarkdownApiException:
                pass
    finally:
        os.chdir(str(original_cwd))

    all_findings.sort(key=lambda f: (f["file"], f["line"], f["rule"]))

    by_file: dict[str, int] = {}
    for f in all_findings:
        by_file[f["file"]] = by_file.get(f["file"], 0) + 1

    profile = "user" if source != "okf-default" else "okf-default"

    data = {
        "findings": all_findings,
        "count": len(all_findings),
        "by_file": by_file,
        "config": {
            "source": source,
            "profile": profile,
            "ignores": ignores,
        },
    }
    return data, config_issues


def _unavailable_payload(bundle_payload_value, args: Namespace) -> int:
    payload = {
        "ok": False,
        "command": "okf.lint",
        "bundle": bundle_payload_value,
        "data": None,
        "issues": [
            issue_payload(
                Issue(
                    code="OKF_LINT_UNAVAILABLE",
                    message="pymarkdownlnt is not installed. Install with: pip install mira-okf[lint]",
                    severity="error",
                )
            )
        ],
        "error": {
            "code": "OKF_LINT_UNAVAILABLE",
            "message": "pymarkdownlnt is not installed.",
            "details": {"suggestion": "pip install mira-okf[lint]"},
        },
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print("mira-okf lint: pymarkdownlnt is not installed. Install with: pip install mira-okf[lint]", file=sys.stderr)
    return 1


def run_lint(args: Namespace) -> int:
    try:
        from pymarkdown.api import PyMarkdownApi  # noqa: F401
    except ImportError:
        return _unavailable_payload(None, args)

    try:
        bundle = resolve_bundle(getattr(args, "bundle", None), "lint")
        bundle, _ = scan_bundle(bundle, None)
    except BundleResolutionError as error:
        payload = {
            "ok": False,
            "command": "okf.lint",
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

    lint_data, lint_issues = _lint_data(bundle)

    if lint_data is None:
        return _unavailable_payload(bundle_payload(bundle), args)

    payload = {
        "ok": True,
        "command": "okf.lint",
        "bundle": bundle_payload(bundle),
        "data": lint_data,
        "issues": [issue_payload(issue) for issue in sorted(lint_issues, key=_issue_key)],
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(_render_human(payload["bundle"]["relative_path"], lint_data, lint_issues))
    return 0


def _render_human(bundle_path: str, data: dict, issues: list[Issue]) -> str:
    lines = [f"{bundle_path}  lint findings: {data['count']}  config: {data['config']['source']} ({data['config']['profile']})"]
    for issue in issues:
        lines.append(f"  config: [{issue.severity}] {issue.code}: {issue.message}")
    for finding in data["findings"]:
        lines.append(f"  {finding['file']}:{finding['line']}:{finding['column']}  [{finding['severity']}] {finding['rule']}: {finding['description']}")
    return "\n".join(lines)


def _issue_key(issue: Issue) -> tuple:
    return (issue.path or "", issue.line if issue.line is not None else 10**9, issue.field or "", issue.code)
