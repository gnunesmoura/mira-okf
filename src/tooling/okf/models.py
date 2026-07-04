from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Issue:
    code: str
    message: str
    severity: str = "warning"
    path: str | None = None
    line: int | None = None
    field: str | None = None
    suggestion: str | None = None
    fatal: bool = False


@dataclass(slots=True)
class Concept:
    concept_id: str
    path: Path
    relative_path: str
    directory: str
    filename: str
    type: str | None = None
    title: str | None = None
    description: str | None = None
    resource: str | None = None
    tags: list[str] = field(default_factory=list)
    timestamp: str | None = None
    body: str = ""
    frontmatter: dict[str, Any] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)


@dataclass(slots=True)
class Directory:
    path: str
    absolute_path: Path
    name: str
    depth: int
    has_index: bool = False
    has_log: bool = False
    concept_count: int = 0
    directory_count: int = 0
    children: list["Directory"] = field(default_factory=list)
    concepts: list[Concept] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)


@dataclass(slots=True)
class Link:
    source_concept_id: str
    source_path: str
    raw: str
    kind: str
    target: str
    resolved: bool = False
    broken: bool = False
    external: bool = False
    target_concept_id: str | None = None
    target_path: str | None = None


@dataclass(slots=True)
class Bundle:
    root_path: Path
    relative_path: str
    source_kind: str
    source_path: Path
    concepts: list[Concept] = field(default_factory=list)
    directories: list[Directory] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    okf_version: str | None = None
    has_root_index: bool = False
    has_root_log: bool = False
    root_index_issues: list[Issue] = field(default_factory=list)
    root_log_issues: list[Issue] = field(default_factory=list)

