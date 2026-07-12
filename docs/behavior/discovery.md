---
type: Behavior
title: Discovery
description: Resolve explicit and automatically discovered OKF bundle paths.
tags: [behavior, discovery]
---

# Discovery

An explicit relative or absolute path is resolved directly. Generic automatic
discovery recursively searches the current directory for directories that look
like OKF bundle roots, but it can be ambiguous for this nested documentation
tree. Use the explicit `docs/` path for commands run from this checkout.
Multiple candidates are fatal and the error lists explicit commands for
disambiguation.

Concept targets resolve by id or bundle-relative path, with or without `.md`.
