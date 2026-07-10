---
type: Policy
title: Change Package Policy
description: Defines the structure, metadata, and relation rules for SDD change packages.
tags:
  - sdd
  - policy
  - change
---

# Change Package Policy

## Required shape

Every change package lives under
`spec-driven-development/changes/<change-id>-<short-name>/` and contains:

- `spec.md`;
- `plan.md`;
- `tasks.md`;
- `acceptance-tests.md`;
- `agent-contract.md`;
- `log.md`.

All artifacts except `log.md` are OKF concepts with parseable frontmatter.
`log.md` has no frontmatter and records chronological history.

## Ownership

- Tech PM owns `spec.md`.
- Architect owns `plan.md`.
- Tech Lead owns `tasks.md`, `acceptance-tests.md`, and `agent-contract.md`.
- The master coordinates package creation and consistency checks.

Agents must work within declared paths and must not create parallel PRDs,
features, or architecture concepts unless explicitly requested.

## Relations

Use canonical bundle-relative paths beginning with `/` for contextual links.
Package artifact membership is derived from the canonical package directory and
filenames; product features, architecture concepts, references, and source
paths belong in the relevant body sections.

## Metadata boundary

Keep package frontmatter to the smallest machine-readable control plane:
`type`, `title`, `description`, `tags`, and `status`.
Derive `change_id` and artifact identity from the canonical package directory
and filename. Do not add owner, created/updated timestamps, artifact IDs, or
retired PRD relations unless an actual validator or workflow requires them.

Put human and contextual relations in body sections: `## Related Product and
Architecture Context`, `## Affected Source Paths`, and `# Citations`.
`status` remains frontmatter because lifecycle tooling must read it without
interpreting prose. Use bundle-root-relative links beginning with `/`.
