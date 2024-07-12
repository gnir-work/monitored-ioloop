import threading
import time
import typing
from dataclasses import dataclass
from logging import getLogger

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


class MonitoredCallback:
    def __init__(
        self,
        callback: typing.Callable[[IoLoopMonitorState], None],
        monitor_callback: typing.Callable[[IoLoopMonitorState], None],
        io_loop_state: IoLoopInnerState,
    ):
        self._callback_to_monitor = callback
        self._original_callback = monitor_callback
        self._ioloop_state = io_loop_state
        self._added_to_loop_time = time.perf_counter()

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        loop_lag = time.perf_counter() - self._added_to_loop_time
        start_wall_time = time.perf_counter()
        response = self._callback_to_monitor(*args, **kwargs)
        self._ioloop_state.decrease_handles_count_thread_safe(1)
        wall_duration = time.perf_counter() - start_wall_time

        try:
            self._original_callback(
                IoLoopMonitorState(
                    callback_wall_time=wall_duration,
                    loop_handles_count=self._ioloop_state.handles_count,
                    loop_lag=loop_lag,
                )
            )
        except Exception:
            logger.warning("Monitor callback failed.", exc_info=True)
        return response

    def __getattr__(self, item: str) -> typing.Any:
        return getattr(self._callback_to_monitor, item)


def wrap_callback_with_monitoring(
    callback: typing.Callable[..., typing.Any],
    monitor_callback: typing.Callable[[IoLoopMonitorState], None],
    ioloop_state: IoLoopInnerState,
) -> typing.Callable[..., typing.Any]:
    ioloop_state.increase_handles_count_thread_safe(1)
    return MonitoredCallback(callback, monitor_callback, ioloop_state)
