# Architecture Log

## 2026-07-09

- **Creation**: Added the [Semantic Analysis Boundary](Semantic%20Analysis%20Boundary.md) decision for the shared raw-body normalization boundary used by semantic scanners and kept separate from `show`.

## 2026-07-06

- **Creation**: Added the [Health Report Contract](Health%20Report%20Contract.md) decision for `health` payload shape, local quality signals, and non-fatal soft signal semantics.

## 2026-07-05

- **Update**: Expanded the [Validation Report Contract](Validation%20Report%20Contract.md) with reserved `index.md` and `log.md` conformance rules from the local OKF specification.
- **Creation**: Added the [Validation Report Contract](Validation%20Report%20Contract.md) decision for `validate` summary payload, issue ordering, and process failure semantics.

## 2026-07-04

- **Update**: Audited the architecture bundle against the OKF spec and confirmed the link-contract references stay aligned with the feature docs.
- **Creation**: Added the [Links Command Contract](Links%20Command%20Contract.md) decision for outbound link extraction, classification, and output.
- **Creation**: Added the [List Command Contract](List%20Command%20Contract.md) decision for concept-only inventory, deterministic filtering, and ordering.
- **Creation**: Added the initial architecture bundle for `tooling` with decisions, boundaries, contracts, command flows, test strategy, and implementation notes.
