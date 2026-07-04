# Architecture

Initial architecture decisions for the local `tooling` library and CLI.

## Documents

- [Architecture Overview](Architecture%20Overview.md) - Summary of the initial design and scope.
- [Discovery and Resolution](Discovery%20and%20Resolution.md) - Bundle discovery, ambiguity handling, and show target resolution.
- [Output and Errors](Output%20and%20Errors.md) - Stable JSON envelope, human output rules, and issue semantics.
- [OKF Boundaries](OKF%20Boundaries.md) - Domain, CLI, parsing, discovery, and serialization boundaries.
- [Data Contracts](Data%20Contracts.md) - Core contracts for bundle, concept, directory, link, and issue records.
- [Command Flows](Command%20Flows.md) - Behavior of `tree`, `list`, `show`, and future interfaces.
- [List Command Contract](List%20Command%20Contract.md) - Concept-only inventory rules, filters, and ordering for `list`.
- [List Result Windowing](List%20Result%20Windowing.md) - Windowed `list` payload shape, totals, and truncation semantics.
- [Links Command Contract](Links%20Command%20Contract.md) - Outbound link extraction, classification, and output for `links`.
- [Test Strategy](Test%20Strategy.md) - Minimum fixtures and test boundaries for the MVP.
- [Incremental Plan and Risks](Incremental%20Plan%20and%20Risks.md) - Small-step implementation order and known risks.
