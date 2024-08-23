import asyncio
import typing
from asyncio import Handle

from monitored_ioloop.monitoring import wrap_callback_with_monitoring
from monitored_ioloop.types import IoLoopMonitorState


class MonitoredSelectorEventLoop(asyncio.SelectorEventLoop):
    def __init__(
        self,
        monitor_callback: typing.Callable[[IoLoopMonitorState], None],
        *args: typing.Any,
        **kwargs: typing.Any,
    ):
        super().__init__(*args, **kwargs)
        self._monitor_callback = monitor_callback

    def call_soon(
        self,
        callback: typing.Callable[..., typing.Any],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> Handle:
        callback_with_monitoring = wrap_callback_with_monitoring(
            callback, self._monitor_callback
        )

        return super().call_soon(callback_with_monitoring, *args, **kwargs)
