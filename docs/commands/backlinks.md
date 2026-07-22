---
type: Command
title: backlinks
description: List inbound links for an OKF concept.
tags: [command, backlinks]
---

# `backlinks`

```text
mira-okf backlinks docs <concept-id-or-path> [--json]
```

The result lists concepts whose links resolve to the selected concept.

## Resolution semantics

Backlinks use the same link resolution as the `links` command. Links beginning
with `/` are resolved from the bundle root; ordinary relative links are resolved
from the source document's directory. Resolution is read-only and missing
targets produce non-fatal warnings.
