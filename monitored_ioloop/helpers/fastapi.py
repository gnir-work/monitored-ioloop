import asyncio

from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Protocol


class AsgiMiddlewareType(Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...


def mask_numeric_segments(path: str) -> str:
    """
    Example:
    mask_numeric_segments("/api/v1/users/123/name") -> "/api/v1/users/_/name"
    """
    path_parts = path.split("/")
    return "/".join((part if not part.isdigit() else "_") for part in path_parts)


def default_callback_pretty_name(scope: Scope) -> str:
    """
    Default callback_pretty_name for FastAPI helper middleware.
    """
    masked_path = mask_numeric_segments(scope["path"])
    return f"[{scope['method']}] {masked_path}"


class MonitoredIOLoopMiddleware:
    """
    This feature requires you to have installed fastapi BY YOURSELF.
    monitored_ioloop DOES NOT REQUIRE fastapi as a dependency.
    In order to allow a more useful callback_pretty_name when using starlette based frameworks (for example FastAPI),
    this middleware will set the current task name to the HTTP method and path.
    For example when a GET request is made to /ping, the current task name will be set to "[GET] /ping".
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        current_task = asyncio.current_task()
        if current_task is not None:
            current_task.set_name(default_callback_pretty_name(scope))

        await self.app(scope, receive, send)
