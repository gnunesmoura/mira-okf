---
type: Feature
title: Feature - OKF Backlinks
description: Backlinks command for OKF bundles that reports which concepts point to a resolved concept.
tags:
  - tooling
  - okf
  - backlinks
  - cli
---

# Feature - OKF Backlinks

## Objective

Help people, scripts, and skills answer one question for a resolved concept: which other concepts reference it in the current OKF bundle.

## Scope

- `tooling okf backlinks [<bundle>] <concept-id-or-path> [--json]` resolves one concept and lists incoming links to it.
- The command uses the shared bundle discovery and target resolution rules.
- The command reuses the same link extraction and normalization rules as `tooling okf links`.
- The result is concept-scoped and ordered deterministically.
- Broken or unresolved references are reported as tolerated issues, not fatal failures.
- JSON output uses the shared envelope and places the backlinks payload in `data`.
- Human output stays concise and path-first.

## Out of Scope

- Outbound link discovery belongs to `tooling okf links`.
- Structural browsing belongs to `tooling okf tree`.
- Concept inventory belongs to `tooling okf list`.
- Concept body reading belongs to `tooling okf show`.
- Link rewriting, editing, and automatic repair are out of scope.
- Validation and health scoring are out of scope.

## User Flow

1. A user provides a bundle path or lets the CLI discover the bundle.
2. The CLI resolves the requested concept by the documented `show` precedence.
3. The CLI collects incoming references that target the resolved concept.
4. The CLI renders a compact human view or a stable JSON payload.
5. The CLI includes tolerated read issues without failing the command unless the bundle cannot be read.

## Acceptance Criteria

- `tooling okf backlinks <bundle> <concept>` returns only references that target the resolved concept.
- The command accepts concept IDs and bundle-relative paths as target forms.
- The command fails deterministically when the target cannot be resolved.
- The output is stable across repeated runs for the same bundle state.
- JSON mode includes the resolved concept and the backlink payload in `data`.
- Tolerated link or read issues appear in `issues` without forcing command failure.
- The command does not invent references that are not present in the bundle read model.
- The command uses the same target-resolution precedence as `show`.

## Minimum Tests

- Resolves a concept by concept ID.
- Resolves a concept by bundle-relative path.
- Returns multiple incoming references for a concept with more than one backlink.
- Returns an empty backlink list for a concept with no inbound references.
- Preserves deterministic ordering of backlink results.
- Emits stable JSON for the resolved concept payload.
- Preserves tolerated issues without failing the command.
- Fails cleanly when the target concept cannot be resolved.

## Relations

- [PRD - Python Tooling Library and CLI](../prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Feature - OKF Links](Feature%20-%20OKF%20Links.md)
