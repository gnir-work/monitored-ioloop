import asyncio
import typing
from asyncio import Handle

from monitored_ioloop.monioted_ioloop_base import BaseMonitoredEventLoopPolicy
from monitored_ioloop.monitoring import (
    wrap_callback_with_monitoring,
    IoLoopMonitorState,
    IoLoopInnerState,
)


class MonitoredSelectorEventLoop(asyncio.SelectorEventLoop):
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

        handle = super().call_soon(callback_with_monitoring, *args, **kwargs)
        callback_with_monitoring.set_handle(handle)
        return handle


class MonitoredAsyncIOEventLoopPolicy(BaseMonitoredEventLoopPolicy):
    """Event loop policy.

    The preferred way to make your application use monitored asyncio selector based ioloop:

    >>> import asyncio
    >>> import monitored_ioloop
    >>> asyncio.set_event_loop_policy(monitored_ioloop.MonitoredAsyncIOEventLoopPolicy())
    >>> asyncio.get_event_loop()
    <uvloop.Loop running=False closed=False debug=False>
    """

    def _loop_factory(self) -> MonitoredSelectorEventLoop:
        loop = MonitoredSelectorEventLoop(self._monitor_callback)
        return loop
