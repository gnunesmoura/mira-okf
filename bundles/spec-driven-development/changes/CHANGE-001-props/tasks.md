---
type: Implementation Task List
title: CHANGE-001 props implementation tasks
description: Orders the implementation and verification work for the props export pilot.
tags: [sdd, change, props, tasks]
status: draft
---

# Ordered Tasks

## Related Product and Architecture Context

- [Tooling Product](/product/Product%20Overview.md)
- [Summarized OKF Navigation](/product/features/Feature%20-%20Summarized%20OKF%20Navigation.md)
- [Data Contracts](/architecture/Data%20Contracts.md)
- [Output and Errors](/architecture/Output%20and%20Errors.md)
- [Command Flows](/architecture/Command%20Flows.md)

## Affected Source Paths

- `/src/tooling/okf/read_model.py`
- `/src/tooling/okf/models.py`
- `/src/tooling/okf/commands.py`
- `/src/tooling/cli.py`
- `/tests/test_list.py`
- `/tests/test_show.py`
- `/tests/test_cli_bootstrap.py`
- `/tests/support.py`

## Citations

- [Open Knowledge Format Specification](/references/Open%20Knowledge%20Format%20Specification.md)
- [Tooling Roadmap](/Tooling%20Roadmap.md)
- [Going Open Source Roadmap](/Going%20Open%20Source%20Roadmap.md)

These tasks are planned only. None is complete until its stated evidence is
recorded during the implementation lifecycle.

1. **Wire the command surface** — add the `props` parser options and command
   dispatch while preserving existing CLI behavior. Depends on the approved
   [spec](spec.md) and [plan](plan.md). Evidence: focused parser and dispatch
   tests pass.
2. **Project the shared read model** — implement the four-field allowlist,
   explicit selection validation, empty/missing/mixed-frontmatter behavior,
   and `concept_id` ordering. Depends on task 1. Evidence: unit tests cover
   each projection rule and show no source mutation.
3. **Implement output formats** — add human table, JSON envelope, and CSV
   serialization with stable field and row ordering. Depends on task 2.
   Evidence: exact-output tests pass for default, selected, and empty output.
4. **Add regression coverage** — create `tests/test_props.py` using existing
   fixture conventions for valid, missing, unknown, empty, and mixed bundles.
   Depends on tasks 2 and 3. Evidence: focused unittest invocation passes.
5. **Run repository validation and review** — run the checks in
   [acceptance tests](acceptance-tests.md) and [agent contract](agent-contract.md),
   inspect the diff, and record evidence before
   changing package status. Depends on tasks 1–4. Evidence: command results,
   `git diff --check`, and human review notes are recorded.

## Completion Gate

The package is not `ready` merely because tasks are listed. Scope, technical
boundaries, dependencies, acceptance checks, agent constraints, and evidence
must be reviewed; implementation statuses belong to a later lifecycle.
