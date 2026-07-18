---
type: Guide
title: Getting started
description: Install MIRA OKF and inspect an OKF bundle.
tags: [guide, installation, okf]
---

# Getting started

## Install

Use Python 3.12 or newer. From a local checkout, create and activate a virtual
environment, then install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Always use `python -m pip` after activating the environment so `pip` installs
into the same Python environment that provides `mira-okf`. Confirm the command
is available before inspecting a bundle:

```bash
mira-okf --help
```

## Inspect a bundle

Give commands a relative or absolute bundle path. This checkout uses `docs/`:

```bash
mira-okf tree docs --depth 2 --summary
mira-okf list docs --json
mira-okf validate docs --json
```

Generic automatic discovery searches recursively and can be ambiguous for this
nested documentation tree. Use the explicit `docs/` path for commands run from
this checkout. See [discovery](behavior/discovery.md).

## Read a concept

Concepts can be selected by bundle-relative path or concept id:

```bash
mira-okf show docs behavior/overview
```

The CLI is read-only and does not require Obsidian, a database, network access,
or an external service.
