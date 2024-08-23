import asyncio
from unittest.mock import Mock

from monitored_ioloop import EventLoopPolicy
from tests.utils import busy_wait

BLOCK_THRESHOLD = 0.05


async def blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)


def test_simple_blocking_coroutine() -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(EventLoopPolicy(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(blocking_coroutine(block_for))
    (blocking_coroutine_monitor,) = mock.mock_calls[0].args
    assert (
        block_for * (1 - BLOCK_THRESHOLD)
        < blocking_coroutine_monitor.single_loop_duration
        < block_for * (1 + BLOCK_THRESHOLD)
    )


async def complex_blocking_coroutine(block_for: float) -> None:
    busy_wait(block_for)
    await asyncio.sleep(1)
    busy_wait(block_for)


def test_complex_blocking_coroutine() -> None:
    mock = Mock()
    asyncio.set_event_loop_policy(EventLoopPolicy(monitor_callback=mock))
    block_for = 0.5
    asyncio.run(complex_blocking_coroutine(block_for))
    (first_blocking_section,) = mock.mock_calls[0].args
    (second_blocking_section,) = mock.mock_calls[1].args
    assert (
        block_for * (1 - BLOCK_THRESHOLD)
        < first_blocking_section.single_loop_duration
        < block_for * (1 + BLOCK_THRESHOLD)
    )
    assert (
        block_for * (1 - BLOCK_THRESHOLD)
        < second_blocking_section.single_loop_duration
        < block_for * (1 + BLOCK_THRESHOLD)
    )
