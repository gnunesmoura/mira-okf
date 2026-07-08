---
type: ArchitectureDecision
title: Health Report Contract
description: Defines the read-only health report payload and soft signal semantics for `tooling okf health`.
tags:
  - tooling
  - okf
  - health
  - architecture
---

# Health Report Contract

## Context

`health` should give a compact status view for one OKF bundle without becoming a second validator, crawler, fixer, or scoring system. It depends on the shared resolver, shared read model, shared issue contract, shared JSON envelope, and the validation report semantics already defined for readable bundles.

The OKF specification separates required conformance from soft quality guidance. Concepts require parseable top-of-file YAML frontmatter and a non-empty `type`; present reserved files must follow `index.md` and `log.md` structure; missing optional fields, unknown types, unknown keys, missing `index.md`, broken cross-links, and missing citations must be tolerated by consumers.

Health therefore needs to expose useful quality signals while preserving the permissive OKF consumption model.

## Decision

`tooling okf health` is a read-only report over the existing bundle read result, validation summary, and link extraction data.

The command should:

- resolve one bundle through the shared discovery rules;
- read the bundle through the shared OKF read model;
- reuse validation report semantics for conformance status and issue counts;
- use the shared top-level JSON envelope with `command: "okf.health"`;
- place only the health report in `data`;
- keep read, validation, and health collection issues in the shared top-level `issues` array;
- treat poor health signals as report data, not command execution failure;
- avoid external URL fetching, citation target verification, historical trend analysis, and opaque scoring;
- sort all path-like detail lists by normalized bundle-relative path and all name-like lists by normalized name.

The JSON envelope remains:

```json
{
  "ok": true,
  "command": "okf.health",
  "bundle": {},
  "data": {},
  "issues": []
}
```

The `data` payload should use this stable shape:

```json
{
  "status": "ok",
  "summary": {
    "status": "ok",
    "validation_passed": true,
    "concept_count": 0,
    "directory_count": 0,
    "warning_signal_count": 0,
    "error_signal_count": 0
  },
  "validation": {
    "passed": true,
    "status": "pass",
    "issue_count": 0,
    "error_count": 0,
    "warning_count": 0,
    "info_count": 0,
    "checked_file_count": 0
  },
  "inventory": {
    "concept_count": 0,
    "directory_count": 0,
    "reserved_file_count": 0,
    "index_file_count": 0,
    "log_file_count": 0,
    "concept_types": []
  },
  "reserved_files": {
    "root_index_present": false,
    "root_log_present": false,
    "index_issue_count": 0,
    "log_issue_count": 0,
    "malformed_reserved_file_count": 0,
    "malformed_reserved_file_paths": []
  },
  "links": {
    "internal_link_count": 0,
    "resolved_internal_link_count": 0,
    "broken_internal_link_count": 0,
    "external_link_count": 0,
    "concepts_with_broken_internal_links_count": 0,
    "concepts_with_broken_internal_links": []
  },
  "indexes": {
    "directory_count": 0,
    "directories_with_index_count": 0,
    "directories_without_index_count": 0,
    "directories_without_index": [],
    "listed_content_count": 0,
    "unlisted_content_count": 0,
    "unlisted_content_paths": []
  },
  "logs": {
    "log_file_count": 0,
    "newest_entry_date": null,
    "malformed_date_heading_count": 0,
    "ordering_issue_count": 0,
    "log_paths_with_issues": []
  },
  "metadata": {
    "fields": []
  },
  "citations": {
    "concepts_with_citations_count": 0,
    "concepts_with_external_links_count": 0,
    "external_linked_without_citations_count": 0,
    "external_linked_without_citations": []
  },
  "connectivity": {
    "concepts_with_internal_links_count": 0,
    "concepts_without_inbound_count": 0,
    "concepts_without_outbound_count": 0,
    "orphan_concept_count": 0,
    "orphan_concepts": []
  }
}
```

`status` and `summary.status` use the same stable values:

- `ok` when validation passes and there are no warning or error health signals;
- `attention` when validation passes but soft health signals are present;
- `invalid` when validation does not pass.

Health signal counts are derived from the grouped report fields, not from the top-level `issues` array. They summarize report concerns such as broken internal links, malformed reserved files, missing recommended metadata, missing indexes, log ordering issues, external links without detectable citations, and orphan concepts.

