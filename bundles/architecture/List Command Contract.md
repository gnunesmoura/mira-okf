---
type: ArchitectureDecision
title: List Command Contract
description: Defines the concept-only inventory contract for `tooling okf list`.
tags:
  - tooling
  - okf
  - list
  - architecture
---

# List Command Contract

## Decision

`tooling okf list` is the concept inventory command.

It returns concept documents only. Reserved files and directories stay out of the result set because they belong to `tree` and other structural views.

## Contract

- Resolve the bundle using the shared discovery and path rules.
- Inventory concepts from the bundle read model.
- Include all concepts when no filters are supplied.
- Apply `--type` and `--tag` as exact-match filters on concepts.
- Combine filters with AND semantics.
- Sort the final concept list by `concept_id` ascending.
- Apply an optional `--offset` and `--limit` window after filtering and sorting.

## Output

- Human output should be concise, stable, and able to report when the visible slice is truncated.
- JSON output should use the shared envelope and put the windowed concept result object in `data`.
- The top-level `issues` array should carry tolerated read problems without failing the command.

## Boundaries

- Do not add reserved files or directories to the list payload.
- Do not infer extra grouping or summarization that changes the semantic inventory.
- Do not let `list` become a second `tree`.

## Why

- The data model already separates `Concept` from `Directory`.
- The command stays easier to consume when it answers one question: which concepts are present?
- Stable ordering, filter semantics, and explicit windowing keep downstream automation predictable.

## Relation

- [Feature - OKF Concept List](../features/Feature%20-%20OKF%20Concept%20List.md)
- [List Result Windowing](List%20Result%20Windowing.md)
