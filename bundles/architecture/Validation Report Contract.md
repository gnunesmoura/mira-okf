---
type: ArchitectureContract
title: Validation Report Contract
description: Defines the read-only validation report payload, ordering, and pass/fail semantics for `tooling okf validate`.
tags:
  - tooling
  - okf
  - validate
  - architecture
---

# Validation Report Contract

## Scope and Context

`validate` should report OKF bundle conformance using the shared resolver, read model, issue fields, and JSON envelope. It should not introduce a stricter parser, a second scan model, write behavior, or command-specific issue semantics.

The local OKF specification makes `index.md` and `log.md` reserved filenames at any depth. They are not concepts, but they are still part of bundle conformance when present: `index.md` is a directory listing, `log.md` is a newest-first update log, and missing `index.md` files are explicitly tolerated.

The specification also defines one narrow frontmatter exception: a bundle-root `index.md` may declare only `okf_version`. No other `index.md` frontmatter is valid.

For concept candidates, the OKF contract requires top-of-file YAML frontmatter. A non-reserved `.md` file without that frontmatter is a validation error, not a warning or informational issue.

## Payload and Behavior Contract

`tooling okf validate` is a read-only report over the existing bundle read result.

The command should:

- resolve one bundle through the shared discovery rules;
- read the bundle through the shared OKF read model;
- treat reserved `index.md` and `log.md` files as bundle metadata, not concepts;
- validate present reserved `index.md` and `log.md` files against their OKF structures using issue records, without creating a parallel concept parser;
- tolerate missing `index.md` files without reporting validation issues;
- treat non-reserved `.md` files as concept candidates;
- classify a non-reserved concept candidate without top-of-file YAML frontmatter as an `error` validation issue;
- surface existing read issues as validation issues without changing parse behavior;
- tolerate unknown frontmatter keys and unknown non-empty `type` values;
- tolerate broken cross-links unless they are already exposed as issues by the shared read model;
- order reported issues deterministically by normalized bundle-relative path, then line when present, then field when present, then code;
- keep validation issues in the shared top-level JSON `issues` array;
- place only validation summary data in `data`.

Reserved-file validation should follow these rules:

- a bundle-root `index.md` without frontmatter is valid;
- a bundle-root `index.md` with frontmatter containing only `okf_version` is valid;
- a bundle-root `index.md` with any frontmatter field other than `okf_version` is a validation issue;
- a non-root `index.md` with any frontmatter is a validation issue;
- a `log.md` date heading that does not use `YYYY-MM-DD` is a validation issue;
- a `log.md` whose date groups are not ordered newest first is a validation issue.

These checks define validation conformance, not parse behavior. The shared read model remains the source of bundle inventory and tolerated reader issues; `validate` only projects those results and reserved-file conformance issues into the common issue contract.

The JSON envelope remains:

```json
{
  "ok": true,
  "command": "okf.validate",
  "bundle": {},
  "data": {},
  "issues": []
}
```

The `data` payload should contain a minimal validation report summary:

- `passed`: boolean validation result;
- `status`: stable string summary such as `pass` or `fail`;
- `issue_count`: total number of validation issues in the top-level `issues` array;
- `error_count`: number of `error` severity validation issues;
- `warning_count`: number of `warning` severity validation issues;
- `info_count`: number of `info` severity validation issues;
- `concept_count`: number of concept documents in the readable bundle model;
- `checked_file_count`: number of markdown files considered by validation, including reserved files and concept candidates.

The top-level `issues` array is authoritative. The `data` payload must not duplicate the full issue list.

Validation passes when the readable bundle has no `error` or `warning` validation issues. `info` issues may be reported without making the report fail. A readable bundle with any `error` or `warning` issue has `passed: false` and `status: "fail"`.

Process failure is reserved for transport and execution failures, including unreadable bundle paths, discovery ambiguity, invalid CLI input, and unexpected execution errors. Content conformance issues do not make the command fail when the bundle can still be read. In JSON mode, a readable bundle with validation issues still uses the success envelope with `ok: true`; the validation failure is expressed by `data.passed: false` and the top-level `issues`.

## Consequences

- `validate` stays a projection over the existing read model instead of becoming a parallel parser.
- Reserved files are checked as structural bundle metadata while staying excluded from concept counts and concept validation.
- The root `index.md` `okf_version` exception is explicit and narrow, preventing version metadata from becoming a general frontmatter escape hatch.
- Missing `index.md` files and broken cross-links remain compatible with the OKF permissive consumption model.
- Concept candidates without top-of-file YAML frontmatter are counted as `error` issues, so they keep the pass/fail summary aligned with the OKF requirement for frontmatter at the start of every concept document.
- Automation can distinguish command execution success from bundle conformance failure.
- Human and JSON output remain consistent with existing OKF commands.
- Future `health` work can aggregate validation outcomes without redefining issue semantics.
- The report is intentionally small; richer diagnostics belong in issue records, not in a second validation-specific schema.

## Invariants

Validation remains read-only and projects the shared read result into the common envelope; `data` contains summary fields only, while the top-level `issues` array remains authoritative for individual validation issues.

## Alternatives Considered

A stricter validation parser was rejected because it would create different behavior from `tree`, `list`, `show`, and `links`.

Treating reserved files as concepts was rejected because the OKF contract gives `index.md` and `log.md` structural meanings at any depth.

Rejecting all `index.md` frontmatter was rejected because the OKF versioning rule allows `okf_version` only in the bundle-root `index.md`.

Failing validation for missing `index.md` files or broken cross-links was rejected because the OKF specification requires consumers to tolerate both cases.

Putting validation issues inside `data` was rejected because `Output and Errors` already makes the top-level `issues` array the shared issue channel.

Failing the process for readable bundles with content errors was rejected because the OKF read model is intentionally permissive and exposes tolerated issues without blocking consumption.

## Compatibility Rules

Preserve shared issue codes, severity meanings, ordering, reserved-file rules, and envelope placement so validation can be consumed alongside `health` without redefining conformance.

## Relations

- [Feature - OKF Validation](../product/features/Feature%20-%20OKF%20Validation.md)
- [Data Contracts](Data%20Contracts.md)
- [Command Flows](Command%20Flows.md)
- [Output and Errors](Output%20and%20Errors.md)
- [Discovery and Resolution](Discovery%20and%20Resolution.md)
- [Test Strategy](Test%20Strategy.md)
- [Tooling Roadmap](../Tooling%20Roadmap.md)
- [Open Knowledge Format Specification](../references/Open%20Knowledge%20Format%20Specification.md)
