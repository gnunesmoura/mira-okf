---
type: ArchitectureDecision
title: List Result Windowing
description: Defines the bounded result model for `tooling okf list`.
tags:
  - tooling
  - okf
  - list
  - architecture
---

# List Result Windowing

## Context

`list` needs to support exact-match filtering, stable ordering, full match counts, and bounded browsing without turning into a structural tree view. The result contract has to carry both the current slice and enough metadata for humans and automation to know whether they are looking at the whole match set.

## Decision

`tooling okf list` returns a windowed inventory object in JSON mode.

- Apply `--type` and `--tag` filters first.
- Sort the full filtered match set by `concept_id` ascending.
- Apply an optional `--offset` and `--limit` window to the sorted matches.
- When no explicit window is supplied, return the full filtered match set.
- Reject negative `--offset` and `--limit` inputs before constructing the result window.
- Represent the JSON payload in `data` as an object with:
    - `concepts`: the concept slice for the current window;
    - `total`: total matched concepts before windowing;
    - `returned`: number of concepts in `concepts`;
    - `offset`: zero-based start of the current window;
    - `limit`: requested window size or `null`;
    - `truncated`: `true` when the current payload does not contain the full filtered match set.

Human output may apply a readability cap, but that cap is a presentation choice and must not alter the sorted filtered inventory used by JSON mode.

## Consequences

- Callers can tell the difference between no matches and matches hidden by a window.
- The command gains a stable browsing model for large bundles.
- JSON consumers need to read `data.concepts` instead of assuming `data` is an array.
- The contract stays deterministic because filtering, sorting, and windowing happen in one defined order.
- Invalid window arguments fail early instead of producing misleading empty slices.

## Alternatives Considered

- Keep `data` as a bare array and add counts elsewhere. Rejected because the envelope would not carry enough information about the current window.
- Use cursor-based pagination. Rejected for the MVP because offset/limit is easier to reason about for fixed, sorted concept inventories.

## Relations

- [Feature - OKF Concept List](../features/Feature%20-%20OKF%20Concept%20List.md)
- [List Command Contract](List%20Command%20Contract.md)
- [Data Contracts](Data%20Contracts.md)
- [Output and Errors](Output%20and%20Errors.md)
