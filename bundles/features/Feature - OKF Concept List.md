---
type: Feature
title: Feature - OKF Concept List
description: Concept inventory command for OKF bundles with exact-match filters, stable output, and large-bundle safeguards.
tags:
  - tooling
  - okf
  - list
  - cli
---

# Feature - OKF Concept List

## Objective

Help people, scripts, and skills inspect the concepts in an OKF bundle without mixing in structural files or directory summaries.

## Scope

- `tooling okf list` returns concept documents only.
- The command ignores reserved files and structural directories in its primary result set.
- When no filters are supplied, the command lists every concept in the resolved bundle.
- `--type` and `--tag` apply as exact-match filters.
- `--type` and `--tag` combine with AND semantics when both are present.
- Results are sorted by `concept_id` ascending.
- Human output is concise and path-first so users can locate a concept quickly.
- Human and JSON output stay stable for automation and skills.
- The command reports total matched concepts so users know whether they are browsing a small or large bundle.
- The command supports chunked browsing of large inventories through bounded result windows.

## Out of Scope

- Structural navigation output belongs to `tooling okf tree`.
- Link and backlink discovery are separate features.
- Grouped, summarized, or inferred concept rollups are not part of this command.
- Rich aggregation and cross-concept analytics are not part of this command.

## Why This Exists

`tree` answers "what structure exists". `list` answers "what concepts exist".

The command gives scripts and agents a fast way to answer:

- what concepts exist;
- which types are present;
- which tags are in use;
- where a concept lives in the bundle.

## User Flow

1. A user points the CLI at a bundle or lets it resolve the bundle path.
2. The CLI reads the bundle and collects concepts.
3. Optional `--type` and `--tag` filters narrow the concept set.
4. Optional bounds keep large result sets readable and browsable.
5. The CLI prints a compact, path-first human view or a stable JSON payload from the same filtered list.

## Acceptance Criteria

- `tooling okf list <bundle>` returns concept documents only.
- `tooling okf list <bundle>` includes every concept in the resolved bundle when no filters are set.
- `tooling okf list <bundle> --type <type>` returns only concepts whose type exactly matches `<type>`.
- `tooling okf list <bundle> --tag <tag>` returns only concepts whose tags include `<tag>`.
- `tooling okf list <bundle> --type <type> --tag <tag>` returns only concepts that satisfy both filters.
- Large result sets can be browsed in bounded windows without changing the stable sort order.
- Output order is stable and sorted by `concept_id`.
- JSON output places the filtered concept window object in `data`.
- Top-level `issues` still carry tolerated read problems.
- Reserved files remain visible in `tree`, not in `list`.
- Human output includes the bundle-relative path for each listed concept.
- `--offset` and `--limit` reject negative values instead of silently normalizing them.
- Invalid window arguments produce an actionable error and a non-zero exit status.

## Minimum Tests

- Lists every concept in a valid bundle.
- Applies `--type` correctly.
- Applies `--tag` correctly.
- Applies both filters together with AND semantics.
- Returns deterministic order after filtering.
- Emits stable JSON for the filtered concept window.
- Preserves tolerated read issues without failing the command.
- Reports the total matched count alongside truncated or bounded result sets.
- Includes the bundle-relative path in human output.
- Rejects negative `--offset` and `--limit` values.

## Relations

- [PRD - Python Tooling Library and CLI](../prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [List Command Contract](../architecture/List%20Command%20Contract.md)
- [Feature - Summarized OKF Navigation](Feature%20-%20Summarized%20OKF%20Navigation.md)
