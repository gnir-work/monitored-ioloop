import typing as _typing

from asyncio.events import BaseDefaultEventLoopPolicy as __BasePolicy

from .monitored_selector_ioloop import (
    MonitoredSelectorEventLoop as _MonitoredSelectorEventLoop,
)
from .monitored_uvloop_ioloop import (
    MonitoredUvloopEventLoop as _MonitoredUvloopEventLoop,
)

__all__ = (
    "MonitoredAsyncIOSelectorEventLoopPolicy",
    "MonitoredUvloopEventLoopPolicy",
    "BaseMonitoredEventLoopPolicy",
)

from .types import IoLoopMonitorState as _IoLoopMonitorState


class BaseMonitoredEventLoopPolicy(__BasePolicy):
    def __init__(
        self,
        monitor_callback: _typing.Callable[[_IoLoopMonitorState], None],
    ):
        super().__init__()
        self._monitor_callback = monitor_callback

    if _typing.TYPE_CHECKING:
        # EventLoopPolicy doesn't implement these, but since they are marked
        # as abstract in typeshed, we have to put them in so mypy thinks
        # the base methods are overridden. This is the same approach taken
        # for the Windows event loop policy classes in typeshed.
        def get_child_watcher(self) -> _typing.NoReturn:
            ...

        def set_child_watcher(self, watcher: _typing.Any) -> _typing.NoReturn:
            ...


class MonitoredAsyncIOSelectorEventLoopPolicy(BaseMonitoredEventLoopPolicy):
    """Event loop policy.

    The preferred way to make your application use monitored asyncio selector based ioloop:

    >>> import asyncio
    >>> import monitored_ioloop
    >>> asyncio.set_event_loop_policy(monitored_ioloop.MonitoredAsyncIOSelectorEventLoopPolicy())
    >>> asyncio.get_event_loop()
    <uvloop.Loop running=False closed=False debug=False>
    """

    def _loop_factory(self) -> _MonitoredSelectorEventLoop:
        loop = _MonitoredSelectorEventLoop(self._monitor_callback)
        return loop


class MonitoredUvloopEventLoopPolicy(BaseMonitoredEventLoopPolicy):
    """Event loop policy.

    The preferred way to make your application use monitored uvloop ioloop:

    >>> import asyncio
    >>> import monitored_ioloop
    >>> asyncio.set_event_loop_policy(monitored_ioloop.MonitoredUvloopEventLoopPolicy())
    >>> asyncio.get_event_loop()
    <uvloop.Loop running=False closed=False debug=False>
    """

    def _loop_factory(self) -> _MonitoredUvloopEventLoop:
        loop = _MonitoredUvloopEventLoop(self._monitor_callback)
        return loop
