"""Task management service."""

from __future__ import annotations

from typing import Optional

from vk.client import VikunjaClient
from vk.config import Config, NameResolver
from vk.models import Task


class TaskService:
    def __init__(self, client: VikunjaClient, config: Config):
        self.client = client
        self.config = config
        self._resolver = NameResolver(client, config)

    def list(
        self,
        project_id: int | None = None,
        bucket_id: int | None = None,
        done: bool | None = None,
    ) -> list[Task]:
        params: dict = {}
        if done is not None:
            params["filter"] = f"done = {str(done).lower()}"
        tasks = self.client.list_tasks(project_id, params=params if params else None)
        result = [Task.from_dict(t) for t in tasks]
        if bucket_id is not None:
            result = [t for t in result if t.bucket_id == bucket_id]
        return result

    def get(self, task_id: int) -> Task:
        data = self.client.get_task(task_id)
        return Task.from_dict(data)

    def create(
        self,
        title: str,
        project_id: int,
        bucket_id: Optional[int] = None,
        due_date: Optional[str] = None,
        priority: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Task:
        data: dict = {"title": title}
        if bucket_id is not None:
            data["bucket_id"] = bucket_id
        if due_date is not None:
            data["due_date"] = due_date
        if priority is not None:
            data["priority"] = priority
        if description is not None:
            data["description"] = description
        result = self.client.create_task(project_id, data)
        return Task.from_dict(result)

    def update(
        self,
        task_id: int,
        title: Optional[str] = None,
        done: Optional[bool] = None,
        priority: Optional[int] = None,
        due_date: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Task:
        data: dict = {}
        if title is not None:
            data["title"] = title
        if done is not None:
            data["done"] = done
        if priority is not None:
            data["priority"] = priority
        if due_date is not None:
            data["due_date"] = due_date
        if description is not None:
            data["description"] = description
        result = self.client.update_task(task_id, data)
        return Task.from_dict(result)

    def move(
        self,
        task_id: int,
        bucket_id: int,
        project_id: int,
        view_id: int | None = None,
    ) -> dict:
        if view_id is None:
            view_id = self._resolver.resolve_view(project_id)
        return self.client.move_task_to_bucket(project_id, view_id, bucket_id, task_id)

    def delete(self, task_id: int) -> None:
        self.client.delete_task(task_id)
