---
type: PRD
title: PRD - OKF Validation
description: Implementation requirements for read-only OKF bundle validation with stable human and JSON reports.
tags:
  - tooling
  - okf
  - validate
  - cli
  - prd
---

# PRD - OKF Validation

## Context

The `show` feature is complete, so the next roadmap step is `validate`: a read-only conformance report over one resolved OKF bundle.

This PRD does not introduce a new parser or discovery path. It directs implementation of `tooling okf validate` using the shared bundle resolver, shared OKF read model, shared `Issue` contract, and stable output envelope.

Validation reports content conformance issues when the bundle can still be read. Those content issues must remain visible without becoming transport or execution failures.
Per the OKF spec, every non-reserved `.md` file must contain parseable YAML frontmatter; missing top-of-file frontmatter on a concept candidate is therefore an `error` validation issue.

## Objective

Implement `tooling okf validate [<bundle>] [--json]` as a deterministic read-only validation report for one OKF bundle, with concise human output, stable JSON output, and non-fatal handling of readable content issues.

## Scope

- Resolve exactly one bundle through the shared OKF bundle discovery rules.
- Read the bundle through the shared OKF read model.
- Validate bundle markdown files, reserved filenames, concept frontmatter presence, and required concept fields.
- Treat `index.md` and `log.md` as reserved files, not concepts.
- Validate present reserved `index.md` and `log.md` files against OKF structures.
- Count present reserved `index.md` and `log.md` files as checked markdown files.
- Tolerate missing `index.md` files without reporting validation issues.
- Treat non-reserved `.md` files as concept candidates.
- Report concept candidate documents without top-of-file YAML frontmatter as `error` validation issues.
- Report missing or empty `type` as an `error` issue.
- Preserve tolerated reader issues and surface them as validation issues.
- Report missing recommended fields such as `title`, `description`, `resource`, `tags`, or `timestamp` as non-fatal issues only when the reader already exposes them.
- Tolerate unknown frontmatter keys and unknown non-empty `type` values.
- Tolerate broken cross-links unless already surfaced as issues by the shared read model.
- Render a compact human report.
- Emit a stable JSON envelope with validation summary data in `data` and validation issues in the top-level `issues` array.
- Preserve existing JSON and process semantics: readable bundles use `ok: true`, conformance failure is represented by `data.passed: false`, and the top-level `issues` array is authoritative.
- Keep the command read-only, deterministic, and free of repair or auto-fix behavior.

## Requirements

- The CLI must support `tooling okf validate [<bundle>] [--json]`.
- `<bundle>` must use the same explicit-path and omitted-path discovery behavior as other OKF commands.
- Discovery ambiguity, unreadable paths, invalid CLI input, and unexpected execution errors must use the shared failure behavior.
- The command must not duplicate parsing rules in the CLI layer.
- The command must build the validation report from the shared readable bundle result.
- The command must be read-only over the existing bundle read result.
- The command must validate present reserved `index.md` and `log.md` files using shared issue records without creating a parallel concept parser.
- Reserved-file checks must define validation conformance only and must not change parse behavior.
- Reserved `index.md` and `log.md` files must count as checked markdown files but must not be reported as concepts.
- Missing `index.md` files must be tolerated and must not produce validation issues.
- A bundle-root `index.md` without frontmatter must be valid.
- A bundle-root `index.md` with frontmatter containing only `okf_version` must be valid.
- A bundle-root `index.md` with any frontmatter field other than `okf_version` must produce a validation issue.
- A non-root `index.md` with any frontmatter must produce a validation issue.
- A `log.md` date heading must use `YYYY-MM-DD`; invalid date headings must produce validation issues.
- `log.md` date groups must be ordered newest first; out-of-order date groups must produce validation issues.
- Non-reserved `.md` files must be treated as concept candidates.
- Concept candidate files without top-of-file YAML frontmatter must produce `error` validation issues.
- Missing or empty `type` must produce an `error` severity validation issue.
- Missing recommended fields may produce `warning` or `info` validation issues only when those issues already exist in the shared read result.
- Unknown frontmatter keys must not produce failures.
- Unknown non-empty `type` values must not produce failures.
- Broken cross-links must not fail validation unless they are already surfaced as issues by the shared read model.
- Validation issues must use the shared `Issue` fields: `code`, `message`, `severity`, `path`, `line`, `field`, `suggestion`, and `fatal`.
- Validation issue severities must be limited to `info`, `warning`, and `error`.
- Validation issues must be ordered by normalized bundle-relative `path`, then `line` when present, then `field` when present, then `code`.
- The validation summary must include `passed`, `status`, `issue_count`, `error_count`, `warning_count`, `info_count`, `concept_count`, and `checked_file_count`.
- `passed` must be `true` only when the readable bundle has no `error` or `warning` validation issues.
- `status` must be `pass` when `passed` is `true` and `fail` when `passed` is `false`.
- `issue_count` must equal the number of validation issues in the top-level JSON `issues` array.
- `error_count`, `warning_count`, and `info_count` must count issues by severity.
- `concept_count` must equal the number of concept documents in the readable bundle model.
- `checked_file_count` must count markdown files considered by validation, including reserved files and concept candidates.
- Human output must start with the resolved bundle path.
- Human output must show a compact validation summary before listing issues.
- Human output must list issues in the deterministic validation order.
- Human output must be path-first, concise, and actionable.
- JSON mode must use the shared success envelope for readable bundles, even when validation fails.
- JSON mode must place only validation summary data in `data`.
- JSON mode must keep the top-level `issues` array as the authoritative full issue list.
- JSON mode must not duplicate the full issue list inside `data`.
- JSON mode must report readable bundles with `ok: true`; conformance failure must be represented by `data.passed: false` and the top-level `issues` array.
- JSON failure envelopes must stay stable and must be reserved for transport and execution failures.
- The command must not write files, repair content, modify frontmatter, or infer fixes beyond optional issue suggestions.
- Existing OKF commands and their human or JSON output must remain backward-compatible.

