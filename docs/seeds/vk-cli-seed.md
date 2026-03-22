# vk — Vikunja CLI and MCP Server

## What this is

A unified Python library for interacting with a Vikunja instance, exposed through three adapters: a CLI (`vk`), an HTTP SSE MCP server, and a stdio MCP server. All three share a single core that owns Vikunja API communication, domain logic, and output formatting.

## Why

Asana's free-tier API rate limit (150 req/min) is a hard blocker for agent-driven household task management. A self-hosted Vikunja instance has no rate limits, full data sovereignty, and a clean REST/Swagger API. But Vikunja has no official CLI, and no MCP server exists. This project fills both gaps with a single codebase.

The `asa` CLI (cristoslc/asa) proved that a thin CLI wrapper over a task management API is the right abstraction for agent workflows. `vk` generalizes that pattern with a hexagonal architecture so the same core serves CLI users, MCP-connected AI agents (Claude, etc.), and future adapters without duplication.

## Prior art

- **cristoslc/asa** — CLI for Asana. Single-purpose CLI, no MCP. Validated the command surface and output patterns. `vk` should feel familiar to `asa` users.
- **Vikunja REST API** — OpenAPI/Swagger documented at `/api/v1/docs.json`. JWT and API token auth. All operations tested in local spike (see trove `task-platform-comparison@62bd18a`).
- **HouseOps Asana skill** — defines the Eisenhower workflow, task hygiene rules, and integration patterns that `vk` must support.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Adapters                       │
│                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ CLI      │  │ MCP (stdio)  │  │ MCP (HTTP/ │  │
│  │ (Click)  │  │              │  │  SSE)      │  │
│  └────┬─────┘  └──────┬───────┘  └─────┬─────┘  │
│       │               │                │         │
│       └───────────────┼────────────────┘         │
│                       │                          │
├───────────────────────┼──────────────────────────┤
│                       ▼                          │
│              ┌────────────────┐                  │
│              │   Core (Ports) │                  │
│              │                │                  │
│              │  TaskService   │                  │
│              │  ProjectService│                  │
│              │  CommentService│                  │
│              │  AttachService │                  │
│              │  SearchService │                  │
│              │  AuthService   │                  │
│              │  BucketService │                  │
│              └───────┬────────┘                  │
│                      │                           │
├──────────────────────┼───────────────────────────┤
│                      ▼                           │
│              ┌────────────────┐                  │
│              │  Vikunja Client│                  │
│              │  (HTTP/REST)   │                  │
│              └────────────────┘                  │
│                                                  │
│              ┌────────────────┐                  │
│              │  Config/Auth   │                  │
│              │  (token store) │                  │
│              └────────────────┘                  │
└─────────────────────────────────────────────────┘
```

### Layers

**Vikunja Client** — HTTP adapter to the Vikunja REST API. Handles auth headers, pagination, multipart file uploads, error mapping. One class, stateless except for base URL and token. Mirrors the Swagger spec closely.

**Core Services** — Domain logic. Each service owns one resource type. Services accept and return domain objects (dataclasses), not raw JSON. Services call the Vikunja client and apply business logic (e.g., "mark done" = set `done:true` + move to Done bucket). This is the **port** layer — adapters depend on it, it depends on nothing above.

**Adapters** — Three ways to invoke the core:

1. **CLI (Click)** — `vk task create`, `vk comment add`, etc. Parses flags, calls core services, formats output (compact or `--json`). Installed as a console script via `pyproject.toml`.

2. **MCP stdio** — Standard MCP server over stdin/stdout. Each core service method becomes an MCP tool. Uses the `mcp` Python SDK. Launched via `vk mcp stdio` or directly as an MCP server entry point.

3. **MCP HTTP/SSE** — Same tool definitions, served over HTTP with SSE transport. Launched via `vk mcp http --port 8456`. Suitable for `.mcp.json` configuration in Claude Code or other MCP clients.

### Key design decisions

- **Dataclasses, not dicts** — Core services work with typed domain objects. Adapters serialize to/from JSON or CLI output. This prevents leaking Vikunja API structure into adapter code.
- **Shared tool definitions** — MCP tool schemas are generated from core service method signatures + docstrings. One source of truth for both MCP adapters.
- **Config is adapter-agnostic** — Base URL and token are resolved by a `Config` class that checks (in order): explicit arguments, environment variables (`VK_URL`, `VK_TOKEN`), dotfile (`.vk-config.json` in project root or `~/.config/vk/config.json`).
- **No ORM, no database** — `vk` is a client library, not a server. State lives in Vikunja.
- **Pagination handled transparently** — Client fetches all pages by default; services expose `limit`/`page` when callers need control.

## Command surface

Mirrors `asa` where applicable. Vikunja-specific additions noted.

```
vk auth login [--url URL] [--token TOKEN]
vk auth status

