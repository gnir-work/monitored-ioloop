import asyncio
import dataclasses
import typing
from asyncio import AbstractEventLoop
from enum import Enum
from typing import Generator

import pytest

from monitored_ioloop.monitored_asyncio import (
    MonitoredAsyncIOEventLoopPolicy,
    monitored_asyncio_loop_factory,
)
from monitored_ioloop.monitored_ioloop_base import BaseMonitoredEventLoopPolicy
from monitored_ioloop.monitored_uvloop import (
    MonitoredUvloopEventLoopPolicy,
    monitored_uvloop_loop_factory,
)
from tests.utils import assert_expected_loop_type
from unittest.mock import Mock


class LoopType(Enum):
    ASYNCIO = "asyncio"
    UVLOOP = "uvloop"


class InterfaceType(Enum):
    POLICY = "policy"
    FACTORY = "factory"


@dataclasses.dataclass
class TestCaseContext:
    loop_type: LoopType
    interface_type: InterfaceType
    factory: typing.Callable[[], AbstractEventLoop] | None
    policy: BaseMonitoredEventLoopPolicy | None
    mock: Mock


@pytest.fixture(params=[LoopType.ASYNCIO, LoopType.UVLOOP])
def loop_type(request: pytest.FixtureRequest) -> LoopType:
    return typing.cast(LoopType, request.param)


@pytest.fixture(params=[InterfaceType.POLICY, InterfaceType.FACTORY])
def api_type(request: pytest.FixtureRequest) -> InterfaceType:
    return typing.cast(InterfaceType, request.param)


@pytest.fixture
def test_case_context(
    loop_type: LoopType, api_type: InterfaceType
) -> Generator[TestCaseContext, None, None]:
    mock = Mock()
    factory: typing.Callable[[], AbstractEventLoop] | None = None
    policy: BaseMonitoredEventLoopPolicy | None = None

    if loop_type == LoopType.ASYNCIO:
        if api_type == InterfaceType.POLICY:
            policy = MonitoredAsyncIOEventLoopPolicy(mock)
        else:
            factory = monitored_asyncio_loop_factory(mock)
    else:
        if api_type == InterfaceType.POLICY:
            policy = MonitoredUvloopEventLoopPolicy(mock)
        else:
            factory = monitored_uvloop_loop_factory(mock)

    yield TestCaseContext(
        loop_type=loop_type,
        interface_type=api_type,
        factory=factory,
        mock=mock,
        policy=policy,
    )

    if api_type == InterfaceType.POLICY:
        if loop_type == LoopType.ASYNCIO:
            assert_expected_loop_type(MonitoredAsyncIOEventLoopPolicy)
        else:
            assert_expected_loop_type(MonitoredUvloopEventLoopPolicy)

    asyncio.set_event_loop_policy(None)
    asyncio.set_event_loop(None)