## Acceptance Criteria

- `tooling okf validate <bundle>` validates the explicit bundle path.
- `tooling okf validate` uses the shared bundle discovery rules when `<bundle>` is omitted.
- A readable bundle with no `error` or `warning` validation issues reports `passed: true` and `status: "pass"`.
- A readable bundle with any `error` or `warning` validation issue reports `passed: false` and `status: "fail"`.
- A readable bundle with only `info` validation issues still reports `passed: true`.
- Missing or empty concept `type` is reported as an `error` validation issue.
- A non-reserved `.md` concept candidate without top-of-file YAML frontmatter is reported as an `error` validation issue.
- Reserved `index.md` and `log.md` files are checked but are not counted as concepts.
- Missing `index.md` files are not reported as validation issues.
- A bundle-root `index.md` without frontmatter is valid.
- A bundle-root `index.md` with frontmatter containing only `okf_version` is valid.
- A bundle-root `index.md` with any frontmatter field other than `okf_version` is reported as a validation issue.
- A non-root `index.md` with any frontmatter is reported as a validation issue.
- A `log.md` date heading that does not use `YYYY-MM-DD` is reported as a validation issue.
- A `log.md` whose date groups are not newest-first is reported as a validation issue.
- Unknown frontmatter keys do not fail validation.
- Unknown non-empty `type` values do not fail validation.
- Broken cross-links do not fail validation unless the shared read model already surfaces them as issues.
- Human output begins with the bundle path, then a compact summary, then deterministic issue rows when issues exist.
- JSON output uses `ok: true` for readable bundles even when `data.passed` is `false`.
- JSON output places the validation summary in `data`.
- JSON output places validation issues only in the top-level `issues` array.
- Discovery ambiguity and unreadable bundle paths use the shared failure envelope.
- Repeated runs over the same bundle produce stable report counts and issue ordering.
- Existing `tree`, `list`, `links`, `backlinks`, and `show` behavior remains unchanged.

## Minimum Tests

- Validates an explicit bundle path.
- Uses shared discovery when `<bundle>` is omitted.
- Fails deterministically when discovery finds multiple bundle candidates.
- Reports missing or empty `type` as an `error` issue.
- Reports a non-reserved markdown file without top-of-file YAML frontmatter as an `error` issue.
- Does not treat `index.md` or `log.md` as concepts.
- Counts reserved markdown files in `checked_file_count`.
- Counts readable concepts in `concept_count`.
- Allows missing `index.md` files without reporting validation issues.
- Allows bundle-root `index.md` without frontmatter.
- Allows bundle-root `index.md` frontmatter containing only `okf_version`.
- Reports bundle-root `index.md` frontmatter containing fields other than `okf_version`.
- Reports non-root `index.md` frontmatter.
- Reports `log.md` date headings that do not use `YYYY-MM-DD`.
- Reports `log.md` date groups that are not newest-first.
- Tolerates unknown frontmatter keys without failing validation.
- Tolerates unknown non-empty `type` values without failing validation.
- Tolerates broken cross-links unless already surfaced by the shared read model.
- Reports `passed: false` and `status: "fail"` when an `error` or `warning` issue exists.
- Reports `passed: true` and `status: "pass"` when only `info` issues exist.
- Emits JSON with validation summary in `data` and full issues only in the top-level `issues` array.
- Keeps `issue_count` equal to the top-level issue list length.
- Orders issues by path, line, field, and code.
- Keeps readable content issues non-fatal in JSON mode with `ok: true`.
- Uses the shared failure envelope for unreadable bundle paths.
- Verifies existing OKF command JSON envelope behavior remains unchanged.

## Non-Goals

- New bundle discovery rules are out of scope.
- New parsing behavior beyond the shared read model is out of scope.
- Repair, write, autofix, or formatting changes are out of scope.
- Changing shared parse behavior or adding a parallel concept parser is out of scope.
- Validation scoring beyond `passed`, `status`, and issue counts is out of scope.
- Health aggregation is out of scope.
- Property export is out of scope.
- Link graph validation beyond issues already exposed by the reader is out of scope.
- Changing the shared JSON envelope or failure envelope is out of scope.
- Changing existing command output is out of scope.

## Relations

- [PRD - OKF Module](PRD%20-%20OKF%20Module.md)
- [Feature - OKF Validation](../features/Feature%20-%20OKF%20Validation.md)
- [Validation Report Contract](../architecture/Validation%20Report%20Contract.md)
- [Open Knowledge Format Specification](../references/Open%20Knowledge%20Format%20Specification.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Tooling Roadmap](../Tooling%20Roadmap.md)
