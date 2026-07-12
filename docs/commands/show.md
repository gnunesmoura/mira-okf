---
type: Command
title: show
description: Read one OKF concept.
tags: [command, show]
---

# `show`

```text
mira-okf okf show docs <concept-id-or-path> [--summary] [--json]
```

Resolve a concept by id or bundle-relative Markdown path. `--summary` requests
the compact representation; without it, the concept content is shown.
