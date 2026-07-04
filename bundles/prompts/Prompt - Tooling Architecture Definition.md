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

You are a senior Python software architect. Define the initial architecture for the local `tooling` Python library and CLI.

Use these primary sources:

- `tooling/bundles/prds/PRD - Python Tooling Library and CLI.md`
- `tooling/bundles/prds/PRD - OKF Module.md`
- `tooling/bundles/features/Feature - Summarized OKF Navigation.md`
- `tooling/bundles/references/Open Knowledge Format Specification.md`

Architecture constraints:

- Start inside this repository with root CLI command `tooling`.
- First domain: OKF through `tooling okf ...`.
- Keep the code small, testable, removable, and OKF-focused.
- Keep library/domain logic separate from CLI, filesystem, parsing, serialization, and presentation.
- Keep the OKF module isolated enough for possible later extraction, but do not design around extraction yet.
- Accept `<bundle>` as a relative or absolute path.
- When `<bundle>` is omitted, discover an OKF bundle from the current directory.
- If discovery finds multiple candidates, fail and list candidates with reference commands.
- Treat broken links, unknown types, missing optional fields, and extra frontmatter fields as tolerated issues, not fatal parse errors.
- Keep human output readable and JSON output stable for skills and automation.

### Required MVP

- `tooling okf tree`
- `tooling okf list`
- `tooling okf show`
- bundle discovery
- basic OKF parsing
- human and JSON output
- consistent error envelope

### Future Interfaces

- `links`
- `backlinks`
- `props`
- `health`
- `validate`

Define contract and test boundaries for future interfaces, but do not make them Phase 1 implementation work.

OKF rules:

- OKF core is Markdown with YAML frontmatter.
- Concept files have required `type`.
- `index.md` and `log.md` are reserved files.
- Unknown frontmatter fields must be preserved.
- Wikilinks may be supported as a convention, but must not require Obsidian.
- Do not depend on fixed vault paths, network, database, or external services.

Deliver:

1. Summarized architecture decision.
2. Directory structure.
3. Boundaries for library, CLI, models, parsing, discovery, serialization, and errors.
4. Data contracts for `Bundle`, `Concept`, `Directory`, `Link`, and `Issue`.
5. Flows for `tree`, `list`, `show`, and future interfaces.
6. Discovery and multiple-candidate error behavior.
7. Human and JSON output contracts.
8. Test strategy and minimum fixtures.
9. Dependencies with justification.
10. Matrix: `command x phase x contract x test`.
11. Small incremental implementation plan and risks.

Response format:

- Start with a summarized architecture decision.
- Separate MVP from future work.
- End with an incremental plan and risks.
- Be direct, technical, and specific enough for implementation.
- Do not implement code.

## Relations

- [PRD - Python Tooling Library and CLI](../prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [Feature - Summarized OKF Navigation](../features/Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Open Knowledge Format Specification](../references/Open%20Knowledge%20Format%20Specification.md)
