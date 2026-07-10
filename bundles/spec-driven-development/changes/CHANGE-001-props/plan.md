---
type: Technical Plan
title: CHANGE-001 props technical plan
description: Sets implementation boundaries, shared contracts, source areas, and risks for props export.
tags: [sdd, change, props, technical-plan]
status: draft
---

# Boundary

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

Implement `props` as a thin projection over the existing resolver, inventory,
and normalized `Concept` records. Planned source areas are the repository
paths in `related.source_paths`; they are areas to inspect or extend, not
evidence of completed work. Do not alter the OKF parser's meaning or add a
second read model.

## Technical Contracts

- The command uses the shared bundle resolution and scan path.
- The supported field contract is the ordered set `type`, `title`,
  `description`, `tags`.
- JSON uses the existing top-level `ok`, `command`, `bundle`, `data`, and
  `issues` envelope. `data` contains selected `fields`, ordered `rows`, and
  row metadata only if needed by the established conventions.
- Human output is concise and path-first; table columns follow selection
  order. CSV has a header and escaped cells according to the standard library.
- Rows sort by `concept_id`, independent of filesystem traversal order.
- Tags preserve source list order; scalar missing fields are null in JSON and
  empty in table/CSV. Unknown explicit fields are an input error.
- Tolerated concept issues remain in the shared issue channel and do not
  silently remove readable rows.

## Source and Test Boundaries

Inspect `src/tooling/okf/read_model.py` and `models.py` for normalized fields,
`src/tooling/okf/commands.py` and `src/tooling/cli.py` for command wiring, and
the existing `tests/test_*.py` patterns for fixtures and CLI assertions.
Create or extend `tests/test_props.py` only as implementation requires. Do
not modify PRDs, features, architecture concepts, indexes, or roadmaps as
part of implementation unless a later approved task explicitly requires it.

## Decisions

1. Reuse normalized fields rather than exporting arbitrary raw frontmatter;
   this keeps unknown producer keys preserved by the reader but outside this
   bounded projection.
2. Reject unknown explicit selections rather than silently dropping columns;
   a typo must be visible to scripts and humans.
3. Sort by `concept_id` and preserve requested field order so repeated exports
   are comparable.
4. Keep read issues visible and non-fatal when the concept remains readable,
   consistent with [Output and Errors](../../architecture/Output%20and%20Errors.md).

## Risks and Mitigations

- Output drift: assert exact envelopes, headers, ordering, and empty values.
- Parser duplication: keep projection logic downstream of `read_model`.
- Mixed frontmatter regressions: use fixtures with missing, unknown, and
  malformed-but-readable metadata.
- CLI compatibility: add only the planned command and format/field options;
  preserve existing commands and exit semantics.

No implementation, test result, or validation is claimed by this draft plan.
