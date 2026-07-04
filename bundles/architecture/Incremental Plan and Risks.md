---
type: ArchitectureDecision
title: Incremental Plan and Risks
description: Gives the implementation order for the MVP and the main risks to watch.
tags:
  - tooling
  - okf
  - delivery
---

# Incremental Plan and Risks

## Plan

1. Implement models, discovery, identity normalization, and the shared error envelope.
2. Implement permissive parsing and bundle inventory.
3. Wire `tree`, `list`, and `show` through the CLI.
4. Add stable JSON rendering, human output formatting, and deterministic sorting.
5. Add regression tests around ambiguity, malformed frontmatter, resolution precedence, and ordering.

## Risks

- YAML parsing can become brittle if the parser grows beyond simple frontmatter extraction.
- Concept resolution can become ambiguous if path and concept ID precedence is not fixed early.
- JSON stability can drift if each command builds its own payload.
- Discovery can become too broad if candidate matching is not tightly scoped.
- Link extraction is easy to overbuild, so it should stay out of Phase 1.
