import time
import typing

import click
from fastapi import FastAPI
import asyncio
from monitored_ioloop import (
    BaseMonitoredEventLoopPolicy,
)
from uvicorn import Config, Server

from monitored_ioloop.types import IoLoopMonitorState
from stress_tests.server.server_utils import IOLoopType

from stress_tests.server.server_utils import get_io_loop_policy_from_type

app = FastAPI()


@app.get("/ping")
async def ping() -> str:
    return "pong"


@app.get("/async_slow")
async def async_slow(sleep_for: int) -> str:
    for _ in range(sleep_for):
        await asyncio.sleep(1)
    return f"slept for {sleep_for} seconds"


@app.get("/blocking_io_slow")
async def blocking_io_slow(sleep_for: int) -> str:
    for _ in range(sleep_for):
        time.sleep(1)
    return f"slept for {sleep_for} seconds"


def monitor(state: IoLoopMonitorState) -> None:
    if state.cpu_loop_duration > 0.1 or state.wall_loop_duration > 0.1:
        print(state)


def set_ioloop_policy(monitor_type: IOLoopType) -> None:
    ioloop_policy = get_io_loop_policy_from_type(monitor_type)
    if monitor_type in (IOLoopType.monitored_uvloop, IOLoopType.monitored_asyncio):
        asyncio.set_event_loop_policy(
            typing.cast(typing.Type[BaseMonitoredEventLoopPolicy], ioloop_policy)(
                monitor
            )
        )
    else:
        asyncio.set_event_loop_policy(ioloop_policy())


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=1441, help="Port to bind to")
@click.option(
    "--monitor-type",
    type=click.Choice(
        [
            str(IOLoopType.uvloop),
            str(IOLoopType.monitored_uvloop),
            str(IOLoopType.asyncio),
            str(IOLoopType.monitored_asyncio),
        ]
    ),
    default=IOLoopType.monitored_asyncio,
    help="Type of ioloop to run",
)
def run(host: str, port: int, monitor_type: IOLoopType) -> None:
    config = Config(app, host=host, port=port)
    server = Server(config)
    set_ioloop_policy(monitor_type)
    asyncio.run(server.serve())


if __name__ == "__main__":
    run()
