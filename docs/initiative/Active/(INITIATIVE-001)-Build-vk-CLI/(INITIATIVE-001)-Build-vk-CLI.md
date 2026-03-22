---
title: "Build vk CLI"
artifact: INITIATIVE-001
track: container
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
parent-vision:
  - VISION-001
priority-weight: high
success-criteria:
  - "vk CLI installs via pyproject.toml and exposes all commands from the seed"
  - "MCP servers launch and serve tool definitions"
  - "Test suite passes with mocked HTTP"
depends-on-artifacts: []
addresses: []
evidence-pool: "task-platform-comparison@62bd18a"
---

# INITIATIVE-001 — Build vk CLI

## Strategic Focus

Deliver the complete vk package: HTTP client, core services, CLI adapter, MCP adapters, and test suite. This is the sole initiative under VISION-001 — it covers the entire build from zero to a working, tested CLI and MCP server pair.

## Desired Outcomes

1. A `vk` console script that manages tasks, projects, buckets, comments, attachments, labels, and search against Vikunja
2. MCP stdio and HTTP/SSE servers auto-generated from core service methods
3. Hexagonal architecture: adapters depend on core, core depends on nothing above
4. Comprehensive test suite with mocked HTTP

## Scope Boundaries

**In scope:** Everything described in vk-cli-seed.md — client, services, CLI, MCP, tests, config/auth.

**Out of scope:** Deployment automation, CI/CD pipelines, CalDAV, webhooks consumer, GUI.

## Child Epics

| Epic | Title | Status |
|------|-------|--------|
| EPIC-001 | Core Library | Active |
| EPIC-002 | Adapters | Active |

## Key Dependencies

- Vikunja REST API v2.2.0+ (self-hosted instance for integration testing)
- Python >=3.11
- click >=8.1, requests >=2.31, mcp >=1.0

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Active | 2026-03-22 | — | Approved for implementation |
