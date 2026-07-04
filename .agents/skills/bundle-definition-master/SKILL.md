---
name: bundle-definition-master
description: Orchestrate bundle-definition work for OKF bundles. Use this skill whenever the user asks to shape, define, plan, or prepare a bundle, especially when the work needs features, architecture decisions, and PRDs coordinated into an implementation-ready bundle.
---

# Bundle Definition Master

Use this skill to coordinate bundle shaping before implementation.

## Workflow

When shaping a bundle, use these role skills in order:

1. `tech-pm` to define user-facing behavior as `Feature` OKF documents.
2. `architect` to capture structural and technical choices as `ArchitectureDecision` OKF documents.
3. `tech-lead` to write implementation-directing `PRD` OKF documents.

Keep the sequence unless the user explicitly asks for one role only.

## Operating Rules

- Read the existing bundle `index.md`, `log.md`, and nearby relevant concepts before writing.
- Preserve OKF frontmatter and existing naming conventions.
- Keep each document narrow: one feature, one decision, or one PRD per file.
- Link related Features, ArchitectureDecisions, and PRDs in `## Relations`.
- Update only the files needed for the requested bundle-definition work.

## Handoff Checks

- After Tech PM: each feature has objective, scope, acceptance criteria, and relations.
- After Architect: each decision states context, decision, consequences, and relations.
- After Tech Lead: each PRD gives implementation scope, requirements, acceptance criteria, minimum tests, and relations.
