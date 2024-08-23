import asyncio
import logging

from monitored_ioloop.monitored_asyncio import MonitoredAsyncIOEventLoopPolicy
import time

BLOCK_THRESHOLD = 0.1


def busy_wait(seconds_to_wait: float = 1) -> None:
    now = time.perf_counter()
    while time.perf_counter() - now < seconds_to_wait:
        pass


async def inner_inner_function():
    print("inner inner function - enter")
    print("inner inner function - Before sleep")
    await asyncio.sleep(1)
    print("inner inner function - After sleep")
    print("inner inner function - exit")


async def inner_function():
    print("inner function - enter")
    print("inner function - Before sleep")
    await asyncio.sleep(1)
    print("inner function - After sleep")
    print("inner function - before inner inner function")
    await inner_inner_function()
    print("inner function - after inner inner function")
    print("inner function - exit")


async def blocking_coroutine(block_for: float) -> None:
    busy_wait(1)
    print("outer function - enter")
    print("outer function - before inner function")
    await inner_function()
    print("outer function - after inner function")
    print("outer function - before sleep")
    await asyncio.sleep(1)
    print("outer function - after sleep")
    print("outer function - exit")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print("starting")
    asyncio.set_event_loop_policy(MonitoredAsyncIOEventLoopPolicy(monitor_callback=lambda x: None))
    print("Set event loop")
    asyncio.run(blocking_coroutine(2))
