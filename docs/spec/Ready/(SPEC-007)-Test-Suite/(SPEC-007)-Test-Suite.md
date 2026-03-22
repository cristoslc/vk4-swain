---
title: "Test Suite"
artifact: SPEC-007
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
  - SPEC-002
  - SPEC-004
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-007 — Test Suite

## Problem Statement

Core services and the HTTP client need automated tests with mocked HTTP to verify behavior without a live Vikunja instance.

## Desired Outcomes

1. Test fixtures with a mock Vikunja client
2. Tests for each core service
3. Tests for the HTTP client's pagination and error handling
4. CLI command tests using Click's test runner

## Acceptance Criteria

- [ ] `conftest.py` with shared fixtures: mock client, sample data factories
- [ ] `test_client.py`: tests for VikunjaClient pagination, auth headers, error mapping
- [ ] `test_services/`: one test file per service, testing happy path and error cases
- [ ] `test_adapters/`: CLI command tests using `CliRunner`
- [ ] All tests pass with `pytest` (no live Vikunja required)
- [ ] HTTP mocking uses `responses` library

## Scope & Constraints

- No integration tests against live Vikunja (that's a future initiative)
- Mock at the HTTP level using `responses`, not by mocking service internals

## Implementation Approach

1. Create `conftest.py` with mock data and fixtures
2. Write `test_client.py` with `responses` mocking
3. Write service tests in `test_services/`
4. Write CLI tests in `test_adapters/`

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Ready | 2026-03-22 | — | Approved for implementation |
