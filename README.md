# Tooling

`tooling` is a local Python library and CLI for reusable repository tools.

The first supported domain is OKF: reading, navigating, validating, and reporting on OKF bundles made of Markdown files with YAML frontmatter.

## Status

This package is intentionally local to this repository for now. It should become a standalone library or CLI only after the API, command behavior, JSON output, and test coverage are stable enough to justify extraction.

## Installation From Source

Install the project in editable mode from the repository root:

```bash
python -m pip install -e .
```

This makes the `tooling` command available in your active environment while keeping the package linked to the local source code.

## Planned CLI

```bash
tooling okf tree [<bundle>] --depth <n> [--summary] [--json]
tooling okf list [<bundle>] [--type <type>] [--tag <tag>] [--offset <n>] [--limit <n>] [--json]
tooling okf show [<bundle>] <concept-id-or-path> [--summary] [--json]
tooling okf links [<bundle>] [--broken] [--external] [--json]
tooling okf backlinks [<bundle>] <concept-id-or-path> [--json]
tooling okf props [<bundle>] [--fields type,title,description,tags] [--format table|json|csv]
tooling okf health [<bundle>] [--json]
tooling okf validate [<bundle>] [--json]
```

`<bundle>` may be a relative or absolute path. If omitted, the CLI should try to discover an OKF bundle in the current working directory. If multiple candidates are found, it should fail and print a reference command for each candidate.

## Knowledge Bundle

The product and architecture knowledge for this tool lives in:

```text
tooling/bundles/
```

Start with:

- [Tooling Overview](bundles/Tooling%20Overview.md)
- [PRD - Python Tooling Library and CLI](bundles/prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Module](bundles/prds/PRD%20-%20OKF%20Module.md)
- [Prompt - Tooling Architecture Definition](bundles/prompts/Prompt%20-%20Tooling%20Architecture%20Definition.md)

## Intended Structure

```text
tooling/
  README.md
  bundles/
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

## Design Constraints

- Keep the first implementation small and OKF-focused.
- Keep library logic separate from CLI presentation.
- Support stable JSON output for skills and automation.
- Do not depend on fixed paths from this repository.
- Do not require Obsidian, network access, databases, or external services.
- Treat broken links as health signals, not fatal parsing errors.
