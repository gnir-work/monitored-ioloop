import threading
import time
import typing
from dataclasses import dataclass


@dataclass
class IoLoopMonitorState:
    wall_loop_duration: float
    cpu_loop_duration: float
    total_handles: int


@dataclass
class IoLoopInnerState:
    total_handles: int
    total_handles_lock = threading.Lock()

    def increase_total_handles_thread_safe(self, increase_by: int) -> None:
        """
        Increase the amount of total handles in a thread safe way.
        """
        with self.total_handles_lock:
            self.total_handles += increase_by

    def decrease_total_handles_thread_safe(self, decrease_by: int) -> None:
        """
        Decrease the amount of total handles in a thread safe way.
        """
        with self.total_handles_lock:
            self.total_handles -= decrease_by


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
    ioloop_state.increase_total_handles_thread_safe(1)

    def wrapper(*inner_args: typing.Any, **inner_kwargs: typing.Any) -> typing.Any:
        start_wall_time = time.time()
        start_cpu_time = time.process_time()
        response = callback(*inner_args, **inner_kwargs)
        ioloop_state.decrease_total_handles_thread_safe(1)
        wall_duration = time.time() - start_wall_time
        cpu_duration = time.process_time() - start_cpu_time
        monitor_callback(
            IoLoopMonitorState(
                wall_loop_duration=wall_duration,
                cpu_loop_duration=cpu_duration,
                total_handles=ioloop_state.total_handles,
            )
        )
        return response

    return wrapper
