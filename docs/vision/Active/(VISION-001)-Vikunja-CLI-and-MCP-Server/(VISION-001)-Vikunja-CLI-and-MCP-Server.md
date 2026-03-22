---
title: "Vikunja CLI and MCP Server"
artifact: VISION-001
track: standing
status: Active
product-type: personal
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: high
depends-on-artifacts: []
evidence-pool: "task-platform-comparison@62bd18a"
---

# VISION-001 — Vikunja CLI and MCP Server

## Target Audience

Solo operators and AI agents managing household and personal tasks through a self-hosted Vikunja instance. Primary users are Claude Code sessions and CLI power users who need scriptable, rate-limit-free task management.

## Problem Statement

Asana's free-tier API rate limit (150 req/min) is a hard blocker for agent-driven household task management. A self-hosted Vikunja instance has no rate limits, full data sovereignty, and a clean REST/Swagger API — but Vikunja has no official CLI and no MCP server exists. This leaves agents without a programmatic interface to the task backend.

## Value Proposition

A unified Python library (`vk`) that exposes a single Vikunja core through three adapters: a CLI, an MCP stdio server, and an MCP HTTP/SSE server. One codebase, three access patterns, zero rate limits.

## Existing Landscape

- **cristoslc/asa** — CLI for Asana. Validated the command surface and output patterns. Single-purpose CLI, no MCP support.
- **Vikunja REST API** — OpenAPI/Swagger documented. JWT and API token auth. All operations validated in local spike.
- **HouseOps Asana skill** — Defines the Eisenhower workflow and integration patterns that vk must support.

## Build vs. Buy

No existing Vikunja CLI or MCP server exists. Building is the only option.

## Maintenance Budget

Low. The Vikunja API is stable (v2.x). The CLI is a thin wrapper. MCP adapters auto-generate tool schemas from core service signatures. Expected maintenance: API version bumps and occasional new Vikunja features.

## Success Metrics

1. All 10 acceptance criteria from the seed document pass
2. CLI commands execute against a live Vikunja instance without rate-limit errors
3. MCP stdio server connects to Claude Code and executes task operations
4. Test suite covers core services with mocked HTTP (no live Vikunja required)

## Non-Goals

- Vikunja server administration (backup, upgrade, user management)
- Web UI or GUI
- Multi-user collaboration features
- CalDAV integration (future initiative)

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Active | 2026-03-22 | — | Approved for implementation |
