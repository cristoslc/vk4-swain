"""Tests for TaskService."""

import responses

from tests.conftest import BASE_URL, make_task
from vk.client import VikunjaClient
from vk.config import Config
from vk.services.tasks import TaskService


@responses.activate
def test_list_tasks():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/projects/1/tasks",
        json=[make_task(id=1), make_task(id=2, title="Second")],
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = TaskService(client, config)
    tasks = svc.list(project_id=1)
    assert len(tasks) == 2
    assert tasks[0].title == "Test Task"
    assert tasks[1].title == "Second"


@responses.activate
def test_get_task():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/tasks/42",
        json=make_task(id=42, title="Specific"),
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = TaskService(client, config)
    task = svc.get(42)
    assert task.id == 42
    assert task.title == "Specific"


@responses.activate
def test_create_task():
    responses.add(
        responses.PUT,
        f"{BASE_URL}/api/v1/projects/1/tasks",
        json=make_task(id=10, title="New", project_id=1),
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = TaskService(client, config)
    task = svc.create(title="New", project_id=1)
    assert task.id == 10
    assert task.title == "New"


@responses.activate
def test_update_task():
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/v1/tasks/10",
        json=make_task(id=10, title="Updated", done=True),
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = TaskService(client, config)
    task = svc.update(10, done=True)
    assert task.done is True


@responses.activate
def test_delete_task():
    responses.add(responses.DELETE, f"{BASE_URL}/api/v1/tasks/10", status=204)
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = TaskService(client, config)
    svc.delete(10)  # should not raise
