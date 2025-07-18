from mypy_extensions import VarArg

from monitored_ioloop.exceptions import NoUvLoopInstalled

try:
    import uvloop
# pragma: no cover
except ImportError:
    # pragma: no cover
    raise NoUvLoopInstalled() from None

import typing
import warnings

from asyncio import Handle

from monitored_ioloop.monitored_ioloop_base import BaseMonitoredEventLoopPolicy
from monitored_ioloop.monitoring import (
    wrap_callback_with_monitoring,
    IoLoopMonitorState,
    IoLoopInnerState,
)

_Ts = typing.TypeVarTuple("_Ts")


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
        callback: typing.Callable[[VarArg(*_Ts)], object],
        *args: *_Ts,
        **kwargs: typing.Any,
    ) -> Handle:
        callback_with_monitoring = wrap_callback_with_monitoring(
            callback, self._monitor_callback, self._state
        )
        return super().call_soon(callback_with_monitoring, *args, **kwargs)


class MonitoredUvloopEventLoopPolicy(BaseMonitoredEventLoopPolicy):
    """Event loop policy.

    .. deprecated:: 0.0.15
        Use :func:`monitored_uvloop_loop_factory` instead.
        The policy-based approach is deprecated in favor of the loop factory approach
        which is preferred by Python's asyncio documentation.

    Usage example:
    >>> import asyncio
    >>> import monitored_ioloop
    >>> asyncio.set_event_loop_policy(monitored_ioloop.MonitoredUvloopEventLoopPolicy())
    >>> asyncio.get_event_loop()
    """

    def __init__(self, monitor_callback: typing.Callable[[IoLoopMonitorState], None]):
        warnings.warn(
            "MonitoredUvloopEventLoopPolicy is deprecated. "
            "Use monitored_uvloop_loop_factory() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(monitor_callback)

    def _loop_factory(self) -> MonitoredUvloopEventLoop:
        loop = MonitoredUvloopEventLoop(self._monitor_callback)
        return loop


def monitored_uvloop_loop_factory(
    monitor_callback: typing.Callable[[IoLoopMonitorState], None],
) -> typing.Callable[[], MonitoredUvloopEventLoop]:
    """Create a loop factory function for use with asyncio.run().

    Usage:
    >>> import asyncio
    >>> import monitored_ioloop
    >>> factory = monitored_ioloop.monitored_uvloop_loop_factory(lambda state: print(state))
    >>> asyncio.run(main(), loop_factory=factory)
    """

    def loop_factory() -> MonitoredUvloopEventLoop:
        return MonitoredUvloopEventLoop(monitor_callback)

    return loop_factory
