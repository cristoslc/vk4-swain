---
title: "MCP Adapters"
artifact: SPEC-006
track: implementable
status: Ready
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: medium
type: enhancement
parent-epic: EPIC-002
parent-initiative: INITIATIVE-001
linked-artifacts: []
depends-on-artifacts:
  - SPEC-004
  - SPEC-005
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-006 — MCP Adapters

## Problem Statement

AI agents (Claude Code, etc.) need MCP-protocol access to Vikunja operations via stdio and HTTP/SSE transports.

## Desired Outcomes

1. Shared MCP tool definitions generated from core service methods
2. MCP stdio server launched via `vk mcp stdio`
3. MCP HTTP/SSE server launched via `vk mcp http --port 8456`

## External Behavior

```bash
vk mcp stdio
# Starts MCP server on stdin/stdout, serves tool definitions

vk mcp http --port 8456
# Starts HTTP/SSE MCP server on port 8456
```

## Acceptance Criteria

- [ ] `mcp_tools.py`: shared tool definitions mapping core service methods to MCP tool schemas
- [ ] Tool names match seed table: `vk_task_list`, `vk_task_create`, etc.
- [ ] `mcp_stdio.py`: MCP server using `mcp` Python SDK with stdio transport
- [ ] `mcp_http.py`: MCP server with HTTP/SSE transport
- [ ] Both servers serve identical tool definitions from `mcp_tools.py`
- [ ] CLI integration: `vk mcp stdio` and `vk mcp http --port PORT` subcommands

## Scope & Constraints

- Uses the `mcp` Python SDK (>=1.0)
- Tool schemas auto-generated from core service method signatures and docstrings
- No custom protocol extensions — standard MCP only

## Implementation Approach

1. Create `mcp_tools.py` with tool definitions derived from core services
2. Create `mcp_stdio.py` using `mcp` SDK's stdio server
3. Create `mcp_http.py` using `mcp` SDK's HTTP/SSE server
4. Add `mcp` Click subgroup to CLI

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Ready | 2026-03-22 | — | Approved for implementation |
