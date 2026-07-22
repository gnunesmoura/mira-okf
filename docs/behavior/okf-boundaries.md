---
type: Behavior
title: OKF boundaries
description: Define the supported read-only OKF boundary.
tags: [behavior, okf]
---

# OKF boundaries

The tool supports OKF Specification 0.1 as a permissive reader. It inventories
Markdown concepts, reserved indexes and logs, frontmatter, and links. Unknown
frontmatter fields and broken links are tolerated as content signals. The tool
does not author, repair, rewrite, or publish bundle content.

## Path boundaries

A leading `/` in a link target is an OKF bundle-root marker, not a
filesystem-root marker. Resolution treats `/concepts/foo` as
`<bundle-root>/concepts/foo.md`.

Resolution precedence:

1. **Root-relative** — targets starting with `/` are resolved against the
   selected bundle root directory.
2. **Source-relative** — all other targets (including `./`, `../`, and bare
   names) are resolved from the directory containing the source document.

This resolution is independent of the caller's current working directory or
repository layout. Resolution is read-only and does not modify bundle content.
