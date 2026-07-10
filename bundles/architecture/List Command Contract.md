---
type: ArchitectureContract
title: List Command Contract
description: Defines the concept-only inventory contract for `tooling okf list`.
tags:
  - tooling
  - okf
  - list
  - architecture
---

# List Command Contract

## Scope

This contract defines the concept-only inventory behavior of `tooling okf list`; structural directory and reserved-file views remain outside its payload.

## Decision

`tooling okf list` is the concept inventory command.

It returns concept documents only. Reserved files and directories stay out of the result set because they belong to `tree` and other structural views.

## Payload and Behavior Contract

- Resolve the bundle using the shared discovery and path rules.
- Inventory concepts from the bundle read model.
- Include all concepts when no filters are supplied.
- Apply `--type` and `--tag` as exact-match filters on concepts.
- Combine filters with AND semantics.
- Sort the final concept list by `concept_id` ascending.
- Apply an optional `--offset` and `--limit` window after filtering and sorting.
- Reject negative `--offset` and `--limit` values instead of coercing them.

## Invariants

The result contains only concepts, is sorted by `concept_id`, applies filters before windowing, and never silently coerces invalid window inputs.

## Output

- Human output should be concise, stable, path-first, and able to show the bundle-relative location of each concept.
- JSON output should use the shared envelope and put the windowed concept result object in `data`.
- The top-level `issues` array should carry tolerated read problems without failing the command.

## Boundaries

- Do not add reserved files or directories to the list payload.
- Do not infer extra grouping or summarization that changes the semantic inventory.
- Do not let `list` become a second `tree`.
- Do not silently normalize invalid window inputs.

## Why

- The data model already separates `Concept` from `Directory`.
- The command stays easier to consume when it answers one question: which concepts are present?
- Stable ordering, filter semantics, and explicit windowing keep downstream automation predictable.
- Human output is more useful when it identifies the concept and where to find it.

## Compatibility Rules

Keep the shared envelope, read-model concept fields, exact-match filter semantics, and window metadata compatible with [List Result Windowing](List%20Result%20Windowing.md).

## Relations

- [Feature - OKF Concept List](../product/features/Feature%20-%20OKF%20Concept%20List.md)
- [List Result Windowing](List%20Result%20Windowing.md)
