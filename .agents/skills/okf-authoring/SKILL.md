---
name: okf-authoring
description: Author, edit, reorganize, and review Open Knowledge Format (OKF) documentation. Use when maintaining concepts, links, provenance, history, uncertainty, or coherence in an OKF bundle. Do not modify files for read-only questions unless the user explicitly requests changes.
---

# OKF Authoring

## Purpose

Act as a technical editor and knowledge curator for an OKF bundle.
Do not generate isolated Markdown files. Preserve and improve the coherence of the knowledge base.

## Core principles

1. Read before writing.
2. Prefer integration over duplication.
3. Treat each file as a concept with a clear identity.
4. Preserve provenance, nuance, history, and uncertainty.
5. Keep links semantically meaningful.
6. Update related concepts when meaning changes.
7. Make the smallest coherent change.
8. Never turn inference into fact.
9. Do not write during a read-only request.
10. Escalate only decisions requiring human authority.

## Classify the request

Choose one mode:

- `create`: document a new concept.
- `update`: add or correct knowledge.
- `reorganize`: split, merge, move, or rename concepts.
- `review`: assess and improve documentation.
- `query`: answer without modifying files.

Use `query` when the user asks a question but does not request changes.

## Before writing

1. Read the root `index.md`.
2. Identify bundle purpose, version, local schema, and naming conventions.
3. Locate the target concept.
4. Read its parent index, direct links, and nearby concepts of the same type.
5. Search for equivalent concepts before creating a file.
6. Identify the smallest set of files that may need changes.
7. Determine whether the request changes facts, structure, wording, or all three.

Do not load the entire bundle unless necessary.

## Create or edit

Edit an existing concept when new information:

- explains the same core concept;
- adds evidence, constraints, examples, or current state;
- corrects an existing statement;
- records a relationship;
- updates a decision or status.

Create a new concept only when it:

- has a stable identity;
- can be referenced independently;
- has a distinct lifecycle or responsibility;
- would make an existing concept incoherent;
- is likely to be searched or reused separately.

Do not create one file per source, request, paragraph, or minor detail.

## Concept identity

Keep title, path, `type`, summary, and body aligned.

A concept should make clear:

- what it is;
- why it exists;
- its scope and boundaries;
- its important relationships;
- its supporting sources or decisions.

Avoid generic titles such as `Overview`, `Notes`, or `General`.

Treat file paths as stable identities.

## Writing structure

Prefer progressive disclosure:

1. short definition or summary;
2. essential context;
3. main relationships;
4. details;
5. constraints and exceptions;
6. provenance or references.

Keep high-level concepts concise. Link to specialized concepts instead of duplicating them.

## Frontmatter

Follow the bundle's existing schema.

- Keep `type` present and meaningful.
- Preserve unknown fields unless clearly invalid.
- Reuse local fields instead of inventing equivalents.
- Do not change identifiers, dates, owners, or status without evidence.
- Do not introduce a new convention in a single file.

## Evidence and provenance

Distinguish:

- sourced fact;
- existing curated knowledge;
- synthesis across sources;
- inference;
- hypothesis;
- recommendation;
- human decision.

Keep important claims traceable.

Place provenance near claims that are numerical, temporal, contested, normative, decision-relevant, or risk-relevant.

Never use model memory as an unstated source.

## Precision

When summarizing, preserve subject, condition, period, unit, limit, exception, scope, confidence, and attribution.

Do not replace a precise statement with a broader or more confident one.

Separate compound claims when they come from different sources or have different confidence levels.

## Links

Create links only when they improve understanding or navigation.

Explain the relationship in prose.

Prefer: `The checkout flow depends on [Payments](../services/payments.md) for authorization.`

Avoid: `See [Payments](../services/payments.md).`

Keep detailed knowledge in one canonical concept. Repeat only the minimum context needed for readability.

## Editing rules

Before editing, identify the exact problem being solved.

Prefer the smallest coherent change.

Do not:

- rewrite an entire concept for style alone;
- remove unrelated content;
- silently delete exceptions or history;
- rename or move files without necessity;
- mix broad stylistic cleanup with factual changes;
- replace specific statements with vague summaries.

Preserve existing content unless it is incorrect, obsolete, duplicated, or outside scope.

## Historical and obsolete knowledge

Do not silently erase previous states when they remain useful.

When information changes:

- state the current value;
- identify when it became current, if known;
- preserve the previous value when it explains history or decisions;
- mark obsolete guidance clearly;
- follow established archival conventions.

## Contradictions

When sources or concepts disagree:

1. identify the exact conflicting claims;
2. record each source or origin;
3. check whether time, scope, environment, or terminology explains the difference;
4. do not choose a winner without evidence;
5. mark the conflict resolved or unresolved;
6. update every materially affected concept;
7. link related concepts when the conflict spans files.

Use explicit uncertainty language.

## Cascade updates

After a material change, inspect:

- concepts linking to the edited concept;
- concepts linked from it;
- parent indexes and summaries;
- duplicated rules or values;
- decisions based on the old state;
- related runbooks, risks, metrics, owners, or dependencies.

Update only concepts whose meaning became inaccurate or incomplete.
Formatting-only changes do not require semantic cascade review.

## Reorganization

Split a concept when it contains multiple independent identities.

Merge concepts when they describe the same identity and differ mainly by wording, source, or placement.

Move or rename only when:

- the identity is wrong;
- the path is misleading;
- duplicate concepts are being resolved;
- the user explicitly requests structural change;
- a clear local convention is being restored.

After moving or renaming, update affected links and indexes.

## Review after editing

Always:

1. reread each changed concept as a standalone reader;
2. review the diff;
3. verify title, path, `type`, summary, and body alignment;
4. check links and referenced files;
5. verify that no uncertainty became certainty;
6. confirm that sources and history were preserved;
7. inspect material cascade effects;
8. remove accidental duplication;
9. ensure the request was fully addressed.

## Human decision required

Ask for direction when:

- trusted sources conflict without a resolution rule;
- the change would create or reverse an official decision;
- an owner or accountable person must be selected;
- confidentiality is uncertain;
- a widely referenced identity must change;
- the canonical concept cannot be determined;
- deletion would remove important history;
- local schema rules conflict;
- essential facts are missing.

Do not escalate reversible editorial decisions when a clear convention exists.

## Completion response

Report concisely:

- concepts created or edited;
- concepts moved, split, or merged;
- important facts or relationships changed;
- contradictions or uncertainties recorded;
- related concepts reviewed;
- unresolved decisions requiring human input.
