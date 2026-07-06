---
type: Product
title: Tooling Roadmap
description: Roadmap spine for the remaining OKF work in tooling.
tags:
  - tooling
  - okf
  - roadmap
  - product
---

# Tooling Roadmap

## Purpose

This document is the roadmap spine for the remaining OKF work in `tooling`.

It keeps the product sequence narrow: finish the core read path, then add validation and health views, then add the remaining frontmatter export surface.

## Current Baseline

The current OKF baseline already covers:

- `tree`
- `list`
- `links`
- `backlinks`
- `show`

The existing baseline PRDs are:

- [PRD - Python Tooling Library and CLI](prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](prds/PRD%20-%20OKF%20Module.md)
- [PRD - OKF Concept List](prds/PRD%20-%20OKF%20Concept%20List.md)
- [PRD - OKF Links](prds/PRD%20-%20OKF%20Links.md)
- [PRD - OKF Show](prds/PRD%20-%20OKF%20Show.md)

## Current Focus

`show` is complete as of the recent implementation history. The next implementation-ready bundle is `validate`, which turns shared read-model issues into a non-blocking conformance report without changing bundle parsing behavior.

## Product Spine

The remaining OKF roadmap should stay read-only, share one bundle resolver and one read model, and keep human and JSON output stable.

The user journey should move from discovering and opening a single concept, to validating bundle conformance, to summarizing bundle health, to exporting selected properties.

## Feature Sequence

1. `show` - completed; establishes the canonical single-concept read path so later commands share the same target-resolution behavior.
2. `validate` - next; defines non-blocking conformance reporting while the read model and issue semantics are still simple.
3. `health` - aggregate inventory and quality signals into a compact bundle status view once validation rules are fixed.
4. `props` - add the narrow frontmatter export surface last, after the shared read model and output contracts are stable.

## PRD Sequence

### Baseline PRDs

- [PRD - Python Tooling Library and CLI](prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](prds/PRD%20-%20OKF%20Module.md)
- [PRD - OKF Concept List](prds/PRD%20-%20OKF%20Concept%20List.md)
- [PRD - OKF Links](prds/PRD%20-%20OKF%20Links.md)
- [PRD - OKF Show](prds/PRD%20-%20OKF%20Show.md)
- [PRD - OKF Validation](prds/PRD%20-%20OKF%20Validation.md)

### Implementation-Ready PRDs

1. `PRD - OKF Validation` - next because validation should define conformance reporting before broader health aggregation.

### PRDs to Create

1. `PRD - OKF Health` - after validation because health should summarize the finalized issue vocabulary and quality signals.
2. `PRD - OKF Properties Export` - last because it is a narrow projection surface that depends on stable frontmatter normalization and output contracts.

## Architecture Decisions to Keep Fixed

- One shared resolver handles bundle discovery and concept resolution for every OKF command.
- One stable read model covers bundles, concepts, directories, links, and issues.
- Tolerated issues stay visible on read paths, but they do not block consumption when content is still readable.
- Human output stays concise and path-first.
- JSON output stays stable and uses one shared envelope.
- Read-only behavior stays fixed: no writes, external services, databases, or Obsidian dependencies.

## Non-Goals

- Replacing the existing OKF read path with a new storage layer.
- Adding write, repair, or auto-fix behavior.
- Introducing new bundle folder conventions or vault-specific assumptions.
- Turning `tree` into detail view or `list` into structural navigation.
- Expanding beyond direct read, validation, and export concerns.
- Re-defining the current permissive parsing model.

## Relations

- [Tooling Overview](Tooling%20Overview.md)
- [Feature - Summarized OKF Navigation](features/Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Feature - OKF Concept List](features/Feature%20-%20OKF%20Concept%20List.md)
- [Feature - OKF Links](features/Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](features/Feature%20-%20OKF%20Backlinks.md)
- [Feature - OKF Show](features/Feature%20-%20OKF%20Show.md)
- [Feature - OKF Validation](features/Feature%20-%20OKF%20Validation.md)
- [Discovery and Resolution](architecture/Discovery%20and%20Resolution.md)
- [Data Contracts](architecture/Data%20Contracts.md)
- [Command Flows](architecture/Command%20Flows.md)
- [Output and Errors](architecture/Output%20and%20Errors.md)
- [Validation Report Contract](architecture/Validation%20Report%20Contract.md)
- [Test Strategy](architecture/Test%20Strategy.md)
- [Incremental Plan and Risks](architecture/Incremental%20Plan%20and%20Risks.md)
