"""Project management service."""

from __future__ import annotations

from vk.client import VikunjaClient
from vk.config import Config
from vk.models import Project


class ProjectService:
    def __init__(self, client: VikunjaClient, config: Config):
        self.client = client
        self.config = config

    def list(self) -> list[Project]:
        data = self.client.list_projects()
        return [Project.from_dict(p) for p in data]

    def get(self, project_id: int) -> Project:
        data = self.client.get_project(project_id)
        return Project.from_dict(data)

    def create(self, title: str, description: str = "") -> Project:
        data = self.client.create_project(title, description)
        return Project.from_dict(data)
