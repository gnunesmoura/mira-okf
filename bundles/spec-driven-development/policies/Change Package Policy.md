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

Use canonical bundle-relative paths beginning with `/`. Link product features,
architecture concepts, references, and source paths through `related` instead
of duplicating their content.
