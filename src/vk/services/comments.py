"""Comment service."""

from __future__ import annotations

from vk.client import VikunjaClient
from vk.config import Config
from vk.models import Comment


class CommentService:
    def __init__(self, client: VikunjaClient, config: Config):
        self.client = client
        self.config = config

    def list(self, task_id: int) -> list[Comment]:
        data = self.client.list_comments(task_id)
        return [Comment.from_dict(c) for c in data]

    def add(self, task_id: int, text: str) -> Comment:
        data = self.client.add_comment(task_id, text)
        return Comment.from_dict(data)
