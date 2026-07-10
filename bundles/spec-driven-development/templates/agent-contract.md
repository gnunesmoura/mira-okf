---
type: Agent Workflow Contract
title: "Agent Contract: [FEATURE NAME]"
description: "Rules for agents implementing [FEATURE NAME]."
tags: [sdd, change, agent, workflow, guardrails]
status: draft
---

# Agent Workflow Contract: [FEATURE NAME]

## Related Product and Architecture Context

- [Product feature or architecture concept](/product/features/example.md)

## Affected Source Paths

- `/src/example.py`

## Citations

- [Supporting or normative source](/references/example.md)

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
