"""Output formatting for CLI: compact tables and JSON."""

from __future__ import annotations

import json
from typing import Any


def format_json(data: Any) -> str:
    """Format data as pretty-printed JSON."""
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    elif isinstance(data, list):
        data = [item.to_dict() if hasattr(item, "to_dict") else item for item in data]
    return json.dumps(data, indent=2, default=str)


def format_table(rows: list[dict], columns: list[tuple[str, str]]) -> str:
    """Format rows as a compact table.

    columns: list of (key, header) tuples.
    """
    if not rows:
        return "(no results)"

    # Calculate column widths
    widths: dict[str, int] = {}
    for key, header in columns:
        widths[key] = len(header)
        for row in rows:
            val = str(row.get(key, ""))
            widths[key] = max(widths[key], len(val))

    # Header
    header_line = "  ".join(h.ljust(widths[k]) for k, h in columns)
    separator = "  ".join("-" * widths[k] for k, _ in columns)
    lines = [header_line, separator]

    # Rows
    for row in rows:
        line = "  ".join(
            str(row.get(k, "")).ljust(widths[k]) for k, _ in columns
        )
        lines.append(line)

    return "\n".join(lines)


def format_task_table(tasks: list) -> str:
    columns = [
        ("id", "ID"),
        ("title", "Title"),
        ("priority", "Pri"),
        ("due_date", "Due"),
        ("done", "Done"),
    ]
    rows = []
    for t in tasks:
        d = t.to_dict() if hasattr(t, "to_dict") else t
        rows.append({
            "id": d["id"],
            "title": d["title"],
            "priority": d.get("priority", 0),
            "due_date": str(d.get("due_date", "") or "—")[:10],
            "done": "✓" if d.get("done") else "",
        })
    return format_table(rows, columns)


def format_project_table(projects: list) -> str:
    columns = [("id", "ID"), ("title", "Title"), ("description", "Description")]
    rows = []
    for p in projects:
        d = p.to_dict() if hasattr(p, "to_dict") else p
        rows.append({
            "id": d["id"],
            "title": d["title"],
            "description": (d.get("description", "") or "")[:50],
        })
    return format_table(rows, columns)


def format_bucket_table(buckets: list) -> str:
    columns = [("id", "ID"), ("title", "Title"), ("count", "Tasks")]
    rows = []
    for b in buckets:
        d = b.to_dict() if hasattr(b, "to_dict") else b
        rows.append({
            "id": d["id"],
            "title": d["title"],
            "count": d.get("count", 0),
        })
    return format_table(rows, columns)


def format_comment_table(comments: list) -> str:
    columns = [("id", "ID"), ("comment", "Comment"), ("created", "Created")]
    rows = []
    for c in comments:
        d = c.to_dict() if hasattr(c, "to_dict") else c
        rows.append({
            "id": d["id"],
            "comment": (d.get("comment", "") or "")[:60],
            "created": str(d.get("created", "") or "")[:10],
        })
    return format_table(rows, columns)


def format_attachment_table(attachments: list) -> str:
    columns = [("id", "ID"), ("file_name", "File"), ("file_size", "Size")]
    rows = []
    for a in attachments:
        d = a.to_dict() if hasattr(a, "to_dict") else a
        rows.append({
            "id": d["id"],
            "file_name": d.get("file_name", ""),
            "file_size": d.get("file_size", 0),
        })
    return format_table(rows, columns)


def format_label_table(labels: list) -> str:
    columns = [("id", "ID"), ("title", "Title"), ("hex_color", "Color")]
    rows = []
    for l in labels:
        d = l.to_dict() if hasattr(l, "to_dict") else l
        rows.append({
            "id": d["id"],
            "title": d["title"],
            "hex_color": d.get("hex_color", ""),
        })
    return format_table(rows, columns)
