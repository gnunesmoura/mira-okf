---
type: Contract
title: Output and errors
description: Explain human output, JSON responses, issues, and exit codes.
tags: [behavior, errors, json]
---

# Output and errors

Human-readable output is the default; `--json` is intended for scripts. A
readable bundle with content issues succeeds with exit code `0` and reports
those issues. An unreadable, missing, or ambiguous bundle is a fatal error with
exit code `1` and an `error` object in the JSON envelope.
