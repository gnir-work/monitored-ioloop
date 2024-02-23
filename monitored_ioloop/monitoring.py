import time
import typing

from monitored_ioloop.types import IoLoopMonitorState


def wrap_callback_with_monitoring(
    callback: typing.Callable[..., typing.Any],
    monitor_callback: typing.Callable[[IoLoopMonitorState], None],
) -> typing.Callable[..., typing.Any]:
    """
    Add monitoring to a callback.
    The callback will be wrapped in a function that will monitor the callbacks execution time and report
    back to the monitor_callback.
    """

    def wrapper(*inner_args: typing.Any, **inner_kwargs: typing.Any) -> typing.Any:
        start_wall_time = time.time()
        start_cpu_time = time.process_time()
        response = callback(*inner_args, **inner_kwargs)
        wall_duration = time.time() - start_wall_time
        cpu_duration = time.process_time() - start_cpu_time
        monitor_callback(
            IoLoopMonitorState(
                wall_loop_duration=wall_duration,
                cpu_loop_duration=cpu_duration,
            )
        )
        return response

    return wrapper
