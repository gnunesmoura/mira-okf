---
type: ArchitectureDecision
title: OKF Boundaries
description: Defines the module boundaries for the OKF domain and the CLI adapters.
tags:
  - tooling
  - okf
  - boundaries
---

# OKF Boundaries

## Library

Own the domain model, bundle discovery, identity normalization, inventory, parsing, query resolution, and issue aggregation.

## CLI

Own command parsing, exit codes, user-facing formatting, and JSON selection.

## Models

Keep typed contracts only. Do not read files or format output in model classes.

## Discovery

Find a bundle from an explicit path or from the current directory using a small, deterministic search order. Discovery must produce one root or one ambiguity error, never an implied fallback.

## Parsing

Read YAML frontmatter and markdown bodies permissively. Do not reject bundles because of unknown keys or unknown `type` values. Preserve raw frontmatter separately from normalized fields.

## Serialization

Centralize stable human and JSON output. Do not let commands invent their own JSON shapes or sort rules.

## Errors

Use a single envelope for fatal command failures. Keep tolerated content problems as `Issue` records attached to the read model. The envelope must be shared by all commands.
