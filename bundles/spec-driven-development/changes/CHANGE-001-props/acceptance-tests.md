---
type: Acceptance Test Suite
title: CHANGE-001 props acceptance tests
description: Defines observable checks for read-only props export behavior and regression evidence.
tags: [sdd, change, props, tests]
status: draft
---

# Observable Checks

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

Each check is expected to be run after implementation. Results are intentionally
not recorded in this draft package.

| ID | Check | Expected result |
| --- | --- | --- |
| AT-01 | Run default `props` against a bundle with several concepts. | Four columns (`type`, `title`, `description`, `tags`) and one row per readable concept; rows are sorted by `concept_id`. |
| AT-02 | Select an ordered subset of supported fields. | Only selected columns appear, in requested order, in table, JSON, and CSV output. |
| AT-03 | Select an unknown field explicitly. | Command exits with a deterministic input error and does not emit a partial export. |
| AT-04 | Read concepts missing one or more approved fields. | JSON uses `null` for missing scalar values and `[]` for missing tags; table and CSV use empty cells. |
| AT-05 | Read an empty bundle. | Successful empty result includes selected columns and zero rows without crashing. |
| AT-06 | Read mixed valid, unknown-key, and malformed-but-readable frontmatter. | Readable concepts remain exported; unknown keys are not projected; tolerated issues remain visible. |
| AT-07 | Repeat the same export with filesystem entries created in different order. | Row order, field order, JSON keys, and CSV header are stable. |
| AT-08 | Compare a bundle before and after export. | No file contents, metadata, or frontmatter are changed. |
| AT-09 | Run existing focused tests plus the props suite. | Existing behavior remains green and the new regression suite passes. |

## Planned Commands and Evidence

The implementation should run the focused suite with
`python -m unittest discover -s tests -p 'test_props.py'` and the repository
suite with `python -m unittest discover -s tests`. Run `git diff --check` and
the repository's available structural/link checks. If `pytest` is absent, use
unittest and report that fact; it is not a blocker. Record actual commands and
results before any status advances beyond draft.
