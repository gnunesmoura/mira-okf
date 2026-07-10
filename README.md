# Tooling

`tooling` is a local Python library and CLI for reading and navigating OKF
(Open Knowledge Format) bundles. An OKF bundle is a directory of Markdown
files with YAML frontmatter, plus reserved `index.md` and `log.md` files.

The project is designed for people, skills, and scripts that need a compact
view of a bundle before opening individual documents. The current product
scope is deliberately local and OKF-focused; it is not yet presented as a
stable public package.

## Status

This repository is the development and validation environment for `tooling`.
The product requirements define a reading MVP and later analysis phases, but
the repository does not currently promise a stable public release or a
published package.

### Documented MVP interface

The project documents these commands as the initial interface:

```text
tooling okf tree [<bundle>] --depth <n> [--summary] [--json]
tooling okf list [<bundle>] [--type <type>] [--tag <tag>] [--json]
tooling okf show [<bundle>] <concept-id-or-path> [--summary] [--json]
```

These commands cover bundle discovery, structure, concept inventory, and
single-concept reading. Confirm the command behavior in the checkout you are
using before relying on it in automation.

### Planned interface

The following commands belong to later product phases and must not be treated
as available or stable:

```text
tooling okf links [<bundle>] [--broken] [--external] [--json]
tooling okf backlinks [<bundle>] <concept-id-or-path> [--json]
tooling okf props [<bundle>] [--fields type,title,description,tags] [--format table|json|csv]
tooling okf health [<bundle>] [--json] [--profile <name>]
tooling okf validate [<bundle>] [--json]
```

## Installation

Requirements:

- Python 3.11 or newer.
- A checkout of this repository.

From the repository root, install the package in an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Editable installation keeps the installed command linked to the checkout. The
project is currently documented for local source installation; it does not
claim to be published on PyPI or another package index.

## Quickstart

Run the command from the repository root and provide a bundle path explicitly:

```bash
tooling okf tree tooling/bundles --depth 2 --summary
```

The documented human-readable result is a compact directory view with counts,
for example:

```text
<bundle>/
  area-a/  index.md  concepts: 1
  area-b/  index.md  log.md
  area-c/  index.md  concepts: 2
```

Use the other MVP commands to narrow the reading journey:

```bash
# Inventory concepts of one type.
tooling okf list tooling/bundles --type PRD

# Read one concept by its bundle-relative path or concept id.
tooling okf show tooling/bundles prds/PRD\ -\ OKF\ Module
```

The exact counts and concept names depend on the bundle contents. The examples
show the documented command shape, not a guarantee about the current fixture.

## Bundle paths and discovery

Every documented MVP command accepts a bundle as either a relative or absolute
path:

```bash
tooling okf tree ./tooling/bundles --depth 2 --summary
tooling okf tree /absolute/path/to/bundle --depth 2 --summary
```

When `<bundle>` is omitted, the documented discovery order is:

1. The current directory, when it looks like an OKF bundle.
2. An `artifacts/` subdirectory, when present.
3. A `tooling/bundles/` subdirectory when called from this repository root.

If more than one candidate is found, the command should fail with the
candidates and an explicit reference command for each one. Use an explicit
path to remove the ambiguity:

```text
More than one OKF bundle found. Provide the path explicitly:
- artifacts/ -> tooling okf tree artifacts --depth 2 --summary
- tooling/bundles/ -> tooling okf tree tooling/bundles --depth 2 --summary
```

## Output

Human-readable output is the default and is intended for interactive reading.
Use `--json` when a skill or script needs structured output:

```bash
tooling okf tree tooling/bundles --depth 2 --summary --json
tooling okf list tooling/bundles --type PRD --json
tooling okf show tooling/bundles prds/PRD\ -\ OKF\ Module --json
```

The product requirements define JSON as a stable machine-readable interface.
Consumers should still treat the interface as provisional until this local
project declares a stable release. Readable content problems are represented
as objective issues where possible instead of preventing the bundle from being
inventoried.

## Errors and limitations

- The CLI is intended to read bundles; the MVP does not automatically rewrite
  bundle documents.
- Broken links, unknown frontmatter fields, and unknown non-empty types are
  content signals rather than reasons to reject a readable bundle in the MVP.
- An omitted bundle path can fail when discovery is ambiguous.
- An invalid or unreadable path is an execution error and should be corrected
  by providing a readable bundle path.
- The tool is designed to run locally without Obsidian, a database, network
  access, or external services.
- Link analysis, health reporting, property export, and validation are planned
  phases, not part of the documented reading MVP.

## Compatibility

The documented runtime requirement is Python 3.11+. The project is currently
designed for local use from this repository and does not document a separate
operating-system matrix or a published distribution channel.

The CLI should not depend on fixed paths from the repository: callers should
provide the bundle path they want to read. Relative and absolute bundle paths
are both part of the documented interface.

## Repository documentation

The product and architecture knowledge for this tool is stored as OKF content
under [`bundles/`](bundles/). External users should start with this README;
the following documents are primarily for maintainers and contributors:

- [Tooling Overview](bundles/Tooling%20Overview.md)
- [PRD - Python Tooling Library and CLI](bundles/prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](bundles/prds/PRD%20-%20OKF%20Module.md)
- [Prompt - Tooling Architecture Definition](bundles/prompts/Prompt%20-%20Tooling%20Architecture%20Definition.md)

The PRDs describe product intent and roadmap status; they are not a substitute
for verifying the behavior of a particular checkout.

## Contributing and licensing

This checkout does not currently provide a license, contribution guide,
security policy, or support channel in the repository context reviewed for this
README. Those gaps should be resolved before the project is presented as a
public open-source package.

## Design constraints

- Keep the first implementation small and OKF-focused.
- Keep reusable library logic separate from CLI presentation.
- Prefer stable JSON output for skills and automation.
- Do not require fixed paths, Obsidian, network access, databases, or external
  services.
- Treat broken links as health signals, not fatal parsing errors.
