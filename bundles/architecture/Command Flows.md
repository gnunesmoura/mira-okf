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

Resolve the bundle, scan directories to the requested depth, count concepts and reserved files, and render a summarized structure.

Tree output should not require full body reads. It may use frontmatter for concept counts and summary metadata, but it should not duplicate parsing rules that already live in the inventory layer.

## list

Resolve the bundle, inventory concepts, apply optional filters, and return a deterministic listing sorted by `concept_id`.

## show

Resolve the bundle and then resolve a target concept by the fixed precedence in `Discovery and Resolution`, returning the parsed concept and its issues.

## Discovery

If the bundle path is omitted, search in the documented order from `Discovery and Resolution`. If multiple candidates exist, fail with a deterministic list of candidates and reference commands.

## Future Interfaces

- `links` should reuse the same inventory and add outbound link extraction.
- `backlinks` should reuse the same link index in reverse.
- `props` should project selected frontmatter fields only.
- `health` should aggregate inventory and link quality metrics.
- `validate` should turn issues into a validation report without changing parse behavior.
