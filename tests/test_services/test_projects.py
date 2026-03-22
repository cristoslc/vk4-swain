"""Tests for ProjectService."""

import responses

from tests.conftest import BASE_URL, make_project
from vk.client import VikunjaClient
from vk.config import Config
from vk.services.projects import ProjectService


@responses.activate
def test_list_projects():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/projects",
        json=[make_project(id=1), make_project(id=2, title="Second")],
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = ProjectService(client, config)
    projects = svc.list()
    assert len(projects) == 2


@responses.activate
def test_create_project():
    responses.add(
        responses.PUT,
        f"{BASE_URL}/api/v1/projects",
        json=make_project(id=3, title="New"),
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = ProjectService(client, config)
    project = svc.create("New")
    assert project.id == 3
    assert project.title == "New"
