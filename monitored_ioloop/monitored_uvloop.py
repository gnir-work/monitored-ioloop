from monitored_ioloop.exceptions import NoUvLoopInstalled

try:
    import uvloop
except ImportError:
    raise NoUvLoopInstalled() from None

import typing

from asyncio import Handle

from monitored_ioloop.monioted_ioloop_base import BaseMonitoredEventLoopPolicy
from monitored_ioloop.monitoring import (
    wrap_callback_with_monitoring,
    IoLoopMonitorState,
    IoLoopInnerState,
)


class MonitoredUvloopEventLoop(uvloop.Loop):
    def __init__(
        self,
        monitor_callback: typing.Callable[[IoLoopMonitorState], None],
        *args: typing.Any,
        **kwargs: typing.Any,
    ):
        super().__init__(*args, **kwargs)
        self._monitor_callback = monitor_callback
        self._state = IoLoopInnerState(handles_count=0)

    def call_soon(
        self,
        callback: typing.Callable[..., typing.Any],
        *args: typing.Any,  # type: ignore
        **kwargs: typing.Any,
    ) -> Handle:
        callback_with_monitoring = wrap_callback_with_monitoring(
            callback, self._monitor_callback, self._state
        )
        return super().call_soon(callback_with_monitoring, *args, **kwargs)


class MonitoredUvloopEventLoopPolicy(BaseMonitoredEventLoopPolicy):
    """Event loop policy.

    The preferred way to make your application use monitored uvloop ioloop:

    >>> import asyncio
    >>> import monitored_ioloop
    >>> asyncio.set_event_loop_policy(monitored_ioloop.MonitoredUvloopEventLoopPolicy())
    >>> asyncio.get_event_loop()
    <uvloop.Loop running=False closed=False debug=False>
    """

    def _loop_factory(self) -> MonitoredUvloopEventLoop:
        loop = MonitoredUvloopEventLoop(self._monitor_callback)
        return loop
