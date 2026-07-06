---
type: Feature
title: Feature - OKF Validation
description: Non-blocking OKF bundle conformance report that exposes existing read issues without changing parsing behavior.
tags:
  - tooling
  - okf
  - validate
  - cli
---

# Feature - OKF Validation

## Objective

Provide a read-only `validate` command that reports OKF bundle conformance issues in a concise human view or stable JSON payload, while keeping tolerated content issues non-fatal when the bundle can still be read.

## Scope

- `tooling okf validate [<bundle>] [--json]` validates one resolved OKF bundle.
- The command uses the shared bundle discovery rules.
- The command reports conformance issues found while reading the bundle.
- Validation covers bundle markdown files, reserved filenames, concept frontmatter presence, and required concept fields.
- `index.md` and `log.md` are recognized as reserved files and are not reported as concepts.
- Non-reserved `.md` files are treated as concept candidates.
- Concept documents without top-of-file YAML frontmatter are reported as `error`-level validation issues.
- Missing or empty `type` is reported as an `error` issue.
- Reserved `index.md` and `log.md` files are validated against their required OKF structures when present.
- Missing `index.md` files are tolerated and must not be reported as validation issues.
- `index.md` files normally reject frontmatter; the only allowed exception is bundle-root `index.md` frontmatter containing only `okf_version`.
- `index.md` frontmatter outside the bundle root, or root `index.md` frontmatter with fields other than `okf_version`, is reported as a validation issue.
- `log.md` date headings that do not use `YYYY-MM-DD` are reported as validation issues.
- `log.md` date groups that are not ordered newest first are reported as validation issues.
- Missing recommended fields such as `title`, `description`, `resource`, `tags`, or `timestamp` may be reported as non-fatal issues when the reader already exposes them.
- Unknown frontmatter keys are tolerated and must not fail validation.
- Unknown non-empty `type` values are tolerated and must not fail validation.
- Broken cross-links are tolerated and must not fail validation unless they are already exposed as issues by the shared read model.
- Human output starts with the bundle path and a compact validation summary, then lists issues in deterministic path-first order.
- JSON output uses the shared envelope and places the validation report in `data`.
- Top-level `issues` remains the authoritative list of validation issues in JSON output.
- Content issues do not make the command a transport or execution failure when the bundle can still be read.

## Out of Scope

- Writing, repairing, formatting, or auto-fixing bundle files.
- Adding new OKF folder conventions.
- Rejecting unknown concept types.
- Rejecting unknown frontmatter keys.
- Changing the permissive parsing model.
- Health scoring, quality grading, or trend reporting.
- Failing validation for broken links beyond issues already exposed by the shared read model.
- Property export or tabular frontmatter projection.
- Concept detail rendering, which belongs to `show`.

## User Flow

1. A user runs `tooling okf validate` inside a bundle or provides an explicit bundle path.
2. The CLI resolves the bundle using shared discovery.
3. The CLI reads the bundle using the existing OKF read model.
4. The CLI collects tolerated issues into a validation report.
5. The CLI prints a concise path-first human report or emits the shared JSON envelope.
6. If the bundle cannot be resolved or read at all, the CLI returns the shared failure envelope or human error.

## Acceptance Criteria

- `tooling okf validate <bundle>` prints a validation report for the resolved bundle.
- `tooling okf validate` uses shared automatic bundle discovery when `<bundle>` is omitted.
- When discovery finds more than one bundle candidate, the command fails deterministically and lists the candidates.
- A readable bundle with no issues reports a passing validation summary.
- A readable bundle with warnings or errors reports a non-passing validation summary without treating content issues as fatal execution failures.
- Human output includes the bundle-relative path for each reported issue when a path is available.
- Human output includes issue severity, code, message, and actionable suggestion when available.
- JSON output uses `{ ok, command, bundle, data, issues }`.
- JSON output sets `command` to `okf.validate`.
- JSON output places validation summary data in `data`.
- JSON output keeps validation issues in the shared top-level `issues` array using the shared issue fields.
- Missing or empty concept `type` appears as an `error` issue.
- Missing top-of-file YAML frontmatter in a non-reserved concept candidate appears as an `error` validation issue and makes the validation summary non-passing.
- `index.md` and `log.md` are not counted or reported as concept documents.
- Present `index.md` files are validated as reserved directory listings, not concepts.
- Missing `index.md` files do not appear as validation issues.
- A bundle-root `index.md` without frontmatter is valid.
- A bundle-root `index.md` with frontmatter containing only `okf_version` is valid.
- A bundle-root `index.md` with frontmatter fields other than `okf_version` appears as a validation issue.
- A non-root `index.md` with frontmatter appears as a validation issue.
- Present `log.md` files are validated as reserved update logs, not concepts.
- A `log.md` date heading that is not ISO `YYYY-MM-DD` appears as a validation issue.
- A `log.md` whose date groups are not newest first appears as a validation issue.
- Unknown frontmatter keys do not fail validation.
- Unknown non-empty `type` values do not fail validation.
- Broken cross-links do not fail validation unless the shared read model already reports them as issues.
- Repeated runs against the same bundle state produce the same report order and output shape.

## Minimum Tests

- Validates a readable bundle with no issues.
- Reports missing top-of-file YAML frontmatter for a non-reserved markdown concept candidate as an `error` issue and a non-passing validation summary.
- Reports missing `type` as an `error` issue.
- Reports empty `type` as an `error` issue.
- Tolerates unknown frontmatter keys.
- Tolerates unknown non-empty concept type values.
- Excludes `index.md` and `log.md` from concept validation.
- Validates present `index.md` files as reserved directory listings.
- Allows missing `index.md` files.
- Allows bundle-root `index.md` frontmatter with only `okf_version`.
- Reports non-root `index.md` frontmatter.
- Reports bundle-root `index.md` frontmatter containing fields other than `okf_version`.
- Validates present `log.md` files as reserved update logs.
- Reports a `log.md` date heading that is not `YYYY-MM-DD`.
- Reports `log.md` date groups that are not newest first.
- Tolerates broken cross-links unless already exposed as reader issues.
- Emits deterministic path-first human output.
- Emits stable JSON with `command: "okf.validate"`, validation data, and top-level issues.
- Preserves content issues as non-fatal for a readable bundle.
- Fails cleanly when bundle discovery is ambiguous.
- Fails cleanly when the bundle cannot be read at all.

## Relations

- [Tooling Roadmap](../Tooling%20Roadmap.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [PRD - OKF Validation](../prds/PRD%20-%20OKF%20Validation.md)
- [Validation Report Contract](../architecture/Validation%20Report%20Contract.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Feature - OKF Show](Feature%20-%20OKF%20Show.md)
