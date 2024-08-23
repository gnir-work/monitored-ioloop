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
            start_wall_time = time.time()
            start_cpu_time = time.process_time()
            response = callback(*inner_args, **inner_kwargs)
            wall_duration = time.time() - start_wall_time
            cpu_duration = time.process_time() - start_cpu_time
            if self._monitor_callback:
                self._monitor_callback(
                    IoLoopMonitorState(
                        wall_loop_duration=wall_duration,
                        cpu_loop_duration=cpu_duration,
                    )
                )
            return response

        return super().call_soon(wrapper, *args, **kwargs)
