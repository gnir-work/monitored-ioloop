import asyncio
import time
import typing

import pytest
from unittest.mock import Mock

from monitored_ioloop.monioted_ioloop_base import (
    BaseMonitoredEventLoopPolicy,
)
from monitored_ioloop.monitored_uvloop import MonitoredUvloopEventLoopPolicy
from monitored_ioloop.monitored_asyncio import (
    MonitoredAsyncIOEventLoopPolicy,
)
from tests.utils import busy_wait, _check_monitor_result


async def blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)


@pytest.mark.parametrize(
    "ioloop_policy_class",
    [MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy],
)
def test_simple_blocking_coroutine(
    ioloop_policy_class: typing.Type[BaseMonitoredEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(blocking_coroutine(block_for))
    print(mock.mock_calls)
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _check_monitor_result(block_for, blocking_coroutine_monitor.wall_loop_duration)
    _check_monitor_result(
        block_for, blocking_coroutine_monitor.cpu_loop_duration, threshold=0.15
    )
    assert (
        mock.mock_calls[0].args[0].handles_count == 1
    ), "Initial handles count should be 1."
    assert (
        mock.mock_calls[-1].args[0].handles_count == 0
    ), "Handles count should drop to 0."


def monitor_callback_with_error(monitor: typing.Any) -> None:
    raise ValueError("This monitor callback raises an exception.")


@pytest.mark.parametrize(
    "ioloop_policy_class",
    [MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy],
)
def test_monitor_callback_error_is_handled(
    ioloop_policy_class: typing.Type[BaseMonitoredEventLoopPolicy],
) -> None:
    asyncio.set_event_loop_policy(
        ioloop_policy_class(monitor_callback=monitor_callback_with_error)
    )
    block_for = 0.1
    asyncio.run(blocking_coroutine(block_for))


async def complex_blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)
    await asyncio.sleep(1)
    busy_wait(block_for)


@pytest.mark.parametrize(
    "ioloop_policy_class",
    [MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy],
)
def test_complex_blocking_coroutine(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
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


@pytest.mark.parametrize(
    "ioloop_policy_class",
    [MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy],
)
def test_task_blocking_coroutine(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(run_blocking_coroutine_in_task(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[1].args
    _check_monitor_result(block_for, blocking_coroutine_monitor.wall_loop_duration)
    _check_monitor_result(block_for, blocking_coroutine_monitor.cpu_loop_duration)


async def non_cpu_intensive_blocking_coroutine(block_time: float) -> None:
    time.sleep(block_time)


@pytest.mark.parametrize(
    "ioloop_policy_class",
    [MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy],
)
def test_non_cpu_intensive_blocking_coroutine(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(non_cpu_intensive_blocking_coroutine(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _check_monitor_result(block_for, blocking_coroutine_monitor.wall_loop_duration)
    assert (
        blocking_coroutine_monitor.cpu_loop_duration < 0.02
    ), "CPU time should be minimal."


async def exception_raising_coroutine() -> None:
    raise ValueError("This coroutine raises an exception.")


@pytest.mark.parametrize(
    "ioloop_policy_class",
    [MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy],
)
def test_handles_count_decreases_even_if_handle_raises_exception(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    with pytest.raises(ValueError):
        asyncio.run(exception_raising_coroutine())
    assert (
        mock.mock_calls[0].args[0].handles_count == 1
    ), "Initial handles count should be 1."
    assert (
        mock.mock_calls[-1].args[0].handles_count == 0
    ), "Handles count should drop to 0."


async def multiple_coroutines() -> None:
    async def sleep() -> None:
        await asyncio.sleep(0.1)

    await asyncio.gather(sleep(), sleep(), sleep())


@pytest.mark.parametrize(
    "ioloop_policy_class",
    [MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy],
)
def test_handles_count_with_multiple_coroutines(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    asyncio.run(multiple_coroutines())
    assert (
        mock.mock_calls[0].args[0].handles_count == 3
    ), "After the first handle finishes we should have 3 sleep coroutines running."
    assert (
        mock.mock_calls[-1].args[0].handles_count == 0
    ), "Handles count should drop to 0."
