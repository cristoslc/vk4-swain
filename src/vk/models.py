"""Domain dataclasses for Vikunja resource types."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


def _parse_dt(val: str | None) -> Optional[datetime]:
    if not val or val == "0001-01-01T00:00:00Z":
        return None
    # Vikunja uses ISO 8601 with Z suffix
    return datetime.fromisoformat(val.replace("Z", "+00:00"))


@dataclass
class Project:
    id: int
    title: str
    description: str = ""
    is_archived: bool = False
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> Project:
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            is_archived=data.get("is_archived", False),
            created=_parse_dt(data.get("created")),
            updated=_parse_dt(data.get("updated")),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created"] = self.created.isoformat() if self.created else None
        d["updated"] = self.updated.isoformat() if self.updated else None
        return d


@dataclass
class View:
    id: int
    title: str
    project_id: int
    view_kind: str = ""
    default_bucket_id: int = 0
    done_bucket_id: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> View:
        return cls(
            id=data["id"],
            title=data["title"],
            project_id=data.get("project_id", 0),
            view_kind=data.get("view_kind", ""),
            default_bucket_id=data.get("default_bucket_id", 0),
            done_bucket_id=data.get("done_bucket_id", 0),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Bucket:
    id: int
    title: str
    project_id: int = 0
    view_id: int = 0
    limit: int = 0
    position: float = 0.0
    count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> Bucket:
        return cls(
            id=data["id"],
            title=data["title"],
            project_id=data.get("project_id", 0),
            view_id=data.get("view_id", 0),
            limit=data.get("limit", 0),
            position=data.get("position", 0.0),
            count=data.get("count", 0),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    done: bool = False
    priority: int = 0
    project_id: int = 0
    bucket_id: int = 0
    due_date: Optional[datetime] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    labels: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            done=data.get("done", False),
            priority=data.get("priority", 0),
            project_id=data.get("project_id", 0),
            bucket_id=data.get("bucket_id", 0),
            due_date=_parse_dt(data.get("due_date")),
            created=_parse_dt(data.get("created")),
            updated=_parse_dt(data.get("updated")),
            labels=data.get("labels") or [],
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["due_date"] = self.due_date.isoformat() if self.due_date else None
        d["created"] = self.created.isoformat() if self.created else None
        d["updated"] = self.updated.isoformat() if self.updated else None
        return d


@dataclass
class Comment:
    id: int
    comment: str
    task_id: int = 0
    author_id: int = 0
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> Comment:
        author = data.get("author", {})
        return cls(
            id=data["id"],
            comment=data.get("comment", ""),
            task_id=data.get("task_id", 0),
            author_id=author.get("id", 0) if isinstance(author, dict) else 0,
            created=_parse_dt(data.get("created")),
            updated=_parse_dt(data.get("updated")),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created"] = self.created.isoformat() if self.created else None
        d["updated"] = self.updated.isoformat() if self.updated else None
        return d


@dataclass
class Attachment:
    id: int
    task_id: int
    file_name: str = ""
    file_size: int = 0
    created: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> Attachment:
        file_info = data.get("file", {})
        return cls(
            id=data["id"],
            task_id=data.get("task_id", 0),
            file_name=file_info.get("name", "") if isinstance(file_info, dict) else "",
            file_size=file_info.get("size", 0) if isinstance(file_info, dict) else 0,
            created=_parse_dt(data.get("created")),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created"] = self.created.isoformat() if self.created else None
        return d


@dataclass
class Label:
    id: int
    title: str
    hex_color: str = ""
    description: str = ""
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> Label:
        return cls(
            id=data["id"],
            title=data["title"],
            hex_color=data.get("hex_color", ""),
            description=data.get("description", ""),
            created=_parse_dt(data.get("created")),
            updated=_parse_dt(data.get("updated")),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created"] = self.created.isoformat() if self.created else None
        d["updated"] = self.updated.isoformat() if self.updated else None
        return d


@dataclass
class User:
    id: int
    username: str
    email: str = ""
    name: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> User:
        return cls(
            id=data["id"],
            username=data.get("username", ""),
            email=data.get("email", ""),
            name=data.get("name", ""),
        )

    def to_dict(self) -> dict:
        return asdict(self)
