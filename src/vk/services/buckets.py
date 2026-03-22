"""Bucket management service."""

from __future__ import annotations

from vk.client import VikunjaClient
from vk.config import Config, NameResolver
from vk.models import Bucket, View


class BucketService:
    def __init__(self, client: VikunjaClient, config: Config):
        self.client = client
        self.config = config
        self._resolver = NameResolver(client, config)

    def list_views(self, project_id: int) -> list[View]:
        data = self.client.list_views(project_id)
        return [View.from_dict(v) for v in data]

    def list(self, project_id: int, view_id: int | None = None) -> list[Bucket]:
        if view_id is None:
            view_id = self._resolver.resolve_view(project_id)
        data = self.client.list_buckets(project_id, view_id)
        return [Bucket.from_dict(b) for b in data]

    def create(
        self, project_id: int, title: str, view_id: int | None = None
    ) -> Bucket:
        if view_id is None:
            view_id = self._resolver.resolve_view(project_id)
        data = self.client.create_bucket(project_id, view_id, title)
        return Bucket.from_dict(data)
