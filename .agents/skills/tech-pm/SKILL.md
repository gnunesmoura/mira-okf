---
name: tech-pm
description: Define product features as Feature OKF documents. Use this skill when the user asks for feature definition, product shaping, acceptance criteria, scope, user behavior, or bundle feature planning.
---

# Tech PM

Use this skill to turn product intent into `Feature` OKF documents.

## Output

Create or update one feature document per feature:

```yaml
---
type: Feature
title: Feature - <Name>
description: <One sentence describing the feature outcome.>
tags:
  - <domain>
---
```

## Feature Structure

Use concise sections:

- `# Feature - <Name>`
- `## Objective`
- `## Scope`
- `## Out of Scope`
- `## User Flow` when behavior has multiple steps
- `## Acceptance Criteria`
- `## Minimum Tests`
- `## Relations`

## Rules

- Define observable behavior, not implementation internals.
- Update the relations off the feature to the PRDs, architecture decisions, and other features it constrains.
- Keep acceptance criteria testable and specific.
- Split unrelated behavior into separate Feature documents.
- Link parent PRDs, dependent features, and relevant architecture decisions.
- Do not invent architecture; leave technical tradeoffs to `architect`.
