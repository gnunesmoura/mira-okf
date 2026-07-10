---
type: Guide
title: SDD Workflow
description: Defines how bounded product changes become executable SDD packages.
tags:
  - sdd
  - guide
  - workflow
---

# SDD Workflow

## Purpose

Use SDD to turn one bounded product change into an explicit, reviewable, and
verifiable package for implementation agents.

## Reading order

Agents should read:

1. the relevant product feature and references;
2. the current change `spec.md`;
3. `plan.md`;
4. `tasks.md`;
5. `acceptance-tests.md`;
6. `agent-contract.md`.

## Definition flow

1. Product intent and user-visible behavior are clarified in `spec.md`.
2. Technical boundaries, contracts, affected paths, risks, and validation are
   recorded in `plan.md`.
3. Implementation work is split into ordered tasks in `tasks.md`.
4. Observable behavior is mapped to acceptance checks in
   `acceptance-tests.md`.
5. Agent constraints and completion evidence are recorded in
   `agent-contract.md`.
6. The package is reviewed for cross-artifact consistency before it becomes
   `ready`.

## Artifact authoring boundary

Keep frontmatter machine-readable and small: use `type`, `title`,
`description`, `tags`, `status`, and links to the other artifacts in the same
package. Derive artifact identity from the package path and filename. Put
product, architecture, source-path, and supporting-source links in the body,
using `## Related Product and Architecture Context`, `## Affected Source
Paths`, and `# Citations` as applicable. Never move lifecycle state into
prose.

## Boundaries

Product features describe durable capabilities. A change package describes
what is changing now. Reusable technical contracts belong in `architecture/`;
do not copy them into every package.

## Clarification rule

If an unresolved question changes behavior, architecture, persistence,
security, compatibility, or scope, record it and stop the affected work until
the decision is explicit.
