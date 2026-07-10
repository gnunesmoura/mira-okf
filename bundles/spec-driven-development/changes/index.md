# SDD Changes

Change packages are the normative, change-specific home for approved SDD work
in this bundle. Reusable templates live in the parent
[`templates/`](../templates/) directory and are not executable packages.

## Package layout

Each package uses one directory named `<change-id>-<short-name>/`, for example
`CHANGE-001-props/`. The directory contains exactly the package artifacts
needed for the change, with these names:

- `spec.md` - approved intent, scope, non-goals, dependencies, behavior, and
  acceptance criteria.
- `plan.md` - technical direction, affected
  boundaries and contracts, source areas, tests, risks, and decisions.
- `tasks.md` - ordered, verifiable implementation
  tasks and their dependencies.
- `acceptance-tests.md` - observable acceptance checks and
  the repository test evidence required for them.
- `agent-contract.md` - agent constraints,
  authoritative sources, invariants, validation commands, and completion
  evidence.
- `log.md` - chronological package history.

The example directory name documents the package shape only. It is not a
request to create that package in this task.

## Artifact frontmatter

Every package artifact except its reserved `log.md` must be a concept document
with a parseable YAML frontmatter block. The minimum SDD metadata is:

```yaml
---
type: <artifact type>
title: <human-readable title>
description: <one-line summary>
tags: [sdd, change]
change_id: "CHANGE-000"
status: draft
related:
  spec: "/spec-driven-development/changes/CHANGE-000-short-name/spec.md"
  plan: "/spec-driven-development/changes/CHANGE-000-short-name/plan.md"
  tasks: "/spec-driven-development/changes/CHANGE-000-short-name/tasks.md"
  acceptance_tests: "/spec-driven-development/changes/CHANGE-000-short-name/acceptance-tests.md"
  agent_contract: "/spec-driven-development/changes/CHANGE-000-short-name/agent-contract.md"
  prds: []
  features: []
  architecture: []
  references: []
  source_paths: []
---
```

`type`, `title`, `description`, `change_id`, and `status` are required for
every package concept. `related` is required and must retain the package
artifact fields (`spec`, `plan`, `tasks`, `tests`, and `contract`) plus the
context fields (`prds`, `features`, `architecture`, `references`, and
`source_paths`). Relation values are explicit bundle-relative links beginning
with `/`, or empty lists when no relation applies. `log.md` is reserved by OKF,
has no frontmatter, and uses date headings newest first.

Artifact types should identify their role: `Change Specification`, `Technical
Plan`, `Implementation Task List`, `Acceptance Test Suite`, and `Agent Workflow
Contract`. Producers may add fields, but must preserve the local OKF rule that
concept frontmatter has a non-empty `type` and that unknown fields remain
compatible.

## Lifecycle

Package status records change execution state and must advance only with the
corresponding evidence:

`draft -> specified -> planned -> ready -> in_progress -> implemented -> validated`

- `draft` - package is being shaped and is not approved for execution.
- `specified` - approved outcome, scope, non-goals, dependencies, and
  observable acceptance criteria are linked.
- `planned` - technical boundaries, contracts, source areas, tests, risks, and
  decisions are recorded.
- `ready` - ordered tasks, acceptance tests, dependencies, agent constraints,
  and completion evidence are actionable and reviewed.
- `in_progress` - ready work has started.
- `implemented` - scoped source work is complete and implementation evidence
  is recorded.
- `validated` - acceptance checks and focused repository checks pass, and
  affected indexes and logs are synchronized.
- `deprecated` - the package or decision no longer applies.

`in_progress` is not completion evidence. A package must not be treated as a
source of current status when it is absent.

## Navigation and authority

This area is linked from the [bundle index](../../index.md). Package artifacts
must link to relevant [product features](../../product/features/),
[architecture](../../architecture/), [references](../../references/), and
source paths through their `related` fields instead of duplicating those
documents.
The local OKF specification and repository policy govern structure; product,
feature, architecture, package, and implementation evidence then govern their
respective scopes as described in the bundle index.
