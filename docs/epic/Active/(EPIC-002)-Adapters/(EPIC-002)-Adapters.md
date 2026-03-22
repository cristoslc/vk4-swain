---
title: "Adapters"
artifact: EPIC-002
track: container
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: high
success-criteria:
  - "CLI exposes all commands from the seed command surface"
  - "All commands accept --json for machine-parseable output"
  - "MCP stdio server launches and serves tool definitions"
  - "MCP HTTP/SSE server launches on configurable port"
depends-on-artifacts:
  - EPIC-001
addresses: []
evidence-pool: ""
---

# EPIC-002 — Adapters

## Goal / Objective

Build the three adapter layers that expose the core library: Click CLI, MCP stdio server, and MCP HTTP/SSE server.

## Desired Outcomes

1. `vk` console script with full command surface from the seed
2. Compact human-readable output by default, `--json` for machine output
3. MCP stdio server via `vk mcp stdio`
4. MCP HTTP/SSE server via `vk mcp http --port 8456`
5. Shared MCP tool definitions generated from core service signatures

## Scope Boundaries

**In scope:** `src/vk/adapters/`, `src/vk/formatting.py`

**Out of scope:** Core services (EPIC-001), deployment

## Child Specs

| Spec | Title | Status |
|------|-------|--------|
| SPEC-005 | CLI Adapter | Ready |
| SPEC-006 | MCP Adapters | Ready |

## Key Dependencies

- EPIC-001 (core services must exist before adapters)

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Active | 2026-03-22 | — | Approved for implementation |
