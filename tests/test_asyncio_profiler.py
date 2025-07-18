import asyncio
import time
import typing

import pytest
from unittest.mock import Mock

from monitored_ioloop.monitored_ioloop_base import (
    BaseMonitoredEventLoopPolicy,
)
from monitored_ioloop.monitored_uvloop import MonitoredUvloopEventLoopPolicy
from monitored_ioloop.monitored_asyncio import monitored_asyncio_loop_factory
from monitored_ioloop.monitored_uvloop import monitored_uvloop_loop_factory
from tests.utils import (
    busy_wait,
    _assert_monitor_result,
    _check_monitor_result,
)


async def blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)


def test_simple_blocking_coroutine(
    ioloop_policy_class: typing.Type[BaseMonitoredEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(blocking_coroutine(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _assert_monitor_result(block_for, blocking_coroutine_monitor.callback_wall_time)
    assert (
        mock.mock_calls[0].args[0].loop_handles_count == 1
    ), "Initial handles count should be 1."
    assert (
        mock.mock_calls[-1].args[0].loop_handles_count == 0
    ), "Handles count should drop to 0."


def monitor_callback_with_error(monitor: typing.Any) -> None:
    raise ValueError("This monitor callback raises an exception.")


def test_monitor_callback_error_is_handled(
    ioloop_policy_class: typing.Type[BaseMonitoredEventLoopPolicy],
) -> None:
    asyncio.set_event_loop_policy(
        ioloop_policy_class(monitor_callback=monitor_callback_with_error)
    )
    block_for = 0.1
    asyncio.run(blocking_coroutine(block_for))


async def coroutine_with_result() -> int:
    await asyncio.sleep(0.1)
    return 10


def test_callback_returns_value_even_if_monitor_callback_fails(
    ioloop_policy_class: typing.Type[BaseMonitoredEventLoopPolicy],
) -> None:
    policy = ioloop_policy_class(monitor_callback=monitor_callback_with_error)
    asyncio.set_event_loop_policy(policy)
    result = asyncio.run(coroutine_with_result())
    assert result == 10


async def complex_blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)
    await asyncio.sleep(1)
    busy_wait(block_for)


def test_complex_blocking_coroutine(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(complex_blocking_coroutine(block_for))
    (first_blocking_section,) = mock.mock_calls[0].args
    (second_blocking_section,) = mock.mock_calls[1].args
    _assert_monitor_result(block_for, first_blocking_section.callback_wall_time)
    _assert_monitor_result(block_for, second_blocking_section.callback_wall_time)


async def run_blocking_coroutine_in_task(block_for: float) -> None:
    task = asyncio.create_task(blocking_coroutine(block_for))
    await task


def test_task_blocking_coroutine(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(run_blocking_coroutine_in_task(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[1].args
    _assert_monitor_result(block_for, blocking_coroutine_monitor.callback_wall_time)


async def non_cpu_intensive_blocking_coroutine(block_time: float) -> None:
    time.sleep(block_time)


def test_non_cpu_intensive_blocking_coroutine(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(non_cpu_intensive_blocking_coroutine(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _assert_monitor_result(block_for, blocking_coroutine_monitor.callback_wall_time)


async def exception_raising_coroutine() -> None:
    raise ValueError("This coroutine raises an exception.")


def test_handles_count_decreases_even_if_handle_raises_exception(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    with pytest.raises(ValueError):
        asyncio.run(exception_raising_coroutine())
    assert (
        mock.mock_calls[0].args[0].loop_handles_count == 1
    ), "Initial handles count should be 1."
    assert (
        mock.mock_calls[-1].args[0].loop_handles_count == 0
    ), "Handles count should drop to 0."


async def multiple_coroutines_partly_blocking(
    blocking_count: int,
    non_blocking_count: int,
) -> None:
    async def sleep() -> None:
        await asyncio.sleep(0.1)

    async def blocking_sleep() -> None:
        time.sleep(0.2)

    await asyncio.gather(
        *(
            [blocking_sleep() for _ in range(blocking_count)]
            + [sleep() for _ in range(non_blocking_count)]
        )
    )


def test_handles_count_with_multiple_coroutines(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    asyncio.run(
        multiple_coroutines_partly_blocking(blocking_count=0, non_blocking_count=3)
    )
    assert (
        mock.mock_calls[0].args[0].loop_handles_count == 3
    ), "After the first handle finishes we should have 3 sleep coroutines running."
    assert (
        mock.mock_calls[-1].args[0].loop_handles_count == 0
    ), "Handles count should drop to 0."


def test_loop_lag(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    non_blocking_coroutines_count = 4
    blocking_coroutines_count = 1
    asyncio.run(
        multiple_coroutines_partly_blocking(
            blocking_count=blocking_coroutines_count,
            non_blocking_count=non_blocking_coroutines_count,
        )
    )
    assert (
        mock.mock_calls[0].args[0].loop_handles_count
        == non_blocking_coroutines_count + blocking_coroutines_count
    ), "After the first handle finishes all coroutines should be registered."
    assert (
        len(
            [
                call
                for call in mock.mock_calls
                if _check_monitor_result(0.2, call.args[0].loop_lag)
            ]
        )
        == non_blocking_coroutines_count
    )


def test_callback_pretty_name__basic_top_level_coroutine_name(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    asyncio.run(non_cpu_intensive_blocking_coroutine(0.1))
    assert (
        len(
            [
                callback_pretty_name
                for call in mock.mock_calls
                if "non_cpu_intensive_blocking_coroutine"
                in (callback_pretty_name := call.args[0].callback_pretty_name)
            ]
        )
        == 1
    )


async def several_coroutines_in_gather_with_pretty_name_testing() -> None:
    async def first_function() -> None:
        time.sleep(0.1)

    async def second_function() -> None:
        time.sleep(0.1)

    await asyncio.gather(
        first_function(),
        first_function(),
        second_function(),
    )


def test_callback_pretty_name__several_coroutines_with_gather(
    ioloop_policy_class: typing.Type[MonitoredUvloopEventLoopPolicy],
) -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(ioloop_policy_class(monitor_callback=mock))
    asyncio.run(several_coroutines_in_gather_with_pretty_name_testing())

    # The function is called twice from the ioloop, once until the gather and once after the gather has finished
    assert (
        len(
            [
                callback_pretty_name
                for call in mock.mock_calls
                if (
                    "several_coroutines_in_gather_with_pretty_name_testing"
                    in (callback_pretty_name := call.args[0].callback_pretty_name)
                    and "first_function" not in callback_pretty_name
                    and "second_function" not in callback_pretty_name
                )
            ]
        )
        == 2
    )

    assert (
        len(
            [
                callback_pretty_name
                for call in mock.mock_calls
                if "first_function"
                in (callback_pretty_name := call.args[0].callback_pretty_name)
            ]
        )
        == 2
    )

    assert (
        len(
            [
                callback_pretty_name
                for call in mock.mock_calls
                if "second_function"
                in (callback_pretty_name := call.args[0].callback_pretty_name)
            ]
        )
        == 1
    )


def test_asyncio_loop_factory_simple_blocking() -> None:
    mock = Mock()
    factory = monitored_asyncio_loop_factory(mock)
    block_for = 0.5
    asyncio.run(blocking_coroutine(block_for), loop_factory=factory)
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _assert_monitor_result(block_for, blocking_coroutine_monitor.callback_wall_time)
    assert (
        mock.mock_calls[0].args[0].loop_handles_count == 1
    ), "Initial handles count should be 1."
    assert (
        mock.mock_calls[-1].args[0].loop_handles_count == 0
    ), "Handles count should drop to 0."


def test_uvloop_loop_factory_simple_blocking() -> None:
    mock = Mock()
    factory = monitored_uvloop_loop_factory(mock)
    block_for = 0.5
    asyncio.run(blocking_coroutine(block_for), loop_factory=factory)
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    _assert_monitor_result(block_for, blocking_coroutine_monitor.callback_wall_time)
    assert (
        mock.mock_calls[0].args[0].loop_handles_count == 1
    ), "Initial handles count should be 1."
    assert (
        mock.mock_calls[-1].args[0].loop_handles_count == 0
    ), "Handles count should drop to 0."
