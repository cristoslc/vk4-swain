---
title: "Vikunja HTTP Client"
artifact: SPEC-002
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
addresses: []
evidence-pool: "task-platform-comparison@62bd18a"
source-issue: ""
swain-do: required
---

# SPEC-002 — Vikunja HTTP Client

## Problem Statement

Core services need a clean HTTP adapter to the Vikunja REST API that handles auth headers, pagination, multipart file uploads, and error mapping.

## Desired Outcomes

1. A `VikunjaClient` class that wraps all Vikunja API endpoints
2. Transparent pagination (fetch all pages by default)
3. Proper error mapping (HTTP errors → typed exceptions)
4. Multipart file upload support for attachments

## External Behavior

```python
client = VikunjaClient(base_url="http://localhost:3456", token="tk_...")
tasks = client.list_tasks(project_id=2)  # returns list of dicts
```

## Acceptance Criteria

- [ ] `VikunjaClient.__init__` accepts `base_url` and `token`
- [ ] All API endpoints from the seed's API notes table are implemented as methods
- [ ] Pagination: `_paginated_get` fetches all pages automatically, returns combined results
- [ ] Auth: every request includes `Authorization: Bearer {token}` header
- [ ] Error mapping: 401 → `AuthError`, 404 → `NotFoundError`, 4xx/5xx → `ApiError`
- [ ] File upload: `upload_attachment(task_id, file_path)` sends multipart form data
- [ ] Client is stateless except for base_url and token

## Scope & Constraints

- Client methods return raw dicts — deserialization to models happens in services
- No retry logic (keep it simple)
- Custom exception classes in a `exceptions.py` module

## Implementation Approach

1. Create `exceptions.py` with `ApiError`, `AuthError`, `NotFoundError`
2. Implement `VikunjaClient` in `client.py` with a `_request` base method
3. Add `_paginated_get` for list endpoints
4. Implement one method per API endpoint from the seed table

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Ready | 2026-03-22 | — | Approved for implementation |
