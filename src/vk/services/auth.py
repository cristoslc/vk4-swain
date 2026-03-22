"""Auth service."""

from __future__ import annotations

from pathlib import Path

from vk.client import VikunjaClient
from vk.config import Config


class AuthService:
    def __init__(self, config: Config):
        self.config = config

    def login(self, url: str, token: str, save_path: Path | None = None) -> Config:
        """Store credentials and return updated config."""
        self.config.url = url
        self.config.token = token
        self.config.save(save_path)
        return self.config

    def status(self) -> dict:
        """Return current auth state."""
        if not self.config.is_configured:
            return {"authenticated": False, "reason": "No URL or token configured"}
        try:
            client = VikunjaClient(self.config.url, self.config.token)
            projects = client.list_projects()
            return {
                "authenticated": True,
                "url": self.config.url,
                "projects_accessible": len(projects),
            }
        except Exception as e:
            return {"authenticated": False, "url": self.config.url, "error": str(e)}
