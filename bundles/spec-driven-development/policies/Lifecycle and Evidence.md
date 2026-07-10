---
type: Policy
title: Lifecycle and Evidence
description: Defines SDD lifecycle transitions and the evidence required for promotion.
tags:
  - sdd
  - policy
  - lifecycle
---

# Lifecycle and Evidence

## Lifecycle

```text
draft -> specified -> planned -> ready -> in_progress -> implemented -> validated
```

- `draft`: package is being shaped.
- `specified`: intent, scope, non-goals, dependencies, and acceptance criteria
  are approved.
- `planned`: technical boundaries, contracts, source areas, tests, risks, and
  decisions are recorded.
- `ready`: tasks, acceptance tests, agent constraints, and completion evidence
  are actionable and consistent.
- `in_progress`: implementation has started.
- `implemented`: scoped source work is complete and task evidence is recorded.
- `validated`: acceptance checks and focused repository checks pass.

File presence is not evidence. A package must not advance because its
artifacts merely exist.

## Promotion rule

Record the commands, results, changed paths, edge-case evidence, synchronized
documents, and unresolved risks before claiming implementation or validation.
