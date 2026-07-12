# Contributing

Thank you for helping improve `tooling`, a local, read-only Python library and
CLI for reading and analyzing OKF bundles.

## Scope and compatibility

The project supports Python 3.12 and newer. Linux is officially supported
when validated; Windows is best effort; macOS is outside the declared scope.
The supported format is OKF Specification 0.1 only.

The CLI and library expose the same capabilities through their appropriate
interfaces. Documented CLI commands and options, JSON fields, exit codes, the
documented Python API, and the OKF reader contract are public compatibility
surfaces. During alpha, breaking changes may occur without a major version;
identify affected interfaces, update documentation, and provide migration
guidance when appropriate.

Keep changes within the local, read-only product boundary. Do not add network
services, authoring or automatic repair, hosted services, or broader
automation without an approved product decision.

## Set up a checkout

Use Python 3.12 or newer and work from the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

The tool does not require Obsidian, a database, network access, or external
services. If you only need to run the source checkout, use the repository's
documented command surface from the root.

## Run tests and validation

Run the full test suite before submitting a change:

```bash
python -m unittest discover -s tests
python -m tooling okf health docs --profile quick --json
python -m tooling okf validate docs --json
python -m tooling okf links docs --broken --json
git diff --check
```

For documentation or bundle changes, preserve Obsidian-compatible Markdown,
keep links valid, and run the applicable repository checks. For OKF bundles,
preserve the required frontmatter, `index.md`, and `log.md` structure and use
the repository's OKF tooling to check bundle health.

## Issues and support

Use the [public issue tracker](https://github.com/gnunesmoura/okf-tooling/issues)
for ordinary bugs, usage help, and feature or improvement requests within the
product scope. Search existing issues first and use the applicable template.
Support is best effort with no SLA; reproducible bugs are useful, but no
response, fix, or feature implementation is promised.

Do not report suspected vulnerabilities in a public issue. Follow
`SECURITY.md` instead.

## Pull requests

Before opening a pull request:

1. Keep the change focused and explain the user-visible outcome.
2. Describe the scope, affected interfaces, and any compatibility impact.
3. Add or update tests when behavior changes; update documentation when the
   command surface, API, format, or workflow changes.
4. Report the validation commands you ran and any unavailable checks.
5. Complete the pull-request template and explain documentation impact,
   migration needs, and platform considerations.

The maintainer is `gnunesmoura`, who is the sole authority for alpha releases
and governance decisions. Contributions can be proposed through the public
repository and may be accepted, revised, or declined based on project scope
and validation evidence.
