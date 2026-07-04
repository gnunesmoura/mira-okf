---
type: Prompt
title: Prompt - Tooling Architecture Definition
description: Prompt for defining the initial architecture of the Python tooling library and CLI with a strict OKF MVP scope.
tags:
  - tooling
  - architecture
  - prompt
  - python
  - okf
---

# Prompt - Tooling Architecture Definition

## Objective

Use this prompt to define the initial architecture of `tooling`: a local Python library and CLI in this repository, starting with the OKF module and a narrow MVP.

## Prompt

You are a senior Python software architect. Define the initial technical architecture for the local `tooling` library and CLI, considering the OKF bundle documents in `tooling/bundles/`.

Required context:

- The product starts inside this repository, in `tooling/`.
- The root CLI must be `tooling`.
- The first domain is OKF, accessed through `tooling okf ...` commands.
- The code should start small, testable, and removable.
- The OKF module should be extractable to a standalone repository or package in the future.
- The CLI must accept `<bundle>` as a relative or absolute path.
- When `<bundle>` is omitted, the CLI should try to discover an OKF bundle in the current directory.
- If multiple candidates are found, the CLI must fail and list candidates with reference commands for each path.
- Broken links, unknown types, and extra fields must be tolerated.
- Human output must be readable; JSON output must be stable for skills and automation.

Separate the scope explicitly:

### Required MVP

- `tooling okf tree`
- `tooling okf list`
- `tooling okf show`
- bundle discovery
- basic OKF parsing
- human and JSON output
- consistent error envelope

### Future interfaces

- `links`
- `backlinks`
- `props`
- `health`
- `validate`

Future interfaces must be included as contract and test boundaries, but not as required Phase 1 implementation work.

Read and use as primary sources:

- `tooling/bundles/prds/PRD - Python Tooling Library and CLI.md`
- `tooling/bundles/prds/PRD - OKF Module.md`
- `tooling/bundles/features/Feature - Summarized OKF Navigation.md`
- `.agents/skills/okf-authoring/references/SPEC.md`

Deliver an architecture proposal with:

1. Recommended directory structure for `tooling/`.
2. Separation between library, CLI, models, parsing, bundle discovery, output serialization, and error envelopes.
3. Main data contracts, including `Bundle`, `Concept`, `Directory`, `Link`, `Issue`, and the minimum fields for each.
4. Execution flow for `tooling okf tree`, `list`, `show`, and the future interfaces.
5. Automatic bundle discovery strategy when `<bundle>` is omitted.
6. Error strategy for multiple candidates, including message format, reference commands, and stable exit behavior.
7. Initial human and JSON output contracts for the MVP commands.
8. Unit test strategy and minimum fixtures.
9. Recommended Python dependencies and justification.
10. Incremental implementation plan in small steps.
11. Matrix `command x phase x contract x test`.

Constraints:

- Do not implement code in this response.
- Do not create generic abstractions before the first OKF use case.
- Do not depend on Obsidian to read wikilinks.
- Do not depend on fixed paths from this vault.
- Do not require network, database, or external services.
- Do not treat broken links as fatal errors.
- Do not reject bundles because of unknown frontmatter fields.
- Treat OKF core as markdown with YAML frontmatter, required `type`, reserved `index.md` and `log.md`, and tolerant parsing.
- Treat wikilinks as a vault convention that can be supported, but not as a core requirement of the SPEC.
- Do not make `links`, `backlinks`, `props`, `health`, or `validate` mandatory implementation work for Phase 1; only define their boundaries, contracts, and tests.

Response format:

- Start with a summarized architecture decision.
- Then detail the proposed structure.
- Then describe flows, contracts, and the MVP versus future split.
- Include a matrix `command x phase x contract x test`.
- End with an incremental plan and risks.
- Be direct, technical, and specific enough for implementation.

## Relations

- [PRD - Python Tooling Library and CLI](../prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [Feature - Summarized OKF Navigation](../features/Feature%20-%20Summarized%20OKF%20Navigation.md)
