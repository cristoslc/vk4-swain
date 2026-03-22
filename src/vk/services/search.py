"""Search service."""

from __future__ import annotations

from typing import Optional

from vk.client import VikunjaClient
from vk.config import Config
from vk.models import Task


class SearchService:
    def __init__(self, client: VikunjaClient, config: Config):
        self.client = client
        self.config = config

    def search(
        self, query: str, project_id: Optional[int] = None, done: Optional[bool] = None
    ) -> list[Task]:
        params: dict = {}
        if done is not None:
            params["filter"] = f"done = {str(done).lower()}"
        data = self.client.search_tasks(query, params=params if params else None)
        tasks = [Task.from_dict(t) for t in data]
        if project_id is not None:
            tasks = [t for t in tasks if t.project_id == project_id]
        return tasks