vk project list [--json]
vk project create --title TITLE [--json]
vk project get ID [--json]

vk bucket list PROJECT [--view VIEW] [--json]
vk bucket create PROJECT --title TITLE [--view VIEW] [--json]

vk task list [PROJECT] [--bucket BUCKET] [--done] [--json]
vk task get ID [--json]
vk task create --title TITLE --project PROJECT [--bucket BUCKET] [--due DATE] [--priority N] [--description TEXT] [--json]
vk task update ID [--title TITLE] [--done] [--priority N] [--due DATE] [--description TEXT] [--json]
vk task move ID --bucket BUCKET [--view VIEW] [--json]
vk task delete ID [--force]

vk comment list TASK [--json]
vk comment add TASK --text TEXT [--json]

vk attach list TASK [--json]
vk attach add TASK --file PATH [--json]
vk attach get TASK ATTACHMENT_ID [--output PATH]

vk search QUERY [--project PROJECT] [--done BOOL] [--json]

vk label list [--json]
vk label create --title TITLE [--color HEX] [--json]

vk mcp stdio                    # Launch MCP server (stdio transport)
vk mcp http [--port 8456]       # Launch MCP server (HTTP/SSE transport)
```

### MCP tools (auto-generated from core)

Each core service method maps to an MCP tool. Example tool definitions:

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `vk_task_list` | List tasks in a project | `project_id`, `bucket_id?`, `done?` |
| `vk_task_create` | Create a task | `title`, `project_id`, `bucket_id?`, `due_date?`, `priority?`, `description?` |
| `vk_task_update` | Update a task | `task_id`, `title?`, `done?`, `priority?`, `due_date?`, `description?` |
| `vk_task_move` | Move task to a bucket | `task_id`, `bucket_id`, `project_id`, `view_id?` |
| `vk_comment_add` | Add a comment to a task | `task_id`, `text` |
| `vk_attach_add` | Attach a file to a task | `task_id`, `file_path` |
| `vk_search` | Search tasks | `query`, `project_id?`, `done?` |
| `vk_project_list` | List all projects | (none) |
| `vk_bucket_list` | List buckets in a project view | `project_id`, `view_id?` |

## Project structure

```
~/Documents/code/vk/
├── pyproject.toml
├── src/
│   └── vk/
│       ├── __init__.py
│       ├── client.py           # Vikunja HTTP client
│       ├── config.py           # URL/token resolution
│       ├── models.py           # Domain dataclasses
│       ├── services/
│       │   ├── __init__.py
│       │   ├── tasks.py
│       │   ├── projects.py
│       │   ├── buckets.py
│       │   ├── comments.py
│       │   ├── attachments.py
│       │   ├── search.py
│       │   ├── labels.py
│       │   └── auth.py
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── cli.py          # Click CLI (entry point: vk)
│       │   ├── mcp_tools.py    # Shared MCP tool definitions
│       │   ├── mcp_stdio.py    # stdio MCP server
│       │   └── mcp_http.py     # HTTP/SSE MCP server
│       └── formatting.py       # Compact + JSON output
└── tests/
    ├── conftest.py             # Shared fixtures, mock client
    ├── test_services/
    ├── test_adapters/
    └── test_client.py
```

## Dependencies

```toml
[project]
name = "vk"
version = "0.1.0-alpha"
description = "Vikunja CLI and MCP server"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "requests>=2.31",
    "mcp>=1.0",
]

[project.scripts]
vk = "vk.adapters.cli:cli"

