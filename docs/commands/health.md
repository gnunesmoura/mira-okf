---
type: Command
title: health
description: Report grouped OKF bundle health signals.
tags: [command, health]
---

# `health`

```text
mira-okf health docs [--profile {quick,full}] [--json]
```

`quick` is the default profile. `full` evaluates additional connectivity,
metadata, citation, and rule signals. Health findings are diagnostics, not
automatic repairs.

## Link resolution

Link checking in health reports uses the same resolution as `mira-okf links`.
Links beginning with `/` are resolved from the bundle root; ordinary relative
links are resolved from the source document's directory. This applies to all
link checks, including `index.md` resolution in the `full` profile. Missing
targets are non-fatal findings in the health output.
