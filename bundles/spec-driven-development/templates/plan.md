---
type: Technical Plan
title: "Technical Plan: [FEATURE NAME]"
description: "Technical implementation plan for [FEATURE NAME]."
tags: [sdd, change, plan, architecture]
change_id: "CHANGE-000"
plan_id: "PLAN-000"
spec_id: "SPEC-000"
status: draft
owner: "[OWNER]"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
related:
  spec: /spec-driven-development/changes/CHANGE-000-short-name/spec.md
  tasks: /spec-driven-development/changes/CHANGE-000-short-name/tasks.md
  acceptance_tests: /spec-driven-development/changes/CHANGE-000-short-name/acceptance-tests.md
  agent_contract: /spec-driven-development/changes/CHANGE-000-short-name/agent-contract.md
  prds: []
  features: []
  architecture: []
  references: []
  source_paths: []
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
