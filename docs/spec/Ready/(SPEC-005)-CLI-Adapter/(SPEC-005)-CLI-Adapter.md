---
title: "CLI Adapter"
artifact: SPEC-005
track: implementable
status: Ready
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: high
type: enhancement
parent-epic: EPIC-002
parent-initiative: INITIATIVE-001
linked-artifacts: []
depends-on-artifacts:
  - SPEC-001
  - SPEC-004
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-005 — CLI Adapter

## Problem Statement

Users need a `vk` command-line tool that wraps core services with Click, providing human-readable compact output by default and `--json` for machine parsing.

## Desired Outcomes

1. Full command surface from the seed document
2. Compact human-readable output by default
3. `--json` flag on every command for machine-parseable output
4. Name resolution (project/bucket names → IDs)

## External Behavior

```bash
vk task list "Household Tasks"
# ID    Title              Priority  Due         Bucket
# 42    Pay electric bill  3         2026-04-01  Do Now
# 43    Fix leaky faucet   2         —           Incoming

vk task list "Household Tasks" --json
# [{"id": 42, "title": "Pay electric bill", ...}, ...]
```

## Acceptance Criteria

- [ ] Click group: `vk` with subgroups: auth, project, bucket, task, comment, attach, search, label, mcp, cache
- [ ] All commands from the seed command surface are implemented
- [ ] `--json` flag on every data-returning command
- [ ] `formatting.py`: compact table formatter and JSON formatter
- [ ] Name resolution: `--project "Name"` and `--bucket "Name"` resolve to IDs
- [ ] `--force` flag on destructive operations (task delete)
- [ ] Exit codes: 0 = success, 1 = error, 2 = auth required

## Scope & Constraints

- CLI is a thin adapter — all logic lives in core services
- Entry point: `vk.adapters.cli:cli` (registered in pyproject.toml)

## Implementation Approach

1. Create `formatting.py` with `format_table()` and `format_json()`
2. Create `adapters/cli.py` with Click groups and commands
3. Wire each command to the corresponding core service method

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Ready | 2026-03-22 | — | Approved for implementation |
