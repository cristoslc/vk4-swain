"""Attachment service."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from vk.client import VikunjaClient
from vk.config import Config
from vk.models import Attachment


class AttachmentService:
    def __init__(self, client: VikunjaClient, config: Config):
        self.client = client
        self.config = config

    def list(self, task_id: int) -> list[Attachment]:
        data = self.client.list_attachments(task_id)
        return [Attachment.from_dict(a) for a in data]

    def add(self, task_id: int, file_path: str) -> Attachment:
        data = self.client.upload_attachment(task_id, file_path)
        return Attachment.from_dict(data)

    def get(self, task_id: int, attachment_id: int, output: Optional[str] = None) -> bytes:
        content = self.client.download_attachment(task_id, attachment_id)
        if output:
            Path(output).write_bytes(content)
        return content
