"""Human-readable health output rendering."""

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
