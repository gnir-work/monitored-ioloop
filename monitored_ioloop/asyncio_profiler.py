import asyncio
import time
import typing
from asyncio import Handle

from monitored_ioloop.types import IoLoopMonitorState


class MonitoredSelectorEventLoop(asyncio.SelectorEventLoop):
    def __init__(
        self,
        monitor_callback: typing.Callable[[IoLoopMonitorState], None] | None = None,
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
        def wrapper(*inner_args: typing.Any, **inner_kwargs: typing.Any) -> typing.Any:
            start = time.time()
            response = callback(*inner_args, **inner_kwargs)
            duration = time.time() - start
            if self._monitor_callback:
                self._monitor_callback(
                    IoLoopMonitorState(single_loop_duration=duration)
                )
            return response

        return super().call_soon(wrapper, *args, **kwargs)

    def call_soon_threadsafe(
        self,
        callback: typing.Callable[..., typing.Any],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> Handle:
        def wrapper(*inner_args: typing.Any, **inner_kwargs: typing.Any) -> typing.Any:
            start = time.time()
            response = callback(*inner_args, **inner_kwargs)
            duration = time.time() - start
            if self._monitor_callback:
                self._monitor_callback(
                    IoLoopMonitorState(single_loop_duration=duration)
                )
            return response

        return super().call_soon_threadsafe(wrapper, *args, **kwargs)
