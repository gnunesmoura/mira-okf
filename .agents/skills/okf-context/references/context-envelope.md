# Context envelope

`okf-context` returns the smallest traceable, read-only context view for a
bounded task. It never creates, edits, renames, or deletes bundle files.

```yaml
context_status: sufficient | insufficient | ambiguous
canonical_target: <bundle-relative path or identifier or null>
required_context:
  - path: <bundle-relative path>
    role: <why it is required>
supporting_evidence:
  - path: <bundle-relative path>
    claim: <supported claim>
unavailable_context:
  - path: <path or description>
    reason: <why it could not be established>
uncertainty:
  - <bounded uncertainty or conflict>
sources_consulted:
  - <path or source identifier>
```

## Status meanings

- `sufficient`: one canonical target and the required context are established;
  supporting evidence and sources are reported.
- `insufficient`: required context or evidence is unavailable, so the task
  cannot be safely bounded.
- `ambiguous`: multiple targets, interpretations, or conflicting sources
  remain; preserve the alternatives and explain the uncertainty.

Start at the bundle root and nearest indexes, then read only supporting paths
needed to resolve the bounded task. Report unavailable or contradictory
context rather than filling gaps from inference. Filesystem writability,
discovery, or this envelope never grants permission to write.
