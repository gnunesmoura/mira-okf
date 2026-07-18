---
type: Command
title: show
description: Read one OKF concept.
tags: [command, show]
---

# `show`

```text
mira-okf show docs <concept-id-or-path> [--summary] [--json]
```

Resolve a concept by id or bundle-relative Markdown path. In human-readable
output, `--summary` presents the same resolved concept compactly: it retains
the path-first identity and available metadata, including description and
tags, while omitting the body. Without it, the concept content is shown. Any
tolerated issues remain visible in the existing `Issues` section at the end.
JSON output always includes the complete concept payload, regardless of
`--summary`; the flag does not reduce or reshape the JSON payload. Bundle
discovery, target resolution, and the command's read-only scope are unchanged.
