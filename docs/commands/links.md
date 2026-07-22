---
type: Command
title: links
description: List outbound links from an OKF bundle.
tags: [command, links]
---

# `links`

```text
mira-okf links docs [--broken] [--external] [--json]
```

By default links are listed with their classification. `--broken` filters to
unresolved internal links and `--external` includes external targets.

## Link resolution

Links beginning with `/` are resolved from the selected bundle root (e.g.
`/concepts/networking` targets `concepts/networking.md` under the bundle root).
Ordinary relative links (`./prefix`, `../sibling`, or bare names) are resolved
from the source document's directory.

```text
# Root-relative — resolved from bundle root
mira-okf links docs --broken
# Output shows concepts/networking.md  ->  concepts/networking.md

# Source-relative — resolved from document directory
mira-okf links docs
# Output shows getting-started.md  ->  docs/getting-started.md
```

Resolution is read-only. Missing or unresolvable targets produce non-fatal
warnings in the output.
