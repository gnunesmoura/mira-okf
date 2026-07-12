---
type: Contract
title: Data contracts
description: Describe the observable command data and JSON envelope.
tags: [behavior, contract, json]
---

# Data contracts

Successful JSON responses use the top-level fields `ok`, `command`, `bundle`,
`data`, and `issues`. Fatal responses set `ok` to `false` and add an `error`
object. Payload data is command-specific: inventories contain concepts, link
reports contain link records, and validation or health contain grouped reports.
Ordering is deterministic for repeatable automation.
