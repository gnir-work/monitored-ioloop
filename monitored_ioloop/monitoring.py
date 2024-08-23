import threading
import time
import typing
from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)


@dataclass
class IoLoopMonitorState:
    # The time it took to execute the callback in wall clock time - https://en.wikipedia.org/wiki/Wall-clock_time
    wall_task_time: float
    # The amount of handles in the loop - https://docs.python.org/3/library/asyncio-eventloop.html#callback-handles
    handles_count: int


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


def wrap_callback_with_monitoring(
    callback: typing.Callable[..., typing.Any],
    monitor_callback: typing.Callable[[IoLoopMonitorState], None],
    ioloop_state: IoLoopInnerState,
) -> typing.Callable[..., typing.Any]:
    """
    Add monitoring to a callback.
    The callback will be wrapped in a function that will monitor the callbacks execution time and report
    back to the monitor_callback.
    """
    ioloop_state.increase_handles_count_thread_safe(1)

    def wrapper(*inner_args: typing.Any, **inner_kwargs: typing.Any) -> typing.Any:
        start_wall_time = time.time()
        response = callback(*inner_args, **inner_kwargs)
        ioloop_state.decrease_handles_count_thread_safe(1)
        wall_duration = time.time() - start_wall_time

        try:
            monitor_callback(
                IoLoopMonitorState(
                    wall_task_time=wall_duration,
                    handles_count=ioloop_state.handles_count,
                )
            )
        except Exception:
            logger.warning("Monitor callback failed.", exc_info=True)
        return response

    return wrapper
