---
type: ArchitectureDecision
title: Discovery and Resolution
description: Defines bundle discovery, ambiguity handling, and show target resolution.
tags:
  - tooling
  - okf
  - discovery
---

# Discovery and Resolution

## Bundle Discovery

When `<bundle>` is provided, treat it as a path to a bundle root directory and resolve it relative to the current working directory when needed.

When `<bundle>` is omitted, inspect the current directory tree in deterministic path order:

1. check the current directory itself;
2. walk its descendant directories;
3. treat every directory that matches the bundle-root rule as a candidate.

A directory is a candidate bundle root if it contains either:

- `index.md`, or
- at least one non-reserved `.md` file with parseable OKF frontmatter.

This lets discovery distinguish between:

- the current directory being the bundle root; and
- the current directory containing a nested bundle root inside one of its folders.

If more than one candidate exists, fail deterministically and print each candidate with a reference command, for example:

```text
More than one OKF bundle found. Provide the path explicitly:
- artifacts/ -> tooling okf tree artifacts --depth 2 --summary
- tooling/bundles/ -> tooling okf tree tooling/bundles --depth 2 --summary
```

Use a stable error code for this condition, such as `OKF_DISCOVERY_AMBIGUOUS`.

## Show Resolution

`show` should resolve targets in this order:

1. exact `concept_id` match;
2. bundle-relative path with `.md` normalized;
3. bundle-relative file path.

If a target still cannot be resolved, return a single not-found error for that target rather than falling back to a different interpretation.

## Normalization

Normalize all bundle-relative paths with `/` separators, derive `concept_id` from the relative file path without `.md`, and use the normalized identity everywhere the CLI renders or compares concepts.
