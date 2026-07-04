---
type: ArchitectureDecision
title: Data Contracts
description: Defines the initial read model for bundles, concepts, directories, list windows, links, and issues.
tags:
  - tooling
  - okf
  - contracts
---

# Data Contracts

The OKF read model should be built once in the shared reader module and reused by `tree`, `list`, and later commands. Command handlers should only transform that model into their own output shape.

## Bundle

- `root_path`
- `relative_path`
- `source_kind`
- `source_path`
- `concepts`
- `directories`
- `issues`
- `okf_version`
- `has_root_index`
- `has_root_log`
- `root_index_issues`
- `root_log_issues`

## Concept

- `concept_id`
- `path`
- `relative_path`
- `directory`
- `filename`
- `type`
- `title`
- `description`
- `resource`
- `tags`
- `timestamp`
- `body`
- `frontmatter`
- `issues`

`frontmatter` preserves the parsed mapping, including unknown keys. Normalized fields such as `type`, `title`, `description`, `resource`, `tags`, and `timestamp` are derived from that mapping and should not discard producer-defined data.

Concept invariants:

- non-reserved `.md` files are concept candidates;
- `type` is required and must be non-empty when a file is treated as a concept;
- `concept_id` is the bundle-relative path without `.md`;
- `title` falls back to a filename-derived value when omitted;
- reserved files are never treated as concepts.

## ListResult

- `concepts`
- `total`
- `returned`
- `offset`
- `limit`
- `truncated`

List result invariants:

- `concepts` contains only concept records and stays sorted by `concept_id`;
- `total` is the number of matched concepts before any window is applied;
- `returned` equals the number of concepts in the current payload;
- `offset` is the zero-based position into the sorted filtered match set;
- `limit` is `null` when the full filtered match set is returned;
- `truncated` is `true` when the current payload does not include every matched concept.
- `offset` and `limit` are non-negative when present; invalid values are rejected before the result object is built.

## Directory

- `path`
- `absolute_path`
- `name`
- `depth`
- `has_index`
- `has_log`
- `concept_count`
- `directory_count`
- `children`
- `concepts`
- `issues`

Directory invariants:

- `index.md` and `log.md` are reserved filenames at any depth;
- directory counts and concept counts should be derived from the normalized inventory, not by ad hoc traversal in each command.

## Link

- `source_concept_id`
- `source_path`
- `raw`
- `kind`
- `target`
- `resolved`
- `broken`
- `external`
- `target_concept_id`
- `target_path`

## Issue

- `code`
- `message`
- `severity`
- `path`
- `line`
- `field`
- `suggestion`
- `fatal`

The contracts should be stable enough for later `links`, `backlinks`, `props`, `health`, and `validate` commands without implementing those commands now.
