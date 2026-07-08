---
type: PRD
title: PRD - OKF Health
description: Implementation requirements for the read-only OKF bundle health command and its stable report signals.
tags:
  - tooling
  - okf
  - health
  - cli
  - prd
---

# PRD - OKF Health

## Context

`tooling okf health` is the compact bundle status command for OKF. It should help developers, scripts, and agents understand whether a resolved bundle is conformant, discoverable, documented, cited, and connected without replacing `tooling okf validate` or failing on tolerated OKF gaps.

The command must follow the local OKF specification's permissive consumption model: required concept frontmatter and reserved-file structure are conformance concerns, while missing optional metadata, missing `index.md`, broken cross-links, external links without citation sections, and weak connectivity are health signals.

## Objective

Implement `tooling okf health [<bundle>] [--json]` as a read-only aggregate report over the shared bundle resolver, shared OKF read model, validation summary, and link extraction data.

## Scope

- Resolve exactly one bundle using the shared explicit-path and omitted-path discovery behavior.
- Read the bundle through the shared OKF read model.
- Reuse validation report semantics and issue counts; do not create a second validator.
- Reuse links and backlinks extraction where practical for internal, external, broken-link, and connectivity signals.
- Report health groups for validation, inventory, reserved files, links, indexes, logs, metadata, citations, and connectivity.
- Emit concise human output and stable JSON output.
- Keep the command read-only and deterministic.
- Preserve existing OKF command behavior.

## Requirements

- The CLI must support `tooling okf health [<bundle>] [--json]`.
- The JSON envelope must use `command: "okf.health"` and place only the health report in `data`.
- Read, validation, and health collection issues must remain in the top-level `issues` array.
- A readable bundle must return `ok: true` even when validation fails or health signals are poor.
- Process failure must be reserved for unreadable bundle paths, discovery ambiguity, invalid CLI input, and unexpected execution errors.
- `data.status` and `data.summary.status` must be `invalid` when validation does not pass, `attention` when validation passes but warning or error health signals exist, and `ok` when validation passes with no warning or error health signals.
- `data.summary` must include `status`, `validation_passed`, `concept_count`, `directory_count`, `warning_signal_count`, and `error_signal_count`.
- `data.validation` must include `passed`, `status`, `issue_count`, `error_count`, `warning_count`, `info_count`, and `checked_file_count` from the validation report contract.
- `data.inventory` must include concept, directory, reserved-file, index-file, log-file, and concept-type counts.
- Concept type entries must be sorted by normalized type name.
- `data.reserved_files` must report root `index.md` and root `log.md` presence, reserved-file issue counts, malformed reserved-file count, and malformed reserved-file paths.
- `data.links` must report internal, resolved internal, broken internal, and external link counts plus concepts with broken internal links.
- Broken internal links must remain tolerated health data, not command failure.
- `data.indexes` must report directory index coverage and detectable linked versus unlisted bundle contents.
- Missing `index.md` files must be discoverability signals, not validation failures.
- `data.logs` must report log count, newest valid entry date, malformed date heading count, ordering issue count, and log paths with issues.
- `data.metadata.fields` must contain fixed entries for `title`, `description`, `resource`, `tags`, and `timestamp`, each with present count, missing count, and missing concepts.
- Missing recommended metadata must be health data only, not validation issues.
- Citation detection must be mechanical: a concept has citations only when its body contains a markdown heading exactly named `Citations`, case-insensitive after trimming heading markers and whitespace.
- `data.citations` must report concepts with citations, concepts with external links, and concepts with external links but no detectable citations.
- `data.connectivity` must use only resolved internal concept-to-concept links.
- Connectivity must report concepts with internal links, concepts without inbound links, concepts without outbound links, and orphan concepts with neither inbound nor outbound resolved internal concept links.
- Path-like detail lists must be sorted by normalized bundle-relative path.
- Name-like detail lists must be sorted by normalized name.
- Human output must start with the resolved bundle path and health status, then group validation, inventory, reserved files, links, indexes, logs, metadata, citations, and connectivity.
- Human output must stay compact and show detail paths only where they make the report actionable.
- The command must not write files, repair content, fetch external URLs, compute trends, emit opaque scores, add folder conventions, or export props.

