import asyncio
import typing
from typing import Generator

import pytest

from monitored_ioloop.monitored_asyncio import MonitoredAsyncIOEventLoopPolicy
from monitored_ioloop.monitored_ioloop_base import BaseMonitoredEventLoopPolicy
from monitored_ioloop.monitored_uvloop import MonitoredUvloopEventLoopPolicy
from tests.utils import assert_expected_loop_type


@pytest.fixture(
    params=[MonitoredAsyncIOEventLoopPolicy, MonitoredUvloopEventLoopPolicy]
)
def ioloop_policy_class(
    request: pytest.FixtureRequest,
) -> Generator[typing.Type[BaseMonitoredEventLoopPolicy], None, None]:
    yield request.param
    assert_expected_loop_type(request.param)
    asyncio.set_event_loop_policy(None)
