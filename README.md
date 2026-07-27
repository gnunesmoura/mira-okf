# MIRA OKF

MIRA OKF is a local tool for exploring and checking Open Knowledge Format
(OKF) bundles. It reads Markdown-based knowledge bases without changing them,
so you can browse concepts, inspect links, project metadata, validate
structure, and review bundle health from the terminal.

MIRA stands for **Markdown Indexing, Retrieval & Analysis**. The `OKF` suffix
makes the supported format explicit.

## Try it

```bash
mira-okf tree path/to/bundle --depth 2 --summary
mira-okf show path/to/bundle concept-id
mira-okf validate path/to/bundle --json
```

The CLI is read-only and works locally: it does not require Obsidian, a
database, a network connection, or a hosted service.

The full interface is documented in [`docs/`](docs/).

The repository's `docs/` directory is itself an OKF bundle, so it can be used
as a local example when trying the commands above.

## Install

Python 3.12 or newer is required. To install the CLI for your user account so
it is available in later terminals:

```bash
python3 -m pip install --user --upgrade "git+https://github.com/gnunesmoura/mira-okf.git"
mira-okf --version
```

If you already cloned this repository, install the checkout instead:

```bash
python3 -m pip install --user --upgrade .
mira-okf --version
```

On Windows, use `py -m pip` instead of `python3 -m pip`. If `mira-okf` is not
found after a user install, add Python's user `Scripts` directory to `PATH`.

## Quick start

With a built wheel or source distribution, an isolated environment is also
supported:

```bash
python3 -m venv /tmp/mira-okf-venv
/tmp/mira-okf-venv/bin/python -m pip install /path/to/mira_okf-0.0.1a4-py3-none-any.whl
/tmp/mira-okf-venv/bin/mira-okf tree /path/to/bundle --depth 2 --summary
```

From this checkout, the public documentation bundle is `docs/`:

```bash
python -m mira_okf tree docs --depth 2 --summary
python -m mira_okf validate docs --json
```

Generic automatic discovery can be ambiguous for this nested documentation
tree, so use the explicit `docs/` path for commands run from this checkout.

## Compatibility and support

The project is alpha, supports OKF Specification 0.1, and officially supports
validated Linux environments. Windows is best effort and macOS is outside the
declared scope. Documented commands, JSON envelopes, exit codes, and the OKF
reader behavior are public compatibility surfaces.

For bugs, usage help, and in-scope feature requests, use the [public issue
tracker](https://github.com/gnunesmoura/mira-okf/issues). Support is best
effort with no SLA. See [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md).

This project is available under the [MIT License](LICENSE).
