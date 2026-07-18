---
type: Command
title: tree
description: Summarize an OKF bundle tree.
tags: [command, tree]
---

# `tree`

```text
mira-okf tree docs --depth <n> [--summary] [--json]
```

`--depth` defaults to `2`. Human-readable output is a compact, depth-respecting
directory tree by default. With `--summary`, the same compact tree also shows
applicable `index.md` and `log.md` presence, `concepts: N`, and `reserved: N`
metadata for each directory. JSON output always includes the complete
structured directory data, regardless of `--summary`; the flag does not reduce
or reshape the JSON payload. Bundle discovery and the command's read-only
scope are unchanged.
