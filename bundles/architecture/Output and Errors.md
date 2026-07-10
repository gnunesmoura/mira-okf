---
type: ArchitectureContract
title: Output and Errors
description: Defines the stable JSON envelope, human output rules, and issue semantics for OKF commands.
tags:
  - tooling
  - okf
  - output
  - show
---

# Output and Errors

## Scope

This contract is authoritative for shared command envelopes, payload placement, human-output conventions, ordering, and tolerated-versus-fatal issue behavior.

## Payload and Behavior Contract

### JSON Envelope

All commands should emit the same top-level shape in JSON mode:

```json
{
  "ok": true,
  "command": "okf.tree",
  "bundle": {},
  "data": {},
  "issues": []
}
```

On failure:

```json
{
  "ok": false,
  "command": "okf.tree",
  "bundle": null,
  "data": null,
  "issues": [],
  "error": {
    "code": "OKF_DISCOVERY_AMBIGUOUS",
    "message": "More than one OKF bundle found",
    "details": {}
  }
}
```

Keep key names stable and predictable so automation can consume them without special casing each command.

### Command Payloads

- `tree` should place the rendered directory inventory in `data`.
- `list` should place the windowed concept result object in `data`.
- `show` should place the resolved concept object in `data`.
- Future commands should reuse the same top-level envelope and only vary the payload inside `data`.

### Human Output

- Keep human output concise, path-first, and actionable.
- Make `tree`, `list`, and `show` visually distinct but structurally consistent.
- `list` should show the bundle-relative path for each concept, alongside the concept identity and other compact summary fields when available.
- `list` may note when a visible slice is truncated, but the JSON payload must carry the authoritative `total` and window metadata.
- `show` should render the resolved concept first and append an `Issues` section at the end only when tolerated issues are present.
- `show` should omit the `Issues` section when there are no tolerated issues.
- `show` summary mode should keep the same end-of-output warning behavior.
- Do not rely on color or terminal width for meaning.
- Do not silently coerce invalid CLI inputs such as negative window bounds.

### Ordering

- Sort directories by bundle-relative path.
- Sort concepts by `concept_id`.
- Sort JSON arrays deterministically.
- Preserve source order for lists where the source order is meaningful, such as tag lists and body text.

## Issue Semantics

- `info`, `warning`, and `error` are the only severity levels.
- Content issues stay non-fatal unless the bundle cannot be read at all.
- `fatal` is reserved for transport and execution failures, not for tolerated OKF content problems.

## Invariants

Every JSON response uses the shared envelope, places command data under `data`, keeps arrays deterministic, and preserves the distinction between tolerated content issues and fatal execution errors.

## Compatibility Rules

Existing envelope keys, issue severity values, payload locations, and ordering rules are compatibility-sensitive; future commands extend `data` without inventing a second top-level shape.

## Relations

- [Feature - OKF Show](../product/features/Feature%20-%20OKF%20Show.md)
- [Command Flows](Command%20Flows.md)
