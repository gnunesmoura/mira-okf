---
type: Implementation Task List
title: "Tasks: [FEATURE NAME]"
description: "Discrete implementation tasks for [FEATURE NAME]."
tags: [sdd, change, tasks, implementation]
change_id: "CHANGE-000"
tasks_id: "TASKS-000"
spec_id: "SPEC-000"
plan_id: "PLAN-000"
status: draft
owner: "[OWNER]"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
related:
  spec: /spec-driven-development/changes/CHANGE-000-short-name/spec.md
  plan: /spec-driven-development/changes/CHANGE-000-short-name/plan.md
  acceptance_tests: /spec-driven-development/changes/CHANGE-000-short-name/acceptance-tests.md
  agent_contract: /spec-driven-development/changes/CHANGE-000-short-name/agent-contract.md
  prds: []
  features: []
  architecture: []
  references: []
  source_paths: []
---

# Tasks: [FEATURE NAME]

## Execution Rules

Agents MUST execute one task at a time, keep tasks independently reviewable,
update status, and record validation evidence. Agents MUST NOT implement
future tasks or modify non-listed paths without justification.

## Status Legend

```text
[ ] not started
[/] in progress
[x] done
[!] blocked
[-] removed
```

## Phase 0 — Preparation

- [ ] **T000** Read `spec.md`, `plan.md`, `acceptance-tests.md`, and
  `agent-contract.md`.
  - Done when: scope, non-goals, dependencies, and validation commands are clear.

## Phase 1 — Tests / Characterization

- [ ] **T001** Add or update tests for current behavior.
  - Paths: `[test paths]`
  - Done when: existing behavior is captured and tests pass.

- [ ] **T002** Add failing tests for the desired behavior.
  - Depends on: T001
  - Done when: failure demonstrates the specified gap.

## Phase 2 — Implementation

- [ ] **T003** Implement the specified behavior.
  - Paths: `[source paths]`
  - Depends on: T002
  - Done when: focused tests pass and invariants hold.

## Phase 3 — Validation and Closeout

- [ ] **T004** Run acceptance tests, repository checks, and `git diff --check`.
  - Depends on: T003
  - Done when: results and unresolved risks are recorded in the package log.
