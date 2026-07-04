---
type: PRD
title: PRD - OKF Links
description: Requirements for the OKF outbound link command in the tooling library and CLI.
tags:
  - tooling
  - okf
  - prd
  - cli
  - links
---

# PRD - OKF Links

## Context

`tooling okf links` is the first relationship command for OKF bundles. It helps humans, scripts, and skills inspect outbound references from concepts without opening every target. The command must stay permissive because the OKF spec treats broken links as tolerated.

## Objective

Provide a stable outbound link inventory for the resolved bundle that distinguishes resolved internal, broken internal, and external links.

## Scope

- `tooling okf links [<bundle>] [--broken] [--external] [--json]`
- Discover or resolve the bundle using the shared resolver.
- Scan concept bodies only; reserved files are not sources.
- Extract standard Markdown links and Obsidian wikilinks from concept bodies.
- Resolve internal targets against the bundle read model.
- Keep broken internal links as tolerated issues or broken link records, not fatal failures.
- Emit stable human output and JSON output.
- Make the visible result set deterministic across repeated runs.

## Out of Scope

- `tooling okf backlinks`.
- Editing or rewriting links.
- Graph traversal beyond direct outbound links.
- Validation, scoring, and health aggregation.

## Requirements

- Default output includes resolved internal links.
- `--broken` adds broken internal links to the visible result set.
- `--external` adds external links to the visible result set.
- JSON mode places the link payload in `data` and keeps tolerated issues in `issues`.
- Output order is stable and based on source concept path and source order.
- The command uses the same bundle discovery and path rules as the rest of OKF.
- The command must not require Obsidian at runtime.

## User Flow

1. The user points the CLI at a bundle or lets it discover one.
2. The CLI inventories concepts and scans their bodies for links.
3. The CLI classifies each link and resolves internal targets when possible.
4. The CLI prints the requested visible subset in human or JSON form.
5. The CLI preserves tolerated read issues without failing the command.

## Acceptance Criteria

- `tooling okf links <bundle>` returns resolved outbound internal links from concept documents.
- Broken internal links appear when `--broken` is set.
- External links appear when `--external` is set.
- The command never fails solely because a link target is missing.
- Output order is deterministic for the same bundle state.
- JSON output uses the shared envelope.
- Tolerated read issues remain visible in `issues`.

## Minimum Tests

- Extracts Markdown links from a concept fixture.
- Extracts wikilinks from a concept fixture.
- Resolves a bundle-relative internal target.
- Resolves a relative internal target.
- Marks a missing internal target as broken.
- Keeps external links out of default output.
- Includes external links when requested.
- Preserves tolerated issues in JSON output.
- Sorts results deterministically across multiple concepts.

## Relations

- [Feature - OKF Links](../features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](../features/Feature%20-%20OKF%20Backlinks.md)
- [PRD - OKF Module](PRD%20-%20OKF%20Module.md)
- [PRD - Python Tooling Library and CLI](PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [Links Command Contract](../architecture/Links%20Command%20Contract.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
