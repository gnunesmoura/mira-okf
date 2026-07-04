---
type: PRD
title: PRD - OKF Concept List
description: Implementation requirements for the concept inventory command with exact-match filters and bounded browsing.
tags:
  - tooling
  - okf
  - list
  - cli
  - prd
---

# PRD - OKF Concept List

## Context

The OKF module already defines the bundle read model, stable JSON envelope, and the `tooling okf list` contract. The product feature behind this PRD is a concept inventory command that answers one question clearly: which concept documents exist in a resolved OKF bundle?

The command must stay separate from structural navigation. Reserved files such as `index.md` and `log.md` belong to tree views, not to concept inventory.

## Objective

Implement `tooling okf list` as a deterministic concept-only inventory command for OKF bundles, with exact-match `--type` and `--tag` filters, stable ordering, bounded browsing, and JSON output that is safe for automation and agent workflows.

## Scope

- Read concepts from a resolved OKF bundle using the shared bundle discovery and parsing layer.
- Return concept documents only.
- Support exact-match filtering by `--type` and `--tag`.
- Combine `--type` and `--tag` with AND semantics.
- Sort the final result set by `concept_id` ascending.
- Support windowing with `--offset` and `--limit` after filtering and sorting.
- Reject negative `--offset` and `--limit` values as invalid user input.
- Emit a stable human-readable summary that includes the bundle-relative path for each concept, and the shared JSON envelope.
- Preserve tolerated read issues in the top-level `issues` array.

## Requirements

- `tooling okf list [<bundle>] [--type <type>] [--tag <tag>] [--offset <n>] [--limit <n>] [--json]` must be supported.
- `<bundle>` must accept relative and absolute paths, and omitted bundle paths must use the shared discovery rules.
- The command must exclude reserved files and structural directories from the inventory payload.
- `--type` must match concept `type` exactly.
- `--tag` must match an individual tag exactly.
- When both filters are provided, a concept must satisfy both to appear in the result.
- Sorting must be stable and deterministic across repeated runs.
- `--offset` and `--limit` must accept only non-negative integers.
- Negative `--offset` and `--limit` values must fail with a non-zero exit status and an actionable error.
- JSON output must place the windowed inventory object in `data`.
- The `data` object must include `concepts`, `total`, `returned`, `offset`, `limit`, and `truncated`.
- `total` must represent the full filtered match count before windowing.
- `truncated` must be `true` whenever the current payload does not include the full filtered match set.
- Human output must include the bundle-relative path for each concept so the listed item can be located quickly.
- Tolerated read problems must not fail the command unless the bundle cannot be read at all.

## Acceptance Criteria

- `tooling okf list <bundle>` returns every concept in the resolved bundle and nothing else.
- `tooling okf list <bundle> --type <type>` returns only concepts whose `type` exactly matches `<type>`.
- `tooling okf list <bundle> --tag <tag>` returns only concepts whose tags include `<tag>`.
- `tooling okf list <bundle> --type <type> --tag <tag>` returns only concepts that satisfy both filters.
- The result order is always sorted by `concept_id` ascending.
- `tooling okf list <bundle> --offset <n> --limit <m>` returns a bounded slice of the filtered set.
- JSON output includes the full match count and window metadata in `data`.
- JSON output marks truncated or bounded views explicitly.
- Reserved files remain excluded from the list output.
- Tolerated read issues are preserved in `issues` without forcing a command failure.

## Minimum Tests

- Lists every concept in a fixture bundle with no filters.
- Applies `--type` as an exact-match filter.
- Applies `--tag` as an exact-match filter.
- Applies both filters with AND semantics.
- Returns deterministic ordering after filtering.
- Returns the expected `total`, `returned`, `offset`, `limit`, and `truncated` values for a bounded window.
- Emits stable JSON for the windowed concept payload.
- Preserves tolerated read issues in the JSON envelope.
- Excludes `index.md` and `log.md` from the concept inventory.
- Rejects negative `--offset` and `--limit` values.
- Includes bundle-relative paths in human output.

## Non-Goals

- Structural navigation and directory summaries belong to `tooling okf tree`.
- Concept detail reading belongs to `tooling okf show`.
- Link, backlink, health, validation, and aggregation features are out of scope.
- Grouping concepts by type or tag in the output is out of scope.
- Changing the shared JSON envelope is out of scope.
- Inferring concepts from non-Markdown sources is out of scope.
- Silent coercion of invalid window arguments is out of scope.

## Relations

- [PRD - Python Tooling Library and CLI](PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](PRD%20-%20OKF%20Module.md)
- [Feature - OKF Concept List](../features/Feature%20-%20OKF%20Concept%20List.md)
- [List Command Contract](../architecture/List%20Command%20Contract.md)
- [List Result Windowing](../architecture/List%20Result%20Windowing.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
