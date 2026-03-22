---
title: "Config and Auth"
artifact: SPEC-003
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
depends-on-artifacts:
  - SPEC-001
  - SPEC-002
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-003 — Config and Auth

## Problem Statement

vk needs a config resolution chain (flags → env → dotfile → user config) and auth commands to store credentials.

## Desired Outcomes

1. `Config` class resolving URL and token from multiple sources
2. `vk auth login` flow that stores credentials
3. `vk auth status` showing current auth state
4. Name resolution cache for projects and buckets

## External Behavior

```bash
vk auth login --url http://localhost:3456 --token tk_abc123
# writes ~/.config/vk/config.json

vk auth status
# Authenticated to http://localhost:3456 as user@example.com
```

## Acceptance Criteria

- [ ] Config resolution order: explicit args → `VK_TOKEN`/`VK_URL` env vars → `.vk-config.json` (walk up to git root) → `~/.config/vk/config.json`
- [ ] Config file format matches seed: url, token, default_project, kanban_view
- [ ] `AuthService.login` stores config to the appropriate file
- [ ] `AuthService.status` returns current auth state
- [ ] Name resolution: `resolve_project(name)` → project_id, `resolve_bucket(name, project_id)` → bucket_id
- [ ] Cache stored in `.vk-cache.json`, refreshable via `vk cache clear`

## Scope & Constraints

- JWT login flow (username/password → JWT → create API token) is nice-to-have; MVP supports `--token` direct input
- Config class is adapter-agnostic — usable from CLI and MCP

## Implementation Approach

1. Implement `Config` class in `config.py` with cascading resolution
2. Implement `AuthService` in `services/auth.py`
3. Add name resolution with local cache

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Ready | 2026-03-22 | — | Approved for implementation |
