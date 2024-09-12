import asyncio
import time
from typing import Type

from monitored_ioloop.monitored_asyncio import (
    MonitoredAsyncIOEventLoopPolicy,
    MonitoredSelectorEventLoop,
)
from monitored_ioloop.monitored_ioloop_base import BaseMonitoredEventLoopPolicy
from monitored_ioloop.monitored_uvloop import (
    MonitoredUvloopEventLoopPolicy,
    MonitoredUvloopEventLoop,
)

BLOCK_THRESHOLD = 0.1


def busy_wait(seconds_to_wait: float = 1) -> None:
    now = time.perf_counter()
    while time.perf_counter() - now < seconds_to_wait:
        pass


def _assert_monitor_result(
    expected_block: float, monitored_block: float, threshold: float = BLOCK_THRESHOLD
) -> None:
    assert _check_monitor_result(
        expected_block, monitored_block, threshold
    ), f"Expected: {expected_block}, Monitored: {monitored_block}, Threshold: {threshold}"


def _check_monitor_result(
    expected_block: float, monitored_block: float, threshold: float = BLOCK_THRESHOLD
) -> bool:
    return (
        expected_block * (1 - threshold)
        < monitored_block
        < expected_block * (1 + threshold)
    )


async def _assert_expected_loop_type(
    loop_policy: Type[BaseMonitoredEventLoopPolicy],
) -> None:
    if issubclass(loop_policy, MonitoredAsyncIOEventLoopPolicy):
        assert isinstance(asyncio.get_event_loop(), MonitoredSelectorEventLoop)
    elif issubclass(loop_policy, MonitoredUvloopEventLoopPolicy):
        assert isinstance(asyncio.get_event_loop(), MonitoredUvloopEventLoop)
    else:
        raise ValueError("Unknown loop policy")


def assert_expected_loop_type(loop_policy: Type[BaseMonitoredEventLoopPolicy]) -> None:
    asyncio.run(_assert_expected_loop_type(loop_policy))
