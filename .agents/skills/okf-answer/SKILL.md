---
name: okf-answer
description: >
  Answer a bounded OKF question from established local evidence with
  provenance and explicit uncertainty. Use for evidence-grounded answers and
  clarification; do not use for canonical-context discovery or bundle updates.
---

# OKF Answer

Produce a bounded answer from an established context view. This skill is
read-only and never creates, edits, renames, or deletes bundle files.

## Workflow

1. Consume the established canonical target, scope, required context, and
   sources. Do not restart discovery or answer beyond that context.
2. Answer only what the evidence establishes. Preserve concept identity,
   scope, provenance, and source paths; label each claim as `fact` or
   `inference` and do not turn inference into authority.
3. State evidence limits, conflicts, and uncertainty plainly. If a unique
   answer is not established, return `insufficient_evidence` or `ambiguous`
   rather than guessing and ask at most one focused clarification question.
4. Load [`answer-envelope.md`](references/answer-envelope.md) when the answer
   needs its detailed fields, status meanings, or fact-versus-inference rule.
5. If additional inspection is necessary, use only the documented read-only
   `mira-okf` CLI surface from the repository root: `tree`, `list`, `show`,
   `links`, `validate`, and `health`. Keep any extra read within the existing
   scope and report its source.

## Output and boundaries

Report the bounded answer, canonical concept, evidence, uncertainty,
clarification question, and sources consulted. Use `answered` only when the
context supports the answer. If the CLI is unavailable, request its
installation; do not invent a fallback command or parser.

Never write bundle files, widen the question, conceal missing evidence, or
claim that a source establishes more than it does.
