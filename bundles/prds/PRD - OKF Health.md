---
type: PRD
title: PRD - OKF Health
description: Implementation requirements for the profile-based read-only OKF bundle health command and its stable report signals.
tags:
  - tooling
  - okf
  - health
  - cli
  - prd
---

# PRD - OKF Health

## Context

`tooling okf health` is the compact bundle status command for OKF. It should help developers, scripts, and agents understand whether a resolved bundle is usable with a short default profile, while keeping broader quality checks opt-in and explicitly declared. It must not replace `tooling okf validate` or fail on tolerated OKF gaps. It must use the shared semantic analysis boundary so body-derived health signals ignore fenced code blocks and inline code spans in the same way as relationship scanners.

The command must follow the local OKF specification's permissive consumption model: required concept frontmatter and reserved-file structure are conformance concerns, while missing optional metadata, missing `index.md`, broken cross-links, external links without citation sections, and weak connectivity are soft signals that only matter when their rule groups are selected.

## Objective

Implement `tooling okf health [<bundle>] [--json] [--profile <name>]` as a read-only profile-based report over the shared bundle resolver, shared OKF read model, validation summary, and selected health groups.

## Scope

- Resolve exactly one bundle using the shared explicit-path and omitted-path discovery behavior.
- Read the bundle through the shared OKF read model.
- Reuse validation report semantics and issue counts; do not create a second validator.
- Support named health profiles, with `quick` as the default.
- Keep inventory, reserved-file, link, and connectivity signals in the default `quick` profile.
- Keep index, log, metadata, and citation checks opt-in rather than part of the default status.
- Evaluate body-derived signals against the normalized semantic text produced by the shared boundary.
- Reuse links and backlinks extraction where practical for internal, external, broken-link, and connectivity signals.
- Report the selected health groups and explicitly declare which groups were evaluated and which were ignored.
- Emit concise human output and stable JSON output.
- Keep the command read-only and deterministic.
- Preserve existing OKF command behavior.

## Requirements

- The CLI must support `tooling okf health [<bundle>] [--json] [--profile <name>]`.
- The JSON envelope must use `command: "okf.health"` and place only the health report in `data`.
- Read, validation, and health collection issues must remain in the top-level `issues` array.
- A readable bundle must return `ok: true` even when validation fails or health signals are poor.
- Process failure must be reserved for unreadable bundle paths, discovery ambiguity, invalid CLI input, and unexpected execution errors.
- `data.rules` must declare the selected profile and the evaluated versus ignored rule groups.
- `data.status` and `data.summary.status` must be `invalid` when validation does not pass, `attention` when validation passes but warning or error health signals exist in the evaluated rule groups, and `ok` when validation passes with no warning or error health signals in the evaluated rule groups.
- `data.summary` must include `status`, `validation_passed`, `concept_count`, `directory_count`, `warning_signal_count`, and `error_signal_count`; `concept_count` is summarized here and not repeated in `data.validation`.
- `data.validation` must include `passed`, `status`, `issue_count`, `error_count`, `warning_count`, `info_count`, and `checked_file_count` from the validation report contract.
- `data.inventory` must include concept, directory, reserved-file, index-file, log-file, and concept-type counts.
- Concept type entries must be sorted by normalized type name.
- `data.reserved_files` must report root `index.md` and root `log.md` presence, reserved-file issue counts, malformed reserved-file count, and malformed reserved-file paths.
- `data.links` must report internal, resolved internal, broken internal, and external link counts plus concepts with broken internal links.
- Broken internal links must remain tolerated health data, not command failure.
- `data.links` must be derived from the normalized semantic body, not the raw body text.
- `data.indexes` must report `directory_count`, `directories_with_index_count`, `directories_without_index_count`, `directories_without_index`, `listed_content_count`, `unlisted_content_count`, and `unlisted_content_paths` when the index group is selected.
- Missing `index.md` files must be discoverability signals, not validation failures.
- `data.logs` must report `log_file_count`, `newest_entry_date`, `malformed_date_heading_count`, `ordering_issue_count`, and `log_paths_with_issues` when the log group is selected.
- `data.metadata.fields` must contain fixed entries for `title`, `description`, `resource`, `tags`, and `timestamp`, each with present count, missing count, and missing concepts when the metadata group is selected.
- Missing recommended metadata must be health data only, not validation issues.
- Citation detection must be mechanical: a concept has citations only when its body contains a markdown heading exactly named `Citations`, case-insensitive after trimming heading markers and whitespace.
- `data.citations` must report concepts with citations, concepts with external links, and concepts with external links but no detectable citations when the citation group is selected.
- `data.connectivity` must use only resolved internal concept-to-concept links.
- Connectivity signals must use the shared normalized semantic body via links and backlinks extraction.
- Connectivity must report concepts with internal links, concepts without inbound links, concepts without outbound links, and orphan concepts with neither inbound nor outbound resolved internal concept links.
- Path-like detail lists must be sorted by normalized bundle-relative path.
- Name-like detail lists must be sorted by normalized name.
- Human output must start with the resolved bundle path, selected profile, and health status, then group only the selected signal families.
- Human output must stay compact and show detail paths only where they make the report actionable.
- The command must not write files, repair content, fetch external URLs, compute trends, emit opaque scores, add folder conventions, or export props.

