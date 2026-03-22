"""Configuration and token resolution for vk."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Resolves Vikunja URL and token from multiple sources.

    Resolution order:
    1. Explicit arguments
    2. Environment variables (VK_URL, VK_TOKEN)
    3. .vk-config.json in current directory (walk up to git root)
    4. ~/.config/vk/config.json
    """

    url: str = ""
    token: str = ""
    default_project: str = ""
    kanban_view: str = "Kanban"
    _resolved: bool = field(default=False, repr=False)

    def resolve(self, url: str | None = None, token: str | None = None) -> Config:
        """Resolve config from all sources, returning self for chaining."""
        # 1. Explicit args
        if url:
            self.url = url
        if token:
            self.token = token

        # 2. Env vars
        if not self.url:
            self.url = os.environ.get("VK_URL", "")
        if not self.token:
            self.token = os.environ.get("VK_TOKEN", "")

        # 3 & 4. Config files
        if not self.url or not self.token:
            file_config = self._load_config_file()
            if not self.url:
                self.url = file_config.get("url", "")
            if not self.token:
                self.token = file_config.get("token", "")
            if not self.default_project:
                self.default_project = file_config.get("default_project", "")
            if self.kanban_view == "Kanban":
                self.kanban_view = file_config.get("kanban_view", "Kanban")

        self._resolved = True
        return self

    def _load_config_file(self) -> dict:
        """Load config from .vk-config.json (walking up) or ~/.config/vk/config.json."""
        # Walk up to find .vk-config.json
        current = Path.cwd()
        while True:
            candidate = current / ".vk-config.json"
            if candidate.is_file():
                return json.loads(candidate.read_text())
            # Stop at git root or filesystem root
            if (current / ".git").exists() or current == current.parent:
                break
            current = current.parent

        # Fall back to user config
        user_config = Path.home() / ".config" / "vk" / "config.json"
        if user_config.is_file():
            return json.loads(user_config.read_text())

        return {}

    def save(self, path: Optional[Path] = None) -> Path:
        """Save config to a JSON file."""
        if path is None:
            path = Path.cwd() / ".vk-config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "url": self.url,
            "token": self.token,
        }
        if self.default_project:
            data["default_project"] = self.default_project
        if self.kanban_view and self.kanban_view != "Kanban":
            data["kanban_view"] = self.kanban_view
        path.write_text(json.dumps(data, indent=2) + "\n")
        return path

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.token)


class NameResolver:
    """Resolves human-readable names to Vikunja IDs with local caching."""

    CACHE_FILE = ".vk-cache.json"

    def __init__(self, client: object, config: Config):
        from vk.client import VikunjaClient

        self.client: VikunjaClient = client  # type: ignore[assignment]
        self.config = config
        self._cache: dict = self._load_cache()

    def _cache_path(self) -> Path:
        return Path.cwd() / self.CACHE_FILE

    def _load_cache(self) -> dict:
        path = self._cache_path()
        if path.is_file():
            return json.loads(path.read_text())
        return {"projects": {}, "buckets": {}, "views": {}}

    def _save_cache(self) -> None:
        self._cache_path().write_text(json.dumps(self._cache, indent=2) + "\n")

    def clear_cache(self) -> None:
        self._cache = {"projects": {}, "buckets": {}, "views": {}}
        path = self._cache_path()
        if path.is_file():
            path.unlink()

    def resolve_project(self, name_or_id: str) -> int:
        """Resolve a project name or ID to a project ID."""
        # Try as numeric ID first
        try:
            return int(name_or_id)
        except ValueError:
            pass

        # Check cache
        if name_or_id in self._cache.get("projects", {}):
            return self._cache["projects"][name_or_id]

        # Fetch and cache
        projects = self.client.list_projects()
        self._cache["projects"] = {}
        for p in projects:
            self._cache["projects"][p["title"]] = p["id"]
        self._save_cache()

        if name_or_id in self._cache["projects"]:
            return self._cache["projects"][name_or_id]

        # Fuzzy match
        matches = [
            t for t in self._cache["projects"] if name_or_id.lower() in t.lower()
        ]
        if len(matches) == 1:
            return self._cache["projects"][matches[0]]
        if matches:
            raise ValueError(
                f"Ambiguous project '{name_or_id}'. Candidates: {matches}"
            )
        raise ValueError(f"Project not found: '{name_or_id}'")

    def resolve_view(self, project_id: int, name_or_id: str | None = None) -> int:
        """Resolve a view name/ID, defaulting to the kanban view."""
        if name_or_id:
            try:
                return int(name_or_id)
            except ValueError:
                pass

        target = name_or_id or self.config.kanban_view
        cache_key = str(project_id)

        if cache_key not in self._cache.get("views", {}):
            views = self.client.list_views(project_id)
            self._cache.setdefault("views", {})[cache_key] = {
                v["title"]: v["id"] for v in views
            }
            # Also store by view_kind for fallback
            self._cache.setdefault("views_by_kind", {})[cache_key] = {
                v.get("view_kind", ""): v["id"] for v in views
            }
            self._save_cache()

        views = self._cache["views"].get(cache_key, {})
        if target in views:
            return views[target]

        # Fallback: first kanban view
        kinds = self._cache.get("views_by_kind", {}).get(cache_key, {})
        if "kanban" in kinds:
            return kinds["kanban"]

        # Return first view if any
        if views:
            return next(iter(views.values()))
        raise ValueError(f"No views found for project {project_id}")

    def resolve_bucket(
        self, name_or_id: str, project_id: int, view_id: int
    ) -> int:
        """Resolve a bucket name or ID to a bucket ID."""
        try:
            return int(name_or_id)
        except ValueError:
            pass

        cache_key = f"{project_id}:{view_id}"
        if cache_key not in self._cache.get("buckets", {}):
            buckets = self.client.list_buckets(project_id, view_id)
            self._cache.setdefault("buckets", {})[cache_key] = {
                b["title"]: b["id"] for b in buckets
            }
            self._save_cache()

        buckets = self._cache["buckets"].get(cache_key, {})
        if name_or_id in buckets:
            return buckets[name_or_id]

        matches = [t for t in buckets if name_or_id.lower() in t.lower()]
        if len(matches) == 1:
            return buckets[matches[0]]
        if matches:
            raise ValueError(
                f"Ambiguous bucket '{name_or_id}'. Candidates: {matches}"
            )
        raise ValueError(f"Bucket not found: '{name_or_id}'")
