---
name: bundle-definition-master
description: Orchestrate Spec-Driven Development change packages for OKF bundles by coordinating product features, architecture context, and implementation-ready SDD artifacts.
---

# Bundle Definition Master

The master coordinates the definition of one bounded change package. The
durable output is a package under
`bundles/spec-driven-development/changes/<change-id>-<short-name>/`.

Do not create a PRD, Feature, ArchitectureDecision, or other parallel concept
as a default output. Link existing product features and architecture concepts
through `related` fields. Create or update a product feature only when the
user explicitly asks to change durable product knowledge.

## Package artifacts

Every change package contains:

- `spec.md` - approved intent, behavior, scope, non-goals, and acceptance
  criteria;
- `plan.md` - technical direction, boundaries, contracts, source areas,
  tests, risks, and decisions;
- `tasks.md` - ordered, independently verifiable implementation work;
- `acceptance-tests.md` - observable checks and required evidence;
- `agent-contract.md` - reading order, scope limits, invariants, validation,
  and closeout rules;
- `log.md` - chronological package history, without frontmatter.

Use the reusable templates in
`bundles/spec-driven-development/templates/`. Read the process guidance in
`bundles/spec-driven-development/guides/` and the normative rules in
`bundles/spec-driven-development/policies/`. Preserve the package layout,
frontmatter, relations, and lifecycle defined by
`bundles/spec-driven-development/changes/index.md`.

## Workflow

Read the bundle indexes, the relevant product features, architecture concepts,
references, and any existing change package before delegating work.

Use fresh role agents in this order:

1. `tech-pm` authors or updates `spec.md`.
2. `architect` authors or updates `plan.md`.
3. `tech-lead` authors or updates `tasks.md`, `acceptance-tests.md`, and
   `agent-contract.md`.

Keep the sequence unless the user explicitly requests one role only. Agents
must receive only the relevant context and must not delegate further work.

The master owns package creation, cross-artifact consistency, index updates,
and status gates. Role agents own the contents of their assigned artifacts.
Do not have multiple agents author the same artifact concurrently.

## Role briefs

### Tech PM

Define the durable user problem and the bounded change behavior. Produce a
`spec.md` with intent, context, problem statement, desired outcome, scope,
non-goals, actors, user stories, functional requirements, domain rules, open
questions, acceptance criteria, and relations to product features and
references.

### Architect

Translate the approved specification into a `plan.md`. Define technical
boundaries, affected components, contracts, data or CLI behavior, test
strategy, validation commands, migration and rollback, risks, trade-offs, and
relations to reusable architecture concepts.

### Tech Lead

Turn the plan into executable delivery guidance. Produce ordered tasks with
dependencies and done conditions, acceptance scenarios mapped to requirements,
and an agent contract covering reading order, allowed paths, invariants,
clarification policy, validation, and closeout evidence.

## SDD lifecycle gates

Use these statuses only with their corresponding evidence:

`draft -> specified -> planned -> ready -> in_progress -> implemented -> validated`

- `specified`: the specification has approved behavior, scope, non-goals,
  dependencies, and observable acceptance criteria;
- `planned`: the technical plan names boundaries, contracts, source areas,
  tests, risks, and decisions;
- `ready`: tasks, acceptance tests, dependencies, agent constraints, and
  completion evidence are actionable and mutually consistent;
- later statuses belong to implementation and validation agents.

Do not advance status merely because files exist. Do not mark implementation
or validation status during bundle definition.

## Consistency checks

Before declaring a package ready, verify:

- all required artifacts exist in one package directory;
- every concept artifact has valid frontmatter with non-empty `type`,
  `title`, `description`, `change_id`, and `status`;
- package relations use canonical paths beginning with
  `/spec-driven-development/changes/`;
- product, architecture, and reference relations point to existing canonical
  documents or are explicitly empty;
- requirements map to acceptance criteria and acceptance tests;
- plan boundaries map to task paths and validation commands;
- agent-contract rules agree with the plan and task list;
- unresolved questions that affect behavior, architecture, persistence,
  security, or compatibility block readiness;
- `log.md` is chronological and records only actual package events.

Reject contradictions instead of silently repairing them. Record a required
follow-up in the package or ask the user when the decision changes scope.

## Concept boundaries

- `product/features/` describes durable user-visible capabilities.
- `architecture/` describes reusable technical boundaries and contracts.
- `spec-driven-development/changes/` describes one bounded change and its
  execution evidence.
- `references/` contains governing specifications and external constraints.

Do not duplicate durable product or architecture guidance inside every change
package. Use concise context and canonical relations.

## Handoff checks

After Tech PM: `spec.md` has an approved outcome, scope, non-goals, behavior,
acceptance criteria, and relevant product relations.

After Architect: `plan.md` has explicit boundaries, contracts, affected areas,
tests, validation commands, risks, and relevant architecture relations.

After Tech Lead: tasks are ordered and verifiable; acceptance tests cover the
requirements; and the agent contract defines executable guardrails.
