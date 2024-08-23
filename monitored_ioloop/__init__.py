import typing as _typing

from asyncio.events import BaseDefaultEventLoopPolicy as __BasePolicy

from .asyncio_profiler import MonitoredSelectorEventLoop as _MonitoredSelectorEventLoop

__all__ = ("EventLoopPolicy",)

from .types import IoLoopMonitorState as _IoLoopMonitorState


class EventLoopPolicy(__BasePolicy):
    """Event loop policy.

    The preferred way to make your application use monitored ioloop:

    >>> import asyncio
    >>> import monitored_ioloop
    >>> asyncio.set_event_loop_policy(monitored_ioloop.EventLoopPolicy())
    >>> asyncio.get_event_loop()
    <uvloop.Loop running=False closed=False debug=False>
    """

    def __init__(
        self,
        monitor_callback: _typing.Callable[[_IoLoopMonitorState], None] | None = None,
    ):
        super().__init__()
        self._monitor_callback = monitor_callback

    def _loop_factory(self) -> _MonitoredSelectorEventLoop:
        loop = _MonitoredSelectorEventLoop(self._monitor_callback)
        return loop

    if _typing.TYPE_CHECKING:
        # EventLoopPolicy doesn't implement these, but since they are marked
        # as abstract in typeshed, we have to put them in so mypy thinks
        # the base methods are overridden. This is the same approach taken
        # for the Windows event loop policy classes in typeshed.
        def get_child_watcher(self) -> _typing.NoReturn:
            ...

        def set_child_watcher(self, watcher: _typing.Any) -> _typing.NoReturn:
            ...
