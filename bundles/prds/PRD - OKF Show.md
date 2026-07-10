---
type: PRD
title: PRD - OKF Show
description: Implementation requirements for the canonical single-concept read path in OKF bundles.
tags:
  - tooling
  - okf
  - show
  - cli
  - prd
---

# PRD - OKF Show

## Context

The roadmap makes `show` the next OKF PRD to create and the canonical single-concept read path. The feature draft already defines the user-facing behavior: shared discovery, fixed target precedence, summary mode, JSON output, tolerated issues, and deterministic rendering. `show` remains the raw presentation path and must stay outside the shared semantic analysis boundary used by relationship and health scanners.

This PRD does not introduce new architecture. It translates the existing `Discovery and Resolution`, `Command Flows`, `Data Contracts`, and `Output and Errors` decisions into implementation requirements for `tooling okf show`.

The implementation change is limited to human output formatting: the resolved concept renders first, and tolerated issues append as an `Issues` section at the end when present. JSON output stays on the existing envelope and issue contract.

## Objective

Implement `tooling okf show` as the deterministic read path for one resolved OKF concept, using the shared bundle resolver and shared read model, while preserving tolerated issues, stable human and JSON output, and the end-of-output `Issues` section for human mode.

## Scope

- Resolve the bundle through the shared discovery path used by the other OKF commands.
- Resolve exactly one target concept using the documented `show` precedence.
- Return the parsed concept and its tolerated issues without changing the read model contract.
- Render the resolved concept first in human mode, then append an `Issues` section at the end only when tolerated issues are present.
- Omit the `Issues` section when the resolved concept has no tolerated issues.
- Support `--summary` as a narrower human presentation of the same resolved concept while keeping the same end-of-output warning behavior.
- Support JSON mode with the resolved concept object in `data` and tolerated issues in the top-level `issues` array.
- Keep the command read-only and deterministic for repeated runs over the same input.
- Preserve the existing stable error envelope for discovery failures, resolution failures, and other command errors.

## Requirements

- `tooling okf show [<bundle>] <concept-id-or-path> [--summary] [--json]` must be supported.
- `<bundle>` must use the shared bundle discovery and resolution rules already defined for OKF commands.
- The target must resolve in this order:
    - Exact `concept_id` match.
    - Bundle-relative path with `.md` normalized.
    - Bundle-relative file path.
- Resolution must stop at the first successful match and must not fall back to a different interpretation after a match is found.
- If the target cannot be resolved, the command must fail with a single not-found error for that target.
- The command must reuse the shared OKF read model and must not build a show-specific model.
- The resolved concept object must include the normalized concept identity and all readable content already covered by the shared contracts.
- Tolerated issues for the resolved concept must remain visible and must not force a failure when the content is still readable.
- Human output must render the resolved concept first, then append an `Issues` section only when tolerated issues exist.
- Human output must omit the `Issues` section when no tolerated issues exist.
- `--summary` must preserve the same end-of-output warning behavior as the default human mode.
- Human output must remain concise, path-first, and deterministic.
- Summary mode must reduce human output detail without changing the resolved concept, issue collection, or JSON payload shape.
- JSON mode must place the resolved concept object in `data`.
- JSON output must keep the top-level `issues` array for tolerated read problems and must not change the human warning-block behavior.
- Output ordering, field ordering, and issue ordering must remain stable across repeated runs for the same bundle and target.
- The command must not introduce any new parsing rules, discovery rules, or target-heuristic behavior beyond the shared contracts.

## Acceptance Criteria

- `tooling okf show <bundle> <concept>` resolves the requested concept through the documented precedence.
- `tooling okf show <bundle> <concept> --json` returns the resolved concept object in `data`.
- `tooling okf show <bundle> <concept> --summary` renders the same resolved concept in a compact human view.
- Human output shows the concept first and appends an `Issues` section at the end only when tolerated issues are present.
- Human output omits the `Issues` section when there are no tolerated issues.
- `--summary` preserves the same end-of-output warning behavior as the default human view.
- `tooling okf show` without a resolvable target fails with one not-found error and no alternate fallback interpretation.
- Tolerated issues remain visible in the command output and do not block readable concepts.
- Repeated runs over the same bundle and target produce deterministic output.
- Discovery ambiguity uses the shared discovery error behavior rather than a show-specific variant.
- JSON mode continues to emit the resolved concept in `data` and tolerated issues in the top-level `issues` array.

## Minimum Tests

- Resolves a concept by exact `concept_id`.
- Resolves a concept by bundle-relative path with `.md` normalization.
- Resolves a concept by bundle-relative file path.
- Returns the resolved concept object in JSON mode.
- Preserves tolerated issues in the JSON envelope.
- Renders the resolved concept before the `Issues` section when tolerated issues are present.
- Omits the `Issues` section when no tolerated issues are present.
- Renders summary mode without changing the resolved target or end-of-output warning behavior.
- Fails with a single not-found error for an unresolved target.
- Uses the shared bundle discovery path when `<bundle>` is omitted.
- Produces stable output for the same fixture bundle and target across repeated runs.

## Non-Goals

- `links`, `backlinks`, `validate`, `health`, and `props` are out of scope.
- New discovery rules, target heuristics, or alternate precedence chains are out of scope.
- Changing the shared JSON envelope is out of scope.
- Adding write, repair, or auto-fix behavior is out of scope.
- Introducing show-specific frontmatter projection or relationship traversal is out of scope.
- Replacing the shared read model with a new show-only model is out of scope.
- Changing the resolved concept data contract is out of scope.

## Relations

- [PRD - Python Tooling Library and CLI](PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](PRD%20-%20OKF%20Module.md)
- [Feature - OKF Show](../features/Feature%20-%20OKF%20Show.md)
- [PRD - OKF Semantic Analysis Boundary](PRD%20-%20OKF%20Semantic%20Analysis%20Boundary.md)
- [Tooling Roadmap](../Tooling%20Roadmap.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
