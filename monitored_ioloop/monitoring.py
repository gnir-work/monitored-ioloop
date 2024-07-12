import threading
import time
import typing
from asyncio import Handle
from dataclasses import dataclass
from logging import getLogger

from monitored_ioloop.formatting_utils import pretty_format_handle, pretty_callback_name

logger = getLogger(__name__)


@dataclass
class IoLoopMonitorState:
    """
    A dataclass containing the state of the loop when the callback was executed.
    This class is the interface that the monitor callback will receive.

    A basic Lexicon:
    * Handle - A wrapper for a callback that is scheduled to be executed by the loop.
    * Callback - The function that is executed by the loop.
    * Loop - The event loop that is executing the callbacks.
    """

    """
    Wall executing time of the callback
    It can be the whole coroutine or parts of it, depending on if the executing control
    was delegated back the loop or not.

    Wall Time explanation - https://en.wikipedia.org/wiki/Wall-clock_time
    """
    callback_wall_time: float

    """
    A best effort try to give a meaningful name to the callback that was currently executed.
    This property will come in handy when trying to debug callbacks with high wall time. 
    """
    callback_pretty_name: str

    """
    The amount of handles in the loop, excluding the current one.
    """
    loop_handles_count: int

    """
    The amount of time it took from the moment the coroutine was added to the loop until it was executed.
    """
    loop_lag: float


@dataclass
class IoLoopInnerState:
    handles_count: int
    handles_count_lock = threading.Lock()

    def increase_handles_count_thread_safe(self, increase_by: int) -> None:
        """
        Increase the amount of total handles in a thread safe way.
        """
        with self.handles_count_lock:
            self.handles_count += increase_by

    def decrease_handles_count_thread_safe(self, decrease_by: int) -> None:
        """
        Decrease the amount of total handles in a thread safe way.
        """
        with self.handles_count_lock:
            self.handles_count -= decrease_by


class MonitoredCallbackWrapper:
    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        monitor_callback: typing.Callable[[IoLoopMonitorState], None],
        io_loop_state: IoLoopInnerState,
    ):
        self._original_callback = callback
        self._monitor_callback = monitor_callback
        self._ioloop_state = io_loop_state
        self._added_to_loop_time = time.perf_counter()
        self._handle: typing.Optional[Handle] = None

    def set_handle(self, handle: Handle) -> None:
        self._handle = handle

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        loop_lag = time.perf_counter() - self._added_to_loop_time
        start_wall_time = time.perf_counter()
        response = self._original_callback(*args, **kwargs)
        self._ioloop_state.decrease_handles_count_thread_safe(1)
        wall_duration = time.perf_counter() - start_wall_time

        try:
            pretty_name = (
                pretty_format_handle(self._handle)
                if self._handle
                else pretty_callback_name(self._original_callback)
            )
            self._monitor_callback(
                IoLoopMonitorState(
                    callback_wall_time=wall_duration,
                    loop_handles_count=self._ioloop_state.handles_count,
                    loop_lag=loop_lag,
                    callback_pretty_name=pretty_name,
                )
            )
        except Exception:
            logger.warning("Monitor callback failed.", exc_info=True)
        return response

    def __getattr__(self, item: str) -> typing.Any:
        return getattr(self._original_callback, item)


def wrap_callback_with_monitoring(
    callback: typing.Callable[..., typing.Any],
    monitor_callback: typing.Callable[[IoLoopMonitorState], None],
    ioloop_state: IoLoopInnerState,
) -> MonitoredCallbackWrapper:
    ioloop_state.increase_handles_count_thread_safe(1)
    return MonitoredCallbackWrapper(callback, monitor_callback, ioloop_state)
