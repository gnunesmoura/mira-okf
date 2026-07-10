# Tooling

Knowledge bundle for the local Python library and CLI `tooling`.

## Areas

- [Product](product/) - Durable product intent and user-visible capabilities.
- [Product Features](product/features/) - Stable capabilities offered by the CLI and library.
- [Architecture](architecture/) - Reusable technical decisions and contracts.
- [References](references/) - Governing specifications and external constraints.
- [Spec-Driven Development](spec-driven-development/) - SDD rules, templates, and change packages.

## Area roles

| Area | Authority | Use it for |
| --- | --- | --- |
| [Product](product/) | Durable product intent | Why the product exists and what it offers |
| [Product Features](product/features/) | Durable observable behavior | What users should be able to see and do |
| [Architecture](architecture/) | Reusable technical contracts | Boundaries, invariants, interfaces, and decisions |
| [References](references/) | Governing specifications | OKF rules and external constraints |
| [SDD Changes](spec-driven-development/changes/) | Current change scope and lifecycle | Specs, plans, tasks, tests, contracts, and evidence |
| `log.md` files | Historical record | What changed; not current authority |

## Authority and conflict resolution

Use this order when sources disagree:

1. The local OKF specification and repository policy govern bundle structure.
2. Product concepts govern durable intent and capabilities.
3. Product feature concepts govern observable behavior.
4. Architecture concepts govern reusable technical boundaries and contracts.
5. The applicable SDD change package governs the approved scope and execution
   state of that change.
6. Source code and tests show implemented behavior and validation evidence.

If two sources conflict, record the discrepancy in the applicable change
package or update the higher-level concept deliberately. Do not resolve the
conflict silently.

## SDD lifecycle

Change packages use:

`draft -> specified -> planned -> ready -> in_progress -> implemented -> validated`

Advance a status only when the corresponding evidence is recorded. An absent
change package cannot be treated as a source of current change status.

## Documents

- [Tooling Overview](Tooling%20Overview.md) - Scope and principles for `tooling`.
- [Tooling Roadmap](Tooling%20Roadmap.md) - Product sequence and current focus.
- [Going Open Source Roadmap](Going%20Open%20Source%20Roadmap.md) - Release and governance direction.
- [Tooling Product](product/Product%20Overview.md) - Durable product definition.
- [Open Knowledge Format Specification](references/Open%20Knowledge%20Format%20Specification.md) - Local OKF reference.
