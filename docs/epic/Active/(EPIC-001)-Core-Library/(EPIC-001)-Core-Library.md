---
title: "Core Library"
artifact: EPIC-001
track: container
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: high
success-criteria:
  - "Domain models cover all Vikunja resource types used by the CLI"
  - "HTTP client handles auth, pagination, error mapping, and multipart uploads"
  - "Config resolves tokens from flags, env vars, and config files"
  - "Core services implement all CRUD operations for tasks, projects, buckets, comments, attachments, labels, and search"
depends-on-artifacts: []
addresses: []
evidence-pool: "task-platform-comparison@62bd18a"
---

# EPIC-001 — Core Library

## Goal / Objective

Build the foundation layers of vk: domain models, HTTP client, config/auth, and all core services. This is the port layer that adapters (CLI, MCP) depend on.

## Desired Outcomes

1. Typed dataclasses for all Vikunja resource types
2. A stateless HTTP client that mirrors the Vikunja Swagger spec
3. Config resolution chain: flags → env vars → local dotfile → user config
4. Service classes for tasks, projects, buckets, comments, attachments, labels, search, and auth

## Scope Boundaries

**In scope:** `src/vk/` — models.py, client.py, config.py, services/*.py, __init__.py

**Out of scope:** Adapters (CLI, MCP), formatting, tests (separate specs)

## Child Specs

| Spec | Title | Status |
|------|-------|--------|
| SPEC-001 | Project Scaffolding and Models | Ready |
| SPEC-002 | Vikunja HTTP Client | Ready |
| SPEC-003 | Config and Auth | Ready |
| SPEC-004 | Core Services | Ready |
| SPEC-007 | Test Suite | Ready |

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Active | 2026-03-22 | — | Approved for implementation |
