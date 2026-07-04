# AGENTS

Use these instructions when developing or maintaining this repository.

## Purpose

- Build a small, reliable Python library and CLI for local developer and agent workflows.
- Keep the code easy to understand, test, replace, and extract.
- Prefer clear domain boundaries over generic abstractions.
- Treat documentation, tests, and CLI behavior as part of the product.

## Engineering Principles

- Write production code in English: module names, classes, functions, commands, errors, comments, and docs.
- Keep changes narrow and intentional.
- Separate domain logic from infrastructure, filesystem access, serialization, and CLI presentation.
- Do not introduce framework-style abstractions before the domain model needs them.
- Prefer explicit data contracts over loosely shaped dictionaries at module boundaries.
- Preserve backward-compatible CLI and JSON behavior unless a documented change requires otherwise.
- Avoid hidden dependencies on a specific machine, vault layout, network, database, or external service.

## Domain-Driven Design

- Model the domain in the library before exposing it through the CLI.
- Use domain names consistently in code, tests, and documentation.
- Keep entities, value objects, services, and errors close to the domain they belong to.
- Make invalid or ambiguous domain states visible through typed results, issues, or explicit errors.
- Keep adapters thin: CLI, filesystem, and output formatting should call domain/application services, not own business rules.

## Test-Driven Development

- Start behavior changes with a failing or missing test whenever practical.
- Write small tests around domain rules before broad integration tests.
- Use fixtures that are minimal, readable, and specific to the behavior under test.
- Cover normal paths, edge cases, and error paths for every public command or contract.
- When fixing a bug, add a regression test that would have failed before the fix.
- Do not weaken or delete tests to make a change pass unless the product behavior was intentionally changed and documented.

## Code Quality

- Prefer simple Python 3.11+ code with minimal dependencies.
- Keep functions short enough to read without losing context.
- Use type hints for public functions, data contracts, and cross-module boundaries.
- Use dataclasses or typed models when they clarify domain structure.
- Keep comments rare and useful; explain why, not what the code already says.
- Make errors actionable: include what failed, where it failed, and what the user can do next.
- Keep human output readable and JSON output stable.

## Documentation

- Update documentation when commands, contracts, setup, domain behavior, or roadmap decisions change.
- Keep product and architecture knowledge in `tooling/bundles/`.
- Content inside `tooling/bundles/` must be written in English.
- If documentation belongs to an OKF bundle, preserve valid YAML frontmatter for concept files and keep `index.md`/`log.md` frontmatter-free.

## Working Rules

- Read the nearby README, PRD, feature, or design note before changing behavior.
- Do not edit generated files manually when a generator owns them.
- Preserve unrelated work in the repository.
- Before finishing, run the narrowest relevant tests or explain why they were not run.