## Acceptance Criteria

- `tooling okf health <bundle>` reports health for an explicit readable bundle.
- `tooling okf health` uses shared bundle discovery when `<bundle>` is omitted.
- Discovery ambiguity and unreadable paths use the shared failure behavior.
- A readable bundle with validation errors emits `ok: true`, `data.status: "invalid"`, and validation counts.
- A readable bundle with passing validation and soft health signals emits `data.status: "attention"`.
- A readable bundle with passing validation and no warning or error health signals emits `data.status: "ok"`.
- JSON output contains the stable `summary`, `validation`, `inventory`, `reserved_files`, `links`, `indexes`, `logs`, `metadata`, `citations`, and `connectivity` groups.
- Top-level `issues` remains available and is not duplicated as a full issue list inside `data`.
- Inventory counts match the shared read model.
- Reserved-file signals distinguish missing optional reserved files from malformed present reserved files.
- Link signals count resolved internal, broken internal, and external links without failing on broken links.
- Index signals report directories without `index.md` and detectable unlisted contents without requiring every directory to have an index.
- Log signals report newest valid date, malformed date headings, and newest-first ordering issues.
- Metadata signals report coverage for all five recommended fields without changing validation pass/fail behavior.
- Citation signals report external-link concepts without a detectable `Citations` heading.
- Connectivity signals report orphan concepts using only resolved internal concept links.
- Repeated runs over the same bundle produce stable counts, statuses, and detail ordering.
- Existing `tree`, `list`, `show`, `links`, `backlinks`, and `validate` behavior remains unchanged.

## Minimum Tests

- Resolves an explicit bundle path.
- Uses shared discovery when the bundle argument is omitted.
- Fails deterministically on ambiguous discovery.
- Emits `ok: true` and `data.status: "invalid"` for a readable bundle with validation errors.
- Emits `data.status: "attention"` for passing validation with at least one soft health signal.
- Emits `data.status: "ok"` for passing validation with no warning or error health signals.
- Verifies JSON includes all required health groups and no duplicated full issue list inside `data`.
- Verifies validation counts mirror the validation report contract.
- Verifies inventory counts for concepts, directories, reserved files, logs, indexes, and concept types.
- Verifies reserved-file presence, malformed reserved-file paths, and issue counts.
- Verifies broken internal links, resolved internal links, external links, and concepts with broken internal links.
- Verifies directory index coverage and detectable unlisted contents.
- Verifies newest log date, malformed date headings, ordering issue counts, and affected log paths.
- Verifies metadata coverage for `title`, `description`, `resource`, `tags`, and `timestamp`.
- Verifies case-insensitive `Citations` heading detection and external-link-without-citation counts.
- Verifies connectivity counts and orphan concepts from resolved internal concept-to-concept links.
- Verifies deterministic sorting for path-like and name-like details.
- Verifies human output starts with bundle path and status, then prints the required groups.
- Verifies existing OKF command JSON envelope behavior remains unchanged.

## Non-Goals

- Writing, repairing, formatting, or autofixing bundle files.
- Reimplementing validation or changing validation pass/fail semantics.
- Failing command execution solely because of soft health signals.
- Opaque scores, grades, trend reporting, or historical comparison.
- Fetching external URLs or verifying citation targets.
- Deciding whether an external claim requires a citation beyond mechanical citation-heading detection.
- Adding new OKF folder conventions.
- Props export or tabular frontmatter projection.
- Changing the shared JSON envelope or existing command output.

## Relations

- [Feature - OKF Health](../features/Feature%20-%20OKF%20Health.md)
- [Health Report Contract](../architecture/Health%20Report%20Contract.md)
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