`inventory.concept_types` contains objects shaped as:

```json
{ "type": "ArchitectureDecision", "count": 0 }
```

Sort concept type entries by `type`. Concepts with missing or unreadable type values should be represented with a stable placeholder such as `"<missing>"` only when they are present in the readable model.

`metadata.fields` contains one object for each recommended optional frontmatter field: `title`, `description`, `resource`, `tags`, and `timestamp`.

```json
{
  "field": "title",
  "present_count": 0,
  "missing_count": 0,
  "missing_concepts": []
}
```

Sort metadata field entries in the fixed order above. Sort `missing_concepts` by `concept_id`. Missing recommended fields are health signals only; they must not be promoted to validation issues.

Index coverage is based on detectable markdown links in present `index.md` files. Missing `index.md` files are reported as discoverability signals, not validation failures. `listed_content_count` and `unlisted_content_count` count bundle contents that can reasonably be matched to concepts or child directories in the corresponding directory scope. Implementations should not infer failures from prose-only index entries that cannot be resolved as links.

Log freshness is based on present `log.md` date headings. `newest_entry_date` is the newest valid `YYYY-MM-DD` heading found across logs, or `null` when no valid log date exists. Malformed date headings and newest-first ordering issues should align with validation reserved-file checks, but health may aggregate their counts and affected paths for compact display.

Citation detection is intentionally mechanical. A concept has citations when its body contains a markdown heading exactly named `Citations`, case-insensitive after trimming heading markers and surrounding whitespace. A concept with one or more external links and no detectable citations section is a health signal, not a validation issue.

Connectivity is based only on internal concept-to-concept links. External links, reserved-file links, and broken links do not create inbound or outbound connectivity for concepts. An orphan concept is one with no inbound and no outbound resolved internal concept link.

Human output should start with the resolved bundle path and the stable health status, then group the same signal families as the JSON payload: validation, inventory, reserved files, links, indexes, logs, metadata, citations, and connectivity. It should remain concise and path-first, with detail paths shown only where they make the status actionable.

Process failure remains reserved for unreadable bundle paths, discovery ambiguity, invalid CLI input, and unexpected execution errors. A readable bundle with validation failures or poor health signals still uses the success envelope with `ok: true`; the bundle state is expressed by `data.status`, `data.validation`, grouped health fields, and top-level `issues`.

## Consequences

- `health` stays an aggregate projection over existing OKF domain data instead of introducing a separate parser or stricter conformance model.
- Automation gets a stable payload for compact bundle status without scraping human output.
- Soft OKF guidance remains visible without violating the specification's tolerant consumption rules.
- Validation remains authoritative for conformance; health only summarizes and complements it.
- The contract intentionally reports counts and sorted detail lists instead of scores, grades, or historical trends.
- Some signals are heuristic by design, especially citation detection and index coverage, so they must remain non-fatal and mechanically explainable.
- Large bundles may produce long detail lists, but the lists are deterministic and belong in JSON; human output can stay compact.

## Alternatives Considered

A single numeric health score was rejected because it would hide which OKF signals matter and create arbitrary weighting.

Failing the command for poor health was rejected because the OKF specification requires consumers to tolerate missing optional fields, missing indexes, broken cross-links, and incomplete citation coverage.

Embedding validation issues inside `data.validation` was rejected because the shared envelope already defines top-level `issues` as the issue channel.

Fetching external links to verify citations was rejected because `health` must stay local, deterministic, fast, and independent of network access.

Reporting only counts was rejected because deterministic detail paths are needed for actionable human output and scriptable remediation, while still keeping the contract smaller than a full lint report.

## Relations

- [Feature - OKF Health](../features/Feature%20-%20OKF%20Health.md)
- [Feature - OKF Validation](../features/Feature%20-%20OKF%20Validation.md)
- [Feature - OKF Links](../features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](../features/Feature%20-%20OKF%20Backlinks.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [Discovery and Resolution](Discovery%20and%20Resolution.md)
- [Data Contracts](Data%20Contracts.md)
- [Command Flows](Command%20Flows.md)
- [Output and Errors](Output%20and%20Errors.md)
- [Validation Report Contract](Validation%20Report%20Contract.md)
- [Links Command Contract](Links%20Command%20Contract.md)
- [Test Strategy](Test%20Strategy.md)
- [Tooling Roadmap](../Tooling%20Roadmap.md)
