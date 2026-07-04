---
type: PRD
title: PRD - Python Tooling Library and CLI
description: Requirements for the local tooling library and CLI, starting with the OKF reading core and leaving links, health, and validation for later phases.
tags:
  - okf
  - tooling
  - cli
  - skills
  - python
---

# PRD - Python Tooling Library and CLI

## Context

The Mulher de Luxo repository uses `artifacts/` as an OKF bundle for knowledge, planning, automation, and attachments. The local SPEC defines a bundle as a Markdown file tree, with concept documents using YAML frontmatter and a required `type`, plus reserved `index.md` and `log.md` files.

`tooling` starts inside this repository as a small Python library and CLI. The first supported domain is OKF. Extraction to another repository should happen only after the API, commands, and usage journeys are mature enough.

## Problem

People and agents need to navigate and read the repository without manually opening the entire tree. For OKF, navigation currently depends on `index.md`, text search, and manual file reading. This limits:

- fast discovery of bundle structure;
- summarized reading before detailed expansion;
- consistent reading of concept, type, and description;
- objective issue reporting without blocking reads;
- skill and automation usage with stable output.

## Objective

Build a local Python library and CLI called `tooling`, used as a common layer by scripts, automations, and skills in this repository. The first module will be `tooling.okf`, focused on reading and inventorying OKF bundles.

The first journey should cover summarized navigation and core reading: `tree`, `list`, `show`, bundle discovery, basic OKF parsing, stable human/JSON output, and objective errors.

## Non-Goals

- Build a web server in the MVP.
- Replace OKF with a database or central schema.
- Automatically rewrite bundle documents in the MVP.
- Reject bundles because of broken links, unknown types, or extra fields.
- Create a separate repository before validating real use here.
- Turn the package into a public product in the MVP.

## Initial Corpus

Initial validation fixture in this repository: `artifacts/`.

Observed on 2026-07-04:

- 52 Markdown files.
- 16 `index.md` files.
- 4 `log.md` files.
- 32 concepts with `type`.
- Existing concept categories include PRDs, roadmaps, products, operations, systems, KPIs, OKRs, governance, access, data, migrations, analyses, plans, procedures, support, automation, infrastructure, and institutional references.
- The bundle uses Obsidian `[[...]]` links, relative Markdown links, and references to paths that may not exist yet.

## Users

- Human OKF author who needs to review structure and gaps.
- Consumption agent that needs summarized context before opening files.
- Authoring agent that needs to validate reading and context before changing a bundle.
- Skill developer who needs a stable interface for local tooling.

## Product

The product is a local Python library with a CLI called `tooling`, maintained in this repository.

The library should separate reusable logic from terminal presentation. The CLI should expose small, composable commands with human-readable output by default. When requested, it should emit stable JSON for skills and automation.

Suggested initial structure:

```text
tooling/
  bundles/
    index.md
    log.md
    prds/
    features/
    prompts/
  pyproject.toml
  src/tooling/
    __init__.py
    cli.py
    okf/
      __init__.py
      models.py
      parser.py
      links.py
      health.py
      commands.py
  tests/
```

The root command should be `tooling`. OKF is exposed as a subcommand. The bundle can be provided as a relative or absolute path:

```bash
tooling okf tree <bundle> --depth 2 --summary
```

## Principles

- OKF remains readable without tooling.
- The CLI consumes bundles permissively, according to the SPEC.
- Skills use the CLI as a common reading and analysis layer.
- Summarized output comes before detailed expansion.
- Every feature must accept a relative or absolute bundle path.
- When `<bundle>` is omitted, the CLI should try to discover an OKF bundle in the current directory.
- The tooling should run locally with minimal dependencies.
- The OKF module should remain isolated for possible future extraction.
- Future extraction should not drive the MVP design.

## MVP Journey

1. The user or skill calls `tooling okf`, pointing to a bundle by relative or absolute path.
2. The OKF library identifies directories, reserved files, and concepts.
3. The CLI shows `tree`, `list`, and `show` with summarized reading.
4. Bundle discovery works when `<bundle>` is omitted.
5. Basic OKF parsing preserves unknown fields and handles permissive content.
6. Human and JSON output remains stable.
7. Errors are objective and do not block reading when content can still be inventoried.

If the bundle is not provided, the CLI should look for a likely OKF root in the current directory. Initial discovery should consider, in this order:

1. the current directory, if it contains `index.md` or Markdown concepts with OKF frontmatter;
2. an `artifacts/` subdirectory, if it exists;
3. a `tooling/bundles/` subdirectory, when called from this repository root.

When more than one candidate exists, the CLI must fail with an objective message listing candidates and a reference command for each discovered path.

Ambiguity failure example:

```text
More than one OKF bundle found. Provide the path explicitly:
- artifacts/ -> tooling okf tree artifacts --depth 2 --summary
- tooling/bundles/ -> tooling okf tree tooling/bundles --depth 2 --summary
```

