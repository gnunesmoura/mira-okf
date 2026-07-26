---
name: okf-update
description: >
  Prepare or host-mediate a bounded proposal or apply operation for an
  existing canonical OKF concept under an explicit concise handoff. Use for
  controlled updates; do not use for context discovery or evidence-grounded
  answering.
---

# OKF Update

Handle only an explicit coordinator handoff for an existing canonical concept.
The CLI is read-only; the host is the only write boundary.

## Workflow

1. Before inspecting the bundle, validate the concise handoff: existing
   target, supported `proposal` or `apply` operation, intended outcome, exact
   allowed bundle-relative path list, constraints, and available context.
   Reject a missing or structurally invalid handoff. Filesystem writability,
   discovery, target plausibility, or generic invocation never grants
   permission.
2. Use only the documented read-only `mira-okf` CLI surface from the repository
   root: `tree`, `list`, `show`, `links`, `validate`, and `health`. Inspect only
   the handed-off target and exact paths needed to validate the bounded
   operation; never add a discovered path to the list.
3. Request a read-only consistency view from
   [`okf-context`](../okf-context/SKILL.md) only when context is absent,
   structurally invalid, or explicitly insufficient. Do not use fallback for
   ambiguous or unavailable context unless its result is a refusal or
   `non_result`; fallback never grants permission, changes the operation, or
   permits apply.
4. Load [`update-envelope.md`](references/update-envelope.md) when the handoff,
   result fields, or evidence rules need detail.
5. Keep proposal and apply separate. A proposal describes the bounded change
   without writing. For apply, the host must confirm the same handoff and
   perform any write itself; this skill and the CLI do not mutate files.
6. Honor `review_requested` only when explicitly requested. There is no
   default human-review gate. Do not create concepts; preserve unrelated
   content and existing history.
7. Report `refused`, `proposed`, `applied`, or `partial`, exact changed paths,
   remaining issues, and validation evidence. Use `partial` only when the
   host can enumerate changed paths and validate the resulting state. Missing
   required evidence is `non_result` with a reason, not an applied result.

## Non-goals

Do not widen paths or operation scope, infer authorization, or add
authorization IDs, tokens, signatures, expiry, rollback, retry, journaling,
locking, transaction, or other recovery machinery. If the `mira-okf` CLI is
unavailable, request its installation rather than inventing a fallback.
