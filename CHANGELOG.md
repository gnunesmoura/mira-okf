# Changelog

This project follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

### Added

### Changed

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
