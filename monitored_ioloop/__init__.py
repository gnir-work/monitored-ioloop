from monitored_ioloop.exceptions import NoUvLoopInstalled as _NoUvLoopInstalled
from monitored_ioloop.monitored_asyncio_ioloop import (
    MonitoredAsyncIOEventLoopPolicy,
)
from monitored_ioloop.types import IoLoopMonitorState

__all__: tuple[str, ...] = ("MonitoredAsyncIOEventLoopPolicy", "IoLoopMonitorState")

try:
    from monitored_ioloop.monitored_uvloop_ioloop import MonitoredUvloopEventLoopPolicy

    __all__ += ("MonitoredUvloopEventLoopPolicy",)
except _NoUvLoopInstalled:
    pass
