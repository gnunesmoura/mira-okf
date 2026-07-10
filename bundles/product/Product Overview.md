---
type: Product
title: Tooling Product
description: Local Python library and CLI that helps people and agents navigate and analyze OKF bundles.
tags: [tooling, product, okf, cli]
---

# Tooling Product

## Purpose

`tooling` is a local Python library and CLI for people, scripts, automations,
and skills that need to read and analyze Open Knowledge Format bundles.

The product provides a common read layer over Markdown concept trees,
including bundle discovery, concept parsing, structural browsing, inventory,
single-concept reading, link analysis, validation, and health reporting.

## Product principles

- Reading is read-only by default; the tooling does not silently mutate bundle
  documents.
- Human output is concise and path-first.
- Machine output is stable and uses explicit contracts.
- Tolerated content issues remain visible without blocking readable content.
- Shared discovery, parsing, resolution, and issue semantics are reused across
  commands.
- OKF remains the portable Markdown-based knowledge format and is not replaced
  by a database or central schema.

## Users

- Human authors reviewing and navigating a knowledge bundle.
- Agents that need progressive disclosure and stable context.
- Skills and automation that consume deterministic JSON output.
- Developers extending the local tooling library and CLI.

## Capabilities

User-visible capabilities are documented in [Product Features](features/).
Implementation-specific work belongs in
[Spec-Driven Development changes](../spec-driven-development/changes/).

## Boundaries

Technical contracts and reusable implementation constraints remain in
[Architecture](../architecture/). The local OKF rules remain in
[References](../references/).
