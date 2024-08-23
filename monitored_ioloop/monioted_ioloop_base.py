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

    if typing.TYPE_CHECKING:
        # EventLoopPolicy doesn't implement these, but since they are marked
        # as abstract in typeshed, we have to put them in so mypy thinks
        # the base methods are overridden. This is the same approach taken
        # for the Windows event loop policy classes in typeshed.
        def get_child_watcher(self) -> typing.NoReturn: ...

        def set_child_watcher(self, watcher: typing.Any) -> typing.NoReturn: ...
