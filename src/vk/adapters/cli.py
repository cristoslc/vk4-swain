"""Click CLI adapter for vk."""

from __future__ import annotations

import sys

import click

from vk.client import VikunjaClient
from vk.config import Config, NameResolver
from vk.formatting import (
    format_attachment_table,
    format_bucket_table,
    format_comment_table,
    format_json,
    format_label_table,
    format_project_table,
    format_task_table,
)
from vk.services.attachments import AttachmentService
from vk.services.auth import AuthService
from vk.services.buckets import BucketService
from vk.services.comments import CommentService
from vk.services.labels import LabelService
from vk.services.projects import ProjectService
from vk.services.search import SearchService
from vk.services.tasks import TaskService


pass_config = click.make_pass_decorator(Config, ensure=True)


def _get_client(config: Config) -> VikunjaClient:
    if not config.is_configured:
        click.echo("Error: not authenticated. Run 'vk auth login' first.", err=True)
        sys.exit(2)
    return VikunjaClient(config.url, config.token)


def _get_resolver(client: VikunjaClient, config: Config) -> NameResolver:
    return NameResolver(client, config)


@click.group()
@click.option("--url", envvar="VK_URL", default=None, help="Vikunja base URL")
@click.option("--token", envvar="VK_TOKEN", default=None, help="API token")
@click.pass_context
def cli(ctx: click.Context, url: str | None, token: str | None) -> None:
    """vk — Vikunja CLI and MCP server."""
    ctx.ensure_object(Config)
    ctx.obj.resolve(url=url, token=token)


# -- Auth --


@cli.group()
def auth() -> None:
    """Authentication commands."""


@auth.command("login")
@click.option("--url", required=True, help="Vikunja base URL")
@click.option("--token", required=True, help="API token")
@pass_config
def auth_login(config: Config, url: str, token: str) -> None:
    """Store Vikunja credentials."""
    svc = AuthService(config)
    svc.login(url, token)
    click.echo(f"Authenticated to {url}. Config saved.")


@auth.command("status")
@pass_config
def auth_status(config: Config) -> None:
    """Show current auth state."""
    svc = AuthService(config)
    status = svc.status()
    if status["authenticated"]:
        click.echo(f"Authenticated to {status['url']} ({status['projects_accessible']} projects accessible)")
    else:
        click.echo(f"Not authenticated: {status.get('reason', status.get('error', 'unknown'))}")


# -- Projects --


@cli.group()
def project() -> None:
    """Project commands."""


@project.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def project_list(config: Config, as_json: bool) -> None:
    """List all projects."""
    client = _get_client(config)
    svc = ProjectService(client, config)
    projects = svc.list()
    if as_json:
        click.echo(format_json(projects))
    else:
        click.echo(format_project_table(projects))


