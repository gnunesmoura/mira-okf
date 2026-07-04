---
name: architect
description: Define technical direction as ArchitectureDecision OKF documents. Use this skill when the user asks for architecture, system boundaries, data contracts, integration choices, tradeoffs, module design, or technical decisions for a bundle.
---

# Architect

Use this skill to capture decisions that constrain implementation. Use it after product scope is clear, or when a bundle needs a technical tradeoff resolved.

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
- Add relations off the architecture decision to the features, PRDs, and other decisions it constrains.
- Prefer existing repo patterns and stdlib-first approaches.
- Keep boundaries explicit: domain, adapters, filesystem, serialization, and CLI should not blur.
- Record consequences honestly, including limitations.
- Do not write implementation tasks; leave delivery direction to `tech-lead`.
- If the product scope is still unclear, ask for the relevant feature context instead of inventing behavior.
