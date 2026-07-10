---
type: Acceptance Test Suite
title: "Acceptance Tests: [FEATURE NAME]"
description: "Behavioral acceptance tests for [FEATURE NAME]."
tags: [sdd, change, acceptance-tests, verification]
change_id: "CHANGE-000"
tests_id: "TESTS-000"
spec_id: "SPEC-000"
plan_id: "PLAN-000"
status: draft
owner: "[OWNER]"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
related:
  spec: /spec-driven-development/changes/CHANGE-000-short-name/spec.md
  plan: /spec-driven-development/changes/CHANGE-000-short-name/plan.md
  tasks: /spec-driven-development/changes/CHANGE-000-short-name/tasks.md
  agent_contract: /spec-driven-development/changes/CHANGE-000-short-name/agent-contract.md
  prds: []
  features: []
  architecture: []
  references: []
  source_paths: []
---

# Acceptance Tests: [FEATURE NAME]

## Purpose

This document defines the observable checks that prove the feature was
implemented correctly.

## Test Matrix

| Requirement | Story | Test Type | Test Name | Status |
|---|---|---|---|---|
| FR-001 | US-001 | [unit / integration / CLI] | `[test name]` | planned |

## Scenarios

### AT-001 — [Scenario title]

Covers: FR-001, REQ-001, US-001.

```gherkin
Given [initial state]
When [action]
Then [expected observable result]
```

Implementation target: `[test path]`

Expected command:

```bash
[focused test command]
```

## Negative Scenarios

### AT-N001 — [Invalid input or edge condition]

```gherkin
Given [invalid state or input]
When [action]
Then [safe error behavior]
And [no invalid state or partial write]
```

## Regression Scenarios

### AT-R001 — [Existing behavior remains unchanged]

```gherkin
Given [existing behavior]
When [same action as before]
Then [previous result still works]
```

## Manual Verification

| Check | Steps | Expected result |
|---|---|---|
| [Check] | [Steps] | [Result] |

## Completion Rule

Every P1 requirement must have an automated check, every relevant edge case
must be covered or justified, and all validation commands from `plan.md` must
pass before the package advances to `validated`.
