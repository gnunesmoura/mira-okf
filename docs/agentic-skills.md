---
type: Guide
title: Agentic OKF Skill Integration
description: Public guidance for using mira-okf as a read-only knowledge layer in focused OKF skill workflows.
tags: [agents, okf, skills, mira-okf]
---

# Agentic OKF skill integration

mira-okf provides a local, read-only knowledge layer for agents and other
automation. It does not ship agent skills, but its stable commands can support
a small family of focused OKF workflows.

The candidate skills below are intentionally separate. Finding context,
answering a question, and updating a concept have different success criteria
and safety boundaries.

## okf-context: find reliable concept context

Use the bundle root index and the nearest relevant indexes to establish scope,
then narrow the read path with the existing commands:

    mira-okf tree <bundle> --depth 2 --profile brief --json
    mira-okf list <bundle> --profile normal --json
    mira-okf show <bundle> <concept-id-or-path> --profile full --json

Use links, backlinks, and props only when the question requires relationships
or selected metadata. The skill should identify the canonical concept, read the
smallest sufficient context, and report the paths it consulted. It should not
scan the whole bundle by default.

## okf-answer: answer bounded bundle questions

This skill uses the context found by okf-context to answer an objective
question from local evidence. It should:

- distinguish canonical facts from inference, dated observations, and scoped
  recommendations;
- cite the relevant concept paths;
- preserve uncertainty when the bundle does not establish a unique answer; and
- ask one focused clarification question when the evidence is insufficient.

This workflow does not require a new CLI command. The existing JSON contracts
provide the structured evidence needed by a host agent.

## okf-update: update a concept and its related references

This skill updates an existing canonical concept and the related bundle
surfaces needed to keep the knowledge coherent. Before proposing or applying
an update, inspect the target and its impact:

    mira-okf show <bundle> <concept-id-or-path> --profile full --json
    mira-okf links <bundle> --broken --external --json
    mira-okf backlinks <bundle> <concept-id-or-path> --json
    mira-okf validate <bundle> --json

Depending on the requested change, a complete update may include the concept
body or frontmatter, affected links and references, parent indexes, metadata,
provenance, uncertainty, history, and post-update validation.

The initial public integration remains read-only at the product layer:
mira-okf exposes the read and validation primitives, while a host skill may
perform an explicitly authorized update. Any writer needs a clear scope,
confirmation, deterministic diff, recovery behavior, and a concise report of
every affected concept. It must not create a duplicate concept or modify
unrelated content.

## Shared expectations

All three workflows should:

- prefer the public mira-okf read layer for bundle discovery, parsing, target
  resolution, and link diagnostics;
- preserve concept identity, provenance, scope, and uncertainty;
- use explicit bundle paths when discovery could be ambiguous; and
- leave the bundle unchanged unless an explicitly authorized update is in
  progress.

These skill names are provisional. They describe distinct user journeys and
may eventually be packaged as separate skills or as one shared navigation core
with specialized answer and update layers.

## Evaluation direction

Evaluate each workflow against an unassisted baseline using the same bundle,
prompt, model, tools, and workspace policy.

- Context retrieval: canonical-target accuracy, required-context recall, and
  unrelated-read overhead.
- Question answering: answer accuracy, evidence grounding, scope
  preservation, and clarification quality.
- Concept update: canonical-target accuracy, affected-reference recall,
  update completeness, diff correctness, preserved labels and anchors, index
  and metadata coherence, post-update validation, and refusal to write when
  authority or scope is ambiguous.

Token count and elapsed time can be reported descriptively. A short answer or
small read set is not a success if it is unsupported.
