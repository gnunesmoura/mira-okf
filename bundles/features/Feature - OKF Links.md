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

Help people, scripts, and skills inspect the outbound relationships in an OKF bundle without opening every target document.

## Scope

- `tooling okf links [<bundle>] [--broken] [--external] [--json]` reports outbound links from concept documents in the resolved bundle.
- The command uses the shared bundle discovery and path rules.
- The command extracts Markdown links and Obsidian wikilinks from concept bodies.
- Internal links are resolved against the bundle and reported as resolved or broken.
- External links are reported separately when `--external` is present.
- Broken internal links are reported when `--broken` is present.
- Output order is deterministic and suitable for automation.
- JSON output uses the shared envelope and places the link payload in `data`.

## Out of Scope

- Inbound link discovery belongs to `tooling okf backlinks`.
- Editing or rewriting links is out of scope.
- Recursive graph traversal is out of scope.
- Treating link semantics as typed relationships is out of scope.
- Failing the command because of broken links is out of scope.

## User Flow

1. A user provides a bundle path or lets the CLI discover a bundle.
2. The CLI scans concept bodies for outbound links.
3. The CLI classifies each link as resolved internal, broken internal, or external.
4. Optional flags include broken or external links in the visible result set.
5. The CLI renders a compact human view or a stable JSON payload.

## Acceptance Criteria

- `tooling okf links <bundle>` returns outbound links from the resolved bundle.
- Resolved internal links are included in the default output.
- `--broken` makes broken internal links visible in the result set.
- `--external` makes external links visible in the result set.
- Broken links are preserved as tolerated issues instead of failing the command.
- Output is stable across repeated runs for the same bundle state.
- JSON mode includes the shared `issues` array.

## Minimum Tests

- Extracts outbound Markdown links from a concept fixture.
- Extracts outbound Obsidian wikilinks from a concept fixture.
- Resolves an internal link to a bundle concept.
- Marks a missing internal target as broken.
- Includes external links only when requested.
- Preserves tolerated read issues in JSON output.
- Emits deterministic ordering for multiple links from multiple concepts.

## Relations

- [PRD - Python Tooling Library and CLI](../prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Feature - OKF Concept List](Feature%20-%20OKF%20Concept%20List.md)
- [Feature - Summarized OKF Navigation](Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Feature - OKF Backlinks](Feature%20-%20OKF%20Backlinks.md)
