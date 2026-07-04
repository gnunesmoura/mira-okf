---
name: architect
description: Define technical direction as ArchitectureDecision OKF documents. Use this skill when the user asks for architecture, system boundaries, data contracts, integration choices, tradeoffs, module design, or technical decisions for a bundle.
---

# Architect

Use this skill to capture decisions that constrain implementation.

## Output

Create or update one decision document per decision:

```yaml
---
type: ArchitectureDecision
title: <Decision Name>
description: <One sentence describing the decision.>
tags:
  - <domain>
---
```

## Decision Structure

Use concise sections:

- `# <Decision Name>`
- `## Context`
- `## Decision`
- `## Consequences`
- `## Alternatives Considered` when there was a real tradeoff
- `## Relations`

## Rules

- State the chosen design clearly enough that implementation can proceed.
- Prefer existing repo patterns and stdlib-first approaches.
- Keep boundaries explicit: domain, adapters, filesystem, serialization, and CLI should not blur.
- Record consequences honestly, including limitations.
- Do not write implementation tasks; leave delivery direction to `tech-lead`.
