---
type: Behavior
title: Semantic analysis
description: Define how semantic scanners treat Markdown code regions.
tags: [behavior, links, analysis]
---

# Semantic analysis

Link and health analysis uses Markdown semantics rather than raw text. Links,
headings, and similar markers inside fenced code blocks or inline code are not
treated as document content. The `show` command preserves the concept's raw
content instead of applying this scanner normalization.
