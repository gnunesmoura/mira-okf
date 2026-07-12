---
type: Command
title: list
description: List concepts in an OKF bundle.
tags: [command, list]
---

# `list`

```text
mira-okf okf list docs [--type <type>] [--tag <tag>]
  [--offset <n>] [--limit <n>] [--json]
```

Results are sorted deterministically. `--type` and `--tag` apply together;
`--offset` and `--limit` window the result using non-negative integers.
