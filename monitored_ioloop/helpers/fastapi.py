import asyncio

from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Protocol, Type, Callable


class AsgiMiddlewareType(Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...


def default_callback_pretty_name(scope: Scope) -> str:
    """
    Default callback_pretty_name for FastAPI helper middleware.
    """
    return f"[{scope['method']}] {scope['path']}"


def get_monitor_async_io_middleware(
    callback_pretty_name_formatter: Callable[
        [Scope], str
    ] = default_callback_pretty_name,
) -> Type[AsgiMiddlewareType]:
    """
    This feature requires you to have installed fastapi BY YOURSELF.
    monitored_ioloop DOES NOT REQUIRE fastapi as a dependency.

    In order to allow a more useful callback_pretty_name when using starlette based frameworks (for example FastAPI),
    this middleware will set the current task name to the HTTP method and path.

    For example when a GET request is made to /ping, the current task name will be set to "[GET] /ping".
    @param callback_pretty_name_formatter: A function that receives the scope and returns a string that will be used
    as the current task name. See "default_callback_pretty_name" for the default implementation.
    """

    class MonitoredAsyncIOMiddleWare:
        def __init__(self, app: ASGIApp) -> None:
            self.app = app

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await self.app(scope, receive, send)
                return

            current_task = asyncio.current_task()
            if current_task is not None:
                current_task.set_name(callback_pretty_name_formatter(scope))

            await self.app(scope, receive, send)

    return MonitoredAsyncIOMiddleWare
