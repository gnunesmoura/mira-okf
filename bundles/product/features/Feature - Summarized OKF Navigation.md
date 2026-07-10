---
type: Feature
title: Feature - Summarized OKF Navigation
description: Guide for the initial journey that shows an OKF bundle tree with configurable depth.
tags:
  - tooling
  - okf
  - navigation
  - cli
---

# Feature - Summarized OKF Navigation

## Objective

Show a short view of an OKF bundle structure to guide humans, scripts, and skills before expanding specific documents. This feature covers bundle discovery, depth-limited tree output, summary mode, JSON output, multiple-bundle errors, and minimum tests.

## Main Command

```bash
tooling okf tree [<bundle>] --depth 2 --summary
```

`<bundle>` may be a relative or absolute path. When omitted, the CLI should inspect the current directory tree to find OKF bundle roots before failing or picking a unique candidate.

## Expected Behavior

- Resolve the bundle by the provided path or by automatic discovery in the current directory tree.
- Fail when discovery finds multiple bundles and list the candidate paths.
- Show directories up to the requested depth.
- Indicate the presence of `index.md` and `log.md`.
- Count concepts by directory.
- Keep `Issue` as a tolerated read contract so bundle consumption is not blocked by non-fatal problems.
- Emit JSON when `--json` is used.
- Avoid extensive body reads in summarized view.
- Keep `tree` focused on navigation; `links` and `backlinks` are planned later and depend on the core OKF reading model, while wikilinks remain a convention rather than a core requirement.

## Expected Human Output

```text
<bundle>/
  area-a/  index.md  concepts: 1
  area-b/  index.md  log.md
  area-c/  index.md  log.md  concepts: 1
```

## Skill Usage

A skill should start with this feature to understand the bundle structure. After that, it can call `show`, `links`, `backlinks`, `props`, `health`, or `validate` only for relevant paths.

## Minimum Tests

- Discover a bundle when `<bundle>` is omitted.
- Discover nested bundle roots when the current directory itself is not the bundle.
- Fail with multiple candidates when discovery finds more than one bundle.
- Respect the configured depth.
- Emit stable JSON for the summarized tree.
- Preserve tolerant reading when `Issue` entries are present.

## Relations

- [Tooling Overview](../Tooling%20Overview.md)
