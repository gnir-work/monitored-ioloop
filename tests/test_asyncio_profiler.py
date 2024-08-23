import time
import asyncio

from monitored_ioloop import run, EventLoopPolicy


def busy_wait(seconds_to_wait: int = 1) -> None:
    now = time.perf_counter()
    while time.perf_counter() - now < seconds_to_wait:
        pass


async def test() -> None:
    print("sleeping for 2 seconds")
    busy_wait(2)


def run_with_run_function() -> None:
    run(test())


def run_with_event_loop_policy() -> None:
    asyncio.set_event_loop_policy(EventLoopPolicy())
    asyncio.run(test())


if __name__ == "__main__":
    run_with_run_function()
    run_with_event_loop_policy()
