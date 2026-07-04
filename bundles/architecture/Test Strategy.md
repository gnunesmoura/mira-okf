---
type: ArchitectureDecision
title: Test Strategy
description: Defines the minimum fixture set and test coverage for the MVP.
tags:
  - tooling
  - okf
  - tests
---

# Test Strategy

## Minimum Fixtures

- a valid nested bundle with `index.md`, `log.md`, and multiple concepts
- an ambiguous setup with two candidate bundles
- a malformed concept missing `type`
- a concept with extra frontmatter keys
- a concept with a broken relative link

## Coverage

- discovery with and without an explicit bundle path
- ambiguity failure with candidate commands
- show resolution precedence by concept ID and path
- depth-limited tree output
- filtered list output
- stable JSON shape and ordering
- stable error envelope shape
- deterministic sort order
- tolerated issues for invalid or incomplete content
- non-fatal handling of unknown `type` values, extra frontmatter fields, and broken links

## Rule

If a bug fix changes the read model or command output, add a regression test in the smallest relevant scope.
