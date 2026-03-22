"""Tests for the Vikunja HTTP client."""

import json

import pytest
import responses

from vk.client import VikunjaClient
from vk.exceptions import ApiError, AuthError, NotFoundError

BASE_URL = "http://vikunja.test"
TOKEN = "tk_test"


@pytest.fixture
def client():
    return VikunjaClient(BASE_URL, TOKEN)


@pytest.fixture
def mocked():
    with responses.RequestsMock() as rsps:
        yield rsps


class TestAuth:
    def test_auth_header(self, client, mocked):
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects", json=[], status=200)
        client.list_projects()
        assert mocked.calls[0].request.headers["Authorization"] == f"Bearer {TOKEN}"


class TestErrorMapping:
    def test_401_raises_auth_error(self, client, mocked):
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects", status=401, body="unauthorized")
        with pytest.raises(AuthError):
            client.list_projects()

    def test_404_raises_not_found(self, client, mocked):
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects/999", status=404, body="not found")
        with pytest.raises(NotFoundError):
            client.get_project(999)

    def test_500_raises_api_error(self, client, mocked):
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects", status=500, body="server error")
        with pytest.raises(ApiError):
            client.list_projects()


class TestPagination:
    def test_single_page(self, client, mocked):
        items = [{"id": 1}, {"id": 2}]
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects", json=items, status=200)
        result = client.list_projects()
        assert len(result) == 2

    def test_multi_page(self, client, mocked):
        page1 = [{"id": i} for i in range(50)]
        page2 = [{"id": 50}]
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects", json=page1, status=200)
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects", json=page2, status=200)
        result = client.list_projects()
        assert len(result) == 51


class TestProjects:
    def test_list_projects(self, client, mocked):
        mocked.add(responses.GET, f"{BASE_URL}/api/v1/projects", json=[{"id": 1, "title": "P1"}], status=200)
        result = client.list_projects()
        assert result[0]["title"] == "P1"

    def test_create_project(self, client, mocked):
        mocked.add(responses.PUT, f"{BASE_URL}/api/v1/projects", json={"id": 2, "title": "New"}, status=200)
        result = client.create_project("New")
        assert result["id"] == 2


class TestTasks:
    def test_list_tasks(self, client, mocked):
        mocked.add(
            responses.GET,
            f"{BASE_URL}/api/v1/projects/1/tasks",
            json=[{"id": 1, "title": "T1"}],
            status=200,
        )
        result = client.list_tasks(project_id=1)
        assert result[0]["title"] == "T1"

    def test_create_task(self, client, mocked):
        mocked.add(
            responses.PUT,
            f"{BASE_URL}/api/v1/projects/1/tasks",
            json={"id": 5, "title": "New Task"},
            status=200,
        )
        result = client.create_task(1, {"title": "New Task"})
        assert result["id"] == 5

    def test_update_task(self, client, mocked):
        mocked.add(
            responses.POST,
            f"{BASE_URL}/api/v1/tasks/5",
            json={"id": 5, "title": "Updated", "done": True},
            status=200,
        )
        result = client.update_task(5, {"done": True})
        assert result["done"] is True

    def test_delete_task(self, client, mocked):
        mocked.add(responses.DELETE, f"{BASE_URL}/api/v1/tasks/5", status=204)
        client.delete_task(5)  # should not raise

    def test_move_task(self, client, mocked):
        mocked.add(
            responses.POST,
            f"{BASE_URL}/api/v1/projects/1/views/1/buckets/3/tasks",
            json={"task_id": 5},
            status=200,
        )
        result = client.move_task_to_bucket(1, 1, 3, 5)
        assert result["task_id"] == 5


class TestComments:
    def test_list_comments(self, client, mocked):
        mocked.add(
            responses.GET,
            f"{BASE_URL}/api/v1/tasks/1/comments",
            json=[{"id": 1, "comment": "hello"}],
            status=200,
        )
        result = client.list_comments(1)
        assert result[0]["comment"] == "hello"

    def test_add_comment(self, client, mocked):
        mocked.add(
            responses.PUT,
            f"{BASE_URL}/api/v1/tasks/1/comments",
            json={"id": 2, "comment": "new comment"},
            status=200,
        )
        result = client.add_comment(1, "new comment")
        assert result["id"] == 2


class TestSearch:
    def test_search_tasks(self, client, mocked):
        mocked.add(
            responses.GET,
            f"{BASE_URL}/api/v1/tasks/all",
            json=[{"id": 1, "title": "electric bill"}],
            status=200,
        )
        result = client.search_tasks("electric")
        assert len(result) == 1


class TestLabels:
    def test_list_labels(self, client, mocked):
        mocked.add(
            responses.GET,
            f"{BASE_URL}/api/v1/labels",
            json=[{"id": 1, "title": "urgent"}],
            status=200,
        )
        result = client.list_labels()
        assert result[0]["title"] == "urgent"

    def test_create_label(self, client, mocked):
        mocked.add(
            responses.PUT,
            f"{BASE_URL}/api/v1/labels",
            json={"id": 2, "title": "low"},
            status=200,
        )
        result = client.create_label("low")
        assert result["id"] == 2
