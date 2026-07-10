---
type: Technical Plan
title: "Technical Plan: [FEATURE NAME]"
description: "Technical implementation plan for [FEATURE NAME]."
tags: [sdd, change, plan, architecture]
status: draft
---

# Technical Plan: [FEATURE NAME]

## Spec Reference

This plan implements [the linked feature spec](spec.md).

## Summary

[Summarize the technical approach without redefining product behavior.]

## Technical Context

| Item | Decision |
|---|---|
| Language / runtime | [Existing repository runtime] |
| Project type | [CLI / library / service] |
| Source of truth | [Markdown / filesystem / other] |
| Test framework | [Command or framework] |
| Validation | [Commands] |

## Related Product and Architecture Context

- [Product feature or architecture concept](/architecture/example.md)

## Affected Source Paths

- `/src/example.py`

## Citations

- [Supporting or normative source](/references/example.md)

## Architecture Constraints

- [Linked architecture boundary or contract]
- [Invariant that must remain unchanged]

## Design Overview

```text
[High-level flow]
```

## Affected Components

| Component / Path | Change | Reason |
|---|---|---|
| `[path]` | [Change] | [Why] |

## Data / CLI / API Design

[Describe affected records, files, command shape, output, and errors.]

## Test Strategy

- Unit tests: [Targets]
- Integration or CLI tests: [Flows]
- Regression tests: [Risks]

## Validation Commands

```bash
[focused validation command]
[full repository validation command]
git diff --check
```

## Migration and Rollback

- Migration: [None or steps]
- Rollback: [Steps]

## Risks and Trade-offs

| Risk | Impact | Mitigation |
|---|---|---|
| [Risk] | [Impact] | [Mitigation] |

## Alternatives Considered

- [Alternative]: [Reason accepted or rejected]

## Agent Implementation Notes

Agents MUST keep changes within the affected paths, add or update tests, and
report validation evidence. Architecture-boundary changes require an explicit
decision or update to the linked architecture concept.
