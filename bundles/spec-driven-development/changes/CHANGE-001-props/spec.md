---
type: Change Specification
title: CHANGE-001 props specification
description: Defines the bounded read-only frontmatter property export for existing OKF concepts.
tags: [sdd, change, props, okf]
status: draft
---

# Intent

Add a read-only `tooling okf props` projection for the existing normalized
frontmatter fields `type`, `title`, `description`, and `tags`. The approved
owner is the Product Develop Team; human maintainer approval was recorded on
2026-07-10 in the [Tooling Roadmap](../../Tooling%20Roadmap.md#approved-sdd-pilot).

## Scope

- Accept an optional bundle path and an optional ordered field selection.
- Use all four approved fields by default.
- Render a concise human table and machine-readable JSON or CSV when selected.
- Keep output read-only and preserve the existing shared resolver and read model.
- Define behavior for missing fields, explicitly selected unknown fields, empty
  bundles, mixed frontmatter, and stable ordering.

Missing normalized fields are represented as `null` in JSON, an empty cell in
table and CSV output, and missing tags normalize to an empty list. A readable
concept with malformed or mixed frontmatter remains visible with its existing
issues and whatever normalized values can be read. Concepts sort by
`concept_id`; selected columns retain the requested order.

An explicitly selected field outside `type`, `title`, `description`, and
`tags` is rejected as an actionable input error before a partial export is
returned. An empty bundle returns a successful empty result with the selected
columns and no rows. The default selection is exactly
`type,title,description,tags`.

## Non-goals

- Mutating bundles, source documents, or frontmatter.
- Defining a new property schema or creating a `props` concept.
- Exporting arbitrary unknown frontmatter keys.
- Release-governance or public-release work.

## Dependencies and Context

The change depends on the shared read model and output conventions in the
[Data Contracts](../../../architecture/Data%20Contracts.md), [Output and Errors](../../../architecture/Output%20and%20Errors.md),
and [Command Flows](../../../architecture/Command%20Flows.md). Product context is
the [Tooling Product](../../../product/Product%20Overview.md) and
[Summarized OKF Navigation](../../../product/features/Feature%20-%20Summarized%20OKF%20Navigation.md).
The [OKF specification](../../references/Open%20Knowledge%20Format%20Specification.md)
and [Going Open Source Roadmap](../../Going%20Open%20Source%20Roadmap.md) remain
constraints and context. No props PRD or feature concept exists yet.

## Related Product and Architecture Context

- [Tooling Product](/product/Product%20Overview.md)
- [Summarized OKF Navigation](/product/features/Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Data Contracts](/architecture/Data%20Contracts.md)
- [Output and Errors](/architecture/Output%20and%20Errors.md)
- [Command Flows](/architecture/Command%20Flows.md)

## Affected Source Paths

- `/src/tooling/okf/read_model.py`
- `/src/tooling/okf/models.py`
- `/src/tooling/okf/commands.py`
- `/src/tooling/cli.py`
- `/tests/test_list.py`
- `/tests/test_show.py`
- `/tests/test_cli_bootstrap.py`
- `/tests/support.py`

## Citations

- [Open Knowledge Format Specification](/references/Open%20Knowledge%20Format%20Specification.md)
- [Tooling Roadmap](/Tooling%20Roadmap.md)
- [Going Open Source Roadmap](/Going%20Open%20Source%20Roadmap.md)

## Acceptance Criteria

1. A default invocation exports the four approved fields from every readable
   concept without changing the bundle.
2. Explicit selection supports any non-empty ordered subset of the four
   fields and rejects unknown names deterministically.
3. Missing values, empty bundles, mixed frontmatter, and tolerated read issues
   have the behaviors defined above.
4. Human table, JSON, and CSV outputs are documented, stable, and distinguish
   empty cells from execution errors.
5. Concepts and output arrays have stable ordering across repeated runs.
6. Regression tests cover the shared reader, command, output formats, and the
   listed edge cases.

The package can advance to `ready` only after these criteria, the [technical
plan](plan.md), [tasks](tasks.md), [acceptance tests](acceptance-tests.md), and [agent
contract](agent-contract.md) are reviewed together.