## Acceptance Criteria

- `tooling okf health <bundle>` reports health for an explicit readable bundle.
- `tooling okf health` uses shared bundle discovery when `<bundle>` is omitted.
- `tooling okf health --profile quick` uses the minimum default rule set.
- Discovery ambiguity and unreadable paths use the shared failure behavior.
- A readable bundle with validation errors emits `ok: true`, `data.status: "invalid"`, and validation counts.
- A readable bundle with passing validation and selected warning or error health signals emits `data.status: "attention"`.
- A readable bundle with passing validation and no warning or error health signals in the selected groups emits `data.status: "ok"`.
- JSON output contains the stable `rules`, `summary`, `validation`, `inventory`, `reserved_files`, `links`, `indexes`, `logs`, `metadata`, `citations`, and `connectivity` groups.
- Top-level `issues` remains available and is not duplicated as a full issue list inside `data`.
- Inventory counts match the shared read model.
- Reserved-file signals distinguish missing optional reserved files from malformed present reserved files.
- Link signals count resolved internal, broken internal, and external links without failing on broken links.
- Selected index, log, metadata, and citation signals report their respective coverage without changing validation pass/fail behavior.
- Non-selected optional groups do not affect the reported status.
- Content inside fenced code blocks and inline code spans does not contribute to health signals.
- Connectivity signals report orphan concepts using only resolved internal concept links.
- Repeated runs over the same bundle produce stable counts, statuses, and detail ordering.
- Existing `tree`, `list`, `show`, `links`, `backlinks`, and `validate` behavior remains unchanged.

## Minimum Tests

- Resolves an explicit bundle path.
- Uses shared discovery when the bundle argument is omitted.
- Fails deterministically on ambiguous discovery.
- Uses `quick` as the default profile.
- Reports the selected profile and evaluated versus ignored groups in JSON.
- Emits `ok: true` and `data.status: "invalid"` for a readable bundle with validation errors.
- Emits `data.status: "attention"` for passing validation with at least one soft health signal in the selected groups.
- Emits `data.status: "ok"` for passing validation with no warning or error health signals in the selected groups.
- Verifies JSON includes the required `rules` group and no duplicated full issue list inside `data`.
- Verifies validation counts mirror the validation report contract.
- Verifies inventory counts for concepts, directories, reserved files, logs, indexes, and concept types.
- Verifies reserved-file presence, malformed reserved-file paths, and issue counts.
- Verifies broken internal links, resolved internal links, external links, and concepts with broken internal links.
- Verifies selected directory index coverage and detectable unlisted contents.
- Verifies selected newest log date, malformed date headings, ordering issue counts, and affected log paths.
- Verifies selected metadata coverage for `title`, `description`, `resource`, `tags`, and `timestamp`.
- Verifies case-insensitive `Citations` heading detection and external-link-without-citation counts when the citation group is selected.
- Verifies that fenced code blocks and inline code spans are ignored by health evaluation.
- Verifies connectivity counts and orphan concepts from resolved internal concept-to-concept links.
- Verifies deterministic sorting for path-like and name-like details.
- Verifies human output starts with bundle path, profile, and status, then prints only the selected groups.
- Verifies existing OKF command JSON envelope behavior remains unchanged.

## Non-Goals

- Writing, repairing, formatting, or autofixing bundle files.
- Reimplementing validation or changing validation pass/fail semantics.
- Failing command execution solely because of soft health signals that are ignored by the selected profile.
- Opaque scores, grades, trend reporting, or historical comparison.
- Fetching external URLs or verifying citation targets.
- Deciding whether an external claim requires a citation beyond mechanical citation-heading detection.
- Adding new OKF folder conventions.
- Props export or tabular frontmatter projection.
- Changing the shared JSON envelope or existing command output.

## Relations

- [Feature - OKF Health](../features/Feature%20-%20OKF%20Health.md)
- [Health Report Contract](../architecture/Health%20Report%20Contract.md)
- [PRD - OKF Semantic Analysis Boundary](PRD%20-%20OKF%20Semantic%20Analysis%20Boundary.md)
- [PRD - OKF Module](PRD%20-%20OKF%20Module.md)
- [PRD - OKF Validation](PRD%20-%20OKF%20Validation.md)
- [PRD - OKF Links](PRD%20-%20OKF%20Links.md)
- [Validation Report Contract](../architecture/Validation%20Report%20Contract.md)
- [Links Command Contract](../architecture/Links%20Command%20Contract.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Open Knowledge Format Specification](../references/Open%20Knowledge%20Format%20Specification.md)
- [Tooling Roadmap](../Tooling%20Roadmap.md)