Desired example:

```bash
tooling okf tree <bundle> --depth 2 --summary
```

Expected human output:

```text
<bundle>/
  area-a/  index.md  concepts: 1
  area-b/  index.md  log.md
  area-c/  index.md  concepts: 2
```

Equivalent JSON output:

```bash
tooling okf tree <bundle> --depth 2 --summary --json
```

## Functional Requirements

### Reading and Inventory

- Accept `<bundle>` as a relative or absolute path.
- Discover an OKF bundle in the current directory when `<bundle>` is omitted.
- Report ambiguity when automatic discovery finds more than one candidate, listing candidates and a reference command for each path.
- Detect concepts, `index.md`, `log.md`, and other Markdown files automatically.
- Parse YAML frontmatter from concepts.
- Preserve unknown fields in the read model.
- Derive `concept_id` from the relative path without `.md`.
- Derive title from frontmatter or filename.
- Detect files without frontmatter when they are not `index.md` or `log.md`.

### Summarized Navigation

- Display a tree by configurable depth.
- Allow filters by `type`, tag, directory, and `index.md` presence.
- Show directory summary: concept count, subdirectory count, indexes, and logs.
- Allow compact mode for agent context.
- Allow JSON mode for skills.

### Links and Relationships

- This phase is outside the core MVP.
- Extract Markdown and Obsidian links.
- Resolve relative, bundle-relative, and wikilink targets when possible.
- List backlinks and outbound links for a concept.
- Separate resolved, broken, and external links.
- Do not fail on broken links.
- Wikilinks are a supported convention in this phase, not a core OKF requirement.

### Health and Quality

- This is a future phase.
- Count concepts by `type`, tag, and directory.
- Measure concepts missing `description`, `title`, tags, and timestamp.
- Measure directories missing `index.md`.
- Measure missing `log.md` in configured areas.
- Measure broken internal links and orphan documents.
- Emit a simple score by bundle and directory, explaining the issues.

### Data Capture

- This is a future phase.
- Export frontmatter properties to CSV and JSON.
- Generate a concept index with path, type, title, description, tags, and links.
- Generate metrics snapshots for future comparison.
- Allow field selection on export.

### OKF Validation

- This is a future phase.
- Validate minimum conformance: parseable frontmatter and non-empty `type` in concepts.
- Validate `index.md` and `log.md` structure as warnings, not blocking errors.
- Report issues with path, line when possible, severity, and suggestion.

## Initial Commands

```bash
tooling okf tree [<bundle>] --depth <n> [--summary] [--json]
tooling okf list [<bundle>] [--type <type>] [--tag <tag>] [--json]
tooling okf show [<bundle>] <concept-id-or-path> [--summary] [--json]
```

## Future Commands

```bash
tooling okf links [<bundle>] [--broken] [--external] [--json]
tooling okf backlinks [<bundle>] <concept-id-or-path> [--json]
tooling okf props [<bundle>] [--fields type,title,description,tags] [--format table|json|csv]
tooling okf health [<bundle>] [--json]
tooling okf validate [<bundle>] [--json]
```

## Skill Suite

### OKF Navigation Skill

Uses `tooling okf tree`, `tooling okf list`, and `tooling okf show` to guide progressive reading. It should start with a summarized view and expand only relevant areas.

### OKF Backlinks Skill

Uses `tooling okf backlinks` and `tooling okf links` to answer questions about relationships, dependencies, and documents pointing to a concept.

### OKF Health Skill

Uses `tooling okf health` and `tooling okf validate` to audit conformance, broken links, orphan documents, missing properties, and index gaps.

### OKF Capture Skill

Uses `tooling okf props` and JSON/CSV snapshots to extract properties for reports, bases, dashboards, or corpus reviews.

### OKF Assisted Authoring Skill

Uses the CLI before changing files to locate the correct context, confirm existing links, and avoid concept duplication.

## Internal Data Model

Minimum entities:

- `Bundle`: root, inferred version, files, directories, and metrics.
- `Concept`: path, `concept_id`, frontmatter, body, title, description, type, and tags.
- `Directory`: path, index presence, log presence, children, and counts.
- `Link`: source, raw target, resolved target, kind `markdown`, `obsidian`, or `external`, and status.
- `Issue`: path, severity, code, message, and suggestion.

`Issue` is a contract from the start to register problems without blocking reads.

## Technical Requirements

- Python 3.11+.
- Minimal dependencies: YAML parser, CLI library, and tests.
- Separate internal library and CLI layer.
- Design commands for shell, skills, and automation use.
- Guarantee stable JSON output.
- Include test fixtures based on small bundles.
- Avoid depending on Obsidian while supporting `[[wikilink]]` syntax in the later links phase.
- Keep the package in its own directory to simplify removal or future extraction.
- Avoid reverse imports from `tooling` into business-specific scripts.
- Maintain an OKF bundle in `tooling/bundles/` with guides, PRDs, features, prompts, and tooling decisions.

