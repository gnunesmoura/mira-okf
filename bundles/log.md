# Tooling - Log

## 2026-07-06

- **Creation**: Added the [PRD - OKF Health](prds/PRD%20-%20OKF%20Health.md) implementation requirements for the read-only `tooling okf health` command and stable health report signals.
- **Creation**: Added the [Health Report Contract](architecture/Health%20Report%20Contract.md) architecture decision for `tooling okf health` report shape and soft health signal semantics.
- **Creation**: Added the [Feature - OKF Health](features/Feature%20-%20OKF%20Health.md) concept for compact read-only bundle status signals after validation.

## 2026-07-05

- **Update**: Expanded `validate` planning to cover reserved `index.md` and `log.md` conformance from the local OKF specification, including the root `okf_version` exception.
- **Creation**: Added the [Feature - OKF Validation](features/Feature%20-%20OKF%20Validation.md), [Validation Report Contract](architecture/Validation%20Report%20Contract.md), and [PRD - OKF Validation](prds/PRD%20-%20OKF%20Validation.md) bundle artifacts for the next implementation target.
- **Update**: Advanced the [Tooling Roadmap](Tooling%20Roadmap.md) from completed `show` work to implementation-ready `validate` planning.
- **Creation**: Added the [Feature - OKF Show](features/Feature%20-%20OKF%20Show.md) and [PRD - OKF Show](prds/PRD%20-%20OKF%20Show.md) bundle artifacts for the canonical single-concept read path.
- **Update**: Kept `show` within the existing `Output and Errors` architecture boundary and added the end-of-output `Issues` rule for human mode.

## 2026-07-04

- **Update**: Audited the OKF bundle docs against the local spec, reconciled the `links` and `backlinks` feature guidance, and verified internal references.
- **Creation**: Added the [PRD - OKF Links](prds/PRD%20-%20OKF%20Links.md) and [Links Command Contract](architecture/Links%20Command%20Contract.md) bundle artifacts for outbound link discovery.
- **Update**: Tightened the OKF concept list definitions so invalid pagination is rejected and human list output exposes bundle-relative paths.
- **Update**: Split the OKF read model into dedicated reader and listing modules so `list` no longer depends on `tree` for shared inventory behavior.
- **Update**: Extracted shared OKF bundle resolution into a dedicated module so `tree`, `list`, and future commands reuse the same discovery and ambiguity rules.
- **Update**: Finalized the [PRD - OKF Concept List](prds/PRD%20-%20OKF%20Concept%20List.md) for concept inventory, exact-match filters, and bounded browsing.
- **Creation**: Added the [Feature - OKF Concept List](features/Feature%20-%20OKF%20Concept%20List.md) concept and aligned the list contract to concepts only.
- **Update**: Tightened the architecture bundle with explicit discovery, resolution, output, and error contracts after council review.
- **Creation**: Added the [Architecture](architecture/) bundle to capture the initial `tooling` library and CLI decisions.
- **Creation**: Added [Open Knowledge Format Specification](references/Open%20Knowledge%20Format%20Specification.md) as a local reference for the tooling bundle.
- **Update**: Aligned the architecture prompt and PRDs around a Phase 1 reading MVP and kept the `tooling` knowledge bundle in English.
- **Update**: Translated the `tooling` knowledge bundle to English and renamed documents, folders, and internal links accordingly.
- **Creation**: Created [Prompt - Tooling Architecture Definition](prompts/Prompt%20-%20Tooling%20Architecture%20Definition.md) to guide the initial library and CLI architecture.
- **Update**: Defined deterministic failure when automatic discovery finds multiple bundles, listing reference commands for each candidate.
- **Update**: Adjusted bundle resolution to accept relative paths, absolute paths, or automatic discovery in the current directory.
- **Update**: Migrated the main library and CLI PRD to [PRD - Python Tooling Library and CLI](prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md).
- **Creation**: Created the `tooling` knowledge bundle.
- **Creation**: Registered the overview, initial OKF module PRD, and summarized navigation feature guide.
