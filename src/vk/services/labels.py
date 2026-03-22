"""Label service."""

from __future__ import annotations

from vk.client import VikunjaClient
from vk.config import Config
from vk.models import Label


class LabelService:
    def __init__(self, client: VikunjaClient, config: Config):
        self.client = client
        self.config = config

    def list(self) -> list[Label]:
        data = self.client.list_labels()
        return [Label.from_dict(l) for l in data]

    def create(self, title: str, hex_color: str = "") -> Label:
        data = self.client.create_label(title, hex_color)
        return Label.from_dict(data)
