"""Tests for SearchService."""

import responses

from tests.conftest import BASE_URL, make_task
from vk.client import VikunjaClient
from vk.config import Config
from vk.services.search import SearchService


@responses.activate
def test_search():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/tasks/all",
        json=[make_task(id=1, title="electric bill")],
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = SearchService(client, config)
    tasks = svc.search("electric")
    assert len(tasks) == 1
    assert "electric" in tasks[0].title


@responses.activate
def test_search_filter_by_project():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/tasks/all",
        json=[
            make_task(id=1, title="bill", project_id=1),
            make_task(id=2, title="other bill", project_id=2),
        ],
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = SearchService(client, config)
    tasks = svc.search("bill", project_id=1)
    assert len(tasks) == 1
    assert tasks[0].project_id == 1
