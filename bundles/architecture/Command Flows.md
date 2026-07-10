---
type: ArchitectureDecision
title: Command Flows
description: Describes the initial command behavior for tree, list, show, discovery, and future interfaces.
tags:
  - tooling
  - okf
  - cli
---

# Command Flows

## tree

Resolve the bundle through the shared resolver, scan directories to the requested depth, count concepts and reserved files, and render a summarized structure.

Tree output should not require full body reads. It may use frontmatter for concept counts and summary metadata, but it should not duplicate parsing rules that already live in the inventory layer.

## list

Resolve the bundle through the shared resolver, inventory concepts only, apply optional exact-match `type` and `tag` filters with AND semantics, sort by `concept_id`, and return a deterministic windowed listing with total-match metadata.

When `--offset` and `--limit` are present, apply them after filtering and sorting so that chunked browsing stays stable.

## show

Resolve the bundle through the shared resolver and then resolve a target concept by the fixed precedence in `Discovery and Resolution`, returning the parsed concept and its issues.

## Discovery

If the bundle path is omitted, search in the documented order from `Discovery and Resolution`. If multiple candidates exist, fail with a deterministic list of candidates and reference commands.

## Future Interfaces

- `links` should reuse the same inventory and add outbound link extraction.
- `backlinks` should reuse the same link index in reverse.
- `props` should project selected frontmatter fields only.
- `health` should aggregate validation summary, inventory, reserved files, links, indexes, logs, metadata, citations, and connectivity into a profile-based status report.
- `validate` should turn issues into a validation report without changing parse behavior.
