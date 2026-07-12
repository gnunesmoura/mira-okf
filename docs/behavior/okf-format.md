---
type: Reference
title: OKF format
description: Curated reference for the readable OKF 0.1 structure.
tags: [reference, okf, format]
---

# OKF format

An OKF bundle is a directory containing UTF-8 Markdown. Concept files have a
YAML frontmatter block beginning and ending with `---` and a non-empty `type`.
`index.md` is a navigation file without frontmatter; `log.md` is an optional
date-grouped history file. Concepts may use relative or bundle-root links.

Consumers must tolerate optional fields, unknown fields, unknown type values,
missing indexes, and broken links. See [validation](../commands/validate.md)
for the observable checks.