@project.command("get")
@click.argument("project_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def project_get(config: Config, project_id: int, as_json: bool) -> None:
    """Get a project by ID."""
    client = _get_client(config)
    svc = ProjectService(client, config)
    p = svc.get(project_id)
    if as_json:
        click.echo(format_json(p))
    else:
        click.echo(format_project_table([p]))


@project.command("create")
@click.option("--title", required=True, help="Project title")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def project_create(config: Config, title: str, as_json: bool) -> None:
    """Create a new project."""
    client = _get_client(config)
    svc = ProjectService(client, config)
    p = svc.create(title)
    if as_json:
        click.echo(format_json(p))
    else:
        click.echo(f"Created project {p.id}: {p.title}")


# -- Buckets --


@cli.group()
def bucket() -> None:
    """Bucket commands."""


@bucket.command("list")
@click.argument("project")
@click.option("--view", default=None, help="View name or ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def bucket_list(config: Config, project: str, view: str | None, as_json: bool) -> None:
    """List buckets in a project."""
    client = _get_client(config)
    resolver = _get_resolver(client, config)
    project_id = resolver.resolve_project(project)
    view_id = resolver.resolve_view(project_id, view) if view else None
    svc = BucketService(client, config)
    buckets = svc.list(project_id, view_id)
    if as_json:
        click.echo(format_json(buckets))
    else:
        click.echo(format_bucket_table(buckets))


@bucket.command("create")
@click.argument("project")
@click.option("--title", required=True, help="Bucket title")
@click.option("--view", default=None, help="View name or ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def bucket_create(
    config: Config, project: str, title: str, view: str | None, as_json: bool
) -> None:
    """Create a bucket in a project."""
    client = _get_client(config)
    resolver = _get_resolver(client, config)
    project_id = resolver.resolve_project(project)
    view_id = resolver.resolve_view(project_id, view) if view else None
    svc = BucketService(client, config)
    b = svc.create(project_id, title, view_id)
    if as_json:
        click.echo(format_json(b))
    else:
        click.echo(f"Created bucket {b.id}: {b.title}")


# -- Tasks --


@cli.group()
def task() -> None:
    """Task commands."""


@task.command("list")
@click.argument("project", required=False)
@click.option("--bucket", default=None, help="Filter by bucket name or ID")
@click.option("--done/--no-done", default=None, help="Filter by done status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def task_list(
    config: Config,
    project: str | None,
    bucket: str | None,
    done: bool | None,
    as_json: bool,
) -> None:
    """List tasks, optionally filtered by project."""
    client = _get_client(config)
    resolver = _get_resolver(client, config)
    project_id = resolver.resolve_project(project) if project else None
    bucket_id = None
    if bucket and project_id:
        view_id = resolver.resolve_view(project_id)
        bucket_id = resolver.resolve_bucket(bucket, project_id, view_id)
    svc = TaskService(client, config)
    tasks = svc.list(project_id=project_id, bucket_id=bucket_id, done=done)
    if as_json:
        click.echo(format_json(tasks))
    else:
        click.echo(format_task_table(tasks))


@task.command("get")
@click.argument("task_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def task_get(config: Config, task_id: int, as_json: bool) -> None:
    """Get a task by ID."""
    client = _get_client(config)
    svc = TaskService(client, config)
    t = svc.get(task_id)
    if as_json:
        click.echo(format_json(t))
    else:
        click.echo(format_task_table([t]))


@task.command("create")
@click.option("--title", required=True, help="Task title")
@click.option("--project", required=True, help="Project name or ID")
@click.option("--bucket", default=None, help="Bucket name or ID")
@click.option("--due", default=None, help="Due date (ISO format)")
@click.option("--priority", type=int, default=None, help="Priority (0-5)")
@click.option("--description", default=None, help="Description text")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def task_create(
    config: Config,
    title: str,
    project: str,
    bucket: str | None,
    due: str | None,
    priority: int | None,
    description: str | None,
    as_json: bool,
) -> None:
    """Create a new task."""
    client = _get_client(config)
    resolver = _get_resolver(client, config)
    project_id = resolver.resolve_project(project)
    bucket_id = None
    if bucket:
        view_id = resolver.resolve_view(project_id)
        bucket_id = resolver.resolve_bucket(bucket, project_id, view_id)
    svc = TaskService(client, config)
    t = svc.create(
        title=title,
        project_id=project_id,
        bucket_id=bucket_id,
        due_date=due,
        priority=priority,
        description=description,
    )
    if as_json:
        click.echo(format_json(t))
    else:
        click.echo(f"Created task {t.id}: {t.title}")


@task.command("update")
@click.argument("task_id", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--done/--no-done", default=None, help="Mark done/undone")
@click.option("--priority", type=int, default=None, help="Priority (0-5)")
@click.option("--due", default=None, help="Due date (ISO format)")
@click.option("--description", default=None, help="Description text")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def task_update(
    config: Config,
    task_id: int,
    title: str | None,
    done: bool | None,
    priority: int | None,
    due: str | None,
    description: str | None,
    as_json: bool,
) -> None:
    """Update a task."""
    client = _get_client(config)
    svc = TaskService(client, config)
    t = svc.update(
        task_id=task_id,
        title=title,
        done=done,
        priority=priority,
        due_date=due,
        description=description,
    )
    if as_json:
        click.echo(format_json(t))
    else:
        click.echo(f"Updated task {t.id}: {t.title}")


@task.command("move")
@click.argument("task_id", type=int)
@click.option("--bucket", required=True, help="Target bucket name or ID")
@click.option("--project", default=None, help="Project name or ID (if not on task)")
@click.option("--view", default=None, help="View name or ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def task_move(
    config: Config,
    task_id: int,
    bucket: str,
    project: str | None,
    view: str | None,
    as_json: bool,
) -> None:
    """Move a task to a different bucket."""
    client = _get_client(config)
    resolver = _get_resolver(client, config)
    # Get the task to find project_id if not specified
    svc = TaskService(client, config)
    if project:
        project_id = resolver.resolve_project(project)
    else:
        t = svc.get(task_id)
        project_id = t.project_id
    view_id = resolver.resolve_view(project_id, view)
    bucket_id = resolver.resolve_bucket(bucket, project_id, view_id)
    result = svc.move(task_id, bucket_id, project_id, view_id)
    if as_json:
        click.echo(format_json(result))
    else:
        click.echo(f"Moved task {task_id} to bucket {bucket}")


@task.command("delete")
@click.argument("task_id", type=int)
@click.option("--force", is_flag=True, help="Skip confirmation")
@pass_config
def task_delete(config: Config, task_id: int, force: bool) -> None:
    """Delete a task."""
    if not force:
        click.confirm(f"Delete task {task_id}?", abort=True)
    client = _get_client(config)
    svc = TaskService(client, config)
    svc.delete(task_id)
    click.echo(f"Deleted task {task_id}")


# -- Comments --


@cli.group()
def comment() -> None:
    """Comment commands."""


@comment.command("list")
@click.argument("task_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def comment_list(config: Config, task_id: int, as_json: bool) -> None:
    """List comments on a task."""
    client = _get_client(config)
    svc = CommentService(client, config)
    comments = svc.list(task_id)
    if as_json:
        click.echo(format_json(comments))
    else:
        click.echo(format_comment_table(comments))


@comment.command("add")
@click.argument("task_id", type=int)
@click.option("--text", required=True, help="Comment text")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def comment_add(config: Config, task_id: int, text: str, as_json: bool) -> None:
    """Add a comment to a task."""
    client = _get_client(config)
    svc = CommentService(client, config)
    c = svc.add(task_id, text)
    if as_json:
        click.echo(format_json(c))
    else:
        click.echo(f"Added comment {c.id}")


# -- Attachments --


@cli.group()
def attach() -> None:
    """Attachment commands."""


@attach.command("list")
@click.argument("task_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def attach_list(config: Config, task_id: int, as_json: bool) -> None:
    """List attachments on a task."""
    client = _get_client(config)
    svc = AttachmentService(client, config)
    attachments = svc.list(task_id)
    if as_json:
        click.echo(format_json(attachments))
    else:
        click.echo(format_attachment_table(attachments))


@attach.command("add")
@click.argument("task_id", type=int)
@click.option("--file", "file_path", required=True, help="File to attach")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def attach_add(config: Config, task_id: int, file_path: str, as_json: bool) -> None:
    """Attach a file to a task."""
    client = _get_client(config)
    svc = AttachmentService(client, config)
    a = svc.add(task_id, file_path)
    if as_json:
        click.echo(format_json(a))
    else:
        click.echo(f"Attached {a.file_name} (id: {a.id})")


@attach.command("get")
@click.argument("task_id", type=int)
@click.argument("attachment_id", type=int)
@click.option("--output", default=None, help="Output file path")
@pass_config
def attach_get(
    config: Config, task_id: int, attachment_id: int, output: str | None
) -> None:
    """Download an attachment."""
    client = _get_client(config)
    svc = AttachmentService(client, config)
    content = svc.get(task_id, attachment_id, output)
    if output:
        click.echo(f"Saved to {output}")
    else:
        sys.stdout.buffer.write(content)


# -- Search --


@cli.command()
@click.argument("query")
@click.option("--project", default=None, help="Filter by project name or ID")
@click.option("--done", type=bool, default=None, help="Filter by done status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def search(
    config: Config, query: str, project: str | None, done: bool | None, as_json: bool
) -> None:
    """Search tasks by keyword."""
    client = _get_client(config)
    resolver = _get_resolver(client, config)
    project_id = resolver.resolve_project(project) if project else None
    svc = SearchService(client, config)
    tasks = svc.search(query, project_id=project_id, done=done)
    if as_json:
        click.echo(format_json(tasks))
    else:
        click.echo(format_task_table(tasks))


# -- Labels --


@cli.group()
def label() -> None:
    """Label commands."""


@label.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def label_list(config: Config, as_json: bool) -> None:
    """List all labels."""
    client = _get_client(config)
    svc = LabelService(client, config)
    labels = svc.list()
    if as_json:
        click.echo(format_json(labels))
    else:
        click.echo(format_label_table(labels))


@label.command("create")
@click.option("--title", required=True, help="Label title")
@click.option("--color", default="", help="Hex color (e.g., #ff0000)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def label_create(config: Config, title: str, color: str, as_json: bool) -> None:
    """Create a label."""
    client = _get_client(config)
    svc = LabelService(client, config)
    l = svc.create(title, color)
    if as_json:
        click.echo(format_json(l))
    else:
        click.echo(f"Created label {l.id}: {l.title}")


# -- Cache --


@cli.group()
def cache() -> None:
    """Cache commands."""


@cache.command("clear")
@pass_config
def cache_clear(config: Config) -> None:
    """Clear the name resolution cache."""
    client = _get_client(config)
    resolver = _get_resolver(client, config)
    resolver.clear_cache()
    click.echo("Cache cleared.")


# -- MCP --


@cli.group()
def mcp() -> None:
    """MCP server commands."""


@mcp.command("stdio")
@pass_config
def mcp_stdio(config: Config) -> None:
    """Launch MCP server (stdio transport)."""
    from vk.adapters.mcp_stdio import run_stdio_server

    run_stdio_server(config)


@mcp.command("http")
@click.option("--port", default=8456, type=int, help="HTTP port")
@pass_config
def mcp_http(config: Config, port: int) -> None:
    """Launch MCP server (HTTP/SSE transport)."""
    from vk.adapters.mcp_http import run_http_server

    run_http_server(config, port)
