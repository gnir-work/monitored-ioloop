import asyncio
import time

from monitored_ioloop.monitored_asyncio import MonitoredAsyncIOEventLoopPolicy
from monitored_ioloop.monitoring import IoLoopMonitorState
from fastapi import FastAPI
from prometheus_client import start_http_server, Histogram
from uvicorn import Server, Config

ioloop_execution_time_histogram = Histogram(
    "ioloop_execution_time_histogram",
    "Histogram of the ioloop execution time",
    buckets=[0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 2, 4],
)

app = FastAPI()


@app.get("/ping")
async def ping() -> str:
    return "pong"


@app.get("/async_slow")
async def async_slow(sleep_for: int, coroutines_number: int) -> str:
    await asyncio.gather(*[asyncio.sleep(sleep_for) for _ in range(coroutines_number)])
    return f"slept for {sleep_for} seconds and created {coroutines_number} coroutines"


@app.get("/blocking_slow")
async def blocking_slow(sleep_for: int) -> str:
    time.sleep(sleep_for)
    return f"slept for {sleep_for} seconds"


def monitor_ioloop(ioloop_monitor_state: IoLoopMonitorState) -> None:
    ioloop_execution_time_histogram.observe(ioloop_monitor_state.wall_task_time)


def main() -> None:
    """
    Current because uvloop does not support settings the ioloop to a custom implementation, we need to
    run the server manually and not from the CLI.
    I am currently working on allowing passing an import string to a custom event loop policy which
    will considerably simplify the fastapi example.
    """
    asyncio.set_event_loop_policy(MonitoredAsyncIOEventLoopPolicy(monitor_ioloop))
    config = Config(app=app, host="localhost", port=1441, loop="asyncio")
    server = Server(config)
    start_http_server(1551)
    asyncio.run(server.serve())


if __name__ == "__main__":
    main()
