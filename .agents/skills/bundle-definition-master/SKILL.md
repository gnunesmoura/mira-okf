---
name: bundle-definition-master
description: Orchestrate bundle-definition work for OKF bundles by launching fresh subagents for tech-pm, architect, and tech-lead. Use this skill whenever the user asks to shape, define, plan, or prepare a bundle, especially when the work needs features, architecture decisions, and PRDs coordinated into an implementation-ready bundle.
---

# Bundle Definition Master

Use this skill to coordinate bundle shaping before implementation.

## Workflow

When shaping a bundle, do not read the role skills into one shared context. Instead, launch fresh subagents for each role and give each one only the question and the minimum context it needs.

Use these role skills in order:

1. `tech-pm` to define user-facing behavior as `Feature` OKF documents.
2. `architect` to capture structural and technical choices as `ArchitectureDecision` OKF documents.
3. `tech-lead` to write implementation-directing `PRD` OKF documents.

Keep the sequence unless the user explicitly asks for one role only.

### Subagent execution model

For each role:

- Start a fresh subagent with no prior bundle conversation unless the prior output is strictly needed as handoff input.
- Pass only the specific role question, the relevant bundle files, and the immediately relevant outputs from earlier roles.
- Pass prior artifacts, not your interpretation of them, when one role depends on another.
- Do not paste the entire chat history or unrelated bundle context into every agent.
- Keep each agent's context separate so the role can reason without anchoring on other roles' assumptions.

Recommended handoff shape:

1. `tech-pm` agent receives the bundle intent, relevant bundle `index.md`/`log.md`, nearby concepts, and any user constraints.
2. `architect` agent receives the approved feature set plus the relevant bundle context and any technical constraints already surfaced.
3. `tech-lead` agent receives the feature set, architecture decisions, and the implementation constraints needed to write the PRDs.

If the bundle has multiple credible shapes and the choice matters, convene `council` first, then feed the council verdict into the role agents as a separate input.

## Operating Rules

- Read the existing bundle `index.md`, `log.md`, and nearby relevant concepts before writing.
- When delegating to subagents, read those files once yourself, then hand each agent a compact context package instead of re-reading everything in every role.
- If the bundle already has related Features, ArchitectureDecisions, or PRDs, include only the directly relevant ones in the handoff.
- Preserve OKF frontmatter and existing naming conventions.
- Keep each document narrow: one feature, one decision, or one PRD per file.
- Link related Features, ArchitectureDecisions, and PRDs in `## Relations`.
- Update only the files needed for the requested bundle-definition work.

## Handoff Checks

- After Tech PM: each feature has objective, scope, acceptance criteria, and relations.
- After Architect: each decision states context, decision, consequences, and relations.
- After Tech Lead: each PRD gives implementation scope, requirements, acceptance criteria, minimum tests, and relations.
