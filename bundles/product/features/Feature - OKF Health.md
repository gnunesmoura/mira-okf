---
type: Feature
title: Feature - OKF Health
description: Compact read-only bundle status view with explicit health profiles and opt-in quality groups.
tags:
  - tooling
  - okf
  - health
  - cli
---

# Feature - OKF Health

## Objective

Help people, scripts, and agents quickly understand whether an OKF bundle is usable with a short default health view, while keeping broader quality checks opt-in and explicitly declared.

## Scope

- `tooling okf health [<bundle>] [--json] [--profile <name>]` reports a compact status view for one resolved OKF bundle.
- The command is read-only and uses the shared bundle discovery rules.
- Health uses named profiles, with `quick` as the default and `full` as the broader audit profile.
- The default `quick` profile focuses on essential structural signals and keeps optional quality checks out of the status result unless they are explicitly selected.
- `quick` includes inventory, reserved-file, link, and connectivity signals.
- `full` adds index coverage, logs, metadata, and citations.
- Health summarizes existing validation outcome and issue counts without replacing `tooling okf validate`.
- Health reports inventory shape, reserved file presence, link health, and connectivity in the default profile.
- Health reports optional quality groups only when selected.
- Health ignores text inside fenced code blocks and inline code spans when evaluating health signals, so examples and snippets do not create false problems.
- Raw content display remains unchanged.
- JSON output declares which profile was used and which rule groups were evaluated versus ignored.
- Human output starts with the bundle path, profile, and compact status summary, then expands only the selected health groups in deterministic path-first or name-first order.
- JSON output uses the shared envelope and places the health report in `data`.
- Top-level `issues` remains available for tolerated read, validation, or health collection issues.
- Command execution succeeds for readable bundles even when health signals are poor.

## Out of Scope

- Writing, repairing, formatting, or auto-fixing bundle files.
- Reimplementing validation rules or changing validation pass/fail semantics.
- Failing command execution solely because of ignored optional groups, broken links, missing optional metadata, missing `index.md`, stale logs, orphan concepts, or missing citations.
- Opaque scoring, letter grades, trend reporting, or historical comparisons.
- Deciding whether external claims require citations beyond simple detectable citation signals.
- Fetching external URLs or verifying citation targets.
- Adding new OKF folder conventions.
- Property export or tabular frontmatter projection.

## User Flow

1. A user runs `tooling okf health` inside a bundle or provides an explicit bundle path.
2. The CLI resolves the bundle using shared discovery.
3. The CLI reads the bundle and summarizes the selected profile's validation, inventory, reserved file, link, index, log, metadata, citation, and connectivity signals.
4. The CLI prints a compact human status view or emits the shared JSON envelope, including the evaluated and ignored rule groups.
5. If the bundle cannot be resolved or read at all, the CLI returns the shared failure envelope or human error.

## Acceptance Criteria

- `tooling okf health <bundle>` prints a compact health report for the resolved bundle.
- `tooling okf health` uses shared automatic bundle discovery when `<bundle>` is omitted.
- `tooling okf health --profile quick` uses the minimum default rule set.
- When discovery finds more than one bundle candidate, the command fails deterministically and lists the candidates.
- A readable bundle with validation errors still produces a health report and surfaces validation status and counts.
- The health report does not change validation pass/fail behavior.
- Human output includes the resolved bundle path and profile before signal details.
- Human output groups only the selected signal groups under stable, concise labels.
- JSON output uses `{ ok, command, bundle, data, issues }`.
- JSON output sets `command` to `okf.health`.
- JSON output places health summary data in `data`.
- JSON output declares the used profile and the evaluated versus ignored rule groups.
- The default `quick` profile includes only essential structural signals and does not surface optional groups as attention by default.
- Broader profiles can include index, log, metadata, and citation groups when explicitly requested.
- Inventory, reserved file, link, and connectivity signals are available in the default profile.
- Optional groups are opt-in and do not affect the status result when they are ignored.
- Repeated runs against the same bundle state produce the same report order and output shape.

## Minimum Tests

- Reports health for a readable bundle with no validation issues.
- Reports health for a readable bundle with validation issues without failing command execution.
- Reports the default `quick` profile as the minimum status view.
- Reports the selected profile and the evaluated versus ignored rule groups in JSON.
- Fails deterministically when bundle discovery is ambiguous.
- Treats missing optional groups as ignored rather than attention when they are not part of the selected profile.
- Reports the selected profile's inventory, reserved file, link, and connectivity signals.
- Reports broader profile coverage for index, log, metadata, and citation groups only when selected.
- Ignores content inside fenced code blocks and inline code spans when evaluating health signals.
- Leaves raw concept content unchanged for `tooling okf show`.
- Emits deterministic human output.
- Emits stable JSON with `command: "okf.health"`, health data, and top-level issues.

## Relations

- [Tooling Roadmap](../Tooling%20Roadmap.md)
- [Discovery and Resolution](../architecture/Discovery%20and%20Resolution.md)
- [Data Contracts](../architecture/Data%20Contracts.md)
- [Command Flows](../architecture/Command%20Flows.md)
- [Output and Errors](../architecture/Output%20and%20Errors.md)
- [Validation Report Contract](../architecture/Validation%20Report%20Contract.md)
- [Health Report Contract](../architecture/Health%20Report%20Contract.md)
- [Test Strategy](../architecture/Test%20Strategy.md)
- [Feature - OKF Validation](Feature%20-%20OKF%20Validation.md)
- [Feature - OKF Links](Feature%20-%20OKF%20Links.md)
- [Feature - OKF Backlinks](Feature%20-%20OKF%20Backlinks.md)
- [Open Knowledge Format Specification](../references/Open%20Knowledge%20Format%20Specification.md)
