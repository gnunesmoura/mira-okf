---
type: Feature
title: Feature - OKF Show
description: Single-concept read path for OKF bundles with deterministic target resolution and end-of-output issues visibility.
tags:
  - tooling
  - okf
  - show
  - cli
---

# Feature - OKF Show

## Objective

Provide one reliable command for opening a single OKF concept in a bundle, keeping the concept body first in human output and appending tolerated issues at the end when present.

## Scope

- `tooling okf show [<bundle>] <concept-id-or-path> [--summary] [--json]` reads one resolved concept from the bundle.
- The command uses the shared bundle discovery rules and the documented `show` target precedence.
- The command accepts concept IDs and bundle-relative paths.
- The command renders a readable human view of the resolved concept first, then appends an `Issues` section at the end when tolerated issues are present.
- The `Issues` section is omitted when the resolved concept has no tolerated issues.
- `--summary` presents a shorter readout of the same resolved concept.
- `--summary` keeps the same end-of-output issues visibility.
- Tolerated read issues remain visible in the result without interrupting the concept rendering flow.
- JSON output continues to return the resolved concept object in `data` and the shared top-level `issues` array.
- Output stays deterministic for the same bundle state.

## Out of Scope

- Structural browsing belongs to `tree`.
- Concept inventory belongs to `list`.
- Outbound links belong to `links`.
- Inbound links belong to `backlinks`.
- Validation, health scoring, property export, editing, and repair are out of scope.
- Showing warnings before the concept content is out of scope.
- Splitting resolution and rendering into separate feature concepts is out of scope.

## User Flow

1. A user points the CLI at a bundle or lets it discover one.
2. The user provides a concept ID or bundle-relative path.
3. The CLI resolves the target using the documented `show` precedence.
4. The CLI renders the concept first in human mode and appends an `Issues` section at the end when tolerated issues exist.
5. The CLI renders a concise human view or a stable JSON payload.
6. If the target cannot be resolved, the CLI reports a clear not-found error.

## Acceptance Criteria

- `tooling okf show <bundle> <concept>` returns the resolved concept.
- `tooling okf show <bundle> <concept>` accepts both concept IDs and bundle-relative paths.
- `tooling okf show --summary <bundle> <concept>` returns a summarized view of the same resolved concept.
- `tooling okf show --json <bundle> <concept>` places the resolved concept object in `data`.
- Omitting `<bundle>` uses the shared bundle discovery rules.
- When discovery finds more than one bundle candidate, the command fails deterministically and lists the candidates.
- A missing target produces a clear not-found error and a non-zero exit status.
- When the resolved concept has tolerated issues, human output ends with an `Issues` section that lists them after the concept content.
- When the resolved concept has no tolerated issues, human output does not show an `Issues` section.
- Tolerated read issues remain visible and do not fail the command when the concept is still readable.
- Repeated runs against the same bundle state produce the same visible output shape.
- Human output is concise, path-first, and focused on one concept.

## Minimum Tests

- Resolves a concept by concept ID.
- Resolves a concept by bundle-relative path.
- Applies the documented target precedence when one target string could match more than one form.
- Shows a summarized view for `--summary`.
- Renders an `Issues` section after the concept content when tolerated issues are present.
- Omits the `Issues` section when the resolved concept has no tolerated issues.
- Emits stable JSON for the resolved concept payload.
- Preserves tolerated read issues without failing the command.
- Fails cleanly when the target concept cannot be resolved.
- Fails deterministically when bundle discovery finds more than one candidate.

## Relations

- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Feature - Summarized OKF Navigation](Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Feature - OKF Concept List](Feature%20-%20OKF%20Concept%20List.md)
- [Feature - OKF Backlinks](Feature%20-%20OKF%20Backlinks.md)
