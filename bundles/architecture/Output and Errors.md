---
type: ArchitectureDecision
title: Output and Errors
description: Defines the stable JSON envelope, human output rules, and issue semantics.
tags:
  - tooling
  - okf
  - output
---

# Output and Errors

## JSON Envelope

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

## Command Payloads

- `tree` should place the rendered directory inventory in `data`.
- `list` should place the filtered concept array in `data`.
- `show` should place the resolved concept object in `data`.
- Future commands should reuse the same top-level envelope and only vary the payload inside `data`.

## Human Output

- Keep human output concise and path-first.
- Make `tree`, `list`, and `show` visually distinct but structurally consistent.
- Do not rely on color or terminal width for meaning.

## Ordering

- Sort directories by bundle-relative path.
- Sort concepts by `concept_id`.
- Sort JSON arrays deterministically.
- Preserve source order for lists where the source order is meaningful, such as tag lists and body text.

## Issue Semantics

- `info`, `warning`, and `error` are the only severity levels.
- Content issues stay non-fatal unless the bundle cannot be read at all.
- `fatal` is reserved for transport and execution failures, not for tolerated OKF content problems.
