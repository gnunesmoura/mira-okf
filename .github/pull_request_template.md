## Scope

- What user or maintainer problem does this change address?
- What is included, and what is intentionally out of scope?

## Validation

<!-- List the commands and checks run, plus any unavailable checks. -->

- [ ] `python -m unittest discover -s tests`
- [ ] Applicable OKF health, validation, or link checks
- [ ] `git diff --check`

Validation details:

## Documentation impact

- [ ] Documentation added or updated
- [ ] No documentation impact

Explain any command, API, format, workflow, or contributor-guidance changes.

## Compatibility considerations

- Affected public interfaces (CLI, JSON, exit codes, library API, OKF reader):
- Python/platform considerations (Python 3.12+, Linux, Windows best effort,
  macOS out of scope):
- Breaking change or migration guidance needed:

## Checklist

- [ ] The change stays within the local, read-only product boundary.
- [ ] Tests or other validation evidence cover the change.
- [ ] I have not included suspected vulnerability details in this public PR.
