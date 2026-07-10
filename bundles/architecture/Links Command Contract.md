---
type: ArchitectureContract
title: Links Command Contract
description: Defines outbound link extraction, classification, and output for `tooling okf links`.
tags:
  - tooling
  - okf
  - links
  - architecture
---

# Links Command Contract

## Scope

This contract governs outbound link extraction and presentation for `links`, while sharing the read model and normalization boundary with related commands. It does not define backlink traversal or body mutation.

## Context

The core OKF read model already inventories concepts, body text, and issues. `links` needs a deterministic way to scan concept bodies for outbound references without making broken links fatal or requiring a particular editor.

## Behavior Contract

`tooling okf links` should:

- resolve the bundle through the shared discovery rules;
- scan concept bodies for standard Markdown links and Obsidian wikilinks;
- classify each extracted link as `internal` or `external`;
- resolve internal targets against the bundle using bundle-relative, relative, and wikilink target rules;
- preserve unresolved internal targets as broken link records instead of failing the command;
- expose only the requested classes in human output, with `--broken` adding broken internal links and `--external` adding external links;
- order the visible result deterministically by source concept path, then source order within the body, then normalized target.

The command should emit a stable JSON payload in `data` containing the visible link records and their classification. Tolerated read issues remain in the top-level `issues` array.

## Invariants

Extraction is read-only, broken internal targets remain records, and result ordering is deterministic by source path, body order, and normalized target.

## Consequences

- Outbound link inspection becomes a read-only projection over the existing bundle model.
- Broken and external links stay visible without preventing automation from consuming the result.
- Backlinks can reuse the same extraction and resolution data in reverse instead of re-parsing body text.
- The command remains permissive and aligned with the OKF specification.

## Compatibility Rules

Use the shared read model, semantic normalization, issue channel, and JSON envelope so `backlinks` can reverse the same link records without a second extraction contract.

## Relations

- [Feature - OKF Links](../product/features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](../product/features/Feature%20-%20OKF%20Backlinks.md)
- [Command Flows](Command%20Flows.md)
- [Data Contracts](Data%20Contracts.md)
- [Output and Errors](Output%20and%20Errors.md)
- [Test Strategy](Test%20Strategy.md)
