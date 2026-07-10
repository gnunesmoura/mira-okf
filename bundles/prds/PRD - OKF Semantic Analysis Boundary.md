---
type: PRD
title: PRD - OKF Semantic Analysis Boundary
description: Implementation requirements for the shared read-only normalization boundary used by OKF semantic scanners.
tags:
  - tooling
  - okf
  - semantic
  - links
  - health
  - show
  - prd
---

# PRD - OKF Semantic Analysis Boundary

## Context

`Concept.body` is stored as raw Markdown. `tooling okf show` must keep rendering that raw content unchanged. `tooling okf links`, `tooling okf backlinks`, and `tooling okf health` need a shared semantic view so fenced code blocks and inline code spans do not produce false link or health signals.

The existing command PRDs already define the command surfaces. This PRD narrows the implementation boundary for the shared normalization step those commands must use.

## Objective

Implement one shared, read-only semantic-normalization boundary over raw concept bodies so relationship and health scanners inspect the same normalized text while presentation remains raw.

## Scope

- Accept raw `Concept.body` text from the shared OKF read model.
- Strip fenced code blocks and inline code spans before semantic scanners inspect the text.
- Provide one shared normalization path for `links`, `backlinks`, and `health`.
- Use normalized semantic text for Markdown link and wikilink detection.
- Use normalized semantic text for body-derived health signals that depend on link presence or other semantic scans.
- Keep `show` outside the semantic boundary so it continues to render raw stored content.
- Keep the boundary read-only and derived from existing bundle data.
- Avoid introducing a new persisted field or mutating stored content.

## Out of Scope

- Changing `tooling okf show` presentation rules.
- Rewriting stored concept bodies or frontmatter.
- Changing validation, discovery, or target-resolution rules.
- Adding new parsing rules beyond the shared normalization boundary.
- Treating semantic normalization as a persisted model or export format.

## Requirements

- The normalization step must operate on raw body text from the shared read model.
- The normalization step must remove fenced code blocks and inline code spans before scanners inspect the text.
- `links` and `backlinks` must run their body scans against the normalized semantic text.
- `health` must use the same normalized semantic text for its body-derived link and connectivity signals.
- `show` must continue to render the raw body text exactly as stored and must not pass through the semantic normalizer.
- The shared normalization behavior must be deterministic for the same input body.
- The shared boundary must be the only implementation of these ignore rules used by the semantic scanners.

## Acceptance Criteria

- Links and backlinks ignore Markdown links and wikilinks inside fenced code blocks and inline code spans.
- Health ignores the same fenced code block and inline code span content when deriving semantic signals.
- `show` still renders fenced code blocks and inline code spans exactly as stored in the raw concept body.
- The same concept body produces the same normalized semantic text across repeated runs.
- No new stored field is required to support the boundary.
- The boundary does not change raw content output or validation behavior.

## Minimum Tests

- Ignores outbound link candidates inside fenced code blocks.
- Ignores outbound link candidates inside inline code spans.
- Ignores inbound link candidates inside fenced code blocks.
- Ignores inbound link candidates inside inline code spans.
- Ignores health signal candidates inside fenced code blocks.
- Ignores health signal candidates inside inline code spans.
- Preserves raw body rendering for `show`.
- Produces stable normalized output for the same input body.

## Relations

- [Feature - OKF Links](../features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](../features/Feature%20-%20OKF%20Backlinks.md)
- [Feature - OKF Health](../features/Feature%20-%20OKF%20Health.md)
- [Feature - OKF Show](../features/Feature%20-%20OKF%20Show.md)
- [PRD - OKF Links](PRD%20-%20OKF%20Links.md)
- [PRD - OKF Health](PRD%20-%20OKF%20Health.md)
- [PRD - OKF Show](PRD%20-%20OKF%20Show.md)
- [PRD - OKF Module](PRD%20-%20OKF%20Module.md)
- [Semantic Analysis Boundary](../architecture/Semantic%20Analysis%20Boundary.md)
- [Links Command Contract](../architecture/Links%20Command%20Contract.md)
- [Health Report Contract](../architecture/Health%20Report%20Contract.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
