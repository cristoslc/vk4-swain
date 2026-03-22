"""Shared test fixtures."""

import pytest
import responses

from vk.client import VikunjaClient
from vk.config import Config

BASE_URL = "http://vikunja.test"
TOKEN = "tk_test_token"


@pytest.fixture
def config():
    cfg = Config(url=BASE_URL, token=TOKEN)
    cfg._resolved = True
    return cfg


@pytest.fixture
def client():
    return VikunjaClient(BASE_URL, TOKEN)


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


# -- Sample data factories --

def make_project(id=1, title="Test Project", **kw):
    return {
        "id": id,
        "title": title,
        "description": kw.get("description", ""),
        "is_archived": False,
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z",
    }


def make_task(id=1, title="Test Task", project_id=1, **kw):
    return {
        "id": id,
        "title": title,
        "description": kw.get("description", ""),
        "done": kw.get("done", False),
        "priority": kw.get("priority", 0),
        "project_id": project_id,
        "bucket_id": kw.get("bucket_id", 0),
        "due_date": kw.get("due_date"),
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z",
        "labels": kw.get("labels", []),
    }


def make_bucket(id=1, title="Incoming", project_id=1, view_id=1, **kw):
    return {
        "id": id,
        "title": title,
        "project_id": project_id,
        "view_id": view_id,
        "limit": 0,
        "position": 0.0,
        "count": kw.get("count", 0),
    }


def make_comment(id=1, comment="Test comment", task_id=1, **kw):
    return {
        "id": id,
        "comment": comment,
        "task_id": task_id,
        "author": {"id": 1},
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z",
    }


def make_label(id=1, title="urgent", **kw):
    return {
        "id": id,
        "title": title,
        "hex_color": kw.get("hex_color", "#ff0000"),
        "description": kw.get("description", ""),
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z",
    }


def make_view(id=1, title="Kanban", project_id=1, **kw):
    return {
        "id": id,
        "title": title,
        "project_id": project_id,
        "view_kind": kw.get("view_kind", "kanban"),
        "default_bucket_id": kw.get("default_bucket_id", 0),
        "done_bucket_id": kw.get("done_bucket_id", 0),
    }
