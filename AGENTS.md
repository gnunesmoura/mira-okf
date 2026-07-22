# AGENTS

This file is the public operating guide for agents using the `mira-okf` CLI.

## Purpose

- Use `mira-okf` commands to inspect and validate OKF bundles.
- Keep CLI usage examples aligned with the public command surface.
- Report behavior and documentation changes with reproducible evidence.

## Supported workflow

Run commands from the repository root and provide an explicit bundle path when
the checkout contains more than one OKF bundle. The public documentation bundle
is `docs/`:

```bash
python -m mira_okf tree docs --depth 2 --summary
python -m mira_okf list docs --json
python -m mira_okf show docs <concept-id-or-path>
python -m mira_okf links docs --broken --json
python -m mira_okf validate docs --json
python -m mira_okf health docs --profile quick --json
```

Generic automatic discovery can be ambiguous for this nested documentation
tree. Use the explicit `docs/` path in repository commands and examples.

## Working rules

- Keep the CLI and library read-only; do not add authoring, repair, network,
  database, or hosted-service behavior without an approved product change.
- Keep delegated tools inside the repository root and the explicitly requested
  paths. Do not broaden permissions or target paths outside the repository
  unless explicitly authorized.
- Keep public command names, options, JSON envelopes, exit codes, and OKF
  semantics stable unless the change explicitly updates the contract.
- Prefer the smallest relevant validation command after a change:

  ```bash
  python -m unittest discover -s tests
  python -m mira_okf validate docs --json
  python -m mira_okf links docs --broken --json
  git diff --check
  ```

- Preserve unrelated work and do not edit generated files manually.
- Keep Markdown portable and use bundle-relative links for documents inside
  `docs/`.
