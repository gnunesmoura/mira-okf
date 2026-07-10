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

The durable product context is documented in [Product](product/) and
[Product Features](product/features/). Implementation-specific scope belongs
in [SDD changes](spec-driven-development/changes/).

## Current Focus

The read and analysis command surface is complete through `health`. The only
remaining product feature is `props`, which adds the narrow frontmatter export
surface needed before release preparation can begin.

## Approved SDD Pilot

**CHANGE-001 — props** was approved in this request on 2026-07-10. Owner:
Product Develop Team. Reviewer/approval: human maintainer approval recorded
on 2026-07-10. The bounded outcome is a
read-only `props` projection of the existing frontmatter fields `type`,
`title`, `description`, and `tags`, with documented human table, JSON, and CSV
output as applicable. The future change package must define predictable
behavior for missing or explicitly selected unknown fields, empty bundles,
mixed frontmatter, stable ordering, and regression tests while reusing the
shared read model and output conventions.

Non-goals are bundle mutation, a new property schema, new `props` concepts,
and release-governance work. Confirmed context: [Tooling Product](product/Product%20Overview.md),
[Data Contracts](architecture/Data%20Contracts.md),
[Output and Errors](architecture/Output%20and%20Errors.md), [Command Flows](architecture/Command%20Flows.md),
[Feature - Summarized OKF Navigation](product/features/Feature%20-%20Summarized%20OKF%20Navigation.md),
[Open Knowledge Format Specification](references/Open%20Knowledge%20Format%20Specification.md),
[Tooling Roadmap](Tooling%20Roadmap.md), and [Going Open Source Roadmap](Going%20Open%20Source%20Roadmap.md).
No change package or implementation is created by this selection.

## Product Spine

The remaining OKF roadmap should stay read-only, share one bundle resolver and one read model, and keep human and JSON output stable.

The user journey should move from discovering and opening a single concept, to validating bundle conformance, to summarizing bundle health, to exporting selected properties.

## Feature Sequence

1. `show` - completed; establishes the canonical single-concept read path so later commands share the same target-resolution behavior.
2. `validate` - completed; provides non-blocking conformance reporting without changing bundle parsing behavior.
3. `health` - completed; provides aggregate inventory and quality signals with quick and full reporting profiles.
4. `props` - next and final product feature; adds the narrow frontmatter export surface after the shared read model and output contracts stabilized.

## SDD Change Sequence

1. `CHANGE-001-props` - next because `props` is the only remaining product
   capability before public release preparation.

Future implementation work should be shaped as a change package under
`spec-driven-development/changes/`, with its own specification, technical
plan, tasks, acceptance tests, and agent contract.

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
- [Product](product/)
- [Product Features](product/features/)
- [SDD Changes](spec-driven-development/changes/)
- [Discovery and Resolution](architecture/Discovery%20and%20Resolution.md)
- [Data Contracts](architecture/Data%20Contracts.md)
- [Command Flows](architecture/Command%20Flows.md)
- [Output and Errors](architecture/Output%20and%20Errors.md)
- [Validation Report Contract](architecture/Validation%20Report%20Contract.md)
- [Test Strategy](architecture/Test%20Strategy.md)
- [Incremental Plan and Risks](architecture/Incremental%20Plan%20and%20Risks.md)
