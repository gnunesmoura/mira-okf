---
type: Feature
title: Feature - OKF Health
description: Compact read-only bundle status view that summarizes OKF inventory, conformance, discoverability, and relationship quality signals.
tags:
  - tooling
  - okf
  - health
  - cli
---

# Feature - OKF Health

## Objective

Help people, scripts, and skills quickly understand whether an OKF bundle is usable, discoverable, and well connected without opening multiple command outputs or treating soft quality gaps as validation failures.

## Scope

- `tooling okf health [<bundle>] [--json]` reports a compact status view for one resolved OKF bundle.
- The command is read-only and uses the shared bundle discovery rules.
- Health summarizes existing validation outcome and issue counts without replacing `tooling okf validate`.
- Health reports inventory shape, including concept count, directory count, reserved file count, and concept type distribution.
- Health reports reserved file presence and conformance for present `index.md` and `log.md` files.
- Health reports broken internal link counts while keeping broken links tolerated and non-fatal.
- Health reports index coverage and discoverability signals, including directories with `index.md` and visible index links to bundle contents where detectable.
- Health reports log freshness and ordering signals for present `log.md` files.
- Health reports optional metadata coverage for recommended fields such as `title`, `description`, `resource`, `tags`, and `timestamp`.
- Health reports citation presence where detectable, including concepts with a `# Citations` section and concepts with external links but no detectable citation section.
- Health reports link graph connectivity signals, including orphan concepts with no inbound or outbound internal links.
- Human output starts with the bundle path and a compact status summary, then groups health signals in deterministic path-first or name-first order.
- JSON output uses the shared envelope and places the health report in `data`.
- Top-level `issues` remains available for tolerated read, validation, or health collection issues.
- Command execution succeeds for readable bundles even when health signals are poor.

## Out of Scope

- Writing, repairing, formatting, or auto-fixing bundle files.
- Reimplementing validation rules or changing validation pass/fail semantics.
- Failing command execution solely because of broken links, missing optional metadata, missing `index.md`, stale logs, orphan concepts, or missing citations.
- Opaque scoring, letter grades, trend reporting, or historical comparisons.
- Deciding whether external claims require citations beyond simple detectable citation signals.
- Fetching external URLs or verifying citation targets.
- Adding new OKF folder conventions.
- Property export or tabular frontmatter projection.

## User Flow

1. A user runs `tooling okf health` inside a bundle or provides an explicit bundle path.
2. The CLI resolves the bundle using shared discovery.
3. The CLI reads the bundle and summarizes validation, inventory, reserved file, link, index, log, metadata, citation, and connectivity signals.
4. The CLI prints a compact human status view or emits the shared JSON envelope.
5. If the bundle cannot be resolved or read at all, the CLI returns the shared failure envelope or human error.

## Acceptance Criteria

- `tooling okf health <bundle>` prints a compact health report for the resolved bundle.
- `tooling okf health` uses shared automatic bundle discovery when `<bundle>` is omitted.
- When discovery finds more than one bundle candidate, the command fails deterministically and lists the candidates.
- A readable bundle with validation errors still produces a health report and surfaces validation status and counts.
- The health report does not change validation pass/fail behavior.
- Human output includes the resolved bundle path before signal details.
- Human output groups signals under stable, concise labels.
- JSON output uses `{ ok, command, bundle, data, issues }`.
- JSON output sets `command` to `okf.health`.
- JSON output places health summary data in `data`.
- Inventory signals include counts for concepts, directories, reserved files, and concept types.
- Reserved file signals distinguish missing optional `index.md` files from malformed present reserved files.
- Link signals count resolved internal links, broken internal links, and external links when detectable.
- Broken internal links affect health signals but do not fail command execution.
- Index signals report directory index coverage and detectable unlisted contents without requiring every directory to have an `index.md`.
- Log signals report newest log date, malformed date headings, and newest-first ordering issues when present.
- Optional metadata signals report coverage counts for `title`, `description`, `resource`, `tags`, and `timestamp` without treating missing fields as fatal.
- Citation signals report detectable `# Citations` sections and concepts with external links but no detectable citation section.
- Connectivity signals report concepts with no inbound or outbound internal links.
- Repeated runs against the same bundle state produce the same report order and output shape.

## Minimum Tests

- Reports health for a readable bundle with no validation issues.
- Reports health for a readable bundle with validation issues without failing command execution.
- Fails deterministically when bundle discovery is ambiguous.
- Includes inventory counts for concepts, directories, reserved files, and concept types.
- Reports present malformed `index.md` and `log.md` files through validation status and reserved file signals.
- Treats missing `index.md` as optional while still reporting index coverage.
- Counts broken internal links without failing the command.
- Reports optional metadata coverage for recommended frontmatter fields.
- Reports log freshness and newest-first ordering signals for present logs.
- Reports detectable citation section coverage and external-link-without-citation signals.
- Reports orphan concepts from the internal link graph.
- Emits deterministic human output.
- Emits stable JSON with `command: "okf.health"`, health data, and top-level issues.

## Relations

- [Tooling Roadmap](../Tooling%20Roadmap.md)
- [PRD - OKF Module](../prds/PRD%20-%20OKF%20Module.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Validation Report Contract](../architecture/Validation%20Report%20Contract.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Feature - OKF Validation](Feature%20-%20OKF%20Validation.md)
- [Feature - OKF Links](Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](Feature%20-%20OKF%20Backlinks.md)
