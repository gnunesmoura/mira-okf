---
type: Feature
title: Feature - OKF Links
description: Outbound link discovery for OKF bundles, including resolved, broken, and external links.
tags:
  - tooling
  - okf
  - links
  - cli
---

# Feature - OKF Links

## Objective

Give people, scripts, and skills a stable outbound link inventory for an OKF bundle without opening every target document.

## Scope

- `tooling okf links [<bundle>] [--broken] [--external] [--json]` reports outbound links from concept documents in the resolved bundle.
- The command uses the shared bundle discovery, path normalization, and target-resolution rules.
- The command scans concept bodies only.
- The command extracts standard Markdown links and Obsidian wikilinks from concept bodies outside fenced code blocks and inline code spans.
- Internal links are resolved against the bundle read model and reported as resolved or broken.
- External links are reported separately when `--external` is present.
- Broken internal links are reported when `--broken` is present.
- Raw content display remains the responsibility of `tooling okf show` and is not altered by link scanning.
- Output order is deterministic and suitable for automation.
- JSON output uses the shared envelope and places the visible link payload in `data`.

## Out of Scope

- Inbound link discovery belongs to `tooling okf backlinks`.
- Editing or rewriting links is out of scope.
- Recursive graph traversal is out of scope.
- Treating link semantics as typed relationships is out of scope.
- Failing the command because of broken links is out of scope.

## User Flow

1. A user provides a bundle path or lets the CLI discover a bundle.
2. The CLI scans concept bodies for outbound Markdown links and wikilinks outside fenced code blocks and inline code spans.
3. The CLI classifies each link as resolved internal, broken internal, or external.
4. Optional flags include broken or external links in the visible result set.
5. The CLI renders a compact human view or a stable JSON payload.

## Acceptance Criteria

- `tooling okf links <bundle>` returns outbound links from the resolved bundle.
- Resolved internal links are included in the default output.
- `--broken` makes broken internal links visible in the result set.
- `--external` makes external links visible in the result set.
- Links inside fenced code blocks and inline code spans are ignored by link extraction.
- The command does not fail solely because a link target is missing.
- Broken links are preserved as tolerated issues instead of failing the command.
- Output is stable across repeated runs for the same bundle state.
- JSON mode includes the shared `issues` array.
- The command does not require Obsidian at runtime.

## Minimum Tests

- Extracts outbound Markdown links from a concept fixture.
- Extracts outbound Obsidian wikilinks from a concept fixture.
- Ignores Markdown links and wikilinks inside inline code spans.
- Ignores Markdown links and wikilinks inside fenced code blocks.
- Resolves an internal link to a bundle concept.
- Marks a missing internal target as broken.
- Includes external links only when requested.
- Preserves tolerated read issues in JSON output.
- Emits deterministic ordering for multiple links from multiple concepts.

## Relations

- [PRD - Python Tooling Library and CLI](../prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [PRD - OKF Links](../prds/PRD%20-%20OKF%20Links.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Links Command Contract](../architecture/Links%20Command%20Contract.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Feature - OKF Concept List](Feature%20-%20OKF%20Concept%20List.md)
- [Feature - Summarized OKF Navigation](Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Feature - OKF Backlinks](Feature%20-%20OKF%20Backlinks.md)
