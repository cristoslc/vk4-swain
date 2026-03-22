"""Tests for CommentService."""

import responses

from tests.conftest import BASE_URL, make_comment
from vk.client import VikunjaClient
from vk.config import Config
from vk.services.comments import CommentService


@responses.activate
def test_list_comments():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/tasks/1/comments",
        json=[make_comment(id=1), make_comment(id=2, comment="second")],
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = CommentService(client, config)
    comments = svc.list(1)
    assert len(comments) == 2


@responses.activate
def test_add_comment():
    responses.add(
        responses.PUT,
        f"{BASE_URL}/api/v1/tasks/1/comments",
        json=make_comment(id=3, comment="new note"),
        status=200,
    )
    client = VikunjaClient(BASE_URL, "tk_test")
    config = Config(url=BASE_URL, token="tk_test")
    svc = CommentService(client, config)
    comment = svc.add(1, "new note")
    assert comment.comment == "new note"
