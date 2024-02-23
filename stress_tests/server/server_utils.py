import enum
import asyncio
import uvloop
from monitored_ioloop import (
    MonitoredAsyncIOSelectorEventLoopPolicy,
    MonitoredUvloopEventLoopPolicy,
)


class IOLoopType(enum.StrEnum):
    uvloop = "uvloop"
    asyncio = "asyncio"
    monitored_uvloop = "monitored_uvloop"
    monitored_asyncio = "monitored_asyncio"


def get_io_loop_policy_from_type(
    ioloop_type: IOLoopType,
) -> type[asyncio.AbstractEventLoopPolicy]:
    if ioloop_type == IOLoopType.uvloop:
        return uvloop.EventLoopPolicy
    if ioloop_type == IOLoopType.asyncio:
        return asyncio.DefaultEventLoopPolicy
    if ioloop_type == IOLoopType.monitored_uvloop:
        return MonitoredUvloopEventLoopPolicy
    if ioloop_type == IOLoopType.monitored_asyncio:
        return MonitoredAsyncIOSelectorEventLoopPolicy
    raise ValueError(f"Unknown IOLoopType: {ioloop_type}")
