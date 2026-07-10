---
type: ArchitectureDecision
title: Semantic Analysis Boundary
description: Defines the shared normalization boundary for OKF semantic scanners while preserving raw concept content for `show`.
tags:
  - tooling
  - okf
  - links
  - health
  - show
  - architecture
---

# Semantic Analysis Boundary

## Context

`Concept.body` stores raw markdown. `show` must render that raw content unchanged. `links`, `backlinks`, and `health` need a deterministic semantic view that ignores fenced code blocks and inline code spans so examples and snippets do not create false link or health signals.

## Decision

The OKF domain should expose one shared semantic-normalization boundary over raw concept bodies.

- The boundary takes raw `Concept.body` text as input.
- It strips fenced code blocks and inline code spans before semantic scanners inspect the text.
- `links` and `backlinks` use the normalized semantic text for Markdown link and wikilink detection.
- `health` uses the same normalized semantic text for body-derived signals that depend on link presence or other semantic scans.
- The boundary is derived and read-only; it does not mutate stored content, parsed frontmatter, or issue records.
- `show` stays outside this boundary and continues to render raw concept content exactly as stored.

## Consequences

- Link and health scanners share one ignore rule instead of each owning a separate copy.
- Examples and snippets no longer leak into link graphs or health signals.
- Raw storage, semantic analysis, and presentation remain explicitly separated.
- No new persisted field is required; the boundary can be implemented as a shared projection over the existing read model.

## Alternatives Considered

Having each semantic command scan raw bodies independently was rejected because it would duplicate ignore rules and allow links, backlinks, and health to disagree.

## Relations

- [Feature - OKF Show](../product/features/Feature%20-%20OKF%20Show.md)
- [Feature - OKF Links](../product/features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](../product/features/Feature%20-%20OKF%20Backlinks.md)
- [Feature - OKF Health](../product/features/Feature%20-%20OKF%20Health.md)
- [OKF Boundaries](OKF%20Boundaries.md)
- [Data Contracts](Data%20Contracts.md)
- [Command Flows](Command%20Flows.md)
- [Links Command Contract](Links%20Command%20Contract.md)
- [Health Report Contract](Health%20Report%20Contract.md)
