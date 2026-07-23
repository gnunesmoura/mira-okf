# Changelog

This project follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

### Added

- `mira-okf lint` command for read-only markdown formatting checks via
  PyMarkdown, with `.markdownlint.json`/`.markdownlint.yaml`/`.yml` config
  discovery, root-only `ignores`, and an OKF default profile. (CHANGE-038)
- `mira-okf health` and `mira-okf validate` include `data.lint` findings when
  the optional `lint` extra is installed; degrade gracefully with an
  informational `OKF_LINT_UNAVAILABLE` issue otherwise. (CHANGE-038)

### Changed

- `mira-okf` resolves canonical bundle-root links (leading `/`) consistently
  across supported bundle invocation contexts (absolute, relative, isolated,
  nested) while preserving non-fatal broken-link reporting. Ordinary relative
  links remain source-relative. (CHANGE-031)

### Fixed

### Deprecated

### Removed

### Security

### Breaking Changes

The `okf` grouping token has been removed from CLI invocations. This is an
intentional pre-1.0 breaking change that shortens the public command surface.

### Migration

Replace `mira-okf okf <command>` with `mira-okf <command>` mechanically; all
following arguments and result handling remain unchanged.

## [0.0.1a3] - 2026-07-22

### Added

- `mira-okf show` can read explicit reserved and generic Markdown files while
  preserving concept resolution and the shared JSON envelope.
