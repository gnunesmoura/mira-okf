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
- a readable bundle fixture for `health` with valid inventory, reserved files, internal links, and a concept containing code blocks and inline code spans
- a readable bundle fixture for `health` with missing optional metadata, missing `index.md`, stale logs, and an external link without a detectable citations section

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
- health with `quick` as the default profile
- health profile evaluation for default versus opt-in rule groups
- health passthrough of validation summary and issue counts
- health ignoring links and headings inside fenced code blocks and inline code spans
- health deterministic JSON and human output ordering

## Rule

If a bug fix changes the read model or command output, add a regression test in the smallest relevant scope.
