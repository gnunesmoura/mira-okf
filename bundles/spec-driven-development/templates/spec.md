---
type: Feature Spec
title: "[FEATURE NAME]"
description: "[One-line summary of the change.]"
tags: [sdd, change]
status: draft
---

# Feature Spec: [FEATURE NAME]

## Intent

[What problem is being solved, for whom, and why now?]

## Context

[Describe the current state and link relevant product, feature, domain,
architecture, and reference concepts.]

## Related Product and Architecture Context

- [Product feature or architecture concept](/product/features/example.md)

## Affected Source Paths

- `/src/example.py`

## Citations

- [Supporting or normative source](/references/example.md)

## Problem Statement

[Who cannot do what, why, and with what impact?]

## Desired Outcome

[Describe the observable result and measurable success conditions.]

## Scope

- [Included behavior]

## Non-Goals

- [Explicitly excluded behavior]

## Users / Actors

| Actor | Description | Goal |
|---|---|---|
| [ACTOR] | [Who or what acts] | [Desired result] |

## User Stories and Acceptance Scenarios

### US-001 — [Story title]

As [actor], I want [capability], so that [benefit].

```gherkin
Given [initial state]
When [action]
Then [observable result]
```

## Functional Requirements

- **FR-001**: The system SHALL [specific behavior].
- **FR-002**: The system SHALL NOT [forbidden behavior].

## EARS Requirements

- **REQ-001**: WHEN [trigger], THE SYSTEM SHALL [response].
- **REQ-002**: IF [precondition], WHEN [trigger], THE SYSTEM SHALL [response].

## Domain Rules

- **DR-001**: [Business or domain rule].

## Open Questions

- **Q-001**: [Question to resolve before `reviewed` or `ready`].

## Agent Notes

Agents MUST read the linked plan, tasks, acceptance tests, and agent contract.
Agents MUST NOT implement non-goals or modify unrelated source paths.
