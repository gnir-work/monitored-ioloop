import asyncio
import time
from unittest.mock import Mock

from monitored_ioloop import EventLoopPolicy
from tests.utils import busy_wait, _check_monitor_result


async def blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)


def test_simple_blocking_coroutine() -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(EventLoopPolicy(monitor_callback=mock))
    block_for = 0.1
    asyncio.run(blocking_coroutine(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _check_monitor_result(block_for, blocking_coroutine_monitor.wall_loop_duration)
    _check_monitor_result(block_for, blocking_coroutine_monitor.cpu_loop_duration)


async def complex_blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)
    await asyncio.sleep(1)
    busy_wait(block_for)


def test_complex_blocking_coroutine() -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(EventLoopPolicy(monitor_callback=mock))
    block_for = 0.1
    asyncio.run(complex_blocking_coroutine(block_for))
    (first_blocking_section,) = mock.mock_calls[0].args
    (second_blocking_section,) = mock.mock_calls[1].args
    _check_monitor_result(block_for, first_blocking_section.wall_loop_duration)
    _check_monitor_result(block_for, second_blocking_section.wall_loop_duration)
    _check_monitor_result(block_for, first_blocking_section.cpu_loop_duration)
    _check_monitor_result(block_for, second_blocking_section.cpu_loop_duration)


async def run_blocking_coroutine_in_task(block_for: float) -> None:
    task = asyncio.create_task(blocking_coroutine(block_for))
    await task


def test_task_blocking_coroutine() -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(EventLoopPolicy(monitor_callback=mock))
    block_for = 0.1
    asyncio.run(run_blocking_coroutine_in_task(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[1].args
    _check_monitor_result(block_for, blocking_coroutine_monitor.wall_loop_duration)
    _check_monitor_result(block_for, blocking_coroutine_monitor.cpu_loop_duration)


async def non_cpu_intensive_blocking_coroutine(block_time: float) -> None:
    time.sleep(block_time)


def test_non_cpu_intensive_blocking_coroutine() -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(EventLoopPolicy(monitor_callback=mock))
    block_for = 0.1
    asyncio.run(non_cpu_intensive_blocking_coroutine(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _check_monitor_result(block_for, blocking_coroutine_monitor.wall_loop_duration)
    assert (
        blocking_coroutine_monitor.cpu_loop_duration < 0.001
    ), "CPU time should be minimal."