[dependency-groups]
dev = [
    "pytest>=9.0",
    "responses>=0.25",     # HTTP mocking
]
```

## Auth and config

### Token resolution order

1. `--token` flag (CLI) or explicit parameter (MCP)
2. `VK_TOKEN` environment variable
3. `.vk-config.json` in current directory (walk up to git root)
4. `~/.config/vk/config.json`

### Config file format

```json
{
  "url": "http://localhost:3456",
  "token": "tk_...",
  "default_project": "Household Tasks",
  "kanban_view": "Kanban"
}
```

The `default_project` and `kanban_view` fields let the CLI resolve buckets without requiring explicit project/view IDs on every command — similar to how `asa` resolves names via cache.

### `vk auth login`

Interactive (or `--url` + `--token` flags). Writes `.vk-config.json`. If no token is provided, prompts for username/password, authenticates via JWT, then creates a long-lived API token via `PUT /tokens` and stores it.

## Name resolution

Like `asa`, `vk` resolves human-readable names to IDs:

- `--project "Household Tasks"` → project ID 2
- `--bucket "Do Now"` → bucket ID 7

Resolution uses a local cache (`.vk-cache.json`) populated on first use and refreshable via `vk cache clear`. Ambiguous matches produce an error listing candidates.

**View resolution**: Vikunja's bucket structure is per-view (a project can have multiple kanban views). `vk` defaults to the view named "Kanban" (or the first `view_kind: kanban` view). Override with `--view`.

## Vikunja API notes (from spike)

Validated against Vikunja v2.2.0 running locally:

| Operation | Method | Endpoint | Notes |
|-----------|--------|----------|-------|
| Register | POST | `/api/v1/register` | Email must be valid format |
| Login (JWT) | POST | `/api/v1/login` | Returns JWT token |
| Create API token | PUT | `/api/v1/tokens` | Requires explicit `permissions` and `expires_at` |
| List projects | GET | `/api/v1/projects` | |
| Create project | PUT | `/api/v1/projects` | Auto-creates List, Gantt, Table, Kanban views |
| List buckets | GET | `/api/v1/projects/:p/views/:v/buckets` | Requires JWT (API tokens need `projects_views_tasks` perm) |
| Create bucket | PUT | `/api/v1/projects/:p/views/:v/buckets` | |
| Create task | PUT | `/api/v1/projects/:p/tasks` | |
| Update task | POST | `/api/v1/tasks/:t` | `done: true` to complete |
| Move to bucket | POST | `/api/v1/projects/:p/views/:v/buckets/:b/tasks` | Body: `{"task_id": N}` |
| Add comment | PUT | `/api/v1/tasks/:t/comments` | Body: `{"comment": "text"}` |
| Upload attachment | PUT | `/api/v1/tasks/:t/attachments` | Multipart: `files=@path` |
| List attachments | GET | `/api/v1/tasks/:t/attachments` | |
| Search tasks | GET | `/api/v1/tasks?s=query` | Full-text search, no rate limit |
| Webhook events | GET | `/api/v1/webhooks/events` | Webhooks ARE supported (v2.2.0) |
| API routes | GET | `/api/v1/routes` | Lists all permission keys for token creation |

### API token permission gotcha

API tokens require per-resource-group permissions (e.g., `tasks`, `projects`, `tasks_comments`, `tasks_attachments`). Some operations (bucket management) may require additional permission groups or fall back to JWT auth. The CLI should prefer a full-access API token but fall back to JWT re-auth if a 401 is returned.

### Bucket model

Buckets belong to a **view**, not a project directly. A project's kanban view has its own set of buckets. Default views are auto-created: List, Gantt, Table, Kanban. The kanban view's `default_bucket_id` and `done_bucket_id` can be configured.

## Trove reference

Research backing this design: `task-platform-comparison@62bd18a`

Vikunja was selected as the top candidate based on: no rate limits (self-hosted), lightweight (single container, SQLite), full REST API with Swagger docs, all features free, CalDAV, and the best household-fit score across 8 platforms evaluated.

## Acceptance criteria

1. `vk task create --title "Test" --project "Household Tasks" --bucket "Incoming"` creates a task and places it in the correct kanban bucket
2. `vk attach add TASK_ID --file /path/to/doc.pdf` uploads a file attachment
3. `vk task move TASK_ID --bucket "Do Now"` moves a task between Eisenhower buckets
4. `vk comment add TASK_ID --text "Progress note"` adds a comment
5. `vk search "electric bill"` finds tasks by keyword
6. `vk mcp stdio` launches a working MCP server that Claude Code can connect to
7. `vk mcp http --port 8456` launches an SSE MCP server
8. All CLI commands accept `--json` for machine-parseable output
9. Auth works via API token stored in config file
10. Test suite covers core services with mocked HTTP (no live Vikunja required)
