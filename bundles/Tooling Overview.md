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

- [PRD - Python Tooling Library and CLI](prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](prds/PRD%20-%20OKF%20Module.md)
- [Feature - Summarized OKF Navigation](features/Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Feature - OKF Concept List](features/Feature%20-%20OKF%20Concept%20List.md)
