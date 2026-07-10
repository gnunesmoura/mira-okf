---
type: Roadmap
title: Going Open Source Roadmap
description: Roadmap for making okf-tooling a mature public Python package and CLI.
tags:
  - tooling
  - roadmap
  - open-source
  - release
  - python
---

# Going Open Source Roadmap

## Objective

Make `okf-tooling` ready for public adoption as a Python library and CLI,
without expanding the product beyond its OKF reading, analysis, and export
boundary. The repository is already dedicated to the project; the remaining
work is product completion, public project hygiene, release confidence, and
distribution.

## Current Baseline

The project already has its own repository and remote:

- Repository: `github.com/gnunesmoura/okf-tooling`.
- Product scope: OKF bundle reading and analysis.
- Implemented command surface: `tree`, `list`, `links`, `backlinks`, `show`,
  `validate`, and `health`.
- Remaining product feature: `props`, for selected frontmatter property
  export.
- Existing bundle guidance covers the read model, discovery, output, errors,
  validation, health, links, and test strategy.

The project is not yet a public package merely because its repository is
separate. Public readiness requires a stable user contract, a license,
contributor guidance, reproducible installation, and a controlled release
path.

## Product Boundary

The first public release should provide a read-only OKF toolkit that:

- reads Markdown bundles with YAML frontmatter;
- discovers and resolves bundle and concept paths;
- navigates concepts and relationships;
- reports validation and health signals without rewriting content;
- exports selected frontmatter properties through `props`;
- supports concise human output and stable JSON for automation;
- runs locally without Obsidian, databases, network access, or external
  services.

The public release should not promise automatic repair, authoring, a hosted
service, a central schema registry, or a broader repository automation
platform.

## Roadmap

### Phase 1 - Finish the Product Surface

Complete `props` as the final missing feature before release preparation.

Acceptance criteria:

- A user can select a defined set of frontmatter fields.
- Human output has a documented format.
- JSON output follows the existing shared envelope and ordering rules.
- CSV output has documented column and escaping behavior, if CSV remains in
  scope.
- Missing fields have predictable output.
- Unknown frontmatter fields remain available when explicitly selected.
- Empty bundles and bundles with mixed frontmatter are handled explicitly.
- `props` has feature, contract, and regression tests.
- The README documents `props` as available rather than planned.

Non-goals:

- Mutating bundle documents.
- Inventing a new property schema.
- Adding dashboard or database export integrations.

### Phase 2 - Establish the Public Quality Gate

Turn the current command contracts into a release gate that applies to every
supported command.

Acceptance criteria:

- A clean environment can install the package without the source checkout
  being present.
- The installed `tooling` command reaches every supported command path.
- Tests cover successful, empty, ambiguous, invalid, and partially malformed
  bundles.
- Human output and JSON output have representative contract fixtures.
- Exit behavior is documented for success, content issues, and execution
  errors.
- Supported Python versions are tested in continuous integration.
- The built distribution contains the package, CLI entry point, README, and
  license metadata.
- No test or documentation depends on a private absolute path or the parent
  `Mulher de Luxo` repository.

Related contracts:

- [Data Contracts](architecture/Data%20Contracts.md)
- [Output and Errors](architecture/Output%20and%20Errors.md)
- [Test Strategy](architecture/Test%20Strategy.md)
- [Discovery and Resolution](architecture/Discovery%20and%20Resolution.md)

### Phase 3 - Make the Repository Publicly Governable

Add the documents and rules that let users understand their rights and
contributors participate safely.

Acceptance criteria:

- A clear open-source license is present at the repository root.
- `CONTRIBUTING.md` explains setup, tests, documentation, and pull requests.
- `CODE_OF_CONDUCT.md` defines expected community behavior.
- `SECURITY.md` explains how to report vulnerabilities privately.
- Issue and pull request templates guide actionable reports.
- A changelog records user-visible changes.
- The README identifies support channels and the project stability level.
- Maintainer ownership and release approval responsibilities are explicit.

The chosen license, support promise, and compatibility policy are product
decisions and must be settled before the first public release.

### Phase 4 - Prepare the Distribution

Make the Python package metadata and release artifacts suitable for a public
package index.

Acceptance criteria:

- The final package name and CLI command name are chosen and checked for
  conflicts.
- `pyproject.toml` contains complete public metadata and project URLs.
- The README renders correctly as the package description.
- Source distribution and wheel can both be built reproducibly.
- Package contents are inspected before upload.
- The package does not include private fixtures, internal prompts, or
  repository-specific assumptions.
- Versioning follows a documented compatibility policy.

The package name, import name, command name, and repository name may differ,
but their relationship must be documented to prevent installation confusion.

### Phase 5 - Validate a Release Candidate

Publish a release candidate to TestPyPI or an equivalent isolated package
index and test it as an external user.

Acceptance criteria:

- A clean environment installs the candidate from the package index.
- The quickstart works without cloning the source repository.
- All supported commands execute against an independently created fixture.
- JSON and CSV consumers can use the documented output contract.
- Installation and upgrade behavior are verified.
- Release notes identify known limitations and compatibility expectations.
- Any issue found in the candidate is fixed before the production release.

### Phase 6 - Publish the First Public Release

Publish the first stable-enough release only after the candidate gate passes.

The release sequence should be:

1. Merge the release changes into the protected default branch.
2. Run the complete quality workflow.
3. Create a version tag and release notes.
4. Build source and wheel distributions from the tagged commit.
5. Publish through a protected CI release workflow.
6. Verify installation from the public package index.
7. Announce the release with supported scope, examples, and known limits.

The publishing workflow should use short-lived, repository-scoped identity
instead of a long-lived secret where the package index supports it.

### Phase 7 - Operate the Public Project

Treat the first release as the beginning of maintenance, not the end of the
roadmap.

Acceptance criteria:

- Issues receive a predictable triage response.
- Security reports have a private handling path.
- Releases have a repeatable cadence or explicit release policy.
- Dependency and supported-Python updates are reviewed regularly.
- Documentation examples are tested or periodically verified.
- Breaking changes are announced before release.
- Usage feedback informs the next feature instead of speculative expansion.

## Release Gates

Do not publish the first public release if any of these are false:

- `props` is complete or intentionally removed from the release scope.
- The package works from a clean installation.
- The README describes the actual command surface.
- The repository has a license.
- Contributors know how to set up, test, and submit changes.
- Security reports have a documented private channel.
- The release can be reproduced from a tag.
- The package can be installed and used without the original repository.

## Immediate Sequence

1. Define and implement the `props` contract.
2. Update the README and bundle contracts for the completed command surface.
3. Add release-quality fixtures and clean-install verification.
4. Decide the license, package name, stability level, and compatibility policy.
5. Add governance and security documents.
6. Complete public package metadata and build verification.
7. Run a TestPyPI release candidate.
8. Publish the first public release through protected automation.
9. Establish post-release maintenance and support practices.

## Relations

- [Tooling Overview](Tooling%20Overview.md)
- [Tooling Roadmap](Tooling%20Roadmap.md)
- [PRD - Python Tooling Library and CLI](prds/PRD%20-%20Python%20Tooling%20Library%20and%20CLI.md)
- [PRD - OKF Health](prds/PRD%20-%20OKF%20Health.md)
- [PRD - OKF Validation](prds/PRD%20-%20OKF%20Validation.md)
- [Architecture Overview](architecture/Architecture%20Overview.md)
- [Test Strategy](architecture/Test%20Strategy.md)
