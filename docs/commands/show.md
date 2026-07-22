---
type: Command
title: show
description: Read one OKF concept or a generic Markdown file.
tags: [command, show]
---

# `show`

```text
mira-okf show <bundle> <target>
  [--profile {brief,normal,full}] [--summary] [--json]
```

Resolve a target by concept id, bundle-relative Markdown path, or explicit
file path. When the target matches a parsed concept the existing concept
output is returned. When the target does not match a concept but resolves to
a readable `.md` file inside the bundle, generic Markdown output is returned.
Targets outside the bundle, hidden targets, directories, non-Markdown files,
and missing paths are rejected with a non-zero exit code.

`--profile` defaults to `normal`. `--summary` is an alias for `--profile brief`;
if both are supplied, `--summary` wins and the active profile is `brief`.

## Profiles

### Concept output

| Profile | Human output | JSON concept fields |
| --- | --- | --- |
| `brief` | Path, type, title, description, and tags; no body | `concept_id`, `title`, `description`, `type`, `tags`, `relative_path` |
| `normal` | Existing output, including body and the `Issues` section | Current fields, including body and frontmatter |
| `full` | Existing output, including body and issues, plus a sorted `Frontmatter` `key: value` section | Current fields, including body and frontmatter |

### Generic Markdown output

When the target is a generic Markdown file (reserved file or non-concept `.md`
file), the output uses the same envelope and identifies itself with the
`document_kind: "markdown"` discriminator in `data`.

| Profile | Human output | JSON generic fields |
| --- | --- | --- |
| `brief` | `<relative_path>  [Markdown]` | `document_kind`, `relative_path` |
| `normal` | Header plus file content | `document_kind`, `relative_path`, `content` |
| `full` | Same as normal | `document_kind`, `relative_path`, `content` |

Show JSON includes `data.profile` with the active profile. Tolerated issues
remain visible in the existing `Issues` section where applicable. The deferred
`raw_frontmatter` field is not part of this contract.

## Examples

```text
# Show a concept with brief profile (via --summary)
mira-okf show docs my-concept --summary

# Show a concept in full profile
mira-okf show docs my-concept --profile full

# Show a generic Markdown file (reserved or non-concept)
mira-okf show docs log.md

# Show a generic Markdown file as JSON
mira-okf show docs readme.md --json

# Show a generic Markdown file with brief profile
mira-okf show docs readme.md --profile brief
```
