---
type: Product
title: Tooling Overview
description: Defines the initial scope of the local Python tooling library and CLI.
tags:
  - tooling
  - cli
  - python
  - okf
---

# Tooling Overview

## Objective

`tooling` is a local Python library and CLI for reusable tools in this repository.

The first supported domain is OKF, focused on summarized navigation, concept inventory, frontmatter property extraction, backlinks, broken links, and bundle health metrics.

## Organization

- `tooling/bundles/` stores knowledge about `tooling` itself in OKF.
- `tooling/src/tooling/` should store the library and CLI code.
- `tooling/tests/` should store automated tests.

## Principles

- Start small and useful inside this repository.
- Separate internal library logic from the command-line interface.
- Keep JSON output stable for skills and automation.
- Avoid tight coupling to the Mulher de Luxo vault layout.
- Leave extraction to a standalone repository as a future step.

## Relations

- [Tooling Product](product/Product%20Overview.md)
- [Product Features](product/features/)
- [SDD Changes](spec-driven-development/changes/)
