---
type: Agent Workflow Contract
title: "Agent Contract: [FEATURE NAME]"
description: "Rules for agents implementing [FEATURE NAME]."
tags: [sdd, change, agent, workflow, guardrails]
change_id: "CHANGE-000"
contract_id: "AGENT-000"
spec_id: "SPEC-000"
status: draft
owner: "[OWNER]"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
related:
  spec: /spec-driven-development/changes/CHANGE-000-short-name/spec.md
  plan: /spec-driven-development/changes/CHANGE-000-short-name/plan.md
  tasks: /spec-driven-development/changes/CHANGE-000-short-name/tasks.md
  acceptance_tests: /spec-driven-development/changes/CHANGE-000-short-name/acceptance-tests.md
  prds: []
  features: []
  architecture: []
  references: []
  source_paths: []
---

# Agent Workflow Contract: [FEATURE NAME]

## Required Reading Order

Agents MUST read:

1. `spec.md`
2. `plan.md`
3. `tasks.md`
4. `acceptance-tests.md`
5. Relevant linked product, feature, architecture, and reference concepts.

## Scope Boundary

The agent may change:

```text
[allowed source and test paths]
```

The agent must not change:

```text
[forbidden paths or behaviors]
```

## Invariants

- [Invariant that must remain true]
- [Compatibility or safety rule]
- [No mutation / no unrelated behavior rule, when applicable]

## Implementation Mode

- Work one task at a time.
- Keep changes traceable to task IDs.
- Do not implement non-goals or solve adjacent problems.
- Prefer small, reviewable changes.

## Clarification Policy

If a requirement is ambiguous, mark the task blocked, record the question in
`spec.md`, and do not guess when the choice affects behavior, architecture,
persistence, security, or compatibility.

## Validation and Closeout Evidence

Run the commands from `plan.md` and the acceptance suite. Report changed
source/test files, command results, edge-case evidence, synchronized durable
documents, and unresolved risks before changing package status.
