---
name: tech-lead
description: Write implementation-directing PRD OKF documents. Use this skill when the user asks for a PRD, implementation plan, delivery requirements, engineering scope, test plan, rollout plan, or developer-ready bundle definition.
---

# Tech Lead

Use this skill to turn shaped product and architecture context into `PRD` OKF documents that direct implementation. Use it after features and architecture decisions are established, or when a bundle needs implementation direction.

## Output

Create or update one PRD document per deliverable:

```yaml
---
type: PRD
title: PRD - <Name>
description: <One sentence describing the implementation outcome.>
tags:
  - <domain>
---
```

## PRD Structure

Use concise sections:

- `# PRD - <Name>`
- `## Context`
- `## Objective`
- `## Scope`
- `## Requirements`
- `## Acceptance Criteria`
- `## Minimum Tests`
- `## Non-Goals`
- `## Relations`

## Rules

- Translate features and architecture decisions into implementation requirements.
- Update relations off the PRD to the features, architecture decisions, and other PRDs it constrains.
- Keep requirements concrete enough for a developer or agent to execute.
- Name files, commands, contracts, and expected outputs when known.
- Include the narrowest useful test plan.
- Do not restate every feature or decision; link them and summarize only what implementation needs.
- If feature scope or technical direction is still missing, call out the blocker instead of inventing requirements.
