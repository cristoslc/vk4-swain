"""Exception types for Vikunja API errors."""


class ApiError(Exception):
    """Base exception for Vikunja API errors."""

    def __init__(self, message: str, status_code: int = 0, response_body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AuthError(ApiError):
    """Authentication/authorization error (401/403)."""


class NotFoundError(ApiError):
    """Resource not found (404)."""
