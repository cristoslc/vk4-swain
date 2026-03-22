"""HTTP client for the Vikunja REST API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from vk.exceptions import ApiError, AuthError, NotFoundError


class VikunjaClient:
    """Stateless HTTP adapter for the Vikunja REST API.

    Handles auth headers, pagination, multipart uploads, and error mapping.
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._session = requests.Session()
        self._session.headers["Authorization"] = f"Bearer {token}"

    # -- low-level helpers --

    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/v1{path}"

    def _handle_error(self, resp: requests.Response) -> None:
        if resp.ok:
            return
        body = resp.text
        if resp.status_code in (401, 403):
            raise AuthError(f"Auth error: {resp.status_code}", resp.status_code, body)
        if resp.status_code == 404:
            raise NotFoundError(f"Not found: {resp.url}", resp.status_code, body)
        raise ApiError(
            f"API error: {resp.status_code}", resp.status_code, body
        )

    def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
        files: dict | None = None,
    ) -> Any:
        resp = self._session.request(
            method, self._url(path), json=json, params=params, files=files
        )
        self._handle_error(resp)
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    def _paginated_get(
        self, path: str, params: dict | None = None, per_page: int = 50
    ) -> list[dict]:
        """Fetch all pages from a paginated endpoint."""
        params = dict(params or {})
        params["per_page"] = per_page
        all_items: list[dict] = []
        page = 1
        while True:
            params["page"] = page
            resp = self._session.get(self._url(path), params=params)
            self._handle_error(resp)
            items = resp.json()
            if not isinstance(items, list):
                return [items] if items else []
            all_items.extend(items)
            if len(items) < per_page:
                break
            page += 1
        return all_items

    # -- Auth --

    def login(self, username: str, password: str) -> dict:
        resp = self._session.post(
            self._url("/login"), json={"username": username, "password": password}
        )
        self._handle_error(resp)
        return resp.json()

    def create_api_token(self, jwt_token: str, title: str, permissions: dict, expires_at: str) -> dict:
        resp = self._session.put(
            self._url("/tokens"),
            json={"title": title, "permissions": permissions, "expires_at": expires_at},
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        self._handle_error(resp)
        return resp.json()

    # -- Projects --

    def list_projects(self) -> list[dict]:
        return self._paginated_get("/projects")

    def get_project(self, project_id: int) -> dict:
        return self._request("GET", f"/projects/{project_id}")

    def create_project(self, title: str, description: str = "") -> dict:
        return self._request("PUT", "/projects", json={"title": title, "description": description})

    # -- Views --

    def list_views(self, project_id: int) -> list[dict]:
        return self._paginated_get(f"/projects/{project_id}/views")

    # -- Buckets --

    def list_buckets(self, project_id: int, view_id: int) -> list[dict]:
        return self._paginated_get(f"/projects/{project_id}/views/{view_id}/buckets")

    def create_bucket(self, project_id: int, view_id: int, title: str) -> dict:
        return self._request(
            "PUT",
            f"/projects/{project_id}/views/{view_id}/buckets",
            json={"title": title},
        )

    # -- Tasks --

    def list_tasks(self, project_id: int | None = None, params: dict | None = None) -> list[dict]:
        if project_id:
            return self._paginated_get(f"/projects/{project_id}/tasks", params=params)
        return self._paginated_get("/tasks/all", params=params)

    def get_task(self, task_id: int) -> dict:
        return self._request("GET", f"/tasks/{task_id}")

    def create_task(self, project_id: int, data: dict) -> dict:
        return self._request("PUT", f"/projects/{project_id}/tasks", json=data)

    def update_task(self, task_id: int, data: dict) -> dict:
        return self._request("POST", f"/tasks/{task_id}", json=data)

    def delete_task(self, task_id: int) -> None:
        self._request("DELETE", f"/tasks/{task_id}")

    def move_task_to_bucket(
        self, project_id: int, view_id: int, bucket_id: int, task_id: int
    ) -> dict:
        return self._request(
            "POST",
            f"/projects/{project_id}/views/{view_id}/buckets/{bucket_id}/tasks",
            json={"task_id": task_id},
        )

    # -- Comments --

    def list_comments(self, task_id: int) -> list[dict]:
        return self._paginated_get(f"/tasks/{task_id}/comments")

    def add_comment(self, task_id: int, text: str) -> dict:
        return self._request(
            "PUT", f"/tasks/{task_id}/comments", json={"comment": text}
        )

    # -- Attachments --

    def list_attachments(self, task_id: int) -> list[dict]:
        return self._paginated_get(f"/tasks/{task_id}/attachments")

    def upload_attachment(self, task_id: int, file_path: str) -> dict:
        path = Path(file_path)
        with open(path, "rb") as f:
            return self._request(
                "PUT",
                f"/tasks/{task_id}/attachments",
                files={"files": (path.name, f)},
            )

    def download_attachment(self, task_id: int, attachment_id: int) -> bytes:
        resp = self._session.get(
            self._url(f"/tasks/{task_id}/attachments/{attachment_id}")
        )
        self._handle_error(resp)
        return resp.content

    # -- Search --

    def search_tasks(self, query: str, params: dict | None = None) -> list[dict]:
        p = dict(params or {})
        p["s"] = query
        return self._paginated_get("/tasks/all", params=p)

    # -- Labels --

    def list_labels(self) -> list[dict]:
        return self._paginated_get("/labels")

    def create_label(self, title: str, hex_color: str = "") -> dict:
        data: dict[str, Any] = {"title": title}
        if hex_color:
            data["hex_color"] = hex_color
        return self._request("PUT", "/labels", json=data)
