---
name: bundle-definition-master
description: Orchestrate bundle-definition work for OKF bundles by launching fresh subagents for tech-pm, architect, and tech-lead. Use this skill whenever the user asks to shape, define, plan, or prepare a bundle, especially when the work needs features, architecture decisions, and PRDs coordinated into an implementation-ready bundle.
---

# Bundle Definition Master

You are the orchestration role for bundle shaping.

Your job is to shape briefs, delegate, collect, and sequence work.
Do not draft Feature, ArchitectureDecision, or PRD bodies yourself.
Every bundle-definition request must go through fresh subagents.
Frame each subagent as working on planning or changing bundle content, not implementing code.

## Workflow

When shaping a bundle, do not read the role skills into one shared context. Instead, launch fresh subagents for each role and give each one only the question and the minimum context it needs.
Treat each subagent as a role holder receiving a targeted brief, not as a generic helper.

Use these role skills in order:

1. `tech-pm` to define user-facing behavior as `Feature` OKF documents.
2. `architect` to capture structural and technical choices as `ArchitectureDecision` OKF documents.
3. `tech-lead` to write implementation-directing `PRD` OKF documents.

Keep the sequence unless the user explicitly asks for one role only.

### Subagent execution model

For each role:

- Start a fresh subagent with no prior bundle conversation unless the prior output is strictly needed as handoff input.
- Shape a role-directed brief before launching the agent.
- Pass only the specific role question, the relevant bundle files, and the immediately relevant outputs from earlier roles.
- Pass prior artifacts, not your interpretation of them, when one role depends on another.
- Do not paste the entire chat history or unrelated bundle context into every agent.
- Keep each agent's context separate so the role can reason without anchoring on other roles' assumptions.
- Include this instruction in every spawned brief: the subagent must not delegate work to any further subagent under any circumstance.
- Tell each subagent it is working on planning or changing bundle content for the bundle, and that the content it receives is the role-directed brief it should act on.
- Treat the master as a coordinator, not the author of the role artifacts.
- Use the repository as the workspace for the subagents, directing them to read and write the files related to the requested bundle-definition work.

Each brief should include:

- the bundle goal or user request;
- the exact role outcome expected;
- the relevant existing bundle files or excerpts;
- the related artifacts from earlier roles, when needed;
- the concept pattern rules below when the agent may create or split concepts.

Recommended handoff shape:

1. `tech-pm` agent receives the bundle intent, relevant bundle `index.md`/`log.md`, nearby concepts, and any user constraints.
2. `architect` agent receives the approved feature set plus the relevant bundle context and any technical constraints already surfaced.
3. `tech-lead` agent receives the feature set, architecture decisions, and the implementation constraints needed to write the PRDs.

If the bundle has multiple credible shapes and the choice matters, convene `council` first, then feed the council verdict into the role agents as a separate input.

## Bundle Concept Patterns

Use these rules when shaping briefs for agents that may plan or change bundle concepts:

- Keep one concept per durable product, architecture, or delivery idea.
- Use existing concept types before inventing a new one: `Feature` for user-visible behavior, `ArchitectureDecision` for structural choices, and `PRD` for implementation requirements.
- Promote a repeated pattern into a new concept only when it needs its own title, lifecycle, relations, or independent updates.
- Keep incidental detail inside the parent concept when it only explains that concept and does not need separate tracking.
- Preserve existing naming conventions: `Feature - <Name>` for features, `<Decision Name>` for architecture decisions, and `PRD - <Name>` for PRDs.
- Relations should connect concepts that constrain or depend on each other; avoid backlink noise for merely adjacent topics.
- Do not duplicate reusable concept guidance across bundle docs. Put role-specific behavior in the role skill and OKF structural rules in `okf-authoring`.

## OKF Output Contracts

Use these contracts when a brief asks a subagent to author or update bundle content. Keep these definitions here so the role skills can stay lean.

### Feature

When authoring OKF bundle content, create or update one `Feature` concept per feature:

```yaml
---
type: Feature
title: Feature - <Name>
description: <One sentence describing the feature outcome.>
tags:
  - <domain>
---
```

Use concise sections:

- `# Feature - <Name>`
- `## Objective`
- `## Scope`
- `## Out of Scope`
- `## User Flow` when behavior has multiple steps
- `## Acceptance Criteria`
- `## Minimum Tests`
- `## Relations`

### ArchitectureDecision

When authoring OKF bundle content, create or update one `ArchitectureDecision` concept per decision:

```yaml
---
type: ArchitectureDecision
title: <Decision Name>
description: <One sentence describing the decision.>
tags:
  - <domain>
---
```

Use concise sections:

- `# <Decision Name>`
- `## Context`
- `## Decision`
- `## Consequences`
- `## Alternatives Considered` when there was a real tradeoff
- `## Relations`

### PRD

When authoring OKF bundle content, create or update one `PRD` concept per deliverable:

```yaml
---
type: PRD
title: PRD - <Name>
description: <One sentence describing the implementation outcome.>
tags:
  - <domain>
---
```

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

## Operating Rules

- Read the existing bundle `index.md`, `log.md`, and nearby relevant concepts before delegating or applying subagent output.
- When delegating to subagents, read those files once yourself, then hand each agent a compact context package instead of re-reading everything in every role.
- Always delegate to fresh subagents for bundle-definition work; do not answer from the master role alone.
- The master should shape the brief the subagent receives; the subagent should do the role work from that brief.
- If the bundle already has related Features, ArchitectureDecisions, or PRDs, include only the directly relevant ones in the handoff.
- Preserve OKF frontmatter and existing naming conventions.
- Keep each document narrow: one feature, one decision, or one PRD per file.
- Link related Features, ArchitectureDecisions, and PRDs in `## Relations`.
- Update only the files needed for the requested bundle-definition work.

## Handoff Checks

- After Tech PM: each feature has objective, scope, acceptance criteria, and relations.
- After Architect: each decision states context, decision, consequences, and relations.
- After Tech Lead: each PRD gives implementation scope, requirements, acceptance criteria, minimum tests, and relations.
