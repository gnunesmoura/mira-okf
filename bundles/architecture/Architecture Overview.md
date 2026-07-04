---
type: ArchitectureDecision
title: Architecture Overview
description: Summarizes the initial architecture for the local tooling library and OKF CLI.
tags:
  - tooling
  - architecture
  - okf
---

# Architecture Overview

`tooling` should start as a small, stdlib-first Python CLI with one domain package for OKF.

The MVP is a read-only navigation layer:

- discover a bundle;
- parse OKF concepts permissively;
- inventory directories and reserved files;
- render `tree`, `list`, and `show`;
- keep human and JSON output stable;
- surface non-fatal problems as issues instead of blocking reads.

The OKF module should stay isolated enough to extract later, but the initial code should not optimize for extraction ahead of usability.

## Core Decisions

- Use a thin CLI that delegates all bundle logic to library services.
- Keep bundle resolution, OKF read-model construction, serialization, and presentation separate from domain models.
- Preserve unknown frontmatter keys.
- Treat broken links, unknown types, missing optional fields, and extra frontmatter fields as tolerated issues.
- Use one consistent machine-readable error envelope for CLI and automation.
- Make discovery and `show` resolution deterministic before adding future interfaces.
- Normalize bundle-relative identity once and reuse it across `tree`, `list`, and `show`.
- Leave `links`, `backlinks`, `props`, `health`, and `validate` as explicit future seams.
