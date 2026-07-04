---
type: PRD
title: PRD - OKF Module
description: Requirements for the OKF module of the tooling library and CLI.
tags:
  - tooling
  - okf
  - prd
  - cli
  - skills
---

# PRD - OKF Module

## Context

The OKF module will be the first domain in the `tooling` library and CLI. It must consume OKF bundles permissively, respecting concepts with YAML frontmatter and required `type`, plus `index.md` and `log.md` as reserved files. OKF core covers reading and navigation; wikilinks are a planned convention for links and backlinks, not a core requirement.

## Objective

Allow people, scripts, and skills to navigate, summarize, and audit OKF bundles without reimplementing Markdown, frontmatter, and link parsing. The MVP is limited to bundle discovery, `tree`, `list`, `show`, basic OKF parsing, and human or JSON output.

## MVP Scope

- Discover an OKF bundle from a relative path, absolute path, or automatic discovery in the current directory.
- Read bundle structure for `tree`, `list`, and `show`.
- Identify concepts, indexes, and logs.
- Parse basic OKF frontmatter and expose the main properties needed for navigation.
- Emit human and JSON output.
- Treat `Issue` as the contract for tolerated read problems that should not block consumption.

## Future Interfaces

- `links`
- `backlinks`
- `props`
- `health`
- `validate`

## Planned Commands

```bash
tooling okf tree [<bundle>] --depth <n> [--summary] [--json]
tooling okf list [<bundle>] [--type <type>] [--tag <tag>] [--json]
tooling okf show [<bundle>] <concept-id-or-path> [--summary] [--json]
```

## Planned Future Commands

```bash
tooling okf links [<bundle>] [--broken] [--external] [--json]
tooling okf backlinks [<bundle>] <concept-id-or-path> [--json]
tooling okf props [<bundle>] [--fields type,title,description,tags] [--format table|json|csv]
tooling okf health [<bundle>] [--json]
tooling okf validate [<bundle>] [--json]
```

## Acceptance Criteria

- The CLI lists the structure of the bundle provided in `<bundle>` without opening all content in the output.
- The CLI accepts `<bundle>` as a relative or absolute path.
- The CLI attempts to discover an OKF bundle in the current directory when `<bundle>` is omitted.
- If discovery finds multiple candidates, the CLI fails and lists candidates with reference commands for each path.
- JSON output from `tree` and `list` is stable for skills.
- Basic OKF parsing tolerates `Issue` entries and other read problems without blocking bundle consumption.
- Concepts missing recommended fields become warnings, not fatal errors.
- `links`, `backlinks`, `props`, `health`, and `validate` are not required for the MVP.
- The OKF module code remains isolated for future extraction.

## Relations

- [PRD - Python Tooling Library and CLI](PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [Tooling Overview](../Tooling%20Overview.md)
- [Feature - Summarized OKF Navigation](../features/Feature%20-%20Summarized%20OKF%20Navigation.md)
