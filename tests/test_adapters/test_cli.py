"""Tests for the Click CLI."""

import json

import responses
from click.testing import CliRunner

from tests.conftest import BASE_URL, make_project, make_task, make_label
from vk.adapters.cli import cli

TOKEN = "tk_test"


def invoke(args, env=None):
    runner = CliRunner()
    env = env or {}
    env.setdefault("VK_URL", BASE_URL)
    env.setdefault("VK_TOKEN", TOKEN)
    return runner.invoke(cli, args, env=env)


class TestProjectCommands:
    @responses.activate
    def test_project_list(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/v1/projects",
            json=[make_project(id=1, title="Household")],
            status=200,
        )
        result = invoke(["project", "list"])
        assert result.exit_code == 0
        assert "Household" in result.output

    @responses.activate
    def test_project_list_json(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/v1/projects",
            json=[make_project(id=1, title="Household")],
            status=200,
        )
        result = invoke(["project", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["title"] == "Household"


class TestTaskCommands:
    @responses.activate
    def test_task_list(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/v1/projects/1/tasks",
            json=[make_task(id=1, title="Pay bill")],
            status=200,
        )
        # Use numeric project ID to skip name resolution
        result = invoke(["task", "list", "1"])
        assert result.exit_code == 0
        assert "Pay bill" in result.output

    @responses.activate
    def test_task_get_json(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/v1/tasks/42",
            json=make_task(id=42, title="Specific"),
            status=200,
        )
        result = invoke(["task", "get", "42", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == 42

    @responses.activate
    def test_task_create(self):
        responses.add(
            responses.PUT,
            f"{BASE_URL}/api/v1/projects/1/tasks",
            json=make_task(id=10, title="New Task", project_id=1),
            status=200,
        )
        result = invoke(["task", "create", "--title", "New Task", "--project", "1"])
        assert result.exit_code == 0
        assert "Created task 10" in result.output


class TestSearchCommand:
    @responses.activate
    def test_search(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/v1/tasks/all",
            json=[make_task(id=1, title="electric bill")],
            status=200,
        )
        result = invoke(["search", "electric"])
        assert result.exit_code == 0
        assert "electric bill" in result.output

    @responses.activate
    def test_search_json(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/v1/tasks/all",
            json=[make_task(id=1, title="electric bill")],
            status=200,
        )
        result = invoke(["search", "electric", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1


class TestLabelCommands:
    @responses.activate
    def test_label_list(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/v1/labels",
            json=[make_label(id=1, title="urgent")],
            status=200,
        )
        result = invoke(["label", "list"])
        assert result.exit_code == 0
        assert "urgent" in result.output


class TestAuthCommands:
    def test_no_auth_exits_2(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["project", "list"], env={"VK_URL": "", "VK_TOKEN": ""})
        assert result.exit_code == 2
