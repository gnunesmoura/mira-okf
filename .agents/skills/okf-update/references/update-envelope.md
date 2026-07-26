# Update envelope

`okf-update` handles an explicit host handoff for an existing canonical
concept. The CLI remains read-only; only the host may write, and only within
the exact handoff paths.

## Handoff and result

```yaml
target_concept: <existing canonical bundle-relative path or identifier>
operation: proposal | apply
intended_outcome: <concise requested outcome>
allowed_paths:
  - <exact bundle-relative path>
constraints:
  - <scope or preservation constraint>
available_context:
  status: sufficient | insufficient | ambiguous | unavailable
  paths: [<bundle-relative paths>]
  reason: <status explanation>
review_requested: false | true
status: refused | proposed | applied | partial
changed_paths: [<exact paths, when evidenced>]
remaining_issues: [<unresolved issue or evidence limit>]
```

Reject a missing or invalid handoff before inspection. Require an existing
canonical target, supported operation, intended outcome, exact path list, and
the stated constraints and context. Never infer permission from a writable
filesystem, discovery, target plausibility, or a context result.

`proposal` inspects and describes the bounded change without writing.
`apply` is separate: the host must confirm the same handoff before it writes.
An apply cannot create a concept. Discovered impact outside `allowed_paths`
is refused; the path list is never widened. Preserve unrelated content and
existing history. Review is optional and pauses only when explicitly
requested; it is not a default gate.

## Context fallback and evidence

Only absent, structurally invalid, or explicitly insufficient context may
request a read-only consistency view from `okf-context`. Ambiguous or
unavailable fallback context is reported as a refusal; fallback never grants
permission, changes the operation, or permits apply.

Use `refused` for a bounded safety or contract refusal, `proposed` for an
evidenced proposal, `applied` only when the host can evidence the requested
write, and `partial` only when the host can enumerate changed paths and
validate the resulting state. Report exact changed paths and validation
evidence for partial outcomes. If changed-path or required validation evidence
is missing, the host must not claim `applied`; report the evidence limit to the
coordinator as an unevaluable outcome (`non_result`) with a reason.

This contract intentionally has no authorization IDs, tokens, signatures,
expiry, formal authorization service, rollback, retry, journaling, locking,
transactions, or mandatory review.
