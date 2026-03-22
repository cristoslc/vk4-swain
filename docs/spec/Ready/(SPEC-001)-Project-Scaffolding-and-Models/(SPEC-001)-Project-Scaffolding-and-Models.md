---
title: "Project Scaffolding and Models"
artifact: SPEC-001
track: implementable
status: Ready
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: high
type: enhancement
parent-epic: EPIC-001
parent-initiative: INITIATIVE-001
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-001 — Project Scaffolding and Models

## Problem Statement

The vk project needs its foundational structure: pyproject.toml, package layout, and typed domain models that all layers depend on.

## Desired Outcomes

1. A valid pyproject.toml with all dependencies and console script entry point
2. Python package at `src/vk/` with proper `__init__.py` files
3. Typed dataclasses for: Task, Project, Bucket, Comment, Attachment, Label, User, View

## External Behavior

Running `uv sync` installs the package in dev mode. `from vk.models import Task` imports successfully.

## Acceptance Criteria

- [ ] `pyproject.toml` declares name, version, dependencies (click, requests, mcp), dev dependencies (pytest, responses), and console script `vk = "vk.adapters.cli:cli"`
- [ ] Package structure matches seed: `src/vk/{__init__, models, client, config, formatting}.py` and `src/vk/services/__init__.py`
- [ ] Domain dataclasses include: Task, Project, Bucket, Comment, Attachment, Label, View with typed fields matching Vikunja API responses
- [ ] Models use `@dataclass` with `from_dict` classmethod for deserialization and `to_dict` method for serialization

## Scope & Constraints

- Models are data containers only — no business logic
- Fields match Vikunja API naming (snake_case Python equivalents)
- Optional fields use `Optional[T]` with `None` defaults

## Implementation Approach

1. Create pyproject.toml from seed dependencies section
2. Create package directory structure with empty `__init__.py` files
3. Implement domain dataclasses in `models.py`

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Ready | 2026-03-22 | — | Approved for implementation |
