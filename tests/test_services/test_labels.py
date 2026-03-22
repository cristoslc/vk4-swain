"""Tests for LabelService."""

import responses

from tests.conftest import BASE_URL, make_label
from vk.client import VikunjaClient
from vk.config import Config
from vk.services.labels import LabelService


@responses.activate
def test_list_labels():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/labels",
        json=[make_label(id=1), make_label(id=2, title="low")],
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = LabelService(client, config)
    labels = svc.list()
    assert len(labels) == 2


@responses.activate
def test_create_label():
    responses.add(
        responses.PUT,
        f"{BASE_URL}/api/v1/labels",
        json=make_label(id=3, title="new"),
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = LabelService(client, config)
    label = svc.create("new")
    assert label.title == "new"
