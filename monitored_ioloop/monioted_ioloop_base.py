import typing
from asyncio.events import BaseDefaultEventLoopPolicy
from monitored_ioloop.monitoring import IoLoopMonitorState


class BaseMonitoredEventLoopPolicy(BaseDefaultEventLoopPolicy):
    def __init__(
        self,
        monitor_callback: typing.Callable[[IoLoopMonitorState], None],
    ):
        super().__init__()
        self._monitor_callback = monitor_callback
