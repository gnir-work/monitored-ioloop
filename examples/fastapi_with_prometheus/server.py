import asyncio
import time

from monitored_ioloop.monitored_asyncio import monitored_asyncio_loop_factory
from monitored_ioloop.monitoring import IoLoopMonitorState
from monitored_ioloop.helpers.fastapi import (
    MonitoredIOLoopMiddleware,
)
from fastapi import FastAPI
from prometheus_client import start_http_server, Histogram
from uvicorn import Server, Config

slow_callbacks_wall_time_histogram = Histogram(
    "slow_callbacks_wall_time_histogram",
    "Histogram of the slow callbacks (coroutines) that are blocking the loop",
    labelnames=["callback_name"],
    buckets=[0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 2, 4],
)

loop_lag_time_histogram = Histogram(
    "loop_lag_time_histogram",
    "Histogram of the loop lag time",
    buckets=[0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 2, 4],
)

app = FastAPI()
app.add_middleware(MonitoredIOLoopMiddleware)


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
    loop_lag_time_histogram.observe(ioloop_monitor_state.loop_lag)
    callback_wall_time = ioloop_monitor_state.callback_wall_time
    callback_pretty_name = ioloop_monitor_state.callback_pretty_name
    if callback_wall_time > 0.5:
        slow_callbacks_wall_time_histogram.labels(callback_pretty_name).observe(
            callback_wall_time
        )


def main() -> None:
    """
    Using the new loop factory API for cleaner integration with asyncio.run().
    """
    loop_factory = monitored_asyncio_loop_factory(monitor_ioloop)
    config = Config(app=app, host="localhost", port=1441, loop="asyncio")
    server = Server(config)
    start_http_server(1551)
    asyncio.run(server.serve(), loop_factory=loop_factory)


if __name__ == "__main__":
    main()
