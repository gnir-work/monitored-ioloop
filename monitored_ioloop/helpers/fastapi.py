import asyncio

from starlette.types import ASGIApp, Receive, Scope, Send


class MonitoredAsyncIOMiddleWare:
    """
    In order to allow a more useful callback_pretty_name when using starlette based frameworks (for example FastAPI),
    this middleware will set the current task name to the HTTP method and path.

    For example when a GET request is made to /ping, the current task name will be set to "[GET] /ping".

    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]
        current_task = asyncio.current_task()
        if current_task is not None:
            current_task.set_name(f"[{method}] {path}")

        await self.app(scope, receive, send)