## Future Extraction Strategy

`tooling` should start locally to reduce coordination cost. Extraction to `/home/gununmo/Documentos/okf-tooling/` or another repository should be considered only when:

- commands are regularly used by skills or scripts;
- the OKF module has tests covering parsing, links, backlinks, and health;
- the JSON interface is stable;
- the package does not depend on fixed paths in this vault;
- installation and usage documentation is sufficient to run outside this repository.

Until then, this repository is the product, validation, and evolution environment.

## MVP Acceptance Criteria

- `tooling okf tree <bundle> --depth 2 --summary` shows the structure of the provided bundle without opening every file in the output.
- `tooling okf tree /absolute/path/to/bundle --depth 2 --summary` works with an absolute path.
- `tooling okf tree relative/path/to/bundle --depth 2 --summary` works with a relative path.
- `tooling okf tree --depth 2 --summary` attempts to discover an OKF bundle in the current directory.
- `tooling okf tree --depth 2 --summary` fails with candidates and reference commands when more than one likely bundle exists in the current directory.
- `tooling okf list <bundle> --type PRD --json` returns PRD concepts with path and main properties.
- `tooling okf show <bundle> <concept>` shows the concept with summarized reading or stable JSON.
- Skills can depend on the CLI without reimplementing OKF parsing.
- The implementation stays contained in `tooling/` and can be removed without changing OKF content.

## Roadmap

### Phase 1 - Reading Core

- Local Python package structure for `tooling`.
- Markdown and frontmatter parser.
- Bundle inventory.
- Commands `tooling okf tree`, `tooling okf list`, and `tooling okf show`.
- Human and JSON output.

### Phase 2 - Links and Backlinks

- Markdown link parser.
- Obsidian wikilink parser.
- Path resolution.
- Commands `tooling okf links` and `tooling okf backlinks`.
- Broken link report.

### Phase 3 - Health and Validation

- Commands `health` and `validate`.
- Metrics by directory, type, and tag.
- Issues with severity.
- JSON snapshots.

### Phase 4 - Capture and Skill Integration

- Command `tooling okf props`.
- CSV and JSON export.
- Skill templates.
- Documentation for the skill -> CLI -> bundle journey.

### Phase 5 - Local Extensions

- Assisted `index.md` generation.
- Related link suggestions.
- Snapshot diffs between commits.
- Markdown health report.
- Optional local cache support.

### Phase 6 - Optional Extraction

- Assess package maturity.
- Remove implicit repository dependencies.
- Create a standalone repository, if there is real benefit.
- Publish installation instructions outside this vault.

## Risks

- Resolving wikilinks ambiguously when multiple files share the same name.
- Creating validations that are too strict and contradict OKF's permissive philosophy.
- Mixing automatic authoring with auditing before read behavior is stable.
- Producing output that is too verbose for agents.
- Coupling `tooling` to the Mulher de Luxo layout and making extraction harder.
- Generalizing too early and delaying real use in this repository.

## Initial Decisions

- Implementation starts in this repository, inside its own `tooling/` directory.
- Tooling knowledge lives in `tooling/bundles/`, using OKF.
- The `artifacts/` bundle is the first real validation fixture.
- The CLI is a prerequisite for the skills.
- The MVP prioritizes core reading and summarized navigation, not complete auditing.
- Broken links are treated as health signals, not fatal errors.
- Extraction to a standalone library or CLI is a future step.

## Command x Phase x Contract x Test Matrix

| Command | Phase | Contract | Test |
|---|---|---|---|
| `tooling okf tree` | Phase 1 | relative/absolute bundle input and automatic discovery | small bundle fixture, human and JSON output |
| `tooling okf list` | Phase 1 | type filter and basic concept reading | predictable list by type, unknown fields preserved |
| `tooling okf show` | Phase 1 | concept reading by id/path and stable JSON | summarized and JSON output comparison |
| `tooling okf links` | Phase 2 | link resolution and status classification | resolved, broken, and external cases |
| `tooling okf backlinks` | Phase 2 | inverse link relationship | fixture with multiple references |
| `tooling okf props` | Phase 4 | field selection and export | CSV/JSON with expected columns |
| `tooling okf health` | Phase 3 | metrics and explainable score | metrics snapshot by bundle/directory |
| `tooling okf validate` | Phase 3 | issues with severity, path, and suggestion | warning and minimum-error cases |

## Relations

- [Tooling Overview](../Tooling%20Overview.md)
- [PRD - OKF Module](PRD%20-%20OKF%20Module.md)
- [Feature - Summarized OKF Navigation](../features/Feature%20-%20Summarized%20OKF%20Navigation.md)
