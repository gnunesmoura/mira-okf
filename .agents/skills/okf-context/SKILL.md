---
name: okf-context
description: >
  Discover the canonical OKF concept and smallest sufficient read-only context
  for a bounded task. Use for concept navigation, context discovery, source
  tracing, and ambiguity mapping; do not use for answering a question or
  editing a bundle.
---

# OKF Context

Build a bounded, traceable context view for another operation. This skill is
read-only and never creates, edits, renames, or deletes bundle files.

## Workflow

1. Identify the OKF bundle root and start there. Read its `index.md`, then the
   nearest relevant parent or directory indexes before reading supporting
   concepts.
2. Establish one canonical target for the bounded task. Use only the
   documented read-only `mira-okf` CLI surface from the repository root:
   `tree`, `list`, `show`, `links`, `validate`, and `health`, with documented
   options such as `--json`, `--depth`, `--summary`, `--broken`, and
   `--profile quick`.
3. Read only the target, required context, and ambiguity-justified supporting
   evidence. Keep paths bundle-relative in the result and record every source
   consulted.
4. Load [`context-envelope.md`](references/context-envelope.md) when the
   context output needs its detailed fields or status meanings.
5. Report `canonical_target`, `required_context`, `supporting_evidence`,
   `unavailable_context`, `uncertainty`, and `sources_consulted`, with a
   `sufficient`, `insufficient`, or `ambiguous` status.

## Boundaries

- Do not infer missing facts, resolve conflicting sources silently, or treat
  discovery or filesystem writability as permission.
- If the `mira-okf` CLI is unavailable, request its installation. Do not invent
  a fallback command, parser, or mutation path.
- Keep the result limited to the requested bundle and task. Report unavailable
  or contradictory context instead of broadening inspection indefinitely.
