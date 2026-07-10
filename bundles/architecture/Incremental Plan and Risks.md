---
type: ArchitectureGuidance
title: Incremental Plan and Risks
description: Gives the implementation order for the MVP and the main risks to watch.
tags:
  - tooling
  - okf
  - delivery
---

# Incremental Plan and Risks

## Purpose

This guidance sets the smallest implementation sequence for the architecture and identifies risks that can undermine shared contracts or deterministic behavior.

## Operating Rules

Follow the sequence below so shared identity, read-model, and issue behavior are established before relationship commands and presentation layers depend on them.

### Plan

1. Freeze the shared read model and resolver contracts first: bundle discovery, concept identity normalization, issue handling, and `show` target precedence.
2. Implement permissive parsing and bundle inventory so the library can read concepts once and reuse the same model across commands.
3. Add outbound link extraction as a read-only projection over the inventory, including Markdown links, wikilinks, and deterministic link classification.
4. Build backlinks as a reverse projection over the same link data, so inbound traversal does not re-parse body text or invent a separate resolution path.
5. Keep `show` as a thin consumer of the shared resolver and concept model, so future implementation does not depend on the link graph.
6. Add stable JSON rendering, human output formatting, and deterministic sorting for the new relationship commands.
7. Add regression tests around discovery ambiguity, malformed frontmatter, resolution precedence, link classification, backlink reversal, and ordering.

## Risks

- YAML parsing can become brittle if the parser grows beyond simple frontmatter extraction.
- Concept resolution can become ambiguous if path and concept ID precedence is not fixed early.
- JSON stability can drift if each command builds its own payload.
- Discovery can become too broad if candidate matching is not tightly scoped.
- Link extraction is easy to overbuild, so it should stay as a small projection over the existing inventory.
- Backlinks can drift from outbound links if they do not share the same normalized link records.
- `show` can become coupled to link traversal if its target-resolution contract is not kept separate from relationship commands.

## Boundaries

The plan covers read-only local bundle behavior and its tests. It does not introduce write, repair, network, database, or external-service behavior, and it does not make future commands available before their contracts are implemented.

## Relations

- [Feature - OKF Links](../product/features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](../product/features/Feature%20-%20OKF%20Backlinks.md)
- [Discovery and Resolution](Discovery%20and%20Resolution.md)
- [Command Flows](Command%20Flows.md)
- [Data Contracts](Data%20Contracts.md)
- [Output and Errors](Output%20and%20Errors.md)
- [Test Strategy](Test%20Strategy.md)
