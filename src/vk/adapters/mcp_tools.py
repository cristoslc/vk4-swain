"""Shared MCP tool definitions generated from core service methods."""

from __future__ import annotations

from typing import Any

from mcp.server import Server

from vk.client import VikunjaClient
from vk.config import Config
from vk.services.attachments import AttachmentService
from vk.services.buckets import BucketService
from vk.services.comments import CommentService
from vk.services.labels import LabelService
from vk.services.projects import ProjectService
from vk.services.search import SearchService
from vk.services.tasks import TaskService


def register_tools(server: Server, config: Config) -> None:
    """Register all vk MCP tools on a server instance."""

    def _client() -> VikunjaClient:
        return VikunjaClient(config.url, config.token)

    @server.tool()
    async def vk_project_list() -> list[dict[str, Any]]:
        """List all projects."""
        svc = ProjectService(_client(), config)
        return [p.to_dict() for p in svc.list()]

    @server.tool()
    async def vk_project_get(project_id: int) -> dict[str, Any]:
        """Get a project by ID."""
        svc = ProjectService(_client(), config)
        return svc.get(project_id).to_dict()

    @server.tool()
    async def vk_project_create(title: str, description: str = "") -> dict[str, Any]:
        """Create a new project."""
        svc = ProjectService(_client(), config)
        return svc.create(title, description).to_dict()

    @server.tool()
    async def vk_bucket_list(project_id: int, view_id: int | None = None) -> list[dict[str, Any]]:
        """List buckets in a project view."""
        svc = BucketService(_client(), config)
        return [b.to_dict() for b in svc.list(project_id, view_id)]

    @server.tool()
    async def vk_bucket_create(project_id: int, title: str, view_id: int | None = None) -> dict[str, Any]:
        """Create a bucket in a project view."""
        svc = BucketService(_client(), config)
        return svc.create(project_id, title, view_id).to_dict()

    @server.tool()
    async def vk_task_list(
        project_id: int | None = None,
        bucket_id: int | None = None,
        done: bool | None = None,
    ) -> list[dict[str, Any]]:
        """List tasks, optionally filtered by project, bucket, or done status."""
        svc = TaskService(_client(), config)
        return [t.to_dict() for t in svc.list(project_id, bucket_id, done)]

    @server.tool()
    async def vk_task_get(task_id: int) -> dict[str, Any]:
        """Get a task by ID."""
        svc = TaskService(_client(), config)
        return svc.get(task_id).to_dict()

    @server.tool()
    async def vk_task_create(
        title: str,
        project_id: int,
        bucket_id: int | None = None,
        due_date: str | None = None,
        priority: int | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new task."""
        svc = TaskService(_client(), config)
        return svc.create(title, project_id, bucket_id, due_date, priority, description).to_dict()

    @server.tool()
    async def vk_task_update(
        task_id: int,
        title: str | None = None,
        done: bool | None = None,
        priority: int | None = None,
        due_date: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a task."""
        svc = TaskService(_client(), config)
        return svc.update(task_id, title, done, priority, due_date, description).to_dict()

    @server.tool()
    async def vk_task_move(
        task_id: int, bucket_id: int, project_id: int, view_id: int | None = None
    ) -> dict[str, Any]:
        """Move a task to a different bucket."""
        svc = TaskService(_client(), config)
        return svc.move(task_id, bucket_id, project_id, view_id)

    @server.tool()
    async def vk_task_delete(task_id: int) -> str:
        """Delete a task."""
        svc = TaskService(_client(), config)
        svc.delete(task_id)
        return f"Deleted task {task_id}"

    @server.tool()
    async def vk_comment_list(task_id: int) -> list[dict[str, Any]]:
        """List comments on a task."""
        svc = CommentService(_client(), config)
        return [c.to_dict() for c in svc.list(task_id)]

    @server.tool()
    async def vk_comment_add(task_id: int, text: str) -> dict[str, Any]:
        """Add a comment to a task."""
        svc = CommentService(_client(), config)
        return svc.add(task_id, text).to_dict()

    @server.tool()
    async def vk_attach_list(task_id: int) -> list[dict[str, Any]]:
        """List attachments on a task."""
        svc = AttachmentService(_client(), config)
        return [a.to_dict() for a in svc.list(task_id)]

    @server.tool()
    async def vk_attach_add(task_id: int, file_path: str) -> dict[str, Any]:
        """Attach a file to a task."""
        svc = AttachmentService(_client(), config)
        return svc.add(task_id, file_path).to_dict()

    @server.tool()
    async def vk_search(
        query: str, project_id: int | None = None, done: bool | None = None
    ) -> list[dict[str, Any]]:
        """Search tasks by keyword."""
        svc = SearchService(_client(), config)
        return [t.to_dict() for t in svc.search(query, project_id, done)]

    @server.tool()
    async def vk_label_list() -> list[dict[str, Any]]:
        """List all labels."""
        svc = LabelService(_client(), config)
        return [l.to_dict() for l in svc.list()]

    @server.tool()
    async def vk_label_create(title: str, hex_color: str = "") -> dict[str, Any]:
        """Create a label."""
        svc = LabelService(_client(), config)
        return svc.create(title, hex_color).to_dict()
