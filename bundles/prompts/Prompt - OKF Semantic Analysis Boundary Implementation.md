---
type: Prompt
title: Prompt - OKF Semantic Analysis Boundary Implementation
description: Prompt for implementing the shared semantic-normalization boundary used by links, backlinks, and health scanning while preserving raw show output.
tags:
  - tooling
  - okf
  - prompt
  - implementation
  - semantic-analysis
---

# Prompt - OKF Semantic Analysis Boundary Implementation

## Objective

Use this prompt to instruct the `ponytail` skill to implement the semantic-analysis boundary change in code.

## Prompt

You are implementing a narrow OKF behavior change in the `tooling` repository.

Use the `ponytail` skill and keep the change minimal.

Primary rule:

- Create one shared, read-only normalization boundary for semantic scanning of `Concept.body`.
- That boundary must strip fenced code blocks and inline code spans before any semantic scanner inspects the text.
- `links`, `backlinks`, and `health` must read semantic text through that shared boundary.
- `show` must stay raw presentation and must continue rendering `Concept.body` exactly as stored, without passing through semantic normalization.

Implementation targets:

- `src/tooling/okf/links.py`
- `src/tooling/okf/health.py`
- `src/tooling/okf/show.py`
- a small shared helper module under `src/tooling/okf/` if needed for the normalization boundary
- `tests/test_links.py`
- `tests/test_health.py`
- `tests/test_show.py`

Implementation requirements:

- Factor semantic-text normalization into a shared helper instead of duplicating stripping logic.
- Reuse the helper everywhere semantic scans inspect concept bodies for links, backlinks, headings, or health signals.
- Keep `show` bound to the raw `Concept.body` payload.
- Do not change the external command contracts, JSON shape, or raw display formatting except where the semantic boundary requires it.
- Add or update tests so inline code spans and fenced code blocks are ignored by semantic scans.
- Add or update tests so raw `show` output still includes the original body text unchanged.

Expected test coverage:

- A link inside inline code or a fenced code block is ignored by `links` and `backlinks`.
- A heading or link inside inline code or a fenced code block is ignored by `health`.
- `show` still prints the original body content, including code spans and fenced blocks, unchanged.

Keep the edit focused on code and tests. Do not redesign the OKF module, command flow, or documentation boundaries.

## Relations

- [Prompt - Tooling Architecture Definition](./Prompt%20-%20Tooling%20Architecture%20Definition.md)
- [Feature - OKF Links](../features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](../features/Feature%20-%20OKF%20Backlinks.md)
- [Feature - OKF Health](../features/Feature%20-%20OKF%20Health.md)
- [Feature - OKF Show](../features/Feature%20-%20OKF%20Show.md)
- [PRD - OKF Semantic Analysis Boundary](../prds/PRD%20-%20OKF%20Semantic%20Analysis%20Boundary.md)
- [Architecture - Semantic Analysis Boundary](../architecture/Semantic%20Analysis%20Boundary.md)
