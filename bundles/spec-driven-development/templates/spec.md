---
type: Feature Spec
title: "[FEATURE NAME]"
description: "[One-line summary of the change.]"
tags: [sdd, change]
change_id: "CHANGE-000"
spec_id: "SPEC-000"
status: draft
owner: "[OWNER]"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
related:
  plan: /spec-driven-development/changes/CHANGE-000-short-name/plan.md
  tasks: /spec-driven-development/changes/CHANGE-000-short-name/tasks.md
  acceptance_tests: /spec-driven-development/changes/CHANGE-000-short-name/acceptance-tests.md
  agent_contract: /spec-driven-development/changes/CHANGE-000-short-name/agent-contract.md
  prds: []
  features: []
  architecture: []
  references: []
  source_paths: []
---

# Feature Spec: [FEATURE NAME]

## Intent

[What problem is being solved, for whom, and why now?]

## Context

[Describe the current state and link relevant product, feature, domain,
architecture, and reference concepts.]

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
