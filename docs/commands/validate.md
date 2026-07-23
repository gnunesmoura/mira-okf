---
type: Command
title: validate
description: Report OKF bundle conformance.
tags: [command, validation, okf]
---

# `validate`

```text
mira-okf validate docs [--json]
```

Validation checks parseable frontmatter, required `type` fields, and reserved
`index.md`/`log.md` structure. Content issues are reported in the result.

## Lint integration

When `pymarkdownlnt` is installed (the `lint` extra), JSON output includes
`data.lint` with lint findings for the bundle.
