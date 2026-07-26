# Answer envelope

`okf-answer` returns an evidence-grounded answer bounded by the established
context. It never creates, edits, renames, or deletes bundle files.

```yaml
answer_status: answered | insufficient_evidence | ambiguous
answer: <bounded answer or explicit evidence limit>
canonical_concept: <bundle-relative path or identifier or null>
evidence:
  - path: <bundle-relative path>
    claim: <observed claim>
    relation: fact | inference
uncertainty:
  - <bounded uncertainty, conflict, or evidence limit>
clarification_question: <one focused question or null>
sources_consulted:
  - <path or source identifier>
```

State facts as facts only when the cited context establishes them. Label
synthesis or interpretation as `inference`; do not turn it into provenance or
authority. Keep the answer within the canonical concept, requested scope,
and available evidence.

Use `insufficient_evidence` when the context cannot support an answer and
`ambiguous` when more than one answer remains established. In either case,
state what is missing or conflicting and ask at most one focused clarification
question. Use `null` when no question would resolve the limit. Do not conceal
evidence insufficiency behind a confident answer.
