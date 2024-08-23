from monitored_ioloop.exceptions import NoUvLoopInstalled as _NoUvLoopInstalled
from monitored_ioloop.monitored_asyncio_ioloop import (
    MonitoredAsyncIOEventLoopPolicy,
)

__all__: tuple[str, ...] = ("MonitoredAsyncIOEventLoopPolicy",)

try:
    from monitored_ioloop.monitored_uvloop_ioloop import MonitoredUvloopEventLoopPolicy

    __all__ += ("MonitoredUvloopEventLoopPolicy",)
except _NoUvLoopInstalled:
    pass
