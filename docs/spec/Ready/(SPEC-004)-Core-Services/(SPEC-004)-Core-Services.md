---
title: "Core Services"
artifact: SPEC-004
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
  - SPEC-003
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-004 — Core Services

## Problem Statement

The domain logic layer needs service classes that own CRUD operations for each resource type, working with typed domain objects rather than raw JSON.

## Desired Outcomes

1. Service classes for: TaskService, ProjectService, BucketService, CommentService, AttachmentService, SearchService, LabelService
2. Services accept/return domain dataclasses
3. Business logic lives in services (e.g., "mark done" = set done:true + move to Done bucket)

## External Behavior

```python
svc = TaskService(client, config)
task = svc.create(title="Test", project_id=2, bucket_id=7)
# returns Task dataclass
tasks = svc.list(project_id=2, done=False)
```

## Acceptance Criteria

- [ ] `TaskService`: list, get, create, update, move, delete
- [ ] `ProjectService`: list, get, create
- [ ] `BucketService`: list, create (requires project_id and view_id)
- [ ] `CommentService`: list, add
- [ ] `AttachmentService`: list, add, get (download)
- [ ] `SearchService`: search (wraps `GET /tasks?s=query`)
- [ ] `LabelService`: list, create
- [ ] All services accept a `VikunjaClient` and `Config` in constructor
- [ ] All methods return domain dataclasses, not raw dicts
- [ ] View resolution: default to kanban view when view_id not specified

## Scope & Constraints

- Services are the port layer — no knowledge of CLI or MCP
- Bucket operations require view_id (Vikunja's bucket-per-view model)
- Services handle the model-level deserialization via `Model.from_dict()`

## Implementation Approach

1. Implement each service in its own file under `services/`
2. Each service takes `VikunjaClient` and `Config`
3. Methods call client, deserialize response to dataclasses, apply business logic

## Lifecycle

| Phase | Date | Hash | Note |
|-------|------|------|------|
| Proposed | 2026-03-22 | — | Created from vk-cli-seed.md |
| Ready | 2026-03-22 | — | Approved for implementation |
