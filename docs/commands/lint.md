---
type: Command
title: lint
description: Lint markdown formatting in an OKF bundle.
tags: [command, lint]
---

# `lint`

```text
mira-okf lint docs [--json]
```

Lint checks markdown formatting rules on all `.md` files in the bundle. It uses
`pymarkdownlnt` under the hood and applies standard Markdown linting rules.

## Configuration

Lint looks for a config file in order of precedence:

1. `.markdownlint.json` (highest priority)
2. `.markdownlint.yaml`
3. `.markdownlint.yml`

The `ignores` array in the bundle config is applied for lint-scoped file
exclusion.

When no config file is found, lint uses the OKF default profile which permits
linting to proceed with sensible defaults.

## Dependencies

`pymarkdownlnt` is an optional dependency. It belongs to the `lint` extra. When
not installed, lint reports an error and skips execution — no findings are
produced.

## JSON output

```json
{
  "data": {
    "findings": [],
    "count": 0,
    "by_file": {},
    "config": {}
  }
}
```

`findings` is a flat list of individual lint results. `count` is the total
number of findings. `by_file` groups findings by file path. `config` records
the resolved configuration used.
