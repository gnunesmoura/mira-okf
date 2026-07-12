---
type: Guide
title: Getting started
description: Install MIRA OKF and inspect an OKF bundle.
tags: [guide, installation, okf]
---

# Getting started

## Install

Use Python 3.12 or newer and install a built wheel or source distribution in
an isolated environment:

```bash
python3 -m venv /tmp/mira-okf-venv
/tmp/mira-okf-venv/bin/python -m pip install /path/to/mira_okf-0.0.1a1-py3-none-any.whl
```

## Inspect a bundle

Give commands a relative or absolute bundle path. This checkout uses `docs/`:

```bash
mira-okf okf tree docs --depth 2 --summary
mira-okf okf list docs --json
mira-okf okf validate docs --json
```

Generic automatic discovery searches recursively and can be ambiguous for this
nested documentation tree. Use the explicit `docs/` path for commands run from
this checkout. See [discovery](behavior/discovery.md).

## Read a concept

Concepts can be selected by bundle-relative path or concept id:

```bash
mira-okf okf show docs behavior/overview
```

The CLI is read-only and does not require Obsidian, a database, network access,
or an external service.
